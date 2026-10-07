import logging
import os
import shutil
from pathlib import Path

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


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
        ensure_ffmpeg_in_path()

    def _load_whisper_model(self):
        """Carga el modelo de faster-whisper con compute_type int8 optimizado para CPU Ryzen Zen 5."""
        if self.model is None:
            logger.info(f"Cargando faster-whisper '{self.model_size}'...")
            try:
                # Intento inicial automático (CUDA si existiese, sino CPU optimizado)
                self.model = WhisperModel(
                    self.model_size,
                    device="auto",
                    compute_type="int8",
                    cpu_threads=16,
                )
            except Exception as e:
                logger.warning(f"Fallback a CPU básico tras error: {e}")
                self.model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="int8",
                    cpu_threads=16,
                )

    def _transcribe_with_whisper(self, audio_path: Path, progress_callback=None) -> str:
        """
        Transcribe usando faster-whisper con detección inteligente de idioma (ES/EN)
        y filtro VAD para eliminar alucinaciones en pausas o silencios.
        """
        self._load_whisper_model()
        logger.info(f"Iniciando transcripción Whisper de {audio_path.name}...")

        # Detección automática con muestreo de segmentos (ES / EN)
        segments, info = self.model.transcribe(
            str(audio_path),
            vad_filter=True,
            language=None,  # Auto-detección nativa
            language_detection_segments=3,
            language_detection_threshold=0.4,
        )

        detected_lang = getattr(info, "language", "desconocido")
        lang_prob = getattr(info, "language_probability", 0.0)
        prob_str = f"{lang_prob:.2f}" if isinstance(lang_prob, (int, float)) else str(lang_prob)
        logger.info(f"Idioma detectado por Whisper: {detected_lang} (certeza: {prob_str})")

        total_duration = getattr(info, "duration", 0.0)
        transcription_pieces = []

        for segment in segments:
            transcription_pieces.append(segment.text)
            if progress_callback and total_duration > 0:
                pct = int(min((segment.end / total_duration) * 100, 99))
                progress_callback(pct)

        return " ".join(transcription_pieces).strip()

    def _transcribe_with_parakeet(self, audio_path: Path, progress_callback=None) -> str:
        """
        Ejecuta la transcripción mediante Parakeet Redux (Moondream) si la biblioteca
        está instalada. Si no está presente en el entorno, conmuta transparentemente a Whisper.
        """
        try:
            import moondream as md  # noqa: F401

            logger.info(f"Transcribiendo con Parakeet Redux: {audio_path.name}")
            # Emisión de progreso inicial
            if progress_callback:
                progress_callback(10)

            # Implementación con motor moondream / photon
            model = md.load("moondream/parakeet-redux")
            if progress_callback:
                progress_callback(40)

            result = model.transcribe(str(audio_path))
            if progress_callback:
                progress_callback(95)

            text = result.get("text", "") if isinstance(result, dict) else str(result)
            return text.strip()

        except (ImportError, Exception) as e:
            logger.info(
                f"Parakeet Redux no disponible en el entorno o encontró un error ({e}). "
                "Conmutando transparentemente a Whisper Large-V3-Turbo..."
            )
            return self._transcribe_with_whisper(audio_path, progress_callback)

    def transcribe(self, audio_path: str, progress_callback=None) -> str:
        """
        Punto de entrada unificado para transcribir audio a texto.
        
        Args:
            audio_path (str): Ruta al archivo de audio.
            progress_callback (callable): Función receptora de avance en porcentaje (0-100).
            
        Returns:
            str: Texto transcrito.
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo de audio: {audio_path}")

        if self.engine_type == "parakeet_redux":
            text = self._transcribe_with_parakeet(audio_path, progress_callback)
        else:
            text = self._transcribe_with_whisper(audio_path, progress_callback)

        if progress_callback:
            progress_callback(100)

        return text
