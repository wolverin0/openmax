<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Stage 1478A (ES) - calibracion del watchdog de rollback del PtP-Colo (T de 45 a 180 s, 500 replicas SimPy por T y opcion, cola exacta del modelo): 60 s en no-DFS, 120 s en DFS; tarjeta operativa reconciliada con el gate 1391A (mtd 8 volcados sin diferencias, mangles *1BA *1BB *19C presentes, *172 ausente, vinculo con el par no probado, 1387A NOT_READY); y simulacion SimPy de Panel1-Guarida de 3 a 4 CPE con FIFO contra FQ-CoDel + AQL (1500 a 12000 us): Jain de airtime, jitter VoIP, goodput, perdida IPTV del CPE lento. Offline, parametros supuestos. -->
# Stage 1478A — Calibración del watchdog del PtP-Colo y simulación AQL de Panel1-Guarida

Wave 73 (Stages 1476A..1481A). Todo offline: sin red, sin SSH, ningún radio tocado.

- **Watchdog y tarjeta reconciliada**: [`stage1476a_ptp_colo_watchdog_calibration_and_1391a_reconciled_card.json`](../artifacts/verification/stage1476a_ptp_colo_watchdog_calibration_and_1391a_reconciled_card.json)
- **Panel1-Guarida**: [`stage1477a_guarida_panel1_4cpe_aql_fqcodel_simpy.json`](../artifacts/verification/stage1477a_guarida_panel1_4cpe_aql_fqcodel_simpy.json)
- **Herramientas**: `tools/research/calibrate_ptp_colo_watchdog_and_reconcile_stage1391a_card.py`, `tools/research/simulate_guarida_panel1_4cpe_aql_fqcodel_simpy.py`
- **Gate**: [`stage1481a_wave73_opus55_gate.json`](../artifacts/verification/stage1481a_wave73_opus55_gate.json)

## 1. Entradas

Los nueve caminos permitidos existen. La única entrada nueva es el gate 1391A (Wave 58). El simulador 1452A y el
generador de tarjeta 1453A se importan sin modificarlos; la suite compara sus hashes con los de sus recibos.
No hay datos de radio de Guarida en la lista permitida: la parte de Guarida usa solo parámetros supuestos y dos
notas de memoria del proyecto ([<memorymaster-id>], [<memorymaster-id>]).

## 2. Reconciliación con el gate 1391A

Cada valor de la tarjeta nombra el chequeo de 1391A del que sale. Lo que 1391A no tiene queda marcado como ausente.

| Dato | Valor | Estado |
| :--- | :--- | :--- |
| Backups mtd de .105.62 y .105.54 | 8 volcados re-hasheados, 0 diferencias contra 1345A | verificado offline, **solo en esta máquina** |
| Particiones mtd0/1/4/5 | 1391A guarda la cantidad (8), no los nombres | rótulo del pedido |
| Mangles `*1BA`, `*1BB`, `*19C` | presentes en la auditoría de Infra | verificado offline |
| Mangle **`*172`** | no figura en 1391A | **no encontrado en la evidencia permitida** |
| Relación mangles y par PtP-Colo | la auditoría de Infra apuntó a .200.51/.50, no a .105.x | **no probada** |
| Checklist 1387A | NOT_READY: G1–G3 PASS, G4–G6 BLOCKER, G7–G8 FAIL | verificado offline |
| G5 | 6035 MHz por encima del tope del driver | BLOCKER |
| Tope de ath10k-ct | 25 canales, último ch165 (5825 MHz) | dato del driver, no regulatorio |

- 1391A solo nombra G1 (backups), G5 (frecuencia) y, por un chequeo de mutación, liga G7 con SG-01. Los demás
  nombres no están en la evidencia permitida y no se inventan.
- **ath10k-ct**: las imágenes OpenWrt usan esa variante. K1b (ch165) está en el último canal que tienen; ch169 y
  ch173 no existen en un extremo OpenWrt, y la fila C04 (5845 MHz) tampoco cabría.

## 3. Calibración del watchdog

