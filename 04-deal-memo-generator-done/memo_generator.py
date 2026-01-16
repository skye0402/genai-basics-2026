"""Part 4: Agentic Deal Memo Generator with Supervisor Pattern (Complete)

This script implements an agentic workflow using LangGraph with a supervisor pattern.
The LLM decides which tools to call and when it has enough information to generate the memo.

Key features:
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
from typing import Literal, Annotated
from typing_extensions import TypedDict

from dotenv import load_dotenv
from hdbcli import dbapi
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_hana import HanaDB
from langgraph.graph import StateGraph, START, END
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from gen_ai_hub.proxy.langchain.init_models import init_llm, init_embedding_model

# Add parent directory to path to import genai module
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Load environment variables from the repo root .env file
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Configuration
MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "6000"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
COMPANY_NAME = os.getenv("COMPANY_NAME", "Sakura Internet")
TICKER = os.getenv("TICKER", "3778.T")
EMBEDDING_MODEL = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-3-small")
TABLE_NAME = os.getenv("HANA_TABLE_NAME", "DEALCRAFTER_DOCS")


# =============================================================================
# STATE DEFINITION
# =============================================================================

class MemoState(TypedDict):
    """State passed between LangGraph nodes."""
    company_name: str
    ticker: str
    # Data gathered by tools
    stock_data: dict
    news_data: str
    doc_data: str
    # Supervisor decisions
    next_action: str
    gathered_sources: list[str]
    # Output
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
# HELPER FUNCTIONS
# =============================================================================

def get_hana_connection():
    """Create a connection to SAP HANA Cloud."""
    address = os.getenv("HANA_DB_ADDRESS")
    user = os.getenv("HANA_DB_USER")
    password = os.getenv("HANA_DB_PASSWORD")
    
    if not address:
        raise ValueError("HANA_DB_ADDRESS environment variable is required")
    if not user:
        raise ValueError("HANA_DB_USER environment variable is required")
    if not password:
        raise ValueError("HANA_DB_PASSWORD environment variable is required")
    
    return dbapi.connect(
        address=address,
        port=int(os.getenv("HANA_DB_PORT", "443")),
        user=user,
        password=password,
        autocommit=True,
    )


# =============================================================================
# MCP TOOL CALLS (reusing pattern from 02/03)
# =============================================================================

async def call_mcp_stock(ticker: str) -> dict:
    """Call MCP server to get stock info."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).parent.parent / "02-data-connector-mcp-done" / "mcp_server.py")],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_stock_info", {"ticker": ticker})
            
            # Parse the result
            if hasattr(result, 'content') and result.content:
                content = result.content[0]
                if hasattr(content, 'text'):
                    try:
                        return json.loads(content.text)
                    except json.JSONDecodeError:
                        return {"raw": content.text}
            return {"error": "Failed to get stock data"}


async def call_mcp_news(query: str) -> str:
    """Call MCP server to search news."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).parent.parent / "02-data-connector-mcp-done" / "mcp_server.py")],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("search_market_news", {"query": query, "limit": 5})
            
            if hasattr(result, 'content') and result.content:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return content.text
            return "No news found"


def get_documents(company_name: str) -> str:
    """Retrieve documents from HANA vector store."""
    try:
        connection = get_hana_connection()
        embeddings = init_embedding_model(EMBEDDING_MODEL)
        db = HanaDB(embedding=embeddings, connection=connection, table_name=TABLE_NAME)
        retriever = db.as_retriever(search_kwargs={"k": 5})
        
        search_query = f"{company_name} business strategy financial performance"
        docs = retriever.invoke(search_query)
        
        if docs:
            return "\n\n---\n\n".join(doc.page_content for doc in docs)
        return "No relevant documents found."
    except Exception as e:
        return f"Document retrieval failed: {str(e)}"


# =============================================================================
# NODE IMPLEMENTATIONS
# =============================================================================

async def supervisor_node(state: MemoState) -> dict:
    """Supervisor decides what action to take next."""
    print(f"\n🧠 Supervisor evaluating next action...")
    
    llm = init_llm(MODEL, max_tokens=100, temperature=0)
    
    prompt = SUPERVISOR_PROMPT.format(
        company_name=state["company_name"],
        ticker=state["ticker"],
        has_stock="✅ Yes" if state.get("stock_data") else "❌ No",
        has_news="✅ Yes" if state.get("news_data") else "❌ No",
        has_docs="✅ Yes" if state.get("doc_data") else "❌ No",
        sources=", ".join(state.get("gathered_sources", [])) or "None yet",
    )
    
    response = llm.invoke(prompt)
    action = response.content.strip().lower()
    
    # Validate action
    valid_actions = ["get_stock", "get_news", "get_docs", "generate_memo"]
    if action not in valid_actions:
        # Default to getting stock first if unclear
        action = "get_stock" if not state.get("stock_data") else "generate_memo"
    
    print(f"   → Decision: {action}")
    return {"next_action": action}


async def get_stock_node(state: MemoState) -> dict:
    """Fetch stock data via MCP."""
    print(f"\n📊 Fetching stock data for {state['ticker']}...")
    
    try:
        stock_data = await call_mcp_stock(state["ticker"])
        
        if "price" in stock_data:
            change = stock_data.get('change_percent', 0) or 0
            change_str = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
            print(f"   ✅ Price: {stock_data.get('currency', '¥')}{stock_data['price']} ({change_str})")
        else:
            print(f"   ✅ Retrieved stock data")
        
        sources = state.get("gathered_sources", []).copy()
        sources.append("stock")
        return {"stock_data": stock_data, "gathered_sources": sources}
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        return {"stock_data": {"error": str(e)}}


async def get_news_node(state: MemoState) -> dict:
    """Search news via MCP."""
    print(f"\n📰 Searching news for {state['company_name']}...")
    
    try:
        query = f"{state['company_name']} {state['ticker']} financial news investment"
        news_data = await call_mcp_news(query)
        print(f"   ✅ Found news articles")
        
        sources = state.get("gathered_sources", []).copy()
        sources.append("news")
        return {"news_data": news_data, "gathered_sources": sources}
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        return {"news_data": f"Error: {str(e)}"}


async def get_docs_node(state: MemoState) -> dict:
    """Retrieve documents from HANA."""
    print(f"\n📄 Retrieving documents...")
    
    try:
        doc_data = get_documents(state["company_name"])
        doc_count = doc_data.count("---") + 1 if "---" in doc_data else (1 if doc_data and "No relevant" not in doc_data else 0)
        print(f"   ✅ Retrieved {doc_count} document chunks")
        
        sources = state.get("gathered_sources", []).copy()
        sources.append("docs")
        return {"doc_data": doc_data, "gathered_sources": sources}
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        return {"doc_data": f"Error: {str(e)}"}


async def generate_memo_node(state: MemoState) -> dict:
    """Generate the Deal Memo using gathered data."""
    print(f"\n📝 Generating Deal Memo...")
    
    llm = init_llm(MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
    
    # Format stock data
    stock_str = ""
    if state.get("stock_data"):
        stock_str = "\n".join(f"  - {k}: {v}" for k, v in state["stock_data"].items() if v is not None)
    
    system_prompt = DEAL_MEMO_SYSTEM_PROMPT.format(
        company_name=state["company_name"],
        ticker=state["ticker"],
    )
    
    user_prompt = f"""Based on the following information about {state['company_name']} ({state['ticker']}), generate a formal 案件概要書 (Deal Memo) in Japanese.

