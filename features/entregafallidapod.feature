            # language: es
            @visita_fallida
            Característica: Registro de visita fallida Courier App

            Esquema del escenario: Registrar visita fallida exitosamente
            Dado El usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
            Y el usuario selecciona el pais "<pais>"
            Y el entorno es "<entorno>"
            Y Usuario abre el portal de forza e ingresa este telefono "<telefono>"
            Cuando el usuario selecciona una entrega pendiente
            Y el usuario selecciona la opcion visita fallida
            Y el usuario selecciona una razon aleatoria de visita fallida
            Y el usuario ingresa un comentario de incidencia
            Y el usuario adjunta una fotografia

            Entonces el usuario envia la visita fallida exitosamente

            Ejemplos:
            | Caso | telefono | url                                      | titulo                      | pais      | entorno |
            | 1    | 59629380 | https://qa-pod.forzadeliveryexpress.com/ | CourierApp - Forza Delivery | Guatemala | QAAWS   |


