# QAForzaDelivery - Automatización de Pruebas Forza Delivery

Framework de automatización de pruebas E2E para el portal de Forza Delivery usando pytest, Playwright y BDD (Gherkin).

## Stack Tecnológico

- **pytest** - Framework de pruebas
- **pytest-bdd** - Soporte para Gherkin (BDD) en español
- **Playwright** (sync) - Automatización de navegador (MS Edge)
- **Allure** - Reportes visuales de ejecución
- **OpenRouter AI** - Generación de resúmenes ejecutivos y cartas de certificación
- **openpyxl** - Manejo de archivos Excel
- **pyodbc** - Conexión a SQL Server
- **Confluence API** - Publicación opcional de resultados

## Estructura del Proyecto

```
QAForzaDelivery/
├── features/
│   └── forza.feature              # Escenarios BDD en Gherkin (español)
├── pages/
│   └── forza_page.py              # Page Object Model - Todas las acciones del portal
├── tests/
│   ├── conftest.py                # Fixtures de Playwright, hooks de reporteo
│   └── test_forza.py              # Definición de pasos (step definitions)
├── reporting/
│   ├── __init__.py
│   ├── openrouter_client.py       # Cliente para API de OpenRouter (IA)
│   ├── execution_summary_parser.py # Parser de JUnit XML
│   ├── documents_generator.py     # Generador de reportes HTML y cartas
│   ├── documents_generator_insert.py
│   └── documents_generator_original.py
├── integrations/
│   └── atlassian/
│       ├── __init__.py
│       └── confluence_client.py   # Publicador a Confluence
├── pytest.ini                     # Configuración de pytest
└── .gitignore
```

## Características Principales

### Portal Forza - Cobertura de Pruebas
- **Login**: Portal Web, Corporativo, Express Center, App Courier
- **Creación de Guías**: COD, Collet, múltiples direcciones
- **Recolección App Courier**: Visita fallida con evidencia fotográfica y geolocalización
- **Carga masiva**: Procesamiento desde archivos Excel
- **Geolocalización**: Soporta múltiples países (Guatemala, República Dominicana, etc.)

### Configuración de Navegador
- Navegador: MS Edge (no headless, maximizado)
- Geolocalización: Guatemala por defecto
- Locale: `es-GT`
- Tracing siempre activo (screenshots + snapshots + sources)

### Reportes Automáticos
1. **Allure Reports**: HTML estático generado automáticamente tras cada ejecución
2. **JUnit XML**: Generado en `reportes/junit-results.xml`
3. **Documentos con IA**: Resumen ejecutivo y carta de certificación vía OpenRouter
4. **Confluence**: Publicación opcional de resultados

## Cómo Ejecutar las Pruebas

