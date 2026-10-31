<!-- doc-head: Wave 81 (1524A-1529A) sintesis ES: calculo exacto de ACK/slot-time/coverage-class por distancia (2d/c) para PtP-Colo y Guarida + wiki persistente hyperresearch + scholar TDMA-CSMA, 100% offline -->
# Reporte ejecutivo - calculo ACK / slot-time / coverage-class y wiki hyperresearch

**Wave 81 - Etapas 1524A-1526A - 2026-10-27 - 100% offline (0 SSH, 0 escritura a radios).**

## Que se hizo

Se verificaron afirmaciones contra la literatura con las cinco herramientas del MCP `scholar`
(`scholar_search`, `scholar_inspect`, `scholar_verify_claim`, `scholar_verify_predicate`,
`scholar_research`) por importacion directa de `scholar.mcp.server`, con el porton Jev System One
`jev-1.14.0` en vivo, y se calculo la matriz exacta de temporizacion 802.11 por distancia. Las notas
de la ola se sincronizaron al wiki persistente real `.hyperresearch/hyperresearch.db` (59 notas).

## Resultado scholar honesto

- **1 de 3 afirmaciones quedo VERIFICADA EN VIVO** (B, hibrido TDMA-CSMA/CA). A (ACK/slot-time vs
  propagacion) y C (rango vs caudal) dan negativo real del porton y se sostienen en norma y fisica.

### Afirmacion A - ACK timeout / slot time vs propagacion

**NO_CANDIDATE_PASSED_GATE + FISICA/NORMA.** Las afirmaciones de slot-time vs propagacion no tuvieron
soporte en arXiv (el paper adyacente **arXiv:0901.2333**, un Q-CSMA por longitud de cola, paso el
filtro sin soportar la afirmacion): negativo honesto. La relacion ACK-timeout / slot-time /
coverage-class es de norma y fisica de libro: **IEEE 802.11-2020** (aSlotTime 9 us, aSIFSTime 16 us
en 5 GHz OFDM) y el analisis CSMA de Kleinrock-Tobagi. La Etapa 1525A calcula la matriz exacta.

### Afirmacion B - Coexistencia hibrida TDMA-a-CSMA/CA

**VERIFICADA EN VIVO.** Contra **arXiv:1401.5528** (*Distributed and Centralized Hybrid CSMA/CA-TDMA
...*), la afirmacion de MAC hibrido dio soportado/verificado (en vivo, `P=0.75`): los protocolos MAC
hibridos combinan acceso programado (TDMA) y por contienda (CSMA/CA). Es la base de literatura para
un MAC exterior programado-mas-contienda.

### Afirmacion C - Rango exterior vs caudal (RTT de propagacion)

**NO_CANDIDATE_PASSED_GATE + FISICA.** Las afirmaciones de RTT / eficiencia no tuvieron soporte en
arXiv (los primeros resultados fueron de modelos de difusion y RTT en grafos). La relacion
rango-vs-RTT es fisica exacta, calculada en la Etapa 1525A: RTT = 2d/c crece lineal con la distancia
y la eficiencia del protocolo cae cuando el RTT se acerca al tiempo de trama.

## Etapa 1525A - matriz exacta de temporizacion

`tools/research/compute_outdoor_ack_slottime_coverage_class_matrix.py` calcula, con procedencia
etiquetada, la propagacion y la temporizacion 802.11 por sitio. La propagacion es `EXACT_PHYSICS`
(RTT = 2d/c, c = 299792458 m/s); slot/ACK/CTS usan constantes `IEEE_STD_CONSTANT` mas el delta por
distancia.

| Sitio | Distancia | RTT (us, exacto) | coverage_class (iw ceil/450) | slot_time (us) | ack_timeout (us) |
|---|---|---|---|---|---|
| banco | 0 m | 0.000 | 0 | 9 | 25 |
| Guarida Panel1 cerca | 200 m | 1.334 | 1 | 12 | 27 |
| Guarida Panel3 medio | 1000 m | 6.671 | 3 | 18 | 32 |
| Guarida Panel2 | 1500 m | 10.007 | 4 | 21 | 36 |
| PtP-Colo | 1800 m | 12.008 | 4 | 21 | 38 |
| Guarida Panel3 lejos | 3000 m | 20.014 | 7 | 30 | 46 |
| Guarida borde | 3500 m | 23.349 | 8 | 33 | 49 |

El comando `iw phy phy0 set distance <d>` programa la coverage class. La propagacion exacta es la
parte inequivoca; la constante base de ACK (25 us = SIFS 16 + slot 9) y la extension de slot
(coverage_class por 3 us) derivan de la norma.

## Discrepancia de coverage class (marcada, no oculta)

El mapeo de libro de `iw` ceil(d/450) da clase 4 a 1500 m y clase 7 a 3000 m, pero el Round 13 en
vivo observo clase 3 a 1500 m y clase 6 a 3000 m (aprox d/500). El hardware en vivo es la autoridad;
los dos mapeos difieren, asi que la matriz marca 1500 m y 3000 m como `NEEDS_LIVE_CONFIRMATION` en
vez de reconciliarlos en silencio. Es un hallazgo real y accionable antes de programar la distancia
en la flota.

## Wiki persistente (Etapa 1524A)

Las notas de literatura se escribieron en `research/notes/scholar_sources/` con frontmatter
`type: note` y se corrio `sync` / `repair` / `index build` / `status` contra la base viva (59 notas).
Las busquedas de ACK timeout, slot time, coverage class, TDMA, CSMA y propagacion devuelven aciertos.
Este reporte se sincronizo al mismo vault.

## Limites y advertencias

- OpenAlex `400` suprimio casi todos los conteos de citas (grafos `PARCIAL`, no cero-citas).
- A y C no tuvieron soporte directo en arXiv: la base real es IEEE 802.11-2020 mas fisica exacta de
  propagacion, no evidencia en contra.
- Las formulas de base de ACK y de slot por coverage class usan constantes estandar; el delta por
  distancia (2d/c) es la parte exacta. El mapeo de coverage class en vivo difiere del de libro y
  queda marcado para confirmacion, no asumido.
- No se cita de memoria ningun valor. Fue un calculo mas una sincronizacion real de vault, no una
  corrida completa de V8.

## Que sigue (abierto, decision del operador)

- Confirmar en el dispositivo el mapeo distancia -> coverage class (1500 m y 3000 m) antes de
  programar `iw set distance` en la flota. El valor de aql_threshold sigue siendo decision del operador.

Recibos: `stage1524a_scholar_ack_slottime_tdma_csma_ledger.json`,
`stage1525a_outdoor_ack_slottime_coverage_class_receipt.json`,
`stage1529a_wave81_hyperresearch_ack_gate.json`.