Se re-corrió el modelo 1452A con la ventana T en {45, 60, 75, 90, 120, 150, 180} s para no-DFS y DFS, 500 réplicas
por opción y por T, con **las mismas semillas en cada T** (comparación pareada). Cada tasa de rollback falso por fase
se contrasta con la cola exacta del modelo, P(subida > T), integrada numéricamente: todas caen dentro de la tolerancia.

| T | Rollback falso no-DFS por fase | Rollback falso DFS por fase | Recuperación ante falla real (K1b, p50) |
| -: | :-: | :-: | -: |
| 45 s | 0,22 % | 100 % | 64 s |
| 60 s | 0,016 % | 100 % | 79 s |
| 75 s | 0,0017 % | 78 % | 94 s |
| 90 s | 0,0002 % | 5,2 % | 109 s |
| 120 s | ≈ 0 | 0,016 % | 139 s |
| 150 s | ≈ 0 | 0,0002 % | 169 s |
| 180 s | 0 | ≈ 0 | 199 s |

- **No-DFS**: con 45 s, K1a y K1b dan 0,6 % de ventanas con rollback falso [0,1 %; 1,7 %]. Con **60 s** la cola baja a
  0,016 % por fase. El costo es que una falla real tarda 15 s más en revertirse.
- **DFS**: 45 y 60 s revierten casi siempre (el CAC solo ya dura 60 s); 90 s todavía da 5 %. **120 s**, la política
  actual, queda en 0,016 %.
- **Un solo T no sirve para las dos clases**: el que conviene a DFS retrasa 60 s la recuperación en no-DFS.
- **Límite de certificación**: 0 rollbacks falsos en 500 réplicas solo acotan la tasa bajo 0,74 % (Clopper-Pearson).
  Lo que resuelve el 0,1 % es la cola analítica.
- Esto calibra el modelo, no los radios: los tiempos de subida son los supuestos de 1452A. El "p99 de 39-41 s" del
  pedido salió de esos mismos supuestos.

La tarjeta reconciliada (dentro de 1476A) lleva las precondiciones nuevas y el watchdog recomendado por opción:
60 s para K1a, K1b y el PtP-Colo de K3; 120 s para K2 y para ptp-abeni-ap en K3.

## 4. Panel1-Guarida de 3 a 4 CPE: modelo

- **CPE**: rotulados por el último octeto (`cpe_41`, `cpe_223`, `cpe_80`, `cpe_200_91`). Los nombres de abonados del
  pedido no se guardan, como exige la higiene de recibos que revisa 1391A.
- **Tráfico por CPE** (bajada): 2 descargas TCP (Reno), IPTV UDP de 6 Mbps y VoIP RTP de 200 B cada 20 ms.
- **PHY supuestas**: 173,3 / 144,4 / 130 Mbps; el CPE nuevo a 52 Mbps (MCS más bajo), con barrido a 26 y 78.
- **FIFO**: un buffer compartido de 1000 paquetes, servicio por llegada, sin equidad de airtime ni WMM.
- **FQ-CoDel + AQL**: fq_codel por estación (CoDel 20 ms / 100 ms), turno por déficit de airtime y AQL por
  estación, que también acota el largo del A-MPDU.
- **Unidad de AQL**: el pedido dice KB; `aql_txq_limit` de mac80211 está en microsegundos de airtime, y así se modeló.
- **Sin airtime** ([<memorymaster-id>]): en el LAP-120 con ath10k-ct el firmware no informa airtime por estación. Se simula
  también ese caso: turno simple entre estaciones y AQL cobrado a una sola tasa, o sea un tope igual en bytes.
- 10 semillas por configuración, 12 s con 2 s de arranque. Todo parámetro está marcado como supuesto.

## 5. Panel1-Guarida: resultados (4 CPE, medias de 10 réplicas)

