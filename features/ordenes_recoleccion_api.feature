Feature: Ordenes de Recoleccion API
  Creacion de solicitudes de recoleccion via API SetPickupServiceByIntegration

  Background: Configurar ruta de templates
    Given La ruta de los request API es "Request_Plantilla/"


  @recoleccion_API
  Scenario Outline: Creacion de orden de recoleccion
    Given El usuario crea una orden de recoleccion API
      | request   | metodo   | staging   | CodApp   | SecretKey   | CodeOfReference   | QuantityOfPieces   | StartDate   | EndDate   | TypeVehicleId   | MensajeEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <CodeOfReference> | <QuantityOfPieces> | <StartDate> | <EndDate> | <TypeVehicleId> | <MensajeEsperado> |

    Examples:
      | Escenario    | request                        | metodo                        | staging                                      | CodApp                   | SecretKey                        | CodeOfReference | QuantityOfPieces | StartDate           | EndDate             | TypeVehicleId | MensajeEsperado                                  |
      | recoleccion1 | plantilla_recoleccion_API.json | SetPickupServiceByIntegration | https://qa-apicore.forzadeliveryexpress.com/ | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | 948850          | 8                | 2026-06-27 08:40:00 | 2026-06-27 23:00:00 | 1             | Solicitud de recolección procesada correctamente |

  @recoleccion_existente
  Scenario Outline: Creacion de orden de recoleccion
    Given El usuario crea una orden de recoleccion API
      | request   | metodo   | staging   | CodApp   | SecretKey   | CodeOfReference   | QuantityOfPieces   | StartDate   | EndDate   | TypeVehicleId   | MensajeEsperado   |
      | <request> | <metodo> | <staging> | <CodApp> | <SecretKey> | <CodeOfReference> | <QuantityOfPieces> | <StartDate> | <EndDate> | <TypeVehicleId> | <MensajeEsperado> |

    Examples:
      | Escenario    | request                        | metodo                        | staging                                      | CodApp                   | SecretKey                        | CodeOfReference | QuantityOfPieces | StartDate           | EndDate             | TypeVehicleId | MensajeEsperado                                                                                          |
      | recoleccion1 | plantilla_recoleccion_API.json | SetPickupServiceByIntegration | https://qa-apicore.forzadeliveryexpress.com/ | SIFDCAPIECOM230920201910 | SHyKQDB3K6dfHxR3Dbqw45CQMv65vgkX | 948850          | 8                | 2026-06-27 08:40:00 | 2026-06-27 23:00:00 | 1             | Ya fue solicitado un servicio de recolección el día de hoy para este Punto de Visita / En estado: Creado |
