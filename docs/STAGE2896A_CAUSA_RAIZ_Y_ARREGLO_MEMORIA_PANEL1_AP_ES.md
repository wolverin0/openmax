<!-- doc-head: Stage 2896A (W343 P1b) ES: presupuesto de memoria del AP de Panel1 (.84, ath79, 56 MB) con 3 CPE; contabilidad de meminfo, factor truesize, fq de mac80211, backlog de netdev con RPS, min_free_kbytes, piso de MemAvailable; derivacion por BDP y retardo objetivo de fq_memory_limit, fq_limit, fq_quantum y netdev_max_backlog; regla de higiene de /tmp; evidencia pendiente -->
Que cubre: por que MemAvailable cayo de 15 MiB a 6 MiB en reposo y despues a 2 MiB con carga, cuanto puede ocupar cada cola en el peor caso, los valores derivados y si entran en el presupuesto.
Estado: solo analisis, sin acceso a equipos. Los valores son PROPUESTOS y NO APLICADOS. Antes de aplicarlos tienen que confirmarlos la prueba de carga en banco (lane 4) y la tendencia horaria (lane 2).
Datos maquina: artifacts/autoresearch/wave343_panel1_ap_memory_budget.json. Mediciones: artifacts/autoresearch/wave342_panel1_ap_memory_measurements.json (lane 2) y artifacts/autoresearch/wave342_bench_lap120_memory_repro.json (lane 4).
Horas: Argentina (UTC-3). Leer cuando: antes de cambiar colas o buffers en un AP de 64 MB, o antes de dejar archivos en /tmp de un equipo de produccion.
<!-- /doc-head -->
# Stage 2896A: causa raiz y arreglo de memoria del AP de Panel1 (W343 P1b)

## 1. Resumen

- **La caida tiene dos partes.**
  - **En reposo**, el AP perdio unos 8 MiB en horas: MemAvailable leia 6,5-9 MiB el 28/10 a la noche y 14,3-18 MiB despues del reinicio del 29/10.
  - **Con carga**, las colas tomaron lo que quedaba (2,1-3,2 MiB a las 14:59-15:01 y 1,9 MiB a las 15:05).
- **Con los valores actuales** (fq 4 MiB, backlog 2048 con RPS activo), el peor caso de colas suma unos 9,8 MiB. Eso no entra ni en el AP recien reiniciado.
- **Los valores derivados** suman 3,6 MiB de peor caso y entran con margen. Pero solo alcanzan si se frena la deriva en reposo: con la memoria del 28/10 tampoco entrarian.
- **El candidato principal de la deriva es la basura en /tmp** (tmpfs cuenta como memoria no disponible). En el banco, 8,9 MB de restos en /tmp dejan 6,2 MB disponibles en reposo, el mismo rango que .84 antes del incidente. En .84 no hay medicion de /tmp previa al reinicio (pendiente).

## 2. Mediciones de .84 (29/10 16:33 local, 75 min despues del reinicio, lane 2)

| Campo de /proc/meminfo | KiB |
| :-- | --: |
| MemTotal | 56120 |
| MemFree / MemAvailable | 13100 / 15276 |
| Cached (incluye Shmem 840) | 13472 |
| AnonPages / Mapped | 4244 / 7316 |
| Slab (SReclaimable 1868, SUnreclaim 6548) | 8416 |
| KernelStack / PageTables / VmallocUsed / Percpu | 432 / 424 / 856 / 32 |
| **Sin contar en ningun campo** | **15144** |

- **Los 15 MiB sin contar** son paginas que se piden directo al asignador de paginas: anillos DMA de ath10k y ag71xx, y fragmentos de pagina de los datos de skb. **Los datos de los paquetes no aparecen en Slab**: solo la cabecera sk_buff esta en slab.
- **No hay detalle por cache de slab:** /proc/slabinfo no existe en este kernel.
- **Procesos con mas RSS:**
  - udapi-bridge 3892 KiB;
  - hostapd 3252 + 1268;
  - wpa_supplicant 2904 + 1276;
  - uhttpd 2016;
  - rpcd 2004.

  El RSS incluye paginas compartidas, asi que no se suma a Slab.
