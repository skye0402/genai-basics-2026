# Part 0: Hello World

> **Goal:** Verify your environment is set up correctly and can connect to SAP Generative AI Hub.

---

## 🎯 What You'll Do

1. Configure your `.env` file with SAP AI Core credentials
2. Send a simple prompt to the LLM
3. Receive a response confirming connectivity

---

## 📋 Prerequisites

Before starting, ensure you have:
- [ ] Python 3.12+ installed
- [ ] `uv` package manager installed
- [ ] Credentials provided by the workshop facilitator

---

## 🚀 Steps

### 1. Set Up Environment

From the repository root:

```bash
# Copy the environment template (if not done already)
cp .env.example .env

# Edit .env with your credentials
# Your facilitator will provide:
# - AICORE_CLIENT_ID
# - AICORE_CLIENT_SECRET
# - AICORE_AUTH_URL
# - AICORE_BASE_URL
```

### 2. Install Dependencies

```bash
cd 00-hello-world
uv sync
```

### 3. Run the Script

```bash
uv run python main.py
```

---

## ✅ Expected Output

You should see something like:

```
🔌 Connecting to SAP Generative AI Hub...
✅ Connected! Using model: gpt-4.1

You: Hello, who are you?
Assistant: Hello! I'm an AI assistant powered by SAP Generative AI Hub...
```

---

## 🏋️ Exercise

Open `main.py` and complete the TODO:

```python
def main():
    # TODO: Initialize the LLM using gen_ai_hub
    # Hint: Use init_llm() from gen_ai_hub.proxy.langchain.init_models
    
    # TODO: Send a simple prompt and print the response
    pass
```

**Hints:**
- Import `init_llm` from `gen_ai_hub.proxy.langchain.init_models`
- Use `llm.invoke("Your prompt here")` to get a response
- The model name is in `os.getenv("LLM_MODEL")`

---

## 🆘 Troubleshooting

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `uv sync` first |
| `Authentication failed` | Check your `.env` credentials |
| `Connection timeout` | Check your network/VPN |

---

## ➡️ Next Step

Once you see a successful response, you're ready for **Part 1: The Research Engine**!
