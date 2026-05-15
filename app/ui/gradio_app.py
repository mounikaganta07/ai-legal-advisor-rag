import gradio as gr

from app.retrieval.hybrid_retriever import hybrid_retrieve
from app.prompts.legal_prompt import build_legal_prompt
from app.llm.openrouter_client import generate_response

def legal_chatbot(query):

    docs = hybrid_retrieve(query)

    context = "\n\n".join([
        doc.page_content for doc in docs
    ])

    prompt = build_legal_prompt(context, query)

    answer = generate_response(prompt)

    sources = "\n\n".join([
        f"Source {i+1}:\n{doc.page_content[:500]}"
        for i, doc in enumerate(docs)
    ])

    final_response = f"""
ANSWER:
{answer}

-----------------------------------

RETRIEVED SOURCES:

{sources}
"""

    return final_response

interface = gr.Interface(
    fn=legal_chatbot,
    inputs=gr.Textbox(
        lines=2,
        placeholder="Ask a legal question..."
    ),
    outputs="text",
    title="AI Legal Advisor",
    description="Advanced RAG-powered legal assistant with source retrieval"
)

interface.launch()