- **Valores actuales:**
  - fq 4194304 / 2048 / 4542, con fq_backlog 0 y fq_memory_usage 0 en el instante de la lectura;
  - netdev_max_backlog 2048;
  - udp_rmem_min y udp_wmem_min 16384;
  - rmem_default y wmem_default 180224;
  - udp_mem 1251/1671/2502 paginas;
  - min_free_kbytes 4096.
- **Script persistido:** sha 01e5f0a0f802. Ademas fija `rps_cpus=1` en eth0, br-lan y phy0-ap0* (punto 6).
- **Telemetria posterior al reinicio (15:25-16:40 local):** MemAvailable en reposo entre 14260 y 18060 KiB.

## 3. Factor truesize: valor y fuente

- **Que limita mac80211:** el fq suma `skb->truesize` en `fq->memory_usage` y descarta del flujo mas gordo cuando pasa `fq_memory_limit` (`include/net/fq_impl.h`). El limite ya esta en bytes truesize, no en bytes de aire.
- **Como se define truesize:** `SKB_TRUESIZE(X) = X + SKB_DATA_ALIGN(sizeof(sk_buff)) + SKB_DATA_ALIGN(sizeof(skb_shared_info))` (`include/linux/skbuff.h`).
- **Por que no depende del tamaño del paquete:** un paquete reenviado conserva el buffer de recepcion del driver, que es de tamaño completo.
- **Valor usado:** truesize ≈ **2560 B por paquete**, INFERRED: unos 2 KiB de datos de recepcion mas el objeto sk_buff y la alineacion. No se midio en este kernel.
- **Factor para tramas completas:** k = 2560 / 1514 = **1,69**. Para paquetes chicos, como los ACK TCP, el factor es mucho mayor; por eso hace falta un limite en paquetes (`fq_limit`) ademas del limite en bytes.
- **Como medir k en el banco:** `fq_memory_usage / fq_backlog` da el truesize medio por paquete en cola.

## 4. Por que se perdio la memoria

1. **Deriva en reposo, de 15 a 6,5 MiB.** Shmem, la memoria de tmpfs, no se puede liberar sin swap.
   - **El analogo del banco:** el mismo modelo, con 8876 KiB de Shmem (5616 KiB de restos FuturaMAX y 800 KiB de firmwares de prueba), queda en 6236 KiB disponibles.
   - **En .84:** antes del reinicio llevaba unas 48 h encendido y varias waves le escribieron en /tmp. Tras el reinicio, /tmp quedo limpio (Shmem 840) y MemAvailable volvio a unos 15 MiB.
   - **Cuanto:** la diferencia, unos 8 MiB, coincide en orden de magnitud con el Shmem del banco.
   - **Confianza:** INFERRED, alta como orden de magnitud. Falta medir la tendencia en .84.
2. **Las colas con carga, de 6,5 a 2 MiB.**
   - fq_overmemory sumo 57 eventos entre las 22:25 del 28/10 y las 14:59 del 29/10, asi que el fq llego a su techo.
   - 6,5 MiB en reposo menos 4 MiB de fq dan unos 2,5 MiB, que es lo que se leyo a las 14:59-15:01.
   - Con 2 MiB, el kernel entra en reclaim directo: vuelve a leer paginas de codigo desde squashfs, y descomprimir xz cuesta CPU. Eso explica la carga de 13 a las 15:05 y que dropbear no pudiera hacer fork entre las 15:14 y las 15:20.
3. **El backlog de netdev si esta en el camino.** Corrijo STAGE2872A: ahi deje dicho que NAPI lo saltea.
   - Con `rps_cpus=1`, cada paquete recibido en eth0, br-lan y phy0-ap0* pasa por `enqueue_to_backlog` (`net/core/dev.c`).
   - Ese backlog esta limitado en paquetes (`netdev_max_backlog`), no en bytes.
   - Peor caso actual: 2048 × 2560 B = 5 MiB.
   - En un SoC de un solo nucleo, RPS no aporta paralelismo: solo agrega esta cola.
