# Tazuna Hayakawa

A Discord bot built around **Tazuna Hayakawa**, secretary to the director at Tracen Academy (from *Umamusume: Pretty Derby*). She answers questions, searches the web for current information, summarizes chat history, translates text, and can read PDFs you give her to answer questions grounded in their contents.

The bot runs entirely on a local LLM via [Ollama](https://ollama.com/), orchestrated with [LangGraph](https://www.langchain.com/langgraph), so no OpenAI/Anthropic API key is required for the core chat logic.

## Commands

| Command | Description | Usage |
|---|---|---|
| `!help` | Shows the list of commands | `!help` |
| `!ask` | Ask a question. Automatically routes to a live web search (via Tavily) if the question needs current information, or answers directly from the model otherwise | `!ask [your question]` |
| `!summarize` | Summarizes channel messages between two dates | `!summarize [YYYY-MM-DD] \| [YYYY-MM-DD]` |
| `!add` | Uploads and saves a PDF to Tazuna's memory | `!add` (with file attachment) |
| `!remove` | Removes a saved PDF, or all of them | `!remove [filename]` or `!remove all` |
| `!memory` | Lists all PDFs currently saved | `!memory` |
| `!source` | Ask a question answered using retrieval over your saved PDFs (RAG) | `!source [your question]` |
| `!translate` | Translates text into a target language | `!translate [text] [language]` |

Long responses (over 2000 characters) are automatically chunked into multiple messages so they fit within Discord's message limits.

## Features

Each feature is implemented as its own [LangGraph](https://www.langchain.com/langgraph) state graph:

- **`!ask`** — A small routing graph first decides whether the question needs static knowledge or live information, then either answers directly with the local LLM or hands off to the search pipeline.
- **`!source`** — A retrieval-augmented generation (RAG) pipeline: PDFs in the local storage folder are loaded, chunked, embedded (`nomic-embed-text` via Ollama), and stored in a [Chroma](https://www.trychroma.com/) vector store.
- **`!summarize`** — Pulls channel message history between two dates and summarizes it with the LLM.
- **`!translate`** — Uses structured output to detect the source language and produce a translation.
- **Chunking** — Long outputs are split into Discord-safe chunks by asking the LLM to divide the text without altering or skipping content.
- **Web search** — Uses [Tavily](https://tavily.com/) to fetch current results, which are then summarized/answered by the LLM grounded in that context.

## Project structure

```
src/
├── main.py                        # Bot entry point and command handlers
├── config/
│   ├── help_message.py            # Text shown by !help
│   └── prompt_template.py         # Shared persona / system prompt
├── feature/
│   ├── ask_function.py            # !ask — routes between direct answer and search
│   ├── ask_source_function.py     # !source — RAG over saved PDFs
│   ├── chat_summarize_function.py # !summarize
│   ├── download_pdf.py            # !add
│   ├── list_pdf.py                # !memory
│   ├── remove_pdf.py              # !remove
│   └── translate_function.py      # !translate
└── util/
    ├── chunk_output.py            # Splits long output into Discord-safe chunks
    └── search_function.py         # Tavily web search + grounded answer
```