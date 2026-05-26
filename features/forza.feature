      # language: es
      @creacionGuias_COD_COLLET
      Característica: Creación de Guías en el Portal Forza

      Esquema del escenario: Portal Individual Guias COD Collet
      Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
      Y el usuario selecciona el pais "<pais>"
      Y el usuario ingresa el correo "<correo>" y el pass "<pass>"
      Y Datos necesarios para crear la guia con origen "<direccionnuevaOrigen>", destino "<direccionnuevaDestino>", tipo "<tipoGuia>", direccion "<NombreDireccion>", collet "<collet>" y tarjeta "<tarjeta>"
      Entonces el usuario indica la cantidad de guias a registrar <cantidad_guias>


      Ejemplos:
      | Escenario                      | url                                  | titulo     | pais      | correo                             | pass        | cantidad_guias | direccionnuevaOrigen | direccionnuevaDestino | tipoGuia        | NombreDireccion                                    | collet | tarjeta                     |
      | COD-Collet-reutili-direcciones | https://qa.portal.forzadelivery.com/ | Hermes Web | Guatemala | carlos.fernandez.gt@forzalatam.com | 12345678Ca@ | 1              | false                | false                 | Servicio C.O.D. | Qa Destino - 63254212 - Ciudad De Guatemala Zona 1 | true   | Qa No Usar - N/a - Xxxx5422 |

      @recoleccion_visita_fallida
      Esquema del escenario: App Courier Recoleccion con Visita Fallida
      Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
      Y Usuario selecciona el pais courier "<pais>"
      Y Usuario abre el portal de forza e ingresa este telefono "<telefono>"
      Cuando Usuario abre la recoleccion pendiente en posicion <posicion>
      Y Usuario reporta visita fallida con imagen "<ruta_imagen>"
      Entonces Usuario valida el mensaje de visita fallida "<mensaje_exitoso>"

      Ejemplos:
      | Escenario           | url                                      | titulo     | pais      | telefono | posicion | ruta_imagen                   | mensaje_exitoso                                      |
      | visita-fallida-pos1 | https://qa-pod.forzadeliveryexpress.com/ | CourierApp - Forza Delivery | Guatemala | 45785994 | 1        | data/evidencia_visita.jpg     | Reporte de visita fallida registrado exitosamente.   |
