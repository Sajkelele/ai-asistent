from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from memory import load_documents

def create_vector_store():
    docs = load_documents()

    documents = [Document(page_content=d) for d in docs]

    embeddings = OpenAIEmbeddings()

    vectorstore = FAISS.from_documents(documents, embeddings)

    return vectorstore