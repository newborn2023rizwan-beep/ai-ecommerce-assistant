"""
llm/ollama_client.py
Low-level wrapper around the Ollama HTTP API.
"""

from __future__ import annotations

import logging
from typing import Generator, Optional

import requests

from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT, STORE_CONTEXT

logger = logging.getLogger(__name__)

# ── Internal helpers ──────────────────────────────────────────────────────────

def _build_payload(
    user_message: str,
    conversation_context: str = "",
    stream: bool = False,
) -> dict:
    """Construct the JSON body for /api/chat."""
    system_prompt = STORE_CONTEXT
    if conversation_context:
        system_prompt += f"\n\nসাম্প্রতিক কথোপকথন:\n{conversation_context}"

    return {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system",  "content": system_prompt},
            {"role": "user",    "content": user_message},
        ],
        "stream": stream,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 512,
        },
    }


# ── Public API ────────────────────────────────────────────────────────────────

def check_ollama_health() -> bool:
    """Return True when Ollama is reachable."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def get_available_models() -> list[str]:
    """Return a list of model names pulled into Ollama."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]
    except requests.RequestException as exc:
        logger.warning("Could not fetch Ollama models: %s", exc)
        return []


def generate_response(
    user_message: str,
    conversation_context: str = "",
) -> str:
    """
    Send *user_message* to Ollama and return the full response text.
    Raises RuntimeError on network/API failure so callers can handle gracefully.
    """
    url     = f"{OLLAMA_BASE_URL}/api/chat"
    payload = _build_payload(user_message, conversation_context, stream=False)

    try:
        resp = requests.post(url, json=payload, timeout=OLLAMA_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]
    except requests.Timeout:
        logger.error("Ollama request timed out after %ss", OLLAMA_TIMEOUT)
        raise RuntimeError("Ollama অনুরোধ সময়সীমা অতিক্রম করেছে। পুনরায় চেষ্টা করুন।")
    except requests.ConnectionError:
        logger.error("Cannot connect to Ollama at %s", OLLAMA_BASE_URL)
        raise RuntimeError(
            f"Ollama সার্ভারে সংযোগ করা যাচ্ছে না ({OLLAMA_BASE_URL})।"
            " Ollama চালু আছে কিনা নিশ্চিত করুন।"
        )
    except (requests.HTTPError, KeyError, ValueError) as exc:
        logger.error("Ollama API error: %s", exc)
        raise RuntimeError(f"Ollama API ত্রুটি: {exc}")


def stream_response(
    user_message: str,
    conversation_context: str = "",
) -> Generator[str, None, None]:
    """
    Yield response tokens one-by-one using Ollama's streaming API.
    Useful for a typing-effect in the UI.
    """
    import json

    url     = f"{OLLAMA_BASE_URL}/api/chat"
    payload = _build_payload(user_message, conversation_context, stream=True)

    try:
        with requests.post(
            url, json=payload, timeout=OLLAMA_TIMEOUT, stream=True
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if chunk.get("done"):
                        break
    except requests.RequestException as exc:
        logger.error("Streaming error: %s", exc)
        yield "\n\n⚠️ সংযোগ বিচ্ছিন্ন হয়েছে।"
