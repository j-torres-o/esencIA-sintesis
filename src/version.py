"""Single Source of Truth for esencIA Application Version & Metadata."""

__version__ = "0.2.1"
APP_NAME = "esencIA"
APP_DESCRIPTION = "Síntesis de Vídeo Académico local usando Ollama y Whisper"
APP_AUTHOR = "esencIA Team"
APP_ID = "com.esencia.video-to-notes.v1"
LICENSE = "GNU GPL v3"


def get_version_info() -> dict[str, str]:
    """Return dictionary with application version and metadata."""
    return {
        "name": APP_NAME,
        "version": __version__,
        "description": APP_DESCRIPTION,
        "author": APP_AUTHOR,
        "app_id": APP_ID,
        "license": LICENSE,
    }
