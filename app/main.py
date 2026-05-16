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

def build_conversation_context(history):

    conversation_context = ""

    for message in history:

        if message["role"] == "user":

            conversation_context += (
                f"User: {message['content']}\n"
            )

        elif message["role"] == "assistant":

            conversation_context += (
                f"Assistant: {message['content']}\n\n"
            )

    return conversation_context

def legal_chatbot(message, history):

    previous_context = (
        build_conversation_context(
            history
        )
    )

    enhanced_query = f"""
Previous Conversation:

{previous_context}

Current User Question:
{message}
"""

    docs = hybrid_retrieve(
        enhanced_query
    )

    context = "\n\n".join([
        doc.page_content
        for doc in docs
    ])

    prompt = build_legal_prompt(
        context,
        enhanced_query
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

        for i, doc in enumerate(docs[:3])

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

    title="⚖️ AI Legal Advisor",

    description=(
        "Conversational legal assistant "
        "powered by Hybrid RAG"
    ),

    chatbot=gr.Chatbot(
        height=650
    ),

    textbox=gr.Textbox(
        placeholder=(
            "Ask a legal question and press Enter..."
        ),
        container=False
    )
)

chat_interface.launch()