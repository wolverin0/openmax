<!-- doc-head -->
# STAGE 2306A — Los tres callbacks de `.data+0x238` y el `file_operations` de carácter en `.data+0x1D0`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2304A — qué hace cada slot

| Slot | Entrada | Tamaño | Marco | Llamadas |
| :--- | :--- | ---: | ---: | :--- |
| `release` | `.text+0x1DE0` | **76** | 24 | **ninguna** |
| `read` | `.text+0x2014` | **92** | 24 | `ubnt_poll_log_buffer_read_ex` |
| `llseek` | `.text+0x20D4` | **44** | 24 | `ubnt_poll_log_buffer_lseek` |

- `CONFIRMED`: los **tres** cuerpos llegan a `jr ra` en **212** bytes por familia. Ninguno tiene nombre en `.symtab`.
- `CONFIRMED`: ninguno carga constantes de cadena. Los tres son envoltorios: no hay `$LC` en sus cuerpos.
- `CONFIRMED`: el slot `read` llama a la **lectura** del búfer de registro, y el slot `llseek` llama al **desplazamiento** del mismo búfer.

### 1.1 Los nombres de campo quedan probados

La wave 209 dejó `UNKNOWN` la asignación de los dos punteros porque el modo declarado no cuadraba. Los llamados lo resuelven:

- `CONFIRMED`: `.text+0x2014` → `ubnt_poll_log_buffer_read_ex` (336 B en `0x5C58`) ⇒ **es el manejador de lectura**.
- `CONFIRMED`: `.text+0x20D4` → `ubnt_poll_log_buffer_lseek` (52 B en `0x5DD0`) ⇒ **es el de desplazamiento**.
- `CONFIRMED`: `.text+0x1DE0` no llama a nada y ocupa el slot `release` ⇒ **es la liberación**.

Es decir, el orden de campos que se había asumido **sí** es el correcto. El `UNKNOWN` de la wave 209 queda **cerrado**.

### 1.2 El modo es cero, no `0o10`

```
0x5424  addiu a1,zero,8      <- segundo argumento de amalloc_private
0x5428  jal   amalloc_private
0x542c  addu  a2,zero,zero   <- relleno de demora
0x5454  addiu a0,a0,$LC133   <- "info"
0x5458  jal   proc_create_data
0x545c  addu  a1,zero,zero   <- relleno de demora: a1 = 0
```

- `CONFIRMED`: el `a1` que recibe `proc_create_data` se fija en el **relleno de demora**, y vale **0**. Lo mismo en `0x54A0` (`0x54A4`).
- `REFUTED`: la lectura de la wave 204, que tomó el `addiu a1,zero,8` de `0x5424` como modo `0o10`. Esa instrucción es el **tamaño** que pide `amalloc_private`, no un modo de fichero. **Sexta corrección de método.**
- `CONFIRMED`: por eso desaparece la contradicción. Con modo 0 y sin `write`, no hay nada que estorbe al manejador de lectura.

### 1.3 Los cinco argumentos, medidos

| Argumento | Registro | Valor en `0x5458` | Valor en `0x54A0` |
| :--- | :--- | :--- | :--- |
| nombre | `a0` | `$LC133` = `info` | `$LC134` = `noack_info` |
| modo | `a1` | **0** | **0** |
| padre | `a2` | `lw a2,116(s0)` | `lw a2,116(s0)` |
| `proc_fops` | `a3` | `.data+0x238` | `.data+0x238` |
| `data` | `16(sp)` | `s1` = `amalloc_private` | `s1` = `amalloc_private` |

- `CONFIRMED`: las **dos** entradas comparten tabla y padre; sólo cambian nombre y reserva.

## 2. Stage 2305A — el `cdev_init` de `radio_add`

```
0x54BC  lui   s5,0x0000        R_MIPS_HI16 contra .data
0x54C0  addiu s1,s0,132        <- a0 = radio+0x84, el cdev embebido
0x54C4  addiu a1,s5,464        R_MIPS_LO16 contra .data
0x54C8  jal   cdev_init
```

