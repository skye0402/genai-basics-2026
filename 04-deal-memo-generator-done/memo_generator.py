"""Part 4: Japanese Deal Memo Generator (Complete)

This script generates a formal Japanese Investment Memo (案件概要書)
by combining all components from Parts 1-3.

Run with:
    uv run python memo_generator.py
"""

import os
from pathlib import Path

import yfinance as yf
from dotenv import load_dotenv
from hdbcli import dbapi
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_hana import HanaDB
from gen_ai_hub.proxy.langchain.init_models import init_llm, init_embedding_model

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
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "perplexity--sonar-pro")


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


def get_system_prompt() -> str:
    """Load and format the Japanese system prompt."""
    return DEAL_MEMO_SYSTEM_PROMPT.format(
        company_name=COMPANY_NAME,
        ticker=TICKER,
    )


# =============================================================================
# DATA GATHERING FUNCTIONS
# =============================================================================

def gather_stock_data() -> dict:
    """Fetch current stock data using yfinance."""
    print(f"📊 Fetching stock data for {TICKER}...")
    
    try:
        stock = yf.Ticker(TICKER)
        info = stock.info
        
        stock_data = {
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
            "business_summary": info.get("longBusinessSummary", "")[:500],
        }
        
        change = stock_data.get('change_percent', 0) or 0
        change_str = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
        print(f"   ✅ Price: ¥{stock_data['price']:,.0f} ({change_str})")
        
        return stock_data
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        return {"error": str(e)}


def gather_news() -> str:
    """Search for recent news using Perplexity."""
    print(f"📰 Searching news for {COMPANY_NAME}...")
    
    try:
        perplexity = init_llm(PERPLEXITY_MODEL, max_tokens=2000, temperature=0.1)
        
        prompt = f"""Search for the 5 most recent and important news articles about {COMPANY_NAME} ({TICKER}).

Focus on:
- Financial results and announcements
- Strategic developments (M&A, partnerships, expansions)
- Market trends affecting the company
- Regulatory or policy changes
- Any controversies or challenges

For each article, provide:
- Title
- 2-3 sentence summary
- Source and approximate date"""

        response = perplexity.invoke(prompt)
        print(f"   ✅ Found recent articles")
        return response.content
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        return f"News search failed: {str(e)}"


def gather_documents() -> str:
    """Retrieve relevant documents from HANA vector store."""
    print(f"📄 Retrieving documents...")
    
    try:
        connection = get_hana_connection()
        embeddings = init_embedding_model(EMBEDDING_MODEL)
        db = HanaDB(embedding=embeddings, connection=connection, table_name=TABLE_NAME)
        retriever = db.as_retriever(search_kwargs={"k": 5})
        
        # Search for company-related documents
        search_query = f"{COMPANY_NAME} business strategy financial performance"
        docs = retriever.invoke(search_query)
        
        if docs:
            context = "\n\n---\n\n".join(doc.page_content for doc in docs)
            print(f"   ✅ Retrieved {len(docs)} chunks")
            return context
        else:
            print(f"   ⚠️ No documents found")
            return "No relevant internal documents found."
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        return f"Document retrieval failed: {str(e)}"


# =============================================================================
# MEMO GENERATION
# =============================================================================

def generate_memo() -> str:
    """Generate the complete Japanese Deal Memo."""
    
    # Gather all data
    stock_data = gather_stock_data()
    news = gather_news()
    documents = gather_documents()
    
    print(f"📝 Generating Japanese memo...")
    
    # Format stock data for prompt
    stock_str = "\n".join(f"  - {k}: {v}" for k, v in stock_data.items() if v is not None)
    
    # Create user prompt with all gathered data
    user_prompt = f"""Based on the following information about {COMPANY_NAME} ({TICKER}), generate a formal 案件概要書 (Deal Memo) in Japanese.

=== STOCK DATA (株式データ) ===
{stock_str}

=== RECENT NEWS (最新ニュース) ===
{news}

=== INTERNAL DOCUMENTS (社内資料) ===
{documents[:4000]}

Please generate a comprehensive 案件概要書 following the exact format specified in the system prompt.
All output must be in professional Japanese (敬語).
Include specific data points and cite sources where applicable."""

    # Generate the memo
    system_prompt = get_system_prompt()
    llm = init_llm(MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])
    
    return response.content


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Run the Deal Memo Generator."""
    
    print("\n" + "=" * 60)
    print("📝 DealCrafter Assistant - 案件概要書 Generator")
    print("=" * 60)
    print(f"Target: {COMPANY_NAME} ({TICKER})")
    print("Output Language: Japanese (敬語)")
    print("=" * 60)
    
    memo = generate_memo()
    
    print("\n" + "=" * 60)
    print("=== 案件概要書 (Deal Memo) ===")
    print("=" * 60)
    print(memo)
    
    # Save to file
    output_file = Path(f"deal_memo_{TICKER.replace('.', '_')}.md")
    output_file.write_text(memo, encoding="utf-8")
    print(f"\n💾 Saved to {output_file}")
    
    print("\n🎉 Deal Memo generation complete!")


if __name__ == "__main__":
    main()
