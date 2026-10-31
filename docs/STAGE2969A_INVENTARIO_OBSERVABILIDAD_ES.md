<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Inventario read-only de observabilidad existente (Wave 346, roadmap 1.9/1.10/1.11) -->
# STAGE2969A - Inventario de observabilidad existente

Objetivo: saber que monitorizacion ya existe antes de instalar nada. Todo se hizo con HTTP GET y
lectura de ficheros. Cero escrituras, cero logins, cero SSH.

## Tabla

| Herramienta | Host:puerto | Responde | Que mide hoy | Datos Fmx | Hueco | Dueno |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| WISP Prometheus | 198.18.0.130:9090 | si | segun infra | no confirmado | sin target Fmx confirmado | infra |
| WISP Grafana | 198.18.0.130:3400 | si | segun infra | no confirmado | sin target Fmx confirmado | infra |
| Uptime Kuma | NAS .206:3001 | si | segun infra | no confirmado | sin target Fmx confirmado | infra |
| UISP NMS | 198.18.0.134 | no | segun infra | no confirmado | verificar scrape | infra/otro |
| Command Center | 198.18.0.135:8787 | no | segun infra | no confirmado | verificar scrape | infra/otro |
| OpenWISP | 198.18.0.130:18080 | no | segun infra | no confirmado | verificar scrape | infra |

## Lo que ya existe

- **PUBLIC_TERM_0003 (.160)**: stack de monitorizacion y daemon Orca en 6768.
- **NAS (.206)**: Uptime Kuma con las sondas 133, 135, 136-140 y 141; 135 y 141 figuran pausadas.
- **UISP (.197, red 192.168.2)**: UISP 3.1.70 con CRM 4.6.17.
- **watcher-pi (.155)**: exporter de 5 VMs y 23 mapas de disco.

## Huecos

1. Ningun target de scrape propio de FuturaMAX esta confirmado en Prometheus. Responder a
   `/api/v1/targets` prueba alcanzabilidad, no que el exporter 9118 o el de este PC este siendo
   recolectado. Hay que leer la lista de targets, no solo el codigo de estado.
2. OpenWISP no se confirmo corriendo en ninguna direccion.
3. airControl2 no aparece en la documentacion de infra leida.

## Siguiente paso

Leer `/api/v1/targets` completo y filtrar por 9118 para cerrar el punto 1. Es una peticion GET y
responde la pregunta de raiz: si FuturaMAX ya publica metricas y nadie las recolecta, el hueco es de
configuracion, no de instalacion.
