<!-- doc-head: Wave258, topología por sitio, despliegue de dos manifiestos y alertas con evidencia limitada -->
Manifiestos instalados y releídos en dos APs; puente de observabilidad implementado localmente.
Las alertas actuales permanecen UNKNOWN por falta de muestras frescas.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# Topología de torre y puente de observabilidad

Se generaron siete manifiestos autocontenidos con su grafo completo.
Los buddies pertenecen al mismo sitio físico; los peers PtP entre sitios
figuran como relaciones distintas. Una relación lógica no demuestra una ruta IP.

| Enlace o sector | Frecuencia MHz | Inventario declarado |
| --- | ---: | --- |
| Almafuerte .60 a Guarida .61 | 5355 | Dos extremos PtP |
| Panel1 .84 | 5240 | 3 activos y 1 inactivo |
| Panel2 .82 | 5805 | 22 activos |
| Panel3 .83 | 5745 | 3 activos |
| Colo .62 a .54 | 6035, canal207 | Dos extremos PtP |

Son 28 CPEs activos declarados entre los tres paneles. Los seis históricos
de Panel3 no se suman al inventario activo. No se incorporaron identidades
individuales de abonados ni se dedujeron firmware o rutas que faltaban.
Las frecuencias proceden del operador; esta ejecución confirmó directamente
5240MHz y 5745MHz en los dos APs intervenidos.

## Despliegue real y alcance

Stage2588 escribió únicamente `/etc/fmx_site_neighbors.json` en
198.18.0.7 y 198.18.0.6 mediante SSH con claves de host previamente
fijadas. Una segunda conexión leyó los bytes completos y comprobó SHA256
e igualdad JSON. Ambos APs mostraron OpenWrt24.10.4/kernel6.6.110 y tres
estaciones antes y después. No hubo reinicios de WiFi ni escrituras MTD.
Esto verifica la instalación del archivo, no una integración ejecutada
por un daemon en los radios ni persistencia probada después de reiniciar.

La primera revisión mezclaba buddies físicos y peers remotos y dependía
de otro archivo de grafo. Fue preservada junto con su recibo. La segunda
revisión se instaló sólo tras verificar el hash de la versión propia anterior.
Cada archivo final contiene el grafo necesario sin instalar archivos adicionales.

## Evaluador y salidas preparadas

Stage2587 conecta el verificador determinista y el desambiguador existente.
Tres observaciones cronológicas forman dos rondas separadas de cinco pings.
La decisión DOWN exige dos fallos RF confirmados, sin asociación ni progreso
L2. UP también exige dos rondas frescas y sanas. Contadores reiniciados,
replays, cambios de boot o colector, tiempos superpuestos, tipos inválidos
y datos ausentes producen UNKNOWN.

La última muestra tiene antigüedad máxima de90s. Cada intervalo tiene límite
de90s; el historial acotado permite una cadencia normal de60s. El llamador
debe conservar `next_state` entre invocaciones para rechazar replays.
El contrato exige sondeos AP_LOCAL que no atraviesen el core; esta etiqueta
de entrada no reemplaza la futura verificación física del recorrido.

El modelo separa dominios de backhaul, sector y CPE. Sólo evidencia nativa
fresca de alimentación y testigos independientes permite atribución PoE.
Un patrón correlacionado o una recomendación del modelo no prueba la causa.

Se prepararon métricas textfile, un dashboard Grafana y descriptores push:

| Servicio indicado | Destino | Estado de esta entrega |
| --- | --- | --- |
| Prometheus | 198.18.0.130:9090 | Payload preparado, sin ingesta verificada |
| Grafana | 198.18.0.130:3400 | JSON generado, sin importar |
| Uptime Kuma | 198.18.0.131:3001 | Veredicto preparado, sin HTTP push |

Prometheus9090 no es un endpoint de escritura de métricas. El textfile
requiere un directorio del colector configurado explícitamente y existente.
Se debe supervisar además la frescura del archivo y desplegar el scheduler.
No se crearon tokens, monitores ni credenciales.

UNKNOWN y PENDING generan `NO_REQUEST` sin campo `status` para Kuma.
Su API considera valores distintos de `up` como DOWN; una ausencia de
evidencia no debe enviarse como estado de salud.

El analizador guardado corresponde a una captura histórica de Panel1.
Se reutilizó sólo su contexto agregado y su hash; no sirve como muestras
actuales de todos los sectores. El resultado de producción generado es
`UNKNOWN_INPUT_NOT_COLLECTED` hasta recibir entradas frescas válidas.

## Evidencia, memoria y aceptación

Los recibos2586/2587 describen generación offline;2588 contiene las dos
lecturas SSH reales. Las pruebas desechables usan fixtures sintéticos
identificados como tales. Ninguna prueba local se presenta como tráfico RF.

Las fuentes oficiales de node_exporter y Kuma se guardaron con SHA256.
Scholar devolvió evaluaciones heurísticas; hay cero verificaciones Jev
semánticas en vivo y no se ejecutó el reactor Hyperresearch completo.
PilarA documenta auditoría de fuentes, sin nueva ingeniería binaria.
MemoryMaster recibe un único claim consolidado de alcance limitado.

El gate2591 exige hashes, lecturas independientes, pruebas y metadatos
de cinco pilares. Su PASS cubre integración local y los dos archivos
desplegados. La ingesta del stack y la salud RF actual siguen sin verificar.

## Archivos de entrada y salida

- [Builder](../tools/uisp/build_stage2586a_live_site_neighbors_and_tower_buddy_bundles.py)
- [Puente](../tools/telemetry/fmx_prometheus_kuma_site_aware_bridge.py)
- [Despliegue](../tools/uisp/deploy_stage2588a_guarida_site_neighbors.py)
- [Topología](../artifacts/autoresearch/wave258/topology/operator_topology.json)
- [Dashboard](../artifacts/autoresearch/wave258/telemetry/grafana_rf_site_aware_dashboard.json)
- [Recibo live](../artifacts/autoresearch/stage2588a_guarida_ap_site_neighbors_live_deploy_receipt.json)
