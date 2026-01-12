# Workshop Requirements Document (WRD)
## DealCrafter Assistant – Itochu × SAP Workshop

**Date:** TBD  
**Location:** SAP Singapore  
**Customer:** Itochu Corporation (Japan)  
**Target Audience:** Business Investment Division, Corporate Planning  
**Duration:** 10:30 AM – 5:00 PM (with optional Hello World pre-session)

---

## 1. Executive Summary

This workshop teaches participants to build an AI-powered **"DealCrafter Assistant"** that automates market research and generates Investment Memos. The assistant leverages SAP BTP Generative AI Hub, SAP HANA Cloud Vector Engine, and modern agentic AI patterns (LangGraph, MCP).

### Value Proposition
- Accelerates the "Brand-new Deal" investment strategy
- Demonstrates SAP BTP's capability for custom AI solutions
- No ERP integration required – focuses on custom logic and external data sources

### Key "Wow" Factor
**Bilingual AI Analyst:** The system reads global news and documents (English/Japanese) and generates professional Japanese investment reports – acting as a fluent bilingual analyst.

---

## 2. Technical Stack

| Component | Technology | Purpose |
|-----------|------------|----------|
| AI Runtime | SAP BTP Generative AI Hub | LLM access (GPT-4.1, Claude, etc.) |
| Vector Store | SAP HANA Cloud Vector Engine | Document embeddings & RAG |
| Web Search | Perplexity AI (via GenAI Hub) | Real-time market research |
| Stock Data | `yfinance` (Python) | Real-time stock prices (free, no API key) |
| Agent Framework | LangGraph | Workflow orchestration |
| Tool Protocol | MCP (Model Context Protocol) | Tool encapsulation & reusability |
| Language | Python 3.12+ | All exercises |
| Package Manager | uv | Fast, isolated environments |

---

## 3. Workshop Schedule Overview

| Time | Session | Type |
|------|---------|------|
| ~10:00 – 10:30 | **Part 0: Hello World** (optional) | Setup verification |
| 10:30 – 11:30 | **Part 1: The Research Engine** | Hands-on |
| 11:30 – 12:30 | **Part 2: The Data Connector (MCP)** | Hands-on |
| 12:30 – 13:30 | **Networking Lunch** | Break |
| 13:30 – 15:00 | **Part 3: The Analyst Workflow** | Hands-on |
| 15:00 – 15:15 | **Coffee Break** | Break |
| 15:15 – 16:30 | **Part 4: The Deal Memo Generator** | Hands-on |
| 16:30 – 16:45 | **Part 5: DealCrafter Assembled** | Demo (facilitator) |
| 16:45 – 17:00 | **Wrap Up & Value Proposition** | Discussion |

---

## 3.1 Workshop Scenario Tracks

Participants choose one of two real-world investment scenarios (or the room is split):

### Track A: M&A Defense – Seven & i Holdings (3382.T)
| Aspect | Details |
|--------|---------|  
| **Company** | Seven & i Holdings (7-Eleven parent) |
| **Ticker** | 3382.T (Tokyo Stock Exchange) |
| **Context** | Hostile takeover bid by Alimentation Couche-Tard (Canada) |
| **Analysis Goal** | Evaluate risk/benefit of the takeover. Should Itochu support or oppose? |
| **Key Themes** | M&A defense, shareholder activism, retail consolidation |

### Track B: Growth Strategy – Sakura Internet (3778.T)
| Aspect | Details |
|--------|---------|  
| **Company** | Sakura Internet Inc. |
| **Ticker** | 3778.T (Tokyo Stock Exchange) |
| **Context** | Japan's "AI Sovereignty" policy, government cloud partnership |
| **Analysis Goal** | Is the stock overvalued or is the growth sustainable? |
| **Key Themes** | National AI strategy, cloud infrastructure, government contracts |

### Track-Agnostic Design
All code uses variables to remain company-agnostic:
```python
COMPANY_NAME = os.getenv("COMPANY_NAME", "Seven & i Holdings")
TICKER = os.getenv("TICKER", "3382.T")
```

Prompt templates use placeholders: `{COMPANY_NAME}`, `{TICKER}`, `{CONTEXT}`

---

## 4. Folder Structure

Each exercise is **self-contained** with its own `pyproject.toml`, `README.md`, and complete solution. This allows participants who fall behind to continue from a working state.

