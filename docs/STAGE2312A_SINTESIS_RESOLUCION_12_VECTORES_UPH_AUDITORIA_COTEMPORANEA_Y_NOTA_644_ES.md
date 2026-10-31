<!-- doc-head: Wave 212 (2310A-2315A) sintesis ES: nota #644 sobre la auditoria de solo lectura 2286A, que leyo juntos los 12 nombres uph_wifi0 en los 4 radios airOS, con las auditorias 2106A, 2142A, 2172A, 2202A y 2256A del mismo arranque: un solo vector por radio; en XC .198 los nombres de 2202A cambiaron entre 08:19 y 08:54 (antes de 2256A es inferido); FIFO de eth0 de Panel1 sigue subiendo; fq_overmemory sin cambio; Panel3 sumo 219 descartes en la clase :2 y Panel2 ninguno; banda :8787 a 1536A..2315A; SIN campeon -->
# Reporte ejecutivo - Nota #644: resolucion de los 12 vectores uph y auditoria cotemporanea

**Wave 212 - Etapas 2310A-2315A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizo el recibo de solo lectura stage2286A (Wave 208) con las cinco auditorias anteriores (2106A,
2142A, 2172A, 2202A y 2256A) en la nota evergreen #644. Se regeneraron las paginas de indice del vault, el
feed del Command Center :8787 se amplio a 1536A..2315A y las tres docs maestras siguen en 179 lineas con 0
apellidos. Titular honesto: **no hay campeon de trafico nuevo**, no hubo escrituras y ningun valor de knob
queda aplicado.

Alcance de lectura: solo las seis auditorias. No se abrio ningun archivo de RE binario ni de desensamblado;
el constructor rechaza cualquier otro recibo. El uptime subio igual en los seis radios desde 2202A
(dispersion 0.5 s): todo es el **mismo arranque**.

Aclaraciones sobre el pedido:

- fq_overmemory no paso de 3794 a 4055: vale 4055 en 2172A y 4055 en 2286A (**sin cambio**). 3794 era el
  conteo de descartes por estacion de 2172A, otro contador.
- Los valores iniciales de time_squeeze del pedido (14862 y 8625) no coinciden con ningun recibo: 2106A da
  14828 en Panel2 y 8644 en Panel3.
- 2286A prueba que los dos subconjuntos coinciden ahora y que los nombres de 2202A cambiaron entre 2202A y
  2286A; que el cambio fuera antes de 2256A es **inferido**, porque 2256A no leyo esos nombres.

## La pregunta de .198 queda resuelta

- En 2286A los 12 nombres imprimen **un solo vector en cada radio airOS** (Panel2, Panel3, XC .198 y XC .253).
- En XC .198 los 12 dan ceros. Los nombres de 2202A daban "3 0 0 ..." en 2202A: **esos nombres cambiaron**
  entre las capturas de 08:19 y 08:54 UTC. Los dos subconjuntos **no** difieren.
- La causa es DESCONOCIDA; ciclos de banco tocaron .198 en esa ventana (notas #640 y #643) y no se
  establece ningun vinculo. Esto cierra la pregunta que la nota #643 dejo sin resolver.

## Panel1 .84 (OpenWrt)

- rx_fifo_errors de eth0: 558, 585, 596, 612 y 636 (2142A a 2286A); entre 26.1 y 76.2 por hora. Sigue
  subiendo despacio; causa DESCONOCIDA.
- "Tx Pause Frames Honored" marca 807: contador que da la vuelta, **no es un total desde el arranque**;
  pausas recibidas 0.
- softnet time_squeeze 3 en 2106A y 3 en 2286A: ninguno nuevo; 0 descartes de backlog. Sigue sin tc.

## Panel2 .82 y Panel3 .83 (airOS 8)

- time_squeeze desde 2106A: Panel2 14828 a 14976 (+148, 82.5 por hora); Panel3 8644 a 8701 (+57, 31.8 por
  hora); 0 descartes de backlog.
- FDB aprendidas en br0: 441 a 449 en ambos paneles (2202A a 2286A).
- Descartes de salida de ath0, todos en la clase :2: Panel2 184548 a 184548 (**0 nuevos**); Panel3 43598 a
  43817 (**+219**, 0.0247 por ciento de lo que envio desde 2172A), requeues 2334 a 2352. Los descartes de
  Panel3 volvieron entre las capturas de 2172A y 2286A; la nota #642 solo cubria 2142A a 2172A.

## Banco XC .198, XC .253 y LTU .110

time_squeeze sin cambio desde 2106A (559, 591 y 1); descartes de backlog sin cambio; FDB aprendidas 39 a 40
en los XC y 1 en el LTU; sin descartes en ath0 de los XC.

## recall-first

6 de 6 consultas al vault tuvieron aciertos. No se corrio chequeo scholar (no se pidio).

## Etapas 2310A y 2311A

La nota #644 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista. La primera corrida vio 685 notas antes y
689 despues; el constructor se volvio a correr para corregir una frase. El tablero se reconstruyo con 356
recibos en la banda, 0 apellidos y 0 alias; el servidor :8787 responde HTTP 200 y sirve la banda nueva.
MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado; 2286A no escribio nada.
- Los paneles difieren en carga, estaciones y perfil de planificacion: no es un A/B controlado y no se
  nombra ninguna causa.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se
  verifico por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Seguir los descartes de la clase :2 de Panel3 en la proxima auditoria.
- Revisar el enlace cableado de eth0 de Panel1 por los errores de FIFO.

Recibos: `stage2310a_cotimed_12vector_settlement_and_guarida_qdisc_note644_receipt.json`,
`stage2311a_command_center_1536a_2315a_refresh_receipt.json`, `stage2313a_memorymaster_ingest_receipt.json`,
`stage2315a_wave212_opus2_gate.json`.
