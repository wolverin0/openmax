<!-- doc-head: Wave 63 (1416A-1421A) sintesis ejecutiva ES: verificacion scholar-mcp de AQL/FQ-CoDel y ACR 5 GHz, honesta y 100% offline -->
# Reporte ejecutivo — HYPERRESEARCH + scholar: AQL, FQ-CoDel y espectro 5 GHz

**Wave 63 · Etapas 1416A–1418A · 2026-10-27 · 100% offline (0 SSH, 0 escritura a radios).**

## Qué se hizo

Se verificaron nuestras afirmaciones de investigación contra la literatura usando las herramientas
del MCP `scholar` (`scholar_search`, `scholar_inspect`, `scholar_verify_claim`,
`scholar_verify_predicate`, `scholar_research`), invocadas por importación directa de
`scholar.mcp.server` (el transporte MCP no está conectado en esta sesión). El portón semántico es
Jev System One `jev-1.14.0` (en vivo; la sonda de vida devolvió `P=0.96, source=live`). Los
candidatos salen de arXiv; las métricas de citación salen de OpenAlex (frecuente `400` en el
filtro por id de arXiv, por eso casi todos los grafos de citación quedan `PARCIAL`).

## Resultado honesto

- **2 de 3 afirmaciones primarias quedaron VERIFICADAS EN VIVO.** La tercera es regulatoria y se
  deriva a normas, no a papers.
- De los 10 descubrimientos aplicables a literatura: 4 encontraron papers relevantes por el portón
  y 6 devolvieron `SIN_CANDIDATO_QUE_PASE_EL_PORTON` (un negativo honesto).
- **A ningún descubrimiento se le forzó un veredicto "soportado".** Los hallazgos de ingeniería
  propios no son afirmaciones publicadas; decirlo es lo honesto.

### Afirmación A — Equidad de airtime + FQ-CoDel (VERIFICADA EN VIVO)

Høiland-Jørgensen et al., *Ending the Anomaly* (USENIX ATC 2017), **arXiv:1703.00064**. Las cuatro
sub-afirmaciones atómicas dieron **soportado/verificado (en vivo)**, mejor `P=0.98`: reducción de
latencia bajo carga de un orden de magnitud; planificador de airtime en el AP sin cambios en los
clientes; esquema de colas que elimina el bufferbloat; equidad de airtime casi perfecta para TCP y
UDP de bajada. Es la base de nuestra línea de airtime/AQM (ath9k/ath10k → kernel Linux).

### Afirmación B — Límites AQL por-AC, 20 MHz vs 40 MHz (VERIFICADA EN VIVO + MODELO DERIVADO)

La premisa de acotar la cola se verifica contra **arXiv:1703.00064** (`P=0.97`, soportado, en
vivo): "limitar los bytes encolados acota la latencia bajo carga". El portón también trajo
**arXiv:1004.4588** (QoS WiFi de campus; relevante pero sin soporte directo).

**Modelo derivado (no es cita).** `limit_bytes = T_airtime_µs × R_phy_Mbps / 8`. A igual
MCS/flujos/GI, 802.11n/ac lleva **108 subportadoras de datos a 40 MHz vs 52 a 20 MHz**
(IEEE 802.11-2020, norma no verificable por scholar), así que `R_phy(40 MHz) ≈ 2.08 × R_phy(20 MHz)`.
Por lo tanto, para mantener el **mismo** objetivo de airtime al pasar de 20→40 MHz, el presupuesto
de bytes AQL debe escalar **≈2.08×**. Un límite fijo mal calibrado al ancho activo o castiga el
caudal (sub-llenado) o dispara la latencia de cola (sobre-llenado): AQL debe ser consciente del
ancho de canal.

**Anclas empíricas locales** (rondas del banco; `RETENER_CAMPEON` = el candidato no superó al
campeón): el acople AQL ingenuo degradó esta plataforma — `S72A-COUPLED-AP-AQL-XC-V20` (caudal
−10.3%, p95 +6.0%); `S72A-R2-AP-AQL-1500-3000-THR-4500` (caudal −2.7%, **p95 +62.1%**);
`S76B-R3-…-AQL1200-2400` (caudal +9.1%, p95 +2.8%). Confirman la advertencia del modelo.

### Afirmación C — ACR y banda de guarda en PtP 5 GHz co-ubicados (NORMA, NO SCHOLAR)

