import sys 
import os
from PyPDF2 import PdfReader
from openai import OpenAI
import httpx

#BASE_URL = "myurl.com"

API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_OPENAI_API_KEY = os.getenv("CHROMA_OPENAI_API_KEY")

#CA_BUNDLE_PATH = os.getenv("CA_BUNDLE_PATH")


# -------- Load PDF Documents --------

def load_pdf_docs(file_paths):
    documents = []
    for path in file_paths:
        reader = PdfReader(path)
        full_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text and text.strip():
                full_text.append(text)
        documents.append("\n".join(full_text))
    return documents

# Example list of PDF document paths
pdf_doc_paths = [
    "knowledgebase/telematics-doc-1.pdf",
    "knowledgebase/telematics-doc-2.pdf",
    "knowledgebase/telematics-doc-3.pdf"
]

# Load and assign unique IDs
documents = load_pdf_docs(pdf_doc_paths)
doc_ids = [f"doc_{i}" for i in range(len(documents))]

# -------- ChromaDB Setup --------

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_db"))
client = chromadb.EphemeralClient()
collection = client.get_or_create_collection(name="rag_docs")

# OpenAI Embedding Function
embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
    api_key=API_KEY,
    model_name="text-embedding-ada-002"
)

# Add to ChromaDB
collection.add(documents=documents, ids=doc_ids)

# -------- Retrieval + RAG Generation --------

def retrieve_context(query, k=2):
    results = collection.query(query_texts=[query], n_results=k)
    return results['documents'][0]  # List of top-k documents

def generate_answer(query):
    context = retrieve_context(query)
    prompt = (
        "Answer the question based on the context below:\n\n"
        f"Context:\n{chr(10).join(context)}\n\n"
        f"Question: {query}\nAnswer:"
    )
    
    # Initialize http client
    #http_client = httpx.Client(verify=CA_BUNDLE_PATH)

    # Initialize OpenAI client
    client = OpenAI(
        #base_url=BASE_URL,
        api_key=API_KEY,
        #http_client=http_client,
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who answers based only on provided context."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    # Close the http client
    http_client.close()
    return response.choices[0].message.content

# -------- Example Query --------

if __name__ == "__main__":
    query = "Please provide a list of ways a third party provider could sell telematics data to a P&C insurance company for profit"
    answer = generate_answer(query)
    print("Question:", query)
    print("Answer:", answer)
