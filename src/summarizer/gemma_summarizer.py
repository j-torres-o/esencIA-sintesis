import os
import openai
from utils.config_manager import ConfigManager

class GemmaSummarizer:
    """
    Clase encargada de generar resúmenes utilizando el modelo Gemma.
    """
    def __init__(self, api_key: str = None):
        """
        Inicializa el resumidor con la clave de API necesaria.
        
        Args:
            api_key (str): Clave de API para acceder al modelo Gemma.
        """
        config = ConfigManager()

        self.api_key = api_key or "ollama"
        
        # Configuración del cliente OpenAI compatible con Ollama/LM Studio
        self.client = openai.OpenAI(
            base_url=config.get("gemma_api_base_url"),
            api_key=self.api_key
        )
        # Obtener el nombre del modelo desde la configuración del usuario
        self.model_name = config.get("gemma_model_name")

    def summarize(self, text: str) -> tuple[str, int]:
        """
        Genera un resumen en formato Markdown a partir de un texto.
        
        Args:
            text (str): El texto transcrito que se desea resumir.
            
        Returns:
            tuple[str, int]: (resumen_markdown, tokens_usados)
            
        Raises:
            Exception: Si ocurre un error durante la llamada a la API.
        """
        if not text.strip():
            return "No se proporcionó texto para resumir.", 0

        prompt = (
            "Eres un analista de información de alta precisión especializado en síntesis académica. "
            "Crea un resumen EJECUTIVO y FIEL de esta sesión basándote EXCLUSIVAMENTE en la transcripción proporcionada. \n\n"
            "### 🛑 REGLAS ESTRICTAS DE FIDELIDAD:\n"
            "1. **SOLO usa la información del texto**: No agregues conocimientos externos ni suposiciones.\n"
            "2. **Proporcionalidad**: El resumen debe reflejar la densidad del contenido original.\n"
            "3. **Exactitud**: Mantén tecnicismos, cifras y nombres exactamente como se mencionan.\n\n"
            "### 🎓 DETECCIÓN DE ENTREGABLES ACADÉMICOS:\n"
            "Si en la transcripción se menciona la creación, requisitos o detalles de un entregable académico "
            "(ej: Ensayo, Artículo de investigación, Revisión de literatura, Estudio de caso, Abstract/Resumen, Tesis, Proyecto, etc.), "
            "DEBES crear una sección especial llamada '📌 Detalles del Entregable Académico' con información EXTRA DETALLADA sobre:\n"
            "- Tipo de entregable mencionado.\n"
            "- Requisitos específicos, estructura solicitada o fechas clave.\n"
            "- Instrucciones metodológicas o de formato (APA, Vancouver, etc.) si se mencionan.\n\n"
            "### 📌 Estructura General Requerida:\n"
            "1. **Título**: Breve y académico.\n"
            "2. **Puntos Clave**: Hechos o conceptos principales.\n"
            "3. **Sección de Entregables** (Solo si aplica): Detalles técnicos y exhaustivos del trabajo solicitado.\n"
            "4. **Desarrollo**: Subtemas diferenciados.\n"
            "5. **Conclusión**: Cierre basado únicamente en el texto.\n\n"
            "--- \n"
            "#### 📝 Transcripción para procesar:\n"
            f"{text}"
        )

        try:
            print(f"Generando resumen estructurado con {self.model_name}... (Longitud de transcripción: {len(text)} caracteres)")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Eres un asistente de documentación de alta precisión. Tu prioridad absoluta es la fidelidad al texto fuente. No agregas información externa."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                extra_body={
                    "options": {
                        "num_ctx": 131072
                    }
                }
            )
            summary_md = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            print("Resumen generado con éxito.")
            return summary_md, tokens_used
        except Exception as e:
            print(f"Error durante la generación del resumen: {e}")
            raise e

if __name__ == "__main__":
    # Prueba rápida de la clase
    # Nota: Requiere un servidor compatible con OpenAI API corriendo (ej. Ollama)
    try:
        summarizer = GemmaSummarizer()
        test_text = "Este es un texto de prueba para verificar que el resumidor funciona correctamente."
        print(summarizer.summarize(test_text))
    except Exception as e:
        print(f"Error en la prueba: {e}")
