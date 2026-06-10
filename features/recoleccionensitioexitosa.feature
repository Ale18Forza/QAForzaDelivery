            # language: es
            @recoleccion_sitio_exitosa
            Característica: Registro de recoleccion en sitio exitosa en Courier App

            Esquema del escenario: Registrar recoleccion en sitio exitosa
            Dado El usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
            Y el usuario selecciona el pais "<pais>"
            Y el entorno es "<entorno>"
            Y Usuario abre el portal de forza e ingresa este telefono "<telefono>"
            Cuando el usuario selecciona el boton de recoleccion en sitio
            Y el usuario carga una guia pendiente de recoleccion
            Y el usuario agrega la guia al lote
            Y el usuario presiona el boton siguiente
            Y el usuario completa la firma del cliente
            Y el usuario finaliza la recoleccion
            Entonces el sistema registra la recoleccion exitosamente
            

            Ejemplos:
            | Caso | telefono | url                                      | titulo                      | pais      | entorno |
            | 1    | 59629380 | https://qa-pod.forzadeliveryexpress.com/ | CourierApp - Forza Delivery | Guatemala | QAAWS   |


