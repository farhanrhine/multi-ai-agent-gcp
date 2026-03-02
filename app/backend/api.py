import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from app.core.ai_agent import get_response_from_ai_agents, stream_response_from_ai_agents
from app.config.settings import settings
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

app = FastAPI(title="MULTI AI AGENT")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "app", "frontend")

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class RequestState(BaseModel):
    model_name: str
    system_prompt: str
    messages: List[str]
    allow_search: bool


@app.get("/")
def serve_frontend():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "Frontend not found"}

@app.get("/health")
def health_check():
    return {"status": "running", "service": "Multi AI Agent API"}

@app.get("/config")
def get_config():
    return {
        "allowed_models": settings.ALLOWED_MODEL_NAMES
    }


@app.post("/chat")
def chat_endpoint(request: RequestState):
    logger.info(f"Received request for model: {request.model_name}")

    if request.model_name not in settings.ALLOWED_MODEL_NAMES:
        logger.warning(f"Invalid model name: {request.model_name}")
        raise HTTPException(status_code=400, detail="Invalid model name")

    try:
        logger.info(f"System prompt: {request.system_prompt}")
        logger.info(f"Allow search: {request.allow_search}")

        response = get_response_from_ai_agents(
            request.model_name,
            request.messages,
            request.allow_search,
            request.system_prompt
        )

        logger.info(f"Successfully got response from AI Agent {request.model_name}")
        return {"response": response}

    except Exception as e:
        logger.error(f"Error during response generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )


@app.post("/chat/stream")
def chat_stream_endpoint(request: RequestState):
    """Stream response token-by-token."""
    logger.info(f"Streaming request for model: {request.model_name}")

    if request.model_name not in settings.ALLOWED_MODEL_NAMES:
        raise HTTPException(status_code=400, detail="Invalid model name")

    def generate():
        for chunk in stream_response_from_ai_agents(
            request.model_name,
            request.messages,
            request.allow_search,
            request.system_prompt
        ):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
