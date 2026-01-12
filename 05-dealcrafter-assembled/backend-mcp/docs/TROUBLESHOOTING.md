# Troubleshooting Guide

## Web Search Tool Issues

### Mock Mode When It Should Use Real API

**Symptom:**
```json
{
  "answer": "This is a mock response. Configure SAP_AI_HUB_ENDPOINT and SAP_AUTH_TOKEN...",
  "sources": ["https://example.com/mock-source-1", "https://example.com/mock-source-2"]
}
```

**Cause:** Environment variables not loaded or `AICORE_SERVICE_KEY` not configured

**Solutions:**

1. **Check server startup logs:**
   ```
   🔧 Configuration:
      LOG_LEVEL: info
      PORT: 3001
      SAP_AI_RESOURCE_GROUP: generative-ai
      AICORE_SERVICE_KEY: ✅ Configured  <-- Should show this
   ```

   If you see `❌ Not configured (mock mode)`, the environment file isn't being loaded.

2. **Verify `.env.local` exists:**
   ```bash
   ls -la .env.local
   ```

3. **Restart the server:**
   The server loads environment variables on startup. After creating/updating `.env.local`:
   ```bash
   # Stop server (Ctrl+C)
   pnpm dev
   ```

4. **Check `.env.local` format:**
   ```bash
   # Should be a single-line JSON string
   AICORE_SERVICE_KEY='{"clientid":"...","clientsecret":"...","url":"...",...}'
   ```

5. **Verify working directory:**
   The server must be started from the `backend-mcp/` directory where `.env.local` is located.

### First Call is Slow

**Symptom:** First web search takes 3-6 seconds, subsequent calls are faster

**Cause:** This is expected behavior - first call initializes cache

**Expected logs on first call:**
```
[WebSearch] Initializing new Perplexity client...
[WebSearch] Resolving deployment URL...
[WebSearch] Deployment URL resolved and cached
[WebSearch] Requesting OAuth2 token...
[WebSearch] OAuth2 token obtained and cached
[WebSearch] Perplexity client created and cached
```

**Expected logs on subsequent calls:**
```
[WebSearch] Using cached Perplexity client
```

**Solution:** This is normal. First call: ~3-6s, subsequent: ~2-5s

### Authentication Errors

**Symptom:**
```
Error: Failed to obtain OAuth2 token: 401 Unauthorized
```

**Causes & Solutions:**

1. **Invalid service key:**
   - Verify service key is correct and up-to-date
   - Check for typos in `.env.local`
   - Ensure JSON is valid (use a JSON validator)

2. **Expired credentials:**
   - Service keys can expire
   - Get a fresh service key from SAP BTP Cockpit

3. **Network issues:**
   - Check connectivity to SAP authentication endpoint
   - Verify firewall/proxy settings

### Deployment Not Found

**Symptom:**
```
Error: Could not resolve Perplexity deployment URL
```

**Causes & Solutions:**

1. **Wrong resource group:**
   ```bash
   # Check your resource group in .env.local
   SAP_AI_RESOURCE_GROUP=generative-ai  # Should match your deployment
   ```

2. **Model not deployed:**
   - Run `pnpm list:deployments` to see available models
   - Verify `sonar` or `sonar-pro` is deployed and RUNNING

3. **Wrong model name:**
   - Current code looks for `sonar`
   - If your deployment has a different name, update `webSearchTool.ts`:
   ```typescript
   model: {
     name: 'your-model-name',  // Change this
   }
   ```

## General Server Issues

### Server Won't Start

**Symptom:**
```
Error: listen EADDRINUSE: address already in use :::3001
```

**Solution:**
```bash
# Find process using port 3001
lsof -i :3001

# Kill the process
kill -9 <PID>

# Or use a different port in .env.local
PORT=3002
```

### TypeScript Errors

**Symptom:** Build fails with TypeScript errors

**Solution:**
```bash
# Clean build
rm -rf dist/
rm tsconfig.tsbuildinfo
pnpm build
```

### Dependency Issues

**Symptom:** Module not found errors

**Solution:**
```bash
# Reinstall dependencies
rm -rf node_modules/
rm pnpm-lock.yaml
pnpm install
```

## Testing Issues

### Test Scripts Fail

**Symptom:** `pnpm test:sap` fails

**Common causes:**

1. **Missing `.env.local`:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your credentials
   ```

2. **Wrong working directory:**
   ```bash
   # Must run from backend-mcp/ directory
   cd backend-mcp/
   pnpm test:sap
   ```

3. **Network connectivity:**
   - Check internet connection
   - Verify access to SAP endpoints

## Performance Issues

### Slow Response Times

**Expected times:**
- First call: 3-6 seconds (includes initialization)
- Cached calls: 2-5 seconds (just API time)

**If slower:**

1. **Check network latency:**
   ```bash
   # Test connectivity to SAP endpoint
   curl -w "@-" -o /dev/null -s 'https://api.ai.prod.ap-northeast-1.aws.ml.hana.ondemand.com'
   ```

2. **Check Perplexity API response time:**
   - Complex queries take longer
   - Try simpler queries for testing

3. **Verify caching is working:**
   - Check logs for "Using cached Perplexity client"
   - If not cached, see "First Call is Slow" above

## Getting Help

### Useful Commands

```bash
# Check server logs
pnpm dev

# Test SAP integration
pnpm test:sap

# List deployments
pnpm list:deployments

# Check environment
cat .env.local

# Verify build
pnpm build
```

### Log Levels

Set in `.env.local`:
```bash
LOG_LEVEL=debug  # Most verbose
LOG_LEVEL=info   # Default
LOG_LEVEL=warn   # Warnings only
LOG_LEVEL=error  # Errors only
```

### Debug Mode

Enable detailed logging:
```bash
# In .env.local
LOG_LEVEL=debug

# Restart server
pnpm dev
```

## Common Gotchas

### 1. Environment Variables Not Loaded
- **Issue:** Server doesn't load `.env.local` automatically
- **Fix:** Server now loads it on startup (after recent fix)
- **Verify:** Check startup logs for configuration status

### 2. Token Expiration
- **Issue:** Token expires after ~12 hours
- **Fix:** Restart server to get fresh token
- **Workshop:** Not an issue for short workshops

### 3. Cache Not Cleared
- **Issue:** Old cached data after configuration change
- **Fix:** Restart server to clear cache

### 4. Wrong Working Directory
- **Issue:** `.env.local` not found
- **Fix:** Always run commands from `backend-mcp/` directory

### 5. JSON Formatting
- **Issue:** Service key has line breaks
- **Fix:** Service key must be single-line JSON string

## Still Having Issues?

1. Check all logs carefully
2. Verify configuration with startup logs
3. Test with `pnpm test:sap` first
4. Check documentation in `docs/` folder
5. Review error messages for specific guidance
