from pytest_bdd import scenarios, given, when, then, parsers
from dataclasses import dataclass
import re
import os
from pages.forza_page import ForzaPage

# Cargamos el archivo de características (Ajusta la ruta según tu proyecto)
scenarios('../features/portal_creacion_guias_ui.feature')
scenarios('../features/recoleccion.feature')
scenarios('../features/portal_corporativo_ui.feature')
scenarios('../features/portal_exec_ui.feature')
scenarios('../features/mis_envios_exec.feature')
scenarios('../features/el-Rastreo.feature')
scenarios('../features/entregafallidapod.feature')

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

@dataclass
class Devolucion:
    pais: str
    destino: str
    tipo_guia: str
    tipo_entrega: str
    tipo_cobro: str
    referencia_destino: str
    poblado: str
    nombre_contacto: str
    telefono: str
    direccion_remitente: str

# ==============================================================================
# DEFINICIÓN DE PASOS (Steps)
# 
# ==============================================================================

def resolve_test_value(value: str) -> str:
    value = value or ""
    if value.strip() in ("-", "N/A"):
        return ""
    if value.startswith("ENV:"):
        env_key = value.split(":", 1)[1]
        env_value = os.getenv(env_key)
        if not env_value:
            raise ValueError(f"No se encontró la variable de entorno requerida: {env_key}")
        return env_value
    return value

@given(parsers.parse('el usuario selecciona la url del portal de forza "{url}" y el titulo de la pagina es "{titulo}"'))
def step_seleccionar_url_y_titulo(forza_page: ForzaPage, url: str, titulo: str):
    forza_page.go_to_page_web(url)
    forza_page.assert_title(titulo)

@given(parsers.parse('el usuario selecciona el pais "{pais}"'))
def step_seleccionar_pais(forza_page: ForzaPage, pais: str):
    # Portales tipo courier (qa-pod...) usan select_country_courier
    if "pod" in forza_page.page.url.lower():
        forza_page.select_country_courier(pais)
    else:
        forza_page.select_country(pais)

@given(parsers.parse('usuario selecciona el pais "{pais}"'))
def step_seleccionar_pais_sin_articulo(forza_page: ForzaPage, pais: str):
    step_seleccionar_pais(forza_page, pais)

@given(parsers.parse('el entorno es "{entorno}"'))
def step_set_entorno(forza_page: ForzaPage, entorno: str):
    forza_page.entorno = entorno

@given(parsers.parse('el usuario ingresa el correo "{usuario}" y el pass "{contrasenia}"'))
def step_ingresar_credenciales(forza_page: ForzaPage, usuario: str, contrasenia: str):
    forza_page.login(resolve_test_value(usuario), resolve_test_value(contrasenia))

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
    forza_page.login_corp(resolve_test_value(codigo), resolve_test_value(usuario), resolve_test_value(contrasenia))

@given('el usuario selecciona la opcion pare crear guias')
def step_opcion_crear_guias(forza_page: ForzaPage):
    forza_page.opcion_crear_guias()

@then('el usuario inicia el proceso de creacion de guias')
def step_iniciar_creacion_guias_corp(forza_page: ForzaPage, direccion: Direccion):
    forza_page.crear_guias_corp(direccion)

@given(parsers.parse('el usuario ingresa la estacion "{estacion}" el correo "{correo}" y su pass "{contrasenia}"'))
def step_login_exec(forza_page: ForzaPage, estacion: str, correo: str, contrasenia: str):
    forza_page.login_exec(estacion, correo, contrasenia)

@given(parsers.parse('usuario ingresa la estacion "{estacion}" el correo "{correo}" y su pass "{contrasenia}"'))
def step_login_exec_sin_articulo(forza_page: ForzaPage, estacion: str, correo: str, contrasenia: str):
    step_login_exec(forza_page, estacion, correo, contrasenia)

@given('usuario selecciona la opcion Servicios')
def step_opcion_servicios_exec(forza_page: ForzaPage):
    forza_page.opcion_servicios_exec()

@then('el usuario visualiza el modulo de Servicios')
def step_visualiza_modulo_servicios(forza_page: ForzaPage):
    forza_page.verificar_modulo_servicios_exec()

@given(parsers.parse('el usuario elige la opcion "{opcion}"'))
@then(parsers.parse('el usuario elige la opcion "{opcion}"'))
def step_elegir_opcion_servicio(forza_page: ForzaPage, opcion: str):
    forza_page.seleccionar_opcion_servicio_exec(opcion)

