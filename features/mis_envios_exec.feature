      # tst
      # language: es
      Característica: Mis Envíos - Portal Express Center (EXEC)
      Vertical: Delivery
      Producto: Hermes Portal - Módulo Mis Envíos EXC
      Release:
      Jira:
      Product Owner: Javier Santizo
      QA Lead: Andy Arevalo

      @mis_envios_carga_inicial
      Escenario: Carga de Mis Envíos tras login EXEC
      Dado el usuario selecciona la url del portal de forza "https://qa-portal.forzadeliveryexpress.com/" y el titulo de la pagina es "Hermes Web"
      Y el usuario selecciona el pais "Guatemala"
      Y el usuario ingresa la estacion "EXC BOSQUES DE SAN NICOLAS" el correo "x_nancy.gamez@forzadelivery.com" y su pass "qaqaqaqa"
      Entonces la pantalla Mis Envíos carga con datos en la tabla

      @mis_envios_filtros_estado
      Esquema del escenario: Filtro por estado en Mis Envíos
      Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
      Y el usuario selecciona el pais "<pais>"
      Y el usuario ingresa la estacion "<estacion>" el correo "<correo>" y su pass "<contrasenia>"
      Cuando el usuario aplica el filtro de estado "<estado>"
      Entonces la tabla de Mis Envíos refleja el filtro "<estado>"

      Ejemplos:
      | url                                          | titulo     | pais      | estacion                            | correo                          | contrasenia | estado              |
      | https://qa-portal.forzadeliveryexpress.com/  | Hermes Web | Guatemala | EXC BOSQUES DE SAN NICOLAS | x_nancy.gamez@forzadelivery.com | qaqaqaqa    | Todos               |
      | https://qa-portal.forzadeliveryexpress.com/  | Hermes Web | Guatemala | EXC BOSQUES DE SAN NICOLAS | x_nancy.gamez@forzadelivery.com | qaqaqaqa    | Envíos por realizar |
      | https://qa-portal.forzadeliveryexpress.com/  | Hermes Web | Guatemala | EXC BOSQUES DE SAN NICOLAS | x_nancy.gamez@forzadelivery.com | qaqaqaqa    | Envíos en proceso   |
      | https://qa-portal.forzadeliveryexpress.com/  | Hermes Web | Guatemala | EXC BOSQUES DE SAN NICOLAS | x_nancy.gamez@forzadelivery.com | qaqaqaqa    | Envíos completados  |

      @mis_envios_busqueda_guia
      Escenario: Búsqueda por número de guía muestra resultado único
      Dado el usuario selecciona la url del portal de forza "https://qa-portal.forzadeliveryexpress.com/" y el titulo de la pagina es "Hermes Web"
      Y el usuario selecciona el pais "Guatemala"
      Y el usuario ingresa la estacion "EXC BOSQUES DE SAN NICOLAS" el correo "x_nancy.gamez@forzadelivery.com" y su pass "qaqaqaqa"
      Cuando el usuario obtiene el numero de la primera guia de Mis Envíos
      Y el usuario busca en Mis Envíos por esa guia
      Entonces la tabla muestra unicamente esa guia en los resultados

      @mis_envios_busqueda_sin_resultados
      Escenario: Búsqueda con texto inexistente muestra estado vacío
      Dado el usuario selecciona la url del portal de forza "https://qa-portal.forzadeliveryexpress.com/" y el titulo de la pagina es "Hermes Web"
      Y el usuario selecciona el pais "Guatemala"
      Y el usuario ingresa la estacion "EXC BOSQUES DE SAN NICOLAS" el correo "x_nancy.gamez@forzadelivery.com" y su pass "qaqaqaqa"
      Cuando el usuario busca en Mis Envíos por texto "GUIA-NO-EXISTE-QA"
      Entonces la tabla de Mis Envíos no muestra resultados

      @mis_envios_filtro_fecha
      Escenario: Filtro por rango de fechas actualiza la tabla
      Dado el usuario selecciona la url del portal de forza "https://qa-portal.forzadeliveryexpress.com/" y el titulo de la pagina es "Hermes Web"
      Y el usuario selecciona el pais "Guatemala"
      Y el usuario ingresa la estacion "EXC BOSQUES DE SAN NICOLAS" el correo "x_nancy.gamez@forzadelivery.com" y su pass "qaqaqaqa"
      Cuando el usuario activa el filtro por fecha y busca desde "01/05/2025" hasta "31/05/2025"
      Entonces la tabla de Mis Envíos se actualiza con el rango de fechas

      @mis_envios_paginacion
      Escenario: Paginación navega a la página siguiente
      Dado el usuario selecciona la url del portal de forza "https://qa-portal.forzadeliveryexpress.com/" y el titulo de la pagina es "Hermes Web"
      Y el usuario selecciona el pais "Guatemala"
      Y el usuario ingresa la estacion "EXC BOSQUES DE SAN NICOLAS" el correo "x_nancy.gamez@forzadelivery.com" y su pass "qaqaqaqa"
      Entonces el usuario puede navegar entre páginas en Mis Envíos

      @mis_envios_rastreo
      Escenario: Clic en número de guía abre el rastreo
      Dado el usuario selecciona la url del portal de forza "https://qa-portal.forzadeliveryexpress.com/" y el titulo de la pagina es "Hermes Web"
      Y el usuario selecciona el pais "Guatemala"
      Y el usuario ingresa la estacion "EXC BOSQUES DE SAN NICOLAS" el correo "x_nancy.gamez@forzadelivery.com" y su pass "qaqaqaqa"
      Cuando el usuario hace clic en el número de la primera guía de Mis Envíos
      Entonces se abre el rastreo con información de la guía

      @mis_envios_generar_excel
      Escenario: Botón Generar Excel genera el reporte Excel de marzo 2026
      Dado el usuario selecciona la url del portal de forza "https://qa-portal.forzadeliveryexpress.com/" y el titulo de la pagina es "Hermes Web"
      Y el usuario selecciona el pais "Guatemala"
      Y el usuario ingresa la estacion "FD EXC INTERPLAZA CHIMALTENANGO" el correo "x_nelly.jimenez@forzadelivery.com" y su pass "qaqaqaqa"
      Entonces el botón Generar Excel está visible, habilitado y abre el modal al hacer clic

      @mis_envios_reimprimir_guias
      Escenario: Botón Generar PDF descarga PDF de guías completadas
      Dado el usuario selecciona la url del portal de forza "https://qa-portal.forzadeliveryexpress.com/" y el titulo de la pagina es "Hermes Web"
      Y el usuario selecciona el pais "Guatemala"
      Y el usuario ingresa la estacion "FD EXC INTERPLAZA CHIMALTENANGO" el correo "x_nelly.jimenez@forzadelivery.com" y su pass "qaqaqaqa"
      Entonces el botón Reimprimir Guías está deshabilitado inicialmente y se habilita al seleccionar una guía
