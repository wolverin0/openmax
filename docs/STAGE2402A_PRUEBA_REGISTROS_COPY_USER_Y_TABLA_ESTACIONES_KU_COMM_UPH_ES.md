<!-- doc-head -->
# STAGE 2402A — Prueba de registros de `__copy_user` y tabla de estaciones en `ku_comm`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Medido sobre `artifacts/firmware_re_xc_ltu/`. WA y XC coinciden en todo lo reportado.
- Este documento no contiene apellidos.

## 1. Stage 2400A — la anchura está probada, la dirección sólo acotada

En los cuatro sitios de copia, la instrucción inmediata que carga el registro de longitud es la misma:

| Estación | Sitio | Longitud | Destino (`a0`) | Origen (`a1`) |
| :--- | :--- | ---: | :--- | :--- |
| `get_stalist` | `0x18674` | **6** | no fijado en la ventana | no fijado |
| `get_stainfo` | `0x187F0` | **6** | `addu a0,v0,zero` con `v0 = sp+16` | no fijado |
| `get_sta_spec_data` | `0x18950` | **6** | `addu a0,a3,zero` | `addiu a1,a2,8` |
| `set_sta_spec_data` | `0x18A64` | **6** | `addu a0,a3,zero` | `addiu a1,a1,8` |

- `CONFIRMED`: **seis bytes** en las cuatro. La anchura sale de la carga inmediata, no del nombre del manejador.
- `CONFIRMED`: en los dos manejadores de spec el destino es el **tercer argumento del ioctl** y el origen un **buffer del núcleo desplazado 8 bytes**.
- `CONFIRMED`: en `get_stainfo` el destino es un **buffer de pila**.
- `INFERRED`: si el tercer argumento es puntero de usuario, los dos de spec copian **núcleo → usuario** y `get_stainfo` **usuario → núcleo**.
- **`UNKNOWN`**: la procedencia del tercer argumento. Sin eso, la dirección no está probada.

### 1.1 Corrección de método

Mi primer informe tomó como destino el `lw a0,4336(s0)`, que es código muerto: `addu` escribe en **`rd`**, no en `rt`, y mi filtro miraba `rt`. El destino real es el `addu` posterior. Esta es la novena corrección de la serie y la causa de que la wave anterior no cerrara.

### 1.2 Cómo entrega `get_info`

- `CONFIRMED`: se le llama en `0x1EDC` y en la ventana sólo se prepara **`lw a0,96(v0)`**.
- `CONFIRMED`: `get_info` no transfiere nada por sí mismo (wave 225), así que **no** copia al usuario.
- **`UNKNOWN`**: el camino por el que su informe llega al espacio de usuario. Ni la llamada ni la función contienen una transferencia.

## 2. Stage 2401A — tabla de estaciones y mutación

| Manejador | Tamaño | Marco | Escrituras fijas | Llamadas con nombre |
| :--- | ---: | ---: | ---: | :--- |
| `get_stalist` | 408 | 24 | 2 | — |
| `get_stainfo` | 312 | 40 | 0 | `sta_hash_find` |
| `get_sta_spec_data` | 276 | 24 | 0 | — |
| `set_sta_spec_data` | 276 | 24 | 0 | — |

- `CONFIRMED`: **`ubnt_poll_host_sta_hash_find`** es la única rutina con nombre que llaman las cuatro, y sólo la usa `get_stainfo`.
- `CONFIRMED`: **`set_sta_spec_data` no escribe en ningún desplazamiento fijo** de la estructura del dispositivo. Sus únicas escrituras directas son los dos salvamentos de prólogo.
- `CONFIRMED`: `get_sta_spec_data` tampoco escribe en desplazamiento fijo.
- `CONFIRMED`: ambos trabajan **enteramente a través de punteros**, que es coherente con los destinos `a3` del apartado anterior.
- **`UNKNOWN`**: los desplazamientos de campo que escribe `set_sta_spec_data`. Al ser escritura indirecta, no aparecen como inmediatos y asignarlos exigiría seguir el registro base.
- **`UNKNOWN`**: los saltos locales que hacen la búsqueda de estación en los tres manejadores sin llamada con nombre.

## 3. Qué cambia
- La anchura de la copia deja de ser una suposición: **6 bytes**, con el sitio y la instrucción de longitud de cada una.
- La dirección deja de estar implícita y pasa a estar **acotada con su supuesto declarado**.
- `set_sta_spec_data` deja de ser «escribe campos» y pasa a ser «escribe **a través de un puntero**, sin desplazamientos legibles».

## 4. Lo que queda abierto
- `UNKNOWN`: la procedencia del tercer argumento del ioctl.
- `UNKNOWN`: los desplazamientos de campo de la escritura indirecta.
- `UNKNOWN`: el camino de entrega del informe de `get_info`.
- `UNKNOWN`: el texto del directorio de `/proc`, `set_rate_override` y `vtable[456]`.

## 5. Stage 2403A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax` y se añadieron las filas con **CRLF**.

## 6. Artefactos
`build_stage2400a_uph_ku_comm_copy_user_args_and_get_info_caller_re.py`, `build_stage2401a_uph_ku_comm_sta_table_offsets_and_mutation_re.py`, `record_stage2403a_memorymaster_ingest.py`, `test_stage2400a_to_2405a_suite.py` y `verify_stage2405a_wave227_opencode_gate.py`, cada uno con su recibo.
