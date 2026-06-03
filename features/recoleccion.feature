                  # language: es
                  @recoleccion
                  Característica: Recoleccion de Guías mediante Carga Masiva
                    Vertical: Delivery
                    Producto: Hermes Portal - Recoleccion de Guias
                    Release:
                    Jira:
                    Product Owner:
                    QA Lead: Carlos Gonzalez

                  Esquema del escenario: Registro exitoso de un lote de guias
                  Dado El usuario selecciona la url del portal de forza "<url>" y el titulo de la pagina es "<titulo>"
                  Y el usuario selecciona el pais "<pais>"
                  Y el entorno es "<entorno>"
                  Y Usuario abre el portal de forza e ingresa este telefono "<telefono>"
                  Y Usuario agrega la ruta del excel "<ruta_excel>"
                  Y Usuario selecciona la hoja "<hoja>"
                  Y Usuario selecciona la columna "<columna>"
                  Y Usuario envia el lote de guias rangoinicial "<rango_inicial>" y rango final "<rango_final>"

                  Ejemplos:
                  | Caso | ruta_excel                                                                | hoja  | columna | rango_inicial | rango_final | telefono | url                                      | titulo                      | pais      | entorno |
                  | 1    | C:\Users\gonzales.c1194\Documents\QAForzaDelivery\Guias\lista_guias1.xlsx | Guias | A       | 2             | 5           | 53581189 | https://qa-pod.forzadeliveryexpress.com/ | CourierApp - Forza Delivery | Guatemala | QAAWS   |
