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
    search_type="mmr",
    search_kwargs={
        "k": 15,
        "fetch_k": 30
    }
)

all_docs = list(
    vectorstore.docstore._dict.values()
)


def normalize_text(text):
    return re.sub(
        r"\s+",
        " ",
        str(text).lower()
    ).strip()


def tokenize(text):
    return re.findall(
        r"[a-zA-Z0-9]+",
        normalize_text(text)
    )


bm25_corpus = [
    tokenize(
        doc.metadata.get("law_name", "")
        + " "
        + doc.metadata.get("article_title", "")
        + " "
        + doc.metadata.get("section_title", "")
        + " "
        + doc.page_content
    )
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


STOPWORDS = {
    "what",
    "is",
    "are",
    "the",
    "a",
    "an",
    "can",
    "be",
    "under",
    "for",
    "of",
    "to",
    "in",
    "on",
    "by",
    "and",
    "or",
    "it",
    "this",
    "that",
    "who",
    "does",
    "do",
    "with",
    "from"
}


def is_noisy_chunk(text):

    text = normalize_text(text)

    noise_matches = sum(
        pattern in text
        for pattern in NOISE_PATTERNS
    )

    if noise_matches >= 2:
        return True

    if len(text.split()) < 20:
        return True

    return False


LEGAL_QUERY_EXPANSIONS = {
    "personal liberty": (
        "life and personal liberty article 21"
    ),

    "life and liberty": (
        "life and personal liberty article 21"
    ),

    "writs": (
        "constitutional remedies supreme court writs article 32 habeas corpus mandamus prohibition quo warranto certiorari"
    ),

    "constitutional remedies": (
        "supreme court writs article 32"
    ),

    "directive principles": (
        "directive principles of state policy article 37 welfare governance"
    ),

    "welfare governance": (
        "directive principles state policy article 37"
    ),

    "international treaties": (
        "international agreements parliament law article 253"
    ),

    "international agreements": (
        "parliament law treaties article 253"
    ),

    "states follow parliamentary laws": (
        "obligation of states and union article 256"
    ),

    "suspended": (
        "emergency suspension of fundamental rights article 359"
    ),

    "suspend": (
        "emergency suspension of fundamental rights article 359"
    ),

    "emergency": (
        "emergency suspension fundamental rights article 359"
    ),

    "dowry prohibition officer": (
        "dowry prohibition officer section 8B Dowry Prohibition Act"
    ),

    "dowry officer": (
        "dowry prohibition officer section 8B Dowry Prohibition Act"
    ),

    "penalty for taking dowry": (
        "penalty for giving or taking dowry section 3 Dowry Prohibition Act"
    ),

    "taking dowry": (
        "taking dowry giving dowry penalty section 3 Dowry Prohibition Act"
    ),

    "giving dowry": (
        "giving dowry taking dowry penalty section 3 Dowry Prohibition Act"
    ),

    "demanding dowry": (
        "demanding dowry dowry prohibition officer section 8B Dowry Prohibition Act"
    ),

    "demand dowry": (
        "demanding dowry dowry prohibition officer section 8B Dowry Prohibition Act"
    ),

    "extra dowry": (
        "demanding dowry dowry prohibition officer section 8B penalty section 3 Dowry Prohibition Act"
    ),

    "domestic violence": (
        "domestic violence definition physical abuse sexual abuse verbal emotional abuse economic abuse section 3 Protection of Women from Domestic Violence Act"
    ),

    "emotional abuse": (
        "verbal and emotional abuse domestic violence definition section 3 Protection of Women from Domestic Violence Act"
    ),

    "verbal abuse": (
        "verbal and emotional abuse domestic violence definition section 3 Protection of Women from Domestic Violence Act"
    ),

    "economic abuse": (
        "economic abuse domestic violence definition section 3 Protection of Women from Domestic Violence Act"
    ),

    "physical abuse": (
        "physical abuse domestic violence definition section 3 Protection of Women from Domestic Violence Act"
    ),

    "sexual abuse": (
        "sexual abuse domestic violence definition section 3 Protection of Women from Domestic Violence Act"
    ),

    "protection officer": (
        "protection officer section 8 section 9 Protection of Women from Domestic Violence Act"
    ),

    "shelter": (
        "shelter home medical examination protection officer section 9 domestic violence"
    ),

    "medical help": (
        "medical examination protection officer section 9 domestic violence"
    )
}


LEGAL_RULE_ARTICLES = {
    "suspend": ["359"],
    "suspended": ["359"],
    "emergency": ["359"],
    "fundamental rights": ["359", "32"],
    "life and personal liberty": ["21"],
    "personal liberty": ["21"],
    "constitutional remedies": ["32"],
    "writs": ["32"],
    "directive principles": ["37"],
    "welfare governance": ["37", "38", "39"],
    "international treaties": ["253"],
    "international agreements": ["253"],
    "parliamentary laws": ["256"],
    "states follow": ["256"]
}


LEGAL_RULE_SECTIONS = {
    "dowry prohibition officer": [
        ("dowry", "8B")
    ],

    "dowry officer": [
        ("dowry", "8B")
    ],

    "penalty for taking dowry": [
        ("dowry", "3")
    ],

    "taking dowry": [
        ("dowry", "3")
    ],

    "giving dowry": [
        ("dowry", "3")
    ],

    "demanding dowry": [
        ("dowry", "8B")
    ],

    "demand dowry": [
        ("dowry", "8B")
    ],

    "extra dowry": [
        ("dowry", "8B"),
        ("dowry", "3")
    ]
}


def expand_query(query):

    expanded_query = normalize_text(query)

    for phrase, expansion in LEGAL_QUERY_EXPANSIONS.items():

        if phrase in expanded_query:

            expanded_query += (
                " " + expansion
            )

    return expanded_query


def get_article_docs(article_numbers):

    matched_docs = []

    for article_number in article_numbers:

        for doc in all_docs:

            doc_article = str(
                doc.metadata.get("article_number", "")
            ).upper()

            doc_type = str(
                doc.metadata.get("provision_type", "")
            ).lower()

            if (
                doc_type == "article"
                and doc_article == article_number.upper()
            ):

                matched_docs.append(doc)

    return matched_docs


def get_section_docs(section_rules):

    matched_docs = []

    for law_keyword, section_number in section_rules:

        for doc in all_docs:

            law_name = normalize_text(
                doc.metadata.get("law_name", "")
            )

            source_file = normalize_text(
                doc.metadata.get("source_file", "")
            )

            doc_section = str(
                doc.metadata.get("section_number", "")
            ).upper()

            doc_type = str(
                doc.metadata.get("provision_type", "")
            ).lower()

            law_match = (
                law_keyword in law_name
                or law_keyword in source_file
            )

            if (
                doc_type == "section"
                and doc_section == section_number.upper()
                and law_match
            ):

                matched_docs.append(doc)

    return matched_docs


def get_rule_based_article_docs(query):

    query_lower = normalize_text(query)

    article_numbers = []

    for keyword, articles in LEGAL_RULE_ARTICLES.items():

        if keyword in query_lower:

            article_numbers.extend(articles)

    unique_article_numbers = []

    seen = set()

    for article in article_numbers:

        if article not in seen:

            seen.add(article)
            unique_article_numbers.append(article)

    return get_article_docs(unique_article_numbers)


def get_rule_based_section_docs(query):

    query_lower = normalize_text(query)

    section_rules = []

    for keyword, rules in LEGAL_RULE_SECTIONS.items():

        if keyword in query_lower:

            section_rules.extend(rules)

    unique_rules = []

    seen = set()

    for rule in section_rules:

        if rule not in seen:

            seen.add(rule)
            unique_rules.append(rule)

    return get_section_docs(unique_rules)


def get_exact_article_docs(query):

    article_matches = re.findall(
        r"\barticle\s+(\d+[A-Z]?)\b",
        query,
        re.IGNORECASE
    )

    if not article_matches:
        return []

    return get_article_docs(article_matches)


def get_exact_section_docs(query):

    section_matches = re.findall(
        r"\bsection\s+(\d+[A-Z]?)\b",
        query,
        re.IGNORECASE
    )

    if not section_matches:
        return []

    matched_docs = []

    for section_number in section_matches:

        for doc in all_docs:

            doc_section = str(
                doc.metadata.get("section_number", "")
            ).upper()

            doc_type = str(
                doc.metadata.get("provision_type", "")
            ).lower()

            if (
                doc_type == "section"
                and doc_section == section_number.upper()
            ):

                matched_docs.append(doc)

    return matched_docs


def score_doc(query, doc):

    query_lower = query.lower()

    query_tokens = [
        token
        for token in tokenize(query)
        if token not in STOPWORDS
    ]

    doc_text = normalize_text(
        doc.metadata.get("law_name", "")
        + " "
        + doc.metadata.get("article_title", "")
        + " "
        + doc.metadata.get("section_title", "")
        + " "
        + doc.page_content
    )

    doc_title = normalize_text(
        doc.metadata.get("article_title", "")
        + " "
        + doc.metadata.get("section_title", "")
    )

    score = 0

    for token in query_tokens:
        if token in doc_text:
            score += 3

    provision_type = str(
        doc.metadata.get("provision_type", "")
    ).lower()

    article_number = str(
        doc.metadata.get("article_number", "")
    ).lower()

    section_number = str(
        doc.metadata.get("section_number", "")
    ).lower()

    law_name = normalize_text(
        doc.metadata.get("law_name", "")
    )

    if "article" in query_lower and provision_type == "article":
        score += 10

    if "section" in query_lower and provision_type == "section":
        score += 10

    article_matches = re.findall(
        r"\barticle\s+(\d+[A-Z]?)\b",
        query,
        re.IGNORECASE
    )

    if article_matches and article_number in [
        item.lower()
        for item in article_matches
    ]:
        score += 50

    section_matches = re.findall(
        r"\bsection\s+(\d+[A-Z]?)\b",
        query,
        re.IGNORECASE
    )

    if section_matches and section_number in [
        item.lower()
        for item in section_matches
    ]:
        score += 30

    if "dowry" in query_lower and "dowry" in law_name:
        score += 25

    if (
        "domestic violence" in query_lower
        or "emotional abuse" in query_lower
        or "verbal abuse" in query_lower
        or "physical abuse" in query_lower
        or "sexual abuse" in query_lower
        or "economic abuse" in query_lower
    ) and "domestic violence" in law_name:
        score += 25

    if (
        "emotional abuse" in query_lower
        or "verbal abuse" in query_lower
        or "physical abuse" in query_lower
        or "sexual abuse" in query_lower
        or "economic abuse" in query_lower
    ) and section_number == "3":
        score += 40

    if "writ" in query_lower and article_number == "32":
        score += 40

    penalty_intent_words = [
        "punishment",
        "penalty",
        "charges",
        "sentence",
        "imprisonment",
        "fine",
        "punishable"
    ]

    officer_intent_words = [
        "officer",
        "duties",
        "functions",
        "powers",
        "can do",
        "role"
    ]

    suspension_intent_words = [
        "suspend",
        "suspended",
        "suspension",
        "emergency"
    ]

    protection_help_words = [
        "protection",
        "protect",
        "help",
        "relief",
        "shelter",
        "medical",
        "assistance"
    ]

    has_penalty_intent = any(
        word in query_lower
        for word in penalty_intent_words
    )

    has_officer_intent = any(
        word in query_lower
        for word in officer_intent_words
    )

    has_suspension_intent = any(
        word in query_lower
        for word in suspension_intent_words
    )

    has_protection_help_intent = any(
        word in query_lower
        for word in protection_help_words
    )

    if has_penalty_intent:
        if (
            "penalty" in doc_title
            or "punishment" in doc_title
            or "punishable" in doc_text
            or "imprisonment" in doc_text
            or "fine" in doc_text
        ):
            score += 45

        if "officer" in doc_title:
            score -= 25

    if has_officer_intent:
        if (
            "officer" in doc_title
            or "duties" in doc_title
            or "functions" in doc_title
            or "powers" in doc_text
        ):
            score += 45

    if has_suspension_intent:
        if article_number == "359":
            score += 70

        if article_number in ["19", "20", "21"]:
            score -= 20

    if (
        has_protection_help_intent
        and "domestic violence" in law_name
    ):
        if section_number == "9":
            score += 60

        if section_number == "3":
            score -= 15

    return score

def rerank_docs(query, docs):

    scored_docs = []

    for index, doc in enumerate(docs):

        score = score_doc(
            query,
            doc
        )

        scored_docs.append(
            (
                score,
                -index,
                doc
            )
        )

    scored_docs.sort(
        key=lambda item: (
            item[0],
            item[1]
        ),
        reverse=True
    )

    return [
        item[2]
        for item in scored_docs
    ]


def hybrid_retrieve(query):

    expanded_query = expand_query(
        query
    )

    exact_article_docs = get_exact_article_docs(
        expanded_query
    )

    exact_section_docs = get_exact_section_docs(
        expanded_query
    )

    rule_based_article_docs = get_rule_based_article_docs(
        expanded_query
    )

    rule_based_section_docs = get_rule_based_section_docs(
        expanded_query
    )

    semantic_docs = retriever.invoke(
        expanded_query
    )

    tokenized_query = tokenize(
        expanded_query
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

    combined_docs = (
        rule_based_section_docs
        + exact_article_docs
        + rule_based_article_docs
        + exact_section_docs
        + semantic_docs
        + bm25_docs
    )

    unique_docs = []

    seen = set()

    for doc in combined_docs:

        provision_type = str(
            doc.metadata.get("provision_type", "")
        )

        article_number = str(
            doc.metadata.get("article_number", "")
        )

        section_number = str(
            doc.metadata.get("section_number", "")
        )

        law_name = str(
            doc.metadata.get("law_name", "")
        )

        content = doc.page_content

        unique_key = (
            law_name,
            provision_type,
            article_number,
            section_number,
            content[:120]
        )

        if unique_key in seen:
            continue

        if is_noisy_chunk(content):
            continue

        seen.add(unique_key)

        unique_docs.append(doc)

    reranked_docs = rerank_docs(
        query,
        unique_docs
    )

    return reranked_docs[:TOP_K_RESULTS]