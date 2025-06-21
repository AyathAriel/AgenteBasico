from typing import Dict, Any, List, Optional
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import Graph, END
from dotenv import load_dotenv
import datetime
import platform
import psutil
import os
import json
import math
import hashlib
from mcp_qdrant_wrapper import MCPQdrantWrapper, DynamicContextManager

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
        api_key=api_key,
        max_tokens=2000
    )
    print("✅ Modelo OpenAI configurado correctamente")
except ValueError as ve:
    print(f"❌ Error de configuración: {str(ve)}")
    exit(1)
except Exception as e:
    print(f"❌ Error al conectar con OpenAI: {str(e)}")
    exit(1)

# Instancias globales para evitar problemas con Pydantic
mcp_wrapper = MCPQdrantWrapper()
context_manager = DynamicContextManager()

class DynamicVectorMemoryTool(BaseTool):
    """Herramienta de memoria vectorial completamente dinámica usando MCP"""
    name: str = "vector_memory"
    description: str = "Interactúa con la base de datos vectorial MCP de Qdrant dinámicamente"

    def _run(self, action: str, query: str = "", content: str = "", metadata: dict = None) -> str:
        try:
            if action == "store":
                if not content:
                    return context_manager.get_response_template("error")
                return mcp_wrapper.store_vector(content, metadata)
            
            elif action == "search":
                if not query:
                    return "❌ Consulta requerida para buscar"
                return mcp_wrapper.search_vectors(query)
            
            elif action == "stats":
                return mcp_wrapper.get_stats()
            
            else:
                return "❌ Acción no válida. Usa: store, search, stats"
                
        except Exception as e:
            return f"❌ Error en base de datos vectorial: {str(e)}"

