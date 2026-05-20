from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path

from forza_delivery_automation.reporting.ollama_client import ask_ollama


_FORZA_DELIVERY_LOGO_BASE64 = """iVBORw0KGgoAAAANSUhEUgAAAgQAAACMCAYAAAADfrEKAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAFJdSURBVHhe7d13fF11/fjx1zl335u9mqZJmrRJmjYddBe6B6VUBNlDFBRU5CeiTBVFRHECiqjoVxGQLXuPUjro3k2bpjOz2UkzbnLXOfee3x9JrslJ2iY3o0n7eT4en8ejOZ+T29xzx3l/1vsjaZqmIQiCIAjCOU3WHxAEQRAE4dwjAgJBEARBEERAIAiCIAiCCAgEQRAEQRABgSAIgiAIiIBAEARBEAREQCAIgiAIAiIgEARBEAQBERAIgiAIgoAICARBEARBQAQEgiAIgiAgAgJBEARBEBABgSAIgiAIiIBAEARBEAREQCAIgiAIAiIgEARBEAQBQNI0TdMfHI58u1bR+MS39YfPWeZJC4i857ngzy6Xi+eee5YnnvhTp/POJQaDgWXLLuSJJ/6sr+ozTdOCRVF81NTUUlpaQnFxMcePH6eiopzq6hpOnKjD6XTidrvx+Xz4/X40TSMQCAAgyzJGoxGj0YjVaiMszEFkZBTx8XGMHDmSpKRRpKWlkZqaQkJCIna7HVmWkWUZSZL0f1a/e/LJP/Of/zyH0+nUVw0bBoMBs9lMeHg4iYmJZGRkkpOTw9Sp00hLS8NisfT5ejb++Tuo+zegBfz6qnOSedpyHFfejWHEaH3VwAr4aXn9UTxrX0bzefS1ITMkjCbslt9iGjtVXzWsnTUBgXfnJzT96Vv6w+cs86SFRN73fPBnl8vFv/71Tx599A+dzjuXGAwGVqxYwVNP/UNf1WuapqGqKqqq0tTUyOHDh9m1axd79uwmPz+f2tpafD6f/tf6jdFoJCoqijFjxjB58hSmTZvOpEkTiY2Nw2KxYDAYkOX+7wB8/PFHefrpp4d1QHAyJpOJ9PR0li5dxkUXrSArKwubzYbBYNCfelqNj92ML3cdiIAAAMvMlTiuuR9DYrq+akCpx/bQ/OqvUfK36Kv6RLKHY11wHWE3PABS/3/OzpSz55kIwiBQVYXmZieFhYW88cYb/PCHP2Dlyou58cav8thjj7J69WrKy8sHNBgAUFWV2tpatm3bxr/+9U9uv/02Vqy4iG9+82b++c9/kp9/gMbGxgH/O84miqJw+PBhnnrqb9x44w388Id3sm7dWhobG/D7xY192NECKIe24i87oq/pM83lRDm4mUDNcX3VsCYCAkHoAa/XS3V1FevXr+cXv3iIq6++kh/96D4+/PADampqGAodbS0tLWzZsoXf/vbXfOUrl/G9793Oe++9R2lpKS6XS3+6cArNzc188skn3Hnn9/nlLx9m3759uN1u/WnCEBaoK0cp2EvAeUJf1S+0hmq8u1bBEPjs9xcREAjCKSiKQnl5OZ988gn33HMPt9/+XV599VVqamqC4/5DkdfrZd26ddx11w+4+eabePXVVygoKMDj6b9x1HNBY2Mjr732Gvfffy/vvvsOJ06cGBLBn3AamoYvfwtK4b4Bu2H7m+pQ9q0l0Fyvrxq2REAgCN3QNI36+no2btzAww//gh/96D7Wrl0z7FramqZx5MhhHn74F9xxx/f44IP3qaioGNLBzFCjaRr5+fk89tijPPvsM1RUVIigYIjTXE2ohXvRTpTrq/pPwI9SWYRyYJO+ZtgSAYEg6CiKwrFjx3j++f/wwAM/4cMPP6C5uVl/2rDi9/vZty+XBx74CY8++nt2796N1+vVnyacQmVlJc899xzPPPNvysvLRVAwhPmO7kY5tgdNVfRV/SpQX4V392o0T4u+algSAYEgdODxeNi1ayePPvoH/va3v1FaWqo/ZVhzuVy8+eab/PjHP+KTTz6hqalJf4pwCvX1J3j99dd49dVXqK2t0VcLQ4DmdeMv3Iu/4pi+qv8pHvzH81uHJs4CIiAQhDYul4sNGzbwhz/8gY8//giX6+yI+vX8fj8HD+bzyCO/5M033+TEiYGZdHW2qqur4+2332L16tXDbgjpXOCvOIZydBeae3B69QJ15fhy18AA90YMBhEQCEJbz8CGDRv4y1/+zPbt286JMfaKigr+9re/8uabb9DQ0KCvFk6hqKiIN998k337cs+J98pwoflVlGN7UIvz9FUDJtDSiHp0N2pVkb5q2BEBgXDOU1WF7du38X//93d27959To0NV1ZW8PTTT/POO++IZXW9tH37Nj766CNqaqr1VcIZEjhRjlqwh0Bjrb5q4Gga/qoilP1fgDa8g0MREAjnNE3TyMvL49///jc7duw4p4KBdmVlx3nmmadZtepT0drtBb/fz5o1n7N7926RuGgo0DTUov0oR3aEfGOWrHYIIWV1oLEG5dA2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"""


