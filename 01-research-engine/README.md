# Part 1: The Research Engine

> **Goal:** Teach the AI to read financial documents using RAG (Retrieval-Augmented Generation).

---

## 🎯 What You'll Build

1. **PDF Ingestion** – Load financial PDFs, chunk text, generate embeddings, store in HANA
2. **RAG Chat** – Ask questions and get answers grounded in your documents

---

## 📋 Scenario

> "We've received {COMPANY_NAME}'s financial reports. Let's make them searchable by our AI analyst."

**Track A:** Seven & i's quarterly earnings reports  
**Track B:** Sakura Internet's factbook and sustainability report

---

## 🚀 Steps

### 1. Install Dependencies

```bash
cd 01-research-engine
uv sync
```

### 2. Ingest PDF Documents

```bash
# Ingest a PDF (choose your track)
uv run python ingest_pdf.py ../rag-material/sakura_internet/factbook.pdf

# Or for Track A:
uv run python ingest_pdf.py ../rag-material/7i_holdings/2026年2月期\ 第3四半期決算説明資料.pdf
```

### 3. Chat with Your Documents

```bash
uv run python chat_documents.py
```

---

## 🏋️ Exercises

### Exercise 1a: PDF Ingestion (`ingest_pdf.py`)

Complete the TODOs to:
1. Load the PDF using `pypdf`
2. Chunk the text using `RecursiveCharacterTextSplitter`
3. Create embeddings and store in HANA

**Key imports:**
```python
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_hana import HanaDB
from gen_ai_hub.proxy.langchain.init_models import init_embedding_model
```

### Exercise 1b: RAG Chat (`chat_documents.py`)

Complete the TODOs to:
1. Connect to HANA and create a retriever
2. Retrieve relevant chunks for a question
3. Pass context + question to the LLM

---

## 💡 Key Concepts

### What is RAG?
**Retrieval-Augmented Generation** grounds LLM responses in your data:
1. User asks a question
2. System retrieves relevant document chunks (via vector similarity)
3. LLM generates answer using the retrieved context

### Vector Embeddings
Text is converted to dense vectors (arrays of numbers) that capture semantic meaning. Similar texts have similar vectors.

### SAP HANA Cloud Vector Engine
HANA stores embeddings and performs fast similarity search. We use `langchain-hana` to integrate.

---

## 🔧 Configuration

Set these in your `.env`:
```bash
HANA_TABLE_NAME=DEALCRAFTER_DOCS  # Your vector store table
RAG_CHUNK_SIZE=500                 # Characters per chunk
RAG_CHUNK_OVERLAP=50               # Overlap between chunks
RAG_TOP_K=5                        # Number of chunks to retrieve
```

---

## ✅ Success Criteria

After ingestion:
```
✅ Ingested 42 chunks from factbook.pdf into table 'DEALCRAFTER_DOCS'
```

After chat:
```
You: What is Sakura Internet's main business?
Assistant: Based on the documents, Sakura Internet is a cloud infrastructure
provider focused on data centers and hosting services...
```

---

## ➡️ Next Step

Once you can chat with your documents, proceed to **Part 2: The Data Connector (MCP)**!
