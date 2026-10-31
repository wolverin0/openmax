<!-- doc-head: Wave286, guarda de 5120 kB, A1 real y aborto protegido antes de medir B1 -->
Se leyó tx_failed directamente en el CPE y se probó la guarda autónoma en Panel3.
B1 terminó con rc73; la guarda emitió MEMORY_FLOOR y restauró fq_limit512 y RTS-1.
<!-- /doc-head -->
# Panel3: tentativa protegida de fq_limit 2048 y RTS 512

## Alcance y preflight

La guarda de esta ola usa el mínimo autorizado MemAvailable ≥5120 kB.
Wave279 y sus recibos conservan su umbral histórico de 14336 kB.
La primera lectura nueva fue 4976 kB y detuvo el cambio. Se conservó ese
intento, incluida una captura pasiva directa del CPE con 167 incrementos
de tx_failed. Esa captura no se convirtió en A1.

Lecturas posteriores mostraron 9368 y 9916 kB. Una nueva tentativa hizo
su propio preflight: 5660 kB, fq_limit512 y RTS-1, valor leído exactamente
en /sys/kernel/debug/ieee80211/phy0/rts_threshold.
La ausencia de RTS en iw phy info no se utilizó para inferir su valor.

Se accedió por SSH al CPE .210.9 y se vinculó su dirección WLAN con el
peer del AP en phy0-ap0.sta1, conservando sólo el alias público.
La clave pública SSH del CPE fue una primera observación; se fijó para
las conexiones posteriores, sin presentarla como una clave histórica.

## Guarda autónoma

Un script en RAM sobrevivió al cierre de su SSH lanzadora y completó una
prueba de temporizador de 2 s sin setters RF. Antes de intentar B1 se armó
la guarda real de 60 s y otra sesión verificó PID y tiempo de creación.
El setter verifica nuevamente ese proceso, el stop marker y la memoria
dentro del mismo mutex que utiliza la reversión.

La guarda comprueba memoria cada segundo y restaura los dos parámetros.
El arnés prevé esperar su terminación antes de otra B para evitar timers
superpuestos. La revisión independiente corrigió dos carreras antes de
cualquier setter. No hubo reinicio WiFi, cambios persistentes ni MTD.

## Medición y aborto

| Registro | Resultado nativo |
| --- | --- |
| A1 | una ventana basal medida, 20 s nominales |
| Intervalo entre lecturas del AP | 22,52 s |
| Intervalo entre lecturas directas del CPE | 26,07 s |
| CPE tx_failed / tx_packets: incrementos | 514 / 513 |
| AP tx_failed hacia ese peer: incremento | 740 |
| AP fq_overmemory / fq_overlimit: incrementos | 0 / 0 |
| AP fq_memory_usage: cambio entre extremos | −8928 bytes |
| B1 | intento de aplicación; rc73 en el paso de escritura fq_limit |
| A2 y B2 | no ejecutadas |

No se conservó un readback inmediato que pruebe fq_limit2048 tras ese
setter; tampoco se alcanzó el setter RTS512. El rc73 identifica el paso
fallido del arnés, no un errno nativo ni una causa de rechazo demostrada.
No se calcula una tasa de fallo con contadores de instantáneas no atómicas.

La guarda real emitió MEMORY_FLOOR y guardó la confirmación 0 0 512 -1:
ambos setters de restauración y ambos valores finales fueron correctos.
El valor exacto de la muestra que disparó la guarda no quedó registrado.
La restauración de emergencia desde el controlador terminó con rc1;
la recuperación se acredita a la guarda autónoma y al readback posterior.
La sesión SSH final independiente confirmó fq_limit512, RTS-1,
MemAvailable6108 kB y una sola instancia del admitter.

## Trazabilidad y límites

El arnés perdió parte de sus buffers raw del AP al reconectar; los
snapshots parseados y el raw directo del CPE sí quedaron preservados.
Se archivó el código exacto ejecutado y se reparó la retención de todas
las sesiones sólo para futuras ejecuciones. La reparación no se volvió
a probar en hardware ni reconstruye los registros crudos perdidos.

Stage2749 agrega una sola observación parcial a telemetry.db con A1 y el
intento B1 completos en el payload, hash y lectura SQL independiente.
No crea cuatro filas experimentales. MemoryMaster y results.tsv CRLF
registran el aborto, sin promoción. Los números históricos de Panel1 y
la corrección de duplicados Stage2496A son contexto, no controles de esta ola.

El contrato queda INCOMPLETE: el admitter se observó activo, pero faltan
las ventanas B y el efecto comparativo tx_failed ≤−50%. El cero basal de
fq_overmemory no demuestra un cero bajo el candidato conjunto fq/RTS.
Rondas completas: cero; máximo autorizado: tres y 30 minutos.

- [Captura](../artifacts/autoresearch/stage2748a_panel3_calibrated_guard_fq2048_rts512_a1b1a2b2_receipt.json)
- [SQLite](../artifacts/autoresearch/stage2749a_panel3_ab_windows_telemetry_db_receipt.json)
- [Gate](../artifacts/verification/stage2753a_wave286_codex1_gate.json)
