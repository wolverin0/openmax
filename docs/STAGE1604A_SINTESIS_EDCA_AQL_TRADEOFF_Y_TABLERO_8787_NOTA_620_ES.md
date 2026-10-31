<!-- doc-head: Wave 94 (1602A-1604A) sintesis ES: feed del Command Center :8787 ampliado a la banda 1536A..1620A con clase de evidencia por item (offsets Wave 88/90 firmware-2.bin/ubntspecd static-binary; WMM EF p95 4.24ms Wave 91 live), nota #620 del compromiso EDCA/AQL airtime-capacity (EF p95 a costa de -11% TCP) y scholar honesto 1/3 -->
# Reporte ejecutivo - Compromiso EDCA/AQL, tablero :8787 ampliado y nota #620

**Wave 94 - Etapas 1602A-1604A - 2026-10-27 - 100% offline (0 SSH, 0 escritura a radios).**

## Que se hizo

Se amplio la banda del feed dinamico del Command Center :8787 de `1536A..1571A` a `1536A..1620A` y se
agregaron los tokens de Wave 88/90/91, cada uno con su propia clase de evidencia. Se ingreso la
sintesis del compromiso EDCA/AQL (airtime-capacity) y la RE de firmware-2.bin como nota #620
(evergreen); el vault paso de 619 a 620 notas.

## Etapa 1602A - feed ampliado a 1620 y tokens Wave 88/90/91

`tools/build_command_center_html.py` sube `RECEIPT_FEED_MAX` a 1620 y el catalogo pasa a llevar una
clase de evidencia por item. Los offsets de Wave 88/90 son **CONFIRMED_STATIC_BINARY** (extraidos de la
imagen ELF/SGMT por `/fullrea`, no lecturas en vivo):

- `0x009b7584` - umbral CCA de ath10k-ct en OpenWrt firmware-2.bin (stage1579A).
- `0x00980f8c` - literal de la tabla de reintento WMI 0x9044 en firmware-2.bin (stage1579A / stage1591A).
- `0x00407db8` / `0x004073b0` - productor y funcion del registro de stride de 188 B de ubntspecd
  (stage1578A / stage1590A).
- `roundtrip_bit_exact` - `patch_openwrt_ath10k_ct_firmware2_sgmt.py` parchea la IE SGMT y recomprime a
  un contenedor byte-identico (stage1579A).

El token de Wave 91 es distinto: **CONFIRMED_LIVE_HARDWARE**, no un offset estatico:

- WMM/EDCA EF (DSCP CS6) p95 = 4.24 ms bajo BE AQL = 600/1200 us, a costa de alrededor de -11% TCP
  (PtP en vivo, stage1584A).

Cada token se muestra solo en el recibo cuyos bytes lo contienen, asi que el feed sigue dinamico y
honesto. Se sincronizaron `champion_state_ledger.json` y `agent_task_board.json` con los nuevos tokens.
Recibo `artifacts/autoresearch/stage1602a_command_center_8787_wave88_91_live_sync.json`.

## Etapa 1603A - compromiso EDCA/AQL, recall-first y scholar (nota #620)

El resultado en vivo que se explica (stage1584A, CONFIRMED_LIVE_HARDWARE): achicar el presupuesto AQL de
AC_BE a 600/1200 us bajo el p95 de EF (voz) a 4.24 ms, pero a costa de aproximadamente -11% de throughput
TCP. Es el compromiso de capacidad de airtime de EDCA hecho concreto: darle acceso mas oportuno a la voz
le quita airtime al best-effort, no es una mejora gratis.

- **recall-first (vault + MemoryMaster):** 7 de 7 consultas con aciertos historicos (EDCA/WMM, AQL 20,
  BQL 20, bufferbloat, TXOP 20, LZ77, firmware QCA988x). MemoryMaster aporto el crossover WMM/TCP-ACK
  (Round 19), el QoE por AC + DSCP steering (Round 9) y el guard de HTT TX de QCA988x (Stage 671A).
- **scholar-mcp (jev-1.14.0, motor vivo P=0.94):** 1 de 3 principios verificado en vivo. La priorizacion
  por categoria de acceso de EDCA quedo VERIFICADA (mejor P=0.97, source=live) y explica la mejora del
  p95 de EF. El principio de bufferbloat (cola/latencia/throughput, mejor P=0.06) y el de compresion
  LZ77 (mejor P=0.07) dieron negativo honesto: ningun abstract top de arXiv los sostuvo directamente al
  umbral 0.5; quedan apoyados en el recall del vault/MemoryMaster y en la RE de binario estatico.

La sintesis se ingreso como **nota #620** (evergreen); el vault paso a 620 notas. Recibo
`artifacts/autoresearch/stage1603a_edca_aql_tradeoff_and_fw2_sgmt_note620.json`.

## Etapa 1604A - reconstruccion y verificacion en vivo :8787

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero. El daemon :8787 (con el
hot-reload del operador) tomo el cambio del builder de forma automatica. Verificacion por CLI:
`curl http://127.0.0.1:8787/FUTURAMAX_COMMAND_CENTER.html` responde **HTTP 200** y los bytes servidos
contienen el badge `RECIBOS 1536A-1620A`, los offsets `0x009b7584` / `0x00407db8` / `roundtrip_bit_exact`,
el item `WMM EF(CS6) p95 4.24ms` etiquetado `CONFIRMED_LIVE_HARDWARE`, y las 4 lineas de metricas de
`results.tsv`. La seccion pasa el balance de etiquetas HTML. Se actualizaron
`docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md` y `docs/CURRENT_STATE.md` (ambos < 180 lineas).

## Limites y advertencias (honestas)

- **Verificacion en navegador real: NO realizada.** Claude-in-Chrome no conecta en esta sesion y no hay
  Playwright; se verifico por CLI (HTTP 200 + bytes servidos) y balance de etiquetas, no por render DOM.
- Los offsets de Wave 88/90 son **CONFIRMED_STATIC_BINARY**, no lecturas en vivo. La mejora del p95 de EF
  es **real pero con costo** (alrededor de -11% TCP): es un compromiso de capacidad de airtime, no una
  ganancia de Pareto. La re-confirmacion en vivo del punto BE = 600/1200 us en A1->B1->A2->B2 sigue
  pendiente.
- El grounding scholar fue mixto y honesto: 1 de 3 verificado (EDCA), 2 negativos honestos (bufferbloat,
  LZ77), sin forzar veredictos.

## Que sigue (abierto, decision del operador)

- Verificacion visual en navegador del feed ampliado y los items con clase de evidencia.
- Promover (o no) el punto BE = 600/1200 us tras una re-verificacion en vivo A1->B1->A2->B2.
- Los TODOs en vivo D1.1..D6.1 siguen pendientes por sus carriles.

Recibos: `stage1602a_command_center_8787_wave88_91_live_sync.json`,
`stage1603a_edca_aql_tradeoff_and_fw2_sgmt_note620.json`, `stage1607a_wave94_opus48_gate.json`.
