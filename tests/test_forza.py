from pytest_bdd import scenarios, given, when, then, parsers
from dataclasses import dataclass
import random
import re
from pages.forza_page import ForzaPage

# Cargamos el archivo de características (Ajusta la ruta según tu proyecto)
scenarios('../features/forza.feature')
scenarios('../features/recoleccion.feature')
scenarios('../features/entregafallidapod.feature')
scenarios('../features/recoleccionensitioexitosa.feature')
scenarios('../features/servicioentregaexc.feature')
scenarios('../features/exccreaciondeguias.feature')

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


# ==============================================================================
# VISITA FALLIDA
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

# ==============================================================================
# RECOLECCION EN SITIO
# ==============================================================================

@when('el usuario selecciona el boton de recoleccion en sitio')
def step_recoleccion_sitio(
    forza_page: ForzaPage
    ):
    forza_page.seleccionar_recoleccion_sitio()


@when('el usuario carga una guia pendiente de recoleccion')
def step_cargar_guia(
    forza_page: ForzaPage
    ):
    forza_page.ingresar_guia_recoleccion()


@when('el usuario agrega la guia al lote')
def step_agregar_guia(
    forza_page: ForzaPage
    ):
    forza_page.agregar_guia_lote()


@when('el usuario presiona el boton siguiente')
def step_siguiente(
    forza_page: ForzaPage
    ):
    forza_page.presionar_siguiente_recoleccion()


@when('el usuario completa la firma del cliente')
def step_firma(
    forza_page: ForzaPage
    ):
    forza_page.completar_firma_cliente()


@when('el usuario finaliza la recoleccion')
def step_finalizar(
    forza_page: ForzaPage
    ):
    forza_page.finalizar_recoleccion()


@then('el sistema registra la recoleccion exitosamente')
def step_validar_exito(
    forza_page: ForzaPage
    ):
    forza_page.validar_recoleccion_exitosa()

# ==============================================================================
# SERVICIO ENTREGA EXEC
# ==============================================================================

@when('el usuario selecciona la opcion servicios')
def step_servicios(forza_page: ForzaPage):
    forza_page.seleccionar_servicios()


@when('el usuario selecciona la opcion servicio entrega')
def step_servicio_entrega(forza_page: ForzaPage):
    forza_page.seleccionar_servicio_entrega()


@when(parsers.parse('el usuario carga una guia "{guia}" pendiente de entrega'))
def step_guia_entrega(forza_page: ForzaPage, guia: str):
    forza_page.ingresar_guia_entrega(guia)


@when('el usuario presiona el boton agregar')
def step_agregar_guia(forza_page: ForzaPage):
    forza_page.agregar_guia_entrega()


@when('el usuario presiona el boton continuar')
def step_continuar(forza_page: ForzaPage):
    forza_page.continuar_entrega()


@when(parsers.parse('el usuario ingresa el nombre del cliente "{nombre_cliente}"'))
def step_nombre_cliente(forza_page: ForzaPage, nombre_cliente: str):
    forza_page.ingresar_nombre_cliente(nombre_cliente)


@when(parsers.parse('el usuario ingresa el dpi "{dpi}"'))
def step_dpi(forza_page: ForzaPage, dpi: str):
    forza_page.ingresar_dpi(dpi)


@when(parsers.parse('el usuario ingresa el nit "{nit}"'))
def step_nit(forza_page: ForzaPage, nit: str):
    forza_page.ingresar_nit(nit)


@when(parsers.parse('el usuario ingresa el nombre "{nombre}"'))
def step_nombre(forza_page: ForzaPage, nombre: str):
    forza_page.ingresar_nombre(nombre)


@when(parsers.parse('el usuario ingresa la direccion "{direccion}"'))
def step_direccion(forza_page: ForzaPage, direccion: str):
    forza_page.ingresar_direccion(direccion)


@when(parsers.parse('el usuario ingresa el correo electronico del cliente "{correo}"'))
def step_correo(forza_page: ForzaPage, correo: str):
    forza_page.ingresar_correo(correo)


@when('el usuario finaliza la entrega')
def step_finalizar_entrega(forza_page: ForzaPage):
    forza_page.finalizar_entrega()


@then('el sistema registra la entrega completada exitosamente')
def step_validar_entrega(forza_page: ForzaPage):
    forza_page.validar_entrega_exitosa()


# ==============================================================================
# FLUJO [STD] - CREACIÓN DE GUÍAS EXPRESS CENTER
# Step definitions for Express Center guide creation
# ==============================================================================

@when('el usuario selecciona la opción Crear Guías')
def step_seleccionar_crear_guias(forza_page: ForzaPage):
    """[STD] Selecciona Crear Guías"""
    forza_page.seleccionar_crear_guias_exc()


@when(parsers.parse('el usuario selecciona el poblado "{Poblado}"'))
def step_seleccionar_poblado(forza_page: ForzaPage, Poblado: str):
    """[STD] Selecciona poblado"""
    forza_page.seleccionar_poblado_exc(Poblado)


