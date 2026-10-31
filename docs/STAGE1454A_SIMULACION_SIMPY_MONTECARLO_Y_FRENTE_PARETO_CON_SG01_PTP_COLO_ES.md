<!-- doc-head: Stage 1454A (ES) - frente Pareto con PTP-Alma-AP fijo (troncal SG-01) bajo tres lecturas de frecuencia de las filas 40/80 MHz, y Monte-Carlo SimPy (500 replicas por opcion) de la ventana Paso 0 drenaje WAN COLO, Paso 1 re-sintonia, Paso 2 OpenWrt con watchdog 45 s / 120 s para K1a ch149, K1b ch165, K2 ch56 DFS y K3 ch149 + ptp-abeni-ap. p50/p95/p99 de corte, perdida de clientes, rollback falso. Tarjeta operativa dry-run. Parametros supuestos. Offline. -->
# Stage 1454A — Simulación SimPy Monte-Carlo y frente Pareto con SG-01 para el PtP-Colo

Wave 69 (Stages 1452A..1457A). Todo offline: sin red, sin SSH, ningún radio tocado.

- **Frente fijado y Monte-Carlo**: [`stage1452a_backbone_pinned_pareto_and_simpy_montecarlo.json`](../artifacts/verification/stage1452a_backbone_pinned_pareto_and_simpy_montecarlo.json)
- **Tarjeta operativa**: [`stage1453a_ptp_colo_operator_execution_card.json`](../artifacts/verification/stage1453a_ptp_colo_operator_execution_card.json)
- **Herramientas**: `tools/research/simulate_ptp_colo_step0_to_step2_outage_and_pareto_guard_v2.py`, `tools/deploy/generate_ptp_colo_operator_runbook_card.py`
- **Gate**: [`stage1457a_wave69_opus55_gate.json`](../artifacts/verification/stage1457a_wave69_opus55_gate.json)

## 1. Entradas y lista permitida

Cuatro de los once caminos de la lista permitida no existen con ese nombre:

| Nombre del pedido | Resolución |
| :--- | :--- |
| `stage1374a_edificio_principal_clean_channel_ranking.json` | se usó `stage1374a_ptp_colo_spectrum_and_channel_selection.json`, la misma etapa y el mismo ranking |
| `stage1423a_ptp_colo_pareto_knee_recommendations.json` | se usó `stage1423a_ptp_colo_k1_k2_k3_sensitivity_matrix.json`, las mismas rodillas |
| `stage1344a_mk2rs_wan_colo_mangle_drain_rehearsal.json` | **ausente, no abierto**: el 1344A real es la radiografía; el drenaje queda como supuesto |
| `stage1386a_ptp_colo_105_62_54_mtd_backup_verification.json` | **ausente, no abierto**: el 1386A real es otro tema; los backups no se re-verifican |

El optimizador permitido lee por dentro sus entradas fijas (1374A, 1375A, 1389A); el recibo guarda sus SHA-256.
El optimizador y el runner se importan sin modificarlos: sus hashes siguen iguales a los de 1422A y 1374A.

## 2. Parte A: frente Pareto con el troncal SG-01 fijo

- **Fijado**: PTP-Alma-AP (Edificio Principal a Almafuerte), cero movimientos. Es el único radio
  co-ubicado que se puede identificar como troncal con las entradas permitidas. ptp-guarida-ap es campo
  lejano y el modelo nunca lo mueve.
- Mismo problema que 1422A: f1 solape, f2 guarda, f3 enlaces movidos, f4 CAC. Exacto hasta k = 3,
  NSGA-II (10 semillas, 300 generaciones) por encima.

| Lectura de las filas 40/80 MHz | Hoy f1 / f2 | Puntos del frente | Mínimo f1 | Mínimo f2 | Mínimo f2 con k ≤ 3 |
| :--- | :-: | -: | :-: | -: | -: |
| frecuencia = centro | 10 / 70 | 17 | 0 con k = 3 | 40 | 45 |
| control, bloque arriba (+10 MHz) | 10 / 85 | 26 | 0 con k = 3 | 40 | 50 |
| control, bloque abajo (−10 MHz) | 10 / 65 | 24 | 0 con k = 3 | 40 | 45 |

