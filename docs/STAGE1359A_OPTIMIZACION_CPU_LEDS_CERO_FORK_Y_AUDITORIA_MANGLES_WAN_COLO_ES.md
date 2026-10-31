<!-- doc-head: Wave53: CPU de indicadores, paquetes v17/WA v7 y auditoría COLO de sólo lectura -->
Ambos PowerBeam cumplen CPU medida <0.5% y <1%, conservando cuatro barras reales.
El bucle elimina procesos de filtrado; mantiene iw y mv para publicación atómica.
La auditoría del router no ejecutó cambios ni demostró drain100/fallback MAIN.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 1359A — Indicadores y auditoría WAN COLO

La versión final se desplegó en `.241` AP y `.242` STA. Usa `POLL_SEC=10`,
parsing builtin, descubrimiento inicial y un `iw station/link` por ciclo.
Los hijos AP/VLAN se redescubren mediante sysfs sin repetir `iw dev`.
La muestra representa la interfaz elegida; no se atribuye a todos los clientes
de un panel simultáneamente. Las placas de un LED indican asociación.

## CPU observada y criterios

Se mide `utime+stime+cutime+cstime` del daemon —padre más hijos esperados—
dividido por el delta de los ocho primeros contadores `/proc/stat`.
Cada intervalo dura al menos 60 s; excluye arranque y no genera carga de prueba.
Las metas son estrictas: **<0.5% preferida/headline**, **<1.0% mínima**.

| Fase preservada | AP CPU % | STA CPU % | Alcance |
| --- | ---: | ---: | --- |
| Legacy original en reposo | 5.9087 | 4.7633 | antes de la primera actualización |
| V2: builtin parsing/cadencia/cache | 0.9433 | 0.8670 | cumple mínima, falla preferida |
| V3: parsing en memoria/btime cache | 0.8843 | 0.8389 | cumple mínima, falla preferida |
| V4 final: lectura acotada de trigger | **0.4508** | **0.3681** | cumple ambas metas |

Final AP: 50/11092 ticks, 110.92 s; STA: 39/10594 ticks, 105.94 s.
Las fases previas, sus fuentes exactas y RAW permanecen archivados; se cambió
código entre fases, sin repetir la misma muestra para seleccionar un verde.
La comparación es secuencial en reposo. Wave48 empleó carga TCP/UDP/ICMP;
sus porcentajes cargados no son un baseline equivalente a estas mediciones.

## Lectura real y coste del bucle

Ambos equipos mantuvieron cuatro barras AUTO al inicio/final, RSSI por encima
del umbral bench65 y lecturas sysfs `1,1,1,1`. El contador de escrituras de brillo
permaneció `0→0`; los contadores de polls pasaron `1→12` en AP y `1→11` en STA.
Colas, canal, configuración RF, boot y contadores de reinicio permanecieron iguales.
La confirmación visual humana sigue siendo UNKNOWN.

El trigger se valida cada ciclo. BusyBox permite leer siete caracteres para
comprobar el selector inicial `[none]`; plataformas sin esa opción usan lectura
POSIX completa. No se omite el control del trigger para reducir CPU.
El reloj JSON usa uptime y btime cacheado, con actualización periódica;
su redondeo entero puede quedar hasta un segundo detrás de `time()`.
El consumidor rechaza timestamps obsoletos ante cambios de reloj.

El ciclo elimina `awk/sed/grep/tr/cut/cat/date`; ejecuta un `iw` y un `mv`.
`mv` conserva la publicación atómica del JSON.
En los radios la espera usa FIFO privado y `read -t` builtin; la alternativa
POSIX emplea `sleep` y queda declarada en `wait_backend`.

## Paquetes y compatibilidad

El packager nuevo sincroniza exactamente el mismo v4 en los overlays v17 y
WA v7, con perfil empaquetado de producción60 y `POLL_SEC=10`.
El bench conserva su override65. TAR declara shell0755/config0644 y el primer
arranque habilita/inicia procd. SHA256SUMS conserva filas ajenas e imágenes.
Los recibos/docs históricos 1304/1327 quedan intactos; payload/TAR/manifiestos
anteriores se conservan por hash. No se reconstruyeron ni flashearon imágenes.
El JSON conserva campos originales y aliases `rssi0..3`, y añade métricas
tipadas de cadence/procesos/cache y `sysfs_name` coherente con el readback.

## Router COLO: alcance realmente auditado

La API autorizada de `198.18.0.44` informó **MK2-RS** y mostró
`198.18.0.2/24` como dirección local, probando ese alias en el mismo equipo.
Se capturaron **ocho reglas COLO** antes/después sin cambios de configuración;
sus contadores pudieron avanzar. Tres selectores LAN funcionales fueron
`*1BA`, `*1BB`, `*172`; no se exige un comentario literal CLIENTCOLO.

| ID activo | Acción | Selector / destino |
| --- | --- | --- |
| `*1BA` | `mark-connection` | `bridgeLAN`, nueva conexión sin marca, PCC `both-addresses:21/13` → `isp12_conn` |
| `*1BB` | `mark-connection` | `bridgeLAN`, nueva conexión sin marca, PCC `both-addresses:21/14` → `isp12_conn` |
| `*172` | `mark-routing` | `bridgeLAN`, conexión `isp12_conn` → tabla `to_isp12` |

La ruta COLO observada usa `198.18.0.119%ether10-colo` en `to_isp12`.
Los extremos PtP-Colo solicitados son `198.18.0.91` y `198.18.0.92`;
esas direcciones de radio no sustituyen el gateway observado del router.

Una muestra real de `ether10-colo` informó RX **30,686,128 bps / 2883 pps**
y TX **1,319,360 bps / 1058 pps**. Son tasas de interfaz, no tasas por regla.
Se preparó CLI reversible con IDs/precondiciones, **sin ejecutarlo**.
Cero mutaciones, cambios PoE o acciones sobre radios desde esa auditoría.

Los comandos exactos, con precondiciones y IDs, quedan como scripts de un
solo bloque RouterOS para que un error previo impida ejecutar el resto:

- [Plan de deshabilitación, no ejecutado](../artifacts/verification/stage1357a_wan_colo_drain_plan.rsc)
- [Rollback limitado, no ejecutado](../artifacts/verification/stage1357a_wan_colo_drain_rollback.rsc)

El rollback restaura únicamente las tres reglas antes habilitadas. Se excluyen
las reglas inbound, output y sondas; no se vacían conexiones ni NAT.

**Drain100 no verificado**; el fallback de tráfico hacia MAIN es
`UNKNOWN_NOT_CAPTURED`. Preparar comandos no demuestra un drenaje completo,
ni autoriza aplicarlos sin el preflight correspondiente.

## Evidencia

- [CPU viva 1356A](../artifacts/verification/stage1356a_zero_fork_rssi_led_cpu_optimization.json)
- [Router 1357A](../artifacts/verification/stage1357a_mikrotik_wan_colo_mangle_and_route_audit.json)
- [Paquetes 1358A](../artifacts/verification/stage1358a_v17_and_wav7_zero_fork_led_sync.json)
- [Gate 1361A](../artifacts/verification/stage1361a_wave53_codex2_gate.json)
