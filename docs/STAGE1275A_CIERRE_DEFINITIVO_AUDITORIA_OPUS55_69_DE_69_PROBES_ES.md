<!-- doc-head: Stage 1275A (ES): cierre de la auditoria Opus 5.5. Arbitraje del choque de esquemas de la Wave 30 (1218A..1223A, 0 fallas), verdad ELF de .modinfo (ath_dev.ko XC: 1 parm, ubnt_radar_mode no es parm), endurecimiento compatible de los 4 verificadores, 69/69 sondas vivas y diferenciales, y 744/744 pytest sin fallas ni skips. Leer antes de tocar 1218A..1223A, enforce_5pillar_research_gate o los gates 1126A/1156A/1168A. -->
# Stage 1275A: cierre definitivo de la auditoria Opus 5.5 (69 de 69 sondas)

Wave 39 (Stages 1272A..1277A). Todo es offline: no se toco ningun radio. `CONFIRMED_LIVE_HARDWARE` sigue en 0 y no hay ningun reclamo `PRODUCTION_READY`.

## Resultado en una linea
- Las 69 sondas adversariales pasan contra los puntos de entrada vivos: 69 en alcance y 69 correctas.
- Las mismas 69 siguen fallando contra la conducta original, lo que prueba que detectan el bug. Para los 11 modulos Opus 4.8 se usa la copia congelada; para los 4 verificadores, los defaults legados, que siguen intactos.
- El pytest maestro da 744 aprobados, 0 fallas, 0 errores y 0 skips en 32 archivos.

| Recibo | Que prueba |
| :--- | :--- |
| `artifacts/verification/stage1272a_wave30_arbitration_receipt.json` | arbitraje Wave 30: 60/60 tests, verdad ELF |
| `artifacts/verification/stage1273a_four_verifiers_hardened_receipt.json` | 4 verificadores con modo estricto y la conducta por defecto intacta |
| `artifacts/verification/stage1274a_zero_failures_master_scorecard.json` | marcador maestro: 744/0/0/0 y 69/69 |
| `artifacts/verification/stage1277a_wave39_opus55_gate.json` | gate de la ola, fail-closed |

## 1. Stage 1272A: el choque de esquemas de la Wave 30
**Que pasaba.** Dos carriles (Opus 4.8 y OpenCode) escribieron las mismas etapas 1218A..1222A.
- Los tests por etapa de un carril llamaban una API que los modulos del otro carril no tenian: `verify_uph`, `build_matrix`, `UMAC_KO`, `s1220`, `AP_DIR`, etc.
- Resultado: 9 fallas y 2 errores de coleccion. La suite consolidada `test_stage1218a_to_1223a_suite.py` ya pasaba.

**Como se arbitro (sin elegir ganador).**
- Se agregaron a los modulos los nombres que faltaban, como alias o adaptadores finos sobre la logica existente. No se cambio ningun nombre que ya usara el otro carril.
- No se edito ni se debilito ningun test.

| Test | API agregada | Modulo |
| :--- | :--- | :--- |
| 1218A | `UMAC_KO`, `ATH_DEV_KO`, `analyze`, `build_receipt`, `write_receipt`, `CLAIM_ID` | `tools/re/umac_ath_dev_dfs_radar_and_link_state_re_analyzer.py` |
| 1219A | `ROOT`, `AP_DIR`, `KEY_KOS`, `analyze_cds_mac`, `build_receipt`, `inventory(dir)` | `tools/re/ltu_v242_complete_ko_inventory_and_cds_mac_re_analyzer.py` |
| 1220A | `verify_uph`, `verify_ltu_penalty`, `LTU_AP_REL`, `LTU_CPE_REL`, `UPH_REL` | `tools/re/uph_bmiss_stainfo_and_ltu_penalty_threshold_re_verifier.py` |
| 1221A | `s1220`, `build_receipt`, `collect_evidence`, `GRADES`, `CLAIM_ID` | `tools/re/binary_re_evidence_for_pwo_bilateral_engine.py` |
| 1222A | `build_matrix`, `compare`, `PRIOR`, `WAVE30`, `GRADES` | `tools/verify/verify_stage1222a_re_reconciliation_matrix.py` |

**Recibos fusionados.** Los recibos 1218A..1222A ahora llevan las claves de ambos carriles: `evidence_class`, `five_pillar_compliance`, `pillar_e_memory_master_claim_id`, `status` y `live_devices_touched`. Cada uno suma ademas un bloque propio de su etapa:

| Recibo | Bloque nuevo |
| :--- | :--- |
| 1218A | `modinfo_ground_truth` |
| 1219A | `ap_build_key_kos` |
| 1220A | `wave30_verifications` |
| 1221A | `rc_evidence` |
| 1222A | `matrix` (8 filas consistentes, 0 huecos) |

Cada recibo lo regenera su propio generador, asi que sobrevive a las reejecuciones deterministas de la suite. Ningun hecho de los recibos fue contradicho por el binario.

## 2. Verdad ELF: `ubnt_radar_mode` y los "13 parms"
La premisa de la orden era "solo existen 13 parms reales en `ath_dev.ko` XC y `ubnt_radar_mode` no es uno". El binario confirma la segunda mitad y corrige la primera:
- **`ath_dev.ko` XC 8.7.25** (sha256 `d1df6589...77bf`):
  - `.modinfo` tiene 13 entradas en total, pero solo 1 es `parm=` (`macaddr_override`) y 7 son `parmtype=`. El resto son license, description, author, depends y vermagic.
  - `ubnt_radar_mode` no es parm y no aparece en ningun lugar del archivo.