def _brand_logo_data_uri() -> str:
    return f"data:image/png;base64,{_FORZA_DELIVERY_LOGO_BASE64}"


def _status_data(summary: dict) -> dict:
    total = int(summary.get("total", 0))
    failures = int(summary.get("failures", 0))
    errors = int(summary.get("errors", 0))
    skipped = int(summary.get("skipped", 0))

    if total > 0 and failures == 0 and errors == 0:
        return {
            "label": "APROBADO",
            "certification": "CERTIFICABLE",
            "class": "ok",
            "message": "La ejecución finalizó satisfactoriamente y no se identificaron fallos bloqueantes en los escenarios automatizados.",
            "tone": "Ejecución estable",
        }

    if total == 0:
        return {
            "label": "SIN EJECUCIÓN",
            "certification": "NO CERTIFICABLE",
            "class": "warn",
            "message": "No se identificaron casos ejecutados en el resumen técnico disponible. Se requiere validar la salida JUnit/Pytest antes de certificar.",
            "tone": "Sin evidencia suficiente",
        }

    if skipped > 0 and failures == 0 and errors == 0:
        return {
            "label": "APROBADO CON OMISIONES",
            "certification": "CERTIFICABLE CON ALCANCE LIMITADO",
            "class": "warn",
            "message": "La ejecución no presenta fallos, pero existen casos omitidos. La certificación aplica únicamente a los escenarios efectivamente ejecutados.",
            "tone": "Alcance parcial",
        }

    return {
        "label": "CON OBSERVACIONES",
        "certification": "NO CERTIFICABLE",
        "class": "bad",
        "message": "La ejecución presenta fallos o errores que requieren revisión antes de emitir una certificación funcional completa.",
        "tone": "Requiere atención",
    }


def _normalize_status(status: str) -> str:
    value = (status or "").strip().upper()
    if value in {"PASSED", "PASS", "SUCCESS", "OK"}:
        return "PASSED"
    if value in {"SKIPPED", "SKIP", "OMITTED"}:
        return "SKIPPED"
    if value in {"ERROR", "FAILED", "FAILURE", "FAIL"}:
        return value
    return value or "SIN ESTADO"


def _status_class(status: str) -> str:
    value = _normalize_status(status)
    if value == "PASSED":
        return "ok"
    if value == "SKIPPED":
        return "warn"
    return "bad"


def _case_rows(summary: dict) -> str:
    rows = []

    for index, case in enumerate(summary.get("test_cases", []), start=1):
        status = _normalize_status(str(case.get("status", "")))
        status_class = _status_class(status)
        message = escape(str(case.get("message", "")).strip()) or "Sin observaciones registradas."

        rows.append(
            f"""
            <tr>
                <td class="index-cell">{index}</td>
                <td><strong>{escape(str(case.get("name", "")))}</strong></td>
                <td>{escape(str(case.get("classname", "")))}</td>
                <td><span class="status {status_class}">{escape(status)}</span></td>
                <td>{float(case.get("time", 0) or 0):.2f}s</td>
                <td>{message}</td>
            </tr>
            """
        )

    return "\n".join(rows) or """
    <tr>
        <td colspan="6" class="empty">No se encontraron casos en el archivo JUnit XML.</td>
    </tr>
    """


