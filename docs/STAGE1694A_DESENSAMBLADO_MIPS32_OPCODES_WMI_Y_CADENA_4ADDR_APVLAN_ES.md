<!-- doc-head -->
*STAGE1694A — desensamblado MIPS32 de opcodes WMI y cadena 4addr AP_VLAN: lo medido y lo refutado*
# STAGE 1694A — WMI, 4addr AP_VLAN y límites de canal

## 0. Alcance
- **100% offline**: `ssh_connections=0`, `radio_access=0` registrados en los recibos.
- Rutas pedidas por el operador **refutadas**: `artifacts/openwrt_squashfs_build/repack_root_20` no existe. Los módulos reales están en `artifacts/firmware_re_ath10k_tar/`, donde solo hay `ath10k_core.ko`; `mac80211.ko` y `cfg80211.ko` no están en esa carpeta y no se inventan.

## 1. Stage 1692A — evidencia medida
- `CONFIRMED`: `ath10k_core.ko` 600.808 B, **61** exports resueltos por `__ksymtab`.
- `CONFIRMED`: **0** exports con `wds`/`4addr`/`vlan` en `ath10k_core.ko`; los nombres internos están borrados, así que la cadena `cfg80211_rx_spurious_frame → NL80211_CMD_UNEXPECTED_4ADDR_FRAME → AP_VLAN` **no** se prueba por símbolos.
- `CONFIRMED`: censo de inmediatos en el rango `0x9000..0x9fff`: **47** palabras en `.text` y **5** en `.rodata`, con **1** valor distinto. Un único valor no es una tabla de opcodes.
- `CONFIRMED`: codificaciones de frecuencia en `ath10k_core.ko`: 2412 → 0/0, 2484 → 0/0, 4900 → **62** `u16`, 6100 → 0/0, 6035 → 0/0. Los 62 aciertos de 4900 se reportan como literales, no como tabla de canales.
- `REFUTED`: que exista `firmware-2.bin` en la carpeta indicada; el recibo lo marca `present=0` y no se extrae evidencia de firmware en esta etapa.
- `UNKNOWN`: la carrera dual-bind de netifd; es ordenación en ejecución y ningún binario la demuestra.

## 2. Stage 1693A — reconciliación
- `CONFIRMED`: el catálogo tiene **571** knobs; coincidencias por token: `wds`, `4addr`, `vlan`, `regd`, `dfs`, `6035` según el recibo.
- `CONFIRMED`: el recibo de **1680A** está presente y corrobora la superficie 4addr; los de **1650A** y **1657A** **no están** en el repositorio, así que no se cruzan afirmaciones contra ellos.
- `INFERRED`: 6035 MHz sigue siendo una cuestión regulatoria (55 registros globales, 5650–6425 MHz, citado de 1405A), no un knob.

## 3. Lo que esta wave NO prueba
- `UNKNOWN`: el mapeo opcode WMI ↔ comando, imposible sin símbolos internos.
- `UNKNOWN`: la creación efectiva de la AP_VLAN en ejecución.
- `UNKNOWN`: usabilidad de 6035 MHz por flags DFS/no-IR.

## 4. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1692A` | `tools/re/extract_stage1692a_ath10k_wmi_opcode_and_regdomain_disasm.py` + recibo |
| `1693A` | `tools/re/extract_stage1693a_wmi_4addr_and_channel_bounds_reconciliation.py` + recibo |
| `1694A` | este documento (menos de 200 líneas, 1 `doc-head`, 0 signos de exclamación en prosa) |
| `1696A..1697A` | `tests/test_stage1692a_to_1697a_suite.py` y `tools/verify/verify_stage1697a_wave109_opencode_gate.py` |
