<!-- doc-head: Stage 3087A (W427) ES: el ledger de perillas (artifacts/knob_index/knob_index.json) suma las pruebas de banco del 30/10 con valor antes y probado, equipo, veredicto, recibo y gate con sha256: coverage_class 0 a 6 (W376 aborto, W384 NO_GO), aql_txq_limit 5000/12000 a 1500/3000 un solo par (W394 NO_GO), set_rate_override CT (W394 caida del firmware), htt_max_amsdu_ampdu 3/64 a 3/32 y 2/64 (W417 NO_GO) y el campeon v2 PtP y PtMP como pruebas combinadas (W363c y W372 NO_GO) -->
Que cubre: que se agrego, como se mezcla con el builder y que bloquea el orquestador.
Estado: offline. 0 escrituras en equipos. Las 8 filas vienen de los recibos y gates citados.
Archivos: artifacts/knob_index/tested_20261030.json (fuente), tools/knob_index/merge_tested.py (mezcla), tests/test_knob_index_tested_20261030.py.
Leer cuando: antes de proponer otra A/B de cobertura, AQL, agregacion, override de tasa o campeon v2.
<!-- /doc-head -->
# Stage 3087A: perillas probadas el 30/10 en el ledger (W427)

## 1. Filas agregadas

| Ola | Familia / perilla | Antes | Probado | Veredicto |
| :-- | :-- | :-- | :-- | :-- |
| W376 | ptmp_openwrt / `coverage_class` | 0 | 6 | NO_GO |
| W384 | ptmp_openwrt / `coverage_class` | 0 | 6 | NO_GO |
| W394 | ptmp_openwrt / `aql_txq_limit` | 5000/12000 en las 4 AC | 1500/3000 en las 4 AC | NO_GO |
| W394 | ptmp_openwrt / `set_rate_override` | sin override | override CT de tasa baja (calificador de MCS bajo para H3) | CRASH |
| W417 | ptmp_openwrt / `htt_max_amsdu_ampdu` | 3 64 | 3 32 | NO_GO |
| W417 | ptmp_openwrt / `htt_max_amsdu_ampdu` | 3 64 | 2 64 | NO_GO |
| W363c | ptp_openwrt / `official_champion_v2_ptp_colo_ram_replica` | perfil nativo OpenWrt del PtP-Colo | replica en RAM de 12 perillas/loops del kit official_champion_v2 (artifacts/champion/official_champion_v2.json) | NO_GO |
| W372 | ptmp_openwrt / `official_champion_v2_ptmp_panel3_candidate` | perfil base | 8 perillas (JSON) | NO_GO |

- Cada fila tiene equipo, ventanas, detalle, recibo y gate, con su sha256. Los cambios medidos van tal como estan en el gate.
- **CONFIRMED:** todas NO_GO salvo `set_rate_override`, que es CRASH: el firmware se cayo 0,33 s despues de activarlo y no se reintento.
- W376 no llego a comparar: aborto por memoria en el primer A/A. Queda NO_GO de seguridad, con comparacion UNKNOWN.

## 2. Combinaciones

- El campeon v2 se probo entero: 12 perillas y loops en el PtP-Colo (W363c) y 8 perillas en Panel3 (W372, valores en el JSON).
- Cada prueba tiene su propia entrada de `tipo: prueba combinada`, con nombres `official_champion_v2`.
- No marca como probada cada perilla suelta, para no bloquear pruebas individuales legitimas. Un test lo verifica.

## 3. Como se mezcla

- El builder principal es `tools/research/build_knob_index.py` y reescribe `knob_index.json` desde los ledgers.
- **Despues de correrlo:** `python tools/knob_index/merge_tested.py`. Es idempotente: cada fila se identifica por stage, ronda y recibo.
- **Verificar:** `merge_tested.py --check` sale con 1 si al indice le faltan filas. Hoy: {"rows_missing": 0}.
- El resumen por familia se recalcula con la misma regla del builder: PtMP probadas de 116 a 121, PtP de 76 a 77.
- Solo cambiaron las 4 entradas de las perillas y se agregaron las 2 combinadas. El resto del indice queda igual.

## 4. Que bloquea el orquestador

- `already_tested_conflicts` rechaza una A/B, barrido o repeticion que nombre `coverage_class`, `aql_txq_limit`, `htt_max_amsdu_ampdu`, `set_rate_override` u `official_champion_v2` sin `retest_reason`. Tests: 23 passed in 1.72s.
- **Limite:** solo reconoce nombres con guion bajo ("A/B coverage_class 0 vs 6": bloquea, "A/B coverage class 0 vs 6": no bloquea, "sweep htt_max_amsdu_ampdu 3/32": bloquea, "sweep AMPDU 64 to 32": no bloquea). "coverage class" o "AMPDU" en texto libre no se bloquean. Normalizar alias en el orquestador queda fuera de esta tarea.
- **Pendiente:** si el builder se corre sin el merge, las filas se pierden del JSON (no de `tested_20261030.json`). Conviene que el builder llame al merge al final; ese archivo no estaba en el alcance.
