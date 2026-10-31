<!-- doc-head -->
# STAGE 2150A — Resolución de `.rel.text` en `ubnt_poll_host` y en `umac`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2148A — las cinco ramas tienen nombre

Las waves 181 y 183 dejaron cinco `jal 0x0` sin destino porque su operando es cero en el objeto. La tabla `.rel.text` sí lo sabe:

| Comando | `nr` | Rama | Símbolo resuelto |
| :--- | ---: | :--- | :--- |
| `0x40905501` | 1 | `0x1ED0` | `ubnt_poll_ku_comm_get_info` |
| `0xC0015502` | 2 | `0x1EF4` | `ubnt_poll_ku_comm_get_stalist` |
| `0xC6945503` | 3 | `0x1F28` | `ubnt_poll_ku_comm_get_stainfo` |
| `0xC2145504` | 4 | `0x1F58` | `ubnt_poll_ku_comm_get_sta_spec_data` |
| `0xC2145505` | 5 | `0x1F88` | `ubnt_poll_ku_comm_set_sta_spec_data` |

- `CONFIRMED`: las cinco llamadas son `R_MIPS_26` con símbolo definido, y los nombres son **idénticos** en las dos familias.
- `CONFIRMED`: cuatro son `get_*` y una es `set_*`. Eso **cierra** la dirección de transferencia que la Stage 2136A sólo podía inferir: U1 a U4 entregan datos del kernel al usuario, U5 recibe datos del usuario.
- `REFUTED`: que el destino de esas llamadas fuera indeterminado. Estaba en la tabla de relocaciones.
- `CONFIRMED`: el nombre de cada rama concuerda con su tamaño declarado: las cuatro `get_*` y la `set_*` de datos por estación son las de 532 y 1684 bytes.

### La inscripción del dispositivo

- `CONFIRMED`: la llamada de `0x1D98` resuelve a **`register_chrdev_region`**, con lo que se confirma por símbolo lo que la Stage 183 había localizado por relocación.
- `CONFIRMED`: el slot de `0x230A0` en `.data` es un `R_MIPS_32` contra la sección `.text`, con añadido `0x1E58`, es decir el puntero al handler.
- `CONFIRMED`: en el mismo bloque hay seis slots (`0x23080`, `0x23088`, `0x2308C`, `0x230A0`, `0x230B0`, `0x230B8`), los cuatro últimos con añadidos locales que la tabla no nombra.
- `UNKNOWN`: el índice exacto de `0x1E58` dentro de la estructura `file_operations`. Se conoce la posición del slot, no su ordinal.

## 2. Stage 2149A — el proveedor es el asignador

La Stage 2137A dejó `0xBBE30` como `UNKNOWN`. La tabla lo resuelve:

| Familia | Instrucción | Símbolo |
| :--- | :--- | :--- |
| WA_umac | `0xBBE30` | **`alloc_netdev_mq`** |
| XC_umac | `0xBBE34` | **`alloc_netdev_mq`** |

- `CONFIRMED`: el `jal` que produce `s0` es la **asignación del dispositivo**, no una consulta.
- `CONFIRMED`: por tanto `s0` es el puntero devuelto por el asignador, y `s0 + 0x1E1B8` cae **dentro del bloque recién asignado**, no en un objeto preexistente.
- `REFUTED`: la lectura de las waves 179 y 181 de que `dev+0x1E1B4` fuera un puntero a un sub-objeto separado. Es un desplazamiento dentro del mismo bloque que el asignador entrega.
- `CONFIRMED`: la llamada previa resuelve a `ether_setup` y el cuarto argumento vale `1`, que es la forma habitual de `alloc_netdev_mq(tamaño, nombre, setup, colas)`.
- `UNKNOWN`: el tamaño del bloque. Se pasa como primer argumento y no aparece como constante en la ventana.

### La ventana de la función

- `CONFIRMED`: entre `0xBBE00` y `0xBC300` hay **124** entradas de relocación, con **49** símbolos distintos.
- `CONFIRMED`: entre ellos están `ether_setup`, `alloc_netdev_mq` y `printk`, además de las cadenas locales `$LC0` a `$LC13`.

### La tabla de `+456`

- `CONFIRMED`: se revisaron todas las relocaciones de `.data` y `.rodata` cuyos símbolos caen en `.text`, y se probó cada una como índice 114 de un bloque con al menos tres punteros a función.
- `CONFIRMED`: el número de tablas estáticas que cumplen esa condición es **cero**, en las cuatro parejas de módulos.
- `REFUTED`: que exista una tabla de operaciones estática con una función real en el índice 114.
- `UNKNOWN`: el destino de `vtable[456]`. La tabla se llena en ejecución y no tiene representación estática en estos objetos.

## 3. Qué cambia respecto de las waves anteriores
- La dirección de las cinco transferencias deja de ser `INFERRED` y pasa a `CONFIRMED` por nombre de función.
- El proveedor de `s0` deja de ser `UNKNOWN` y pasa a ser `alloc_netdev_mq`.
- El campo `+0x1E1B8` deja de describirse como "campo del `net_device`" y pasa a ser un desplazamiento dentro del bloque asignado.
- El destino de `vtable[456]` sigue `UNKNOWN`, pero ahora con una búsqueda por símbolo y no sólo por punteros crudos.

## 4. Lo que queda abierto
- `UNKNOWN`: el tamaño del bloque que pide el asignador.
- `UNKNOWN`: el índice de `0x1E58` en la estructura de operaciones.
- `UNKNOWN`: el nombre de los cuatro slots locales del bloque de `.data`.
- `UNKNOWN`: el destino de `vtable[456]`, que se llena en ejecución.

## 5. Stage 2151A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2148A` | `tools/re/extract_stage2148a_uph_0x1e58_and_0x1d98_rel_text_symbol_resolver_re.py` y su recibo |
| `2149A` | `tools/re/reconcile_stage2149a_umac_0xbbe30_rel_text_and_vtable456_symbol_re.py` y su recibo |
| `2151A` | `tools/verify/record_stage2151a_memorymaster_ingest.py` y su recibo |
| `2152A` | `tests/test_stage2148a_to_2153a_suite.py` |
| `2153A` | `tools/verify/verify_stage2153a_wave185_opencode_gate.py` y su recibo |
