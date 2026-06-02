import os
import requests
import json
import wikipedia
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain_classic import hub
from langsmith import Client

# Cargamos las variables de entorno
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Faltan las claves TELEGRAM_TOKEN o GEMINI_API_KEY en el archivo .env")

# 1. Configuramos el modelo de Gemini para LangChain
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", google_api_key=GEMINI_API_KEY)

# Cargamos la base de datos vectorial (ChromaDB)
DIRECTORIO_DB = "./chroma_db"
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
vectorstore = Chroma(persist_directory=DIRECTORIO_DB, embedding_function=embeddings)

@tool
def tool_rag(query: str) -> str:
    """Consulta la base de conocimientos oficial del curso para dudas sobre temario y horarios."""
    docs = vectorstore.similarity_search(query, k=3)
    return "\n\n".join([doc.page_content for doc in docs])

@tool
def pokemon_tool(pokemon_name: str) -> str:
    """Consulta información técnica sobre un Pokémon (peso, altura, habilidades, tipos). 
    El parámetro de entrada debe ser el nombre del Pokémon en minúsculas."""
    name = pokemon_name.lower().strip()
    url = f"https://pokeapi.co/api/v2/pokemon/{name}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            datos_reducidos = {
                "name": data["name"],
                "weight": data["weight"],
                "height": data["height"],
                "abilities": [a["ability"]["name"] for a in data["abilities"]],
                "types": [t["type"]["name"] for t in data["types"]]
            }
            return json.dumps(datos_reducidos)
        return f"No he podido encontrar al Pokémon '{name}'."
    except Exception as e:
        return f"Error al consultar la API: {e}"

@tool
def weather_tool(ciudad: str) -> str:
    """Consulta el clima actual de una ciudad en tiempo real. El parámetro debe ser el nombre de la ciudad."""
    # Sustituimos espacios por + para la URL
    ciudad_url = ciudad.strip().replace(" ", "+")
    url = f"https://wttr.in/{ciudad_url}?format=j1"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            actual = data['current_condition'][0]
            # Reducimos el JSON para ahorrar tokens
            datos_clima = {
                "temp_C": actual['temp_C'],
                "descripcion": actual['lang_es'][0]['value'] if 'lang_es' in actual else actual['weatherDesc'][0]['value'],
                "humedad": actual['humidity'],
                "sensacion": actual['FeelsLikeC']
            }
            return json.dumps(datos_clima)
        return "No he podido obtener el clima para esa ciudad."
    except Exception as e:
        return f"Error al consultar el clima: {e}"

# Configuración de Wikipedia
wikipedia.set_user_agent("AI_Assistant_PIA/1.0")
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500, lang="es")
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

tools = [tool_rag, wiki_tool, pokemon_tool, weather_tool]

# Configuración del Agente
client_ls = Client()
prompt = client_ls.pull_prompt("hwchase17/react", dangerously_pull_public_prompt=True)
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde al comando /start"""
    usuario = update.effective_user.first_name
    await update.message.reply_text(
        f"¡Hola, {usuario}! Soy tu asistente multidisciplinar. Puedo ayudarte con el temario, Wikipedia, Pokémon o el clima."
    )

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el mensaje del usuario mediante el Agente"""
    mensaje_espera = await update.message.reply_text("🤖 Pensando...")
    
    try:
        pregunta = update.message.text
        # El agente decide qué herramienta usar automáticamente
        resultado = agent_executor.invoke({"input": pregunta})        
        await mensaje_espera.edit_text(resultado["output"])
        
    except Exception as e:
        await mensaje_espera.edit_text("⚠️ No he podido procesar esa consulta.")
        print(f"Error en el agente: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("🚀 Bot Agente en marcha...")
    app.run_polling()

if __name__ == "__main__":
    main()