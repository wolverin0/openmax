<!-- doc-head: Wave 201 (2244A-2249A) sintesis ES: nota #640 une el ciclo reversible 2203A (tx_queue_len de eth0 1000 -> 256 en .198, tcp_frto 2 -> 0 en .253, tcp_early_retrans 3 -> 0 en .110, todo restaurado) con los ciclos 2173A y 2143A y las auditorias de solo lectura 2172A (colas) y 2202A (puente): 9 de 9 escrituras restauradas, 0 por ciento de perdida ICMP, sin efecto atribuido; banda :8787 a 1536A..2249A; SIN campeon -->
# Reporte ejecutivo - Nota #640: ciclos tx_queue_len, tcp_frto, tcp_dsack y contexto de puente

**Wave 201 - Etapas 2244A-2249A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizo el ciclo en vivo stage2203A junto con los ciclos 2173A y 2143A y las auditorias de solo
lectura 2172A y 2202A en la nota evergreen #640. Se regeneraron las paginas de indice del vault, el feed del
Command Center :8787 se amplio a 1536A..2249A y las tres docs maestras siguen en 179 lineas con 0
apellidos. Titular honesto: **no hay campeon de trafico nuevo** y ningun valor de knob queda aplicado.

Alcance de lectura: solo los recibos 2203A, 2202A, 2173A, 2172A y 2143A. No se abrio ningun archivo de RE
binario ni de desensamblado; el constructor rechaza cualquier otro recibo.

Aclaraciones sobre el pedido:

- 2203A, 2173A y 2143A son ciclos de escritura y restauracion en RAM, no telemetria; solo 2172A y 2202A son
  de solo lectura.
- El "dsack" del nombre corresponde a 2173A (tcp_dsack 1 -> 0 en .253); 2203A probo tcp_frto y
  tcp_early_retrans.
- Un knob por iteracion: tx_queue_len de eth0 solo en .198, tcp_frto solo en .253 y tcp_early_retrans solo
  en .110 (el unico kernel que lo tiene).

## stage2203A - el ciclo

- A1 -> B1 -> A2 -> B2, 3 iteraciones, watchdog de 60 s, parada por maximo de iteraciones.
- Iteracion 1: tx_queue_len de eth0 1000 -> 256 en XC .198; lectura final 1000; p95 de cpe_41 13.03 ms.
- Iteracion 2: tcp_frto 2 -> 0 en XC .253; lectura final 2; p95 27.087 ms.
- Iteracion 3: tcp_early_retrans 3 -> 0 en LTU .110; lectura final 3; p95 23.304 ms.
- Las tres escrituras tuvieron efecto y **todas se restauraron** (1000, 2 y 3); 0 escrituras a flash, RF
  sin arrancar; perdida ICMP 0 por ciento en cpe_41 y cpe_80.
- La lectura base de eth0 en .198 coincide con la de 2172A. B = 256 es el valor de phy0-ap0 en OpenWrt;
  eth0 en los paneles airOS corre 1000.

## Tres ciclos de banco en el alcance (9 escrituras)

- 2143A: netdev_budget 600 -> 300 en .198, netdev_max_backlog 768 -> 1000 en .253, netdev_budget 300 -> 600
  en .110.
- 2173A: tx_queue_len de ath0 1000 -> 256 en .198, tcp_dsack 1 -> 0 en .253, tx_queue_len de eth0 256 ->
  1000 en .110.
- 2203A: tx_queue_len de eth0 1000 -> 256 en .198, tcp_frto 2 -> 0 en .253, tcp_early_retrans 3 -> 0 en
  .110.
- **9 de 9 escrituras restauradas** y 0 por ciento de perdida ICMP en todos los pliegues. El goodput es
  trafico ambiente: **no se atribuye** efecto de cola, de recuperacion de perdidas ni en el aire.
- No hay repeticiones exactas dentro de estos tres ciclos. La iteracion 1 de 2203A repite el contraste
  1000 -> 256 de 2173A en .198, pero en eth0 en vez de ath0. La comparacion con ciclos anteriores a 2143A
  no se corrio (fuera del alcance de lectura).
- Rango de pliegues: fmx_loss de 0.580987 a 1.083548; p95 de 3.952 a 41.768 ms. Solo la iteracion 3 de
  2173A supera el maximo del piso de la nota #637 (31.542 ms).
- Cada etiqueta "keep" del harness es sobre trafico ambiente: la linea base inicial de cada ciclo y la
  "mejora" de la iteracion 2 de 2173A. No es una mejora.

## stage2202A - contexto de puente (solo lectura)

Entradas FDB (locales / aprendidas): Panel2 2 / 441, Panel3 2 / 441, XC .198 2 / 39, XC .253 3 / 39, LTU
0 / 1. Panel1 no tiene la herramienta: queda **sin medir**. No se imprime ninguna MAC y ningun ciclo
escribio ajustes de puente.

## recall-first

4 de 6 consultas al vault tuvieron aciertos (tx_queue_len, tcp_dsack, netdev_budget y fdb); tcp_frto y
tcp_early_retrans, ninguno. No se corrio chequeo scholar (no se pidio).

## Etapa 2244A - vault

La nota #640 quedo en research/notes/scholar_sources/ como evergreen. `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y 15 paginas de indice la listan, _recent.md entre ellas. La
corrida vio 675 notas antes y 677 despues.

## Etapa 2245A - banda 1536A..2249A y docs maestras

El tablero se reconstruyo con 322 recibos en la banda, 0 apellidos y 0 alias en toda la pagina; 2203A y
2244A aparecen en el feed con su clase de evidencia. Los recibos 2250A y 2251A (de otras lineas) quedan
fuera a proposito. El servidor :8787 responde HTTP 200 y sirve la banda nueva. MASTER, CURRENT y CURATED
siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado.
- Los radios del banco no tienen carga ni par por aire: ningun ciclo puede mostrar un efecto.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se
  verifico por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Una prueba con carga donde el host del knob reenvie el trafico medido, en vez de mas ciclos de banco.

Recibos: `stage2244a_txqueuelen_frto_dsack_and_bridge_telemetry_note640_receipt.json`,
`stage2245a_command_center_1536a_2249a_refresh_receipt.json`, `stage2247a_memorymaster_ingest_receipt.json`,
`stage2249a_wave201_opus2_gate.json`.
