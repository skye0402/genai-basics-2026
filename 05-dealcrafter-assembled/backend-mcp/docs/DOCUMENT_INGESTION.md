# Document Ingestion with HANA Cloud Vector Store

This MCP server provides document ingestion and semantic search capabilities using SAP HANA Cloud Vector Store and SAP AI SDK embeddings.

## Features

- **Document Upload**: Ingest text, markdown, and PDF documents via REST API
- **Semantic Chunking**: Automatically split documents into manageable chunks with overlap
- **Vector Embeddings**: Generate embeddings using SAP AI SDK (Azure OpenAI)
- **HANA Vector Store**: Store and retrieve document chunks with metadata
- **Multi-tenancy**: Isolate documents by tenant for secure data separation
- **Semantic Search**: Find relevant document chunks using natural language queries (MCP tool for LLM)

## Architecture

```
Application → REST API → Document Service → HANA Cloud
                              ↓
                         Embed & Store
                              
LLM → MCP Tool (search_documents) → HANA Cloud → Context
```

### Key Distinction

**REST API Endpoints** (for applications):
- Upload documents
- Delete documents
- Manage document lifecycle

**MCP Tools** (for LLM):
- Search documents to retrieve context during conversations
- LLM uses this to augment responses with document knowledge

## REST API Endpoints

### 1. POST /api/documents/upload

Upload and ingest one or more documents into HANA Cloud Vector Store.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `files`: File(s) to upload (max 10 files, 50MB each)
  - `tenant_id` (optional): Tenant identifier
  - `metadata` (optional): JSON string with additional metadata

**Example (curl):**
```bash
curl -X POST http://localhost:3001/api/documents/upload \
  -F "files=@document.pdf" \
  -F "tenant_id=customer-123" \
  -F 'metadata={"author":"John Doe","category":"financial-report"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Processed 1 document(s), 1 successful",
  "results": [
    {
      "success": true,
      "document_id": "document",
      "filename": "document.pdf",
      "chunks_created": 15,
      "tenant_id": "customer-123",
      "timestamp": "2025-11-15T05:55:00.000Z"
    }
  ]
}
```

### 2. POST /api/documents/search

Search for relevant document chunks (also available as MCP tool for LLM).

Search for relevant document chunks using semantic similarity.

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
  - `query` (string, required): Search query text
  - `tenant_id` (string, optional): Filter results by tenant
  - `k` (number, optional): Number of results to return (default: 4)

**Example (curl):**
```bash
curl -X POST http://localhost:3001/api/documents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the revenue projections for Q4?",
    "tenant_id": "customer-123",
    "k": 5
  }'
```

**Response:**
```json
{
  "success": true,
  "query": "What are the revenue projections for Q4?",
  "count": 5,
  "results": [
    {
      "rank": 1,
      "content": "Q4 revenue projections show...",
      "metadata": {
        "document_id": "financial-report",
        "chunk_id": "financial-report#chunk_003",
        "tenant_id": "customer-123"
      },
      "score": 0.92
    }
  ]
}
```

### 3. DELETE /api/documents/:document_id

Delete a document and all its chunks from HANA Cloud Vector Store.

**Request:**
- Method: `DELETE`
- URL: `/api/documents/{document_id}?tenant_id={tenant_id}`
- Query Parameters:
  - `tenant_id` (optional): Tenant identifier for isolation

**Example (curl):**
```bash
curl -X DELETE "http://localhost:3001/api/documents/financial-report?tenant_id=customer-123"
```

**Response:**
```json
{
  "success": true,
  "message": "Document financial-report deleted successfully"
}
```

## Configuration

Add the following environment variables to your `.env.local` file:

```bash
# HANA Cloud Vector Store Configuration
HANA_DB_ADDRESS=your-hana-instance.hanacloud.ondemand.com
HANA_DB_PORT=443
HANA_DB_USER=your-username
HANA_DB_PASSWORD=your-password

# Vector Store Table Configuration
HANA_TABLE=LANGCHAIN_DEMO_DOCS

# Document Processing Configuration
CHUNK_SIZE=2000
CHUNK_OVERLAP=200

# Embedding Model Configuration
EMBEDDING_MODEL=text-embedding-3-small

# Multi-tenancy Configuration
DEFAULT_TENANT_ID=default-tenant
```

## Setup

1. **Install Dependencies**:
   ```bash
   pnpm install
   ```

2. **Configure Environment**:
   - Copy `.env.example` to `.env.local`
   - Fill in your HANA Cloud credentials
   - Configure your SAP AI Core service key

3. **Build and Run**:
   ```bash
   pnpm build
   pnpm start
   ```

## MCP Tool for LLM

### search_documents

The LLM can use this tool during conversations to retrieve relevant context from uploaded documents.

**Tool Name:** `search_documents`

**Description:** Search for relevant document chunks in HANA Cloud Vector Store using semantic similarity. Use this to find information from uploaded documents to answer user questions.

**Parameters:**
- `query` (string): Search query text
- `tenant_id` (string, optional): Filter results by tenant
- `k` (number, optional): Number of results (default: 4)

**Usage:** The LLM automatically calls this tool when it needs information from documents to answer user questions.

## Usage with Claude Desktop

Add the MCP server to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "backend-mcp": {
      "command": "node",
      "args": ["/path/to/backend-mcp/dist/server.js"],
      "env": {
        "HANA_DB_ADDRESS": "your-hana-instance.hanacloud.ondemand.com",
        "HANA_DB_USER": "your-username",
        "HANA_DB_PASSWORD": "your-password"
      }
    }
  }
}
```

**Note:** The MCP server provides:
1. **MCP endpoint** at `http://localhost:3001/mcp` for Claude Desktop
2. **REST API** at `http://localhost:3001/api/documents/*` for your application

## Document Metadata Schema

Each document chunk is stored with the following metadata:

```typescript
{
  // Traceability
  document_id: string;        // Unique document identifier
  source_filename: string;    // Original filename
  created_at: string;         // ISO timestamp
  
  // Chunking
  chunk_id: string;           // Unique chunk identifier
  chunk_index: number;        // Position in document
  total_chunks: number;       // Total chunks in document
  
  // Domain
  document_type: string;      // pdf_document, text_document, etc.
  
  // Multi-tenancy
  tenant_id: string;          // Tenant identifier
  
  // Optional
  page_number?: number;       // For PDF documents
  [key: string]: any;         // Custom metadata
}
```

## Supported File Types

- `.txt` - Plain text files
- `.md` - Markdown files
- `.pdf` - PDF documents (requires pdf-parse)

## RAG (Retrieval-Augmented Generation) Pattern

Use document search to enhance LLM responses:

1. **Ingest documents**: Upload relevant documents to HANA
2. **Search on query**: Find relevant chunks for user questions
3. **Augment prompt**: Include retrieved chunks in LLM context
4. **Generate response**: LLM answers using document context

## Troubleshooting

### Connection Issues
- Verify HANA Cloud credentials
- Check network connectivity to HANA instance
- Ensure HANA instance is running

### Embedding Issues
- Verify SAP AI Core service key is configured
- Check AI Core deployment is active
- Ensure embedding model is available

### Performance
- Adjust `CHUNK_SIZE` and `CHUNK_OVERLAP` for your use case
- Consider creating HNSW index for large datasets
- Use appropriate `k` value for search results

## Migration from Python Backend

This implementation replaces the Python-based document ingestion service to avoid package conflicts. The functionality is equivalent but uses:

- TypeScript instead of Python
- SAP AI SDK for TypeScript instead of gen-ai-hub
- Native HANA client instead of langchain-hana

All API contracts remain compatible with existing clients.
