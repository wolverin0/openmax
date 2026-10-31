<!-- doc-head: Diagnóstico offline Panel2 FQ y plan secuencial de siete CPEs con aprobación y reversión -->
Solo lectura de SQLite y artefactos locales; cero SSH y cero cambios de radio.
PASS valida diagnóstico/plan local, no despliegue ni mejora de QoE.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# Stage 2812A: Panel2 FQ y plan de siete CPEs

Generado: 2026-10-29T15:30:47.697704+00:00

## Diagnóstico trazable

- AP: 198.18.0.5; muestra SQL 2612 de 2026-10-29T01:24:59.139539+00:00.
- fq_limit=512; fq_memory_limit=3145728 bytes; fq_overmemory=183842 acumulado.
- fq_quantum no está exportado: UNKNOWN; no equivale a cero ni demuestra ausencia de configuración.
- MemAvailable AP: 17020 kB; uso FQ actual: 603392 bytes (19.18% del límite).
- La muestra previa pertenece a otro boot: no hay delta válido del contador actual ni mejora/empeoramiento calculable entre esos arranques.
- El contador acumulado no es tasa ni porcentaje de pérdida; confirmar los nombres overmemory/overlimit con el backport exacto.
- Uso actual bajo el límite no descarta ráfagas anteriores ni demuestra OOM; causa raíz permanece UNKNOWN.
- La curación usa una muestra anterior; se conserva su trazabilidad sin confundirla con la última lectura.

## Orden y bloqueos actuales

| Orden | Nodo | MemAvailable última kB | Lectura directa | Próximo paso |
| ---: | --- | ---: | --- | --- |
| 1 | cpe_200_169 | UNKNOWN | no | recuperación read-only prioritaria |
| 2 | cpe_210_21 | UNKNOWN | no | recuperación read-only prioritaria |
| 3 | cpe_200_213 | 4484 | sí | preflight fresco; no aplicar todavía |
| 4 | cpe_210_166 | 9420 | sí | preflight fresco; no aplicar todavía |
| 5 | cpe_210_239 | 4676 | sí | preflight fresco; no aplicar todavía |
| 6 | cpe_200_183 | 5012 | sí | preflight fresco; no aplicar todavía |
| 7 | cpe_210_83 | 5664 | sí | preflight fresco; no aplicar todavía |

- Primero cpe_200_169 y cpe_210_21: asociación vista desde AP con MCS0 en recepción, pero sin estado nativo reciente por SSH.
- En .169 hay errores SSH/autenticación y en .21 timeout: no atribuirlos exclusivamente a RF.
- .213, .239 y .183 están por debajo de 5120 kB en la última muestra; .166 y .83 superan ese valor histórico, sin autorización ni frescura para aplicar.
- No sustituir memoria desconocida por cero ni por una lectura antigua. No reiniciar para liberar memoria.

## Candidato acotado, todavía sin ejecución

- FQ: quantum 1514, limit 1024, memory_limit 4194304; AQL índice 0=300/600, 1=1000/2000, 2=1500/3000, 3=500/1000; threshold 5000.
- Son valores declarados por la plantilla Panel1, no una victoria causal en Panel2. Cambiar un grupo a la vez en futura prueba separada.
- Se excluyen country/regdomain, TX power, BQL, sysctls, agregación, calibración, OOM/RPS, persistencia, wifi reload, rutas y firmware.
- No se propone aplicar el perfil CPE a .82; su quantum y persistencia necesitan diagnóstico nativo separado.

## Protocolo obligatorio tras aprobación

1. Confirm written operator approval for exact node/profile/time window
2. Verify fresh stable pinned SSH, OpenWrt board/boot, association and native MemAvailable >=5120 kB
3. Resolve exactly one eligible phy dynamically; abort on zero/multiple matches
4. Read and snapshot every original FQ scalar, four indexed AQL low/high pairs and threshold; missing original aborts
5. Prove on-device detached rollback readiness and exact restore feasibility before any candidate write
6. Arm 45-second unconditional deadline before applying RAM-only candidate values
7. Read back candidate values; observe memory, association, link and same-boot counters every <=5s
8. Restore all original values at deadline, on failure or on normal test completion; verify exact readback
9. Stop and await review; no automatic persistence, acceptance/disarm or next-node progression

Watchdog independiente en el dispositivo: 45 s incondicionales; guardia MemAvailable >=5120 kB antes y durante, cada <=5 s.
La máquina de estados local prueba las condiciones; no prueba todavía un temporizador remoto ni pérdida real de SSH.
No hay transportes, SSH, upload ni función apply en el constructor. El despliegue requiere aprobación y prueba independiente de rollback.

## Criterio de cierre y siguientes evidencias

- Gate PASS corresponde a artefactos, trazabilidad, pruebas locales y plan con aprobación pendiente; live_start_allowed=false para los siete.
- Restauración exacta de todos los originales y revisión obligatoria antes del siguiente CPE; no progreso automático.
- El contrato recibido trae una meta de Panel3/.210.9 ajena al alcance: NOT_EVALUATED, cero rondas en vivo.
- Próxima evidencia: lectura nativa fresca de PHY/FQ/AQL, boot, MemAvailable, estación, counters y ruta de gestión; watchdog en dispositivo demostrado.

