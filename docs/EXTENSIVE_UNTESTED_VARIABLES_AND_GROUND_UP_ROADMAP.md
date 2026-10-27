<!-- doc-head: EXTENSIVE_UNTESTED_VARIABLES_AND_GROUND_UP_ROADMAP.md preserved document content -->
<!-- /doc-head -->

# Extensive Roadmap of Untested Variables, Device/Mode Improvement Matrix & Ground-Up Discoveries

- **Updated**: `2026-10-25`
- **Catalog Scope**: `571` total hardware/driver/firmware descriptors (`302` actuation controls, `142` telemetry/observability sensors, `127` safety-excluded)
- **Empirical Corpus**: `326` physical rounds (`1,232+` sub-phases) across `12` physical radios (`Stage 1` through `Stage 17`)
- **Champion State Ledger**: [`artifacts/autoresearch/champion_state_ledger.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/champion_state_ledger.json)

---

## 1. What We Discovered That Humans / Prior Community Work Had Missed or Left Unused

| # | Undocumented / Unexplored Discovery | Where It Lives in Hardware / Firmware | Why Humans Missed It & What It Unlocks |
| :---: | :--- | :--- | :--- |
| **1** | **`QCA988x` (`AR9888v2`) `SGMT` Target Firmware Has `0` Cryptographic Signature Bytes** (`PB-011` / `PB-040`) | `umac.ko` embedded `athwlan_AR9888v2_{ptmp_ap,ptmp_sta,ptp}_bin` (`magic=0x544d4753` `"SGMT"`, `BMI_LZ_DATA=14`) | Community assumed QCA988x target firmware was cryptographically locked. We proved `consumed_bytes == container_size` (`0` RSA/ECDSA bytes) and built [`firmware/xtensa_sgmt_surgical_patcher.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/xtensa_sgmt_surgical_patcher.py) (`12/12` segments `100%` byte-identical round-trip) to surgically patch the Xtensa target CPU in RAM (`/tmp/firmware-5.bin` bind-mount, zero Flash risk). |
| **2** | **Ubiquiti's Hidden WMI Tunnel (`0x9064` vs `0x9070`) & 51-Entry Xtensa Jump Table at `0x009b2037`** (`PB-010`) | DRAM `.data` `0x0040fb54` (`0x00009064` on 5 GHz `10.1` vs `0x00009070` on 2.4 GHz `10.2`) $\rightarrow$ IRAM `.text` `0x009b2037` | Explains the exact binary boundary of `ubnt_poll` inside the radio CPU: 51 proprietary sub-commands (including `0x17` `set_txq_param` $\rightarrow$ `0x009b5c02` and `0x1e` `set_rate_override`) that bypass standard Linux `mac80211`. |
| **3** | **Per-Packet `12.5 ns` Hardware Locationing Clock & 16-Word Pilot EVM Discarded by `ath10k` `skb_pull`** (`PB-010` / `PB-021`) | `rx_ppdu_end_qca988x` dword `18 [7:0]` (`locationing_timestamp`, `80 MHz` fractional clock = `12.5 ns`) & dwords `0..15` (`evm_p0..evm_p15`) | Linux `ath10k_htt_rx_amsdu_pop` strips `htt_rx_desc` via `skb_pull` before `mac80211` sees the frame. Exporting those 84 bytes before `skb_pull` gives **per-packet sub-stream EVM (SNR per spatial stream)** and **1.8-meter physical ranging resolution** without GPS or extra air overhead. |
| **4** | **Strict Epistatic Gatekeeping of `aql_txq_limit` Over All Host Queue Knobs** (`R165..R182` & `PB-060`) | `/sys/kernel/debug/ieee80211/phy0/aql_txq_limit` (`900/1500 us` PtP, `1850/3700 us` Multi-CPE PtMP) | Community guides tune `fq_quantum`, `codel_target`, or `tcp_limit_output_bytes` with stock AQL (`5000/12000 us`), which yields **`0.0%` effect** because the QCA988x target queue absorbs the backlog. Only after lowering `aql_txq_limit` do `fq_quantum=1514` and `codel=10/50ms` unlock `0.9520` Jain fairness and `+15.79%` goodput. |
| **5** | **`LTU-Lite` Native Kernel Short-Queue (`SQ`) Micro-AP Mode (`0 < ptmp_max_cpe <= 16`)** (`Stage 17A`) | `/bin/ame_drv.sh` line `266` $\rightarrow$ `/tmp/ame.cfg` $\rightarrow$ `/sys/class/ame/ame_ctrl_dev/ini` (`ptmp_max_cpe`) | Known Web-Inspector tricks only flipped `role=ap` in the UI, leaving `ptmp_max_cpe=0` (full 64+ CPE ring allocation). Setting `ptmp_max_cpe = 4..8` activates a dedicated **Short-Queue (`SQ`) DMA scheduler** built by Ubiquiti engineers specifically for 3–8 client micro-sectors. |
| **6** | **Asymmetric SIMO-TX / 2x2-MRC-RX (`txchainmask=2, rxchainmask=3`) + `ubnt_ewma_delegate_on=1` on Tree-Obstructed Links** (`PBM5-R27..R36`) | `/proc/net/ubnt_poll/query_mac_info` + `ath_rate_atheros` `ubnt_ewma_delegate_on` | Standard `airOS` leaves both chains enabled on TX when one polarization is obstructed by foliage (`6–8 dB` imbalance), causing `32%–42%` PER on 2-stream `MCS 11..15`. Silencing TX on the degraded chain while keeping 2x2 MRC on RX boosts remote RSSI by **`+5 dB`**, raises CCQ from **`58%` to `95.5%`**, and cuts `p95` RTT by **`-68.0%`**. |

