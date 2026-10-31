<!-- doc-head: Stage 1264A: pruebas RSSI LEDs con fixtures desechables -->
Pruebas locales separadas de la aceptación visual física.
<!-- /doc-head -->

# Stage 1264A — Pruebas RSSI LEDs

La suite `tests/test_stage1260a_to_1265a_suite.py` usa fixtures desechables.
Ejecuta el daemon real en Linux: umbrales inclusivos, WDS AP/VLAN, STA,
desconexión, RSSI conservador, sysfs ambiguo/incompleto, dry-run sin escrituras
y restauración después del lamp-test. Verifica POWER/LAN e integridad del overlay.

En Windows los directorios sysfs con dos puntos no son representables en NTFS;
los escenarios nativos usan Linux. Las dos ejecuciones con lanzamientos WSL
individuales preservaron errores de conexión del entorno, sin ocultarlos.
El coordinador ejecuta la suite íntegra dentro de una única sesión Linux.

El gate recoge los nodeids y verifica su correspondencia exacta con JUnit,
exigiendo cero fallos, errores y saltos. El recibo se escribe únicamente a partir
de esa ejecución: `artifacts/verification/stage1264a_wave37_rssi_led_pytest.json`.
La aceptación física visual permanece UNKNOWN; pytest no prueba luz visible.
