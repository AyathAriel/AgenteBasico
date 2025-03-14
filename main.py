from typing import Dict, Any, List
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import Graph, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import datetime
import platform
import psutil
import os


load_dotenv()

def show_menu():
    """Muestra el menú de opciones disponibles"""
    print("\n=== Menú de Opciones ===")
    print("1. Comandos del Sistema:")
    print("   1.1 - Información del sistema")
    print("   1.2 - Hora actual")
    print("   1.3 - Uso de memoria RAM")
    print("\n2. Interacción con ChatGPT:")
    print("   2.1 - Hacer una pregunta general")
    print("   2.2 - Iniciar conversación natural")
    print("   2.3 - Ver última respuesta")
    print("\n3. Utilidades:")
    print("   3.1 - Ver historial de comandos")
    print("   3.2 - Limpiar pantalla")
    print("   3.3 - Mostrar este menú")
    print("\n0. Salir")
    print("=====================")

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
        return f"Sistema: {system}, Versión: {version}, Arquitectura: {machine}"

class TimeTool(BaseTool):
    name: str = "get_time"
    description: str = "Obtiene la hora actual"

    def _run(self) -> str:
        return datetime.datetime.now().strftime("%H:%M:%S")

class MemoryUsageTool(BaseTool):
    name: str = "memory_usage"
    description: str = "Obtiene el uso de memoria del sistema"

    def _run(self) -> str:
        memory = psutil.virtual_memory()
        return f"Memoria total: {memory.total/1024/1024/1024:.1f}GB, Usada: {memory.percent}%"

class AskGPTTool(BaseTool):
    name: str = "ask_gpt"
    description: str = "Pregunta algo a ChatGPT"

    def _run(self, query: str) -> str:
        try:
            messages = [HumanMessage(content=query)]
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            error_msg = str(e)
            if "insufficient_quota" in error_msg:
                return "Error: Has excedido tu cuota de OpenAI. Por favor, verifica tu saldo."
            elif "invalid_api_key" in error_msg:
                return "Error: La API key no es válida. Por favor, verifica tu configuración."
            else:
                return f"Error al consultar ChatGPT: {error_msg}"


tools = [
    SystemInfoTool(),
    TimeTool(),
    MemoryUsageTool(),
    AskGPTTool()
]

def process_command(command: str, option: str = None) -> str:
    """Procesa comandos básicos y devuelve resultados"""
    if option == "1.1":
        return tools[0]._run()
    elif option == "1.2":
        return tools[1]._run()
    elif option == "1.3":
        return tools[2]._run()
    elif option in ["2.1", "2.2"]:
        return tools[3]._run(command)
    else:
        # Procesar comando directo
        command = command.lower()
        if "sistema" in command or "info" in command:
            return tools[0]._run()
        elif "hora" in command or "tiempo" in command:
            return tools[1]._run()
        elif "memoria" in command or "ram" in command:
            return tools[2]._run()
        else:
            return tools[3]._run(command)

def agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Función principal del agente"""
    

    current_input = state["input"]
    current_option = state.get("option", None)
    

    response = process_command(current_input, current_option)
    

    history = state.get("history", [])
    history.append({
        "command": current_input,
        "option": current_option,
        "response": response
    })
    
    return {
        "history": history,
        "output": response,
        "last_option": current_option
    }

def create_agent_graph() -> Graph:
    """Crea el grafo del agente"""
    workflow = Graph()
    workflow.add_node("agent", agent)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)
    return workflow.compile()

def show_history(history):
    """Muestra el historial de comandos"""
    print("\n=== Historial de Comandos ===")
    for i, entry in enumerate(history, 1):
        print(f"\n{i}. Comando: {entry['command']}")
        if entry.get('option'):
            print(f"   Opción: {entry['option']}")
        print(f"   Respuesta: {entry['response']}")
    print("===========================")

def run_agent():
    """Ejecuta el agente"""
    
    # Crear el grafo
    agent_graph = create_agent_graph()
    
    # Estado inicial
    state = {
        "history": [],
        "input": "",
        "output": "",
        "option": None
    }
    
    print("\n=== Agente Básico con OpenAI ===")
    show_menu()
    
    while True:
        try:
            # Obtener opción del usuario
            option = input("\nIngrese una opción (3.3 para ver menú): ").strip()
            
            # Procesar opciones especiales
            if option == "0":
                print("\nAgente: ¡Hasta pronto!")
                break
            elif option == "3.1":
                show_history(state["history"])
                continue
            elif option == "3.2":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            elif option == "3.3":
                show_menu()
                continue
            
            # Obtener comando/pregunta del usuario
            if option.startswith("2"):
                prompt = "Pregunta: "
            else:
                prompt = "Comando: "
            
            command = input(prompt).strip()
            
            # Verificar comando vacío
            if not command:
                print("\nAgente: Por favor, ingrese un comando o pregunta.")
                continue
            
            # Actualizar estado
            state["input"] = command
            state["option"] = option
            
            # Ejecutar agente
            result = agent_graph.invoke(state)
            
            # Actualizar estado
            state = result
            
            # Mostrar resultado
            print("\nResultado:", result["output"])
            
        except KeyboardInterrupt:
            print("\n\nAgente: Ejecución interrumpida.")
            break
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Por favor, intenta de nuevo.")
            continue

if __name__ == "__main__":
    run_agent()
