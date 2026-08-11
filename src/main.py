import ctypes
import sys
from pathlib import Path

# Ensure src path is in sys.path
src_path = Path(__file__).parent.resolve()
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from PyQt6.QtWidgets import QApplication  # noqa: E402

from ui.main_window import MainWindow  # noqa: E402
from version import APP_ID, APP_NAME, __version__  # noqa: E402


def main():
    # Set explicit AppUserModelID for Windows taskbar grouping and icon rendering
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(__version__)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
