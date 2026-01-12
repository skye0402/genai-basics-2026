# Part 5: DealCrafter Assembled (Complete Demo)

> **The complete DealCrafter Assistant** with a polished React frontend.
> This is the **final demo/target state** – fully functional out of the box.

---

## 🎯 What This Is

A fully assembled version combining:
- **React Frontend** (UI5 Fiori) – Beautiful chat interface with streaming
- **Python Backend** (FastAPI + DeepAgent) – LangGraph orchestration
- **MCP Server** (Node.js) – Stock data, news search, document tools

This folder contains **complete copies** of all three tiers, customized for DealCrafter.

---

## 🏗️ Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│     Frontend        │────▶│      Backend        │────▶│    Backend-MCP      │
│  React + UI5 Fiori  │     │  FastAPI + DeepAgent │     │  Node.js + MCP      │
│    Port: 5173       │     │    Port: 8000       │     │    Port: 3001       │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                                     │                           │
                                     ▼                           ▼
                            ┌─────────────────┐        ┌─────────────────────┐
                            │ SAP GenAI Hub   │        │ Tools:              │
                            │ (LLM + Embed)   │        │ - get_stock_info    │
                            └─────────────────┘        │ - web_search        │
                                                       │ - web_research      │
                                                       │ - search_document_content│
                                                       │ - get_time_and_place│
                                                       └─────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js 20+** and **pnpm**
- **Python 3.12+** and **uv**

### Step 1: Start Backend-MCP (Port 3001)

```bash
cd backend-mcp
pnpm install
pnpm dev
```

### Step 2: Start Backend (Port 8000)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

### Step 3: Start Frontend (Port 5173)

```bash
cd frontend
pnpm install
pnpm dev
```

### Step 4: Open Browser

Navigate to http://localhost:5173

---

## 🔧 Configuration

### Backend-MCP `.env.local`

```env
# SAP AI Core service key (JSON)
AICORE_SERVICE_KEY={"clientid":"...","clientsecret":"...","url":"...","serviceurls":{"AI_API_URL":"..."}}
SAP_AI_RESOURCE_GROUP=default

# HANA Cloud (for document search)
HANA_HOST=your-instance.hanacloud.ondemand.com
HANA_PORT=443
HANA_USER=WORKSHOP01
HANA_PASSWORD=your-password
```

### Backend `.env`

```env
# SAP GenAI Hub
AICORE_CLIENT_ID=your-client-id
AICORE_CLIENT_SECRET=your-client-secret
AICORE_AUTH_URL=https://your-subdomain.authentication.region.hana.ondemand.com
AICORE_BASE_URL=https://api.ai.region.aws.ml.hana.ondemand.com

# Mode
MOCK_MODE=false
AGENTIC_MODE=true  # Enable DeepAgent with MCP tools

# LLM
LLM_MODEL=gpt-4.1
```

---

## 💬 Example Interactions

### Stock Analysis
```
User: What's the current price of Sakura Internet (3778.T)?

🔧 Calling: get_stock_info(ticker="3778.T")
✅ Result: {price: 5230, currency: "JPY", change: +2.3%}