```
genai-basics-2026/
├── .env.example                    # Template for credentials
├── README.md                       # Workshop overview & setup
├── wrd.md                          # This document
│
├── rag-material/                   # PDF documents for RAG (pre-provided)
│   ├── 7i_holdings/               # Track A materials
│   └── sakura_internet/           # Track B materials
│
├── prompts/                        # Shared prompt templates
│   └── deal_memo_system_prompt.md
│
├── 00-hello-world/                 # Part 0: Setup check (hands-on)
│   ├── README.md
│   ├── main.py                     # TODO: implement LLM call
│   └── pyproject.toml
├── 00-hello-world-done/            # Part 0: Complete (skip-able)
│   ├── README.md
│   ├── main.py
│   └── pyproject.toml
│
├── 01-research-engine/             # Part 1: RAG (hands-on)
│   ├── README.md
│   ├── ingest_pdf.py              # TODO: implement PDF loading
│   ├── chat_documents.py          # TODO: implement RAG chat
│   └── pyproject.toml
├── 01-research-engine-done/        # Part 1: Complete (skip-able)
│   ├── README.md
│   ├── ingest_pdf.py
│   ├── chat_documents.py
│   └── pyproject.toml
│
├── 02-data-connector-mcp/          # Part 2: MCP tools (hands-on)
│   ├── README.md
│   ├── mcp_server.py              # TODO: implement tools
│   ├── agent_client.py            # Pre-built agent client
│   └── pyproject.toml
├── 02-data-connector-mcp-done/     # Part 2: Complete (skip-able)
│   ├── README.md
│   ├── mcp_server.py
│   ├── agent_client.py
│   └── pyproject.toml
│
├── 03-analyst-workflow/            # Part 3: LangGraph (hands-on)
│   ├── README.md
│   ├── analyst_agent.py           # Graph provided; TODO: node logic
│   └── pyproject.toml
├── 03-analyst-workflow-done/       # Part 3: Complete (skip-able)
│   ├── README.md
│   ├── analyst_agent.py
│   └── pyproject.toml
│
├── 04-deal-memo-generator/         # Part 4: Final app (hands-on)
│   ├── README.md
│   ├── memo_generator.py          # TODO: implement memo formatting
│   └── pyproject.toml
├── 04-deal-memo-generator-done/    # Part 4: Complete (skip-able)
│   ├── README.md
│   ├── memo_generator.py
│   └── pyproject.toml
│
├── 05-dealcrafter-assembled/       # Part 5: Full demo with React frontend
│   ├── README.md                  # Architecture overview
│   ├── SETUP.md                   # Integration instructions
│   ├── tools/
│   │   └── stockTool.ts           # Stock info tool for Node.js MCP
│   └── prompts/
│       └── dealcrafter_system.md  # System prompt for DeepAgent
│
├── documentation/                  # Reference materials (from old_workshop)
│
└── old_workshop/                   # Previous workshop (reference only, gitignored)
```

---

## 5. Detailed Exercise Specifications

### Part 0: Hello World (Pre-Session, ~30 min)

**Goal:** Verify all participants have working environments before the main workshop starts.

**What Participants Do:**
1. Clone the repository
2. Copy `.env.example` → `.env` and fill in credentials (provided)
3. Run `uv sync` and execute `main.py`
4. Confirm they receive a response from SAP Generative AI Hub

**Success Criteria:** "Hello from GPT-4.1!" or similar response printed.

**Reuse from old_workshop:** `01-hello-world/main.py` (adapt directly)

---

### Part 1: The Research Engine (10:30 – 11:30, 60 min)

**Goal:** Teach the AI to read financial documents using RAG.

**Scenario:** 
> "We've received {COMPANY_NAME}'s annual report and analyst materials. Let's make them searchable by our AI."

**Track A Example:** Seven & i's investor presentation on the Couche-Tard bid  
**Track B Example:** Sakura Internet's government partnership announcement

**Technical Components:**
- PDF loading with `pypdf` or `unstructured`
- Text chunking with `langchain_text_splitters`
- Embedding generation via SAP GenAI Hub (`text-embedding-3-small`)
- Storage in SAP HANA Cloud Vector Engine via `langchain-hana`
- RAG chat interface for Q&A over documents

**Exercise Structure:**

| File | Exercise Task | Difficulty |
|------|---------------|------------|
| `ingest_pdf.py` | Load PDF, chunk text, store embeddings | ⭐⭐ |
| `chat_documents.py` | Implement retrieval + LLM response | ⭐⭐ |

