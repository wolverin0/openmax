<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head -->
*STAGE1814A — RE binario de `ubnt_poll_host.ko` y `ath10k_core.ko`: déficit de airtime, ciclo de poll y prioridad VoIP*
# STAGE 1814A — Airtime, poll y VoIP

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0` en los tres recibos.
- Todo se midió sobre cuatro módulos ELF32 MIPS big-endian que ya estaban en el repositorio. Nada se cargó, nada se ejecutó y no hubo captura en vuelo.
- Etiquetas `CONFIRMED`, `INFERRED`, `UNKNOWN` y `REFUTED`. Identificadores de CPE con prefijo `cpe_`; no se usan apellidos.

## 1. Stage 1812A — planificador de poll
- `CONFIRMED`: `ubnt_poll_host.ko` 8.7.25 mide **189880** bytes, conserva **154** funciones con nombre semántico y **no tiene sección `__param`**.
- `CONFIRMED`: publica **31 descriptores proc** en `.rodata` con un paso medido de **44 bytes**, modo **0644** y `maxlen` de **4**, **64** o **2048**.
- `CONFIRMED`: los 31 descriptores apuntan a solo **3 ranuras `.bss`** (`.bss+0x1a4`, `.bss+0x9a4`, `.bss+0x9a8`). Ningún knob tiene variable propia: el valor se parsea desde un buffer compartido.
- `CONFIRMED`: los manejadores resuelven a **dos funciones locales sin símbolo**, en `.text+0x2138` y `.text+0x45f0`. El módulo no las nombra.
- `CONFIRMED`: de los 14 nombres de la familia VoIP/airtime, solo **3** son entradas proc reales: `voip_bias`, `ff_mcast_airtime_limit` y `sta_priority`.
- `REFUTED`: los otros **11** (`voip_pps_min`, `voip_pps_max`, `cbp_dur_slot`, `ff_cbp_slots`, `ff_frame_dur`, `ff_dl_alloc`, `ff_unit_shift`, `ff_guard_units`, `ff_sta_rx_rssi_th`, `down_dur_min`, `cfp_dur_min`) **no son knobs**: son etiquetas dentro de cadenas de formato de volcado diagnóstico.
- `CONFIRMED`: `_voip_dynamic_duration_levels` es una tabla de **60 bytes** en `.rodata+0xe68` que decodifica como **30 valores u16 big-endian**. Su conjunto distinto es `{0, 512, 768, 1024, 1280, 1536, 1792, 2048, 7500, 15000}`.
- `INFERRED`: el grupo 512→2048 avanza de 256 en 256 y 15000 y 7500 se repiten, lo que encaja con una escalera de duraciones. El emparejamiento umbral/duración es `UNKNOWN` porque el paso del registro no está probado.

## 2. Stage 1812A — lado OpenWrt
- `CONFIRMED`: el `ath10k_core.ko` de este repositorio está **sin símbolos**: **286 de 286** funciones se llaman `_N` y **38 de 39** objetos son marcadores.
- `REFUTED`: por tanto es falso que se puedan atribuir funciones concretas de `ath10k_core.ko` al déficit de airtime. El recibo lo declara con `function_attribution=REFUTED`.
- `CONFIRMED`: sobrevive la **superficie de importación**: `ieee80211_sta_register_airtime`, `ieee80211_txq_may_transmit`, `ieee80211_next_txq`, `ieee80211_txq_schedule_start`, `__ieee80211_schedule_txq` y `ieee80211_txq_get_depth`.
- `CONFIRMED`: sobrevive la cadena `WMI_SERVICE_REPORT_AIRTIME` en `.rodata.str1.4`, con **0** referencias resueltas por `lui`+`addiu`.

## 3. Stage 1813A — reconciliación
- `CONFIRMED`: **8 objetivos**. **2** son estructurales (`airtime_interface`, `aql_limits`), **4** quedan en binario más catálogo (`voip_bias`, `mcast_airtime_limit`, `station_priority`, `fixed_frame`) y **2** solo en binario (`poll_cycle_timing`, `voip_duration_ladder`).
- `CONFIRMED`: `mac80211.ko` aporta **21** símbolos de airtime, txq y AQL; `ath10k_core.ko` aporta **6** importaciones de airtime.
- `CONFIRMED`: la familia airtime/VoIP del catálogo de 571 tiene **13** knobs y **4** no aparecen en ningún binario medido: `aql_txq_limit`, `fq_quantum`, `wmi10_1_pdev_burst_dur` y `wmi10_1_vdev_slot_time`.
- `INFERRED`: el ciclo de poll con su geometría de slots y la escalera VoIP son **específicos de Ubiquiti**; OpenWrt no tiene un equivalente estructural, solo portadores genéricos de airtime y txq. Un portador genérico nunca asciende un veredicto en este recibo.

## 4. Stage 1815A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax` y `source_agent=opencode-session`: `<memorymaster-id>`, `<memorymaster-id>~2` y `<memorymaster-id>`.
- `CONFIRMED`: la lectura de ida y vuelta por `list_claims` devolvió los **3** con estado `candidate` y alcance `project:futuramax`.
- `CONFIRMED`: ambos recibos llevan los identificadores en `pillar_e_memory_master_claim_id`.
- `UNKNOWN`: la promoción de `candidate` a confirmado es acción de steward y no se ejecutó.

## 5. Lo que no se prueba
- `UNKNOWN`: el cuanto de un deficit round-robin. No existe como símbolo con nombre en ninguno de los dos módulos.
- `UNKNOWN`: el peso de airtime por estación. Hay `sta_priority` como entrada proc, pero su efecto numérico no se midió.
- `UNKNOWN`: la unidad de `voip_bias` (microsegundos, slots o multiplicador).
- `UNKNOWN`: el emparejamiento exacto de la tabla de 60 bytes.
- `UNKNOWN`: cualquier comportamiento en vuelo. No hubo radio, ni `pktlog`, ni captura de ciclo de poll.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1812A` | `tools/re/extract_stage1812a_ubnt_poll_and_ath10k_airtime_deficit_re.py` y su recibo |
| `1813A` | `tools/re/reconcile_stage1813a_airtime_deficit_and_voip_preemption_knobs.py` y su recibo |
| `1815A` | `tools/verify/record_stage1815a_memorymaster_ingest.py` y su recibo |
| `1816A` | `tests/test_stage1812a_to_1817a_suite.py` |
| `1817A` | `tools/verify/verify_stage1817a_wave129_opencode_gate.py` y la compuerta de la wave |
