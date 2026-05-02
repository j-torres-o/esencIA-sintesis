import sys
import os
import time
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QObject, QUrl, QEvent
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from converter.video_converter import VideoConverter
from transcriber import AudioTranscriber
from summarizer import GemmaSummarizer
from utils.config_manager import ConfigManager
from utils.resource_handler import get_resource_path
from version import __version__
import dotenv
import requests


class ProcessingThread(QThread):
    """
    Hilo para realizar el procesamiento pesado sin bloquear la UI.
    """
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    stats_signal = pyqtSignal(dict)
    progress_pct_signal = pyqtSignal(int, str)

    def __init__(self, video_path: str):
        super().__init__()
        self.video_path = video_path

    def run(self):
        try:
            start_time = datetime.now()
            output_dir = Path(self.video_path).parent
            base_name = Path(self.video_path).stem
            
            self.progress_signal.emit(f"Iniciando proceso a las {start_time.strftime('%H:%M:%S')}...")
            
            # 1. Conversión
            self.progress_signal.emit("Iniciando conversión de video a audio...")
            converter = VideoConverter(output_dir=str(output_dir))
            def conv_cb(pct):
                self.progress_pct_signal.emit(pct, "Convirtiendo video a MP3...")
            audio_path = converter.convert_mp4_to_mp3(self.video_path, conv_cb)
            self.progress_pct_signal.emit(100, "Conversión de MP3 Completada")
            time.sleep(0.5)

            # 2. Transcripción
            self.progress_signal.emit("Iniciando transcripción de audio...")
            transcriber = AudioTranscriber()
            def trans_cb(pct):
                self.progress_pct_signal.emit(pct, "Transcribiendo audio...")
            transcription_text = transcriber.transcribe(str(audio_path), trans_cb)
            self.progress_pct_signal.emit(100, "Transcripción Completada")
            time.sleep(0.5)
            
            # Guardar la transcripcion cruda para auditoria INMEDIATAMENTE
            transcription_file = output_dir / f"{base_name}_transcription.txt"
            with open(transcription_file, "w", encoding="utf-8") as f:
                f.write(transcription_text)

            # 3. Resumen
            summarizer = GemmaSummarizer()
            self.progress_signal.emit(f"Generando resumen con {summarizer.model_name}...")
            
            summary_md, tokens_used = summarizer.summarize(transcription_text)

            # 4. Guardar resultados Automáticos (Resumen MD)
            summary_file = output_dir / f"{base_name}_summary.md"
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary_md)
                
            # Generar PDF automáticamente
            # (se ha movido a la ejecución principal en on_finished para evitar crasheos por uso de motor GUI en hilos secundarios)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            stats = {
                "start_time": start_time.strftime("%H:%M:%S"),
                "end_time": end_time.strftime("%H:%M:%S"),
                "duration": str(duration).split('.')[0], # Remove microseconds
                "tokens": tokens_used
            }
            self.stats_signal.emit(stats)

            
            self.finished_signal.emit(summary_md)

        except Exception as e:
            self.error_signal.emit(str(e))

class UIBackend(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.window = main_window
        self.config = ConfigManager()

    @pyqtSlot(result=str)
    def get_theme_preference(self):
        return self.config.get("theme_preference")

    @pyqtSlot(str)
    def save_theme_preference(self, theme):
        self.config.set("theme_preference", theme)

    @pyqtSlot(result=str)
    def get_model_name(self):
        return self.config.get("gemma_model_name")

    @pyqtSlot(result=list)
    def get_ollama_models(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=1.5)
            if response.status_code == 200:
                return [m['name'] for m in response.json().get('models', [])]
            return []
        except:
            return []

    @pyqtSlot(str)
    def save_model_name(self, model_name):
        self.config.set("gemma_model_name", model_name)

    @pyqtSlot()
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.window, "Seleccionar Video", "", "Video Files (*.mp4 *.avi *.mov)"
        )
        if file_path:
            self.on_file_dropped(file_path)

    @pyqtSlot(str)
    def on_file_dropped(self, file_path):
        if str(file_path).lower().endswith(".mp4"):
            self.window.start_processing(file_path)
        else:
            self.window.run_js(f"updateLog('{datetime.now().strftime('%H:%M')}','Error: El archivo debe ser un MP4.');")

    @pyqtSlot()
    def download_summary(self):
        self.window.download_summary()

    @pyqtSlot()
    def download_pdf(self):
        self.window.download_pdf()


    @pyqtSlot()
    def toggle_theme(self):
        self.window.toggle_theme()

class SilentWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if "tailwindcss.com" in message and "production" in message:
            return
        super().javaScriptConsoleMessage(level, message, lineNumber, sourceID)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"esencIA v{__version__} | Académico")
        self.resize(1200, 800)

        # Set Window Icon
        icon_path = get_resource_path("src/ui/assets/icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Setup WebEngineView
        self.browser = QWebEngineView()
        self.browser.setPage(SilentWebEnginePage(self.browser))
        
        # Permitir carga de scripts y fuentes externas desde archivos locales
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        
        # Interceptar Drag & Drop a nivel nativo
        self.browser.installEventFilter(self)
        if self.browser.focusProxy():
            self.browser.focusProxy().installEventFilter(self)
        
        # Setup WebChannel
        self.channel = QWebChannel()
        self.backend = UIBackend(self)
        self.channel.registerObject("backend", self.backend)
        self.browser.page().setWebChannel(self.channel)

        # Load local HTML file
        html_path = get_resource_path("src/ui/index.html")
        self.browser.setUrl(QUrl.fromLocalFile(html_path))

        self.setCentralWidget(self.browser)

        self.current_theme = "dark"
        self.current_summary_md = ""
        
        # Verificar Ollama al iniciar (después de que el browser esté listo)
        self.browser.loadFinished.connect(self.initial_health_check)

    def initial_health_check(self):
        """Verifica si Ollama está corriendo al iniciar la app."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=1)
            if response.status_code != 200:
                self.run_js("showOllamaWarning(true);")
        except:
            self.run_js("showOllamaWarning(true);")

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.Drop:
            mime = event.mimeData()
            if mime and mime.hasUrls():
                file_path = mime.urls()[0].toLocalFile()
                self.backend.on_file_dropped(file_path)
                return True # Evita que el navegador web parsee o descargue el archivo
        return super().eventFilter(source, event)

    def run_js(self, script):
        self.browser.page().runJavaScript(script)

    def toggle_theme(self):
        if self.current_theme == "light":
            self.current_theme = "dark"
            self.run_js("toggleDarkMode(true);")
        else:
            self.current_theme = "light"
            self.run_js("toggleDarkMode(false);")

    def start_processing(self, file_path):
        self.current_video_path = file_path
        
        # Pre-Flight Checks Ollama Health & Model
        model_name = self.backend.config.get("gemma_model_name")
        
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                if model_name not in models and f"{model_name}:latest" not in models:
                    safe_name = str(model_name).replace('\\', '\\\\').replace("'", "\\'")
                    self.run_js(f"updateLog('{datetime.now().strftime('%H:%M')}','❌ ERROR: El modelo {safe_name} no está instalado en tu servidor Ollama local.');")
                    return
            else:
                self.run_js(f"updateLog('{datetime.now().strftime('%H:%M')}','❌ ERROR: Ollama respondió con error en su API local.');")
                return
        except requests.exceptions.ConnectionError:
            self.run_js(f"updateLog('{datetime.now().strftime('%H:%M')}','❌ ERROR: Ollama no está ejecutándose. Ábrelo y vuelve a soltar el archivo.');")
            return

        safe_path = Path(file_path).name.replace('\\', '\\\\').replace("'", "\\'")
        self.run_js(f"updateLog('{datetime.now().strftime('%H:%M')}','Iniciando procesamiento de {safe_path}');")
        self.run_js("clearLogs();")
        
        self.thread = ProcessingThread(file_path)
        self.thread.progress_signal.connect(self.on_progress)
        self.thread.progress_pct_signal.connect(self.update_progress_pct)
        self.thread.finished_signal.connect(self.on_finished)
        self.thread.error_signal.connect(self.on_error)
        self.thread.stats_signal.connect(self.on_stats)
        self.thread.start()

    @pyqtSlot(int, str)
    def update_progress_pct(self, pct, label):
        self.run_js(f"updateProgress({pct}, '{label}')")

    def on_progress(self, message):
        safe_msg = message.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('\n',' ')
        self.run_js(f"updateLog('{datetime.now().strftime('%H:%M')}', '{safe_msg}');")

    def on_finished(self, summary):
        self.current_summary_md = summary
        safe_summary = summary.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
        self.run_js(f"setSummary(`{safe_summary}`);")
        
        # Generar PDF en el hilo nativo GUI (seguro)
        try:
            output_dir = Path(self.current_video_path).parent
            base_name = Path(self.current_video_path).stem
            pdf_file = output_dir / f"{base_name}_summary.pdf"
            
            from PyQt6.QtGui import QTextDocument, QPdfWriter
            doc = QTextDocument()
            doc.setMarkdown(summary)
            doc.setDefaultStyleSheet("body { font-family: Arial, sans-serif; font-size: 14pt; } h1 { color: #3F51B5; }")
            writer = QPdfWriter(str(pdf_file))
            doc.print(writer)
            
            self.on_progress(f"¡Proceso automatizado finalizado! Medios físicos guardados en: {output_dir}")
        except Exception as e:
            self.on_error(f"Error generando PDF final: {e}")
            
            
        self.run_js(f"updateLog('{datetime.now().strftime('%H:%M')}', '¡Todo listo!');")


    def on_error(self, error_message):
        safe_msg = error_message.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('\n',' ')
        self.run_js(f"updateLog('{datetime.now().strftime('%H:%M')}', '❌ ERROR: {safe_msg}');")

    def on_stats(self, stats):
        self.on_progress(f"Tokens consumidos: {stats['tokens']}")
        self.on_progress(f"Tiempo total: {stats['duration']}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
