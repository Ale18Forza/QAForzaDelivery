from __future__ import annotations

"""
ai_client.py
============
Fachada unificada de proveedores de IA.

Selecciona el proveedor activo según la variable AI_PROVIDER del .env:

    AI_PROVIDER=openrouter   → usa OpenRouter  (default)
    AI_PROVIDER=google       → usa Google Gemini

Esto permite cambiar de proveedor sin tocar el código de generación
de documentos — solo se modifica el .env.

Límites conocidos (plan gratuito):
    - OpenRouter:  depende del modelo elegido (ver openrouter.ai/models)
    - Google:      5 requests/min · 20 requests/día
"""

import os

from reporting.openrouter_client import ask_openrouter
from reporting.gemini_client import ask_gemini

_PROVIDERS = ("openrouter", "google")


def ask_ai(prompt: str) -> str:
    """
    Envía el prompt al proveedor de IA configurado en AI_PROVIDER.

    Args:
        prompt: El prompt a enviar.

    Returns:
        Respuesta de texto del modelo.

    Raises:
        ValueError:   Si AI_PROVIDER tiene un valor desconocido.
        RuntimeError: Si el proveedor devuelve un error.
    """
    provider = os.getenv("AI_PROVIDER", "openrouter").lower().strip()

    if provider == "openrouter":
        return ask_openrouter(prompt)

    if provider == "google":
        return ask_gemini(prompt)

    raise ValueError(
        f"AI_PROVIDER='{provider}' no es válido.\n"
        f"Opciones disponibles: {', '.join(_PROVIDERS)}"
    )
