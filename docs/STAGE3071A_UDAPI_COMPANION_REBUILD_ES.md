<!-- doc-head: W411: companion musl MIPS32 BE, fuente e354 fijada y 33 tests host nuevos -->
Fuente 25500 B SHA256 e354c9f1b26ca1fe94a37856ad8e2fee31ecc7a1c42ebef5b5190aaab399480d intacta antes/después.
Binario 68312 B SHA256 4f08fce7196436632afe01206a03808e455f02624aa89bd38642973075a96833.
Suite W407 sin modificar: 33/33 OK, cero skips; sólo build y fixtures locales, sin acceso a equipos.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# W411 — Rebuild del companion de W407

Artefacto: `artifacts/ground_up/udapi_companion_build/w411/udapi_cache_server.mipsbe-musl-static`, con `.sha256` adjunto. Un intento de compilación exitoso, sin reparaciones. `build_receipt.json`, `source_pin.json`, `commands.json` y `final_readback.json` conservan los pines, comandos y lecturas finales.

Receta exacta W406: compilador OpenWrt SDK musl GCC 13.3.0; `-Os -mips32r2 -mabi=32 -EB -msoft-float -static`, warnings como errores, stack protector y fortify. Sólo cambian los paths de entrada/salida/map. `file` y `readelf` confirman ELF32 MSB, MIPS32r2, o32, soft-float, sin PT_INTERP ni DT_NEEDED. Los ocho proveedores LOAD del mapa coinciden por SHA con W406.

El host usa el mismo C congelado y el suite `test_udapi_transport.py`, 20301 B, SHA256 `13bd9c4f071427d38eaf479729064dd077c1787f1cc7fe8c6c11c95b62e9a412`. Se fijó también el recibo de lane_2 `build/w407_host/test_receipt.json` (6867 B, SHA256 `e61c42bcc1d0da4891de7650879cf1bda6d99e7ef9bf94a1151190cbfbe00546`). Las tres entradas coinciden antes/después y tienen snapshots en `w411/host/`.

Ejecución nueva Linux: compilación host rc=0; suite completa rc=0, 33 tests OK, cero skips, 13,053 s de proceso. `host/host_receipt.json` y `host/tests_33.log` conservan resultado y comandos. Los fixtures AF_UNIX/caché son desechables; no se ejecuta el binario MIPS. El baseline 405 de PUT/services contra fuente 4a77 se conserva como evidencia reutilizada del recibo W407; no se volvió a ejecutar ni se usa para aceptar el candidato.

El gate acepta build estático y comportamiento host del fuente fijado. Runtime MIPS, memoria real del CPE, UISP remoto, asociación y métricas RF permanecen UNKNOWN; el objetivo Karpathy físico no se evalúa en este contrato offline. No se modificaron el C original, los builds anteriores ni el estado del orquestador.

Gate: `artifacts/verification/wave411_lane4_companion_rebuild_gate.json`. Revisión independiente: `w411/review/`. Ruta, SHA y tests enviados exclusivamente al orquestador mediante `<orca-id>`. La siguiente prioridad autorizada es W409 LTU; W402 permanece preservado en cola.
