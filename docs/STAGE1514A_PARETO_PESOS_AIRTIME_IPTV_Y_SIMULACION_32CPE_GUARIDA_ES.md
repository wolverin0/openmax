<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Stage 1514A (ES) - Panel1-Guarida: pesos airtime_weight por CPE, aql_txq_limit por AC (microsegundos) y promocion de IPTV a AC_VI optimizados con pymoo NSGA-II/NSGA-III + SimPy; con airtime por estacion (lo que muestra 213A en vivo) hay soluciones que cumplen VoIP p99 < 25 ms, IPTV del CPE lento < 2 % y goodput >= 105 Mbps, sin airtime (<memorymaster-id>) ninguna; costo para el CPE lento. Escalado a 32 CPE en 3 paneles (FIFO, AQL igual, AQL ponderado + AC_VI). Watchdog de doble temporizador verificado por exploracion acotada: BLOCKED con la evidencia actual. Offline. -->
# Stage 1514A — Pesos de airtime, IPTV en AC_VI y simulación de 32 CPE en Guarida

Wave 79 (Stages 1512A..1517A). Todo offline: sin red, sin SSH, ningún radio tocado. CPE rotulados por octeto.

- **Pareto de Panel1**: [`stage1512a_guarida_panel1_weighted_airtime_pareto.json`](../artifacts/verification/stage1512a_guarida_panel1_weighted_airtime_pareto.json)
- **Torre de 32 CPE y watchdog**: [`stage1513a_guarida_32cpe_3panel_qoe_and_dual_watchdog_fsm.json`](../artifacts/verification/stage1513a_guarida_32cpe_3panel_qoe_and_dual_watchdog_fsm.json)
- **Herramientas**: `tools/research/optimize_guarida_panel1_weighted_airtime_and_iptv_qoe_pareto.py`, `tools/research/simulate_guarida_32cpe_3panel_qoe_and_dual_watchdog_fsm.py`
- **Gate**: [`stage1517a_wave79_opus55_gate.json`](../artifacts/verification/stage1517a_wave79_opus55_gate.json)

## 1. Evidencia nueva que cambia el planteo

- **Panel1 sí informa airtime de bajada.** La lectura en vivo 213A (LAP-120, OpenWrt 24.10.4) muestra `tx duration`
  distinto de cero, `tx bitrate` poblado y `airtime weight: 256` en cada estación; `rx duration` es 0. La nota
  [<memorymaster-id>] (LAP-120 de banco, 2026-10-05, TX 0 us) sigue valiendo para ese banco; para Panel1 el régimen con airtime
  es el que tiene evidencia y el de respaldo sin airtime queda como comparación.
- **Tasas reales de Panel1** (213A): `cpe_41` 144,4, `cpe_223` 173,3 y `cpe_80` 144,4 Mbps. 1477A había supuesto
  173,3 / 144,4 / 130. El cuarto CPE, `cpe_200_91`, sigue sin medición (1017A: pendiente); sus 52 Mbps son un
  supuesto y todo el problema del CPE lento depende de él (barrido a 26 y 78).
- **AQL en vivo** (1022A, alto/bajo en microsegundos): VO 600/300, VI 2000/1000, BE 3000/1500. La caja del pedido
  (1000 a 24000 us) deja afuera el VO vivo de 600 us; la configuración viva se evaluó igual, como referencia.
- **Mangles**: `*1BA`, `*1BB` y `*19C` están en una auditoría de Infra que apuntó a .200.51/.50, no al par PtP-Colo;
  `*172` no figura en 1391A. La relación con el par sigue sin probar.

## 2. Modelo

- Se extiende el modelo 1477A (importado, sin modificarlo) con categorías WMM: VoIP en AC_VO (DSCP EF, mapeo por
  defecto de mac80211), IPTV en AC_BE salvo que se promueva a AC_VI, TCP en AC_BE. La radio atiende VO, luego VI,
  luego BE, con AIFS, CWmin y límite de TXOP de cada AC. AQL por AC en microsegundos de airtime.
- `airtime_weight`: cuanto por estación = 1000 us × peso / 256. Un CPE que gastó su cuanto **espera** a que todos
  los activos de su AC gasten el suyo; sin esa retención los pesos no tienen efecto. El modelo 1477A no retenía:
  su airtime igual salía de AQL más la ronda del hardware. Sus resultados con pesos iguales siguen valiendo.
