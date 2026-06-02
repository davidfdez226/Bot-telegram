import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# 1. Configurar rutas

DIRECTORIO_DB = "./chroma_db"
ARCHIVO_CONOCIMIENTO = "conocimiento.txt"


def iniciar_ingesta():
    # Verificar que el archivo de conocimiento existe
    if not os.path.exists(ARCHIVO_CONOCIMIENTO):
        print(f"❌ Error: Crea primero el archivo '{ARCHIVO_CONOCIMIENTO}' con la información para el bot.")
        return

    print("📂 Cargando documento...")
    # Cargamos el archivo de texto plano
    loader = TextLoader(ARCHIVO_CONOCIMIENTO, encoding="utf-8")
    documentos = loader.load()
    print(f"Documentos cargados: {len(documentos)}")
    if len(documentos) > 0:
        print(f"Contenido del primer doc: {documentos[0].page_content[:100]}...")

    print("✂️ Dividiendo texto en fragmentos (Chunks)...")
    # Dividimos en trozos de 1000 caracteres con un solapamiento de 200
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(documentos)
    print(f"✅ Texto dividido en {len(chunks)} fragmentos.")

    print("🧠 Generando embeddings y guardando en ChromaDB...")
    # Usamos un modelo multilingüe ligero para generar los vectores
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Creamos la base de datos vectorial y la persistimos en la carpeta indicada
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DIRECTORIO_DB
    )
    
    print(f"🚀 ¡RAG creado con éxito! Guardado en: {DIRECTORIO_DB}")

if __name__ == "__main__":
    iniciar_ingesta()