---

## 2. Matrix of Devices & Modes With Remaining Room for Improvement (`~225` Untested Physical Variables)

| Device / Radio Family | Mode (`AP` / `CPE` / `PtP` / `PtMP`) | What Is Already Solved (`Champion` State) | Remaining Room for Improvement (Untested Variables Ready for Autoresearch) |
| :--- | :---: | :--- | :--- |
| **`LiteAP 120` + `NanoStation 5AC Loco` (`OpenWrt 24.10.4` `QCA988x`)** | **PtP & Multi-CPE PtMP (`AP` + `CPE`)** | Host queue/airtime wall reached at `20 MHz` (`77.57 Mbps` PtP, `69.01 Mbps` 5-Sta Near-Far, `-40.7%` `p95` RTT, `Jain=0.9520`) | 1. **`PB-040` Live RAM Surgical Firmware Patch (`PB040-CANARY-RODATA` $\rightarrow$ `PB040-CCA-AGC-OVERRIDE`)**: Bind-mount `/tmp/firmware-5.bin` in RAM and verify live target boot + `cca_thresh62` desensitization.<br>2. **`PB-030` Sub-20 MHz (`5 MHz` Quarter-Rate / `10 MHz` Half-Rate)**: `+3 dB` / `+6 dB` SNR gain + `2x`/`4x` OFDM symbol length for severe foliage/NLOS links.<br>3. **Per-Peer 4-Series WMI Rate/Retry Table (`0x9044` + `series_bw` LDPC/STBC/SGI)**: Force hardware retry fallback from `2x2 VHT` $\rightarrow$ `1x2 STBC` on retry #2 without waiting for rate-control collapse.<br>4. **`PB-021` Live Per-PPDU `16-Pilot EVM` + `12.5 ns` Ranging Extractor**: Predictive MCS clamping before packet loss occurs. |
| **`LTU-Lite` (`v2.4.0`) & `LTU-Rocket` (`v2.1.0`) (`UBNT AME SoC` + `AD9361`)** | **Micro-AP PtMP (`SQ`), PtP & Macro-Sector PtMP** | `Stage 15` (`ame_core` runtime tuning: `+9.86%` goodput, `-47.02%` `p95` RTT) & `Stage 16A` (`NanoStation 5AC Loco` `eth0` L2 IPv6 bridge verified at `0.78 ms`) | 1. **`Stage 17B` Live OTA `LTU-Lite` as PtP AP & Micro-AP PtMP (`SQ` `ptmp_max_cpe=4`)**: Once the two `LTU-Lite` units (`Boca 5` & `Boca 2`, both `v2.4.0`) are separated by `1.5–2 m`, run live OTA `A/B/A/B` benchmarks comparing `ptmp_max_cpe=0` vs `ptmp_max_cpe=4` (`SQ` mode) + `LTU-Rocket`.<br>2. **Live `4096-QAM` (`12X`) & `OFDMA` Activation on Matched `v2.4.0` Pair**: Test `max_tx_rate=12` (`4096-QAM`) over the air between the two `v2.4.0` `LTU-Lite` units.<br>3. **Independent Split-Frequency (`TX != RX` LO on `AD9361` SDR)**: Test asymmetric TX/RX center frequencies to dodge asymmetric tower vs CPE interference. |
| **`Rocket Prism 5AC Gen2` (`XC.v8.7.25`) & `Rocket 2AC Prism` (`2XC.v8.7.11`)** | **High-Noise Tower `AP` (`PtMP` / `PtP`) with Active `AirPrism`** | `Stage 12` solved `STA` co-location (`-67.9%` `p50` RTT on 5AC) and `2.4 GHz AP` (`-54.3%` `p50` RTT on 2AC); `Stage 14` tested stock `Compat 802.11` AP | 1. **Active `AirPrism` Filter Register Tuning Under Co-Channel / Adjacent Interference**: Sweep AirPrism passband attenuation and `ani_ofdm_level` / `Transient_immunity` on `Rocket Prism 5AC Gen2` acting as AP.<br>2. **`Mode B` (`airOS` `ubnt_poll` TDMA AP Tuning)**: Apply `txop_params`, `no_ack_rate`, `no_auto_prio`, and `ubnt_ewma_delegate_on=1` on `Rocket Prism 5AC Gen2` in native `airMAX` PtMP AP mode. |
| **`PowerBeam M5 300` (`XW.v6.3.22`) & `LiteBeam M5` (`XW`)** | **Legacy `M5` `PtP` & Mixed `AC+M5` `PtMP`** | `PBM5-R1..R36` solved weak-link chain imbalance (`+5 dB` RSSI, `95.5%` CCQ, `-68%` `p95` RTT) and `Stage 13B` integrated into 5-Sta Near-Far (`+21.63%` sector goodput) | 1. **`AirSelect` Frequency-Hopping TDD Coordination**: Test rapid 2-channel coordinated hopping under pulsed interference.<br>2. **Dynamic Per-CPE `txchainmask` Auto-Daemon (`Stage 16B` port)**: Closed-loop daemon that monitors per-chain RSSI delta (`>= 5 dB`) and automatically switches between `txchainmask=3` (`2x2`) and `txchainmask=1/2` (`1x2 MRC`) when wind/rain moves tree foliage. |
| **`airFiber 4X` (`AF06.v4.1.0` `Invictus v2` FPGA)** | **Backhaul `PtP` (`Master` / `Slave`)** | `AF4X-R1..R20` (`framelength=2.5ms`, `flowcntl=on`, `cp=8`, `stricttiming=on`: `-22.8%` `p95` RTT, `+15.3%` stream) | 1. **Asymmetric TDD Duty-Cycle (`75/25`, `67/33`, `50/50`) vs Cyclic Prefix (`cp=4/8/16`)**: Joint optimization of TDD split and cyclic prefix under multipath backhaul conditions. |

