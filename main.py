import subprocess
import os
import sys
from dotenv import load_dotenv
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

load_dotenv()

# Backend configuration from environment variables
BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = os.getenv("BACKEND_PORT", "9999")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def run_backend():
    try:
        logger.info(f"Starting backend service on {BACKEND_HOST}:{BACKEND_PORT}..")
        subprocess.run(
            ["uvicorn", "app.backend.api:app", "--host", BACKEND_HOST, "--port", BACKEND_PORT],
            check=True,
            cwd=PROJECT_ROOT
        )
    except subprocess.CalledProcessError:
        pass  # Process was terminated
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error("Problem with backend service")
        raise CustomException("Failed to start backend", e)


def main():
    logger.info("Starting Multi AI Agent application...")
    logger.info(f"✨ Single-File App (SFA) is running at: http://{BACKEND_HOST}:{BACKEND_PORT}/")

    # Run backend in the main thread
    try:
        run_backend()
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    finally:
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
