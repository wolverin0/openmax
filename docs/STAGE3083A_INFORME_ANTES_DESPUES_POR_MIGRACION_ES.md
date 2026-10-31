<!-- doc-head: Stage 3083A (W423) ES: informe automatico antes/despues por migracion desde telemetry.db (sidecar origin=core, despues office, despues colector; nunca mezcla origenes), ventanas de 1 h en las mismas horas ART 24-72 h a cada lado, banda A/A del propio equipo y veredicto GO, ROLLBACK o NO_VERDICT; CLI + HTML; sobre el cambio historico stock a OpenWrt de la Guarida da NO_VERDICT en los 18 nodos porque la base no tiene el lado stock -->
Que cubre: que mide el informe, como decide, como se corre y que dio sobre la Guarida.
Estado: solo lectura sobre telemetry.db. 0 escrituras en equipos. Tests: 11 passed in 1.36s.
Codigo: tools/observability/before_after_report/ (report.py, __main__.py). Informes: docs/STAGE3083A_INFORME_GUARIDA_24H.html y _72H.html, JSON al lado.
Leer cuando: despues de cada migracion o cambio de perfil, para decidir GO o ROLLBACK con datos.
<!-- /doc-head -->
# Stage 3083A: informe antes/despues por migracion (W423)

## 1. Uso

`python -m tools.observability.before_after_report --node panel2_ap --change 2026-11-02T15:00Z --hours 24 --html informe.html --json informe.json`
- Varios pares `--node/--change` en un solo informe. `--hours` de 24 a 72.

## 2. Que compara

- **Ventanas:** de 1 h. H horas antes del cambio y H horas despues de 1 h de asentamiento (deja fuera el cambio mismo).
- **Mismas horas:** solo las horas del dia (ART) presentes en los dos lados.
- **Metricas:**
  - Latencia p50, p95 y p99, y perdida. Fuente: la primera que cubra los dos lados entre sidecar origin=core, sidecar origin=office y el ICMP del colector. La misma fuente en los dos lados.
  - Goodput proxy: mediana de la tasa PHY tx/rx de las estaciones. Es tasa de enlace, no trafico medido.
  - Reintentos y TX fallidos por hora, con deltas entre muestras consecutivas del mismo arranque. Un reinicio se saltea.
  - Drops `fq_overmemory` por hora (delta del colector).
  - Reclamos por cliente del nodo o su celda, por dia.

## 3. Como decide

- **Banda A/A** (metodo W388 del plan de rollout): por corrida y por equipo, con las ventanas de antes, cuantiles tipo 7. q0,995 donde mas alto es peor y q0,005 para goodput.
- **ROLLBACK:** la mediana de despues de una metrica primaria (p95, p99, perdida, goodput, drops fq) sale de la banda hacia el lado malo, o suben los reclamos por cliente.
- **GO:** todas las primarias con datos en los dos lados quedan dentro de la banda, con latencia o perdida medida.
- **NO_VERDICT:** menos de 12 ventanas por lado en latencia o perdida. Muestra la cobertura de cada fuente.
- El minimo de 12 ventanas y la hora de asentamiento son decisiones de diseno, no umbrales medidos. La mediana contra q0,995 es indulgente a proposito: pocos falsos ROLLBACK.

## 4. Guarida, cambio stock a OpenWrt (cortes de W377)

| Nodo | 24 h | Ventanas antes (24 h) | (72 h) | Plataforma antes |
| :-- | :-- | --: | --: | :-- |
| panel1_ap | NO_VERDICT | 0 | 0 | - |
| panel2_ap | NO_VERDICT | 2 | 2 | airOS |
| panel3_ap | NO_VERDICT | 0 | 0 | - |
| ptp_colo_ap | NO_VERDICT | 2 | 2 | airOS |
| ptp_colo_sta | NO_VERDICT | 2 | 2 | airOS |
| cpe_200_41 | NO_VERDICT | 0 | 0 | - |
| cpe_200_223 | NO_VERDICT | 0 | 0 | - |
| cpe_200_80 | NO_VERDICT | 4 | 4 | NOT_OPENWRT |
| cpe_210_9 | NO_VERDICT | 0 | 0 | - |
| cpe_210_235 | NO_VERDICT | 0 | 0 | - |
| cpe_210_238 | NO_VERDICT | 0 | 0 | - |
| cpe_200_213 | NO_VERDICT | 0 | 0 | airOS |
| cpe_210_166 | NO_VERDICT | 0 | 0 | airOS |
| cpe_200_169 | NO_VERDICT | 0 | 0 | airOS |
| cpe_210_239 | NO_VERDICT | 0 | 0 | airOS |
| cpe_200_183 | NO_VERDICT | 0 | 0 | airOS |
| cpe_210_21 | NO_VERDICT | 0 | 0 | airOS |
| cpe_210_83 | NO_VERDICT | 0 | 0 | airOS |

- **CONFIRMED:** NO_VERDICT en los 18 nodos, con 24 y con 72 h. telemetry.db tiene a lo sumo 2 h de muestras stock antes del corte (la ultima lectura airOS minutos antes). Panel1 corto el 23/10, antes de que el colector juntara datos continuos.
- El antes stock de la Guarida solo existe en UISP (W377), con otra sonda. Este informe no lo mezcla.
- **Placebo con datos reales** (cambio ficticio 29/10 15:00 UTC, 10 nodos densos): horas comunes cpe_200_223 8, cpe_200_41 8, cpe_210_238 8, cpe_210_235 8, panel1_ap 7, panel3_ap 8, ptp_colo_ap 5, ptp_colo_sta 5, cpe_200_183 4, cpe_210_83 4. Hay un hueco del colector del 29/10 01:00 al 15:00 UTC. Ninguno llega a 12, ningun veredicto: el informe no inventa.
- **INFERRED:** el primer cambio con 24 h de origin=core en los dos lados es uno hecho despues del 31/10 a las 17 UTC (el sidecar mide desde el core desde el 30/10 17:06).

## 5. Pruebas

- Base sintetica: sin cambio GO; latencia x3 ROLLBACK; perdida ROLLBACK; reclamos por cliente arriba ROLLBACK; sin lado antes NO_VERDICT.
- Tambien prueba que nunca mezcla origenes entre lados, que compara solo las mismas horas, que un reinicio no da reintentos negativos y que CLI y HTML funcionan.
- Karpathy: colector vivo True (ultima muestra hace 0.0 min), nodos desde el core en 10 min 72, filas delta 435: PASS.
