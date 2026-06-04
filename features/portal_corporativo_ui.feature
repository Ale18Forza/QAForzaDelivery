      # language: es
      Característica: Creación de Guías en Portal Corporativo
        Vertical: Delivery
        Producto: Hermes Portal - Creacion de Guias Portal Corporativo UI
        Release:
        Jira:
        Product Owner:
        QA Lead: Carlos Gonzalez

      @creacionGuias_COD_COLLET_corporativo
      Esquema del escenario: Portal Corporativo Guias COD
      Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
      Y el usuario selecciona el pais "<pais>"
      Y el usuario ingresa el codigo "<codigo>" el usuario "<usuario>" y su pass "<contrasenia>"
      Y el usuario selecciona la opcion pare crear guias
      Y datos corp para crear guia tipo "<tipo_guia>" collet "<collet>"
      Entonces el usuario inicia el proceso de creacion de guias

      Ejemplos:
      | Escenario               | url                               | titulo     | pais      | codigo | usuario      | contrasenia | tipo_guia       | collet |
      | COD-Collet-corporativo  | https://portal.forzadelivery.com/ | Hermes Web | Guatemala | 103492 | nidias.lucys | qaqaqaqa    | Servicio C.O.D. | true   |
      | COD-Credito-corporativo | https://portal.forzadelivery.com/ | Hermes Web | Guatemala | 103492 | nidias.lucys | qaqaqaqa    | Servicio C.O.D. | false  |

      @creacionGuias_STD_corporativo
      Esquema del escenario: Portal Corporativo Guias STD
      Dado el usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
      Y el usuario selecciona el pais "<pais>"
      Y el usuario ingresa el codigo "<codigo>" el usuario "<usuario>" y su pass "<contrasenia>"
      Y el usuario selecciona la opcion pare crear guias
      Y datos corp para crear guia tipo "<tipo_guia>" collet "<collet>"
      Entonces el usuario inicia el proceso de creacion de guias

      Ejemplos:
      | Escenario               | url                               | titulo     | pais      | codigo | usuario      | contrasenia | tipo_guia         | collet |
      | STD-Collet-corporativo  | https://portal.forzadelivery.com/ | Hermes Web | Guatemala | 103492 | nidias.lucys | qaqaqaqa    | Servicio Estándar | true   |
      | STD-Credito-corporativo | https://portal.forzadelivery.com/ | Hermes Web | Guatemala | 103492 | nidias.lucys | qaqaqaqa    | Servicio Estándar | false  |