**Hands-On Steps:**
1. **Explain** (10 min): What is RAG? Vector embeddings? HANA Vector Engine?
2. **Demo** (5 min): Show complete solution ingesting a sample PDF
3. **Exercise** (30 min): Participants implement `ingest_pdf.py`
4. **Test** (10 min): Run chat, ask questions about the document
5. **Wrap-up** (5 min): Show solution, troubleshoot issues

**Key Code Snippets to Provide (in README):**
```python
# HANA connection pattern
from hdbcli import dbapi
conn = dbapi.connect(
    address=os.getenv("HANA_DB_ADDRESS"),
    port=int(os.getenv("HANA_DB_PORT", "443")),
    user=os.getenv("HANA_DB_USER"),
    password=os.getenv("HANA_DB_PASSWORD"),
)

# Embedding init pattern
from gen_ai_hub.proxy.langchain.init_models import init_embedding_model
embeddings = init_embedding_model("text-embedding-3-small")
```

**Reuse from old_workshop:** `03-cli-embedding/ingest.py` and `chat_rag.py` (adapt for PDF)

---

### Part 2: The Data Connector – MCP (11:30 – 12:30, 60 min)

**Goal:** Connect the agent to live data via MCP tools.

**Scenario:**
> "Our analyst needs real-time stock prices for {TICKER} and market news about {COMPANY_NAME}. Let's give the AI these superpowers."

**Technical Components:**
- MCP server with `fastmcp`
- Two tools:
  - **Stock Price Tool**: Fetch current/historical prices via `yfinance`
  - **News Search Tool**: Search market news via Perplexity AI
- Agent client using `langchain-mcp-adapters`

**Tool Specifications:**

| Tool | Input | Output | Implementation |
|------|-------|--------|----------------|
| `get_stock_info` | `ticker: str` | `{price, change_percent, currency, market_cap, pe_ratio}` | `yfinance` library |
| `search_market_news` | `query: str, limit: int` | `[{title, summary, source, url}]` | Perplexity AI via GenAI Hub |

**Exercise Structure:**

| File | Exercise Task | Difficulty |
|------|---------------|------------|
| `mcp_server.py` | Implement `get_stock_info` with yfinance | ⭐⭐ |
| `mcp_server.py` | Implement `search_market_news` with Perplexity | ⭐⭐⭐ |

**Hands-On Steps:**
1. **Explain** (10 min): What is MCP? Why tool encapsulation matters?
2. **Demo** (5 min): Show MCP Inspector with working tools
3. **Exercise 2a** (15 min): Implement `get_stock_info` with yfinance
4. **Exercise 2b** (20 min): Implement `search_market_news` with Perplexity
5. **Test** (5 min): Run agent client, ask "What's {TICKER}'s current stock price?"
6. **Wrap-up** (5 min): Discuss MCP reusability across languages/frontends

**yfinance Integration Pattern:**
```python
import yfinance as yf

@mcp.tool()
def get_stock_info(ticker: str) -> dict:
    """Get current stock information for a given ticker symbol."""
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "currency": info.get("currency", "JPY"),
        "change_percent": info.get("regularMarketChangePercent"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "company_name": info.get("longName"),
    }
```

**Perplexity AI Integration Pattern:**
```python
from gen_ai_hub.proxy.langchain.init_models import init_llm

# Perplexity is accessed as a model in GenAI Hub
perplexity = init_llm("perplexity--sonar-pro", max_tokens=4000)
result = perplexity.invoke(f"Search for recent news about {query}")
```

**Reuse from old_workshop:** `07-mcp-tutorial/mcp_server.py` and `agent_client.py` (adapt tools)

**Post-Part 2 Checkpoint:** 
All tools now live inside the MCP server. From Part 3 onwards, we only interact via MCP.

---

### 🍽️ Networking Lunch (12:30 – 13:30)

---

### Part 3: The Analyst Workflow (13:30 – 15:00, 90 min)

**Goal:** Orchestrate complex multi-step analysis using LangGraph.

**Scenario:**
> "Build an analyst workflow for {COMPANY_NAME}: Fetch stock data → Search news → Retrieve internal docs → Analyze → Generate preliminary report."

**Track A Focus:** Analyze the Couche-Tard takeover: risk vs. opportunity  
**Track B Focus:** Analyze Sakura's government AI contracts: sustainable growth vs. bubble

**Technical Components:**
- LangGraph `StateGraph` with typed state
- Multiple nodes: `fetch_stock`, `search_news`, `retrieve_docs`, `analyze`
- Conditional routing based on findings
- Integration with MCP tools from Part 2

