"""
gemini_client.py
------------------
Small shared helper around the Google Gemini API.

Every feature module (qna, explanation, quiz, summarizer, learning_path)
imports `generate_content()` from here instead of talking to the Gemini
SDK directly. That keeps API-key handling, model selection, and error
handling in exactly one place.
"""

import os
import json
import logging

import google.generativeai as genai

logger = logging.getLogger("edugenie")

_GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

_configured = False
_config_error = None


def _ensure_configured():
    """Configure the Gemini SDK with the API key from the environment.

    Runs once, lazily, the first time a module actually needs to call the
    API. This means the server can still start (and serve the frontend)
    even if the key is missing; the error only surfaces when someone
    actually tries to use an AI feature.
    """
    global _configured, _config_error

    if _configured or _config_error:
        return

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        _config_error = (
            "GEMINI_API_KEY is not set. Create a .env file (see .env.example) "
            "and add your Gemini API key."
        )
        logger.error(_config_error)
        return

    genai.configure(api_key=api_key)
    _configured = True


class GeminiError(Exception):
    """Raised whenever the Gemini API can't be reached or fails."""


def generate_content(prompt: str, expect_json: bool = False, max_output_tokens: int = 1024) -> str:
    """Call Gemini with a single prompt and return the text response.

    Args:
        prompt: The full prompt to send to the model.
        expect_json: If True, asks Gemini to respond in JSON mode so the
            caller can safely json.loads() the result.
        max_output_tokens: Upper bound on the response length.

    Raises:
        GeminiError: on missing API key, network failure, or an empty/
            malformed response from the API. Callers (the FastAPI routes)
            catch this and turn it into a clean HTTP error - the raw
            exception/traceback is never shown to the end user.
    """
    _ensure_configured()

    if _config_error:
        raise GeminiError(_config_error)

    try:
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": max_output_tokens,
        }
        if expect_json:
            generation_config["response_mime_type"] = "application/json"

        model = genai.GenerativeModel(
            model_name=_GEMINI_MODEL_NAME,
            generation_config=generation_config,
        )

        response = model.generate_content(prompt)

        text = getattr(response, "text", None)
        if not text:
            # Model may have refused / returned no candidates.
            raise GeminiError("Gemini returned an empty response.")

        return text.strip()

    except GeminiError:
        raise
    except Exception as exc:  # noqa: BLE001 - we deliberately want a single catch-all
        logger.exception("Gemini API call failed")
        raise GeminiError(f"Gemini API request failed: {exc}") from exc


def safe_json_loads(raw_text: str):
    """Parse JSON out of a Gemini response, tolerating ```json fences.

    Gemini is asked for JSON mode, but some models/SDK versions still wrap
    output in markdown code fences occasionally, so we strip those before
    parsing.
    """
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        # remove a leading "json" language tag if present
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise GeminiError(f"Gemini did not return valid JSON: {exc}") from exc