- **Costo de fijar el troncal**: sin fijar, f1 = 0 llegaba con 2 movimientos y f2 bajaba a 25 (1422A).
  Fijado, f1 = 0 pide 3 movimientos (mover ptp-jose-ap, 80 MHz, en lugar de PTP-Alma-AP) y f2 no baja de 40.
- Los 11 puntos fijados con k ≤ 3 quedan dominados o igualados por el frente de 1422A, como debe ser.
- **Las rodillas del PtP-Colo no cambian** con ninguna de las 9 lecturas (centro y las 8 combinaciones
  de ±10 MHz): K1a, K1b, K2 y K3 quedan iguales. La ambigüedad de 1389A mueve la línea base del
  sitio (f2 de 65 a 85), no las opciones del PtP-Colo.

## 3. Parte B: modelo conceptual de la ventana

Secuencia simulada por réplica, en segundos:

1. **Paso 0**, drenaje de mangles WAN COLO en MK2-RS. El PtP-Colo sigue arriba; los clientes WAN COLO salen de él.
2. **Paso 1**, re-sintonía con watchdog. K3 mueve primero ptp-abeni-ap y después el PtP-Colo.
3. **Paso 2**, conversión OpenWrt: STA y después AP. El flasheo y el primer arranque no tienen
   watchdog; el watchdog solo vigila la subida del enlace después del arranque.

- **Watchdog**: se arma al empezar cada subida; si al cerrar la ventana (45 s no-DFS, 120 s DFS) el
  enlace no está arriba, revierte. **Rollback falso**: la ventana cerró sobre un enlace que iba a
  subir. **Rollback real**: el enlace no podía subir (radar o canal malo).
- **Corte de la ventana**: cualquier rollback termina la ventana. En K3, si ptp-abeni-ap revierte, el
  PtP-Colo no se mueve.

Parámetros, todos **supuestos y sin calibrar en campo** salvo el CAC (política del repo):

| Parámetro | Valor |
| :--- | :--- |
| Drenaje | lognormal, mediana 30 s |
| Aplicar y reiniciar radio | lognormal, mediana 10 s |
| Asociación | lognormal, mediana 8 s |
| Flasheo y primer arranque, por extremo | lognormal, mediana 150 s |
| Reinicio tras rollback del Paso 2 | lognormal, mediana 60 s |
| CAC en DFS | 60 s fijo |
| Radar por CAC | 2 % (barrido 0,5 % a 5 %) |
| Falla del canal por falta de guarda | 0,5 % + 4 % × (20 − hueco)/20 (barrido de la pendiente 0 a 8 %) |
| Ancho de ptp-abeni-ap en K1a | 10, 20 o 40 MHz con igual probabilidad (prior arbitrario) |

Semillas: `SeedSequence([1452, opción, réplica, flujo])`, 8 flujos aleatorios separados, 500 réplicas por opción.

## 4. Resultados (pendiente 4 %, radar 2 %)

| Opción | Corte PtP-Colo p50 / p95 / p99 | Completa | Rollback falso | Rollback real | Otro enlace p50 / p95 |
| :--- | :-: | :-: | :-: | :-: | :-: |
| K1a ch149 | 341 / 423 / 447 s | 94,2 % | 0,6 % | 5,2 % | — |
| K1b ch165 | 334 / 424 / 457 s | 93,8 % | 0,6 % | 5,6 % | — |
| K2 ch56 (DFS) | 459 / 545 / 642 s | 95,8 % | 0,0 % | 4,2 % | — |
| K3 ch149 + abeni | 340 / 424 / 457 s | 97,2 % | 0,0 % | 2,8 % | 79 / 95 s (ptp-abeni-ap) |

- Las CI 95 % de la p95 (bootstrap) van de unos ±8 s (no-DFS) a −9/+23 s (K2); las del rollback falso son exactas (Clopper-Pearson):
  K1a y K1b 0,6 % [0,1 %; 1,7 %], K2 y K3 0 % [0 %; 0,7 %].
- **Clientes**: con el drenaje primero, la pérdida de los clientes WAN COLO es 0 en las cuatro opciones
  (por construcción). Sin drenaje, cargarían con todo el corte: p95 de 423 a 545 s, cerca del 90 % de la ventana.
