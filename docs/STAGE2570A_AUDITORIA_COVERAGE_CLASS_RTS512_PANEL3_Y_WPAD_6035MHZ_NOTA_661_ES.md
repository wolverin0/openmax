<!-- doc-head: Wave 255 (2568A-2573A) sintesis ES: nota #661 sobre el CPE .9 de Panel3 (2532A: coverage class 0 y distancia sin configurar en los dos extremos, ninguna sesion de block-ack; 2534A: un solo ciclo A-B-A con RTS 512 revertido, envios fallidos 4202 a 1052 y RTT 80 a 20 ms pero perdida 16.7% y la vuelta A2 no regreso a la base), la cadena wpad/netifd/cfg80211 de OpenWrt 24.10.4 para 6035 MHz (2539A: sin parche de mac80211, resolucion del canal 207 en hostapd sin probar) y la preparacion de Panel2 (2545A: HOLD en 22 de 22); banda :8787 a 1536A..2573A; SIN campeon -->
# Reporte ejecutivo - Nota #661: coverage class y RTS 512 en Panel3, y cadena wpad para 6035 MHz

**Wave 255 - Etapas 2568A-2573A - 2026-10-28 - sintesis 100% offline (esta wave no toco ningun equipo).**

## Que se hizo

Se concilio en la nota evergreen #661 la auditoria de RF del CPE .9 de Panel3 (2532A), la prueba de RTS 512 (2534A),
la auditoria de la cadena de 6035 MHz en la imagen OpenWrt 24.10.4 (2539A) y la preparacion de Panel2 (2545A), con la
radiografia del 24-10 para las distancias. Se regeneraron los indices del vault, el feed del Command Center :8787 se
amplio a 1536A..2573A, se agregaron filas CRLF a orchestration/autoresearch/results.tsv y las tres docs maestras
siguen en 179 lineas.

Titular honesto: lo del CPE .9 es **una lectura y un solo ciclo revertido**; no quedo nada aplicado (RTS apagado en
los dos extremos, 0 escrituras persistentes). **No hay campeon** y no se afirma ninguna mejora.

Alcance de lectura: cuatro recibos JSON y la radiografia. No se abrio la captura cruda, la imagen ni ningun binario o
desensamblado. Los equipos se nombran solo por el ultimo octeto; no hay MAC ni nombres de abonados.

## Aclaraciones sobre el pedido

- RTS 512: los numeros coinciden (envios fallidos de 4202 a 1052, RTT de 80 a 20 ms), pero es **un solo ciclo**, sin
  duracion registrada de las ventanas, la perdida siguio en 16.7% y la ventana de vuelta A2 no regreso a la base
  (2671 fallidos, 46 ms). Es una observacion prometedora, no un ajuste validado.
- "2275 m": es el dato de la radiografia; el recibo de RTS dice que el largo real del enlace es desconocido.
- "272-300 m de Panel1": la radiografia pone a los cuatro CPEs de Panel1 en 272, 300, 300 y 327 m. **Ninguna fuente
  registra el coverage class ni la distancia configurada en Panel1**, asi que la comparacion es solo de largo de enlace.
- closed_loop_research_reactor.py no tiene la opcion --sync-hyperresearch (su arranque regenera recibos viejos) y
  build_hyperresearch_vault_index.py no existe; se uso `hyperresearch sync` y `hyperresearch index build`.

## CPE .9: estado de RF (2532A, solo lectura)

- **Coverage class 0 (hasta 0 m)** en el AP y en el CPE, y la opcion distance **vacia en los dos extremos**. Limites de
  reintento 7 cortos y 4 largos; canal 149 (5745 MHz), 20 MHz, potencia del AP 20 dBm.
- Vista del AP: MCS 0 de subida y 1 de bajada, una sola cadena espacial, senal -48 dBm con cadenas a -58 y -49 dBm
  (9 dB de diferencia), 54101 envios fallidos y 23883 reintentos desde la asociacion.
- Vista del CPE: MCS 0 en las dos direcciones, senal -53 dBm, 30358 envios fallidos.
- **Ninguna sesion de block-ack**: las 16 filas de TID estan en 0 en recepcion y transmision, en los dos extremos. No
  hay agregacion A-MPDU para esta estacion.

## Prueba de RTS 512 (2534A, escritura en vivo solo en el AP .83, watchdog de 240 s)

| ventana | RTS | envios fallidos | reintentos | perdida % | RTT medio ms |
| --- | --- | --- | --- | --- | --- |
| A, base | apagado | 4202 | 1781 | 21.7 | 80 |
| B | 512 | 1052 | 437 | 16.7 | 20 |
| A2, vuelta | apagado | 2671 | 795 | 20.0 | 46 |

- RTS quedo apagado de nuevo en los dos extremos; no se escribio nada persistente.
- Un primer intento se aborto: la sesion SSH al CPE se corto apenas se puso RTS 512 en el AP, y RTS se apago en los dos
  extremos en cerca de un minuto.
- Coverage class y distancia **no se tocaron**; el valor del AP aplicaria a las tres estaciones de Panel3.

## Cadena de 6035 MHz en OpenWrt 24.10.4 (2539A, estatica)

- netifd lleva el canal 207 sin cambios en VHT20: no hace falta parchear mac80211.
- La estacion puede fijar la frecuencia con `option freq 6035`, sin depender del numero de canal.
- wpad no tiene una tabla fija de 5 GHz; **no esta probado si hostapd acepta el canal 207** con hw_mode=a. No se aplico
  ningun parche ni se regenero la imagen.
- La imagen auditada es para PtP-Colo, cuyas radios corren airOS 8 (2521A, nota #658); solo aplica si se convierten a
  OpenWrt.

## Preparacion de Panel2 (2545A, offline, foto del 24-10)

- Estado **HOLD**: 0 listos y 22 en espera; cutover no aprobado; firmware desconocido en los 22; ninguna metrica actual.
- Nueve requisitos, todos sin resolver (inventario actual, cadenas y mascaras, psk2, interoperabilidad, WDS, AQL,
  banco, imagen y recuperacion, aprobacion del operador).
- Coincide con el lote 0 de la nota #660: volver a medir antes de escribir nada en Panel2.

## Etapas 2568A y 2569A

La nota #661 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e `hyperresearch index build`
devolvieron 0 y el vault llego a 727 notas. El tablero se reconstruyo con 484 recibos en la banda y el servidor :8787
responde HTTP 200; la tarjeta de 2568A no tiene nombres ni MAC. La seccion heredada Stage 12 sigue mostrando los nombres
de la radiografia (aviso de la Wave 254, sin corregir). MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon**, sin campana A/B y nada aplicado por esta wave.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico por CLI
  con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Si se quiere validar RTS 512 en Panel3: repetir varios ciclos con ventanas de duracion fija antes de dejarlo.
- Medir el largo real del enlace del .9 antes de configurar distancia, porque cambia el tiempo de ACK de las tres
  estaciones del AP.
- Investigar por que no se abre ninguna sesion de block-ack con el .9.
- Mantener Panel2 en HOLD hasta cumplir los nueve requisitos.

Recibos: `stage2568a_panel3_coverage_class_rts512_and_wpad_6035mhz_note661_receipt.json`,
`stage2569a_command_center_1536a_2573a_refresh_receipt.json`, `stage2571a_memorymaster_ingest_receipt.json`,
`stage2573a_wave255_opus2_gate.json`.
