import os
import sys
from pathlib import Path

def get_resource_path(relative_path: str) -> str:
    """
    Obtiene la ruta absoluta a un recurso, compatible con el entorno de desarrollo
    y con el empaquetado de PyInstaller.
    
    PyInstaller crea una carpeta temporal en sys._MEIPASS para los datos incluidos
    con el flag --add-data.
    """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Si no estamos en un entorno empaquetado, usamos la raíz del proyecto
        # Asumimos que este archivo está en src/utils/resource_handler.py
        # Subimos dos niveles para llegar a la raíz (src/utils -> src -> raíz)
        # O mejor, usamos el directorio de ejecución actual o el padre de 'src'
        current_file_path = Path(__file__).resolve()
        # intentamos encontrar la carpeta 'src' y subir un nivel
        if "src" in current_file_path.parts:
            idx = current_file_path.parts.index("src")
            base_path = Path(*current_file_path.parts[:idx])
        else:
            base_path = Path(os.getcwd())

    return str((base_path / relative_path).resolve())