**Workflow Diagram:**
```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌───────────────┐
│ User Query  │────▶│ Fetch Stock  │────▶│ Search News  │────▶│ Retrieve Docs │
│ {COMPANY}   │     │ (MCP Tool)   │     │ (MCP Tool)   │     │ (RAG)         │
└─────────────┘     └──────────────┘     └──────────────┘     └───────┬───────┘
                                                                      │
                                                                      ▼
                                                            ┌─────────────────┐
                                                            │ Analyze &       │
                                                            │ Summarize       │
                                                            └─────────────────┘
```

**State Definition (Provided in exercise skeleton):**
```python
class AnalystState(TypedDict):
    company_name: str             # e.g., "Seven & i Holdings"
    ticker: str                   # e.g., "3382.T"
    query: str                    # User's research question
    stock_info: dict              # From get_stock_info tool
    news_results: list[dict]      # From news search
    doc_context: str              # From RAG retrieval
    analysis: str                 # Final analysis output
    step_count: int               # Safety counter
```

**⚠️ Exercise Design Philosophy:**
> **The graph structure is 100% pre-built.** Participants focus ONLY on writing the logic inside each node (prompts, data processing). They should NOT fight with LangGraph wiring syntax.

**Exercise Structure:**

| File | What's Provided | What Participants Implement |
|------|-----------------|-----------------------------|
| `analyst_agent.py` | Full graph definition, state schema, node stubs, edges | Logic inside `fetch_stock_node()` |
| `analyst_agent.py` | (same) | Logic inside `search_news_node()` |
| `analyst_agent.py` | (same) | Logic inside `retrieve_docs_node()` |
| `analyst_agent.py` | (same) | Logic inside `analyze_node()` – the prompt engineering |

**Exercise Skeleton Structure:**
```python
# === GRAPH STRUCTURE (DO NOT MODIFY) ===
agent_builder = StateGraph(AnalystState)
agent_builder.add_node("fetch_stock", fetch_stock_node)
agent_builder.add_node("search_news", search_news_node)
agent_builder.add_node("retrieve_docs", retrieve_docs_node)
agent_builder.add_node("analyze", analyze_node)
agent_builder.add_edge(START, "fetch_stock")
agent_builder.add_edge("fetch_stock", "search_news")
agent_builder.add_edge("search_news", "retrieve_docs")
agent_builder.add_edge("retrieve_docs", "analyze")
agent_builder.add_edge("analyze", END)
agent = agent_builder.compile()

# === EXERCISES: Implement node logic below ===

def fetch_stock_node(state: AnalystState) -> dict:
    """EXERCISE 3a: Call the MCP get_stock_info tool."""
    # TODO: Use the MCP client to fetch stock data for state["ticker"]
    raise NotImplementedError("Implement fetch_stock_node")

def search_news_node(state: AnalystState) -> dict:
    """EXERCISE 3b: Call the MCP search_market_news tool."""
    # TODO: Search for news about state["company_name"]
    raise NotImplementedError("Implement search_news_node")

def retrieve_docs_node(state: AnalystState) -> dict:
    """EXERCISE 3c: Query the RAG vector store."""
    # TODO: Retrieve relevant document chunks
    raise NotImplementedError("Implement retrieve_docs_node")

def analyze_node(state: AnalystState) -> dict:
    """EXERCISE 3d: Generate analysis using LLM."""
    # TODO: Craft a prompt combining stock_info, news, and doc_context
    # TODO: Call the LLM and return the analysis
    raise NotImplementedError("Implement analyze_node")
```

**Hands-On Steps:**
1. **Explain** (15 min): LangGraph concepts – nodes, edges, state (show the pre-built graph)
2. **Demo** (10 min): Run complete analyst workflow, show audit log
3. **Exercise 3a** (15 min): Implement `fetch_stock_node` (MCP call)
4. **Exercise 3b** (15 min): Implement `search_news_node` (MCP call)
5. **Exercise 3c** (10 min): Implement `retrieve_docs_node` (RAG query)
6. **Exercise 3d** (15 min): Implement `analyze_node` (prompt engineering)
7. **Test** (5 min): Run "Analyze {COMPANY_NAME}'s market position"
8. **Wrap-up** (5 min): Review workflow, discuss extensions

**Reuse from old_workshop:** `05-agent-graph-complete/license_agent_complete.py` (adapt workflow)

---

### ☕ Coffee Break (15:00 – 15:15)

---

