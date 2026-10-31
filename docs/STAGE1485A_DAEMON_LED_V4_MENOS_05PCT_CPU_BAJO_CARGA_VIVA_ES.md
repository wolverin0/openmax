<!-- doc-head: Wave74: LED v4 bajo carga, objetivo estricto de CPU no alcanzado -->
Tres candidatos y sus capturas originales quedan conservados sin promoción.
Las pruebas locales pasan; la CPU física supera 0.5% en ambos radios.
El heartbeat, la adquisición RSSI y el readback GPIO tienen fechas distintas.
<!-- /doc-head -->

# Stage 1485A — Daemon LED v4: objetivo menor que 0.5% no alcanzado

El candidato final `17c60861ab8662d0086a8305f96d9b08c997ae837d8d63daaffd657e656664b6`
quedó activo en el banco PowerBeam AP `.241` y STA `.242`. La instalación
1483 verificó bytes, init/procd, cuatro barras AUTO, salud y configuración.
Esta aceptación de instalación no certifica el objetivo de CPU bajo carga.

La medición nueva 1484 fue válida y completa, pero **REFUTÓ** el objetivo
estricto menor que 0.5% en ambos extremos. No hubo más optimizaciones ni
ventanas después de las dos reparaciones autorizadas.

| Radio | Ticks daemon y descendientes esperados / CPU total | Duración CPU | CPU |
| :--- | :--- | ---: | ---: |
| AP `.241` | 127 / 15645 | 156.45 s | 0.811761% |
| STA `.242` | 145 / 15646 | 156.48 s | 0.926754% |

La contabilidad incluye proceso padre y descendientes esperados que ya
terminaron, con brackets de hijos quietos y los primeros ocho contadores
de `/proc/stat`. El mínimo prerregistrado fue 120 s por radio. Cada ventana
CPU quedó contenida en la carga real; no se reutilizó la CPU de otro stage.

## Cadencia y límites de la versión final

La comprobación nominal de carrier/operstate se ejecuta cada 1 s. En kernel
real, el backend validado lee prefijos conocidos; los fixtures usan enums
completos y rechazan estados no confiables. La evaluación completa es cada
10 ticks y los bytes RX/TX se consultan cada 5 ticks. Los límites nominales
son 10 s para contadores y detección idle, y 5 s para reset de tasa.

`iw` adquiere cada 10 s en idle y cada 60 s en bulk; el TTL es 75 s.
El umbral bulk es 131072 bytes/s y la referencia btime se refresca cada
300 s. La clasificación usa `NOMINAL_WAIT_TICKS_NOT_MEASURED_ELAPSED`:
es una heurística de tráfico, no una medición de goodput.

Los drops son `OBSERVATIONAL_NOT_ASSOCIATION_VETO`: se observan y publican,
pero un incremento por sí solo no invalida la asociación ni fuerza `iw`.
Un reset o falta de los contadores de tasa exige una adquisición nueva.
Carrier0 o interfaz ausente apagan las barras; carrier1 nunca crea asociación.
El guard rápido no demuestra presencia continua del peer entre adquisiciones.

`updated_epoch` fecha la publicación del JSON. `signal_sampled_epoch`,
`signal_age_sec`, `signal_source`, `association_verified_epoch` y
`last_verified_associated` conservan la procedencia de RSSI/asociación.
Un heartbeat reciente no convierte `CACHED_IW` en señal actual.
`led_readback_epoch` y `led_readback_age_sec` fechan por separado el readback.
La edad RSSI máxima observada fue aproximadamente 61 s AP y 63 s STA.

## Resultados físicos conservados

Se observaron 166 muestras AP y 162 STA: **328/328 con cuatro GPIO AUTO**.
Los contadores de escrituras LED permanecieron en cero; PID y fuente fueron
estables. `iw_total_calls` aumentó sólo dos veces por radio durante la
ventana. RF, configuración, boot/reset e init permanecieron iguales.
La salud final dio 3/3 respuestas en cada extremo y ambos leases se liberaron.

Esto confirma estabilidad muestreada y ausencia de reescrituras del daemon.
La ausencia óptica continua de parpadeo sigue **UNKNOWN**: no hubo inspección
visual humana continua. Tampoco hay control LED-OFF emparejado que permita
atribuir causalmente Sirq al daemon.

