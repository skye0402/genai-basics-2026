# DealCrafter Backend

FastAPI backend with DeepAgent for the DealCrafter financial research assistant.

## Features

- **DeepAgent Integration**: LangGraph-based agent with MCP tool support
- **SSE Streaming**: Real-time response streaming to frontend
- **Session Management**: Persistent chat history with SQLite storage
- **Multimodal Support**: Image attachments in chat messages
- **SAP GenAI Hub**: LLM integration via SAP AI Core

## Prerequisites

- Python 3.12+
- uv (Python package manager)

## Installation

```bash
uv sync
```

## Development

Start the development server:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

The backend runs on http://localhost:8000.

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Required Environment Variables

```env
# SAP GenAI Hub Authentication
AICORE_CLIENT_ID=your-client-id
AICORE_CLIENT_SECRET=your-client-secret
AICORE_AUTH_URL=https://your-subdomain.authentication.region.hana.ondemand.com
AICORE_BASE_URL=https://api.ai.region.aws.ml.hana.ondemand.com
AICORE_RESOURCE_GROUP=default

# Mode Configuration
MOCK_MODE=false           # Set to true for testing without SAP infrastructure
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
