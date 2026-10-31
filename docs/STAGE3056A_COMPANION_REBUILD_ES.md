<!-- doc-head: W396 rebuild offline del companion con fuente57e250b2 y receta OpenWrt musl W380 -->
Fuente17365B verificada antes/despues; copia de compilacion identica.
Binario69400B ELF32 MSB, MIPS32r2/o32, soft-float, estatico.
Misma receta/compiler W380; sin reutilizar aceptacion runtime anterior.
Sin equipos, SSH, red, QEMU, instalaciones ni reinicio WSL.
<!-- /doc-head -->

# W396 / Stage3056A: rebuild urgente del companion

Binario: `artifacts/ground_up/udapi_companion_build/w396/udapi_cache_server.mipsbe-musl-static`.
SHA-256: `1647b4a4de469f2e284d4f6c6a8ffc6eed8bf3a4755ad0f2e1fbf5502522001f`.
Tamano: **69400 B**; sidecar `.sha256` junto al ejecutable.

Fuente original readonly: `tools/uisp_bridge_openwrt/udapi_cache_server.c`,
**17365 B**, SHA `57e250b24f33a23ae6fd2f704413e1b01aa99a1e8e404607feb00766a543d015`.
El snapshot `w396/source/udapi_cache_server.c` y el original coinciden con ese
pin antes y despues. No se editaron fuentes de lane_2 ni builds anteriores.

Compiler OpenWrt GCC13.3.0, mips_24kc musl, SHA
`8bc9eb688f660839e55606d8e9fd278ee98029005de8096a540949c6dc9541e9`.
Receta exacta de W380: `-std=c99 -Os -mips32r2 -mabi=32 -EB -msoft-float`,
`-Wall -Wextra -Werror -fstack-protector-strong -D_FORTIFY_SOURCE=2`,
`-static -Wl,--fatal-warnings`. Solo cambian paths de fuente, salida y map.
Compilacion intento1 rc0. Se guardan14comandos, logs y linker map con ocho
objetos/archivos SDK fijados por SHA, incluyendo libc/libgcc y libssp_nonshared.

`file` y `readelf -h -A -l -d` confirman ELF32MSB/MIPS32r2/o32,
FP ABI Soft float, CPR1size0, flags0x70001005, sin INTERP ni NEEDED.
Se conserva el binario sinstrip para inspeccion. El tamano de archivo no es RSS.

Recibo de build: `artifacts/ground_up/udapi_companion_build/w396/build_receipt.json`.
Pin de fuente: `artifacts/ground_up/udapi_companion_build/w396/source_pin.json`.
Revision independiente y gate cierran solo compilacion y ABI estaticos.
No se ejecutaron QEMU, companion o dispositivos; integracion y rendimiento
fisicos no se validan por este gate. W390 se retoma despues del reporte.

Gate: `artifacts/verification/wave396_lane4_companion_rebuild_gate.json`.