4. **Minimos de socket.** `udp_rmem_min` y `udp_wmem_min` de 16384 cuestan como mucho unos 192 KiB mas que el default de 4096, en los ~8 sockets UDP del AP (ntpd, udapi-bridge y otros). Es despreciable y no se cambia.
5. **Fuga en slab:** no se puede descartar sin slabinfo. SUnreclaim 6548 KiB queda como linea base para la tendencia de lane 2.

## 5. Derivacion de los valores

**Datos de entrada:**
- tasa de diseño R = 70 Mbit/s;
- pico medido R_pico = 147,92 Mbit/s (3 CPE, 20 MHz, W334);
- RTT de abonado 50 ms (INFERRED: entre 10 y 15 ms al core mas el upstream);
- retardo objetivo de CoDel en mac80211 D_obj = 20 ms;
- intervalo D_duro = 100 ms;
- A-MSDU de 2 tramas (`htt_max_amsdu_ampdu 2 64`);
- intervalo maximo entre pasadas del softirq T = 20 ms (`netdev_budget_usecs` 20000).

**Por que D_duro = 100 ms:** es el intervalo de CoDel. CoDel deja crecer la cola hasta ese punto antes de que su ley de control empiece a descartar. Una cola dura mas larga no suma throughput, solo retardo y memoria. La cola estable la sostiene CoDel en D_obj.

| Magnitud | Formula | Valor |
| :-- | :-- | --: |
| BDP | R · RTT / 8 | 437 500 B |
| BDP con 10 flujos | BDP / √10 | 138 350 B |
| Cola estable al objetivo | R · D_obj / 8 | 175 000 B |
| Cola dura en aire | R · D_duro / 8 | 875 000 B |
| **fq_memory_limit** | R · D_duro / 8 · k = 1 479 524 → redondeado hacia arriba a paso de 256 KiB | **1 572 864 B (1,5 MiB)** |
| **fq_limit** | ⌊fq_memory_limit / truesize⌋ | **614 paquetes** |
| **fq_quantum** | htt_max_amsdu · 1514 | **3028 B** |
| Margen del fq al pico | fq_memory_limit / k / (R_pico / 8) | 50,3 ms ≥ 2·D_obj ✓ |
| pps pico | R_pico / (1514 · 8) · 1,5 (incluye 1 ACK cada 2 segmentos) | 18 319 pps |
| **netdev_max_backlog** | pps_pico · T · 1,5 = 549,6 → redondeado a 10 | **550** |

- **fq_limit:** con este valor el limite en bytes manda para tramas completas y el limite en paquetes manda para paquetes chicos. Los dos dan el mismo techo de memoria.
- **fq_quantum:** permite que cada flujo saque un A-MSDU completo por ronda de DRR. 4542 son 3 tramas: mas de lo que agrega el firmware, con una equidad mas gruesa y unos 0,52 ms extra contra 0,35 ms por ronda a 70 Mbit/s.
- **Margen al pico:** al pico medido, el fq todavia guarda 50 ms de rafaga sobre el objetivo, asi que el limite no recorta throughput.
- **netdev_max_backlog:** cubre una pasada de softirq a pico con 50 % de margen. El valor actual, 2048, es 3,7 veces ese peor caso.

## 6. Presupuesto de memoria (KiB)

- **Piso:** MemAvailable ≥ **6144** en el peor caso de ocupacion de colas. Es el mismo umbral del guard del daemon de lane 2. Por debajo de unos 2 MiB se vio reclaim con thrash y fallas de fork.
- **min_free_kbytes = 4096: se mantiene.** Es la reserva para asignaciones atomicas del softirq, y MemAvailable ya la descuenta.
  - Una pasada de softirq puede rellenar `netdev_budget` 600 × 2560 B = 1,5 MiB.
  - Con 2× de margen hacen falta unos 3 MiB, y 4096 lo cubre.
  - Subirla le resta memoria disponible 1:1; bajarla arriesga fallas de GFP_ATOMIC en un equipo que reenvia trafico.

