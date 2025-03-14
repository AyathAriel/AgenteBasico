from typing import Dict, Any, List
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import datetime
import platform
import psutil
import os

# Cargar variables de entorno
load_dotenv()

def check_openai_api_key():
    """Verifica que la API key de OpenAI esté configurada"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "\n❌ No se encontró la API key de OpenAI. Por favor:\n"
            "1. Ve a https://platform.openai.com/api-keys\n"
            "2. Crea una API key si no tienes una\n"
            "3. Crea un archivo .env en el directorio del proyecto\n"
            "4. Añade tu API key así: OPENAI_API_KEY=tu-api-key\n"
        )
    return api_key

# Configurar el modelo de OpenAI
try:
    api_key = check_openai_api_key()
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        api_key=api_key
    )
    # Verificar la conexión con una pregunta de prueba
    test_message = [HumanMessage(content="Hola, ¿estás funcionando?")]
    test_response = llm.invoke(test_message)
    print("\n✅ Conexión con OpenAI establecida correctamente!")
except ValueError as ve:
    print(f"\n❌ Error de configuración: {str(ve)}")
    exit(1)
except Exception as e:
    print(f"\n❌ Error al conectar con OpenAI: {str(e)}")
    print("Asegúrate de:")
    print("1. Tener una API key válida")
    print("2. Tener saldo disponible en tu cuenta")
    print("3. Tener una conexión a internet estable")
    exit(1)

class SystemInfoTool(BaseTool):
    name: str = "system_info"
    description: str = "Obtiene información del sistema"

    def _run(self) -> str:
        system = platform.system()
        version = platform.version()
        machine = platform.machine()
        return f"Tu sistema es {system} {version} en arquitectura {machine}"

class TimeTool(BaseTool):
    name: str = "get_time"
    description: str = "Obtiene la hora actual"

    def _run(self) -> str:
        return f"Son las {datetime.datetime.now().strftime('%H:%M:%S')}"

class MemoryUsageTool(BaseTool):
    name: str = "memory_usage"
    description: str = "Obtiene el uso de memoria del sistema"

    def _run(self) -> str:
        memory = psutil.virtual_memory()
        return f"Tu computadora tiene {memory.total/1024/1024/1024:.1f}GB de RAM y está usando el {memory.percent}%"

class AskGPTTool(BaseTool):
    name: str = "ask_gpt"
    description: str = "Consulta a ChatGPT para responder preguntas generales"

    def _run(self, query: str) -> str:
        try:
            messages = [HumanMessage(content=query)]
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            error_msg = str(e)
            if "insufficient_quota" in error_msg:
                return "Lo siento, he excedido mi cuota de uso. ¿Podrías intentarlo más tarde?"
            elif "invalid_api_key" in error_msg:
                return "Parece que hay un problema con mi configuración. ¿Podrías verificar la API key?"
            else:
                return "Lo siento, tuve un problema al procesar tu pregunta. ¿Podrías intentarlo de nuevo?"

def analyze_intent(message: str) -> tuple:
    """Analiza el mensaje del usuario para determinar la intención"""
    message = message.lower()
    
    # Patrones para reconocer intenciones
    system_patterns = ["sistema", "computadora", "pc", "ordenador", "información", "specs", "especificaciones"]
    time_patterns = ["hora", "tiempo", "actual", "reloj", "que hora"]
    memory_patterns = ["memoria", "ram", "almacenamiento", "espacio"]
    
    # Verificar intenciones específicas
    if any(pattern in message for pattern in system_patterns):
        return "system_info", None
    elif any(pattern in message for pattern in time_patterns):
        return "get_time", None
    elif any(pattern in message for pattern in memory_patterns):
        return "memory_usage", None
    else:
        return "ask_gpt", message

def get_welcome_message() -> str:
    return """
¡Hola! Soy tu asistente virtual. 👋

Puedo ayudarte con información sobre tu computadora, decirte la hora,
revisar el uso de memoria y responder cualquier otra pregunta que tengas.

¿En qué puedo ayudarte hoy?

(Para salir, escribe 'salir' o 'exit')
"""

def run_assistant():
    """Ejecuta el asistente virtual"""
    
    # Crear herramientas
    tools = [
        SystemInfoTool(),
        TimeTool(),
        MemoryUsageTool(),
        AskGPTTool()
    ]
    
    # Mapear herramientas
    tool_map = {tool.name: tool for tool in tools}
    
    print("\n=== Asistente Virtual ===")
    print(get_welcome_message())
    
    while True:
        try:
            # Obtener mensaje del usuario
            message = input("\nTú: ").strip()
            
            # Verificar si el usuario quiere salir
            if message.lower() in ['salir', 'exit', 'quit']:
                print("\nAsistente: ¡Hasta pronto! 👋")
                break
            
            # Verificar mensaje vacío
            if not message:
                print("\nAsistente: Por favor, dime en qué puedo ayudarte.")
                continue
            
            # Analizar la intención del mensaje
            tool_type, query = analyze_intent(message)
            
            # Obtener respuesta
            try:
                if tool_type == "ask_gpt":
                    response = tool_map[tool_type]._run(message)
                else:
                    response = tool_map[tool_type]._run()
                print("\nAsistente:", response)
            except Exception as e:
                print("\nAsistente: Lo siento, no pude procesar tu solicitud correctamente.")
                print("¿Podrías intentar preguntarlo de otra manera?")
            
        except KeyboardInterrupt:
            print("\n\nAsistente: ¡Hasta pronto! 👋")
            break
        except Exception as e:
            print(f"\nAsistente: Ups, algo salió mal: {str(e)}")
            print("¿Podrías intentarlo de nuevo?")

if __name__ == "__main__":
    run_assistant()
