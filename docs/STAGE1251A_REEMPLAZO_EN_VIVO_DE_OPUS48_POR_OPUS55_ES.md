<!-- doc-head: Stage 1251A reemplazo en el lugar (in-place) de la logica Opus 4.8 por la endurecida de Opus 5.5 en los modulos PWO 1183A, 1212A, 1213A, 1214A, 1215A y 1238A, sondas vivas run_live_probes, cuatro sondas nuevas (PWO-16, 29, 40, 41) con sus limites, y rollback desde opus48_baseline; offline, CONFIRMED_LIVE_HARDWARE 0. Receipt: stage1250a_inplace_pwo_and_4probes_upgrade.json. -->
# Stage 1251A - Opus 4.8 reemplazado en el lugar por Opus 5.5 (PWO)

Documento del Stage 1250A (receipt `artifacts/verification/stage1250a_inplace_pwo_and_4probes_upgrade.json`). Offline,
`live_devices_touched=false`, `simulated=true`. **CONFIRMED_LIVE_HARDWARE = 0**: nada de esto toca un equipo.

## 1. Que cambio y por que
- En Wave 34 (1244A) el codigo endurecido vivia al costado y los modulos 4.8 seguian rotos. Ahora llamar a la funcion
  ORIGINAL (`bridge_recommendation`, `evaluate_rules`, `frame_valid`...) ejecuta la logica endurecida.
- Los nombres publicos, las firmas y las claves de salida legadas se conservan; solo se agregan claves.
- Cada cambio lleva un comentario `# Wave 35 (OPUS48-PWO-NN): ...`.
- La logica endurecida sigue en `tools/uisp/opus55_hardened_pwo_bridge_and_rules_verifier.py` (1244A); los modulos vivos la
  importan. Para evitar ciclos, 1244A no importa los modulos vivos al cargar: el lado "4.8" usa el baseline congelado
  (`tools/uisp/opus48_baseline`, `load_opus48`) y los helpers vivos se importan de forma perezosa.
- Verificado con `python -c "import <modulo>"` en un interprete nuevo para los 7 modulos (6 vivos + 1244A): los 7 OK.

## 2. Cambios por modulo y compatibilidad
| Modulo | Cambio | Nota de compatibilidad |
| :--- | :--- | :--- |
| 1183A bridge | `bridge_recommendation` delega en `bridge_recommendation_hardened` (hallazgos PWO-01..11) | `channel` ahora es MHz entero (antes el eco del valor); se agregan `channel_mhz`, `channel_number`, `channel_unit`, `schema_errors`, `contract_source`; ancho desconocido da NO-CHANGE (trampa 8); `PREFLIGHT_GATES` sale del spec (texto: `maintenance window (02:00-06:00 ART)`); se expone `validate_pwo_payload`; el `_fixture` del modulo declara `width_mhz` |
| 1212A LTU | `qam_12x_allowed` y `frame_valid` delegan en las versiones endurecidas (PWO-12/13/14); `TX_BACKOFF_DBM` tipado `{min_dbm,max_dbm}` (PWO-15); nueva `verify_constants_against_binary` (PWO-16) | `reconcile_ltu_capabilities()["qam"]["tx_backoff_dbm"]` conserva la forma legada (16 / `"10-12"`) y se suma `tx_backoff_dbm_typed`; `frame_valid` ya no lanza |
| 1213A reglas | `evaluate_rules` delega en `evaluate_rules_hardened` (PWO-17..25); `_num` ignora NaN/inf | misma forma de tarjeta; `evidence.data_quality` lista campos descartados; se eliminaron los `_rule_*` privados (sin otros usuarios) |
| 1214A constantes | veredicto derivado de la evidencia (PWO-26), ELF seguro (PWO-27), citas ancladas por texto (PWO-28), `PARTIAL` si falta un build (PWO-29) | claves nuevas `conclusion_code`, `binary_status`, `builds_readable`, `builds_total`; cita desplazada va a `provenance` con `cite_drifted`; con los datos reales la salida es identica salvo claves nuevas |
| 1215A advisor | la tarjeta de canal sale del bridge endurecido y se valida con `validate_pwo_payload` | claves nuevas `channel.pwo_validation`, `pwo_payload`, `pwo_payload_valid`; si el bridge rechaza el canal sale una tarjeta `fmx-1215a-channel-no-change` |
| 1238A exportador | `_walk` valida con `validate_pwo_payload` toda clave `bridge` | el bundle trae `bridge` arriba (no es seccion): `SECTIONS` y las 6 secciones no cambian |
| 1244A | proxys perezosos, `run_live_probes`, 4 sondas nuevas, cadena de receipts, `pytest_summary_ok`, `--write-inplace-receipt` | ids de sondas viejos intactos (01..37); nuevos 38..41 |

Aviso de edicion concurrente: `unified_bilateral_and_forum_grounded_pwo_advisor.py` estaba bloqueado por otro lane en Wave 34.
Se edito de forma quirurgica: sha256 al leer `a7552a5f...`, re-chequeo justo antes de escribir (sin cambios), sha256 nuevo en el receipt.

## 3. Sondas
- `run_differential_probes()`: 41 sondas (37 + 4). El lado 4.8 corre contra el baseline CONGELADO, asi `opus48_failed`
  sigue siendo verdad aunque los modulos vivos ya esten corregidos. Resultado: 41/41 con `opus48_failed` y `opus55_correct`.
- `run_live_probes() -> list[dict]`: repite la MISMA entrada adversarial contra el entrypoint VIVO. Cada entrada:
  `{id, finding_id, live_target "<ruta>::<funcion>", live_in_scope, live_correct, live_observed}`.
