<!-- doc-head -->
# STAGE 2180A — Addend in-place de `R_MIPS_26` en `ubnt_poll_host` y los envoltorios de `ubntbox`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2178A — el addend estaba en la instrucción

La wave 188 no pudo nombrar las llamadas locales de los cinco manejadores porque leía el símbolo de la relocación y lo encontraba vacío. En un objeto reubicable MIPS el desplazamiento viaja **dentro de la instrucción**: `(insn & 0x03FFFFFF) << 2`, y sumado al valor del símbolo —cero para un símbolo de sección— da el destino.

| Tag | Manejador | Llamadas | Destinos externos |
| :--- | :--- | ---: | :--- |
| U1 | `…get_info` | 22 | ninguno |
| U2 | `…get_stalist` | 11 | `ubnt_poll_ht_comm_parse` |
| U3 | `…get_stainfo` | 9 | `ubnt_poll_host_sta_hash_find`, `ubnt_poll_ht_comm_parse` |
| U4 | `…get_sta_spec_data` | 6 | `ubnt_poll_ht_comm_parse` |
| U5 | `…set_sta_spec_data` | 6 | `ubnt_poll_ht_comm_parse` |

- `CONFIRMED`: **108** llamadas por familia, con los mismos destinos en WA y XC.
- `CONFIRMED`: el ayudante compartido es **`ubnt_poll_ht_comm_parse`**, en `0x14894`, de **5564** bytes.
- `CONFIRMED`: U2, U3, U4 y U5 lo llaman; **U1 no lo llama nunca**, todas sus llamadas son internas.
- `CONFIRMED`: U3 además llama a `ubnt_poll_host_sta_hash_find`.
- `REFUTED`: que las llamadas locales de los dos manejadores `spec_data` fueran irresolubles. Se resuelven, y las dos van al mismo ayudante.
- `REFUTED`: que exista un envoltorio propio de `copy_from_user` o de `copy_to_user` con esos nombres. El único ayudante compartido es el de parseo.
- `UNKNOWN`: qué hace `ubnt_poll_ht_comm_parse` con sus argumentos. La etapa lo nombra, no lo caracteriza.

## 2. Stage 2179A — `ubntbox` construye la ruta con subcampos

`ubntbox` contiene **21** cadenas con `uph` por familia. La mayoría son **subrutas** bajo el dispositivo:

| Forma | Ejemplos |
| :--- | :--- |
| `/dev/uph_%s/<campo>` | `fixed_frame`, `sta_rx_rssi_th`, `enable`, `noack_mode`, `daprot`, `sta_priority`, `ff_cap_rep`, `cms_bias`, `ff_mcast_airtime_limit`, `ptp_xmit`, `atpc` |
| literales fijos | `/dev/uph/gps_info`, `/dev/uph/gpsreset`, `/dev/uph/addradio`, `/dev/uph_wait0/ff_cap_rep` |
| base | `/dev/uph_%s` |

- `CONFIRMED`: existe un literal **`/dev/uph_wait0/ff_cap_rep`**, con el índice de radio fijo en `0`.
- `CONFIRMED`: la ruta base es la misma `/dev/uph_%s` que usa `ubntspecd`.
- `INFERRED`: los envoltorios hermanos abren subrutas del mismo dispositivo y comparten el descriptor. La reutilización se deduce de la ruta común, no de un flujo de datos seguido.

### El pedido U1 en `ubntbox`

- `CONFIRMED`: hay **exactamente un** sitio que materializa `0x40905501`, en **`0x63B58`**, idéntico en las dos familias.
- `CONFIRMED`: de 95 constantes candidatas con el byte de tipo `0x55`, **sólo ésa** es un `ioctl` real.
- `REFUTED`: que `ubntbox` emita varios pedidos de la familia `'U'`. Emite uno.
- `REFUTED`: que las otras 94 candidatas sean pedidos. `0x55555556` es la constante de división por 3, y las demás son aritmética o direcciones. El filtro por byte de tipo las deja pasar, pero no son `ioctl`.

## 3. Lo que cambia
- Las llamadas de U2 a U5 tienen destino nombrado: `ubnt_poll_ht_comm_parse`.
- El pedido de `ubntbox` queda localizado en una sola instrucción y no en un censo difuso.
- Queda medido que `ubntbox` usa el mismo dispositivo por **subrutas**, no por más comandos.

## 4. Lo que queda abierto
- `UNKNOWN`: la semántica de `ubnt_poll_ht_comm_parse`.
- `UNKNOWN`: si los envoltorios de `ubntbox` reutilizan el descriptor o lo reabren cada vez.
- `UNKNOWN`: si los subcampos `/dev/uph_%s/<campo>` son dispositivos del kernel o atributos sysfs.
- `UNKNOWN`: `vtable[456]`, que sigue llenándose en ejecución.

## 5. Stage 2181A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2178A` | `tools/re/extract_stage2178a_uph_mips_rel_inplace_addend_and_local_symtab_re.py` y su recibo |
| `2179A` | `tools/re/reconcile_stage2179a_ubntbox_uph_wifi0_and_0x40905501_callers_re.py` y su recibo |
| `2181A` | `tools/verify/record_stage2181a_memorymaster_ingest.py` y su recibo |
| `2182A` | `tests/test_stage2178a_to_2183a_suite.py` |
| `2183A` | `tools/verify/verify_stage2183a_wave190_opencode_gate.py` y su recibo |
