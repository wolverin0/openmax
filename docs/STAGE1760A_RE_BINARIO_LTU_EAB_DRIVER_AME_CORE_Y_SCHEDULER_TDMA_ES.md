<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head -->
*STAGE1760A — RE binario de los módulos LTU: eab_driver ausente, ame_core con 9.799 símbolos, y el desajuste de nombres TDMA/burst/ATPC*
# STAGE 1760A — LTU `eab_driver`/`ame_core` y el scheduler

## 0. Frontera
- **100% offline**: `ssh_connections=0`, `radio_writes=0`. No se carga ningún módulo.
- Orca entregó el dispatch de esta wave (`<orca-id>`) con `orca orchestration check`.

## 1. Stage 1758A — inventario y censo
- `CONFIRMED`: **4 de 5** módulos presentes. Presentes: `ame_core.ko`, `ame_dev.ko`, `ame_radio_mod.ko`, `ame_dfs.ko`.
- `REFUTED` (arrastrado de `1518A`): **`eab_driver.ko` no existe** como fichero en la rootfs LTU. Su superficie TDMA **no se puede medir** y no se simula.
- `CONFIRMED`: `ame_core.ko` expone **9.799 símbolos** con nombre, lo que permite leer el censo por nombre real, no por heurística de cadenas.
- `CONFIRMED`: censo en `ame_core.ko`: **frame_len = 11**, **qam = 1**, **1024 = 10**, **4096 = 12**.
- `REFUTED`: los tokens **`tdma` = 0**, **`burst` = 0** y **`atpc` = 0** dentro de `ame_core.ko`. Es decir, el binario **no usa esos nombres**: el scheduler aparece con otros identificadores (`sched`, `frame`, `duty`).
- `INFERRED`: buscar "tdma" o "atpc" en este módulo es buscar el nombre equivocado; el vocabulario del binario es `sched`/`frame_len`/`duty`.
- `UNKNOWN`: la temporización de burst y el lazo ATPC. El binario prueba que el código existe, no cuánto dura un burst ni cómo converge el lazo.

## 2. Stage 1759A — reconciliación
- `CONFIRMED`: el catálogo tiene **571** knobs.
- `CONFIRMED`: coincidencias por token en el catálogo: **tdma 9**, **burst 5**, **atpc 2**, **qam 2**, **1024 17**, **4096 20**.
- `CONFIRMED`: **24** ficheros de telemetría LTU `.110` presentes en disco.
- `INFERRED`: el catálogo habla de `tdma`/`burst`/`atpc` (9/5/2) mientras el binario no contiene esas cadenas; el puente entre catálogo y binario exige traducir vocabulario, no solo casar nombres.
- `UNKNOWN`: el puente binario→banco. Los 24 ficheros de telemetría no se han abierto en esta etapa y no se afirma su contenido.

## 3. Lo que no se prueba
- `UNKNOWN`: valores reales de frame length, duty cycle y umbrales de modulación en ejecución.
- `UNKNOWN`: si 4096-QAM está habilitado en un enlace concreto.
- `UNKNOWN`: cualquier superficie de `eab_driver.ko`, inexistente como módulo.

## 4. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1758A` | `tools/re/extract_stage1758a_ltu_eab_and_ame_tdma_scheduler_re.py` + recibo |
| `1759A` | `stage1759a_ltu_tdma_and_modulation_knob_reconciliation_receipt.json` |
| `1760A` | este documento (menos de 160 líneas, 1 `doc-head`, 0 signos de exclamación en prosa) |
| `1762A..1763A` | `tests/test_stage1758a_to_1763a_suite.py` y la compuerta de la wave |
