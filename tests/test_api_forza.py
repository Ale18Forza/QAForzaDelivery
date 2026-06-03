"""
test_api_forza.py
=================
Step definitions BDD para los tests de API de Forza Delivery.

Cubre:
  - features/creacion_guia_api.feature
    · @creacion_COD_API          — Guía COD Guatemala
    · @creacion_STD_API_contenedor — Guía STD + contenedor

Cómo ejecutar:
    python -m pytest -m creacion_COD_API -v

"""

import pytest
from pytest_bdd import scenarios, given, parsers

import allure

from api.request_builder import execute_guide_creation, execute_pickup_creation, execute_proof_of_delivery

# Cargar todos los escenarios de los features API
scenarios("../features/creacion_guia_api.feature")
scenarios("../features/ordenes_recoleccion_api.feature")
scenarios("../features/proof_of_delivery_api.feature")


def _scenario_name(request) -> str:
    """
    Extrae un nombre limpio del escenario para usarlo como nombre de carpeta.

    request.node.name        → test_creacion_de_guias_cod[collet-plantilla_COD-...-https://...]
    request.node.originalname→ test_creacion_de_guias_cod
    resultado                → Creacion_de_guias_cod

    Así la carpeta queda como:
        TestResults_Creacion_de_guias_cod
    en lugar de:
        TestResults_test_creacion_de_guias_cod[collet-plantilla_COD_API_GT.json-GetService...]
    """
    name = request.node.originalname          # sin los [parametros]
    name = name.removeprefix("test_")         # quitar prefijo test_
    return name


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def api_context() -> dict:
    """Contexto compartido entre steps del mismo escenario (equivale a ScenarioContext en C#)."""
    return {"templates_ruta": "Request_Plantilla/", "guides": []}


# ==============================================================================
# BACKGROUND
# ==============================================================================

@given(parsers.parse('La ruta de los request API es "{ruta}"'))
def step_set_ruta(ruta: str, api_context: dict) -> None:
    """
    Configura la ruta base de los templates JSON.

    Equivalente a C#: GivenLaRutaDeLosRequestEs()
    """
    api_context["templates_ruta"] = ruta
    allure.dynamic.description(f"Templates dir: {ruta}")


# ==============================================================================
# CREACIÓN DE GUÍAS — step principal
# ==============================================================================

@given("El usuario selecciona el request API con los siguientes datos")
def step_seleccionar_request_api(datatable, api_context: dict, request) -> None:
    """
    Carga el template, reemplaza placeholders, llama al API y valida la respuesta.

    Acepta cualquier combinación de columnas de la tabla:
      Mínimo: request, metodo, staging, CodApp, SecretKey, cantidad, CountPieces, Collected
      Opcional: CrearContenedor, User, Token, IdCustomer, Prefijo, LongitudContainer

    Equivalente a C#: GivenElUsuarioSeleccionaElRequest() → ParseoRequest.requestJson()
    """
    # ── Parsear la DataTable (fila 0 = cabeceras, fila 1 = valores) ───────────
    headers = [cell for cell in datatable[0]]
    values  = [cell for cell in datatable[1]]
    params  = dict(zip(headers, values))

    # ── Nombre del escenario para archivos de resultados ─────────────────────
    scenario_name = _scenario_name(request)   # solo el título, sin [parametros]

    # ── Parámetros de la guía ─────────────────────────────────────────────────
    template_name = params["request"]
    method        = params["metodo"]
    staging       = params["staging"]
    cod_app       = params["CodApp"]
    secret_key    = params["SecretKey"]
    cantidad      = int(params.get("cantidad", 1))

    staging_urls = getattr(request.config, "_staging_urls", [])
    if staging and staging not in staging_urls:
        staging_urls.append(staging)

    # ── Parámetros del contenedor (opcionales) ────────────────────────────────
    crear_contenedor = params.get("CrearContenedor", "false").strip().lower() == "true"
    prefijo           = params.get("Prefijo", "CT")
    longitud          = int(params.get("LongitudContainer", 10))
    user              = params.get("User", "")
    token_cont        = params.get("Token", "")
    id_customer       = params.get("IdCustomer", 0)
    reference_cont    = params.get("ReferenceContainer", "")

    # ── Resto de columnas → placeholders del template ────────────────────────
    # Claves que controlan la ejecución pero NO son placeholders del template JSON.
    # Nota: IdCustomer NO está aquí porque también aparece como {{IdCustomer}}
    # en algunos templates (p.ej. plantilla_STD_API_GT.json).
    skip_keys = {
        "request", "metodo", "staging", "CodApp", "SecretKey", "cantidad",
        "CrearContenedor", "Prefijo", "LongitudContainer",
        "User", "Token", "ReferenceContainer",
        "ejecutarStaging", "Escenario",
    }
    template_params = {k: v for k, v in params.items() if k not in skip_keys}

    with allure.step(f"Creando {cantidad} guía(s) — template: {template_name}"):
        guides = execute_guide_creation(
            template_name=template_name,
            method=method,
            staging=staging,
            cod_app=cod_app,
            secret_key=secret_key,
            cantidad=cantidad,
            scenario_name=scenario_name,
            crear_contenedor=crear_contenedor,
            prefijo=prefijo,
            longitud_container=longitud,
            user=user,
            token=token_cont,
            id_customer=id_customer,
            reference_container=reference_cont,
            **template_params,
        )

    # Guardar en el contexto por si algún step posterior los necesita
    api_context["guides"] = guides

    # Afirmación final de que se crearon las guías esperadas
    assert len(guides) == cantidad, (
        f"Se esperaban {cantidad} guías creadas pero se obtuvieron {len(guides)}"
    )


