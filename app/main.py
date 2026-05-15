import gradio as gr

from app.retrieval.hybrid_retriever import (
    hybrid_retrieve
)

from app.prompts.legal_prompt import (
    build_legal_prompt
)

from app.llm.openrouter_client import (
    generate_response
)

def legal_chatbot(message, history):

    docs = hybrid_retrieve(
        message
    )

    context = "\n\n".join([
        doc.page_content
        for doc in docs
    ])

    prompt = build_legal_prompt(
        context,
        message
    )

    answer = generate_response(
        prompt
    )

    formatted_sources = "\n\n".join([

        f"""
### Source {i+1}

Article Number:
{doc.metadata.get('article_number', 'N/A')}

Title:
{doc.metadata.get('article_title', 'N/A')}

Content:
{doc.page_content[:500]}
"""

        for i, doc in enumerate(docs)

    ])

    final_response = f"""
{answer}

---

## Retrieved Legal Sources

{formatted_sources}
"""

    return final_response

chat_interface = gr.ChatInterface(

    fn=legal_chatbot,

    title="AI Legal Advisor",

    description=(
        "Hybrid RAG-powered legal assistant "
        "with deterministic article retrieval"
    )
)

chat_interface.launch()