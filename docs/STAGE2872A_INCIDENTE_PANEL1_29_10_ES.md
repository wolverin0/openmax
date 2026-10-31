<!-- doc-head: Stage 2872A (W341 P1) ES: analisis offline del incidente de Panel1 del 29/10 (15:55-18:25 UTC): cronologia desde telemetry.db y recibos, ranking de causas con evidencia a favor y en contra, cambio minimo reversible al script del AP y guarda de memoria -->
Que cubre: la cronologia del incidente, el reinicio del AP que el despacho no vio, cuatro causas candidatas, el cambio propuesto y lo que falta medir.
Estado: solo analisis. 0 SSH, telemetry.db abierta con mode=ro. Nada de lo propuesto esta aplicado: aplicarlo requiere orden del operador.
Datos maquina: artifacts/autoresearch/wave341_panel1_incident_timeline.json (todas las muestras usadas, sin MACs ni IPs completas).
Leer cuando: antes de tocar el script de persistencia de .84, de subir memoria de colas en un AP de 64 MB o de sumar sondas SSH a Panel1.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# Stage 2872A: incidente de Panel1 del 29/10 (W341 P1)

## 1. Resumen

- **Que paso.** Entre las 18:03 y las 18:20 UTC las 3 CPE de Panel1 (.41, .223, .80) dejaron de responder desde el colector. El AP .84 respondia ping por cable pero no podia atender SSH.
- **Como termino.** No fue una recuperacion espontanea: **.84 se reinicio a las 18:20:34 UTC** (±2 s). Se deduce del uptime de 289,5 s en la muestra de las 18:25:24 y del `boot_id` nuevo. Las CPE no se reiniciaron: mantienen el mismo `boot_id`.
- **Mecanismo mas probable:** agotamiento de memoria del AP (64 MB). Un dato fijo lo respalda: MemAvailable bajo de 6,5-9 MiB (28/10) a 1,9-3,2 MiB (29/10, 17:59-18:05). Las causas de esa caida son INFERRED: no hay muestras del AP entre 01:25 y 15:56 UTC.
- **Quien reinicio el AP: UNKNOWN.** Lane 3 no envio ningun comando de reinicio, y en lo guardado no hay log del kernel, de procd ni del watchdog.

## 2. Cronologia (UTC, 29/10 salvo indicacion)

| Hora | Hecho | Fuente |
| :-- | :-- | :-- |
| 27/10 18:23 | Arranque anterior de .84 (deducido de su uptime) | telemetry.db |
| 28/10 23:11-01:25 | .84 OBSERVED: MemAvailable 6480-9092 KiB, fq 3 MiB / limit 512 / quantum 3028, 3 estaciones | telemetry.db |
| 01:25-15:56 | Sin muestras del AP (hueco del daemon) | telemetry.db |
| entre 01:25 y 15:23 | El fq del AP pasa a 4 MiB / 2048 / 4542. Es la rama AP de `deploy_cpe_champion_persistence.py` ("fix de cpe_200_80"); la hora exacta no esta guardada | W337 read-back 15:23 |
| ~15:45-15:55 | W338 aplica en RAM 23 sysctl en .84 y reescribe su script y su copia hotplug, sin reload de Wi-Fi. Las estaciones siguen conectadas | gate W338 |
| 15:56 | Primera muestra del daemon reiniciado: .84 en ERROR (TimeoutError). Sigue en ERROR/BACKOFF hasta las 17:58 | telemetry.db |
| 15:57-18:02 | Las 3 CPE OBSERVED (112 muestras cada una), señal estable, ping del colector al AP 0 % de perdida | telemetry.db |
| 17:50:57 | Lane 2 detiene el daemon para actualizar el retry; vuelve a las ~17:54 | gate W339 lane 2 |
| 17:59-18:01 | .84 OBSERVED: MemAvailable 2812 / 2100 / 3176 KiB, 3 estaciones, fq_overmemory 4127 (era 4070 a la 01:25) | telemetry.db |
| ~17:55-18:05 | Lane 3 (W339): 3 preflights de solo lectura (unas 3 sesiones SSH por corrida) y 2 lecturas de diagnostico sobre .84 | notas W339 |
| PUBLIC_DEVICE_0079 | Tercera preflight de lane 3; termina con timeout de SSH | notas W339 |
| PUBLIC_DEVICE_0080 | Las 3 CPE pasan a ERROR en 3 s, con 100 % de perdida desde el colector | telemetry.db |
| 18:05 | Lectura de lane 3 en .84: load 13,22 / 7,21 / 3,35, MemAvailable 1948 KiB; el station dump volvio vacio (puede ser `iw` sin poder hacer fork, no prueba de desasociacion) | notas W339 |
| 18:05 | Lane 3 deja de hacer SSH a Panel1 | notas W339 |
| 18:06-18:12 | Ping del colector: .84 0 % de perdida; las CPE 40-80 % | notas W339 |
| 18:14-18:20 | .84 da SSHException (no entrega el banner): el puerto acepta pero dropbear no responde | telemetry.db |
| PUBLIC_DEVICE_0081 | Ping a las CPE: 5/5, 4/5, 5/5 | notas W339 |
| **18:20:34** | **Reinicio de .84** | uptime 18:25 |
| 18:25:24 | .84 OBSERVED: MemAvailable 15224 KiB, 3 estaciones, fq_overmemory 0. El script volvio a aplicar fq 4 MiB / 2048 y backlog 2048 | telemetry.db |