def _compact_test_cases_for_ai(summary: dict) -> list[dict]:
    cases = []
    for index, case in enumerate(summary.get("test_cases", []) or [], start=1):
        cases.append({
            "index": index,
            "name": str(case.get("name", "") or ""),
            "classname": str(case.get("classname", "") or ""),
            "status": _normalize_status(str(case.get("status", "") or "")),
            "time_seconds": float(case.get("time", 0) or 0),
            "message": str(case.get("message", "") or "").strip() or "Sin observaciones registradas.",
        })
    return cases


def _summary_for_ai(summary: dict) -> dict:
    return {
        "execution_name": str(summary.get("execution_name", "") or ""),
        "tests_requested": str(summary.get("tests_requested", "") or ""),
        "base_url": str(summary.get("base_url", "") or ""),
        "total": int(summary.get("total", 0) or 0),
        "passed": int(summary.get("passed", 0) or 0),
        "failures": int(summary.get("failures", 0) or 0),
        "errors": int(summary.get("errors", 0) or 0),
        "skipped": int(summary.get("skipped", 0) or 0),
        "duration_seconds": summary.get("duration", 0),
        "test_cases": _compact_test_cases_for_ai(summary),
    }


def _ai_narrative(summary: dict) -> dict:
    ai_summary = _summary_for_ai(summary)
    prompt = f"""
Actúa como QA Senior Automation y redacta documentación ejecutiva para gerencia, QA y desarrollo.

Reglas obligatorias:
- Usa únicamente el resumen técnico proporcionado.
- No inventes funcionalidades, bancos, módulos, pantallas, flujos ni criterios que no aparezcan en los casos ejecutados.
- La narrativa debe estar basada en los test cases ejecutados dentro de test_cases.
- Si solo existe un test case, redacta todo únicamente sobre ese test case específico.
- Si hay varios test cases, agrupa la lectura ejecutiva solo con base en esos casos.
- No menciones que faltó información, no rellenes con cobertura genérica y no uses frases vagas.
- Mantén tono profesional, ejecutivo, claro, directo y útil para toma de decisión.
- Si hay fallos o errores, indica impacto y necesidad de revisión sin exagerar.
- Si todo aprobó, indica estabilidad del alcance validado sin extender la certificación fuera de los casos ejecutados.

Resumen técnico de ejecución:
{ai_summary}

Devuelve exactamente este formato, sin texto adicional antes ni después:

RESUMEN_EJECUTIVO:
<6 a 8 líneas ejecutivas basadas únicamente en los test cases ejecutados>

CONCLUSION_EJECUTIVA:
<4 a 6 líneas indicando estado general, valor de la automatización y decisión sugerida>

ALCANCE_VALIDADO:
<4 a 6 líneas describiendo únicamente el alcance cubierto por los test cases ejecutados>

CRITERIOS_ACEPTACION:
<lista corta de criterios cubiertos, uno por línea, sin viñetas obligatorias si no aplica>

CARTA_CERTIFICACION:
<6 a 8 líneas formales indicando alcance, ambiente, resultado y límite de certificación>

OBSERVACION_CIERRE:
<3 a 5 líneas ejecutivas de cierre, basadas en el resultado real de la ejecución>
""".strip()

    response = ask_ollama(prompt)
    if not response or not str(response).strip():
        raise RuntimeError("Ollama no devolvió narrativa para la documentación de ejecución.")

    labels = [
        "RESUMEN_EJECUTIVO:",
        "CONCLUSION_EJECUTIVA:",
        "ALCANCE_VALIDADO:",
        "CRITERIOS_ACEPTACION:",
        "CARTA_CERTIFICACION:",
        "OBSERVACION_CIERRE:",
    ]

    missing = [label for label in labels if label not in response]
    if missing:
        raise ValueError(f"La respuesta de Ollama no contiene las secciones requeridas: {', '.join(missing)}")

    def extract(label: str, next_label: str | None = None) -> str:
        start = response.index(label) + len(label)
        end = response.index(next_label) if next_label and next_label in response else len(response)
        value = response[start:end].strip()
        if not value:
            raise ValueError(f"La sección {label} vino vacía desde Ollama.")
        return value

    return {
        "executive_summary": extract("RESUMEN_EJECUTIVO:", "CONCLUSION_EJECUTIVA:"),
        "executive_conclusion": extract("CONCLUSION_EJECUTIVA:", "ALCANCE_VALIDADO:"),
        "validated_scope": extract("ALCANCE_VALIDADO:", "CRITERIOS_ACEPTACION:"),
        "acceptance_criteria": extract("CRITERIOS_ACEPTACION:", "CARTA_CERTIFICACION:"),
        "certificate_narrative": extract("CARTA_CERTIFICACION:", "OBSERVACION_CIERRE:"),
        "closing_observation": extract("OBSERVACION_CIERRE:"),
    }


