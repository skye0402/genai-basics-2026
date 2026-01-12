# Web Search Tool - Perplexity via SAP Generative AI Hub

## Overview

The MCP server now includes a web search tool that uses Perplexity AI's `sonar` model through SAP Generative AI Hub. This enables AI-powered web research with cited sources.

## Features

- **AI-Synthesized Answers**: Get comprehensive answers from web research
- **Source Citations**: Receive URLs of sources used in the answer
- **Mock Mode**: Automatic fallback to mock responses when SAP AI Hub is not configured
- **Configurable Results**: Control the maximum number of source citations returned

## Configuration

### Environment Variables

Add these to your `.env` file (see `.env.example`):

```bash
# SAP Generative AI Hub configuration
SAP_AI_HUB_ENDPOINT=https://your-sap-ai-hub-endpoint.com/v2
SAP_AUTH_TOKEN=your-oauth2-bearer-token
SAP_AI_RESOURCE_GROUP=default
```

### Getting SAP Credentials

1. **SAP AI Hub Endpoint**: This is the base URL for your SAP Generative AI Hub deployment
   - Format: `https://<your-instance>.aicore.sap/v2`
   - Contact your SAP BTP administrator for the exact endpoint

2. **OAuth2 Token**: Use SAP AI SDK to obtain the token programmatically:
   ```typescript
   import { getDestination } from '@sap-ai-sdk/ai-api';
   
   // The SDK handles OAuth2 client credentials flow automatically
   // when AICORE_SERVICE_KEY is configured
   ```

3. **Resource Group**: The AI Core resource group (usually `default`)

## Usage

### Tool Schema

**Input:**
```typescript
{
  query: string;           // The search query or research question
  max_results?: number;    // Maximum number of source URLs to return (default: 5)
}
```

**Output:**
```typescript
{
  answer: string;          // AI-synthesized answer from web research
  sources?: string[];      // Array of source URLs (up to max_results)
}
```

### Example MCP Tool Call

```json
{
  "tool": "web_search",
  "arguments": {
    "query": "What are the latest developments in SAP BTP AI services?",
    "max_results": 3
  }
}
```

**Response:**
```json
{
  "answer": "SAP Business Technology Platform has recently enhanced its AI capabilities with...",
  "sources": [
    "https://www.sap.com/products/technology-platform.html",
    "https://help.sap.com/docs/btp",
    "https://blogs.sap.com/..."
  ]
}
```

## Mock Mode

When `SAP_AI_HUB_ENDPOINT` or `SAP_AUTH_TOKEN` are not configured, the tool automatically falls back to mock mode:

- Returns predefined answers for common queries
- Simulates API delay (500ms)
- Provides example source URLs
- Useful for testing and development

### Mock Responses

The mock includes responses for:
- "latest AI developments"
- "SAP BTP"
- Generic fallback for other queries

## Integration with SAP AI SDK

The tool is designed to work with SAP's authentication infrastructure:

### Using Service Keys (Recommended)

```bash
# Set the AI Core service key
export AICORE_SERVICE_KEY='{"clientid": "...", "clientsecret": "...", "url": "...", "serviceurls": {"AI_API_URL": "..."}}'
```

Then use the SAP AI SDK to get authenticated access:

```typescript
import { AiCoreService } from '@sap-ai-sdk/ai-api';

// SDK automatically uses AICORE_SERVICE_KEY for OAuth2
const deployment = await AiCoreService.getDeployment({
  deploymentId: 'your-perplexity-deployment-id'
});
```

### Custom Authentication Flow

For custom OAuth2 flows, the Perplexity client accepts:
- `baseURL`: Your SAP AI Hub endpoint
- `defaultHeaders`: Including `Authorization: Bearer <token>`

## Architecture

```
┌─────────────────┐
│   MCP Client    │
└────────┬────────┘
         │
         │ Tool Call: web_search
         ▼
┌─────────────────┐
│   MCP Server    │
│  (webSearchTool)│
└────────┬────────┘
         │
         ├─── SAP_AI_HUB_ENDPOINT configured?
         │
         ├─── YES ──────────────────┐
         │                          │
         │                          ▼
         │              ┌────────────────────┐
         │              │ Perplexity Client  │
         │              │ (Custom Endpoint)  │
         │              └─────────┬──────────┘
         │                        │
         │                        │ HTTPS + OAuth2
         │                        ▼
         │              ┌────────────────────┐
         │              │  SAP Generative    │
         │              │    AI Hub          │
         │              └─────────┬──────────┘
         │                        │
         │                        │ Proxies to
         │                        ▼
         │              ┌────────────────────┐
         │              │  Perplexity AI     │
         │              │  (sonar model)     │
         │              └────────────────────┘
         │
         └─── NO ───────────────────┐
                                    │
                                    ▼
                          ┌──────────────────┐
                          │   Mock Search    │
                          │ (Local Fallback) │
                          └──────────────────┘
```

## Logging

All tool executions are automatically logged with:
- Timestamp
- Tool name (`web_search`)
- Input parameters (truncated if long)
- Output data (truncated if long)

Set `LOG_LEVEL=debug` in `.env` for verbose logging.

## Error Handling

The tool handles several error scenarios:

1. **Missing Configuration**: Falls back to mock mode
2. **API Errors**: Propagates errors with context
3. **Network Issues**: Standard retry behavior from Perplexity SDK
4. **Invalid Responses**: Returns "No answer available" with empty sources

## Perplexity Model Details

- **Model**: `sonar` (Perplexity's web-search optimized model)
- **Max Tokens**: 1000
- **Temperature**: 0.2 (focused, factual responses)
- **Features**: 
  - Real-time web search
  - Citation tracking
  - Multi-source synthesis

## Future Enhancements

Potential improvements for production use:

1. **Token Refresh**: Implement automatic OAuth2 token refresh
2. **Caching**: Cache search results to reduce API calls
3. **Rate Limiting**: Add request throttling for API quota management
4. **Streaming**: Support streaming responses for long answers
5. **Advanced Filters**: Add date ranges, domain filters, etc.
6. **SAP AI SDK Integration**: Use `@sap-ai-sdk/foundation-models` for unified client

## Troubleshooting

### "Environment variables required" Error

**Cause**: `SAP_AI_HUB_ENDPOINT` or `SAP_AUTH_TOKEN` not set

**Solution**: Either configure the variables or use mock mode for testing

### Authentication Errors

**Cause**: Invalid or expired OAuth2 token

**Solution**: 
1. Verify your service key is correct
2. Check token expiration
3. Ensure proper scopes are granted

### No Citations Returned

**Cause**: Perplexity API may not always return citations

**Solution**: This is expected behavior; the `sources` field is optional

## Related Documentation

- [Perplexity API Docs](https://docs.perplexity.ai/)
- [SAP AI Core Documentation](https://help.sap.com/docs/sap-ai-core)
- [SAP Cloud SDK for AI](https://sap.github.io/ai-sdk/)
