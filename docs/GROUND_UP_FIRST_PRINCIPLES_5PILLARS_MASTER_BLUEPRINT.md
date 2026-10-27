<!-- doc-head: Canonical Master Blueprint for FuturaMAX's 5 Ground-Up First-Principles RF, Baseband, and Cooperative Intelligence Pillars -->
Unifies the 5 Clean-Sheet ("Ground-Up") hardware/firmware breakthroughs that go beyond host Linux sysctls into the QCA988x Xtensa target CPU, per-PPDU DMA descriptors, WMI 0x9064/0x9065 hooks, LTU AD9361 SDR/FPGA internals, and zero-false-positive cooperative CPE sensing.
<!-- /doc-head -->

# FuturaMAX — Ground-Up First-Principles Architecture (`5` Groundbreaking Pillars)

- **Status**: Active Engineering & Live Bench Verification Roadmap (`2026-10-26`)
- **Companion Documents**:
  - [`docs/EXTENSIVE_UNTESTED_VARIABLES_AND_GROUND_UP_ROADMAP.md`](EXTENSIVE_UNTESTED_VARIABLES_AND_GROUND_UP_ROADMAP.md)
  - [`docs/STAGE17_PB010_011_XTENSA_TARGET_AND_WMI_MAP.md`](STAGE17_PB010_011_XTENSA_TARGET_AND_WMI_MAP.md)
  - [`docs/STAGE17_PB021_031_GROUND_UP_PHY_AND_LTU_SQ_AP.md`](STAGE17_PB021_031_GROUND_UP_PHY_AND_LTU_SQ_AP.md)
  - [`docs/STAGE17_PB040_XTENSA_SURGICAL_RAM_PATCH_SPEC.md`](STAGE17_PB040_XTENSA_SURGICAL_RAM_PATCH_SPEC.md)
  - [`docs/COOPERATIVE_CPE_FEASIBILITY.md`](COOPERATIVE_CPE_FEASIBILITY.md)
  - [`docs/ZEROCLAW_EDGE_COMPATIBILITY.md`](ZEROCLAW_EDGE_COMPATIBILITY.md)

---

## Executive Summary: Why These 5 Pillars Are Groundbreaking

Conventional WISP and OpenWrt tuning stops at the **Linux host boundary** (`sysctl`, `fq_codel`, `AQL`, `BQL`, `IRQ` affinity). While our host-level Autoresearch already delivered **`+25.9%` to `+47.6%` goodput** and **`-38%` to `-68%` `p95` RTT**, the biggest unsolved walls in outdoor wireless live **inside the radio silicon and baseband descriptors** where standard Linux drivers have no visibility or control.

By reverse-engineering the target binaries (`QCA988x` Xtensa `SGMT` firmware, `ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko`, `ame_core.ko`, `cds_mac_mod.ko`), we uncovered **five clean-sheet capabilities** that neither the OpenWrt community nor commercial WISP toolchains had ever unlocked.

---

## Pillar 1 — Live RAM-Only Surgical Patching of the `QCA988x` Xtensa Target CPU (`PB-011` / `PB-030` / `PB-031` / `PB-040`)

