from __future__ import annotations

import os
import requests
from typing import Optional


_DEFAULT_MODEL = "meta-llama/llama-3.1-8b-instruct:free"


def ask_openrouter(prompt: str, model: str | None = None) -> str:
    """
    Sends a prompt to OpenRouter and returns the response.
    Uses OPENROUTER_API_KEY from environment.
    Model priority: argument > OPENROUTER_MODEL env var > default free model.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENROUTER_API_KEY environment variable")

    model = model or os.getenv("OPENROUTER_MODEL", _DEFAULT_MODEL)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 2048,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"OpenRouter API error: {e}")
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected OpenRouter response format: {e}")
