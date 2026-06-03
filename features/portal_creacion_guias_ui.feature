      # language: es
      @creacionGuias_COD_COLLET
      Característica: Creación de Guías en el Portal Forza
        Vertical: Delivery
        Producto: Hermes Portal - Creacion de Guias UI
        Release:
        Jira:
        Product Owner:
        QA Lead: Carlos Gonzalez

      Esquema del escenario: Portal Individual Guias COD Collet
      Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
      Y el usuario selecciona el pais "<pais>"
      Y el usuario ingresa el correo "<correo>" y el pass "<pass>"
      Y Datos necesarios para crear la guia con origen "<direccionnuevaOrigen>", destino "<direccionnuevaDestino>", tipo "<tipoGuia>", direccion "<NombreDireccion>", collet "<collet>" y tarjeta "<tarjeta>"
      Entonces el usuario indica la cantidad de guias a registrar <cantidad_guias>


      Ejemplos:
      | Escenario                      | url                                  | titulo     | pais      | correo                             | pass        | cantidad_guias | direccionnuevaOrigen | direccionnuevaDestino | tipoGuia        | NombreDireccion                                    | collet | tarjeta                     |
      | COD-Collet-reutili-direcciones | https://qa.portal.forzadelivery.com/ | Hermes Web | Guatemala | carlos.fernandez.gt@forzalatam.com | 12345678Ca@ | 1              | false                | false                 | Servicio C.O.D. | Qa Destino - 63254212 - Ciudad De Guatemala Zona 1 | true   | Qa No Usar - N/a - Xxxx5422 |