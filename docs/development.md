# Guía de Desarrollo Local - esencIA

Esta guía describe cómo preparar el entorno de desarrollo para construir, depurar y empacar **esencIA**.

---

## 📋 Requisitos del Sistema

* **Python 3.10+** (Recomendado 3.10 o 3.11).
* **Ollama**: Servicio local de modelos de lenguaje. [Descargar Ollama](https://ollama.com).
* **FFmpeg**: Herramienta de procesamiento multimedia necesaria para la extracción de audio.
* **Inno Setup** *(opcional)*: Requerido solo si deseas generar el instalador ejecutable (`Setup.exe`).

---

## ⚙️ Pasos de Instalación

1. **Clonar e Instalar Dependencias**:
   ```powershell
   git clone https://github.com/tu-usuario/video_to_notes_app.git
   cd video_to_notes_app
   python -m venv venv
   .\venv\Scripts\activate
   pip install -e .[dev]
   ```

2. **Configuración de Ollama**:
   Verifica que Ollama esté corriendo e inicia el modelo configurado:
   ```powershell
   ollama pull gemma
   ollama run gemma
   ```

3. **Ejecución en Modo Desarrollo**:
   ```powershell
   python src/main.py
   ```

---

## 📦 Proceso de Compilación (PyInstaller)

Para generar la distribución binaria de Windows:

```powershell
.\scripts\build_exe.ps1
```

El binario resultante se guardará en `dist/esencIA/esencIA.exe`.