@when(parsers.parse('el usuario selecciona "{CantidadPaquetes}" paquete'))
def step_seleccionar_cantidad_paquetes(forza_page: ForzaPage, CantidadPaquetes: str):
    """[STD] Selecciona cantidad de paquetes"""
    forza_page.seleccionar_cantidad_paquetes_std(CantidadPaquetes)


@when('el usuario presiona el botón Calcular')
def step_presionar_calcular(forza_page: ForzaPage):
    """[STD] Presiona botón Calcular"""
    forza_page.presionar_calcular_exc()


@when('el usuario presiona el botón Seleccionar para confirmar el servicio')
def step_presionar_seleccionar(forza_page: ForzaPage):
    """[STD] Presiona botón Seleccionar"""
    forza_page.presionar_seleccionar_exc()


@when(parsers.parse('el usuario ingresa el nombre remitente "{NombreRemitente}"'))
def step_ingresar_nombre_remitente(forza_page: ForzaPage, NombreRemitente: str):
    """[STD] Ingresa nombre remitente"""
    forza_page.ingresar_nombre_remitente_exc(NombreRemitente)


@when(parsers.parse('el usuario ingresa el teléfono remitente "{TelefonoRemitente}"'))
def step_ingresar_telefono_remitente(forza_page: ForzaPage, TelefonoRemitente: str):
    """[STD] Ingresa teléfono remitente"""
    forza_page.ingresar_telefono_remitente_exc(TelefonoRemitente)


@when(parsers.parse('el usuario ingresa el correo remitente "{CorreoRemitente}"'))
def step_ingresar_correo_remitente(forza_page: ForzaPage, CorreoRemitente: str):
    """[STD] Ingresa correo remitente"""
    forza_page.ingresar_correo_remitente_exc(CorreoRemitente)


@when(parsers.parse('el usuario selecciona el tipo de destinatario "{TipoDestinatario}"'))
def step_seleccionar_tipo_destinatario(forza_page: ForzaPage, TipoDestinatario: str):
    """[STD] Selecciona tipo de destinatario"""
    forza_page.seleccionar_tipo_destinatario_exc(TipoDestinatario)


@when(parsers.parse('el usuario ingresa el nombre destinatario "{NombreDestinatario}"'))
def step_ingresar_nombre_destinatario(forza_page: ForzaPage, NombreDestinatario: str):
    """[STD] Ingresa nombre destinatario"""
    forza_page.ingresar_nombre_destinatario_exc(NombreDestinatario)


@when(parsers.parse('el usuario ingresa el teléfono destinatario "{TelefonoDestinatario}"'))
def step_ingresar_telefono_destinatario(forza_page: ForzaPage, TelefonoDestinatario: str):
    """[STD] Ingresa teléfono destinatario"""
    forza_page.ingresar_telefono_destinatario_exc(TelefonoDestinatario)


@when(parsers.parse('el usuario ingresa el correo destinatario "{CorreoDestinatario}"'))
def step_ingresar_correo_destinatario(forza_page: ForzaPage, CorreoDestinatario: str):
    """[STD] Ingresa correo destinatario"""
    forza_page.ingresar_correo_destinatario_exc(CorreoDestinatario)


@when(parsers.parse('el usuario ingresa la dirección destinatario "{DireccionDestinatario}"'))
def step_ingresar_direccion_destinatario(forza_page: ForzaPage, DireccionDestinatario: str):
    """[STD] Ingresa dirección destinatario"""
    forza_page.ingresar_direccion_destinatario_exc(DireccionDestinatario)


@when('el usuario presiona el botón Siguiente')
def step_presionar_siguiente(forza_page: ForzaPage):
    """[STD] Presiona botón Siguiente"""
    forza_page.presionar_siguiente_exc()


@when('el usuario presiona el botón Siguiente nuevamente')
def step_presionar_siguiente_nuevamente(forza_page: ForzaPage):
    """[STD] Presiona botón Siguiente nuevamente"""
    forza_page.presionar_siguiente_exc()


@when(parsers.parse('el usuario selecciona forma de pago "{Pago}"'))
def step_seleccionar_forma_pago(forza_page: ForzaPage, Pago: str):
    """[STD] Selecciona forma de pago"""
    forza_page.seleccionar_forma_pago_exc(Pago)


@when('el usuario presiona el botón Mostrar Resumen')
def step_presionar_mostrar_resumen(forza_page: ForzaPage):
    """[STD] Presiona botón Mostrar Resumen"""
    forza_page.presionar_mostrar_resumen_exc()


@when('el usuario presiona el botón Mis envíos')
def step_presionar_mis_envios(forza_page: ForzaPage):
    """[STD] Presiona botón Mis envíos"""
    forza_page.presionar_ver_envios_exc()


@then('el sistema registra la guía creada exitosamente')
def step_validar_guia_creada(forza_page: ForzaPage):
    """[STD] Valida guía creada"""
    forza_page.validar_guia_creada_exitosamente_exc()

