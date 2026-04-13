r"""
config_manager.py
-----------------
Gestor de configuración de usuario centralizado para SintesisVideo.

Las preferencias se almacenan en un archivo JSON dentro del directorio
estándar de datos de la aplicación del sistema operativo:
  - Windows : %APPDATA%\SintesisVideo\config.json
  - macOS   : ~/Library/Application Support/SintesisVideo/config.json
  - Linux   : ~/.config/SintesisVideo/config.json

Las claves de API y secretos se mantienen en el archivo .env del proyecto.
"""

import json
import os
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Valores por defecto de la aplicación
DEFAULT_CONFIG: dict = {
    "theme_preference": "system",          # "light" | "dark" | "system"
    "gemma_model_name": "gemma",           # Nombre del modelo Ollama activo
    "gemma_api_base_url": "http://localhost:11434/v1",  # URL base de la API
}


def _get_app_data_dir() -> Path:
    """
    Retorna el directorio estándar de datos de usuario según el SO.
    Crea el directorio si no existe.
    """
    app_name = "SintesisVideo"

    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        # Linux / Unix: respetar XDG_CONFIG_HOME si existe
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    app_dir = base / app_name
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


class ConfigManager:
    """
    Clase singleton para gestionar la configuración persistente del usuario.
    Uso:
        config = ConfigManager()
        theme = config.get("theme_preference")
        config.set("gemma_model_name", "llama3")
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._config_path = _get_app_data_dir() / "config.json"
        self._data: dict = {}
        self._load()

    # ------------------------------------------------------------------
    # Propiedades públicas
    # ------------------------------------------------------------------

    @property
    def config_path(self) -> Path:
        """Ruta completa al archivo de configuración en disco."""
        return self._config_path

    # ------------------------------------------------------------------
    # Interfaz pública
    # ------------------------------------------------------------------

    def get(self, key: str, fallback=None):
        """
        Retorna el valor de una clave de configuración.
        Si la clave no existe, usa el valor por defecto de DEFAULT_CONFIG
        y, si tampoco existe ahí, retorna `fallback`.
        """
        return self._data.get(key, DEFAULT_CONFIG.get(key, fallback))

    def set(self, key: str, value) -> None:
        """
        Actualiza una clave de configuración y guarda inmediatamente en disco.
        """
        self._data[key] = value
        self._save()

    def get_all(self) -> dict:
        """Retorna una copia de toda la configuración activa."""
        merged = {**DEFAULT_CONFIG, **self._data}
        return dict(merged)

    def reset_to_defaults(self) -> None:
        """Restaura todas las configuraciones a sus valores por defecto y guarda."""
        self._data = dict(DEFAULT_CONFIG)
        self._save()
        logger.info("Configuración restablecida a valores por defecto.")

    # ------------------------------------------------------------------
    # Métodos privados
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """
        Carga la configuración desde el archivo JSON.
        Si el archivo no existe o está corrupto, usa los valores por defecto.
        """
        if not self._config_path.exists():
            logger.info("Archivo de configuración no encontrado. Se usarán valores por defecto.")
            self._data = {}
            return

        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if not isinstance(loaded, dict):
                raise ValueError("El archivo de configuración no contiene un objeto JSON válido.")
            self._data = loaded
            logger.info(f"Configuración cargada desde: {self._config_path}")
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Configuración corrupta ({e}). Se restaurarán los valores por defecto.")
            self._data = {}
            # Sobreescribir el archivo dañado con los defaults para repararlo
            self._save()

    def _save(self) -> None:
        """Guarda la configuración actual en el archivo JSON de forma atómica."""
        tmp_path = self._config_path.with_suffix(".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)
            tmp_path.replace(self._config_path)
            logger.debug(f"Configuración guardada en: {self._config_path}")
        except OSError as e:
            logger.error(f"No se pudo guardar la configuración: {e}")
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
