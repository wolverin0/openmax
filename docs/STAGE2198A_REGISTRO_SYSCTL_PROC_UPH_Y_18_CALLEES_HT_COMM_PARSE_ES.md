<!-- doc-head -->
# STAGE 2198A — Registro sysctl/proc en `ubnt_poll_host` y los callees de `ht_comm_parse`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2196A — corrección de la wave 191

La wave 191 informó que ninguna cadena de knob aparecía en el módulo. **Era un error de alcance**: el barrido sólo abría `.rodata` y `.data`, y las cadenas viven en **`.rodata.str1.4`**.

| Medición | WA_uph | XC_uph |
| :--- | ---: | ---: |
| Cadenas de knob encontradas | **12** | **12** |
| Registros `ctl_table` resueltos | **12** | **12** |

- `CONFIRMED`: las doce cadenas existen en `.rodata.str1.4`, sección que la etapa anterior no abrió.
- `REFUTED`: el «cero» de la wave 191. No era una ausencia de datos, era un barrido incompleto.

### Sitios de registro

| Símbolo | Dirección |
| :--- | :--- |
| `register_sysctl_table` | `0x1D5C` |
| `register_sysctl_table` | `0x5400` |
| `proc_mkdir` | `0x5414` |

- `CONFIRMED`: los tres sitios son idénticos en WA y XC.
- `CONFIRMED`: hay **dos** registros de tabla y una creación de directorio, no uno.

### Las hojas de la tabla

| `.procname` | Registro | `.data` | `.maxlen` | `.mode` |
| :--- | :--- | :--- | ---: | :--- |
| `gpsreset` | `0x150` | `0x114` | 4 | `0x1A4` |
| `gps_info` | `0x17C` | `0x14` | 256 | `0x1A4` |
| `noack_mode` | `0x31C` | `0x9A4` | 4 | `0x1A4` |
| `sta_priority` | `0x374` | `0x1A4` | 2048 | `0x1A4` |

- `CONFIRMED`: `.mode` vale `0x1A4` en todas, que es `0644`: lectura para todos, escritura sólo para el dueño.
- `CONFIRMED`: los `.maxlen` varían con el campo: 4 bytes para un entero, 256 para una cadena, 2048 para una lista.
- `CONFIRMED`: `.child` es nulo en las cuatro, así que son hojas.
- `UNKNOWN`: `.proc_handler`. El valor leído es cero en el desplazamiento probado, lo que indica que el campo no está donde se buscó. Se reporta como no medido, no como nulo.

## 2. Stage 2197A — los callees locales del parse

| Medición | WA | XC |
| :--- | ---: | ---: |
| Llamadas locales en `ubnt_poll_ht_comm_parse` | 27 | 27 |
| Que caen en el inicio de un símbolo | **0** | **0** |

- `CONFIRMED`: **ninguna** de las llamadas locales cae en el primer byte de una función con símbolo.
- `CONFIRMED`: los destinos resueltos son `0x0` —sin resolver— o `0x15E34`, que está **5536** bytes dentro del propio ayudante, en su cola.
- `REFUTED`: que las 18 llamadas de la wave 190 fueran a funciones distintas con nombre. No lo son: o no se resuelven, o entran en la cola compartida del mismo ayudante.
- `UNKNOWN`: los destinos reales de las llamadas no resueltas. El addend in-place vale cero y el símbolo es de sección, así que el desplazamiento no está en la instrucción.

## 3. Qué cambia
- La superficie de knobs **sí** está en el módulo, y con nombres, tamaños y permisos medidos.
- El «cero» de la wave 191 queda corregido y atribuido a un barrido de dos secciones en vez de todas.
- Los callees del parse dejan de contarse como «18 funciones»: no hay funciones distintas.

## 4. Lo que queda abierto
- `UNKNOWN`: `.proc_handler` de cada hoja, por desplazamiento mal ubicado.
- `UNKNOWN`: los destinos reales de las llamadas locales no resueltas.
- `UNKNOWN`: qué hace el segundo `register_sysctl_table` de `0x5400` frente al de `0x1D5C`.
- `UNKNOWN`: `vtable[456]`.

## 5. Stage 2199A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2196A` | `tools/re/extract_stage2196a_uph_register_sysctl_and_leaf_ctl_table_re.py` y su recibo |
| `2197A` | `tools/re/reconcile_stage2197a_uph_ht_comm_parse_18_callees_re.py` y su recibo |
| `2199A` | `tools/verify/record_stage2199a_memorymaster_ingest.py` y su recibo |
| `2200A` | `tests/test_stage2196a_to_2201a_suite.py` |
| `2201A` | `tools/verify/verify_stage2201a_wave193_opencode_gate.py` y su recibo |
