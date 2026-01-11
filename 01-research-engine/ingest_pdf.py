"""Part 1: PDF Ingestion into SAP HANA Cloud Vector Engine

This script loads a PDF document, chunks the text, generates embeddings,
and stores them in SAP HANA Cloud for RAG queries.

Run with:
    uv run python ingest_pdf.py <path-to-pdf>

Example:
    uv run python ingest_pdf.py ../rag-material/sakura_internet/factbook.pdf
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from the repo root .env file
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Configuration from environment
CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))
EMBEDDING_MODEL = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-3-small")
TABLE_NAME = os.getenv("HANA_TABLE_NAME", "DEALCRAFTER_DOCS")


def get_hana_connection():
    """Create a connection to SAP HANA Cloud."""
    from hdbcli import dbapi
    
    return dbapi.connect(
        address=os.getenv("HANA_DB_ADDRESS"),
        port=int(os.getenv("HANA_DB_PORT", "443")),
        user=os.getenv("HANA_DB_USER"),
        password=os.getenv("HANA_DB_PASSWORD"),
        autocommit=True,
        sslValidateCertificate=False,
    )


def main():
    """Load PDF, chunk, embed, and store in HANA."""
    
    # Get PDF path from command line
    if len(sys.argv) < 2:
        print("Usage: uv run python ingest_pdf.py <path-to-pdf>")
        print("Example: uv run python ingest_pdf.py ../rag-material/sakura_internet/factbook.pdf")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)
    
    print(f"📄 Loading PDF: {pdf_path.name}")
    
    # ==========================================================================
    # EXERCISE 1a: Load PDF and extract text
    # ==========================================================================
    #
    # TODO 1: Import PdfReader from pypdf
    # Hint: from pypdf import PdfReader
    #
    # TODO 2: Load the PDF and extract text from all pages
    # Hint: reader = PdfReader(pdf_path)
    # Hint: text = "\n".join(page.extract_text() or "" for page in reader.pages)
    #
    # ==========================================================================
    
    raise NotImplementedError("Exercise 1a: Load the PDF using pypdf")
    
    # ==========================================================================
    # EXERCISE 1b: Chunk the text
    # ==========================================================================
    #
    # TODO 3: Import RecursiveCharacterTextSplitter
    # Hint: from langchain_text_splitters import RecursiveCharacterTextSplitter
    #
    # TODO 4: Create a splitter with CHUNK_SIZE and CHUNK_OVERLAP
    # Hint: splitter = RecursiveCharacterTextSplitter(
    #           chunk_size=CHUNK_SIZE,
    #           chunk_overlap=CHUNK_OVERLAP,
    #       )
    #
    # TODO 5: Create documents from the text
    # Hint: from langchain_core.documents import Document
    # Hint: docs = splitter.split_documents([
    #           Document(page_content=text, metadata={"source": str(pdf_path)})
    #       ])
    #
    # ==========================================================================
    
    raise NotImplementedError("Exercise 1b: Chunk the text")
    
    # ==========================================================================
    # EXERCISE 1c: Store in HANA with embeddings
    # ==========================================================================
    #
    # TODO 6: Initialize the embedding model
    # Hint: from gen_ai_hub.proxy.langchain.init_models import init_embedding_model
    # Hint: embeddings = init_embedding_model(EMBEDDING_MODEL)
    #
    # TODO 7: Connect to HANA and create the vector store
    # Hint: from langchain_hana import HanaDB
    # Hint: connection = get_hana_connection()
    # Hint: db = HanaDB(embedding=embeddings, connection=connection, table_name=TABLE_NAME)
    #
    # TODO 8: Delete existing chunks from this source (avoid duplicates) and add new ones
    # Hint: db.delete(filter={"source": str(pdf_path)})
    # Hint: db.add_documents(docs)
    #
    # TODO 9: Print success message
    # Hint: print(f"✅ Ingested {len(docs)} chunks from {pdf_path.name} into table '{TABLE_NAME}'")
    #
    # ==========================================================================
    
    raise NotImplementedError("Exercise 1c: Store embeddings in HANA")


if __name__ == "__main__":
    main()
