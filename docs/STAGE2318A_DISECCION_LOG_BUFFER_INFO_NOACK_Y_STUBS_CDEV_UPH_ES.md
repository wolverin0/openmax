<!-- doc-head -->
# STAGE 2318A — Búfer de registro `info`/`noack_info`, sus lectores y los callbacks del nodo de carácter

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2316A — la familia del búfer de registro

Ocho rutinas llevan el prefijo `ubnt_poll_log_buffer_`. Suman **944** bytes por familia y las dos familias coinciden byte a byte en desplazamiento y tamaño.

| Rutina | Entrada | Tamaño | Marco | Llamadas |
| :--- | :--- | ---: | ---: | :--- |
| `get_length` | `0x5C50` | **8** | 0 | ninguna |
| `create` | `0x5A9C` | 60 | 24 | `amalloc_private` |
| `puts` | `0x5AD8` | 284 | 48 | `amalloc_private`, `memcpy` |
| `printf` | `0x5BF4` | 92 | **808** | `vsnprintf`, `puts` |
| `read_ex` | `0x5C58` | **336** | 48 | ninguna con nombre |
| `read` | `0x5DA8` | 40 | 24 | `read_ex` |
| `lseek` | `0x5DD0` | 52 | 0 | ninguna con nombre |
| `destroy` | `0x5E04` | 72 | 24 | `afree_private` |

- `CONFIRMED`: `printf` reserva **808** bytes de marco, el mayor de la familia, porque aloja el `va_list` y el texto formateado.

### 1.1 Quién los llama

| Rutina | Sitios |
| :--- | :--- |
| `read_ex` | `0x2030` (slot `read` de `/proc`), `0x5DB8` (envoltorio `read`) |
| `lseek` | `0x20E0` (slot `llseek` de `/proc`) |
| `create` | `0x1FC4`, `0x2108` |
| `destroy` | `0x1FF8` |
| `puts` | `0x5C30` (dentro de `read_ex`) |
| `printf` | **21** sitios, de `0xA86C` a `0xB1D4` |
| `get_length` | **ninguno** |
| `read` | **ninguno** |

- `CONFIRMED`: `get_length` y `read` **no tienen llamador** en el módulo. `read` es un envoltorio que existe pero nadie usa; `get_length` queda como acceso muerto.

### 1.2 La estructura del anillo: 24 bytes

Tres medidas independientes fijan el tamaño:

1. `create` pide `amalloc_private(0, 24, 0)` y **pone a cero** las palabras en los desplazamientos `0`, `4`, `8`, `12`, `16` y `20`.
2. `get_length` devuelve la palabra en `+0x00`.
3. `lseek` escribe la posición pedida en `+0x0C` y limpia `+0x10` en su rama de error.

| Offset | Uso medido |
| :--- | :--- |
| `+0x00` | longitud devuelta por `get_length` |
| `+0x04` | puntero al payload, asignado por `puts` |
| `+0x08` | leído por `puts` al comienzo |
| `+0x0C` | posición de lectura y escritura |
| `+0x10` | mutado por `read_ex` y limpiado por `lseek` |
| `+0x14` | mutado por `read_ex` |

- `CONFIRMED`: el payload se pide aparte, con `addiu a1,zero,780` en `0x5B18`, y se guarda en `+0x04`.
- `UNKNOWN`: el significado de `+0x08`, `+0x10` y `+0x14`. Se miden sus accesos, no su papel.

### 1.3 No hay bloqueo

- `CONFIRMED`: **cero** llamadas a `spin_lock`, `mutex_lock`, `atomic_*`, semáforos o `down`/`up` en toda la familia. El anillo está **sin sincronizar**.
- `CONFIRMED`: el estado del anillo se muta desde `read_ex`, `lseek` y `puts` sin ninguna protección. Con `printf` llamado desde 21 sitios del camino de registro, eso es una condición de carrera real, no teórica.

## 2. Stage 2317A — la cola de `radio_add`

```
0x5424  addiu a1,zero,8      ; tamaño de la reserva
0x5428  jal   amalloc_private
0x5430  addu  s1,v0,zero
0x5434  sw    s0,4(v0)       ; +4 = radio
0x5438  lui   v0,.text
0x543C  addiu v0,v0,0x2100   ; puntero a función
0x5444  sw    v0,0(s1)       ; +0 = 0x2100
```

- `CONFIRMED`: cada reserva mide **8** bytes y contiene `{ puntero a función, puntero a radio }`.
- **`REFUTED`**: el brief las llama «los dos búferes de registro asignados en `radio_add`». **No son búferes.** El búfer de 24 bytes lo crea `ubnt_poll_log_buffer_create`, que no se llama en `radio_add`. Estas reservas son objetos de despacho para las entradas de `/proc`.
- `CONFIRMED`: la primera lleva `.text+0x2100` y la segunda `.text+0x1FBC`. Ambas funciones llaman a `create`, de ahí que ésta tenga dos llamadores.

