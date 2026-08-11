# Arquitectura del Sistema - esencIA

Este documento detalla la estructura lógica, los componentes principales y el flujo de datos de la aplicación **esencIA**.

---

## 🏗️ Vista General de Componentes y Flujo de Checkpoints

```mermaid
graph TD
    Input["Entrada: C:/Ruta/Del/Usuario/video.mp4"] --> CheckMP3{"¿Existe video.mp3?"}
    
    CheckMP3 -- "No" --> Converter["VideoConverter (MP4 -> MP3)"]
    CheckMP3 -- "Sí (Omitir)" --> CheckTXT{"¿Existe video_transcription.txt?"}
    Converter --> CheckTXT
    
    CheckTXT -- "No" --> Transcriber["AudioTranscriber (Whisper con 1 Auto-Retry)"]
    CheckTXT -- "Sí (Omitir)" --> CheckMD{"¿Existe video_summary.md?"}
    Transcriber --> CheckMD
    
    CheckMD -- "No" --> Summarizer["GemmaSummarizer (Ollama con 1 Auto-Retry)"]
    CheckMD -- "Sí (Omitir)" --> Exporter["Export Engine (PDF)"]
    Summarizer --> Exporter
```

---

## 🧩 Descripción de Módulos

### 1. `src/version.py`
Contiene la fuente única de verdad para los metadatos de la aplicación (nombre, versión, identificador de Windows, autor y licencia).

### 2. `src/ui/main_window.py` (`ProcessingThread`)
Gestiona el hilo secundario asíncrono para el procesamiento sin congelar la UI.
- **Puntos de Control (Checkpoints)**: Evalúa la existencia de archivos intermedios (`.mp3`, `_transcription.txt`, `_summary.md`) en la **misma carpeta del vídeo del usuario** (`video_path.parent`) para reanudar trabajos en 0 segundos.
- **Reintentos Automáticos (Auto-Retry)**: Ejecuta 1 reintento transparente ante excepciones o fallas temporales de modelo/GPU.

### 3. `src/converter/video_converter.py`
Extrae el audio de archivos de vídeo MP4 y genera archivos de audio optimizados en formato MP3 con reporte de progreso mediante callbacks.

### 4. `src/transcriber/audio_transcriber.py`
Procesa el archivo MP3 mediante el motor CTranslate2 (`faster-whisper`), aplicando filtro VAD (*Voice Activity Detection*) para eliminar silencios y alucinaciones.

### 5. `src/summarizer/gemma_summarizer.py`
Se conecta a la API local compatible con OpenAI expuesta por Ollama. Aplica un prompt estructurado de alta fidelidad para extraer resúmenes académicos y detectar entregables (ensayos, tesis, fechas).

---

## 🛠️ Herramientas y Empaquetado

- **`pyproject.toml`**: Configuración unificada para `pytest`, `ruff` y `black`, resolviendo dinámicamente la versión desde `src/version.py`.
- **`scripts/build_exe.ps1`**: Script de PowerShell para compilar la aplicación a través de PyInstaller y generar el paquete distribuible.
