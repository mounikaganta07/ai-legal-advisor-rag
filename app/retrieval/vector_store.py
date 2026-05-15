from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from app.utils.config import (
    EMBEDDING_MODEL,
    VECTOR_DB_PATH
)

embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

def load_vectorstore():

    vectorstore = FAISS.load_local(
        VECTOR_DB_PATH,
        embedding_model,
        allow_dangerous_deserialization=True
    )

    return vectorstore