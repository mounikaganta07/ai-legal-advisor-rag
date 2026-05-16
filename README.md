# AI Legal Advisor

A Hybrid RAG-based conversational legal assistant built using LangChain, FAISS, BM25 retrieval, Sentence Transformers, and OpenRouter LLM APIs.

## Features

- Hybrid Retrieval (Semantic Search + BM25)
- Conversational Memory
- Constitution-based Legal Question Answering
- Source-grounded Responses
- FAISS Vector Database
- Gradio-based Chat Interface
- Query Expansion for Legal Terminology
- Retrieval Evaluation and Benchmarking
- Top-K and Top-1 Retrieval Metrics

## Tech Stack

- Python
- LangChain
- FAISS
- BM25
- Sentence Transformers
- Gradio
- OpenRouter API

## Project Structure

```bash
ai-legal-advisor/

│── app/
│   │
│   ├── evaluation/
│   ├── ingestion/
│   ├── llm/
│   ├── prompts/
│   ├── retrieval/
│   ├── utils/
│   │
│   ├── main.py
│   └── rag_pipeline.py
│
│── data/
│   └── legal_docs/
│
│── tests/
│
│── requirements.txt
│── README.md
│── .gitignore
```

## Installation

```bash
git clone <your-repository-url>

cd ai-legal-advisor

pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_api_key
```

## Run Application

```bash
python -m app.main
```

## Evaluation

Run retrieval benchmark evaluation:

```bash
python -m app.evaluation.evaluate_retrieval
```

### Current Retrieval Performance

| Metric | Score |
|---|---|
| Top-K Retrieval Accuracy | 86.67% |
| Top-1 Retrieval Accuracy | 80.00% |

Evaluation performed on a paraphrased constitutional law benchmark dataset.

## Example Questions

- What is Article 21?
- Can the government take away personal liberty?
- Explain directive principles
- What gives Supreme Court power to issue writs?
- Which article discusses suspension of fundamental rights during emergency?

## Future Improvements

- Cross-encoder reranking
- Legal-specific embedding models
- Streaming responses
- Advanced citation ranking
- Multi-document support
- Cloud deployment
- User authentication and chat history

## Author

Mounika Ganta