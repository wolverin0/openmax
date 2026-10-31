<!-- doc-head: Stage 1113A resumen ejecutivo en espanol para el operador - paquete PtP v17 preparado offline NO verificado en radio, veredictos por equipo, decisiones abiertas y safety gates Guarida; BRIEF_ONLY, nada es PRODUCTION_READY -->
# Stage 1113A - Resumen ejecutivo PtP v17 y Guarida

Estado: `BRIEF_ONLY`. Dueno de la ejecucion: Codex #1 (live lane). Este documento se escribio 100% offline: no hubo SSH ni contacto con equipos.
Receipt: `artifacts/autoresearch/stage1113a_operator_executive_ptp_and_guarida_readiness_brief.json`.

## Que es y que NO es

- El paquete PtP v17 esta **preparado offline, NO verificado en radio**.
- Ningun veredicto de abajo equivale a PRODUCTION_READY. Ninguno.
- Sin evidencia controlada (A/A valido + carga fisica + procedencia) no se puede declarar mejora ni listo.

## Veredictos

| Equipo | Veredicto | Motivo |
| --- | --- | --- |
| PowerBeam PtP | NOT_READY | v17 sin canary en radio; checklist 1101A no ejecutado |
| LiteBeam PtP | NO_EVIDENCE | no hay datos propios; NO es equivalente a PowerBeam |
| Guarida Panel1 .84 | NO_CONTROLLED_EVIDENCE | solo lectura, sin control A/A |
| Guarida LTU-Lite .110 | NO_CONTROLLED_EVIDENCE | solo lectura, sin control A/A |
| Guarida Panel2 | NOT_READY | 882A: ready 0/34; 1010A no auditó Panel2 |
| Guarida Panel3 | NO_EVIDENCE | nunca medido |

## Las 4 decisiones abiertas

1. `aql_threshold` 24000 vs 12000: sin evidencia controlada que decida; no cambiar a ciegas.
2. Re-firma de `SHA256SUMS`: ahora cubierta en 1109A (las entradas nuevas quedan firmadas).
3. LiteBeam sin evidencia: hace falta sesion propia; no heredar resultados de PowerBeam.
4. Kits v17 runtime-only: se pierden al reiniciar; hay que re-aplicar u hornear tras reboot (decision del operador).

## Que debe producir Codex #1 para cambiar un veredicto

- El set de senales 1009A: `controlled_aa_valid`, `physical_workload_acceptance`, `evidence_provenance_class`.
- Salida del bundler 1073A sobre esa sesion.
- Control A/A `886A` y MDE `977A` (minimo efecto detectable) calculados sobre datos reales.
- Mientras falte cualquiera, el veredicto se mantiene; esta lane offline no puede subirlo.

## Safety gates Guarida

- SG-01: backbone PoE, 0 escrituras (solo lectura).
- SG-03..SG-05: zero-touch del lado AP, sin tocar CPE ni clientes.
- Watchdog v17: 45 s de ventana de confirmacion, 120 s de rollback automatico.

## Proximo paso

Codex #1 ejecuta el checklist `1101A` en radio y entrega la evidencia arriba descrita. Hasta entonces: BRIEF_ONLY.
