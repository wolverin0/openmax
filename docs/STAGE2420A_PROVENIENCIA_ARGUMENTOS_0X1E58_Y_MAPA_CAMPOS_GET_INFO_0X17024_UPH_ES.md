<!-- doc-head -->
# STAGE 2420A — Proveniencia de argumentos en `0x1E58` y mapa de campos de `get_info` (`0x17024`)

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Medido sobre `artifacts/firmware_re_xc_ltu/`. WA y XC coinciden en todo lo reportado.
- Este documento no contiene apellidos.

## 1. Stage 2418A — qué recibe el ioctl y qué entrega

### 1.1 El orden de argumentos queda probado

```
0x1E60  lw    v0,248(a0)     ; v0 = inode->i_cdev
0x1E64  lw    a0,104(a1)     ; a0 = filp->private_data
0x1E68  addiu v1,v0,-132     ; v1 = cdev - 0x84 = radio
0x1E6C  bne   a0,v1,+79      ; si private_data != radio -> error
0x1E70  addiu v1,zero,-22    ; EINVAL
```

- `CONFIRMED`: `inode = a0`, `filp = a1`. El dispositivo sale del **inodo**, en `+0xF8` (248).
- `CONFIRMED`: `radio = inode->i_cdev - 132`, y se **valida** contra `filp->private_data` en `+0x68` (104).
- `CONFIRMED`: si no coinciden, devuelve **-22** sin tocar nada.

### 1.2 El primer argumento no es `radio`

| Llamada | Primer argumento | Segundo argumento |
| :--- | :--- | :--- |
| `get_info` `0x1EDC` | `lw a0,96(v0)` | `addu a1,a3,zero` |
| `get_stalist` `0x1F00` | `lw a0,96(v0)` | `addu a1,a3,zero` |
| `get_stainfo` `0x1F34` | `lw a0,96(v0)` | `addu a1,a3,zero` |
| `get_sta_spec_data` `0x1F64` | `lw a0,96(v0)` | `addu a1,a3,zero` |
| `set_sta_spec_data` `0x1F94` | `lw a0,96(v0)` | `addu a1,a3,zero` |

- **`REFUTED`**: el brief dice que `0x1E58` pasa **`(radio, arg)`**. No pasa `radio`.
- `CONFIRMED`: las cinco llamadas cargan el primer argumento como **offset 96 del dispositivo**, que es **`radio + 0xE4`** (96 + 132 = 228).
- `CONFIRMED`: es el **mismo hueco `+0xE4`** que leían los dos callbacks de `/proc` en la wave 216. Ese puntero es el contexto compartido.
- `CONFIRMED`: el segundo argumento es el **tercer argumento del ioctl** (`a3`), movido en el relleno de demora.
- `CONFIRMED`: las cinco coinciden. No hay variación.

### 1.3 La entrega del informe

- `CONFIRMED`: el cuerpo del ioctl **no contiene ninguna referencia a copia** (`ioctl_copies = 0`).
- `CONFIRMED`: `get_info` hace **178 escrituras** a través de su segundo argumento.
- `CONFIRMED`: por tanto `get_info` **no usa ayudante de copia**: escribe **directo** en el puntero que recibe.
- Esto cierra el `UNKNOWN` de la wave 227: el camino de entrega es el **puntero del llamador**, con almacenes normales.

### 1.4 Una contradicción que no resuelvo

- `CONFIRMED`: `get_info` escribe en `arg` con **almacenes planos**.
- `CONFIRMED`: los manejadores de spec copian a `arg` con **`__copy_user`** (wave 225).
- **`UNKNOWN`**: cuál de las dos lecturas es la correcta. O `arg` es un buffer del núcleo y el `__copy_user` de los otros sobra, o `get_info` escribe directo a memoria de usuario, lo que en MIPS es incorrecto. **No lo resuelvo por suposición.**

## 2. Stage 2419A — el mapa del informe

| | Valor |
| :--- | :--- |
| Escrituras por el 2.º argumento | **178** |
| Offsets distintos escritos | **60** |
| Extensión del informe | `0x00`..`0x92` (**146** bytes) |
| Lecturas por el 1.er argumento | **84** |
| Lecturas por el 3.er puntero | **12** |

- `CONFIRMED`: el informe ocupa como máximo **146 bytes** y empieza en el offset 0.
- `CONFIRMED`: los offsets escritos empiezan densos y consecutivos —`0,1,2,3,4,8,12,16,17,18,20,24,28,30,32`— lo que es una **cabecera de estado**, no una tabla de longitud variable.
- `CONFIRMED`: el origen se lee del primer argumento en `0,12,16,20,24,25,26,28,32,268,276,280` y luego en el bloque **`4332`..`4494`** (`0x10EC`..`0x118E`).
- `CONFIRMED`: ese bloque alto es la **misma región** que los callbacks de `/proc` seleccionaban en la wave 216 según la bandera de `+0x118`. El informe y el registro leen el mismo sitio.
- `CONFIRMED`: el tercer puntero aporta 12 lecturas en `121,122,124,152,160,162,976,984,986,1798,1802,1809`, una **ficha de estación** y no la estructura del dispositivo.

## 3. Qué cambia
- El orden de argumentos deja de ser convención: lo fijan los offsets de `i_cdev` y `private_data`.
- El primer argumento de las cinco llamadas deja de ser `radio` y pasa a ser el puntero de `radio+0xE4`.
- La entrega del informe deja de ser `UNKNOWN`: **escritura directa**, sin ayudante.

## 4. Lo que queda abierto
- `UNKNOWN`: si `arg` es puntero de usuario o buffer del núcleo. La contradicción entre escritura plana y `__copy_user` queda registrada sin resolver.
- `UNKNOWN`: el nombre del hueco `radio+0xE4`.
- `UNKNOWN`: el significado de los offsets de cabecera `0..32`.
- `UNKNOWN`: `set_rate_override`, `vtable[456]` y el nombre del directorio de `/proc`.

## 5. Stage 2421A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax` y se añadieron las filas con **CRLF**.

## 6. Artefactos
`build_stage2418a_uph_0x1e58_get_info_return_and_3rd_arg_provenance_re.py`, `build_stage2419a_uph_0x17024_get_info_field_map_and_offsets_re.py`, `record_stage2421a_memorymaster_ingest.py`, `test_stage2418a_to_2423a_suite.py` y `verify_stage2423a_wave230_opencode_gate.py`, cada uno con su recibo.
