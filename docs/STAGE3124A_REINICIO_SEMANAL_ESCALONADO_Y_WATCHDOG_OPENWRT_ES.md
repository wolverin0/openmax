<!-- doc-head: Wave 456; reinicio por cron probado en un LiteBeam, watchdog conservador y plan pendiente de aprobación -->
Prueba física limitada a bench_lbe116; no se instalaron cambios en producción.
Umbrales numéricos sin calibración permanecen deshabilitados.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Reinicio nocturno OpenWrt y watchdog acotado

## Resultado y alcance

**CONFIRMED:** el cron real del LiteBeam de banco ejecutó un reinicio suave con
`/sbin/reboot`. Se verificó un boot_id diferente, retorno con la misma clave SSH
fijada y persistencia del runtime, políticas y cron. Los hashes de las
configuraciones de red, Wi-Fi y sistema se conservaron.

La autorización fue la liberación explícita `<orca-id>`.
No se accedió a los otros bancos reservados ni a radios de producción.
No hubo acciones PoE, cambios RF, escrituras de firmware ni cambios de particiones.

| Evidencia física | Resultado |
| --- | --- |
| Modelo / versión | LiteBeam AC Gen2, OpenWrt 24.10.4 |
| MemAvailable previo | 7180 KiB |
| Snapshot previo | 12198 bytes, privado, dueño root, hash verificado |
| Retorno autenticado | Cota superior de 76,031 s desde la última lectura del boot anterior |
| Cron enviado a primer boot nuevo autenticado | 91,406 s |
| Estado final | Configuración persistente con `enabled=0` |

La cota incluye espera y transporte: no es una duración exacta del arranque ni
una calibración del tiempo de recuperación de ath10k. Se observaron desconexiones
y timeouts durante el reinicio; quedaron conservados en el recibo.
El reloj del banco estaba aproximadamente 338 s atrasado y usaba UTC.
No se ajustó. NTP correcto es un requisito pendiente para horarios de producción.

## Implementación y límites

Código: [runtime](../tools/ops/fmx_night_restart/runtime/fmx-night-restart),
[generador](../tools/ops/fmx_night_restart/planner.py),
[runner de banco](../tools/ops/fmx_night_restart/bench.py),
[verificador local](../tools/ops/fmx_night_restart/verify.py).
El runner no se debe volver a ejecutar sobre el recibo existente.

El runtime admite `status`, `scheduled` y `fault`; inspecciona por defecto.
Solamente `--apply` permite actuar. Identidad de placa y hardware, políticas
privadas, hashes, ámbito y aprobación deben coincidir. No evalúa configuración
como código. Usa exclusión mutua y bloquea una segunda acción del mismo boot.

Antes de cada acción escribe en flash una instantánea de meminfo (incluye Slab),
cola de dmesg y cola de logread. Cada snapshot tiene tope de 16384 bytes y hay
dos posiciones rotativas: como máximo 32768 bytes de snapshots, más metadatos.
La publicación es atómica, con permisos 0600 y sincronización antes del reinicio.
Si la captura, validación o persistencia falla, no se reinicia.
Los logs pueden contener datos operativos: quedan privados en el dispositivo.

El disparo extraordinario del banco usó un token privado de un solo uso y una
entrada cron para el siguiente minuto. Se consumió el token y se retiró esa
entrada después del retorno. No se esperó una semana para demostrar el cron.
El cron definitivo permanece instalado, pero no puede actuar con `enabled=0`.

## Watchdog: qué está probado y qué sigue desconocido

Sólo se admite la condición explícita y terminal de ath10k `WEDGED`; un evento
anterior seguido de recuperación no dispara. Timestamps inválidos o futuros se
rechazan. Hay un presupuesto persistente de un solo reinicio automático por
falla hasta revisión manual, para evitar un ciclo de reinicios entre boots.
No dispara por pérdida de ping, RSSI, fq_overmemory ni carga de clientes.

**Prueba local:** fixtures desechables verifican WEDGED, recuperación, memoria
inválida, integridad, snapshot y presupuesto. **UNKNOWN en hardware:** no se
inyectó una caída de firmware ni agotamiento de memoria en este ensayo.

