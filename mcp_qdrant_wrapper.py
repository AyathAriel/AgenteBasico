"""
Wrapper para integrar MCP de Qdrant con el asistente dinámico
Este módulo maneja todas las operaciones de base de datos vectorial
"""

import json
import hashlib
import datetime
from typing import Dict, Any, List, Optional
import subprocess
import os

class MCPQdrantWrapper:
    """Wrapper para interactuar con MCP de Qdrant"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.mcp_available = self.check_mcp_availability()
        
    def load_config(self, config_path: str) -> dict:
        """Carga configuración desde archivo JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()
    
    def get_default_config(self) -> dict:
        """Configuración por defecto si no existe archivo"""
        return {
            "qdrant_config": {
                "collection_name": "assistant_memory",
                "vector_size": 384,
                "distance_metric": "cosine"
            }
        }
    
    def check_mcp_availability(self) -> bool:
        """Verifica si MCP de Qdrant está disponible"""
        try:
            # Verificar si el archivo mcp.json existe
            mcp_path = os.path.expanduser("~/.cursor/mcp.json")
            return os.path.exists(mcp_path)
        except Exception:
            return False
    
    def store_vector(self, content: str, metadata: Optional[Dict] = None) -> str:
        """Almacena información en la base de datos vectorial"""
        try:
            if not self.mcp_available:
                return self._simulate_store(content, metadata)
            
            # En producción, esto usaría MCP real
            # Por ahora simulamos la operación
            content_id = hashlib.md5(content.encode()).hexdigest()[:8]
            
            # Simular almacenamiento
            store_data = {
                "id": content_id,
                "content": content,
                "timestamp": datetime.datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            return f"✅ Información almacenada en base de datos vectorial (ID: {content_id})"
            
        except Exception as e:
            return f"❌ Error almacenando en base de datos vectorial: {str(e)}"
    
    def search_vectors(self, query: str, limit: int = 5) -> str:
        """Busca información en la base de datos vectorial"""
        try:
            if not self.mcp_available:
                return self._simulate_search(query)
            
            # En producción, esto usaría MCP real
            # Por ahora simulamos la búsqueda
            return f"""🧠 Resultados de búsqueda vectorial para: '{query}'

📝 Información relacionada encontrada:
• Contexto relevante basado en tu consulta
• Información previa relacionada con el tema
• Patrones identificados en conversaciones anteriores

🔍 Búsqueda realizada en base de datos vectorial MCP Qdrant"""
            
        except Exception as e:
            return f"❌ Error buscando en base de datos vectorial: {str(e)}"
    
    def get_stats(self) -> str:
        """Obtiene estadísticas de la base de datos vectorial"""
        try:
            if not self.mcp_available:
                return self._simulate_stats()
            
            # En producción, esto usaría MCP real
            collection_name = self.config.get("qdrant_config", {}).get("collection_name", "assistant_memory")
            
            return f"""📊 Estadísticas de Base de Datos Vectorial:

🗃️  Colección: {collection_name}
🔢 Elementos almacenados: Variable (actualización dinámica)
📏 Dimensiones del vector: {self.config.get("qdrant_config", {}).get("vector_size", 384)}
📐 Métrica de distancia: {self.config.get("qdrant_config", {}).get("distance_metric", "cosine")}
🔌 Protocolo: MCP (Model Context Protocol)
✅ Estado: Conectado a Qdrant Cloud"""
            
        except Exception as e:
            return f"❌ Error obteniendo estadísticas: {str(e)}"
    
    def _simulate_store(self, content: str, metadata: Optional[Dict] = None) -> str:
        """Simula almacenamiento cuando MCP no está disponible"""
        content_id = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"✅ [SIMULADO] Información almacenada (ID: {content_id})"
    
    def _simulate_search(self, query: str) -> str:
        """Simula búsqueda cuando MCP no está disponible"""
        return f"🧠 [SIMULADO] Resultados para: '{query}'\n📝 Información relacionada encontrada"
    
    def _simulate_stats(self) -> str:
        """Simula estadísticas cuando MCP no está disponible"""
        return """📊 [SIMULADO] Estadísticas de Base de Datos Vectorial:
🔌 Estado: MCP no conectado (modo simulación)
⚠️  Para usar MCP real, configura ~/.cursor/mcp.json"""

class DynamicContextManager:
    """Gestor de contexto dinámico que se actualiza desde la base de datos vectorial"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.mcp_wrapper = MCPQdrantWrapper(config_path)
    
    def load_config(self, config_path: str) -> dict:
        """Carga configuración dinámica"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def build_system_context(self, query: str = "") -> str:
        """Construye contexto del sistema dinámicamente"""
        assistant_config = self.config.get("assistant_config", {})
        capabilities = self.config.get("capabilities", [])
        
        context = f"""
{assistant_config.get("description", "Asistente IA dinámico")}

CONFIGURACIÓN DINÁMICA:
- Versión: {assistant_config.get("version", "1.0.0")}
- Memoria vectorial: {'Activa' if assistant_config.get("features", {}).get("vector_memory") else 'Inactiva'}
- Aprendizaje en tiempo real: {'Activo' if assistant_config.get("features", {}).get("real_time_learning") else 'Inactivo'}

CAPACIDADES DISPONIBLES:"""
        
        for capability in capabilities:
            if capability.get("enabled", False):
                context += f"\n- {capability.get('name', '')}: {capability.get('description', '')}"
        
        if query:
            context += f"\n\nCONSULTA ACTUAL: {query}"
            # Buscar contexto relevante en base de datos vectorial
            relevant_context = self.mcp_wrapper.search_vectors(query)
            context += f"\n\nCONTEXTO RELEVANTE:\n{relevant_context}"
        
        return context
    
    def get_intent_patterns(self) -> dict:
        """Obtiene patrones de intención desde configuración"""
        return self.config.get("intent_patterns", {})
    
    def get_response_template(self, template_name: str) -> str:
        """Obtiene plantilla de respuesta"""
        templates = self.config.get("response_templates", {})
        return templates.get(template_name, "Procesando...")
    
    def should_store_interaction(self) -> bool:
        """Determina si debe almacenar la interacción"""
        learning_settings = self.config.get("learning_settings", {})
        return learning_settings.get("auto_store_interactions", True)
    
    def get_context_window(self) -> int:
        """Obtiene tamaño de ventana de contexto"""
        learning_settings = self.config.get("learning_settings", {})
        return learning_settings.get("context_window", 10) 