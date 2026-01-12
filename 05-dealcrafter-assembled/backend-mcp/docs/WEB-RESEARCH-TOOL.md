# Web Research Tool

## Overview

The `web_research` tool provides **deep, comprehensive web research** using Perplexity's Sonar Pro model. It's designed for complex research questions that require in-depth investigation and analysis.

## When to Use Which Tool

### Use `web_search` (Sonar) for:
- ✅ Quick factual queries
- ✅ Simple questions with straightforward answers
- ✅ Current events and news
- ✅ Basic information lookup
- ✅ Fast responses needed

**Example queries:**
- "What's the stock price of SAP today?"
- "Who won the latest Formula 1 race?"
- "What is the capital of France?"

### Use `web_research` (Sonar Pro) for:
- ✅ Complex research questions
- ✅ In-depth analysis needed
- ✅ Multi-faceted topics
- ✅ Comprehensive overviews
- ✅ Technical deep dives

**Example queries:**
- "Comprehensive analysis of AI impact on enterprise software development"
- "Compare and contrast different approaches to microservices architecture"
- "What are the latest trends in quantum computing and their business implications?"

## Technical Differences

| Feature | `web_search` (Sonar) | `web_research` (Sonar Pro) |
|---------|---------------------|---------------------------|
| **Model** | `sonar` | `sonar-pro` |
| **Max Tokens** | 1000 | 2000 |
| **Response Length** | Shorter, concise | Longer, detailed |
| **Processing Time** | Faster (~2-5s) | Slower (~5-10s) |
| **Use Case** | Quick answers | Deep research |
| **Cost** | Lower | Higher |

## Usage

### Basic Usage

```json
{
  "tool": "web_research",
  "arguments": {
    "query": "Your complex research question here",
    "max_results": 5
  }
}
```

### Parameters

- **`query`** (required): The research question or topic
- **`max_results`** (optional): Maximum number of source URLs to return (default: 5)

### Response Format

```json
{
  "answer": "Comprehensive, detailed answer based on web research...",
  "sources": [
    "https://source1.com",
    "https://source2.com",
    "https://source3.com"
  ]
}
```

## Implementation Details

### Shared Infrastructure

Both `web_search` and `web_research` share:
- ✅ Same authentication mechanism (OAuth2 via SAP AI Core)
- ✅ Same caching system (separate caches per model)
- ✅ Same error handling and fallback to mock mode
- ✅ Same API structure and response format

### Separate Caching

Each model has its own cache:
```typescript
let cachedClientSonar: Perplexity | null = null;
let cachedClientSonarPro: Perplexity | null = null;
let cachedDeploymentUrlSonar: string | null = null;
let cachedDeploymentUrlSonarPro: string | null = null;
```

OAuth2 token is shared between both models:
```typescript
let cachedToken: string | null = null;  // Shared
```

### Performance

**First call to each tool:**
- Resolve deployment URL: ~500ms
- Request OAuth2 token: ~300ms (only on first call overall)
- Create client: ~50ms
- Execute query: ~5-10s (Sonar Pro is slower)
- **Total: ~6-11 seconds**

**Subsequent calls (cached):**
- Return cached client: ~1ms
- Execute query: ~5-10s
- **Total: ~5-10 seconds**

## Configuration

### Required Environment Variables

Same as `web_search`:
```bash
AICORE_SERVICE_KEY='{"clientid":"...","clientsecret":"...","url":"...",...}'
SAP_AI_RESOURCE_GROUP=generative-ai  # Or your resource group
```

### Deployment Requirements

Both `sonar` and `sonar-pro` must be deployed in your SAP AI Core instance:

```bash
# Verify deployments
pnpm list:deployments

# Should show both:
# - sonar (for web_search)
# - sonar-pro (for web_research)
```

## Examples

### Example 1: Technology Analysis

**Query:**
```json
{
  "tool": "web_research",
  "arguments": {
    "query": "What are the key differences between SAP BTP and AWS in terms of enterprise integration capabilities?"
  }
}
```

**Expected Response:**
Comprehensive analysis covering:
- Platform architectures
- Integration services
- Enterprise features
- Use cases
- Pros and cons
- With multiple authoritative sources

### Example 2: Market Research

**Query:**
```json
{
  "tool": "web_research",
  "arguments": {
    "query": "Analyze the current state of the ERP market and emerging trends for 2025"
  }
}
```

**Expected Response:**
Detailed market analysis including:
- Current market leaders
- Emerging players
- Technology trends
- Business implications
- Future predictions
- Industry sources

### Example 3: Technical Deep Dive

**Query:**
```json
{
  "tool": "web_research",
  "arguments": {
    "query": "Explain the architecture and implementation patterns for event-driven microservices in cloud-native applications"
  }
}
```

**Expected Response:**
Technical explanation covering:
- Architecture patterns
- Implementation approaches
- Best practices
- Common pitfalls
- Real-world examples
- Technical documentation sources

## Troubleshooting

### Same as web_search

All troubleshooting steps from `web_search` apply to `web_research`:
- Environment configuration
- Authentication issues
- Deployment resolution
- Mock mode fallback

See [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) for details.

### Specific to web_research

**Issue: "Could not resolve deployment URL for sonar-pro"**

**Solution:**
1. Verify `sonar-pro` is deployed:
   ```bash
   pnpm list:deployments | grep sonar-pro
   ```

2. If not deployed, deploy it in SAP AI Core or use `web_search` instead

**Issue: Responses are too long/truncated**

**Cause:** Sonar Pro can generate longer responses (up to 2000 tokens)

**Solution:** This is expected behavior. The tool is configured for comprehensive responses.

## Best Practices

### 1. Choose the Right Tool

- Start with `web_search` for quick queries
- Escalate to `web_research` for complex topics
- Let the AI decide based on query complexity

### 2. Craft Better Research Questions

**Good:**
- "Analyze the impact of AI on healthcare diagnostics, including current applications, challenges, and future trends"

**Bad:**
- "AI healthcare" (too vague, use `web_search` instead)

### 3. Use Appropriate max_results

- Default (5) is usually sufficient
- Increase for broader topics
- Decrease for focused research

### 4. Monitor Performance

- First call to each tool will be slower (initialization)
- Subsequent calls use cached clients
- Sonar Pro is inherently slower than Sonar

## Workshop Considerations

### For Participants

- Demonstrate both tools side-by-side
- Show when to use each one
- Highlight the quality difference in responses
- Explain the performance trade-off

### For Instructors

- Pre-warm both caches before demos (make one call to each)
- Prepare example queries for both tools
- Have backup queries ready
- Monitor server logs for caching confirmation

## Future Enhancements

Potential improvements for production:

1. **Adaptive Token Limits**
   - Adjust based on query complexity
   - Dynamic max_tokens selection

2. **Streaming Responses**
   - Stream tokens as they're generated
   - Better UX for long responses

3. **Query Classification**
   - Auto-route to appropriate tool
   - Based on query complexity analysis

4. **Response Caching**
   - Cache common research queries
   - Reduce API calls and costs

5. **Cost Tracking**
   - Monitor token usage
   - Track costs per tool
   - Usage analytics

## Related Documentation

- [README-WEB-SEARCH.md](./README-WEB-SEARCH.md) - Web search tool documentation
- [CACHING.md](./CACHING.md) - Caching implementation details
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues and solutions
- [README-SAP-AI-SDK-INTEGRATION.md](./README-SAP-AI-SDK-INTEGRATION.md) - SAP integration guide
