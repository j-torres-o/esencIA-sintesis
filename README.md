# esencIA - Síntesis de Vídeo Académico (v0.2.0)

esencIA es una herramienta de escritorio potente y elegante diseñada para convertir vídeos académicos (clases, conferencias, seminarios) en notas estructuradas y resúmenes ejecutivos utilizando inteligencia artificial **100% local**.

![esencIA Logo](src/ui/assets/icon.png)

## 🚀 Características Principales

- **Transcripción Ultra-Rápida**: Utiliza `faster-whisper` (basado en CTranslate2) para transcribir audio a texto de forma eficiente, incluso en CPUs estándar.
- **IA Local (Privacidad Total)**: Integración con **Ollama** para generar resúmenes detallados usando modelos como `Gemma`, asegurando que tus datos nunca salgan de tu máquina.
- **Interfaz Moderna**: UI fluida y receptiva construida con PyQt6 y QWebEngine, con soporte para **Modo Oscuro** automático.
- **Detección de Entregables Académicos**: El motor de IA identifica automáticamente menciones a ensayos, tesis, proyectos o exámenes, generando una sección de detalles exhaustivos con requisitos y fechas.
- **Exportación Automática**: Genera de forma automática archivos Markdown (`.md`) y documentos **PDF** profesionales listos para estudiar.
- **Drag & Drop**: Arrastra tus archivos MP4 directamente a la interfaz para iniciar el procesamiento instantáneo.

## 🛠️ Requisitos Previos

Para que esencIA funcione correctamente, necesitas tener instalado:

1.  **Ollama**: [Descargar Ollama](https://ollama.com)
    -   Asegúrate de haber descargado el modelo configurado (por defecto: `gemma`).
    -   Comando: `ollama run gemma`
2.  **FFmpeg**: Necesario para la extracción de audio de los vídeos.

## 📦 Instalación y Uso

### Opción A: Ejecutable (Para Usuarios)
Si tienes el instalador (`esencIA_Setup.exe`):
1. Ejecuta el instalador.
2. Sigue los pasos del asistente.
3. Abre esencIA desde tu escritorio.

### Opción B: Desarrollo (Para Programadores)
1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/video_to_notes_app.git
   cd video_to_notes_app
   ```
2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configura tus variables de entorno:
   - Copia `.env.example` a `.env` y ajusta según sea necesario.
4. Ejecuta la aplicación:
   ```bash
   python run_app.py
   ```

## 🏗️ Estructura del Proyecto

- `src/`: Lógica principal de la aplicación.
  - `converter/`: Módulo de conversión Vídeo -> Audio.
  - `transcriber/`: Motor de transcripción basado en `faster-whisper`.
  - `summarizer/`: Conexión con la API local de Ollama.
  - `ui/`: Interfaz gráfica (HTML/JS/Python).
  - `utils/`: Gestores de configuración y recursos.
- `build_exe.ps1`: Script de automatización para generar el binario `.exe`.
- `esencIA.spec`: Configuración avanzada de PyInstaller.
- `esencia_installer.iss`: Script de Inno Setup para crear el instalador de Windows.

## 🛡️ Licencia
Este proyecto está bajo la Licencia **GNU GPL v3**. Consulta el archivo `LICENSE` para más detalles.

---
### 📝 Créditos y Agradecimientos
Este proyecto fue desarrollado con la asistencia del agente de IA **Antigravity** de Google DeepMind, utilizando modelos **Gemini** y **Gemma** para optimizar la estructura del código, la lógica académica y la interfaz de usuario.

---
*Desarrollado con ❤️ para facilitar el aprendizaje académico.*