## 3. Causas candidatas, ordenadas

### C1. Menos margen de memoria por el fq del AP subido a 4 MiB / 2048 (antes de W338)
- **A favor:**
  - `fq_memory_limit` deja que mac80211 retenga hasta 4 MiB de skbs. En un AP que tenia 6,5-9 MiB disponibles, ese 1 MiB extra pesa.
  - `fq_limit` pasa de 512 a 2048 paquetes.
  - fq_overmemory sumo 57 eventos entre la 01:25 y las 17:59: la cola si llego al techo de memoria.
- **En contra:**
  - fq_memory_usage leia 0 en cada muestra. Es un instante y no muestra los picos.
  - El cambio es de antes de las 15:23 y el AP siguio estable hasta las 18:02.
- **Confianza:** media. **Atribucion:** Linux mac80211, por configuracion nuestra.

### C2. Carga de SSH y de sondas sobre un AP ya justo de memoria (disparador)
- **A favor:**
  - Cada sesion de dropbear y cada lectura de debugfs, `iw` o `sysctl` hace fork en un equipo sin swap.
  - El daemon volvio a las 15:56 con sondas extendidas y 3 reintentos para panel1_ap.
  - Entre las 17:55 y las 18:05 se sumaron las lecturas de lane 3. El colapso (18:03:42) cae justo al final de la tercera preflight de lane 3, y a las 18:05 la carga era 13.
  - En W337, un `sysctl -a` ya habia llevado a .84 a load 4,9 con 6 MB libres y habia cortado su SSH.
- **En contra:**
  - Las CPE aguantaron 2 h con el daemon activo.
  - Los ERROR del daemon desde las 15:56 pueden ser un timeout de 8 s demasiado corto para sondas lentas, no una inanicion: las sesiones de lane 3, con 30-45 s de timeout, si entraron a las 17:5x.
- **Confianza:** media como disparador y baja como causa de fondo. **Atribucion:** controlador externo (nuestras sondas) sobre Linux.

### C3. Los sysctl que W338 aplico en vivo en .84 (amplificador posible)
- **Cambios reales** (lectura W337 de las 15:23 contra W338):
  - netdev_max_backlog 1000 → 2048;
  - optmem_max 10240 → 20480;
  - udp_rmem_min y udp_wmem_min 4096 → 16384;
  - dev_weight 64 → 48;
  - tcp_fin_timeout 30 → 15;
  - tcp_limit_output_bytes 1 MiB → 64 KiB;
  - tcp_notsent_lowat sin limite → 8192;
  - pacing 120/200 → 110/150;
  - netdev_tstamp_prequeue 1 → 0.
- **A favor:**
  - En el peor caso, el backlog puede retener 2048 skbs (varios MiB).
  - Los minimos UDP garantizan 16 KiB por socket aun con el sistema bajo presion.
  - El primer ERROR del daemon llega 1 min despues del apply.
- **En contra:**
  - El forwarding del bridge usa NAPI, asi que el backlog casi no se usa.
  - El AP tiene pocos sockets UDP.
  - Los cambios TCP reducen memoria en lugar de sumarla.
  - Despues del apply, el AP sirvio 3 estaciones durante 2 h.
  - El hueco 01:25-15:56 impide saber si la memoria ya habia caido antes de W338.
