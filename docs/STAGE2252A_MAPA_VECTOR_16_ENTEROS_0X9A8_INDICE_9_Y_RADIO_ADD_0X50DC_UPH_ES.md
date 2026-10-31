<!-- doc-head -->
# STAGE 2252A — El vector de 16 enteros en `+0x9A8` y la instanciación por radio

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2250A — por qué leer cualquier archivo imprime los 16 enteros

Dieciséis registros comparten **el mismo** puntero de datos y **la misma** longitud:

| Campo | Valor |
| :--- | :--- |
| `.data` | `0x9A8` |
| `.maxlen` | `0x40` = 64 bytes = **16 enteros** |
| Registros que lo comparten | **16** |

Los dieciséis: `set_host_diag`, `set_diag`, `timing`, `sqparam`, `get_reg`, `set_reg`, `ro`, `swr_limit`, `evm_meas_config`, `atpc`, `cms_bias`, `ff_cap_rep`, `ff_mcast_airtime_limit`, `voip_bias`, `fixed_frame`, `sta_rx_rssi_th`.

- `CONFIRMED`: **todos** apuntan a `radio + 0x9A8` con longitud 64.
- `CONFIRMED`: por eso leer cualquiera de esos archivos vuelca **el vector completo**, no un campo.
- `REFUTED`: que cada knob corresponda a un índice. Ninguno posee un índice: comparten el arreglo.
- `REFUTED`: que el índice 9 sea «el knob 9». `0x9A8 + 9×4 = 0x9CC` es simplemente el décimo entero de un vector compartido.
- `UNKNOWN`: qué significa cada uno de los 16 enteros. La etapa mide el contenedor, no la semántica.

### El mecanismo del despacho

| Medición | WA | XC |
| :--- | ---: | ---: |
| Relocaciones en `0x2138..0x2938` | **144** | **144** |
| `R_MIPS_26` | 39 | 39 |
| `R_MIPS_HI16` | 47 | 47 |
| `R_MIPS_LO16` | 58 | 58 |
| Constantes de cadena | **25** | **25** |

Ayudantes alcanzados: `set_diag`, `get_diag`, `set_host_diag`, `set_reg`, `get_reg`, `set_swr_limit`, `set_evm_meas_config`, `set_rate_override`, `set_txq_param`, `get_txq_param`, `printk`.

- `CONFIRMED`: el cuerpo **compara contra 25 cadenas** y llama al ayudante que corresponde.
- `CONFIRMED`: hay **once** destinos distintos, no uno.
- `REFUTED`: que el handler sea genérico y no discrimine. Discrimina por nombre, y ahora está medido: las cadenas están ahí.
- `CONFIRMED`: los seis `printk` son el caso de nombre no reconocido.

## 2. Stage 2251A — `ubnt_poll_host_radio_add`, 1188 bytes

| Medición | WA | XC |
| :--- | ---: | ---: |
| Tamaño | **1188** | **1188** |
| Relocaciones | **65** | **65** |
| Símbolos | 27 | 27 |
| Cadenas | 18 | 18 |
| Secciones | 20 | 20 |

Llamadas: `amalloc_private`, `memset`, `memcpy`, `snprintf`, `printk`, **`proc_create_data`**, `proc_mkdir`, `register_sysctl_table`, **`cdev_init`**, **`cdev_add`**.

- `CONFIRMED`: la función **asigna, copia, crea entradas `proc`, registra la tabla sysctl, inicializa un `cdev` y lo añade**.
- `CONFIRMED`: `proc_create_data` aparece **dos veces**: dos entradas por radio.
- `CONFIRMED`: es la ruta de instanciación por radio, no un ayudante de registro genérico.
- `REFUTED`: que los campos `+0x1A4`, `+0x9A4` y `+0x9A8` se inicialicen con inmediatos literales. La búsqueda de esos tres valores como desplazamiento literal devuelve **cero**.
- `UNKNOWN`: cómo se alcanzan esos tres campos dentro de `radio_add`. Se llega por punteros calculados, no por inmediato.

## 3. Qué cambia
- El comportamiento observado en vivo queda explicado: **el vector es compartido**, no hay un knob por índice.
- El despacho por nombre de `0x2138` queda **medido**, no inferido: 25 cadenas y 11 destinos.
- Los tres offsets de radio no se escriben con literales en `radio_add`, lo que descarta la vía más simple.

## 4. Lo que queda abierto
- `UNKNOWN`: el significado de cada uno de los 16 enteros.
- `UNKNOWN`: cómo alcanza `radio_add` los campos `+0x1A4`, `+0x9A4`, `+0x9A8`.
- `UNKNOWN`: el destino de los seis `printk`.
- `UNKNOWN`: `vtable[456]`.

## 5. Stage 2253A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2250A` | `tools/re/extract_stage2250a_uph_0x2138_all_rel_text_and_16int_vector_re.py` y su recibo |
| `2251A` | `tools/re/reconcile_stage2251a_uph_radio_add_0x50dc_full_1188b_re.py` y su recibo |
| `2253A` | `tools/verify/record_stage2253a_memorymaster_ingest.py` y su recibo |
| `2254A` | `tests/test_stage2250a_to_2255a_suite.py` |
| `2255A` | `tools/verify/verify_stage2255a_wave202_opencode_gate.py` y su recibo |
