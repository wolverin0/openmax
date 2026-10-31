<!-- doc-head -->
# STAGE 2390A — `ku_comm_get_info` (`0x17024`) y dónde ocurre realmente la copia al usuario

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Medido sobre `artifacts/firmware_re_xc_ltu/`. WA y XC coinciden en todo lo reportado.
- Este documento no contiene apellidos.

## 1. Stage 2388A — `get_info` no transfiere nada

| | Valor |
| :--- | :--- |
| Entrada | `0x17024` |
| Tamaño | **5524** |
| Marco | **32** |
| Instrucciones | 1381 |
| Llamadas con nombre | **0** |
| Llamadas locales | **0** |
| Transferencias indirectas | **0** |
| Referencias a copia | **0** |
| Referencias a bloqueo | **0** |

- `CONFIRMED`: `ubnt_poll_ku_comm_get_info` **no llama a nada**, ni por nombre, ni a etiqueta local, ni por registro.
- `CONFIRMED`: tampoco contiene ninguna referencia al símbolo de copia ni a un primitivo de bloqueo.
- `CONFIRMED`: es un **constructor puro**. Arma el informe en su propio espacio y devuelve; la entrega la hace su llamador.
- `CONFIRMED`: 5524 bytes y **cero** transferencias es el dato más fuerte de la etapa: no hay ruta de salida dentro de la función.

## 2. Stage 2389A — la corrección que importa

Wave 222 informó **cero copias** en los cuatro manejadores de estación. **Esa conclusión es `REFUTED`.**

El censo anterior sólo miró relocaciones de **llamada con nombre**. Este módulo **no importa** `copy_to_user` ni `copy_from_user`: su único símbolo de copia es **`__copy_user`**, y se alcanza por registro:

```
lui   at,%hi(__copy_user)
addiu at,at,%lo(__copy_user)
jalr  at
```

Con esa forma, una lista construida con relocaciones de llamada **no puede verla**. Contando referencias al símbolo **sin importar el tipo de transferencia**, el resultado se invierte:

| Manejador | Tamaño | Pares de copia | Indirectas | Bloqueos |
| :--- | ---: | ---: | ---: | ---: |
| `get_info` | 5524 | **0** | 0 | 0 |
| `get_stalist` | 408 | **1** | 1 | 0 |
| `get_stainfo` | 312 | **1** | 1 | 0 |
| `get_sta_spec_data` | 276 | **1** | 1 | 0 |
| `set_sta_spec_data` | 276 | **1** | 1 | 0 |

- `CONFIRMED`: **cuatro** de los cinco manejadores contienen exactamente **una** `__copy_user`.
- `CONFIRMED`: la copia ocurre **dentro del manejador**, no en un ayudante delegado.
- `CONFIRMED`: **cero** bloqueos en los cinco.
- **`REFUTED`**: «cero `copy_from_user`, cero `copy_to_user`, cero `__copy_user`» de la wave 222. Lo que era cierto es que no hay `copy_from_user` ni `copy_to_user` importados; la conclusión de que no había copia era falsa.
- **`REFUTED`** también la lectura derivada: el nodo **no** es sólo superficie de control. Es **ruta de datos** para los cuatro manejadores de estación.

Sitios exactos, medidos:

| Manejador | Desplazamientos de la pareja |
| :--- | :--- |
| `get_stalist` | `0x18674`, `0x18678` |
| `get_stainfo` | `0x187F0`, `0x187F4` |
| `get_sta_spec_data` | `0x18950`, `0x18954` |
| `set_sta_spec_data` | `0x18A64`, `0x18A68` |

- `CONFIRMED`: cada pareja es un `HI16` + `LO16`, que es la firma de la carga de dirección en registro.

### 2.1 La dirección de la copia

- **`INFERRED`**: los tres `get_*` escriben hacia el usuario y `set_sta_spec_data` lee desde el usuario. Se deduce del nombre del manejador.
- **`UNKNOWN`**: la dirección **probada**. `__copy_user(destino, origen, n)` no distingue por la relocación, y probarla exige seguir los registros de argumento hasta el `jalr`.

## 3. Qué cambia
- El nodo de carácter deja de ser «sólo control». Cuatro de sus cinco manejadores **entregan o reciben datos del usuario**.
- La ausencia de copia en `get_info` deja de ser una rareza y pasa a ser un hecho estructural: construye y delega.
- Corregido el método: **un censo de copias no puede basarse en llamadas con nombre** cuando el módulo usa `__copy_user` por registro.

## 4. Lo que queda abierto
- `UNKNOWN`: la dirección de cada copia, probada.
- `UNKNOWN`: qué rutina del llamador consume el informe de `get_info`.
- `UNKNOWN`: el texto del directorio de `/proc`.
- `UNKNOWN`: `set_rate_override` y `vtable[456]`.

## 5. Stage 2391A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`.

## 6. Artefactos
`extract_stage2388a_uph_ku_comm_get_info_0x17024_and_callees_re.py`, `reconcile_stage2389a_uph_ku_comm_delegated_helpers_and_user_copy_re.py`, `record_stage2391a_memorymaster_ingest.py`, `test_stage2388a_to_2393a_suite.py` y `verify_stage2393a_wave225_opencode_gate.py`, cada uno con su recibo.
