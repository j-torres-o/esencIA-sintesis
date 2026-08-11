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
