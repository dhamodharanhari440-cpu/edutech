"""
main.py
-------
EduGenie - AI-powered learning assistant.

FastAPI backend that serves the frontend (templates/index.html) and
exposes REST endpoints that call Google's Gemini API through the
modules/ package.

Run with:
    uvicorn main:app --reload

Then open:
    http://127.0.0.1:8000
"""

import logging
import os

from dotenv import load_dotenv

# Load environment variables from .env before anything else touches them.
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from modules.gemini_client import GeminiError
from modules import qna, explanation, quiz, summarizer, learning_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("edugenie")

app = FastAPI(title="EduGenie", description="AI-powered learning assistant", version="1.0.0")

# CORS: locked down to same-origin by default. If you serve the frontend
# from a different origin during development, add it here.
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

MAX_INPUT_LENGTH = 8000  # generous cap to stop absurdly large payloads


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)


class QuizRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)


class ApiResponse(BaseModel):
    success: bool
    result: object = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ---------------------------------------------------------------------------
# Helper for uniform error handling across every AI endpoint
# ---------------------------------------------------------------------------

def _friendly_error_response(exc: Exception, status_code: int = 502) -> JSONResponse:
    """Turn any backend/Gemini failure into a safe, user-friendly JSON error.

    Never leaks stack traces or internal exception details to the client -
    only a short, friendly message. Full details go to the server log.
    """
    logger.error("Request failed: %s", exc)
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "result": None,
            "error": "Unable to generate the response right now. Please try again.",
        },
    )


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.post("/api/qa", response_model=ApiResponse)
async def api_qa(payload: TextRequest):
    question = payload.text.strip()
    if not question:
        return JSONResponse(status_code=400, content={"success": False, "result": None, "error": "Question cannot be empty."})
    try:
        answer = qna.answer_question(question)
        return {"success": True, "result": answer, "error": None}
    except GeminiError as exc:
        return _friendly_error_response(exc)
    except Exception as exc:  # noqa: BLE001
        return _friendly_error_response(exc, status_code=500)


@app.post("/api/explain", response_model=ApiResponse)
async def api_explain(payload: TextRequest):
    topic = payload.text.strip()
    if not topic:
        return JSONResponse(status_code=400, content={"success": False, "result": None, "error": "Topic cannot be empty."})
    try:
        result = explanation.explain_topic(topic)
        return {"success": True, "result": result, "error": None}
    except GeminiError as exc:
        return _friendly_error_response(exc)
    except Exception as exc:  # noqa: BLE001
        return _friendly_error_response(exc, status_code=500)


@app.post("/api/quiz", response_model=ApiResponse)
async def api_quiz(payload: QuizRequest):
    source_text = payload.text.strip()
    if not source_text:
        return JSONResponse(status_code=400, content={"success": False, "result": None, "error": "Please provide a topic or passage."})
    try:
        quiz_data = quiz.generate_quiz(source_text)
        return {"success": True, "result": quiz_data, "error": None}
    except GeminiError as exc:
        return _friendly_error_response(exc)
    except Exception as exc:  # noqa: BLE001
        return _friendly_error_response(exc, status_code=500)


@app.post("/api/summarize", response_model=ApiResponse)
async def api_summarize(payload: TextRequest):
    text = payload.text.strip()
    if not text:
        return JSONResponse(status_code=400, content={"success": False, "result": None, "error": "Please paste some text to summarize."})
    try:
        result = summarizer.summarize_text(text)
        return {"success": True, "result": result, "error": None}
    except GeminiError as exc:
        return _friendly_error_response(exc)
    except Exception as exc:  # noqa: BLE001
        return _friendly_error_response(exc, status_code=500)


@app.post("/api/learn/recommendations", response_model=ApiResponse)
async def api_learning_path(payload: TextRequest):
    topic = payload.text.strip()
    if not topic:
        return JSONResponse(status_code=400, content={"success": False, "result": None, "error": "Please provide a topic."})
    try:
        result = learning_path.generate_learning_path(topic)
        return {"success": True, "result": result, "error": None}
    except GeminiError as exc:
        return _friendly_error_response(exc)
    except Exception as exc:  # noqa: BLE001
        return _friendly_error_response(exc, status_code=500)


# ---------------------------------------------------------------------------
# Fallback handler: never leak a raw traceback to the client for anything
# that slips through the per-route try/except blocks above.
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server error")
    return JSONResponse(
        status_code=500,
        content={"success": False, "result": None, "error": "Something went wrong on our end. Please try again."},
    )
