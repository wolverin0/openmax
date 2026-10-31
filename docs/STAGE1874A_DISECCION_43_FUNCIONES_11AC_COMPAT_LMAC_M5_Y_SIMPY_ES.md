<!-- doc-head -->
*STAGE1874A — disección de las 43 funciones `_11ac_compat_lmac_*` del M5 y simulación de coexistencia por slots*
# STAGE 1874A — 43 funciones y coexistencia

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0` en los tres recibos.
- La disección se hizo sobre `ubnt_poll.ko` de XW 6.1.4 ya presente en el repositorio. La simulación es un modelo determinista: no hubo radio, ni captura, ni tramas.
- Etiquetas `CONFIRMED`, `INFERRED`, `INFERRED_ANALYTIC`, `SIMULATED_MODEL` y `UNKNOWN`. Identificadores de CPE con prefijo `cpe_`; no se usan apellidos.

## 1. Stage 1872A — inventario de la capa
- `CONFIRMED`: las **43** funciones `_11ac_compat_*` ocupan **9208** bytes y **2302** instrucciones MIPS32.
- `CONFIRMED`: el decodificador resolvió **2255** instrucciones y dejó **47** como `.word` (2.04 %); el listado lineal completo está en `stage1872a_m5_11ac_compat_lmac_43funcs.asm`.
- `CONFIRMED`: **22** funciones establecen marco de pila, entre **24** y **80** bytes. La más pesada es `_11ac_compat_lmac_log_misc` con **1464** bytes.
- `CONFIRMED`: el grafo de llamadas internas tiene **5 aristas**, **38** raíces, **38** hojas y es **acíclico**.
- `CONFIRMED`: esas 5 aristas son delegaciones exactas del nivel host al nivel LMAC: `on_scan → lmac_on_scan`, `on_vap_open → lmac_on_vap_start`, `on_vap_close → lmac_on_vap_stop`, `on_vap_create → lmac_on_vap_create`, `on_vap_delete → lmac_on_vap_destroy`.
- `INFERRED`: el resto de las funciones son ganchos independientes que el marco de `ubnt_poll` invoca por tabla, no entre sí. Eso explica 38 raíces y 38 hojas en 43 nodos.
- `CONFIRMED`: hay **85** llamadas externas. Las más frecuentes son `ubnt_poll_log_buffer_printf` (28, todas en `log_misc`), `printk` (4), `ath_hal_reg_read` (3), `amalloc_private`, `snprintf` y `afree_private`.
- `CONFIRMED`: los llamadores externos son `ubnt_poll_on_vap_attach` (3), `ubnt_poll_on_tx_done` (2) y seis ganchos más (`linux_classify_hook`, `on_hw_timer`, `on_vap_detach`, `on_vap_close`, `sta_disconnect_hook`, `sta_auth_hook`).

## 2. Stage 1872A — puntos de decisión de la coexistencia
- `CONFIRMED`: existen tres funciones de decisión sin llamadores internos: `_11ac_compat_lmac_should_run_sched` (12 B), `_11ac_compat_lmac_should_continue_sched` (180 B) y `_11ac_compat_lmac_should_aggr` (84 B).
- `CONFIRMED`: existen dos funciones de control por estación: `_11ac_compat_lmac_set_sta_priority` (36 B) y `_11ac_compat_lmac_set_atpc` (24 B).
- `INFERRED`: `should_run_sched` y `should_continue_sched` son el punto donde el planificador decide si un peer heredado entra en el ciclo; su tamaño pequeño sugiere una condición, no una política completa.
- `UNKNOWN`: qué condición exacta evalúan. La disección reduce el problema a tres funciones, pero no lo resuelve.

## 3. Stage 1873A — modelo de coexistencia
- `SIMULATED_MODEL`: sector con **6** CPE AC y **1 a 4** CPE M5 heredados, ciclo de **10 ms**, reparto igual por peer, eficiencia MAC **0.62**, tasa AC **866.7 Mb/s**, tasa heredada **300 Mb/s** y **5 %** de sobrecarga por slot heredado.
- `SIMULATED_MODEL`: cada peer ofrece **200 Mb/s** de bulk más **2 Mb/s** de VoIP; el VoIP se sirve primero y puede usar hasta el **75 %** del slot.

| CPE heredados | Mixed Mb/s | Pure AC Mb/s | Pérdida | Amplificación | Jain mixed | VoIP p95 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 485.83 | 537.35 | 9.59 % | 2.749 | 0.937 | 10 ms |
| 2 | 447.19 | 537.35 | 16.78 % | 2.531 | 0.891 | 10 ms |
| 3 | 417.14 | 537.35 | 22.37 % | 2.361 | 0.858 | 10 ms |
| 4 | 393.09 | 537.35 | 26.85 % | 2.225 | 0.832 | 10 ms |

- `INFERRED_ANALYTIC`: la pérdida crece de forma monótona con el número de heredados y se acerca a la fracción de airtime que consumen.
- `INFERRED_ANALYTIC`: la amplificación de airtime cae de **2.749** a **2.225** al crecer el número de heredados, porque su cuota de bytes sube más rápido que su cuota de airtime.
- `SIMULATED_MODEL`: el VoIP no sufre en este modelo: **2 Mb/s** por peer caben en cualquier slot, incluso en el heredado. El costo se paga en bulk y en justicia, con Jain de 0.832 frente a 1.000.
- `UNKNOWN`: el valor real de la sobrecarga de compatibilidad. El 5 % es un supuesto de esta etapa, no una medición.

## 4. Stage 1875A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax` y `source_agent=opencode-session`.
- `CONFIRMED`: la lectura de ida y vuelta por `list_claims` devolvió los **3** con estado `candidate`.
- `CONFIRMED`: ambos recibos llevan los identificadores en `pillar_e_memory_master_claim_id`.

## 5. Lo que no se prueba
- `UNKNOWN`: qué condición evalúan `should_run_sched` y `should_continue_sched`.
- `UNKNOWN`: la sobrecarga real de la capa de compatibilidad.
- `UNKNOWN`: cualquier pérdida medida en el aire. La tabla es del modelo, no del sector.
- `UNKNOWN`: el MCS, NSS y ancho de canal reales de cada peer.
- `UNKNOWN`: si la migración a OpenWrt iguala la tasa de un CPE AC nativo; el brazo puro lo asume.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1872A` | `tools/re/extract_stage1872a_m5_11ac_compat_lmac_43funcs_re.py`, su recibo y el listado `.asm` |
| `1873A` | `tools/sim/run_stage1873a_mixed_ac_m5_tdma_slot_simpy.py` y su recibo |
| `1875A` | `tools/verify/record_stage1875a_memorymaster_ingest.py` y su recibo |
| `1876A` | `tests/test_stage1872a_to_1877a_suite.py` |
| `1877A` | `tools/verify/verify_stage1877a_wave139_opencode_gate.py` y la compuerta de la wave |
