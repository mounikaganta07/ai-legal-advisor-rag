import re

def enrich_metadata(chunks):

    print("Enhancing metadata...")

    for i, chunk in enumerate(chunks):

        text = chunk.page_content

        article_match = re.search(
            r"Article\s+\d+",
            text,
            re.IGNORECASE
        )

        section_match = re.search(
            r"Section\s+\d+",
            text,
            re.IGNORECASE
        )

        if article_match:

            chunk.metadata["reference"] = (
                article_match.group()
            )

        elif section_match:

            chunk.metadata["reference"] = (
                section_match.group()
            )

        else:

            chunk.metadata["reference"] = (
                "Unknown"
            )

        chunk.metadata["chunk_id"] = i

    print("Metadata enrichment completed")

    return chunks