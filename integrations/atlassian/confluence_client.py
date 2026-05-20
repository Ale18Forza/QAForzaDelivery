from __future__ import annotations

import base64
import html
from datetime import datetime
from pathlib import Path
import os

import requests


def _auth_header(config: dict) -> dict[str, str]:
    token = base64.b64encode(f"{config['email']}:{config['api_token']}".encode("utf-8")).decode("utf-8")
    return {"Authorization": f"Basic {token}", "Accept": "application/json"}


def _validate_config(config: dict) -> None:
    missing = []
    if not config.get("email"):
        missing.append("ATLASSIAN_EMAIL")
    if not config.get("api_token"):
        missing.append("ATLASSIAN_API_TOKEN")
    if not config.get("confluence_space_key"):
        missing.append("CONFLUENCE_SPACE_KEY")
    if not config.get("confluence_parent_page_id"):
        missing.append("CONFLUENCE_PARENT_PAGE_ID")
    if missing:
        raise ValueError("Faltan variables Atlassian: " + ", ".join(missing))


def create_confluence_page(config: dict, title: str, html_body: str) -> str:
    _validate_config(config)

    url = config["base_url"].rstrip("/") + "/wiki/rest/api/content"

    payload = {
        "type": "page",
        "title": title,
        "ancestors": [{"id": config["confluence_parent_page_id"]}],
        "space": {"key": config["confluence_space_key"]},
        "body": {
            "storage": {
                "value": html_body,
                "representation": "storage",
            }
        },
    }

    headers = _auth_header(config) | {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    return response.json()["id"]


def _execution_result(summary: dict) -> str:
    failures = int(summary.get("failures", 0))
    errors = int(summary.get("errors", 0))

    if failures == 0 and errors == 0:
        return "CERTIFICABLE"

    return "NO CERTIFICABLE"


def _build_test_cases_table(summary: dict) -> str:
    test_cases = summary.get("test_cases", [])

    if not test_cases:
        return """
        <p>No se encontraron casos ejecutados en el archivo JUnit de resultados.</p>
        """

    rows = []

    for index, case in enumerate(test_cases, start=1):
        test_name = html.escape(case.get("name", ""))
        status = html.escape(case.get("status", ""))
        duration = html.escape(str(case.get("time", "")))
        message = html.escape(case.get("message", ""))

        if status == "PASSED":
            result_text = "El caso finalizó correctamente según el resultado de Pytest."
        elif status == "FAILED":
            result_text = f"El caso finalizó con fallo. {message}"
        elif status == "ERROR":
            result_text = f"El caso finalizó con error técnico. {message}"
        elif status == "SKIPPED":
            result_text = "El caso fue omitido durante la ejecución."
        else:
            result_text = "Resultado registrado por la ejecución automatizada."

        rows.append(
            f"""
            <tr>
                <td>{index}</td>
                <td>{test_name}</td>
                <td>{status}</td>
                <td>{duration} segundos</td>
                <td>{html.escape(result_text)}</td>
            </tr>
            """
        )

    return f"""
    <table>
        <tbody>
            <tr>
                <th>#</th>
                <th>Test case</th>
                <th>Estado</th>
                <th>Duración</th>
                <th>Resultado</th>
            </tr>
            {''.join(rows)}
        </tbody>
    </table>
    """


def _build_confluence_body(summary: dict, documents: dict[str, Path]) -> str:
    execution_name = html.escape(summary.get("execution_name", "Ejecución QA"))
    tests_requested = html.escape(summary.get("tests_requested", "all"))
    base_url = html.escape(summary.get("base_url", ""))
    allure_report = html.escape(summary.get("allure_report", ""))
    result = _execution_result(summary)

    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    failures = summary.get("failures", 0)
    errors = summary.get("errors", 0)
    skipped = summary.get("skipped", 0)
    duration = summary.get("duration", 0)

    execution_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    table_html = _build_test_cases_table(summary)

    informe_path = documents.get("informe")
    carta_path = documents.get("carta")

    informe_link_text = "Generado correctamente" if informe_path and informe_path.exists() else "No generado"
    carta_link_text = "Generada correctamente" if carta_path and carta_path.exists() else "No generada"

    return f"""
    <h1>Resultado de ejecución automatizada</h1>

    <p><strong>Proyecto:</strong> Forza Delivery - Automatización QA con Python, Playwright, Allure y OpenRouter</p>
    <p><strong>Ejecución:</strong> {execution_name}</p>
    <p><strong>Fecha:</strong> {execution_date}</p>
    <p><strong>Tests solicitados:</strong> {tests_requested}</p>
    <p><strong>Ambiente:</strong> QA</p>
    <p><strong>URL base:</strong> {base_url}</p>
    <p><strong>Resultado general:</strong> {result}</p>

    <p>
        Esta página fue generada automáticamente a partir de la ejecución de pruebas automatizadas.
        Incluye el resumen técnico, resultado general, trazabilidad de casos ejecutados y estado de la documentación generada.
    </p>

    <ul>
        <li><strong>Tests:</strong> {total}</li>
        <li><strong>Passed:</strong> {passed}</li>
        <li><strong>Failed:</strong> {failures}</li>
        <li><strong>Errors:</strong> {errors}</li>
        <li><strong>Skipped:</strong> {skipped}</li>
        <li><strong>Duración total:</strong> {duration} segundos</li>
    </ul>

    <h2>Documentación generada</h2>

    <ul>
        <li><strong>Informe de resultados:</strong> {informe_link_text}</li>
        <li><strong>Carta de certificación:</strong> {carta_link_text}</li>
        <li><strong>Reporte Allure local:</strong> {allure_report}</li>
    </ul>

    <h2>Casos ejecutados</h2>

    {table_html}

    <h2>Observación de cierre</h2>
    <p>
        La ejecución fue procesada por el framework de automatización QA.
        Los resultados fueron consolidados automáticamente y la narrativa documental fue generada con apoyo de OpenRouter.
        Esta publicación no adjunta archivos; únicamente registra el resumen ejecutivo y técnico dentro de Confluence.
    </p>
    """


def publish_execution_to_confluence(summary: dict, documents: dict[str, Path], zip_path: Path | None = None) -> None:
    config = {
        "email": os.getenv("ATLASSIAN_EMAIL"),
        "api_token": os.getenv("ATLASSIAN_API_TOKEN"),
        "base_url": os.getenv("ATLASSIAN_BASE_URL", "https://your-domain.atlassian.net"),
        "confluence_space_key": os.getenv("CONFLUENCE_SPACE_KEY"),
        "confluence_parent_page_id": os.getenv("CONFLUENCE_PARENT_PAGE_ID"),
        "confluence_page_title_prefix": os.getenv("CONFLUENCE_PAGE_TITLE_PREFIX", "QA Forza Delivery"),
    }

    try:
        execution_name = summary.get("execution_name", datetime.now().strftime("%Y%m%d_%H%M%S"))
        title = f"{config['confluence_page_title_prefix']} - {execution_name}"

        page_body = _build_confluence_body(summary=summary, documents=documents)
        page_id = create_confluence_page(config, title, page_body)

        print(f"[Confluence] Página creada correctamente sin adjuntos. Page ID: {page_id}")

    except Exception as exc:
        print(f"[Confluence][WARN] No fue posible publicar en Confluence: {exc}")
