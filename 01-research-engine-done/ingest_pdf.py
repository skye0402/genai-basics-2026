"""Part 1: PDF Ingestion into SAP HANA Cloud Vector Engine (Complete)

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
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_hana import HanaDB
from hdbcli import dbapi
from gen_ai_hub.proxy.langchain.init_models import init_embedding_model

# Load environment variables from the repo root .env file
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Configuration from environment
CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))
EMBEDDING_MODEL = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-3-small")
TABLE_NAME = os.getenv("HANA_TABLE_NAME", "DEALCRAFTER_DOCS")


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
    
    # Load PDF and extract text
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    
    if not text.strip():
        print("❌ No text extracted from PDF")
        sys.exit(1)
    
    print(f"   Extracted {len(text):,} characters from {len(reader.pages)} pages")
    
    # Chunk the text
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    docs = splitter.split_documents([
        Document(page_content=text, metadata={"source": str(pdf_path.name)})
    ])
    
    print(f"   Split into {len(docs)} chunks")
    
    # Initialize embedding model
    print(f"   Generating embeddings with {EMBEDDING_MODEL}...")
    embeddings = init_embedding_model(EMBEDDING_MODEL)
    
    # Connect to HANA and store
    print(f"   Connecting to HANA and storing in table '{TABLE_NAME}'...")
    connection = get_hana_connection()
    db = HanaDB(embedding=embeddings, connection=connection, table_name=TABLE_NAME)
    
    # Delete existing chunks from this source (avoid duplicates)
    db.delete(filter={"source": str(pdf_path.name)})
    
    # Add new documents
    db.add_documents(docs)
    
    print(f"✅ Ingested {len(docs)} chunks from {pdf_path.name} into table '{TABLE_NAME}'")


if __name__ == "__main__":
    main()
