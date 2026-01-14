"""Part 1: RAG Chat with SAP HANA Cloud Vector Engine (Complete)

This script provides a chat interface that retrieves relevant document
chunks from HANA and uses them to answer questions.

Run with:
    uv run python chat_documents.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from hdbcli import dbapi
from langchain_hana import HanaDB
from gen_ai_hub.proxy.langchain.init_models import init_llm, init_embedding_model

# Load environment variables from the repo root .env file
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Configuration from environment
MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
EMBEDDING_MODEL = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-3-small")
TABLE_NAME = os.getenv("HANA_TABLE_NAME", "DEALCRAFTER_DOCS")
TOP_K = int(os.getenv("RAG_TOP_K", "5"))


def get_hana_connection():
    """Create a connection to SAP HANA Cloud."""
    # Validate required environment variables
    address = os.getenv("HANA_DB_ADDRESS")
    user = os.getenv("HANA_DB_USER")
    password = os.getenv("HANA_DB_PASSWORD")
    
    if not address:
        raise ValueError("HANA_DB_ADDRESS environment variable is required")
    if not user:
        raise ValueError("HANA_DB_USER environment variable is required")
    if not password:
        raise ValueError("HANA_DB_PASSWORD environment variable is required")
    
    return dbapi.connect(
        address=address,
        port=int(os.getenv("HANA_DB_PORT", "443")),
        user=user,
        password=password,
        autocommit=True,
    )


def main():
    """Run an interactive RAG chat session."""
    
    print("📚 Starting RAG Chat")
    print("Type your questions about the ingested documents.")
    print("Press Enter on empty line to exit.\n")
    
    # Set up the vector store and retriever
    embeddings = init_embedding_model(EMBEDDING_MODEL)
    connection = get_hana_connection()
    db = HanaDB(embedding=embeddings, connection=connection, table_name=TABLE_NAME)
    retriever = db.as_retriever(search_kwargs={"k": TOP_K})
    
    # Initialize the LLM
    llm = init_llm(MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
    
    print(f"✅ Connected to HANA table '{TABLE_NAME}' with {TOP_K} chunks per query\n")
    
    # Chat loop
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
            
        if not question:
            print("Goodbye!")
            break
        
        # Retrieve relevant document chunks
        docs = retriever.invoke(question)
        
        if not docs:
            print("Assistant: I couldn't find any relevant information in the documents.\n")
            continue
        
        context = "\n\n---\n\n".join(doc.page_content for doc in docs)
        
        # Create prompt with context
        prompt = f"""Based on the following context from the documents, answer the question.
If the answer is not in the context, say so. Where possible cite the source(s) at the end of the answer using footnote numbers.

Context:
{context}

Question: {question}

Answer:"""
        
        # Stream the response
        print("Assistant: ", end="", flush=True)
        for chunk in llm.stream(prompt):
            content = getattr(chunk, "content", str(chunk))
            print(content, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    main()