| Dimension | Ground-Truth Engineering Detail |
| :--- | :--- |
| **Epistemic Status** | `CONFIRMED BY STATIC RE` (`12/12` `SGMT` segments byte-identical round-trip) · **Active Implementation: `Stage 347A` & `Stage 353A`** |
| **Core Discovery** | The `QCA9880`/`QCA9882` (`AR9888v2`) target firmware (`athwlan_AR9888v2_{ptp,ptmp_ap,ptmp_sta}_bin` and OpenWrt `firmware-5.bin`) uses a `0x544d4753` (`"SGMT"`) `BMI_LZ_DATA` (`LZ77`) container with **`0` cryptographic signature bytes** (`consumed_bytes == container_size`). |
| **Why It Is Groundbreaking** | Allows modifying instructions and baseband register tables inside the radio's dedicated Xtensa CPU **purely in RAM** (`mount --bind /tmp/firmware-5.bin /lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin` + `rmmod/insmod ath10k_pci`) with **zero Flash writes** (a power cycle always restores stock). |
| **3 Surgical Capabilities** | 1. **`PB040-CANARY-RODATA`**: Non-behavioral version-string canary proving clean `BMI_LZ_DATA` decompression and `WMI_READY` boot.<br>2. **`PB040-CCA-AGC-OVERRIDE` (`PB-031`)**: Raised `cca_thresh62` energy-detect threshold inside the `QCA988x` baseband WHAL table so co-located tower sectors do not self-throttle on adjacent-panel RF energy.<br>3. **`PB040-SUB20MHZ-PLL-DIV` (`PB-030`)**: Unlocks **`5 MHz` (Quarter-Rate)** and **`10 MHz` (Half-Rate)** channels on `802.11ac` (`QCA988x`) via PLL clock-divider overrides (`+3 dB` / `+6 dB` thermal noise floor improvement + `2x`/`4x` OFDM cyclic prefix tolerance for NLOS/foliage). |
| **Code & Docs** | [`firmware/xtensa_sgmt_surgical_patcher.py`](../firmware/xtensa_sgmt_surgical_patcher.py) · [`docs/STAGE17_PB040_XTENSA_SURGICAL_RAM_PATCH_SPEC.md`](STAGE17_PB040_XTENSA_SURGICAL_RAM_PATCH_SPEC.md) · `tools/firmware/build_stage347a_xtensa_sgmt_ram_patch_profiles.py` · `tools/re/build_stage353a_sub20mhz_pll_ofdm_timing_matrix.py` |

---

## Pillar 2 — Per-Packet `16-Pilot EVM` & `12.5 ns` (`1.87 m`) Hardware Ranging Before `ath10k` `skb_pull` (`PB-021`)

| Dimension | Ground-Truth Engineering Detail |
| :--- | :--- |
| **Epistemic Status** | `CONFIRMED BY STATIC RE` (`rx_ppdu_end_qca988x` offset layout proven) · **Active Implementation: `Stage 348A`** |
| **Core Discovery** | Every received PPDU from `QCA988x` carries an 84-byte hardware trailer (`rx_ppdu_end_qca988x`) containing **16 per-stream OFDM pilot EVM words (`dwords 0..15`, `evm_p0..evm_p15`)** and an **`80 MHz` fractional hardware arrival clock (`dword 18 [7:0]`, `locationing_timestamp`, `12.5 ns` resolution = `1.87 m`)**. Standard Linux `ath10k_htt_rx_amsdu_pop` discards these 84 bytes via `skb_pull` before `mac80211` ever sees the frame. |
| **Why It Is Groundbreaking** | 1. **Predictive Sub-Stream Modulation Clamping**: Detects pilot EVM degradation on Spatial Stream 1 vs Spatial Stream 0 *hundreds of milliseconds before* CRC/FCS frame loss occurs (e.g., wind moving wet tree branches) and proactively clamps `NSS=1` or `MCS` with **zero packet drops**.<br>2. **Passive `1.87 m` Hardware Ranging & Multipath Spread**: Measures exact ToA/RTT distance and reflection delay spread per client without GPS or extra air probes. |
| **Code & Docs** | [`docs/STAGE17_PB021_031_GROUND_UP_PHY_AND_LTU_SQ_AP.md`](STAGE17_PB021_031_GROUND_UP_PHY_AND_LTU_SQ_AP.md) · `tools/re/build_stage348a_pb021_ppdu_evm_ranging_extractor.py` · `docs/STAGE348A_PB021_PPDU_EVM_RANGING_EXTRACTOR.md` |

---

## Pillar 3 — Unlocking Ubiquiti's Hidden `WMI 0x9064 / 0x9065` Tunnel, `32` Target Polling Hooks & `4-Series` Hardware Retry Table (`PB-010`)

