import sys
import os
import ctypes
from pathlib import Path

# Fix for imports when running as a module or script
src_path = Path(__file__).parent.resolve()
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from ui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication

def main():
    # Fix for taskbar icon in Windows (AppUserModelID)
    try:
        # Use a unique ID for the application
        myappid = 'com.esencia.video-to-notes.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