Los datos reales no permiten fijar un umbral crítico de MemAvailable:

- El mismo Loco estuvo sano con 2032 KiB en W439.
- En W445 sufrió OOM bajo carga, con lecturas adyacentes de 2880 y 2948 KiB.
- La SQLite del daemon registra un AP observado con 2100 KiB en seq 4601.

Una lectura instantánea no separa esos estados. Los pisos de 3/6 MiB del
colector limitan sondeos; no son umbrales de reinicio.
`memory_enabled=0` y `crashes_enabled=0` son deliberados. Cero significa
deshabilitado, no una medición saludable. Falta calibrar cada clase con series
sincronizadas de memoria/presión y una secuencia completa de caída/recuperación.
Los 5 s y cuatro fallas del código fuente 6.18 no calibran el stack desplegado.
La lógica existe, pero habilitarla sin datos queda fuera de esta aceptación.

## Plan propuesto para aprobar

El [plan exacto de 18 nodos](../tools/ops/fmx_night_restart/production_rollout_plan.json)
está ligado por SHA al registro local del daemon. Todas sus filas están
`approved=false`, `enabled=false`; no instala nada.

| Sitio | Noche / hora Argentina inicial | Orden |
| --- | --- | --- |
| Torre Guarida | Lunes 03:10 | CPEs, luego paneles |
| Colo | Miércoles 03:40 | PtP al final de su ventana, con aprobación del responsable WAN |

Separación propuesta: `ceil(76,031 / 60) + 1 = 3` minutos por nodo. Es un margen
inicial de planificación derivado de este banco; falta medir los demás modelos.
El generador rechaza una secuencia que cruza la medianoche y convierte ART al
huso horario efectivamente verificado en cada crond.
Ejemplo equivalente: lunes 03:10 ART corresponde a lunes 06:10 en un nodo UTC.

La secuencia temporal de cron no certifica que el grupo anterior haya vuelto.
Antes de habilitar producción se debe resolver el interbloqueo de salud externo
u operacional y definir la suspensión de los siguientes grupos ante un fallo.
No hay comandos para modificar routers ni para ciclar switches.

### Instalación futura y rollback para revisión

1. Aprobar listado, sitio, horarios, indisponibilidad WAN y responsable de recuperación.
2. Validar NTP/huso, espacio en overlay, identidad y retorno de cada modelo.
3. Guardar cron y cualquier archivo previo en `/etc/fmx_rollback/`, fuera de `/tmp`.
4. Instalar `/usr/sbin/fmx-night-restart`, `/etc/fmx-night-restart.conf` y los
   archivos privados `identity.conf`, `approval.conf`, `calibration.conf` en
   `/etc/fmx-night-restart/`; verificar SHA y ejecutar `status` y dry-run.
5. El generador actual rechaza habilitar producción. Se necesita aprobación
   nueva y resolver los requisitos anteriores antes de generar una política activa.
6. Para revertir: deshabilitar primero la política, retirar sólo el bloque cron
   marcado W456, restaurar el cron y archivos previos verificados, y comprobar
   que el servicio de cron conserva los demás trabajos. No reiniciar red ni PoE.

En este banco el cron original no existía; su marcador es
`/etc/fmx_rollback/w456-night-restart/root.cron.ABSENT`.
El estado persistente quedó deshabilitado para no interrumpir al siguiente dueño.

## Verificación reproducible

```text
python -m pytest tools/ops/fmx_night_restart/test_night_restart.py -q
python tools/ops/fmx_night_restart/verify.py
```

El recibo conserva el primer fallo local (31 PASS, 3 FAIL) y la corrección
(34 PASS), además del resultado final con tests de manipulación de evidencia.
El primer fallo detectó un pin de calibración omitido y dos fixtures con CRLF.
El código nativo probado contiene las correcciones; no se borraron los fallos.

Recibo: `artifacts/autoresearch/wave456_night_restart.json`.
Gate: `artifacts/verification/wave456_lane2_night_restart_gate.json`.
La aceptación cubre el reinicio por cron en un banco y las comprobaciones locales.
El despliegue de producción requiere aprobación del operador y cierre de las
brechas señaladas; no se declara aprobado ni desplegado.
