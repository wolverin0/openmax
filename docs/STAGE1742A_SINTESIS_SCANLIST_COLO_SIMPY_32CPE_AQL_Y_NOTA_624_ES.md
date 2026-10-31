<!-- doc-head: Wave 117 (1740A-1742A) sintesis ES: nota #624 une Wave 105 (imagen colo repack ban_time=1200 + step-0 en vivo .241/.242 AB + scanlist .54 con 6035/5170/5200 MHz), Wave 111 (SimPy 32 CPE airtime + Pareto pymoo Panel2/3, simulados) y Wave 115 (RE ath10k slot/ack + mac80211 AQL); banda del Command Center :8787 a 1536A..1745A; SIN campeon nuevo; scholar INCONCLUSIVO por rate-limit; IDs de abonado solo como cpe_41/cpe_223/cpe_80/cpe_91 -->
# Reporte ejecutivo - Nota #624: scanlist colo, SimPy 32 CPE y AQL

**Wave 117 - Etapas 1740A-1742A - 2026-10-28 - 100% offline (0 SSH, 0 escritura a radios).**

## Que se hizo

Se sintetizaron las Waves 105, 111 y 115 en la nota evergreen #624. El feed del Command Center :8787 se
amplio a 1536A..1745A. El titular honesto: una sola evidencia en vivo (sondeo step-0 del colo + scanlist),
una imagen re-empaquetada localmente, dos simulaciones y dos RE estaticas. **No hay campeon de trafico
nuevo.** La identidad de abonado se registra solo como cpe_41/cpe_223/cpe_80/cpe_91, nunca por apellido.

## Etapa 1740A - sintesis (nota #624)

**Wave 105 (imagen repack + step-0 en vivo):** stage1668A (ACTUAL_LOCAL_NATIVE_FACTORY_REPACK) re-empaqueto
localmente una imagen SquashFS del colo con ban_time=1200 y la re-extrajo de forma independiente para
verificar el repack (artefacto de imagen, NO flasheado). stage1669A (CONFIRMED_LIVE_HARDWARE) corrio el
plan de canal step-0 del PtP-Colo en vivo + un A/B .241<->.242; el scanlist leido del extremo .54 lista
**6035, 5170 y 5200 MHz** como canales candidatos (el superchannel 6035 mas los respaldos de 5 GHz).

**Wave 111 (SimPy + Pareto, simulados):** stage1704A (SIMULATED_MODEL) modelo SimPy determinista del
dual-bind + airtime fairness de los 32 CPEs de Guarida (28 CPEs modelados, ban_time=1200). stage1705A
(SIMULATED_MODEL) schedule Pareto pymoo NSGA-II para Panel2/Panel3 (aql_enable=1, sharing de airtime).
Ambos son simulaciones, no corridas en vivo.

**Wave 115 (RE estatica):** stage1728A (CONFIRMED_STATIC_BINARY) RE de slot/ack de ath10k + AQL de
mac80211 (airtime_flags_mac=1, AQL habilitado). stage1729A (CONFIRMED_STATIC_DATA) reconciliacion de knob
AQL + bench (airtime 21 refs, aql_threshold) - mapeo estatico, pendiente de confirmacion en vivo.

**recall-first:** aciertos fuertes (airtime fairness AQL 20, SimPy 32 CPE 8, pareto schedule 5, mac80211
AQL slot/ack 1; scanlist 6035 y repack ban_time 0). La sintesis se ingreso como nota #624 (evergreen); el
vault paso a 624 notas. Recibo
`artifacts/autoresearch/stage1740a_hyperresearch_colo_scanlist_simpy_aql_note624_receipt.json`.

## Etapa 1740A - scholar (chequeo unico suave, INCONCLUSIVO honesto)

Se hizo UN chequeo suave de un principio atomico de airtime fairness, con 4 s de espacio. El sondeo de
liveness del motor funciono (P=0.96, source=live), pero el unico scholar_verify_claim dio FETCH_FAILED
(HTTP 429): la ruta de verify sigue rate-limited entre waves. Por eso la pata scholar queda INCONCLUSIVA
(fetch degradado), NO un negativo; la sintesis se apoya en el recall y en los recibos propios en
vivo/repack/simulados/estaticos.

## Etapa 1741A - banda del feed a 1536A..1745A

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero con la banda ampliada; los 6
recibos de Wave 117 aparecen con su propia clase de evidencia (1 en vivo, 1 factory-repack, 2 simulados,
2 estaticos). Se verifico que el render del tablero NO contiene apellidos de abonado (solo cpe_*), tras
anonimizar las etiquetas de Panel1 en el builder. Recibo
`artifacts/autoresearch/stage1741a_command_center_1745a_band_refresh_receipt.json`.

## Limites y advertencias (honestas)

- **Sin campeon de trafico nuevo** esta wave. La unica evidencia en vivo es el sondeo step-0 del colo +
  scanlist; la imagen del colo es un repack local (no flasheado); el airtime de 32 CPEs y el schedule de
  Panel2/3 son SIMULACIONES; el trabajo de slot/ack/AQL es RE estatica.
- **scholar INCONCLUSIVO** por rate-limit (HTTP 429), no un negativo; motor vivo (P=0.96).
- **Privacidad:** se anonimizaron apellidos a cpe_41/cpe_223/cpe_80/cpe_91 en el builder del tablero, la
  nota #623 y el doc STAGE1718A. Quedan apellidos en archivos previos no mios (topic_guarida-sectors.md,
  STAGE168A, STAGE169A) para que el operador decida depurarlos.
- **Verificacion en navegador real: NO realizada** (Claude-in-Chrome no conecta); se verifico por CLI
  (HTTP 200 + bytes servidos) y balance de etiquetas; restart limpio del daemon :8787 para la banda 1745.

## Que sigue (abierto, decision del operador)

- Cutover en vivo del colo a un canal del scanlist (6035/5170/5200) y validacion en vivo de las
  predicciones SimPy/AQL.
- Depurar apellidos en los 3 archivos previos marcados; re-correr scholar tras el rate-limit.

Recibos: `stage1740a_hyperresearch_colo_scanlist_simpy_aql_note624_receipt.json`,
`stage1741a_command_center_1745a_band_refresh_receipt.json`, `stage1745a_wave117_opus2_gate.json`.
