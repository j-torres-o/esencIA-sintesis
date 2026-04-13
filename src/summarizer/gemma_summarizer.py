import os
import openai
from config import GEMMA_API_KEY
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

        self.api_key = api_key or GEMMA_API_KEY or "ollama"
        
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
            "Crea un resumen detallado de esta sesion, Con todos los parametros, recomendaciones, indicaciones. "
            "Eres un asistente experto en toma de notas y síntesis de información. "
            "La síntesis debe ser estructurada y profesional en formato Markdown. El resumen debe incluir:\n\n"
            "### 📌 Estructura del Resumen:\n"
            "1. **Título Descriptivo**: Un título (con #) que resuma claramente el tema principal.\n"
            "2. **Introducción**: Un breve párrafo que contextualice el contenido.\n"
            "3. **Puntos Clave**: Una lista con viñetas con los conceptos o ideas principales.\n"
            "4. **Desarrollo Detallado**: Organizado por subtítulos (##) según las temáticas o instrucciones dadas.\n"
            "5. **Conclusión/Cierre**: Un resumen claro de la conclusión.\n\n"
            "### 🛠️ Instrucciones de Estilo:\n"
            "- Utiliza un tono profesional.\n"
            "- Usa negritas (`**texto**`) para términos importantes.\n"
            "- Asegúrate de replicar todas las indicaciones, fechas o métricas textualmente.\n\n"
            "--- \n"
            "#### 📝 Transcripción para procesar:\n"
            f"{text}"
        )

        try:
            print(f"Generando resumen estructurado con {self.model_name}... (Longitud de transcripción: {len(text)} caracteres)")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Eres un analista de información y asistente de documentación."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
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
