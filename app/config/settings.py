from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

    ALLOWED_MODEL_NAMES = [
        "qwen/qwen3-32b",
        "qwen/qwen3-72b",
        "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ]

    # Verify API keys are set
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set in environment variables")
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY not set in environment variables")

settings = Settings()