- `CONFIRMED`: `cdev_init(radio+0x84, .data+0x1D0)`. El segundo argumento sale de un par `lui`/`addiu` **relocado contra `.data`**, con inmediato **464**.
- `CONFIRMED`: `.data+0x1D0` es una tabla **distinta** de la de `/proc` (`.data+0x238`). Son dos objetos separados por 104 bytes.
- `CONFIRMED`: la tabla tiene **cinco** slots poblados y **cuatro** con código.

| Offset | Campo | Valor | Destino |
| :--- | :--- | :--- | :--- |
| `+0x00` | `owner` | 0 | `__this_module` |
| `+0x08` | `read` | `0x1E48` | 8 B, sin llamadas |
| `+0x0C` | `write` | `0x1E50` | 8 B, sin llamadas |
| `+0x20` | `ioctl` | `0x1E58` | **356 B**, cinco llamadas |
| `+0x30` | `release` | `0x1E2C` | 20 B, sin llamadas |

- `CONFIRMED`: el `ioctl` de `0x1E58` despacha a `ubnt_poll_ku_comm_get_info`, `get_stalist`, `get_stainfo`, `get_sta_spec_data` y `set_sta_spec_data`. Es la **superficie de control** del nodo de carácter.
- `CONFIRMED`: el slot de desplazamiento queda **vacío**, así que el núcleo aplica su valor por defecto.
- `CONFIRMED`: `read` y `write` son envoltorios de **8 bytes** sin llamadas: no copian datos por sí mismos.

### 2.1 Las dos tablas frente a frente

| | `/proc` `.data+0x238` | carácter `.data+0x1D0` |
| :--- | :--- | :--- |
| `owner` | `__this_module` | `__this_module` |
| `llseek` | `.text+0x20D4` | **vacío** |
| `read` | `.text+0x2014` → búfer de registro | `.text+0x1E48` (8 B) |
| `write` | **vacío** | `.text+0x1E50` (8 B) |
| `ioctl` | **vacío** | `.text+0x1E58` (356 B) |
| `release` | `.text+0x1DE0` | `.text+0x1E2C` |

- `CONFIRMED`: son complementarias. La de `/proc` **lee** el registro; la de carácter **controla** por `ioctl` y sus `read`/`write` son cascarones.
- `UNKNOWN`: qué copian exactamente esos dos cascarones de 8 bytes. Su cuerpo no contiene llamadas, así que delegan en otro sitio o no hacen nada.

## 3. Qué cambia
- Los nombres `read` y `llseek` dejan de ser una suposición: los prueba el llamado.
- El modo de las entradas `/proc` es **0**, y con eso cae la contradicción de la wave 209.
- Aparece una **segunda** tabla de operaciones, la del nodo de carácter, con su `ioctl`.

## 4. Lo que queda abierto
- `UNKNOWN`: el destino real de los cascarones de 8 bytes en `0x1E48` y `0x1E50`.
- `UNKNOWN`: los tres tipos de mensaje de `set_rate_override`.
- `UNKNOWN`: las 7 materializaciones sin pareja de la wave 204.
- `UNKNOWN`: `vtable[456]`.

## 5. Stage 2307A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2304A` | `tools/re/extract_stage2304a_uph_0x1de0_0x2014_0x20d4_fops_callbacks_re.py` y su recibo `.json` |
| `2305A` | `tools/re/reconcile_stage2305a_uph_0x50dc_cdev_init_fops_and_callbacks_re.py` y su recibo |
| `2307A` | `tools/verify/record_stage2307a_memorymaster_ingest.py` y su recibo |
| `2308A` | `tests/test_stage2304a_to_2309a_suite.py` |
| `2309A` | `tools/verify/verify_stage2309a_wave211_opencode_gate.py` y su recibo |
