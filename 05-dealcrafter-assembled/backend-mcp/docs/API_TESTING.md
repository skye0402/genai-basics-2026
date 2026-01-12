# Document API Testing Guide

## Server Architecture

The MCP server exposes **two types of endpoints**:

### 1. REST API (for applications)
- **Base URL:** `http://localhost:3001/api/documents`
- **Purpose:** Document management (upload, delete)
- **Used by:** Your frontend application, scripts, services

### 2. MCP Protocol (for LLMs)
- **Endpoint:** `http://localhost:3001/mcp`
- **Purpose:** LLM tool access (search_documents)
- **Used by:** Claude Desktop, other MCP clients

## Testing REST API Endpoints

### 1. Upload a Document

```bash
# Upload a single text file
curl -X POST http://localhost:3001/api/documents/upload \
  -F "files=@/path/to/document.txt" \
  -F "tenant_id=test-tenant"

# Upload with metadata
curl -X POST http://localhost:3001/api/documents/upload \
  -F "files=@/path/to/report.pdf" \
  -F "tenant_id=customer-123" \
  -F 'metadata={"author":"John Doe","category":"financial","year":2024}'

# Upload multiple files
curl -X POST http://localhost:3001/api/documents/upload \
  -F "files=@document1.txt" \
  -F "files=@document2.md" \
  -F "tenant_id=test-tenant"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Processed 1 document(s), 1 successful",
  "results": [
    {
      "success": true,
      "document_id": "document",
      "filename": "document.txt",
      "chunks_created": 5,
      "tenant_id": "test-tenant",
      "timestamp": "2025-11-15T06:22:00.000Z"
    }
  ]
}
```

### 2. Search Documents

```bash
# Basic search
curl -X POST http://localhost:3001/api/documents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "revenue projections",
    "k": 3
  }'

# Search with tenant filter
curl -X POST http://localhost:3001/api/documents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key findings?",
    "tenant_id": "customer-123",
    "k": 5
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "query": "revenue projections",
  "count": 3,
  "results": [
    {
      "rank": 1,
      "content": "Revenue projections for Q4 show...",
      "metadata": {
        "document_id": "financial-report",
        "chunk_id": "financial-report#chunk_003",
        "chunk_index": 3,
        "total_chunks": 10,
        "tenant_id": "test-tenant"
      },
      "score": 0.89
    }
  ]
}
```

### 3. Delete a Document

```bash
# Delete without tenant filter
curl -X DELETE http://localhost:3001/api/documents/financial-report

# Delete with tenant filter
curl -X DELETE "http://localhost:3001/api/documents/financial-report?tenant_id=customer-123"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Document financial-report deleted successfully"
}
```

### 4. Health Check

```bash
curl http://localhost:3001/api/documents/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "document_ingestion",
  "vector_store": "connected"
}
```

## Testing MCP Tool (for LLM)

The `search_documents` tool is available to the LLM through the MCP protocol.

### Using with Claude Desktop

1. Configure MCP server in Claude Desktop settings
2. Start a conversation
3. Ask Claude to search documents:
   - "Search the uploaded documents for information about revenue"
   - "What do the documents say about Q4 projections?"
   - "Find information about customer satisfaction in the reports"

Claude will automatically call the `search_documents` tool when needed.

## Integration Example (JavaScript)

### Upload from Frontend

```javascript
async function uploadDocument(file, tenantId, metadata) {
  const formData = new FormData();
  formData.append('files', file);
  formData.append('tenant_id', tenantId);
  if (metadata) {
    formData.append('metadata', JSON.stringify(metadata));
  }

  const response = await fetch('http://localhost:3001/api/documents/upload', {
    method: 'POST',
    body: formData,
  });

  return await response.json();
}

// Usage
const file = document.getElementById('fileInput').files[0];
const result = await uploadDocument(file, 'customer-123', {
  author: 'John Doe',
  category: 'financial',
});
console.log(result);
```

### Search from Frontend

```javascript
async function searchDocuments(query, tenantId, k = 4) {
  const response = await fetch('http://localhost:3001/api/documents/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      tenant_id: tenantId,
      k,
    }),
  });

  return await response.json();
}

// Usage
const results = await searchDocuments(
  'What are the revenue projections?',
  'customer-123',
  5
);
console.log(results);
```

## Common Issues

### 1. Connection Refused
**Problem:** `curl: (7) Failed to connect to localhost port 3001`

**Solution:** 
- Ensure MCP server is running: `pnpm start` or `pnpm dev`
- Check if port 3001 is available

### 2. HANA Connection Failed
**Problem:** `"status": "unhealthy", "error": "Connection failed"`

**Solution:**
- Verify HANA credentials in `.env.local`
- Check HANA instance is running
- Verify network connectivity to HANA Cloud

### 3. File Upload Failed
**Problem:** `"error": "Unsupported file type"`

**Solution:**
- Only `.txt`, `.md`, and `.pdf` files are supported
- Check file extension is correct

### 4. No Search Results
**Problem:** `"count": 0, "results": []`

**Solution:**
- Verify documents were uploaded successfully
- Check tenant_id matches between upload and search
- Try a different search query

## Performance Tips

1. **Chunk Size:** Adjust `CHUNK_SIZE` in `.env.local` for your documents
   - Larger chunks (2000-3000): Better for long-form content
   - Smaller chunks (500-1000): Better for precise retrieval

2. **Search Results:** Use appropriate `k` value
   - Too low: May miss relevant information
   - Too high: May include irrelevant results

3. **Batch Uploads:** Upload multiple files in one request for efficiency

4. **Tenant Isolation:** Always use `tenant_id` for multi-tenant applications

## Next Steps

1. Test basic upload and search workflow
2. Integrate with your frontend application
3. Configure Claude Desktop to use MCP tool
4. Test RAG (Retrieval-Augmented Generation) workflow
5. Monitor HANA Cloud performance and adjust settings
