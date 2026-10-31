<!-- doc-head -->
*STAGE1712A — RE binario de ptp_xmit/atpc/noack en XC y add_pm_dbg en LTU, con reconciliación contra 571 knobs*
# STAGE 1712A — XC `ptp_xmit`/`atpc`/`noack` y LTU `add_pm_dbg`

## 0. Alcance
- **100% offline**: `ssh_connections=0`, `radio_writes=0` en ambos recibos.
- Se leen módulos ya presentes en el repo. Nada se carga ni se ejecuta.

## 1. Stage 1710A — evidencia por módulo
- `CONFIRMED`: **4** módulos presentes y **1** ausente. Presentes: `ubnt_poll_host.ko`, `ath_dev.ko`, `umac.ko`, `ame_core.ko`. Ausente: `eab_driver.ko`.
- `CONFIRMED`: `ubnt_poll_host.ko` es donde vive la superficie pedida: **ptp_xmit = 1** acierto, **atpc = 7**, **noack = 6** (símbolos, exports, imports y cadenas sumados).
- `CONFIRMED`: `ame_core.ko` aporta **add_pm_dbg = 1** y **pm_dbg = 1**.
- `CONFIRMED`: los parámetros de módulo se leen de `.modinfo`; ninguno de los nombres medidos aparece como parámetro, así que no hay un knob de línea de carga que gobierne estos tokens.
- `REFUTED` (arrastrado de `1518A`): `eab_driver.ko` no existe como fichero en ninguna de las dos rootfs LTU. Su superficie `add_pm_dbg` **no se puede medir** y no se simula.
- `INFERRED`: `atpc` y `noack` son decisiones de runtime dentro de `ubnt_poll_host.ko`; el binario demuestra que los nombres existen, no cuándo se toman.

## 2. Stage 1711A — reconciliación
- `CONFIRMED`: el catálogo tiene **571** knobs.
- `CONFIRMED`: coincidencias por token: **ptp_xmit = 2**, **atpc = 2**, **noack = 6**, **add_pm_dbg = 0**, **pm_dbg = 0**.
- `CONFIRMED`: **0** recibos de `stage1675A` presentes en el repositorio, así que el lado de controles vivos **no se puede cruzar**.
- `INFERRED`: hay knobs que nombran `noack` (6) y `ptp_xmit`/`atpc` (2+2), pero un nombre en el catálogo no prueba que el knob controle esa rama del binario.
- `UNKNOWN`: el puente binario→vivo. Sin `1675A`, no hay control medido contra el que contrastar.

## 3. Lo que no se prueba
- `UNKNOWN`: cuándo `ptp_xmit` elige una ruta u otra, y bajo qué condición se activa `noack`.
- `UNKNOWN`: superficie `add_pm_dbg` de `eab_driver.ko`, inexistente como módulo.
- `UNKNOWN`: correlación con los controles vivos de `1675A`, ausentes.

## 4. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1710A` | `tools/re/extract_stage1710a_xc_ptp_xmit_and_ltu_pm_dbg_binary_re.py` + `stage1710a_xc_ptp_xmit_and_ltu_pm_dbg_binary_re_receipt.json` |
| `1711A` | `stage1711a_xc_ltu_knob_binary_to_live_reconciliation_receipt.json` |
| `1712A` | este documento (menos de 160 líneas, 1 `doc-head`, 0 signos de exclamación en prosa) |
| `1713A..1715A` | filas en `results.tsv`, `tests/test_stage1710a_to_1715a_suite.py` y la compuerta de la wave |
