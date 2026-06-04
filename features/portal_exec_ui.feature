      # language: es
      Característica: Creación de Guías en Portal Express Center (EXEC)
      Vertical: Delivery
      Producto: Hermes Portal - Creacion de Guias Express Center UI
      Release:
      Jira:
      Product Owner:
      QA Lead: Carlos Gonzalez

      @creacionGuias_COD_COLLET_EXEC
      Esquema del escenario: Portal EXEC Guias COD
      Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
      Y el usuario selecciona el pais "<pais>"
      Y el usuario ingresa la estacion "<estacion>" el correo "<correo>" y su pass "<contrasenia>"
      Y el usuario selecciona la opcion pare crear guias
      Y datos exec para crear guia tipo "<tipo_guia>" collet "<collet>"
      Entonces el usuario inicia el proceso de creacion de guias en EXEC

      Ejemplos:
      | Escenario       | url                                         | titulo     | pais      | estacion       | correo                            | contrasenia | tipo_guia       | collet |
      | COD-Collet-EXEC | https://qa-portal.forzadeliveryexpress.com/ | Hermes Web | Guatemala | FD EXC JUTIAPA | x_LILIAN.GARCIA@FORZADELIVERY.COM | qaqaqaqa    | Servicio C.O.D. | true   |

      @creacionGuias_STD_EXEC
      Esquema del escenario: Portal EXEC Guias STD
      Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
      Y el usuario selecciona el pais "<pais>"
      Y el usuario ingresa la estacion "<estacion>" el correo "<correo>" y su pass "<contrasenia>"
      Y el usuario selecciona la opcion pare crear guias
      Y datos exec para crear guia tipo "<tipo_guia>" collet "<collet>"
      Entonces el usuario inicia el proceso de creacion de guias en EXEC

      Ejemplos:
      | Escenario       | url                                         | titulo     | pais      | estacion       | correo                            | contrasenia | tipo_guia         | collet |
      | STD-Collet-EXEC | https://qa-portal.forzadeliveryexpress.com/ | Hermes Web | Guatemala | FD EXC JUTIAPA | x_LILIAN.GARCIA@FORZADELIVERY.COM | qaqaqaqa    | Servicio Estándar | true   |
