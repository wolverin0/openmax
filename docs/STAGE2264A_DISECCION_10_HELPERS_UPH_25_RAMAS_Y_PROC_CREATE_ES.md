<!-- doc-head -->
# STAGE 2264A — Los 10 ayudantes de `0x2138`, las ramas de cadena y `proc_create_data`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.
- Nota: el cuerpo del despacho de la Wave 204 llegó truncado a 515 bytes y se recuperó completo después, con 2358 bytes. Las etapas siguen el texto íntegro.

## 1. Stage 2262A — los diez ayudantes, con tamaño y forma

Los diez ayudantes que `0x2138` alcanza, en orden de dirección:

| Ayudante | Entrada | Tamaño | Llamadas | Almacenes |
| :--- | :--- | ---: | ---: | ---: |
| `get_diag` | `0x7CC8` | 96 | 1 | 5 |
| `set_host_diag` | `0x7D28` | 36 | **0** | 1 |
| `set_reg` | `0x7F0C` | 100 | 1 | 6 |
| `get_reg` | `0x7F70` | 84 | 1 | 5 |
| `set_diag` | `0xA314` | 144 | 3 | 6 |
| `get_txq_param` | `0xB26C` | 40 | 1 | 3 |
| `set_txq_param` | `0xB294` | 64 | 1 | 7 |
| `set_rate_override` | `0xB2D4` | 304 | 2 | 9 |
| `set_swr_limit` | `0xB404` | 104 | 3 | 5 |
| `set_evm_meas_config` | `0xB46C` | 144 | 1 | 8 |

- `CONFIRMED`: son **exactamente diez**, y coinciden con la lista del encargo (`missing=[]`, `extra=[]`).
- `CONFIRMED`: suman **1116** bytes por familia, idénticos en WA y XC.
- `CONFIRMED`: cada uno tiene su propia tabla de relocaciones por tipo (`R_MIPS_26`, `HI16`, `LO16`) y sus cadenas.
- `CONFIRMED`: `set_rate_override` es el mayor (304 B) y `set_host_diag` el menor (36 B).
- `CONFIRMED`: `set_host_diag` **no llama a nada**; los otros nueve sí.
- `CONFIRMED`: `0x2138` también alcanza `printk`, que no es un ayudante interno y queda fuera de los diez.

## 2. Stage 2263A — las ramas de cadena

| Medición | WA | XC |
| :--- | ---: | ---: |
| Materializaciones de `$LC` en `0x2138..0x2938` | **56** | **56** |
| Constantes únicas | 25 | 25 |
| Emparejadas con una acción | **21** | **21** |

- `CONFIRMED`: hay **56** materializaciones para **25** constantes, porque cada uso emite un par `HI16`/`LO16` sobre el mismo `$LC`.
- `CONFIRMED`: **21** de ellas quedan emparejadas con una llamada o una rama concreta.
- `UNKNOWN`: las 7 restantes. El comparador no aparece dentro de la ventana de búsqueda, así que la pareja no se cierra.
- `INFERRED`: el despacho es una cadena de comparaciones de nombre, no una tabla.

### Las dos entradas `proc`

- `CONFIRMED`: hay **dos** llamadas a `proc_create_data` por familia, en **`0x5458`** y **`0x54A0`**.
- `CONFIRMED`: los nombres de fichero resueltos contra `.rodata.str1.4` son **`info`** (`$LC133`) y **`noack_info`** (`$LC134`).
- `CONFIRMED`: ambas se crean con modo **`0o10`** (8), es decir **sólo escritura para el dueño**: son disparadores, no lectores.
- `CONFIRMED`: el cuarto argumento de ambas es `s4 + 568` (`0x238`), el puntero de instancia de la radio.
- `UNKNOWN`: la estructura `file_operations`. Ningún símbolo de `.data`, `.rodata` o `.bss` aparece en la ventana, así que el puntero llega por un registro.

## 3. Qué cambia
- Los diez ayudantes dejan de ser nombres sueltos: tienen dirección, tamaño, llamadas y almacenes.
- Las ramas de cadena quedan contadas y **parcialmente** emparejadas, con el número exacto de las que faltan.
- Las dos entradas `proc` quedan localizadas por dirección y por constante, aunque su modo y su `fops` no se resolvieron.

## 4. Lo que queda abierto
- `UNKNOWN`: las 7 materializaciones sin pareja.
- `UNKNOWN`: la estructura `file_operations` de `0x5458` y `0x54A0`.
- `UNKNOWN`: el significado de los campos en `info` y `noack_info`.
- `UNKNOWN`: `vtable[456]`.

## 5. Stage 2265A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2262A` | `tools/re/extract_stage2262a_uph_10_internal_helpers_re.py` y su recibo |
| `2263A` | `tools/re/reconcile_stage2263a_uph_25_string_branches_and_proc_create_re.py` y su recibo |
| `2265A` | `tools/verify/record_stage2265a_memorymaster_ingest.py` y su recibo |
| `2266A` | `tests/test_stage2262a_to_2267a_suite.py` |
| `2267A` | `tools/verify/verify_stage2267a_wave204_opencode_gate.py` y su recibo |
