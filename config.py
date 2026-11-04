"""LLM configuration for the starter Job Agent."""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
MODEL = os.getenv("GROQ_MODEL","openai/gpt-oss-120b")


def get_llm():
    """Create the LLM only when needed and provide an actionable config error."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "replace_with_your_new_key":
        raise RuntimeError(
            "GROQ_API_KEY is missing. Copy .env.example to .env and add a NEW Groq API key."
        )
    return ChatGroq(model=MODEL, temperature=0, api_key=api_key)
