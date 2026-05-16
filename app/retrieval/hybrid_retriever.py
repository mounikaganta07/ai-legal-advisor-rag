import re

from rank_bm25 import BM25Okapi

from app.retrieval.vector_store import (
    load_vectorstore
)

from app.utils.config import (
    TOP_K_RESULTS
)

# -----------------------------------
# LOAD VECTOR STORE
# -----------------------------------

vectorstore = load_vectorstore()

# -----------------------------------
# IMPROVED RETRIEVER
# -----------------------------------

retriever = vectorstore.as_retriever(

    search_type="mmr",

    search_kwargs={
        "k": 15,
        "fetch_k": 30
    }
)

# -----------------------------------
# LOAD ALL DOCUMENTS
# -----------------------------------

all_docs = list(
    vectorstore.docstore._dict.values()
)

# -----------------------------------
# BM25 SETUP
# -----------------------------------

bm25_corpus = [

    (
        (
            doc.metadata.get(
                "article_title",
                ""
            )
            +
            " "
            +
            doc.page_content
        ).split()
    )

    for doc in all_docs
]

bm25 = BM25Okapi(
    bm25_corpus
)

# -----------------------------------
# NOISE FILTERING
# -----------------------------------

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

# -----------------------------------
# QUERY EXPANSION
# -----------------------------------

LEGAL_QUERY_EXPANSIONS = {

    "personal liberty": (
        "life and personal liberty"
    ),

    "writs": (
        "constitutional remedies supreme court writs"
    ),

    "directive principles": (
        "governance state welfare principles"
    ),

    "emergency suspension": (
        "suspension of fundamental rights emergency"
    ),

    "international treaties": (
        "international agreements parliament law"
    ),

    "supreme court directly": (
        "constitutional remedies supreme court"
    )
}

def expand_query(query):

    expanded_query = query.lower()

    for phrase, expansion in (
        LEGAL_QUERY_EXPANSIONS.items()
    ):

        if phrase in expanded_query:

            expanded_query += (
                " " + expansion
            )

    return expanded_query

# -----------------------------------
# HYBRID RETRIEVAL
# -----------------------------------

def hybrid_retrieve(query):

    expanded_query = expand_query(
        query
    )

    exact_article_docs = []

    article_match = re.search(
        r'article\s+(\d+[A-Z]?)',
        expanded_query,
        re.IGNORECASE
    )

    # -----------------------------------
    # EXACT ARTICLE MATCH
    # -----------------------------------

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

    # -----------------------------------
    # SEMANTIC RETRIEVAL
    # -----------------------------------

    semantic_docs = retriever.invoke(
        expanded_query
    )

    # -----------------------------------
    # BM25 RETRIEVAL
    # -----------------------------------

    tokenized_query = (
        expanded_query.split()
    )

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

    # -----------------------------------
    # COMBINE RESULTS
    # -----------------------------------

    if exact_article_docs:

        combined_docs = (
            exact_article_docs
            +
            semantic_docs
            +
            bm25_docs
        )

    else:

        combined_docs = (
            semantic_docs
            +
            bm25_docs
        )

    # -----------------------------------
    # DEDUPLICATION
    # -----------------------------------

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