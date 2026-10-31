<!-- doc-head: Telemetría persistente antes/después, supervisión Windows y límites de aceptación -->
Colección observacional de OpenWrt con identidad de proceso, progreso SQLite y evidencias separadas.
Los servicios alternativos son plantillas sin desplegar; el arranque sin sesión no está aceptado.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 2582A — Demonio persistente de métricas antes/después

## Alcance y medición

El colector toma instantáneas de solo lectura e ICMP acotado. No cambia radio, firmware,
colas, potencia ni configuración. El intervalo solicitado es 60 segundos; un ciclo puede
tardar más por las consultas secuenciales y sus plazos. Cada muestra conserva su fecha,
estado, identidad de arranque y hashes del registro y de la referencia congelada.

Se publican los valores disponibles y su procedencia. Una sonda sin respuesta no produce
RTT cero; los datos ausentes quedan nulos. Las tasas entre contadores exigen el mismo
arranque y tiempo de actividad creciente. El ruido, la señal, AQL pendiente y las colas
solo se afirman cuando existe lectura válida; la indisponibilidad permanece explícita.

El monitor histórico tiene 699 intervalos observados: eso no acredita 72 horas completas.
La carga, el recorrido y el estadístico históricos difieren de la observación actual.
`CONTEXT_MISMATCH` impide convertir esa comparación en mejora porcentual causal.

## Persistencia Windows observada

La tarea `FuturaMAX-BeforeAfterTelemetry-2581A` tiene lectura nativa verificada y estado
`Running`. Usa `InteractiveToken`, privilegio mínimo, disparador al iniciar sesión,
`Hidden=true`, `MultipleInstances=IgnoreNew`, `ExecutionTimeLimit=PT0S` y reinicio
de la acción cada minuto si falla, hasta 999 intentos. No tiene disparador de arranque.
La aceptación de inicio sin sesión es **falsa**; depende de una sesión interactiva.

El lanzador permanece esperando al supervisor, por lo que la acción de la tarea cubre
la vida del supervisor. El proceso hijo usa una ventana oculta y el directorio absoluto
del repositorio. La exclusión mutua combina la política de la tarea y un bloqueo nativo
de archivo del supervisor.

La propiedad exige PID, tiempo real de creación, ejecutable, argumentos completos,
hash del código y token del manifiesto. La terminación controlada retiene un identificador
nativo del proceso y vuelve a comprobar su generación; un PID reutilizado no autoriza
terminar otro proceso. Cambiar código, registro o referencia sellados detiene la aceptación.

El supervisor distingue actividad del productor y muestras válidas. Filas de error por sí
solas no acreditan salud: exige muestras `OBSERVED` recientes de ambos AP, además del
proceso propio y progreso SQLite del `run_id` actual. La recuperación solo se acepta con
nuevo PID y `run_id`, nuevas filas válidas y continuidad del supervisor.

## Evidencia y fallas conservadas

La primera sonda remota utilizó una opción de ping no soportada; quedó archivada y se
corrigió antes de aceptar las sondas. Los permisos nativos rechazaron S4U con arranque y
la variante interactiva con arranque. Una tercera inscripción no se inició porque la
lectura XML trató dos valores omitidos como ausentes en vez de sus valores de esquema.

La tarea propia sin procesos se retiró con comprobación de propiedad. La reparación
interpreta únicamente los nodos omitidos como `LeastPrivilege` y `Enabled=true`;
valores explícitos inválidos siguen fallando. La reinscripción usó una sola estrategia
interactiva al iniciar sesión y conservó los intentos anteriores y sus XML privados.

La prueba desechable también detectó una conexión SQLite retenida después de consultar
progreso. Se conservó el fallo de limpieza, se detuvo y retiró únicamente la instancia
propia y se reparó el cierre explícito con `contextlib.closing`. La instalación posterior
sella la revisión corregida, sin reemplazar las pruebas de las revisiones anteriores.

El primer arranque posterior alcanzó el plazo de 180 segundos sin supervisor vivo;
la causa queda **UNKNOWN** y las consultas nativas se conservaron. El inicio idempotente
de la tarea ya propia lanzó el productor; la aceptación siguiente verificó sus muestras.

La recuperación real mantuvo el supervisor PID `114636` y reemplazó el colector propio
PID `84312` por `94296`, con otro `run_id`, mediante un identificador nativo retenido.
Antes había ocho filas: siete `OBSERVED` y un nodo bloqueado. Después había ocho nuevas
filas del nuevo ciclo: seis `OBSERVED`, el nodo sin clave y un `TimeoutError` temporal.
Ambas verificaciones nativas terminaron con código cero y muestras recientes de los dos AP.
No se terminó ningún proceso ajeno. El demonio quedó funcionando tras esta captura acotada.

`runtime_healthy=true` acredita los AP requeridos y al productor; **no** significa salud
del 100% de los CPE. Cada AP tiene tres respuestas válidas en su sonda al par RF; las
sondas RF originadas directamente en CPE siguen sin resolverse. No se afirma un recorrido
RF puro para cada medición. El recibo conserva los errores y la disponibilidad por nodo.

## Datos, identidad y alternativas

SQLite conserva las tablas preexistentes y agrega `openwrt_before_after_samples`.
La exportación probatoria se limita a esa tabla y los `run_id` seleccionados; no publica
la base completa de otras aplicaciones. JSONL y las filas guardan el hash canónico de
la muestra. La instantánea probatoria contiene 26 filas seleccionadas. El estado actual
y el resumen no reemplazan ese historial ni acreditan duración ilimitada ya observada.

Los XML originales, SID, token de propiedad y argumentos privados quedan fuera de los
recibos públicos; estos usan hashes. Cinco CPE recibieron fijación inicial TOFU de clave
antes de autenticarse: no equivale a una validación histórica independiente. El CPE
pendiente permanece bloqueado sin clave fijada, sin fabricar métricas.

Las plantillas systemd para PUBLIC_TERM_0003 y procd para OpenWrt **no están desplegadas**.
Requieren habilitación explícita y transferencia de propiedad para evitar dos colectores.
El muestreador procd local es opcional, de solo lectura y RAM, sin dependencia de Python;
su presencia como archivo no prueba ejecución, persistencia ni aceptación de hardware.

| Plantilla | Destino propuesto, sin instalación |
| --- | --- |
| `fmx-before-after-telemetry.service` | PUBLIC_TERM_0003: `/etc/systemd/system/fmx-before-after-telemetry.service` |
| `fmx-before-after-native.procd` | OpenWrt: `/etc/init.d/fmx-site-telemetry` |
| `fmx_before_after_native_sampler.sh` | OpenWrt: `/usr/sbin/fmx_before_after_native_sampler.sh` |

## Fuentes de ejecución

- [Recibo del colector](../artifacts/autoresearch/stage2580a_persistent_before_after_openwrt_daemon_receipt.json).
- [Recibo de persistencia y supervisión](../artifacts/autoresearch/stage2581a_before_after_daemon_persistence_supervisor_receipt.json).
- [Prueba de recuperación](../artifacts/autoresearch/stage2580a/recovery.json).
- [Metodología y seguridad](../artifacts/autoresearch/stage2580a/methodology_and_safety.json).
- [Fallas iniciales conservadas](../artifacts/autoresearch/stage2580a/task_initial_failures.json).
- [Lectura nativa de la tarea reparada](../artifacts/autoresearch/stage2580a/task_install_readback_repaired.json).
- [Supervisor](../tools/observability/ensure_fmx_before_after_daemon_running.py).
- [Plantillas de persistencia](../tools/observability/persistence/).