| Partida | Derivado | Actual |
| :-- | --: | --: |
| MemAvailable en reposo (minimo tras el reinicio) | 14260 | 14260 |
| − piso | 6144 | 6144 |
| − picos de userspace (1 sesion SSH + 1 corrida del hotplug), INFERRED | 2048 | 2048 |
| − tope de /tmp (seccion 7) | 512 | 512 |
| − reserva de deriva (pendiente de la tendencia) | 1024 | 1024 |
| **= presupuesto de colas** | **4532** | **4532** |
| fq al limite | 1536 | 4096 |
| backlog al limite (× 2560 B) | 1375 | 5120 |
| qdisc de eth0 (pendiente) + sockets | 512 + 256 | 512 + 256 |
| **Peor caso de colas** | **3679 ✓** | **9984 ✗** |
| MemAvailable con todo lleno | 6997 (≥ piso) | 692 |

**Advertencia:** con el reposo del 28/10 (6480 KiB), incluso los valores derivados dejan 6480 − 3679 − 2048 = 753 KiB. Bajar las colas sin frenar la deriva no alcanza.

## 7. Regla de higiene de /tmp para nuestros scripts (equipos de 64 MB)

1. **Un solo prefijo por corrida:** `/tmp/fmx_<wave>_*`. Cada script borra lo suyo con `trap ... EXIT`, y la sesion termina con un `ls /tmp/fmx_*` que debe salir vacio.
2. **Tope total de 512 KiB de archivos FuturaMAX en /tmp.** Antes de copiar algo:
   - se comprueba que `used + tamaño` quede bajo el tope;
   - se comprueba que `MemAvailable − tamaño` quede sobre el piso, porque tmpfs ocupa RAM 1:1.
3. **Firmwares y binarios en /tmp de produccion:** solo durante una ventana de flasheo autorizada, y se borran al terminar.
4. **Las copias de rollback que tienen que sobrevivir un reinicio van a /overlay.** La copia que W338 dejo en /tmp se perdio en el reinicio de las 15:20.
5. **Los logs en /tmp se truncan a 64 KiB.** En el banco, `fmx_wds_churn_healer.log` llego a 308 KiB.

## 8. Evidencia pendiente (antes de aplicar)

**Lane 2, tendencia horaria en .84 durante 24 h** (una sola sesion por hora, sin otras sondas):
- campos: MemAvailable, Shmem, Slab, SUnreclaim, AnonPages, los KiB sin contar, `du -s /tmp` y el delta de fq_overmemory;
- interpretacion:
  - si la caida en reposo sigue a Shmem, se confirma la causa 1;
  - si sigue a SUnreclaim o a lo sin contar, hay una fuga en el kernel o en el driver, y la causa 1 se descarta como principal.
- tambien:
  - la velocidad de eth0 (`/sys/class/net/eth0/speed`) y `tc -s qdisc show dev eth0` (memory_limit), para reemplazar los 512 KiB supuestos;
  - las estaciones leidas tambien en las interfaces WDS `phy0-ap0.staN`: el export de 16:33 las salteo y por eso mostro 0 estaciones.

**Lane 4, prueba de carga en banco con el camino probado** (tx_packets de la estacion antes y despues):
- 10 min con los valores actuales y 10 min con los derivados, a ≥ 70 Mbit/s;
- medir el maximo de fq_memory_usage, el minimo de MemAvailable, el truesize medio (`fq_memory_usage / fq_backlog`), las caidas del backlog (segunda columna de `/proc/net/softnet_stat`), el goodput y el p95 de RTT.

**Criterio de aceptacion para .84:**
- k medido ≤ 1,9;
- MemAvailable minimo con carga ≥ 6144;
- goodput con los valores derivados ≥ 97 % del de los actuales;
- p95 sin empeorar.

**Abierto, decision aparte:** sacar `rps_cpus=1` en un SoC de un nucleo elimina el backlog del camino de recepcion. Hay que medirlo en banco antes de proponerlo.

## 9. Limites

- Sin acceso a equipos en esta etapa. telemetry.db se abrio con mode=ro.
- El truesize, el RTT de abonado, los picos de userspace y la qdisc de eth0 son INFERRED y estan marcados como tales.
- Tamaño de pagina asumido: 4 KiB (smaps no se exporto). No hay datos de slab por cache.
- Labels con los dos ultimos octetos; sin MACs ni nombres de abonados.
