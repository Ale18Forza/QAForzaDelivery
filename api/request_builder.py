"""
request_builder.py
==================
Carga templates JSON, reemplaza placeholders y ejecuta la creación de guías.

Migrado desde C#: ApiForza/Support/ParseoRequest.cs
  - getpath() / setRutaRequest()    → TEMPLATES_DIR constante + load_template()
  - GenerarValorAleatorio()          → _random_amount()
  - requestJson()                    → execute_guide_creation()
  - creacionContenedor()             → (incluido en execute_guide_creation si CrearContenedor=true)
  - GenerarCodigoConPrefijo()        → generate_container_code()

Los templates JSON viven en  QAForzaDelivery/Request_Plantilla/
Los resultados se guardan en  QAForzaDelivery/reportes/api_results/
"""

import json
import random
import re
import string
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import allure

from api.api_client import APIClient

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent          # QAForzaDelivery/
TEMPLATES_DIR = _ROOT / "Request_Plantilla"
RESULTS_DIR = _ROOT / "reportes" / "api_results"


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _strip_json_comments(content: str) -> str:
    """
    Limpia el template para que sea JSON parseable:
      1. Elimina comentarios //  (p.ej. //"IdSettlement": 839)
      2. Elimina comas colgantes antes de } o ]
         (quedan cuando la línea comentada era el último elemento del objeto/array)
    """
    # Paso 1: eliminar comentarios de línea
    content = re.sub(r"//[^\n]*", "", content)
    # Paso 2: trailing commas  →  ej: "IdMerchant": 95019,\n  }  →  ...95019\n  }
    content = re.sub(r",\s*([}\]])", r"\1", content)
    return content


def _random_amount(min_val: int = 31, max_val: int = 3500) -> int:
    """Genera un monto aleatorio para COD. Equivale a C# GenerarValorAleatorio()."""
    return random.randint(min_val, max_val)


def generate_container_code(prefix: str, total_length: int) -> str:
    """
    Genera un código de contenedor como "CT1234567890".

    Equivalente a C# GenerarCodigoConPrefijo().
    """
    if not prefix:
        raise ValueError("El prefijo no puede estar vacío.")
    if total_length <= len(prefix):
        raise ValueError("total_length debe ser mayor que la longitud del prefijo.")
    numeric_length = total_length - len(prefix)
    digits = "".join(random.choices(string.digits, k=numeric_length))
    return prefix + digits