- **K3 deja clientes sin cubrir**: los de ptp-abeni-ap sufren su re-sintonía DFS (p50 79 s), y el
  drenaje WAN COLO no los protege.
- **Margen del watchdog**: el p99 supuesto de subida es 39-41 s contra una ventana de 45 s en no-DFS,
  y 97-98 s contra 120 s en DFS. Con estos supuestos la ventana de 45 s es la más ajustada.

## 5. Estadística

- Estimando: corte del PtP-Colo por ventana. Kruskal-Wallis H = 906,6, p < .001.
- Mann-Whitney por pares con Holm. **K2 contra cualquier no-DFS**: +118 a +125 s de mediana, rango
  biserial cerca de 0,90; es el costo de dos CAC.
- **K1a contra K1b**: 6,5 s de mediana, rango biserial 0,06, p Holm = .174. **K1a contra K3**: 0,3 s.
  Entre las tres opciones no-DFS no hay diferencia práctica de corte.
- Con datos simulados el p-valor depende del N elegido (500): se informa el efecto y la CI, no solo p.

## 6. Barrido de supuestos (9 celdas)

- **Corte**: en las 9 celdas K1a, K1b y K3 quedan juntas en el p95 más bajo (dentro de 15 s); K2 siempre
  agrega unos 120 s.
- **Ventanas completas** (dentro de 2 puntos del mejor):
  - con pendiente 0 (la guarda no importa) ganan K1a y K1b;
  - con pendiente 4 u 8 % ganan K2 y K3 en 5 de 6 celdas;
  - con radar al 5 % y pendiente 4 % K2 cae de ese grupo.
- K3 está en el grupo de más ventanas completas en 8 de las 9 celdas.
- **Conclusión condicional**: si la guarda escasa sí rompe enlaces, K3 es la más robusta (corte de no-DFS,
  completa casi siempre); si no, K1a o K1b alcanzan. Ese supuesto es el que hay que medir.

## 7. Tarjeta operativa (1453A)

Por opción: precondiciones, pasos 0, 1, 2a y 2b (K3 agrega 1a), ventana de watchdog y CAC, criterios de
seguir y de abortar, y los números simulados. Todos los comandos son `--dry-run` del runner; ninguno es
`--apply`; `executed: false`.

- **Decisiones del operador**: ancho de ptp-abeni-ap, airView en ambos extremos, DFS o dos enlaces,
  agenda con Infra para el drenaje.
- **Precondiciones**: plan de drenaje de Infra (Stage 1357A, no leído en esta wave); backups mtd (1345A, no
  re-verificados); perfil OpenWrt hoy con `flash_ready=false` (1346A, de waves anteriores).
- Para ptp-abeni-ap (K3 paso 1a) no hay herramienta dry-run en el repo: es un cambio manual en airOS o UISP.

## 8. Límites honestos

- Toda duración y probabilidad del Monte-Carlo es supuesta; no hay mediciones de campo de esta ventana.
- Omitidos: reintentos, tiempo de reacción del operador, degradación parcial, falsos disparos por ping
  con el enlace arriba, el NOP de 30 min tras radar, y un flasheo fallido. El watchdog v17 restaura
  configuración, no firmware (1335A y 1347A, de waves anteriores).
- ptp-jose-ap (80 MHz) podría estar corrido 30 MHz y no 10 si su canal de control es uno exterior.
- Solo PTP-Alma-AP queda fijo; ningún otro radio co-ubicado se pudo clasificar como troncal.
- Por encima de k = 3 el frente es una aproximación de NSGA-II.

## 9. Verificación

```
python tools/research/simulate_ptp_colo_step0_to_step2_outage_and_pareto_guard_v2.py --write
python tools/deploy/generate_ptp_colo_operator_runbook_card.py --write
python -m pytest tests/test_stage1452a_to_1457a_suite.py -q
python tools/verify/verify_stage1457a_wave69_opus55_gate.py --write
```

La simulación tarda cerca de 90 s; dos corridas dan bytes idénticos.

Método según los skills pymoo, simpy y statistical-analysis de K-Dense. Cita tomada de sus SKILL.md, sin
consultarla en red: Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). Scientific Agent
Skills: A Library of Procedural Knowledge for Research Agents. arXiv:2609.00065.
