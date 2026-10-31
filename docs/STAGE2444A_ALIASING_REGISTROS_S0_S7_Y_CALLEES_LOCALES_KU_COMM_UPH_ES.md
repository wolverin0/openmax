<!-- doc-head -->
# STAGE 2444A — Alias de registros `s0..s7` y callees locales en los manejadores `ku_comm`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Medido sobre `artifacts/firmware_re_xc_ltu/`. WA y XC coinciden en todo lo reportado.
- Este documento no contiene apellidos.

## 1. Stage 2442A — el alias, con liveness

Se rastreó el segundo argumento (el tercer argumento del ioctl) buscando `addu rd,a1,zero` y su vuelco a pila, **con seguimiento de redefinición**: cuando el registro de alias se reescribe, deja de contar.

| Manejador | Puntos de alias | Volcado a pila | Escrituras por alias vivo |
| :--- | ---: | ---: | ---: |
| `get_stalist` | 1 | 0 | **2** |
| `get_stainfo` | 2 | 0 | 0 |
| `get_sta_spec_data` | 1 | 0 | 0 |
| `set_sta_spec_data` | 1 | 0 | 0 |

- `CONFIRMED`: **5** puntos de alias en total, **cero** volcados a pila.
- `CONFIRMED`: sólo `get_stalist` escribe a través del alias, con **2** almacenes cuyo registro base sigue siendo el alias en ese punto.
- **Corrección de la wave 232**: allí medí `get_stalist` en **1 byte** contando sólo el registro `a1` como base. Los 2 almacenes por alias **no** se contaron. La cifra de 1 byte es por tanto una **cota inferior** para ese manejador, no su superficie.
- `CONFIRMED`: `get_info` **no** aparece en esta tabla porque no usa alias: su cifra de **144 bytes** se midió directa y **no** está afectada por esta corrección.

### 1.1 La superficie de desreferencia, revisada

| Comando | Declarado | Medido directo | Por alias | Superficie real |
| :--- | ---: | ---: | ---: | :--- |
| `0x40905501` `get_info` | 144 | **144** | 0 | **144** (`CONFIRMED`) |
| `0xC0015502` `get_stalist` | 1 | 1 | **+2 almacenes** | **>1** (`CONFIRMED`) |
| `0xC6945503` `get_stainfo` | 1684 | 0 | 0 | 6 B por primitiva |
| `0xC2145504` spec get | 532 | 0 | 0 | 6 B por primitiva |
| `0xC2145505` spec set | 532 | 0 | 0 | 6 B por primitiva |

- `CONFIRMED`: `get_stalist` **supera su tamaño declarado de 1 byte** en cuanto se cuenta el alias. El comando declara 1 y el manejador escribe al menos 2 almacenes más.
- **`UNKNOWN`**: los desplazamientos exactos de esos 2 almacenes. Se registran en el recibo con su offset, pero no se interpretan aquí.

## 2. Stage 2443A — los callees locales

Los cuatro manejadores hacen **12 llamadas**: **5 entradas locales** sin símbolo y **una** con nombre.

| Entrada | Tamaño | Marco | Copia | La llama |
| :--- | ---: | ---: | :---: | :--- |
| `0x15E50` | 180 | 8 | **sí** | `get_stalist` |
| `0x15F04` | **sin medir** | — | no | `get_stainfo` |
| `0x16B50` | 156 | 40 | **sí** | `get_stainfo` |
| `0x16DF4` | 300 | 64 | **sí** | `get_sta_spec_data` |
| `0x16F20` | 260 | 56 | **sí** | `get_sta_spec_data` |

- `CONFIRMED`: **cuatro de las cinco** entradas locales contienen una referencia de copia.
- `CONFIRMED`: los callees locales **son los envoltorios de copia**. Eso explica por qué los manejadores no contienen `__copy_user` directo y sin embargo copian: la copia está un nivel abajo, en funciones sin símbolo.
- `CONFIRMED`: la búsqueda de estación es la **única** función con nombre, `ubnt_poll_host_sta_hash_find`, y **sólo** la usa `get_stainfo`.
- **`UNKNOWN`**: el tamaño de `0x15F04`. No alcanza un `jr ra` dentro de la ventana de escaneo, así que se reporta **sin medir** en lugar de con un número inventado.

### 2.1 Cómo trabaja la búsqueda

- `CONFIRMED`: los cuatro manejadores localizan la estación por el identificador de **6 bytes** que copian o leen, y sólo `get_stainfo` usa la rutina con nombre; los otros tres pasan por etiquetas locales.
- **`UNKNOWN`**: el reparto de campos dentro de `sta_hash_find`. Se mide su tamaño en la wave 222 y su llamada aquí, no su cuerpo campo a campo.

## 3. Qué cambia
- El alias deja de ser una suposición: **5 puntos, cero volcados**, y sólo uno escribe.
- La cifra de `get_stalist` de la wave 232 queda **corregida al alza**: 1 byte era una cota inferior.
- Los callees locales dejan de ser opacos: **tamaños y marcos medidos**, cuatro de cinco con copia.

## 4. Lo que queda abierto
- `UNKNOWN`: los offsets de los 2 almacenes por alias.
- `UNKNOWN`: el tamaño de `0x15F04`.
- `UNKNOWN`: el reparto de campos de `sta_hash_find`.
- `UNKNOWN`: `set_rate_override`, `vtable[456]`, nombre del directorio de `/proc`.

## 5. Stage 2445A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax` y se añadieron las filas con **CRLF**.

## 6. Artefactos
`build_stage2442a_uph_ku_comm_saved_reg_aliasing_and_1684_532_delivery_re.py`, `build_stage2443a_uph_ku_comm_local_callees_and_sta_lookup_dissection_re.py`, `record_stage2445a_memorymaster_ingest.py`, `test_stage2442a_to_2447a_suite.py` y `verify_stage2447a_wave234_opencode_gate.py`, cada uno con su recibo.
