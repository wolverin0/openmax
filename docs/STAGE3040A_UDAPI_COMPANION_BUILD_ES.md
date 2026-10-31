<!-- doc-head: W380 binario UDAPI ath79 construido con SDK musl; ABI y ejecucion local separadas de hardware -->
PARTIAL global: build/ABI y20 tests PASS; suite QEMU explicita y procedencia SDK pendientes.
Fuentes lane_2 intactas; snapshots, comandos, linker map y fallos retenidos.
CLI QEMU 24Kc/74Kf rc2 esperado; la fuente carece de --help/--selftest internos.
Ensayo de transporte y aceptacion final en recibos; sin equipos ni cambios al Orchestrator.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# W380 / Stage3040A: companion UDAPI para ath79

**PARTIAL global.** Compilacion y veinte tests funcionales emulados PASS.
Faltan la suite bajo qemu-mips-static identificado y completar la evidencia
de release/config y tres objetos del SDK. La revision independiente coincide.

Alcance: build offline del companion de lane_2 con el toolchain OpenWrt musl
existente. No hubo SSH, acceso a dispositivos, despliegue, instalaciones, descargas,
reinicio de WSL ni cambios a las fuentes o al estado del Orchestrator.
Atribucion: external controller para compilacion; Linux userspace para servidor
local y fixtures; ninguna aceptacion de hardware o UISP.

## Artefacto y fuentes

Binario: `artifacts/ground_up/udapi_companion_build/w380_sdk_musl/udapi_cache_server.mipsbe-musl-static`.
**69176 B**, SHA-256 `1e216ca0f2a29c2b03fed4d666821ea726f93bc69e4f019888a4a42514d629f3`.
El sidecar `.sha256` queda junto al ejecutable. Se conserva tambien el ELF sin
strip (357556 B) y el linker map para inspeccion. Las doce secciones alloc
coinciden entre las versiones stripped/unstripped, verificado independientemente.

| Fuente original de solo lectura | Bytes | SHA-256 |
| --- | ---: | --- |
| udapi_cache_server.c | 16759 | dcb18dfea4003180dbe3cc40260210e5ecceb4d3967ab9fa862f8f9379918686 |
| build_udapi_cache_server.py | 14319 | c88ef6d777aa382a19a267ad2ccae6ba217d064009e48a21fd1886c7685b7199 |
| test_udapi_transport.py | 11621 | c622e6fdd451f2a8886b3a0f1964e6ee473cfdbbe4d1433625e74ffaa0c5d0da |

Originales, snapshots bajo `w380_sdk_musl/source/` y manifiesto coinciden.
La fuente de intentos anteriores tenia 16286 B y otro hash: no se reutilizaron
sus resultados como pruebas del binario actual. El builder original escribe en
el directorio de lane_2 y apunta a otra ruta; esta wave usa runners aislados.

## Toolchain y enlace

Toolchain local: `<wsl-home>/futuramax/night-20261007-reproduce/staging_dir/toolchain-mips_24kc_gcc-13.3.0_musl`.
Compiler: `mips-openwrt-linux-musl-gcc`, OpenWrt GCC 13.3.0, revision
`r28959-29397011cc`; SHA `8bc9eb688f660839e55606d8e9fd278ee98029005de8096a540949c6dc9541e9`.
No se uso GCC cross de Debian para compilar este ELF.

Flags decisivos: `-Os -mips32r2 -mabi=32 -EB -msoft-float -static`,
`-Wall -Wextra -Werror -fstack-protector-strong -D_FORTIFY_SOURCE=2`,
`-Wl,--fatal-warnings` y linker map. Compilacion intento1 rc0, sin warnings.
`link_inputs.json` conserva hashes de libc.a, libgcc.a y crt1/crti/crtn del SDK;
libc.a: `9e8a85b823a966d6b4e2c44a44760a8dbe21f1cab2814c47469fa45e6d81f455`,
libgcc.a: `93a3f51660cf4e955ceb589981c54de22bd3cfe648e2a255e456d8eb70329f59`.
El mapa incluye ademas crtbeginT/crtend/libssp_nonshared del mismo toolchain:
sus hashes independientes y el refresco de configuracion/release exacta del SDK
quedaron pendientes por el fallo del transporte WSL. No se presenta esa lectura
como realizada. La evidencia del compilador y del enlace se conserva completa.

