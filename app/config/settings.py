from dotenv import load_dotenv
import os
from app.common.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

    ALLOWED_MODEL_NAMES = [
        "qwen/qwen3-32b",
        "llama-3.3-70b-versatile",
    ]

    def __init__(self):
        # Verify API keys are set with helpful error messages
        if not self.GROQ_API_KEY:
            error_msg = "GROQ_API_KEY not set in environment variables. Please add it to .env file or set it as an environment variable."
            logger.error(error_msg)
            raise ValueError(error_msg)
        if not self.TAVILY_API_KEY:
            error_msg = "TAVILY_API_KEY not set in environment variables. Please add it to .env file or set it as an environment variable."
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info("All required API keys have been configured successfully.")

settings = Settings()

