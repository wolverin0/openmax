<!-- doc-head: Reddit Post Update (r/wisp & r/Ubiquiti) — Clean Copy-Paste Format in English & Spanish through Stage 98D (2026-10-26) -->
# Reddit Post Update (`r/wisp` / `r/Ubiquiti`) — Zero-Table Format (Clean Copy-Paste for Mobile & Desktop)

> **Why this format**: Reddit's composer and mobile app often mangle Markdown tables (`| col | col |`). This version uses **clean bullet cards + native code/quote blocks + optional `>! Spoiler !<` tags** so it renders cleanly on both desktop and mobile when pasted into Reddit's **Markdown Editor**.

---

## 🇬🇧 English Copy-Paste Block (for `r/wisp` / `r/Ubiquiti`)

```markdown
**Title:** openMAX Update: Live production sector results on Ubiquiti airMAX AC (~10x lower wireless ping, -80% to -94% bufferbloat, 0-touch stock airOS 8 interop & multi-vendor PtMP)

Hey r/wisp,

Quick, no-fluff update on **openMAX** (https://github.com/wolverin0/openmax) — our open-source project squeezing maximum real-world performance out of existing Ubiquiti `airMAX AC` hardware (`LiteAP 120`, `Rocket Prism 5AC Gen2`, `LiteBeam 5AC Gen2`, `NanoStation 5AC Loco`).

All the deep kernel docs, scripts, and benchmark JSONs are in the repo. Here is what we have working on real hardware and in live production:

* **Switch tower APs to OpenWrt while stock `airOS 8` CPEs keep connecting out of the box:** We migrated our live sector AP (`LiteAP 120`) to OpenWrt 24.10.4 (`Linux 6.6.110`) and customer CPEs running **100% unmodified stock `airOS 8.7.25`** connected automatically. Even if a customer's radio is powered off during cutover and turned back on days later, it associates with zero touch.
* **Run multi-vendor & mixed-generation clients on the same Ubiquiti AP:** We simultaneously connect **Ubiquiti 5AC (`LiteBeam Gen2`, `Loco 5AC`, `Rocket Prism`)**, legacy **Ubiquiti M5 (`airOS 6`)**, and **MikroTik (`SXT Lite5`)** CPEs on the same sector without a single weak/obstructed client dragging everyone else down.
* **Full channel-width flexibility (`20, 40, 80 MHz`, plus `5/10 MHz` between OpenWrt radios):** On a `20 MHz` channel, our airtime scheduler hits **`0.95` Jain fairness** and nearly **`4 bit/s/Hz`** spectral efficiency.
* **Full OpenWrt AP + OpenWrt CPE in live production:** Once the AP is running OpenWrt, we remotely upgrade CPEs over the air in ~4 minutes while preserving their management IP, WebUI, hardware-accelerated NAT (`flow_offloading=1`), and the exact DHCP lease of the customer's indoor Wi-Fi router.
* **Uncovered inside `Rocket Prism` & `LTU` (`v2.4.2`) firmware:** We mapped the hardware control table for **AirPrism** active RF filtering on `Rocket Prism 5AC Gen2`, and confirmed that LTU's greyed-out **`4096-QAM` (`12X`)** and **`OFDMA`** modes have real driver and rate-table routines compiled inside `v2.4.2` (being tested on our physical bench right now).

---

### 📊 Live Production Numbers (Same tower, same rooftop radios, `20 MHz` channel — Before vs. After)

* **Unloaded Wireless Sector Ping (`p50`):**
  * Stock `airOS 8.7.25`: `22.58 ms`
  * **openMAX (OpenWrt 24.10.4):** **`1.93 ms – 2.42 ms`** -> **~10x faster (-90% base latency)**
* **Wireless Ping Jitter / Spikes (`p95`):**
  * Stock `airOS 8.7.25`: `98.77 ms`
  * **openMAX (OpenWrt 24.10.4):** **`4.47 ms – 14.90 ms`** -> **6.6x to 22x more stable (-85% to -95% jitter)**
* **Ping Under Heavy Download (Bufferbloat DL):**
  * Stock `airOS 8.7.25`: `31.49 ms` (`p50`) / `54.40 ms` (`p95`)
  * **openMAX (OpenWrt 24.10.4):** **`8.43 ms – 9.86 ms` (`p50`)** -> **3.5x to 5x lower lag (-73% to -80%)**
* **Ping Under Heavy Upload (Bufferbloat UL):**
  * Stock `airOS 8.7.25`: `195 ms – 224 ms` *(caused by airOS tshaper's 127-packet SFQ queue)*
  * **openMAX (OpenWrt 24.10.4):** **`10.37 ms – 16.64 ms` (`p50`)** -> **12x to 18x lower lag (-91% to -94%)**
* **Usable `20 MHz` Sector Capacity (Real TCP Goodput):**
  * Stock `airOS 8.7.25`: `~35 – 45 Mbps` typical
  * **openMAX (OpenWrt 24.10.4):** **`69.80 Mbps` DL / `30.74 Mbps` UL** -> **1.5x to 1.8x more capacity (+50% to +80% more Mbps/MHz)**
* **CPE CPU Headroom (Routing + NAT):**
  * Stock `airOS 8.7.25`: Kernel `2.6.32` (software NAT)
  * **openMAX (OpenWrt 24.10.4):** Kernel `6.6.110` (`flow_offloading=1`) -> **~2.5x more CPU headroom (+150% packet/s capacity)**

> **Bottom line:** On the exact same rooftop hardware and `20 MHz` channel, wireless ping is **~10x faster (`~2 ms` vs `~22 ms`)**, lag under saturation drops by **80%–94%**, and usable sector capacity increases by **+50% to +80%**.

---

### 🔌 Next up: Native UISP Reporting (`udapi-bridge`) on OpenWrt

Moving a radio to pure OpenWrt stops Ubiquiti's `/bin/udapi-bridge` agent, so UISP marks it offline.
>!We unpacked `/bin/udapi-bridge` from `WA.v8.7.25`: it does not depend on the old kernel or TDMA module; it is a userspace WebSocket (`EVP_aes_256_gcm`) client that reads `/etc/board.info`, `/tmp/system.cfg` (`unms.uri`), `/usr/www/status.cgi`, and `/bin/wstalist`. We are packaging a lightweight OpenWrt wrapper so migrated radios stay Online and green inside UISP with their original device ID and live telemetry.!<

---

### 🧪 Latest Bench Autoresearch Wins (`320+` Paired `A/B/A/B` Rounds Across 12 Physical Radios)

* **1-Knob `aql_txq_limit` (`900/1500 us`) Proof (`R165..R188` across `1 km..14 km` on `LAP-120 ↔ Loco 5AC`):** Orthogonal 1-factor ablation proved `aql_txq_limit` is the primary hardware gatekeeper (`fq_quantum`, `codel`, `airtime_flags`, `amsdu`, and `tcp_tsq` are 100% inert when `AQL` is at stock `5000/12000 us`). Lowering `aql_txq_limit` alone boosts pure `AC_BE` (`dscp=0`) bidirectional goodput by **`+3.14%` to `+15.79%` (`77.57 vs 66.99 Mbps` in `20 MHz`)** and cuts `p95` RTT by **`-33.1%` to `-40.7%`**, while adding `fq_quantum=1514` + `codel=10/50ms` raises 4-flow Jain fairness from `0.8734` to **`0.9520`**.
* **8-Flow Uplink Hammering (`R189..R194` across `1 km..14 km`):** Under heavy 8-stream uplink saturation (`dscp=0`), our stack increases UL goodput by **`+0.53%` to `+5.52%`** while cutting `p95` RTT by **`-12.1%` to `-35.7%`** (`-53.2%` `p99` at `3 km`).
* **Asymmetric Chain-Mask Rescue on Obstructed Links (`PBM5-R27..R36` on `2x PowerBeam M5 300`):** Using `/proc/net/ubnt_poll/query_mac_info`, we caught `32%–42%` PER on 2-stream `MCS 11..15` caused by a `6–8 dB` chain imbalance (`-87` vs `-79 dBm`). Pinning TX to the clean chain while keeping 2x2 MRC on RX (`txchainmask=2, rxchainmask=3`) boosted remote RSSI by **`+5 dB` (`-81 -> -76 dBm`)**, lifted CCQ from **`58%` to `95.5%`**, and slashed OTA `p95` RTT by **`-68.0%`**; enabling `ubnt_ewma_delegate_on=1` (disabled by default in airOS) cut `1400B p95` RTT by another **`-18.5%`**.
* **3-Unit `LTU` PtMP Sector (`LTU-Rocket` AP + `2x LTU-Lite` CPEs, `Stage 15` `LTU-S15-R1..R8`, `Stage 17A/17B` & `Stage 24F`):** Mapped the cross-generation TDD cyclic-zone boundary between `aflturocket.v2.1.0` (`cz_len=3`, `SYM#7`) and `afltu.v2.4.0` (`cz_len=6`, `SYM#4`), kept the bare-connector `LTU-Rocket` cool (`79 °C` at `powerout=0` / `-26 dBm`), proved 4 runtime `ame_core` wins (`multi_ack=1 + send_ctrl_in_data=1 + send_map=1`: **`+9.86%` goodput, `-47.02%` `p95` RTT**; `sched_max_agg_cnt=8`: **`-39.56%` `p95` RTT**; `sched_mcs_limit_symbol_begin=14`: **`-25.40%` `p95` RTT**; `change_ssd_pause_flag=1`: **`-17.21%` `p95` RTT**), unlocked `LTU-Lite` (`0xae08`) as a native **`AP-PtMP` Short-Queue (`SQ`, `ptmp_max_cpe=4`) and `AP-PtP` master on `v2.4.0`/`v2.4.2`** in RAM via `board_ssid=0xae05` in `/tmp/ame.cfg` (`Stage 17B`), and in **`Stage 24F` (`S24F-R1`)** proved that isolating pure symbol-window widening (`sched_mcs_limit_symbol_begin=12`, `sched_ap_mcs_limit_symbol_end=62`, `sched_mcs_limit_symbol_end=72` with `DGAIN_DL_ENABLE=0` and `pb_boost=2`) boosts goodput by **`+1.36%`** and slashes **`p95` RTT by `-38.76%` (`2.76 -> 1.69 ms`) and `p99` RTT by `-45.93%` (`4.29 -> 2.32 ms`)**.
* **3-CPE Heterogeneous & 5-Station Near-Far Sector (`Stage 13A/13B/14`, `M1-R1..R6`, `M2-R7..R12`, `S14-R1..R6`):** Simultaneously connected `NanoStation 5AC Loco` (`2x2 AC`), `Rocket Prism 5AC Gen2` (`2x2 AC`), and `LiteBeam M5` (`1x1 N`) on `5180 MHz` (`0.0%` loss with 3-chain `nft` FDB loop isolation), boosting 3-CPE goodput by **`+7.31%` (`M1-R1`)**, **`+8.65%` (`M1-R4` `airtime_weight=512:512:128`)**, and **`+10.58%` at `6000m` (`M1-R6`: `56.43 -> 62.40 Mbps`)**; in the 5-station Near-Far sector (`+2x PowerBeam M5 300` at `-81 dBm`), co-designed AP+CPE tuning delivered **`+21.63%` sector goodput (`55.66 -> 67.69 Mbps`) and `-11.85%` `p95` RTT (`M2-R11`)** (`+15.46%` holdout in `M2-R12`), and our `LAP-120` OpenWrt AP won `6/6` shootout rounds against `Rocket Prism 5AC Gen2` in `Stage 14`.
* **Incremental Champion Ladder (`Champion v1 -> v6` across `Stage 19/21/24C/24E/25` via `scholar` MCP + `hyperresearch` Dual-Engine Discovery):** Starting from our already-optimized `Champion v1` (`900/1500 us` AQL, `thresh=4000`, `fq_codel 1514/10ms/50ms`) as Baseline `A`, we stacked 5 consecutive hardware-verified upgrades:
  1. **`Champion v2` (`S19-R2`/`S19-R3`):** `retry short 5 long 4 + nf_cal_period=30 + txqueuelen=256` (**`+4.23%` goodput, `-19.77%` `p95` RTT** in 1-CPE; **`+38.55%` goodput (`51.02 -> 70.68 Mbps`)** in 2-CPE AP+Rocket STA Co-Design).
  2. **`Champion v3` (`S21-R2`/`S21-R3`):** `tcp_notsent_lowat=16384 + netdev_budget=600` (**`-12.35%` `p95` RTT** in 1-CPE; **`-9.89%` sector `p95` RTT** in 3-CPE All-Champion Co-Design).
  3. **`Champion v4` (`S24C-R1`/`S24C-R2`):** `AirBBR` TCP pacing (`ca_ratio=110, ss_ratio=150`) + `Responsible Airtime` overhead-corrected weights (`640:512:96`) + `per-AC AQL 750..1500/1500..3000` (**`+11.19%` 3-CPE goodput (`45.73 -> 50.84 Mbps`), `-22.70%` `p95` RTT**).
  4. **`Champion v5` (`S24E-R1`/`S24E-R2`):** `M2` EVM/Retry Adaptive RTS/CTS (`rts off` in 1-CPE clean SNR: **`+21.87%` goodput (`60.43 -> 73.64 Mbps`)**; `rts 512` + dynamic responsible-airtime weights in 3-CPE contention: **`+5.24%` goodput (`56.79 -> 59.76 Mbps`), `-41.98%` `p95` RTT (`110.40 -> 64.06 ms`, `>3.8x` lower `p99` RTT)**).
  5. **`Champion v6` (`Stage 25` `S25-R2`):** `M5` Asymmetric UL/DL TCP ACK Pacing (`tcp_thin_linear_timeouts=1, tcp_early_retrans=3, tcp_autocorking=0, AC_VO AQL 600/1200`) discovered via our `scholar` MCP (`jev-1.14.0`, `prob=0.97`) + `hyperresearch` (`v0.12.0`) fusion (**`+3.66%` additional 3-CPE goodput to `63.30 Mbps` mean / `64.56 Mbps` (`3.23 Mbps/MHz`) peak, and `-10.33%` additional `p95` RTT reduction (`74.73 -> 67.02 ms`, `0.0%` loss)**).
  6. **`PtMP Champion v22` & `PtP Champion v9` (`Stages 79..95C` — Kernel `.ko` Fast-Path Dissection):** Disassembling `umac.ko`, `ath_dev.ko`, `ath_pktlog.ko`, and `ubnt_poll_host.ko` across `WA` (`8.7.25`), `XC` (`8.7.11`/`8.7.25`), and `XW` (`6.1.4`/`6.3.6`) uncovered per-PPDU packet-log overhead (`rmmod ath_pktlog` on `XC`: **`+23.35%` 3-CPE sector goodput `46.53 -> 57.39 Mbps`, `-20.81%` `p99` RTT, `-22.58%` IPTV jitter, `0.00%` VoIP loss**), safe VoW telemetry bypass (`iwpriv wifi0 vow_extstats 0`), hardware WMM multi-queue dispatch (`set_multiq=3` + `AC_VO/VI/BE/BK Minfree = 0/4/8/16`), and `XW` `rcRateFind_11nViVo` (`0x26c7c`) video/voice rate protection. On dedicated `PowerBeam 5AC Gen2` PtP (`Stage 94A/95B`), `PtP Champion v9` delivered **`+41.01%` total goodput (`+70.60%` Bulk TCP), `-64.80%` `p95` RTT, `0.000%` VoIP loss**, and **hitless `802.11h` `CSA` frequency hopping (`0.000s` outage / `0/80` missed probes)**.
  7. **Zero-Touch Dynamic Channel-Width (`20 MHz <-> 40 MHz`, `Stage 95C`) & MikroTik `802.1Q` Trunk Co-Design (`Stage 97A`):** Proved on live hardware that even when a stock `airOS 8` CPE has `cwmenable=0` in `/etc/sysinit/radio.conf`, its `umac.ko` state machine in `mode=auto` automatically follows the OpenWrt AP's `VHT Operation IE` between `20 MHz` and `40 MHz` and rejoins in **`8.78s–12.10s` (`< 15s`)** with zero customer touch (**`-31.28%` IPTV jitter in `40 MHz`**). Pairing the OpenWrt AP with a MikroTik RouterBOARD (`RB951G-2HnD`, `RouterOS 6.47`) over an `802.1Q` VLAN trunk (`PCP 0..7` + `DSCP EF/CS4`) cut end-to-end `CPE -> Air -> Switch -> MikroTik` `p50` RTT by **`-54.84%` (`4.39 -> 1.98 ms`)** and `p95` RTT by **`-46.18%`**.
  8. **`AF-LTU` Dual-Core ARM Cortex-A9 SMP Isolation & `80`-Symbol `2.0 ms` Superframe (`Stages 80A, 96A, 97C, 99B`):** On `LTU-Lite` (`Beetle` SoC + `ame_ASIC0`, unlocked as `AP-PTMP(Run)` at `4096-QAM 12x`), isolating `500 Hz` TDMA `AME.mrx`/`AME.mtx` (`IRQ 52/53`) on `CPU0` while offloading `GMAC0` (`IRQ 63`) and `AME.l2p` (`IRQ 92`) `100%` to `CPU1` alongside our 5-offset `ame_dev.ko` fast-path boosted SoC TCP goodput by **`+8.5%` to `+9.9%` (`189.81 Mbps`, peak `210.28 Mbps`)** and cut loaded `p50` RTT by **`-12.5%`** with **`0` `500 Hz` superframe deadline misses**.
