"""Part 3: LangGraph Analyst Workflow

This script implements a multi-step analysis workflow using LangGraph.
The graph structure is provided - you implement the node logic.

Run with:
    uv run python analyst_agent.py
"""

import os
from pathlib import Path
from typing_extensions import TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

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
# STATE DEFINITION (PROVIDED - DO NOT MODIFY)
# =============================================================================

class AnalystState(TypedDict):
    """State passed between LangGraph nodes."""
    company_name: str             # e.g., "Seven & i Holdings"
    ticker: str                   # e.g., "3382.T"
    query: str                    # User's research question
    stock_info: dict              # From get_stock_info
    news_results: str             # From news search (as formatted string)
    doc_context: str              # From RAG retrieval
    analysis: str                 # Final analysis output
    step_count: int               # Track progress


# =============================================================================
# NODE IMPLEMENTATIONS (EXERCISES - IMPLEMENT THESE)
# =============================================================================

def fetch_stock_node(state: AnalystState) -> dict:
    """EXERCISE 3a: Fetch stock data using yfinance.
    
    TODO:
    1. Import yfinance
    2. Get stock info for state["ticker"]
    3. Return {"stock_info": {...}, "step_count": state["step_count"] + 1}
    """
    print(f"📊 Step 1: Fetching stock data for {state['ticker']}...")
    
    # ==========================================================================
    # TODO: Import yfinance
    # Hint: import yfinance as yf
    #
    # TODO: Get stock info
    # Hint: stock = yf.Ticker(state["ticker"])
    # Hint: info = stock.info
    #
    # TODO: Build stock_info dict
    # Hint: stock_info = {
    #     "price": info.get("currentPrice") or info.get("regularMarketPrice"),
    #     "currency": info.get("currency", "JPY"),
    #     "change_percent": info.get("regularMarketChangePercent"),
    #     "market_cap": info.get("marketCap"),
    #     "pe_ratio": info.get("trailingPE"),
    # }
    #
    # TODO: Print and return
    # Hint: print(f"   ✅ Price: {stock_info['currency']}{stock_info['price']}")
    # Hint: return {"stock_info": stock_info, "step_count": state["step_count"] + 1}
    # ==========================================================================
    
    raise NotImplementedError("Exercise 3a: Implement fetch_stock_node")


def search_news_node(state: AnalystState) -> dict:
    """EXERCISE 3b: Search for market news using Perplexity.
    
    TODO:
    1. Initialize Perplexity LLM
    2. Search for news about the company
    3. Return {"news_results": "...", "step_count": ...}
    """
    print(f"📰 Step 2: Searching news for {state['company_name']}...")
    
    # ==========================================================================
    # TODO: Import and initialize Perplexity
    # Hint: from gen_ai_hub.proxy.langchain.init_models import init_llm
    # Hint: perplexity = init_llm(PERPLEXITY_MODEL, max_tokens=2000)
    #
    # TODO: Create search prompt
    # Hint: prompt = f"Search for the 5 most recent news articles about {state['company_name']}..."
    #
    # TODO: Invoke and return
    # Hint: response = perplexity.invoke(prompt)
    # Hint: print(f"   ✅ Found news articles")
    # Hint: return {"news_results": response.content, "step_count": state["step_count"] + 1}
    # ==========================================================================
    
    raise NotImplementedError("Exercise 3b: Implement search_news_node")


