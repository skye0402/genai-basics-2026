# Part 1: The Research Engine (Complete)

> **This is the complete, runnable version.** Use this if you want to skip the exercise or verify your solution.

---

## 🚀 Quick Run

```bash
cd 01-research-engine-done
uv sync

# Ingest a PDF
uv run python ingest_pdf.py ../rag-material/sakura_internet/factbook.pdf

# Chat with your documents
uv run python chat_documents.py
```

---

## ✅ Expected Output

After ingestion:
```
📄 Loading PDF: factbook.pdf
✅ Ingested 42 chunks from factbook.pdf into table 'DEALCRAFTER_DOCS'
```

After chat:
```
📚 Starting RAG Chat for Sakura Internet
Type your questions about the ingested documents.

You: What is Sakura Internet's main business?
Assistant: Based on the documents, Sakura Internet is a leading cloud 
infrastructure provider in Japan, specializing in data center services,
cloud hosting, and server solutions...
```
