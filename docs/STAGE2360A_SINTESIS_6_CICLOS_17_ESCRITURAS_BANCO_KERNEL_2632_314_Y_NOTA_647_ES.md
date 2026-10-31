<!-- doc-head: Wave 220 (2358A-2363A) sintesis ES: nota #647 con los seis ciclos de escritura y restauracion en RAM del banco (2143A, 2173A, 2203A, 2257A, 2287A y 2323A; XC .198, XC .253 y LTU .110); 17 escrituras, 17 restauradas, watchdog de 60 s por ciclo, 0 por ciento de perdida ICMP en cpe_41 y cpe_80; tcp_early_retrans y tcp_thin_linear_timeouts no existen en el kernel 2.6.32 de los XC y solo corrieron en el LTU; una repeticion exacta; banda :8787 a 1536A..2363A; SIN campeon -->
# Reporte ejecutivo - Nota #647: seis ciclos, 17 escrituras del banco y la division por kernel

**Wave 220 - Etapas 2358A-2363A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizaron los seis ciclos de escritura y restauracion del banco en la nota evergreen #647. Se regeneraron
las paginas de indice del vault, el feed del Command Center :8787 se amplio a 1536A..2363A y las tres docs
maestras siguen en 179 lineas con 0 apellidos. Titular honesto: **no hay campeon de trafico nuevo**, ningun valor
de knob queda aplicado y no hay cambios permanentes.

Alcance de lectura: solo los seis recibos de ciclo (2143A, 2173A, 2203A, 2257A, 2287A y 2323A). No se abrio
ningun archivo de RE binario ni de desensamblado; el constructor rechaza cualquier otro recibo.

## Aclaraciones sobre el pedido

- El pedido dice que el LTU corre Linux 3.14. Los seis recibos solo registran el kernel de los XC (2.6.32.68);
  **la version del kernel del LTU no esta en este alcance**, asi que no se repite.
- Los "2 huecos" no ejecutables son uno por XC, y a cada uno le faltan las dos variables: 4 ausencias en total.
- El watchdog de 60 s figura una vez por ciclo; los recibos no lo detallan escritura por escritura.
- Hay una **repeticion exacta**: 2323A iteracion 1 (tcp_early_retrans de 3 a 0 en .110) repite 2203A iteracion 3.
  Las 17 escrituras cubren 16 combinaciones distintas.

## Matriz por equipo (base, valor escrito, lectura final)

| knob | XC .198 | XC .253 | LTU .110 |
| --- | --- | --- | --- |
| ath0 tx_queue_len | 2173A 1000, 256, 1000 | - | - |
| eth0 tx_queue_len | 2203A 1000, 256, 1000 | 2257A 1000, 256, 1000 | 2173A 256, 1000, 256 |
| netdev_budget | 2143A 600, 300, 600 | - | 2143A 300, 600, 300 |
| netdev_max_backlog | - | 2143A 768, 1000, 768 | - |
| tcp_dsack | - | 2173A 1, 0, 1 | 2257A 1, 0, 1 |
| tcp_early_retrans | - | - | 2203A y 2323A 3, 0, 3 |
| tcp_frto | 2257A 2, 0, 2 | 2203A 2, 0, 2 | - |
| tcp_mtu_probing | 2287A 0, 1, 0 | - | 2287A 0, 1, 0 |
| tcp_reordering | - | 2287A 3, 6, 3 | - |
| tcp_thin_linear_timeouts | - | - | 2323A 0, 1, 0 |

## La division por kernel (2323A)

- tcp_early_retrans y tcp_thin_linear_timeouts **no existen** en XC .198 ni en XC .253 (kernel 2.6.32.68). Una
  lectura de solo lectura lo comprobo y el ciclo marco esos huecos como **no ejecutables**, sin escribir nada.
- En el LTU .110 corrieron las dos: tcp_early_retrans de 3 a 0 y vuelta a 3, tcp_thin_linear_timeouts de 0 a 1 y
  vuelta a 0. Las dos se restauraron.

## Restauracion y perdida

- **17 de 17 escrituras restauradas**: lectura final igual a la base y restauracion completa verificada. Las 17
  tomaron efecto; 0 escrituras a flash; RF sin arrancar; ningun knob PROTECTED.
- Las mediciones OTA de los seis ciclos nombran cpe_41 y cpe_80. Perdida ICMP **0 por ciento** en los 17 resumenes.
- Las mediciones son del enlace ambiente de Panel1 .84: los radios del banco no llevan carga, asi que no se mide
  ningun efecto de retransmision, cola ni aire. Las etiquetas "keep" del arnes son sobre trafico ambiente y no
  son mejoras.

## recall-first

5 de 6 consultas al vault tuvieron aciertos; tcp_thin_linear_timeouts no tenia notas previas. No se corrio chequeo
scholar (no se pidio).

## Etapas 2358A y 2359A

La nota #647 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista (el vault paso de 693 a 696 notas). El tablero se
reconstruyo con 376 recibos en la banda, 0 apellidos y 0 alias; el servidor :8787 responde HTTP 200 y sirve la
banda nueva. MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo**, sin valor de knob conservado y sin cambios permanentes.
- Escribir y restaurar sin perdida prueba que estos knobs son seguros de tocar; no dice nada de su efecto. No es
  un A/B controlado.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico
  por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Una prueba con carga donde el equipo del knob reenvie el trafico medido.
- No repetir combinaciones ya probadas en los proximos ciclos del banco.

Recibos: `stage2358a_six_cycle_17write_bench_matrix_and_kernel_2632_314_split_note647_receipt.json`,
`stage2359a_command_center_1536a_2363a_refresh_receipt.json`, `stage2361a_memorymaster_ingest_receipt.json`,
`stage2363a_wave220_opus2_gate.json`.
