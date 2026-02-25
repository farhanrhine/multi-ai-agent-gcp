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

def run_backend():
    try:
        logger.info("starting backend service..")
        subprocess.run(["uvicorn" , "app.backend.api:app" , "--host" , "127.0.0.1" , "--port" , "9999"], check=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    except CustomException as e:
        logger.error("Problem with backend service")
        raise CustomException("Failed to start backend" , e)
    
def run_frontend():
    try:
        logger.info("Starting Frontend service")
        # Add project root to PYTHONPATH for Streamlit subprocess
        env = os.environ.copy()
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')
        subprocess.run(["streamlit" , "run" , "app/frontend/ui.py"],check=True, cwd=project_root, env=env)
    except CustomException as e:
        logger.error("Problem with frontend service")
        raise CustomException("Failed to start frontend" , e)

def main():
    try:
        threading.Thread(target=run_backend).start()
        time.sleep(2)
        run_frontend()
    
    except CustomException as e:
        logger.exception(f"CustomException occured : {str(e)}")

if __name__=="__main__":
    main()


    
