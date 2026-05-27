from pytest_bdd import scenarios, given, then, parsers
from dataclasses import dataclass
from pages.forza_page import ForzaPage

# Cargamos el archivo de características (Ajusta la ruta según tu proyecto)
scenarios('../features/portal_creacion_guias_u.feature')
scenarios('../features/recoleccion.feature')

# ==============================================================================
# MODELO DE DATOS
# ==============================================================================
@dataclass
class Direccion:
    direccion_nueva_origen: str
    direccion_nueva_destino: str
    tipo_guia: str
    nombre_direccion: str
    collet: str
    tarjeta: str 

# ==============================================================================
# DEFINICIÓN DE PASOS (Steps)
# 
# ==============================================================================

@given(parsers.parse('el usuario selecciona la url del portal de forza "{url}" y el titulo de la pagina es "{titulo}"'))
def step_seleccionar_url_y_titulo(forza_page: ForzaPage, url: str, titulo: str):
    forza_page.go_to_page_web(url)
    forza_page.assert_title(titulo)

@given(parsers.parse('el usuario selecciona el pais "{pais}"'))
def step_seleccionar_pais(forza_page: ForzaPage, pais: str):
    # Detecta portales de recoleccion (contienen "pod" en la URL)
    if "pod" in forza_page.page.url.lower():
        forza_page.select_country_recoleccion(pais)
    else:
        forza_page.select_country(pais)

@given(parsers.parse('el entorno es "{entorno}"'))
def step_set_entorno(forza_page: ForzaPage, entorno: str):
    forza_page.entorno = entorno

@given(parsers.parse('el usuario ingresa el correo "{usuario}" y el pass "{contrasenia}"'))
def step_ingresar_credenciales(forza_page: ForzaPage, usuario: str, contrasenia: str):
    forza_page.login(usuario, contrasenia)

@given(parsers.parse('el usuario elige el tipo de guia crear {tipo_servicio}'))
def step_elegir_tipo_guia(forza_page: ForzaPage, tipo_servicio: str):
    forza_page.opcion_tipo_servicio(tipo_servicio)

@given(parsers.parse('Datos necesarios para crear la guia con origen "{origen}", destino "{destino}", tipo "{tipo}", direccion "{nombre_dir}", collet "{collet}" y tarjeta "{tarjeta}"'), target_fixture="direccion")
def step_datos_crear_guia(origen: str, destino: str, tipo: str, nombre_dir: str, collet: str, tarjeta: str):
    return Direccion(
        direccion_nueva_origen=origen,
        direccion_nueva_destino=destino,
        tipo_guia=tipo,
        nombre_direccion=nombre_dir,
        collet=collet,
        tarjeta=tarjeta # <--- LO GUARDAMOS EN EL OBJETO
    )

@then(parsers.parse('el usuario indica la cantidad de guias a registrar {cantidad:d}'))
def step_indicar_cantidad_guias(forza_page, cantidad: int, direccion: Direccion):
    forza_page.creacion_guias(cantidad, direccion)

# ==============================================================================
# PASOS CORPORATIVOS (Login Corp / Exec)
# ==============================================================================

@given(parsers.parse('el usuario ingresa el codigo "{codigo}" el usuario "{usuario}" y su pass "{contrasenia}"'))
def step_login_corp(forza_page: ForzaPage, codigo: str, usuario: str, contrasenia: str):
    forza_page.login_corp(codigo, usuario, contrasenia)

@given('el usuario selecciona la opcion pare crear guias')
def step_opcion_crear_guias(forza_page: ForzaPage):
    forza_page.opcion_crear_guias()

@then('el usuario inicia el proceso de creacion de guias')
def step_iniciar_creacion_guias_corp(forza_page: ForzaPage, direccion: Direccion):
    forza_page.crear_guias_corp(direccion)

@given(parsers.parse('el usuario ingresa la estacion "{estacion}" el correo "{correo}" y su pass "{contrasenia}"'))
def step_login_exec(forza_page: ForzaPage, estacion: str, correo: str, contrasenia: str):
    forza_page.login_exec(estacion, correo, contrasenia)

@then('el usuario inicia el proceso de creacion de guias en EXEC')
def step_iniciar_creacion_guias_exec(forza_page: ForzaPage, direccion: Direccion):
    forza_page.crear_guias_exec(direccion)

# ==============================================================================
# PASOS APP COURIER Y EXCEL
# ==============================================================================

@given(parsers.parse('Usuario abre el portal de forza e ingresa este telefono "{telefono}"'))
def step_ingresar_telefono(forza_page: ForzaPage, telefono: str):
    forza_page.login_courier_app(telefono)

@given(parsers.parse('Usuario agrega la ruta del excel "{ruta}"'))
def step_ruta_excel(forza_page: ForzaPage, ruta: str):
    forza_page.ruta_excel_obtener(ruta)

@given(parsers.parse('Usuario selecciona la hoja "{hoja}"'))
def step_seleccionar_hoja(forza_page: ForzaPage, hoja: str):
    forza_page.hoja_excel(hoja)

@given(parsers.parse('Usuario selecciona la columna "{columna}"'))
def step_seleccionar_columna(forza_page: ForzaPage, columna: str):
    forza_page.columna_excel(columna)

@given(parsers.parse('Usuario envia el lote de guias rangoinicial "{inicial}" y rango final "{final}"'))
def step_enviar_lote_guias(forza_page: ForzaPage, inicial: str, final: str):
    rango_inicial = int(inicial)
    rango_final = int(final)
    forza_page.ingresar_a_recoleccion(rango_inicial, rango_final)