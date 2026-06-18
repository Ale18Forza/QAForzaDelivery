Feature: Intercept And Return API
  Vertical: Delivery
  Producto: InterceptAndReturn API
  Release: AGUST26
  Product Owner: Braulio
  QA Lead: Carlos Gonzalez

  Background: Configurar ruta de templates
    Given La ruta de los request API es "Request_Plantilla/"


  @intercept_and_return_exitoso_exisentente
  Scenario Outline: Guia bloqueda exitosamente con bloqueo previo
    Given El usuario ejecuta intercept and return API
      | request   | metodo   | staging   | CodApp   | SecretKey   | GuideNumber   | StatusCodeEsperado   | DescriptionEsperada   | StatusEsperado   | CountryIdEsperado   | MessageEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <GuideNumber> | <StatusCodeEsperado> | <DescriptionEsperada> | <StatusEsperado> | <CountryIdEsperado> | <MessageEsperado> |

    Examples:
      | Escenario      | request                             | metodo             | staging                 | CodApp                   | SecretKey                        | GuideNumber | StatusCodeEsperado | DescriptionEsperada | StatusEsperado                                    | CountryIdEsperado | MessageEsperado             |
      | bloqueo_activo | plantilla_intercept_and_return.json | InterceptAndReturn | http://localhost:59798/ | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | FD30775604  | 200                | Success             | El remitente ya bloqueo la entrega deeste paquete | GT                | El bloqueo ya estaba activo |


  @bloquear_entrega_exitoso
  Scenario Outline: Bloqueo de entrega creado por primera vez - Intercept and Return
    Given El usuario ejecuta intercept and return API
      | request   | metodo   | staging   | CodApp   | SecretKey   | GuideNumber   | StatusCodeEsperado   | DescriptionEsperada   | StatusEsperado   | CountryIdEsperado   | MessageEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <GuideNumber> | <StatusCodeEsperado> | <DescriptionEsperada> | <StatusEsperado> | <CountryIdEsperado> | <MessageEsperado> |

    Examples:
      | Escenario     | request                             | metodo             | staging                 | CodApp                   | SecretKey                        | GuideNumber | StatusCodeEsperado | DescriptionEsperada | StatusEsperado                                  | CountryIdEsperado | MessageEsperado |
      | bloqueo_nuevo | plantilla_intercept_and_return.json | InterceptAndReturn | http://localhost:59798/ | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | FD30775748  | 200                | Success             | El remitente bloqueo la entrega de este paquete | GT                |                 |


  @intercept_guia_entregada
  Scenario Outline: Guia ya entregada, no se puede bloquear
    Given El usuario ejecuta intercept and return API
      | request   | metodo   | staging   | CodApp   | SecretKey   | GuideNumber   | StatusCodeEsperado   | DescriptionEsperada   | StatusEsperado   | CountryIdEsperado   | MessageEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <GuideNumber> | <StatusCodeEsperado> | <DescriptionEsperada> | <StatusEsperado> | <CountryIdEsperado> | <MessageEsperado> |

    Examples:
      | Escenario      | request                             | metodo             | staging                 | CodApp                   | SecretKey                        | GuideNumber | StatusCodeEsperado | DescriptionEsperada                                                             | StatusEsperado | CountryIdEsperado | MessageEsperado                                                |
      | guia_entregada | plantilla_intercept_and_return.json | InterceptAndReturn | http://localhost:59798/ | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | FD30775387  | 406                | Not Acceptable - El paquete ya fue entregado. No es posible aplicar el bloqueo. |                | GT                | El paquete ya fue entregado. No es posible aplicar el bloqueo. |


  @intercept_guia_no_existe
  Scenario Outline: Guia inexistente, no se puede bloquear
    Given El usuario ejecuta intercept and return API
      | request   | metodo   | staging   | CodApp   | SecretKey   | GuideNumber   | StatusCodeEsperado   | DescriptionEsperada   | StatusEsperado   | CountryIdEsperado   | MessageEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <GuideNumber> | <StatusCodeEsperado> | <DescriptionEsperada> | <StatusEsperado> | <CountryIdEsperado> | <MessageEsperado> |

    Examples:
      | Escenario | request                             | metodo             | staging                 | CodApp                   | SecretKey                        | GuideNumber | StatusCodeEsperado | DescriptionEsperada                                    | StatusEsperado | CountryIdEsperado | MessageEsperado                             |
      | no_existe | plantilla_intercept_and_return.json | InterceptAndReturn | http://localhost:59798/ | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | FD63251241  | 404                | NotFound - Número de guía no encontrado en el sistema. |                |                   | Número de guía no encontrado en el sistema. |
