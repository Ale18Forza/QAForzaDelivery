            # language: es
            @servicio_entrega_exc
            Característica: Registro de servicio entrega desde express center

            Esquema del escenario: Registrar recoleccion en sitio exitosa
            Dado El usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
            Y el usuario selecciona el pais "<pais>"
            Y el entorno es "<entorno>"
            Y el usuario ingresa la estacion "<Estación>" el correo "<Correo Electrónico>" y su pass "<Contraseña>"
            Cuando el usuario selecciona la opcion servicios
            Y el usuario selecciona la opcion servicio entrega
            Y el usuario carga una guia pendiente de entrega
            Y el usuario presiona el boton agregar
            Y el usuario presiona el boton continuar
            Y el usuario ingresa el nombre del cliente
            Y el usuario ingresa el dpi
            Y el usuario ingresa el nit
            Y el usuario ingresa el nombre
            Y el usuario ingresa la direccion
            Y el usuario ingresa el correo electronico
            Y el usuario finaliza la entrega
            Entonces el sistema registra la entrega completada exitosamente

            Ejemplos:
            | Caso | Estación                 |Correo Electrónico              |Contraseña| url                                                | titulo     | pais      | entorno |
            | 1    | FD CNC SAN ANDRES ITZAPA |x_fredy.roquel@forzadelivery.com|qaqaqaqa  |https://qa-portal.forzadeliveryexpress.com/login-exc| Hermes Web | Guatemala | QAAWS   |


