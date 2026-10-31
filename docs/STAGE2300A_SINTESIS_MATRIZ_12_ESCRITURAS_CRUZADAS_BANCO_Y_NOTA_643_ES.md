<!-- doc-head: Wave 210 (2298A-2303A) sintesis ES: nota #643 une los cuatro ciclos de escritura y restauracion del banco 2143A, 2173A, 2203A y 2257A (12 escrituras en RAM en XC .198, XC .253 y LTU .110) con las auditorias de solo lectura 2202A y 2256A: 12 de 12 restauradas, 0 por ciento de perdida ICMP en los 12 resumenes, tx_queue_len de eth0, tcp_frto y tcp_dsack en dos o mas equipos; el vector de .198 queda sin resolver y se corrigio la redaccion de las notas #641 y #642; banda :8787 a 1536A..2303A; SIN campeon -->
# Reporte ejecutivo - Nota #643: matriz de 12 escrituras cruzadas en el banco

**Wave 210 - Etapas 2298A-2303A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizaron los cuatro ciclos de escritura y restauracion en RAM del banco (2143A, 2173A, 2203A y 2257A)
con las auditorias de solo lectura 2202A y 2256A en la nota evergreen #643. Se regeneraron las paginas de
indice del vault, el feed del Command Center :8787 se amplio a 1536A..2303A y las tres docs maestras siguen
en 179 lineas con 0 apellidos. Titular honesto: **no hay campeon de trafico nuevo** y ningun valor de knob
queda aplicado.

Alcance de lectura: solo los seis recibos del pedido. No se abrio ningun archivo de RE binario ni de
desensamblado; el constructor rechaza cualquier otro recibo. 2258A tampoco se abrio.

Aclaraciones sobre el pedido:

- Los cuatro ciclos son pruebas de escritura y restauracion en radios sin carga, no telemetria.
- Los recibos traen 12 resumenes (uno por escritura, cada uno sobre las rondas A1, B1, A2 y B2), no 48
  mediciones separadas.

## Matriz equipo por knob

- tx_queue_len de eth0: .198 (2203A, 1000 -> 256), .253 (2257A, 1000 -> 256) y .110 (2173A, 256 -> 1000).
- tcp_frto: .253 (2203A) y .198 (2257A), 2 -> 0 en ambos.
- tcp_dsack: .253 (2173A) y .110 (2257A), 1 -> 0 en ambos.
- Ademas: tx_queue_len de ath0 en .198, netdev_budget en .198 y .110, netdev_max_backlog en .253 y
  tcp_early_retrans en .110.
- tcp_frto y tcp_dsack tienen el mismo valor base en todos los equipos; tx_queue_len de eth0 y netdev_budget
  no (los XC y el LTU traen valores distintos de fabrica).
- Ninguna de las 12 escrituras repite exactamente otra.

## Restauracion y perdida

- **12 de 12 escrituras tuvieron efecto y se restauraron**; 0 escrituras a flash; RF sin arrancar; ningun
  knob PROTECTED.
- Perdida ICMP 0 por ciento en cpe_41 y cpe_80 en los 12 resumenes.
- El trafico medido es el enlace ambiente de Panel1 .84: **no se atribuye** efecto de cola, de recuperacion
  de perdidas ni en el aire. Cada "keep" del harness es una linea base o trafico ambiente, no una mejora.

## El vector compartido de .198: sin resolver, y una correccion

- 2202A leyo atpc, cms_bias, ff_cap_rep, ff_mcast_airtime_limit, fixed_frame y sta_rx_rssi_th; 2256A leyo
  evm_meas_config, ro, sqparam, swr_limit, timing y voip_bias. Los dos subconjuntos no se superponen y 2256A
  no releyo los nombres de 2202A.
- En Panel2, Panel3 y XC .253 ambos subconjuntos dan el mismo vector. En XC .198 el de 2202A dio "3 0 0 ..."
  y el de 2256A da ceros.
- Entre las dos capturas (08:19 y 08:36 UTC) solo 2203A escribio en .198 (tx_queue_len de eth0) y lo
  restauro; no se establece ningun vinculo.
- **Sin resolver**: el vector de .198 cambio con el tiempo, o en .198 los dos subconjuntos difieren.
- Correccion: las notas #641 y #642 lo describian como un cambio. Se corrigio su redaccion y la de sus
  reportes en espanol, y sus compuertas 2273A y 2285A volvieron a dar CONFIRMED. El recibo 2256A fue
  reescrito por su linea (veredicto SHARED_VECTOR_MISMATCH_VS_2202A); la compuerta 2273A lo detecto.

## recall-first

6 de 6 consultas al vault tuvieron aciertos. No se corrio chequeo scholar (no se pidio).

## Etapas 2298A y 2299A

La nota #643 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista. El tablero se reconstruyo con 348 recibos
en la banda, 0 apellidos y 0 alias; el servidor :8787 responde HTTP 200 y sirve la banda nueva. MASTER,
CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado.
- Los radios del banco no tienen carga: ningun ciclo puede mostrar un efecto.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se
  verifico por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Una prueba con carga donde el host del knob reenvie el trafico medido.
- Una auditoria que lea los dos subconjuntos de nombres de .198 en la misma foto.

Recibos: `stage2298a_cross_host_12write_txqueuelen_frto_dsack_matrix_note643_receipt.json`,
`stage2299a_command_center_1536a_2303a_refresh_receipt.json`, `stage2301a_memorymaster_ingest_receipt.json`,
`stage2303a_wave210_opus2_gate.json`.
