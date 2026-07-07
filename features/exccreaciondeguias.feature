      # language: es
      @creacion_guias_exc
      Característica: Registro de creación de guías Estándar en Express Center

      Esquema del escenario: Registrar servicio entrega express center
      Dado El usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
      Y el usuario selecciona el pais "<pais>"
      Y el entorno es "<entorno>"
      Y el usuario ingresa la estacion "<Estacion>" el correo "<CorreoElectronico>" y su pass "<Contrasena>"
      
      Cuando el usuario selecciona la opción Crear Guías
      Y el usuario selecciona el poblado "<Poblado>"
      Y el usuario selecciona "<CantidadPaquetes>" paquete
      Y el usuario presiona el botón Calcular
      Y el usuario presiona el botón Seleccionar para confirmar el servicio
      Y el usuario ingresa el nombre remitente "<NombreRemitente>"
      Y el usuario ingresa el teléfono remitente "<TelefonoRemitente>"
      Y el usuario ingresa el correo remitente "<CorreoRemitente>"
      Y el usuario selecciona el tipo de destinatario "<TipoDestinatario>"
      Y el usuario ingresa el nombre destinatario "<NombreDestinatario>"
      Y el usuario ingresa el teléfono destinatario "<TelefonoDestinatario>"
      Y el usuario ingresa el correo destinatario "<CorreoDestinatario>"
      Y el usuario ingresa la dirección destinatario "<DireccionDestinatario>"
      Y el usuario presiona el botón Siguiente
      Y el usuario presiona el botón Siguiente nuevamente
      Y el usuario selecciona forma de pago "Efectivo"
      Y el usuario presiona el botón Mostrar Resumen
      Y el usuario presiona el botón Mis envíos
      Entonces el sistema registra la guía creada exitosamente

      Ejemplos:
        | Caso | url                                                  | titulo     | pais      | entorno | Estacion                 | CorreoElectronico                | Contrasena | Poblado                      | CantidadPaquetes | NombreRemitente | TelefonoRemitente | CorreoRemitente               | TipoDestinatario | NombreDestinatario | TelefonoDestinatario | CorreoDestinatario           | DireccionDestinatario |
        | STD  | https://qa-portal.forzadeliveryexpress.com/login-exc | Hermes Web | Guatemala | QA      | FD CNC SAN ANDRES ITZAPA | x_fredy.roquel@forzadelivery.com | qaqaqaqa   | Cahabon, Santa Maria Cahabon | 2                | Yeimi           | 59629380          | yeimi.gudiel@forzadelivery.com | Persona          | Yeimi01            | 59629380             | yeimi.destinatario@test.com  | ciudad                |