def _html_paragraph(text: str) -> str:

    return escape(str(text or "")).replace("\n", "<br>")


def _html_list(text: str) -> str:
    raw_items = []
    for line in str(text or "").splitlines():
        item = line.strip()
        item = item.lstrip("-•*0123456789. )")
        if item:
            raw_items.append(item)

    if not raw_items and str(text or "").strip():
        raw_items = [str(text or "").strip()]

    return "\n".join(f"<li>{escape(item)}</li>" for item in raw_items) or "<li>No se recibió detalle de criterios desde Ollama.</li>"


def _maybe_link(value: str, label: str | None = None) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "No disponible"

    safe_raw = escape(raw)
    safe_label = escape(label or raw)

    if raw.startswith(("http://", "https://", "file:///")):
        return f'<a href="{safe_raw}" target="_blank" rel="noopener noreferrer">{safe_label}</a>'

    return safe_raw


def _allure_action(summary: dict) -> str:
    allure = str(summary.get("allure_report", "") or "").strip()
    if allure and allure.lower() not in {"no disponible", "n/a", "none", "null"}:
        return f'<a class="action-button primary" href="{escape(allure)}" target="_blank" rel="noopener noreferrer">Abrir reporte Allure</a>'

    return '<span class="action-button disabled">Reporte Allure no disponible</span>'


