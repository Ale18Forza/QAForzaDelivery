Feature: Creacion de Guias Guatemala API
  Vertical: Delivery
  Producto: Hermes Portal - Creacion de Guias API
  Release:
  Jira:
  Product Owner:
  QA Lead: Carlos Gonzalez

  Background: Configurar ruta de templates
    Given La ruta de los request API es "Request_Plantilla/"

  @creacion_COD_DROPI
  Scenario Outline: Creacion de guias COD DROPI
    Given El usuario selecciona el request API con los siguientes datos
      | request   | metodo   | AmmountCashOnDelivery   | cantidad   | CountPieces   | staging   | CodApp   | SecretKey   | Collected   | IdCustomer   | CodeOfReference   |
      | <request> | <metodo> | <AmmountCashOnDelivery> | <cantidad> | <CountPieces> | <staging> | <CodApp> | <SecretKey> | <Collected> | <IdCustomer> | <CodeOfReference> |

    Examples:
      | Escenario | request                   | metodo                        | AmmountCashOnDelivery | cantidad | CountPieces | staging                                      | Collected | CodApp                   | SecretKey                        | IdCustomer | CodeOfReference |
      | collet    | plantilla_COD_API_GT.json | GetServiceByHeaderCodeRequest | valor                 | 5        | 1           | https://qa-apicore.forzadeliveryexpress.com/ | false     | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | 98285      | 1785488         |

  @creacion_COD_QA
  Scenario Outline: Creacion de guias COD QA
    Given El usuario selecciona el request API con los siguientes datos
      | request   | metodo   | AmmountCashOnDelivery   | cantidad   | CountPieces   | staging   | CodApp   | SecretKey   | Collected   | IdCustomer   | CodeOfReference   |
      | <request> | <metodo> | <AmmountCashOnDelivery> | <cantidad> | <CountPieces> | <staging> | <CodApp> | <SecretKey> | <Collected> | <IdCustomer> | <CodeOfReference> |

    Examples:
      | Escenario | request                   | metodo                        | AmmountCashOnDelivery | cantidad | CountPieces | staging                                      | Collected | CodApp                   | SecretKey                        | IdCustomer | CodeOfReference |
      | collet    | plantilla_COD_API_GT.json | GetServiceByHeaderCodeRequest | valor                 | 8        | 1           | https://qa-apicore.forzadeliveryexpress.com/ | false     | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | 91721      | 1514500         |


  @creacion_COD_BOXFUL_SV
  Scenario Outline: Creacion de guias COD BOXFUL
    Given El usuario selecciona el request API con los siguientes datos
      | request   | metodo   | AmmountCashOnDelivery   | cantidad   | CountPieces   | staging   | CodApp   | SecretKey   | Collected   | IdCustomer   | CodeOfReference   |
      | <request> | <metodo> | <AmmountCashOnDelivery> | <cantidad> | <CountPieces> | <staging> | <CodApp> | <SecretKey> | <Collected> | <IdCustomer> | <CodeOfReference> |

    Examples:
      | Escenario | request                   | metodo                        | AmmountCashOnDelivery | cantidad | CountPieces | staging                                      | Collected | CodApp                   | SecretKey                        | IdCustomer | CodeOfReference |
      | collet    | plantilla_COD_API_SV.json | GetServiceByHeaderCodeRequest | valor                 | 10       | 1           | https://qa-apicore.forzadeliveryexpress.com/ | false     | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | 88813      | 2124670         |


  @creacion_COD_HN
  Scenario Outline: Creacion de guias COD QA HN
    Given El usuario selecciona el request API con los siguientes datos
      | request   | metodo   | AmmountCashOnDelivery   | cantidad   | CountPieces   | staging   | CodApp   | SecretKey   | Collected   | IdCustomer   | CodeOfReference   |
      | <request> | <metodo> | <AmmountCashOnDelivery> | <cantidad> | <CountPieces> | <staging> | <CodApp> | <SecretKey> | <Collected> | <IdCustomer> | <CodeOfReference> |

    Examples:
      | Escenario | request                           | metodo                        | AmmountCashOnDelivery | cantidad | CountPieces | staging                                      | Collected | CodApp                   | SecretKey                        | IdCustomer | CodeOfReference |
      | collet    | plantilla_COD_API_HN_Poblado.json | GetServiceByHeaderCodeRequest | valor                 | 8        | 1           | https://qa-apicore.forzadeliveryexpress.com/ | false     | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | 91726      | 1514554         |



  @creacion_COD_SV
  Scenario Outline: Creacion de guias COD QA SV
    Given El usuario selecciona el request API con los siguientes datos
      | request   | metodo   | AmmountCashOnDelivery   | cantidad   | CountPieces   | staging   | CodApp   | SecretKey   | Collected   | IdCustomer   | CodeOfReference   |
      | <request> | <metodo> | <AmmountCashOnDelivery> | <cantidad> | <CountPieces> | <staging> | <CodApp> | <SecretKey> | <Collected> | <IdCustomer> | <CodeOfReference> |

    Examples:
      | Escenario | request                   | metodo                        | AmmountCashOnDelivery | cantidad | CountPieces | staging                                      | Collected | CodApp                   | SecretKey                        | IdCustomer | CodeOfReference |
      | collet    | plantilla_COD_API_SV.json | GetServiceByHeaderCodeRequest | valor                 | 8        | 1           | https://qa-apicore.forzadeliveryexpress.com/ | false     | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | 88813      | 2124670         |