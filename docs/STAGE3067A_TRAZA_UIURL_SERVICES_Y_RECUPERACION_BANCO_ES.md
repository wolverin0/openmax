<!-- doc-head: Wave407, traza nativa UI-URL y recuperación verificada del banco -->
Se preservan fallos, límites del observador, validación local y restauración real.
<!-- /doc-head -->
# Stage3067A — UI-URL, services y recuperación del banco

Resultado: **BLOCKED**. Objetivo ACTIVE con CPU/RAM: **False**.

## Alcance y observaciones

PBE242 únicamente, RAM y procesos propios. Consultas UISP mediante GET; cero cambios RF, flash o producción.
Se reutilizó el strace oficial fijado por SHA256 y el bridge nativo sin modificar su ELF.
Los buffers y credenciales potenciales permanecen en archivos privados; el informe publica hashes y formas.

## Evidencia estática y corrección implementada

Lane 4 comunicó que el bridge maneja UI-URL internamente: lee `/services`, exige `unms`,
inserta `unms.uiURL` y ejecuta PUT `/services`. Un resultado nulo/no exitoso produce error 4/400.
La traducción incorpora `unms.enabled` únicamente tras leer `unms.status=enabled` de su configuración privada.
El companion candidato acepta sólo el cambio de `unms.uiURL` contra la caché fresca y devuelve el objeto.
Rechaza cambios de SSH, adiciones/borrados de otros campos y claves duplicadas; no escribe servicios ni caché.
Compilación MIPS: lane 4; 33 pruebas host aprobadas y regresión baseline 405 reproducida.
La corrección no quedó validada como ACTIVE en hardware.

## Trazas reales y límites

- Primera invocación: strace rechazó `vfork` en MIPS; no se interpreta como traza del bridge.
- Tras corregir el perfil, se capturaron syscalls de red y archivos, con JSON completo contra el companion.
- La traza de 100 s terminó antes del PUT objetivo; la observación amplia alteró mucho los tiempos.
- Las conexiones fallidas a `/dev/log` corresponden a syslog, no a un backend ausente.
- Se observaron GET `/services`; esto no demuestra un PUT ni el origen exacto del error.
- El último perfil solicitó filtrado seccomp-BPF de red; no se certifica que se instalara o completara.
- Frames de services capturados: 3; PUT al companion demostrado: 0.
- Destino del PUT y origen exacto de 400 en runtime: UNKNOWN. La ruta estática no sustituye esa prueba.

## Fallos y recuperación

La limpieza inicial detectó una identidad pendiente ausente. Se preservó el fallo y se verificó
ausencia de procesos, mappings y namespaces propios, más hashes de configuración, antes de recuperarla.
Se corrigió la publicación de identidad antes del marcador y la carrera de lectura durante limpieza.
La última preparación quedó bajo el suelo ordinario de 10 MiB y no produjo muestras de aceptación.
La recuperación de procesos/archivos propios utilizó transporte específico de restauración de 5 MiB;
no se rebajó el suelo de sondeo o de nuevos canarios. No hubo quinto canario.
Tras liberar el payload se verificaron de nuevo los hashes y la ausencia de referencias propias.
Hashes de host restaurados: True. Anuncio anterior 8.3.2/prospective: True.
MemAvailable después de la recuperación: 19684 kB en el recibo; no es una tendencia ni una garantía futura.

## Archivos y siguiente paso

- Recibo: `artifacts/autoresearch/wave407_uiurl_trace.json`.
- Gate: `artifacts/verification/wave407_lane2_uiurl_gate.json`.
- Pruebas del parser y transporte no certifican aceptación del servidor.
Pendiente: probar el candidato con margen de RAM suficiente y una traza IPC de baja perturbación,
capturar el PUT real completo y confirmar ACTIVE con series CPU/RAM frescas antes de promoverlo.
