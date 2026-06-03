from __future__ import annotations

import re
from pathlib import Path


_META_KEYS = {
    "vertical", "producto", "release", "jira",
    "product owner", "qa lead",
}


def parse_feature_metadata(feature_file: Path) -> dict[str, str]:
    """
    Lee el bloque de descripción de un .feature y extrae pares clave: valor.

    Ejemplo en el feature:
        Feature: Creacion de Guias Guatemala API
          Vertical: Delivery
          Producto: Hermes Desktop
          Release: 2.1.0
          Jira: https://...
          Product Owner: Braulio Gomez
          QA Lead: Carlos Gonzalez
    """
    meta: dict[str, str] = {}
    if not feature_file or not Path(feature_file).exists():
        return meta

    in_description = False
    with open(feature_file, encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()

            # Inicio del Feature
            if re.match(r"^(Feature|Característica):", stripped, re.IGNORECASE):
                in_description = True
                continue

            # Salimos del bloque de descripción cuando empieza Background/Scenario/etc.
            if re.match(
                r"^(Background|Scenario|Esquema|@|\s*Given|\s*When|\s*Then|Examples)",
                stripped,
                re.IGNORECASE,
            ):
                break

            if in_description and ":" in stripped:
                key, _, value = stripped.partition(":")
                key_norm = key.strip().lower()
                if key_norm in _META_KEYS:
                    meta[key_norm] = value.strip()

    return meta
