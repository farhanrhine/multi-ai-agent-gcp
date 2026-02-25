import sys
import os

# Add project root to path so app module can be imported
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import requests

from app.config.settings import settings
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

# --- Page Config ---
st.set_page_config(
    page_title="Multi AI Agent",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit default header & footer */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 750px;
    }

    /* Header */
    .app-header {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
    }
    .app-header h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin: 0;
    }
    .app-header p {
        color: #6b7280;
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }

    /* Labels */
    .stTextArea label, .stSelectbox label, .stCheckbox label {
        font-weight: 600;
        color: #374151;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    /* Text inputs */
    .stTextArea textarea {
        border: 1.5px solid #e5e7eb;
        border-radius: 10px;
        font-size: 0.95rem;
        padding: 0.75rem;
        transition: border-color 0.2s;
        background: #fafafa;
    }
    .stTextArea textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.1);
    }

    /* Select box */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 1.5px solid #e5e7eb;
        background: #fafafa;
    }

    /* Checkbox */
    .stCheckbox {
        padding: 0.25rem 0;
    }

    /* Button */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        letter-spacing: 0.02em;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(99,102,241,0.4);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* Response container */
    .response-box {
        background: #f8f9fc;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        line-height: 1.7;
        color: #1f2937;
        font-size: 0.95rem;
    }
    .response-box p {
        margin-bottom: 0.8rem;
    }

    /* Divider */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
        margin: 1.5rem 0;
        border: none;
    }

    /* Model badge */
    .model-badge {
        display: inline-block;
        background: #eef2ff;
        color: #6366f1;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #6366f1 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Backend URL ---
BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "9999")
API_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/chat"

logger.info(f"Connecting to backend at: {API_URL}")

# --- Header ---
st.markdown("""
<style>
    .tech-badge {
        display: inline-block;
        background: #f0f0f5;
        color: #555;
        padding: 0.25rem 0.65rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        margin: 0 0.15rem;
        letter-spacing: 0.02em;
    }
</style>
<div class="app-header">
    <h1>🤖 Multi AI Agent</h1>
    <p>
        <span class="tech-badge">⚡ Groq</span>
        <span class="tech-badge">🔍 Tavily</span>
        <span class="tech-badge">� LangChain</span>
        <span class="tech-badge">�🧠 LangGraph</span>
    </p>
</div>
<div class="custom-divider"></div>
""", unsafe_allow_html=True)

# --- Agent Configuration ---
system_prompt = st.text_area(
    "🎯 System Prompt",
    placeholder="e.g. You are a specialized medical research assistant...",
    height=80
)

col1, col2 = st.columns([3, 1])
with col1:
    selected_model = st.selectbox("🧠 Model", settings.ALLOWED_MODEL_NAMES)
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    allow_web_search = st.checkbox("🔍 Web Search", value=False)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# --- Query Input ---
user_query = st.text_area(
    "💬 Your Query",
    placeholder="Ask anything...",
    height=120
)

# --- Submit ---
if st.button("⚡ Ask Agent") and user_query.strip():

    payload = {
        "model_name": selected_model,
        "system_prompt": system_prompt,
        "messages": [user_query],
        "allow_search": allow_web_search
    }

    try:
        logger.info("Sending request to backend")

        with st.spinner("Thinking..."):
            response = requests.post(API_URL, json=payload, timeout=120)

        if response.status_code == 200:
            agent_response = response.json().get("response", "")
            logger.info("Successfully received response from backend")

            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

            st.markdown(
                f'<span class="model-badge">{selected_model}</span>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="response-box">{agent_response}</div>',
                unsafe_allow_html=True
            )
        else:
            logger.error(f"Backend error: {response.status_code}")
            st.error(f"Backend returned error (status {response.status_code})")

    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to backend")
        st.error("Cannot connect to backend. Make sure the API is running on port 9999.")
    except requests.exceptions.Timeout:
        logger.error("Request timed out")
        st.error("Request timed out. The model took too long to respond.")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        st.error(str(CustomException("Failed to communicate with backend")))
