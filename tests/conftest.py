import hashlib
import os
import re
import subprocess
import unicodedata
from pathlib import Path
from dotenv import load_dotenv
import pytest
from playwright.sync_api import sync_playwright
from pages.forza_page import ForzaPage

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def pytest_sessionfinish(session, exitstatus):
    try:
        # 1. Generar reporte Allure (HTML estático)
        feature_file = os.path.join(os.path.dirname(__file__), "..", "features", "forza.feature")
        feature_name = "reporte"
        try:
            with open(feature_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'Característica:' in line or 'Feature:' in line:
                        feature_name = line.split(':', 1)[1].strip()
                        break
        except:
            pass
        
        # Eliminar acentos y sanitizar nombre
        feature_name_no_accents = unicodedata.normalize('NFKD', feature_name).encode('ascii', 'ignore').decode('ascii')
        safe_name = re.sub(r'[^\w\-_]', '_', feature_name_no_accents)
        
        # Carpeta con nombre del feature
        output_dir = Path(os.path.join(os.path.dirname(__file__), "..", "allure-reports", safe_name))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convertir rutas a formato Windows para cmd.exe
        def to_win(p):
            p_str = str(p)
            if p_str.startswith('/mnt/'):
                drive = p_str[5].upper()
                rest = p_str[6:].replace('/', '\\')
                return f"{drive}:{rest}"
            return p_str.replace('/', '\\')
        
        output_file_win = to_win(output_dir / "report.html")
        results_win = to_win(Path(os.path.join(os.path.dirname(__file__), "..", "allure-results")))
        
        # Generar reporte vía cmd.exe (usa allure de Windows)
        cmd = f'cmd.exe /c "allure generate \"{results_win}\" --single-file -o \"{output_file_win}\" --clean"'
        subprocess.run(cmd, shell=True, check=True)
        print(f"\nReporte Allure generado: {output_file_win}")
        
        # 2. Parsear JUnit XML y generar documentos
        try:
            from reporting.execution_summary_parser import parse_junit_summary
            from reporting.documents_generator import generate_documents
            from integrations.atlassian.confluence_client import publish_execution_to_confluence
            
            junit_xml = Path(os.path.join(os.path.dirname(__file__), "..", "reportes", "junit-results.xml"))
            if junit_xml.exists():
                summary = parse_junit_summary(junit_xml)
                summary["execution_name"] = safe_name
                summary["tests_requested"] = "all"
                summary["allure_report"] = str(output_dir / "report.html")
                summary["base_url"] = os.getenv("BASE_URL", "https://qa.portal.forzadelivery.com/")
                
                # Generar documentos (usa OpenRouter)
                documents_dir = Path(os.path.join(os.path.dirname(__file__), "..", "reportes"))
                documents_dir.mkdir(parents=True, exist_ok=True)
                generated_docs = generate_documents(summary=summary, output_dir=documents_dir)
                
                # Publicar en Confluence si está habilitado
                if os.getenv("ATLASSIAN_SYNC_ENABLED", "false").lower() == "true":
                    zip_path = documents_dir / "evidencias.zip"
                    publish_execution_to_confluence(summary=summary, documents=generated_docs, zip_path=zip_path)
                else:
                    print("\n[Atlassian] Sincronización desactivada. Para activar usar variable ATLASSIAN_SYNC_ENABLED=true")
        except ImportError as e:
            print(f"\nNo se pudieron generar documentos: {e}")
            
    except Exception as e:
        print(f"\nError en pytest_sessionfinish: {e}")


@pytest.fixture
def page(request, base_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge", 
            headless=False,
            args=["--start-maximized"]
        )
    
        context = browser.new_context(
            base_url=base_url,
            no_viewport=True, 
            geolocation={"longitude": -69.9312, "latitude": 18.4861},
            permissions=["geolocation"],
            timezone_id="America/Santo_Domingo",
            locale="es-DO"
        )
    
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
    
        nueva_pagina = context.new_page()
        yield nueva_pagina 
    
        # Cerramos y guardamos trace con nombre único por escenario
        nombre_test = request.node.originalname
        params_hash = hashlib.md5(request.node.name.encode()).hexdigest()[:8]
        trace_path = f"trace_{nombre_test}_{params_hash}.zip"
        context.tracing.stop(path=trace_path)
        browser.close()


# Inyectamos nuestra página al POM
@pytest.fixture
def forza_page(page):
    return ForzaPage(page)
