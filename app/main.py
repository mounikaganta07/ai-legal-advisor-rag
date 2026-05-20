import re
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


def get_message_content(message):

    content = None

    if isinstance(message, dict):
        content = message.get("content", "")

    elif isinstance(message, (list, tuple)):

        if len(message) >= 2:
            content = message[1] or ""

        elif len(message) == 1:
            content = message[0] or ""

    elif isinstance(message, str):
        content = message

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, dict):
                text_parts.append(
                    item.get("text", "")
                )

            elif isinstance(item, str):
                text_parts.append(item)

        return "\n".join(text_parts)

    return ""


def extract_last_legal_reference(history):

    for item in reversed(history):

        if isinstance(item, dict):

            if item.get("role") != "user":
                continue

            content = get_message_content(item)

        elif isinstance(item, (list, tuple)) and len(item) >= 1:

            content = get_message_content(item[0])

        else:
            continue

        article_match = re.search(
            r"\barticle\s+(\d+[A-Z]?)\b",
            content,
            re.IGNORECASE
        )

        if article_match:
            return f"Article {article_match.group(1).upper()}"

        section_match = re.search(
            r"\bsection\s+(\d+[A-Z]?)\b",
            content,
            re.IGNORECASE
        )

        if section_match:
            return f"Section {section_match.group(1).upper()}"

    for item in reversed(history):

        if isinstance(item, dict):

            if item.get("role") != "assistant":
                continue

            content = get_message_content(item)

        elif isinstance(item, (list, tuple)) and len(item) >= 2:

            content = get_message_content(item[1])

        else:
            continue

        first_source = content.split("### Source 2")[0]

        provision_match = re.search(
            r"Provision:\s*\n?\s*(Article|Section)\s+([0-9]+[A-Z]?)",
            first_source,
            re.IGNORECASE
        )

        if provision_match:
            return (
                f"{provision_match.group(1)} "
                f"{provision_match.group(2).upper()}"
            )

    return ""


def rewrite_followup_query(message, history):

    has_direct_reference = re.search(
        r"\b(article|section)\s+\d+[A-Z]?\b",
        message,
        re.IGNORECASE
    )

    if has_direct_reference:
        return message

    message_lower = message.lower()

    followup_keywords = [
        "it",
        "this",
        "that",
        "can it",
        "is it",
        "does it",
        "what about it",
        "explain it",
        "serious crime",
        "means"
    ]

    is_followup = any(
        keyword in message_lower
        for keyword in followup_keywords
    )

    if not is_followup:
        return message

    last_reference = extract_last_legal_reference(
        history
    )

    if not last_reference:
        return message

    return f"{message} about {last_reference}"


def source_limit_for_query(query):

    if re.search(
        r"\bwhat\s+is\s+article\s+\d+[A-Z]?\b",
        query,
        re.IGNORECASE
    ):
        return 1

    return 2


def build_context_from_docs(docs):

    return "\n\n".join([

        f"""
Law:
{doc.metadata.get("law_name", "Unknown Legal Document")}

Provision:
{doc.metadata.get("provision_type", "Provision")} {doc.metadata.get("article_number") or doc.metadata.get("section_number") or "N/A"}

Title:
{doc.metadata.get("article_title") or doc.metadata.get("section_title") or "N/A"}

Content:
{doc.page_content}
"""

        for doc in docs
    ])


def extract_target_article(query):

    matches = re.findall(
        r"\barticle\s+(\d+[A-Z]?)\b",
        query,
        re.IGNORECASE
    )

    if not matches:
        return None

    return matches[-1].upper()


def is_suspension_query(query):

    query_lower = query.lower()

    return (
        "suspend" in query_lower
        or "suspended" in query_lower
        or "emergency" in query_lower
    )


def extract_excluded_articles_from_text(text):

    excluded_articles = set()

    matches = re.findall(
        r"except\s+articles?\s+([0-9A-Za-z,\sand]+)",
        text,
        re.IGNORECASE
    )

    for match in matches:

        numbers = re.findall(
            r"\d+[A-Z]?",
            match,
            re.IGNORECASE
        )

        for number in numbers:
            excluded_articles.add(
                number.upper()
            )

    return excluded_articles


def get_article_359_doc(docs):

    for doc in docs:

        article_number = str(
            doc.metadata.get("article_number", "")
        )

        if article_number == "359":
            return doc

    return None


def get_suspension_answer(query, docs):

    if not is_suspension_query(query):
        return None

    target_article = extract_target_article(
        query
    )

    if not target_article:
        return None

    article_359_doc = get_article_359_doc(
        docs
    )

    if not article_359_doc:
        return None

    excluded_articles = extract_excluded_articles_from_text(
        article_359_doc.page_content
    )

    if target_article in excluded_articles:

        return (
            f"No, Article {target_article} cannot be suspended during an emergency. "
            f"Article 359 allows suspension of enforcement of certain Part III rights, "
            f"but it expressly excludes Article {target_article}."
        )

    return (
        f"Yes, enforcement of Article {target_article} can be suspended during an emergency "
        f"if it is included in a Presidential order under Article 359. "
        f"Article 359 excludes only Articles "
        f"{', '.join(sorted(excluded_articles))}."
    )


def format_source(doc, index):

    law_name = doc.metadata.get(
        "law_name",
        doc.metadata.get(
            "source_file",
            "Unknown Legal Document"
        )
    )

    provision_type = doc.metadata.get(
        "provision_type",
        "provision"
    )

    if provision_type == "article":

        number = doc.metadata.get(
            "article_number",
            "N/A"
        )

        title = doc.metadata.get(
            "article_title",
            "N/A"
        )

        label = "Article"

    elif provision_type == "section":

        number = doc.metadata.get(
            "section_number",
            "N/A"
        )

        title = doc.metadata.get(
            "section_title",
            "N/A"
        )

        label = "Section"

    else:

        number = (
            doc.metadata.get("article_number")
            or doc.metadata.get("section_number")
            or "N/A"
        )

        title = (
            doc.metadata.get("article_title")
            or doc.metadata.get("section_title")
            or "N/A"
        )

        label = "Provision"

    return f"""
### Source {index}

Law:
{law_name}

Provision:
{label} {number}

Title:
{title}

Content:
{doc.page_content[:500]}
"""


def legal_chatbot(message, history):

    standalone_query = rewrite_followup_query(
        message,
        history
    )

    docs = hybrid_retrieve(
        standalone_query
    )

    source_limit = 1

    precise_docs = docs[:source_limit]

    deterministic_answer = get_suspension_answer(
        standalone_query,
        docs
    )

    if deterministic_answer:

        answer = deterministic_answer

        article_359_doc = get_article_359_doc(
            docs
        )

        if article_359_doc:
            precise_docs = [
                article_359_doc
            ]

    else:

        context = build_context_from_docs(
            precise_docs[:1]
        )

        prompt = build_legal_prompt(
            context,
            standalone_query
        )

        answer = generate_response(
            prompt
        )

    formatted_sources = "\n\n".join([
        format_source(doc, i + 1)
        for i, doc in enumerate(precise_docs)
    ])

    return f"""
{answer}

---

## Retrieved Legal Sources

{formatted_sources}
"""


chat_interface = gr.ChatInterface(

    fn=legal_chatbot,

    title="AI Legal Advisor",

    description=(
        "Conversational legal assistant powered by Hybrid RAG"
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


if __name__ == "__main__":
    chat_interface.launch()