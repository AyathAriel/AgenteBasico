#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión a Qdrant Cloud
y crear la colección assistant_memory para el asistente
"""

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import hashlib
import datetime

# Configuración de Qdrant
QDRANT_URL = "https://afd9656e-bb71-4d33-9efe-a4a07c666b27.eu-central-1-0.aws.cloud.qdrant.io:6333"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.xTqQX2bZH-7HHi_5Yz0XRWvCOvu5knxP1O9hP2b8kbM"
COLLECTION_NAME = "assistant_memory"

def test_qdrant_connection():
    """Prueba la conexión a Qdrant y verifica funcionalidades básicas"""
    
    try:
        print("🔄 Conectando a Qdrant Cloud...")
        qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        print("✅ Cliente Qdrant creado exitosamente!")
        
        # Listar colecciones existentes
        print("\n📁 Verificando colecciones existentes...")
        collections = qdrant_client.get_collections()
        existing_collections = [c.name for c in collections.collections]
        print(f"   Colecciones encontradas: {existing_collections}")
        
        # Crear colección si no existe
        if COLLECTION_NAME not in existing_collections:
            print(f"\n🏗️  Creando colección '{COLLECTION_NAME}'...")
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            print(f"✅ Colección '{COLLECTION_NAME}' creada exitosamente!")
        else:
            print(f"ℹ️  La colección '{COLLECTION_NAME}' ya existe.")
        
        # Obtener información de la colección
        print(f"\n📊 Información de la colección '{COLLECTION_NAME}':")
        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        print(f"   Puntos almacenados: {collection_info.points_count}")
        print(f"   Dimensiones del vector: {collection_info.config.params.vectors.size}")
        print(f"   Métrica de distancia: {collection_info.config.params.vectors.distance}")
        
        # Probar inserción de un vector de prueba
        print(f"\n🧪 Probando inserción de vector de prueba...")
        test_vector = [0.1] * 384  # Vector de prueba con 384 dimensiones
        test_content = f"Vector de prueba creado el {datetime.datetime.now().isoformat()}"
        test_id = hashlib.md5(test_content.encode()).hexdigest()
        
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=test_id,
                    vector=test_vector,
                    payload={
                        "content": test_content,
                        "type": "test",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "test": True
                    }
                )
            ]
        )
        print(f"✅ Vector de prueba insertado con ID: {test_id[:8]}...")
        
        # Verificar la inserción
        print(f"\n🔍 Verificando inserción...")
        updated_info = qdrant_client.get_collection(COLLECTION_NAME)
        print(f"   Puntos después de inserción: {updated_info.points_count}")
        
        # Probar búsqueda
        print(f"\n🔎 Probando búsqueda vectorial...")
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=test_vector,
            limit=3,
            with_payload=True
        )
        
        if search_results:
            print(f"✅ Búsqueda exitosa! Resultados encontrados: {len(search_results)}")
            for i, result in enumerate(search_results[:2]):
                print(f"   Resultado {i+1}: Score {result.score:.3f}")
                print(f"      Contenido: {result.payload.get('content', 'N/A')[:50]}...")
        else:
            print("⚠️  No se encontraron resultados en la búsqueda")
        
        print(f"\n🎉 ¡Todas las pruebas de Qdrant completadas exitosamente!")
        print(f"✅ La base de datos vectorial está lista para el asistente")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas de Qdrant:")
        print(f"   Tipo de error: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        return False

def print_connection_summary():
    """Imprime un resumen de la configuración de conexión"""
    print("\n" + "="*60)
    print("📋 RESUMEN DE CONFIGURACIÓN QDRANT")
    print("="*60)
    print(f"🔗 URL: {QDRANT_URL}")
    print(f"🔑 API Key: {QDRANT_API_KEY[:20]}...")
    print(f"📁 Colección: {COLLECTION_NAME}")
    print(f"📏 Dimensiones: 384")
    print(f"📐 Métrica: Cosine")
    print("="*60)

if __name__ == "__main__":
    print("🧠 VERIFICADOR DE CONEXIÓN QDRANT PARA ASISTENTE IA")
    print("="*60)
    
    print_connection_summary()
    
    success = test_qdrant_connection()
    
    if success:
        print(f"\n🚀 ¡Tu asistente IA está listo para usar Qdrant!")
        print(f"   Puedes ejecutar 'python main.py' para comenzar.")
    else:
        print(f"\n⚠️  Hay problemas con la conexión a Qdrant.")
        print(f"   Verifica tu configuración antes de continuar.") 