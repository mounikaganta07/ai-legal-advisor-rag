import re

from rank_bm25 import BM25Okapi

from app.retrieval.vector_store import (
    load_vectorstore
)

from app.utils.config import (
    TOP_K_RESULTS
)

vectorstore = load_vectorstore()

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 10}
)

all_docs = list(
    vectorstore.docstore._dict.values()
)

bm25_corpus = [
    doc.page_content.split()
    for doc in all_docs
]

bm25 = BM25Okapi(
    bm25_corpus
)

NOISE_PATTERNS = [
    "amendment act",
    "omitted by",
    "inserted by",
    "subs. by",
    "w.e.f",
    "paragraph",
    "schedule",
    "cl.",
]

def is_noisy_chunk(text):

    text = text.lower()

    noise_matches = sum(
        pattern in text
        for pattern in NOISE_PATTERNS
    )

    if noise_matches >= 1:
        return True

    if text.strip().startswith((
        "1.",
        "2.",
        "3.",
        "4."
    )):
        return True

    if len(text.split()) < 25:
        return True

    return False

def hybrid_retrieve(query):

    exact_article_docs = []

    article_match = re.search(
        r'article\s+(\d+[A-Z]?)',
        query,
        re.IGNORECASE
    )

    if article_match:

        target_article = (
            article_match.group(1)
        )

        for doc in all_docs:

            article_number = doc.metadata.get(
                "article_number",
                ""
            )

            if (
                article_number.lower()
                ==
                target_article.lower()
            ):

                exact_article_docs.append(
                    doc
                )

    semantic_docs = retriever.invoke(
        query
    )

    tokenized_query = query.split()

    bm25_scores = bm25.get_scores(
        tokenized_query
    )

    top_bm25_indices = sorted(
        range(len(bm25_scores)),
        key=lambda i: bm25_scores[i],
        reverse=True
    )[:10]

    bm25_docs = [
        all_docs[i]
        for i in top_bm25_indices
    ]

    if exact_article_docs:

        combined_docs = exact_article_docs

    else:

        combined_docs = (
            semantic_docs
            +
            bm25_docs
        )

    unique_docs = []

    seen = set()

    for doc in combined_docs:

        content = doc.page_content

        if content in seen:
            continue

        if is_noisy_chunk(content):
            continue

        seen.add(content)

        unique_docs.append(doc)

    return unique_docs[:TOP_K_RESULTS]