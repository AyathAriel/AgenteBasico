from typing import Dict, Any
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import Graph, END
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
    print("\n✅ Asistente listo para ayudarte!")
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
            messages = [
                SystemMessage(content="Eres un asistente amigable y servicial. Proporciona respuestas claras y útiles."),
                HumanMessage(content=query)
            ]
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

def analyze_intent(message: str) -> str:
    """Analiza el mensaje del usuario para determinar la herramienta a usar"""
    message = message.lower()
    
    if any(word in message for word in ["sistema", "computadora", "pc", "ordenador", "specs"]):
        return "system_info"
    elif any(word in message for word in ["hora", "tiempo", "reloj"]):
        return "get_time"
    elif any(word in message for word in ["memoria", "ram"]):
        return "memory_usage"
    return "ask_gpt"

def process_message(state: Dict[str, Any]) -> Dict[str, Any]:
    """Procesa el mensaje del usuario y genera una respuesta"""
    message = state["current_input"]
    tools = state["tools"]
    tool_map = {tool.name: tool for tool in tools}
    
    try:
        tool_name = analyze_intent(message)
        
        if tool_name == "ask_gpt":
            response = tool_map[tool_name]._run(message)
        else:
            response = tool_map[tool_name]._run()
            
        state["current_response"] = response
        
    except Exception as e:
        state["current_response"] = "Lo siento, tuve un problema al procesar tu mensaje. ¿Podrías intentarlo de nuevo?"
    
    return state

def create_chat_workflow() -> Graph:
    """Crea el flujo de trabajo del chat usando LangGraph"""
    workflow = Graph()
    
    # Agregar nodo de procesamiento
    workflow.add_node("process", process_message)
    
    # Definir el flujo
    workflow.set_entry_point("process")
    workflow.add_edge("process", END)
    
    return workflow.compile()

def run_assistant():
    """Ejecuta el asistente virtual"""
    
    # Crear herramientas
    tools = [
        SystemInfoTool(),
        TimeTool(),
        MemoryUsageTool(),
        AskGPTTool()
    ]
    
    # Crear el flujo de trabajo
    workflow = create_chat_workflow()
    
    # Estado inicial
    state = {
        "tools": tools,
        "current_input": "",
        "current_response": None
    }
    
    print("\n👋 ¡Hola! Soy tu asistente virtual.")
    print("Puedes preguntarme cualquier cosa y haré lo mejor para ayudarte.")
    print("Para salir, escribe 'salir' o presiona Ctrl+C")
    
    while True:
        try:
            message = input("\nTú: ").strip()
            
            if message.lower() in ['salir', 'exit', 'quit']:
                print("\nAsistente: ¡Hasta pronto! 👋")
                break
                
            if not message:
                print("\nAsistente: Por favor, dime algo.")
                continue
                
            # Actualizar estado con el mensaje actual
            state["current_input"] = message
            
            # Procesar mensaje
            result = workflow.invoke(state)
            
            # Mostrar respuesta
            print("\nAsistente:", result["current_response"])
            
            # Actualizar estado
            state = result
            
        except KeyboardInterrupt:
            print("\n\nAsistente: ¡Hasta pronto! 👋")
            break
        except Exception as e:
            print(f"\nAsistente: Ups, algo salió mal: {str(e)}")
            print("¿Podrías intentarlo de nuevo?")

if __name__ == "__main__":
    run_assistant()
