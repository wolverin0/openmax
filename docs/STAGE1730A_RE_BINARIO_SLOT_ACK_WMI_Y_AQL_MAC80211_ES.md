<!-- doc-head -->
*STAGE1730A — RE binario de AQL en mac80211 y de slot/ack/coverage en ath10k, con reconciliación de knobs*
# STAGE 1730A — AQL, slot/ack y coverage_class

## 0. Alcance
- **100% offline**: `ssh_connections=0`, `radio_writes=0` en ambos recibos.
- Los `.ko` se tomaron del tar cuando existían y de la imagen OpenWrt cuando faltaban, porque AQL vive en `mac80211.ko` y ese fichero no está en el tar.

## 1. Stage 1728A — evidencia
- `CONFIRMED`: **3 de 3** módulos presentes (`ath10k_core.ko`, `mac80211.ko`, `cfg80211.ko`).
- `CONFIRMED`: `mac80211.ko` contiene **los tres nombres de debugfs de AQL**: `aql_txq_limit`, `aql_threshold` y `aql_enable` (1 acierto cada uno).
- `CONFIRMED`: `airtime_flags` aparece **1** vez en `mac80211.ko` y **0** en `cfg80211.ko`.
- `REFUTED`: `slot_time`, `ack_timeout` y `coverage_class` **no** aparecen como cadena en ninguno de los tres módulos (0/0/0). No son debugfs con nombre en este build.
- `UNKNOWN`: los identificadores de parámetro PDEV de WMI para slot_time, ack_timeout y coverage_class. Son constantes de enum sin símbolo ni cadena; **no se adivinan**.
- `INFERRED`: la contabilidad de airtime se gobierna desde `mac80211.ko`; el lado ath10k no expone esos nombres.

## 2. Stage 1729A — reconciliación
- `CONFIRMED`: el catálogo tiene **571** knobs.
- `CONFIRMED`: coincidencias por token: `aql` **2**, `aql_txq_limit` **1**, `aql_threshold` **1**, `aql_enable` **0**, `airtime` **21**, `slot_time` **1**, `ack_timeout` **0**, `coverage_class` **1**.
- `CONFIRMED`: `1662A` y `1663A` **no** están presentes; `1669A` **sí** existe (se resuelve por directorio, no por fichero suelto) y el recibo lo declara con `prior_1669a = 1`. El puente binario→banco sigue **parcial**.
- `REFUTED`: que los tres recibos previos estén ausentes a la vez.
- `INFERRED`: el catálogo sí nombra `aql_threshold` y `aql_txq_limit`, que son exactamente los debugfs medidos; `aql_enable` no está en el catálogo aunque sí exista en el binario.

## 3. Lo que no se prueba
- `UNKNOWN`: que escribir esos debugfs cambie la contabilidad de airtime en ejecución.
- `UNKNOWN`: los ids WMI de slot/ack/coverage.
- `UNKNOWN`: la correlación con los controles de banco, ausentes.

## 4. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1728A` | `tools/re/extract_stage1728a_ath10k_slot_ack_and_mac80211_aql_re.py` + recibo |
| `1729A` | `stage1729a_slot_ack_aql_knob_and_bench_reconciliation_receipt.json` |
| `1730A` | este documento (menos de 160 líneas, 1 `doc-head`, 0 signos de exclamación en prosa) |
| `1731A..1733A` | filas en `results.tsv`, `tests/test_stage1728a_to_1733a_suite.py` y la compuerta |