- **Confianza:** baja-media. **Atribucion:** Linux, por configuracion de lane 3.

### C4. RF externa
- **A favor:** nada en lo guardado. Tampoco hay espectro de esa ventana (UNKNOWN).
- **En contra:**
  - Las 3 CPE cayeron en el mismo intervalo de 3 s.
  - El AP respondia ping por cable al 0 %.
  - Las señales eran estables (AP -37 a -54 dBm, CPE -40 a -53 dBm) y los tx_failed estaban quietos hasta las 18:01.
  - La salida coincide con el reinicio del AP.
  - La RF no explica que el SSH del AP fallara por cable.
- **Confianza:** muy baja.

**Lectura conjunta.** C1 y C3 reducen el margen y C2 lo agota. Ninguna se demuestra sola con la evidencia guardada. Despues del reinicio el AP volvio a la misma configuracion, asi que **el riesgo de que se repita sigue abierto**.

## 4. Cambio minimo reversible propuesto (no aplicado)

Va en el script persistido de .84 (`/usr/sbin/fmx_panel1_champion_persistence.sh` y su copia hotplug), en dos lineas de valor y una guarda:

1. `fq_memory_limit` vuelve a 3145728, el valor con el que .84 funciono mas de 30 h sin incidente. fq_quantum 4542 y fq_limit 2048 no se tocan. Asi el bloque B1 de STAGE2816A conserva su factor, ahora con techo de 3 MiB en ambos brazos.
2. `net.core.netdev_max_backlog` vuelve a 1000, el default leido en W337. El resto de las claves de W338 queda como esta: reducen memoria o no la usan.
3. **Guarda de memoria** antes de cualquier escritura que suba colas o buffers (fq, backlog, minimos UDP):

```sh
MA=$(awk '/^MemAvailable:/{print $2}' /proc/meminfo)
if [ "${MA:-0}" -lt 4096 ]; then
    logger -t fmx-champion "MemAvailable ${MA} KiB < 4096: queue/buffer raises skipped"
    SKIP_RAISE=1
fi
```

Con `SKIP_RAISE=1` el script no sube fq ni backlog ni los minimos UDP. Solo deja los valores que bajan consumo.

- **Reversion:** volver a los dos valores anteriores en el mismo script, sin reinicio y sin reload de Wi-Fi: son dos `sysctl -w`/`echo` en RAM y dos archivos en /overlay.
- **Atencion:** la copia previa que W338 dejo en /tmp se perdio con el reinicio de las 18:20. El script anterior a W338 (sha 77813923fe44) hay que reconstruirlo desde `deploy_cpe_champion_persistence.py`. La copia del repo `tools/panel1/fmx_panel1_champion_persistence.sh` es mas vieja (fq 3 MiB, sha 40487229279c) y no es el script del equipo.

**Guarda operativa (pertenece a lane 2 y a lane 3, propuesta):**
- una sola sesion SSH a la vez sobre panel1_ap;
- sin reintentos cuando la muestra anterior leyo MemAvailable < 3 MiB;
- nunca `sysctl -a` ni lecturas completas de debugfs en APs de 64 MB.

El runner A/B de W340 ya rechaza una noche con MemAvailable < 2 MiB.

## 5. Que falta para cerrar la causa

- **Muestras de MemAvailable de .84 cada 1-5 min durante 24 h tras el reinicio**, sin otras sondas. Si la memoria vuelve a caer sin carga SSH, gana C1 o C3; si se mantiene, gana C2.
- **`logread` y `dmesg` de .84 despues del reinicio:** si la causa fue OOM, panic o el watchdog de procd, deberian quedar huellas. Esta lectura necesita una ventana de SSH, de una sola sesion y autorizada.
- **Si .84 guarda contadores de reinicio del watchdog de hardware.** Por ahora UNKNOWN.

## 6. Limites

- No hubo SSH en esta etapa. Todo sale de telemetry.db (abierta con mode=ro), de los gates W338/W339 y de las notas de lane 3.
- Las horas de la tabla son las de las muestras: ±1 ciclo del daemon (~60 s).
- La hora del reinicio sale del uptime: ±2 s.
- Labels con los dos ultimos octetos; sin MACs ni nombres de abonados.