---

## 3. Prioritized Next Execution Queue (`Stage 17B` -> `Stage 20`)

1. **`Stage 17B` (`T-S17B-LTU-LITE-OTA-SQ-AND-12X`) — Live OTA `LTU-Lite #1` AP $\leftrightarrow$ `LTU-Lite #2` CPE + `LTU-Rocket`**:
   - **Pre-condition**: Separate `LTU-Lite #1` (`Boca 5`) and `LTU-Lite #2` (`Boca 2`) by `1.5–2 m`.
   - **Experiments**:
     - `S17B-R1`: `LTU-Lite` PtP AP (`wireless_mode=ptp, role=ap`) vs `LTU-Lite` PtMP AP (`wireless_mode=ptmp, role=ap, ptmp_max_cpe=0`).
     - `S17B-R2`: `LTU-Lite` Micro-AP Short-Queue (`ptmp_max_cpe=4` `SQ` mode) vs full queue (`ptmp_max_cpe=0`).
     - `S17B-R3`: Split-Frequency (`TX freq != RX freq` on `AD9361` SDR) under co-channel interference from `5180 MHz` AC sector.
     - `S17B-R4`: High-order modulation (`10X` `1024-QAM` vs `12X` `4096-QAM`) on matched `v2.4.0` pair.
2. **`Stage 18` (`T-S18-PB040-LIVE-RAM-XTENSA-CANARY`) — First Live RAM-Only Xtensa Target Patch on `Loco 5AC` / `LAP-120`**:
   - Bind-mount `/tmp/pb040/firmware-5.bin` (`PB040-CANARY-RODATA`, zero Flash writes) and prove clean `BMI_LZ_DATA` target boot + `WMI_READY` handshake on live hardware, then test `PB040-CCA-AGC-OVERRIDE` (`PB-031`) and `PB040-SUB20MHZ-PLL-DIV` (`PB-030`).
3. **`Stage 19` (`T-S19-ROCKET-PRISM-AIRPRISM-AND-MODE-B-AP`) — `Rocket Prism 5AC Gen2` Active `AirPrism` + `ubnt_poll` AP Autoresearch**:
   - Test `AirPrism` interference rejection and `Mode B` (`ubnt_poll` TDMA) knobs on `Rocket Prism 5AC Gen2` acting as AP.
4. **`Stage 20` (`T-S20-CLOSED-LOOP-ADAPTIVE-PHY-DAEMON`) — Unified Closed-Loop Daemon Combining `PB-060` Surrogate + `Stage 16B` Guards**:
   - Real-time daemon on `LAP-120` that switches between the `1-CPE Champion` (`900/1500 us`), `Multi-CPE Champion` (`1850/3700 us`), and `Asymmetric Chain-Mask Rescue` automatically based on live station count and per-chain RSSI imbalance.