def _base_css() -> str:
    return """
    :root {
        --surface: #ffffff;
        --surface-soft: #f7f8fa;
        --surface-strong: #f0f2f5;
        --ink: #101113;
        --ink-soft: #525a64;
        --ink-muted: #737b86;
        --line: #d9dee5;
        --black: #050505;
        --graphite: #2f3a45;
        --graphite-dark: #171b20;
        --orange: #f05a1a;
        --orange-soft: #fff1e9;
        --orange-line: #ffd3bd;
        --green: #16803a;
        --green-soft: #eaf7ee;
        --amber: #b76b00;
        --amber-soft: #fff5df;
        --danger: #b42318;
        --danger-soft: #fff0ee;
        --shadow: 0 24px 60px rgba(0, 0, 0, 0.10);
        --shadow-soft: 0 14px 34px rgba(0, 0, 0, 0.07);
        --radius: 26px;
    }

    * { box-sizing: border-box; }

    body {
        margin: 0;
        font-family: Inter, "Segoe UI", Arial, sans-serif;
        color: var(--ink);
        background:
            radial-gradient(circle at top right, rgba(240, 90, 26, 0.14), transparent 25%),
            linear-gradient(180deg, #f6f7f9 0%, #eceff2 100%);
        line-height: 1.6;
    }

    .page {
        width: min(1320px, calc(100% - 44px));
        margin: 22px auto 38px;
    }

    .topbar {
        height: 14px;
        background: linear-gradient(90deg, var(--orange), var(--black) 30%, var(--graphite-dark) 72%, var(--orange));
        border-radius: 18px 18px 0 0;
    }

    .hero-card {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fb 100%);
        border: 1px solid var(--line);
        border-top: none;
        border-radius: 0 0 var(--radius) var(--radius);
        padding: 28px 30px;
        box-shadow: var(--shadow);
        display: flex;
        justify-content: space-between;
        gap: 24px;
        align-items: center;
    }

    .letter-card { align-items: flex-start; }

    .brand-block {
        display: flex;
        gap: 24px;
        align-items: center;
    }

    .brand-logo {
        width: 250px;
        max-width: 42vw;
        height: auto;
        object-fit: contain;
        border-radius: 18px;
        background: #fff;
        padding: 8px 10px;
        border: 1px solid rgba(217, 222, 229, 0.7);
    }

    .eyebrow {
        margin: 0 0 8px;
        color: var(--orange);
        font-size: 12px;
        font-weight: 900;
        letter-spacing: 0.22em;
        text-transform: uppercase;
    }

    h1 {
        margin: 0;
        font-size: clamp(30px, 4vw, 46px);
        line-height: 1.03;
        color: var(--black);
        letter-spacing: -0.04em;
    }

    h2 {
        margin: 0;
        font-size: 24px;
        color: var(--black);
        letter-spacing: -0.02em;
    }

    h3 {
        margin: 0 0 12px;
        font-size: 18px;
        color: var(--black);
    }

    p {
        margin: 0;
        color: var(--ink-soft);
        line-height: 1.75;
    }

    .lead {
        margin: 14px 0 0;
        max-width: 780px;
        color: var(--ink-soft);
        font-size: 16px;
        line-height: 1.7;
    }

    .hero-side {
        display: flex;
        gap: 12px;
        align-items: center;
        flex-wrap: wrap;
        justify-content: flex-end;
    }

    .seal {
        min-width: 190px;
        text-align: center;
        padding: 18px 20px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 900;
        letter-spacing: 0.16em;
        color: #fff;
        background: var(--graphite-dark);
        box-shadow: var(--shadow-soft);
    }

    .seal.ok { background: linear-gradient(135deg, var(--green), #0f5f29); }
    .seal.warn { background: linear-gradient(135deg, var(--amber), #805000); }
    .seal.bad { background: linear-gradient(135deg, var(--danger), #78170f); }

    .action-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        padding: 14px 18px;
        border-radius: 16px;
        font-weight: 900;
        border: 1px solid transparent;
        white-space: nowrap;
    }

    .action-button.primary {
        background: var(--graphite-dark);
        color: #fff;
    }

    .action-button.primary:hover { background: var(--black); }

    .action-button.disabled {
        background: #edf0f3;
        color: #7a8087;
        border-color: var(--line);
    }

    .stats-grid {
        margin-top: 22px;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
    }

    .card,
    .panel,
    .coverage-card {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 22px;
        box-shadow: var(--shadow);
    }

    .card { padding: 20px; }

    .card-label {
        color: var(--ink-soft);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 8px;
        font-weight: 800;
    }

    .card-value {
        font-size: 32px;
        font-weight: 950;
        color: var(--black);
        margin-bottom: 8px;
        word-break: break-word;
    }

    .card-value.ok { color: var(--green); }
    .card-value.warn { color: var(--amber); }
    .card-value.bad { color: var(--danger); }

    .card-help {
        color: var(--ink-soft);
        font-size: 13px;
        line-height: 1.55;
    }

    .grid.two-up {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 18px;
        margin-top: 18px;
    }

    .section-panel,
    .letter-panel {
        margin-top: 18px;
        padding: 26px;
    }

    .formal-letter {
        max-width: 980px;
        margin-left: auto;
        margin-right: auto;
    }

    .section-head {
        display: flex;
        justify-content: space-between;
        gap: 18px;
        align-items: flex-end;
        margin-bottom: 18px;
    }

    .section-head.compact { margin-bottom: 10px; }

    .section-tag {
        margin: 0 0 6px;
        font-size: 11px;
        font-weight: 900;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--orange);
    }

    .meta-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 14px;
    }

    .meta-item {
        background: var(--surface-soft);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 16px;
    }

    .meta-label {
        color: var(--ink-soft);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 8px;
        font-weight: 800;
    }

    .meta-value {
        color: var(--black);
        font-weight: 750;
        line-height: 1.55;
        word-break: break-word;
    }

    .meta-value a,
    .letter-reference a {
        color: var(--graphite-dark);
        font-weight: 900;
        text-decoration: none;
        border-bottom: 2px solid var(--orange);
    }

    .status {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 8px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 900;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .status.ok { background: var(--green-soft); color: var(--green); }
    .status.warn { background: var(--amber-soft); color: var(--amber); }
    .status.bad { background: var(--danger-soft); color: var(--danger); }

    .table-wrap { overflow-x: auto; }

    table {
        width: 100%;
        border-collapse: collapse;
        min-width: 980px;
    }

    th,
    td {
        padding: 14px 12px;
        border-bottom: 1px solid var(--line);
        text-align: left;
        vertical-align: top;
    }

    th {
        color: var(--ink-soft);
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    td {
        color: var(--black);
        font-size: 14px;
        line-height: 1.65;
    }

    .index-cell {
        color: var(--orange);
        font-weight: 900;
    }

    .empty {
        text-align: center;
        padding: 30px;
        color: var(--ink-soft);
    }

    .chip-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .chip {
        display: inline-flex;
        align-items: center;
        padding: 10px 12px;
        border-radius: 999px;
        background: rgba(47, 58, 69, 0.08);
        color: var(--graphite-dark);
        font-size: 13px;
        font-weight: 800;
        border: 1px solid rgba(47, 58, 69, 0.12);
    }

    .chip.accent {
        background: var(--orange-soft);
        border-color: var(--orange-line);
        color: #b94710;
    }

    .coverage-card { padding: 20px; }

    .mini-kpi {
        padding: 12px 16px;
        background: var(--graphite-dark);
        color: #fff;
        border-radius: 14px;
        font-weight: 900;
    }

    .notes {
        margin: 0;
        padding-left: 18px;
        color: var(--ink-soft);
    }

    .notes li { margin-bottom: 8px; }

    .letter-header-line {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        font-weight: 900;
        color: var(--graphite-dark);
        margin-bottom: 22px;
    }

    .letter-strong {
        color: var(--black);
        font-size: 16px;
    }

    .mini-section {
        margin-top: 18px;
        padding: 18px 20px;
        border-radius: 18px;
        background: var(--surface-soft);
        border: 1px solid var(--line);
    }

    .letter-scope-box {
        border-left: 6px solid var(--orange);
    }

    .letter-list {
        margin: 12px 0 0;
        padding-left: 20px;
        color: var(--ink-soft);
        line-height: 1.7;
    }

    .letter-reference,
    .letter-footnote { margin-top: 16px; }

    .signature-panel {
        margin-top: 22px;
        padding-top: 18px;
        border-top: 2px solid var(--line);
        display: flex;
        gap: 18px;
        align-items: center;
    }

    .signature-mark {
        width: 76px;
        height: 4px;
        border-radius: 999px;
        background: linear-gradient(90deg, var(--orange), var(--graphite-dark));
    }

    .signature-name {
        font-size: 18px;
        font-weight: 950;
        color: var(--black);
    }

    .signature-role,
    .signature-meta {
        color: var(--ink-soft);
        line-height: 1.6;
    }

    footer {
        margin-top: 18px;
        text-align: center;
        color: #6d7680;
        font-size: 12px;
    }

    @media print {
        body { background: white; }
        .page { width: 100%; margin: 0; }
        .card, .panel, .coverage-card, .hero-card { box-shadow: none; }
        .action-button { display: none; }
    }

    @media (max-width: 980px) {
        .page { width: min(100% - 24px, 1320px); }
        .hero-card,
        .brand-block {
            flex-direction: column;
            align-items: flex-start;
        }
        .hero-side { justify-content: flex-start; }
        .grid.two-up { grid-template-columns: 1fr; }
        .letter-header-line { flex-direction: column; }
    }
    """


