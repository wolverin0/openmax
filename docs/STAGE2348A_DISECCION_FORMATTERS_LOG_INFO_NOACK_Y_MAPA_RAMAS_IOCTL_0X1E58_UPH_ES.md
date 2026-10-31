<!-- doc-head -->
# STAGE 2348A — Formateadores `log_info`/`noack_info` y mapa de ramas del `ioctl` de `0x1E58`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre `artifacts/firmware_re_xc_ltu/`. WA y XC coinciden en todo lo reportado.
- Este documento no contiene apellidos.

## 1. Stage 2346A — el formato viaja en `a1`

- **Corrección de método**: en `ubnt_poll_log_buffer_printf(buffer, fmt, ...)` el **primer** argumento es el anillo y el **segundo** es el formato. Las lecturas anteriores sobre `a0` no podían resolverlo. Ésta es la octava corrección de la serie.
- `CONFIRMED`: con `a1`, resuelven **21 de 21** sitios.
- `CONFIRMED`: **14** cadenas llevan conversiones y son formatos reales; **7** no llevan ninguna y se registran como **no-formatos**, sin asignarlas.

Ejemplos medidos:

```
|   |%04d|%04d|%04d|%04d|%04d|%04d|%04d|%08X/%08X|
\nNOACK mode RATE CTRL DATA\nRIX: %d PROBE-RIX: %d NCPC: %d OVERALL-PER: %d
```

- `CONFIRMED`: WA y XC producen la misma lista, en el mismo orden.

### 1.1 La salida temprana del noack

```
0xA7FC  beq a0,zero,->0xAB48     ; argumento nulo
0xA804  lw  v0,12(a0)
0xA80C  beq v0,zero,->0xAB48     ; palabra en +0x0C nula
0xA840  lw  v1,280(a0)           ; bandera en +0x118
0xA844  bne v1,1,->0xA854        ; distinto de 1: usa +0x10F0
0xA850  lw  s2,4332(a0)          ; igual a 1: usa +0x10EC
0xA858  beq s2,zero,->0xAB1C     ; puntero elegido nulo: salida temprana
```

- `CONFIRMED`: `noack_info` devuelve **0 bytes** en tres casos — argumento nulo, `+0x0C` nulo, o puntero elegido nulo.
- `CONFIRMED`: la bandera está en **`+0x118`** (280) y se compara contra **1**. Ese es el discriminador de modo.
- `CONFIRMED`: las salidas son `0xAB48` (nulo) y `0xAB1C` (puntero nulo). Son dos salidas distintas, no una.

## 2. Stage 2347A — mapa de ramas

Recorrido **secuencial**: en cada `beq`/`bne` que compara el registro de comando contra un temporal, se resuelve ese temporal contra el `lui` + `addiu`/`ori` **más cercano anterior** en el mismo registro. El camino de coincidencia es el destino en `beq` y la caída en `bne`.

| Comando | Rama | Manejador |
| :--- | :--- | :--- |
| `0x40905501` | `0x1E98` | `ubnt_poll_ku_comm_get_info` |
| `0xC0015502` | `0x1EA4` | `ubnt_poll_ku_comm_get_stalist` |
| `0xC6945503` | `0x1EC0` | `ubnt_poll_ku_comm_get_stainfo` |
| `0xC2145505` | — | **sin mapear** |

- `CONFIRMED`: **cuatro** comandos se comparan, no cinco. La quinta palabra, `0xC2145504`, se materializa en `a0` y **nunca se compara**: es argumento, no despacho.
- `CONFIRMED`: tres pares quedan probados por destino de rama.
- **`UNKNOWN`**: `0xC2145505` no alcanza ningún `jal` de la familia dentro del rango. Queda sin mapear en vez de adivinarse.
- **Conflicto registrado**: dos ramas resolvieron al mismo valor `0xC0015502`; se conserva la primera y se apunta la rechazada. El resolutor todavía pierde un valor cuando el registro se reutiliza tras una rama.

### 2.1 El nombre del directorio de `/proc`

- `CONFIRMED`: `proc_mkdir` en `0x5414`, con `a0` producido por `addu a0,s1,zero` y `a1 = init_net.proc_net`.
- `CONFIRMED`: hay una llamada de **construcción** de cadena antes del `proc_mkdir`, no un literal en `a0`. El nombre se arma, no se copia.
- **`UNKNOWN`**: el texto exacto. No queda un literal contiguo que lo resuelva y esta etapa no reconstruye el búfer destino.

## 3. Lo que cambia
- El formato deja de ser un `UNKNOWN`: 14 de 21 son formatos ciertos y el resto queda explícitamente marcado.
- El modo noack tiene un discriminador concreto, `+0x118` contra 1.
- El `ioctl` pasa de «cuatro palabras y cinco manejadores sin relación» a **tres pares probados**, un comando sin mapear y un conflicto declarado.

## 4. Lo que queda abierto
- `UNKNOWN`: `0xC2145505` y los otros dos manejadores (`get_sta_spec_data`, `set_sta_spec_data`).
- `UNKNOWN`: el texto del nombre del directorio de `/proc`.
- `UNKNOWN`: las 7 cadenas sin conversión.
- `UNKNOWN`: `set_rate_override` y `vtable[456]`.

## 5. Stage 2349A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`.

## 6. Artefactos
`extract_stage2346a_uph_log_info_and_noack_info_full_formatters_re.py`, `reconcile_stage2347a_uph_0x1e58_branch_map_and_proc_mkdir_name_re.py`, `record_stage2349a_memorymaster_ingest.py`, `test_stage2346a_to_2351a_suite.py` y `verify_stage2351a_wave218_opencode_gate.py`, cada uno con su recibo.
