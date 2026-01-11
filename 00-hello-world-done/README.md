# Part 0: Hello World (Complete)

> **This is the complete, runnable version.** Use this if you want to skip the exercise or verify your solution.

---

## 🚀 Quick Run

```bash
cd 00-hello-world-done
uv sync
uv run python main.py
```

---

## ✅ Expected Output

```
🔌 Connecting to SAP Generative AI Hub...
✅ Connected! Using model: gpt-4.1

You: Hello! Please introduce yourself briefly.
Assistant: Hello! I'm an AI assistant powered by SAP Generative AI Hub...
```

---

## 📝 What This Does

1. Loads credentials from `.env`
2. Initializes an LLM via `gen_ai_hub.proxy.langchain.init_models`
3. Sends a simple prompt
4. Prints the response

This confirms your SAP AI Core connection is working correctly.
