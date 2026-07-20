<div align="center">

# 🤖 Bot-telegram

_Un bot de Telegram con un agente de IA que decide por sí solo dónde buscar la respuesta: en una base de conocimiento propia, en Wikipedia, en la PokeAPI o consultando el tiempo en tiempo real._

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)]()
[![LangChain](https://img.shields.io/badge/LangChain-Agente%20ReAct-1C3C3C)]()
[![Gemini](https://img.shields.io/badge/LLM-Gemini%202.5%20Flash-8E75B2)]()
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4?logo=telegram)]()

</div>

---

## 📖 Índice

- [Descripción](#-descripción)
- [Cómo funciona el agente](#-cómo-funciona-el-agente)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Tecnologías](#-tecnologías)
- [Ideas de mejora](#-ideas-de-mejora)
- [Cómo contribuir](#-cómo-contribuir)
- [Autoría](#-autoría)
- [Licencia](#-licencia)

---

## 🧭 Descripción

Este bot de Telegram no responde con reglas fijas: usa un **agente de IA (patrón ReAct, vía LangChain)** que, ante cada pregunta, decide de forma autónoma qué herramienta usar para responder. En concreto, es capaz de:

- 📚 Consultar una **base de conocimiento propia** (temario y horarios de un curso, indexados en una base vectorial con ChromaDB).
- 🌐 Buscar en **Wikipedia** en español cuando la pregunta no está en su base de conocimiento.
- 🐾 Consultar la **PokeAPI** para dar datos técnicos de cualquier Pokémon (peso, altura, habilidades, tipos).
- ⛅ Consultar el **tiempo en tiempo real** de cualquier ciudad.

El propio agente elige qué herramienta encaja mejor con la pregunta del usuario, sin necesidad de comandos específicos para cada función.

## 🧠 Cómo funciona el agente

1. El usuario escribe un mensaje al bot en Telegram.
2. El mensaje llega a un **agente ReAct** (`create_react_agent`, de LangChain) construido sobre **Gemini 2.5 Flash**.
3. El agente razona qué herramienta necesita y la ejecuta:
   - `tool_rag` → busca en la base vectorial (ChromaDB) generada a partir de `conocimiento.txt`.
   - `wiki_tool` → busca en Wikipedia en español.
   - `pokemon_tool` → consulta la [PokeAPI](https://pokeapi.co/).
   - `weather_tool` → consulta el tiempo vía [wttr.in](https://wttr.in/).
4. Devuelve la respuesta final al usuario en Telegram.

## ✅ Requisitos

- Python 3.10 o superior
- Un **token de bot de Telegram** (se obtiene hablando con [@BotFather](https://t.me/BotFather))
- Una **API key de Google Gemini**
- Conexión a internet (Wikipedia, PokeAPI y wttr.in se consultan en tiempo real)

## ⚙️ Instalación

Clona el repositorio:

```bash
git clone https://github.com/davidfdez226/Bot-telegram.git
cd Bot-telegram
```

Crea un entorno virtual e instala las dependencias:

```bash
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Crea un archivo `.env` en la raíz del proyecto con tus claves:

```env
TELEGRAM_TOKEN=tu_token_de_botfather
GEMINI_API_KEY=tu_api_key_de_gemini
```

Genera (o actualiza) la base de conocimiento vectorial a partir de `conocimiento.txt`:

```bash
python ingesta.py
```

## ▶️ Uso

Lanza el bot:

```bash
python bot.py
```

Una vez en marcha, abre una conversación con tu bot en Telegram y prueba, por ejemplo:

- `/start` → mensaje de bienvenida
- _"¿Cuándo es el examen del curso?"_ → responde con la base de conocimiento propia
- _"¿Quién fue Alan Turing?"_ → responde consultando Wikipedia
- _"Háblame de Pikachu"_ → responde consultando la PokeAPI
- _"¿Qué tiempo hace en Cáceres?"_ → responde con el clima en tiempo real

## 🗂️ Estructura del proyecto

```
Bot-telegram/
├── bot.py                # Lógica del bot y del agente (herramientas + Telegram)
├── ingesta.py             # Procesa conocimiento.txt y lo indexa en ChromaDB
├── conocimiento.txt        # Base de conocimiento en texto plano (temario/horarios)
├── chroma_db/              # Base de datos vectorial generada por ingesta.py
├── Documentación.pdf       # Documentación del proyecto
└── requirements.txt
```

## 🛠️ Tecnologías

| Herramienta | Uso en el proyecto |
|---|---|
| [python-telegram-bot](https://python-telegram-bot.org/) | Interfaz del bot con la API de Telegram |
| [LangChain](https://www.langchain.com/) | Orquestación del agente y sus herramientas (RAG) |
| [Google Gemini](https://ai.google.dev/) (`gemini-2.5-flash`) | Modelo de lenguaje que razona y responde |
| [ChromaDB](https://www.trychroma.com/) | Base de datos vectorial para la búsqueda por conocimiento propio |
| [sentence-transformers](https://www.sbert.net/) | Embeddings multilingües para indexar `conocimiento.txt` |
| [Wikipedia API](https://pypi.org/project/wikipedia/) | Búsqueda de información general en español |
| [PokeAPI](https://pokeapi.co/) | Datos técnicos de Pokémon |
| [wttr.in](https://wttr.in/) | Consulta del tiempo en tiempo real |
| [LangSmith](https://www.langchain.com/langsmith) | Prompt del agente ReAct y trazabilidad |

## 💡 Ideas de mejora

- [ ] Desplegar el bot en un servidor (Docker + VPS o similar) para que funcione 24/7
- [ ] Ampliar la base de conocimiento a más de un curso o temática
- [ ] Añadir memoria de conversación para preguntas de seguimiento
- [ ] Registrar métricas de uso (preguntas más frecuentes, herramienta más usada)

## 🤝 Cómo contribuir

1. Haz un fork del proyecto
2. Crea una rama para tu cambio (`git checkout -b feature/mi-cambio`)
3. Haz commit de tus cambios (`git commit -m 'Añade mi-cambio'`)
4. Sube la rama (`git push origin feature/mi-cambio`)
5. Abre un Pull Request

## ✍️ Autoría

Desarrollado por **[David Fernández](https://github.com/davidfdez226)**.

## 📄 Licencia

Este repositorio no especifica actualmente una licencia. Si quieres que el proyecto pueda reutilizarse libremente, considera añadir un archivo `LICENSE` (por ejemplo, con la [licencia MIT](https://choosealicense.com/licenses/mit/)).
