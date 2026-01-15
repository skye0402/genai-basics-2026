# DealCrafter Backend

FastAPI backend with DeepAgent for the DealCrafter financial research assistant.

## Features

- **DeepAgent Integration**: LangGraph-based agent with MCP tool support
- **SSE Streaming**: Real-time response streaming to frontend
- **Session Management**: Persistent chat history with SQLite storage
- **Multimodal Support**: Image attachments in chat messages
- **LiteLLM Proxy**: LLM integration via OpenAI-compatible LiteLLM endpoint

## Prerequisites

- Python 3.12+
- uv (Python package manager)

## Installation

```bash
python dev_setup.py
```

## Development

Start the development server:

```bash
python dev_setup.py --install deepagents --start-server
```

The backend runs on http://localhost:8000.

To enable auto-reload file watching (optional):

```bash
UVICORN_RELOAD=true python dev_setup.py --start-server
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Required Environment Variables

```env
# LiteLLM (OpenAI-compatible)
LITELLM_PROXY_URL=https://your-litellm-host/
LITELLM_API_KEY=sk-your-key

# Audio transcription (SAP AI Core)
AICORE_BASE_URL=https://api.ai.<region>.aws.ml.hana.ondemand.com/v2
AICORE_AUTH_URL=https://<subdomain>.authentication.<region>.hana.ondemand.com/oauth/token
AICORE_CLIENT_ID=...
AICORE_CLIENT_SECRET=...
AICORE_RESOURCE_GROUP=...

# Resolve deployment URL by model name (recommended)
AUDIO_MODEL_NAME=gemini-2.5-flash

# Or override with an explicit deployment id
# AUDIO_DEPLOYMENT_ID=<deployment-id>

# Audio is sent to Gemini as multimodal inline data via the deployment's
# /models/{model}:generateContent endpoint (no api-version parameter).

# Mode Configuration
MOCK_MODE=false           # Set to true for testing without external LLM connectivity
AGENTIC_MODE=true         # Enable DeepAgent with MCP tools

# LLM Model
LLM_MODEL=gpt-4.1
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── chat.py             # Chat streaming endpoint
│   │   └── chat_history.py     # Session management
│   ├── core/             # Core configuration
│   │   └── config.py           # Settings from environment
│   ├── models/           # Pydantic models
│   │   └── schemas.py          # Request/response schemas
│   ├── services/         # Business logic
│   │   ├── deepagent_service.py    # DeepAgent with MCP tools
│   │   ├── llm_service.py          # Simple LLM service
│   │   ├── mock_service.py         # Mock responses for testing
│   │   └── service_factory.py      # Service routing
│   ├── storage/          # Data persistence
│   │   └── session_storage.py      # SQLite session storage
│   └── main.py           # FastAPI application
├── tests/                # Test files
├── data/                 # SQLite database (gitignored)
├── pyproject.toml        # Python dependencies
└── uv.lock               # Dependency lock file
```

## API Endpoints

### Chat

- `POST /api/chat-stream` - Stream chat responses (SSE)

### Sessions

- `GET /api/sessions` - List all chat sessions
- `GET /api/sessions/{session_id}` - Get session with messages
- `POST /api/sessions` - Create new session
- `DELETE /api/sessions/{session_id}` - Delete session

### Health

- `GET /health` - Health check endpoint

## Service Modes

The backend supports three service modes controlled by environment variables:

1. **Mock Mode** (`MOCK_MODE=true`): Returns simulated responses for testing
2. **LLM Mode** (`AGENTIC_MODE=false`): Simple LLM without tools
3. **Agentic Mode** (`AGENTIC_MODE=true`): DeepAgent with MCP tools (default)

## MCP Tool Integration

When running in agentic mode, the backend connects to the MCP server at `http://localhost:3001/mcp` and loads available tools:

- `web_search` - Perplexity web search
- `web_research` - Deep web research
- `search_document_content` - RAG document search
- `get_stock_info` - Yahoo Finance stock data
- `get_time_and_place` - Time/location context

## Browser Timezone Support

The backend accepts an optional `timezone` field in chat requests. When provided, it's prepended to the user message as context, allowing the agent to greet users based on their local time.
