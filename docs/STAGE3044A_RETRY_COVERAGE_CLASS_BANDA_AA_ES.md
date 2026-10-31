<!-- doc-head: Wave384, retry de costo coverage class sin piso RAM fijo -->
Banco LAP-120; banda A/A de la corrida, receptor Loco autorizado y restauracion por watchdog.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Coverage class 0 frente a 6: retry de banco

**NO_GO por el criterio empirico acordado: goodput de B1 bajo el minimo A/A.**
Clase6 efectivamente aplicada y leida; AP restaurado a clase0. Sin piso RAM ni OOM nuevo.

## Contrato y metodo

- AP LAP-120 .20; clase A=0, B=6. Se modifica solo el AP en RAM.
- La Loco .250/.200.41 participa como receptor TCP y telemetria de memoria, sin cambios RF/config.
- Autorizacion del Orchestrator <orca-id>: presupuesto180min y protocolo corto.
- Tres A/A; luego tres rondas A1-B1-A2-B2: doce ventanas previstas.
- Cada fase:5s de asentamiento y20s de carga; ping nativo cada1s.
- TCP cuatro flujos por sentido, bidireccional, socket -w16K y bloque -l16K.
- Los buffers pequenos fueron autorizados para reducir la memoria del receptor tras el OOM W379.
- Las comparaciones usan solo el A/A con esta misma carga; no se usan las tasas W379 como control.
- Watchdog compartido45s renovado cada8s; restaura coverage0 y retira alias/NAT privados.
- Lecturas al inicio y final: coverage, otras colas/config, boot y estado del enlace.
- MemAvailable de AP y receptor en cada ventana, sin ningun piso numerico de aborto.
- Un OOM nuevo o goodput menor al minimo A/A o p99 mayor al maximo A/A detiene la corrida.
- Mejoras de goodput o p99 no se tratan como dano por salir del extremo favorable de la banda.
- Se mantienen controles de identidad, lease, enlace y validez del instrumento.
- GO significa aceptacion empirica de esta carga en banco; no prueba formal de no inferioridad ni promocion.

## Contabilidad del instrumento

Goodput DL usa sum_received del servidor, y UL sum_received_bidir_reverse del cliente.
Son contadores de los respectivos receptores; se cotejan con sus propias sumas por flujo.
Se verifica recibido no mayor a enviado por el extremo opuesto.
Los resumenes remotos de bytes enviados quedan como diagnostico; no equivalen a bytes recibidos.

Se preservan dos intentos detenidos por el lector, ambos antes de completar A/A y sin clase6.
El servidor informo cero en su campo remoto de recepcion UL, y hubo una diferencia de16KiB
entre dos snapshots del contador de envio. Se corrigio el mapeo, sin tolerancia de rendimiento nueva.
Los originales quedan en attempts; dos replays nativos y dos mutaciones invalidas verifican el lector.
No se reutilizan esas ventanas como controles de la corrida corregida: faltan readbacks de cierre de fase.

## Ventanas medidas

| Fase | Clase AP inicio/fin | DL Mbps | UL Mbps | Total Mbps | p95 ms | p99 ms |
|---|---|---:|---:|---:|---:|---:|
|AA1|0/0|18.764|30.830|49.594|37.313|61.203|
|AA2|0/0|17.238|30.953|48.191|26.692|29.409|
|AA3|0/0|16.511|31.062|47.573|17.352|18.287|
|A1|0/0|16.980|30.842|47.822|22.805|23.954|
|B1|6/6|17.881|28.370|46.251|29.999|35.826|

Banda A/A: goodput47.572700..49.593542Mbps, p99 max61.202540ms.
B1=46.251003Mbps: -2.778267% frente al minimo A/A y -3.285124% frente a A1.
El p99 de B1=35.826270ms queda dentro del extremo de dano A/A; el disparador fue solo goodput.
Se midieron3AA+2de12ventanasAB. Las10restantes no se ejecutaron tras el cruce; no hubo reintento de rendimiento.

## Limites y restauracion

La secuencia A/A de caudal desciende; un solo par no separa coverage de deriva temporal.
Todos los fq_backlog muestreados fueron0: esta carga con buffers pequenos no demuestra saturacion RF.
NO_GO es el resultado operacional de la banda; no prueba causal una penalidad universal de clase6.
Minimos muestreados: AP8368KiB, Loco6928KiB; no se usaron como guardas numericas.
Todos los pings de las5ventanas llegaron20/20. Sin OOM nuevo frente a los mensajes historicos separados.
Dos rondas finales leyeron APclase0, perfil original, enlace asociado y ausencia de iperf3/ping propio.
Loco asociada, sin iperf3 y clase0 al cierre; ningun cambio de configuracion o RF en la Loco.
NAT, alias, directorio y handle privados del AP retirados. Sin reinicio ni escrituras flash.
El primer intento de lectura final via IPaerea fallo tras retirar el alias temporal, como corresponde;
la verificacion final uso .100.250 con la misma clave de host fijada, sin volver a agregar rutas.

[Recibo](../artifacts/autoresearch/wave384_coverage_class_retry.json) ? [Gate](../artifacts/verification/wave384_lane1_coverage_class_retry_gate.json)
