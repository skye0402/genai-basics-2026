# Web Search Tool - Caching Implementation

## Overview

The web search tool implements **module-level caching** to improve performance by reusing connections and avoiding repeated authentication calls.

## What is Cached

### 1. Perplexity Client Instance
- **Cached**: The entire `Perplexity` client object
- **Lifetime**: Server process lifetime
- **Benefit**: Reuses HTTP connections and client configuration

### 2. OAuth2 Token
- **Cached**: Access token from SAP authentication
- **Lifetime**: Server process lifetime (~12 hours token validity)
- **Benefit**: Eliminates 200-500ms OAuth2 request on subsequent calls

### 3. Deployment URL
- **Cached**: Resolved Perplexity deployment URL from SAP AI SDK
- **Lifetime**: Server process lifetime
- **Benefit**: Eliminates 300-800ms deployment resolution on subsequent calls

## Performance Impact

### First Call (Cold Start)
```
1. Resolve deployment URL    ~500ms
2. Request OAuth2 token       ~300ms
3. Create Perplexity client   ~50ms
4. Execute search query       ~2-5s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: ~3-6 seconds
```

### Subsequent Calls (Cached)
```
1. Return cached client       ~1ms
2. Execute search query       ~2-5s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: ~2-5 seconds
```

**Speed improvement**: ~1 second faster per call after the first request

## Implementation

### Cache Variables
```typescript
// Module-level cache (top of webSearchTool.ts)
let cachedClient: Perplexity | null = null;
let cachedToken: string | null = null;
let cachedDeploymentUrl: string | null = null;
```

### Cache Logic
```typescript
async function createPerplexityClient(): Promise<Perplexity> {
  // Fast path: return cached client
  if (cachedClient) {
    return cachedClient;
  }

  // Slow path: initialize and cache
  // 1. Resolve deployment URL (if not cached)
  // 2. Get OAuth2 token (if not cached)
  // 3. Create client and cache it
  
  return cachedClient;
}
```

## Cache Invalidation

### Automatic Invalidation
Cache is automatically cleared when:
- Server process restarts
- Server crashes or is stopped

### Manual Invalidation
To clear cache without restarting:
1. Stop the server (`Ctrl+C`)
2. Start the server (`pnpm dev`)

### No Expiration Management
For workshop purposes, **no token expiration handling** is implemented:
- Token is valid for ~12 hours
- Workshop duration < 12 hours
- Simple implementation without complexity

## Logging

The implementation includes console logging for debugging:

```
[WebSearch] Initializing new Perplexity client...
[WebSearch] Resolving deployment URL...
[WebSearch] Deployment URL resolved and cached
[WebSearch] Requesting OAuth2 token...
[WebSearch] OAuth2 token obtained and cached
[WebSearch] Perplexity client created and cached
```

Subsequent calls show:
```
[WebSearch] Using cached Perplexity client
```

## Workshop Considerations

### Why This Approach?

✅ **Simple**: No expiration logic or refresh mechanisms  
✅ **Fast**: Significant performance improvement  
✅ **Reliable**: Token won't expire during workshop  
✅ **Minimal Code**: ~15 lines of caching logic  

### Production Considerations

For production use, consider adding:

1. **Token Expiration Handling**
   ```typescript
   let tokenExpiresAt: number | null = null;
   
   if (!cachedToken || Date.now() >= tokenExpiresAt) {
     // Refresh token
   }
   ```

2. **Error Recovery**
   ```typescript
   try {
     return cachedClient;
   } catch (error) {
     // Clear cache and retry
     cachedClient = null;
     return createPerplexityClient();
   }
   ```

3. **Metrics/Monitoring**
   - Track cache hit rate
   - Monitor token refresh frequency
   - Alert on authentication failures

## Testing

### Verify Caching Works

1. Start server:
   ```bash
   pnpm dev
   ```

2. Make first web search request:
   ```
   [WebSearch] Initializing new Perplexity client...
   [WebSearch] Resolving deployment URL...
   [WebSearch] Deployment URL resolved and cached
   [WebSearch] Requesting OAuth2 token...
   [WebSearch] OAuth2 token obtained and cached
   [WebSearch] Perplexity client created and cached
   ```

3. Make second web search request:
   ```
   [WebSearch] Using cached Perplexity client
   ```

### Performance Testing

Compare response times:
- First request: ~3-6 seconds
- Second request: ~2-5 seconds
- Improvement: ~1 second

## Troubleshooting

### Cache Not Working

**Symptom**: Every request shows "Initializing new Perplexity client"

**Causes**:
- Server restarting between requests
- Module being reloaded (hot reload in dev mode)
- Error clearing cache variables

**Solution**: Check server logs for restart messages

### Stale Token

**Symptom**: Authentication errors after long server uptime

**Cause**: Token expired (>12 hours)

**Solution**: Restart server to get fresh token

### Memory Concerns

**Question**: Does caching cause memory leaks?

**Answer**: No. Only 3 variables cached:
- 1 client object (~few KB)
- 1 token string (~2KB)
- 1 URL string (~200 bytes)

Total memory impact: < 10KB

## Related Documentation

- [README-WEB-SEARCH.md](./README-WEB-SEARCH.md) - User guide
- [README-SAP-AI-SDK-INTEGRATION.md](./README-SAP-AI-SDK-INTEGRATION.md) - SAP integration
- [IMPLEMENTATION-SUMMARY.md](./IMPLEMENTATION-SUMMARY.md) - Implementation overview
