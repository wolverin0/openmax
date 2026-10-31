<!-- doc-head: Stage 2966A (W346 P1) ES: evidencia con fuentes para dimensionar fq de mac80211 (fq_memory_limit, fq_limit, fq_quantum), AQL, BQL y netdev_max_backlog en un AP ath79/ath10k de 56 MB con OpenWrt 24.10; defaults upstream (16 MiB, 8192, 300) y la excepcion de 4 MiB solo para no-VHT; truesize medido 2048-2226 B; etiquetas cruzadas fq_overlimit/fq_overmemory en debugfs; set de valores recomendado; CONFIRMED vs INFERRED vs UNKNOWN -->
Que cubre: que asumen los defaults de mac80211, que dicen las fuentes sobre equipos de poca RAM, cuanto ocupa de verdad cada paquete en cola, como entra AQL, y el set de valores recomendado contra lo medido.
Estado: investigacion offline. Cero SSH, cero cambios en equipos. Valores PROPUESTOS, NO APLICADOS; van primero al banco.
Datos maquina: artifacts/autoresearch/wave346_small_ram_queue_research.json. Fuentes: notas `research/notes/` con tag wave346; log en research/notes/wave346_small_ram_queue_scholar_log.md.
Horas: Argentina (UTC-3). Leer cuando: antes de tocar colas en un AP de 64 MB, o antes de leer `fq_overmemory` del debugfs `aqm`.
<!-- /doc-head -->
# Stage 2966A: colas en un AP de poca RAM, evidencia (W346 P1)

## 1. Respuesta corta

- **mac80211 asume RAM de sobra en hardware VHT.** El default es 16 MiB y 8192 paquetes. La unica concesion a poca RAM es 4 MiB, y solo si la placa no tiene VHT. El QCA9882 de .84 es VHT, asi que arranca con 16 MiB en un equipo de 56 MB.
- **Cada paquete reenviado ocupa unos 2048 B en el fq**, sin importar su tamaño: medido en banco y coherente con el driver ag71xx.
- **El limite que manda debe ser el de paquetes**, derivado del retardo, y el de memoria solo lo respalda.
- **Las etiquetas del debugfs estan cruzadas:** `fq_overmemory` cuenta todas las caidas del fq, y `fq_overlimit` cuenta las caidas por memoria. Esto cambia como se leen datos anteriores (seccion 5).
- **La latencia sigue UNKNOWN:** la unica ventana completa (D) dio p95 de 172 ms. Las fuentes no la explican y no se resolvio.

## 2. Que dicen las fuentes (CONFIRMED)

| # | Fuente (nota) | Hecho |
| :-- | :-- | :-- |
| S1 | `fq_impl.h` v6.6 y v6.12 | `fq_init`: quantum 300, limit 8192, memory_limit 16 MiB |
| S2 | `fq_impl.h` v6.12 | suma `skb->truesize` en memory_usage; descarta del flujo mas gordo si backlog > limit o memoria > memory_limit; `overlimit++` en cada caida, `overmemory++` solo en las de memoria |
| S3 | `tx.c` v6.12, parche 3/3 de 2016 | 4 MiB solo si ninguna banda es VHT. La carta del parche: 16 MB "puede ser fatal" con 32 MB de RAM; 4 MB son 2048 paquetes |
| S4 | `tx.c` v6.12 | CoDel de mac80211: intervalo 100 ms, objetivo 20 ms, ECN |
| S5 | `debugfs.c` v6.12 | `aqm` imprime `fq->overmemory` como `fq_overlimit` y `fq->overlimit` como `fq_overmemory` |
| S6 | parche AQL v11 de 2019, `tx.c` | AQL por txq 5000/12000 µs, umbral 24000 µs; solo actua si el driver declara `NL80211_EXT_FEATURE_AQL` |
| S7 | LWN 454390, `ag71xx.c` | BQL limita bytes en el anillo del driver. ag71xx upstream lo usa, con anillo TX 128 y RX 256 (el arbol ag71xx propio del target ath79 no se leyo) |
| S8 | man tc-fq_codel | la qdisc fq_codel tiene memory_limit por defecto de 32 MB |
| S9 | `net.rst` | `netdev_max_backlog` cuenta paquetes de entrada, no bytes |
| S10 | Ending the Anomaly (arXiv 1703.00064) | FQ-CoDel en mac80211 con equidad de airtime baja la latencia con carga en un orden de magnitud |
| S11 | Appenzeller 2004 (doi 10.1145/1015467.1015499) | buffer = BDP/√n con n flujos largos (base de STAGE2896A) |

