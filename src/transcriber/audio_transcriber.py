import os
from pathlib import Path
from faster_whisper import WhisperModel

class AudioTranscriber:
    """
    Clase encargada de la transcripción de archivos de audio a texto usando faster-whisper.
    """
    def __init__(self, model_size: str = "base"):
        """
        Inicializa el transcritor con un modelo de faster-whisper.
        
        Args:
            model_size (str): Tamaño del modelo (e.g., 'tiny', 'base', 'small', 'medium', 'large-v3').
        """
        self.model_size = model_size
        self.model = None
        self._ensure_ffmpeg_in_path()

    def _ensure_ffmpeg_in_path(self):
        """Intenta encontrar ffmpeg y añadirlo al PATH si es necesario."""
        ffmpeg_path = r"C:\Users\ready\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"
        if os.path.exists(ffmpeg_path):
            os.environ["PATH"] += os.pathsep + ffmpeg_path

    def _load_model(self):
        """Carga el modelo de faster-whisper optimizado para GPU si es posible."""
        if self.model is None:
            print(f"Cargando modelo faster-whisper '{self.model_size}'...")
            # Automatically detects if CUDA is available, otherwise uses CPU
            self.model = WhisperModel(self.model_size, device="cuda", compute_type="float16")

    def transcribe(self, audio_path: str, progress_callback=None) -> str:
        """
        Transcribe un archivo de audio a texto e informa el progreso fluidamente.
        
        Args:
            audio_path (str): Ruta al archivo de audio (MP3).
            progress_callback (callable): Función para recibir el porcentaje de progreso.
            
        Returns:
            str: El texto transcrito.
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo de audio: {audio_path}")

        try:
            self._load_model()
            print(f"Iniciando transcripción de {audio_path.name}...")
            
            # Vad_filter es esencial para evitar las alucinaciones en silencios
            segments, info = self.model.transcribe(str(audio_path), vad_filter=True, language="es")
            
            total_duration = info.duration
            transcription_pieces = []
            
            for segment in segments:
                transcription_pieces.append(segment.text)
                if progress_callback and total_duration > 0:
                    pct = int(min((segment.end / total_duration) * 100, 99))
                    progress_callback(pct)
                    
            text = " ".join(transcription_pieces).strip()
            print(f"Transcripción completada con éxito.")
            return text
            
        except Exception as e:
            print(f"Error durante la transcripción GPU: {e}")
            # Fallback en caso de que el driver CUDA no este bien configurado 
            print("Intentando fallback a CPU (más lento)...")
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            segments, info = self.model.transcribe(str(audio_path), vad_filter=True, language="es")
            
            total_duration = info.duration
            transcription_pieces = []
            for segment in segments:
                transcription_pieces.append(segment.text)
                if progress_callback and total_duration > 0:
                    pct = int(min((segment.end / total_duration) * 100, 99))
                    progress_callback(pct)
            return " ".join(transcription_pieces).strip()

if __name__ == "__main__":
    transcriber = AudioTranscriber(model_size="tiny")
