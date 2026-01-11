"""Part 3: LangGraph Analyst Workflow (Complete)

This script implements a multi-step analysis workflow using LangGraph.

Run with:
    uv run python analyst_agent.py
"""

import os
from pathlib import Path
from typing_extensions import TypedDict

import yfinance as yf
from dotenv import load_dotenv
from hdbcli import dbapi
from langchain_hana import HanaDB
from langgraph.graph import StateGraph, START, END
from gen_ai_hub.proxy.langchain.init_models import init_llm, init_embedding_model

# Load environment variables from the repo root .env file
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Configuration
MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4000"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
COMPANY_NAME = os.getenv("COMPANY_NAME", "Sakura Internet")
TICKER = os.getenv("TICKER", "3778.T")
EMBEDDING_MODEL = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-3-small")
TABLE_NAME = os.getenv("HANA_TABLE_NAME", "DEALCRAFTER_DOCS")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "perplexity--sonar-pro")


# =============================================================================
# STATE DEFINITION
# =============================================================================

class AnalystState(TypedDict):
    """State passed between LangGraph nodes."""
    company_name: str
    ticker: str
    query: str
    stock_info: dict
    news_results: str
    doc_context: str
    analysis: str
    step_count: int


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_hana_connection():
    """Create a connection to SAP HANA Cloud."""
    return dbapi.connect(
        address=os.getenv("HANA_DB_ADDRESS"),
        port=int(os.getenv("HANA_DB_PORT", "443")),
        user=os.getenv("HANA_DB_USER"),
        password=os.getenv("HANA_DB_PASSWORD"),
        autocommit=True,
        sslValidateCertificate=False,
    )


# =============================================================================
# NODE IMPLEMENTATIONS
# =============================================================================

def fetch_stock_node(state: AnalystState) -> dict:
    """Fetch stock data using yfinance."""
    print(f"📊 Step 1: Fetching stock data for {state['ticker']}...")
    
    try:
        stock = yf.Ticker(state["ticker"])
        info = stock.info
        
        stock_info = {
            "company_name": info.get("longName") or info.get("shortName"),
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "currency": info.get("currency", "JPY"),
            "change_percent": info.get("regularMarketChangePercent"),
            "previous_close": info.get("previousClose"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
        }
        
        change_str = f"▲{stock_info['change_percent']:.1f}%" if stock_info.get('change_percent', 0) >= 0 else f"▼{abs(stock_info['change_percent']):.1f}%"
        print(f"   ✅ Price: {stock_info['currency']}{stock_info['price']} ({change_str})")
        
        return {"stock_info": stock_info, "step_count": state["step_count"] + 1}
    except Exception as e:
        print(f"   ⚠️ Error fetching stock: {e}")
        return {"stock_info": {"error": str(e)}, "step_count": state["step_count"] + 1}


def search_news_node(state: AnalystState) -> dict:
    """Search for market news using Perplexity."""
    print(f"📰 Step 2: Searching news for {state['company_name']}...")
    
    try:
        perplexity = init_llm(PERPLEXITY_MODEL, max_tokens=2000, temperature=0.1)
        
        prompt = f"""Search for the 5 most recent news articles about {state['company_name']} ({state['ticker']}).
Focus on:
- Financial performance
- Strategic announcements
- Market trends affecting the company
- Any recent controversies or challenges

For each article, provide the title, a brief 2-sentence summary, and source."""
        
        response = perplexity.invoke(prompt)
        print(f"   ✅ Found news articles")
        
        return {"news_results": response.content, "step_count": state["step_count"] + 1}
    except Exception as e:
        print(f"   ⚠️ Error searching news: {e}")
        return {"news_results": f"Error: {str(e)}", "step_count": state["step_count"] + 1}


def retrieve_docs_node(state: AnalystState) -> dict:
    """Retrieve relevant documents from HANA vector store."""
    print(f"📄 Step 3: Retrieving documents...")
    
    try:
        connection = get_hana_connection()
        embeddings = init_embedding_model(EMBEDDING_MODEL)
        db = HanaDB(embedding=embeddings, connection=connection, table_name=TABLE_NAME)
        retriever = db.as_retriever(search_kwargs={"k": 5})
        
        # Combine company name and query for better retrieval
        search_query = f"{state['company_name']} {state['query']}"
        docs = retriever.invoke(search_query)
        
        if docs:
            context = "\n\n---\n\n".join(doc.page_content for doc in docs)
            print(f"   ✅ Retrieved {len(docs)} relevant chunks")
        else:
            context = "No relevant documents found in the database."
            print(f"   ⚠️ No documents found")
        
        return {"doc_context": context, "step_count": state["step_count"] + 1}
    except Exception as e:
        print(f"   ⚠️ Error retrieving docs: {e}")
        return {"doc_context": f"Error: {str(e)}", "step_count": state["step_count"] + 1}


def analyze_node(state: AnalystState) -> dict:
    """Generate analysis using LLM."""
    print(f"🧠 Step 4: Analyzing...")
    
    llm = init_llm(MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
    
    # Format stock info for prompt
    stock_str = "\n".join(f"  - {k}: {v}" for k, v in state["stock_info"].items() if v is not None)
    
    prompt = f"""You are a senior financial analyst. Analyze {state['company_name']} ({state['ticker']}).

=== CURRENT STOCK DATA ===
{stock_str}

=== RECENT NEWS ===
{state['news_results']}

=== INTERNAL DOCUMENTS ===
{state['doc_context'][:3000]}

=== USER QUESTION ===
{state['query']}

Provide a comprehensive analysis covering:
1. **Executive Summary** - Key takeaways in 3 bullets
2. **Market Position** - Current standing and trends
3. **Financial Health** - Based on available data
4. **Risks** - Key concerns and challenges
5. **Opportunities** - Growth potential
6. **Preliminary Assessment** - Your initial recommendation (Buy/Hold/Sell with reasoning)

Be concise but thorough. Cite specific data points from the provided information."""

    response = llm.invoke(prompt)
    return {"analysis": response.content}


# =============================================================================
# GRAPH DEFINITION
# =============================================================================

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


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Run the analyst workflow."""
    
    print(f"\n🔄 Starting analyst workflow for {COMPANY_NAME} ({TICKER})")
    print("=" * 60)
    
    default_query = f"Analyze the investment potential of {COMPANY_NAME}"
    query = input(f"Enter your analysis question [{default_query}]: ").strip()
    if not query:
        query = default_query
    
    print()
    
    result = agent.invoke({
        "company_name": COMPANY_NAME,
        "ticker": TICKER,
        "query": query,
        "stock_info": {},
        "news_results": "",
        "doc_context": "",
        "analysis": "",
        "step_count": 0,
    })
    
    print("\n" + "=" * 60)
    print("=== ANALYSIS RESULT ===")
    print("=" * 60)
    print(result["analysis"])


if __name__ == "__main__":
    main()
