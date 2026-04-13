from moviepy import VideoFileClip
import os
from pathlib import Path
import proglog

class MyBarLogger(proglog.ProgressBarLogger):
    def __init__(self, on_progress):
        super().__init__()
        self.on_progress = on_progress
        
    def bars_callback(self, bar, attr, value, old_value=None):
        if bar == 'chunk' and self.bars[bar]['total'] > 0:
            percentage = int((value / self.bars[bar]['total']) * 100)
            if self.on_progress:
                self.on_progress(percentage)

class VideoConverter:
    """
    Clase encargada de la conversión de archivos de video a audio.
    """
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def convert_mp4_to_mp3(self, video_path: str, progress_callback=None) -> Path:
        """
        Convierte un archivo MP4 a MP3.
        
        Args:
            video_path (str): Ruta al archivo de video original.
            progress_callback (callable): Función para recibir el progreso (0-100).
            
        Returns:
            Path: Ruta al archivo MP3 generado.
            
        Raises:
            ValueError: Si el archivo no es un MP4 válido.
            Exception: Si ocurre un error durante la conversión.
        """
        video_path = Path(video_path)
        if video_path.suffix.lower() != '.mp4':
            raise ValueError("El archivo de entrada debe ser un MP4.")

        if not video_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {video_path}")

        # Definir el nombre del archivo de salida
        audio_filename = video_path.stem + ".mp3"
        audio_path = self.output_dir / audio_filename

        try:
            print(f"Iniciando conversión de {video_path.name} a {audio_filename}...")
            video = VideoFileClip(str(video_path))
            
            logger = 'bar'
            if progress_callback:
                logger = MyBarLogger(progress_callback)
                
            video.audio.write_audiofile(str(audio_path), logger=logger)
            video.close()
            print(f"Conversión completada con éxito: {audio_path}")
            return audio_path
        except Exception as e:
            print(f"Error durante la conversión: {e}")
            raise e

if __name__ == "__main__":
    # Prueba rápida de la clase
    converter = VideoConverter()
    # Reemplaza con un archivo real para probar localmente
    # converter.convert_mp4_to_mp3("test_video.mp4")
