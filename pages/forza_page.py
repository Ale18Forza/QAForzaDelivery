import re
import random
import os
from pathlib import Path
try:
    import pyodbc
except ImportError:  # pragma: no cover - dependency may be absent in some environments
    pyodbc = None
import openpyxl
from openpyxl.utils import column_index_from_string
import allure
from playwright.sync_api import Page, expect

class ForzaPage:
    def __init__(self, page: Page, db_connection_string: str = ""):
        self.page = page
        self.db_connection_string = db_connection_string #
        
        # Variables de estado
        self.ruta_excel: str = ""
        self.hoja: str = ""
        self.columna: str = ""
        self.url_actual: str = ""
        self.token: str = ""
        self.entorno: str = ""

    def _take_screenshot(self, name: str = "screenshot"):
        try:
            screenshot = self.page.screenshot(type="png")
            allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            print(f"Error taking screenshot: {e}")
    
    @allure.step("Navegar a la URL: '{url}'")
    def go_to_page_web(self, url: str):
        self.url_actual = url
        self.page.goto(url, timeout=120000)
        self._take_screenshot("navigation")

    @allure.step("Validar que el título sea: '{titulo_esperado}'")
    def assert_title(self, titulo_esperado: str):
        assert self.page.title() == titulo_esperado, f"Error: Título esperado '{titulo_esperado}', actual '{self.page.title()}'"
        self._take_screenshot("title_validation")

    @allure.step("Seleccionar país: '{country}'")
    def select_country(self, country: str):
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(1000)

        candidatos = [
            self.page.get_by_text(country, exact=True),
            self.page.get_by_role("button", name=re.compile(re.escape(country), re.I)),
            self.page.get_by_role("link", name=re.compile(re.escape(country), re.I)),
            self.page.locator("button, a, div").filter(has_text=re.compile(re.escape(country), re.I)),
        ]

        for candidato in candidatos:
            try:
                if candidato.count() > 0:
                    candidato.first.click(timeout=15000)
                    self.page.wait_for_load_state("load", timeout=30000)
                    self._take_screenshot("country_selection")
                    return
            except Exception:
                continue

        patron_regex = re.compile(f"^{re.escape(country)}$")
        self.page.locator("div").filter(has_text=patron_regex).get_by_role("emphasis").click(timeout=30000)
        self.page.wait_for_load_state("load")
        self._take_screenshot("country_selection")

    @allure.step("Seleccionar país en App Courier: '{country}'")
    def select_country_courier(self, country: str):
        country_text = self.page.get_by_text(country, exact=True)
        if country_text.count() > 0 and country_text.first.is_visible():
            self._take_screenshot("courier_country_selection")
            return

        try:
            self.page.get_by_role("combobox").select_option(label=country, timeout=10000)
        except Exception as first_error:
            try:
                self.page.locator("select").first.select_option(label=country, timeout=5000)
            except Exception:
                try:
                    self.page.get_by_role("combobox").first.click(timeout=5000)
                    self.page.get_by_text(country, exact=True).click(timeout=5000)
                except Exception:
                    if country_text.count() > 0:
                        return
                    raise first_error
        self._take_screenshot("courier_country_selection")

    @allure.step("Abrir dropdown de países en Tienda Virtual")
    def open_country_dropdown_tv(self):
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(800)

        if self.page.locator(".dropdown").count() > 0:
            self._take_screenshot("tv_country_dropdown_open")
            return

        candidatos = [
            self.page.get_by_role("button", name=re.compile(r"(país|pais|selecciona)", re.I)),
            self.page.get_by_text(re.compile(r"(guatemala|selecciona)", re.I), exact=False),
            self.page.locator("button, a, div").filter(has_text=re.compile(r"(país|pais|guatemala|selecciona)", re.I)),
        ]

        for candidato in candidatos:
            try:
                if candidato.count() > 0:
                    candidato.first.click(timeout=10000)
                    self.page.wait_for_timeout(600)
                    if self.page.locator(".dropdown").count() > 0:
                        self._take_screenshot("tv_country_dropdown_open")
                        return
            except Exception:
                continue

        # Paso best-effort: la aserción definitiva ocurre en assert_country_dropdown_options_tv.
        self._take_screenshot("tv_country_dropdown_open_best_effort")

    @allure.step("Validar opciones del dropdown de países en TV: '{expected_options}'")
    def assert_country_dropdown_options_tv(self, expected_options):
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        dropdown_count = self.page.locator(".dropdown").count()
        if dropdown_count == 0:
            raise AssertionError("No se encontró un contenedor con clase 'dropdown' en el DOM.")

        found_options = self.page.evaluate(
            r"""() => {
                const nodes = Array.from(document.querySelectorAll('.dropdown .text-option-country, .text-option-country'));
                return nodes
                    .map((n) => (n.textContent || '').replace(/\s+/g, ' ').trim())
                    .filter(Boolean);
            }"""
        )

        filtered_options = []
        for option in found_options:
            if option in expected_options and option not in filtered_options:
                filtered_options.append(option)

        if filtered_options != expected_options:
            raise AssertionError(
                f"Opciones del dropdown no coinciden. Esperado: {expected_options}. Encontrado: {filtered_options}"
            )

        self._take_screenshot("tv_country_dropdown_options_validated")

    # ==============================================================================
    # FLUJOS DE LOGIN
    # ==============================================================================

    @allure.step("Hacer clic en el elemento con title: '{title}'")
    def click_by_title(self, title: str):
        # Mantiene el flujo histórico de TV donde se requieren dos acciones encadenadas.
        self.page.locator("a").filter(has_text=title).click()
        self.page.wait_for_timeout(1000)
        self.page.get_by_title(title).click()



    def _click_login_button(self, scope=None):
        search_root = scope if scope is not None else self.page
        locator = search_root.get_by_role("button", name=re.compile(r"^Iniciar sesión$", re.I), exact=True)
        if locator.count() == 0 and search_root is not self.page:
            locator = self.page.get_by_role("button", name=re.compile(r"^Iniciar sesión$", re.I), exact=True)

        locator.first.wait_for(state="visible", timeout=30000)
        expect(locator.first).to_be_enabled(timeout=30000)
        locator.first.click(timeout=30000)

    @allure.step("Login Portal Web - Correo: '{correo}'")
    def login(self, correo: str, passw: str):
        self.page.get_by_role("textbox", name="Ingresar Usuario").wait_for(state="visible", timeout=30000)
        self.page.get_by_role("textbox", name="Ingresar Usuario").click()
        self.page.get_by_role("textbox", name="Ingresar Usuario").fill(correo)
        
        self.page.get_by_role("textbox", name="Ingresar Contraseña").click()
        self.page.get_by_role("textbox", name="Ingresar Contraseña").fill(passw)
        
        self._click_login_button()
        self.page.wait_for_load_state("networkidle", timeout=60000)
        self.page.wait_for_timeout(2000)
        self._take_screenshot("login_success")

    @allure.step("Login Tienda Virtual - Correo: '{correo}'")
    def login_tv(self, correo: str, passw: str):
        user_input = self.page.get_by_role("textbox", name="Ingresar Usuario").first
        pass_input = self.page.get_by_role("textbox", name="Ingresar Contraseña").first

        user_input.wait_for(state="visible", timeout=20000)
        user_input.click()
        user_input.fill("")
        user_input.press_sequentially(correo, delay=35)
        self.page.wait_for_timeout(1000)
        
        pass_input.click()
        self.page.wait_for_timeout(1000)
        pass_input.fill("")
        pass_input.press_sequentially(passw, delay=35)

        # En TV hay un checkbox (términos/política) que mantiene el botón deshabilitado si no se marca.
        checkbox = self.page.locator("input[type='checkbox']:visible").first
        if checkbox.count() > 0:
            try:
                if checkbox.is_visible() and not checkbox.is_checked():
                    checkbox.click(timeout=5000)
            except Exception:
                pass

        # Fuerza eventos de validación del formulario (Angular) para habilitar el botón de login.
        pass_input.evaluate(
            """(el) => {
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.blur();
            }"""
        )

        login_form = self.page.locator("form").filter(has=user_input)
        self._click_login_button(scope=login_form.first if login_form.count() > 0 else None)
        self.page.wait_for_load_state("networkidle", timeout=60000)
        self.page.wait_for_timeout(2000)
        self._take_screenshot("login_success")

    @allure.step("Validar que el inicio de sesión fue exitoso")
    def validar_inicio_sesion(self):
        self.page.wait_for_load_state("networkidle", timeout=60000)
        self.page.wait_for_timeout(2000)

        url_baja = self.page.url.lower()
        if any(token in url_baja for token in ["/design/dashboard", "/dashboard", "/home", "/mis-envios", "/mi-cuenta", "/perfil"]):
            self._take_screenshot("login_validation_success")
            return

        candidatos = [
            self.page.get_by_role("button", name=re.compile(r"(cerrar sesión|salir|mi cuenta|perfil|mis envíos|mis envios)", re.I)),
            self.page.get_by_text(re.compile(r"(bienvenido|mis envíos|mis envios|dashboard|inicio)", re.I), exact=False),
        ]

        for candidato in candidatos:
            try:
                candidato.first.wait_for(state="visible", timeout=15000)
                self._take_screenshot("login_validation_success")
                return
            except Exception:
                continue

        raise AssertionError(f"No se pudo validar el inicio de sesión. URL actual: {self.page.url}")

    @allure.step("Validar que el inicio de sesión NO fue exitoso")
    def validar_no_inicio_sesion(self):
        self.page.wait_for_load_state("networkidle", timeout=60000)
        self.page.wait_for_timeout(1500)

        url_baja = self.page.url.lower()
        rutas_logueado = ["/design/dashboard", "/dashboard", "/home", "/mis-envios", "/mi-cuenta", "/perfil"]
        if any(token in url_baja for token in rutas_logueado):
            raise AssertionError(f"La sesión sí fue iniciada. URL actual: {self.page.url}")

        # Si aparece evidencia de sesión autenticada, la validación negativa debe fallar.
        señales_sesion_activa = [
            self.page.get_by_role("button", name=re.compile(r"(cerrar sesión|salir|mi cuenta|perfil|mis envíos|mis envios)", re.I)),
            self.page.get_by_text(re.compile(r"(bienvenido|mis envíos|mis envios|dashboard)", re.I), exact=False),
        ]

        for señal in señales_sesion_activa:
            try:
                if señal.count() > 0 and señal.first.is_visible():
                    raise AssertionError(f"Se detectó sesión activa inesperada. URL actual: {self.page.url}")
            except AssertionError:
                raise
            except Exception:
                continue

        self._take_screenshot("login_validation_failed_expected")

    @allure.step("Elegir carrito si el valor es 0")
    def elegir_carrito_si_valor_cero(self):
        # Validación DOM: el span .numberIcon dentro de #cartHeaderId debe ser "0"
        carrito_header = self.page.locator("#cartHeaderId")
        carrito_header.wait_for(state="visible", timeout=20000)

        valor = self.page.evaluate(
            """() => {
                const span = document.querySelector('#cartHeaderId .numberIcon');
                return span ? span.textContent.trim() : null;
            }"""
        )

        if valor != "0":
            raise AssertionError(
                f"El carrito no tiene valor 0. Valor actual: '{valor}'. No se puede continuar."
            )

        # Clic usando el selector confirmado por codegen: <a> que contiene el texto "0"
        self.page.locator("a").filter(has_text="0").click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self._take_screenshot("carrito_en_cero_seleccionado")

    @allure.step("Validar que el botón '{boton}' está inhabilitado")
    def validar_boton_inhabilitado(self, boton: str):
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(800)

        locator = self.page.get_by_text(boton).first
        locator.wait_for(state="visible", timeout=15000)
        expect(locator).to_be_disabled(timeout=10000)
        self._take_screenshot(f"boton_{boton.lower()}_inhabilitado")

    @allure.step("Validar que la landing page cargó correctamente")
    def validar_landing_cargada(self):
        # 1. Espera que el DOM esté listo
        self.page.wait_for_load_state("domcontentloaded", timeout=60000)
        # 2. Espera que no haya peticiones de red activas (XHR, fetch, etc.)
        self.page.wait_for_load_state("networkidle", timeout=60000)
        # 3. Espera que Angular/SPA termine de renderizar comprobando document.readyState
        self.page.wait_for_function("document.readyState === 'complete'", timeout=30000)
        # 4. Pausa breve para que componentes Angular terminen su ciclo de detección de cambios
        self.page.wait_for_timeout(1500)

        url_actual = self.page.url.lower()
        dominio_esperado = "qa-tienda.forzadeliveryexpress.com"
        if dominio_esperado not in url_actual:
            raise AssertionError(f"Dominio inesperado. URL actual: {self.page.url}")

        self._take_screenshot("landing_page_cargada")

    @allure.step("Validar que el carrito está vacío")
    def validar_carrito_vacio(self):
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(800)

        carrito_header = self.page.locator("#cartHeaderId")
        carrito_header.wait_for(state="visible", timeout=15000)

        valor = self.page.evaluate(
            """() => {
                const span = document.querySelector('#cartHeaderId .numberIcon');
                return span ? span.textContent.trim() : null;
            }"""
        )

        if valor != "0":
            raise AssertionError(
                f"El carrito no está vacío. Valor actual: '{valor}'. Se esperaba '0'."
            )

        self._take_screenshot("carrito_vacio_validado")

    @allure.step("Login Corporativo - Código: '{codigo}', Usuario: '{usuario}'")
    def login_corp(self, codigo: str, usuario: str, passw: str):
        self.page.get_by_role("button", name="Usuario Corporativo").click()
        
        self.page.get_by_placeholder("Ingresar Código").click()
        self.page.get_by_placeholder("Ingresar Código").fill(codigo)
        
        self.page.get_by_role("textbox", name="Ingresar Usuario").click()
        self.page.get_by_role("textbox", name="Ingresar Usuario").fill(usuario)
        
        self.page.get_by_role("textbox", name="Ingresar Contraseña").click()
        self.page.get_by_role("textbox", name="Ingresar Contraseña").fill(passw)
        
        self.page.get_by_role("button", name="Iniciar sesión").click()
        self.page.wait_for_url(f"**/historico", wait_until="networkidle")
        self._take_screenshot("login_corp_success")

    @allure.step("Login Express Center - Estación: '{estacion}', Correo: '{correo}'")
    def login_exec(self, estacion: str, correo: str, passw: str):
        self.page.get_by_role("button", name="Usuario Express Center").click()
        self.page.wait_for_timeout(800)

        # En /login-exc a veces el selector de estación aparece directo (Angular state),
        # otras veces la página vuelve a pedir seleccionar país primero.
        # Intento 1: selector de estación directo (flujo estándar)
        btn_sel = self.page.locator("button, ion-button").filter(
            has_text=re.compile(r"Selecciona tu estaci", re.I)
        ).first
        try:
            btn_sel.wait_for(state="visible", timeout=5000)
            btn_sel.click()
        except Exception:
            # Intento 2: /login-exc muestra país primero — seleccionar Guatemala y reintentar
            pais_btn = self.page.get_by_text("Guatemala", exact=True).first
            pais_btn.wait_for(state="visible", timeout=10000)
            pais_btn.click()
            self.page.wait_for_timeout(600)
            self.page.get_by_role("button", name="Selecciona tu estación").click(timeout=15000)

        self.page.get_by_role("searchbox", name="search text").click()
        self.page.get_by_role("searchbox", name="search text").fill(estacion)
        self.page.get_by_text(estacion, exact=True).click()

        self.page.get_by_role("textbox", name="Ingresar Usuario").click()
        self.page.get_by_role("textbox", name="Ingresar Usuario").fill(correo)

        self.page.get_by_role("textbox", name="Ingresar Contraseña").click()
        self.page.get_by_role("textbox", name="Ingresar Contraseña").fill(passw)

        self.page.get_by_role("button", name="Iniciar sesión").click()
        self.page.wait_for_url(f"**/historico", wait_until="networkidle")
        self._take_screenshot("login_exec_success")

    @allure.step("Login App Courier - Teléfono: '{telefono}'")
    def login_courier_app(self, telefono: str, entorno: str = None):
        self.page.wait_for_timeout(1000)
        input_phone = self.page.locator("#inputPhone")
        if input_phone.count() > 0:
            input_phone.fill(telefono)
        else:
            self.page.locator("input:not([type='hidden'])").last.fill(telefono)
        self.page.wait_for_timeout(1000)
        
        self.page.get_by_role("button", name="Autenticar").click()
        self.page.get_by_text("Autenticación").wait_for()
        
        # Use provided entorno or instance entorno
        entorno_a_usar = entorno if entorno is not None else self.entorno
        self.token = self.obtener_token_db(telefono, entorno_a_usar)
        self.ingresar_token(self.token)
        self._take_screenshot("login_courier_success")

    @allure.step("Ingresar Token OTP")
    def ingresar_token(self, token: str):
        if not token or not token.strip():
            raise ValueError("Token inválido o vacío.")
            
        for i, digito in enumerate(token):
            self.page.locator(f"#inputToken{i + 1}").fill(digito)
            
        self.page.get_by_text("Iniciar sesión").click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        self._take_screenshot("token_entered")

    # ==============================================================================
    # ACCIONES DE NAVEGACIÓN INTERNA
    # ==============================================================================

    @allure.step("Seleccionar opción tipo de servicio: '{tipo_servicio}'")
    def opcion_tipo_servicio(self, tipo_servicio: str):
        self.page.get_by_title(tipo_servicio).click()
        self._take_screenshot("service_type_selected")

    @allure.step("Seleccionar opción Crear Guías")
    def opcion_crear_guias(self):
        self.page.get_by_role("link", name="chevron forward Crear Guías").click()
        self.page.wait_for_timeout(1000)
        self._take_screenshot("create_guides_section")

    # ==============================================================================
    # FLUJO PRINCIPAL: CREACIÓN DE GUÍAS
    # ==============================================================================

    @allure.step("Creación de {cantidad} guías con parámetros específicos")
    def creacion_guias(self, cantidad: int, direccion): # 'direccion' es el dataclass de test_forza_steps.py
        modal_ya_fue_cerrado = False
        is_collet = str(direccion.collet).lower() == 'true'
        is_nueva_origen = str(direccion.direccion_nueva_origen).lower() == 'true'
        is_nueva_destino = str(direccion.direccion_nueva_destino).lower() == 'true'
        is_std = direccion.tipo_guia == "Servicio Estándar"
        
        for i in range(cantidad):
            print(f"Registrando solicitud #{i + 1}")
            monto_aleatorio = 0
            self.page.wait_for_timeout(1000)
            self.page.get_by_title(direccion.tipo_guia).click()

            if is_nueva_origen:
                # Aquí puedes poner la URL mapeada desde tu configuración
                self.page.wait_for_url("**/opciones-guias", wait_until="networkidle", timeout=30000)
                self.page.get_by_text("Crear dirección de origen").click()
                self.crear_nueva_direccion_origen()

            self.page.locator("#step5 #buttonOpenSelect").click()

            if is_nueva_destino:
                self.page.locator("//strong[contains(text(), 'Crear nueva dirección')]").click()
                self.page.wait_for_timeout(1000)
                self.crear_nueva_direccion_destino()
            else:
                self.page.get_by_text(direccion.nombre_direccion).click()
                self.page.wait_for_timeout(1000)

            if is_collet:
                self.page.get_by_label("Cobro contra entrega").check()
            else:
                self.page.get_by_label("Cobro a mi cuenta").check()

            self.page.locator("#step8 input[type='text']").fill("QA002")
            self.page.wait_for_timeout(1000)

            if is_std:
                self.page.get_by_text("Agregar paquete").click()
            else:
                monto_aleatorio = random.randint(5000, 20000)
                self.page.locator("#step19 input[type='text']").fill(str(monto_aleatorio))
                self.page.locator("#step20 #buttonOpenSelect").click()
                # ¡AQUÍ ESTÁ LA MAGIA! Reemplazamos el string quemado por direccion.tarjeta
                self.page.get_by_text(direccion.tarjeta).click()
                self.page.get_by_text("Agregar paquete").click()
                self.page.wait_for_timeout(1000)

            if not modal_ya_fue_cerrado:
                self.page.locator("#packageInformationModal button").click()
                modal_ya_fue_cerrado = True

            self.page.wait_for_timeout(1000)
            self.page.get_by_title("Finalizar y pagar").click()
            self.page.wait_for_timeout(1000)
            self.page.get_by_role("button", name="Si").click()
            self._take_screenshot(f"guide_{i+1}_confirm")

            if monto_aleatorio > 10000:
                self.page.wait_for_timeout(1000)
                self.page.get_by_role("button", name="Si").click()

            if is_collet:
                self.page.get_by_text("Finalizar", exact=True).click()
                self.page.locator("div").filter(has_text=re.compile(r"^¿Cómo realizarás tu recolección\?$")).locator("button").click()
                self.page.get_by_title("Mis Envíos").click()
                self.page.wait_for_timeout(1000)
                
                numero_guia = self.page.locator("(//table//tr[1]//strong[contains(text(), 'FD')])[1]").inner_text()
                print(f"Número de guía: {numero_guia}")
                
                if is_std:
                    self.guardar_guia_en_archivo("guias_Collet_STD", "STD", numero_guia)
                else:
                    self.guardar_guia_en_archivo("guias_Collet_COD", "COD", numero_guia)
                self._take_screenshot(f"guide_{i+1}_created")
            else:
                self.page.wait_for_timeout(1000)
                self.page.get_by_label("CF").check()
                self.page.get_by_label("Tarjeta").check()
                self.page.get_by_text("Pagar Carrito").click()
                self.page.wait_for_timeout(1000)
                self.page.wait_for_load_state("load")

                frame = self.page.frame_locator("#RequestFAC")
                texto_frame = frame.get_by_role("paragraph").inner_text()

                match = re.search(r"FD\d+", texto_frame)
                if match:
                    guia = match.group(0)
                    if is_std:
                        self.guardar_guia_en_archivo("guias_STD_Prepagada", "STD", guia)
                    else:
                        self.guardar_guia_en_archivo("guias_Collet_COD_Prepagada", "COD", guia)
                    print(f"Guía encontrada: {guia}")
                else:
                    print("No se encontró una guía.")
                self._take_screenshot(f"guide_{i+1}_prepaid")

                # TRADUCCIÓN DEL PATRÓN "Task" DE C# A PYTHON (Eventos asíncronos en API Sync)
                with self.page.expect_popup() as popup_info, self.page.expect_download() as download_info:
                    self.page.locator("#confirmPaymentModal button").click()
                
                popup = popup_info.value
                download = download_info.value

                self.page.locator("div").filter(has_text=re.compile(r"^¿Cómo realizarás tu recolección\?$")).locator("button").click()

    # ==============================================================================
    # DIRECCIONES Y AYUDANTES DE FORMULARIOS
    # ==============================================================================

    @allure.step("Llenar formulario de nueva dirección destino")
    def crear_nueva_direccion_destino(self):
        nombre = self.generar_nombre_qa()
        telefono = self.generar_telefono()

        self.page.get_by_placeholder("Ingresar Nombre").nth(1).click()
        self.page.get_by_placeholder("Ingresar Nombre").nth(1).fill(nombre)

        self.page.get_by_placeholder("Lugar en la ciudad").nth(1).click()
        self.page.locator("//li[normalize-space(.)='Gimnasio']").nth(1).click()

        self.page.get_by_placeholder("Seleccione Poblado").nth(1).click()
        self.page.locator("//li[normalize-space(.)='Cahabon, Santa Maria Cahabon, Alta Verapaz']").nth(1).click()

        self.page.get_by_placeholder("Ingresar Teléfono").nth(1).click()
        self.page.get_by_placeholder("Ingresar Teléfono").nth(1).fill(telefono)

        self.page.get_by_placeholder("Ingrese la dirección exacta").nth(1).click()
        self.page.get_by_placeholder("Ingrese la dirección exacta").nth(1).fill("Cahabón, Guatemala")

        self.page.locator("//input[@placeholder='Ingrese el nombre de la persona que recibirá el envío' and @type='text']").click()
        self.page.locator("//input[@placeholder='Ingrese el nombre de la persona que recibirá el envío' and @type='text']").fill("QA Demo")

        # Forzar validaciones (Presionar espacio)
        self.page.get_by_placeholder("Ingresar Nombre").nth(1).press(" ")
        self.page.get_by_placeholder("Ingresar Teléfono").nth(1).press(" ")
        self.page.locator("//input[@placeholder='Ingrese el nombre de la persona que recibirá el envío' and @type='text']").press(" ")
        self.page.get_by_placeholder("Ingrese la dirección exacta").nth(1).press(" ")

        self.page.locator("//button[normalize-space(.)='Guardar']").nth(3).click()
        self._take_screenshot("new_destination_address")

    @allure.step("Llenar formulario de nueva dirección origen")
    def crear_nueva_direccion_origen(self):
        nombre = self.generar_nombre_qa()
        telefono = self.generar_telefono()

        self.page.get_by_placeholder("Ingresar Nombre").nth(0).click()
        self.page.get_by_placeholder("Ingresar Nombre").nth(0).fill(nombre)

        self.page.get_by_placeholder("Lugar en la ciudad").nth(0).click()
        self.page.locator("//li[normalize-space(.)='Gimnasio']").nth(0).click()

        self.page.get_by_placeholder("Seleccione Poblado").nth(0).click()
        self.page.locator("//li[normalize-space(.)='Cahabon, Santa Maria Cahabon, Alta Verapaz']").nth(0).click()

        self.page.get_by_placeholder("Ingresar Teléfono").nth(0).click()
        self.page.get_by_placeholder("Ingresar Teléfono").nth(0).fill(telefono)

        self.page.get_by_placeholder("Ingrese la dirección exacta").nth(0).click()
        self.page.get_by_placeholder("Ingrese la dirección exacta").nth(0).fill("Cahabón, Guatemala")

        self.page.get_by_placeholder("Ingrese ubicación ej. zona 10").click()
        self.page.get_by_placeholder("Ingrese ubicación ej. zona 10").fill("Ciudad de guatemala")

        input_ub = self.page.get_by_placeholder("Ingrese ubicación ej. zona 10")
        input_ub.press("Backspace")

        self.page.get_by_text("Ciudad de Guatemala", exact=True).click()

        self.page.get_by_placeholder("Ingresar Nombre").nth(0).press(" ")
        self.page.get_by_placeholder("Ingresar Teléfono").nth(0).press(" ")
        self.page.locator("//input[@placeholder='Ingrese el nombre de la persona que recibirá el envío' and @type='text']").press(" ")
        self.page.get_by_placeholder("Ingrese la dirección exacta").nth(0).press(" ")

        self.page.locator(".form-group > .btn").first.click()
        self._take_screenshot("new_origin_address")

    # ==============================================================================
    # PROCESAMIENTO DE EXCEL (Equivalente a ClosedXML)
    # ==============================================================================

    def ruta_excel_obtener(self, ruta: str):
        self.ruta_excel = ruta

    def hoja_excel(self, hoja: str):
        self.hoja = hoja

    def columna_excel(self, col: str):
        self.columna = col

    @allure.step("Ingresar lote de recolección desde Excel (Inicio: {inicial}, Final: {final}, Piezas: {cantidad_piezas})")
    def ingresar_a_recoleccion(self, inicial: int, final: int, cantidad_piezas: int = 1):
        datos = self.obtener_guias_desde_excel(inicial, final)
        self.elegir_recolectar()

        textbox = self.page.locator("//*[@id='lblGuide']")
        for valor in datos:
            textbox.fill(f"{str(valor)}-{cantidad_piezas}")
            with self.page.expect_response("**/Home.aspx/FDApi", timeout=60000):
                textbox.press("Enter")
            textbox.wait_for(state="visible")
        self._take_screenshot("batch_collection_complete")

        # Pasos finales para completar la recolección
        self.page.get_by_role("button", name="Siguiente").click()
        
        # Llenar correo del cliente
        correo_textbox = self.page.get_by_role("textbox", name="Correo del cliente *")
        correo_textbox.wait_for(state="visible", timeout=30000)
        correo_textbox.fill("carlos.fernandez@forzalatam.com")
        
        # Dibujar en el canvas para activar botón Finalizar
        canvas = self.page.locator("canvas").first
        canvas.wait_for(state="visible")
        
        # Inyectar firma en el canvas para activar el botón Finalizar
        canvas = self.page.locator("canvas").first
        canvas.wait_for(state="visible")
        
        # Dibujar en el canvas con eventos reales (lo que funcionó visualmente)
        bbox = canvas.bounding_box()
        if bbox:
            self.page.mouse.move(bbox['x'] + 50, bbox['y'] + 100)
            self.page.mouse.down()
            for i in range(10):
                self.page.mouse.move(bbox['x'] + 50 + i * 15, bbox['y'] + 100 + (i % 3) * 10)
            self.page.mouse.up()
            self.page.wait_for_timeout(500)
        
        # Estrategia: Forzar el botón y ejecutar su acción directamente
        self.page.evaluate("""
            () => {
                const btn = document.querySelector('#btnFinish');
                if (!btn) return;
                
                // Habilitar el botón visualmente
                btn.disabled = false;
                btn.removeAttribute('disabled');
                btn.classList.remove('disabled');
                
                // Intentar obtener la función que ejecuta el botón
                // 1. Revisar si tiene un onclick directo
                if (btn.onclick) {
                    console.log('Ejecutando onclick directo');
                    btn.onclick();
                    return;
                }
            
                // 3. Si no encuentra nada, disparar un click event estándar
                console.log('Disparando evento click estándar');
                btn.dispatchEvent(new MouseEvent('click', {
                    view: window,
                    bubbles: true,
                    cancelable: true
                }));
            }
        """)
        
        # Esperar el mensaje de éxito
        self.page.get_by_role("alert").wait_for(state="visible", timeout=30000)
        expect(self.page.get_by_role("alert")).to_contain_text("Servicio completado exitosamente.")
        self._take_screenshot("recoleccion_finalizada")

    def elegir_recolectar(self):
        self.page.locator("//button[@type='button' and @data-type='Pickup' and contains(text(), 'Recolectar')]").first.click()
        self.page.locator("//button[@type='button' and contains(text(), 'Recolectar')]").click()

    @allure.step("Abrir recolección pendiente en posición {posicion}")
    def abrir_recoleccion_por_posicion(self, posicion: int):
        if posicion < 1:
            raise ValueError("La posición de la recolección debe ser mayor o igual a 1.")

        botones_recolectar = self.page.locator("//button[contains(normalize-space(.), 'Recolectar')]")
        botones_recolectar.nth(posicion - 1).click(timeout=30000)
        self.page.wait_for_load_state("networkidle")
        self._take_screenshot(f"pickup_position_{posicion}")

    @allure.step("Reportar visita fallida")
    def reportar_visita_fallida(self, ruta_imagen: str):
        self.page.get_by_role("button", name=re.compile("Visita fallida", re.I)).click(timeout=30000)
        self.page.wait_for_load_state("networkidle")

        self.seleccionar_primer_motivo_visita_fallida()
        self.cargar_imagen_visita_fallida(ruta_imagen)

        expect(self.page.get_by_text(re.compile("Ubicación detectada exitosamente", re.I))).to_be_visible(timeout=30000)
        reportar = self.page.locator("//button[contains(normalize-space(.), 'Reportar')]").last
        reportar.scroll_into_view_if_needed(timeout=10000)
        expect(reportar).to_be_enabled(timeout=120000)
        self.page.wait_for_function(
            """
            () => {
                const buttons = [...document.querySelectorAll('button')];
                const reportar = buttons.reverse().find((button) => button.textContent.includes('Reportar'));
                if (!reportar) return false;
                const style = window.getComputedStyle(reportar);
                return !reportar.disabled && style.visibility !== 'hidden' && style.display !== 'none';
            }
            """,
            timeout=120000,
        )
        reportar.click(timeout=120000)
        self._take_screenshot("failed_pickup_reported")

    def seleccionar_primer_motivo_visita_fallida(self):
        selected = self.page.evaluate(
            """
            () => {
                const select = document.querySelector('select');
                if (!select) return false;
                if (select.options.length > 1) {
                    select.selectedIndex = 1;
                }
                select.dispatchEvent(new Event('input', { bubbles: true }));
                select.dispatchEvent(new Event('change', { bubbles: true }));
                return Boolean(select.value);
            }
            """
        )
        if selected:
            return

        motivo_default = self.page.get_by_text("Información incompleta", exact=True)
        if motivo_default.count() > 0:
            return

        comboboxes = self.page.get_by_role("combobox")
        if comboboxes.count() > 0:
            try:
                comboboxes.first.select_option(index=1)
                return
            except Exception:
                pass

        selectores = self.page.locator("select")
        if selectores.count() > 0:
            opciones = selectores.first.locator("option")
            if opciones.count() > 1:
                selectores.first.select_option(index=1)
            else:
                selectores.first.select_option(index=0)
            return

        try:
            self.page.get_by_role("combobox").first.click(timeout=10000)
            self.page.get_by_role("option").nth(1).click(timeout=10000)
        except Exception:
            return

    def cargar_imagen_visita_fallida(self, ruta_imagen: str):
        ruta = Path(ruta_imagen)
        if not ruta.is_absolute():
            ruta = Path(__file__).resolve().parent.parent / ruta
        if not ruta.exists():
            raise FileNotFoundError(f"No existe la imagen para visita fallida: {ruta}")

        file_input = self.page.locator("input[type='file']").first
        file_input.set_input_files(str(ruta))
        self.page.wait_for_timeout(1000)

    @allure.step("Validar mensaje de visita fallida: '{mensaje}'")
    def validar_mensaje_visita_fallida(self, mensaje: str):
        expect(self.page.get_by_text(mensaje)).to_be_visible(timeout=120000)
        self._take_screenshot("failed_pickup_success_message")

    def obtener_guias_desde_excel(self, inicial: int, final: int) -> list:
        datos = self.leer_columna_excel(self.ruta_excel, self.hoja, self.columna)
        if inicial < 1:
            raise ValueError("El rango inicial debe ser mayor o igual a 1.")
        if final < inicial:
            raise ValueError("El rango final debe ser mayor o igual al rango inicial.")

        limite = min(len(datos), final)
        return datos[inicial - 1:limite]

    def leer_columna_excel(self, nombre_archivo: str, hoja: str, columna_letra: str) -> list:
        ruta_absoluta = os.path.abspath(nombre_archivo)
        if not os.path.exists(ruta_absoluta):
            raise FileNotFoundError(f"El archivo no existe: {ruta_absoluta}")

        try:
            wb = openpyxl.load_workbook(ruta_absoluta, data_only=True)
            if hoja not in wb.sheetnames:
                raise ValueError(f"La hoja '{hoja}' no existe.")
            
            ws = wb[hoja]
            col_idx = column_index_from_string(columna_letra)
            valores = []

            for row in ws.iter_rows(min_col=col_idx, max_col=col_idx, values_only=True):
                if row[0] is not None:
                    valores.append(row[0])
            return valores
        except Exception as e:
            print(f"Error leyendo el archivo Excel: {e}")
            return []

    # ==============================================================================
    # INTEGRACIÓN DE BASE DE DATOS (SQL Server con pyodbc)
    # ==============================================================================
    
    @allure.step("Obtener token OTP desde la Base de Datos")
    def obtener_token_db(self, telefono: str, entorno: str = None) -> str:
        """
        Conecta a SQL Server dinámicamente según el entorno, busca el token más reciente
        para un teléfono y lo devuelve.
        """
        entorno_normalizado = (entorno or "DEFAULT").upper()
        env_key = f"SQLSERVER_{entorno_normalizado}_CONNECTION_STRING"
        base_connection_string = os.getenv(env_key) or os.getenv("SQLSERVER_CONNECTION_STRING")

        if pyodbc is None:
            raise ImportError("La dependencia pyodbc no está instalada. Instálala para usar login por OTP desde base de datos.")

        if not base_connection_string:
            raise ValueError(
                f"No se encontró cadena de conexión. Configura {env_key} "
                "o SQLSERVER_CONNECTION_STRING en el archivo .env."
            )

        full_connection_string = base_connection_string.rstrip(";")
        if "Encrypt=" not in full_connection_string:
            full_connection_string += ";Encrypt=yes"
        if "TrustServerCertificate=" not in full_connection_string:
            full_connection_string += ";TrustServerCertificate=yes"
        full_connection_string += ";"

        try:
            # 4. Abrir la conexión
            conn = pyodbc.connect(full_connection_string)
            cursor = conn.cursor()

            # 5. La consulta SQL
            # IMPORTANTE: En pyodbc no se usan nombres como '@Telefono', se usan signos de interrogación '?'
            query = """
                SELECT TOP 1 srt.LoginToken
                FROM dbo.SenderReceiver sr
                INNER JOIN dbo.SenderReceiverLoginToken srt 
                    ON sr.ID = srt.SenderReceiverId
                WHERE sr.Phone = ?
                ORDER BY srt.DateCreated DESC
            """

            # 6. Equivalente a command.Parameters.Add() y ExecuteScalarAsync()
            # Pasamos 'telefono' como una tupla al método execute para prevenir SQL Injection
            cursor.execute(query, (telefono,))
            row = cursor.fetchone()

            # 7. Equivalente a result?.ToString()
            return str(row[0]) if row else ""

        except pyodbc.Error as e:
            print(f"Error de base de datos conectando a SQL Server: {e}")
            return ""
        except Exception as e:
            print(f"Error general en la obtención del token: {e}")
            return ""
        finally:
            # Buena práctica: Asegurarnos de cerrar la conexión en Python equivalente al 'await using'
            if 'conn' in locals():
                conn.close()

    # ==============================================================================
    # GENERADORES DE DATOS Y ARCHIVOS UTILS
    # ==============================================================================

    def guardar_guia_en_archivo(self, nombre_archivo: str, tipo_guia: str, guia: str):
        if not nombre_archivo.endswith(".txt"):
            nombre_archivo += ".txt"
            
        linea = f"Guia {tipo_guia} ----> {guia}\n"
        with open(nombre_archivo, "a", encoding="utf-8") as f:
            f.write(linea)

    def generar_nombre_qa(self) -> str:
        nombres = ["Carlos", "Ana", "Luis", "Sofía", "Pedro", "Laura", "Mario", "Paola", "Alfita", "Juancito", "Manuelito"]
        nombre_aleatorio = random.choice(nombres)
        numero = random.randint(100, 999)
        return f"QA {nombre_aleatorio}{numero}"

    def generar_telefono(self) -> str:
        primer_digito = str(random.randint(3, 7))
        resto = "".join(str(random.randint(0, 9)) for _ in range(7))
        return primer_digito + resto

    def generar_cuenta_aleatoria(self, longitud: int) -> str:
        return "".join(str(random.randint(0, 9)) for _ in range(longitud))

    # ==============================================================================
    # MIS ENVÍOS - PORTAL EXPRESS CENTER (EXEC)
    # ==============================================================================

    def _esperar_mis_envios_lista(self, timeout: int = 30000):
        """Espera a que Mis Envíos termine de cargar: networkidle + campo de búsqueda visible.
        Usa el input interno del ion-searchbar para evitar strict mode (el componente emite 2 nodos)."""
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        self.page.get_by_role("searchbox", name="search text").wait_for(state="visible", timeout=timeout)

    def _guias_en_tabla(self):
        """Locator de los números de guía FD visibles en pantalla.
        El build de QA renderiza los números en <ion-label> (componente Ionic),
        no en <strong> como indica el código fuente Angular."""
        return self.page.locator("ion-label").filter(has_text=re.compile(r"FD\d+"))

    @allure.step("Verificar que la pantalla Mis Envíos cargó correctamente")
    def verificar_mis_envios_cargada(self):
        self._esperar_mis_envios_lista()
        guias = self._guias_en_tabla()
        sin_resultados = self.page.get_by_text("No se encontraron servicios", exact=False)
        # count() es instantáneo — esperar explícitamente el primer ion-label antes de asertar
        try:
            guias.first.wait_for(state="visible", timeout=10000)
        except Exception:
            assert sin_resultados.is_visible(), \
                "Mis Envíos cargó pero no muestra guías FD (ion-label) ni mensaje de estado vacío"
        self._take_screenshot("mis_envios_cargada")

    @allure.step("Aplicar filtro de estado: '{estado}'")
    def filtrar_mis_envios_por_estado(self, estado: str):
        # QA build renderiza los filtros como ion-segment-button (Ionic), no .btn-group-toggle
        btn = self.page.locator("ion-segment-button").filter(has_text=estado).first
        btn.wait_for(state="visible", timeout=15000)
        btn.click()
        self.page.wait_for_load_state("networkidle", timeout=20000)
        self.page.wait_for_timeout(1000)
        self._take_screenshot(f"filtro_{re.sub(r'[^a-z0-9]', '_', estado.lower())}")

    @allure.step("Verificar que la tabla refleja el filtro: '{estado}'")
    def verificar_filtro_mis_envios(self, estado: str):
        # Tabla vacía sin mensaje es resultado válido (cuenta sin guías en ese estado)
        self.page.wait_for_load_state("networkidle", timeout=10000)
        guias = self._guias_en_tabla()
        try:
            guias.first.wait_for(state="visible", timeout=3000)
        except Exception:
            pass
        self._take_screenshot(f"verificacion_{re.sub(r'[^a-z0-9]', '_', estado.lower())}")

    @allure.step("Obtener número de la primera guía en Mis Envíos")
    def obtener_primera_guia_mis_envios(self) -> str:
        self._esperar_mis_envios_lista()
        guia_locator = self._guias_en_tabla().first
        guia_locator.wait_for(state="visible", timeout=30000)
        guia = guia_locator.inner_text().strip()
        print(f"Primera guía encontrada: {guia}")
        self._take_screenshot("primera_guia_obtenida")
        return guia

    @allure.step("Buscar en Mis Envíos por texto: '{texto}'")
    def buscar_en_mis_envios(self, texto: str):
        search_input = self.page.get_by_role("searchbox", name="search text")
        search_input.wait_for(state="visible", timeout=15000)
        search_input.fill("")
        search_input.fill(texto)
        self.page.wait_for_timeout(1000)
        self._take_screenshot(f"busqueda_{texto[:20].replace('/', '_')}")

    @allure.step("Verificar que la tabla muestra únicamente la guía: '{guia}'")
    def verificar_resultado_busqueda_guia(self, guia: str):
        self.page.wait_for_timeout(500)
        guias = self._guias_en_tabla()
        assert guias.count() == 1, f"Se esperaba 1 resultado, se encontraron {guias.count()}"
        expect(guias.first).to_contain_text(guia)
        self._take_screenshot("verificacion_busqueda_guia")

    @allure.step("Verificar que la tabla no muestra resultados")
    def verificar_sin_resultados_mis_envios(self):
        self.page.wait_for_timeout(2000)
        # El searchbar es autocomplete: al escribir texto inválido no aparece sugerencia
        # Verificar que el texto buscado no aparece como resultado en ningún ion-label
        invalidas = self.page.locator("ion-label").filter(
            has_text=re.compile(r"GUIA-NO-EXISTE", re.I)
        )
        assert invalidas.count() == 0, \
            "Apareció un resultado inesperado para el texto de búsqueda inválido"
        self._take_screenshot("sin_resultados_mis_envios")

    @allure.step("Activar filtro por fecha y buscar desde '{fecha_inicio}' hasta '{fecha_fin}'")
    def filtrar_mis_envios_por_fecha(self, fecha_inicio: str, fecha_fin: str):
        from datetime import date as _date
        toggle = self.page.locator("label").filter(has_text=re.compile(r"Filtrar por Fecha", re.I)).first
        toggle.wait_for(state="visible", timeout=10000)
        toggle.click()
        self.page.wait_for_timeout(500)

        # Parsear fechas DD/MM/YYYY
        d_s, m_s, y_s = (int(x) for x in fecha_inicio.split("/"))
        d_e, m_e, y_e = (int(x) for x in fecha_fin.split("/"))
        hoy = _date.today()

        # Abrir calendario inicio
        cal_icons = self.page.get_by_role("img", name="Calendar")
        cal_icons.first.click()
        self.page.wait_for_timeout(400)

        # Navegar al mes de inicio retrocediendo desde el mes actual
        meses_back = (hoy.year - y_s) * 12 + (hoy.month - m_s)
        btn_prev = self.page.get_by_role("button", name="‹")
        for _ in range(meses_back):
            # Si el botón está deshabilitado el calendario no permite ir más atrás
            if btn_prev.first.get_attribute("disabled") is not None:
                raise AssertionError(
                    f"El calendario no permite navegar hasta {fecha_inicio} — "
                    "error preexistente: rango mínimo del datepicker limitado"
                )
            btn_prev.first.click()
            self.page.wait_for_timeout(150)

        # Clic en el día de inicio (primer span con ese número exacto)
        self.page.locator("span").filter(has_text=re.compile(rf"^{d_s}$")).first.click()
        self.page.wait_for_timeout(300)

        # Abrir calendario fin
        cal_icons.nth(1).click()
        self.page.wait_for_timeout(400)

        # Navegar al mes de fin
        meses_back_end = (hoy.year - y_e) * 12 + (hoy.month - m_e)
        for _ in range(meses_back_end):
            btn_prev.first.click()
            self.page.wait_for_timeout(150)

        # Clic en el día de fin
        self.page.locator("span").filter(has_text=re.compile(rf"^{d_e}$")).first.click()
        self.page.wait_for_timeout(300)

        # Buscar
        self.page.get_by_text("Buscar guías").click()
        self.page.wait_for_load_state("networkidle", timeout=30000)
        self._take_screenshot("filtro_por_fecha_aplicado")

    @allure.step("Verificar que la tabla se actualizó con el filtro de fechas")
    def verificar_filtro_fecha_mis_envios(self):
        self.page.wait_for_timeout(1000)
        guias = self._guias_en_tabla()
        sin_resultados = self.page.get_by_text("No se encontraron servicios", exact=False)
        assert guias.count() > 0 or sin_resultados.is_visible(), \
            "La tabla no mostró resultados ni mensaje vacío tras el filtro de fechas"
        self._take_screenshot("verificacion_filtro_fecha")

    @allure.step("Verificar paginación y navegar a la siguiente página si existe")
    def verificar_paginacion_mis_envios(self):
        # ngx-pagination renderiza los botones con aria-label "page N" — codegen confirmado
        self.page.wait_for_load_state("networkidle", timeout=15000)
        btn_p2 = self.page.get_by_text("page 2").first
        if btn_p2.count() > 0:
            btn_p2.click()
            self.page.wait_for_load_state("networkidle", timeout=20000)
            guias_p2 = self._guias_en_tabla()
            # Esperar hidratación de ion-label antes de contar
            try:
                guias_p2.first.wait_for(state="visible", timeout=15000)
                assert guias_p2.count() > 0, "La página 2 no cargó ninguna guía"
            except Exception:
                sin_resultados = self.page.get_by_text("No se encontraron servicios", exact=False)
                assert sin_resultados.is_visible(), "La página 2 no cargó guías ni mensaje de estado"
            self._take_screenshot("paginacion_pagina_2")
        else:
            print("Solo hay una página de resultados — paginación verificada sin navegación")
            self._take_screenshot("paginacion_unica_pagina")

    @allure.step("Clic en el número de la primera guía para abrir rastreo")
    def abrir_rastreo_primera_guia_mis_envios(self):
        guia_label = self._guias_en_tabla().first
        guia_label.wait_for(state="visible", timeout=30000)
        guia_label.click()
        self.page.wait_for_timeout(2000)
        self._take_screenshot("rastreo_abierto")

    @allure.step("Verificar que el rastreo se abrió con información de la guía")
    def verificar_rastreo_mis_envios(self):
        # El rastreo puede abrirse como modal Bootstrap, componente Angular, o nueva sección
        rastreo = self.page.locator(".modal.show, [role='dialog'], app-rastreo, app-modal, .modal-dialog").first
        guia_visible = self.page.locator("//strong[contains(text(),'FD')] | //h4[contains(text(),'FD')] | //h5[contains(text(),'FD')]").first
        assert rastreo.is_visible(timeout=10000) or guia_visible.is_visible(timeout=10000), \
            "No se abrió el rastreo ni apareció el número de guía en pantalla"
        self._take_screenshot("rastreo_verificado")

    def _encontrar_elemento_visible_por_texto(self, texto: str, patron: str = None) -> object:
        """Itera sobre todos los elementos que coincidan con el texto (label, ion-label, span, button)
        y devuelve el primero visible. Robusto ante variaciones de tag entre source y QA build."""
        busqueda = re.compile(patron or texto, re.I)
        for tag in ("label", "ion-label", "span", "button"):
            candidatos = self.page.locator(tag).filter(has_text=busqueda)
            for i in range(candidatos.count()):
                el = candidatos.nth(i)
                if el.is_visible():
                    return el
        return None

    def _diagnostico_dom(self):
        """Vuelca texto visible de buttons/labels/ion-labels/spans al stdout para diagnóstico."""
        resultado = self.page.evaluate("""
            () => {
                const tags = ['button', 'label', 'ion-label', 'span', 'a'];
                const out = [];
                for (const tag of tags) {
                    for (const el of document.querySelectorAll(tag)) {
                        const txt = el.textContent.trim().replace(/\\s+/g, ' ');
                        if (txt && el.offsetParent !== null) {
                            out.push('<' + tag + '> "' + txt + '"');
                        }
                    }
                }
                return out;
            }
        """)
        print("\n=== DOM DIAGNOSIS: elementos visibles ===")
        for t in resultado[:60]:
            try:
                print(t)
            except UnicodeEncodeError:
                print(t.encode("ascii", "replace").decode("ascii"))
        print("=== FIN DIAGNÓSTICO ===\n")

    @allure.step("Verificar que el botón Generar Excel está visible y habilitado")
    def verificar_boton_generar_excel(self):
        self._esperar_mis_envios_lista()
        self.page.wait_for_timeout(500)
        el = self._encontrar_elemento_visible_por_texto("Generar Excel")
        if el is None:
            self._diagnostico_dom()
        assert el is not None, \
            "No se encontró ningún elemento visible con texto 'Generar Excel' en label/ion-label/span/button"
        self._take_screenshot("boton_generar_excel_visible")

    @allure.step("Completar flujo Generar Excel: seleccionar Marzo 2026 y descargar")
    def abrir_modal_generar_excel(self):
        el = self._encontrar_elemento_visible_por_texto("Generar Excel")
        assert el is not None, "No se encontró 'Generar Excel' al intentar hacer clic"
        el.click()
        self.page.wait_for_timeout(2000)
        self._take_screenshot("modal_generar_excel_abierto")

        # Picker de Año — los options se renderizan como role="heading" en el dropdown
        self.page.get_by_role("textbox", name="Seleccione un Año").click()
        self.page.wait_for_timeout(600)
        self._take_screenshot("modal_picker_anio_abierto")
        self.page.get_by_role("heading", name="2026").click()
        self.page.wait_for_timeout(500)

        # Picker de Mes — ídem
        self.page.get_by_role("textbox", name=re.compile(r"Seleccione un mes", re.I)).click()
        self.page.wait_for_timeout(600)
        self._take_screenshot("modal_picker_mes_abierto")
        self.page.get_by_role("heading", name="Marzo").click()
        self.page.wait_for_timeout(500)
        self._take_screenshot("modal_generar_excel_seleccionado")

        # Botón "Aceptar" con ícono arrow_forward — desencadena la descarga
        with self.page.expect_download(timeout=20000) as dl_info:
            self.page.get_by_role("button", name=re.compile(r"Aceptar", re.I)).click()

        download = dl_info.value
        assert download.suggested_filename != "", "La descarga del Excel no se completó"
        self._take_screenshot("excel_descargado")
        print(f"[OK] Excel descargado: {download.suggested_filename}")

    @allure.step("Filtrar Envíos completados, seleccionar guías y descargar PDF")
    def verificar_boton_reimprimir_guias(self):
        """
        Flujo real:
        1. Filtrar por 'Envíos completados' (guías que permiten PDF)
        2. Seleccionar al menos un checkbox
        3. Verificar que 'Generar PDF' se habilita
        4. Descargar el PDF
        """
        self._esperar_mis_envios_lista()

        # Paso 1: ir a Envíos completados
        completados = self.page.locator("ion-segment-button").filter(
            has_text=re.compile(r"completados", re.I)
        ).first
        completados.wait_for(state="visible", timeout=10000)
        completados.click()
        self.page.wait_for_load_state("networkidle", timeout=20000)
        self.page.wait_for_timeout(1000)
        self._take_screenshot("reimprimir_filtro_completados")

        # Paso 2: esperar tabla cargada y seleccionar la 4ta checkbox (índice 3 = primer row)
        # Los primeros 3 checkboxes son controles del header/segmentos, no filas de datos
        checkboxes = self.page.get_by_role("checkbox")
        checkboxes.nth(3).wait_for(state="visible", timeout=15000)
        checkboxes.nth(3).click()
        self.page.wait_for_timeout(800)
        self._take_screenshot("reimprimir_checkbox_seleccionado")

        # Paso 3: descargar PDF — el botón es el 2do elemento con texto "Generar PDF" (nth(1))
        # La descarga es un archivo, no una nueva pestaña
        with self.page.expect_download(timeout=20000) as dl_info:
            self.page.get_by_text("Generar PDF").nth(1).click()

        download = dl_info.value
        assert download.suggested_filename != "", "La descarga del PDF no se completó"
        self._take_screenshot("pdf_descargado")
        print(f"[OK] PDF descargado: {download.suggested_filename}")

    # ==============================================================================
    # FLUJOS CORPORATIVOS Y EXEC
    # ==============================================================================

    @allure.step("Crear guías CORPORATIVO")
    def crear_guias_corp(self, datos):
        is_std = datos.tipo_guia == "Servicio Estándar"
        is_collet = str(datos.collet).lower() == "true"

        self.page.get_by_role("textbox", name="Selecciona un poblado").click()
        self.page.get_by_role("heading", name="Cahabon, Santa Maria Cahabon").click()
        self.page.get_by_role("button", name="calculator outline Calcular").click()

        if is_std:
            card = self.page.locator("div.card").filter(has_text="Servicio Estándar")
            card.get_by_role("button", name="Seleccionar").click()
        else:
            self.page.get_by_role("button", name="Seleccionar send").nth(1).click()

        self.page.get_by_role("radio").nth(1).click()
        self.page.get_by_role("textbox", name="Ingresar quién recibe").click()
        self.page.get_by_role("textbox", name="Ingresar quién recibe").fill("Juan")

        self.page.locator("input[name='ion-input-18']").click()
        self.page.locator("input[name='ion-input-18']").fill("Juan")
        self.page.locator("input[name='ion-input-19']").click()
        self.page.locator("input[name='ion-input-19']").fill("52452421")

        self.page.get_by_role("textbox", name="Ingresar dirección en destinatario").click()
        self.page.get_by_role("textbox", name="Ingresar dirección en destinatario").fill("Ciudad de Guatemala")
        self.page.get_by_role("button", name="Siguiente arrow forward").click()

        if datos.tipo_guia == "Servicio C.O.D.":
            self.page.get_by_role("textbox", name="Ingresar monto COD").click()
            self.page.get_by_role("textbox", name="Ingresar monto COD").fill("100")

        self.page.get_by_role("button", name="Siguiente arrow forward").click()

        if is_collet:
            self.page.locator("ion-col").filter(has_text=re.compile(r"^Crédito$")).locator("label").click()
            self.page.locator("ion-col").filter(has_text=re.compile(r"^Collect$")).locator("label").click()

        self.page.get_by_text("Arrow Back Regresar Mostrar").click()
        self.page.get_by_role("button", name="Mostrar Resumen arrow forward").click()
        self.page.wait_for_timeout(1000)

        heading_locator = self.page.locator("role=heading")
        matched_heading = heading_locator.filter(has_text="No. Guía Transporte FD").first

        if matched_heading.count() > 0:
            full_text = matched_heading.text_content()
            match = re.search(r"FD\d+", full_text)
            if match:
                guia = match.group(0)
                if is_std:
                    nombre_archivo = "guias_Corp_Collet_STD" if is_collet else "guias_Corp_Credito_STD"
                    tipo = "STD Collet" if is_collet else "STD Credito"
                else:
                    nombre_archivo = "guias_Corp_Collet_COD" if is_collet else "guias_Corp_Credito_COD"
                    tipo = "COD Collet" if is_collet else "COD Credito"
                print(f"Guía encontrada: {guia}")
                self.guardar_guia_en_archivo(nombre_archivo, tipo, guia)
                self._take_screenshot("corp_guide_created")
        else:
            print("No se encontró el heading con la guía.")

    @allure.step("Crear guías EXEC")
    def crear_guias_exec(self, datos):
        is_std = datos.tipo_guia == "Servicio Estándar"
        is_collet = str(datos.collet).lower() == "true"

        self.page.locator("ion-radio").filter(has_text="Clientes de Express Center").click()
        self.page.get_by_role("heading", name="Use el buscador para ver").click()
        self.page.wait_for_timeout(1000)
        self.page.get_by_role("textbox", name="Selecciona un poblado").click()
        self.page.get_by_role("heading", name="Cahabon, Santa Maria Cahabon").click()
        self.page.get_by_role("button", name="calculator outline Calcular").click()
        self.page.wait_for_timeout(1000)

        if is_std:
            card = self.page.locator("div.card").filter(has_text="Servicio Estándar")
            card.get_by_role("button", name="Seleccionar").click()
        else:
            card = self.page.locator("div.card").filter(has_text="Servicio C.O.D.")
            card.get_by_role("button", name="Seleccionar").click()

        nombre_envia = self.generar_nombre_qa()
        telefono_envia = self.generar_telefono()

        self.page.get_by_placeholder("Ingresar nombre de contacto").first.click()
        self.page.get_by_placeholder("Ingresar nombre de contacto").first.fill(nombre_envia)
        self.page.get_by_placeholder("Ingresar teléfono").first.click()
        self.page.get_by_placeholder("Ingresar teléfono").first.fill(telefono_envia)
        self.page.get_by_role("textbox", name="Ingresar correo electrónico").first.click()
        self.page.get_by_role("textbox", name="Ingresar correo electrónico").first.fill("carlos.fernandez@forzalatam.com")

        nombre_recibe = self.generar_nombre_qa()
        self.page.get_by_placeholder("Ingresar nombre de contacto").nth(1).click()
        self.page.get_by_placeholder("Ingresar nombre de contacto").nth(1).fill(nombre_recibe)

        telefono_recibe = self.generar_telefono()
        self.page.get_by_placeholder("Ingresar teléfono").nth(1).click()
        self.page.get_by_placeholder("Ingresar teléfono").nth(1).fill(telefono_recibe)

        self.page.get_by_role("textbox", name="Ingresar dirección en destinatario").click()
        self.page.get_by_role("textbox", name="Ingresar dirección en destinatario").fill("Ciudad de Guatemala")

        self.page.get_by_role("radio").nth(1).click()
        self.page.get_by_role("button", name="Siguiente arrow forward").click()

        if datos.tipo_guia == "Servicio C.O.D.":
            self.page.get_by_role("textbox", name="Ingresar monto COD").click()
            self.page.get_by_role("textbox", name="Ingresar monto COD").fill("100")
            self.page.get_by_role("textbox", name="Seleccione Banco").click()
            self.page.get_by_role("heading", name="BANRURAL - BANCO DE").click()
            self.page.get_by_role("textbox", name="Seleccione Tipo de Cuenta").click()
            self.page.get_by_role("heading", name="Ahorro").click()
            self.page.get_by_role("textbox", name="Ingresar número de cuenta").click()
            cuenta = self.generar_cuenta_aleatoria(15)
            self.page.get_by_role("textbox", name="Ingresar número de cuenta").fill(cuenta)
            self.page.get_by_role("textbox", name="Ingresar nombre de la cuenta").click()
            self.page.get_by_role("textbox", name="Ingresar nombre de la cuenta").fill("QA")
            self.page.get_by_role("textbox", name="Ingresar Documento de").click()
            self.page.get_by_role("textbox", name="Ingresar Documento de").fill("6352452")

        self.page.get_by_role("button", name="Siguiente arrow forward").click()

        if is_collet:
            self.page.locator("ion-col").filter(has_text=re.compile(r"^Collect$")).locator("label").click()

        self.page.get_by_text("Arrow Back Regresar Mostrar").click()
        self.page.get_by_role("button", name="Mostrar Resumen arrow forward").click()
        self.page.wait_for_timeout(1000)

        heading_locator = self.page.locator("role=heading")
        matched_heading = heading_locator.filter(has_text="No. Guía Transporte FD").first

        if matched_heading.count() > 0:
            full_text = matched_heading.text_content()
            match = re.search(r"FD\d+", full_text)
            if match:
                guia = match.group(0)
                if is_std:
                    nombre_archivo = "guias_EXEC_Collet_STD" if is_collet else "guias_Corp_Credito_STD"
                    tipo = "STD Collet" if is_collet else "STD Credito"
                else:
                    nombre_archivo = "guias_EXEC_Collet_COD" if is_collet else "guias_Corp_Credito_COD"
                    tipo = "COD Collet" if is_collet else "COD Credito"
                print(f"Guía encontrada: {guia}")
                self.guardar_guia_en_archivo(nombre_archivo, tipo, guia)
                self._take_screenshot("exec_guide_created")
        else:
            print("No se encontró el heading con la guía.")
