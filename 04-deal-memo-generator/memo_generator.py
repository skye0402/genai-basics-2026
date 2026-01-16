"""Part 4: Agentic Deal Memo Generator with Supervisor Pattern (Exercise)

This script implements an agentic workflow using LangGraph with a supervisor pattern.
The LLM decides which tools to call and when it has enough information to generate the memo.

Key features to implement:
- Supervisor LLM decides next actions (not hardcoded sequence)
- Conditional routing based on LLM decisions
- Tool loop until supervisor is satisfied
- Quality check with optional refinement

Run with:
    uv run python memo_generator.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Literal
from typing_extensions import TypedDict

from dotenv import load_dotenv

# Load environment variables from the repo root .env file
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Add parent directory to path to import genai module
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Configuration
MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "6000"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
COMPANY_NAME = os.getenv("COMPANY_NAME", "Sakura Internet")
TICKER = os.getenv("TICKER", "3778.T")
EMBEDDING_MODEL = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-3-small")
TABLE_NAME = os.getenv("HANA_TABLE_NAME", "DEALCRAFTER_DOCS")


# =============================================================================
# EXERCISE 4a: Define the State for the Agent
# =============================================================================

class MemoState(TypedDict):
    """State passed between LangGraph nodes.
    
    TODO: This is already defined for you. Study the fields:
    - company_name, ticker: Target company info
    - stock_data, news_data, doc_data: Data gathered by tools
    - next_action: Supervisor's decision on what to do next
    - gathered_sources: List of sources already gathered
    - memo: The generated Deal Memo
    - quality_score: Quality rating (1-10)
    - iteration: Number of memo generation attempts
    """
    company_name: str
    ticker: str
    stock_data: dict
    news_data: str
    doc_data: str
    next_action: str
    gathered_sources: list[str]
    memo: str
    quality_score: int
    iteration: int


# =============================================================================
# JAPANESE SYSTEM PROMPT (経営企画部 Persona)
# =============================================================================

DEAL_MEMO_SYSTEM_PROMPT = """
# Role
You are an elite Senior Strategy Analyst at Itochu Corporation's Corporate Planning Division (経営企画部).
Your task is to draft a "Deal Memo" (案件概要書 / Investment Review Document) for the Investment Committee.

# Instructions
1. **Analyze** the provided context (News, Financials, PDF excerpts) regarding the target company: {company_name} ({ticker}).
2. **Synthesize** the information into a strictly formatted Japanese business document.
3. **Translation & Nuance:** Even if the source text is English, the output must be professional Japanese (敬語/Keigo).
4. **Tone:** Objective, concise, risk-aware, and profit-driven ("Earn" mindset).

# Output Format (Strictly follow this structure)

# 案件概要書 (Deal Memo): {company_name}

## 1. エグゼクティブサマリー (Executive Summary)
* [Provide a 3-bullet summary of the opportunity/threat]
* [Conclusion: 買い (Buy), 保有 (Hold), or 売り (Sell)?]

## 2. 企業概要 (Company Overview)
* **社名:** {company_name}
* **主要事業:** [Brief description in Japanese]
* **直近株価:** [Insert price from data] (変動率: [Insert change %])

## 3. 市場分析・外部環境 (Market Analysis)
* [Analyze the market trends affecting this company]
* [Consider global and Japan-specific factors]

## 4. 財務・リスク評価 (Financial & Risk Assessment)
* **強み (Pros):** [Key financial strengths in Japanese]
* **リスク (Cons):** [Key risks in Japanese]

