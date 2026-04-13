import os
from PIL import Image
from pathlib import Path

def convert_png_to_ico(source_png: str, target_ico: str):
    """
    Convierte un archivo PNG en un archivo ICO con múltiples resoluciones
    para asegurar que se vea bien en todas las áreas de Windows.
    """
    if not os.path.exists(source_png):
        print(f"Error: No se encontró el archivo {source_png}")
        return

    print(f"Abriendo {source_png}...")
    img = Image.open(source_png)
    
    # Formatos de tamaño estándar para iconos de Windows
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # Guardar como ICO
    print(f"Generando {target_ico} con {len(icon_sizes)} tamaños...")
    img.save(target_ico, format='ICO', sizes=icon_sizes)
    print("¡Conversión completada con éxito!")

if __name__ == "__main__":
    # Rutas basadas en la estructura del proyecto
    base_dir = Path(__file__).parent.parent.resolve()
    source = base_dir / "ui" / "assets" / "icon.png"
    target = base_dir / "ui" / "assets" / "icon.ico"
    
    convert_png_to_ico(str(source), str(target))
