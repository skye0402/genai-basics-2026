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

---

## 2. Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| AI Runtime | SAP BTP Generative AI Hub | LLM access (GPT-4.1, Claude, etc.) |
| Vector Store | SAP HANA Cloud Vector Engine | Document embeddings & RAG |
| Web Search | Perplexity AI (via GenAI Hub) | Real-time market research |
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
| 16:30 – 17:00 | **Wrap Up & Value Proposition** | Discussion |

---

## 4. Folder Structure

Each exercise is **self-contained** with its own `pyproject.toml`, `README.md`, and complete solution. This allows participants who fall behind to continue from a working state.

```
genai-basics-2026/
├── .env.example                    # Template for credentials
├── README.md                       # Workshop overview & setup
├── wrd.md                          # This document
│
├── 00-hello-world/                 # Pre-session setup check
│   ├── README.md
│   ├── main.py                     # Simple GenAI Hub connectivity test
│   └── pyproject.toml
│
├── 01-research-engine/             # Part 1: PDF ingestion + RAG
│   ├── README.md
│   ├── exercise/                   # Skeleton for hands-on
│   │   ├── ingest_pdf.py          # TODO: implement PDF loading
│   │   ├── chat_documents.py      # TODO: implement RAG chat
│   │   └── pyproject.toml
│   ├── solution/                   # Complete working code
│   │   ├── ingest_pdf.py
│   │   ├── chat_documents.py
│   │   └── pyproject.toml
│   └── data/                       # Sample financial documents
│       └── sample_annual_report.pdf
│
├── 02-data-connector-mcp/          # Part 2: MCP tools
│   ├── README.md
│   ├── exercise/
│   │   ├── mcp_server.py          # TODO: implement tools
│   │   ├── agent_client.py        # Pre-built agent client
│   │   └── pyproject.toml
│   ├── solution/
│   │   ├── mcp_server.py          # Stock price + news tools
│   │   ├── agent_client.py
│   │   └── pyproject.toml
│   └── docs/
│       └── perplexity_api.md      # Perplexity integration guide
│
├── 03-analyst-workflow/            # Part 3: LangGraph orchestration
│   ├── README.md
│   ├── exercise/
│   │   ├── analyst_agent.py       # TODO: implement workflow nodes
│   │   └── pyproject.toml
│   ├── solution/
│   │   ├── analyst_agent.py       # Complete workflow
│   │   └── pyproject.toml
│   └── prompts/
│       └── analyst_persona.md     # System prompt templates
│
├── 04-deal-memo-generator/         # Part 4: Final application
│   ├── README.md
│   ├── exercise/
│   │   ├── memo_generator.py      # TODO: implement memo formatting
│   │   └── pyproject.toml
│   ├── solution/
│   │   ├── memo_generator.py      # Complete generator
│   │   └── pyproject.toml
│   └── templates/
│       └── itochu_memo_template.md # Memo format specification
│
├── documentation/                  # Reference materials
│   ├── sap-gen-ai-hub-sdk/
│   ├── hana-cloud-vs/
│   └── mcp-server-python.md
│
└── old_workshop/                   # Previous workshop (reference only)
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
> "We've received Startup X's annual report. Let's make it searchable by our AI."

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
> "Our analyst needs real-time stock prices and market news. Let's give the AI these superpowers."

**Technical Components:**
- MCP server with `fastmcp`
- Two tools:
  - **Stock Price Tool**: Fetch current/historical prices (mock or real API)
  - **News Search Tool**: Search market news via Perplexity AI
- Agent client using `langchain-mcp-adapters`

**Tool Specifications:**

| Tool | Input | Output | Implementation |
|------|-------|--------|----------------|
| `get_stock_price` | `ticker: str` | `{price, change, currency}` | Mock data or Yahoo Finance |
| `search_market_news` | `query: str, limit: int` | `[{title, summary, source, url}]` | Perplexity AI via GenAI Hub |

**Exercise Structure:**

| File | Exercise Task | Difficulty |
|------|---------------|------------|
| `mcp_server.py` | Implement `get_stock_price` tool | ⭐ |
| `mcp_server.py` | Implement `search_market_news` tool | ⭐⭐⭐ |

**Hands-On Steps:**
1. **Explain** (10 min): What is MCP? Why tool encapsulation matters?
2. **Demo** (5 min): Show MCP Inspector with working tools
3. **Exercise 2a** (15 min): Implement `get_stock_price` (simple)
4. **Exercise 2b** (20 min): Implement `search_market_news` with Perplexity
5. **Test** (5 min): Run agent client, ask "What's Toyota's stock price?"
6. **Wrap-up** (5 min): Discuss MCP reusability across languages/frontends

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
> "An analyst workflow: Search for news → Retrieve internal policies → Compare → Generate summary report."

**Technical Components:**
- LangGraph `StateGraph` with typed state
- Multiple nodes: `search_news`, `retrieve_policy`, `compare`, `summarize`
- Conditional routing based on findings
- Integration with MCP tools from Part 2

**Workflow Diagram:**
```
┌─────────────┐     ┌──────────────────┐     ┌───────────┐     ┌───────────┐
│ User Query  │────▶│ Search News      │────▶│ Retrieve  │────▶│ Compare & │
│             │     │ (MCP Tool)       │     │ Policy    │     │ Analyze   │
└─────────────┘     └──────────────────┘     │ (RAG)     │     └─────┬─────┘
                                             └───────────┘           │
                                                                     ▼
                                                            ┌───────────────┐
                                                            │ Generate      │
                                                            │ Summary Report│
                                                            └───────────────┘