| Dimension | Ground-Truth Engineering Detail |
| :--- | :--- |
| **Epistemic Status** | `CONFIRMED BY STATIC RE` (`51`-entry jump table at `0x009b2037` + `32` hooks at `0x0040f688`) · **Active Implementation: `Stages 317A..322A` & `Stage 354A`** |
| **Core Discovery** | Dissected the complete binary boundary between host MIPS and target Xtensa: `WMI_UBNT_CMDID` (`0x9064` on 5 GHz `10.1` / `0x9070` on 2.4 GHz `10.2`), `WMI_UBNT_HT_COMM_CMDID` (`0x9065`, 36-opcode state machine), the 51-entry Xtensa jump table at `0x009b2037` (`0x17 set_txq_param` $\rightarrow$ `0x009b5c02`, `0x1e set_rate_override`), and `WMI_PEER_RATE_RETRY_SCHED_CMDID` (`0x9044`). |
| **Why It Is Groundbreaking** | 1. **Deterministic Hardware Retry Fallback (`0x9044`)**: Programs the 4 hardware retry series inside the `QCA988x` MAC so that if Try #1 (`2x2 VHT-NSS 2 SGI`) fails an immediate Block-ACK, Try #2 (`50 µs` later in hardware!) automatically transmits at **`1x2 STBC/CDD VHT-NSS 1 LGI (`sgi=0`)`** instead of wasting 10 retries on a dead spatial stream.<br>2. **OpenWrt-Driven Soft-TDMA & Target Hook Control**: Enables driving target airtime/queue hooks from modern Linux `6.6.110` without legacy `airOS` `2.6.32`. |
| **Code & Docs** | [`docs/STAGE17_PB010_011_XTENSA_TARGET_AND_WMI_MAP.md`](STAGE17_PB010_011_XTENSA_TARGET_AND_WMI_MAP.md) · `tools/re/qca988x_target_full_polling_hooks_dissection.py` (`Stage 319A`) · `tools/re/ubnt_poll_ht_comm_state_machine_dissection.py` (`Stage 320A`) · `tools/sim/build_stage354a_wmi_4series_retry_fallback_pareto.py` (`Stage 354A`) |

---

## Pillar 4 — `LTU` Ground-Up Architecture: Native `Short-Queue (SQ)` Micro-AP, Independent `AD9361` Split-Frequency (`TX != RX`), and `4096-QAM` (`12X`)

| Dimension | Ground-Truth Engineering Detail |
| :--- | :--- |
| **Epistemic Status** | `CONFIRMED BY STATIC RE` & `7` Live Bench Rounds (`84` windows on `.110`) · **Active Implementation: `Stages 341A..346A`** |
| **Core Discovery** | 1. **Native Kernel `Short-Queue (SQ)` Micro-AP Mode**: `/bin/ame_drv.sh` line `266` and `ame_core.ko` check `0 < ptmp_max_cpe <= 16` to activate a dedicated low-latency **Short-Queue (`SQ`) DMA scheduler** instead of the heavy 64-CPE macro-sector rings (`ptmp_max_cpe=0`).<br>2. **Independent `TX_LO` vs `RX_LO` on `AD9361` SDR**: Unlike `802.11ac` chips that share a single synthesizer for TDD TX/RX, `LTU`'s Analog Devices `AD9361` agile transceiver has separate `TX` and `RX` local oscillators (`70 MHz–6.0 GHz`), allowing split-frequency operation where the AP transmits on a clean downlink channel and listens on a separate uplink channel.<br>3. **Thermal-Aware `4096-QAM` (`12X`, code `0x1f`)**: Mapped the `0.15 dB / 10°C` PA EVM drift above `45°C` (`Stage 301A`) and built the `SimPy + NSGA-II` hysteresis guard (`Stage 302A`, `601.69 Mbps`). |
| **Code & Docs** | [`docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md`](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md) · [`docs/STAGE301A_LTU_THERMAL_TCXO_IQ_CAL_RE.md`](STAGE301A_LTU_THERMAL_TCXO_IQ_CAL_RE.md) · `tools/re/dissect_stage342a_ltu_short_queue_micro_ap_re.py` · `tools/re/dissect_stage343a_ltu_ad9361_sdr_spi_registers_re.py` · [`firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh`](../firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh) |

