<!-- doc-head: W472 huecos temporales SQLite por nodo, origen y validez de observaci?n -->
Auditor?a local sin SSH, red ni cambios en colectores o radios.
CONFIRMED para timestamps retenidos; causa del corte UNKNOWN.
<!-- /doc-head -->

# Huecos de telemetr?a del 31 de octubre

## Snapshot y alcance

Artefacto: `artifacts/autoresearch/wave472_telemetry_gap.json`, secci?n `db_audit`.
Generado: `2026-10-31T19:32:30.626185+00:00`.
SQLite `tools/observability/telemetry.db`: URI `mode=ro`, `query_only=1`,
transacci?n consistente; ?ltimo `seq=51972`, 51972 filas del colector.
No se publica un SHA global de una base activa con WAL. Se conservan SQL,
l?mites del snapshot y pins del roster y de ambos colectores.

Ventana solicitada: 2026-10-24 00:00 UTC hasta el snapshot.
La ventana m?vil exacta de siete d?as empieza en `2026-10-24T19:32:30.626185+00:00`.
Cada hueco indica si la intersecta; no se confunden ambos intervalos.
El archivo de roster revisado contiene **18 nodos habilitados**, todos presentes.
La serie ICMP lateral abarca **73 identificadores**, con alcance mayor que ese roster.
Las colas incluyen 13 CPEs; no se inventan filas de los otros cinco nodos.

## Resultado del intervalo 16:30?17:25 UTC

CONFIRMED: el hueco no est? limitado al colector SSH principal.

| Serie global | ?ltima marca antes del hueco | Primera marca despu?s | Separaci?n |
|---|---|---|---:|
| `openwrt_before_after_samples` | 2026-10-31T16:30:07.792279+00:00 | 2026-10-31T17:25:18.588161+00:00 | 3310.795882 s |
| `fmx_sidecar_e2e_minute / office` | 2026-10-31T16:30:00+00:00 | 2026-10-31T17:20:00+00:00 | 3000.0 s |
| `fmx_sidecar_e2e_minute / core` | 2026-10-31T16:30:00+00:00 | 2026-10-31T17:21:00+00:00 | 3060.0 s |
| `fmx_sidecar_queue_minute` | 2026-10-31T16:29:00+00:00 | 2026-10-31T17:29:00+00:00 | 3600.0 s |

Dentro de 16:30?17:25 aparecen s?lo **cuatro filas principales**, todas `OBSERVED`,
entre 16:30:03.165929 y 16:30:07.792279. Son la cola final del ciclo previo:
no hay filas principales entre 16:30:07.792279 y 17:25:18.588161.
No debe describirse ese tramo como una serie de observaciones fallidas o vac?as.

El sidecar tampoco mantiene continuidad central: `office` reaparece a 17:20
y `core` a 17:21, antes que el colector principal. Las colas reaparecen a 17:29.
Esto prueba ausencia simult?nea de datos retenidos en varios colectores.
Los or?genes office/core no prueban colectores en hosts independientes.
**UNKNOWN:** que el motor SQLite estuviera ca?do, bloqueado o fuera la causa.
`minute_utc` y `collected_utc` no son la hora de INSERT/COMMIT; pudieron existir
buffering, reanudaci?n parcial u otras causas que estas tablas no identifican.

## Hueco principal por nodo

Marcas exactas del salto adyacente `all_rows` que intersecta la ventana.
Los predecesores/sucesores respecto de los l?mites exactos 16:30 y 17:25
tambi?n est?n guardados por separado en el JSON.

| Nodo | ?ltima fila | Siguiente fila | Separaci?n s |
|---|---|---|---:|
| `cpe_200_169` | 2026-10-31T16:29:50.124023+00:00 | 2026-10-31T17:25:35.794150+00:00 | 3345.670127 |
| `cpe_200_183` | 2026-10-31T16:30:05.507070+00:00 | 2026-10-31T17:25:44.119432+00:00 | 3338.612362 |
| `cpe_200_213` | 2026-10-31T16:29:59.036668+00:00 | 2026-10-31T17:25:35.648022+00:00 | 3336.611354 |
| `cpe_200_223` | 2026-10-31T16:30:03.165929+00:00 | 2026-10-31T17:25:40.240678+00:00 | 3337.074749 |
| `cpe_200_41` | 2026-10-31T16:30:04.446032+00:00 | 2026-10-31T17:25:41.185639+00:00 | 3336.739607 |
| `cpe_200_80` | 2026-10-31T16:29:49.958825+00:00 | 2026-10-31T17:25:27.211047+00:00 | 3337.252222 |
| `cpe_210_166` | 2026-10-31T16:29:58.968582+00:00 | 2026-10-31T17:25:35.637435+00:00 | 3336.668853 |
| `cpe_210_21` | 2026-10-31T16:29:58.968582+00:00 | 2026-10-31T17:25:44.130167+00:00 | 3345.161585 |
| `cpe_210_235` | 2026-10-31T16:29:49.969815+00:00 | 2026-10-31T17:25:27.190673+00:00 | 3337.220858 |
| `cpe_210_238` | 2026-10-31T16:29:56.686170+00:00 | 2026-10-31T17:25:33.176208+00:00 | 3336.490038 |
| `cpe_210_239` | 2026-10-31T16:29:59.089247+00:00 | 2026-10-31T17:25:41.588065+00:00 | 3342.498818 |
| `cpe_210_83` | 2026-10-31T16:30:07.792279+00:00 | 2026-10-31T17:25:44.257418+00:00 | 3336.465139 |
| `cpe_210_9` | 2026-10-31T16:29:50.124023+00:00 | 2026-10-31T17:25:27.189502+00:00 | 3337.065479 |
| `panel1_ap` | 2026-10-31T16:29:41.554859+00:00 | 2026-10-31T17:25:18.651642+00:00 | 3337.096783 |
| `panel2_ap` | 2026-10-31T16:29:41.551272+00:00 | 2026-10-31T17:25:18.667567+00:00 | 3337.116295 |
| `panel3_ap` | 2026-10-31T16:29:41.549283+00:00 | 2026-10-31T17:25:18.667567+00:00 | 3337.118284 |
| `ptp_colo_ap` | 2026-10-31T16:29:41.499132+00:00 | 2026-10-31T17:25:18.588161+00:00 | 3337.089029 |
| `ptp_colo_sta` | 2026-10-31T16:29:47.830386+00:00 | 2026-10-31T17:25:24.833842+00:00 | 3337.003456 |