## 5. 伊藤忠商事としての戦略的意義 (Strategic Fit)
* [How does this align with the "Brand-new Deal" strategy?]
* [Potential synergies with Itochu's existing businesses]

## 6. 推奨アクション (Recommendation)
* [Clear final recommendation in Japanese]
* [Next steps if applicable]

---
注: 本文書はAIによる分析に基づく参考資料です。投資判断は別途精査が必要です。
"""


SUPERVISOR_PROMPT = """You are a research supervisor coordinating the creation of a Deal Memo for {company_name} ({ticker}).

Your job is to decide what information to gather next. You have access to these tools:
- **get_stock**: Fetch real-time stock data (price, market cap, PE ratio, etc.)
- **get_news**: Search for recent news articles about the company
- **get_docs**: Retrieve internal documents from the knowledge base
- **generate_memo**: Generate the final Deal Memo (only when you have enough data)

Current status:
- Stock data: {has_stock}
- News data: {has_news}
- Document data: {has_docs}
- Sources gathered: {sources}

IMPORTANT: You must gather AT LEAST stock data AND news before generating the memo.
Documents are optional but recommended if available.

Respond with ONLY one of these actions (no explanation):
- get_stock
- get_news
- get_docs
- generate_memo
"""


QUALITY_CHECK_PROMPT = """You are a quality reviewer for Deal Memos.

Review this Deal Memo and rate its quality from 1-10:

{memo}

Consider:
1. Does it follow the required format with all 6 sections?
2. Does it include specific data points (stock price, market cap, etc.)?
3. Is it written in professional Japanese (敬語)?
4. Does it provide a clear recommendation?

Respond with ONLY a number from 1-10."""


# =============================================================================
# EXERCISE 4b: Implement Helper Functions
# =============================================================================

def get_hana_connection():
    """Create a connection to SAP HANA Cloud.
    
    TODO: Reuse the pattern from Part 1/3
    """
    # ==========================================================================
    # TODO: Import hdbcli and create connection
    # Hint: from hdbcli import dbapi
    # Hint: return dbapi.connect(
    #     address=os.getenv("HANA_DB_ADDRESS"),
    #     port=int(os.getenv("HANA_DB_PORT", "443")),
    #     user=os.getenv("HANA_DB_USER"),
    #     password=os.getenv("HANA_DB_PASSWORD"),
    #     autocommit=True,
    # )
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4b: Implement get_hana_connection")


# =============================================================================
# EXERCISE 4c: Implement MCP Tool Calls
# =============================================================================

async def call_mcp_stock(ticker: str) -> dict:
    """Call MCP server to get stock info.
    
    TODO: Reuse the MCP pattern from Part 2/3
    """
    # ==========================================================================
    # TODO: Import MCP client
    # Hint: from mcp import ClientSession, StdioServerParameters
    # Hint: from mcp.client.stdio import stdio_client
    #
    # TODO: Create server params pointing to 02-data-connector-mcp-done
    # Hint: server_params = StdioServerParameters(
    #     command=sys.executable,
    #     args=[str(Path(__file__).parent.parent / "02-data-connector-mcp-done" / "mcp_server.py")],
    # )
    #
    # TODO: Connect and call the tool
    # Hint: async with stdio_client(server_params) as (read, write):
    #     async with ClientSession(read, write) as session:
    #         await session.initialize()
    #         result = await session.call_tool("get_stock_info", {"ticker": ticker})
    #         # Parse result.content[0].text as JSON
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4c: Implement call_mcp_stock")


async def call_mcp_news(query: str) -> str:
    """Call MCP server to search news.
    
    TODO: Similar to call_mcp_stock but call search_market_news
    """
    # ==========================================================================
    # TODO: Implement similar to call_mcp_stock
    # Hint: Call "search_market_news" with {"query": query, "limit": 5}
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4c: Implement call_mcp_news")


def get_documents(company_name: str) -> str:
    """Retrieve documents from HANA vector store.
    
    TODO: Reuse the RAG pattern from Part 1/3
    """
    # ==========================================================================
    # TODO: Connect to HANA and retrieve documents
    # Hint: from langchain_hana import HanaDB
    # Hint: from gen_ai_hub.proxy.langchain.init_models import init_embedding_model
    # Hint: connection = get_hana_connection()
    # Hint: embeddings = init_embedding_model(EMBEDDING_MODEL)
    # Hint: db = HanaDB(embedding=embeddings, connection=connection, table_name=TABLE_NAME)
    # Hint: retriever = db.as_retriever(search_kwargs={"k": 5})
    # Hint: docs = retriever.invoke(f"{company_name} business strategy")
    # Hint: return "\n\n---\n\n".join(doc.page_content for doc in docs)
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4c: Implement get_documents")


# =============================================================================
# EXERCISE 4d: Implement Node Functions
# =============================================================================

async def supervisor_node(state: MemoState) -> dict:
    """Supervisor decides what action to take next.
    
    TODO: 
    1. Initialize LLM
    2. Format SUPERVISOR_PROMPT with current state
    3. Call LLM and parse the action
    4. Return {"next_action": action}
    """
    print(f"\n🧠 Supervisor evaluating next action...")
    
    # ==========================================================================
    # TODO: Initialize LLM
    # Hint: from gen_ai_hub.proxy.langchain.init_models import init_llm
    # Hint: llm = init_llm(MODEL, max_tokens=100, temperature=0)
    #
    # TODO: Format the supervisor prompt
    # Hint: prompt = SUPERVISOR_PROMPT.format(
    #     company_name=state["company_name"],
    #     ticker=state["ticker"],
    #     has_stock="✅ Yes" if state.get("stock_data") else "❌ No",
    #     has_news="✅ Yes" if state.get("news_data") else "❌ No",
    #     has_docs="✅ Yes" if state.get("doc_data") else "❌ No",
    #     sources=", ".join(state.get("gathered_sources", [])) or "None yet",
    # )
    #
    # TODO: Call LLM and extract action
    # Hint: response = llm.invoke(prompt)
    # Hint: action = response.content.strip().lower()
    #
    # TODO: Validate action is one of: get_stock, get_news, get_docs, generate_memo
    # Hint: valid_actions = ["get_stock", "get_news", "get_docs", "generate_memo"]
    # Hint: if action not in valid_actions:
    #     action = "get_stock" if not state.get("stock_data") else "generate_memo"
    #
    # Hint: print(f"   → Decision: {action}")
    # Hint: return {"next_action": action}
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4d: Implement supervisor_node")


async def get_stock_node(state: MemoState) -> dict:
    """Fetch stock data via MCP.
    
    TODO:
    1. Call call_mcp_stock with ticker
    2. Update gathered_sources
    3. Return {"stock_data": ..., "gathered_sources": ...}
    """
    print(f"\n📊 Fetching stock data for {state['ticker']}...")
    
    # ==========================================================================
    # TODO: Call MCP to get stock data
    # Hint: stock_data = await call_mcp_stock(state["ticker"])
    # Hint: sources = state.get("gathered_sources", []).copy()
    # Hint: sources.append("stock")
    # Hint: return {"stock_data": stock_data, "gathered_sources": sources}
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4d: Implement get_stock_node")


async def get_news_node(state: MemoState) -> dict:
    """Search news via MCP.
    
    TODO: Similar to get_stock_node but for news
    """
    print(f"\n📰 Searching news for {state['company_name']}...")
    
    # ==========================================================================
    # TODO: Call MCP to search news
    # Hint: query = f"{state['company_name']} {state['ticker']} financial news"
    # Hint: news_data = await call_mcp_news(query)
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4d: Implement get_news_node")


async def get_docs_node(state: MemoState) -> dict:
    """Retrieve documents from HANA.
    
    TODO: Call get_documents and update state
    """
    print(f"\n📄 Retrieving documents...")
    
    # ==========================================================================
    # TODO: Retrieve documents
    # Hint: doc_data = get_documents(state["company_name"])
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4d: Implement get_docs_node")


async def generate_memo_node(state: MemoState) -> dict:
    """Generate the Deal Memo using gathered data.
    
    TODO:
    1. Format stock data as string
    2. Create system and user prompts
    3. Call LLM with messages
    4. Return {"memo": ..., "iteration": ...}
    """
    print(f"\n📝 Generating Deal Memo...")
    
    # ==========================================================================
    # TODO: Initialize LLM
    # Hint: from gen_ai_hub.proxy.langchain.init_models import init_llm
    # Hint: from langchain_core.messages import SystemMessage, HumanMessage
    # Hint: llm = init_llm(MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
    #
    # TODO: Format stock data
    # Hint: stock_str = "\n".join(f"  - {k}: {v}" for k, v in state["stock_data"].items() if v)
    #
    # TODO: Create prompts
    # Hint: system_prompt = DEAL_MEMO_SYSTEM_PROMPT.format(
    #     company_name=state["company_name"],
    #     ticker=state["ticker"],
    # )
    # Hint: user_prompt = f"""Based on the following information...
    #     === STOCK DATA ===
    #     {stock_str}
    #     === NEWS ===
    #     {state.get('news_data', '')}
    #     === DOCUMENTS ===
    #     {state.get('doc_data', '')}
    #     Generate the 案件概要書..."""
    #
    # TODO: Call LLM
    # Hint: response = llm.invoke([
    #     SystemMessage(content=system_prompt),
    #     HumanMessage(content=user_prompt),
    # ])
    # Hint: return {"memo": response.content, "iteration": state.get("iteration", 0) + 1}
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4d: Implement generate_memo_node")


async def quality_check_node(state: MemoState) -> dict:
    """Check the quality of the generated memo.
    
    TODO:
    1. Call LLM with QUALITY_CHECK_PROMPT
    2. Parse the score (1-10)
    3. Return {"quality_score": score}
    """
    print(f"\n🔍 Quality check...")
    
    # ==========================================================================
    # TODO: Initialize LLM and check quality
    # Hint: llm = init_llm(MODEL, max_tokens=50, temperature=0)
    # Hint: prompt = QUALITY_CHECK_PROMPT.format(memo=state["memo"][:2000])
    # Hint: response = llm.invoke(prompt)
    # Hint: score = int(response.content.strip())
    # Hint: return {"quality_score": score}
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4d: Implement quality_check_node")


# =============================================================================
# EXERCISE 4e: Implement Routing Functions
# =============================================================================

def route_supervisor(state: MemoState) -> Literal["get_stock", "get_news", "get_docs", "generate_memo"]:
    """Route based on supervisor's decision.
    
    TODO: Return the next_action from state
    """
    # ==========================================================================
    # TODO: Return the supervisor's decision
    # Hint: return state["next_action"]
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4e: Implement route_supervisor")


def route_quality(state: MemoState) -> Literal["refine", "end"]:
    """Route based on quality score.
    
    TODO: If score < 6 and iteration < 2, return "refine", else "end"
    """
    # ==========================================================================
    # TODO: Check quality and decide whether to refine
    # Hint: if state.get("quality_score", 10) < 6 and state.get("iteration", 0) < 2:
    #     return "refine"
    # Hint: return "end"
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4e: Implement route_quality")


# =============================================================================
# EXERCISE 4f: Build the LangGraph Agent
# =============================================================================

def build_agent():
    """Build the LangGraph agent with supervisor pattern.
    
    TODO:
    1. Create StateGraph with MemoState
    2. Add all nodes
    3. Add edges (START -> supervisor)
    4. Add conditional edges from supervisor to tools/generate_memo
    5. Add edges from tools back to supervisor
    6. Add edge from generate_memo to quality_check
    7. Add conditional edge from quality_check to refine/end
    8. Compile and return
    """
    # ==========================================================================
    # TODO: Import StateGraph
    # Hint: from langgraph.graph import StateGraph, START, END
    #
    # TODO: Create builder
    # Hint: builder = StateGraph(MemoState)
    #
    # TODO: Add nodes
    # Hint: builder.add_node("supervisor", supervisor_node)
    # Hint: builder.add_node("get_stock", get_stock_node)
    # Hint: builder.add_node("get_news", get_news_node)
    # Hint: builder.add_node("get_docs", get_docs_node)
    # Hint: builder.add_node("generate_memo", generate_memo_node)
    # Hint: builder.add_node("quality_check", quality_check_node)
    #
    # TODO: Add entry edge
    # Hint: builder.add_edge(START, "supervisor")
    #
    # TODO: Add conditional edges from supervisor
    # Hint: builder.add_conditional_edges(
    #     "supervisor",
    #     route_supervisor,
    #     {
    #         "get_stock": "get_stock",
    #         "get_news": "get_news",
    #         "get_docs": "get_docs",
    #         "generate_memo": "generate_memo",
    #     }
    # )
    #
    # TODO: Add edges from tools back to supervisor
    # Hint: builder.add_edge("get_stock", "supervisor")
    # Hint: builder.add_edge("get_news", "supervisor")
    # Hint: builder.add_edge("get_docs", "supervisor")
    #
    # TODO: Add edge from generate_memo to quality_check
    # Hint: builder.add_edge("generate_memo", "quality_check")
    #
    # TODO: Add conditional edge from quality_check
    # Hint: builder.add_conditional_edges(
    #     "quality_check",
    #     route_quality,
    #     {"refine": "generate_memo", "end": END}
    # )
    #
    # TODO: Compile and return
    # Hint: return builder.compile()
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4f: Implement build_agent")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def main():
    """Run the agentic Deal Memo Generator."""
    
    print("\n" + "=" * 60)
    print("📝 DealCrafter - Agentic 案件概要書 Generator")
    print("=" * 60)
    print(f"Target: {COMPANY_NAME} ({TICKER})")
    print("Mode: Supervisor Agent with Tool Loop")
    print("=" * 60)
    
    # Build the agent
    agent = build_agent()
    
    # Initial state
    initial_state = {
        "company_name": COMPANY_NAME,
        "ticker": TICKER,
        "stock_data": {},
        "news_data": "",
        "doc_data": "",
        "next_action": "",
        "gathered_sources": [],
        "memo": "",
        "quality_score": 0,
        "iteration": 0,
    }
    
    # Run the agent
    result = await agent.ainvoke(initial_state)
    
    print("\n" + "=" * 60)
    print("=== 案件概要書 (Deal Memo) ===")
    print("=" * 60)
    print(result["memo"])
    
    # Save to file
    output_file = Path(f"deal_memo_{TICKER.replace('.', '_')}.md")
    output_file.write_text(result["memo"], encoding="utf-8")
    print(f"\n💾 Saved to {output_file}")
    
    print(f"\n📊 Final quality score: {result['quality_score']}/10")
    print(f"📋 Sources used: {', '.join(result['gathered_sources'])}")
    print("\n🎉 Deal Memo generation complete!")


if __name__ == "__main__":
    asyncio.run(main())
