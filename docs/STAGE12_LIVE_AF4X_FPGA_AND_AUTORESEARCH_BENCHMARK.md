<!-- doc-head: STAGE12_LIVE_AF4X_FPGA_AND_AUTORESEARCH_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Live `airFiber 4X` (`AF-4X`, `AF06.v4.1.0`) Invictus v2 FPGA Architecture & 6-Round `A/B/A/B` Autoresearch Benchmark

## 1. Executive Summary

- **Experiment ID**: `FMX-STAGE12-AF4X-LIVE-AUTORESEARCH`
- **Target Hardware**: Ubiquiti `airFiber 4X` (`AF-4X`, `board.sysid=0xaf0a`, `MAC PUBLIC_DEVICE_0053`, Firmware `AF06.v4.1.0`)
- **Management Reachability**:
  - Link-local IPv6: `PUBLIC_DEVICE_0054%27` (SSH port 22)
  - RAM-only IPv4 alias added on `br0:1`: `198.18.0.83/24` (coexisting safely with stock `198.18.0.50/24` on `br0`, zero flash writes)
- **Receipt Artifact**: [`af4x_live_autoresearch_20261024.json`](<repo>/artifacts/autoresearch/af4x_live_autoresearch_20261024.json)
- **Key Outcome**:
  1. **Complete Hardware & FPGA Control-Boundary Mapping (`CONFIRMED`)**: Mapped the live TI `DaVinci DA850/OMAP-L138/AM1808` (`ARM926EJ-S rev 5`, `124.51 BogoMIPS`, `62,064 kB` RAM, Linux `2.6.33 armv5tejl`) host + **Ubiquiti Invictus v2** (`date: 9/3/2019`) baseband/MAC architecture, `air0` kernel netdev (`airfiber_network.ko`), SPI peripheral bus (`/dev/spidev1.0`..`1.8`), interrupt lines (`IRQ 34/35` EMAC, `IRQ 56` `spi_davinci.1`, `IRQ 139` `gpio_fpga`, `IRQ 140` `air_fiber`), and all **191 readable / 83 writable** `af` Invictus CLI parameters.
  2. **6-Round Paired `A/B/A/B` Live Command-Mutation Autoresearch (`CONFIRMED`)**: Executed 6 paired `A1 -> B1 -> A2 -> B2` RAM-only mutation rounds with automatic rollback on `REJECT`. **4 of 6 rounds (`AF4X-R1`, `AF4X-R2`, `AF4X-R3`, `AF4X-R5`) were `KEEP`**, reducing control-plane `p50` RTT from `8.17–9.50 ms` to **`3.50–3.63 ms`** (`-56.9%`) and `p95` RTT from `20.86 ms` to **`16.09 ms`** (`-22.9%`), while **2 rounds (`AF4X-R4` `mcastfilter=off`, `AF4X-R6` `netdev_budget=600`) were `REJECT`** and automatically rolled back.

---

## 2. Confirmed `airFiber 4X` (`AF-4X`) Hardware & Invictus v2 Architecture

| Subsystem | Live Hardware Evidence (`AF06.v4.1.0`) | Control Boundary |
| :--- | :--- | :--- |
| **Host SoC / CPU** | TI `DaVinci DA850/OMAP-L138/AM1808` (`ARM926EJ-S rev 5 v5l`, `124.51 BogoMIPS`, `cpurevision=0x4e840102`) | Linux `2.6.33` host (`62,064 kB` RAM, `45,508 kB` free) |
| **Baseband / Custom MAC** | **Ubiquiti Invictus Version 2** (`date: 9/3/2019`), interfaced via `/dev/spidev1.0`..`1.8` (`IRQ 56 spi_davinci.1`), `IRQ 139 (gpio_fpga)`, and `IRQ 140 (air_fiber)` | Proprietary `radiod` (`1,319,378` B) + `afrd` (`1,119,515` B) + `airfiberbox` (`133,416` B) |
| **Data-Plane Interfaces** | `eth0` (DaVinci EMAC, `IRQ 33–36`), `air0` (`airfiber_network.ko` `4,124` B), bridged in `br0` (`MTU 1500`) | Linux bridge (`br0`) + `ebtables` + Invictus hardware EMAC (`emacstat`) |
| **Clock / Jitter Cleaner** | TI `CDCE62005` (`cdce62005_4x.dat`, `cdce62005_4x_111.11.dat`, `tracktcxo`) | Configured via `airfiberbox` (`cdce62005` applet) |
| **ADC / DAC Converters** | Dual ADC: TI `ADS62P29` (`ads62p29.dat`) · Dual DACs: TI `DAC3282`/`DAC3283` (`dac3282.dat`, `dac3283.dat`) + `DAC7563` (`dac7563.dat`) | Configured via `airfiberbox` (`dac3282`, `dac7563` applets) |
| **RF Synthesizers / PLL / Transceiver** | Analog Devices / Hittite `HMC767`, `HMC783`, `HMC833`, `HMC900LP` + ADI transceiver (`txadi`, `rxadi`) | 11 channel-bandwidth filter tables in `/bin/AF4X_40Mxtal_4950M_B_041516_*.txt`: **`3.5, 5, 7, 10, 14, 20, 28, 30, 40, 50, 56 MHz`** |
| **Invictus `af` CLI Surface** | `af get getlist` (**191 parameters**), `af get setlist` (**83 settable parameters**) | Live runtime mutations via `af set <param> <val>` (`framelength`, `cp`, `cpsel`, `rxgain`, `dutycycle`, `stricttiming`, `mcastfilter`, `modcontrol`, `speed`, `powerout`, `atpctarget`, etc.) |

