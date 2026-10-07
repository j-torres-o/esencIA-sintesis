import logging
import os
import shutil
from pathlib import Path

from faster_whisper import BatchedInferencePipeline, WhisperModel

logger = logging.getLogger(__name__)


def format_timestamp(seconds: float) -> str:
    """
    Convierte segundos a una marca de tiempo legible:
    - [MM:SS] para duraciones menores a una hora.
    - [HH:MM:SS] para duraciones de una hora o más.
    """
    total_seconds = max(0, int(seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def get_optimal_cpu_threads() -> int:
    """
    Calcula la cantidad óptima de hilos CPU para inferencia local ASR.
    Reserva hilos para garantizar fluidez del sistema operativo e interfaz gráfica.
    En una CPU de 32 hilos (Zen 5), asigna 24 hilos de inferencia paralela.
    """
    total_threads = os.cpu_count() or 4
    if total_threads >= 24:
        return total_threads - 8  # e.g., 32 - 8 = 24 hilos
    elif total_threads >= 8:
        return total_threads - 2
    return max(1, total_threads)



def ensure_ffmpeg_in_path():
    """
    Verifica si ffmpeg está en el PATH del sistema o lo localiza dinámicamente
    en rutas de instalación estándar de WinGet / Chocolatey / Scoop / AppData.
    """
    if shutil.which("ffmpeg") is not None:
        return

    # Búsqueda dinámica en carpetas estándar del usuario
    candidate_roots = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages",
        Path(os.environ.get("PROGRAMFILES", "")) / "ffmpeg",
        Path(os.environ.get("PROGRAMDATA", "")) / "chocolatey" / "bin",
        Path.home() / "scoop" / "shims",
    ]

    for root in candidate_roots:
        if root.exists():
            for ffmpeg_exe in root.rglob("ffmpeg.exe"):
                bin_dir = str(ffmpeg_exe.parent)
                os.environ["PATH"] += os.pathsep + bin_dir
                logger.info(f"ffmpeg detectado y añadido al PATH: {bin_dir}")
                return


class AudioTranscriber:
    """
    Clase central para la transcripción de audio a texto.
    Admite selección desacoplada de motores locales:
      - 'parakeet_redux': Moondream Parakeet Redux (178 MB, ultra-rápido >100x CPU)
      - 'whisper_large_v3_turbo': Faster-Whisper Large-V3-Turbo (máxima fidelidad, code-switching)
    """

    SUPPORTED_ENGINES = {
        "parakeet_redux": "Parakeet Redux (Ultra-rápido, 178MB)",
        "whisper_large_v3_turbo": "Whisper Large-V3-Turbo (Máxima precisión)",
    }

    def __init__(self, engine_type: str = "parakeet_redux", model_size: str = None):
        """
        Inicializa el transcriptor.
        
        Args:
            engine_type (str): 'parakeet_redux' o 'whisper_large_v3_turbo'.
            model_size (str): Parámetro de compatibilidad opcional.
        """
        self.engine_type = engine_type or "parakeet_redux"
        if model_size and model_size != "base":
            self.model_size = model_size
        elif self.engine_type == "whisper_large_v3_turbo":
            self.model_size = "large-v3-turbo"
        else:
            self.model_size = "large-v3-turbo"

        self.model = None
        self.batched_pipeline = None
        ensure_ffmpeg_in_path()

    def _load_whisper_model(self):
        """Carga el modelo faster-whisper con compute_type int8 y BatchedInferencePipeline optimizado para CPU multihilo."""
        if self.model is None:
            threads = get_optimal_cpu_threads()
            logger.info(f"Cargando faster-whisper '{self.model_size}' con {threads} hilos CPU e int8...")
            try:
                # Intento inicial automático (CUDA si existiese, sino CPU multihilo optimizado)
                self.model = WhisperModel(
                    self.model_size,
                    device="auto",
                    compute_type="int8",
                    cpu_threads=threads,
                    num_workers=2,
                )
            except Exception as e:
                logger.warning(f"Fallback a CPU básico tras error: {e}")
                self.model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="int8",
                    cpu_threads=threads,
                )

            # Optimización de inferencia por lotes (BatchedInferencePipeline) si se ejecuta el modelo real
            if BatchedInferencePipeline is not None and type(self.model) is WhisperModel:
                try:
                    self.batched_pipeline = BatchedInferencePipeline(self.model)
                    logger.info("BatchedInferencePipeline inicializado exitosamente (batch_size=16).")
                except Exception as e:
                    logger.warning(f"No se pudo inicializar BatchedInferencePipeline ({e}). Usando inferencia secuencial.")
                    self.batched_pipeline = None

    def _transcribe_with_whisper(
        self,
        audio_path: Path,
        progress_callback=None,
        include_timestamps: bool = True,
    ) -> str:
        """
        Transcribe usando faster-whisper con marcas de tiempo de segmento [MM:SS],
        detección inteligente de idioma (ES/EN) y filtro VAD para eliminar alucinaciones.
        Aprovecha BatchedInferencePipeline para acelerar el procesamiento en CPUs multihilo.
        """
        self._load_whisper_model()
        logger.info(f"Iniciando transcripción Whisper de {audio_path.name}...")

        pipeline = self.batched_pipeline if self.batched_pipeline is not None else self.model
        transcribe_kwargs = {
            "vad_filter": True,
            "language": None,  # Auto-detección nativa
            "language_detection_segments": 3,
            "language_detection_threshold": 0.4,
        }
        if self.batched_pipeline is not None:
            transcribe_kwargs["batch_size"] = 16

        segments, info = pipeline.transcribe(
            str(audio_path),
            **transcribe_kwargs,
        )

        detected_lang = getattr(info, "language", "desconocido")
        lang_prob = getattr(info, "language_probability", 0.0)
        prob_str = f"{lang_prob:.2f}" if isinstance(lang_prob, (int, float)) else str(lang_prob)
        logger.info(f"Idioma detectado por Whisper: {detected_lang} (certeza: {prob_str})")

        total_duration = getattr(info, "duration", 0.0)
        transcription_pieces = []

        for segment in segments:
            clean_text = segment.text.strip()
            if clean_text:
                if include_timestamps:
                    start_time = getattr(segment, "start", 0.0)
                    transcription_pieces.append(f"[{format_timestamp(start_time)}] {clean_text}")
                else:
                    transcription_pieces.append(clean_text)

            if progress_callback and total_duration > 0:
                pct = int(min((segment.end / total_duration) * 100, 99))
                progress_callback(pct)

        separator = "\n" if include_timestamps else " "
        return separator.join(transcription_pieces).strip()

    def _transcribe_with_parakeet(
        self,
        audio_path: Path,
        progress_callback=None,
        include_timestamps: bool = True,
    ) -> str:
        """
        Ejecuta la transcripción mediante Parakeet Redux (Moondream) con marcas de tiempo si la biblioteca
        está instalada. Si no está presente en el entorno, conmuta transparentemente a Whisper.
        """
        try:
            import moondream as md  # noqa: F401

            logger.info(f"Transcribiendo con Parakeet Redux: {audio_path.name}")
            if progress_callback:
                progress_callback(10)

            # Implementación con motor moondream / photon
            model = md.load("moondream/parakeet-redux")
            if progress_callback:
                progress_callback(40)

            try:
                result = model.transcribe(str(audio_path), timestamps="segments" if include_timestamps else False)
            except TypeError:
                result = model.transcribe(str(audio_path))

            if progress_callback:
                progress_callback(95)

            if isinstance(result, dict) and "segments" in result and include_timestamps:
                formatted_segments = []
                for seg in result["segments"]:
                    start = seg.get("start", 0.0)
                    seg_text = seg.get("text", "").strip()
                    if seg_text:
                        formatted_segments.append(f"[{format_timestamp(start)}] {seg_text}")
                if formatted_segments:
                    return "\n".join(formatted_segments).strip()

            text = result.get("text", "") if isinstance(result, dict) else str(result)
            return text.strip()

        except (ImportError, Exception) as e:
            logger.info(
                f"Parakeet Redux no disponible en el entorno o encontró un error ({e}). "
                "Conmutando transparentemente a Whisper Large-V3-Turbo..."
            )
            return self._transcribe_with_whisper(
                audio_path,
                progress_callback,
                include_timestamps=include_timestamps,
            )

    def transcribe(
        self,
        audio_path: str,
        progress_callback=None,
        include_timestamps: bool = True,
    ) -> str:
        """
        Punto de entrada unificado para transcribir audio a texto.
        
        Args:
            audio_path (str): Ruta al archivo de audio.
            progress_callback (callable): Función receptora de avance en porcentaje (0-100).
            include_timestamps (bool): Si es True (predeterminado), genera marcas de tiempo [MM:SS] por segmento.
            
        Returns:
            str: Texto transcrito.
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo de audio: {audio_path}")

        if self.engine_type == "parakeet_redux":
            text = self._transcribe_with_parakeet(
                audio_path,
                progress_callback,
                include_timestamps=include_timestamps,
            )
        else:
            text = self._transcribe_with_whisper(
                audio_path,
                progress_callback,
                include_timestamps=include_timestamps,
            )

        if progress_callback:
            progress_callback(100)

        return text

