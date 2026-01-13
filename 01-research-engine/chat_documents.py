"""Part 1: RAG Chat with SAP HANA Cloud Vector Engine

This script provides a chat interface that retrieves relevant document
chunks from HANA and uses them to answer questions.

Run with:
    uv run python chat_documents.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from hdbcli import dbapi

# Load environment variables from the repo root .env file
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Configuration from environment
MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
EMBEDDING_MODEL = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-3-small")
TABLE_NAME = os.getenv("HANA_TABLE_NAME", "DEALCRAFTER_DOCS")
TOP_K = int(os.getenv("RAG_TOP_K", "5"))

COMPANY_NAME = os.getenv("COMPANY_NAME", "the company")


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
    
    print(f"📚 Starting RAG Chat for {COMPANY_NAME}")
    print("Type your questions about the ingested documents.")
    print("Press Enter on empty line to exit.\n")
    
    # ==========================================================================
    # EXERCISE 2a: Set up the vector store and retriever
    # ==========================================================================
    #
    # TODO 1: Initialize the embedding model
    # Hint: from gen_ai_hub.proxy.langchain.init_models import init_embedding_model
    # Hint: embeddings = init_embedding_model(EMBEDDING_MODEL)
    #
    # TODO 2: Connect to HANA and create the vector store
    # Hint: from langchain_hana import HanaDB
    # Hint: connection = get_hana_connection()
    # Hint: db = HanaDB(embedding=embeddings, connection=connection, table_name=TABLE_NAME)
    #
    # TODO 3: Create a retriever
    # Hint: retriever = db.as_retriever(search_kwargs={"k": TOP_K})
    #
    # ==========================================================================
    
    raise NotImplementedError("Exercise 2a: Set up the vector store retriever")
    
    # ==========================================================================
    # EXERCISE 2b: Initialize the LLM
    # ==========================================================================
    #
    # TODO 4: Initialize the LLM
    # Hint: from gen_ai_hub.proxy.langchain.init_models import init_llm
    # Hint: llm = init_llm(MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
    #
    # ==========================================================================
    
    raise NotImplementedError("Exercise 2b: Initialize the LLM")
    
    # Chat loop
    while True:
        question = input("You: ").strip()
        if not question:
            print("Goodbye!")
            break
        
        # ======================================================================
        # EXERCISE 2c: Retrieve context and generate answer
        # ======================================================================
        #
        # TODO 5: Retrieve relevant document chunks
        # Hint: docs = retriever.invoke(question)
        # Hint: context = "\n\n---\n\n".join(doc.page_content for doc in docs)
        #
        # TODO 6: Create a prompt with context
        # Hint: prompt = f"""Based on the following context, answer the question.
        #
        # Context:
        # {context}
        #
        # Question: {question}
        # """
        #
        # TODO 7: Get and print the response (with streaming)
        # Hint: print("Assistant: ", end="", flush=True)
        # Hint: for chunk in llm.stream(prompt):
        # Hint:     print(chunk.content, end="", flush=True)
        # Hint: print()
        #
        # ======================================================================
        
        raise NotImplementedError("Exercise 2c: Implement RAG response")


if __name__ == "__main__":
    main()
