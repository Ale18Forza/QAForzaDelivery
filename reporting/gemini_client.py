from __future__ import annotations

import os
from typing import Optional

try:
    from google import genai
    from google.genai import types
    _GOOGLE_AVAILABLE = True
except ImportError:
    _GOOGLE_AVAILABLE = False


def ask_gemini(prompt: str, model: Optional[str] = None) -> str:
    """
    Envía un prompt a Google Gemini y retorna el texto de respuesta.

    Usa GEMINI_API_KEY y GEMINI_MODEL del entorno.

    Límites del plan gratuito:
        - 5 requests por minuto
        - 20 requests por día

    Args:
        prompt: El prompt a enviar al modelo.
        model:  Nombre del modelo. Si no se pasa, lee GEMINI_MODEL del .env.
                Default: "gemini-2.0-flash"

    Returns:
        Texto de respuesta del modelo.

    Raises:
        ImportError:  Si google-genai no está instalado.
        ValueError:   Si falta GEMINI_API_KEY en el entorno.
        RuntimeError: Si la API retorna un error o respuesta inesperada.
    """
    if not _GOOGLE_AVAILABLE:
        raise ImportError(
            "El paquete 'google-genai' no está instalado.\n"
            "Instálalo con:  pip install google-genai"
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "Falta la variable de entorno GEMINI_API_KEY.\n"
            "Obtén tu clave en: https://aistudio.google.com/app/apikey"
        )

    model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=model,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                )
            ],
        )

        text = response.text
        if not text:
            raise RuntimeError("Gemini retornó una respuesta vacía.")

        return text.strip()

    except Exception as e:
        # Re-lanzar como RuntimeError para que el caller lo maneje igual
        # que los errores de OpenRouter
        raise RuntimeError(f"Gemini API error: {e}") from e
