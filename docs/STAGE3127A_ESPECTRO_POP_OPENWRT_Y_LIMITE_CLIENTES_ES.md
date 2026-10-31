<!-- doc-head: Wave 460; variantes spectral, FFT en canal en LiteBeam de banco y motor por POP en modo recomendación -->
Capturas físicas y coste de gestión local; coste RF con clientes pendiente de liberar W457.
Ninguna escritura de producción, retune, scan ap-force ni cambio automático de canal.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Espectro por POP en OpenWrt

## Qué se reutilizó

FMX-0010/0011 ya demostraron spectral en LAP-120 y conservaron la receta de
`futuramax-r28959-spectral`. No se repitió ese descubrimiento ni se presentó su
captura histórica como nueva. La ABI actual se contrastó con el header retenido
y con [spectral.c de ath10k-ct](https://raw.githubusercontent.com/greearb/ath10k-ct/ac71b14d/ath10k-6.10/spectral.c).
La copia local tiene SHA `467b333b57b6e19afb3ae262fb7e3691cfa8bfab7f3c17579bc1b689c6a7456d`.

El protocolo propietario de ubntspecd depende de `ubnt_poll_host` y
`/dev/uph_wifi0`. Esta implementación usa la interfaz pública debugfs/relay de
ath10k; no presupone que aquel ejecutable funcione en OpenWrt.
DEC-013 sigue vigente: no hay `iw scan ap-force`, barridos fuera del canal ni
retunes en el colector. Medir otros canales requiere otro receptor o una ventana aprobada.

## Dos pistas de imagen

Las variantes están en `firmware/openwrt/2410_bp_spectral/` y
`firmware/openwrt/2512_bp_spectral/`. Cada una conserva los parches de estabilidad
y WDS de su pista base, añade spectral y el colector persistente, sin init ni autostart.
Los hashes, tamaños, logs y extracciones están en sus `build_evidence.json` y `SHA256SUMS`.

| Pista | Modelos | Factory, rango de bytes | Estado |
| --- | ---: | ---: | --- |
| 24.10.4 + backport + spectral | 5 | 6816408–6947480 | Build/extracción offline verificados |
| 25.12.6 + backport + spectral | 5 | 7209624–7275160 | Build/extracción offline verificados |

Hay 10 factory y 10 sysupgrade finales. El colector empaquetado tiene SHA
`1e03793b32cb29f97bfa59c1060c2fbfc88a29337c49c305ae1d1da8f7a18099`.

La advertencia histórica sobre RELAY se verificó contra estos artefactos:
los kernels reales de ambos ImageBuilder ya contienen sus símbolos y los SDK
exportan RELAY. Se conserva el kernel/ABI oficial y se compilan los drivers con
`ATH_DEBUG` y `ATH_SPECTRAL`. ImageBuilder sólo ensambla después; no habilita
spectral por sí solo ni sustituye la compilación del SDK.

El verificador exige cinco perfiles por pista y factory/sysupgrade reales,
extracción rc=0, módulos MIPS con vermagic correcto, WDS idéntico al track y el
hash del colector dentro del SquashFS. La partición usada en el presupuesto es
`0xf60000 = 16121856` bytes; el espacio restante calculado no prueba RAM libre.
Es el presupuesto de la receta base: sólo se leyó MTD vivo de .116, no de cada
modelo de producción. Hay que verificar geometría y particiones del destino antes de flashear.
Los nuevos tracks no se flashearon ni arrancaron en esta ola. El banco ya tenía spectral.

## Colector acotado

Fuente final offline: `tools/spectral_pop/fmx-pop-spectral-collect.sh`.
El banco conserva una revisión anterior inactiva en `/usr/sbin/fmx-pop-spectral-collect`;
el Orquestador congeló más escrituras. Sin parámetros sólo inspecciona.
Una captura requiere `capture phy0 --apply`, memoria suficiente y control
inicial `disable`; no se apropia de una captura ajena.

Modo manual, cuenta uno, espera configurada de 100 ms y separación mínima de 60 s.
El guardián publica readiness con PID/starttime/SID y vigila directamente al reader.
Tras GO, sondea hasta 1 s y espera 2 s antes de actuar; no es una cota de tiempo real.
El cleanup sólo desarma el guardián tras restauración y readback correctos.
No usa PID=SID como criterio BusyBox. La espera configurada no es duración exacta:
el código final expone los instantes de uptime del intervalo de control, no airtime RF.
La calificación nativa de esta revisión final está pendiente.

| Recurso | Límite o medición |
| --- | --- |
| Raw de una lectura | Menos de 65536 B; llegar al cap rechaza el resultado |
| Raw temporal máximo | Tres archivos de hasta 64 KiB, incluyendo reemplazo |
| Capturas en flash | Cero; sólo `/tmp` |
| Runtime final offline | 7805 B, sin autostart; revisiones previas preservadas |
| Directorio temporal final observado | 16 KiB asignados |
| Piso para iniciar captura | MemAvailable 6144 KiB, no umbral de reboot |
| Temporizador corregido | 0,11 s observado con `/proc/uptime` para `ucode sleep(100)` |

El cap del archivo **no es el coste total de kernel**. La fuente pide un relay
global por PHY de `1140 × 2500 = 2850000` B, más alineación y metadatos.
El callback marca `is_global=1`; no se multiplica por CPU. Se reserva al crear
spectral y sólo se libera al destruirlo; `disable` no libera ese buffer.
Las variantes no quedan aprobadas para equipos de poca memoria por caber en flash.

## Datos físicos nuevos

Se usó exclusivamente el LiteBeam .116, OpenWrt 24.10.4/kernel 6.6.110.
Ya exponía `phy0/ath10k/spectral_scan0`, por lo que no hizo falta flashear.
Los dos pulsos de la segunda campaña dieron un frame real de 93 bytes cada uno, en 5180 MHz,
64 bins y span FFT 22 MHz, correspondiente al canal nominal de 20 MHz.
Los TSF crecieron 60913951 microsegundos entre capturas; no se interpretan como UTC.

El parser valida tipo 3, metadata de 26 B, TSF unsigned64, longitud y presupuesto.
Truncamientos y basura se rechazan sin resincronización silenciosa.
El bin DC interpolado por el driver se conserva crudo pero se excluye del proxy.
Se informa noise del driver como signed16, con calibración absoluta desconocida.
El proxy de bins dentro de 10 dB del pico mide forma espectral, **no ocupación temporal**.

La ocupación temporal se obtiene por separado de deltas `iw survey dump`.
Sin `BSS receive time`, `U_dirty` es una cota superior que incluye RX no clasificado.
Los otros canales que aparecen en la caché del survey no avanzaron en este ensayo:
su edad es desconocida y no se presentan como un mapa nuevo de todo el POP.

## Ensayo de coste y límite de aceptación

Campaña histórica normal de la revisión `51ba0fd8`: C1/C2, luego A1/B1/A2/B2; ventanas de 30 s,
con un pulso sólo en B. Un dispositivo y repeticiones temporales no equivalen a
replicación independiente de distintos POPs. Se aplicó la habilidad experimental-design.

| Medida | Control A | Ventana con pulso B |
| --- | ---: | ---: |
| CPU ocupada media | 2,258% | 3,913% |
| Softirq media | 1,710% | 1,768% |
| Pérdida de gestión | 0% | 0% |
| p95 de gestión nativo | 0 ms | 0 ms |

Estos costes pertenecen a esa revisión previa, no al helper final corregido.
El incremento descriptivo de CPU fue 1,655 puntos porcentuales; la diferencia
entre los controles nulos fue 0,761 puntos. No se declara coste cero ni una
prueba formal de no inferioridad. El RTT entero de Windows está bajo su resolución,
no físicamente en cero. MemAvailable mínimo en los extremos de las ventanas: 6500 KiB.
Una inspección posterior dio 6116 KiB y el diagnóstico siguiente aproximadamente
6108 KiB con SSH activo. El arnés abortó la tercera campaña ANTES de otro pulso
por estar bajo 6144. Limpiar nuestras capturas archivadas no recuperó margen;
no se bajó ese piso para obtener un PASS.

La gestión fue PC→Ethernet del banco, no carga OTA. Por instrucción del
Orquestador `<orca-id>`, no se generó tráfico RF mientras W457 usa su AP.
El coste con clientes sigue **PENDING_W457_RELEASE** y debe medirse A/A con
tráfico acotado desde .116 al peer que libere el Orquestador.
`<orca-id>` ordenó cerrar PARTIAL sin reiniciar ahora. La siguiente ronda
hará un soft reboot autorizado de .116 cuando W457 libere el AP, instalará el
helper final y validará captura/guardián/coste RF. No hay permiso para reiniciar antes.

## Recomendación por POP

`tools/spectral_pop/recommend.py` conecta los motores existentes de ancho y
geometría por sitio sin modificarlos. El CLI admite un POP o una lista de POPs,
mantiene site_id separados y preserva la guarda co-sitio de 15 MHz.
No convierte bins relativos en U_dirty ni permite `--apply`.

FFT se adjunta como diagnóstico. Los requisitos del motor de ancho siguen
vigentes: encuestas suficientes de hora pico, reloj verificado, calibración y
vecinos correctos. Los timestamps no verificados del banco no habilitan ensanches.
El resultado del banco es HOLD por evidencia insuficiente; cambiar frecuencias
sigue necesitando evidencia multicanal, regulación y aprobación del operador.

## Fallos conservados y reproducción

El primer colector obtuvo FFT, pero BusyBox rechazó `sleep 0.1` y la salida
incorrectamente siguió en cero. Ese intento está marcado `timing_valid=false`,
con sus fuentes y capturas; no valida los 100 ms. Se corrigió con ucode y
propagación explícita del error, y se ejecutó una campaña nueva completa.
También quedó registrado un error de nombre de propiedad en la derivación offline.
Los fallos de build y extracción se conservan en la evidencia de cada pista.
La revisión encontró además cleanup que cancelaba el guard ante fallo, readiness
ausente, reader sin PID/start y un derivador que aceptaba fases omitidas, rc fallido
y NaN. Las regresiones reprodujeron estos casos; `<orca-id>` autorizó una
corrección offline adicional y reensamblado, sin tocar radios. La nueva revisión
rechaza esos casos; esto no reemplaza la validación física pendiente.
Resultado final: 373 pruebas PASS y una omitida por privilegio de symlink en
Windows. Los siete fallos de regresión reproducidos antes del último arreglo
quedaron conservados en `pytest_review_regressions.xml`.

```text
python -m pytest tools/spectral_pop/test_fft.py tools/spectral_pop/test_recommend.py -q
python tools/spectral_pop/summarize_bench.py
python tools/spectral_pop/verify.py
```

Recibo: `artifacts/autoresearch/wave460_spectral_pop.json`.
Gate: `artifacts/verification/wave460_lane2_spectral_pop_gate.json`.
El gate declara `status=CONFIRMED`, `completion=PARTIAL` y `full_gate_passed=false`:
confirma evidencia y límites, no cumplimiento completo. No aprueba
despliegue de producción, nuevos tracks en hardware ni cambios automáticos de canal.