| Configuración | Jain airtime | Goodput | VoIP p99 retardo | VoIP p99 IPDV | IPTV perdida CPE nuevo | Airtime CPE nuevo |
| :--- | :-: | -: | -: | -: | -: | -: |
| FIFO | 0,78 | 95,2 Mbps | 124 ms | 35,6 ms | 0,1 % | 47 % |
| FQ-CoDel + AQL 1500 us | 1,00 | 107,8 Mbps | 13,9 ms | 6,2 ms | 37 % | 26 % |
| FQ-CoDel + AQL 3000 us | 1,00 | 113,7 Mbps | 26,0 ms | 7,1 ms | 35 % | 26 % |
| FQ-CoDel + AQL 12000 us | 1,00 | 116,5 Mbps | 65,7 ms | 13,2 ms | 32 % | 25 % |
| Sin airtime, AQL 1500 us | 0,88 | 96,5 Mbps | 19,9 ms | 4,2 ms | 0 % | 41 % |
| Sin airtime, AQL 12000 us | 1,00 | 116,5 Mbps | 180,7 ms | 13,2 ms | 18 % | 25 % |

- **Efecto del cuarto CPE con FIFO**: el goodput cae de 135,5 a 95,2 Mbps y el Jain de 0,92 a 0,78. El CPE lento se
  lleva el 47 % del airtime (anomalía de rendimiento).
- **FQ-CoDel + AQL** recupera 13 a 21 Mbps y baja el retardo VoIP p99 de 124 ms a 14-66 ms. Contra FIFO, d de Cohen
  de 3,8 a 6,4 en goodput y p Holm < .001; con datos simulados el p depende de las 10 réplicas elegidas.
- **Límite AQL**: más bajo da menos retardo VoIP y algo menos de goodput (1500 us: −7,5 % contra 12000 us).
  3000 us queda en el medio: 113,7 Mbps y 26 ms.
- **Costo para el CPE lento**: con equidad estricta de airtime su 25 % no alcanza para IPTV de 6 Mbps más dos TCP;
  fq_codel reparte por flujo y la IPTV pierde 32-37 %. Con FIFO no pierde porque se lleva casi la mitad del aire.
  Haría falta prioridad para IPTV o más peso de airtime para ese CPE; eso no se simuló.
- **Barrido del CPE nuevo**: a 26 Mbps, FIFO cae a 73 Mbps con 161 ms de VoIP p99, y con AQL 3000 us la IPTV del
  CPE lento pierde 60 %; a 78 Mbps la pérdida baja a 1,2 %.
- **Sin airtime** la mejora depende del límite: con 1500 us el CPE lento recupera airtime (41 %) y no pierde IPTV,
  pero el goodput queda como FIFO; con 12000 us el retardo VoIP llega a 181 ms.

## 6. Límites honestos

- Watchdog: calibrado sobre los tiempos supuestos de 1452A; falta un ensayo cronometrado de banco.
- `*172` no está en 1391A; la relación de los mangles con el par PtP-Colo no está probada; los backups mtd solo se
  verifican en esta máquina.
- Guarida: ninguna medición real; solo bajada, sin reintentos, sin WMM, sin subida ni interferencia. El IPDV puede
  salir bajo con un patrón periódico aunque el retardo sea alto: se lee junto con el retardo p99.
- No está en la evidencia permitida si Panel1 usa la pila ath10k-ct de [<memorymaster-id>]; esa respuesta decide qué fila
  FQ-CoDel aplica.

## 7. Verificación

```
python tools/research/calibrate_ptp_colo_watchdog_and_reconcile_stage1391a_card.py --write
python tools/research/simulate_guarida_panel1_4cpe_aql_fqcodel_simpy.py --write
python -m pytest tests/test_stage1476a_to_1481a_suite.py -q
python tools/verify/verify_stage1481a_wave73_opus55_gate.py --write
```

Las dos herramientas dan bytes idénticos en dos corridas (unos 4 s y 63 s).

Método según los skills pymoo, simpy y statistical-analysis de K-Dense. Cita tomada de sus SKILL.md, sin
consultarla en red: Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). Scientific Agent
Skills: A Library of Procedural Knowledge for Research Agents. arXiv:2609.00065.
