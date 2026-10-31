<!-- doc-head: Stage 1245A critica honesta en espanol de Opus 5.5 sobre Opus 4.8 en el bridge PWO 1183A, reconciliador LTU 1212A, reglas 1213A, constantes 1214A, exportador 1238A y verificadores 1121A-1168A, con sondas diferenciales ejecutadas (receipt 1244A); todo offline, simulado, recommend-only -->
# Stage 1245A - Critica de Opus 5.5 a Opus 4.8 (PWO, reglas y verificadores)

Documento de critica (sin receipt propio; el receipt es el de 1244A). Offline, `live_devices_touched=false`, `simulated=true`.

## 1. Veredicto honesto
- Opus 4.8 escribio modulos ordenados, con receipts y gates, pero casi todo es **forma sin comportamiento**: los gates miran que existan claves, no que el codigo haga lo que dice.
- El fallo mas grave: el bridge 1183A, alimentado con la salida REAL del motor 1181A, recomienda un cambio de canal con `channel: None`.
- El segundo: el ancho se puede esconder (`width_mhz=20` junto a `requested_width_mhz=40` pasa) y un ancho desconocido recomienda igual (trampa 8 del spec).
- El tercero: el gate de 5 pilares se supera con `{"boards":{}, "rounds":[], "stage":"x", "outputs":{}}` sin una sola evidencia.
- Opus 5.5 no "reescribio todo": agrego adaptadores endurecidos (fail-closed) y, sobre todo, **sondas que ejecutan ambos lados** sobre la misma entrada.
- Resultado: 41 hallazgos (3 CRITICAL, 9 HIGH, 20 MEDIUM, 9 LOW) y 37 sondas; en las 37 el 4.8 falla y el 5.5 responde bien. Cuatro hallazgos NO tienen sonda (ver 9).
- Lo que 4.8 hizo bien: guard de ancho por defecto fail-closed, `auto_approve` siempre `False`, escritura de receipts con chequeo NUL/readback, citas con needle (provenance_gap en vez de confiar).

## 2. Metodo (por que las sondas no son autoafirmacion)
- Modulo: `tools/uisp/opus55_hardened_pwo_bridge_and_rules_verifier.py`. Cada sonda importa el original 4.8 y la funcion endurecida y los ejecuta con la misma entrada adversarial.
- `opus48_failed` y `opus55_correct` salen de predicados evaluados sobre lo observado; una excepcion del 4.8 se registra como fallo observado.
- Ejemplo central: `evaluate_channel_change(build_site_graph(), "ptp-almafuerte60-guarida61", 5500)` (1181A real) va a los dos bridges.
- El contrato del spec se parsea de `network-and-pwo.md` (sha256 pineado); si no esta, snapshot pineado con `source: "pinned_snapshot"`.
- Spec leido solo con lectura; nada se escribe fuera de `artifacts/verification/` y `docs/`.

