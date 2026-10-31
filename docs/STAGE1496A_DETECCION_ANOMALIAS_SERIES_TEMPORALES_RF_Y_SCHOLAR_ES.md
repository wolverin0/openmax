<!-- doc-head: Wave 76 (1494A-1499A) sintesis ES: scholar cambio de regimen y adaptacion de tasa + regla aeon de 3 compuertas sostenidas (cero falsos positivos en fixtures) para observabilidad RF WISP, 100% offline -->
# Reporte ejecutivo - deteccion de anomalias en series temporales RF y scholar

**Wave 76 - Etapas 1494A-1496A - 2026-10-27 - 100% offline (0 SSH, 0 escritura a radios).**

## Que se hizo

Se verificaron afirmaciones contra la literatura con las cinco herramientas del MCP `scholar`
(`scholar_search`, `scholar_inspect`, `scholar_verify_claim`, `scholar_verify_predicate`,
`scholar_research`) por importacion directa de `scholar.mcp.server` (transporte MCP no conectado).
Porton Jev System One `jev-1.14.0` en vivo. Candidatos de arXiv; citas de OpenAlex (frecuente `400`,
grafos `PARCIAL`). Cada afirmacion es atomica y, con paper canonico, usa las palabras de su resumen.
Ademas se construyo y evaluo una regla de 3 compuertas sostenidas para observabilidad RF.

## Resultado honesto

- **2 de 3 afirmaciones quedaron VERIFICADAS EN VIVO** (A cambio de regimen, B adaptacion de tasa).
  La C (correlacion de alarmas) da negativo real del porton y se sostiene en practica operativa.

### Afirmacion A - Deteccion de cambio de regimen / anomalias en telemetria

**VERIFICADA EN VIVO.** Contra **arXiv:0710.3742** (Adams y MacKay, *Bayesian Online Changepoint
Detection*), el paper canonico: la deteccion de cambio identifica puntos donde cambian los parametros
generativos de una secuencia (`P=0.79`), un algoritmo en linea detecta cambios a medida que llegan
los datos (`P=0.68`) y el modelo detecta cambios en la distribucion subyacente (`P=0.67`). Ese es el
mecanismo para distinguir un cambio de regimen sostenido de RSSI/SNR/MCS (degradacion persistente) de
un desvanecimiento transitorio: una prueba de cambio / ventana sostenida reacciona a un salto de
nivel, un valor atipico de una sola muestra no se acumula.

### Afirmacion B - Adaptacion de tasa IEEE 802.11 bajo perdida e interferencia

**VERIFICADA EN VIVO + NON_ARXIV_REFERENCE.** Contra **arXiv:1609.09726** (*Revisiting 802.11 Rate
Adaptation from Energy Consumption*): un algoritmo de adaptacion elige la tasa 802.11 segun las
condiciones del canal (`P=0.72`) y responde al cambio de calidad de enlace (`P=0.57`). Minstrel /
Minstrel-HT es un algoritmo del kernel Linux (`rc80211_minstrel_ht`); su descripcion canonica es el
codigo del kernel y la documentacion de Linux-wireless (`NON_ARXIV_REFERENCE`), no un paper de arXiv,
asi que la evidencia soporta el principio de adaptacion de tasa, no la implementacion exacta.

### Afirmacion C - Correlacion de alarmas y filtrado por ventana sostenida

**NO_CANDIDATE_PASSED_GATE + GATE_RELEVANT.** Las afirmaciones de correlacion de alarmas no tuvieron
soporte directo en arXiv; el porton trajo **arXiv:2607.17336** (*When Drift Detectors cry Wolf: False
Alarm Rates ...*), topicamente adyacente (tasas de falsa alarma en deteccion de deriva) pero sin
soporte directo. La correlacion multi-condicion y la confirmacion por ventana sostenida son practica
operativa de monitoreo, no un resultado de arXiv; se aplican directo en la regla de la Etapa 1495A.

## Regla aeon y evaluacion de cero falsos positivos (Pillar D)

aeon no esta instalado, asi que la metodologia de cambio / ventana sostenida se implementa con stdlib
(un CUSUM de una cola mas una regla de 3 compuertas) y se cita aeon como libreria de referencia.

**Regla de 3 compuertas sostenidas.** Una alarma se dispara solo cuando las tres compuertas se
cumplen por `W=2` sondeos consecutivos (confirmacion AP-local de 2 rondas): delta-RSSI menor o igual
a `-6 dB`, caida de MCS de al menos `2` pasos, y PER (o reintentos TX) mayor o igual a `10%`. La
corroboracion entre tres metricas independientes mas una ventana sostenida suprime los picos
transitorios de una sola metrica que causan falsos positivos. Los umbrales son valores modelados, no
calibrados en campo.

**Evaluacion en fixtures SIMULADOS etiquetados** (sin telemetria en vivo, sin lectura de dispositivo):

| Fixture | Espera alarma | Alarma | Correcto |
|---|---|---|---|
| S1 fade transitorio (bajada RSSI 1 sondeo) | no | no | si |
| S2 pico PER de una metrica | no | no | si |
| S3 degradacion sostenida 3 compuertas | si | si | si |
| S4 dos de tres compuertas | no | no | si |

Matriz en fixtures: TP=1, FP=0, FN=0, TN=3 - cero falsos positivos y cero omisiones en estos casos.
El CUSUM marca el salto de nivel persistente de RSSI en S3 e ignora la bajada de un sondeo de S1.

**Escenarios de enlace.** PtP-Colo (`.105.62 <-> .105.54`, PtP) y Guarida Panel1/2/3 (`.84`, PtMP)
sondean RSSI, MCS y PER/reintentos; la regla exige corroboracion de 3 compuertas por enlace (o por
CPE) sostenida por `W` sondeos antes de alertar. La regla es solo-recomendacion y no autoriza ninguna
accion en el dispositivo; el cero falsos positivos es en fixtures, no en campo.

## Limites y advertencias

- OpenAlex `400` suprimio casi todos los conteos de citas (grafos `PARCIAL`, no cero-citas).
- La C no tuvo soporte directo en arXiv: negativo real del porton, con base en practica operativa.
- El cero falsos positivos es sobre cuatro fixtures etiquetados, no datos de campo; la validacion de
  campo necesita telemetria real y un set de umbrales calibrado.
- aeon no esta instalado; la logica CUSUM/ventana sostenida es un sustituto stdlib de su metodologia.
- Esto fue una extension del reactor, no una corrida completa de HYPERRESEARCH V8 (Etapa 1495A).

## Que sigue (abierto, decision del operador)

- Validar la regla con telemetria real de PtP-Colo y Guarida y calibrar los umbrales; no se corre
  nada en vivo aqui. El valor de aql_threshold sigue siendo decision del operador.

Recibos: `stage1494a_scholar_mcp_rf_timeseries_anomaly_ledger.json`,
`stage1495a_aeon_timeseries_rf_observability_receipt.json`,
`stage1499a_wave76_hyperresearch_scholar_gate.json`.
