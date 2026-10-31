<!-- doc-head: W472 diagnostico solo lectura del hueco SQLite del 31 de octubre -->
CONFIRMED: intervalos sin muestras y nuevo proceso del colector a las 17:25Z.
UNKNOWN: causa inicial; no se confunde el hueco con una caida RF o del motor SQLite.
<!-- /doc-head -->

# Hueco de telemetria: causa y limites de la evidencia

**La causa inicial queda UNKNOWN.** Se confirma una interrupcion compartida de
observaciones retenidas y la creacion de un nuevo hijo del supervisor existente.
Un bloqueo del plano local de recoleccion/persistencia o de recursos del host
es INFERRED; falta evidencia historica para elegir entre espera de red, locks,
I/O, bloqueo de un worker u otra causa. No se aplico ningun parche ni reinicio.

Artefacto verificable: `artifacts/autoresearch/wave472_telemetry_gap.json`.
El [anexo DB](STAGE3143A_DB_GAPS_ES.md) contiene el roster, metodos y cadencias.
Los tiempos siguientes son UTC. La ventana nominal corresponde a 13:30-14:25 ART.

## Intervalos exactos retenidos

| Serie global | Ultima muestra antes del hueco | Primera despues | Separacion |
| --- | --- | --- | --- |
| Colector Before/After | 16:30:07.792279 | 17:25:18.588161 | 3310.795882 s |
| Sidecar ICMP, origen office | 16:30:00 | 17:20:00 | 3000 s |
| Sidecar ICMP, origen core | 16:30:00 | 17:21:00 | 3060 s |
| Sidecar colas | 16:29:00 | 17:29:00 | 3600 s |

Los 18 nodos habilitados tienen sus extremos propios en el JSON. Hay cuatro filas
del colector entre 16:30:00 y 17:25:00: son la cola OBSERVED del ciclo anterior,
no muestras continuas del intervalo ausente. No se sustituyo ausencia por loss=100
ni por RTT=0. La separacion incluye la cadencia normal de un ciclo, aproximadamente 60 s.

`collected_utc` es tiempo de coleccion, y `minute_utc` la etiqueta de la muestra;
no existe un timestamp independiente del commit SQLite. Por eso no se puede
afirmar que el motor DB permanecio bloqueado exactamente durante esos intervalos.
`office` y `core` son origenes de sonda, no prueba de procesos en hosts independientes.

## Procesos, supervisor e historial

- Supervisor PID 246980: creado a las 04:28:01.309211Z, sigue vivo.
- Colector PID 249256: creado a las 17:25:07.357402Z; padre PID 246980.
- Lanzamiento registrado 17:25:11.094199Z; identidad escrita a las 17:25:13.464967Z.
- La tarea permanece Running; LastRunTime 04:27:27Z, missed runs=0.
- Politica del supervisor: poll=5 s, stall=240 s; restart_count=19 acumulado.
  Ese contador no fecha 19 reinicios en esta ventana.

**CONFIRMED:** el supervisor existente creo el proceso actual, que produjo filas
desde 17:25:18Z. **INFERRED:** recuperacion de un colector sin progreso por la
supervision. La causa exacta del reemplazo y el fin del PID anterior no se retuvieron;
no se descarta una intervencion externa. El estado del supervisor se sobrescribe,
por lo que el actual RUNNING no conserva un anterior OWNED_DB_STALL_RESTART.

`daemon.stderr.log` tiene 282886 bytes y ultima modificacion 15:51:13.073603Z,
anterior al hueco. Contiene cuatro excepciones historicas `database is locked`,
18 OSError y una PermissionError seleccionadas, pero sin timestamp individual.
Esos errores no permiten atribuir este incidente a SQLite. stdout tiene cero bytes.

El origen releido tiene dos barreras `Future.result()` sin timeout agregado.
Cada sonda tiene sus limites, pero la falta de trazas de fase impide saber si el
colector se quedo en una barrera, en append/commit o en otro punto. Es una
posibilidad de bloqueo, no una demostracion causal de este hueco.

## Windows, almacenamiento, WSL y red

