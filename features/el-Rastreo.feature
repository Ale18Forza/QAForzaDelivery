# language: es
@el_rastreo
Característica: Rastreo de Guías en Portal Express Center (EXEC)
Vertical: Delivery
Producto: Hermes Portal - Rastreo de Guías Express Center UI
Release:
Jira:
Product Owner:
QA Lead: Marko

#@el_rastreo
#Escenario: Rastreo de una guía en EXEC usando número fijo
#  Dado el usuario selecciona la url del portal de forza "https://qa-portal.forzadeliveryexpress.com/" y el titulo de la pagina es "Hermes Web"
#  Y el usuario selecciona el pais "Guatemala"
#  Y el usuario ingresa la estacion "FD EXC JUTIAPA" el correo "x_LILIAN.GARCIA@FORZADELIVERY.COM" y su pass "qaqaqaqa"
#  Y el usuario selecciona la opcion Rastreo
#  Cuando el usuario ingresa el numero de guia "30775684"
#  Y el usuario hace click en el boton RASTREAR

Esquema del escenario: Rastreo de una guía en EXEC usando número fijo
  Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
  Y el usuario selecciona el pais "<pais>"
  Y el usuario ingresa la estacion "<estacion>" el correo "<correo>" y su pass "<pass>"
  Y el usuario selecciona la opcion "<opcion>"  
  Y el usuario ingresa el numero de guia "<numero_guia>"
  Entonces el usuario hace click en el boton RASTREAR

  Ejemplos:
    | Escenario      | url                                         | titulo     | pais      | estacion       | correo                            | pass     | opcion  | numero_guia |
    | Rastreo-guia   | https://qa-portal.forzadeliveryexpress.com/ | Hermes Web | Guatemala | FD EXC JUTIAPA | x_LILIAN.GARCIA@FORZADELIVERY.COM | qaqaqaqa | Rastreo | 30775684    |
