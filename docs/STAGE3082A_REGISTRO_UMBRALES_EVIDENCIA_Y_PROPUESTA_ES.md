<!-- doc-head: Wave 422, Stage 3082A: registro unico propuesto de 29 familias de umbrales con fuentes file:line. Lecturas reales .20 y aritmetica offline, sin cambios de scripts ni dispositivos. Guardas de ciclo de vida preservadas; limites fisicos no medidos siguen UNKNOWN. -->
<!-- /doc-head -->
# Registro de umbrales: evidencia, contratos y valores pendientes

## Resultado y alcance

CONFIRMED para inventario, propuesta y mediciones acotadas; no significa calibracion fisica completa.
Se creo [orchestration/thresholds.json](../orchestration/thresholds.json), ausente al inicio, con las29 filas auditadas.
Cada entrada y componente tiene fuente file:line, extracto y hash; los valores desconocidos permanecen null.
El registro es una propuesta: ningun consumidor fue migrado, ningun script modificado ni radio configurado.
Se consultaron solo lecturas SSH del banco LAP-120 .20. No se contacto CPE, LTU ni produccion.

## Decision por fila

| ID | Decision / limite de evidencia |
| :-- | :-- |
| D01 | Preservar presupuesto operador: docs<220, o el limite mas estricto del encargo. |
| L01 | Banda A/A de perdida de la misma corrida y workload. |
| L02 | Banda A/A p99 de la misma corrida y workload. |
| L03 | Objetivo y banda A/A comparables, sin normalizadores universales. |
| L04 | Banda A/A por metrica; rollout y holdout siguen requeridos. |
| L05 | W388 parcial: perdida/p99 observados, sin control positivo de dano. |
| L06 | W388 parcial: perdida/drops observados; fallo real sigue siendo aborto. |
| L08 | UNKNOWN: faltan EVM/retry nativos y escenario multi-CPE comparable. |
| L09 | UNKNOWN: bmiss/EVM sin semantica y control positivo equivalentes. |
| L10 | UNKNOWN: faltan etiquetas reales de falla y correlacion multi-CPE. |
| L12 | Retirar universales64kbps/200ms; preservar admision y stop por PID verificado. |
| M01 | Retirar piso universal5120; sin reemplazo. |
| M02 | Retirar piso universal6144; sin reemplazo. |
| M03 | UNKNOWN:3636 sano no refuta3072; retirar solo pretension de calibracion. |
| M04 | UNKNOWN para UISP; lecturas sanas bajo10240 no califican operaciones UISP. |
| M05 | Retirar piso universal14336; sin reemplazo. |
| S02 | Derivar enumeracion/precision; conservar presupuesto e inferencia declarados. |
| T01 | Decision previa de quitar STOP72; conservar sensores y alcance. |
| T02 | REMOVE71 como certificado termico; seguridad fisica UNKNOWN. |
| T03 | Decision previa de quitar STOP70; conservar sensores y alcance. |
| T04 | REMOVE65/68/-40 como autorizacion termica; enfriado UNKNOWN. |
| T05 | 45=60-15 derivado; tiempos no demuestran enfriado; conservar parada acotada. |
| W02 | Conservar lease/renew/restore; hold/cadencia optimos UNKNOWN. |
| W03 | Politica previa sin valle ni un nodo/noche; gates siguen vigentes. |
| W04 | Tiempos medidos solo como descriptores; preservar deadlines. |
| W05 | Conservar backoff, pin, deadline y no replay; calibracion numerica UNKNOWN. |
| W06 | Sin caps globales de tarea; preservar limites IO/receptor/rollback. |
| W07 | Polling/checkpoint no es seguridad RF; max-wait actual1800, no900. |
| W08 | Preservar expiry/ownership y preimagen1100mBm; TTL/metricas no calibrados. |

REMOVE se refiere al numero o a su pretension de calibracion, no a eliminar ownership, autenticacion, admision, datos validos o rollback.
M03 no tiene un caso sano medido debajo3072 KiB; M04 no tiene una prueba del workload UISP bajo10240 KiB.
No se propuso ningun reemplazo termico, de RAM ni de timeout para toda la flota.

## Lecturas reales y W04/W05

