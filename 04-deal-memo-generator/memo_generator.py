"""Part 4: Japanese Deal Memo Generator (案件概要書)

This script generates a formal Japanese Investment Memo by combining
all the components from Parts 1-3.

Run with:
    uv run python memo_generator.py
"""

import os
from pathlib import Path
from typing_extensions import TypedDict

from dotenv import load_dotenv

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
# EXERCISE 4a: Load and format the system prompt
# =============================================================================

def get_system_prompt() -> str:
    """Load and format the Japanese system prompt.
    
    TODO:
    1. Use the DEAL_MEMO_SYSTEM_PROMPT template above
    2. Format it with COMPANY_NAME and TICKER
    """
    # ==========================================================================
    # TODO: Format the system prompt with company details
    # Hint: return DEAL_MEMO_SYSTEM_PROMPT.format(
    #     company_name=COMPANY_NAME,
    #     ticker=TICKER,
    # )
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4a: Format the system prompt")


# =============================================================================
# EXERCISE 4b: Gather data from previous parts
# =============================================================================

def gather_stock_data() -> dict:
    """Fetch current stock data.
    
    TODO: Reuse the yfinance pattern from Part 2/3
    """
    print(f"📊 Fetching stock data for {TICKER}...")
    
    # ==========================================================================
    # TODO: Import yfinance and fetch stock data
    # Hint: import yfinance as yf
    # Hint: stock = yf.Ticker(TICKER)
    # Hint: return stock.info
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4b: Fetch stock data")


def gather_news() -> str:
    """Search for recent news.
    
    TODO: Reuse the Perplexity pattern from Part 2/3
    """
    print(f"📰 Searching news for {COMPANY_NAME}...")
    
    # ==========================================================================
    # TODO: Use Perplexity to search for news
    # Hint: from gen_ai_hub.proxy.langchain.init_models import init_llm
    # Hint: perplexity = init_llm(PERPLEXITY_MODEL, max_tokens=2000)
    # Hint: response = perplexity.invoke(f"Recent news about {COMPANY_NAME}...")
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4b: Search news")


def gather_documents() -> str:
    """Retrieve relevant documents from HANA.
    
    TODO: Reuse the RAG pattern from Part 1/3
    """
    print(f"📄 Retrieving documents...")
    
    # ==========================================================================
    # TODO: Connect to HANA and retrieve documents
    # Hint: Reuse the retriever pattern from Part 1/3
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4b: Retrieve documents")


# =============================================================================
# EXERCISE 4c: Generate the Japanese memo
# =============================================================================

def generate_memo() -> str:
    """Generate the complete Japanese Deal Memo.
    
    TODO:
    1. Gather all data
    2. Combine into a user prompt
    3. Call LLM with system prompt
    4. Return the Japanese memo
    """
    print(f"\n🔄 Generating Deal Memo for {COMPANY_NAME} ({TICKER})")
    print("=" * 60)
    
    # ==========================================================================
    # TODO: Get the system prompt
    # Hint: system_prompt = get_system_prompt()
    #
    # TODO: Gather all data
    # Hint: stock_data = gather_stock_data()
    # Hint: news = gather_news()
    # Hint: documents = gather_documents()
    #
    # TODO: Create user prompt with all data
    # Hint: user_prompt = f"""
    # === STOCK DATA ===
    # {stock_data}
    #
    # === RECENT NEWS ===
    # {news}
    #
    # === INTERNAL DOCUMENTS ===
    # {documents}
    #
    # Please generate the 案件概要書 based on this information.
    # """
    #
    # TODO: Initialize LLM and generate memo
    # Hint: from gen_ai_hub.proxy.langchain.init_models import init_llm
    # Hint: llm = init_llm(MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
    # Hint: from langchain_core.messages import SystemMessage, HumanMessage
    # Hint: response = llm.invoke([
    #     SystemMessage(content=system_prompt),
    #     HumanMessage(content=user_prompt),
    # ])
    # Hint: return response.content
    # ==========================================================================
    
    raise NotImplementedError("Exercise 4c: Generate the Japanese memo")


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
    
    # Optionally save to file
    output_file = Path(f"deal_memo_{TICKER.replace('.', '_')}.md")
    output_file.write_text(memo, encoding="utf-8")
    print(f"\n💾 Saved to {output_file}")


if __name__ == "__main__":
    main()
