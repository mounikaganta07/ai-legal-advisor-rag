from langchain_community.vectorstores import (
    FAISS
)

from langchain_huggingface import (
    HuggingFaceEmbeddings
)

from app.ingestion.document_loader import (
    load_legal_documents
)

from app.ingestion.legal_structure_parser import (
    extract_articles
)

from app.ingestion.text_chunker import (
    process_and_chunk_documents
)

from app.ingestion.metadata_processor import (
    enrich_metadata
)

def build_vector_database():

    print("\nStarting legal ingestion pipeline...\n")

    documents = load_legal_documents()

    structured_docs = extract_articles(
        documents
    )

    chunks = process_and_chunk_documents(
        structured_docs
    )

    enriched_chunks = enrich_metadata(
        chunks
    )

    print("\nGenerating embeddings...\n")

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("\nBuilding FAISS vector database...\n")

    vectorstore = FAISS.from_documents(
        enriched_chunks,
        embedding_model
    )

    vectorstore.save_local("vector_db")

    print("\nVector database created successfully!")

if __name__ == "__main__":
    build_vector_database()