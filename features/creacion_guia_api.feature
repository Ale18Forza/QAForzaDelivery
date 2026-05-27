Feature: Creacion de Guias Guatemala API
  Cliente de integracion CPX, SOCIEDAD ANONIMA en Guatemala

  Background: Configurar ruta de templates
    Given La ruta de los request API es "Request_Plantilla/"

  @creacion_COD_DROPI
  Scenario Outline: Creacion de guias COD DROPI
    Given El usuario selecciona el request API con los siguientes datos
      | request   | metodo   | AmmountCashOnDelivery   | cantidad   | CountPieces   | staging   | CodApp   | SecretKey   | Collected   | IdCustomer   | CodeOfReference   |
      | <request> | <metodo> | <AmmountCashOnDelivery> | <cantidad> | <CountPieces> | <staging> | <CodApp> | <SecretKey> | <Collected> | <IdCustomer> | <CodeOfReference> |

    Examples:
      | Escenario | request                   | metodo                        | AmmountCashOnDelivery | cantidad | CountPieces | staging                                      | Collected | CodApp                   | SecretKey                        | IdCustomer | CodeOfReference |
      | collet    | plantilla_COD_API_GT.json | GetServiceByHeaderCodeRequest | valor                 | 5        | 1           | https://qa-apicore.forzadeliveryexpress.com/ | false     | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | 0          | 0               |