- Sin airtime ([<memorymaster-id>]): los pesos no tienen entrada (ronda simple) y AQL se cobra a una sola tasa.

## 3. Optimización 1512A

8 variables: 4 pesos (100..1024), AQL de VO, VI y BE (1000..24000 us, grilla de 250 us) y promoción de IPTV (0/1).
Objetivos: VoIP p99, pérdida de IPTV del CPE lento y goodput; los tres umbrales del pedido como restricciones.
NSGA-II y NSGA-III (16 individuos, 8 generaciones) sobre un cribado de 2 semillas de 12 s; cada elección y cada
referencia se volvió a correr con 10 semillas. Un primer intento con cribado de 6 s dio 259 configuraciones
"factibles" sin airtime que fallaron todas en la validación (IPTV del CPE lento 4 a 11 %): por eso el cribado largo.

Referencias (10 semillas, medias):

| Configuración | VoIP p99 | IPTV CPE lento | Goodput | Jain | Goodput CPE lento |
| :--- | -: | -: | -: | -: | -: |
| FIFO | 125,6 ms | 0,04 % | 94,0 Mbps | 0,73 | 24,5 Mbps |
| AQL vivo, pesos iguales | 3,4 ms | 36,9 % | 114,3 Mbps | 1,00 | 11,6 Mbps |
| AQL vivo, solo promoción a AC_VI | 3,3 ms | 0 % | 102,9 Mbps | 0,98 | 14,0 Mbps |
| Igual sin airtime | 4,1 ms | 26,9 % | 112,5 Mbps | 0,99 | 12,7 Mbps |

El problema de 1477A **sobrevive con las tasas reales**. La promoción sola salva la IPTV pero deja el goodput bajo 105.

Elecciones validadas con airtime por estación (las tres cumplen también con el intervalo de confianza):

| Elección | VoIP p99 | IPTV lento | Goodput | Jain | Goodput lento | AQL VO/VI/BE | Peso CPE lento |
| :--- | -: | -: | -: | -: | -: | :--- | -: |
| Máximo goodput | 4,2 ms | 0 % | 120,9 Mbps | 0,80 | 8,0 Mbps | 8000 / 24000 / 22750 | 104 |
| Equilibrada | 2,3 ms | 0 % | 114,6 Mbps | 0,84 | 8,5 Mbps | 8750 / 24000 / 2000 | 104 |
| Mínimo VoIP | 1,4 ms | 0 % | 107,0 Mbps | 0,93 | 7,3 Mbps | 21250 / 24000 / 1000 | 111 |

- **La receta**: IPTV en AC_VI (prioridad estricta protege su caudal) y el peso del CPE lento casi en el mínimo,
  para que su TCP no consuma el aire que la IPTV ya no necesita compartir. El exponente implícito de la elección
  de máximo goodput es 1,08: pesos casi proporcionales a la tasa.
- **El costo**: el TCP del CPE lento baja a unos 8 Mbps (11,6 con pesos iguales, 24,5 con FIFO) y el Jain cae a
  0,80-0,93. La IPTV queda intacta; la navegación de ese abonado, más lenta.
- Los pesos de dos CPE con la misma tasa (`cpe_41`, `cpe_80`) no salen únicos: el frente es plano en esa dirección.
- **Sin airtime por estación no hay ninguna solución**: 0 de 232 configuraciones cumplen los tres umbrales. Confirmado:
  dos vectores de pesos muy distintos dan métricas idénticas en ese régimen.
- **Sensibilidad al CPE lento**: a 26 Mbps la elección de máximo goodput baja a 102,5 Mbps (no llega a 105, IPTV 0 %);
  a 78 Mbps sube a 127,8.

## 4. Torre de 32 CPE (1513A)

Hipótesis: los tres sectores con la pila OpenWrt. Panel2 y Panel3 corren airOS TDMA hoy, así que la fila FIFO no
es su comportamiento actual. Tasas: Panel1 de 1512A; 10 lecturas vivas de 243A (7 en Panel2, 3 en Panel3); las 18
restantes sorteadas de esas 10 (marcadas IMPUTED). Actividad supuesta de hora pico: 0/1/2 descargas TCP con
40/40/20 %, IPTV 35 %, VoIP 15 %. Pesos a priori: 256 × (tasa / mediana)^γ con γ = 1 (a favor de la tasa) o
γ = −0,5 (a favor del CPE lento). 10 semillas.

