# AgenteBasico 🤖

Un asistente virtual inteligente desarrollado con LangChain, LangGraph y OpenAI que puede responder preguntas, proporcionar información del sistema y mantener conversaciones naturales.

## 🌟 Características

- **Conversación Natural**: Interactúa con el asistente usando lenguaje natural
- **Información del Sistema**: Obtén datos sobre tu computadora (specs, memoria, etc.)
- **Consultas de Tiempo**: Pregunta la hora actual
- **Integración con ChatGPT**: Respuestas inteligentes para preguntas generales
- **Interfaz de Línea de Comandos**: Fácil de usar desde la terminal

## 🛠️ Herramientas Disponibles

El asistente incluye las siguientes herramientas:

1. **SystemInfoTool**: Información del sistema operativo y arquitectura
2. **TimeTool**: Hora actual
3. **MemoryUsageTool**: Uso de memoria RAM
4. **AskGPTTool**: Consultas generales a ChatGPT

## 📋 Requisitos

- Python 3.8 o superior
- Cuenta de OpenAI con API key
- Conexión a Internet

## 🚀 Instalación

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/AgenteBasico.git
   cd AgenteBasico
   ```

2. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura tu API key de OpenAI**:
   - Ve a [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Crea una nueva API key
   - Crea un archivo `.env` en el directorio del proyecto
   - Añade tu API key:
     ```
     OPENAI_API_KEY=tu-api-key-aqui
     ```

## 🎯 Uso

Ejecuta el asistente:

```bash
python main.py
```

### Ejemplos de Interacción

```
Tú: ¿Qué hora es?
Asistente: Son las 14:30:25

Tú: ¿Cuánta memoria RAM tiene mi computadora?
Asistente: Tu computadora tiene 16.0GB de RAM y está usando el 45%

Tú: ¿Cuál es la capital de Francia?
Asistente: La capital de Francia es París...

Tú: salir
Asistente: ¡Hasta pronto! 👋
```

## 📁 Estructura del Proyecto

```
AgenteBasico/
├── main.py           # Archivo principal con la lógica del asistente
├── requirements.txt  # Dependencias del proyecto
├── README.md        # Este archivo
└── .env             # Variables de entorno (crear manualmente)
```

## 🔧 Configuración Avanzada

### Cambiar el Modelo de OpenAI

Puedes modificar el modelo en `main.py`:

```python
llm = ChatOpenAI(
    model="gpt-4",  # Cambia a gpt-4 si tienes acceso
    temperature=0.7,
    api_key=api_key
)
```

### Añadir Nuevas Herramientas

Para añadir nuevas herramientas, crea una clase que herede de `BaseTool`:

```python
class MiNuevaHerramienta(BaseTool):
    name: str = "mi_herramienta"
    description: str = "Descripción de la herramienta"

    def _run(self) -> str:
        # Tu lógica aquí
        return "Resultado"
```

## 🐛 Solución de Problemas

### Error de API Key
```
❌ No se encontró la API key de OpenAI
```
**Solución**: Verifica que hayas creado el archivo `.env` con tu API key.

### Error de Cuota Excedida
```
Lo siento, he excedido mi cuota de uso
```
**Solución**: Verifica tu saldo en OpenAI o espera a que se renueve tu límite.

### Error de Conexión
```
❌ Error al conectar con OpenAI
```
**Solución**: Verifica tu conexión a internet y que tu API key sea válida.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ve el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

Desarrollado con ❤️ por [Tu Nombre]

## 🙏 Agradecimientos

- [LangChain](https://python.langchain.com/) - Framework para aplicaciones LLM
- [OpenAI](https://openai.com/) - API de inteligencia artificial
- [LangGraph](https://python.langchain.com/docs/langgraph) - Librería para flujos de trabajo

---

¿Tienes preguntas? ¡Abre un issue o contacta al desarrollador!