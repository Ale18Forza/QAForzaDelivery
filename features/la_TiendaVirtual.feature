# language: es
@tv_abre-sitio
Característica: Abrir el sitio de la tienda virtual (TV)
Vertical: Delivery
Producto: Forza Delivery Express - Tienda Vrtual UI
Release:
Jira:
Product Owner:
QA Lead: Marko.


Esquema del escenario: Abre el sitio de la tienda virtual sin iniciar sesión
  Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
  Y el usuario selecciona el pais "<pais>"
  Y el usuario hace clic en el elemento con title "Iniciar Sesión"
  Y el usuario ingresa correo "<correo>" y pass "<pass>"
  Entonces el usuario valida que la sesión quedó iniciada

  Ejemplos:
    | Escenario       | url                                                   | titulo                 | pais      | correo                          | pass         |
    | Abre-sitio-tv   | https://qa-tienda.forzadeliveryexpress.com/bienvenida | Forza Delivery Express | Guatemala | marco.monterroso@forzalatam.com | LatamForza5* |


@tv_login_fallido
Esquema del escenario: Valida que la sesión no se pudo iniciar en tienda virtual
  Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
  Y el usuario selecciona el pais "<pais>"
  Y el usuario hace clic en el elemento con title "Iniciar Sesión"
  Y el usuario ingresa correo "<correo>" y pass "<pass>"
  Entonces el usuario valida que la sesión no quedó iniciada

  Ejemplos:
    | Escenario              | url                                                   | titulo                 | pais      | correo                             | pass         |
    | Login-no-iniciado-tv   | https://qa-tienda.forzadeliveryexpress.com/bienvenida | Forza Delivery Express | Guatemala | marco.monterroso@forzalatam.com    | Forza5* |


@tv_carrito_en_cero
Esquema del escenario: Valida que el botón Siguiente está inhabilitado con carrito en cero
  Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
  Y el usuario selecciona el pais "<pais>"
  Y el usuario elige elemento carrito si el valor = 0
  Entonces el usuario valida que el botón "Siguiente" está inhabilitado

  Ejemplos:
    | Escenario                  | url                                                   | titulo                 | pais      |
    | Carrito-en-cero-siguiente  | https://qa-tienda.forzadeliveryexpress.com/bienvenida | Forza Delivery Express | Guatemala |


@tv_dropdown_paises_dom
Esquema del escenario: Valida en DOM el dropdown de países en tienda virtual
  Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
  Y el usuario selecciona el pais "<pais>"
  Cuando el usuario abre el dropdown de pais en tienda virtual
  Entonces el usuario valida en el DOM que el dropdown de pais contiene Guatemala, Honduras y El Salvador

  Ejemplos:
    | Escenario                  | url                                                   | titulo                 | pais      |
    | Dropdown-paises-tv-en-dom  | https://qa-tienda.forzadeliveryexpress.com/bienvenida | Forza Delivery Express | Guatemala |

