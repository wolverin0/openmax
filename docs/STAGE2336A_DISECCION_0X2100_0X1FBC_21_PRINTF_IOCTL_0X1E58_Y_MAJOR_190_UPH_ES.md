<!-- doc-head -->
# STAGE 2336A — Callbacks `0x2100`/`0x1FBC`, las 21 llamadas a `printf`, el `ioctl` de `0x1E58` y el mayor 190

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2334A — quién asigna el búfer

| Callback | Entrada | Tamaño | Llamadas |
| :--- | :--- | ---: | :--- |
| `info` | `.text+0x2100` | **56** | `ubnt_poll_log_buffer_create`, `ubnt_poll_host_log_info` |
| `noack_info` | `.text+0x1FBC` | **56** | `ubnt_poll_log_buffer_create`, `ubnt_poll_host_log_noack_info` |
| `open` | `.text+0x1DE0` | **76** | **ninguna directa** |

- `CONFIRMED`: los dos callbacks son gemelos de **56** bytes. Crean el búfer y lo entregan al formateador que les toca.
- `CONFIRMED`: ambos leen su primer argumento en **`+0xE4`** (228) del objeto que reciben. Es el mismo desplazamiento en los dos, así que ese hueco es compartido y no distingue `info` de `noack_info`.
- `CONFIRMED`: el slot `open` de `.data+0x238` en `+0x30` es `0x1DE0` y **no llama a nada**: tiene un solo salto **indirecto** (`jalr`). Llega al callback por registro.
- **`REFUTED`**: el brief dice que el slot `open` «asigna el búfer de 24 bytes vía `ubnt_poll_log_buffer_create` e invoca el callback de `+0x00`». La asignación **no** está en `open`: está en el callback, un nivel más abajo. `open` sólo transfiere.
- `CONFIRMED`: `open` carga la constante **-25** (`ENOTTY`) y la guarda en `file+28` cuando la llamada indirecta falla.

### 1.1 Las 21 llamadas a `printf`

- `CONFIRMED`: son **21** por familia, y **21 de 21** caen dentro de los dos formateadores. Cero fuera.
- `CONFIRMED`: el formateador `noack_info` ocupa `0xA7FC`..`0xAB50` y el de `info` ocupa `0xAB50`..`0xB26C`. La pertenencia se prueba por **contención de rango**, no por inspección de cada sitio.
- `CONFIRMED`: por tanto `/proc/net/uph_wifi0/info` lo compone `ubnt_poll_host_log_info` (**1820** B) y `/proc/net/uph_wifi0/noack_info` lo compone `ubnt_poll_host_log_noack_info` (**852** B).
- `CONFIRMED`: `puts` no tiene más que un llamador en `0x5C34`, dentro de `read_ex`.
- **`UNKNOWN`**: cuál de los candidatos es el formato de cada sitio. En la ventana de `0xA870` se captura **una** candidata real, la cabecera `NOACK mode BLOCK ACK DATA`, y no alcanza para decidir si es ésa la que consume la llamada. Se registra como **candidato**, sin asignar.
- **`UNKNOWN`**: una cadena vista en una sonda previa, `PTMP Network Configuration initialized ...`, **no se reproduce** con la regla actual de ventana. Queda sin confirmar y no se sostiene.
- `CONFIRMED`: las otras llamadas tampoco se asignan. El registro que carga la cadena no es siempre el primer argumento en la ventana inmediata.

## 2. Stage 2335A — `ioctl` y registro del dispositivo

### 2.1 El manejador de `0x1E58`

- `CONFIRMED`: **356** bytes. Construye **cuatro** palabras de comando y despacha a **cinco** rutinas.

| Comando | Origen |
| :--- | :--- |
| `0xC2145505` | `lui v1,0xC214` en `0x1E74` + `addiu` en `0x1E80` |
| `0x40905501` | `lui v1,0x4090` en `0x1E90` + `addiu` en `0x1E94` |
| `0xC0015502` | `lui v1,0xC001` en `0x1E9C` + `addiu` en `0x1EA0` |
| `0xC6945503` | `lui v1,0xC694` en `0x1EB8` + `addiu` en `0x1EBC` |

