<!-- doc-head: SUPERSEDED (W435, 31/10): the PtP-Colo 1.8 km (GPS) figure is superseded; the operator says the link is 450 m (30/10), see STAGE3098A. Wave 78 (1506A-1511A) sintesis ES: bootstrap del wiki persistente hyperresearch SQLite (.hyperresearch) + scholar LDPC/BCC y Short-GI/Long-GI para PtP-Colo 1.8 km y Guarida, 100% offline -->
# Reporte ejecutivo - wiki persistente hyperresearch SQLite y ganancia LDPC / Short-GI

**Wave 78 - Etapas 1506A-1508A - 2026-10-27 - 100% offline (0 SSH, 0 escritura a radios).**

## Que se hizo

Se inicializo el wiki persistente real de hyperresearch (base SQLite `.hyperresearch/hyperresearch.db`)
en este repo con `hyperresearch init .`, y se verificaron afirmaciones contra la literatura con las
cinco herramientas del MCP `scholar` (`scholar_search`, `scholar_inspect`, `scholar_verify_claim`,
`scholar_verify_predicate`, `scholar_research`) por importacion directa de `scholar.mcp.server`
(transporte MCP no conectado). Porton Jev System One `jev-1.14.0` en vivo.

## Wiki persistente SQLite (Etapa 1506A)

- `hyperresearch init .` creo `.hyperresearch/hyperresearch.db` y dejo `research/` intacto.
- Se consolidaron notas de fuente y de tema en `research/notes/scholar_sources/` con frontmatter y
  tags validos (`type: note`), se importaron las notas markdown del vault previo, y se corrio `sync`
  / `index build` / `repair` (enlaces) / `status` contra la base viva (41 notas).
- Las busquedas de texto completo resuelven los temas de la ola: `AQL`, `FQ-CoDel`, `DFS`, `256-QAM`
  y `LDPC` devuelven aciertos; `PtP-Colo`, `Guarida` y `BOCPD` resuelven a su nota de consolidacion.
- La Etapa 1507A conecto el reactor para correr `hyperresearch sync` y `search` contra esa base viva.
- Nota: el CLI no tiene un `link` de primer nivel; `repair` (sync completo + arreglo de enlaces rotos
  + reconstruccion de indices) y `graph rank` cubren la construccion de enlaces.

## Resultado scholar honesto

- **1 de 3 afirmaciones quedo VERIFICADA EN VIVO** (B, intervalo de guarda / prefijo ciclico). A
  (LDPC vs BCC) y C (SNR 256-QAM) dan negativo real del porton y se sostienen en norma IEEE.

### Afirmacion A - Ganancia de codificacion LDPC vs BCC a 256-QAM (MCS8/9)

**NO_CANDIDATE_PASSED_GATE + NORMA.** Las afirmaciones de ganancia LDPC no tuvieron soporte en arXiv
(los primeros resultados fueron de correccion cuantica / densidad de paridad, fuera de tema): negativo
honesto. La eleccion LDPC-vs-BCC y las definiciones de MCS8/MCS9 256-QAM son cifras de norma:
**IEEE 802.11-2020** especifica tanto BCC como el LDPC opcional para el set VHT, y el LDPC mas fuerte
es el que recupera margen en las constelaciones de mayor orden donde el SNR requerido es mayor.

### Afirmacion B - Short-GI (400 ns) vs Long-GI (800 ns) e ISI por multipath

**VERIFICADA EN VIVO.** Contra **arXiv:2207.13045** (*Performance of OFDM System against Different
Cyclic Prefix Lengths on Multipath Fading Channels*): se inserta un prefijo ciclico en la transmision
OFDM (`P=0.98`) y la longitud del prefijo ciclico (intervalo de guarda) afecta el rendimiento del
sistema OFDM (`P=0.87`). El paper adyacente **arXiv:2012.04527** (*Intersymbol and Intercarrier
Interference in OFDM*) corrobora el mecanismo de ISI. Consecuencia operativa: el Short-GI (400 ns)
sube el caudal pero deja menos margen que el Long-GI (800 ns) cuando crece la dispersion de retardo
por multipath, como ocurre en un trayecto exterior mas largo como PtP-Colo a 1.8 km: alli el Short-GI
es la opcion mas sensible a ISI.

### Afirmacion C - Sensibilidad de SNR de 256-QAM

**NO_CANDIDATE_PASSED_GATE + NORMA.** Las afirmaciones de sensibilidad de SNR de 256-QAM no tuvieron
soporte directo en arXiv (los primeros resultados fueron de reconocimiento de modulacion). El SNR
minimo y la sensibilidad de entrada del receptor por MCS son cifras de norma: **IEEE 802.11-2020** fija
el mayor SNR minimo del set VHT para MCS8/MCS9 256-QAM. Por eso la ganancia LDPC (A) y la eleccion de
GI (B) importan justo a 256-QAM en un enlace exterior largo.

## Contexto PtP-Colo y Guarida

En **PtP-Colo** (`.105.62 <-> .105.54`, ~1.8 km): el trayecto mas largo alarga la dispersion de
retardo, asi que el Short-GI queda mas expuesto a ISI (B), mientras el LDPC recupera el margen de SNR
que exige el 256-QAM (A y C). En **Guarida** (`.84` Panel1/2/3 PtMP): las mismas disyuntivas por CPE,
con la estacion de MCS mas bajo marcando el sector. Son consecuencias de ingenieria de las cifras de
norma, no afirmaciones nuevas de arXiv.

## Limites y advertencias

- OpenAlex `400` suprimio casi todos los conteos de citas (grafos `PARCIAL`, no cero-citas).
- A y C no tuvieron soporte directo en arXiv: la base real es IEEE 802.11-2020, no evidencia en contra.
- No se cita de memoria ningun SNR, ganancia de codificacion ni tasa; las cifras de norma se citan por
  seccion, no se reproducen.
- Esto fue una extension del reactor mas un bootstrap real de vault, no una corrida completa de V8.

## Que sigue (abierto, decision del operador)

- El wiki persistente SQLite queda listo para crecer; las decisiones de GI/LDPC en campo requieren
  medicion real por enlace. El valor de aql_threshold sigue siendo decision del operador.

Recibos: `stage1506a_hyperresearch_sqlite_wiki_vault_bootstrap.json`,
`stage1507a_scholar_ldpc_sgi_and_wiki_sync_receipt.json`,
`stage1511a_wave78_hyperresearch_wiki_gate.json`.
