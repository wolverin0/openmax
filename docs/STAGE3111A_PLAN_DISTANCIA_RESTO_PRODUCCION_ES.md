<!-- doc-head: Stage 3111A (W451) ES: plan de distancia / ACK timeout para los nodos OpenWrt de produccion que quedan (Panel1 AP y 3 CPE, cercanas de Panel2 y Panel3, PtP-Colo 450 m), solo lectura de recibos W431/W433/W443/W447/W448; conclusion: no queda ninguna CPE lejana sin corregir, el beneficio esperado es bajo, un solo candidato condicional (cpe_210_83) y el resto verificar en lectura -->
Que cubre: fuentes de distancia, clase actual, si hace falta cambio, uci exacto, orden por beneficio y riesgo de subir el AP.
Estado: PLAN (0 escrituras, 0 SSH; nada aplicado). Datos: artifacts/autoresearch/wave431_h2_h4.json, wave433_panel3_distance.json, wave447_panel2_regression.json, wave448_panel3_distance_rerun.json, artifacts/observability/wave443_prod_metrics.json.
Leer cuando: antes de tocar `distance` en cualquier nodo que no sea Panel2/Panel3 ya persistido.
<!-- /doc-head -->
# Stage 3111A: plan de distancia para el resto de produccion

## 1. Regla y base de calculo

- **Clase = ceil(distancia/450 m) (INFERRED):** 3 puntos persistidos: 2250 m clase 5, 2700 m clase 6 (cubre 2700), 2850 m clase 7 (cubre 3150) (wave447 persist, wave431 h2_canary.class_covers_m). Verificar con readback en cada nodo.
- **Frontera de clase 0 (INFERRED, wave431 labels):** sano hasta ~1,2 km (cpe_210_235, wstalist 150-1200 m, falla/paquete 0,0 en las 7 ventanas de wave448 y en W431), falla desde ~2,0 km (cpe_200_169 1,0005 a 2250 m).
- **Fuente de distancia (orden de confianza):** airOS wstalist (MEASURED, solo existia antes de migrar) > distancia UISP `uisp_distance_m` (INFERRED) > coordenadas UISP (dos estaban mal: cpe_200_80 4404 m y cpe_200_213 6068 m contra 272 y 259 m, wave431 `uisp_coordinates_wrong`).
- **Estado de clase:** 0 en los 3 AP y todas las CPE el 30/10 (CONFIRMED, wave431 h4). Despues: Panel3 AP + cpe_210_9 en clase 7 (wave448, 02:17Z), Panel2 AP clase 6, cpe_200_169 clase 5, cpe_210_21 clase 6 (wave447, 03:50-03:59Z). Todo lo demas sigue en 0 (INFERRED: no hay escritura registrada).

## 2. Tabla por nodo (orden por beneficio esperado)

