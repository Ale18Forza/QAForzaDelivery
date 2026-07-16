# language: es

Característica: Tienda Usuario

      @tienda_usuario @tienda_usuario_gt
      Esquema del escenario: Compra de membresia Club Forza en tienda GT
      Dado el usuario abre la tienda "<url>" y selecciona el pais "<pais>"
      Y el usuario inicia sesion en tienda con correo "<correo>" y pass "<contrasenia>"
      Cuando el usuario compra la membresia "<producto>" con facturacion "<facturacion>" y metodo de pago "<metodo_pago>"
      Entonces el usuario valida que la compra en tienda fue realizada

      Ejemplos:
      | Escenario                    | url                                      | pais      | correo                | contrasenia                | producto   | facturacion | metodo_pago |
      | gt_tienda_club_forza_tarjeta | https://qa-tienda.forzadeliveryexpress.com | Guatemala | ENV:TIENDA_GT_USUARIO | ENV:TIENDA_GT_CONTRASENIA | Club Forza | CF          | Tarjeta     |

      @tienda_usuario @tienda_usuario_hn
      Esquema del escenario: Compra de paquete de guias prepago en tienda HN
      Dado el usuario abre la tienda "<url>" y selecciona el pais "<pais>"
      Y el usuario inicia sesion en tienda con correo "<correo>" y pass "<contrasenia>"
      Cuando el usuario compra la membresia "<producto>" con facturacion "<facturacion>" y metodo de pago "<metodo_pago>"
      Entonces el usuario valida que la compra en tienda fue realizada

      Ejemplos:
      | Escenario                       | url                                      | pais     | correo                | contrasenia                | producto       | facturacion | metodo_pago |
      | hn_tienda_guias_prepago_tarjeta | https://qa-tienda.forzadeliveryexpress.com | Honduras | ENV:TIENDA_HN_USUARIO | ENV:TIENDA_HN_CONTRASENIA | Paquete MICRO | CF          | Tarjeta     |