## ABI y tamano

`file` informa ELF 32-bit MSB executable, MIPS32 rel2, statically linked, stripped.
`readelf -h -A -l -d` confirma o32, flags `0x70001005`, MIPS32r2, FP ABI Soft float,
CPR1 size 0 y ausencia de INTERP/dinamica/NEEDED. El label generico Machine MIPS
R3000 es EM_MIPS; la ISA procede de flags y ABI flags, no de ese label.
La revision independiente tambien parsea estos campos desde bytes en Windows.
`.text` 49904 B; `.rodata` 12920 B; `.bss` 524784 B. El tamano de archivo
no es RSS: stack, paginas, buffers kernel y procesos auxiliares quedan fuera.

## Ejecucion local, fallos y limites

La fuente no implementa --help ni --selftest. --help y ausencia de argumentos
devuelven 2, observado explicitamente con qemu-mips-static en CPU 24Kc y 74Kf,
sin SIGILL. Ese rechazo no es un selftest funcional aprobado.
La prueba funcional externa reutiliza los veinte tests AF_UNIX existentes:
siete GET/metadata, framing prefijado/raw/NUL, fragmentacion/pipeline, rechazos
de escrituras/INTERNAL, JSON estricto, traversal/symlink, caches viejas, limites,
regulatory explicito y reemplazo atomico. Solo el ejecutor y directorio temporal
cambian en el harness; C y tests originales permanecen intactos.

Fallos retenidos: probe inicial de shell con quoting incorrecto; expectativa
incorrecta de rc0 para `qemu -cpu help` (devuelve 1 y lista CPUs); veinte fallas
de setup AF_UNIX en DrvFS; WSL/Service/WSAETIMEDOUT antes de observar la suite
corregida y la revision independiente. No se reinicio WSL ni se afirma conocer
el estado del invitado a partir de un timeout. Los veinte fallos de bind no
prueban un defecto del dispatcher: no llegaron a ejercitarlo.

Como alternativa local se uso Docker con imagen existente, `--pull never`,
`--network none` y contenedores descartables. La CLI del ELF y un arranque/parada
del servidor dieron rc2 y rc0 respectivamente, con socket retirado. El directorio
binfmt del contenedor estaba vacio: no se inventa CPU ni identidad del interprete.
Los intentos de leer el ELF desde el bind mount y de capturar /proc/PID/exe dieron
ENOMEM; aumentar el limite de 256 MiB a 1 GiB no lo resolvio. Se conservaron
ambos resultados y los inputs congelados se transfirieron por stdin al filesystem
nativo del contenedor. Esos limites de contenedor no son consumo del companion.

La revision independiente ejecuto los **20 tests: PASS, cero fallos, errores u
omisiones** en un contenedor descartable x86_64 con el ELF MIPS por ejecucion
foreign-ELF implicita. Los hashes de binario y tests coinciden antes/despues.
Se conserva `review/docker_functional_attempt1_receipt.json` y el log completo.
La identidad del interprete y la CPU de ESA suite siguen UNKNOWN: no se atribuye
a qemu-mips-static ni a 24Kc/74Kf. Es distinta de la CLI QEMU explicita anterior.
No se ejecuto el companion en radios ni se midieron RSS, goodput o RTT.
Los objetivos Karpathy requieren hardware y permanecen NOT_EVALUATED_OFFLINE.

## Recibos y continuacion

- Cierre del coordinador: `artifacts/ground_up/udapi_companion_build/runtime_recovery/final_build_receipt.json`.
- Revision final: `artifacts/ground_up/udapi_companion_build/review/final_independent_review.json`.
- Build congelado: `artifacts/ground_up/udapi_companion_build/w380_sdk_musl/build_receipt.json`.
- Suite funcional independiente: `artifacts/ground_up/udapi_companion_build/review/docker_functional_attempt1_receipt.json`.
- Revision independiente: `artifacts/ground_up/udapi_companion_build/review/independent_windows_review.json`.
- Alternativa Docker y fallos: `artifacts/ground_up/udapi_companion_build/runtime_recovery/`.
- Gate: `artifacts/verification/wave380_lane4_udapi_companion_build_gate.json`.

El siguiente paso permitido para runtime exige un despacho especifico de banco;
esta wave no autoriza instalar o iniciar el binario en un equipo.
