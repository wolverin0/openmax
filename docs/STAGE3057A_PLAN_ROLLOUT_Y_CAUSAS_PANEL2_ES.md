<!-- doc-head: Stage 3057A (W397) ES: plan de rollout del campeon v2 actualizado a la politica del operador del 30/10 y ranking de causas del salto de radio de 40 ms de Panel2 con telemetria de solo lectura. Causa 1 (INFERRED): la subida de Panel2 quema aire a MCS 0-1 con muchos reintentos; el canal del AP esta ocupado 77 % con solo 4 Mbit/s de trafico. Incluye el A/B de banco que probaria el mecanismo -->
Que cubre: que cambio en el plan de rollout y por que, y las causas ordenadas de la latencia de Panel2 con su evidencia.
Estado: solo docs y telemetria en modo ro (daemon y sidecar_e2e). 0 accesos a equipos.
Datos maquina: artifacts/autoresearch/wave397_panel2_causes.json. Plan: docs/PLAN_ROLLOUT_CAMPEON_V2_ES.md.
Leer cuando: antes de ejecutar el rollout del campeon v2 o de probar una mejora para Panel2.
<!-- /doc-head -->
# Stage 3057A: plan de rollout y causas de Panel2 (W397)

## 1. Cambios en el plan de rollout

- **Alcance:** 1 PtP (PtP-Colo) y los 3 paneles de menos de 15 clientes.
- **Ritmo:** cualquier hora, lo mas rapido posible; sin ventana valle ni un nodo por noche.
- **Precondicion:** gate PASS de banco del cambio exacto.
- **Aborto:** fuera de la banda A/A del mismo equipo medida en la misma corrida (metodo W388), en vez de porcentajes fijos.
- **Memoria:** se quito el piso de 5120 kB. W379 no califico ningun piso; se aborta por OOM nuevo o reinicio.
- **Monitoreo:** daemon before/after y sidecar_e2e (W393).

## 2. Evidencia de Panel2 (MEASURED, solo lectura)

| Celda | Canal ocupado | Trafico del sector (mediana) | Subida de las CPE | p50 E2E de las CPE |
| :-- | --: | --: | :-- | :-- |
| Panel1 | 14,7 % | 2,8 Mbit/s | MCS 4 en las 3 | 13-14 ms |
| Panel2 | 76,8 % | 4,1 Mbit/s | MCS 0-1 en 4 de 7 | 37-65 ms |
| Panel3 | 53,6 % | 0,3 Mbit/s | MCS 3-4, cpe_210_9 en 0 | 23-50 ms |

- **Reintentos de subida:** 15 000 a 54 000 por hora en 5 CPE de Panel2, contra 800 a 3200 en Panel1.
- **Bajada:** las CPE cercanas de Panel2 bajan en MCS 6-8 con senal de unos -50 dBm. La asimetria apunta a la recepcion del AP.
- **Trafico propio:** el p95 por minuto casi no sigue al trafico de cada CPE (rho -0,2 a 0,3).

## 3. Causas ordenadas

1. **Aire quemado en una subida lenta (INFERRED).** MCS 0-1 con muchos reintentos llena el canal con poco trafico, y cada trama espera detras de esas.
2. **Estaciones lejanas en MCS 0 (INFERRED).** cpe_210_21 y cpe_200_169, a mas de 2 km, fallan mas de 30 000 veces por hora y tienen p95 de 300-350 ms. Suman, pero no explican el sector solas.
3. **Aire ajeno o ruido en la torre (UNKNOWN).** El survey acumulado no separa aire propio de ajeno.
4. **Cola AQL del AP (UNKNOWN).** Con carga baja no es la principal; `aql_pending_us` no se pudo leer.
5. **Retardo por distancia (REFUTED).** 3 km son unos 10 us frente a 40 ms.

## 4. Prueba de banco para la causa 1

- **Montaje:** LAP-120 .20 con la Loco .250 (OpenWrt) y el Rocket .198 (airOS stock). No usa .241/.242.
- **A:** control de tasa normal. **B:** la Loco fija en MCS 0-1 en su subida, solo en RAM, con carga baja.
- **Medir:** RTT p50/p95 de la estacion rapida, canal ocupado del AP, tx/rx duration por estacion y goodput agregado.
- **Veredicto:** B fuera de la banda A/A del mismo equipo en la misma corrida. Si la causa 1 es cierta, la estacion rapida pasa a decenas de ms con poco trafico total.
- **Lectura en produccion, despues:** delta de tx/rx duration por estacion y de survey en Panel2 durante 10 min, para separar aire propio de ajeno (causa 3).

## 5. Limites y contrato

- El sidecar tiene menos de 1 h de minutos. Los reintentos son conteos por hora, no tasas.
- **Karpathy: TARGET_NOT_MET.** Admitter de Panel3 UNKNOWN (sin SSH), tx_failed de cpe_210_9 sin linea de base, fq_overmemory de panel3_ap 2030 en la ultima hora.