| # | Nodo | Distancia y fuente | Clase hoy | Falla/paquete a clase 0 | Cambio? | uci exacto / clase | Beneficio |
| :-- | :-- | :-- | --: | :-- | :-- | :-- | :-- |
| 1 | cpe_210_83 (Panel2, cercana) | wstalist 450 m; UISP 578 m (MEASURED/INFERRED) | 0 | subida 0,0363 en W431 (la mas alta de las cercanas); bajada 0,0; collector 5793 fallas/h p50 | CONDICIONAL: solo si una lectura nueva, con el AP ya en clase 6, sigue con subida > 0,01 | `wireless.radio0.distance=600` (clase 2, 900 m) | Bajo a moderado. Con AP en clase 6 sus B1/B2 de W447 ya mejoraron (p95 54,3 / 46,7 ms contra A 71,6-90,8). |
| 2 | cpe_200_80 (Panel1) | UISP distancia 272 m (INFERRED); coordenadas 4404 m = error | 0 | bajada 0,0015; subida 0,0 | NO. Otra causa: perdida core 24,28 % en sidecar (p95 39,2 ms) contra 1,1 % del collector; UNKNOWN; reflasheada 28/10 23:02Z | ninguno | Ninguno por distancia |
| 3 | cpe_200_183 (Panel2) | wstalist 300 m; UISP 578 m | 0 | subida 0,0049 | NO | ninguno | Nulo (B1/B2 W447: 0,001 / 0,0) |
| 4 | cpe_210_166 (Panel2) | wstalist 600 m; UISP 578 m | 0 | subida 0,0023 | NO | ninguno | Nulo |
| 5 | cpe_210_239 (Panel2) | wstalist 300-450 m | 0 | subida 0,0014 | NO | ninguno | Nulo |
| 6 | cpe_200_213 (Panel2) | wstalist 300 m; UISP 259 m (coordenadas 6068 m = error) | 0 | bajada 0,0003 | NO | ninguno | Nulo |
| 7 | cpe_210_238 (Panel3) | wstalist 600-900 m | 0 | 0,0 en B1/B2; 8 de 58 mil en A/A | NO | ninguno | Nulo (su p95 bajo de 37-61 a 21-28 ms por el cambio del AP) |
| 8 | cpe_210_235 (Panel3) | wstalist 150-1200 m | 0 | 0,0 en todas las ventanas de W448; collector 116 fallas/h | NO | ninguno | Nulo |
| 9 | cpe_200_41 (Panel1) | UISP 1139 m (INFERRED) | 0 | bajada 0,0; subida 0,0; MCS 8 | NO (1,14 km esta en el borde sano de ~1,2 km) | ninguno; si apareciera falla > 0,01, `distance=1200` = clase 3 | Nulo hoy |
| 10 | Panel1 AP (LAP-120) | max CPE 1139 m | 0 | collector tx_failed 0/h p50 | NO | ninguno | Nulo; ver riesgo de la seccion 3 |
| 11 | cpe_200_223 (Panel1) | UISP 9 m | 0 | 0,0 | NO | ninguno | Nulo |
| 12 | PtP-Colo .62/.54 | 450 m (OPERATOR, wave438; reemplaza 7 km y 1,8 km) | UNKNOWN: W431 solo leyo los 3 AP; sin `distance` en los kits champion (INFERRED 0) | collector tx_failed 0/h p50 en AP y STA | NO. A 450 m clase 0 esta lejos de la frontera de ~2 km | si se quisiera: `distance=450` = clase 1 (cubre 450 justo, sin margen) | Nulo; los retries del STA (96 645/h p50) son de aire, con fallas = 0 |

## 3. Riesgo de subir el valor del AP (mac80211)

- **Mecanica:** el coverage class del AP alarga el slot y el ACK timeout para todas sus estaciones; las cercanas pagan el aire extra aunque no lo necesiten (INFERRED, mac80211).
- **Evidencia a favor:** en W447 las 5 cercanas bajaron p95 core en B1 y B2 con el AP en clase 6, y en W448 cpe_210_238 y cpe_210_235 bajaron de 37-61 a 21-34 ms, con 0 fallas y perdida dentro de la banda.
- **Matiz:** esa mejora es INFERRED que viene de quitar las tramas fallidas de la CPE lejana (fallaban todo y ocupaban el aire de la celda), no del slot mayor. Las dos celdas tenian una CPE a 2,25-2,85 km.
- **Regla para el resto:** NO subir el AP de Panel1 (CPE max 1139 m, ninguna lejana): no hay tramas fallidas que quitar, el slot mayor seria costo puro y sin evidencia de que no dane. Solo se justifica subir un AP con una CPE medida > 1,5 km y falla/paquete > 0,5.
- **Panel2 AP ya en clase 6:** ninguna cercana necesita cambio; no bajar el AP.
- **Si se aplica #1:** el valor va en la CPE, no en el AP (que ya cubre 2700 m). El slot sube a clase 2 solo para esa CPE.

## 4. Pasos (orden)

1. **Lectura sin escritura (SSH de solo lectura, con aprobacion del orquestador):** `iw phy phy0 info | grep -i coverage` y `iw dev <if> station dump` x2 en cpe_210_83, cpe_200_80, Panel1 AP, PtP-Colo .62/.54. Objetivo: clase real y falla/paquete de subida y bajada.
2. **#1 solo si** la subida de cpe_210_83 es > 0,01 con paquetes suficientes (>= 500): canario A/A x3 + ABAB, regla hasheada antes, watchdog, backup `/etc/fmx_rollback/wireless.pre_w451`; persistir solo con GO.
3. **#2:** diagnostico aparte (perdida de sidecar 24 %, otra causa; no distancia).
4. **Resto:** sin cambio. Registrar la `distance` real en el inventario de nodos para evitar el default 0 silencioso.

## 5. Limites

- **UNKNOWN:** clase actual de PtP-Colo y de las CPE de los tres paneles despues de las persistencias (solo se infiere de los recibos).
- **UNKNOWN:** distancia airOS de Panel1 (migrado a OpenWrt el 23/10, sin wstalist); solo hay UISP.
- **Sin umbral inventado:** el 0,01 de subida es un disparador de lectura, no una guarda; el veredicto de #1 sale de la regla del canario.
