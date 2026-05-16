# ⚖️ AI Legal Advisor

A Hybrid RAG-powered conversational legal assistant built using:

- LangChain
- FAISS Vector Database
- BM25 Retrieval
- Sentence Transformers
- Gradio UI
- OpenRouter LLM API

## Features

- Hybrid Retrieval (Semantic + BM25)
- Conversational Memory
- Legal Document Question Answering
- Constitution-based Retrieval
- Clean Gradio Chat Interface
- Source-backed Responses

## Tech Stack

- Python
- LangChain
- FAISS
- Gradio
- Sentence Transformers
- OpenRouter API

## Project Structure

```bash
app/
│
├── ingestion/
├── llm/
├── prompts/
├── retrieval/
├── ui/
├── utils/
│
├── main.py
├── rag_pipeline.py
└── vector_store.py