@given(parsers.parse('el usuario ingresa la guia "{guia}" en "{nombre_textbox}"'))
@then(parsers.parse('el usuario ingresa la guia "{guia}" en "{nombre_textbox}"'))
def step_ingresar_guia_recepcion(forza_page: ForzaPage, guia: str, nombre_textbox: str):
    forza_page.ingresar_guia_recepcion_exec(nombre_textbox, guia)

@given(parsers.parse('el usuario hace click en el boton "{nombre_boton}"'))
@then(parsers.parse('el usuario hace click en el boton "{nombre_boton}"'))
def step_click_boton_por_nombre(forza_page: ForzaPage, nombre_boton: str):
    forza_page.click_boton_exec(nombre_boton)

@given(parsers.parse('usuario hace click en boton "{nombre_boton}"'))
@then(parsers.parse('usuario hace click en boton "{nombre_boton}"'))
def step_click_boton_exec_continuar(forza_page: ForzaPage, nombre_boton: str):
    forza_page.click_boton_continuar_exec(nombre_boton)

@given(parsers.parse('el usuario ingresa el nombre de cliente "{nombre_cliente}"'))
@then(parsers.parse('el usuario ingresa el nombre de cliente "{nombre_cliente}"'))
def step_ingresar_nombre_cliente(forza_page: ForzaPage, nombre_cliente: str):
    forza_page.ingresar_nombre_cliente_exec(nombre_cliente)

@given(parsers.parse('el usuario ingresa el DPI "{dpi}"'))
@then(parsers.parse('el usuario ingresa el DPI "{dpi}"'))
def step_ingresar_dpi(forza_page: ForzaPage, dpi: str):
    forza_page.ingresar_dpi_exec(dpi)

@then(parsers.parse('el usuario verifica el link "{nombre_link}"'))
def step_verificar_link_devolucion(forza_page: ForzaPage, nombre_link: str):
    forza_page.verificar_link_servicio_exec(nombre_link)

@then('el usuario verifica Recepcion Exitosa')
def step_verificar_recepcion_exitosa(forza_page: ForzaPage):
    forza_page.verificar_link_recepcion_exec("chevron forward Servicio Recepción")

@then('el usuario verifica Devolucion Exitosa')
def step_verificar_devolucion_exitosa(forza_page: ForzaPage):
    forza_page.verificar_link_devolucion_exec("chevron forward Servicio Devolución")

@then('el usuario inicia el proceso de creacion de guias en EXEC')
def step_iniciar_creacion_guias_exec(forza_page: ForzaPage, direccion: Direccion):
    forza_page.crear_guias_exec(direccion)

@given(parsers.parse('datos corp para crear guia tipo "{tipo_guia}" collet "{collet}"'), target_fixture="direccion")
def step_datos_corp(tipo_guia: str, collet: str):
    return Direccion(
        direccion_nueva_origen="false",
        direccion_nueva_destino="false",
        tipo_guia=tipo_guia,
        nombre_direccion="",
        collet=collet,
        tarjeta="",
    )

@given(parsers.parse('datos para crear devolucion pais "{pais}" destino "{destino}" tipo "{tipo_guia}" entrega "{tipo_entrega}" cobro "{tipo_cobro}" referencia "{referencia_destino}" poblado "{poblado}" nombre "{nombre_contacto}" telefono "{telefono}" direccion "{direccion_remitente}"'), target_fixture="devolucion")
def step_datos_devolucion(pais: str, destino: str, tipo_guia: str, tipo_entrega: str, tipo_cobro: str, referencia_destino: str, poblado: str, nombre_contacto: str, telefono: str, direccion_remitente: str):
    return Devolucion(
        pais=pais,
        destino=destino,
        tipo_guia=tipo_guia,
        tipo_entrega=tipo_entrega,
        tipo_cobro=tipo_cobro,
        referencia_destino=resolve_test_value(referencia_destino),
        poblado=resolve_test_value(poblado),
        nombre_contacto=resolve_test_value(nombre_contacto),
        telefono=resolve_test_value(telefono),
        direccion_remitente=resolve_test_value(direccion_remitente),
    )

@then('el usuario inicia el proceso de servicio de devolucion')
def step_iniciar_servicio_devolucion(forza_page: ForzaPage, devolucion: Devolucion):
    forza_page.crear_guia_devolucion_corp(devolucion)