## 3. Bridge 1183A (`tools/uisp/pwo_bilateral_recommendation_bridge.py`)
| Id | Falla 4.8 (linea) | Sev | Correccion 5.5 | Sonda |
|---|---|---|---|---|
| PWO-01 | L60 lee `channel`/`proposed_channel`; el motor emite `candidate_channel_mhz` -> `channel: None` | CRITICAL | resuelve 4 claves, entrega `channel_mhz` y `channel_number` enteros | P-01 |
| PWO-02 | L41 `_requested_width` devuelve la primera clave no nula: `width_mhz=20` oculta `requested_width_mhz=40` | CRITICAL | recorre todas las claves de ancho a cualquier profundidad | P-02 |
| PWO-03 | L38 solo mira `proposal[k]` (un nivel) | HIGH | recursion con tope 32, exceso = veto | P-03 |
| PWO-04 | L47 sin ancho = recomienda; el spec dice que ancho desconocido se rechaza | HIGH | ancho desconocido = error de esquema, NO-CHANGE | P-04 |
| PWO-05 | L53 `allowed` por veracidad: `"false"` o `[0]` pasan | HIGH | `allowed` debe ser `bool`; solo `True` sin vetos recomienda | P-05 |
| PWO-06 | L60 sin unidad ni rango: 99999, o 157 en una clave `_mhz` | HIGH | MHz 5150-5925 en raster de 5, o numero de canal 32-196 (se convierte) | P-06 |
| PWO-07 | L78 `evaluated_ends` se copia sin validar (1, `[]`) aunque el texto dice "ambos extremos" | MEDIUM | debe ser 2 o lista de 2 extremos distintos | P-07 |
| PWO-08 | L21 gates y `SOURCE_DOC` (ruta absoluta de Windows) copiados a mano; el texto ya deriva (parentesis) | MEDIUM | gates extraidos del spec, snapshot + sha256 | P-08 |
| PWO-09 | L134 el receipt dice `source_doc_read` pero ningun codigo abre el doc | MEDIUM | `extract_pwo_contract_from_spec` lee y hashea de verdad | P-09 |
| PWO-10 | L65 no hay validador del payload; el bundle 1238A no lo incluye | MEDIUM | `validate_pwo_payload` (modo, auto_approve, ancho, gates, fuentes, canal) | P-10 |
| PWO-11 | L49 `vetoes="boom"` se vuelve la razon `b; o; o; m` | LOW | vetos no-lista = error de esquema, texto intacto | P-11 |
- Nota de honestidad: los gates 4.8 difieren del spec solo en formato (parentesis); la cantidad (6) coincide. No es un fallo funcional, es deriva.
- Nota: las demos de 1202A solo llegan a vetos, asi que el `channel: None` esta **latente** en el pipeline (lo dispara cualquier evaluacion permitida).

## 4. Reconciliador LTU 1212A (`tools/uisp/pwo_ltu_binary_capabilities_and_frame_reconciler.py`)
| Id | Falla 4.8 (linea) | Sev | Correccion 5.5 | Sonda |
|---|---|---|---|---|
| PWO-12 | L53 `frame_valid` lanza ValueError/OverflowError/TypeError con NaN, inf, str, None | MEDIUM | `frame_valid_hardened` devuelve `False`, nunca lanza | P-12 |
| PWO-13 | L53 `round()` acepta 2.0004 ms como 2000 us | LOW | coincidencia exacta a 1e-6 us | P-13 |
| PWO-14 | L49 `"2X2"` se rechaza | LOW | `2x2` sin distinguir mayusculas/espacios | P-14 |
| PWO-15 | L22 `TX_BACKOFF_DBM` mezcla `16` y `"10-12"`; sumar lanza TypeError | LOW | `tx_backoff_dbm_typed()` con `min_dbm`/`max_dbm` | P-15 |
| PWO-16 | L20 inmediatos 2000/2500/4000/5000 us y anchos QAM escritos a mano | MEDIUM | **no verificado aqui**: no re-derive nada de `ame_core.ko` | - |
- `qam_12x_allowed` con NaN, negativo, str, bool: el 4.8 devuelve `False` correctamente. Esa pista no se confirmo.

## 5. Reglas 1213A (`tools/uisp/pwo_coverage_gap_rules_stall_eth_disconnect.py`)
| Id | Falla 4.8 (linea) | Sev | Correccion 5.5 | Sonda |
|---|---|---|---|---|
| PWO-17 | L68 `ping_loss_pct=NaN`: `nan < 20` es falso, enlace sano dispara tarjeta de stall | HIGH | no finitos y fuera de rango se ignoran | P-16 |
| PWO-18 | L63 `associated="false"` (str truthy) cuenta como asociado | HIGH | `associated` debe ser exactamente `True` | P-17 |
| PWO-19 | L40 `_num` manda str/None/bool a 0.0: `"80"` no genera tarjeta y nadie se entera | MEDIUM | igual regla + `rules_data_quality()` lista cada campo descartado | P-18 |
| PWO-20 | L59 RSSI positivo (+55, error de signo) cuenta como sano | MEDIUM | RSSI > 0 invalido, salud desconocida | P-19 |
| PWO-21 | L113 `cpe_total=NaN` oculta una tormenta real; total ausente dispara en silencio | MEDIUM | total desconocido = severidad medium y bandera; fraccion tope 1 | P-20 |
| PWO-22 | L105 la recomendacion siempre dice "no es RF" aunque la RF este degradada | MEDIUM | texto segun `ethernet_vs_rf` | P-21 |
| PWO-23 | L122 NaN en la evidencia; `json.dumps` escribe `NaN` y `JSON.parse` de Node lo rechaza | MEDIUM | evidencia saneada, JSON estricto | P-22 |
| PWO-24 | L71 cero bytes sin perdida en enlace sano = severidad high (puede ser enlace ocioso) | LOW | medium + `idle_possible` | P-23 |
| PWO-25 | L94 `peer_observation={}` lanza ValueError y aborta toda la pasada | MEDIUM | forma validada, cae a chequeo de RF | P-24 |
- Fronteras documentadas (todas inclusivas): RSSI >= -70, SNR >= 25, perdida >= 20, CRC >= 100, reasoc >= 5 y fraccion >= 0.3. `evaluate_rules_hardened` sigue lanzando TypeError si no recibe un dict.
- Pista descartada: ZeroDivision en la tormenta no existe (el 4.8 lo protege); el problema real es NaN/total ausente.

