<!-- doc-head: Stage 3072A (W412) ES: tabla de candidatos a migrar a OpenWrt en toda la red dentro del alcance del operador (1 PtP + paneles de menos de 15 clientes), con modelo, firmware, clientes, latencia del sidecar, uso de bajada, reclamos por cliente y la prueba de banco que falta por candidato. Primero: panel panel1_baigorria y PtP c44af853 -->
Que cubre: de donde sale cada columna, como se ordena y que prueba falta en cada candidato.
Estado: solo lectura (UISP del 30/10, sidecar_e2e y reclamos). 0 escrituras.
Datos maquina: artifacts/autoresearch/wave412_candidates.json. Informe: artifacts/2026-10-30-candidatos-migracion.html.
Leer cuando: antes de elegir el proximo panel o PtP a migrar.
<!-- /doc-head -->
# Stage 3072A: candidatos de migracion (W412)

## 1. Fuentes

- **UISP** (GET del 30/10): modelo, firmware, clientes del AP, modelos de CPE y uso de bajada y subida.
- **Sidecar:** p50/p95/p99 y perdida desde las 15:54 UTC; para los nodos nuevos son pocos minutos.
- **Reclamos:** 30 dias por sector, con el cliente como hash.
- **Retries y airtime por estacion:** solo existen en Guarida; fuera de Guarida se usa el uso de UISP.

## 2. Orden

- Primero el hardware con OpenWrt ya probado: LAP-120 (banco .20 y 3 paneles de Guarida) y LBE-5AC-Gen2 en PtP (PtP-Colo).
- Dentro: reclamos por cliente, p95, perdida y uso de bajada.
- Sin OpenWrt probado: Rocket Prism 5AC (espejo .198 en airOS), LAP-GPS y PrismStation (sin espejo), PBE-5AC (falta el PtP OpenWrt en .241/.242) y LTU (sin OpenWrt).

## 3. Resultado

- Paneles en alcance: 14; el primero es panel1_baigorria (LAP-120, 13 clientes).
- PtP: 13; el primero es c44af853 (LBE-5AC-Gen2).
- Cada candidato lista lo que falta; en todos falta el gate PASS de banco del cambio exacto, que es la precondicion del plan.
