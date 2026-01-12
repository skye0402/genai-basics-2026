# SAP AI SDK Integration for Web Search

## Overview

The web search tool now uses the **SAP AI SDK** (`@sap-ai-sdk/ai-api`) for automatic deployment resolution and OAuth2 authentication. This eliminates the need for manual endpoint and token configuration.

## How It Works

### 1. Service Key Configuration

The tool requires the `AICORE_SERVICE_KEY` environment variable containing your SAP AI Core service credentials:

```bash
AICORE_SERVICE_KEY='{"clientid":"sb-xxx","clientsecret":"xxx","url":"https://xxx.authentication.xxx.hana.ondemand.com","identityzone":"xxx","identityzoneid":"xxx","appname":"xxx","serviceurls":{"AI_API_URL":"https://api.ai.xxx"}}'
```

### 2. Automatic Deployment Resolution

The SDK's `resolveDeploymentUrl()` function automatically:
- Queries SAP AI Core for available deployments
- Finds the Perplexity `sonar` model deployment
- Returns the deployment URL endpoint

```typescript
const deploymentUrl = await resolveDeploymentUrl({
  scenarioId: 'foundation-models',
  model: {
    name: 'perplexity--sonar',
    version: 'latest',
  },
  resourceGroup: process.env.SAP_AI_RESOURCE_GROUP || 'default',
});
```

### 3. OAuth2 Client Credentials Flow

The tool implements OAuth2 client credentials authentication:

1. Parses the service key from `AICORE_SERVICE_KEY`
2. Requests an access token from the OAuth2 endpoint
3. Uses the token in the `Authorization` header

```typescript
const tokenResponse = await fetch(`${serviceKey.url}/oauth/token`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    grant_type: 'client_credentials',
    client_id: serviceKey.clientid,
    client_secret: serviceKey.clientsecret,
  }),
});

const { access_token } = await tokenResponse.json();
```

### 4. Perplexity Client Configuration

The authenticated client is configured with:
- **Base URL**: Deployment URL from SAP AI SDK
- **Authorization**: OAuth2 Bearer token
- **Resource Group**: SAP AI Core resource group header

```typescript
return new Perplexity({
  baseURL: deploymentUrl,
  defaultHeaders: {
    'Authorization': `Bearer ${authToken}`,
    'AI-Resource-Group': process.env.SAP_AI_RESOURCE_GROUP || 'default',
  },
  apiKey: 'not-used',
});
```

## Configuration Steps

### 1. Get Your Service Key

From SAP BTP Cockpit:
1. Navigate to your **AI Core** service instance
2. Go to **Service Keys**
3. Create a new service key or view an existing one
4. Copy the JSON output

### 2. Configure Environment

Add to your `.env` file (create from `.env.example`):

```bash
# Required: SAP AI Core service key (single-line JSON)
AICORE_SERVICE_KEY='{"clientid":"sb-2be5ea0e-81f6-4592-a1e380!b1808|aicore!b44","clientsecret":"315399a5-f06c-41-a3d2ff60ef1c$NP7LcR_hyZ74xVwd219U4opSzLHVLPoYn4e2HU=","url":"https://apjdl-aicorelp.authentication.jp10.hana.ondemand.com","identityzone":"apjdl-aicorelp","identityzoneid":"af3d4a55-b37d-4f08-9863-b874aaa51fe4","appname":"2be5ea0e-81f6-4592-aef1-5984bd21e380!b1808|aicore!b44","serviceurls":{"AI_API_URL":"https://api.ai.prod.ap-northeast-1.aws.ml.hana.ondemand.com"}}'

# Optional: Resource group (defaults to 'default')
SAP_AI_RESOURCE_GROUP=default
```

**Important**: The service key must be a single-line JSON string (remove all line breaks).

### 3. Ensure Perplexity is Deployed

