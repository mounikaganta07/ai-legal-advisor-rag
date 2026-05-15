from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader
)

import os

RAW_DATA_PATH = "data/legal_docs"

def load_legal_documents():

    documents = []

    print("Loading legal documents...")

    for file in os.listdir(RAW_DATA_PATH):

        file_path = os.path.join(
            RAW_DATA_PATH,
            file
        )

        if file.endswith(".pdf"):

            loader = PyPDFLoader(file_path)

            loaded_docs = loader.load()

        elif file.endswith(".txt"):

            loader = TextLoader(
                file_path,
                encoding="utf-8"
            )

            loaded_docs = loader.load()

        else:
            continue

        for doc in loaded_docs:

            doc.metadata["source_file"] = file

            doc.metadata["document_type"] = (
                "constitution"
                if "constitution" in file.lower()
                else "legal_document"
            )

        documents.extend(loaded_docs)

        print(f"Loaded: {file}")

    return documents