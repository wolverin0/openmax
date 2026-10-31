<!-- doc-head: Wave 259 (2592A-2597A) nota 663 ES: estado verificado hasta Wave 256 y proximas tareas en 8 dominios (PtP, PtMP, Ground-Up, Autoresearch, Hyperresearch/Scholar, REA/fullrea, Site-Aware, Antes/Despues) -->
PtP-Colo: imagenes 6035 MHz Ch 207 construidas pero EN ESPERA (fallan el CRC de carga uImage, despliegue no autorizado, HOLD).
PtMP: Panel1 y Panel3 en OpenWrt psk2; CPE .9 en coverage class 0, distancia sin configurar, un solo ciclo RTS 512 revertido.
Ground-Up, Autoresearch, Hyperresearch, REA, Site-Aware y Antes/Despues: cada uno con una proxima tarea concreta.
Nada nuevo se midio ni se toco ningun equipo; vault 732 notas; tablero :8787 banda 1536A..2597A HTTP 200. Sin campeon.
Wave 261: se agrego la seccion Reglas prohibidas de olvidar (9 reglas del contrato 2604A, incluido el banco LTU-Lite).
<!-- /doc-head -->
# Reporte ejecutivo - Nota #663: estado global y proximas tareas en 8 dominios

**Wave 259 - Etapas 2592A-2597A - 2026-10-28 - sintesis 100% offline (esta wave no toco ningun equipo).**

## Que se hizo

Se armo en la nota evergreen #663 un mapa del estado verificado hasta la Wave 256 y de las proximas tareas en los
ocho dominios que pidio el operador. Cada linea de estado se recalculo de un recibo; cada proxima tarea es un paso, no
una promesa de resultado. Se regeneraron los indices del vault, el tablero :8787 se amplio a 1536A..2597A, se
actualizo el final de CURRENT_STATE.md y se agregaron filas CRLF a results.tsv.

Titular honesto: **no se midio nada nuevo y no se toco ningun equipo**. No hay campeon.

Alcance y aclaraciones: no se abrio ningun binario ni desensamblado; el estado de RE viene de recibos previos. El
pedido nombra closed_loop_research_reactor.py --sync-hyperresearch y build_hyperresearch_vault_index.py; esa opcion no
existe y ese script tampoco, asi que se uso `hyperresearch sync` e `hyperresearch index build`.

## (i) PtP

- PtP-Colo .62 / .54: respaldo de mtd0/1/4/5 y system.cfg verificado 8 de 8 (2538A); el kernel y el rootfs no se
  volcaron. Dos imagenes OpenWrt 24.10.4 para 6035 MHz canal 207 construidas (2520A) y auditadas (2544A), pero
  **fallan el CRC de la carga uImage y no estan aceptadas para despliegue**; el cutover atomico lleva un watchdog de
  45 s con reserva en 5200 MHz y el paquete de activacion esta **habilitado pero inerte** (despliegue no autorizado,
  HOLD). Las dos radios corren airOS 8 y ya estan en 6035 MHz; las imagenes son para OpenWrt, que no corren.
- Proximas tareas: reconstruir las imagenes para que incluyan el watchdog y pasen el CRC; probar que wpad acepta el
  canal 207 a 6035 MHz; aportar el archivo de par esperado y validar la reserva de 5200 MHz; decidir si PtP-Colo sigue
  en airOS 8 o se convierte a OpenWrt. Almafuerte .60 <-> Guarida .61 y el banco .241/.242 no tienen recibo nuevo aca.

## (ii) PtMP

- Panel1 .84: 2 CPEs en OpenWrt 24.10.4 psk2; la radiografia registra una baja del RTT de subida con carga de -88.57%
  (.41) y -88.9% (.223) calculado de sus propios pares (el valor guardado para .223, -83.77%, no coincide).
- Panel3 .83: 3 CPEs en OpenWrt 24.10.4 psk2 (confirmado 3 de 3). **CPE .9: coverage class 0, distancia sin
  configurar**, distancia de radiografia 2275 m; un solo ciclo RTS 512 revertido movio el RTT 80 -> 20 -> 46 ms, nada
  quedo aplicado. Ninguna fuente cuenta respuestas DUP; solo el 2496A dice que desaparecieron tras psk2.
- Panel2 .82: 22 CPEs auditados (2545A), estado HOLD (0 listos). LTU .110 nombrada, sin verificar aca.
- Proximas tareas: medir el largo real del enlace del .9 y recien ahi configurar coverage class / distancia (cambia el
  tiempo de ACK de las tres estaciones); validar RTS 512 en varios ciclos con ventanas de duracion fija; decidir el
  perfil AQL de Panel3 y mantener el admitidor activo; volver a medir las 15 filas modeladas de Panel2 antes de migrar.

## (iii) Ground-Up First Principles

- El blueprint y la hoja de ruta de variables no probadas estan presentes.
- Proxima tarea: elegir la proxima variable no probada con un camino de banco reversible y seguro.

