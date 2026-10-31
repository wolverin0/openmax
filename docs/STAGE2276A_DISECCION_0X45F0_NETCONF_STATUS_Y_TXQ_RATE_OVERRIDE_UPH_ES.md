<!-- doc-head -->
# STAGE 2276A — El handler `0x45F0`, sus siete registros y los ayudantes txq/rate

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2274A — el segundo handler compartido

`0x45F0` va de la entrada al `jr ra` en **`0x50D0`**: **696 instrucciones** por familia, idénticas en WA y XC.

| Medición | WA | XC |
| :--- | ---: | ---: |
| Instrucciones | **696** | **696** |
| `R_MIPS_26` | 54 | 54 |
| `R_MIPS_HI16` | 48 | 48 |
| `R_MIPS_LO16` | 49 | 49 |
| Constantes de cadena | **31** | **31** |

Llamadas: `proc_dostring`, `snprintf`, `sscanf`, `printk`, y nueve ayudantes del módulo entre ellos `ubnt_poll_host_hsr_diag`, `ubnt_poll_host_get_ptmp_netconf`, `ubnt_poll_host_set_sta_priority`, `ubnt_poll_host_debug_block_sta`, `ubnt_poll_host_debug_tid`.

- `CONFIRMED`: `proc_dostring` está presente, así que el handler **lee y escribe texto**, no enteros.
- `CONFIRMED`: conviven `snprintf` y `sscanf`: imprime y también parsea.
- `CONFIRMED`: hay **31** constantes de cadena por familia.

### Los siete registros, medidos

`hsr_diag`, `netconf`, `sta_priority`, `set_remote_host_diag`, `set_remote_target_diag`, `debug_block_sta`, `debug_tid`. Todos con `.data = 0x1A4` y `.maxlen = 0x800`.

- `REFUTED`: la lista de siete que traía el encargo. Faltan en ella `sta_priority`, `set_remote_host_diag`, `debug_block_sta` y `debug_tid`, y sobran `status`, `gqparam`, `get_diag` y `get_host_diag`. Los cuatro que sobran son registros de `0x2138`, no de este handler.
- `CONFIRMED`: el conjunto medido tiene exactamente siete elementos, así que el número del encargo es correcto y la composición no.

### Los campos de `netconf`

- `CONFIRMED`: las cadenas contienen `down_dur`, `up_dur`, `cbp_dur`, `cbp_usable_dur`, `downlink_active_thresh`, `cbp_duty_cycle_thresh`, `hyb_cfp_min_dur_low_use`, `hyb_bal_dl_avg_dur_thresh`, `hyb_cfp_dur_unit`, `ff_frame_dur`, `ff_dl_alloc`, `ff_cbp_slots`, `voip_bias`, `cms_bias`, `atpc_target_rssi`.
- `CONFIRMED`: los nombres que el encargo menciona (`down_dur`, `up_dur`, `ff_frame_dur`, `hyb_*`) aparecen literalmente.

## 2. Stage 2275A — el argumento `a3` y los tres ayudantes

En los dos sitios de `proc_create_data`:

| Sitio | Instrucción | Valor |
| :--- | :--- | :--- |
| `0x5458` | `addiu a3,s4,568` | `s4 + 0x238` |
| `0x54A0` | `addiu a3,s4,568` | `s4 + 0x238` |

- `CONFIRMED`: `a3` **no** es el puntero de operaciones. Es `s4 + 568`, el mismo puntero de instancia que ya aparecía como cuarto argumento. Es el argumento **`data`**.
- `REFUTED`: que el `file_operations` se pase en `a3`. Va por **pila**, en el quinto hueco.
- `UNKNOWN`: el `file_operations`. No se resolvió por la vía de `a3` porque no está ahí, y el almacén de pila no se siguió.

### Los tres ayudantes

| Ayudante | Entrada | Tamaño | Llamadas | Inmediatos |
| :--- | :--- | ---: | :--- | :--- |
| `set_txq_param` | `0xB294` | 64 | `ht_comm_tx` | ninguno |
| `get_txq_param` | `0xB26C` | 40 | `ht_comm_tx` | ninguno |
| `set_rate_override` | `0xB2D4` | 304 | `ht_comm_tx`, `printk` | **1, 2, 40** |

- `CONFIRMED`: los tres hablan por `ubnt_poll_host_ht_comm_tx`, el canal con el host.
- `CONFIRMED`: `set_rate_override` es el único con inmediatos propios y con un `printk`.
- `INFERRED`: los valores 1, 2 y 40 son **tipos de mensaje** del canal, no tamaños.
- `UNKNOWN`: cuál es cuál. La etapa mide los valores, no su significado.

## 3. Qué cambia
- La composición de los siete registros de `0x45F0` queda **corregida**: el número era correcto, la lista no.
- Queda claro que `a3` en los `proc_create_data` es el puntero de datos y no el de operaciones.
- Los tres ayudantes de txq y rate quedan con tamaño, canal y tipos de mensaje.

## 4. Lo que queda abierto
- `UNKNOWN`: el `file_operations` de los dos `proc`, que viaja por pila.
- `UNKNOWN`: el significado de los tipos 1, 2 y 40.
- `UNKNOWN`: las 7 materializaciones de cadena sin pareja de la wave anterior.
- `UNKNOWN`: `vtable[456]`.

## 5. Stage 2277A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2274A` | `tools/re/extract_stage2274a_uph_0x45f0_netconf_status_handler_re.py` y su recibo |
| `2275A` | `tools/re/reconcile_stage2275a_uph_proc_fops_and_txq_rate_override_re.py` y su recibo |
| `2277A` | `tools/verify/record_stage2277a_memorymaster_ingest.py` y su recibo |
| `2278A` | `tests/test_stage2274a_to_2279a_suite.py` |
| `2279A` | `tools/verify/verify_stage2279a_wave206_opencode_gate.py` y su recibo |
