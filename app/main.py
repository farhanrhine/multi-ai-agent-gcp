import subprocess
import threading
import time
import os
import sys
from dotenv import load_dotenv
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger=get_logger(__name__)

load_dotenv()

# Backend configuration from environment variables
BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = os.getenv("BACKEND_PORT", "9999")
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "8501")

def run_backend():
    try:
        logger.info(f"starting backend service on {BACKEND_HOST}:{BACKEND_PORT}..")
        subprocess.run(["uvicorn" , "app.backend.api:app" , "--host" , BACKEND_HOST , "--port" , BACKEND_PORT], check=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    except CustomException as e:
        logger.error("Problem with backend service")
        raise CustomException("Failed to start backend" , e)
    
def run_frontend():
    try:
        logger.info(f"Starting Frontend service on port {FRONTEND_PORT}")
        # Add project root to PYTHONPATH for Streamlit subprocess
        env = os.environ.copy()
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')
        env['BACKEND_HOST'] = BACKEND_HOST
        env['BACKEND_PORT'] = BACKEND_PORT
        subprocess.run(["streamlit" , "run" , "app/frontend/ui.py", "--server.port", FRONTEND_PORT],check=True, cwd=project_root, env=env)
if __name__=="__main__":
    main()


    
