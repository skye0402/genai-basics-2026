# Part 2: The Data Connector (Complete)

> **This is the complete, runnable version.** Use this if you want to skip the exercise.

---

## 🚀 Quick Run

```bash
cd 02-data-connector-mcp-done
uv sync

# Test with MCP Inspector
uv run mcp dev mcp_server.py

# Or run the agent client
uv run python agent_client.py --verbose
```

---

## ✅ Expected Output

```
🔌 Connecting to MCP Server...
✅ Loaded 3 tools from MCP server:
   - get_stock_info: Get current stock information...
   - search_market_news: Search for recent market news...
   - get_stock_history: Get historical stock data...

🤖 DealCrafter Agent Ready!
   Analyzing: Sakura Internet (3778.T)

You: What's the current stock price?
  🔧 Calling tool: get_stock_info({"ticker": "3778.T"})
  ✅ Result: {"ticker": "3778.T", "price": 5230.0, "currency": "JPY"...}
