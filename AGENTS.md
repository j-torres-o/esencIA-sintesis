# AGENTS.md

Guía y reglas de arquitectura para agentes de IA que trabajan en la base de código de **esencIA (video_to_notes_app)**.

## 🚀 Comandos de Construcción y Prueba

### Ejecutar Pruebas Unitarias
```powershell
pytest
```

### Ejecutar Linters
```powershell
ruff check src tests
```

### Probar Ejecución Local de la App
```powershell
python src/main.py
```

### Generar Ejecutable para Windows
```powershell
.\scripts\build_exe.ps1
```

---

## 🏛️ Reglas Arquitectónicas y de Flujo de Trabajo

1. **Privacidad Local Ante Todo**: Toda la inferencia de LLM y transcripción debe ejecutarse en local vía Ollama y `faster-whisper`. Nunca agregar llamadas remotas por defecto.
2. **Fuente Única de Verdad de Versión**: La versión de la aplicación y metadatos residen exclusivamente en [src/version.py](file:///c:/Projects/video_to_notes_app/src/version.py). Seguir el estándar **Semantic Versioning** (`MAJOR.MINOR.PATCH`).
3. **Manejo de Excepciones**: No usar bloques `try...except` vacíos con `pass`. Capturar y registrar las excepciones o propagarlas adecuadamente.
4. **UI Decoupling**: La interfaz gráfica (`src/ui/`) se comunica con el backend mediante señales o callbacks asíncronos para no congelar el hilo principal de PyQt6.
5. **Flujo de Git y Manejo de Ramas (Git Flow)**:
   - **NUNCA realizar commits directamente sobre la rama `main`**.
   - Crear siempre una rama temática (*feature/bugfix/refactor branch*), por ejemplo: `feat/nombre-funcionalidad`, `fix/correccion-bug`, `refactor/mejora-estrucutral`.
   - Utilizar mensajes de commit bajo la especificación **Conventional Commits** (`feat:`, `fix:`, `refactor:`, `style:`, `test:`, `ci:`, `docs:`, `build:`).
   - Preparar las ramas para su integración hacia `main` mediante **Pull Requests (PR)** sometidos a verificación CI/CD.
6. **Estrategia Profesional de Versionamiento y Releases**:
   - **Flujo de Integración Cotidiana**:
     - Las ramas temáticas (`feat/`, `fix/`, `refactor/`) se fusionan a `main` mediante PR con CI en verde.
     - **NO** es obligatorio incrementar la versión ni publicar una Release por cada PR individual o corrección menor.
   - **Criterios para una Release Oficial en GitHub**:
     - Se publica una Release únicamente al completar un **Hito Significativo (Milestone)** que aporte valor tangible (ej. nuevas funcionalidades integradas, mejoras acumuladas de UX/rendimiento) o un lote consolidado de correcciones críticas (`PATCH`).
     - **Semantic Versioning (`MAJOR.MINOR.PATCH`)**:
       - `PATCH` (ej. `v0.4.0` -> `v0.4.1`): Lote de correcciones de estabilidad y bugs.
       - `MINOR` (ej. `v0.4.0` -> `v0.5.0`): Hito con nuevas características (ej. nuevos motores ASR, rediseño, refactors mayores).
       - `MAJOR`: Cambios disruptivos o arquitectónicos completos.
     - **Empaquetado Obligatorio**: Toda Release en GitHub debe incluir el binario instalador compilado para Windows (`.\scripts\build_exe.ps1`) y notas de versión detalladas (*Release Notes*).
   - **Procedimiento de Corte de Release**:
     1. Crear rama `chore/release-vX.Y.Z`.
     2. Actualizar versión en [src/version.py](file:///c:/Projects/video_to_notes_app/src/version.py) y registrar notas de cambios.
     3. Fusionar a `main` tras pasar CI.
     4. Generar el instalador `.exe` y publicar la Release oficial en GitHub.
