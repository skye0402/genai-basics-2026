# Part 4: The Deal Memo Generator

> **Goal:** Generate a professional Investment Memo in **Japanese** (案件概要書) based on multilingual inputs.

---

## 🎯 What You'll Build

The final piece: a **bilingual AI analyst** that:
- Reads English/Japanese news, documents, and stock data
- Generates a formal Japanese 案件概要書 (Deal Memo)
- Follows Itochu's Corporate Planning Division (経営企画部) format

---

## 🌏 The "Wow" Factor

| Input | Output |
|-------|--------|
| News articles (English/Japanese) | **Japanese** |
| PDF documents (English/Japanese) | **Japanese** |
| Stock data (English) | **Japanese** |
| → Final Deal Memo | **100% Japanese (敬語/Business Japanese)** |

The AI acts as an elite bilingual analyst!

---

## 📋 Scenario

> "Take all the analysis from Parts 1-3 and generate a formal Deal Memo for {COMPANY_NAME} in Itochu format."

---

## 🚀 Steps

### 1. Install Dependencies

```bash
cd 04-deal-memo-generator
uv sync
```

### 2. Run the Generator

```bash
uv run python memo_generator.py
```

---

## 📝 Output Format (案件概要書)

```markdown
# 案件概要書 (Deal Memo): {COMPANY_NAME}

## 1. エグゼクティブサマリー (Executive Summary)
* [3-bullet summary]
* [Conclusion: 買い/保有/売り]

## 2. 企業概要 (Company Overview)
* **社名:** {COMPANY_NAME}
* **主要事業:** [Description]
* **直近株価:** ¥X,XXX (変動率: X.X%)

## 3. 市場分析・外部環境 (Market Analysis)
* [Market trends and external factors]

## 4. 財務・リスク評価 (Financial & Risk Assessment)
* **強み (Pros):** [Strengths]
* **リスク (Cons):** [Risks]

## 5. 伊藤忠商事としての戦略的意義 (Strategic Fit)
* [Alignment with "Brand-new Deal" strategy]

## 6. 推奨アクション (Recommendation)
* [Clear recommendation]
```

---

## 🏋️ Exercises

### Exercise 4a: Load the System Prompt

```python
def get_system_prompt() -> str:
    # TODO: Format the system prompt with company details
```

### Exercise 4b: Run the Full Workflow

```python
def generate_memo(query: str) -> str:
    # TODO: Reuse the analyst workflow from Part 3
    # TODO: Pass the analysis to the LLM with the Japanese system prompt
    # TODO: Return the formatted 案件概要書
```

---

## 💡 Key Concepts

### Bilingual Prompt Engineering

The system prompt instructs the LLM to:
1. Accept multilingual input
2. Generate professional Japanese output (敬語/Keigo)
3. Follow strict document formatting

### The 経営企画部 Persona

The AI adopts the role of a "Strategic Planning Department Chief":
- Objective and risk-aware
- Profit-driven ("Earn" mindset)
- Formal business Japanese

---

## ✅ Success Criteria

```
🔄 Generating Deal Memo for Sakura Internet (3778.T)
📊 Fetching stock data...
📰 Searching news...
📄 Retrieving documents...
📝 Generating Japanese memo...

============================================================
# 案件概要書 (Deal Memo): さくらインターネット株式会社

## 1. エグゼクティブサマリー
* 政府クラウド事業の急成長により、売上高は前年比150%増
* AI主権政策による追い風は継続見込み
* **結論: 買い（短期的な調整リスクあり）**

## 2. 企業概要
* **社名:** さくらインターネット株式会社
* **主要事業:** クラウドインフラ、データセンター運営
* **直近株価:** ¥5,230 (変動率: +2.3%)
...
```

---

## 🎭 Demo: React Frontend

At the end of this exercise, the facilitator will demo a **React frontend** that:
- Connects to the MCP server you built in Part 2
- Displays the Deal Memo in a polished UI
- Shows the workflow execution in real-time

This is **not hands-on** but shows what's possible!

---

## 🏁 Congratulations!

You've built a complete **DealCrafter Assistant** that:
1. ✅ Ingests financial PDFs into HANA Vector Engine
2. ✅ Fetches real-time stock data via MCP tools
3. ✅ Searches market news via Perplexity AI
4. ✅ Orchestrates analysis with LangGraph
5. ✅ Generates bilingual Japanese reports

**Welcome to the future of investment analysis on SAP BTP!**
