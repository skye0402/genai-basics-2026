"""Part 0: Hello World - SAP Generative AI Hub Connectivity Test

This script verifies that your environment is correctly configured
to connect to SAP Generative AI Hub.

Run with:
    uv run python main.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from the repo root .env file
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Configuration from environment
MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))


def main():
    """Send a simple prompt to SAP Generative AI Hub and print the response."""
    
    print("🔌 Connecting to SAP Generative AI Hub...")
    
    # ==========================================================================
    # EXERCISE: Initialize the LLM and send a prompt
    # ==========================================================================
    # 
    # TODO 1: Import and initialize the LLM
    # Hint: from gen_ai_hub.proxy.langchain.init_models import init_llm
    # Hint: llm = init_llm(MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
    #
    # TODO 2: Send a prompt and get a response
    # Hint: response = llm.invoke("Hello! Please introduce yourself briefly.")
    #
    # TODO 3: Print the response
    # Hint: print(f"Assistant: {response.content}")
    #
    # ==========================================================================
    
    raise NotImplementedError(
        "Exercise: Implement the LLM call. See the hints above!"
    )


if __name__ == "__main__":
    main()