- Resultado: **30 en alcance, 30 correctas**; 11 fuera de alcance, 0 correctas (esperado, ver 5).
- Los 3 casos donde la observacion 4.8 no sirve para juzgar el vivo usan un criterio propio (PWO-15 tipado, PWO-19 informe de campos
  invalidos, PWO-21 severidad y `total_unknown`); el resto es "la sonda ya no falla" o el criterio 5.5.

## 4. Las cuatro sondas nuevas (honesto)
**PWO-16 (1212A, PROBE-1244-38) - PARCIAL, no ABANDON.** Binario usado: el `ame_core.ko` STOCK de aflturocket 2.4.2
(`artifacts/firmware_re_xc_ltu/ltu_extracted/.../ame_core.ko`, sha256 `a8d58e8d...`, ARM LE, ignorado por git, presente en disco).
El unico modulo versionado es el parcheado por FMX (Stage 64A), asi que se uso solo como segunda observacion.
- Anchos 12x: se re-derivan de `table_ptpPwrRange` (448 B, `.data`+0x1f8, offset de archivo `0x2056d0`; 4 perfiles x 8 anchos x 7
  modulaciones x 2 bytes; entrada 0 = 4096-QAM). Resultado: habilitado en 10/20/30/40/50, anulado `(0,0)` en 60/80/100 en los 4 perfiles.
  El orden de anchos sale del RE de Stage 12 (supuesto, no re-derivado).
- Inmediatos de frame: 2000 us en 83 sitios (`dp_imm`), 2500 en 46 (`movw`), 4000 en 65, 5000 en 61 (offsets en el receipt, p.ej. 0x7f14,
  0x7f28, 0x7f38, 0x7f44). Hay 18 lugares que cargan los CUATRO valores a menos de 48 bytes: evidencia de co-ubicacion de una escalera de frames.
- NO verificado: el rol. La funcion selectora no se decodifico (`frame_role_verified=false`), el censo de un valor suelto es debil
  (3000 us tambien aparece en 18 sitios) y el conteo "45 sitios" de RC-22 no se reproduce. Tambien: 8000 us aparece 5 veces como inmediato,
  asi que la nota del vector 1212A "no hay inmediato 8000 us" no la respalda un censo; no se toco ese vector.
- Falla 4.8: las constantes estan tipeadas y no hay verificador (`has_binary_verifier=false`). 5.5: sobre el stock `CONFIRMED`; sobre una copia
  con 12x activado en 60/80/100 `MISMATCH` (anchos); con la tabla tipeada `[2000,2500,4000,4999]` `MISMATCH`.
- Observacion lateral (a revisar por el dueno de Stage 64A): el modulo FMX-parcheado cambia 12 entradas de la tabla, pero todas en la ranura 6
  (QPSK 1x) de 60/80/100 MHz; la ranura 0 (4096-QAM) sigue en `(0,0)`. La derivacion de anchos no lo ve (el ancho 12x no cambia).

**PWO-29 (1214A, PROBE-1244-39).** Con un build legible de dos, 4.8 dice "60 is binary-confirmed". 5.5 (`penalty_verdict_hardened`)
exige todos los builds legibles; si no, `PARTIAL` (1 de 2). Ya cableado en `_penalty` (`binary_status`).

**PWO-40 (compuerta 1156A, PROBE-1244-40).** Un receipt con `status=FAILED` honesto se cambia a `CONFIRMED`: el `run_gate` 4.8 lo acepta
(corre con `DIRS`/`RECEIPT` apuntados a un tmp para no tocar el receipt del repo). `receipt_chain_build(paths)` / `receipt_chain_verify(chain)`
(sha256 sobre JSON canonico + eslabon previo) lo rechazan. Limite: si el atacante reconstruye toda la cadena, hay que anclar `head` afuera.

**PWO-41 (compuerta 1126A, PROBE-1244-41).** Un self-test con 1 passed y 1 skipped sale con rc 0 y la compuerta 4.8 lo da por bueno.
`pytest_summary_ok(texto)` rechaza skipped/xfailed/xpassed/deselected/failed y la falta de linea de resumen.

## 5. Sondas cuyo objetivo vivo esta FUERA de la lista de edicion
Son 11: PROBE-1244-29..37 (gate de 5 pilares `enforce_5pillar_research_gate`, `_doc_check`/`_find_key`/`SYNTH_FLAG_RE` de 1156A,
`check_1165a` de 1168A) y PROBE-1244-40/41 (`run_gate` 1156A, `check_selftests` 1126A). Esos verificadores NO se editaron (el lead consulta al
operador), por eso `live_in_scope=false` y `live_correct=false` se informa tal cual: las defensas 5.5 existen en 1244A pero ninguna compuerta
vigente las usa todavia.

## 6. Tests legados
- 27 archivos 1181A..1241A: 537 passed, 13 failed; los 13 son los preexistentes de otro lane (1218A-1223A, 1220A, 1221A, 1222A). Ningun fallo nuevo.
- Una asercion cambiada: `tests/test_stage1183a_pwo_bridge.py::test_data_sources_and_gates` (PWO-04): un evento sin ancho pasa de
  RECOMMEND a NO-CHANGE; se agrego la variante con `width_mhz=20` que sigue recomendando.
- No se corrieron las compuertas 1186A/1217A/1227A/1241A directamente: reescriben receipts historicos; las cubren las suites.
- 1245A (critica) sigue diciendo "37 sondas / cuatro sin sonda": es historico y no se edito.

## 7. Rollback
Restaurar el archivo congelado sobre el vivo: `tools/uisp/opus48_baseline/src/<modulo.dotted>.py.frozen` (sha256 en `MANIFEST.json`).
Nunca editar `opus48_baseline/`. Tras restaurar, `run_live_probes()` vuelve a marcar los modulos revertidos como incorrectos.