def _metadata_panel(summary: dict, generated_at: str) -> str:
    return f"""
    <section class="panel section-panel">
        <div class="section-head compact">
            <div>
                <p class="section-tag">Trazabilidad</p>
                <h2>Información de ejecución</h2>
            </div>
        </div>
        <div class="meta-grid">
            <div class="meta-item">
                <div class="meta-label">Ejecución</div>
                <div class="meta-value">{escape(str(summary.get("execution_name", "") or "No especificada"))}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Fecha de generación</div>
                <div class="meta-value">{generated_at}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Ambiente / URL</div>
                <div class="meta-value">{_maybe_link(str(summary.get("base_url", "") or ""))}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Casos solicitados</div>
                <div class="meta-value">{escape(str(summary.get("tests_requested", "") or "No especificados"))}</div>
            </div>
        </div>
    </section>
    """


def _stats_grid(total: int, passed: int, failures: int, errors: int, skipped: int, duration: float | int) -> str:
    return f"""
    <section class="stats-grid">
        <div class="card"><div class="card-label">Total</div><div class="card-value">{total}</div><div class="card-help">Casos procesados</div></div>
        <div class="card"><div class="card-label">Exitosos</div><div class="card-value ok">{passed}</div><div class="card-help">Validaciones correctas</div></div>
        <div class="card"><div class="card-label">Fallos</div><div class="card-value bad">{failures}</div><div class="card-help">Diferencias funcionales</div></div>
        <div class="card"><div class="card-label">Errores</div><div class="card-value bad">{errors}</div><div class="card-help">Errores técnicos</div></div>
        <div class="card"><div class="card-label">Omitidos</div><div class="card-value warn">{skipped}</div><div class="card-help">No ejecutados</div></div>
        <div class="card"><div class="card-label">Duración</div><div class="card-value">{duration}</div><div class="card-help">Segundos registrados</div></div>
    </section>
    """


