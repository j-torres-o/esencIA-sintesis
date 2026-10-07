import requests

from utils.config_manager import ConfigManager


class OllamaSummarizer:
    """
    Clase encargada de generar resúmenes utilizando la API REST directa de Ollama (HTTP POST /api/generate).
    Envía la transcripción completa en una sola solicitud HTTP estructurada con etiquetas XML.
    """
    def __init__(self, host: str = None):
        self.config = ConfigManager()

        base_url = host or self.config.get("gemma_api_base_url") or "http://localhost:11434"
        base_url = base_url.rstrip("/")
        if base_url.endswith("/v1"):
            base_url = base_url[:-3].rstrip("/")
        if base_url.endswith("/api"):
            base_url = base_url[:-4].rstrip("/")

        self.api_url = f"{base_url}/api/generate"
        self.model_name = self.config.get("gemma_model_name") or "gemma"

    def _clean_response(self, text: str) -> str:
        """Remueve etiquetas de razonamiento interno como <think>...</think> si el modelo las incluye."""
        if not text:
            return ""
        if "</think>" in text:
            return text.split("</think>")[-1].strip()
        return text.strip()

    def summarize(self, text: str) -> tuple[str, int]:
        """
        Genera un resumen en formato Markdown enviando la transcripción completa en una sola solicitud a /api/generate
        con delimitadores semánticos XML (<role>, <rules>, <detection_rules>, <output_structure>, <transcription>).
        
        Args:
            text (str): El texto transcrito que se desea resumir.
            
        Returns:
            tuple[str, int]: (resumen_markdown, tokens_usados)
        """
        if not text.strip():
            return "No se proporcionó texto para resumir.", 0

        prompt = (
            "<role>\n"
            "Eres un analista de información de alta precisión especializado en síntesis académica. "
            "Crea un resumen EJECUTIVO y FIEL de esta sesión basándote EXCLUSIVAMENTE en la transcripción proporcionada.\n"
            "</role>\n\n"
            "<rules>\n"
            "1. SOLO usa la información del texto: No agregues conocimientos externos ni suposiciones.\n"
            "2. Proporcionalidad: El resumen debe reflejar la densidad del contenido original.\n"
            "3. Exactitud: Mantén tecnicismos, cifras y nombres exactamente como se mencionan.\n"
            "</rules>\n\n"
            "<detection_rules>\n"
            "Si en la transcripción se menciona la creación, requisitos o detalles de un entregable académico "
            "(ej: Ensayo, Artículo de investigación, Revisión de literatura, Estudio de caso, Abstract/Resumen, Tesis, Proyecto, etc.), "
            "DEBES crear una sección especial llamada '📌 Detalles del Entregable Académico' con información EXTRA DETALLADA sobre:\n"
            "- Tipo de entregable mencionado.\n"
            "- Requisitos específicos, estructura solicitada o fechas clave.\n"
            "- Instrucciones metodológicas o de formato (APA, Vancouver, etc.) si se mencionan.\n"
            "</detection_rules>\n\n"
            "<output_structure>\n"
            "Genera el resumen directamente en formato Markdown siguiendo esta estructura estricta:\n"
            "1. **Título**: Breve y académico.\n"
            "2. **Puntos Clave**: Hechos o conceptos principales.\n"
            "3. **Sección de Entregables** (Solo si aplica): Detalles técnicos y exhaustivos del trabajo solicitado.\n"
            "4. **Desarrollo**: Subtemas diferenciados.\n"
            "5. **Conclusión**: Cierre basado únicamente en el texto.\n"
            "</output_structure>\n\n"
            "<transcription>\n"
            f"{text}\n"
            "</transcription>"
        )

        num_ctx = self.config.get("ollama_num_ctx") or 65536
        try:
            num_ctx = int(num_ctx)
        except (ValueError, TypeError):
            num_ctx = 65536

        payload = {
            "model": self.model_name.strip(),
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": num_ctx,
                "temperature": 0.2,
            },
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=900)
            response.raise_for_status()
        except requests.exceptions.ConnectionError as err:
            raise ConnectionError(
                f"No se pudo conectar al servidor local de Ollama en '{self.api_url}'. "
                "Asegúrate de que la aplicación Ollama esté abierta y ejecutándose."
            ) from err
        except requests.exceptions.Timeout as err:
            raise TimeoutError(
                f"La solicitud a Ollama para el modelo '{self.model_name}' excedió el tiempo límite (15 minutos)."
            ) from err
        except requests.exceptions.HTTPError as err:
            error_msg = response.text if "response" in locals() and response is not None else str(err)
            raise RuntimeError(f"Error devuelto por Ollama ({err.response.status_code}): {error_msg}") from err

        data = response.json()

        raw_text = data.get("response", "")
        summary_md = self._clean_response(raw_text)

        prompt_cnt = data.get("prompt_eval_count")
        eval_cnt = data.get("eval_count")

        prompt_cnt = prompt_cnt if isinstance(prompt_cnt, int) else 0
        eval_cnt = eval_cnt if isinstance(eval_cnt, int) else 0

        tokens_used = prompt_cnt + eval_cnt

        return summary_md, tokens_used


# Alias de retrocompatibilidad
GemmaSummarizer = OllamaSummarizer