El rechazo de canal adyacente y la separación de bordes de banda son temas regulatorios; el portón
devolvió **`SIN_CANDIDATO_QUE_PASE_EL_PORTON`** para las dos afirmaciones de coexistencia (negativo
honesto). Referencias que gobiernan: **FCC 47 CFR §15.407** (bordes U-NII-1 5150–5250 MHz, U-NII-3
5725–5850 MHz y emisiones fuera de banda), **IEEE 802.11-2020** (máscara espectral de transmisión y
mínimos de rechazo de canal adyacente/alterno) y **ETSI EN 301 893** (RLAN 5 GHz, UE). Consecuencia
operativa: en PtP exterior co-ubicado hacen falta canales no solapados más una banda de guarda
dimensionada a la curva de ACR del receptor; U-NII-1 y U-NII-3 difieren en margen de borde y en
obligaciones DFS.

## Mapa de descubrimientos (FMX-DISC-20..36)

Descubrimientos de ingeniería inversa de binarios (offsets de símbolos, gramáticas de ioctl,
auditorías SquashFS/flash) son `NO_APLICABLE_RE_BINARIO`: la literatura no los puede confirmar, así
que solo llevan clasificación — **FMX-DISC-20, 22, 29, 30, 33, 34, 35**.

Aplicables a literatura, con el resultado del portón `scholar_research`:

| Descubrimiento | Aplicabilidad | Resultado del portón | Paper(s) relevante(s) |
|---|---|---|---|
| FMX-DISC-21 (control de potencia TX) | PARCIAL | SIN_CANDIDATO | — |
| FMX-DISC-23 (encolado por flujo ↓ latencia) | ALTA | RELEVANTE | arXiv:1601.07597 |
| FMX-DISC-24 (tiempo CAC de DFS) | PARCIAL | SIN_CANDIDATO | — |
| FMX-DISC-25 (menos canales de escaneo ↓ handoff) | PARCIAL | RELEVANTE | arXiv:1102.5189, arXiv:0901.4642 |
| FMX-DISC-26 (aviso de cambio de canal) | PARCIAL | SIN_CANDIDATO | — |
| FMX-DISC-27 (overhead por-paquete ↓ caudal) | ALTA | SIN_CANDIDATO | — |
| FMX-DISC-28 (overhead de estadísticas por-paquete) | PARCIAL | RELEVANTE | arXiv:2312.07152 |
| FMX-DISC-31 (canal más ancho ↑ caudal) | ALTA | SIN_CANDIDATO | — |
| FMX-DISC-32 (shaping con prioridad acota latencia) | PARCIAL | RELEVANTE | arXiv:2008.03904 |
| FMX-DISC-36 (overhead de reenvío mesh 802.11s) | PARCIAL | SIN_CANDIDATO | — |

Los papers "relevantes" pasaron el filtro `P_empirical`/`P_applicable` pero **no** soportaron de
forma directa la afirmación específica (quedó `unsupported, live`): son evidencia relacionada, no
confirmación.

## Límites y advertencias

- **OpenAlex 400** suprimió casi todos los conteos de citación (grafos `PARCIAL`, no "cero citas").
- **Afirmación C y 6 descubrimientos**: `SIN_CANDIDATO_QUE_PASE_EL_PORTON` es un negativo real del
  portón, no evidencia en contra de la ingeniería.
- **Cifras de norma** (subportadoras, bordes de banda, mínimos de ACR) son
  `NORMA_NO_VERIFICABLE_POR_SCHOLAR`; no se cita ninguna tasa PHY de memoria.
- Esto fue una **extensión del reactor**, no una corrida completa de HYPERRESEARCH V8 (Etapa 1417A).

## Qué sigue (abierto)

- Si se quiere confirmación directa de los descubrimientos, haría falta una corrida HYPERRESEARCH V8
  completa (no se lanzó: son 16 pasos + subagentes + Stop hook) o fuentes no-arXiv (IEEE Xplore).
- La decisión de valor de `aql_threshold` y el ancho AQL por-ancho-de-canal siguen siendo decisión
  del operador / lane de campeones, no resolubles por literatura.

Recibos: `stage1416a_scholar_mcp_claim_verification_ledger.json`,
`stage1417a_hyperresearch_v8_reactor_run_receipt.json`,
`stage1421a_wave63_hyperresearch_scholar_gate.json`.
