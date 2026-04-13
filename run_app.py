import sys
import os
from pathlib import Path

# Configurar el path para que reconozca la carpeta src
src_path = Path(os.getcwd()) / 'src'
sys.path.append(str(src_path))

# Importar y lanzar la aplicación
from ui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())