### 2.1 Qué offset recibe qué

| Offset | Recibe | Origen |
| :--- | :--- | :--- |
| `radio+0x78` | entrada `/proc` `info` | retorno de `proc_create_data` |
| `radio+0x7C` | entrada `/proc` `noack_info` | retorno de `proc_create_data` |
| `radio+0xE8` | objeto 1 | `amalloc_private` |
| `radio+0xEC` | objeto 2 | `amalloc_private` |
| `radio+0xA8` | `__this_module` | `lui`/`addiu` |
| `radio+0xAC` | `.data+0x1D0` | `lui`/`addiu` |

- **`REFUTED`**: el brief empareja `124(s0)`/`0x7C` con `236(s0)`/`0xEC` como si ambos fueran punteros de búfer. `0x7C` guarda la **entrada de `/proc`** y sólo `0xEC` guarda un objeto; su pareja es `0xE8`, no `0x7C`.

### 2.2 El registro del dispositivo

- `CONFIRMED`: `cdev_init(radio+0x84, .data+0x1D0)`.
- `CONFIRMED`: `cdev_add(radio+0x84, dev, 1)`. El contador es **1** (`addiu a2,zero,1` en el relleno de demora de `0x54F4`).
- `CONFIRMED`: tras el alta se imprime `$LC136` = `ubnt_poll_host %s: Char device created succesfully err %d` (el texto del firmware trae esa falta) y en la rama de error `$LC135` = `... could not be created err %d`.
- `UNKNOWN`: el **número de dispositivo**. Llega en `s3`, pero `s3` se construye entre `0x5124` y `0x51F8` con `lbu` y aritmética de dígitos, y **no hay** llamada a `register_chrdev_region` ni `alloc_chrdev_region` en la cola. Resolver el mayor y el menor exige una etapa propia.

### 2.3 La tabla de carácter completa: seis slots

| Offset | Campo | Valor | Cuerpo |
| :--- | :--- | :--- | :--- |
| `+0x00` | `owner` | 0 | `__this_module` |
| `+0x08` | `read` | `0x1E48` | 8 B, devuelve **-22** |
| `+0x0C` | `write` | `0x1E50` | 8 B, devuelve **-22** |
| `+0x20` | `ioctl` | `0x1E58` | 356 B |
| `+0x30` | `open` | `0x1E2C` | 20 B |
| `+0x38` | `release` | `0x1E40` | 8 B |

- `CONFIRMED`: `read` y `write` devuelven **-22** (`EINVAL`) sin tocar datos. El nodo no transporta flujo, sólo control.
- `CONFIRMED`: `open` hace `file->private_data = inode->i_cdev - 132` y devuelve 0.
- `CONFIRMED`: `release` ocupa **8** bytes y no llama a nada.

### 2.4 Séptima corrección de método: `+0x30` es `open`

- El `struct file_operations` de este núcleo incluye `ioctl`, `unlocked_ioctl` y `compat_ioctl`, así que `open` cae en **`+0x30`** y `release` en **`+0x38`**.
- `CONFIRMED`: el código de `+0x30` **escribe `private_data` y devuelve 0**, que es la forma de un `open`. El de `+0x38` ocupa 8 bytes y no hace nada.
- **`REFUTED`**: la etiqueta `release` para `+0x30` que di la wave 211. También queda corto el recuento: son **seis** slots poblados y **cinco** con código, no cinco y cuatro.
- Esto **no** cambia el hallazgo de la wave 213 anterior sobre `.data+0x238`: la tabla de `/proc` sigue teniendo `llseek` en `+0x04` y `read` en `+0x08`, y su `+0x30` también es un `open`.

## 3. Lo que queda abierto
- `UNKNOWN`: el número de dispositivo con su mayor y menor.
- `UNKNOWN`: el papel de `+0x08`, `+0x10` y `+0x14` del anillo.
- `UNKNOWN`: los tres tipos de mensaje de `set_rate_override`.
- `UNKNOWN`: `vtable[456]`.

## 5. Stage 2319A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`.

## 6. Artefactos
Los cinco guiones de la wave y sus recibos: `extract_stage2316a_uph_log_buffer_read_lseek_and_writers_re.py`, `reconcile_stage2317a_uph_cdev_stubs_and_radio_log_ptrs_re.py`, `record_stage2319a_memorymaster_ingest.py`, `test_stage2316a_to_2321a_suite.py` y `verify_stage2321a_wave213_opencode_gate.py`.