```

**State Definition:**
```python
class AnalystState(TypedDict):
    query: str                    # User's research question
    news_results: list[dict]      # From news search
    policy_context: str           # From RAG retrieval
    analysis: str                 # Comparison output
    report: str                   # Final summary
    step_count: int               # Safety counter
```

**Exercise Structure:**

| File | Exercise Task | Difficulty |
|------|---------------|------------|
| `analyst_agent.py` | Define state schema | ⭐ |
| `analyst_agent.py` | Implement `search_news_node` | ⭐⭐ |
| `analyst_agent.py` | Implement `retrieve_policy_node` | ⭐⭐ |
| `analyst_agent.py` | Implement `analyze_node` | ⭐⭐ |
| `analyst_agent.py` | Wire the graph with edges | ⭐⭐⭐ |

**Hands-On Steps:**
1. **Explain** (15 min): LangGraph concepts – nodes, edges, state, routing
2. **Demo** (10 min): Run complete analyst workflow, show audit log
3. **Exercise 3a** (20 min): Implement state + `search_news_node`
4. **Exercise 3b** (20 min): Implement `retrieve_policy_node` + `analyze_node`
5. **Exercise 3c** (15 min): Wire graph edges and routing logic
6. **Test** (5 min): Run "Analyze Toyota's market position"
7. **Wrap-up** (5 min): Review workflow, discuss extensions

**Reuse from old_workshop:** `05-agent-graph-complete/license_agent_complete.py` (adapt workflow)

---

### ☕ Coffee Break (15:00 – 15:15)

---

### Part 4: The Deal Memo Generator (15:15 – 16:30, 75 min)

**Goal:** Generate a professional Investment Memo in Itochu's format.

**Scenario:**
> "Evaluate a potential partnership with Startup X and generate a draft Investment Memo."

**Technical Components:**
- Integration of all previous components
- Structured output generation
- Template-based memo formatting
- Multi-section document generation

**Memo Structure (Itochu Format):**
```markdown
# 投資メモ / Investment Memo

## 1. Executive Summary
## 2. Company Overview  
## 3. Market Analysis
## 4. Financial Assessment
## 5. Risk Factors
## 6. Strategic Fit with Itochu
## 7. Recommendation
## 8. Appendix: Data Sources
```

**Exercise Structure:**

| File | Exercise Task | Difficulty |
|------|---------------|------------|
| `memo_generator.py` | Implement section generators | ⭐⭐ |
| `memo_generator.py` | Integrate with analyst workflow | ⭐⭐⭐ |
| `memo_generator.py` | Format final output | ⭐⭐ |

**Hands-On Steps:**
1. **Explain** (10 min): Structured output, prompt engineering for reports
2. **Demo** (10 min): Generate complete memo for sample company
3. **Exercise 4a** (25 min): Implement individual section generators
4. **Exercise 4b** (20 min): Wire everything together
5. **Test & Polish** (10 min): Generate memo, review quality

**Optional Demo (Facilitator Only):**
At the end, show the React frontend that presents the Deal Memo in a polished UI. This will **not** be a hands-on exercise but serves as inspiration for what's possible.

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

## 9. Open Questions for Discussion

1. **Sample Data:** What financial documents/companies should we use for exercises? 
   - Option A: Public company (Toyota, Sony) – real data available
   - Option B: Fictional "Startup X" – more creative freedom

2. **Stock Price API:** 
   - Mock data (simpler, no external dependencies)
   - Real API (Yahoo Finance, Alpha Vantage) – more impressive but needs API keys

3. **Japanese Language:** Should we include Japanese in prompts/templates for Itochu?

4. **Group Size:** How many participants expected? Impacts:
   - Number of HANA users needed
   - Pair programming vs. individual work
   - Amount of troubleshooting support

5. **React Frontend Demo:** Should this be:
   - A quick 10-min demo at the end
   - A separate take-home repository
   - Excluded entirely

6. **Time Buffer:** Previous workshop ran over. Should we:
   - Reduce scope (drop one exercise)
   - Make some exercises demo-only
   - Keep as-is but mark optional sections

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
- [ ] Implement `get_stock_price` tool
- [ ] Implement `search_market_news` with Perplexity
- [ ] Adapt agent client from `07-mcp-tutorial`
- [ ] Document Perplexity integration

### Part 3: Analyst Workflow
- [ ] Design LangGraph state schema
- [ ] Implement workflow nodes
- [ ] Create routing logic
- [ ] Add audit log printing
- [ ] Write exercise skeleton with TODOs

### Part 4: Deal Memo Generator
- [ ] Design memo template (Itochu format)
- [ ] Implement section generators
- [ ] Create final integration
- [ ] Test end-to-end flow

### Documentation
- [ ] Each exercise has clear README
- [ ] Error handling guidance
- [ ] Troubleshooting FAQ

---

## 11. Notes

- **No ERP integration** in this workshop – focus is on custom AI logic
- **All credentials** will be provided; participants don't need their own SAP accounts
- **Frontend** (React) is out of scope for hands-on but can be demoed
- **Time is tight** – prioritize working demos over comprehensive exercises