| Goodput (Mbps) | FIFO | AQL igual | Ponderado γ=1 + AC_VI | Ponderado γ=−0,5 + AC_VI | γ=1 sin airtime |
| :--- | -: | -: | -: | -: | -: |
| Panel1 (4) | 112,7 | 116,5 | 122,7 | 112,4 | 116,8 |
| Panel2 (22) | 88,7 | 109,3 | 88,8 | 80,1 | 85,3 |
| Panel3 (6) | 125,2 | 122,8 | 126,9 | 120,8 | 123,0 |
| **Torre** | 326,6 | **348,6** | 338,4 | 313,4 | 325,1 |

- **VoIP p99**: FIFO 93 a 149 ms; todas las políticas FQ-CoDel entre 3,3 y 4,3 ms.
- **IPTV de CPE lentos (< 60 Mbps) en Panel2**: AQL igual pierde 51,6 %; FIFO 6,5 %; ponderado γ=1 4,7 %;
  γ=−0,5 5,1 %; γ=1 sin airtime 2,3 %. Panel3 no tiene CPE lentos.
- **Jain en Panel2**: 1,00 con AQL igual y 0,59 a 0,62 con FIFO o con las ponderadas.
- **Lectura**: la receta de Panel1 sirve en Panel1 y Panel3 pero no se traslada a Panel2. Con 22 CPE y uno a 26 Mbps
  a 2100 m, muchas IPTV compiten en AC_VI y el goodput cae de 109 a 89 Mbps sin bajar la pérdida de IPTV bajo 2 %.
  Panel2 necesita otra medida (por ejemplo resolver el enlace de 26 Mbps) antes de copiar la de Panel1.

## 5. Watchdog de doble temporizador (1513A)

Exploración acotada de estados explícitos: búsqueda en anchura sobre todas las secuencias por segundo de
{tick, enlace arriba, radar}, desde BLOCKED, con invariantes sobre cada estado y transición. Además, una grilla de
fuerza bruta contra el resultado de forma cerrada (16 668 y 2928 puntos, 0 diferencias).

- Un solo temporizador armado y acorde a la clase: 60 s no-DFS, 120 s DFS. Sin violaciones.
- COMMITTED es absorbente; no hay commit después de radar; el rollback solo ocurre al vencer con el enlace caído.
- Ventana de commit: no-DFS de 0 a 59 s; DFS de 60 a 119 s (después del CAC de 60 s).
- **Contraejemplo**: con el temporizador viejo de 45 s, un canal DFS nunca puede hacer commit.
- **BLOCKED hoy**: con la evidencia de 1476A el drenaje no está confirmado (no hay ensayo; `*172` ausente) y la
  relación de mangles con el par no está probada. La máquina no sale de BLOCKED sin una anulación explícita del
  operador. Los backups mtd (8 volcados, 0 diferencias) y el techo de canal (ch165) sí cumplen.
- El chequeo prueba las propiedades de este modelo de 1 s, no del script de shell del kit.

## 6. Límites honestos

- La tasa del cuarto CPE de Panel1 es supuesta; 18 de 32 tasas de la torre son imputadas; la actividad es supuesta.
- Solo bajada, sin reintentos ni aire de subida; mac80211 tiene dos límites AQL por AC y uno global, el modelo usa uno.
- El cribado usa 2 semillas; solo la validación de 10 semillas cuenta como resultado.
- Que Panel1 informe airtime hoy no garantiza que siga así tras un cambio de firmware.

## 7. Verificación

```
python tools/research/optimize_guarida_panel1_weighted_airtime_and_iptv_qoe_pareto.py --write
python tools/research/simulate_guarida_32cpe_3panel_qoe_and_dual_watchdog_fsm.py --write
python -m pytest tests/test_stage1512a_to_1517a_suite.py -q
python tools/verify/verify_stage1517a_wave79_opus55_gate.py --write
```

Las dos herramientas dan bytes idénticos en dos corridas (unos 5,7 min y 41 s).

Método según los skills pymoo, simpy y statistical-analysis de K-Dense. Cita tomada de sus SKILL.md, sin
consultarla en red: Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). Scientific Agent
Skills: A Library of Procedural Knowledge for Research Agents. arXiv:2609.00065.