## 6. Constantes 1214A (`tools/re/reconcile_stage1187a_binary_constants_audit.py`) y exportador 1238A
| Id | Falla 4.8 (linea) | Sev | Correccion 5.5 | Sonda |
|---|---|---|---|---|
| PWO-26 | L164 el veredicto "Stage 10 mejor sustentado / 70A es error de unidad" es texto fijo, incluso con 0 binarios leidos | HIGH | `missing_poll_conclusion_hardened` deriva del dato; sin binarios = `INCONCLUSIVE_NO_BINARY_EVIDENCE` | P-25 |
| PWO-27 | L94 ELF truncado/sin `.text` lanza `struct.error`/KeyError y aborta el receipt entero | MEDIUM | `scan_elf_safe` registra `provenance_gap` | P-26 |
| PWO-28 | L72 citas `(doc, linea, needle)`: si el doc se corre 3 lineas, falso gap | MEDIUM | `locate_cite` ancla en el needle y reporta deriva | P-27 |
| PWO-29 | L227 "60 confirmado por binario" aunque solo se lea 1 de 2 builds | LOW | sin sonda: exigir todos los builds legibles | - |
| PWO-30 | 1238A L27 sin seccion de bridge; `_walk` solo atrapa `auto_approve`, no ancho/modo/gates | MEDIUM | `validate_pwo_payload` cubre el payload | P-28 |
- Hoy las 17 citas de 1214A siguen validas (la podredumbre es latente) y un binario ausente SI queda como `provenance_gap`; lo fallido es la conclusion fija. Con un `.ko` truncado el 4.8 aborta todo.

## 7. Verificadores 1121A-1168A y gate de 5 pilares
| Id | Falla 4.8 (linea) | Sev | Correccion 5.5 | Sonda |
|---|---|---|---|---|
| PWO-31 | `enforce_5pillar` L46: `boards:{}` satisface A/B/D, `rounds` C, `stage`+`outputs:{}` E | CRITICAL | `five_pillar_audit_hardened`: bloques anidados, `CONFIRMED`, archivos que existen | P-29 |
| PWO-32 | L89/L105 tres palabras magicas dentro de `str(receipt)` satisfacen C y D | HIGH | la palabra necesita valor numerico; senal `keyword_only` | P-30 |
| PWO-33 | L117 cualquier bloque anidado no vacio pasa, incluso `{"status":"FAILED"}` | HIGH | `status` debe ser `CONFIRMED` con evidencia por pilar | P-31 |
| PWO-34 | 1213A L165 `claims_verified` de otra etapa (1212A), nadie lo senala | LOW | senal asesora `claims_verified_stage_mismatch` (no fallo duro) | P-32 |
| PWO-35 | 1156A L74 `_doc_check` acepta 3 encabezado y uno vacio (solo 1162A exige uno) | MEDIUM | `doc_check_hardened` | P-33 |
| PWO-36 | 1156A L125 `"BLOCKED"` por subcadena acepta `NOT_BLOCKED` | MEDIUM | `blocked_state_ok` mira campos `*status*` | P-34 |
| PWO-37 | 1156A L79 `_find_key` toma el primer match: un senuelo anidado gana al valor real | MEDIUM | `find_key_strict` (nivel superior gana, conflicto lanza) | P-35 |
| PWO-38 | 1168A L131 `broken_links=False` pasa `bl != 0` | MEDIUM | `count_is_zero` rechaza bool | P-36 |
| PWO-39 | 1156A L39 regex solo ve `true` literal, no `"true"` | LOW | `synthetic_flag_present` parsea JSON | P-37 |
| PWO-40 | 1156A L176 el gate cree `status: CONFIRMED` autodeclarado; sin hash/mtime/codigo | MEDIUM | sin sonda: exige cadena de receipts con hash | - |
| PWO-41 | 1126A L170 pytest rc 0 con tests saltados cuenta como pass | LOW | sin sonda: leer el resumen de skips | - |
- `audit_verifier_weaknesses()` ejecuta estas comprobaciones contra 1126A/1132A/1150A/1156A/1168A (21 filas, `confirmed` calculado, no escrito a mano).
- Pistas no confirmadas: el gate no traga excepciones como pass (un UTF-8 roto o un JSON-lista aborta: fail-closed); 1126A hashea el manifiesto del kit, pero tampoco ata el receipt.
- Control positivo: 1162A SI exige un unico encabezado. Es la prueba de que el patron correcto ya existia y no se propago.

