import re

from langchain_core.documents import Document


def detect_law_name(source_file):
    file_name = source_file.lower()

    if "constitution" in file_name:
        return "Constitution of India"

    if "dowry" in file_name:
        return "Dowry Prohibition Act, 1961"

    if "domestic" in file_name or "violence" in file_name:
        return "Protection of Women from Domestic Violence Act, 2005"

    return "Unknown Legal Document"


def detect_document_type(source_file):
    file_name = source_file.lower()

    if "constitution" in file_name:
        return "constitution"

    if "dowry" in file_name:
        return "dowry_law"

    if "domestic" in file_name or "violence" in file_name:
        return "domestic_violence_law"

    return "legal_document"


def clean_text(text):
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = re.sub(
        r"\s+([,.;:])",
        r"\1",
        text
    )

    return text.strip()


def normalize_newlines(text):
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\d+\[\s*(\d+[A-Z]?\.\s+[A-Z])",
        r"\n\1",
        text
    )

    text = re.sub(
        r"(?<!\n)(\d+[A-Z]?\.\s+[A-Z][A-Za-z ]{3,}?(?:—|-))",
        r"\n\1",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text


def combine_pages_by_source(documents):
    grouped = {}

    for doc in documents:
        source_file = doc.metadata.get(
            "source_file",
            "unknown"
        )

        if source_file not in grouped:
            grouped[source_file] = []

        grouped[source_file].append(
            doc.page_content
        )

    combined_docs = []

    for source_file, pages in grouped.items():
        combined_text = "\n".join(pages)

        combined_docs.append(
            Document(
                page_content=combined_text,
                metadata={
                    "source_file": source_file
                }
            )
        )

    return combined_docs


def extract_title(provision_text):
    title_match = re.match(
        r"^\s*\d+[A-Z]?\.\s+(.+?)(?:—|-|\.)",
        provision_text
    )

    if title_match:
        return title_match.group(1).strip()

    return provision_text[:120].strip()


def is_valid_constitution_article(article_number, article_text):
    text = article_text.lower()

    if len(article_text.split()) < 25:
        return False

    noisy_phrases = [
        "amendment of article",
        "substitution of article",
        "insertion of new article",
        "omitted by",
        "subs. by",
        "w.e.f.",
        "the constitution (",
    ]

    if any(phrase in text[:200] for phrase in noisy_phrases):
        return False

    title = extract_title(article_text).lower()

    if len(title) < 5:
        return False

    return True


def is_valid_act_section(section_number, section_text):
    text = section_text.lower()

    if len(section_text.split()) < 20:
        return False

    noisy_start_patterns = [
        r"^\d+[a-z]?\.\s*\d+\s*\(",
        r"^\d+[a-z]?\.\s*\d+\s*provided",
        r"^\d+[a-z]?\.\s*\d+\s*w\.e\.f",
        r"^\d+[a-z]?\.\s*\d+\s*subs",
    ]

    for pattern in noisy_start_patterns:
        if re.search(pattern, text):
            return False

    noisy_phrases = [
        "w.e.f.",
        "subs. by",
        "inserted by",
        "omitted by",
    ]

    noisy_count = sum(
        phrase in text[:250]
        for phrase in noisy_phrases
    )

    if noisy_count >= 2:
        return False

    title = extract_title(section_text).lower()

    if len(title) < 5:
        return False

    return True


def extract_constitution_articles(text, base_metadata):
    structured_docs = []

    text = normalize_newlines(text)

    article_pattern = re.compile(
        r"(?m)^\s*(\d+[A-Z]?)\.\s+(.+?)(?=\n\s*\d+[A-Z]?\.\s+|\Z)",
        re.DOTALL
    )

    matches = list(
        article_pattern.finditer(text)
    )

    for match in matches:
        article_number = match.group(1).strip()

        article_text = clean_text(
            match.group(0)
        )

        if not is_valid_constitution_article(
            article_number,
            article_text
        ):
            continue

        article_title = extract_title(
            article_text
        )

        metadata = base_metadata.copy()

        metadata.update({
            "law_name": "Constitution of India",
            "document_type": "constitution",
            "article_number": article_number,
            "article_title": article_title,
            "section_number": "",
            "section_title": "",
            "provision_type": "article"
        })

        structured_docs.append(
            Document(
                page_content=article_text,
                metadata=metadata
            )
        )

    return structured_docs


def extract_act_sections(text, base_metadata):
    structured_docs = []

    text = normalize_newlines(text)

    section_pattern = re.compile(
        r"(?m)^\s*(\d+[A-Z]?)\.\s+(.+?)(?=\n\s*\d+[A-Z]?\.\s+|\Z)",
        re.DOTALL
    )

    matches = list(
        section_pattern.finditer(text)
    )

    for match in matches:
        section_number = match.group(1).strip()

        section_text = clean_text(
            match.group(0)
        )

        if not is_valid_act_section(
            section_number,
            section_text
        ):
            continue

        section_title = extract_title(
            section_text
        )

        metadata = base_metadata.copy()

        metadata.update({
            "article_number": "",
            "article_title": "",
            "section_number": section_number,
            "section_title": section_title,
            "provision_type": "section"
        })

        structured_docs.append(
            Document(
                page_content=section_text,
                metadata=metadata
            )
        )

    return structured_docs


def extract_articles(documents):
    structured_docs = []

    combined_documents = combine_pages_by_source(
        documents
    )

    for doc in combined_documents:
        text = doc.page_content

        source_file = doc.metadata.get(
            "source_file",
            "unknown"
        )

        law_name = detect_law_name(
            source_file
        )

        document_type = detect_document_type(
            source_file
        )

        base_metadata = {
            "source_file": source_file,
            "law_name": law_name,
            "document_type": document_type
        }

        if document_type == "constitution":
            extracted_docs = extract_constitution_articles(
                text,
                base_metadata
            )

        else:
            extracted_docs = extract_act_sections(
                text,
                base_metadata
            )

        structured_docs.extend(
            extracted_docs
        )

    print(
        f"Extracted {len(structured_docs)} structured legal provisions"
    )

    return structured_docs