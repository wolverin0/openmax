<!-- doc-head: 1357A read-only COLO audit; exact unexecuted selectors; drain100 not verified -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# MainRouter COLO read-only mangle and routing audit

Estado: CONFIRMED_LIVE_READONLY_CORE200; auditoria de lectura, cero cambios de dispositivo.

Identidad API: [{'name': 'MK2-RS'}]; recurso: [{'version': '7.18.2 (stable)', 'board-name': 'RB1100AHx4'}].
Alias198.18.0.2/24 en bridgeLAN: CONFIRMED_LOCAL_ADDRESS_ON_CORE200.
Consulta autenticada a198.18.0.44; no se abrio login separado a la alias.
Puntero existente: WISP_CORE_ROUTER_PASS/hass; infra/.env no existe; cero secretos exportados.
Dos sesiones API de lectura: radiografia acotada y confirmacion de alias/matchers; cero SSH.
Estado de las ocho reglas observadas antes/despues identico salvo bytes/packets.
Muestra bps/pps: [{'name': 'ether10-colo', 'rx-bits-per-second': '30686128', 'tx-bits-per-second': '1319360', 'rx-packets-per-second': '2883', 'tx-packets-per-second': '1058'}].
COLO: ether10-colo, tabla to_isp12, gateway198.18.0.119%ether10-colo activo.
PtP-Colo corregido:198.18.0.91 y198.18.0.92; no se contactaron radios.
Plan no ejecutado: *1BA y*1BB clasifican clientes PCC bridgeLAN a isp12_conn; *172 enruta a to_isp12.
CLIENTCOLO describe funcion; no requiere un comentario literal en RouterOS.
Excluidos: *95 entradaCOLO; *178/output; *1FE/*1FF probes; *19C scraper ambiguo sin matcher LAN.
CLI exacto en reversible_cli del JSON: primero valida identidad, IDs, disabled, comment, action,
chain, marks, interfaces, clasificadores, tabla y gateway; solo entonces propone disable de esos3IDs.
Rollback valida la misma preimagen con disabled=true y habilita solo esos3IDs antes habilitados.
No incluye enable de reglas previamente deshabilitadas; no ejecuta scripts generados.
No se acredita drenaje efectivo, cero downtime ni continuidad TCP por preparar estos comandos.
No se cambio mangle/rutas, conntrack, PoE ni servicios; ether2-sw-poe200 protegido.
Recibo inicial bloqueado preservado; muestra y comandos API estan pinneados en native_raw_pins.

Alcance del drain100: NO EJECUTADO / UNKNOWN. Preparar o deshabilitar esos selectores no prueba redireccion100%.
La captura no incluye una default activa alternativa de main; el fallback actual sigue UNKNOWN.
Conntrack/NAT existentes no migran por cambiar mangle; flujos pueden necesitar expirar o reconectar.
*178 y probes*1FE/*1FF quedan fuera del plan; trafico totalCOLO puede continuar.
No se autorizaron ni ejecutaron flush, reset de conexiones/contadores ni consultas extra para esta precision.
El JSON incluye comandos de lectura pendientes para bps/pps, connmarkISP12, contadores de los3IDs y defaultmain.
El conteo connmarkISP12 es agregado y no certifica por si solo ausencia de clientesCOLO.