- **El stack desplegado es mac80211 de backports 6.12.52** (`kmod-mac80211` con version de backports 6.12.52, kernel 6.6.110, en el manifest r28959 de ath79). Por eso se leyeron las fuentes de v6.12. La version estable puntual no se leyo aparte.
- **Busqueda academica:** ningun paper da una regla de presupuesto de memoria para el fq en equipos de 32-64 MB. La pagina de OpenWrt sobre equipos 8/64 es un esbozo sin guia. La unica guia de poca RAM es el parche de 2016.

## 3. Lo medido, comparado con las fuentes

- **Defaults en el banco (LAP-120, mismo modelo que .84): 16777216 / 8192 / 300**, y backlog 1000. Coincide con S1 y S3 para VHT (CONFIRMED). Los 4 MiB de .84 del 29/10 y los 3 MiB del 27/10 son ajustes FuturaMAX, no defaults.
- **Truesize por paquete en el fq:**
  - **Banco:** 399360/195, 1245184/608 y 2801664/1368 dan **2048 B exactos** en los tres picos (CONFIRMED).
  - **Produccion, .84 el 27/10:** 514176/231 da **2226 B** en un instante (CONFIRMED, una sola lectura).
  - **Mecanismo:** ag71xx arma el skb sobre su buffer de recepcion completo (`napi_build_skb`). Por eso un ACK de 66 B ocupa lo mismo que una trama de 1514. Coincide con los "4 MB = 2048 paquetes" de S3. INFERRED: se leyo el ag71xx upstream, no el del target ath79, y los tamaños de struct en MIPS32 no se midieron.
  - **Correccion:** STAGE2896A uso 2560 B (INFERRED). El valor real es menor.
- **Banco D** (1,5 MiB / 614 / 3028 / 550, unos 79 Mbit/s de ingreso):
  - el pico de backlog fue 608 de 614, asi que manda el limite de paquetes;
  - MemAvailable minimo 6072 KiB, 72 KiB bajo el piso de 6144;
  - RTT p50/p95/p99 de 78/172/218 ms;
  - la cola es intermitente: 38 de 148 muestras.
- **Banco C, confirmacion final** (4 MiB / 2048 / 4542 / 2048):
  - MemAvailable bajo de 11900 a 5216 KiB, con 2736 KiB en el fq;
  - los otros 3948 KiB son, INFERRED, el backlog de netdev (hasta 2048 × 2048 B = 4 MiB) mas la sesion.
  - Es la segunda cola grande, y confirma el punto 3 de STAGE2896A §4.
- **AQL en .84 (27/10):** BE 1500/3000 µs, mas bajo que el default. Si ath10k-ct activa AQL es UNKNOWN: el debugfs existe igual aunque el driver no lo use.

## 4. Como interactua AQL (CONFIRMED por S6, aplicacion INFERRED)

- **Que hace:** AQL limita el airtime pendiente por estacion en el driver o firmware. Con 1500-3000 µs entran uno o dos agregados; el resto espera en el fq, donde CoDel lo controla.
- **Con AQL activo**, la cola de pie esta en el fq. `fq_limit` y `fq_memory_limit` son entonces el techo real de memoria, y el firmware casi no guarda paquetes.
- **Sin AQL**, el firmware guarda lo que permitan sus descriptores (la variante smallbuffers los reduce) y CoDel no ve ese retardo.
- **Lectura:** el p95 de 172 ms de D, con un objetivo de 20 ms, sugiere esto ultimo, o CPU saturada en un solo nucleo. Es UNKNOWN y se mide antes de prometer latencia.

## 5. Correcciones a documentos anteriores (no edite esos archivos: estan fuera de mi alcance)