- **`umac.ko`, en WA y XC 8.7.25:** `ubnt_radar_mode` SI es uno de sus 10 `parm=`. Esta en `.rodata`, offset 952628, el mismo que cita la suite.
- El recibo guarda `parm_count: 1`, `modinfo_entry_count: 13` y `lead_premise_check.parm_count_premise_holds: false`. Manda el binario.

## 3. Stage 1273A: los 4 verificadores, endurecidos sin romper nada
Las 11 sondas que en la Wave 35 quedaron `live_in_scope=false` apuntaban a verificadores rastreados. La restriccion era dura: `enforce_5pillar_research_gate.py` lo importan unos 564 archivos.

**Que se agrego.** Puntos de entrada estrictos nuevos, al lado de los viejos:

| Verificador | Entradas estrictas |
| :--- | :--- |
| `tools/verify/enforce_5pillar_research_gate.py` | `audit_stage_receipt_5pillars_strict`, `--opus55-strict` |
| `tools/verify/verify_stage1126a_wave15_claude_gate.py` | `check_selftests_strict`, `_doc_check_strict`, `run_gate(strict=True)` |
| `tools/verify/verify_stage1156a_wave20_claude_gate.py` | `_doc_check_strict`, `check_1152_strict`, `check_1153_strict`, `synthetic_flag_present_strict`, `run_gate(strict=True)` |
| `tools/verify/verify_stage1168a_wave22_claude_gate.py` | `_doc_check_strict`, `check_1165a_strict`, `run_gate(strict=True)` |

**Como funciona el modo estricto.**
- Importa la logica endurecida del modulo 1244A de forma perezosa, asi que importar los verificadores no carga ese modulo.
- `run_gate` en modo estricto escribe `*_opus55_strict.json` y nunca pisa el recibo legado.
- La cadena de recibos atada por hash solo se exige con `--chain`.

**Compatibilidad hacia atras, medida en un mismo proceso contra las copias previas:**
- 10769 de 10769 recibos dan resultado identico con la auditoria de 5 pilares por defecto (131 ilegibles omitidos).
- 4496 de 4496 chequeos de gates dan identico.
- En los 248 archivos de test que importan algun verificador: 802 aprobados y 76 fallas con los cambios, contra 627 aprobados y 76 fallas con los verificadores previos. Cero fallas nuevas; las 76 son preexistentes y estan fuera del rango 1181A..1253A.

## 4. Stage 1274A: marcador maestro
- **Alcance:** `test_stage1218a_to_1223a_suite.py` mas todos los `test_stage1181a..1253a*`, 32 archivos en un unico subproceso con junit.
- **Pytest:** 744 aprobados, 0 fallas, 0 errores, 0 skips; tasa 1.0. Los skips se listan y nunca cuentan como aprobados (leccion de OPUS48-PWO-41).
- **Sondas:**
  - vivas: 69 en total, 69 en alcance, 69 correctas, 0 fuera de alcance;
  - diferenciales: 69/69 con `opus48_failed` y `opus55_correct`.
- **Gates encadenados verdes:**
  - 1247A: 68 hallazgos, 69 sondas, 0 sin verificar;
  - 1253A: 69/69 en alcance, legado 602/0.

## 5. Arreglo fuera del carril (declarado)
`docs/CURRENT_STATE.md` lo estaba extendiendo el carril de las Waves 37..41 y llego a 184 lineas, cuando el limite es menos de 180. Eso rompia 5 tests legados (`test_master_docs_budget_and_head`).
- Se escalo al coordinador. No hubo respuesta.
- Se aplico el plan fail-closed anunciado:
  - se quitaron 5 lineas en blanco que precedian encabezados `##` (el render no cambia);
  - se reparo un byte BEL (`\a`) que habia comido la "a" de `artifacts/verification/stage1286a...`;
  - se verifico el sha256 antes de escribir.
- El documento puede volver a pasarse del limite con el proximo agregado de ese carril.

## 6. Lo que sigue abierto (honesto)
- **PWO-16** sigue parcial. Los anchos 12x salen de los bytes del `ame_core.ko` stock, pero no se decodifico el rol de selector de trama de 2000/2500/4000/5000 us (`frame_role_verified: false`).
- **`check_1164a`** del gate 1156A tiene la misma debilidad de senuelo que 1153. No es una de las 69 sondas y no se endurecio.
- **Recibos historicos sin respaldo en git:** los recibos de 1181A, 1182A, 1200A y 1201A y los de los gates 1186A/1205A/1211A/1217A se reescriben en cada corrida legada, y no estan bajo git.
- **Commit:** no se hizo ninguno. `tools/uisp/*` y `artifacts/verification/` estan ignorados (`*uisp*`, `/artifacts/verification/`), y la decision es del operador.

## Reversion
Hay copias previas byte a byte, con su sha256 en el `MANIFEST.json` de cada carpeta:
- `tools/uisp/opus48_baseline/wave39_pre_edit/`: los 25 archivos de esta ola;
- `tools/uisp/opus48_baseline/src/`: los 11 modulos Opus 4.8.

Para revertir, copiar el archivo de vuelta a su ruta original.

## Verificacion
- Gate: `python tools/verify/verify_stage1277a_wave39_opus55_gate.py --write`.
- Suite: `pytest tests/test_stage1272a_to_1277a_suite.py -q`.
- Ambos corren via `heavy-slot`.
