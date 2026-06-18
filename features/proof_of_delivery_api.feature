Feature: Proof Of Delivery API
  Vertical: Delivery
  Producto: Hermes Portal - Proof of Delivery API
  Release:AGUST26
  Jira:https://cashlogisticsgroup.atlassian.net/browse/FDAPI-6287
  Product Owner: Braulio
  QA Lead: Carlos Gonzalez

  Background: Configurar ruta de templates
    Given La ruta de los request API es "Request_Plantilla/"

  @code_200 @proof_of_delivery_local
  Scenario Outline: Consulta de evidencia de entrega exitosa code 200
    Given El usuario consulta la evidencia de entrega API
      | request   | metodo   | staging   | CodApp   | SecretKey   | GuideSerie   | GuideNumber   | StatusCodeEsperado   | MensajeEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <GuideSerie> | <GuideNumber> | <StatusCodeEsperado> | <MensajeEsperado> |

    Examples:
      | Escenario | request                          | metodo          | staging                 | CodApp                   | SecretKey                        | GuideSerie | GuideNumber | StatusCodeEsperado | MensajeEsperado                |
      | exitoso   | plantilla_proof_of_delivery.json | ProofOfDelivery | http://localhost:59798/ | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | FD         | 30775749    | 200                | Operación realizada con éxito. |

  @code_409 @proof_of_delivery_local
  Scenario Outline: Consulta de evidencia de entrega - guia sin evidencia code 409
    Given El usuario consulta la evidencia de entrega API
      | request   | metodo   | staging   | CodApp   | SecretKey   | GuideSerie   | GuideNumber   | StatusCodeEsperado   | MensajeEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <GuideSerie> | <GuideNumber> | <StatusCodeEsperado> | <MensajeEsperado> |

    Examples:
      | Escenario     | request                          | metodo          | staging                 | CodApp                   | SecretKey                        | GuideSerie | GuideNumber | StatusCodeEsperado | MensajeEsperado                                                |
      | sin_evidencia | plantilla_proof_of_delivery.json | ProofOfDelivery | http://localhost:59798/ | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | FD         | 2390390     | 409                | No se encontró evidencia de entrega para la guía proporcionada |

  @code_404 @proof_of_delivery_local
  Scenario Outline: Consulta de evidencia de entrega - guia inexistente code 404
    Given El usuario consulta la evidencia de entrega API
      | request   | metodo   | staging   | CodApp   | SecretKey   | GuideSerie   | GuideNumber   | StatusCodeEsperado   | MensajeEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <GuideSerie> | <GuideNumber> | <StatusCodeEsperado> | <MensajeEsperado> |

    Examples:
      | Escenario   | request                          | metodo          | staging                 | CodApp                   | SecretKey                        | GuideSerie | GuideNumber | StatusCodeEsperado | MensajeEsperado                                   |
      | inexistente | plantilla_proof_of_delivery.json | ProofOfDelivery | http://localhost:59798/ | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | FD         | 99999999    | 404                | El número o serie de guía no existe en el sistema |

  @code_400 @proof_of_delivery_local
  Scenario Outline: Consulta de evidencia de entrega - parametros invalidos code 400
    Given El usuario consulta la evidencia de entrega API
      | request   | metodo   | staging   | CodApp   | SecretKey   | GuideSerie   | GuideNumber   | StatusCodeEsperado   | MensajeEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <GuideSerie> | <GuideNumber> | <StatusCodeEsperado> | <MensajeEsperado> |

    Examples:
      | Escenario   | request                          | metodo          | staging                 | CodApp                   | SecretKey                        | GuideSerie | GuideNumber | StatusCodeEsperado | MensajeEsperado                                            |
      | serie_vacia | plantilla_proof_of_delivery.json | ProofOfDelivery | http://localhost:59798/ | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX |            | 30775499    | 400                | Los parámetros enviados no son válidos o están incompletos |


  @code_500 @proof_of_delivery_local
  Scenario Outline: Consulta de evidencia de entrega - error interno del servidor code 500
    Given El usuario consulta la evidencia de entrega API
      | request   | metodo   | staging   | CodApp   | SecretKey   | GuideSerie   | GuideNumber   | StatusCodeEsperado   | MensajeEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <GuideSerie> | <GuideNumber> | <StatusCodeEsperado> | <MensajeEsperado> |

    Examples:
      | Escenario   | request                              | metodo          | staging                 | CodApp                   | SecretKey                        | GuideSerie | GuideNumber | StatusCodeEsperado | MensajeEsperado                         |
      | params_null | plantilla_proof_of_delivery_500.json | ProofOfDelivery | http://localhost:59798/ | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | FD         | 30775499    | 500                | Ocurrió un error interno en el servidor |


  @code_200_prod @proof_of_delivery_produccion
  Scenario Outline: Consulta de evidencia de entrega exitosa code 200 (prod)
    Given El usuario consulta la evidencia de entrega API
      | request   | metodo   | staging   | CodApp   | SecretKey   | GuideSerie   | GuideNumber   | StatusCodeEsperado   | MensajeEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <GuideSerie> | <GuideNumber> | <StatusCodeEsperado> | <MensajeEsperado> |

    Examples:
      | Escenario | request                          | metodo          | staging                           | CodApp                    | SecretKey                        | GuideSerie | GuideNumber | StatusCodeEsperado | MensajeEsperado                |
      | exitoso   | plantilla_proof_of_delivery.json | ProofOfDelivery | https://apicore.forzadelivery.io/ | SICPXSAPIECOM250620241123 | sTMQdkrMTQxNGc3jo3795qvZvht8uRrf | FD         | 34367366    | 200                | Operación realizada con éxito. |

  @code_409_prod @proof_of_delivery_produccion
  Scenario Outline: Consulta de evidencia de entrega - guia sin evidencia code 409 (prod)
    Given El usuario consulta la evidencia de entrega API
      | request   | metodo   | staging   | CodApp   | SecretKey   | GuideSerie   | GuideNumber   | StatusCodeEsperado   | MensajeEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <GuideSerie> | <GuideNumber> | <StatusCodeEsperado> | <MensajeEsperado> |

    Examples:
      | Escenario     | request                          | metodo          | staging                           | CodApp                    | SecretKey                        | GuideSerie | GuideNumber | StatusCodeEsperado | MensajeEsperado                                                |
      | sin_evidencia | plantilla_proof_of_delivery.json | ProofOfDelivery | https://apicore.forzadelivery.io/ | SICPXSAPIECOM250620241123 | sTMQdkrMTQxNGc3jo3795qvZvht8uRrf | FD         | 2390390     | 409                | No se encontró evidencia de entrega para la guía proporcionada |

  @code_404_prod @proof_of_delivery_produccion
  Scenario Outline: Consulta de evidencia de entrega - guia inexistente code 404 (prod)
    Given El usuario consulta la evidencia de entrega API
      | request   | metodo   | staging   | CodApp   | SecretKey   | GuideSerie   | GuideNumber   | StatusCodeEsperado   | MensajeEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <GuideSerie> | <GuideNumber> | <StatusCodeEsperado> | <MensajeEsperado> |

    Examples:
      | Escenario   | request                          | metodo          | staging                           | CodApp                    | SecretKey                        | GuideSerie | GuideNumber | StatusCodeEsperado | MensajeEsperado                                   |
      | inexistente | plantilla_proof_of_delivery.json | ProofOfDelivery | https://apicore.forzadelivery.io/ | SICPXSAPIECOM250620241123 | sTMQdkrMTQxNGc3jo3795qvZvht8uRrf | FD         | 99999999    | 404                | El número o serie de guía no existe en el sistema |

  @code_400_prod @proof_of_delivery_produccion
  Scenario Outline: Consulta de evidencia de entrega - parametros invalidos code 400 (prod)
    Given El usuario consulta la evidencia de entrega API
      | request   | metodo   | staging   | CodApp   | SecretKey   | GuideSerie   | GuideNumber   | StatusCodeEsperado   | MensajeEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <GuideSerie> | <GuideNumber> | <StatusCodeEsperado> | <MensajeEsperado> |

    Examples:
      | Escenario   | request                          | metodo          | staging                           | CodApp                    | SecretKey                        | GuideSerie | GuideNumber | StatusCodeEsperado | MensajeEsperado                                            |
      | serie_vacia | plantilla_proof_of_delivery.json | ProofOfDelivery | https://apicore.forzadelivery.io/ | SICPXSAPIECOM250620241123 | sTMQdkrMTQxNGc3jo3795qvZvht8uRrf |            | 30775499    | 400                | Los parámetros enviados no son válidos o están incompletos |

  @code_500_prod @proof_of_delivery_produccion
  Scenario Outline: Consulta de evidencia de entrega - error interno del servidor code 500 (prod)
    Given El usuario consulta la evidencia de entrega API
      | request   | metodo   | staging   | CodApp   | SecretKey   | GuideSerie   | GuideNumber   | StatusCodeEsperado   | MensajeEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <GuideSerie> | <GuideNumber> | <StatusCodeEsperado> | <MensajeEsperado> |

    Examples:
      | Escenario   | request                              | metodo          | staging                           | CodApp                    | SecretKey                        | GuideSerie | GuideNumber | StatusCodeEsperado | MensajeEsperado                         |
      | params_null | plantilla_proof_of_delivery_500.json | ProofOfDelivery | https://apicore.forzadelivery.io/ | SICPXSAPIECOM250620241123 | sTMQdkrMTQxNGc3jo3795qvZvht8uRrf | FD         | 30775499    | 500                | Ocurrió un error interno en el servidor |
