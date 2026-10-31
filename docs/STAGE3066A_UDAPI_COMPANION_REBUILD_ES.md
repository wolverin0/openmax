<!-- doc-head: W406: rebuild musl MIPS32 BE del companion, fuente fijada y 28 tests host con baseline HOL reproducido -->
Fuente 20366 B SHA256 4a77a6c6d1cfaefc06347b124cabe186d9463c32f1ca790af851232d6b1241f8 intacta antes/después.
Binario 67544 B SHA256 93d1addd73acf20d00c8e51a8e86003c85130f2519b6c0e568e72a9499368720.
28/28 tests Linux host, cero skips; el código anterior reproduce TimeoutError en el segundo cliente con el fixture corregido.
Solo build y fixtures locales: sin acceso a equipos ni ejecución del binario MIPS.
<!-- /doc-head -->
# W406 — Companion UDAPI recompilado

Artefacto: `artifacts/ground_up/udapi_companion_build/w406/udapi_cache_server.mipsbe-musl-static`; SHA en el archivo `.sha256` adjunto. El recibo `build_receipt.json` fija fuente, snapshot, compilador, librerías, comandos, tamaños y hashes. Un intento de compilación, sin reparaciones.

Se reutilizó la receta exacta de W396/W380: SDK OpenWrt, `mips-openwrt-linux-musl-gcc` 13.3.0, `-Os -mips32r2 -mabi=32 -EB -msoft-float -static`, warnings como errores, stack protector y fortify. Solo cambian las rutas de entrada/salida/map. `file` y `readelf` confirman ELF32 MSB, MIPS32r2, o32, soft-float, sin intérprete ni dependencias dinámicas. El mapa enlaza librerías del SDK, no del cross-toolchain Debian.

`host/host_receipt.json` conserva la ejecución nueva de los fixtures. Se fijaron también `test_udapi_transport.py` (15995 B, SHA256 `672a593ec94e49565bfebfe3df7ca6af3406505a31a2a8ae7ac8fe23ec7f98ce`) y `baseline_serial.c` (17365 B, SHA256 `57e250b24f33a23ae6fd2f704413e1b01aa99a1e8e404607feb00766a543d015`). Las tres entradas coinciden antes/después y tienen copias congeladas.

| Verificación nueva | Resultado |
| --- | --- |
| Compilación host baseline/current con flags de W400 | Ambas rc=0 |
| Fixture HOL corregido contra baseline serial | rc=1 esperado: `TimeoutError: timed out` en `Reader(second).reply()`; un test, 1,068 s |
| Suite completa contra el host del C nuevo | rc=0; 28 tests, 28 OK, cero skips; 11,793 s de proceso |
| Fuente, suite y baseline después de los tests | Pines idénticos |

El `frozen_source_receipt.json` de W400 preserva un intento anterior de 27/28, un `TypeError` del fixture y un bloqueo WSL posterior. Ese error previo ocurría antes de operar el segundo socket y no demostraba HOL. Se mantuvo esa evidencia; W406 usa el fixture ya corregido y reproduce el timeout real en el baseline antes de pasar los 28 tests del código nuevo.

Los tests usan sockets AF_UNIX y cachés desechables en Linux local. No ejecutan código MIPS, no validan asociación RF, UISP remoto ni memoria/RTT de un CPE. Los objetivos Karpathy RF no son evaluables en este contrato offline. La aceptación cubre build estático y comportamiento host del mismo fuente fijado; cualquier aceptación física requiere su propio recibo.

Gate: `artifacts/verification/wave406_lane4_companion_rebuild_gate.json`. El recibo de revisión independiente está bajo `w406/review/`. Tras entregar W406 se retoma W402 con sus evidencias estáticas preservadas.
