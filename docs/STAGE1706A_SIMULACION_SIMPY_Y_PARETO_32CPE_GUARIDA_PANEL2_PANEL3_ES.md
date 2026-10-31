<!-- doc-head -->
*STAGE1706A — simulación de doble bind y horario Pareto para los 28 CPE de Guarida (Paneles 2 y 3)*
# STAGE 1706A — Doble bind y horario Pareto

## 0. Frontera
- **100% offline**: `ssh_connections=0`, `radio_writes=0` en ambos recibos.
- Todo lo cuantitativo es **modelo**, no medida. Los parámetros son supuestos etiquetados.

## 1. Stage 1704A — simulación de eventos
- `CONFIRMED`: SimPy está importable, pero el modelo ejecutado es un **bucle determinista propio** con semilla `20261028`; el recibo lo declara así.
- `CONFIRMED`: **28 CPEs** simulados en 6 h: **Panel 3 = 6**, **Panel 2 = 22**.
- `CONFIRMED`: **9 fallos de doble bind**, de los que **6 se recuperan** dentro de la ventana y **3 quedan atascados** pese al healer con `ban_time=1200`.
- `CONFIRMED`: Panel 3 aporta **1** fallo (utilización `0.6673`, p95 `42.07 ms`); Panel 2 aporta **8** (utilización `0.9583`, p95 `113.11 ms`).
- `CONFIRMED`: `wpa_group_rekey=86400` genera **6** eventos de rekey en la ventana simulada.
- `INFERRED`: el Panel 2 está mucho más cerca de la saturación por aire; el doble bind duele más allí porque la recuperación compite con una utilización del 96 %.
- `UNKNOWN`: la tasa real de doble bind. El modelo no la prueba.

## 2. Stage 1705A — horario Pareto
- `CONFIRMED`: pymoo está importable, pero se usa un **NSGA-II propio** (ordenamiento no dominado rápido + distancia de congestión), población 40, 25 generaciones, semilla `20261028`.
- `CONFIRMED`: frentes de **40** individuos en cada panel, es decir que con estas funciones objetivo casi toda la población resulta no dominada.
- `CONFIRMED`: rodilla del Panel 3: ventana **0.375 h**, **2.0** fallos esperados, capacidad **909.2 Mbps**, `aql=1`, `atf` y `quantum` según el recibo.
- `INFERRED`: el frente es plano porque las tres funciones no se oponen con fuerza; la rodilla es una **propuesta**, no una jerarquía.
- `UNKNOWN`: la capacidad real post-migración.

## 3. Lo que no se prueba
- `UNKNOWN`: la tasa de doble bind en producción y la eficacia real del healer en Panel 2/3.
- `UNKNOWN`: que la secuencia propuesta reduzca el riesgo medido.
- `UNKNOWN`: cualquier cifra de capacidad o latencia fuera del modelo.

## 4. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1704A` | `tools/sim/run_stage1704a_guarida_32cpe_dualbind_and_airtime_simpy.py` + recibo |
| `1705A` | `tools/autoresearch/run_stage1705a_guarida_panel2_panel3_pareto_schedule.py` + recibo |
| `1706A` | este documento (menos de 150 líneas, 1 `doc-head`, 0 signos de exclamación en prosa) |
| `1707A..1709A` | filas en `results.tsv`, `tests/test_stage1704a_to_1709a_suite.py` y la compuerta de la wave |
