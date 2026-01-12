# Part 2: The Data Connector (MCP)

> **Goal:** Connect the agent to live market data using MCP tools.

---

## 🎯 What You'll Build

An **MCP Server** exposing two tools:
1. **`get_stock_info`** – Fetch real-time stock prices via `yfinance`
2. **`search_market_news`** – Search market news via Perplexity AI

An **Agent Client** that connects to the MCP server and uses the tools automatically.

---

## 📋 Scenario

> "Our analyst needs real-time stock prices for {TICKER} and market news about {COMPANY_NAME}. Let's give the AI these superpowers."

---

## 🚀 Steps

### 1. Install Dependencies

```bash
cd 02-data-connector-mcp
uv sync
```

### 2. Test the MCP Server (Inspector)

```bash
uv run mcp dev mcp_server.py
```

This opens the MCP Inspector where you can test your tools interactively.

After setup you can test the MCP server **on its own** using the MCP Inspector web UI.
This is useful for debugging your tools before wiring them into the agent.

1. In the Inspector UI:
   - **Transport type**: `STDIO`
   - **Command**: `python`
   - **Arguments**: `mcp_server.py`
2. Click **Connect**, then use the **Tools** tab to call your MCP tools interactively.

### 3. Run the Agent Client

```bash
uv run python agent_client.py
```

Ask questions like:
- "What's the current stock price of 3382.T?"
- "Search for recent news about Seven & i Holdings takeover"

---

## 🏋️ Exercises

### Exercise 2a: Stock Info Tool (`mcp_server.py`)

Implement `get_stock_info()` using `yfinance`:

```python
import yfinance as yf

@mcp.tool()
def get_stock_info(ticker: str) -> dict:
    """Get current stock information for a ticker symbol."""
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "currency": info.get("currency", "JPY"),
        # TODO: Add more fields
    }
```

### Exercise 2b: News Search Tool (`mcp_server.py`)

Implement `search_market_news()` using Perplexity AI:

```python
from gen_ai_hub.proxy.langchain.init_models import init_llm

@mcp.tool()
def search_market_news(query: str, limit: int = 5) -> str:
    """Search for recent market news about a topic."""
    perplexity = init_llm("perplexity--sonar-pro", max_tokens=4000)
    # TODO: Invoke Perplexity and return results
```

---

## 💡 Key Concepts

### What is MCP?

**Model Context Protocol** is a standard for connecting AI systems to external tools. Benefits:
- **Language-agnostic** – Python server, JavaScript client (or vice versa)
- **Reusable** – Build once, use in multiple agents
- **Testable** – MCP Inspector for debugging

### Tool Structure

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.tool()
def my_tool(arg1: str, arg2: int) -> dict:
    """Tool description shown to the LLM."""
    return {"result": "..."}
```

---

## 🔧 Testing with MCP Inspector

```bash
uv run mcp dev mcp_server.py
```

In the inspector:
1. Click on a tool
2. Enter test parameters
3. Click "Run" to see the result

---

## ✅ Success Criteria

MCP Inspector shows:
```json
{
  "ticker": "3778.T",
  "price": 5230.0,
  "currency": "JPY",
  "company_name": "Sakura Internet Inc."
}
```

Agent client:
```
You: What's the stock price of Sakura Internet?
🔧 Calling tool: get_stock_info({"ticker": "3778.T"})
✅ Result: {"ticker": "3778.T", "price": 5230.0, ...}
Assistant: Sakura Internet (3778.T) is currently trading at ¥5,230...
```

---

## ➡️ Next Step

Once your tools are working, proceed to **Part 3: The Analyst Workflow (LangGraph)**!
