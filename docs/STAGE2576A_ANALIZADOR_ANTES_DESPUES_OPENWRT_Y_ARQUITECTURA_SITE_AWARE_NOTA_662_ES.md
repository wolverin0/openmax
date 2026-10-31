<!-- doc-head: Wave 256 (2574A-2579A) nota 662 ES: antes y despues de OpenWrt en Guarida y estado del analizador 72h, del motor Site-Aware y del stack de observabilidad -->
Panel1: RTT de subida con carga de 198.78 a 22.73 ms (.41) y de 93.45 a 10.37 ms (.223); el porcentaje guardado para .223 no coincide.
Ventana 72h: 699 de 4320 intervalos (11.65 h), perdida RF bajo 0.06%, perdida punta a punta cerca de 5.9% por el tramo a Edificio Principal.
Panel3: antes en airOS y despues en OpenWrt con metricas distintas; el CPE .9 bajo a MCS 0.
Analizador 72h solo para Panel1 y detenido desde 2026-10-24; los motores Site-Aware son modelos offline con marcadores.
Stack (Prometheus, Grafana, Uptime Kuma, UISP, OpenWISP) documentado, no sondeado; Command Center 8787 HTTP 200. Sin campeon.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# Reporte ejecutivo - Nota #662: antes y despues de OpenWrt, analizador 72h y arquitectura Site-Aware

**Wave 256 - Etapas 2574A-2579A - 2026-10-28 - sintesis 100% offline (esta wave no toco ningun equipo).**

## Que se hizo

Se armo en la nota evergreen #662 una comparacion antes y despues de OpenWrt en Guarida y un inventario del analizador
diferencial de 72 h, de los motores Site-Aware / Peer-Buddy y del stack de observabilidad. Se regeneraron los indices
del vault, el feed del Command Center :8787 se amplio a 1536A..2579A, se agrego una fila a la tabla de ruteo de
AGENTS.md y se agregaron filas CRLF a orchestration/autoresearch/results.tsv.

Titular honesto: todos los numeros salen de recibos ya existentes; en esta wave no se midio nada ni se sondeo ningun
servicio salvo el Command Center local. **No hay campeon** y no se afirma ninguna mejora nueva: la unica registrada es
el par de Panel1 que ya guardaba la radiografia. Antes y despues usan herramientas y fechas distintas, asi
que la unica comparacion directa es el RTT de subida con carga de Panel1, que la radiografia guarda en pares.

Alcance de lectura: la radiografia, el resumen de 72 h, los recibos 2498A, 2499A, 2532A, 2534A y 2484A, y el codigo
fuente de seis herramientas (leido, no ejecutado). No se abrio ningun binario ni desensamblado. Los nombres de abonados
del pedido no se copiaron; equipos y servicios se nombran solo por el ultimo octeto.

## Aclaraciones sobre el pedido

- El resumen de 72 h solo tiene los dos CPEs con OpenWrt (.41 y .223); el de airOS de fabrica no esta. Ademas cubre
  699 de 4320 intervalos (11.65 h de 72 h) y termina el 24-10.
- La radiografia guarda -83.77% para .223, pero su propio par (93.45 a 10.37 ms) da -88.9%. Se uso el valor calculado.
- 2498A dice que la tercera estacion de Panel1 no respondio y que la unidad .80 es un equipo airOS que no pertenece a
  esta celda, mientras la radiografia la pone en Panel1. Queda registrado, sin resolver.
- El stack de observabilidad se documento desde la matriz de la Stage 59A; ningun servicio remoto se sondeo.
- closed_loop_research_reactor.py no tiene la opcion --sync-hyperresearch (su arranque regenera recibos viejos) y
  build_hyperresearch_vault_index.py no existe; se uso `hyperresearch sync` y `hyperresearch index build`.

## Panel1: antes y despues

| CPE | RTT de subida con carga en airOS (ms) | en OpenWrt (ms) | cambio |
| --- | --- | --- | --- |
| .41 | 198.78 | 22.73 | -88.6% |
| .223 | 93.45 | 10.37 | -88.9% |

Ventana de 72 h (23-10 22:01 a 24-10 15:07 UTC):

- RF entre el AP y los CPEs: p50 1.94 ms (.41) y 1.78 ms (.223), p95 cerca de 29 ms, perdida 0.029% y 0.057%.
- Tramo hacia Guarida p50 0.63 ms y hacia Almafuerte 2.37 ms, ambos sin perdida.
- Tramo hacia Edificio Principal: p50 7.85 ms, **6.15% de perdida** y un maximo de 2423 ms.
- Punta a punta: p50 10 y 9 ms con cerca de **5.9% de perdida**, que coincide con el tramo a Edificio Principal y no con el
  RF (inferido; las cantidades de muestras difieren).
- Al 28-10 (2498A): .41 y .223 en OpenWrt 24.10.4 con psk2, MCS 7, dos cadenas espaciales.

## Panel3: antes (airOS, 24-10) y despues (OpenWrt, 28-10)

