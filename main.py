import subprocess
import threading
import time
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
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "8501")

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


def run_frontend():
    try:
        logger.info(f"Starting frontend service on port {FRONTEND_PORT}")
        env = os.environ.copy()
        env['PYTHONPATH'] = PROJECT_ROOT + os.pathsep + env.get('PYTHONPATH', '')
        env['BACKEND_HOST'] = BACKEND_HOST
        env['BACKEND_PORT'] = BACKEND_PORT
        subprocess.run(
            ["streamlit", "run", "app/frontend/ui.py", "--server.port", FRONTEND_PORT],
            check=True,
            cwd=PROJECT_ROOT,
            env=env
        )
    except subprocess.CalledProcessError:
        pass  # Process was terminated
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error("Problem with frontend service")
        raise CustomException("Failed to start frontend", e)


def main():
    logger.info("Starting Multi AI Agent application...")

    # Run backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()

    # Give backend a moment to start
    time.sleep(2)

    # Run frontend in the main thread
    try:
        run_frontend()
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    finally:
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
