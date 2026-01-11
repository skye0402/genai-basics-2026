"""Part 0: Hello World - SAP Generative AI Hub Connectivity Test (Complete)

This script verifies that your environment is correctly configured
to connect to SAP Generative AI Hub.

Run with:
    uv run python main.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from gen_ai_hub.proxy.langchain.init_models import init_llm

# Load environment variables from the repo root .env file
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Configuration from environment
MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))


def main():
    """Send a simple prompt to SAP Generative AI Hub and print the response."""
    
    print("🔌 Connecting to SAP Generative AI Hub...")
    
    # Initialize the LLM via SAP Generative AI Hub
    llm = init_llm(MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
    
    print(f"✅ Connected! Using model: {MODEL}\n")
    
    # Send a simple prompt
    prompt = "Hello! Please introduce yourself briefly."
    print(f"You: {prompt}")
    
    response = llm.invoke(prompt)
    print(f"Assistant: {response.content}\n")
    
    print("🎉 Success! Your environment is ready for the workshop.")


if __name__ == "__main__":
    main()
