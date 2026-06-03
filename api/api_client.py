"""
api_client.py
=============
Cliente REST con firma HMAC-SHA256 para la API de Forza Delivery.

Migrado desde C#: ApiForza/Base/APIClient.cs
  - ProcessLauValue()         → process_lau_value()
  - DecodePayloadResponse()   → decode_payload_response()
  - SendDataToForzaAPI()      → send_data_to_forza_api()

Flujo de una llamada:
  1. Construir payload = {"Method": method, "Params": body}
  2. Serializar a JSON compacto (sin espacios)
  3. Firmar con HMAC-SHA256(payload_bytes, secret_key_bytes) → LauValue (Base64)
  4. Encodear payload_bytes en Base64 → PayLoad
  5. POST  {CodApp, PayLoad}  con header  LauValue
  6. Respuesta: {PayLoad: base64(json_response)} → decodificar
"""

import base64
import hmac
import hashlib
import json
from typing import Any, Optional

import requests
import urllib3

# Equivalente a ServicePointManager.ServerCertificateValidationCallback = _ => true
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class APIClient:
    """
    Cliente HTTP firmado para la API de Forza Delivery Express.

    Todos los métodos son estáticos — sin estado, igual que la clase C# original.
    """

    @staticmethod
    def process_lau_value(request_body: str, secret_key: str) -> tuple[str, str]:
        """
        Firma el cuerpo del request con HMAC-SHA256.

        Args:
            request_body: JSON serializado del payload (sin espacios extras).
            secret_key:   Clave secreta del cliente (CodApp).

        Returns:
            (lau_value_b64, payload_b64)
                lau_value_b64 → va como header "LauValue"
                payload_b64   → va como campo "PayLoad" en el body
        """
        json_bytes = request_body.encode("utf-8")
        key_bytes = secret_key.encode("utf-8")

        signature = hmac.new(key_bytes, json_bytes, hashlib.sha256).digest()

        lau_b64 = base64.b64encode(signature).decode("utf-8")
        payload_b64 = base64.b64encode(json_bytes).decode("utf-8")

        return lau_b64, payload_b64

    @staticmethod
    def decode_payload_response(response_b64: str) -> Optional[str]:
        """
        Decodifica el campo PayLoad de la respuesta del API (Base64 → JSON string).

        Equivalente a C# DecodePayloadResponse().
        """
        try:
            data = base64.b64decode(response_b64)
            return data.decode("utf-8")
        except Exception:
            return None

    @staticmethod
    def send_data_to_forza_api(
        controller: str,
        method: str,
        body: dict,
        staging: str,
        cod_app: str,
        secret_key: str,
        timeout: int = 60,
    ) -> Optional[dict]:
        """
        Envía un POST firmado a la API de Forza Delivery y retorna la respuesta decodificada.

        Equivalente a C# APIClient.SendDataToForzaAPI().

        Estructura del request:
            Header:  LauValue = base64(HMAC-SHA256(payload_json, secret_key))
            Body:    { "CodApp": cod_app, "PayLoad": base64(payload_json) }
            donde payload_json = '{"Method":"...", "Params":{...}}'

        Args:
            controller:  Segmento de URL, p.ej. "Ecommerce" o "Container"
            method:      Nombre del método API, p.ej. "GetServiceByHeaderCodeRequest"
            body:        Dict con los parámetros del request (la guía, dirección, etc.)
            staging:     URL base del ambiente, p.ej. "https://apicore.forzadeliveryexpress.com/"
            cod_app:     Código de la aplicación cliente
            secret_key:  Clave secreta HMAC
            timeout:     Tiempo máximo de espera en segundos

        Returns:
            Dict con la respuesta decodificada, o None si hay error.
        """
        # 1. Construir el inner payload
        payload_obj = {"Method": method, "Params": body}

        # 2. Serializar de forma compacta (igual que Newtonsoft JsonConvert.SerializeObject por defecto)
        payload_str = json.dumps(payload_obj, separators=(",", ":"), ensure_ascii=False)

        # 3. Firmar y encodear
        lau_b64, payload_b64 = APIClient.process_lau_value(payload_str, secret_key)

        # 4. Armar el body del POST
        request_data = {"CodApp": cod_app, "PayLoad": payload_b64}

        # 5. Construir la URL
        url = f"{staging.rstrip('/')}/{controller}/{method}"

        print(f"\n[APIClient] POST → {url}")
        print(f"[APIClient] CodApp: {cod_app}")

        # 6. Enviar — dejamos que las excepciones de red suban al caller para diagnóstico
        response = requests.post(
            url,
            json=request_data,
            headers={
                "LauValue": lau_b64,
                "Content-Type": "application/json",
            },
            verify=False,   # Equivalente a ServerCertificateValidationCallback = true
            timeout=timeout,
        )

        print(f"[APIClient] HTTP Status: {response.status_code}")
        print(f"[APIClient] Raw response (primeros 500 chars): {response.text[:500]}")

        response.raise_for_status()

        # 7. Decodificar la respuesta
        outer = response.json()

        if "PayLoad" not in outer:
            raise ValueError(
                f"La respuesta no contiene campo 'PayLoad'. Respuesta completa: {outer}"
            )

        decoded_str = APIClient.decode_payload_response(outer["PayLoad"])

        if not decoded_str:
            raise ValueError(
                f"No se pudo decodificar el PayLoad base64. Valor recibido: {outer['PayLoad'][:100]}"
            )

        return json.loads(decoded_str)
