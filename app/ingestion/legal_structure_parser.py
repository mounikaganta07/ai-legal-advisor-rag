import re

from langchain_core.documents import (
    Document
)

def extract_articles(documents):

    structured_docs = []

    article_pattern = re.compile(

        r'^\s*(\d+[A-Z]?)\.\s+([A-Z][^\n]{5,})',

        re.MULTILINE
    )

    for doc in documents:

        text = doc.page_content

        matches = list(
            article_pattern.finditer(text)
        )

        if not matches:
            continue

        for i in range(len(matches)):

            start = matches[i].start()

            end = (
                matches[i + 1].start()
                if i + 1 < len(matches)
                else len(text)
            )

            article_text = text[start:end].strip()

            if len(article_text.split()) < 40:
                continue

            article_number = matches[i].group(1)

            article_title = matches[i].group(2)

            structured_doc = Document(

                page_content=article_text,

                metadata={

                    "article_number":
                    article_number,

                    "article_title":
                    article_title,

                    "source_file":
                    doc.metadata.get(
                        "source_file",
                        "unknown"
                    )
                }
            )

            structured_docs.append(
                structured_doc
            )

    print(
        f"Extracted {len(structured_docs)} structured articles"
    )

    return structured_docs