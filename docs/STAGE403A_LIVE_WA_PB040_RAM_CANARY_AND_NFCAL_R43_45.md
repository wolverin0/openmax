<!-- doc-head: STAGE403A_LIVE_WA_PB040_RAM_CANARY_AND_NFCAL_R43_45.md preserved document content -->
<!-- /doc-head -->


# Stage 403A — Live `WA` RAM-Only Xtensa `SGMT` Firmware Canary (`PB-040`), `nf_cal_period` & `pktlog_filter=0` (`R43..R45`)

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `Stage 403A` (`S403A-R43..R45`, reaching **`184` cumulative live windows** across `45` counterbalanced rounds).
- **Historic First (`PB-040` Live Hardware Proof)**: Executed the first live RAM-only surgical `SGMT` (`BMI_LZ`) firmware override on both `AP .20` and `CPE .250` (`/tmp/firmware-2-pb040.bin` bind-mounted over `/lib/firmware/ath10k/QCA988X/hw2.0/firmware-2.bin` with `0` Flash writes and a `45s` rollback watchdog).
- **Cryptographic & Target SRAM Verification**:
  - Stock `firmware-2.bin` (`204,796 B`): `SHA-256 = 398e4380e7e55105f3da0f78af29d1e437404ed3a82597aa4b6daaa7dce1a38e` (`fw_checksums`: `firmware-N.bin = 3e4cf97f`, `athwlan = 477a6960`, `otp = 4c4fd0bc`).
  - Patched `/tmp/firmware-2-pb040.bin` (`204,796 B`): `SHA-256 = 8d50c1ce5d9e3a97458fc44b19f3b31510ad2af4fcf3746e3252722dfa9b3d9c` (`fw_checksums`: **`firmware-N.bin = 912bcb63`**, **`athwlan = 278d2d76`**, `otp = 4c4fd0bc`).
  - Confirmed `BMIFastDownload` of all 4 `SGMT` segments (`0x00980000`, `0x0040b000` `.rodata` canary `@ 0x0040bc30`, `0x0040bd10`, `0x00983c00` `.text`/INI `@ 0x009b7584`), clean `WMI_READY` (`vdevs: 16, peers: 127, tid: 256, msdu-desc: 1424`), and live hardware register readout `0x00029e00 = 0x13761320`.
- **Primary Artifact**: [`artifacts/autoresearch/stage403a_live_wa_pb040_ram_canary_and_nfcal_r43_45.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage403a_live_wa_pb040_ram_canary_and_nfcal_r43_45.json)

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`R43..R45`)

| Round | Knob Under Test (`Arm A` vs `Arm B`) | Arm A Goodput (`Mbps`) | Arm B Goodput (`Mbps`) | Arm A `p50` / `p95` (`ms`) | Arm B `p50` / `p95` (`ms`) | Arm A / B Jitter (`ms`) | Decision & Attribution |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`S403A-R43`** | `PB040-CANARY-RODATA` + `0x00029e00` (`0x13721320` vs `0x13761320`) | **`58.630`** (`59.557` in `A1`) | `56.757` (`58.325` in `B1`) | **`21.203`** / **`71.400`** | `30.282` / `74.927` | **`1.864`** / `2.183` | `RETAIN_ARM_A` (`QCA firmware`: proves `PB-040` RAM loader works; `0x13721320` optimal on clean LOS) |
| **`S403A-R44`** | `ath10k` `nf_cal_period`: `30s` vs `120s` | `56.882` | **`58.465`** (`+2.78%`, **`61.740`** in `B2`) | `22.402` / `68.425` | `32.035` / **`65.303`** (`-4.56%`) | `1.796` / `2.707` | **`PROMOTE_ARM_B`** (`Pareto +0.24%`; `QCA firmware` / `ath10k` reduced NF cal off-air stalls) |
| **`S403A-R45`** | `ath10k` `pktlog_filter`: `0x40` vs `0x0` (16-Stream Burst) | `55.816` | **`71.252`** (**`+27.66%`**, `72.834` in `B2`) | `17.633` / `61.422` | `19.052` / **`59.635`** (`-2.91%`) | `5.104` / **`2.468`** (**`-51.65%`**, `1.666` in `B2`) | **`PROMOTE_ARM_B`** (**`Pareto +81.14%`**; `ath10k` / `hardware` PCIe Copy Engine DMA relief) |

## 3. Mechanistic Attribution (`CONFIRMED`)
1. **`PB040-CANARY-RODATA` & `PB040-CCA-AGC-OVERRIDE` (`S403A-R43`, `QCA firmware` + `ath10k`)**:
   - Confirmed that `QCA9882` (`Peregrine v2`) ROM/BMI accepts a surgically patched `SGMT` (`BMI_LZ`) stream bind-mounted in volatile `/tmp` RAM (`fw_checksums = 912bcb63 / 278d2d76`), executing `ar9888_reset` to program `0x00029e00` (`BB_timing_controls_1`). On the clean LOS bench link, default `0x13721320` (`cca_thresh62 = 0x1c`) preserves lower `p50` RTT (`21.203 ms`).
2. **`pktlog_filter=0x0` (`S403A-R45`, `ath10k` + `QCA firmware` PCIe CE DMA)**:
   - By default `ath10k-ct` sets `pktlog_filter = 0x00000040`, copying per-PPDU packet log events across the PCIe Copy Engine ring into host skbs on the `600 MHz` `AR9342` CPU. Setting `pktlog_filter = 0x0` boosted 16-stream burst goodput by **`+27.66%` (`55.816 -> 71.252 Mbps`)** and cut VoIP jitter by **`-51.65%` (`5.104 -> 2.468 ms`)**.