---

## Pillar 5 — Zero-False-Positive Cooperative CPE Differential Sensing & Closed-Loop Asymmetric Chain-Mask Rescue (`< 48 KB` C Edge Worker)

| Dimension | Ground-Truth Engineering Detail |
| :--- | :--- |
| **Epistemic Status** | `CONFIRMED ON BENCH` (`PBM5` `+5 dB` RSSI / `-68%` `p95` RTT; `.241 <-> .242` `1472 B` `100% -> 0%` loss with `nss=1 sgi=0`) · **Active Implementation: `Stage 349A` & `Stage 350A`** |
| **Core Discovery** | 1. **Closed-Loop Asymmetric Chain-Mask / Spatial-Stream Rescue Daemon (`Stage 349A`)**: We proved on both `PowerBeam M5` and `PowerBeam 5AC Gen2` (`.241 <-> .242`) that when one polarization/chain is degraded by `>= 6 dB` (due to tree foliage, Fresnel obstruction, or near-field reflections), forcing 2-stream `VHT-NSS 2` or `sgi=1` causes **`60%–100%` loss on full-MTU `1472 B` packets**, whereas switching to **`nss=1 sgi=0` (`1` spatial stream CDD + `800 ns` Long Guard Interval)** while keeping `2x2 MRC` RX restores **`0%` packet loss (`20/20` on `1472 B`, `2.23 ms` RTT)**.<br>2. **Cooperative Multi-CPE Differential Fault Classifier (`Stage 350A`)**: Cross-correlates `evm`, `rx_phy_err`, `chain_delta`, `bmiss`, and `eth0` carrier counters across all CPEs in a sector via a `< 48 KB` C worker (`fmx_micro_worker.c`, `< 96 KB` RAM, zero Flash wear) to mathematically separate: **(A)** Tower AP interference, **(B)** Localized neighborhood Wi-Fi interference affecting 2 adjacent homes, **(C)** Single-CPE foliage/alignment (`chain_delta >= 6 dB`), and **(D)** Customer indoor PoE/cable faults. |
| **Code & Docs** | [`docs/COOPERATIVE_CPE_FEASIBILITY.md`](COOPERATIVE_CPE_FEASIBILITY.md) · [`docs/ZEROCLAW_EDGE_COMPATIBILITY.md`](ZEROCLAW_EDGE_COMPATIBILITY.md) · [`docs/STAGE59A_ZERO_FALSE_POSITIVE_WISP_RF_OBSERVABILITY_AND_GUARIDA_PLAN.md`](STAGE59A_ZERO_FALSE_POSITIVE_WISP_RF_OBSERVABILITY_AND_GUARIDA_PLAN.md) · `tools/firmware/build_stage349a_chain_imbalance_rescue_daemon.py` · `tools/observability/build_stage350a_cooperative_cpe_differential_classifier.py` |

---

## Verification & Promotion Gate (How Every Ground-Up Pillar Is Proven)

1. **Static Binary & ELF Proof (`/fullrea`)**: Every register, WMI command ID, `SGMT` segment offset, and kernel symbol is extracted deterministically with SHA-256 receipts and `pytest` suites.
2. **SimPy + `pymoo` (`NSGA-II`) Pareto Proof**: Multi-objective stress simulation (`goodput`, `p95/p99` latency, `Jain` fairness, packet loss) across 1–64 CPEs before touching hardware.
3. **Counterbalanced Live Hardware Proof (`A1 -> B1 -> A2 -> B2` + `45s/120s` Watchdog)**: Tested in RAM first (`0` Flash risk) on our physical bench radios (`.241 <-> .242` `PBE-5AC-Gen2`, `.20 <-> .250` `LAP-120/Loco5AC`, `.198` `Rocket Prism`, `.253` `Rocket 2AC`, `.110` `LTU-Lite`) before baking into universal SquashFS (`hsqs`) images.
