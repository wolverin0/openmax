<!-- doc-head: Wave362, kits de campeón v2 y aceptación offline con BusyBox real -->
Valores exclusivamente del diff oficial; sysfs/debugfs simulados en WSL.
Sin SSH, radios ni despliegue; aceptación física y QoE fuera de este gate.
<!-- /doc-head -->

# Stage3022A: kits de campeón v2

Estado: 28 pruebas pytest PASS; 15 casos nativos PASS. Sin acceso a dispositivos.

## Fuente y cinco kits

`artifacts/champion/official_champion_v2.json` define los cambios por nodo.
`tools/champion_kits/build_champion_kits.py` conserva archivos desconocidos y
genera configuración, script, watchdog aceptado y manifiesto SHA256.
Nodos: panel1_ap, panel2_ap, panel3_ap, ptp_colo_ap y ptp_colo_sta.
Las cantidades de knobs distintos son respectivamente 4,10,8,9 y9.
Los valores oficiales no se modificaron durante esta tarea.

## Correcciones verificables

- Escritura debugfs mediante `echo`, seguida de readback estricto por knob.
- Rechazo de lecturas vacías, truncadas, duplicadas o mal formadas.
- Eliminación de la dependencia de `od`, ausente en el BusyBox probado.
- `action.flock` compartido con el timer, más boot, token, deadline y memoria.
- Persistencia y transacciones de los bucles coordinadas con el mismo watchdog.
- Rollback explícito mediante la API de restauración y verificación posterior.
- No se recuperan ni borran generaciones ajenas.
- Limpieza reconoce un timer `Z/X` solo tras verificar PID y startticks.
- Log limitado por bytes, en lugar de conservar un número arbitrario de líneas.

El kit guarda el pre-image real antes de cambiar valores. Una diferencia
inesperada respecto de la instalación declarada rechaza el preflight.
Un write exitoso sin readback correcto inicia restauración y no se confirma.

## Harness y límites

`tests/test_champion_kits.py` ejecuta una matriz mediante
`tools/champion_kits/wave362_native.py` y `wave362_linux_driver.py`.
Usa WSL Ubuntu, QEMU-MIPS y el BusyBox sin modificar de OpenWrt24.10.4.
El SHA256 de BusyBox es
`b475c18d851941fc9245414b5ea7356e28c0d9500a9b4cf31fd6b47e0ee496f1`.

Cada caso tiene chroot y namespaces privados de montaje, red y PID.
Un FUSE desechable modela comandos y lecturas AQM/AQL. BQL y sysctls son
archivos falsos. No se monta sysfs real ni se escribe proc/sys del host.
Los helpers de enlace y salud son simulados; no hay acceso a dispositivos.
Se prueban scripts y applets reales, no el comportamiento del driver físico.

## Casos por nodo

1. Aplicar solo su diff y comprobar también los knobs no incluidos.
2. Leer los valores aplicados y restaurar el pre-image mediante rollback explícito.
3. Matar el controlador después de aplicar y observar el timer independiente.
4. Ignorar una escritura en el modelo, devolviendo éxito, y exigir rechazo por readback.
5. Comprobar log acotado y ausencia de copias de lectura o loop canario abandonadas.

Los casos de expiración mantienen lease45s y hold60s originales, sin acelerar
el reloj. Los casos de commit usan hold0 para evitar una espera no pertinente;
esa modificación pertenece exclusivamente al fixture y queda en su recibo.

En los dos PtP-Colo se cambia AQL VI únicamente en la configuración simulada y
se espera el cierre de la transacción para verificar su recarga por el bucle.
El journal exige cero escrituras AQM en esos dos nodos: no escriben `fq_limit`.

## Evidencia y ejecución

Los intentos y errores anteriores se conservan, incluidos el fallo del fixture
por ruta de chroot, el applet ausente y el cierre del timer zombi.
Resultados y hashes están bajo `tools/champion_kits/wave362_native_runs/`.
JUnit: `tools/champion_kits/wave362_pytest_attempt*.xml`.
El lanzador exige que los inputs conserven su SHA antes y después de ejecutar.

Ejecutar mediante el wrapper de capacidad:
`node ../wezbridge/scripts/heavy-slot.cjs run -- python -m pytest tests/test_champion_kits.py -q`.

Gate: `artifacts/verification/wave362_lane3_champion_kits_gate.json`.
No se midieron Mbps, RTT, pérdidas RF ni efectos térmicos. El objetivo heredado
de rendimiento no se presenta como alcanzado por estas pruebas offline.
La autorización para aplicar los kits en producción permanece fuera de alcance.

## Resultado final

| Nodo | Aplicación/rollback | Expiración completa s | Readback falso |
|---|---|---:|---|
| panel1_ap | PASS | 47.7 | Rechazado y restaurado |
| panel2_ap | PASS | 49.5 | Rechazado y restaurado |
| panel3_ap | PASS | 48.2 | Rechazado y restaurado |
| ptp_colo_ap | PASS | 50.8 | Rechazado y restaurado |
| ptp_colo_sta | PASS | 51.9 | Rechazado y restaurado |

Las duraciones incluyen aplicación inicial y observación; el lease permanece en45s.
Gate final: CONFIRMED exclusivamente para lógica nativa con kernel simulado.
