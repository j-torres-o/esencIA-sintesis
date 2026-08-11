# Guía de Contribución para esencIA (video_to_notes_app)

¡Gracias por tu interés en contribuir a **esencIA**! Este documento proporciona pautas y estándares para el desarrollo del proyecto.

---

## 🛠️ Configuración del Entorno de Desarrollo

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/video_to_notes_app.git
   cd video_to_notes_app
   ```

2. **Crear y activar un entorno virtual**:
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Linux/macOS:
   source venv/bin/activate
   ```

3. **Instalar dependencias en modo editable**:
   ```bash
   pip install -e .[dev]
   ```

---

## 📏 Estándares de Código y Calidad

El proyecto utiliza `pyproject.toml` para mantener un estilo de código consistente.

* **Linters**:
  ```bash
  ruff check src tests
  ```

* **Formateador**:
  ```bash
  black --check src tests
  ```

* **Pruebas Unitarias**:
  ```bash
  pytest
  ```

---

## 🔀 Flujo de Trabajo con Git

1. Crea una rama (`branch`) descriptiva para tu característica o corrección:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
2. Asegúrate de que las pruebas unitarias y linters pasen sin errores.
3. Realiza commits con mensajes claros e informativos.
4. Abre un Pull Request (PR) hacia la rama `main`.

---

## 📋 Licencia
Al contribuir, aceptas que tus aportes estarán bajo la Licencia **GNU GPL v3**.
