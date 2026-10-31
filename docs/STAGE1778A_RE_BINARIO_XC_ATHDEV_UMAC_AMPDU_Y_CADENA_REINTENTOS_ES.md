<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head -->
*STAGE1778A — RE binario XC `ath_dev.ko` y `umac.ko`: límites A-MPDU, cadena de reintentos y sondeo de rate-control*
# STAGE 1778A — A-MPDU y reintentos en XC

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0` en los cuatro recibos de la wave.
- Todo se midió sobre módulos ELF32 MIPS big-endian que ya estaban en el repositorio. Nada se descompiló a código C y nada se cargó en un equipo.
- Cada afirmación lleva etiqueta `CONFIRMED`, `INFERRED`, `UNKNOWN` o `REFUTED`. Los identificadores de CPE son `cpe_`; no se usan apellidos.

## 1. Stage 1776A — censo binario
- `CONFIRMED`: se analizaron **6 de 6** módulos declarados. El par primario es `xc_8725_rootfs`: `ath_dev.ko` de **287216** bytes (sha256 `d1df6589…`) y `umac.ko` de **2358768** bytes (sha256 `ec1df9e6…`).
- `CONFIRMED`: `ath_dev.ko` declara **7 registros de nombre A-MPDU** en `.rodata`: `getAMPDU` `0x1f38`, `AMPDULim` `0x1f50`, `getAMPDULim` `0x1f68`, `AMPDUFrames` `0x1f80`, `getAMPDUFrames` `0x1f98`, `AMPDURxBsize` `0x1fb0`, `getAMPDURxBsize` `0x1fc8`.
- `CONFIRMED`: declara además **6 registros Aggr** en `0x2070..0x20e8` (`AggrProt`, `AggrProtDur`, `AggrProtMax` y sus getters), con un paso medido de **24 bytes** dentro de cada grupo.
- `CONFIRMED`: **13 de 13** direcciones de nombre tienen **cero** materializaciones `lui`+`addiu` en `.text`. La tabla se alcanza por su base, no por nombre.
- `INFERRED`: por eso los límites numéricos viven en una estructura de ejecución y no en la tabla de nombres. La etiqueta es `INFERRED` porque la estructura no se identificó.
- `CONFIRMED`: el método de reconstrucción de direcciones se validó contra un conjunto de control: **11 de 400** cadenas de formato de `.rodata.str1.4` resuelven a una función, frente a **0 de 58** cadenas del subconjunto aggregation/retry/rate. El método encuentra referencias; el subconjunto no las tiene.
- `CONFIRMED`: `umac.ko` expone **109** símbolos con `rate`, **8** de block-ack y la función `_RATE_GetTxRetrySchedule` de **2284** bytes.
- `CONFIRMED`: los únicos globales de 32 bits legibles como escalares son `g_default_xretry_per_penalty=30`, `g_rc_cck_rate_allowed=1` y `g_rc_rate_max_per_thr=65`. `pBasicRateSet` es un puntero relocalizado, no un escalar.
- `CONFIRMED`: `g_rc_rts_bw_probe` está declarado en `.bss` con tamaño 4 y **sin inicializador estático**.

## 2. Censos de inmediatos
- `CONFIRMED`: dentro de las funciones de agregación y reintento aparecen, entre otras, las constantes `0x1`, `0x2`, `0x4`, `0x8`, `0x10`, `0x20`, `0x40`, `0x100`, `0x1000`, `0x2000`, `0x8000` y `0xffff`.
- `UNKNOWN`: **cuál** de esas constantes es el límite de bytes A-MPDU. El censo prueba presencia de bytes, no semántica.
- `CONFIRMED`: `0xffff` aparece en `ath_addba_requestprocess`, `ol_rx_addba_handler`, `wmi_unified_addba_setresponse` y `wmi_unified_send_addba_send`.
- `CONFIRMED`: `0x2000` aparece en `ath_tx_complete_aggr_rifs` y en `ath_tx_sched_normal`. No se le atribuye significado.

## 3. Stage 1777A — reconciliación
- `CONFIRMED`: la unión de nombres entre el binario, el catálogo de **571** knobs y los módulos OpenWrt produce **5 de 9** objetivos `RECONCILED`.
- `CONFIRMED`: `ampdu_enable` y `rate_control` quedan en equivalencia `CONFIRMED_NAME`; `max_ampdu`, `vht_max_ampdu` y `rts_probe` quedan en `INFERRED_SEMANTIC`.
- `CONFIRMED`: **2** objetivos quedan en `BINARY_AND_CATALOG` (`retry_chain`, `txop_limit`): el binario y el catálogo los nombran, pero ningún símbolo OpenWrt offline los porta.
- `CONFIRMED`: **1** objetivo queda en `BINARY_ONLY` (`aggr_protection`). `AggrProt`, `AggrProtDur` y `AggrProtMax` existen en el binario y **no tienen knob** en el catálogo de 571.
- `CONFIRMED`: **1** objetivo queda en `CATALOG_ONLY` (`debug_tid`), que pertenece a `ubnt_poll_host` y no a `umac`.
- `CONFIRMED`: el excedente del catálogo en esta familia es **1** knob (`aql_threshold`), que es un concepto de mac80211 y no un knob de XC.
- `INFERRED`: que un nombre coincida no prueba comportamiento idéntico. La columna de equivalencia existe para no confundir ambas cosas.

## 4. Stage 1779A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax` y `source_agent=opencode-session`: `<memorymaster-id>`, `<memorymaster-id>` y `<memorymaster-id>`.
- `CONFIRMED`: la lectura de ida y vuelta por `list_claims` devolvió los **3** con estado `candidate` y alcance `project:futuramax`.
- `CONFIRMED`: ambos recibos guardan los identificadores en `pillar_e_memory_master_claim_id`.
- `UNKNOWN`: la promoción de `candidate` a confirmado es una acción de steward y no se ejecutó.

## 5. Lo que no se prueba
- `UNKNOWN`: el valor numérico del límite de bytes A-MPDU.
- `UNKNOWN`: la tabla de reintentos por TID. Los símbolos de reintento existen, pero el arreglo indexado por TID no está identificado por nombre.
- `UNKNOWN`: el intervalo de sondeo de rate-control. No hay inicializador estático y no se nombró ninguna constante de intervalo.
- `UNKNOWN`: cualquier comportamiento en vuelo. No hubo radio, ni `pktlog`, ni captura.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1776A` | `tools/re/extract_stage1776a_xc_athdev_umac_ampdu_and_retry_re.py` y su recibo |
| `1777A` | `tools/re/reconcile_stage1777a_xc_ampdu_and_retry_knobs.py` y su recibo |
| `1779A` | `tools/verify/record_stage1779a_memorymaster_ingest.py` y su recibo |
| `1780A` | `tests/test_stage1776a_to_1781a_suite.py` |
| `1781A` | `tools/verify/verify_stage1781a_wave123_opencode_gate.py` y la compuerta de la wave |