| CPE | antes: senal dBm / diferencia entre cadenas dB / capacidad estimada Mbit/s | despues: MCS x cadenas (Mbit/s) / senal dBm |
| --- | --- | --- |
| .9 | -62 / 0 / 107.9 | MCS 0 x1 (6.5) / -53 |
| .235 | -60 / 10 / 135.72 | MCS 8 x2 (173.3) / -36 |
| .238 | -56 / 0 / 84.5 | MCS 6 x2 (117.0) / -46 |

- Las metricas no son las mismas (capacidad estimada en airOS contra tasa fisica en OpenWrt); solo sirven como direccion.
- .235 y .238 quedaron con dos cadenas y MCS alto; **.9 cayo a MCS 0**. .238 muestra 23 dB de desbalance en su propia vista.
- Despues: coverage class 0 en el AP y un solo ciclo de RTS 512 revertido; no quedo nada aplicado.
- fq_overmemory por hora de uptime: 2358.64 en Panel3 contra 220.65 en Panel1.

## Inventario: analizador 72h y motores Site-Aware

| archivo | lineas | tipo | archivos de test |
| --- | --- | --- | --- |
| tools/panel1/collect_72h_sector_latency_monitor.py | 302 | en vivo (SSH y ping) | 1 |
| tools/uisp/bilateral_site_topology_and_blast_radius_engine.py | 164 | modelo offline | 6 |
| tools/uisp/on_tower_peer_buddy_and_anomaly_disambiguator.py | 134 | modelo offline | 4 |
| tools/uisp/opus55_hardened_bilateral_rf_and_sg01_engine.py | 1573 | modelo offline | 1 |
| tools/uisp/zero_false_positive_bilateral_observability_pipeline.py | 157 | modelo offline | 4 |
| tools/telemetry/deterministic_rf_monitor_verifier.py | 515 | offline | 2 |

- El analizador de 72 h es solo para Panel1, tiene 20 direcciones fijas en el codigo y no hay otro colector de 72 h
  en tools/ (un plan de la Stage 580A solo propone extenderlo a Panel2 y Panel3). Su ultimo resumen es del 24-10.
- Los cuatro modulos Site-Aware se declaran modelos offline; la topologia y el quorum llevan marcadores y atajos
  explicitos, asi que sus resultados son salidas de modelo, no lecturas de campo.

## Inventario: stack de observabilidad

| sistema | punto de acceso (solo ultimo octeto) | estado en esta wave |
| --- | --- | --- |
| Prometheus + mktxp en PUBLIC_TERM_0003 | .160:9090 | no sondeado |
| Grafana WISP en PUBLIC_TERM_0003 | .160:3400 | no sondeado |
| Uptime Kuma (NAS) con verificador | .206:3001 | no sondeado |
| UISP 3.1.70 | .197 | no sondeado |
| OpenWISP (docker local) | localhost:18080 | no sondeado |
| LibreNMS / SmokePing | descartado | no aplica |
| Command Center | :8787 local | HTTP 200 |

- La matriz asigna roles: Prometheus y Grafana para series de tiempo, Uptime Kuma para empujes confirmados en dos
  rondas, UISP para los equipos airOS de fabrica y OpenWISP para plantillas de OpenWrt. Las extensiones de RF que propone
  son planes; no se verifico si existen.
- El AP de Panel3 corre panel3_admitter, udapi-bridge y uhttpd, y reporto UNMS conectado el 28-10 (2484A).

## AGENTS.md

Se agrego una fila a la tabla de ruteo con el contrato anti-amnesia de OpenWrt (admitidor hibrido fijo, Site-Aware y
comparacion antes y despues contra Prometheus, Grafana, Kuma, UISP y OpenWISP) que apunta a tools/uisp/, al analizador
de 72 h y a este documento. Para mantener AGENTS.md por debajo de 6000 bytes se acortaron los textos visibles de los
trece enlaces de la misma tabla; los destinos y la linea 21 no cambiaron. Quedo en 5959 bytes. Otro carril lo
reescribio despues; el coordinador fijo esta version como la valida y se restauro.

## Etapas 2574A y 2575A

La nota #662 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e `hyperresearch index build`
devolvieron 0. hyperresearch corta el id a 80 caracteres, asi que en el vault la nota figura con el id terminado en
note66. El tablero se reconstruyo hasta la banda 2579 y el servidor :8787 responde HTTP 200.

## Limites y advertencias (honestas)

- **Sin campeon**, sin A/B y sin ninguna medicion nueva.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico por CLI
  con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Decidir si se reactiva el analizador de 72 h y si se extiende a Panel3, para tener un antes y despues comparable.
- Investigar la perdida de 6% en el tramo a Edificio Principal, que domina la perdida punta a punta de Panel1.
- Verificar en vivo el estado del stack de observabilidad cuando se habilite una wave con red.

Recibos: `stage2574a_before_after_analyzer_and_site_aware_stack_note662_receipt.json`,
`stage2575a_command_center_1536a_2579a_refresh_receipt.json`, `stage2577a_memorymaster_ingest_receipt.json`,
`stage2579a_wave256_opus2_gate.json`.