@then('el usuario valida la guia de devolucion creada en mis envios')
def step_validar_devolucion_mis_envios(forza_page: ForzaPage):
    forza_page.validar_guia_devolucion_en_mis_envios()

@given(parsers.parse('datos exec para crear guia tipo "{tipo_guia}" collet "{collet}"'), target_fixture="direccion")
def step_datos_exec(tipo_guia: str, collet: str):
    return Direccion(
        direccion_nueva_origen="false",
        direccion_nueva_destino="false",
        tipo_guia=tipo_guia,
        nombre_direccion="",
        collet=collet,
        tarjeta="",
    )

# ==============================================================================
# PASOS APP COURIER Y EXCEL
# ==============================================================================

@given(parsers.parse('Usuario abre el portal de forza e ingresa este telefono "{telefono}"'))
def step_ingresar_telefono(forza_page: ForzaPage, telefono: str):
    forza_page.login_courier_app(telefono)

@given(parsers.parse('Usuario selecciona el pais courier "{pais}"'))
def step_seleccionar_pais_courier(forza_page: ForzaPage, pais: str):
    forza_page.select_country_courier(pais)

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

@when(parsers.parse('Usuario abre la recoleccion pendiente en posicion {posicion:d}'))
def step_abrir_recoleccion_por_posicion(forza_page: ForzaPage, posicion: int):
    forza_page.abrir_recoleccion_por_posicion(posicion)

@when(parsers.parse('Usuario reporta visita fallida con imagen "{ruta_imagen}"'))
def step_reportar_visita_fallida(forza_page: ForzaPage, ruta_imagen: str):
    forza_page.reportar_visita_fallida(ruta_imagen)

@then(parsers.parse('Usuario valida el mensaje de visita fallida "{mensaje}"'))
def step_validar_mensaje_visita_fallida(forza_page: ForzaPage, mensaje: str):
    forza_page.validar_mensaje_visita_fallida(mensaje)


# ==============================================================================
# PASOS MIS ENVÍOS - PORTAL EXPRESS CENTER (EXEC)
# ==============================================================================

@then("la pantalla Mis Envíos carga con datos en la tabla")
def step_verificar_mis_envios_cargada(forza_page: ForzaPage):
    forza_page.verificar_mis_envios_cargada()

@when(parsers.parse('el usuario aplica el filtro de estado "{estado}"'))
def step_filtrar_por_estado(forza_page: ForzaPage, estado: str):
    forza_page.filtrar_mis_envios_por_estado(estado)

@then(parsers.parse('la tabla de Mis Envíos refleja el filtro "{estado}"'))
def step_verificar_filtro_estado(forza_page: ForzaPage, estado: str):
    forza_page.verificar_filtro_mis_envios(estado)

@when("el usuario obtiene el numero de la primera guia de Mis Envíos", target_fixture="guia_encontrada")
def step_obtener_primera_guia(forza_page: ForzaPage) -> str:
    return forza_page.obtener_primera_guia_mis_envios()

@when("el usuario busca en Mis Envíos por esa guia")
def step_buscar_por_guia_encontrada(forza_page: ForzaPage, guia_encontrada: str):
    forza_page.buscar_en_mis_envios(guia_encontrada)

@then("la tabla muestra unicamente esa guia en los resultados")
def step_verificar_resultado_busqueda(forza_page: ForzaPage, guia_encontrada: str):
    forza_page.verificar_resultado_busqueda_guia(guia_encontrada)

@when(parsers.parse('el usuario busca en Mis Envíos por texto "{texto}"'))
def step_buscar_por_texto(forza_page: ForzaPage, texto: str):
    forza_page.buscar_en_mis_envios(texto)

@then("la tabla de Mis Envíos no muestra resultados")
def step_verificar_sin_resultados(forza_page: ForzaPage):
    forza_page.verificar_sin_resultados_mis_envios()

@when(parsers.parse('el usuario activa el filtro por fecha y busca desde "{fecha_inicio}" hasta "{fecha_fin}"'))
def step_filtrar_por_fecha(forza_page: ForzaPage, fecha_inicio: str, fecha_fin: str):
    forza_page.filtrar_mis_envios_por_fecha(fecha_inicio, fecha_fin)

@then("la tabla de Mis Envíos se actualiza con el rango de fechas")
def step_verificar_filtro_fecha(forza_page: ForzaPage):
    forza_page.verificar_filtro_fecha_mis_envios()

@then("el usuario puede navegar entre páginas en Mis Envíos")
def step_verificar_paginacion(forza_page: ForzaPage):
    forza_page.verificar_paginacion_mis_envios()