- `CONFIRMED`: las cuatro palabras llevan la mitad baja `0x5501`..`0x5505`, consecutiva con un hueco. Es una familia numerada, no cuatro valores sueltos.
- `UNKNOWN`: el mapeo comando → manejador. Se miden las cuatro palabras y las cinco llamadas, pero atribuir cada rama a su rutina requiere seguir los destinos de salto, y esta etapa no lo hace.

| Manejador | Entrada | Tamaño |
| :--- | :--- | ---: |
| `ku_comm_get_info` | `0x17024` | **5524** |
| `ku_comm_get_stalist` | `0x185B8` | 408 |
| `ku_comm_get_stainfo` | `0x18750` | 312 |
| `ku_comm_get_sta_spec_data` | `0x18888` | 276 |
| `ku_comm_set_sta_spec_data` | `0x1899C` | 276 |

- `CONFIRMED`: `get_info` sola pesa **5524** bytes, más que las otras cuatro juntas. Es el núcleo del nodo de control.

### 2.2 El registro: mayor 190 y **cuatro** menores

```
0x1D84  lui   a2,$LC3
0x1D88  addiu sp,sp,-24
0x1D8C  lui   a0,0x0BE0     ; 0x0BE00000 = MKDEV(190, 0)
0x1D90  addiu a1,zero,4     ; cuatro menores
0x1D98  jal   register_chrdev_region
0x1D9C  addiu a2,a2,$LC3    ; relleno: el nombre
```

- `CONFIRMED`: `ubnt_poll_host_init_char_dev` (`0x1D84`, 76 B) registra **`0x0BE00000`** con cuenta **4**. Es mayor **190** (`0xBE`), menor 0, **cuatro** menores.
- `CONFIRMED`: `ubnt_poll_host_uninit_char_dev` (`0x1DD0`, 12 B) hace `unregister_chrdev_region(0x0BE00000, 4)`. El rango se libera exactamente como se pidió.
- `CONFIRMED`: el mayor que el brief daba por observado en vivo, **190**, queda probado en el binario, no sólo observado.
- **Nuevo respecto al brief**: son **cuatro** menores, no uno. `cdev_add` registra **un** dispositivo con cuenta 1, así que el módulo reserva cuatro y usa uno.

### 2.3 El directorio de `/proc`

- `CONFIRMED`: `proc_mkdir` se llama en `0x5414`. En `0x5410` se carga `lw a1,28(v1)` con `v1 = init_net`, es decir el padre es **`init_net.proc_net`**.
- `UNKNOWN`: el **nombre** del directorio. Se pasa en `a0` desde `s1`, materializado antes de la ventana, y no queda un `$LC` contiguo que lo resuelva. Que sea `uph_wifi0` lo dice el brief y la observación en vivo, no esta etapa.

## 3. Lo que queda abierto
- `UNKNOWN`: las otras 20 cadenas de formato de `printf`.
- `UNKNOWN`: el mapeo comando → manejador del `ioctl`.
- `UNKNOWN`: el nombre del directorio de `/proc`.
- `UNKNOWN`: los tres tipos de mensaje de `set_rate_override`.
- `UNKNOWN`: `vtable[456]`.

## 4. Stage 2337A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`.

## 5. Artefactos
Los cinco guiones de la wave y sus recibos: `extract_stage2334a_uph_0x2100_0x1fbc_open_and_21_printf_callsites_re.py`, `reconcile_stage2335a_uph_0x1e58_ioctl_ku_comm_and_chrdev_major190_re.py`, `record_stage2337a_memorymaster_ingest.py`, `test_stage2334a_to_2339a_suite.py` y `verify_stage2339a_wave216_opencode_gate.py`.