=== STOCK DATA (株式データ) ===
{stock_str or "Not available"}

=== RECENT NEWS (最新ニュース) ===
{state.get('news_data', 'Not available')[:3000]}

=== INTERNAL DOCUMENTS (社内資料) ===
{state.get('doc_data', 'Not available')[:4000]}

Please generate a comprehensive 案件概要書 following the exact format specified.
All output must be in professional Japanese (敬語).
Include specific data points and cite sources where applicable."""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])
    
    print(f"   ✅ Memo generated")
    return {"memo": response.content, "iteration": state.get("iteration", 0) + 1}


async def quality_check_node(state: MemoState) -> dict:
    """Check the quality of the generated memo."""
    print(f"\n🔍 Quality check...")
    
    llm = init_llm(MODEL, max_tokens=50, temperature=0)
    
    prompt = QUALITY_CHECK_PROMPT.format(memo=state["memo"][:2000])
    response = llm.invoke(prompt)
    
    try:
        score = int(response.content.strip())
    except ValueError:
        score = 7  # Default if parsing fails
    
    print(f"   → Quality score: {score}/10")
    return {"quality_score": score}


# =============================================================================
# ROUTING FUNCTIONS
# =============================================================================

def route_supervisor(state: MemoState) -> Literal["get_stock", "get_news", "get_docs", "generate_memo"]:
    """Route based on supervisor's decision."""
    return state["next_action"]


def route_quality(state: MemoState) -> Literal["refine", "end"]:
    """Route based on quality score."""
    # If score is low and we haven't iterated too many times, refine
    if state.get("quality_score", 10) < 6 and state.get("iteration", 0) < 2:
        return "refine"
    return "end"


# =============================================================================
# GRAPH DEFINITION
# =============================================================================

def build_agent():
    """Build the LangGraph agent with supervisor pattern."""
    
    builder = StateGraph(MemoState)
    
    # Add nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("get_stock", get_stock_node)
    builder.add_node("get_news", get_news_node)
    builder.add_node("get_docs", get_docs_node)
    builder.add_node("generate_memo", generate_memo_node)
    builder.add_node("quality_check", quality_check_node)
    
    # Entry point
    builder.add_edge(START, "supervisor")
    
    # Supervisor routes to appropriate tool or memo generation
    builder.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "get_stock": "get_stock",
            "get_news": "get_news",
            "get_docs": "get_docs",
            "generate_memo": "generate_memo",
        }
    )
    
    # After each tool, go back to supervisor
    builder.add_edge("get_stock", "supervisor")
    builder.add_edge("get_news", "supervisor")
    builder.add_edge("get_docs", "supervisor")
    
    # After memo generation, check quality
    builder.add_edge("generate_memo", "quality_check")
    
    # Quality check routes to end or refine
    builder.add_conditional_edges(
        "quality_check",
        route_quality,
        {
            "refine": "generate_memo",  # Try generating again
            "end": END,
        }
    )
    
    return builder.compile()


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