## (iv) Metodo Autoresearch (Karpathy)

- Ejemplo vivo 2534A: A1-B1-A2 con watchdog de reversion de 240 s, restaurado; el arnes vive en orchestration/autoresearch/.
- Proxima tarea: correr una campana RTS 512 A-B-A-B de varios bloques en Panel3 con ventanas de duracion fija.

## (v) HYPERRESEARCH V8 + Scholar MCP

- Vault unificado en 732 notas; el reactor esta presente; el MCP de scholar no se corrio en esta wave.
- Proxima tarea: correr un chequeo scholar sobre la pregunta de ACK-timeout / coverage class en enlaces PtMP largos.

## (vi) REA y /fullrea

- 6035 MHz: parche de ath10k_core (2490A, reemplaza 5845/5865 por 6015/6035, hw 203/207) y regulatory.db (2491A, 8
  reglas); wpad ELF auditado (2539A): **no hace falta parche de mac80211, la aceptacion del canal 207 no esta probada**.
  Modulos del catalogo: ubnt_poll_host.ko, ame_core.ko, eab_driver.ko, mac80211.ko (chequeo de duplicados RX),
  ath10k_core.ko.
- Proximas tareas: resolver si hostapd mapea el canal 207 a 6035 MHz; ningun binario se abrio en esta wave, el /fullrea
  queda como tarea autorizada aparte.

## (vii) Site-Aware & Peer-Buddy

- Cuatro modulos en tools/uisp/, todos modelos offline con marcadores de valores provisorios.
- Proxima tarea: reemplazar los marcadores de topologia y quorum con datos relevados antes de confiar en un veredicto.

## (viii) Analizador Antes/Despues OpenWrt + stack WISP

- El analizador es solo para Panel1 y se detuvo a los 699 de 4320 intervalos; la perdida punta a punta sigue el tramo
  de backhaul a Edificio Principal, no el enlace de RF. El stack (Prometheus, Grafana, Kuma, UISP, OpenWISP, :8787)
  esta documentado pero **no se sondeo en esta wave**.
- Proximas tareas: reactivar el analizador de 72 h y extenderlo a Panel3; investigar la perdida de 6% del tramo a
  Edificio Principal.

## Etapas 2592A a 2594A

La nota #663 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e `hyperresearch index
build` devolvieron 0 y el vault llego a 732 notas (hyperresearch corta el id a 80 caracteres). El tablero se
reconstruyo hasta la banda 2597 y responde HTTP 200. Se agrego al final de CURRENT_STATE.md la seccion de sincronizacion
Wave 155..259 con el estado y las proximas tareas de los 8 dominios, manteniendo intactas las lineas 1 a 179 y el total
por debajo de 220. MASTER, CURRENT y CURATED siguen dentro del presupuesto.

## Reglas prohibidas de olvidar (contrato 2604A, Wave 261)

Agregado en la Wave 261: estas nueve reglas deben figurar igual en el hook de agy, AGENTS.md, CURRENT_STATE.md y este
documento; `tools/verify/enforce_prohibited_to_forget_contract.py` falla si falta alguna o si un sitio cambia de octeto.
Es un contrato de texto: no se sondeo ningun equipo. Detalle en STAGE2606A y en la nota #664.

- R01 admitidor hibrido fijo siempre: cada AP PtMP OpenWrt mantiene su admitter de panel activo para que un CPE airOS 8 que vuelve se asocie solo.
- R02 demonio continuo Antes/Despues OpenWrt en SQLite: fmx_persistent_before_after_openwrt_daemon.py guarda RTT, perdida y CPU en tools/observability/telemetry.db.
- R03 Site-Aware / Peer-Buddy: /etc/fmx_site_neighbors.json desplegado y releido en Panel1 y Panel3 (2588A); puente Prometheus/Grafana/Kuma solo offline (2587A).
- R04 banco LTU-Lite .110: alcanzado en vivo en 2473A (sysctl en RAM, restaurado, RF estacionada, sin efecto medido); snapshot calibrado BLOQUEADO (1135A).
- R05 a R09: PtP-Colo .62 / .54, Panel1 .84, Panel2 .82, Panel3 .83 y tablero :8787.

## Limites y advertencias (honestas)

- **Sin campeon**, sin A/B y sin ninguna medicion nueva en esta wave.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico por CLI
  con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Prioridad PtP: el CRC de la carga uImage de las imagenes de PtP-Colo es el bloqueo mas cargado; decidir reconstruirlas
  o quedarse en airOS 8.
- Prioridad PtMP: el coverage class y el largo real del enlace del CPE .9.
- Elegir cuales de las ocho proximas tareas entran en la proxima wave.

Recibos: `stage2592a_master_8domain_state_and_next_tasks_note663_receipt.json`,
`stage2593a_command_center_1536a_2597a_refresh_receipt.json`, `stage2595a_memorymaster_ingest_receipt.json`,
`stage2597a_wave259_opus2_gate.json`.
