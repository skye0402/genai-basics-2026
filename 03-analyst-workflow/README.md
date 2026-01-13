# Part 3: The Analyst Workflow

> **Goal:** Orchestrate complex multi-step analysis using LangGraph and MCP tools.

---

## 🎯 What You'll Build

A **LangGraph workflow** that chains together multiple analysis steps using **MCP (Model Context Protocol) tools**:
1. **Fetch Stock** → Get current stock data via MCP tools
2. **Search News** → Find recent market news via MCP tools
3. **Retrieve Docs** → Query ingested PDFs via RAG
4. **Analyze** → Generate a comprehensive analysis

---

## 📋 Scenario

> "Build an analyst workflow for {COMPANY_NAME}: Fetch stock data → Search news → Retrieve internal docs → Analyze → Generate preliminary report."

**Track A Focus:** Analyze the Couche-Tard takeover: risk vs. opportunity  
**Track B Focus:** Analyze Sakura's government AI contracts: sustainable growth vs. bubble

---

## 🚀 Steps

### 1. Install Dependencies

```bash
cd 03-analyst-workflow
uv sync
```

### 2. Run the Workflow

```bash
uv run python analyst_agent.py
```

---

## 🏗️ Workflow Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌───────────────┐
│ User Query  │────▶│ Fetch Stock  │────▶│ Search News  │────▶│ Retrieve Docs │
│ {COMPANY}   │     │  (via MCP)   │     │  (via MCP)   │     │ (RAG)         │
└─────────────┘     └──────────────┘     └──────────────┘     └───────┬───────┘
                                                                      │
                                                                      ▼
                                                            ┌─────────────────┐
                                                            │ Analyze &       │
                                                            │ Summarize       │
                                                            └─────────────────┘
```

---

## ⚠️ Exercise Design

**The graph structure is 100% pre-built.** You focus ONLY on implementing the logic inside each node.

### What's Provided (DO NOT MODIFY)
- State schema (`AnalystState`)
- Graph definition with all nodes and edges
- Main execution loop
- MCP helper functions structure

### What You Implement
- `retrieve_docs_node()` – Query HANA vector store
- `analyze_node()` – Craft prompt and call LLM

---

## 🏋️ Exercises

### Exercise 3a: `fetch_stock_node`
```python
async def fetch_stock_node(state: AnalystState) -> dict:
    # TODO: Use await _async_get_stock_info(state["ticker"])
    # Return: {"stock_info": {...}, "step_count": state["step_count"] + 1}
```

### Exercise 3b: `search_news_node`
```python
async def search_news_node(state: AnalystState) -> dict:
    # TODO: Use await _async_search_news(query, 5)
    # Return: {"news_results": "...", "step_count": state["step_count"] + 1}
```

### Exercise 3c: `retrieve_docs_node`
```python
async def retrieve_docs_node(state: AnalystState) -> dict:
    # TODO: Query HANA vector store with HanaDB and retriever
    # Return: {"doc_context": "...", "step_count": state["step_count"] + 1}
```

### Exercise 3d: `analyze_node`
```python
async def analyze_node(state: AnalystState) -> dict:
    # TODO: Combine all data sources and call LLM
    # Return: {"analysis": "..."}
```

---

## 🔌 MCP Integration

This module integrates with the **Model Context Protocol (MCP)** to access tools from the `02-data-connector-mcp` module:

### MCP Tools Used
- **`get_stock_info(ticker)`** - Fetches current stock data using yfinance
- **`search_market_news(query, limit)`** - Searches recent news using Perplexity AI

### MCP Connection Pattern
The code uses direct MCP tool calls through async helper functions:

```python
async def _async_get_stock_info(ticker: str) -> dict:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).parent.parent / "02-data-connector-mcp" / "mcp_server.py")],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_stock_info", {"ticker": ticker})
            return result.content
```

---

## 💡 Key Concepts

### LangGraph State
```python
class AnalystState(TypedDict):
    company_name: str
    ticker: str
    query: str
    stock_info: dict
    news_results: str
    doc_context: str
    analysis: str
    step_count: int
```

### Node Functions
Each node receives the current state and returns updates:
```python
async def my_node(state: AnalystState) -> dict:
    # Do async work...
    return {"field_to_update": new_value}
```

### Graph Edges
```python
graph.add_edge("node_a", "node_b")  # A → B
graph.add_edge(START, "first_node")
graph.add_edge("last_node", END)
```

### Async Execution
The workflow runs asynchronously:
```python
result = await agent.ainvoke({
    "company_name": COMPANY_NAME,
    "ticker": TICKER,
    "query": query,
    # ... other state fields
})
```

---

## ✅ Success Criteria

```
🔄 Starting analyst workflow for Sakura Internet (3778.T)
📊 Step 1: Fetching stock data for 3778.T...
   ✅ Price: ¥5,230 (▲2.3%)
📰 Step 2: Searching news for Sakura Internet...
   ✅ Found news articles
📄 Step 3: Retrieving documents...
   ✅ Retrieved 5 relevant chunks
🧠 Step 4: Analyzing...

=== ANALYSIS RESULT ===
Based on the available data...
```

---

## ➡️ Next Step

Once your workflow produces analysis, proceed to **Part 4: The Deal Memo Generator**!
