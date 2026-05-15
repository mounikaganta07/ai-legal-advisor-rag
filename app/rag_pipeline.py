from app.retrieval.hybrid_retriever import (
    hybrid_retrieve
)

from app.prompts.legal_prompt import (
    build_legal_prompt
)

from app.llm.openrouter_client import (
    generate_response
)

while True:

    query = input(
        "\nAsk a legal question: "
    )

    if query.lower() == "exit":
        break

    docs = hybrid_retrieve(
        query
    )

    context = "\n\n".join([
        doc.page_content
        for doc in docs
    ])

    prompt = build_legal_prompt(
        context,
        query
    )

    answer = generate_response(
        prompt
    )

    print("\nANSWER:\n")

    print(answer)

    print(
        "\n-----------------------------------"
    )

    print(
        "\nRETRIEVED SOURCES:\n"
    )

    for i, doc in enumerate(docs):

        print(
            f"""
Source {i+1}:

Article Number:
{doc.metadata.get('article_number', 'N/A')}

Title:
{doc.metadata.get('article_title', 'N/A')}

Content:
{doc.page_content[:700]}
"""
        )