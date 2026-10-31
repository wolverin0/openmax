<!-- doc-head: Wave269, dos rondas reales desde SQLite y salud limitada al alcance observado -->
Una campaña alcanzó los tres objetivos; no hubo segunda campaña ni cambios RF.
Clasificación confirmada para dos celdas y probes de alcance; no significa cero pérdida.
<!-- /doc-head -->
# Site-Aware desde telemetry.db

Dominio: `D10_SITE_AWARE_WISP_STACK`. Presupuesto:25min y dos campañas como máximo.
Se detuvo con `STOP_TARGET_REACHED` después de la primera campaña.

| Objetivo Karpathy | Resultado verificado |
| --- | --- |
| two_round_verdict_live | true |
| buddy_disambiguation_complete | true |
| dashboard_8787_http_200 | true |

## Antes y después

El baseline2576 documentaba un analizador histórico sólo de Panel1 y motores
Site-Aware sin conexión a observaciones actuales. Wave262 añadió una captura
de dos celdas; el contexto de buddies/backhaul permanecía incompleto.
Esta wave incorpora datos actuales de ambos APs, sus buddies y los hops
hacia Guarida .61 y core .1. No se deduce una mejora de rendimiento entre fechas.

## Adquisición y base de datos

Se leyeron Panel1 .84 y Panel3 .83 por SSH, verificando sus manifiestos.
Cada AP aportó tres muestras: baseline y dos rondas de cinco pings.
Se midieron seis peers RF y seis rutas dirigidas: los APs entre sí, y cada
AP hacia .61 y .1. No se hizo SSH a los routers ni se cambió configuración.

Las seis filas232–237 se añadieron a `openwrt_before_after_samples` usando
el Store existente. Una conexión SQLite `mode=ro` verificó sus JSON y SHA256.
El censo previo de231pares secuencia/hash se conserva. La evaluación se
construye desde esas filas leídas, con asociación, contadores, rutas y boots.

| Evidencia | Respuestas / enviados |
| --- | ---: |
| Peers RF | 88/90 |
| Buddy y hops .61/.1 | 90/90 |
| Total | 178/180 |

Un peer RF respondió13/15. `CONFIRMED_SITE_HEALTHY` significa continuidad RF
y alcance confirmado en dos rondas para `OBSERVED_PANEL1_PANEL3_TOWER_CORE_REACHABILITY`.
No significa cero pérdida, ausencia de degradación o diagnóstico causal.
Almafuerte .60 y Panel2 .82 siguen explícitamente no observados.
Los pings de hops no se presentan como asociación RF ni como bypass del core.

## Validación y límites de procedencia

Una revisión independiente encontró que comparar etiquetas SHA no bastaba:
el contrato ahora recalcula el hash del payload completo y exige membresía
exacta de cada hop y muestra RF, además de boot coherente por AP.
El gate relee SQL y revalida con ese contrato en la época original de captura.
La captura y exportación originales se conservan sin reemplazo ni cambio de fecha.

El daemon compartido cambió concurrentemente durante la captura. Se guardaron
ambos hashes; los bytes de la revisión ejecutada anterior no se recuperaron.
Por ello `whole_execution_source_stable=false` y la revisión exacta del writer
permanece `UNAVAILABLE_EXACT_EXECUTED_SOURCE`. Las lecturas y hashes SQL sí
están confirmados. El PASS del gate cubre el objetivo observado, no una
reproducción completa del writer histórico.

## Exportación y dashboard

Se escribió `fmx_site_aware_wave269.prom` con seis monitores y12filas numéricas
antes/después. La frescura se calcula desde la observación más antigua entre
los últimos datos de cada peer/ruta; el TTL es90s y no se rebasa al exportar.
El archivo fue exportado dentro de ese TTL. Al ser estático, su gauge se llama
`snapshot_fresh_at_export`; la salud actual exige ambos límites de reloj al consultar.

El Command Center8787 respondió HTTP200 con contenido HTML y hash guardado.
No se regeneró el HTML ni se modificó el servicio9297, su job Prometheus o Kuma.
El archivo local está listo para colector; nueva ingesta remota no fue ejecutada.
No se instaló sondeo continuo ni se enviaron pushes.

## Archivos

- [Captura DB](../artifacts/autoresearch/stage2640a_site_buddy_live_db_receipt.json)
- [Exportación](../artifacts/autoresearch/stage2641a_site_aware_textfile_and_dashboard_receipt.json)
- [Textfile](../artifacts/autoresearch/wave269/export/fmx_site_aware_wave269.prom)
- [Contrato estricto](../tools/telemetry/site_buddy_db_contract.py)
- [Gate y relectura SQL](../tools/verify/verify_stage2645a_wave269_codex1_gate.py)