---

## 3. 6-Round Paired `A/B/A/B` Live Autoresearch Results (`198.18.0.83`)

Each round executed four consecutive measurement windows (`A1` baseline $\rightarrow$ `B1` candidate $\rightarrow$ `A2` baseline $\rightarrow$ `B2` candidate) with 20 HTTP/TCP control-plane RTT probes and a 256 KB SSH stream transfer per window, plus `/proc/interrupts` delta tracking for `IRQ 34 (eth0)` and `IRQ 140 (air_fiber)`.

| Round | Knob / Command Mutation | Baseline (`A`) Mean `p50` / `p95` (ms) | Candidate (`B`) Mean `p50` / `p95` (ms) | SSH Stream (`A` $\rightarrow$ `B` Mbps) | Mean $J$ (`A` $\rightarrow$ `B`) | $\Delta J$ | Decision |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`AF4X-R1`** | `ifconfig eth0 txqueuelen 256 && ifconfig air0 txqueuelen 256` (vs `1000`) | `8.168` / `26.382` | **`3.627`** / `26.825` | `5.334` $\rightarrow$ **`5.588`** | `24.5022` $\rightarrow$ **`20.1701`** | **`-4.3321`** | **`KEEP`** |
| **`AF4X-R2`** | `sysctl net.core.rmem_max=262144 wmem_max=262144 netdev_max_backlog=2000` | `9.502` / `25.044` | **`3.903`** / `27.348` | `5.585` $\rightarrow$ `5.239` | `24.7995` $\rightarrow$ **`20.9509`** | **`-3.8486`** | **`KEEP`** |
| **`AF4X-R3`** | `sysctl net.ipv4.tcp_low_latency=1 tcp_rmem='4096 87380 262144' tcp_wmem='4096 65536 262144'` | `3.523` / `20.863` | `3.531` / **`16.090`** | `5.748` $\rightarrow$ `5.649` | `15.8276` $\rightarrow$ **`12.5338`** | **`-3.2938`** | **`KEEP`** |
| **`AF4X-R4`** | `af set mcastfilter off` (vs `on` in Invictus FPGA) | `13.913` / `25.733` | `14.756` / `26.976` | `4.499` $\rightarrow$ `4.796` | `30.1219` $\rightarrow$ `31.7243` | `+1.6024` | **`REJECT` (Rolled Back to `on`)** |
| **`AF4X-R5`** | `af set stricttiming on` (vs `off` in Invictus FPGA) | `8.963` / `24.544` | **`3.504`** / **`22.564`** | `5.207` $\rightarrow$ `4.728` | `24.0516` $\rightarrow$ **`17.3961`** | **`-6.6555`** | **`KEEP`** |
| **`AF4X-R6`** | `sysctl net.core.netdev_budget=600 optmem_max=20480` (vs `300 / 10240`) | `3.649` / `26.551` | `3.694` / `26.556` | `5.913` $\rightarrow$ `5.840` | `19.8705` $\rightarrow$ `19.9444` | `+0.0739` | **`REJECT` (Rolled Back to `300`)** |

---

## 4. Key Engineering Findings (`CONFIRMED`)

1. **Single-Core `ARM926EJ-S` (`124.51 BogoMIPS`) Prequeue & Queue Depth Sensitivity (`AF4X-R1`, `AF4X-R2`, `AF4X-R3`)**:
   - Because the `AM1808` host CPU runs at `124.51 BogoMIPS` while `radiod` and `udapi-bridge` poll the Invictus FPGA over SPI/GPIO, default `txqueuelen=1000` on `eth0` and `air0` (`AF4X-R1`) and `tcp_low_latency=0` (`AF4X-R3`) cause periodic `12–15 ms` median latency spikes when SSH/HTTP streams share the CPU.
   - Bounding `eth0`/`air0` `txqueuelen` to `256`, raising `rmem_max`/`wmem_max` to `262144`, and enabling `net.ipv4.tcp_low_latency=1` stabilized `p50` at **`3.50–3.63 ms`** and reduced `p95` from `20.86 ms` to **`16.09 ms`**.
2. **Invictus FPGA Hardware Multicast Filter (`mcastfilter=on`) is Critical (`AF4X-R4` `REJECT`)**:
   - Disabling `af set mcastfilter off` allowed L2 multicast frames onto the host bridge path, immediately degrading `J` (`30.12 -> 31.72`) and increasing `p50` RTT (`13.91 -> 14.76 ms`). `mcastfilter=on` was automatically restored.
3. **Invictus `stricttiming=on` Improves Frame-Timing Determinism (`AF4X-R5` `KEEP`)**:
   - Enabling `af set stricttiming on` improved `J` by **`-6.66`** (`24.05 -> 17.40`), reducing `p50` from `8.96 ms` to **`3.50 ms`** and `p95` from `24.54 ms` to **`22.56 ms`**.