Crear entorno local e instalar dependencias:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest pytest-bdd playwright allure-pytest python-dotenv openpyxl pyodbc requests pytest-base-url
```

Si no existe `.venv`, créalo antes con Python 3.12+:

```powershell
python -m venv .venv
```

Ejecutar solo la automatización de recolección con visita fallida:

```powershell
.\.venv\Scripts\python.exe -m pytest -m recoleccion_visita_fallida -s
```

Ejecutar todos los escenarios:

```powershell
.\.venv\Scripts\python.exe -m pytest -s
```

Markers disponibles:

- `creacionGuias_COD_COLLET` - Flujo de guías COD Collet
- `recoleccion_visita_fallida` - Flujo App Courier de recolección con visita fallida

## Configuración

### pytest.ini
- `base_url`: Placeholder (la URL real viene de la tabla Examples en el .feature)
- `addopts`: `--alluredir=allure-results --junitxml=reportes/junit-results.xml`
- `pythonpath = .` para imports desde la raíz del proyecto

### Variables de Entorno (.env)

```env
SQLSERVER_CONNECTION_STRING=Driver={ODBC Driver 17 for SQL Server};Server=SERVIDOR;Database=BASE;UID=USUARIO;PWD=PASSWORD;
SQLSERVER_QA_CONNECTION_STRING=Driver={ODBC Driver 17 for SQL Server};Server=SERVIDOR;Database=BASE;UID=USUARIO;PWD=PASSWORD;
OPENROUTER_API_KEY=tu_api_key_aqui
ATLASSIAN_SYNC_ENABLED=false
ATLASSIAN_EMAIL=email@dominio.com
ATLASSIAN_API_TOKEN=tu_token
CONFLUENCE_SPACE_KEY=ESPACIO
CONFLUENCE_PARENT_PAGE_ID=123456
```

`OPENROUTER_API_KEY` es opcional. Si no está configurado, se omite la generación de documentos ejecutivos con IA.

### Allure CLI

El proyecto busca Allure local en `tools/allure-2.42.0/bin/allure.bat`. Si no existe, intenta usar `allure` desde el `PATH`.

Para instalar Allure localmente sin subir binarios al repositorio:

```powershell
$version='2.42.0'
$zip='C:\tmp\allure-2.42.0.zip'
$url="https://github.com/allure-framework/allure2/releases/download/$version/allure-$version.zip"
Invoke-WebRequest -Uri $url -OutFile $zip
New-Item -ItemType Directory -Force -Path tools | Out-Null
Expand-Archive -LiteralPath $zip -DestinationPath tools -Force
```

Requiere Java instalado.

## Flujo BDD

El archivo `features/forza.feature` define escenarios parametrizados:

```gherkin
Característica: Creación de Guías en el Portal Forza

Esquema del escenario: Portal Individual Guias COD Collet
Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
Y el usuario selecciona el pais "<pais>"
Y el usuario ingresa el correo "<correo>" y el pass "<pass>"
Y Datos necesarios para crear la guia con origen "<direccionnuevaOrigen>", destino "<direccionnuevaDestino>", tipo "<tipoGuia>", direccion "<NombreDireccion>", collet "<collet>" y tarjeta "<tarjeta>"
Entonces el usuario indica la cantidad de guias a registrar <cantidad_guias>
```

Escenario de recolección con visita fallida:

```gherkin
@recoleccion_visita_fallida
Esquema del escenario: App Courier Recoleccion con Visita Fallida
Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
Y Usuario selecciona el pais courier "<pais>"
Y Usuario abre el portal de forza e ingresa este telefono "<telefono>"
Cuando Usuario abre la recoleccion pendiente en posicion <posicion>
Y Usuario reporta visita fallida con imagen "<ruta_imagen>"
Entonces Usuario valida el mensaje de visita fallida "<mensaje_exitoso>"
```

## Page Object Model

`ForzaPage` en `pages/forza_page.py` contiene todos los métodos de interacción:
- Navegación y validación de títulos
- Login (Web, Corp, Exec, Courier App)
- Creación de guías y tipos de servicio
- Recolección con visita fallida por posición
- Carga de evidencia fotográfica para visita fallida
- Manejo de Excel para carga masiva
- Obtención de tokens desde base de datos

## Reportes Generados

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| Allure Report | `allure-reports/<feature>/report.html` | Reporte visual interactivo |
| JUnit XML | `reportes/junit-results.xml` | Resultados para parsing |
| Evidencias | `reportes/` | Documentos generados por IA |

## Notas Importantes

- La URL base en `pytest.ini` es un placeholder; use la tabla Examples en el `.feature`
- Las cadenas de conexión a BD se leen desde `.env`
- El tracing genera archivos `trace_<testname>_<hash>.zip` con evidencia completa
- Las guías creadas se guardan en archivos `.txt` (ej. `guias_Collet_COD.txt`)
- La imagen fija de visita fallida vive en `data/evidencia_visita.jpg`

## Requisitos

- Python 3.12+
- Playwright con MS Edge instalado
- Allure command-line tool (versión Windows para WSL)
- Variables de entorno configuradas en `.env`

# CoDEGEN
- playwright codegen https://qa.portal.forzadelivery.com/  
- playwright codegen https://qa-pod.forzadeliveryexpress.com/