Tres autenticaciones secuenciales y una conexion fijada para30 comandos:10 por perfil, orden rotado.
Todos rc0, mismo boot; consulta acotada de memoria/AQM/AQL, cero escrituras y sin trafico de carga.
| Perfil | n | Mediana s | Maximo observado s |
| :-- | --: | --: | --: |
| uptime | 10 | 0.078000 | 0.079000 |
| meminfo_small | 10 | 0.078000 | 0.094000 |
| bounded_snapshot | 10 | 0.094000 | 0.125000 |

W388 ya registro212 lecturas bajo otra carga, maximo2,562 s. No se repitio esa campana.
Los cuantiles de10 lecturas son descriptivos, sin cobertura de la cola poblacional ni garantia para enlaces lentos.
El limite de captura10 s del arnes es instrumentacion, no un umbral fisico recien validado.
No se ensayaron fallas de autenticacion, enlaces lejanos ni HTTP/Orca: no se recalibraron30/50 s o los reintentos del daemon.

## W02/W08: no retirar mecanismos necesarios

El watchdog aceptado admite1..600 s; el kit actual admite lease10..600, hold0..600 y renew=lease/3.
W350 prueba comportamiento volatil en .20: fire120, cancel480 y renew45. No demuestra un hold60 optimo para todos los kits.
W421 prueba su campana Loco con el watchdog revisionado; no valida parada de air_fpga ni guardas gateway distintas.
W08 contiene expiracion cooperativa y seleccion de rutas, no aceptacion del watchdog compartido ante SIGKILL.
Los1100mBm son preimagen congelada de11dBm: quitarlos ampliaria peligrosamente la admision de una restauracion fija.
Se conserva la identidad exacta de rutas/PID/boot y la deteccion de colisiones; no se altero TTL ni potencia.

## S02: calculo no equivale a potencia estadistica

El codigo canonico actual usa cap16 y un atajo binomial exacto; el helper historico conservaba cap14.
Enumeracion exacta:2^n signos; minimo bilateral2/2^n para diferencias no nulas, sujeto al diseno/intercambiabilidad.
Para16 bloques son65536 signos y p minimo0,0000305176. El presupuesto MC no controla esa rama exacta.
La rama MC actual toma el maximo de plus-one y la cota binomial superior con confianza0,999.
Ejemplo matematico, no familia real inferida: alpha familiar0,05 con500 hipotesis da alpha efectivo0,000102581327 bajo los supuestos de la correccion.
Con65536 sorteos y cero extremos, la minima cota MC actual es0,000105398426: aun no alcanza ese alpha.
Harian falta al menos67336 sorteos en ese mejor caso; no demuestra potencia ni autoriza promocion.
No se cambio alpha, confianza, presupuesto, codigo estadistico ni decisiones de gatekeeper.

## Proveniencia, huecos y verificacion

[Recibo con runner, generador, fuentes y tests congelados](../artifacts/autoresearch/wave422_thresholds.json).
73 referencias verificadas; las de observaciones propias usan hash de proyeccion y extracto para evitar digests circulares.
La auditoria inicial tiene locators viejos y coincidencias de numeros ajenas al concepto; se registraron fuentes actuales aparte.
Los docs1014A/1049A/1050A/1089A/81A y los tres anchors del indice se leyeron como contexto, no como ensayos termicos.
Los punteros MemoryMaster solicitados no produjeron los tres cuerpos exactos:6328 sin resultado,7d8e solo reemplazos,189e solo contexto suministrado.
No se uso una memoria aproximada como prueba numerica o autoridad actual.
17 tests pytest offline pasaron: schema,73 fuentes, proyecciones, timing, aritmetica, codigo estadistico y adulteracion.
La revision independiente detecto M03 sobregeneralizado; se corrigio a UNVERIFIED/UNKNOWN antes del cierre.
La primera construccion se detuvo antes de escribir por drift en la fuente UISP bench; intento y revisiones se conservan.
No se editaron el daemon supervisado, master_orchestrator_state.json ni los scripts de otros propietarios.
Los ensayos especificos LTU, enlaces lentos, control positivo de dano y workload UISP siguen pendientes; no se certifican como PASS fisico.
