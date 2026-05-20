def _allure_action(summary: dict) -> str:
    allure = str(summary.get("allure_report", "") or "").strip()
    if allure and allure.lower() not in {"no disponible", "n/a", "none", "null"}:
        return f'<a class="action-button primary" href="{escape(allure)}" target="_blank" rel="noopener noreferrer">Abrir reporte Allure</a>'

    return '<span class="action-button disabled">Reporte Allure no disponible</span>'