* **Cross-Platform Multi-Radio Gains (`Rocket Prism 5AC Gen2`, `Rocket 2AC Prism`, `airFiber 4X`):** On `Rocket Prism 5AC Gen2`, `airview1 down` + `ani_enable=0` + `swretry=4/6` cut `p50` RTT by **`-67.9%` (`1.81 ms`)**; on `Rocket 2AC Prism` (`2.4 GHz`, `Stage 98D`), `ani_enable=1` + `shpreamble=1` + `vow_extstats 0` + `IRQ 2` AirView governance eliminated `100%` of `15,480` parasitic interrupts (**`+13.0%` peak TCP, `-54.3%` `p50` RTT**); on `airFiber 4X` (`Invictus v2`), `framelength=2.5ms` + `flowcntl=on` + `cp=8` reduced TDD interrupt load from `500` to `400 Hz` (**`+15.3%` stream, `-22.8%` `p95` RTT**).

Full documentation, scripts, and benchmark receipts:
👉 https://github.com/wolverin0/openmax
```

---

## 🇦🇷 Bloque Listo para Copiar y Pegar en Español (Sin tablas que se rompan)

```markdown
**Título:** Actualización openMAX: Qué logramos en producción real sobre equipos Ubiquiti airMAX AC (~10x menos ping en el aire, -80% a -94% de lag bajo carga, multimarca y migración sin tocar al cliente)