1. **STAGE2896A §4.2** dice "fq_overmemory sumo 57 eventos, el fq llego a su techo". Por S5, esos 57 son **todas las caidas del fq**, por paquetes o por memoria. Las caidas por memoria en .84 son la columna `fq_overlimit`, que no se reporto.
   - **Chequeo independiente:** por S2, `overlimit ≥ overmemory` siempre. En las tres lecturas, la columna `fq_overmemory` es mayor o igual que `fq_overlimit`: 8090/0, 1612/19 y 0/0. Solo cuadra con las etiquetas cruzadas.
2. **STAGE2896A §3:** el truesize pasa de 2560 B (INFERRED) a 2048-2226 B (medido).
3. **`fq_overmemory_delta`** del gate W344 de lane 1, y del objetivo Karpathy de esta wave, mide caidas totales. Propongo dos campos:
   - `fq_drops_total_delta`, que lee la etiqueta `fq_overmemory`;
   - `fq_memory_drops_delta`, que lee la etiqueta `fq_overlimit`.

## 6. Set recomendado (PROPUESTO, NO APLICADO)

| Knob | Actual .84 (29/10) | W343 | **W346** | Por que |
| :-- | --: | --: | --: | :-- |
| fq_limit | 2048 | 614 | **577** | ⌊R·D_duro/8/1514⌋ con R 70 Mbit/s y D_duro 100 ms (intervalo CoDel, S4): cola dura de 100 ms en tramas completas |
| fq_memory_limit | 4194304 | 1572864 | **1310720** | 577 × 2226 B (peor truesize medido), redondeado hacia arriba a 256 KiB |
| fq_quantum | 4542 | 3028 | **3028** | 2 × 1514, un A-MSDU de 2 tramas por ronda; sin cambio |
| netdev_max_backlog | 2048 | 550 | **550** | una pasada de softirq a pico con 50 % de margen; sin cambio. Memoria: 550 × 2048 B = 1100 KiB |
| AQL BE | 1500/3000 µs | — | **sin cambio** | primero confirmar que AQL esta activo |
| BQL eth0 | kernel | — | **sin cambio** | ya acota el anillo; la qdisc fq_codel encima (32 MB por defecto) solo se llena hacia eth |

- **Presupuesto** (mismo metodo que STAGE2896A §6):
  - peor caso de colas: 1280 (fq) + 1100 (backlog) + 512 (qdisc eth0, supuesto) + 256 (sockets) = **3148 KiB**;
  - con el reposo de 14260 KiB, MemAvailable con todo lleno queda en **7528 KiB**, sobre el piso de 6144.
- **Contra el banco D:** bajar de 614 a 577 ahorra unos 74 KiB, que es el faltante de D (6072 contra 6144). No lo prueba: D corrio con /tmp sucio y otro reposo.
- **Condicion:** sin frenar la deriva en reposo, ningun set alcanza (STAGE2896A §6). El arreglo del admitter de la W344 todavia no esta desplegado.
- **Panel2 (7 CPE) y Panel3:** misma formula. Solo cambia R si su tasa de diseño es otra.

## 7. Que falta para pasar a CONFIRMED (sin SSH en esta wave)

1. **En banco:** una ventana de 300 s con el set W346 y la misma carga que D. Medir:
   - el minimo de MemAvailable;
   - las dos columnas de caidas;
   - el p95 de RTT con el ping en un flujo propio.
2. **Lectura de solo lectura en .84:** si `iw phy phy0 info` muestra AQL, cual ath10k corre, y la qdisc de eth0 (no hay `tc`).
3. **Latencia:** si D sigue en un p95 mayor a 100 ms con la cola del fq chica, el retardo no esta en el fq. Ningun valor de fq lo arregla.

## 8. Limites

- No se corrio el pipeline V8 completo de hyperresearch. Se uso `scholar search` mas `fetch-batch` de fuentes primarias: 15 notas de fuentes y 1 log de busqueda, mas un fallo HTTP 403 en ACM Queue.
- El truesize de produccion es una sola lectura. R = 70 Mbit/s y la qdisc de eth0 son supuestos heredados de STAGE2896A.
- Sin IPs completas, MACs ni nombres de abonados.