Se consultaron eventos de 16:00 a 17:45Z: 84 en System y 3283 en TaskScheduler.
No hubo eventos de la tarea de telemetria en esa ventana ni eventos de
power/sleep/boot/cambio de hora en la seleccion System. Hay eventos Windows en
varios bloques de cinco minutos del intervalo; no se sustenta una suspension completa.
System conserva eventos desde el 12/10; TaskScheduler desde el 31/10 10:00Z,
por lo que ambos cubren la ventana estudiada. Application niveles 1/2/3: cero eventos.
Esto no demuestra ausencia de un bloqueo de procesos o de recursos.

Hay 19 eventos disk/7 entre 16:24:46.775851 y 16:31:44.420987Z:
`Harddisk3`, modelo WDC WD10EZEX, volumen E:, informa bad block.
La DB esta en G:, disco 5 Samsung SSD 970 EVO Plus; Ubuntu WSL y pagefile estan en C:.
**No se establece una averia directa del disco que contiene SQLite.** Una repercusion
global de E: tampoco puede confirmarse ni descartarse solo con esos eventos.
El resto incluye DCOM, Schannel y un timeout DNS; no prueban la causa del colector.

WslService y vmcompute estan Running; el LxssManager heredado esta Stopped.
Los procesos wsl/wslhost observados nacieron el 30/10 22:57Z y preceden el hueco.
El daemon corre como Python nativo Windows y no invoca directamente `wsl.exe`.
No hay traza historica WSL util para esta ventana; el WSAETIMEDOUT anterior es un
antecedente aportado por el operador, sin timestamp corroborado aqui.
Security no es accesible con el permiso actual y Sysmon no esta presente.
WSL no queda demostrado como causa ni se descarta una dependencia indirecta.

La falta de sondas retenidas impide afirmar reachability de Guarida dentro del hueco.
El corte de energia aportado, 13:29-14:29Z, es otra ventana y no prueba una causa
para la ausencia posterior. Tampoco se demuestra un segundo corte de red o energia.

## Otros huecos mayores a cinco minutos

**Si:** en la ventana movil auditada hay 23 intervalos globales del colector >300 s,
incluido este; por lo tanto son 22 adicionales. El JSON conserva todos los extremos.
Ejemplos: 30/10 23:01:08.308668-23:30:58.158606 y
31/10 02:08:45.685931-04:28:20.982730. Colas tiene otro intervalo de 360 s
el 31/10 04:11-04:17. El sidecar ICMP no tiene otro hueco global en su retencion.

Son separaciones entre muestras, no incidentes independientes ni outages de clientes.
Los periodos iniciales incluyen evidencias esporadicas previas al servicio persistente;
el sidecar empieza el 30/10. No existe cobertura continua de siete dias para calcular
un SLA de disponibilidad ni declarar una red sana en los periodos sin datos.

## Propuesta sin aplicar

No se identifica una falla causal de codigo que justifique un cambio funcional.
Para un proximo incidente conviene conservar un journal acotado, sin secretos,
con eventos CHILD_EXIT, STALL_DETECTED y CHILD_STARTED: UTC, PID/run_id,
last_seq, segundos sin progreso y exit code. Dos archivos de 64 KiB bastan como
limite tecnico de evidencia, sin copiar argv, owner_token o payloads de abonados.
Agregar fase/cycle_id antes/despues de snapshot, recoleccion y commit facilitaria
distinguir bloqueo de una sonda, SQLite y lectura del manifest.

Test propuesto, **no ejecutado ni implementado**: reloj falso y DB sin progreso
durante 240 s, verificar un STALL_DETECTED y CHILD_STARTED durables; simular
progreso, cierre inesperado y fallo de escritura del journal, comprobar rotacion
y ausencia de secretos. No se presenta como fix confirmado de la causa.

## Verificacion del diagnostico

Snapshot DB seq 51972; roster de 18 nodos y 716 series separadas por semantica.
355 saltos por nodo contrastados con SQL LEAD independiente, tolerancia 2 ms.
No se corrio pytest porque no se cambio codigo. La verificacion usa consultas
reales, estructura/privacy del artefacto y hash exacto del daemon antes/despues.
El ultimo resumen releido tenia 17 observaciones, 44 filas de delta y edad 61.6 s;
es evidencia de reanudacion, no explicacion del incidente ni aceptacion RF.