def retrieve_docs_node(state: AnalystState) -> dict:
    """EXERCISE 3c: Retrieve relevant documents from HANA vector store.
    
    TODO:
    1. Connect to HANA
    2. Query vector store with the user's query
    3. Return {"doc_context": "...", "step_count": ...}
    """
    print(f"📄 Step 3: Retrieving documents...")
    
    # ==========================================================================
    # TODO: Import required modules
    # Hint: from hdbcli import dbapi
    # Hint: from langchain_hana import HanaDB
    # Hint: from gen_ai_hub.proxy.langchain.init_models import init_embedding_model
    #
    # TODO: Connect to HANA
    # Hint: connection = dbapi.connect(
    #     address=os.getenv("HANA_DB_ADDRESS"),
    #     port=int(os.getenv("HANA_DB_PORT", "443")),
    #     user=os.getenv("HANA_DB_USER"),
    #     password=os.getenv("HANA_DB_PASSWORD"),
    #     autocommit=True,
    #     sslValidateCertificate=False,
    # )
    #
    # TODO: Create vector store and retriever
    # Hint: embeddings = init_embedding_model(EMBEDDING_MODEL)
    # Hint: db = HanaDB(embedding=embeddings, connection=connection, table_name=TABLE_NAME)
    # Hint: retriever = db.as_retriever(search_kwargs={"k": 5})
    #
    # TODO: Retrieve and format context
    # Hint: docs = retriever.invoke(state["query"])
    # Hint: context = "\n\n---\n\n".join(doc.page_content for doc in docs)
    # Hint: print(f"   ✅ Retrieved {len(docs)} relevant chunks")
    # Hint: return {"doc_context": context, "step_count": state["step_count"] + 1}
    # ==========================================================================
    
    raise NotImplementedError("Exercise 3c: Implement retrieve_docs_node")


def analyze_node(state: AnalystState) -> dict:
    """EXERCISE 3d: Generate analysis using LLM.
    
    TODO:
    1. Combine all gathered data into a prompt
    2. Call the LLM to generate analysis
    3. Return {"analysis": "..."}
    """
    print(f"🧠 Step 4: Analyzing...")
    
    # ==========================================================================
    # TODO: Import and initialize LLM
    # Hint: from gen_ai_hub.proxy.langchain.init_models import init_llm
    # Hint: llm = init_llm(MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
    #
    # TODO: Create analysis prompt
    # Hint: prompt = f"""You are a financial analyst. Analyze {state['company_name']} ({state['ticker']}).
    #
    # STOCK DATA:
    # {state['stock_info']}
    #
    # RECENT NEWS:
    # {state['news_results']}
    #
    # INTERNAL DOCUMENTS:
    # {state['doc_context']}
    #
    # USER QUESTION: {state['query']}
    #
    # Provide a comprehensive analysis covering:
    # 1. Current market position
    # 2. Key risks and opportunities
    # 3. Your assessment
    # """
    #
    # TODO: Generate and return analysis
    # Hint: response = llm.invoke(prompt)
    # Hint: return {"analysis": response.content}
    # ==========================================================================
    
    raise NotImplementedError("Exercise 3d: Implement analyze_node")


# =============================================================================
# GRAPH DEFINITION (PROVIDED - DO NOT MODIFY)
# =============================================================================

# Build the graph
agent_builder = StateGraph(AnalystState)

# Add nodes
agent_builder.add_node("fetch_stock", fetch_stock_node)
agent_builder.add_node("search_news", search_news_node)
agent_builder.add_node("retrieve_docs", retrieve_docs_node)
agent_builder.add_node("analyze", analyze_node)

# Add edges (linear flow)
agent_builder.add_edge(START, "fetch_stock")
agent_builder.add_edge("fetch_stock", "search_news")
agent_builder.add_edge("search_news", "retrieve_docs")
agent_builder.add_edge("retrieve_docs", "analyze")
agent_builder.add_edge("analyze", END)

# Compile the graph
agent = agent_builder.compile()


# =============================================================================
# MAIN EXECUTION (PROVIDED - DO NOT MODIFY)
# =============================================================================

def main():
    """Run the analyst workflow."""
    
    print(f"\n🔄 Starting analyst workflow for {COMPANY_NAME} ({TICKER})")
    print("=" * 60)
    
    # Get user query
    default_query = f"Analyze the investment potential of {COMPANY_NAME}"
    query = input(f"Enter your analysis question [{default_query}]: ").strip()
    if not query:
        query = default_query
    
    print()
    
    # Run the workflow
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
    
    # Print results
    print("\n" + "=" * 60)
    print("=== ANALYSIS RESULT ===")
    print("=" * 60)
    print(result["analysis"])


if __name__ == "__main__":
    main()
