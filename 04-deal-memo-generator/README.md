# Part 4: Agentic Deal Memo Generator

> **Goal:** Build an **agentic workflow** using LangGraph's supervisor pattern to generate a professional Japanese Investment Memo (案件概要書).

---

## 🎯 What You'll Build

An **agentic AI system** that:
- Uses a **supervisor LLM** to decide which tools to call
- Implements **conditional routing** based on LLM decisions
- Loops until the supervisor has enough data
- Includes a **quality check** with optional refinement
- Generates a formal Japanese 案件概要書 (Deal Memo)

---

## 🧠 Agentic vs Sequential

| Sequential (Old) | Agentic (New) |
|------------------|---------------|
| Hardcoded order: stock → news → docs → memo | LLM decides what to gather next |
| Always runs all steps | Stops when it has enough data |
| No quality feedback | Quality check with refinement loop |
| Simple linear flow | Conditional edges + loops |

---

## 🏗️ Architecture

```
                    ┌─────────────┐
                    │   START     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
              ┌─────│  Supervisor │◄────────────────┐
              │     └──────┬──────┘                 │
              │            │ (decides next action)  │
              │     ┌──────┴──────┐                 │
              │     │ Conditional │                 │
              │     │   Edges     │                 │
              │     └─────┬───────┘                 │
              │           │                         │
    ┌─────────┼───────────┼───────────┐            │
    │         │           │           │            │
┌───▼───┐ ┌───▼───┐ ┌─────▼─────┐ ┌───▼────┐      │
│ Stock │ │ News  │ │   Docs    │ │Generate│      │
│ Node  │ │ Node  │ │   Node    │ │  Memo  │      │
└───┬───┘ └───┬───┘ └─────┬─────┘ └───┬────┘      │
    │         │           │           │            │
    └─────────┴───────────┴───────────┘            │
              │                       │            │
              │ (back to supervisor)  │            │
              └───────────────────────┘            │
                                      │            │
                               ┌──────▼──────┐     │
                               │   Quality   │     │
                               │    Check    │     │
                               └──────┬──────┘     │
                                      │            │
                               ┌──────┴──────┐     │
                               │ score < 6?  │─YES─┘
                               └──────┬──────┘ (refine)
                                      │ NO
                               ┌──────▼──────┐
                               │     END     │
                               └─────────────┘
```

---

## 🚀 Steps

### 1. Install Dependencies

```bash
cd 04-deal-memo-generator
uv sync
```

### 2. Run the Generator

```bash
uv run python memo_generator.py
```

---

## 🏋️ Exercises

### Exercise 4a: Study the State Definition

The `MemoState` TypedDict defines what data flows through the graph:
- `stock_data`, `news_data`, `doc_data`: Gathered information
- `next_action`: Supervisor's decision
- `gathered_sources`: Track what's been collected
- `quality_score`: Quality rating (1-10)

### Exercise 4b: Implement Helper Functions

```python
def get_hana_connection():
    # TODO: Reuse the HANA connection pattern from Part 1/3
```

### Exercise 4c: Implement MCP Tool Calls

```python
async def call_mcp_stock(ticker: str) -> dict:
    # TODO: Call MCP server to get stock info (reuse Part 2/3 pattern)

async def call_mcp_news(query: str) -> str:
    # TODO: Call MCP server to search news

def get_documents(company_name: str) -> str:
    # TODO: Retrieve documents from HANA vector store
```

### Exercise 4d: Implement Node Functions

```python
async def supervisor_node(state: MemoState) -> dict:
    # TODO: LLM decides what action to take next
    # Key: Format SUPERVISOR_PROMPT and parse the response

async def get_stock_node(state: MemoState) -> dict:
    # TODO: Fetch stock data via MCP

async def generate_memo_node(state: MemoState) -> dict:
    # TODO: Generate the Deal Memo using gathered data

async def quality_check_node(state: MemoState) -> dict:
    # TODO: Rate the memo quality (1-10)
```

### Exercise 4e: Implement Routing Functions

```python
def route_supervisor(state) -> Literal["get_stock", "get_news", "get_docs", "generate_memo"]:
    # TODO: Return the supervisor's decision from state

def route_quality(state) -> Literal["refine", "end"]:
    # TODO: If score < 6 and iteration < 2, refine; else end
```

### Exercise 4f: Build the LangGraph Agent

```python
def build_agent():
    # TODO: Create StateGraph with MemoState
    # TODO: Add nodes (supervisor, get_stock, get_news, get_docs, generate_memo, quality_check)
    # TODO: Add conditional edges from supervisor
    # TODO: Add edges from tools back to supervisor
    # TODO: Add quality check routing
    # TODO: Compile and return
```

---

## 💡 Key Concepts

### Supervisor Pattern

The supervisor LLM acts as a "manager" that:
1. Evaluates current state (what data do we have?)
2. Decides next action (get_stock, get_news, get_docs, or generate_memo)
3. Loops until satisfied

### Conditional Edges

LangGraph's `add_conditional_edges` allows routing based on state:
```python
builder.add_conditional_edges(
    "supervisor",
    route_supervisor,  # Function that returns next node name
    {"get_stock": "get_stock", "get_news": "get_news", ...}
)
```

### Quality Check Loop

After generating the memo, a quality check node rates it 1-10.
If score < 6, the graph loops back to regenerate.

---

## ✅ Success Criteria

```
📝 DealCrafter - Agentic 案件概要書 Generator
============================================================
Target: Sakura Internet (3778.T)
Mode: Supervisor Agent with Tool Loop

🧠 Supervisor evaluating next action...
   → Decision: get_stock

📊 Fetching stock data for 3778.T...
   ✅ Price: ¥5,230 (+2.3%)

🧠 Supervisor evaluating next action...
   → Decision: get_news

📰 Searching news for Sakura Internet...
   ✅ Found news articles

🧠 Supervisor evaluating next action...
   → Decision: get_docs

📄 Retrieving documents...
   ✅ Retrieved 5 document chunks

🧠 Supervisor evaluating next action...
   → Decision: generate_memo

📝 Generating Deal Memo...
   ✅ Memo generated

🔍 Quality check...
   → Quality score: 8/10

============================================================
=== 案件概要書 (Deal Memo) ===
============================================================
# 案件概要書 (Deal Memo): さくらインターネット株式会社
...

📊 Final quality score: 8/10
📋 Sources used: stock, news, docs
🎉 Deal Memo generation complete!
```

---

## 🏁 Congratulations!

You've built a complete **Agentic DealCrafter** that:
1. ✅ Uses a supervisor LLM to orchestrate tool calls
2. ✅ Implements conditional routing with LangGraph
3. ✅ Loops until the agent has enough data
4. ✅ Includes quality check with refinement
5. ✅ Generates bilingual Japanese reports

**This is true agentic AI - the LLM decides, not the code!**
