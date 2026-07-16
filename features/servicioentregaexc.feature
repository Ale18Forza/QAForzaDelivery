            # language: es
            @servicio_entrega_exc
            Característica: Registro de servicio entrega desde express center
 
            Esquema del escenario: Registrar servicio entrega express center
            Dado El usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
            Y el usuario selecciona el pais "<pais>"
            Y el entorno es "<entorno>"
            Y el usuario ingresa la estacion "<Estación>" el correo "<Correo Electrónico>" y su pass "<Contraseña>"
            Cuando el usuario selecciona la opcion servicios
            Y el usuario selecciona la opcion servicio entrega
            Y el usuario carga una guia "<Guía>" pendiente de entrega
            Y el usuario presiona el boton agregar
            Y el usuario presiona el boton continuar
            Y el usuario ingresa el nombre del cliente "<nombre del cliente>"
            Y el usuario ingresa el dpi "<DPI>"
            Y el usuario ingresa el nit "<NIT>"
            Y el usuario ingresa el nombre "<Nombre>"
            Y el usuario ingresa la direccion "<Dirección>"
            Y el usuario ingresa el correo electronico del cliente "<Correo Electrónico cliente>"
            Y el usuario finaliza la entrega
            Entonces el sistema registra la entrega completada exitosamente
 
            Ejemplos:
            | Caso | Estación                 |Correo Electrónico              |Contraseña| url                                                | titulo     | pais      | entorno |nombre del cliente|DPI          |NIT|Nombre|Dirección|Correo Electrónico cliente    |Guía        |
            | 1    | FD CNC SAN ANDRES ITZAPA |x_fredy.roquel@forzadelivery.com|qaqaqaqa  |https://qa-portal.forzadeliveryexpress.com/login-exc| Hermes Web | Guatemala | QAAWS   | Liz              |2995237490203|CF |Liz   |Ciudad   |yeimi.gudiel@forzadelivery.com|FD30775620-1|

