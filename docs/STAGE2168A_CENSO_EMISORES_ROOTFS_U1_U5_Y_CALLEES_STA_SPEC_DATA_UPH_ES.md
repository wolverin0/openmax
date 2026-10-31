<!-- doc-head -->
# STAGE 2168A — Censo de emisores `U1..U5` en los rootfs y los dos manejadores de `sta_spec_data`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los árboles ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2166A — quién emite cada comando

Se recorrieron los dos rootfs completos y se escaneó cada ELF dos veces: por palabra cruda, que no depende de la arquitectura, y por el par `lui`/`addiu` de MIPS, que da el sitio de la instrucción.

| Comando | WA | XC | Quién |
| :--- | ---: | ---: | :--- |
| U1 `0x40905501` | 3 | 3 | `ubntbox`, `ubntspecd`, `ubnt_poll_host.ko` |
| U2 `0xC0015502` | 1 | 1 | sólo `ubnt_poll_host.ko` |
| U3 `0xC6945503` | 1 | 1 | sólo `ubnt_poll_host.ko` |
| U4 `0xC2145504` | **0** | **0** | nadie |
| U5 `0xC2145505` | **0** | **0** | nadie |

- `CONFIRMED`: sólo **6** archivos en los dos árboles contienen un comando o una cadena `uph`.
- `CONFIRMED`: **`ubntbox` también emite U1**, además de `ubntspecd`. La Stage 2160A sólo había mirado `ubntspecd`.
- `REFUTED`: que algún programa de usuario emita U2 o U3. Las dos únicas apariciones están dentro del propio módulo del kernel, que las compara, no las envía.
- `REFUTED`: que U4 y U5 tengan emisor. **No aparecen en ningún binario de los dos rootfs.**
- `INFERRED`: U4 y U5 son superficie del kernel sin cliente en este firmware.

## 2. Stage 2167A — los dos manejadores son gemelos de tamaño, no de cuerpo

| Manejador | Entrada | Tamaño | Llamadas reubicadas |
| :--- | :--- | ---: | ---: |
| `ubnt_poll_ku_comm_get_sta_spec_data` | `0x18888` | 276 | 6 |
| `ubnt_poll_ku_comm_set_sta_spec_data` | `0x1899C` | 276 | 6 |

- `CONFIRMED`: los dos miden **276** bytes en las dos familias y tienen **6** llamadas reubicadas cada uno.
- `REFUTED`: que sus cuerpos sean idénticos. El tamaño coincide, el contenido no.
- `UNKNOWN`: los destinos locales de esas 12 llamadas. La relocación apunta a la sección `.text` con añadido **cero** en la palabra de la instrucción, así que el desplazamiento del destino no se recupera de ahí.

### El despacho U4 contra U5

- `CONFIRMED`: en la ventana `0x1E80..0x1ED0` hay **8** comparaciones sobre `a2`.
- `CONFIRMED`: U4 compara contra `0xC2145504` y salta a `0x1F58`; U5 compara contra `0xC2145505` y salta a `0x1F88`. Son dos entradas separadas, no una con cola compartida.
- `CONFIRMED`: las dos difieren sólo en la palabra de comando y en el destino. El resto de la cadena es común.

### La dirección `_IOC`, con dos lecturas que no coinciden

| Comando | Bits 30-31 | Lectura Linux | Lectura por máscara (la del encargo) |
| :--- | ---: | :--- | :--- |
| U1 | 1 | **`write`** | `READ` |
| U2 | 3 | `read_write` | `READ` + `WRITE` |
| U3 | 3 | `read_write` | `READ` + `WRITE` |
| U4 | 3 | `read_write` | `READ` + `WRITE` |
| U5 | 3 | `read_write` | `READ` + `WRITE` |

- `CONFIRMED`: el campo `_IOC_DIR` es un enumerado de dos bits: `0` ninguno, `1` escritura, `2` lectura, `3` ambas.
- `REFUTED`: que la lectura por máscara del encargo describa estos bits. Con esa tabla, U1 saldría `READ` cuando en realidad es `write`, y U2 a U5 arrastrarían un bit `NONE` que no está puesto.
- `CONFIRMED`: los cinco son coherentes con la lectura Linux, y encajan con los nombres: U1 a U4 son `get_*` que **escriben** hacia el usuario, U5 es `set_*` que **lee** desde el usuario.

## 3. Lo que cambia
- `ubntbox` entra en la lista de emisores de U1, que antes sólo tenía a `ubntspecd`.
- U4 y U5 quedan como superficie **sin emisor** en todo el firmware, no sólo en un binario.
- La lectura de los bits de dirección del encargo queda corregida, con la tabla de ambos criterios.

## 4. Lo que queda abierto
- `UNKNOWN`: los destinos de las 12 llamadas locales de los dos manejadores.
- `UNKNOWN`: si `ubntbox` envía U1 por la misma ruta que `ubntspecd`.
- `UNKNOWN`: si algún binario fuera de estos dos rootfs emite U4 o U5.
- `UNKNOWN`: `vtable[456]`, que sigue llenándose en ejecución.

## 5. Stage 2169A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2166A` | `tools/re/extract_stage2166a_rootfs_u2_to_u5_ioctl_emitters_census_re.py` y su recibo |
| `2167A` | `tools/re/reconcile_stage2167a_uph_sta_spec_data_local_callees_re.py` y su recibo |
| `2169A` | `tools/verify/record_stage2169a_memorymaster_ingest.py` y su recibo |
| `2170A` | `tests/test_stage2166a_to_2171a_suite.py` |
| `2171A` | `tools/verify/verify_stage2171a_wave188_opencode_gate.py` y su recibo |