### Part 4: The Deal Memo Generator (15:15 – 16:30, 75 min)

**Goal:** Generate a professional Investment Memo in **Japanese** (案件概要書) based on multilingual inputs.

**Scenario:**
> "Take all the analysis from Parts 1-3 and generate a formal Deal Memo for {COMPANY_NAME} in the format used by Itochu's Corporate Planning Division (経営企画部)."

**🌏 Key Requirement: Bilingual AI Analyst**
| Input | Output |
|-------|--------|
| News articles (English/Japanese) | **Japanese** |
| PDF documents (English/Japanese) | **Japanese** |
| Stock data (English) | **Japanese** |
| → Final Deal Memo | **100% Japanese (Keigo/Business Japanese)** |

This is the "wow" factor: The AI acts as an elite bilingual analyst who reads global sources and writes formal Japanese business documents.

**Technical Components:**
- Integration of all previous components (RAG, MCP tools, LangGraph)
- Structured output generation with strict formatting
- Japanese business writing (敬語/Keigo)
- Template-based memo with variable substitution

**Memo Structure (案件概要書 Format):**
```markdown
# 案件概要書 (Deal Memo): {COMPANY_NAME}

## 1. エグゼクティブサマリー (Executive Summary)
* [3-bullet summary of the opportunity/threat]
* [Conclusion: 買い/保有/売り (Buy/Hold/Sell)?]

## 2. 企業概要 (Company Overview)
* **社名:** {COMPANY_NAME}
* **主要事業:** [Brief description]
* **直近株価:** [From tool] (変動率: [volatility])

## 3. 市場分析・外部環境 (Market Analysis)
* [Track A: Global retail consolidation, M&A trends]
* [Track B: Gov Cloud/AI trends, national AI policy]

## 4. 財務・リスク評価 (Financial & Risk Assessment)
* **強み (Pros):** [Key financial strengths]
* **リスク (Cons):** [Key risks]

## 5. 伊藤忠商事としての戦略的意義 (Strategic Fit)
* [Alignment with "Brand-new Deal" strategy]
* [Synergy potential]

## 6. 推奨アクション (Recommendation)
* [Clear final recommendation]
```

**Exercise Structure:**

| File | Exercise Task | Difficulty |
|------|---------------|------------|
| `memo_generator.py` | Configure the Japanese system prompt | ⭐⭐ |
| `memo_generator.py` | Implement section generators (call Part 3 workflow) | ⭐⭐ |
| `memo_generator.py` | Format and output the final Japanese memo | ⭐⭐ |

**System Prompt (経営企画部 Persona):**
See `prompts/deal_memo_system_prompt.md` for the full prompt. Key elements:
- Role: Senior Strategy Analyst at Itochu Corporate Planning Division
- Instruction: Synthesize English/Japanese sources into formal Japanese
- Tone: Objective, concise, risk-aware, profit-driven ("Earn" mindset)
- Output: Strictly formatted 案件概要書

**Hands-On Steps:**
1. **Explain** (10 min): Bilingual prompt engineering, Japanese business writing norms
2. **Demo** (10 min): Generate complete memo for sample company, show Japanese output
3. **Exercise 4a** (25 min): Configure system prompt, implement section calls
4. **Exercise 4b** (20 min): Wire everything together, handle {COMPANY_NAME} substitution
5. **Test & Polish** (10 min): Generate memo, review Japanese quality

**Demo/Target State (Facilitator Only):**
At the end, show the **React frontend** that presents the Deal Memo in a polished UI. This connects to the same MCP server participants built. **Not a hands-on exercise** – serves as inspiration and a take-home reference.

---

### Wrap Up & Value Proposition (16:30 – 17:00)

**Topics:**
- Recap of what was built
- SAP BTP value proposition for custom AI
- Next steps: How to bring this to production
- Q&A

**Takeaways for Participants:**
- Complete, working code repository
- Understanding of RAG, MCP, LangGraph patterns
- Blueprint for building custom AI agents on SAP BTP

---

## 6. Exercise Philosophy

### Fail-Safe Design
Each exercise folder contains both `exercise/` (skeleton) and `solution/` subdirectories. If a participant falls behind:

1. They can copy the solution folder to continue
2. They can follow along with the demo
3. They won't block the next exercise

### Hands-On Balance
- **~40%** explanation/demo
- **~50%** coding exercises
- **~10%** testing/troubleshooting