def _hero(title: str, subtitle: str, status: dict, action: str, letter: bool = False) -> str:
    letter_class = " letter-card" if letter else ""
    return f"""
    <header class="hero-shell">
        <div class="topbar"></div>
        <div class="hero-card{letter_class}">
            <div class="brand-block">
                <img class="brand-logo" src="{_brand_logo_data_uri()}" alt="Forza Delivery Express">
                <div>
                    <p class="eyebrow">QA Automation</p>
                    <h1>{escape(title)}</h1>
                    <p class="lead">{escape(subtitle)}</p>
                </div>
            </div>
            <div class="hero-side">
                <div class="seal {status["class"]}">{escape(status["label"] if not letter else status["certification"])}</div>
                {action}
            </div>
        </div>
    </header>
    """


def generate_documents(summary: dict, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    narrative = _ai_narrative(summary)
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    status = _status_data(summary)

    total = int(summary.get("total", 0) or 0)
    passed = int(summary.get("passed", 0) or 0)
    failures = int(summary.get("failures", 0) or 0)
    errors = int(summary.get("errors", 0) or 0)
    skipped = int(summary.get("skipped", 0) or 0)
    duration = summary.get("duration", 0)

    action = _allure_action(summary)
    stats_grid = _stats_grid(total, passed, failures, errors, skipped, duration)
    metadata_panel = _metadata_panel(summary, generated_at)

    informe = f"""
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe de Resultados QA - Forza Delivery</title>
    <style>{_base_css()}</style>
</head>
<body>
    <main class="page">
        {_hero("Informe de Resultados QA", "Forza Delivery · Validación automatizada con Python, Playwright, Pytest, Allure y OpenRouter.", status, action)}

        {stats_grid}

        <section class="grid two-up">
            <div class="panel section-panel">
                <div class="section-head compact">
                    <div>
                        <p class="section-tag">Resumen</p>
                        <h2>Resumen ejecutivo</h2>
                    </div>
                    <span class="mini-kpi">{escape(status["tone"])}</span>
                </div>
                <p>{_html_paragraph(narrative["executive_summary"])}</p>
                <div class="chip-wrap" style="margin-top:18px;">
                    <span class="chip accent">Selenium</span>
                    <span class="chip accent">Pytest</span>
                    <span class="chip accent">Allure</span>
                    <span class="chip">Ollama / Mistral</span>
                    <span class="chip">QA Evidence</span>
                </div>
            </div>

            <div class="panel section-panel">
                <div class="section-head compact">
                    <div>
                        <p class="section-tag">Resultado</p>
                        <h2>Estado general</h2>
                    </div>
                    <span class="status {status["class"]}">{escape(status["label"])}</span>
                </div>
                <p>{escape(status["message"])}</p>
                <div class="mini-section letter-scope-box">
                    <p><strong>Lectura ejecutiva:</strong> el resultado se determina con base en la salida técnica de la ejecución automatizada y su evidencia asociada.</p>
                </div>
            </div>
        </section>

        {metadata_panel}

        <section class="grid two-up">
            <div class="coverage-card">
                <div class="section-head compact">
                    <div>
                        <p class="section-tag">Cobertura</p>
                        <h2>Alcance validado</h2>
                    </div>
                </div>
                <p>{_html_paragraph(narrative["validated_scope"])}</p>
            </div>
            <div class="coverage-card">
                <div class="section-head compact">
                    <div>
                        <p class="section-tag">Criterios</p>
                        <h2>Criterios de aceptación cubiertos</h2>
                    </div>
                </div>
                <ul class="notes">
                    {_html_list(narrative["acceptance_criteria"])}
                </ul>
            </div>
        </section>

        <section class="panel section-panel">
            <div class="section-head">
                <div>
                    <p class="section-tag">Detalle técnico</p>
                    <h2>Casos ejecutados</h2>
                </div>
                <span class="mini-kpi">{total} caso(s)</span>
            </div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Caso</th>
                            <th>Clase</th>
                            <th>Estado</th>
                            <th>Tiempo</th>
                            <th>Mensaje</th>
                        </tr>
                    </thead>
                    <tbody>
                        {_case_rows(summary)}
                    </tbody>
                </table>
            </div>
        </section>

        <section class="panel section-panel">
            <div class="section-head compact">
                <div>
                    <p class="section-tag">Cierre</p>
                    <h2>Conclusión ejecutiva</h2>
                </div>
            </div>
            <p>{_html_paragraph(narrative["executive_conclusion"])}</p>
        </section>

        <footer>Generado automáticamente el {generated_at}. Forza Delivery QA Automation.</footer>
    </main>
</body>
</html>
"""

    carta = f"""
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carta de Certificación QA - Forza Delivery</title>
    <style>{_base_css()}</style>
</head>
<body>
    <main class="page">
        {_hero("Carta de Certificación QA", "Forza Delivery · Certificación funcional basada en evidencia automatizada.", status, action, letter=True)}

        {stats_grid}

        <section class="panel letter-panel formal-letter">
            <div class="letter-header-line">
                <span>Guatemala, {generated_at}</span>
                <span>Estado: {escape(status["certification"])}</span>
            </div>

            <div class="section-head compact">
                <div>
                    <p class="section-tag">Certificación</p>
                    <h2>Descripción</h2>
                </div>
                <span class="status {status["class"]}">{escape(status["certification"])}</span>
            </div>

            <p class="letter-strong">Por medio de la presente se deja constancia del resultado obtenido durante la ejecución automatizada de pruebas funcionales sobre Forza Delivery.</p>
            <p style="margin-top:12px;">{_html_paragraph(narrative["certificate_narrative"])}</p>

            <div class="mini-section letter-scope-box">
                <h3>Alcance certificado</h3>
                <p>{_html_paragraph(narrative["validated_scope"])}</p>
                <ul class="letter-list">
                    <li>Ambiente validado: {escape(str(summary.get("base_url", "") or "No especificado"))}</li>
                    <li>Ejecución: {escape(str(summary.get("execution_name", "") or "No especificada"))}</li>
                    <li>Casos solicitados: {escape(str(summary.get("tests_requested", "") or "No especificados"))}</li>
                </ul>
            </div>

            <div class="mini-section">
                <h3>Detalle de evidencia</h3>
                <p>
                    La evidencia técnica se encuentra registrada en Allure, incluyendo steps, trazabilidad,
                    screenshots ante fallo y video de ejecución cuando la grabación está habilitada.
                </p>
            </div>

            <div class="mini-section">
                <h3>Observación de cierre</h3>
                <p>{_html_paragraph(narrative["closing_observation"])}</p>
            </div>

            <div class="signature-panel">
                <div class="signature-mark"></div>
                <div>
                    <div class="signature-name">QA Automation</div>
                    <div class="signature-role">Forza Delivery Express</div>
                    <div class="signature-meta">Documento generado automáticamente con evidencia de ejecución.</div>
                </div>
            </div>
        </section>

        {metadata_panel}

        <footer>Generado automáticamente el {generated_at}. Forza Delivery QA Automation.</footer>
    </main>
</body>
</html>
"""

    informe_path = output_dir / "informe-resultados.html"
    carta_path = output_dir / "carta-certificacion.html"

    informe_path.write_text(informe, encoding="utf-8")
    carta_path.write_text(carta, encoding="utf-8")

    return {"informe": informe_path, "carta": carta_path}
