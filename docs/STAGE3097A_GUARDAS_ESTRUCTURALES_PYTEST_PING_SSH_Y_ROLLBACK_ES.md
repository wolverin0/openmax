<!-- doc-head: Wave 437 centraliza guardas de evidencia, ping, SSH y restauración -->
Validación offline con fixtures desechables; cero acceso a dispositivos.
Recibos históricos inmutables, A/A y aceptación física fuera de esta prueba.
<!-- /doc-head -->

# Stage 3097A: guardas estructurales

## Evidencia y pytest

`tools/common/gate_integrity.py` verifica pins antes de ejecutar y antes de publicar.
Sin flags, o con `--no-write`, evalúa sin escribir el recibo.
`--write-receipt --receipt NUEVA_RUTA` crea un nombre nuevo; nunca reemplaza uno existente.
`--pin RUTA=SHA256` permite exigir una identidad histórica antes del cuerpo del gate.
Un snapshot de bytes actuales detecta deriva durante la corrida; no acredita autenticidad histórica.
La publicación enlaza atómicamente un archivo temporal completo y sincronizado, sin overwrite.
Los snapshots incluyen dependencias directas evaluadas: herramientas, tests, docs, corpus y binarios.

La presencia de `PYTEST_ADDOPTS`, incluso vacío, falla; no se borra para ocultar contaminación.
El plugin cuenta colección y llamadas ejecutadas; deben coincidir con los testcase del JUnit fresco.
Se comprueban además los agregados XML, rc, fallos, errores, skips, XFAIL y XPASS.
El runner usa archivos host temporales nuevos y conserva XML, hash, stdout y stderr en su resultado.

Adopción: gates 1018A, 1114A y 1223A; auditoría 1112A con escritura explícita create-only.
Se eliminaron sus writers de overwrite/reintento y los checks pytest basados sólo en rc.
1114A consume el JSON fresco del audit, no un recibo anterior posiblemente desactualizado.
Su contador exige entero exacto cero; `false`, nulos y floats no equivalen a una auditoría válida.
Esta migración no certifica todos los scripts históricos del repositorio.

## Ping

`tools/common/ping_accounting.py` exige un resumen único y usa enviados/recibidos reales.
BusyBox rc=0 con 2/3 respuestas sigue siendo entrega incompleta.
Detecta DUP por detalle, secuencia repetida o contador del resumen.
Si hay detalle, sus respuestas únicas deben concordar con el resumen.
Los porcentajes redondeados sólo se comprueban por coherencia; no reemplazan los contadores.
El consumidor `tools/bench/check_openwrt_ptp_led_and_rf_bars.py` adopta el parser común.

## Preimagen y rollback

`tools/common/rollback.py` captura valores numéricos en objetos inmutables y rutas limitadas.
Restaura mediante echo y lee cada valor de nuevo; intenta los restantes aun si uno falla.
AQM se lee con cat y se interpreta localmente, sin depender de awk remoto.
El texto `ROLLBACK VERIFIED` con rc=0 no prueba restauración: una lectura diferente falla.
Las copias de scripts persistentes quedan en `/etc/fmx_rollback/`, con generación única.
Se verifica SHA antes/después de copiar y antes/después de restaurar; no se usa /tmp para esas copias.
El caller conserva autorización, watchdog, fence de escritura y criterio de memoria.

## SSH y cableado de banco

`tools/common/ssh_session.py` reserva un ID canónico desde el intento de conexión hasta su cierre.
Excluye sesiones simultáneas en el mismo proceso; no coordina otros procesos ni alias desconocidos.
La factory del caller verifica host key y autenticación; el módulo no abre red al importarse.
READ usa una gramática restringida; se rechazan sysctl -a e inventarios debugfs recursivos.
WRITE observa MemAvailable fresco y exige política explícita del caller, sin inventar un piso.
Los comandos de más de 10 KiB UTF8 se envían con sh -s por stdin.
`tools/bench/device_safety.py` conecta ese helper a rollback y exige un wrapper remoto del watchdog.
Debe revalidar lease, propietario, token y boot dentro del action lock antes de escribir, tras observar memoria.
Un contexto host-only o un wrapper identidad se rechazan; su forma no acredita el fence físico.
No es sandbox contra shell hostil ni una prueba de rollback remoto.

## Reproducción

`python -B tools/verify/verify_stage3097a_structural_guards.py --no-write`

Exige los cuatro nombres de suite previstos, no sólo cantidad; verifica fuentes y recibos históricos,
y exige igualdad de colección, ejecución y JUnit sin skips.
Para publicar, usar `--write-receipt`; una reejecución posterior debe conservar no-write o elegir otro nombre.
El gate final es `artifacts/verification/wave437_lane1_structural_guards_gate.json`.
Toda evidencia de esta etapa es local/offline: no valida hardware, RF, persistencia física ni despliegue.
