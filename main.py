import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import main as app_main

if __name__ == "__main__":
    app_main()