### Difficulty Progression
- Part 1: Foundation (moderate)
- Part 2: Tool building (moderate, one challenging task)
- Part 3: Orchestration (challenging)
- Part 4: Integration (moderate, builds on previous)

---

## 7. Prerequisites (Sent to Participants)

### Required Software
- [ ] VS Code (or preferred IDE)
- [ ] Python 3.12+
- [ ] uv package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- [ ] Git

### Credentials (Provided at Workshop)
- SAP AI Core service key (JSON)
- HANA Cloud user credentials
- Perplexity API access (via GenAI Hub deployment)

### Pre-Workshop Steps
1. Clone repository
2. Run `00-hello-world` to verify setup
3. Report any issues before the workshop

---

## 8. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Setup issues | Pre-session hello-world; backup HANA users |
| Slow participants | Solution folders available; pair programming |
| Network issues | Local mock data fallbacks |
| Time overrun | Each exercise has "minimum viable" scope |
| Perplexity quota | Rate limiting; shared demo account |

---

## 9. Resolved Decisions

| Decision | Resolution |
|----------|------------|
| Sample Data | Two real-world tracks: Seven & i (M&A) and Sakura Internet (Growth) |
| Stock Price API | `yfinance` library (free, no API key needed) |
| Japanese Language | Input: EN/JP; Output (Part 4): Japanese only |
| React Frontend | Demo/target state only – not hands-on |
| LangGraph complexity | Provide full graph boilerplate; participants only write node logic |

## 9.1 Additional Resolved Decisions

| Decision | Resolution |
|----------|------------|
| Group Size | 5-6 participants total, max 2 per group (small, intimate) |
| PDF Preparation | Already provided in `rag-material/` folder |
| Time Buffer | Each part has a `-done` folder for skip-ability (see below) |

### Time Buffer Strategy: `-done` Folders

Every exercise has two parallel folders:
- `XX-part-name/` → Hands-on version with TODOs
- `XX-part-name-done/` → Complete, runnable solution

If time gets tight, facilitator can **skip hands-on** and just demo the `-done` version.

### PDF Materials Location

```
rag-material/
├── 7i_holdings/                    # Track A: Seven & i
│   ├── 2026年2月期 第3四半期決算短信.pdf
│   ├── 2026年2月期 第3四半期決算補足資料.pdf
│   └── 2026年2月期 第3四半期決算説明資料.pdf
└── sakura_internet/                # Track B: Sakura Internet
    ├── factbook.pdf
    └── s-report2025j.pdf
```

---

## 10. Implementation Checklist

### Repository Setup
- [ ] Create folder structure as specified
- [ ] Set up `.env.example` with all required variables
- [ ] Create root `README.md` with setup instructions

### Part 0: Hello World
- [ ] Adapt from `old_workshop/01-hello-world`
- [ ] Test connectivity to GenAI Hub

### Part 1: Research Engine
- [ ] Create PDF ingestion script (adapt from `03-cli-embedding`)
- [ ] Add PDF loading with `pypdf`
- [ ] Create RAG chat interface
- [ ] Prepare sample financial PDF
- [ ] Write exercise README with hints

### Part 2: MCP Data Connector
- [ ] Create MCP server skeleton
- [ ] Implement `get_stock_info` tool with yfinance
- [ ] Implement `search_market_news` with Perplexity
- [ ] Adapt agent client from `07-mcp-tutorial`
- [ ] Document yfinance and Perplexity integration

### Part 3: Analyst Workflow
- [ ] Design LangGraph state schema
- [ ] **Create full graph boilerplate** (participants don't touch this)
- [ ] Implement workflow nodes (solution)
- [ ] Write exercise skeleton with node stubs + TODOs
- [ ] Add audit log printing

### Part 4: Deal Memo Generator
- [ ] Create Japanese system prompt (経営企画部 persona)
- [ ] Design 案件概要書 template
- [ ] Implement section generators with bilingual handling
- [ ] Create final integration
- [ ] Test end-to-end flow with Japanese output

### Documentation
- [ ] Each exercise has clear README
- [ ] Error handling guidance
- [ ] Troubleshooting FAQ

---

## 11. Notes

- **No ERP integration** in this workshop – focus is on custom AI logic
- **All credentials** will be provided; participants don't need their own SAP accounts
- **Frontend** (React) is demo/target state only – connects to the MCP server participants build
- **Time is tight** – prioritize working demos over comprehensive exercises
- **Bilingual output** is the key differentiator – emphasize this "wow" factor
- **Two tracks** allow participants to choose based on interest (M&A vs. Growth investing)