def _append_txt(path: Path, line: str) -> None:
    """Equivalente a C# ManejoArchivo.AppendTXT()."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def _sanitize_name(name: str, max_len: int = 80) -> str:
    """
    Convierte un nombre de escenario pytest en un nombre válido para Windows.

    Problema: request.node.name en Scenario Outline incluye los parámetros:
      test_creacion_de_guias_cod[collet-plantilla_COD.json-...-https://api.com/]
    Esos caracteres  [ ] : / * ? " < > |  son inválidos en rutas de Windows.

    Estrategia:
      1. Reemplazar caracteres problemáticos por guion bajo
      2. Colapsar múltiples __ seguidos
      3. Truncar a max_len para evitar rutas demasiado largas
    """
    sanitized = re.sub(r'[\\/:*?"<>|\[\]]+', "_", name)
    sanitized = re.sub(r"_+", "_", sanitized)   # colapsar ____ → _
    sanitized = sanitized.strip("_. ")
    return sanitized[:max_len]


# ---------------------------------------------------------------------------
# Template loading
# ---------------------------------------------------------------------------

def load_template(template_name: str) -> str:
    """
    Carga un archivo JSON de la carpeta Request_Plantilla como STRING puro,
    eliminando únicamente los comentarios //.

    IMPORTANTE: No parsea el JSON todavía — los templates contienen placeholders
    sin comillas como  "CodeOfReference": {{CodeOfReference}}  que hacen el
    archivo inválido como JSON hasta que los valores sean reemplazados.
    Igual que en C# donde se hace string.Replace() ANTES de JObject.Parse().

    Args:
        template_name: Nombre del archivo, p.ej. "plantilla_COD_API_GT.json"

    Returns:
        Contenido del template como string (con placeholders intactos).
    """
    path = TEMPLATES_DIR / template_name
    if not path.exists():
        raise FileNotFoundError(f"Template no encontrado: {path}")
    content = path.read_text(encoding="utf-8")
    return _strip_json_comments(content)


# ---------------------------------------------------------------------------
# Placeholder replacement
# ---------------------------------------------------------------------------

def replace_placeholders(template_str: str, params: dict) -> dict:
    """
    Reemplaza {{placeholder}} en el string del template y luego parsea el JSON.

    Orden de operaciones (igual que C# ParseoRequest.requestJson):
      1. Reemplazar cada {{key}} con su valor en el string
      2. Eliminar cualquier {{placeholder}} que quede sin reemplazar
      3. json.loads() — en este punto el string ya es JSON válido

    Reglas especiales:
      - AmmountCashOnDelivery = "valor" → número aleatorio entre 31 y 3500
      - Collected              = "true"/"false" string → valor booleano JSON

    Args:
        template_str: String raw del template (salida de load_template).
        params:       Dict con los valores a inyectar.

    Returns:
        Dict Python ya parseado del JSON resultante.
    """
    for key, value in params.items():
        placeholder = f"{{{{{key}}}}}"
        if placeholder not in template_str:
            continue

        if key == "AmmountCashOnDelivery":
            str_val = str(value).strip()
            value_str = str(_random_amount()) if str_val.lower() == "valor" else str_val
        elif key == "Collected":
            value_str = "true" if str(value).lower() in ("true", "1", "yes") else "false"
        elif value is None:
            value_str = ""
        else:
            value_str = str(value)

        template_str = template_str.replace(placeholder, value_str)

    # Limpiar placeholders que quedaron sin reemplazar.
    # Es crítico distinguir contexto para no generar JSON inválido:
    #
    #   "key": "{{placeholder}}"   → "key": ""      (quoted  → empty string)
    #   "key":  {{placeholder}}    → "key":  null   (unquoted → null)
    #
    # Paso 1: placeholders que son el contenido completo de un string JSON → ""
    template_str = re.sub(r'"(\{\{[^}]*\}\})"', '""', template_str)
    # Paso 2: placeholders sin comillas (numéricos/booleanos sin valor) → 0
    # Usamos 0 en lugar de null para coincidir con el comportamiento C# donde los
    # campos int (IdCustomer, CodeOfReference) defaultean a 0 cuando no están en la tabla.
    template_str = re.sub(r"\{\{[^}]*\}\}", "0", template_str)

    return json.loads(template_str)


# ---------------------------------------------------------------------------
# Parcel duplication
# ---------------------------------------------------------------------------

def _duplicate_parcels(payload: dict, count_pieces: int) -> dict:
    """
    Si CountPieces > 1 duplica el arreglo de parcels con pesos aleatorios.

    Equivalente a la lógica de duplicación en C# ParseoRequest.requestJson().
    """
    parcels = payload.get("parcels", [])
    if count_pieces > 1 and len(parcels) == 1:
        base = parcels[0]
        new_parcels = []
        total_weight = 0
        for i in range(count_pieces):
            parcel = dict(base)
            weight = random.randint(1, 5)
            parcel["weight"] = weight
            parcel["ParcelCode"] = f"EXP0{i + 1:02d}"
            total_weight += weight
            new_parcels.append(parcel)
        payload["parcels"] = new_parcels
        payload["TotalWeight"] = total_weight
    return payload


# ---------------------------------------------------------------------------
# Save results
# ---------------------------------------------------------------------------

def _save_guide_result(scenario_name: str, guide: str, url: str = "") -> None:
    """
    Guarda el número de guía y la URL del PDF en archivos .txt.

    Equivalente a C# ManejoArchivo.AppendTXT() para guías creadas.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    clean = scenario_name.replace(" ", "_")
    _append_txt(RESULTS_DIR / f"{clean}.txt", f"{guide} ---> {url}")
    _append_txt(RESULTS_DIR / f"{clean}v2.txt", guide)


def _save_recoleccion_result(service_id: int, code_of_reference: str, message: str) -> None:
    """
    Guarda el número de recolección (ServiceId) en un .txt dedicado.

    Formato del archivo  recolecciones.txt  (en la raíz del proyecto, igual que guias_*.txt):
        13309180 ---> CodeOfReference: 948850 | Solicitud de recolección procesada correctamente

    Formato del archivo  recolecciones_ids.txt  (solo el ServiceId, para uso rápido):
        13309180
    """
    root = _ROOT  # QAForzaDelivery/
    linea_completa = f"{service_id} ---> CodeOfReference: {code_of_reference} | {message}"
    _append_txt(root / "recolecciones.txt", linea_completa)
    _append_txt(root / "recolecciones_ids.txt", str(service_id))


def _log_transaction(tipo: str, modulo: str, contenido: str, scenario_name: str) -> None:
    """
    Guarda request/response en archivo y lo adjunta a Allure.

    Equivalente a C# ParseoRequest.guardarTransaccion().
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    clean = scenario_name.replace(" ", "_")
    filename = RESULTS_DIR / f"TestResults_{clean}" / f"{tipo}_{modulo}_{_timestamp()}.txt"
    filename.parent.mkdir(parents=True, exist_ok=True)
    filename.write_text(contenido, encoding="utf-8")

    # Adjuntar a Allure
    allure.attach(
        contenido,
        name=f"{tipo} — {modulo}",
        attachment_type=allure.attachment_type.JSON
        if contenido.strip().startswith("{")
        else allure.attachment_type.TEXT,
    )


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def execute_guide_creation(
    template_name: str,
    method: str,
    staging: str,
    cod_app: str,
    secret_key: str,
    cantidad: int = 1,
    scenario_name: str = "escenario",
    crear_contenedor: bool = False,
    # Container params (opcionales)
    prefijo: str = "CT",
    longitud_container: int = 10,
    user: str = "",
    token: str = "",
    id_customer: int = 0,
    reference_container: str = "",
    # Extra placeholders que se inyectan en el template
    **params,
) -> list[dict]:
    """
    Flujo completo de creación de guías vía API.

    Equivalente a C# ParseoRequest.requestJson() (+ opcionalmente creacionContenedor()).

    Args:
        template_name:       Nombre del JSON en Request_Plantilla/
        method:              Método del API (p.ej. "GetServiceByHeaderCodeRequest")
        staging:             URL base del ambiente
        cod_app:             Código de la app cliente
        secret_key:          Clave HMAC
        cantidad:            Número de guías a crear (loop)
        scenario_name:       Nombre del escenario (para archivos de resultados)
        crear_contenedor:    Si True, agrupa las guías en un contenedor
        prefijo:             Prefijo del código de contenedor (p.ej. "CT")
        longitud_container:  Longitud total del código de contenedor
        user/token/id_customer/reference_container: Datos del contenedor
        **params:            Resto de placeholders para el template

    Returns:
        Lista de dicts con { tracking, pdf_url, response } por cada guía creada.
    """
    # Sanitizar el nombre del escenario para usarlo como nombre de carpeta/archivo
    # (el node name de pytest en Scenario Outline incluye parámetros con chars inválidos)
    scenario_name = _sanitize_name(scenario_name)

    # Cargar el template como STRING (no como dict) — los placeholders sin comillas
    # como {{CodeOfReference}} hacen el JSON inválido hasta ser reemplazados.
    template_str = load_template(template_name)
    created_guides: list[dict] = []
    guide_list: list[dict] = []  # Para armar el contenedor

    all_params = {**params}

    for i in range(cantidad):
        with allure.step(f"Creando guía {i + 1} de {cantidad}"):
            # Reemplazar placeholders en el string y luego parsear a dict
            payload = replace_placeholders(template_str, all_params)

            # Duplicar parcels si CountPieces > 1
            count_pieces = int(payload.get("CountPieces") or 1)
            if count_pieces > 1:
                payload = _duplicate_parcels(payload, count_pieces)

            # Log del request
            _log_transaction("Request", template_name, json.dumps(payload, indent=2, ensure_ascii=False), scenario_name)

            # Llamada al API — ahora lanza excepción descriptiva en lugar de retornar None
            try:
                response = APIClient.send_data_to_forza_api(
                    "Ecommerce", method, payload, staging, cod_app, secret_key
                )
            except Exception as api_exc:
                error_msg = f"Error al llamar al API:\n  URL: {staging}{method}\n  Detalle: {api_exc}"
                _log_transaction("ERROR", template_name, error_msg, scenario_name)
                raise AssertionError(error_msg) from api_exc

            # Log de la respuesta
            _log_transaction("Response", template_name, json.dumps(response, indent=2, ensure_ascii=False), scenario_name)

            # Validaciones
            assert response is not None, "La respuesta de la API fue nula"
            assert response.get("StatusCode") == 200, (
                f"StatusCode inesperado: {response.get('StatusCode')} "
                f"— {response.get('Description')}"
            )
            assert response.get("ObjectValue"), "ObjectValue vacío en la respuesta"

            tracking: str = response["ObjectValue"][0]["TrackingNumber"]
            pdf_list = response["ObjectValue"][0].get("PDF") or []
            pdf_url: str = pdf_list[0] if pdf_list else ""

            print(f"  ✔ Guía creada: {tracking}")
            print(f"    PDF: {pdf_url}")
            allure.attach(f"Guía: {tracking}\nPDF: {pdf_url}", name=f"Guía {i + 1}", attachment_type=allure.attachment_type.TEXT)

            # Guardar en .txt
            _save_guide_result(scenario_name, tracking, pdf_url)

            # Extraer serie y número para el contenedor
            serie = "".join(c for c in tracking if c.isalpha())
            number_str = "".join(c for c in tracking if c.isdigit())
            guide_list.append({
                "GuideSerie": serie,
                "GuideNumber": int(number_str) if number_str else 0,
                "TicketNumber": "",
            })

            created_guides.append({"tracking": tracking, "pdf_url": pdf_url, "response": response})

    # ---- Contenedor (opcional) ----
    if crear_contenedor and guide_list:
        with allure.step("Creando contenedor con las guías"):
            ref = reference_container or generate_container_code(prefijo, int(longitud_container))
            contenedor_payload = {
                "ReferenceContainer": ref,
                "User": user,
                "Token": token,
                "IdCustomer": int(id_customer) if id_customer else 0,
                "GuideList": guide_list,
            }

            _log_transaction("RequestContenedor", "Contenedor", json.dumps(contenedor_payload, indent=2), scenario_name)

            cont_response = APIClient.send_data_to_forza_api(
                "Container", "SetGuidesContainer", contenedor_payload, staging, cod_app, secret_key
            )

            _log_transaction("ResponseContenedor", "Contenedor", json.dumps(cont_response, indent=2) if cont_response else "None", scenario_name)

            print(f"  ✔ Contenedor creado: {ref}")
            allure.attach(str(cont_response), name="Respuesta Contenedor", attachment_type=allure.attachment_type.TEXT)

    return created_guides


# ---------------------------------------------------------------------------
# Pickup / Recolección
# ---------------------------------------------------------------------------

def execute_pickup_creation(
    template_name: str,
    method: str,
    staging: str,
    cod_app: str,
    secret_key: str,
    scenario_name: str = "recoleccion",
    mensaje_esperado: str = "",
    **params,
) -> dict:
    """
    Crea una orden de recolección vía API SetPickupServiceByIntegration.

    A diferencia de execute_guide_creation, la respuesta tiene ObjectValue como
    objeto simple (no array):
        {
          "StatusCode": 200,
          "ObjectValue": {
              "IdResult": 200,
              "Message": "Solicitud de recolección procesada correctamente",
              "ServiceId": 13309180
          }
        }

    Args:
        template_name:  Archivo JSON en Request_Plantilla/ (ej. plantilla_recoleccion_API.json)
        method:         Nombre del método API (SetPickupServiceByIntegration)
        staging:        URL base del ambiente
        cod_app:        Código de la app cliente
        secret_key:     Clave HMAC
        scenario_name:  Nombre del escenario para logs/archivos
        **params:       Placeholders del template (CodeOfReference, QuantityOfPieces, etc.)

    Returns:
        Dict con { service_id, message, id_result, response }
    """
    scenario_name = _sanitize_name(scenario_name)
    template_str = load_template(template_name)
    payload = replace_placeholders(template_str, params)

    with allure.step(f"Creando orden de recolección — {method}"):
        # Log del request
        _log_transaction("Request", template_name, json.dumps(payload, indent=2, ensure_ascii=False), scenario_name)

        # Llamada al API
        try:
            response = APIClient.send_data_to_forza_api(
                "Ecommerce", method, payload, staging, cod_app, secret_key
            )
        except Exception as api_exc:
            error_msg = f"Error al llamar al API de recolección:\n  Detalle: {api_exc}"
            _log_transaction("ERROR", template_name, error_msg, scenario_name)
            raise AssertionError(error_msg) from api_exc

        # Log de la respuesta
        _log_transaction("Response", template_name, json.dumps(response, indent=2, ensure_ascii=False), scenario_name)

        # Validaciones
        assert response is not None, "La respuesta de la API fue nula"
        assert response.get("StatusCode") == 200, (
            f"StatusCode inesperado: {response.get('StatusCode')} "
            f"— {response.get('Description')}"
        )
        assert response.get("ObjectValue"), "ObjectValue vacío en la respuesta"

        obj = response["ObjectValue"]
        service_id = obj.get("ServiceId")
        message    = obj.get("Message", "")
        id_result  = obj.get("IdResult")

        # Assert del mensaje si se proporcionó uno esperado desde el feature.
        # .strip() en ambos lados para ignorar espacios de relleno que Gherkin
        # agrega al alinear columnas en la tabla de Examples.
        if mensaje_esperado:
            assert message.strip() == mensaje_esperado.strip(), (
                f"Mensaje inesperado en la respuesta.\n"
                f"  Esperado: '{mensaje_esperado.strip()}'\n"
                f"  Recibido: '{message.strip()}'"
            )

        print(f"  ✔ Recolección creada: ServiceId={service_id}")
        print(f"    Mensaje: {message}")

        allure.attach(
            f"ServiceId: {service_id}\nIdResult: {id_result}\nMensaje: {message}",
            name="Orden de Recolección",
            attachment_type=allure.attachment_type.TEXT,
        )

        # Guardar el ServiceId (número de recolección) en archivos dedicados
        code_of_reference = str(params.get("CodeOfReference", ""))
        _save_recoleccion_result(service_id, code_of_reference, message)

    return {"service_id": service_id, "message": message, "id_result": id_result, "response": response}


# ---------------------------------------------------------------------------
# Proof Of Delivery
# ---------------------------------------------------------------------------

def execute_proof_of_delivery(
    template_name: str,
    method: str,
    staging: str,
    cod_app: str,
    secret_key: str,
    scenario_name: str = "proof_of_delivery",
    status_code_esperado: int = 200,
    mensaje_esperado: str = "",
    **params,
) -> dict:
    """
    Consulta la evidencia de entrega de una guía vía API ProofOfDelivery.

    Maneja dos casos:
      - StatusCode 200: éxito, ObjectValue.ProofUrl debe estar presente.
      - StatusCode 409: error esperado, ObjectValue.ProofUrl debe ser null.

    Args:
        template_name:        Archivo JSON en Request_Plantilla/
        method:               Nombre del método API (ProofOfDelivery)
        staging:              URL base del ambiente
        cod_app:              Código de la app cliente
        secret_key:           Clave HMAC
        scenario_name:        Nombre del escenario para logs/archivos
        status_code_esperado: StatusCode que se espera en el JSON de respuesta (200 ó 409)
        mensaje_esperado:     Mensaje esperado en ObjectValue.Message
        **params:             Placeholders del template (GuideSerie, GuideNumber)

    Returns:
        Dict con { status_code, code, message, proof_url, response }
    """
    scenario_name = _sanitize_name(scenario_name)
    template_str = load_template(template_name)
    payload = replace_placeholders(template_str, params)

    with allure.step(f"Consultando evidencia de entrega — {method}"):
        _log_transaction("Request", template_name, json.dumps(payload, indent=2, ensure_ascii=False), scenario_name)

        # ── DEBUG: loguear el request HTTP completo antes de enviarlo ────────
        # Descomentar para diagnosticar problemas de URL/firma/payload
        # inner_payload_obj = {"Method": method, "Params": payload}
        # inner_payload_str = json.dumps(inner_payload_obj, separators=(",", ":"), ensure_ascii=False)
        # lau_b64, payload_b64 = APIClient.process_lau_value(inner_payload_str, secret_key)
        # url_debug = f"{staging.rstrip('/')}/Ecommerce/{method}"
        # debug_info = (
        #     f"=== REQUEST HTTP DEBUG ===\n"
        #     f"URL       : {url_debug}\n"
        #     f"LauValue  : {lau_b64}\n"
        #     f"CodApp    : {cod_app}\n"
        #     f"PayLoad   : {payload_b64}\n\n"
        #     f"=== INNER PAYLOAD (decoded) ===\n"
        #     f"{json.dumps(inner_payload_obj, indent=2, ensure_ascii=False)}"
        # )
        # print(f"\n{debug_info}")
        # _log_transaction("DEBUG_Request_HTTP", template_name, debug_info, scenario_name)
        # ─────────────────────────────────────────────────────────────────────

        try:
            response = APIClient.send_data_to_forza_api(
                "Ecommerce", method, payload, staging, cod_app, secret_key
            )
        except Exception as api_exc:
            error_msg = f"Error al llamar al API ProofOfDelivery:\n  Detalle: {api_exc}"
            _log_transaction("ERROR", template_name, error_msg, scenario_name)
            raise AssertionError(error_msg) from api_exc

        _log_transaction("Response", template_name, json.dumps(response, indent=2, ensure_ascii=False), scenario_name)

        assert response is not None, "La respuesta de la API fue nula"

        actual_status_code = response.get("StatusCode")
        # El API siempre retorna StatusCode 200 en el envelope exterior, incluso
        # cuando no encuentra evidencia. El error se codifica dentro de ObjectValue.
        assert actual_status_code == 200, (
            f"StatusCode HTTP inesperado: {actual_status_code}\n"
            f"Description: {response.get('Description')}"
        )

        obj = response.get("ObjectValue", {}) or {}
        code      = obj.get("Code")
        message   = obj.get("Message", "")
        proof_url = obj.get("ProofUrl") or ""  # normalizar None y "" al mismo valor

        if mensaje_esperado:
            assert message.strip() == mensaje_esperado.strip(), (
                f"Mensaje inesperado en la respuesta.\n"
                f"  Esperado: '{mensaje_esperado.strip()}'\n"
                f"  Recibido: '{message.strip()}'"
            )

        # status_code_esperado se usa como flag: 200 = esperar ProofUrl, otro = esperar vacío
        if status_code_esperado == 200:
            #assert proof_url, "ProofUrl está vacío en la respuesta exitosa"
            print(f"  ✔ ProofUrl obtenido: {proof_url}")
        else:
            assert not proof_url, f"ProofUrl debería estar vacío en error, pero fue: {proof_url}"
            print(f"  ✔ Sin evidencia (esperado): {message}")

        allure.attach(
            f"StatusCode: {actual_status_code}\nCode: {code}\nMensaje: {message}\nProofUrl: {proof_url}",
            name="Proof Of Delivery",
            attachment_type=allure.attachment_type.TEXT,
        )

    return {"status_code": actual_status_code, "code": code, "message": message, "proof_url": proof_url, "response": response}
