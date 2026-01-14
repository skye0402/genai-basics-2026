# Perplexity Sonar Integration for SAP Generative AI Hub

This module provides integration for Perplexity's Sonar and Sonar Pro models through SAP Generative AI Hub, using the SDK's deployment selection mechanism for models not yet officially listed in the "Supported Models" table.

## Overview

Perplexity's Sonar models are "online" LLMs that can perform real-time web searches and access current information, making them ideal for:
- News gathering and research
- Market intelligence
- Real-time data analysis
- Current events monitoring

## Supported Models

- **sonar**: Base Perplexity model with online search capabilities
- **sonar-pro**: Advanced model with enhanced reasoning and search performance

## Prerequisites

### 1. SAP Generative AI Hub Setup

Ensure you have:
- Active SAP BTP account with AI Core/Generative AI Hub enabled
- Valid AI Core credentials (client ID, secret, auth URL, base URL)
- Appropriate resource group access

### 2. Perplexity Deployment

You must have a **RUNNING** Perplexity deployment in your SAP Generative AI Hub:

1. Log in to SAP AI Launchpad
2. Navigate to **ML Operations** > **Deployments**
3. Verify you have a deployment with:
   - Model name: `sonar` or `sonar-pro`
   - Version: `perplexity-us`
   - Status: **RUNNING** (green)
   - Scenario: `foundation-models` (or your custom scenario)

**Finding your deployment:**
- Note the **Deployment ID** (format: `dxxxxxxxxxxxxxxx`)
- Note the exact **Model Name** (should be `sonar` or `sonar-pro`)

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Required: AI Core credentials
AICORE_CLIENT_ID=sb-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx!b1808|aicore!b44
AICORE_CLIENT_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx$xxxxxxxxxxxxxxxxxxxxx
AICORE_AUTH_URL=https://your-subdomain.authentication.jp10.hana.ondemand.com
AICORE_BASE_URL=https://api.ai.prod.ap-northeast-1.aws.ml.hana.ondemand.com
AICORE_RESOURCE_GROUP=generative-ai

# Perplexity Model Selection
PERPLEXITY_MODEL=perplexity--sonar-pro  # or perplexity--sonar

# Optional: Pin to specific deployment (recommended if you have multiple)
PERPLEXITY_DEPLOYMENT_ID=dxxxxxxxxxxxxxxx

# Optional: Custom scenario (only if not using foundation-models)
# PERPLEXITY_SCENARIO_ID=foundation-models
```

## Usage

### Basic Usage

```python
from genai.perplexity_sonar import PerplexitySonarClient

# Create client
client = PerplexitySonarClient(
    model_name="sonar-pro",  # or "sonar"
    temperature=0.1,
    max_tokens=2000
)

# Simple prompt
response = client.invoke("What are the latest trends in AI?")
print(response)
```

### With Factory Function

```python
from genai.perplexity_sonar import create_perplexity_client
import os

# Creates client from environment variables
client = create_perplexity_client(
    model=os.getenv("PERPLEXITY_MODEL", "perplexity--sonar-pro"),
    temperature=0.1,
    max_tokens=2000,
    deployment_id=os.getenv("PERPLEXITY_DEPLOYMENT_ID")
)

response = client.invoke("Search for recent AI developments")
```

### Chat Format

```python
messages = [
    {"role": "system", "content": "You are a research assistant."},
    {"role": "user", "content": "What's the latest news about Tesla?"}
]

response = client.chat(messages=messages)
print(response)
```

### In the Deal Memo Generator

The `04-deal-memo-generator-done/memo_generator.py` uses Perplexity for news gathering:

```python
def gather_news() -> str:
    """Search for recent news using Perplexity Sonar/Sonar Pro."""
    perplexity = create_perplexity_client(
        model=PERPLEXITY_MODEL,
        temperature=0.1,
        max_tokens=2000,
        deployment_id=PERPLEXITY_DEPLOYMENT_ID
    )
    
    prompt = f"""Search for the 5 most recent news articles about {COMPANY_NAME}..."""
    response = perplexity.invoke(prompt)
    return response
```

## How It Works

### SDK Integration Pattern

This implementation uses the SAP AI SDK's "unsupported model" pattern:

1. **Proxy Client**: Uses `gen_ai_hub.proxy.native.openai.clients.OpenAI`
2. **Deployment Selection**: Automatically selects deployments via `GenAIHubProxyClient.select_deployment()`
3. **OpenAI-Compatible API**: Calls through the GenAI Hub OpenAI proxy
4. **No Hardcoded Routes**: Uses SDK's deployment routing instead of fixed URLs

### Behind the Scenes

```python
# The client does this internally:
proxy_client = GenAIHubProxyClient.from_env()
deployment = proxy_client.select_deployment(model_name="sonar-pro")