In SAP AI Core, ensure you have:
- A deployment of the Perplexity `sonar` model
- The deployment is in the `foundation-models` scenario
- The deployment is in your specified resource group

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Server                              │
│                  (webSearchTool)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 1. Read AICORE_SERVICE_KEY
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              SAP AI SDK (@sap-ai-sdk/ai-api)                │
│                                                             │
│  resolveDeploymentUrl({                                    │
│    scenarioId: 'foundation-models',                        │
│    model: { name: 'perplexity--sonar' }                    │
│  })                                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 2. Query deployments
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   SAP AI Core API                           │
│         (https://api.ai.xxx/v2/lm/deployments)             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 3. Return deployment URL
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              OAuth2 Token Request                           │
│                                                             │
│  POST {serviceKey.url}/oauth/token                         │
│  Body: client_credentials grant                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 4. Return access_token
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Perplexity Client                              │
│                                                             │
│  baseURL: deploymentUrl                                    │
│  headers: { Authorization: Bearer {token} }                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 5. API Request
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            SAP Generative AI Hub                            │
│          (Proxies to Perplexity AI)                         │
└─────────────────────────────────────────────────────────────┘
```

## Benefits of SAP AI SDK Integration

### ✅ Automatic Deployment Discovery
- No need to manually find deployment URLs
- SDK queries AI Core and finds the right deployment
- Handles multiple deployments and resource groups

### ✅ Simplified Configuration
- Single `AICORE_SERVICE_KEY` environment variable
- No separate endpoint and token management
- Service key contains all necessary credentials

### ✅ OAuth2 Handled Correctly
- Implements proper client credentials flow
- Tokens are requested on-demand
- Follows SAP's authentication patterns

### ✅ Resource Group Support
- Configurable via `SAP_AI_RESOURCE_GROUP`
- Defaults to `'default'` if not specified
- Passed in request headers

## Mock Mode Fallback

If `AICORE_SERVICE_KEY` is not configured, the tool automatically falls back to mock mode:

```typescript
try {
  const client = await createPerplexityClient();
  // ... use real API
} catch (error) {
  if (error.message.includes('AICORE_SERVICE_KEY')) {
    console.warn('SAP AI Core not configured, using mock web search');
    return mockWebSearch(query, maxResults);
  }
  throw error;
}
```

This allows:
- Development without SAP infrastructure
- Testing with predictable responses
- Gradual migration to production

## Dependencies

### Installed Packages

```json
{
  "@sap-ai-sdk/ai-api": "^2.1.0",
  "@sap-cloud-sdk/connectivity": "^3.x",
  "@sap-cloud-sdk/http-client": "^3.x",
  "@perplexity-ai/perplexity_ai": "^0.16.0"
}
```

### What Each Package Does

- **`@sap-ai-sdk/ai-api`**: Deployment resolution, AI Core API client
- **`@sap-cloud-sdk/connectivity`**: Destination and authentication utilities
- **`@sap-cloud-sdk/http-client`**: HTTP client with SAP-specific features
- **`@perplexity-ai/perplexity_ai`**: Perplexity AI SDK for chat completions

## Troubleshooting

### Error: "AICORE_SERVICE_KEY environment variable is required"

**Cause**: The environment variable is not set

**Solution**: 
1. Copy your service key from SAP BTP Cockpit
2. Add to `.env` file as a single-line JSON string
3. Restart the MCP server

### Error: "Could not resolve Perplexity deployment URL"

**Cause**: No Perplexity deployment found in SAP AI Core

**Solution**:
1. Verify Perplexity is deployed in your AI Core instance
2. Check the deployment is in the correct resource group
3. Ensure the model name is `perplexity--sonar`

### Error: "Failed to obtain OAuth2 token"

**Cause**: Invalid service key credentials

**Solution**:
1. Verify the service key is correct and up-to-date
2. Check `clientid` and `clientsecret` are valid
3. Ensure the OAuth2 URL is accessible

### Mock Mode Activates Unexpectedly

**Cause**: Service key is not properly configured

**Solution**:
1. Check `.env` file has `AICORE_SERVICE_KEY` set
2. Verify the JSON is valid (use a JSON validator)
3. Ensure no line breaks in the service key string

## Token Lifecycle

### Current Implementation
- Tokens are requested on each tool invocation
- No caching or token reuse
- Simple but may hit rate limits with high usage

### Future Enhancement
```typescript
// Cache tokens with expiration
let cachedToken: { value: string; expiresAt: number } | null = null;

async function getAuthToken(): Promise<string> {
  if (cachedToken && Date.now() < cachedToken.expiresAt) {
    return cachedToken.value;
  }
  
  // Request new token
  const tokenData = await requestOAuth2Token();
  cachedToken = {
    value: tokenData.access_token,
    expiresAt: Date.now() + (tokenData.expires_in * 1000) - 60000, // 1min buffer
  };
  
  return cachedToken.value;
}
```

## Security Best Practices

### ✅ Do's
- Store service key in `.env` file (gitignored)
- Use environment variables for all credentials
- Rotate service keys periodically
- Monitor OAuth2 token usage

### ❌ Don'ts
- Never commit `.env` file to git
- Don't hardcode service keys in code
- Don't share service keys in documentation
- Don't log full service key or tokens

## Next Steps

1. **Test the Integration**:
   ```bash
   # Set your service key in .env
   echo "AICORE_SERVICE_KEY='...'" >> .env
   
   # Start the server
   pnpm dev
   
   # Test with MCP client
   ```

2. **Monitor Performance**:
   - Check OAuth2 token request times
   - Monitor deployment resolution latency
   - Track API response times

3. **Optimize for Production**:
   - Implement token caching
   - Add retry logic for transient failures
   - Set up monitoring and alerting

## Related Documentation

- [SAP AI SDK Documentation](https://sap.github.io/ai-sdk/)
- [SAP AI Core Service Guide](https://help.sap.com/docs/sap-ai-core)
- [OAuth 2.0 Client Credentials](https://oauth.net/2/grant-types/client-credentials/)
