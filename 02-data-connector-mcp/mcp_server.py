"""Part 2: MCP Server with Stock and News Tools

This server exposes tools for fetching stock data and searching market news.
The agent client connects to this server and uses the tools automatically.

Run with MCP Inspector:
    uv run mcp dev mcp_server.py

Run as stdio server (for agent client):
    uv run python mcp_server.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from the repo root .env file
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Create an MCP server
mcp = FastMCP("DealCrafter Tools")


# =============================================================================
# EXERCISE 2a: Implement the Stock Info Tool
# =============================================================================

@mcp.tool()
def get_stock_info(ticker: str) -> dict:
    """Get current stock information for a given ticker symbol.
    
    Args:
        ticker: Stock ticker symbol (e.g., "3382.T" for Seven & i Holdings,
                "3778.T" for Sakura Internet)
    
    Returns:
        Dictionary with stock information including price, currency, etc.
    """
    # ==========================================================================
    # TODO 1: Import yfinance
    # Hint: import yfinance as yf
    #
    # TODO 2: Create a Ticker object and get info
    # Hint: stock = yf.Ticker(ticker)
    # Hint: info = stock.info
    #
    # TODO 3: Return a dictionary with stock data
    # Hint: return {
    #     "ticker": ticker,
    #     "price": info.get("currentPrice") or info.get("regularMarketPrice"),
    #     "currency": info.get("currency", "JPY"),
    #     "change_percent": info.get("regularMarketChangePercent"),
    #     "market_cap": info.get("marketCap"),
    #     "pe_ratio": info.get("trailingPE"),
    #     "company_name": info.get("longName"),
    # }
    # ==========================================================================
    
    raise NotImplementedError("Exercise 2a: Implement get_stock_info with yfinance")


# =============================================================================
# EXERCISE 2b: Implement the News Search Tool
# =============================================================================

@mcp.tool()
def search_market_news(query: str, limit: int = 5) -> str:
    """Search for recent market news about a topic using Perplexity AI.
    
    Args:
        query: Search query (e.g., "Seven & i Holdings takeover bid")
        limit: Maximum number of news items to return
    
    Returns:
        String containing news summaries with sources
    """
    # ==========================================================================
    # TODO 1: Import the LLM initializer
    # Hint: from gen_ai_hub.proxy.langchain.init_models import init_llm
    #
    # TODO 2: Get the Perplexity model name from environment
    # Hint: model = os.getenv("PERPLEXITY_MODEL", "perplexity--sonar-pro")
    #
    # TODO 3: Initialize Perplexity
    # Hint: perplexity = init_llm(model, max_tokens=4000, temperature=0.1)
    #
    # TODO 4: Create a search prompt and invoke Perplexity
    # Hint: prompt = f"""Search for the {limit} most recent news articles about: {query}
    # 
    # For each article, provide:
    # - Title
    # - Brief summary (2-3 sentences)
    # - Source
    # 
    # Focus on financial and business news."""
    #
    # Hint: response = perplexity.invoke(prompt)
    # Hint: return response.content
    # ==========================================================================
    
    raise NotImplementedError("Exercise 2b: Implement search_market_news with Perplexity")


# =============================================================================
# BONUS: Additional useful tools you could add
# =============================================================================

@mcp.tool()
def get_stock_history(ticker: str, period: str = "1mo") -> dict:
    """Get historical stock data for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    
    Returns:
        Dictionary with historical price data
    """
    # This is a bonus tool - implement if you have time!
    raise NotImplementedError("Bonus: Implement get_stock_history")


if __name__ == "__main__":
    # Run with stdio transport for agent client connection
    mcp.run(transport="stdio")
