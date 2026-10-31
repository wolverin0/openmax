<!-- doc-head -->
# STAGE 2294A — Los nueve ayudantes de `0x45F0` y el `file_operations` en `.data+0x238`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2292A — los nueve ayudantes

| Ayudante | Entrada | Tamaño | Llamadas |
| :--- | :--- | ---: | :--- |
| `get_ptmp_netconf` | `0xE658` | **36** | `ht_comm_tx` |
| `hsr_diag` | `0x7EBC` | 80 | `strlen`, `ht_comm_tx` |
| `set_ap_sta_priority` | `0x7C44` | 132 | `ht_comm_tx`, `sta_hash_find` |
| `set_sta_priority` | `0x768C` | 68 | `ht_comm_tx` |
| `debug_block_sta` | `0xB5DC` | 312 | `printk`, `create_sta_lite`, `sta_add`, `sta_hash_find` |
| `debug_unblock_sta` | `0xB714` | 200 | `printk`, `sta_remove` |
| `debug_tid` | `0xB4FC` | 224 | `ht_comm_tx` |
| `set_remote_host_diag` | `0x7DF0` | 164 | `ht_comm_tx`, `setup_packet` |
| `set_remote_target_diag` | `0x7D4C` | 164 | `ht_comm_tx`, `setup_packet` |

- `CONFIRMED`: los **nueve** existen, `missing=[]`, y suman **2760** bytes por familia.
- `CONFIRMED`: **seis de los nueve** hablan por `ubnt_poll_host_ht_comm_tx`; los tres de depuración además crean o borran estaciones.
- `CONFIRMED`: `get_ptmp_netconf` es el **más pequeño** (36 B) y **sólo** llama a `ht_comm_tx`: pide el bloque al firmware, no lo compone.

## 2. Stage 2293A — `s4` es base de sección, y `a3` sí es el `fops`

```
0x5404  lui   s4,0x0000     R_MIPS_HI16 contra .data
0x544C  addiu a3,s4,568     R_MIPS_LO16 contra .data
0x5450  sw    s1,16(sp)
```

- `CONFIRMED`: `s4` es la **base de `.data`**, no un puntero de estructura. La relocación del `lui` es lo que lo decide.
- `CONFIRMED`: `addiu a3,s4,568` carga `.data + 0x238`, una dirección **estática**.
- `CONFIRMED`: bajo la convención O32, `a3` es el **cuarto argumento**, `proc_fops`. **La corrección va en este sentido**: la lectura anterior, que llamaba a `a3` puntero de datos, era errónea.
- `CONFIRMED`: el **quinto** argumento, `data`, va en `16(sp)` y `s1` viene de `jal amalloc_private` seguido de `addu s1,v0,zero`. Es decir, el dato es **la reserva**, no un campo.

### La estructura en `.data+0x238`

| Offset | Campo (orden 2.6) | Valor |
| :--- | :--- | :--- |
| `+0x00` | `owner` | `__this_module` |
| `+0x04` | `llseek` | `.text + 0x20D4` |
| `+0x08` | `read` | `.text + 0x2014` |
| `+0x0C` | `write` | **0** |
| `+0x30` | `release` | `.text + 0x1DE0` |

- `CONFIRMED`: **cuatro** campos con símbolo por familia: `owner`, `llseek`, `read`, `release`.
- `CONFIRMED`: `write` vale cero.
- `UNKNOWN`: la asignación exacta de los dos punteros a `.text`. El modo declarado es `0o10` (sólo escritura) y el campo etiquetado `read` no está vacío, lo que **no cuadra**. La causa probable es que el orden de campos de este kernel no sea el que se asumió, y la etapa reporta los punteros por **offset** para no forzar el nombre.
- `CONFIRMED`: el `fops` de `info` y el de `noack_info` son **el mismo objeto**, porque ambos sitios cargan `s4+568`.

## 3. Qué cambia
- `a3` vuelve a ser el `proc_fops`, esta vez con la relocación como prueba.
- El `fops` deja de ser `UNKNOWN`: está en `.data+0x238`, es el mismo para las dos entradas, y tiene cuatro campos con símbolo.

## 4. Lo que queda abierto
- `UNKNOWN`: el nombre exacto de `.text+0x2014` y `.text+0x20D4`, por la discrepancia con el modo `0o10`.
- `UNKNOWN`: el significado de los tres tipos de mensaje de `set_rate_override`.
- `UNKNOWN`: las 7 materializaciones sin pareja de la wave 204.
- `UNKNOWN`: `vtable[456]`.

## 5. Stage 2295A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2292A` | `tools/re/extract_stage2292a_uph_get_ptmp_netconf_and_0x45f0_helpers_re.py` y su recibo |
| `2293A` | `tools/re/reconcile_stage2293a_uph_0x5404_s4_plus_568_fops_and_s1_re.py` y su recibo |
| `2295A` | `tools/verify/record_stage2295a_memorymaster_ingest.py` y su recibo |
| `2296A` | `tests/test_stage2292a_to_2297a_suite.py` |
| `2297A` | `tools/verify/verify_stage2297a_wave209_opencode_gate.py` y su recibo |
