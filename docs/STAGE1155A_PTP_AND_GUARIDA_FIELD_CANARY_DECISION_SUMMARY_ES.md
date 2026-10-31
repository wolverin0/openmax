<!-- doc-head: Stage 1155A resumen en espanol de la decision de canario de campo (PtP PBE-5AC, Guarida .84, LTU-Lite .110) a partir de las inspecciones 1151A y 1152A; decision global NO-GO / PENDIENTE, sin afirmar preparacion de produccion -->
# Stage 1155A - Decision de canario de campo (resumen para el operador)

## Decision en una linea

**NO-GO / PENDIENTE.** Ninguna superficie tiene hoy evidencia suficiente para un canario
de campo. Este documento no autoriza ningun cambio en equipos reales y no declara
preparacion de produccion.

## Que se uso como entrada (y de que clase es)

| Entrada | Que inspecciona | Clase de evidencia |
| --- | --- | --- |
| `artifacts/verification/stage1151a_ptp_bench_artifacts_1043a_to_1048a_inspector.json` | Artefactos de banco PtP, etapas 1043A..1048A | Inspeccion offline de archivos; no toca equipos |
| `artifacts/verification/stage1152a_wa_guarida_ltu_live_receipts_inspector.json` | Recibos WA / Guarida / LTU, etapas 1133A..1138A | Inspeccion offline de recibos ya existentes; no toca equipos |

Ambas son inspecciones sin acceso a equipos (`live_devices_touched` false). Reportan lo que
los recibos dicen; no lo convierten en hardware confirmado. Ninguna entrada de este resumen
queda como `CONFIRMED_LIVE_HARDWARE` por haber sido inspeccionada.

## Superficie 1 - PtP PBE-5AC: PENDIENTE (cohorte incompleta)

- El experimento A/B del PtP necesita una cohorte completa de recibos 1043A..1048A.
- Faltan los recibos de las etapas `1045A`, `1046A` y `1047A`: solo existen sus documentos.
  Un documento describe un plan; no es un resultado medido.
- Sin esos recibos no se puede comparar A contra B, asi que no hay base para promover nada.
- El inspector 1151A informa `cohort_status` (INCOMPLETE) y la lista `missing_receipts`.
  Que el estado sea INCOMPLETE es el resultado honesto, no un fallo del inspector.
- Decision: **PENDIENTE**. Para destrabarlo hay que generar los tres recibos ausentes
  con corridas reales de banco, autorizadas por el operador, y volver a inspeccionar.

## Superficie 2 - Guarida .84: segun el recibo 1134A (dry-run)

- La informacion disponible es el recibo de la etapa `1134A`, que es un dry-run.
- Un dry-run demuestra que la logica y los comandos se arman bien; no demuestra
  comportamiento en el aire ni en el equipo real.
- Decision: se mantiene lo que dice `1134A` (ensayo en seco). No se interpreta como
  canario aprobado. Cualquier paso a un cambio real requiere decision explicita del operador
  y un recibo posterior de ejecucion real.

## Superficie 3 - LTU-Lite .110: BLOQUEADO

- La etapa `1135A` quedo en estado BLOCKED_ACCESS: el SSH fue rechazado y se tomaron
  0 snapshots.
- Sin acceso no hay linea base ni lectura del equipo; no hay nada que comparar.
- El inspector 1152A conserva ese estado honesto (BLOCKED) en su lista por etapa.
- Decision: **BLOQUEADO**. No se evita el bloqueo con credenciales alternativas ni con
  datos sinteticos. Destrabar el acceso es una accion del operador.

## Tabla de decision

| Superficie | Decision | Motivo |
| --- | --- | --- |
| PtP PBE-5AC | PENDIENTE | Cohorte A/B incompleta (faltan 1045A, 1046A, 1047A) |
| Guarida .84 | Segun `1134A` dry-run | Solo ensayo en seco, sin ejecucion real |
| LTU-Lite .110 | BLOQUEADO | `1135A` BLOCKED_ACCESS, SSH rechazado, 0 snapshots |
| Global | NO-GO / PENDIENTE | Ningun canario habilitado |

## Que NO dice este resumen

- No dice que algo este listo para produccion.
- No dice que algun recibo sea hardware confirmado en vivo.
- No dice que la cohorte PtP este completa ni que LTU-Lite sea accesible.
- No reemplaza la verificacion del gate `tools/verify/verify_stage1156a_wave20_claude_gate.py`,
  que solo comprueba que las inspecciones se ejecutaron y reportaron, no que todo este verde.

## Que necesito del operador

1. Decidir si se autorizan corridas de banco para generar los recibos `1045A`, `1046A`, `1047A`.
2. Resolver el acceso SSH a LTU-Lite .110 (o confirmar que sigue fuera de alcance).
3. Decidir si el dry-run `1134A` de Guarida .84 pasa a ejecucion real.

## Referencias internas

- `docs/STAGE1156A_WAVE20_CLAUDE_GATE.md`
- `artifacts/verification/stage1153a_master_pytest_matrix_1127a_1150a.json`
- `artifacts/autoresearch/stage1154a_master_docs_sync_through_1156a.json`
