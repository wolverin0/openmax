<!-- doc-head -->
*STAGE1766A — máquina de estados de 6 cohortes/28 CPE en Guarida y simulación de transición Triple-Play*
# STAGE 1766A — 6 cohortes, 28 CPE

## 0. Frontera
- **100% offline**: `ssh_connections=0`, `radio_writes=0` en ambos recibos. Nada se ejecuta sobre una radio.
- Identificadores de CPE exclusivamente `cpe_`; no se usan apellidos.

## 1. Stage 1764A — máquina de estados unificada
- `CONFIRMED`: **6 cohortes / 28 CPEs**: Panel 3 aporta **2 cohortes de 3** (`.83`) y Panel 2 **4 cohortes de 6/6/5/5** (`.82`), heredadas de `1699A` y `1735A`.
- `CONFIRMED`: **6 estados** (`PREFLIGHT`, `VERIFY_4ADDR`, `MIGRATE`, `VERIFY_3LAYER`, `DONE`, `ROLLBACK`) con transiciones declaradas.
- `CONFIRMED`: compuertas duras por cohorte: **`brport/state=3`**, **`multicast_to_unicast=1`** y healer con **`ban_time=1200`**.
- `CONFIRMED`: **6 de 6 cohortes bloqueadas** en `PREFLIGHT` con todas las compuertas en `null`.
- `CONFIRMED`: el rollback es automático: una compuerta fallida o **dos fallos de doble bind** en la ventana de la cohorte.
- `INFERRED`: el orden Panel 3 → Panel 2 mantiene primero el grupo pequeño y medido, y deja el grupo grande para cuando las compuertas ya tienen evidencia.

## 2. Stage 1765A — simulación de transición
- `CONFIRMED`: simulación determinista con semilla `20261028`, `coverage_class=1` y AQL reducido (`threshold=3000`, `txq` 800/3200).
- `CONFIRMED`: **5 fallos de doble bind**, **0 rollbacks**, **84** streams IPTV convertidos de multicast a unicast, ventana total **0.700 h**.
- `INFERRED`: con una probabilidad de fallo del 18 % por CPE y cohortes de 3 a 6, dos fallos en la misma cohorte son raros; por eso el modelo no dispara ningún rollback.
- `UNKNOWN`: si el rollback automático se dispararía igual en la realidad.

## 3. Lo que no se prueba
- `UNKNOWN`: cualquier compuerta medida; no hay cohorte ejecutada.
- `UNKNOWN`: la latencia y el jitter reales; los valores son del modelo.
- `UNKNOWN`: el comportamiento de las 3 CPEs del Panel 3 sin medición.

## 4. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1764A` | `tools/rollout/run_stage1764a_guarida_28cpe_unified_cohort_state_machine.py` + recibo |
| `1765A` | `tools/sim/run_stage1765a_guarida_28cpe_cohort_transition_simpy.py` + recibo |
| `1766A` | este documento (menos de 160 líneas, 1 `doc-head`, 0 signos de exclamación en prosa) |
| `1768A..1769A` | `tests/test_stage1764a_to_1769a_suite.py` y la compuerta de la wave |