# Then routes through OpenAI proxy:
openai_client = OpenAI()  # Uses GenAI Hub proxy
response = openai_client.chat.completions.create(
    model_name="sonar-pro",  # Routes to your deployment
    messages=[...]
)
```

## Troubleshooting

### Error: "Could not find Perplexity deployment"

**Cause**: No matching deployment found in GenAI Hub

**Solutions**:
1. Verify deployment is RUNNING in AI Launchpad
2. Check model name matches exactly: `sonar` or `sonar-pro`
3. Set explicit `PERPLEXITY_DEPLOYMENT_ID` in .env
4. Verify AI Core credentials are correct
5. Check resource group access

### Error: "Multiple deployments match the query"

**Cause**: Multiple Perplexity deployments with same model name

**Solution**: Set `PERPLEXITY_DEPLOYMENT_ID` to pin to a specific deployment:
```bash
PERPLEXITY_DEPLOYMENT_ID=d1234567890abcdef
```

### Error: Authentication failed

**Cause**: Invalid or expired AI Core credentials

**Solutions**:
1. Regenerate service key in BTP Cockpit
2. Update credentials in .env
3. Verify auth URL and base URL are correct
4. Check resource group name

### Custom Scenario

If your Perplexity deployments are in a custom scenario (not `foundation-models`):

```python
from gen_ai_hub.proxy.gen_ai_hub_proxy.client import GenAIHubProxyClient

# Register custom scenario before creating client
GenAIHubProxyClient.add_foundation_model_scenario(
    scenario_id="your-custom-scenario",
    config_names="*"
)

# Then create client normally
client = create_perplexity_client(...)
```

## Model Characteristics

### Sonar (Base Model)
- Real-time web search
- General knowledge queries
- Suitable for most research tasks
- Lower cost

### Sonar Pro (Advanced Model)
- Enhanced reasoning capabilities
- Better at complex queries
- Improved search quality
- More detailed responses
- Higher cost

## Best Practices

1. **Temperature**: Use 0.0-0.2 for factual research, 0.3-0.7 for creative tasks
2. **Max Tokens**: Set 1000-2000 for summaries, 3000-4000 for detailed analysis
3. **Prompting**: Be specific about:
   - Time frame ("last 24 hours", "this month")
   - Source types (news, research, official announcements)
   - Output format (bullets, paragraphs, structured data)
4. **Rate Limits**: Be aware of GenAI Hub quotas for your deployment
5. **Caching**: Consider caching frequent queries to avoid redundant calls

## Example: News Research

```python
from genai.perplexity_sonar import create_perplexity_client

client = create_perplexity_client(model="perplexity--sonar-pro")

prompt = """Search for the most recent news about Apple Inc. in the last 7 days.

Focus on:
- Product announcements
- Financial results
- Executive changes
- Strategic partnerships

For each article:
- Title
- 2-3 sentence summary
- Source and date
"""

news = client.invoke(prompt)
print(news)
```

## Testing

Test your integration:

```bash
# Run the deal memo generator with Perplexity news gathering
cd 04-deal-memo-generator-done
uv run python memo_generator.py
```

Expected output:
```
📰 Searching news for Sakura Internet...
✅ Found Perplexity deployment: dxxxxxxxxxxxxxxx
   Model: sonar-pro
   Config: perplexity-sonar-pro
✅ Found recent articles
```

## API Reference

### PerplexitySonarClient

```python
class PerplexitySonarClient:
    def __init__(
        self,
        model_name: Literal["sonar", "sonar-pro"] = "sonar-pro",
        temperature: float = 0.1,
        max_tokens: int = 2000,
        deployment_id: Optional[str] = None,
        top_p: Optional[float] = None,
    )
    
    def invoke(self, prompt: str, stream: bool = False) -> str
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> str
```

### create_perplexity_client

```python
def create_perplexity_client(
    model: str = "perplexity--sonar-pro",
    temperature: float = 0.1,
    max_tokens: int = 2000,
    deployment_id: Optional[str] = None,
) -> PerplexitySonarClient
```

## Related Documentation

- [SAP Generative AI Hub SDK Documentation](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html)
- [SAP AI Core Documentation](https://help.sap.com/docs/AI_CORE)
- [Perplexity AI Documentation](https://docs.perplexity.ai/)

## Support

For issues specific to:
- **This integration**: Check GitHub issues or contact the workshop team
- **SAP AI Core/GenAI Hub**: Use SAP Support Portal
- **Perplexity models**: Refer to Perplexity documentation

## License

This integration is part of the DealCrafter workshop materials.