| Métrica de carga | Resultado |
| :--- | :--- |
| HTTP, payload completado | 285212672 bytes / 175.10 s |
| Goodput de aplicación | 13.030847 Mbps |
| Cota inferior dentro de la ventana CPU | 12.222665 Mbps |
| Sirq AP / STA | 26.4493% / 34.2643% |
| ICMP 64 B, recibidos/enviados | 110/120; pérdida 8.3333% |
| ICMP 1316 B, recibidos/enviados | 115/120; pérdida 4.1667% |
| RTT 64 B p50/p95/p99 | 22.013 / 44.3414 / 80.79989 ms |
| RTT 1316 B p50/p95/p99 | 23.965 / 74.0432 / 114.51172 ms |

Las pérdidas quedan visibles; no se declara QoE sin pérdidas. HTTP mide
payload de aplicación, no tasa PHY. Los intervalos CPU y HTTP tienen
duraciones diferentes y se documentan por separado.

## Tres candidatos y aceptación separada

| Candidato | Exposición | CPU AP / STA | Resultado |
| :--- | :--- | :--- | :--- |
| `792d2f37…` inicial | HTTP1 terminó con rc4; cobertura completa inválida | 1.943437% / 2.034269%, diagnóstico | Sin certificación bajo carga |
| `10f3d545…` reparación 1 | Completa y válida | 1.138093% / 1.094867% | Objetivo CPU incumplido |
| `17c60861…` reparación 2 | Completa y válida, 156 s por radio | 0.811761% / 0.926754% | Objetivo CPU incumplido |

Cada cambio tuvo fuente y protocolo congelados antes de datos nuevos.
Los intentos previos se conservan con sus recibos, fuentes ejecutadas y RAW;
no se repinnearon al candidato actual ni se descartaron por desfavorables.

El paquete final conserva 40 fixtures Linux del daemon y 14 casos exactos
del backend de enums. Las siete suites LED anteriores pasan **414/414**,
sin fallos, errores ni skips. La ejecución fresca protegió 15 artefactos
sellados con hashes idénticos antes y después.

Una fixture histórica escribía en un recibo compartido. Se preservaron los
bytes sobrescritos, se restauraron los originales sólo tras verificar su
SHA256 y longitud exactos y se aisló la salida futura en un directorio por
ejecución. El recibo sellado no se repinneó; el cambio de fixture y su fuente
anterior quedan archivados explícitamente.

El payload v4 es un companion separado: no activa automáticamente el default
v17 ni modifica los aliases v3 históricos. El banco tiene v4 activo, **sin
certificación CPU**; aceptación de producción y flota siguen **UNKNOWN**.

El primer gate de cinco pilares falló: `AGENTS.md` ocupaba 11684 bytes frente
al presupuesto menor que 6000. Durante el cierre ese archivo cambió fuera
de este trabajo a 5998 bytes. Se preservaron el fallo y el primer cierre
bloqueado; una comprobación nueva del estado actual dio `compliant=true`,
exit0. Esta reparación externa del repositorio no cambia el fallo físico
de CPU ni identifica quién modificó las instrucciones compartidas.

## Recibos y reproducción local

- [Fixtures 1482](../artifacts/verification/stage1482a_v4_adaptive_zero_fork_led_daemon_fixtures.json).
- [Instalación 1483](../artifacts/verification/stage1483a_live_v4_led_daemon_deployment.json).
- [Carga 1484](../artifacts/verification/stage1484a_live_v4_loaded_cpu_under_05pct_verification.json).
- [Intento inicial preservado](../artifacts/verification/stage1484a/attempt1/preservation.json).
- [Reparación 1 preservada](../artifacts/verification/stage1484a/attempt2/preservation.json).
- [Prueba fresca 414 y guardas selladas](../artifacts/verification/stage1486a/attempt2/execution.json).
- [Restauración exacta de fixture](../artifacts/verification/stage1486a/legacy_fixture_recovery/recovery_proof.json).
- [Gate de repositorio](../artifacts/verification/stage1487a_five_pillar_check.json).
- [Primer cierre conservado](../artifacts/verification/stage1486a/final_closure_attempt1/preservation.json).

`python tools/verify/verify_stage1487a_wave74_codex2_gate.py --run-tests`
reproduce las verificaciones locales sin red. El cierre físico es
`PARTIAL_STRICT_LOADED_CPU_TARGET_UNMET`; las pruebas de software se informan
por separado y no cambian ese resultado.