# ==============================================================================
# ÓRDENES DE RECOLECCIÓN
# ==============================================================================

@given("El usuario crea una orden de recoleccion API")
def step_crear_recoleccion_api(datatable, api_context: dict, request) -> None:
    """
    Crea una orden de recolección vía SetPickupServiceByIntegration.

    Columnas requeridas en la tabla:
        request, metodo, staging, CodApp, SecretKey, CodeOfReference, QuantityOfPieces

    Columnas opcionales (con default en el template):
        StartDate, EndDate, TypeVehicleId
    """
    headers = [cell for cell in datatable[0]]
    values  = [cell for cell in datatable[1]]
    params  = dict(zip(headers, values))

    scenario_name = _scenario_name(request)   # solo el título, sin [parametros]

    # Extraer parámetros de llamada (no son placeholders del template)
    template_name    = params["request"]
    method           = params["metodo"]
    staging          = params["staging"]
    cod_app          = params["CodApp"]
    secret_key       = params["SecretKey"]
    mensaje_esperado = params.get("MensajeEsperado", "")

    staging_urls = getattr(request.config, "_staging_urls", [])
    if staging and staging not in staging_urls:
        staging_urls.append(staging)

    skip_keys = {"request", "metodo", "staging", "CodApp", "SecretKey",
                 "MensajeEsperado", "ejecutarStaging", "Escenario"}
    template_params = {k: v for k, v in params.items() if k not in skip_keys}

    with allure.step(f"Orden de recolección — template: {template_name}"):
        result = execute_pickup_creation(
            template_name=template_name,
            method=method,
            staging=staging,
            cod_app=cod_app,
            secret_key=secret_key,
            scenario_name=scenario_name,
            mensaje_esperado=mensaje_esperado,
            **template_params,
        )

    api_context["pickup"] = result


# ==============================================================================
# PROOF OF DELIVERY
# ==============================================================================

@given("El usuario consulta la evidencia de entrega API")
def step_consultar_proof_of_delivery(datatable, api_context: dict, request) -> None:
    """
    Consulta la evidencia de entrega de una guía vía ProofOfDelivery.

    Columnas requeridas en la tabla:
        request, metodo, staging, CodApp, SecretKey, GuideSerie, GuideNumber

    Columnas opcionales:
        StatusCodeEsperado (default 200), MensajeEsperado
    """
    headers = [cell for cell in datatable[0]]
    values  = [cell for cell in datatable[1]]
    params  = dict(zip(headers, values))

    scenario_name = _scenario_name(request)

    template_name        = params["request"]
    method               = params["metodo"]
    staging              = params["staging"]
    cod_app              = params["CodApp"]
    secret_key           = params["SecretKey"]
    status_code_esperado = int(params.get("StatusCodeEsperado", 200))
    mensaje_esperado     = params.get("MensajeEsperado", "")

    staging_urls = getattr(request.config, "_staging_urls", [])
    if staging and staging not in staging_urls:
        staging_urls.append(staging)

    skip_keys = {"request", "metodo", "staging", "CodApp", "SecretKey",
                 "StatusCodeEsperado", "MensajeEsperado", "ejecutarStaging", "Escenario"}
    template_params = {k: v for k, v in params.items() if k not in skip_keys}

    with allure.step(f"Proof of Delivery — {method}"):
        result = execute_proof_of_delivery(
            template_name=template_name,
            method=method,
            staging=staging,
            cod_app=cod_app,
            secret_key=secret_key,
            scenario_name=scenario_name,
            status_code_esperado=status_code_esperado,
            mensaje_esperado=mensaje_esperado,
            **template_params,
        )

    api_context["proof_of_delivery"] = result
