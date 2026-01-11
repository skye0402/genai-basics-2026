# Part 3: The Analyst Workflow

> **Goal:** Orchestrate complex multi-step analysis using LangGraph.

---

## 🎯 What You'll Build

A **LangGraph workflow** that chains together multiple analysis steps:
1. **Fetch Stock** → Get current stock data
2. **Search News** → Find recent market news
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
│ {COMPANY}   │     │              │     │              │     │ (RAG)         │
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

### What You Implement
- `fetch_stock_node()` – Call yfinance
- `search_news_node()` – Call Perplexity
- `retrieve_docs_node()` – Query HANA vector store
- `analyze_node()` – Craft prompt and call LLM

---

## 🏋️ Exercises

### Exercise 3a: `fetch_stock_node`
```python
def fetch_stock_node(state: AnalystState) -> dict:
    # TODO: Use yfinance to get stock info for state["ticker"]
    # Return: {"stock_info": {...}}
```

### Exercise 3b: `search_news_node`
```python
def search_news_node(state: AnalystState) -> dict:
    # TODO: Use Perplexity to search news about state["company_name"]
    # Return: {"news_results": [...]}
```

### Exercise 3c: `retrieve_docs_node`
```python
def retrieve_docs_node(state: AnalystState) -> dict:
    # TODO: Query HANA vector store with state["query"]
    # Return: {"doc_context": "..."}
```

### Exercise 3d: `analyze_node`
```python
def analyze_node(state: AnalystState) -> dict:
    # TODO: Combine stock_info, news_results, doc_context
    # TODO: Craft a prompt and call the LLM
    # Return: {"analysis": "..."}
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
    news_results: list[dict]
    doc_context: str
    analysis: str
```

### Node Functions
Each node receives the current state and returns updates:
```python
def my_node(state: AnalystState) -> dict:
    # Do work...
    return {"field_to_update": new_value}
```

### Graph Edges
```python
graph.add_edge("node_a", "node_b")  # A → B
graph.add_edge(START, "first_node")
graph.add_edge("last_node", END)
```

---

## ✅ Success Criteria

```
🔄 Starting analyst workflow for Sakura Internet (3778.T)
📊 Step 1: Fetching stock data...
   ✅ Price: ¥5,230 (▲2.3%)
📰 Step 2: Searching news...
   ✅ Found 5 relevant articles
📄 Step 3: Retrieving documents...
   ✅ Retrieved 5 relevant chunks
🧠 Step 4: Analyzing...

=== ANALYSIS RESULT ===
Based on the available data...
```

---

## ➡️ Next Step

Once your workflow produces analysis, proceed to **Part 4: The Deal Memo Generator**!
