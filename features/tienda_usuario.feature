# language: es

Característica: Tienda Usuario

      @tienda_usuario @tienda_usuario_gt
      Esquema del escenario: Compra de membresia Club Forza en tienda GT
      Dado el usuario abre la tienda "<url>"
      Y el usuario inicia sesion en tienda con correo "<correo>" y pass "<contrasenia>"
      Cuando el usuario compra la membresia "<producto>" con facturacion "<facturacion>" y metodo de pago "<metodo_pago>"
      Entonces el usuario valida que la compra en tienda fue realizada

      Ejemplos:
      | Escenario                    | url                                          | correo                | contrasenia                | producto   | facturacion | metodo_pago |
      | gt_tienda_club_forza_tarjeta | https://qa-tienda.forzadeliveryexpress.com/GT | ENV:TIENDA_GT_USUARIO | ENV:TIENDA_GT_CONTRASENIA | Club Forza | CF          | Tarjeta     |
