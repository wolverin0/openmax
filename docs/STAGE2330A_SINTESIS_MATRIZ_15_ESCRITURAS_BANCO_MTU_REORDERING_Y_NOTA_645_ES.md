<!-- doc-head: Wave 215 (2328A-2333A) sintesis ES: nota #645 con la matriz de escrituras reversibles en RAM del banco (XC .198, XC .253 y LTU .110); la lista permitida nombra cinco recibos pero 2233A es un refresco del tablero, asi que son 4 ciclos y 12 escrituras, no 15; 12 de 12 restauradas, watchdog de 60 s por ciclo, 0 por ciento de perdida ICMP en cpe_41 y cpe_80 (cpe_223 no aparece); 2287A suma tcp_mtu_probing y tcp_reordering; banda :8787 a 1536A..2333A; SIN campeon -->
# Reporte ejecutivo - Nota #645: matriz de escrituras del banco con MTU probing y reordering

**Wave 215 - Etapas 2328A-2333A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizaron los ciclos de escritura y restauracion del banco de la lista permitida en la nota evergreen #645.
Se regeneraron las paginas de indice del vault, el feed del Command Center :8787 se amplio a 1536A..2333A y las
tres docs maestras siguen en 179 lineas con 0 apellidos. Titular honesto: **no hay campeon de trafico nuevo**, ningun
valor de knob queda aplicado y no hay cambios permanentes.

Alcance de lectura: solo los cinco recibos de la lista (2173A, 2203A, 2233A, 2257A y 2287A). No se abrio ningun
archivo de RE binario ni de desensamblado; el constructor rechaza cualquier otro recibo.

## Aclaraciones sobre el pedido

- **Son 12 escrituras, no 15.** 2233A es el recibo del refresco del tablero de la Wave 199, sin ninguna escritura.
  Los cuatro ciclos reales (2173A, 2203A, 2257A y 2287A) tienen tres iteraciones cada uno. No se abrio ningun ciclo
  fuera de la lista para completar el numero.
- **cpe_223 no aparece** en ninguna medicion de estos ciclos: solo cpe_41 y cpe_80.
- El watchdog de 60 s figura una vez por ciclo; los recibos no lo detallan escritura por escritura.
- No hay campeon porque el banco no tiene carga ni par OTA, asi que no se mide ningun efecto del knob; no es solo
  por no tener abonados.

## Matriz por equipo (base, valor escrito, lectura final)

| knob | XC .198 | XC .253 | LTU .110 |
| --- | --- | --- | --- |
| ath0 tx_queue_len | 2173A 1000, 256, 1000 | - | - |
| eth0 tx_queue_len | 2203A 1000, 256, 1000 | 2257A 1000, 256, 1000 | 2173A 256, 1000, 256 |
| tcp_dsack | - | 2173A 1, 0, 1 | 2257A 1, 0, 1 |
| tcp_early_retrans | - | - | 2203A 3, 0, 3 |
| tcp_frto | 2257A 2, 0, 2 | 2203A 2, 0, 2 | - |
| tcp_mtu_probing | 2287A 0, 1, 0 | - | 2287A 0, 1, 0 |
| tcp_reordering | - | 2287A 3, 6, 3 | - |

- Lo nuevo de 2287A: tcp_mtu_probing en .198 y en .110 (0 a 1 y vuelta a 0) y tcp_reordering en .253 (3 a 6 y
  vuelta a 3).
- tcp_mtu_probing arranca en 0 en los dos equipos donde se probo; eth0 tx_queue_len arranca distinto en los XC
  (1000) y en el LTU (256).
- Ninguna escritura se repitio exactamente.

## Restauracion y perdida

- **12 de 12 escrituras restauradas**: la lectura final igual a la base y la restauracion completa verificada.
  Las 12 tomaron efecto; 0 escrituras a flash; RF sin arrancar; ningun knob PROTECTED.
- Perdida ICMP **0 por ciento** en cpe_41 y cpe_80 en los 12 resumenes de medicion (uno por escritura, sobre sus
  cuatro rondas A1, B1, A2 y B2).
- Las mediciones son del enlace ambiente de Panel1 .84: los radios del banco no llevan carga, asi que no se mide
  ningun efecto de MTU, reordering, cola ni aire. Las etiquetas "keep" del arnes son sobre trafico ambiente y no
  son mejoras.

## recall-first

4 de 6 consultas al vault tuvieron aciertos; tcp_mtu_probing y tcp_reordering no tenian notas previas. No se corrio
chequeo scholar (no se pidio).

## Etapas 2328A y 2329A

La nota #645 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista. La primera corrida vio 689 notas antes y 692
despues; el constructor se volvio a correr para renombrar un campo del recibo. El tablero se reconstruyo con 360 recibos en la banda, 0 apellidos y 0 alias; el servidor :8787 responde HTTP 200 y sirve la banda
nueva. MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo**, sin valor de knob conservado y sin cambios permanentes.
- Escribir y restaurar sin perdida prueba que estos knobs son seguros de tocar; no dice nada de su efecto. No es
  un A/B controlado.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico
  por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Una prueba con carga donde el equipo del knob reenvie el trafico medido.
- Confirmar si la wave buscaba un quinto ciclo de banco y cual es su numero de etapa.

Recibos: `stage2328a_cross_host_15write_bench_cycle_matrix_note645_receipt.json`,
`stage2329a_command_center_1536a_2333a_refresh_receipt.json`, `stage2331a_memorymaster_ingest_receipt.json`,
`stage2333a_wave215_opus2_gate.json`.