Hola a todos,

Les comparto un resumen corto y al grano de lo que ya tenemos funcionando en producción real en nuestro WISP con **openMAX** (https://github.com/wolverin0/openmax). Toda la evidencia cruda y los scripts están en el repo; acá va lo concreto que logramos en la cancha:

* **Cambiar los AP a OpenWrt y que los CPEs con `airOS 8` original sigan conectando solos:** Podés migrar un panel (`LiteAP 120` / `Rocket`) a OpenWrt 24.10.4 y los clientes que tienen **su firmware original `airOS 8.7.25` de fábrica** se conectan solos sin tocarles nada. Si un cliente estaba apagado el día del cambio y enchufa la antena una semana después, conecta derecho.
* **Hacer funcionar equipos de todas las marcas y generaciones contra el mismo AP Ubiquiti:** En un mismo panel conectamos en simultáneo equipos **Ubiquiti 5AC (`LiteBeam Gen2`, `Loco 5AC`, `Rocket Prism`)**, equipos viejos **Ubiquiti M5 (`airOS 6`)** y equipos **MikroTik (`SXT Lite5`)**, sin que un cliente con mala señal o tapado por árboles tire abajo al resto del sector.
* **Conectar en distintos anchos de canal (`20, 40, 80 MHz`, y hasta `5/10 MHz` entre equipos OpenWrt):** En canales de `20 MHz` logramos repartir el aire de forma pareja (`0.95` de equidad Jain) sacándole casi **`4 Mbps por cada MHz` de espectro**.
* **Migrar el sector completo (AP + CPEs) a OpenWrt en vivo sin cortar al cliente:** Una vez migrado el AP, actualizamos los CPEs por aire en ~4 minutos manteniendo su IP, su interfaz web, su NAT acelerado y la misma IP del router Wi-Fi adentro de la casa del cliente.
* **Destapar lo que traen oculto los firmwares de `Rocket Prism` y `LTU` (`v2.4.2`):** Mapeamos cómo manejar el filtro activo **AirPrism** en los `Rocket Prism 5AC Gen2`, y confirmamos que la modulación **`4096-QAM` (`12X`)** y el **`OFDMA`** que Ubiquiti dejó deshabilitados en `LTU` tienen las tablas y funciones reales adentro del firmware (probándose ahora mismo en el banco).

---

### 📊 Los números reales en producción (Mismo panel, mismas antenas en el techo, canal de `20 MHz` — Antes vs. Ahora)

* **Ping base en el aire (`p50`):**
  * Antes (`airOS 8.7.25`): `22.58 ms`
  * **Ahora (`openMAX / OpenWrt 24.10.4`):** **`1.93 ms – 2.42 ms`** -> **~10x más rápido (-90% de latencia base)**
* **Estabilidad / Picos de ping (`p95`):**
  * Antes (`airOS 8.7.25`): `98.77 ms`
  * **Ahora (`openMAX / OpenWrt 24.10.4`):** **`4.47 ms – 14.90 ms`** -> **6.6x a 22x más estable (-85% a -95% de jitter)**
* **Ping descargando a tope (Bufferbloat DL):**
  * Antes (`airOS 8.7.25`): `31.49 ms` (`p50`) / `54.40 ms` (`p95`)
  * **Ahora (`openMAX / OpenWrt 24.10.4`):** **`8.43 ms – 9.86 ms` (`p50`)** -> **3.5x a 5x menos lag (-73% a -80% en hora pico)**
* **Ping subiendo a tope (Bufferbloat UL):**
  * Antes (`airOS 8.7.25`): `195 ms – 224 ms` *(por la cola SFQ de 127 paquetes de airOS)*
  * **Ahora (`openMAX / OpenWrt 24.10.4`):** **`10.37 ms – 16.64 ms` (`p50`)** -> **12x a 18x menos lag (-91% a -94% al subir)**
* **Capacidad útil en `20 MHz` (TCP real):**
  * Antes (`airOS 8.7.25`): `~35 – 45 Mbps` típicos
  * **Ahora (`openMAX / OpenWrt 24.10.4`):** **`69.80 Mbps` DL / `30.74 Mbps` UL** -> **1.5x a 1.8x más capacidad (+50% a +80% más megas útiles)**
* **Margen de CPU del CPE ruteando + NAT:**
  * Antes (`airOS 8.7.25`): Kernel `2.6.32` (NAT clásico)
  * **Ahora (`openMAX / OpenWrt 24.10.4`):** Kernel `6.6.110` (`flow_offloading=1`) -> **~2.5x más margen de CPU (+150% paquetes/s)**

> **En resumen:** Con exactamente los mismos equipos en el techo y el mismo canal de `20 MHz`, el enlace responde **~10 veces más rápido (`~2 ms` en vez de `~22 ms`)**, el lag cuando el cliente satura la línea baja entre un **80% y un 94%**, y al panel se le saca entre **+50% y +80% más capacidad útil**.

---

### 🔌 Próximo paso en marcha: Puente nativo a UISP en OpenWrt

Al pasar un equipo a OpenWrt puro, deja de correr el agente de Ubiquiti (`udapi-bridge`) y UISP lo deja de ver.
>!Ya desarmamos `/bin/udapi-bridge` de `WA.v8.7.25`: es un cliente WebSocket (`AES-256-GCM`) de espacio de usuario que lee `/etc/board.info`, `/tmp/system.cfg` (`unms.uri`), `/usr/www/status.cgi` y `/bin/wstalist`. Estamos armando el wrapper liviano para que los equipos con OpenWrt sigan reportando Online y en verde adentro de UISP con su mismo ID, señal, tráfico y clientes.!<

---

### 🧪 Últimos Wins del Banco Físico (`320+` Rondas Pareadas `A/B/A/B` en 12 Radios Reales)

* **`LAP-120 ↔ Loco 5AC` (`R165..R188` Ablación 1-a-1 y Barrido `1 km..14 km` en `AC_BE` puro):** Demostramos que `aql_txq_limit=900/1500 us` es la llave maestra obligatoria (tocar `fq_quantum`, `codel`, `airtime_flags`, `amsdu` o `tcp_tsq` sin bajar `AQL` da `0%` de cambio). Bajar solo `aql_txq_limit` sube el goodput un **`+3,14%` a `+15,79%` (`77,57 vs 66,99 Mbps` en `20 MHz`)** y recorta **`-33,1%` a `-40,7%` el `p95` RTT**, y sumarle `fq_quantum=1514 + codel=10/50ms` lleva la equidad Jain de `0.8734` a **`0.9520`**.
* **`LAP-120 ↔ Loco 5AC` (`R189..R194` Uplink Hammering 8 Flujos `1 km..14 km`):** Bajo tormenta pesada de subida (`8 flujos TCP` en `dscp=0`), el stack sube **`+0,53%` a `+5,52%` el goodput UL** y baja **`-12,1%` a `-35,7%` la latencia `p95`** (`-53,2%` en `p99` a `3 km`).
* **`PowerBeam M5 300` Enlace OTA (`PBM5-R27..R36`, Rondas 101–110 Multi-Radio):** Descubrimos con `/proc/net/ubnt_poll/query_mac_info` que un desbalance de cadenas de `8 dB` (`-87` vs `-79 dBm`) causaba `32%–42%` de PER en `MCS 11..15`. Separar las cadenas fijando TX en la cadena limpia y RX 2x2 MRC (`txchainmask=2, rxchainmask=3`) subió **`+5 dB` la señal recibida (`-81 -> -76 dBm`)**, levantó el CCQ de **`58%` a `95,5%`** y bajó **`-68,0%` el `p95` RTT**; además, activar `ubnt_ewma_delegate_on=1` (apagado de fábrica en airOS) recortó otro **`-18,5%` el `p95` RTT**.
* **Sector `LTU` de 3 Unidades (`LTU-Rocket` AP + `2x LTU-Lite` CPEs, `Stage 15` `LTU-S15-R1..R8`, `Stage 17A/17B` y `Stage 24F`):** Diagnosticamos la frontera TDD entre `aflturocket.v2.1.0` (`cz_len=3`, `SYM#7`) y `afltu.v2.4.0` (`cz_len=6`, `SYM#4`), mantuvimos frío el `LTU-Rocket` (`79–80 °C` a `powerout=0` / `-26 dBm`), logramos **`+9,86%` más goodput y `-47,02%` menos `p95`** con `multi_ack_enable=1 + send_ctrl_in_data=1 + send_map_enable=1` (`LTU-S15-R6`), **`-39,56%` menos `p95`** con `sched_max_agg_cnt=8` (`LTU-S15-R2`), **`-25,40%` menos `p95`** con `sched_mcs_limit_symbol_begin=14` (`LTU-S15-R8`), **`-17,21%` menos `p95`** pausando el barrido SSD (`LTU-S15-R1`), en **`Stage 17B` destrabamos el modo AP-PtMP (`SQ` Short-Queue `ptmp_max_cpe = 4`) y AP-PtP en `LTU-Lite` con firmware `v2.4.0` / `v2.4.2`** (`board_ssid = 0xae05` en `/tmp/ame.cfg` sin tocar Flash), y en **`Stage 24F` (`S24F-R1`)** demostramos que aislar la ventana de símbolos pura (`sched_mcs_limit_symbol_begin=12`, `sched_ap_mcs_limit_symbol_end=62`, `sched_mcs_limit_symbol_end=72` con `DGAIN_DL_ENABLE=0` y `pb_boost=2`) sube **`+1,36%` el goodput** y recorta **`-38,76%` el `p95` RTT (`2,76 -> 1,69 ms`) y `-45,93%` el `p99` RTT (`4,29 -> 2,32 ms`)**.
* **Sector Heterogéneo de 3 CPEs y Near-Far de 5 Estaciones (`Stage 13A/13B/14`, `M1-R1..R6`, `M2-R7..R12`, `S14-R1..R6`):** Conectamos en simultáneo `NanoStation 5AC Loco` (`2x2 AC`), `Rocket Prism 5AC Gen2` (`2x2 AC`) y `LiteBeam M5` (`1x1 N`) en `5180 MHz` (`0,0%` pérdida con aislamiento L2 de 3 cadenas `nft`), subiendo el goodput del sector un **`+7,31%` (`M1-R1`)**, **`+8,65%` (`M1-R4` `airtime_weight=512:512:128`)** y **`+10,58%` a `6000m` (`M1-R6`: `56,43 -> 62,40 Mbps`)**; en el sector Near-Far de 5 estaciones (`+2x PowerBeam M5 300` a `-81 dBm`), el stack co-diseñado AP+CPE logró **`+21,63%` más goodput (`55,66 -> 67,69 Mbps`) y `-11,85%` menos `p95` RTT (`M2-R11`)** (`+15,46%` en `M2-R12`), y nuestro `LAP-120` OpenWrt le ganó `6/6` rondas mano a mano al `Rocket Prism 5AC Gen2` como AP (`Stage 14`).
* **Ingeniería Inversa Xtensa `QCA988x` y Parcheo Quirúrgico en RAM (`Stage 17/18B/20/23` `PB-010..060`):** Decodificamos las 3 imágenes Xtensa `AR9888v2` (`ptmp_ap` `309,4 KB`, `ptmp_sta` `289,7 KB`, `ptp` `266,0 KB`), demostramos **`0` bytes de firma criptográfica** en los contenedores `SGMT` `BMI_LZ`, verificamos re-empaquetado `BMI_LZ` `100%` idéntico byte a byte en los `12` segmentos (`firmware/xtensa_sgmt_surgical_patcher.py`), mapeamos la tabla Xtensa de 51 entradas de `WMI 0x9064`/`0x9070` (`0x009b2037`), construimos el controlador de horarios por paquete `WMI_PDEV_RATE_SCHEDULE_CMDID = 0x9044` + planificación Sub-20 MHz (`5/8/10/15 MHz`), el telemetro ToA de `12,5 ns` (`3,75 m`) + EVM de 16 pilotos (`rx_ppdu_end_qca988x`, `Stage 20`), el preparador `PB-040` de inyección RAM `tmpfs` bind-mount con `0` escrituras Flash (`Stage 23`), y entrenamos un optimizador Bayesiano GP condicional + EHVI sobre `398` contrastes (`pb060_epistasis_surrogate_optimizer.py`).
* **Escalera Incremental del Perfil Campeón (`Stage 19/21/24C/24E/25`, arrancando de `A = Champion` v1 $\rightarrow$ v2 $\rightarrow$ v3 $\rightarrow$ v4 $\rightarrow$ v5 $\rightarrow$ v6):** Partiendo del perfil Campeón (`900/1500 us`, `thresh=4000`, `fq_codel 1514/10ms/50ms`), apilamos 5 saltos consecutivos verificados en hardware real:
  1. **`Champion v2` (`S19-R2`/`S19-R3`):** `retry short 5 long 4 + nf_cal_period=30 + txqueuelen=256` (**`+4,23%` goodput (`71,05 -> 74,05 Mbps`), `-19,77%` `p95` RTT (`23,96 -> 19,22 ms`)** en 1-CPE; y **`+38,55%` goodput (`51,02 -> 70,68 Mbps`)** en 2-CPE AP+Rocket STA Co-Design).
  2. **`Champion v3` (`S21-R2`/`S21-R3`):** `tcp_notsent_lowat=16384 + netdev_budget=600` (**`-12,35%` `p95` RTT (`19,92 -> 17,46 ms`)** en 1-CPE; **`-9,89%` `p95` RTT (`63,36 -> 57,09 ms`)** en el sector de 3 CPEs).
  3. **`Champion v4` (`S24C-R1`/`S24C-R2`):** `AirBBR` (`tcp_pacing_ca_ratio=110/ss_ratio=150`) + `Responsible Airtime` (`640:512:96` corregido por overhead MAC/ACK + `per-AC AQL 750..1500/1500..3000`) (**`+11,19%` más de goodput en 3 CPEs (`45,73 -> 50,84 Mbps`) y `-22,70%` menos `p95` RTT (`95,09 -> 73,50 ms`)**).
  4. **`Champion v5` (`S24E-R1`/`S24E-R2`):** `M2` RTS/CTS Adaptativo por EVM/Reintentos (`rts off` en 1-CPE SNR limpio: **`+21,87%` más goodput (`60,43 -> 73,64 Mbps`)**; `rts 512` + pesos dinámicos en 3 CPEs contendiendo: **`+5,24%` más goodput (`56,79 -> 59,76 Mbps`, pico `60,56 Mbps` / `3,03 Mbps/MHz`) y `-41,98%` menos `p95` RTT (`110,40 -> 64,06 ms`, `>3,8x` menos `p99` RTT)**).
  5. **`Champion v6` (`Stage 25` `S25-R2`):** `M5` Asymmetric UL/DL TCP ACK Pacing (`tcp_thin_linear_timeouts=1, tcp_early_retrans=3, tcp_autocorking=0, AC_VO AQL 600/1200`), descubierto fusionando **`scholar` MCP (`jev-1.14.0`, `prob=0.97`) + `hyperresearch` (`v0.12.0`)**, que encima del `Champion v5` sumó otro **`+3,66%` más de goodput al sector de 3 CPEs (`61,07 -> 63,30 Mbps` promedio, `64,56 Mbps` / `3,23 Mbps/MHz` en `B2`) y recortó otro `-10,33%` adicional el `p95` RTT (`74,73 -> 67,02 ms`, `0,0%` pérdida)**.
  6. **`PtMP Champion v22` y `PtP Champion v9` (`Stages 79..95C` — Disección de Módulos `.ko` en Kernel):** Desensamblando `umac.ko`, `ath_dev.ko`, `ath_pktlog.ko` y `ubnt_poll_host.ko` en `WA`, `XC` y `XW`, eliminamos el overhead por paquete de `ath_pktlog` en `XC` (**`+23,35%` más de goodput en el sector de 3 CPEs: `46,53 -> 57,39 Mbps`, `-20,81%` `p99` RTT, `-22,58%` jitter IPTV y `0,00%` pérdida VoIP**), apagamos la telemetría pesada `vow_extstats 0`, activamos despacho multi-cola WMM en hardware (`set_multiq=3` + reservas `Minfree 0/4/8/16`) y protección de voz/video en `M5 XW` (`rcRateFind_11nViVo`). En el enlace dedicado `PowerBeam 5AC Gen2` PtP (`Stage 94A/95B`), `PtP Champion v9` logró **`+41,01%` más de capacidad total (`+70,60%` en Bulk TCP), `-64,80%` menos `p95` RTT, `0,000%` pérdida VoIP** y **salto de frecuencia `802.11h CSA` en vivo con `0,000 s` de corte (`0/80` probes perdidos)**.
  7. **Cambio Dinámico `20 MHz <-> 40 MHz` Zero-Touch (`Stage 95C`) y Co-Diseño con `MikroTik` (`Stage 97A`):** Comprobamos en el banco real que aunque un CPE `airOS 8` tenga `cwmenable=0` en su configuración, su driver `umac.ko` en `mode=auto` sigue automáticamente el `VHT Operation IE` del AP OpenWrt entre `20 MHz` y `40 MHz` y reconecta solo en **`8,78 s a 12,10 s` (`< 15 s`)** (**`-31,28%` de jitter IPTV en `40 MHz`**). Y conectando un `MikroTik RB951G-2HnD` (`RouterOS 6.47`) por un trunk `802.1Q VLAN` (`PCP 0..7` + `DSCP EF/CS4`) contra el AP OpenWrt, bajamos la latencia extremo a extremo `CPE -> Aire -> Switch -> MikroTik` un **`-54,84%` en `p50` (`4,39 -> 1,98 ms`)** y **`-46,18%` en `p95`**.
  8. **`AF-LTU` Aislamiento Dual-Core ARM SMP y Superframe de `80` Símbolos (`Stages 80A, 96A, 97C, 99B`):** En el `LTU-Lite` (destrabado en RAM como `AP-PTMP(Run)` a `4096-QAM 12X`), aislando las interrupciones TDMA de `500 Hz` (`IRQ 52/53`) en `CPU0` y descargando el `100%` de Ethernet `GMAC0` (`IRQ 63`) + `AME.l2p` (`IRQ 92`) en `CPU1` junto al fast-path de `ame_dev.ko`, subimos el throughput TCP del SoC un **`+8,5%` a `+9,9%` (`189,81 Mbps`, pico `210,28 Mbps`)** y bajamos **`-12,5%` la latencia `p50` bajo carga** con **`0` pérdidas de superframe**.
* **Mejoras Multi-Plataforma (`Rocket Prism 5AC Gen2`, `Rocket 2AC Prism`, `airFiber 4X`):** En `Rocket Prism 5AC Gen2`, `airview1 down` + `ani_enable=0` + `swretry=4/6` bajó **`-67,9%` el `p50` RTT (`1,81 ms`)**; en `Rocket 2AC Prism` (`2.4 GHz`, `Stage 98D`), `ani_enable=1` + `shpreamble=1` + `vow_extstats 0` + control de `IRQ 2` eliminó el `100%` de las `15.480` interrupciones parásitas de `AirView` (**`+13,0%` pico TCP, `-54,3%` `p50` RTT**); en `airFiber 4X` (`Invictus v2`), `framelength=2.5ms` + `flowcntl=on` + `cp=8` redujo las interrupciones TDD de `500` a `400 Hz` (**`+15,3%` stream, `-22,8%` `p95` RTT**).

Todo el código, las pruebas y la documentación están abiertos acá:
👉 https://github.com/wolverin0/openmax
```