## 8. Topologia (1181A/1182A/1200A/1202A/1206A): resumen corto
- Esas auditorias son de otro carril: ver `artifacts/verification/stage1242a_opus55_review_of_opus48_topology_engines.json` y `docs/STAGE1243A_OPUS55_DEEP_AUDIT_AND_UPGRADE_OF_OPUS48_TOPOLOGY_ENGINES.md` (27 hallazgos: 4 CRITICAL, 11 HIGH, 10 MEDIUM, 2 LOW; 28/28 sondas con falla 4.8 y correccion 5.5). Total de la ola en `stage1246a_opus55_vs_opus48_scorecard.json`.
- Hechos que verifique yo ejecutando el 4.8: `evaluate_channel_change` emite `candidate_channel_mhz` y `evaluated_ends: 2` (entero); acepta cualquier entero positivo: `157` como MHz sale `allowed: True` (no hay validacion de rango).
- Ese 157 en MHz es justo la confusion MHz/numero de canal que el bridge 4.8 arrastra (la `_fixture()` usa 157 como numero).
- `run_pipeline` de 1202A pasa la forma real del motor al bridge; en las 5 demos todas las tarjetas son `NO-CHANGE`.
- Para 1181A/1182A/1200A/1202A/1206A (SG-01, bilateral, blast radius) no emito veredicto aqui.

## 9. Que sigue SIMULATED_MODEL_ONLY
- Todo lo de este stage: payloads, reglas y sondas corren sobre entradas fabricadas; no hay radios ni llamadas en vivo.
- Las atribuciones a `.ko` y los inmediatos de frame (2000/2500/4000/5000 us) son RE estatico, no reproduccion en vivo; PWO-16 queda sin verificar.
- La conducta de PWO real (`ChangeExecutor`, `WirelessExperimentGates`) no se probo: solo el contrato del spec.
- Hallazgos sin sonda: PWO-16, PWO-29, PWO-40, PWO-41.
- `CONFIRMED_LIVE_HARDWARE` sigue en 0. No hay ningun claim `PRODUCTION_READY`.

## 10. Decisiones y desviaciones
- Ancho desconocido = veto (spec trampa 8): una evaluacion sin clave de ancho ya NO recomienda, aunque la `_fixture()` 4.8 si.
- Cadenas numericas ("80") se tratan como invalidas (no se coercionan) y se reportan con `rules_data_quality`.
- El modulo supera las ~800 lineas recomendadas porque el contrato pedia un solo archivo.

## Correr
`python tools/uisp/opus55_hardened_pwo_bridge_and_rules_verifier.py --write-receipt` y `pytest tests/test_stage1212a_to_1217a_suite.py tests/test_stage1236a_to_1241a_suite.py -q`.
