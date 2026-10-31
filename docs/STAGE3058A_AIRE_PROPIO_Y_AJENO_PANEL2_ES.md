<!-- doc-head: Stage 3058A (W398) ES: reparto del aire del canal de Panel2-Guarida en 10 min de lectura (survey del AP, tx duration por estacion y por CPE). Ocupado 77,5 %: bajada del AP 49,6 %, subida de las CPE medidas 8,0 %, ajeno o no decodificado 19,9 %. Corrige W397: la mayor consumidora es la bajada, no la subida -->
Que cubre: cuanto del canal usa la propia celda, cuanto es ajeno y cuanto aire usa cada CPE en subida y en bajada.
Estado: solo lectura por SSH en Panel2 (iw y survey). 0 escrituras. cpe_200_169 UNKNOWN (SSH fallo en las 6 rondas).
Datos maquina: artifacts/autoresearch/wave398_panel2_airtime.json.
Leer cuando: antes de probar cambios de tasa, agregacion o canal en Panel2.
<!-- /doc-head -->
# Stage 3058A: aire propio y ajeno en Panel2 (W398)

## 1. Canal del AP en 10 min (MEASURED, 14:52-15:02 UTC)

| Uso | % del tiempo |
| :-- | --: |
| Bajada del AP (tx del survey) | 49,6 |
| Subida de las 6 CPE medidas (tx duration de cada CPE) | 8,0 |
| Ajeno o no decodificado (ocupado menos tx y rx propios) | 19,9 |
| Libre | 22,5 |

El rx del survey (7,6 %) coincide con la subida medida, asi que el resto ocupado no son tramas de la celda.

## 2. Por CPE

| CPE | Subida % del canal | MCS sube | Parte del tx del AP % | MCS baja | us por paquete bajada | Mbit/s bajada | p50 ms |
| :-- | --: | --: | --: | --: | --: | --: | --: |
| cpe_200_213 | 4,7 | 1 | 24,5 | 7 | 1267 | 2.271 | 45.2 |
| cpe_210_166 | 1,4 | 4 | 12,3 | 8 | 1080 | 1.056 | 41.9 |
| cpe_210_239 | 0,2 | 5 | 1,9 | 8 | 319 | 0.015 | 38.3 |
| cpe_200_183 | 0,3 | 0 | 1,9 | 7 | 311 | 0.009 | 41.4 |
| cpe_210_21 | 0,6 | 0 | 1,4 | 0 | 305 | 0.005 | 93.5 |
| cpe_210_83 | 0,9 | 1 | 7,6 | 7 | 862 | 0.524 | 38.8 |

- La parte del tx del AP se escala al tx del survey: la suma cruda de tx duration por estacion da 78,7 % y supera al survey, asi que solo vale como reparto.
- **cpe_200_213** usa una cuarta parte del canal en bajada con 2,3 Mbit/s: 1267 us por paquete en MCS 7, varias veces lo esperable para ese tamano.
- cpe_210_21 falla casi todo en los dos sentidos (MCS 0), pero usa poco aire.

## 3. Que cambia

- **Correccion de W397:** la subida usa unos 8,0 % del canal. La mayor consumidora es la **bajada del AP**, sobre todo hacia cpe_200_213 y cpe_210_166, con mucho aire por paquete.
- **Aire ajeno:** unos 19,9 % del tiempo el canal esta ocupado sin tramas propias (otras redes, ruido o colisiones). Es real, pero menor que la bajada propia.
- **Siguiente prueba:** por que la bajada a cpe_200_213 gasta tanto aire por paquete (agregacion, reintentos de firmware o tasa real distinta de la reportada). En banco: misma carga hacia una estacion, comparar us por paquete con agregacion por defecto contra la del ledger.

## 4. Contrato

- **Karpathy: TARGET_NOT_MET.** Las tres metricas son de Panel3 y esta ola solo lee Panel2.