Las dos estaciones intermitentes tienen un hueco mayor en **?xito directo**:
`cpe_200_169`: 16:26:04.818390?17:25:35.794150, 3570.975760 s;
`cpe_210_21`: 16:26:12.305349?17:25:44.130167, 3571.824818 s.
Sus filas posteriores a 16:26 anteriores al corte no equivalen a ?xito directo.

## Profundidad, cadencia y otros huecos

| Tabla | Filas retenidas | Interpretaci?n |
|---|---:|---|
| `agent_runs` | 0 | vac?a |
| `fmx_airos_before_baselines` | 54 | referencias Before hist?ricas |
| `fmx_counterbalanced_blocks` | 2 | experimentos/ingesta no peri?dicos |
| `fmx_counterbalanced_phases` | 8 | fases de experimentos no peri?dicas |
| `fmx_sidecar_before_after_delta` | 435 | resumen derivado sobrescrito |
| `fmx_sidecar_complaints_daily` | 61 | agregado diario, sin hora UTC |
| `fmx_sidecar_e2e_minute` | 224462 | ICMP por nodo/minuto/origen |
| `fmx_sidecar_queue_minute` | 21229 | contadores de colas |
| `fmx_sidecar_status` | 6 | ?ltimo estado por componente |
| `openwrt_before_after_samples` | 51972 | colecci?n principal y estados |
| `tool_telemetry` | 0 | vac?a |

El JSON contiene la lista completa por serie de todos los saltos >300 s,
no s?lo el del incidente: **355 saltos `all_rows` por nodo**, y 23 globales
del colector principal. Son intervalos, no 355/23 incidentes independientes.
El sidecar global tiene un hueco por origen ICMP y dos huecos de colas;
sus series v?lidas/de ?xito pueden presentar otros saltos adicionales.

Cadencias por nodo: p10/p50/p90/p99, m?nimo/m?ximo y conteo de diferencias
positivas entre tiempos distintos. Tambi?n se informa el subconjunto <=300 s,
una selecci?n descriptiva que no sustituye el resultado completo.
`cycle_cadence` conserva 69 runs y sus ciclos por separado: primer timestamp
de colecci?n por ciclo como proxy, nunca inicio real del scheduler.
Run inmediatamente anterior: 39 ciclos de 18 filas, p50 59.739984 s,
p10 55.961723 s y p90 63.759272 s. Run posterior: 126 ciclos de 18 filas,
p50 59.759038 s, p10 57.057372 s y p90 63.821556 s.
**18 filas por ciclo no implica 18 observaciones exitosas.**

No hay cobertura hist?rica continua de siete d?as: el sidecar empieza el
30 de octubre (office 14:27, core 17:06, colas 14:28 UTC), y el principal
tiene otros huecos, incluido 24 oct 21:10?28 oct 11:18:44.046226.
Las fronteras de retenci?n y la edad final se publican sin extrapolar.

## Sem?ntica y comprobaciones

- `all_rows`: incluye error, backoff y holds; no se confunde con disponibilidad.
- `direct_success_status`: estados de ?xito directo, excluyendo holds conocidos.
- `association_only_status`: evidencia pasiva, no lectura SSH del CPE.
- `fresh_memory_capture`: epoch nativo de captura con `sampled=true`; no cach?.
- ICMP v?lido exige enviados positivos y cuentas coherentes; ?xito exige
  recibidos positivos y p50 finito. `office` y `core` nunca se mezclan.
- `boot_id`, `run_id`, `cycle_id` y seq seguros se conservan en extremos,
  sin texto de clientes, credenciales, MAC ni contenido SSH crudo.

**PASS_QUERY_SANITY:** 355 huecos por nodo contrastados con SQL independiente
`LEAD`, normalizando UTC y tolerancia de 2 ms para el c?lculo `julianday`.
Se verificaron l?mite seq, conteos y roster; no se necesit? pytest ni escrituras DB.
Un error inicial de sintaxis y una comparaci?n inicial de formatos UTC se
documentan en `verification`; no modificaron ni reemplazaron la evidencia.
