from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from app.utils.text_cleaner import (
    clean_legal_text
)

def process_and_chunk_documents(documents):

    print("Cleaning legal documents...")

    for doc in documents:

        doc.page_content = clean_legal_text(
            doc.page_content
        )

    print("Chunking legal documents...")

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=1500,

        chunk_overlap=300,

        separators=[
            "\n\n",
            "\n",
            ". ",
            " "
        ]
    )

    chunks = splitter.split_documents(
        documents
    )

    print(f"Generated {len(chunks)} chunks")

    return chunks