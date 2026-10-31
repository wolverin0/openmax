<!-- doc-head -->
# STAGE 2186A — El ayudante `0x14894` y el llamador `0x63B58` de `ubntbox`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2184A — qué hace el ayudante compartido

`ubnt_poll_ht_comm_parse` vive en `0x14894` y mide **5564** bytes, igual en WA y XC.

| Callee con nombre | Llamadas |
| :--- | ---: |
| `amalloc_private` | 5 |
| `memcpy` | 3 |
| `memset` | 1 |

- `CONFIRMED`: **18** llamadas con nombre por familia, y **18** locales resueltas por el addend in-place.
- `CONFIRMED`: el ayudante **asigna y copia**: cinco reservas, tres copias y un borrado.
- `CONFIRMED`: no importa `copy_from_user` ni `copy_to_user`. La transferencia con el usuario no ocurre aquí.
- `CONFIRMED`: la estructura de control es corta: **6** comparaciones por familia, repartidas en `v0` (3), `v1`, `t8` y `t9`.
- `REFUTED`: que el ayudante sea un despachador de comandos grande. Tiene seis comparaciones en 5564 bytes: el volumen está en el parseo, no en el salto.
- `CONFIRMED`: sólo **una** referencia a `.rodata`/`.data` por familia. El ayudante casi no usa cadenas.
- `UNKNOWN`: el significado de cada una de las seis comparaciones.

## 2. Stage 2185A — el llamador de U1 y los nombres de los knobs

### El lado del usuario

- `CONFIRMED`: `ubntbox` contiene **21** cadenas de ruta por familia, 42 en total entre las dos.
- `CONFIRMED`: la mayoría son subrutas `/dev/uph_%s/<campo>`; los knobs presentes son `fixed_frame`, `sta_rx_rssi_th`, `enable`, `noack_mode`, `daprot`, `sta_priority`, `ff_cap_rep`, `cms_bias`, `ff_mcast_airtime_limit`, `ptx_xmit`… y los literales `gps_info`, `gpsreset`, `addradio`.
- `UNKNOWN`: la entrada de la función que contiene `0x63B58`. El barrido de prólogo no la cerró, así que el llamador queda localizado por dirección y no por función.

### El lado del kernel

- `CONFIRMED`: `ubnt_poll_host.ko` importa **`proc_mkdir`** y **`register_sysctl_table`**. Es decir, sí registra una tabla de sysctl.
- `CONFIRMED`: **ninguna** de las cadenas de knob de `ubntbox` aparece como literal en `.data` ni en `.rodata` del módulo: el recuento es **0**.
- `REFUTED`: que las rutas `/dev/uph_%s/<campo>` de `ubntbox` se correspondan con nombres literales de `ctl_table` en este módulo. No coinciden.
- `INFERRED`: la tabla de sysctl se registra con nombres que no están en el binario del módulo, o se construye con otra forma —posiblemente en `.bss` o mediante una macro que arma la cadena en ejecución.
- `UNKNOWN`: dónde viven esos nombres, y por tanto el emparejamiento knob por knob.

## 3. Lo que cambia
- El ayudante compartido deja de ser una caja negra: **reserva y copia**, no despacha.
- Queda medido que la transferencia con el usuario **no** está en el ayudante.
- Queda refutado el emparejamiento directo entre las rutas de `ubntbox` y las cadenas del módulo.

## 4. Lo que queda abierto
- `UNKNOWN`: la semántica de las seis comparaciones del ayudante.
- `UNKNOWN`: la entrada de la función que contiene `0x63B58`.
- `UNKNOWN`: dónde están los nombres de la tabla de sysctl del módulo.
- `UNKNOWN`: `vtable[456]`, que sigue llenándose en ejecución.

## 5. Stage 2187A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2184A` | `tools/re/extract_stage2184a_uph_ht_comm_parse_0x14894_dissection_re.py` y su recibo |
| `2185A` | `tools/re/reconcile_stage2185a_ubntbox_0x63b58_and_proc_sys_dev_uph_re.py` y su recibo |
| `2187A` | `tools/verify/record_stage2187a_memorymaster_ingest.py` y su recibo |
| `2188A` | `tests/test_stage2184a_to_2189a_suite.py` |
| `2189A` | `tools/verify/verify_stage2189a_wave191_opencode_gate.py` y su recibo |
