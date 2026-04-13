# Plan de Trabajo: Video to Notes App

Este documento sirve como punto de recuperación para el agente de IA. Contiene el progreso actual y las tareas pendientes para el desarrollo de la aplicación.

## 📌 Descripción del Proyecto
Aplicación de escritorio en Python para convertir videos MP4 en archivos MP3 y generar resúmenes detallados en Markdown utilizando el modelo Gemma (local) y Whisper (transcripción local).

## 🚀 Estado Actual
- **Arquitectura**: Estructura de carpetas definida (Separación de responsabilidades: `converter`, `summarizer`, `ui`, `transcriber`).
- **Tecnologías**: Python, MoviePy (conversión), OpenAI-Whisper (transcripción), OpenAI SDK (para Gemma local), PyQt6 (UI).
- **Configuración**: Archivos `.env` y `config.py` preparados para gestión de variables de entorno.

## 🛠️ Progreso por Etapas

### Etapa 1: Infraestructura y Configuración (✅ COMPLETADO)
- [x] Planificación de la estructura del proyecto.
- [x] Creación de la estructura de carpet 
- [x] Configuración de dependencias (`requirements.txt`).
- [x] Configuración de entorno (`.env`, `config.py`).

### Etapa 2: Lógica de Procesamiento (✅ COMPLETADO)
- [x] **Módulo Converter**: Implementación de `VideoConverter` (MP4 $\rightarrow$ MP3) usando MoviePy.
- [x] **Módulo Transcriber**: Implementación de `AudioTranscriber` (MP3 $\rightarrow$ Texto) usando Whisper.
- [x] **Módulo Summarizer**: Implementación de `GemmaSummarizer` (Texto $\rightarrow$ Markdown) usando Gemma vía API compatible (Ollama/LM Studio).

### Etapa 3: Interfaz de Usuario (✅ COMPLETADO)
- [x] Desarrollo de la GUI con **PyQt6**.
- [x] Implementación de funcionalidad **Drag-and-Drop** para archivos MP4.
- [x] Barra de progreso para los procesos de conversión y transcripción.
- [x] Visualización del resumen generado en la interfaz.

### Etapa 4: Gestión de Archivos y Salida (✅ COMPLETADO)
- [x] Implementación de la lógica para guardar el archivo `.mp3`.
- [x] Implementación de la lógica para guardar el resumen en `.md`.
- [x] Gestión de la carpeta `outputs/` con nombres de archivo descriptivos y timestamps.
- [x] Configuración del directorio de salida mediante variables de entorno.

### Etapa 5: Pruebas y Refinamiento (❌ EN PROGRESO)
- [X] Pruebas unitarias para cada módulo.
- [X] Refinamiento del prompt de Gemma para asegurar la calidad del Markdown.
- [ ] Empaquetado de la aplicación (opcional).

## 📝 Notas para el Agente
Si retomas este proyecto, lee primero el `src/main.py` para entender el flujo principal y revisa los módulos en `src/` para verificar la lógica de cada componente.