@when("el usuario hace clic en el número de la primera guía de Mis Envíos")
def step_clic_guia_rastreo(forza_page: ForzaPage):
    forza_page.abrir_rastreo_primera_guia_mis_envios()

@then("se abre el rastreo con información de la guía")
def step_verificar_rastreo(forza_page: ForzaPage):
    forza_page.verificar_rastreo_mis_envios()

@then("el botón Generar Excel está visible, habilitado y abre el modal al hacer clic")
def step_verificar_generar_excel(forza_page: ForzaPage):
    forza_page.verificar_boton_generar_excel()
    forza_page.abrir_modal_generar_excel()


# ======================================================================
# PASOS PARA EL FEATURE el-Rastreo
# ======================================================================


@given(parsers.parse('el usuario selecciona la opcion "{opcion}"'))
def step_seleccionar_opcion(forza_page: ForzaPage, opcion: str):
    strategies = [
        ("title", lambda: forza_page.page.get_by_title(opcion)),
        ("text_exact", lambda: forza_page.page.get_by_text(opcion, exact=True)),
        ("text_partial", lambda: forza_page.page.get_by_text(opcion, exact=False)),
        ("role_button", lambda: forza_page.page.get_by_role("button", name=opcion)),
        ("role_link", lambda: forza_page.page.get_by_role("link", name=opcion)),
        ("role_menuitem", lambda: forza_page.page.get_by_role("menuitem", name=opcion)),
    ]

    clicked = False
    for name, fn in strategies:
        try:
            locator = fn()
            if locator.count() > 0:
                locator.first.click(timeout=8000)
                clicked = True
                break
        except Exception:
            continue

    if not clicked:
        raise AssertionError(f"No se pudo encontrar la opción '{opcion}' con las estrategias conocidas")

    forza_page._take_screenshot("opcion_selected")


@given(parsers.parse('el usuario ingresa el numero de guia "{numero_guia}"'))
@when(parsers.parse('el usuario ingresa el numero de guia "{numero_guia}"'))
def step_ingresar_numero_guia(forza_page: ForzaPage, numero_guia: str):
    try:
        input_locator = forza_page.page.get_by_placeholder("Número de guía")
        if input_locator.count() > 0:
            input_locator.fill(numero_guia)
            forza_page._take_screenshot("guia_ingresada")
            return
    except Exception:
        pass

    inputs = forza_page.page.locator("input:not([type='hidden'])")
    if inputs.count() > 0:
        inputs.first.fill(numero_guia)
        forza_page._take_screenshot("guia_ingresada")
        return

    raise AssertionError("No se encontró un campo de entrada para el número de guía")


@then('el usuario hace click en el boton RASTREAR')
def step_click_rastrear(forza_page: ForzaPage):
    try:
        forza_page.page.get_by_role("button", name=re.compile(r"rastrea", re.I)).click(timeout=10000)
    except Exception:
        try:
            forza_page.page.get_by_text("RASTREAR", exact=True).click(timeout=10000)
        except Exception:
            forza_page.page.get_by_text("Rastrear", exact=False).click(timeout=10000)
    forza_page._take_screenshot("click_rastrear")

@then("el botón Reimprimir Guías está deshabilitado inicialmente y se habilita al seleccionar una guía")
def step_verificar_reimprimir_guias(forza_page: ForzaPage):
    forza_page.verificar_boton_reimprimir_guias()


# ==============================================================================
# VISITA FALLIDA (POD)
# ==============================================================================

@when('el usuario selecciona una entrega pendiente')
def step_seleccionar_entrega(forza_page: ForzaPage):
    forza_page.seleccionar_entrega()

@when('el usuario selecciona la opcion visita fallida')
def step_visita_fallida(forza_page: ForzaPage):
    forza_page.visita_fallida()

@when('el usuario selecciona una razon aleatoria de visita fallida')
def step_razon_aleatoria(forza_page: ForzaPage):
    forza_page.seleccionar_razon_aleatoria()

@when('el usuario ingresa un comentario de incidencia')
def step_comentario(forza_page: ForzaPage):
    forza_page.ingresar_comentario_visita()

@when('el usuario adjunta una fotografia')
def step_adjuntar_foto(forza_page: ForzaPage):
    forza_page.adjuntar_fotografia()

@then('el usuario envia la visita fallida exitosamente')
def step_enviar_visita(forza_page: ForzaPage):
    forza_page.enviar_visita_fallida()
