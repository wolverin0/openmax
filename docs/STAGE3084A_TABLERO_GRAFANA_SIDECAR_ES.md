<!-- doc-head: SUPERSEDED (W435, 31/10): complaints are now in Prometheus (W426: fmx_sidecar_complaints and fmx_sidecar_complaint_clients per node and cell, 1d and 7d) with Grafana panels. Stage 3084A (W424) ES: tablero Grafana 11 para las metricas fmx_sidecar_* que el Prometheus de PUBLIC_TERM_0003 ya junta (job fmx_sidecar_e2e): latencia p50/p95/p99 y perdida por panel y PtP con origen core y oficina, diferencia oficina menos core, tramo de la oficina, colas por cliente, salud del colector; reclamos no estan en Prometheus; JSON e instrucciones para infra, sin aplicar -->
Que cubre: que muestra el tablero, como se valido y como lo importa infra.
Estado: offline. No se importo ni se toco Grafana ni Prometheus (solo GET de consultas para validar). 0 escrituras.
Archivos: tools/observability/grafana/fmx_sidecar_dashboard.json (generado por build_sidecar_dashboard.py), check_sidecar_dashboard.py, provisioning_fmx_sidecar.yaml.
Leer cuando: al importar el tablero, o antes de cambiar etiquetas del sidecar.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# Stage 3084A: tablero Grafana del sidecar (W424)

## 1. Que muestra

- **Variables:** fuente Prometheus, celda (`cell`) y nodo (`node_id`), las dos con multiple y All.
- **Paneles** (16): Nodos sin respuesta (por origen); Componentes del sidecar con error; Tramo oficina: perdida 1 h; RTT p95; RTT p99; RTT p50; Perdida (media 5 min); Mas perdida desde el core (1 h); p95 oficina menos p95 core; Perdida oficina menos core (media 15 min); Trafico de la cola; Descartes de la cola; Nodos sin respuesta ahora; Segundos desde la ultima respuesta (peores 15); Componentes; Reclamos por celda: no estan en Prometheus.
- **Origen:** cada serie de latencia y perdida lleva `origin` (core = la sonda la manda el RB1100; office = la PC, que cruza el RB1100). Las series anteriores a W414 (30/10 17:06 UTC) no tienen la etiqueta: el tablero las lee como office. Usa `serie_nueva or label_replace(serie_vieja)` para que la vieja y la nueva no choquen en el reinicio.
- **Reclamos:** no estan en Prometheus. Estan en `fmx_sidecar_complaints_daily`, dentro de telemetry.db en la PC. El tablero lo dice en un panel de texto. Para graficarlos hace falta un gauge nuevo en el sidecar (fuera de esta tarea).

## 2. Validacion (CONFIRMED)

- `check_sidecar_dashboard.py` revisa ids unicos, que no haya paneles superpuestos ni de mas de 24 columnas, y que cada consulta use la variable de fuente.
- Corre cada consulta contra el Prometheus de PUBLIC_TERM_0003 (2.55.1), instantanea y de 12 h, con celda y nodo en `.*`. Resultado: 17 de 17 consultas OK, 0 errores de estructura.
- La consulta de 12 h encontro el choque de etiquetas en el reinicio de W414. Esta corregido arriba.
- Grafana de PUBLIC_TERM_0003 es 11.3.1; el JSON usa schemaVersion 39 y uid `fmx-sidecar-e2e`.

## 3. Como importarlo (infra; no aplicado)

**Por la interfaz:**
1. Grafana de PUBLIC_TERM_0003 (puerto 3400), Dashboards, New, Import.
2. Subir `tools/observability/grafana/fmx_sidecar_dashboard.json`.
3. Elegir la carpeta (sugerido FuturaMAX). En la variable "Prometheus" elegir la fuente que ya junta el job `fmx_sidecar_e2e`.

**Por API** (con un token de servicio de infra; el token no pasa por FuturaMAX):
`curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" http://<grafana>/api/dashboards/db -d "{\"dashboard\": $(cat fmx_sidecar_dashboard.json), \"folderUid\": \"<carpeta>\", \"overwrite\": false}"`

**Por provisioning:**
1. `provisioning_fmx_sidecar.yaml` va en `provisioning/dashboards/` del contenedor `wisp-grafana`.
2. El JSON va en la ruta del yaml.
3. Reiniciar Grafana. El espejo del stack esta en `infra/scripts/wisp/observabilidad`, de dueño infra.

**Volver atras:** borrar el tablero de uid `fmx-sidecar-e2e`, o sacar el yaml y el JSON y reiniciar. Prometheus no cambia.
**Regenerar:** `python tools/observability/grafana/build_sidecar_dashboard.py`, y despues `check_sidecar_dashboard.py`. Sale con 0 si todo da OK.

## 4. Limites

- Desde el core la sonda corre cada 10 s (registro) o 60 s (resto), asi que la perdida de 5 min es ruidosa en nodos de 60 s. Los paneles de diferencia usan 15 min.
- Las colas solo cubren las CPE del registro (13). El resto de los clientes no esta mapeado a nodos.
- Karpathy: colector vivo True, nodos desde el core 72, filas delta 435: PASS.