class DynamicSystemInfoTool(BaseTool):
    """Herramienta de información del sistema completamente dinámica"""
    name: str = "system_info"
    description: str = "Obtiene información del sistema y la almacena dinámicamente"

    def _run(self) -> str:
        try:
            # Obtener información del sistema dinámicamente
            system_info = {
                "sistema": platform.system(),
                "version": platform.version(),
                "arquitectura": platform.machine(),
                "procesador": platform.processor(),
                "python": platform.python_version(),
                "memoria_total": f"{psutil.virtual_memory().total/1024**3:.1f}GB",
                "memoria_uso": f"{psutil.virtual_memory().percent}%",
                "disco_total": f"{psutil.disk_usage('/').total/1024**3:.1f}GB",
                "disco_uso": f"{psutil.disk_usage('/').percent}%",
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Almacenar en base de datos vectorial
            store_result = mcp_wrapper.store_vector(
                content=json.dumps(system_info), 
                metadata={"type": "system_info", "auto_generated": True}
            )
            
            # Formatear respuesta dinámicamente
            response = f"""🖥️  INFORMACIÓN DEL SISTEMA:

Sistema: {system_info['sistema']} {system_info['version']}
Arquitectura: {system_info['arquitectura']}
Procesador: {system_info['procesador']}
Python: {system_info['python']}
RAM Total: {system_info['memoria_total']}
RAM Usada: {system_info['memoria_uso']}
Disco Total: {system_info['disco_total']}
Disco Usado: {system_info['disco_uso']}

📊 {store_result}"""
            
            return response
            
        except Exception as e:
            return f"❌ Error obteniendo información del sistema: {str(e)}"

class DynamicCalculatorTool(BaseTool):
    """Calculadora completamente dinámica con almacenamiento vectorial"""
    name: str = "calculator"
    description: str = "Realiza cálculos y almacena resultados dinámicamente"

    def _run(self, expression: str) -> str:
        try:
            # Funciones matemáticas cargadas dinámicamente
            math_functions = {
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'sqrt': math.sqrt, 'log': math.log, 'log10': math.log10,
                'exp': math.exp, 'pow': math.pow, 'abs': abs,
                'pi': math.pi, 'e': math.e, 'factorial': math.factorial,
                'ceil': math.ceil, 'floor': math.floor, 'round': round
            }
            
            # Entorno seguro dinámico
            safe_dict = {"__builtins__": {}}
            safe_dict.update(math_functions)
            
            result = eval(expression, safe_dict)
            
            # Almacenar cálculo dinámicamente
            calculation_data = {
                "expression": expression,
                "result": str(result),
                "timestamp": datetime.datetime.now().isoformat(),
                "type": "calculation"
            }
            
            store_result = mcp_wrapper.store_vector(
                content=f"Cálculo: {expression} = {result}",
                metadata=calculation_data
            )
            
            return f"🧮 RESULTADO: {result}\n\n📊 {store_result}"
            
        except Exception as e:
            return f"❌ Error en el cálculo: {str(e)}"

class DynamicSmartAssistantTool(BaseTool):
    """Asistente inteligente completamente dinámico"""
    name: str = "smart_assistant"
    description: str = "Asistente que usa contexto completamente dinámico y base de datos vectorial"

    def _run(self, query: str, context: str = "") -> str:
        try:
            # Construir contexto completamente dinámico
            dynamic_context = context_manager.build_system_context(query)
            
            # Agregar contexto de conversación si existe
            if context:
                dynamic_context += f"\n\nCONTEXTO CONVERSACIÓN:\n{context}"
            
            messages = [
                SystemMessage(content=dynamic_context),
                HumanMessage(content=query)
            ]
            
            response = llm.invoke(messages)
            
            # Almacenar interacción si está configurado
            if context_manager.should_store_interaction():
                interaction_data = {
                    "query": query,
                    "response": response.content,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "interaction",
                    "context_used": bool(context)
                }
                
                mcp_wrapper.store_vector(
                    content=f"Q: {query}\nA: {response.content}",
                    metadata=interaction_data
                )
            
            return response.content
            
        except Exception as e:
            return f"❌ Error procesando consulta: {str(e)}"

def analyze_intent_dynamically(message: str, conversation_history: List[str] = None) -> tuple:
    """Análisis de intención completamente dinámico basado en configuración"""
    message_lower = message.lower()
    intent_patterns = context_manager.get_intent_patterns()
    
    # Verificar operaciones de memoria
    memory_ops = intent_patterns.get("memory_operations", {})
    for operation, patterns in memory_ops.items():
        if any(pattern in message_lower for pattern in patterns):
            if operation == "store":
                return "vector_memory", f"store|{message}"
            elif operation == "search":
                return "vector_memory", f"search|{message}"
            elif operation == "stats":
                return "vector_memory", "stats|"
    
    # Verificar cálculos
    calc_patterns = intent_patterns.get("calculations", [])
    if any(pattern in message_lower for pattern in calc_patterns):
        return "calculator", message
    
    # Verificar información del sistema
    system_patterns = intent_patterns.get("system_info", [])
    if any(pattern in message_lower for pattern in system_patterns):
        return "system_info", ""
    
    # Por defecto, usar asistente inteligente
    context = ""
    if conversation_history:
        context_window = context_manager.get_context_window()
        context = "\n".join(conversation_history[-context_window:])
    
    return "smart_assistant", f"{message}|{context}"

def process_message_dynamically(state: Dict[str, Any]) -> Dict[str, Any]:
    """Procesamiento completamente dinámico de mensajes"""
    message = state["current_input"]
    tools = state["tools"]
    history = state.get("conversation_history", [])
    tool_map = {tool.name: tool for tool in tools}
    
    try:
        tool_name, processed_input = analyze_intent_dynamically(message, history)
        
        if tool_name == "vector_memory":
            parts = processed_input.split("|")
            action = parts[0]
            content = parts[1] if len(parts) > 1 else ""
            
            if action == "store":
                response = tool_map[tool_name]._run("store", content=content)
            elif action == "search":
                response = tool_map[tool_name]._run("search", query=content)
            elif action == "stats":
                response = tool_map[tool_name]._run("stats")
            else:
                response = tool_map[tool_name]._run("search", query=message)
        
        elif tool_name == "smart_assistant":
            parts = processed_input.split("|")
            query = parts[0]
            context = parts[1] if len(parts) > 1 else ""
            response = tool_map[tool_name]._run(query, context)
        
        elif tool_name == "calculator":
            response = tool_map[tool_name]._run(processed_input)
        
        elif tool_name == "system_info":
            response = tool_map[tool_name]._run()
        
        else:
            response = tool_map["smart_assistant"]._run(message)
        
        state["current_response"] = response
        
        # Gestión dinámica del historial
        if "conversation_history" not in state:
            state["conversation_history"] = []
        
        state["conversation_history"].append(f"Usuario: {message}")
        state["conversation_history"].append(f"Asistente: {response}")
        
        # Gestión de historial con base de datos vectorial
        context_window = context_manager.get_context_window()
        if len(state["conversation_history"]) > (context_window * 2):
            # Almacenar historial antiguo
            old_history = state["conversation_history"][:-context_window*2]
            mcp_wrapper.store_vector(
                content="\n".join(old_history),
                metadata={"type": "conversation_history", "auto_archived": True}
            )
            state["conversation_history"] = state["conversation_history"][-context_window*2:]
            
    except Exception as e:
        state["current_response"] = f"❌ Error procesando mensaje: {str(e)}"
    
    return state

def create_dynamic_workflow() -> Graph:
    """Crea flujo de trabajo completamente dinámico"""
    workflow = Graph()
    workflow.add_node("process", process_message_dynamically)
    workflow.set_entry_point("process")
    workflow.add_edge("process", END)
    return workflow.compile()

def run_dynamic_assistant():
    """Ejecuta el asistente completamente dinámico"""
    
    # Cargar configuración dinámica
    config = context_manager.config
    assistant_config = config.get("assistant_config", {})
    
    # Herramientas dinámicas
    tools = [
        DynamicVectorMemoryTool(),
        DynamicSystemInfoTool(),
        DynamicCalculatorTool(),
        DynamicSmartAssistantTool()
    ]
    
    workflow = create_dynamic_workflow()
    
    state = {
        "tools": tools,
        "current_input": "",
        "current_response": None,
        "conversation_history": []
    }
    
    # Interfaz completamente dinámica
    assistant_name = assistant_config.get("name", "Asistente IA Dinámico")
    version = assistant_config.get("version", "2.0.0")
    
    print("\n" + "="*80)
    print(f"🧠 {assistant_name.upper()} v{version}")
    print("="*80)
    print(f"\n📋 DESCRIPCIÓN:")
    print(f"   {assistant_config.get('description', 'Asistente con configuración dinámica')}")
    
    print(f"\n🎯 CARACTERÍSTICAS DINÁMICAS:")
    features = assistant_config.get("features", {})
    for feature, enabled in features.items():
        status = "✅" if enabled else "❌"
        feature_name = feature.replace("_", " ").title()
        print(f"   {status} {feature_name}")
    
    print(f"\n🔗 INTEGRACIONES:")
    if mcp_wrapper.mcp_available:
        print("   ✅ MCP Qdrant Cloud - Conectado")
    else:
        print("   ⚠️  MCP Qdrant Cloud - Modo simulación")
    
    print(f"\n🚀 CAPACIDADES HABILITADAS:")
    capabilities = config.get("capabilities", [])
    for capability in capabilities:
        if capability.get("enabled", False):
            print(f"   • {capability.get('name', '').title()}: {capability.get('description', '')}")
    
    print(f"\n💡 COMANDOS DINÁMICOS:")
    print("   • 'Recordar [información]' - Almacenar en base de datos vectorial")
    print("   • 'Buscar [tema]' - Búsqueda semántica")
    print("   • 'Calcular [expresión]' - Operaciones matemáticas")
    print("   • 'Estado del sistema' - Información del hardware")
    print("   • Cualquier consulta general")
    
    print("\n" + "="*80)
    print("🚀 Asistente dinámico iniciado - Configuración cargada exitosamente")
    print("Para salir, escribe 'salir' o presiona Ctrl+C")
    print("="*80)
    
    # Saludo dinámico
    greeting = context_manager.get_response_template("greeting")
    print(f"\n🤖 {greeting}")
    
    while True:
        try:
            message = input("\n🟢 Tú: ").strip()
            
            if message.lower() in ['salir', 'exit', 'quit', 'adiós']:
                print(f"\n🤖 Asistente: ¡Gracias por usar {assistant_name}! Tu información permanece segura en la base de datos vectorial. ¡Hasta pronto! 👋")
                break
                
            if not message:
                print(f"\n🤖 Asistente: ¿En qué puedo ayudarte? Mi configuración es completamente dinámica y se actualiza desde la base de datos vectorial.")
                continue
            
            print("\n🔄 Procesando con configuración dinámica...")
            
            state["current_input"] = message
            result = workflow.invoke(state)
            
            print(f"\n🤖 Asistente:\n{result['current_response']}")
            
            state = result
            
        except KeyboardInterrupt:
            print(f"\n\n🤖 Asistente: ¡Hasta pronto! Tu información se mantiene segura en la base de datos vectorial 👋")
            break
        except Exception as e:
            error_template = context_manager.get_response_template("error")
            print(f"\n❌ {error_template}\nDetalle: {str(e)}")

if __name__ == "__main__":
    run_dynamic_assistant()
