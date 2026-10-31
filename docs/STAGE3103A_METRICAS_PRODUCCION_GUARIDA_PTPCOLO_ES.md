<!-- doc-head: Stage 3103A (W433 paralelo, W443) ES: metricas de produccion antes y despues para Guarida y PtP-Colo, solo lectura; antes = UISP API publica (7 dias, cubetas de 2 h), despues = sidecar core y colector, comparacion cruzada INFERRED; salto RF (CPE menos su AP) mejora en Panel1, empeora en las 7 CPE de Panel2 y en la lejana de Panel3; ningun nodo CONFIRMED -->
Que cubre: fuentes, metodo, resultado por celda, limites y que falta para CONFIRMED.
Estado: INFERRED en los 18 nodos; CONFIRMED en ninguno.
Datos: artifacts/observability/wave443_prod_metrics.json. Vista: artifacts/2026-10-31-metricas-produccion-guarida-ptpcolo.html. Generador: artifacts/observability/wave443_build.py.
Leer cuando: antes de decidir sobre Panel2 o de afirmar mejoras por la migracion.
<!-- /doc-head -->
# Stage 3103A: metricas de produccion antes y despues (W443)

## 1. Fuentes

- **Antes:** UISP API publica v2.1, `GET /devices/{id}/statistics?interval=month`. Son cubetas de 2 h; se toman los 7 dias previos a cada migracion. Sin debug API, sin escrituras.
- **Despues, mismo campo:** UISP, solo donde el puente FMX publica. Hay datos de ping y link score para la celda de Panel1 y, a ratos, Panel3; en el resto, 0 puntos. Es otro productor, asi que va como INFERRED.
- **Despues, otro instrumento:** sidecar core del RB1100 (desde 30/10) y daemon colector (telemetry.db).
- **Reclamos:** tabla diaria de telemetry.db por celda.
- **Monitor de 72 h de Panel1:** empezo despues de su migracion (23/10 22:01Z), asi que no sirve como antes.

## 2. Metodo

- **Comparacion directa:** p50 antes contra p50 despues de cada campo, con al menos 12 puntos por lado.
- **Salto RF:** p50 de la CPE menos p50 de su AP, calculado dentro de un mismo instrumento en cada lado. Asi se cancela el camino comun hasta el AP, que es lo que cambio de instrumento. Sigue siendo INFERRED: cambian el origen (NMS o RB1100) y la cubeta (2 h o 1 min).

## 3. Resultado (salto RF p50 en ms)

| Nodo | Celda | Antes (UISP) | Despues (core) | Delta | Perdida core % |
| :-- | :-- | --: | --: | --: | --: |
| cpe_200_41 | panel1 | 5,8 | -0,2 | -6,0 | 2,9 |
| cpe_200_223 | panel1 | 5,2 | 2,2 | -3,0 | 3,5 |
| cpe_200_80 | panel1 | 12,3 | 4,1 | -8,2 | 24,3 |
| cpe_210_9 | panel3 | 3,0 | 24,0 | 21,0 | 10,3 |
| cpe_210_235 | panel3 | 3,7 | 6,6 | 2,8 | 2,4 |
| cpe_210_238 | panel3 | 3,7 | 9,2 | 5,5 | 1,9 |
| cpe_200_213 | panel2 | 12,6 | 31,4 | 18,7 | 3,8 |
| cpe_210_166 | panel2 | 12,1 | 25,8 | 13,7 | 2,5 |
| cpe_200_169 | panel2 | 16,7 | 76,8 | 60,1 | 26,2 |
| cpe_210_239 | panel2 | 11,6 | 24,7 | 13,2 | 3,6 |
| cpe_200_183 | panel2 | 11,1 | 26,5 | 15,5 | 8,2 |
| cpe_210_21 | panel2 | 14,0 | 46,1 | 32,1 | 14,8 |
| cpe_210_83 | panel2 | 12,2 | 28,2 | 16,0 | 5,4 |

- **Panel1:** mejora de 3 a 9 ms.
- **Panel2:** empeora en las 7 CPE, de +13 a +61 ms. Pasa tambien en CPE con buena senal (cpe_210_239 en -45 dBm antes): no es solo distancia (INFERRED).
- **Panel3:** las cercanas suben 3 y 5 ms; la lejana, 21 ms.
- **Lejanas:** cpe_200_169, cpe_210_21 y cpe_210_9 concentran las fallas por hora y la perdida. Coincide con el ACK timeout de clase 0 de W431.
- **Senal, MCS y capacidad despues:** UNKNOWN. El puente no publica esos campos.
- **Reclamos:** pocos en ambos lados, sin senal util.

## 4. Que falta para CONFIRMED

- **El antes no se puede rehacer** con el sidecar, que empezo el 30/10.
- **Banda A/A del despues:** 7 dias de sidecar core la fijan.
- **CONFIRMED** pide una ventana de vuelta atras A/B en una celda, o una celda testigo en stock medida con el mismo sidecar.
- **Panel2** es la candidata a mirar primero.
