"""Part 2: MCP Server with Stock and News Tools (Complete)

This server exposes tools for fetching stock data and searching market news.

Run with MCP Inspector:
    uv run mcp dev mcp_server.py

Run as stdio server (for agent client):
    uv run python mcp_server.py
"""

import os
import sys
from pathlib import Path

import yfinance as yf
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Add parent directory to path to import genai module
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from genai.perplexity_sonar import create_perplexity_client

# Load environment variables from the repo root .env file
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Create an MCP server
mcp = FastMCP("DealCrafter Tools")


@mcp.tool()
def get_stock_info(ticker: str) -> dict:
    """Get current stock information for a given ticker symbol.
    
    Args:
        ticker: Stock ticker symbol (e.g., "3382.T" for Seven & i Holdings,
                "3778.T" for Sakura Internet)
    
    Returns:
        Dictionary with stock information including price, currency, etc.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            "ticker": ticker,
            "company_name": info.get("longName") or info.get("shortName"),
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "currency": info.get("currency", "JPY"),
            "change_percent": info.get("regularMarketChangePercent"),
            "previous_close": info.get("previousClose"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}


@mcp.tool()
def search_market_news(query: str, limit: int = 5) -> str:
    """Search for recent market news about a topic using Perplexity AI.
    
    Args:
        query: Search query (e.g., "Seven & i Holdings takeover bid")
        limit: Maximum number of news items to return
    
    Returns:
        String containing news summaries with sources
    """
    try:
        # Create Perplexity client using the dedicated Sonar integration
        perplexity = create_perplexity_client(
            model=os.getenv("PERPLEXITY_MODEL", "perplexity--sonar-pro"),
            temperature=0.1,
            max_tokens=4000,
            deployment_id=os.getenv("PERPLEXITY_DEPLOYMENT_ID")
        )
        
        prompt = f"""Search for the {limit} most recent news articles about: {query}

For each article, provide:
- Title
- Brief summary (2-3 sentences)
- Source and date if available

Focus on financial and business news. Be concise."""
        
        response = perplexity.invoke(prompt)
        return response
    except Exception as e:
        return f"Error searching news: {str(e)}"


@mcp.tool()
def get_stock_history(ticker: str, period: str = "1mo") -> dict:
    """Get historical stock data for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period - 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    
    Returns:
        Dictionary with historical price data summary
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            return {"error": "No historical data available", "ticker": ticker}
        
        return {
            "ticker": ticker,
            "period": period,
            "start_date": str(hist.index[0].date()),
            "end_date": str(hist.index[-1].date()),
            "start_price": round(hist["Close"].iloc[0], 2),
            "end_price": round(hist["Close"].iloc[-1], 2),
            "high": round(hist["High"].max(), 2),
            "low": round(hist["Low"].min(), 2),
            "avg_volume": int(hist["Volume"].mean()),
            "price_change_percent": round(
                ((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0]) * 100, 2
            ),
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}


if __name__ == "__main__":
    mcp.run(transport="stdio")
