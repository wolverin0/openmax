<!-- doc-head -->
# STAGE 2216A — Xrefs de los 12 knobs y los handlers `0x50DC`, `0x1B00`, `0x1BFC`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2214A — los diez registros que faltaban estaban en `.rodata`

La wave 195 encontró dos registros porque comparaba direcciones virtuales. La sección de cadenas **tiene dirección cero**, así que la relocación guarda un **desplazamiento relativo**, no una dirección. Trabajando en desplazamientos y recorriendo **todas** las secciones `.rel.*`, aparecen los doce.

| Sección | Registros | Knobs |
| :--- | ---: | :--- |
| `.rodata` | 10 | `noack_mode`, `sta_priority`, `atpc`, `cms_bias`, `ff_cap_rep`, `ff_mcast_airtime_limit`, `ptp_xmit`, `fixed_frame`, `sta_rx_rssi_th`, `daprot` |
| `.data` | 2 | `gpsreset`, `gps_info` |

- `CONFIRMED`: **24** coincidencias, 12 por familia, **sin ningún knob perdido**.
- `REFUTED`: que los otros diez registros no existieran. Estaban en `.rodata`, sección que el barrido anterior no abría para esta búsqueda.
- `CONFIRMED`: hay **cuatro** handlers distintos, no uno:

| Handler | Knobs |
| :--- | :--- |
| `0x2138` | `noack_mode`, `atpc`, `cms_bias`, `ff_cap_rep`, `ff_mcast_airtime_limit`, `ptp_xmit`, `fixed_frame`, `sta_rx_rssi_th`, `daprot` |
| `0x45F0` | `sta_priority` |
| `0x1B00` | `gpsreset` |
| `0x1BFC` | `gps_info` |

- `CONFIRMED`: nueve knobs comparten el handler `0x2138`; `sta_priority` tiene el suyo.

## 2. Stage 2215A — el bloque de registro clona la plantilla

`0x50DC` tiene **204** instrucciones y **10** llamadas con nombre:

```
amalloc_private, memset, snprintf, amalloc_private, memcpy,
amalloc_private, memcpy, amalloc_private, memcpy, register_sysctl_table
```

- `CONFIRMED`: la secuencia es **reservar, borrar, formatear, copiar tres veces y registrar**. Eso es una **clonación de plantilla**: se construye una copia por radio y se registra.
- `REFUTED`: que la plantilla por radio se registre tal cual. Se copia antes.
- `CONFIRMED`: `snprintf` construye el nombre con el índice de radio, lo que encaja con `/dev/uph_%s`.

### Los dos handlers de GPS no son gemelos

| Handler | Instrucciones | Llamadas |
| :--- | ---: | :--- |
| `0x1B00` (`gpsreset`) | 62 | `ubnt_poll_host_gps_reset`, `proc_dointvec` |
| `0x1BFC` (`gps_info`) | 64 | `sscanf`, `ubnt_poll_host_radio_add` |

- `CONFIRMED`: **no** son un par de plantilla. Uno escribe un entero con el manejador estándar `proc_dointvec`; el otro **parsea una cadena** con `sscanf` y llama a `ubnt_poll_host_radio_add`.
- `REFUTED`: que compartan cuerpo. Comparten tamaño aproximado, no lógica.
- `INFERRED`: `gpsreset` es de escritura y `gps_info` de alta de radio.

## 3. Qué cambia
- Los doce knobs quedan localizados, con sección, registro y handler.
- El bloque de registro queda identificado como **clonador**, no como registrador directo.
- Los dos handlers de GPS quedan separados por función, no por tamaño.

## 4. Lo que queda abierto
- `UNKNOWN`: el nombre de los handlers `0x2138` y `0x45F0`.
- `UNKNOWN`: el significado de cada uno de los nueve knobs que comparten `0x2138`.
- `UNKNOWN`: la raíz exacta que recibe cada `register_sysctl_table`.
- `UNKNOWN`: `vtable[456]`.

## 5. Stage 2217A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2214A` | `tools/re/extract_stage2214a_uph_all_rel_sections_12_knob_xrefs_re.py` y su recibo |
| `2215A` | `tools/re/reconcile_stage2215a_uph_0x50dc_and_gps_handlers_0x1b00_0x1bfc_re.py` y su recibo |
| `2217A` | `tools/verify/record_stage2217a_memorymaster_ingest.py` y su recibo |
| `2218A` | `tests/test_stage2214a_to_2219a_suite.py` |
| `2219A` | `tools/verify/verify_stage2219a_wave196_opencode_gate.py` y su recibo |
