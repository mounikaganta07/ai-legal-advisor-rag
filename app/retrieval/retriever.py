from app.retrieval.vector_store import load_vectorstore
from app.utils.config import TOP_K_RESULTS

vectorstore = load_vectorstore()

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": TOP_K_RESULTS}
)

def retrieve_documents(query):

    docs = retriever.invoke(query)

    return docs