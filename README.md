# DealCrafter Assistant Workshop

> **SAP × Itochu GenAI Workshop** | Build an AI-powered Investment Memo Generator

This workshop teaches you to build a **bilingual AI analyst** that reads financial documents and market news (English/Japanese) and generates professional Investment Memos in Japanese.

---

## 🎯 What You'll Build

The **DealCrafter Assistant** – an agentic AI system that:
1. **Ingests** PDF financial documents into SAP HANA Cloud Vector Engine
2. **Fetches** real-time stock data via MCP tools
3. **Searches** market news using Perplexity AI
4. **Orchestrates** analysis workflows with LangGraph
5. **Generates** Japanese 案件概要書 (Deal Memos) in Itochu format

---

## 📋 Workshop Schedule

| Time | Part | Topic |
|------|------|-------|
| ~10:00 | **Part 0** | Hello World – Setup verification |
| 10:30 | **Part 1** | The Research Engine – PDF ingestion + RAG |
| 11:30 | **Part 2** | The Data Connector – MCP tools (yfinance, Perplexity) |
| 12:30 | *Lunch* | Networking |
| 13:30 | **Part 3** | The Analyst Workflow – LangGraph orchestration |
| 15:15 | **Part 4** | The Deal Memo Generator – Japanese output |
| 16:30 | **Wrap Up** | Value proposition & next steps |

---

## 🏢 Scenario Tracks

Choose your investment analysis scenario:

### Track A: M&A Defense – Seven & i Holdings (3382.T)
- **Context:** Hostile takeover bid by Alimentation Couche-Tard
- **Goal:** Evaluate risk/benefit of the takeover

### Track B: Growth Strategy – Sakura Internet (3778.T)
- **Context:** Japan's "AI Sovereignty" policy, government cloud partnership
- **Goal:** Is the stock overvalued or sustainable?

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- VS Code (recommended)

### Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd genai-basics-2026

# 2. Copy environment template
cp .env.example .env
# Then edit .env with your credentials (provided at workshop)

# 3. Verify setup with Hello World
cd 00-hello-world-done
uv sync
uv run python main.py
```

You should see a response from SAP Generative AI Hub. If not, check your `.env` credentials.

---

## 📁 Folder Structure

Each part has two folders:
- `XX-part-name/` → **Hands-on** version with TODOs
- `XX-part-name-done/` → **Complete** version (use if short on time)

```
├── 00-hello-world/              # Part 0: Setup check
├── 00-hello-world-done/
├── 01-research-engine/          # Part 1: PDF + RAG
├── 01-research-engine-done/
├── 02-data-connector-mcp/       # Part 2: MCP tools
├── 02-data-connector-mcp-done/
├── 03-analyst-workflow/         # Part 3: LangGraph
├── 03-analyst-workflow-done/
├── 04-deal-memo-generator/      # Part 4: Japanese output
├── 04-deal-memo-generator-done/
├── rag-material/                # PDF documents for analysis
│   ├── 7i_holdings/            # Track A materials
│   └── sakura_internet/        # Track B materials
└── prompts/                     # Shared prompt templates
```

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|------------|
| AI Runtime | SAP BTP Generative AI Hub |
| Vector Store | SAP HANA Cloud Vector Engine |
| Stock Data | `yfinance` |
| News Search | Perplexity AI |
| Agent Framework | LangGraph |
| Tool Protocol | MCP (Model Context Protocol) |
| Language | Python 3.12+ |
| Package Manager | uv |

---

## 📚 Documentation

### Core Technologies
- [SAP Generative AI Hub SDK](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [MCP Python SDK](https://modelcontextprotocol.io/docs)
- [yfinance](https://github.com/ranaroussi/yfinance)

### Perplexity Integration
- **[Perplexity Sonar Integration Guide](genai/README_PERPLEXITY.md)** - Complete setup and usage documentation
- Models available: `sonar` and `sonar-pro` (online search capabilities)
- Integrated via SAP Generative AI Hub using the SDK's "unsupported model" pattern
- Used in Part 4 for real-time news gathering and market intelligence

---

## 🎓 Workshop Requirements Document

See [wrd.md](wrd.md) for detailed technical specifications and exercise breakdowns.

---

**Built with ❤️ by SAP for Itochu**
