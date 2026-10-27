<!-- doc-head: STAGE24_HYPERRESEARCH_NOVEL_MECHANISMS_SYNTHESIS.md preserved document content -->
<!-- /doc-head -->

# Stage 24A — HyperResearch Deep Literature Sweep & Novel Hardware-Executable Mechanisms Synthesis

**Task ID**: `T-S24A-HYPERRESEARCH-BACKGROUND-DEEP-SWEEP`  
**Status**: `CONFIRMED` (`hyperresearch` v0.12.0 Vault Populated, Repaired, and Verified)  
**Persistent Knowledge Base**: `artifacts/hyperresearch_vault` (`vault_tag: stage24a-20261025`)  
**Ingestion & Verification Script**: [`tools/bench/run_stage24a_hyperresearch_sweep.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/bench/run_stage24a_hyperresearch_sweep.py)  
**Vault Receipt Artifact**: [`artifacts/autoresearch/stage24_hyperresearch_vault_receipt_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage24_hyperresearch_vault_receipt_20261025.json)  

---

## 1. Executive Summary

Using the `hyperresearch` (`hpr` v0.12.0) academic discovery (`openalex`, `crossref`, `doab`), web source fetching (`hyperresearch fetch`), linked markdown note graph (`hyperresearch note new` + `hyperresearch link` + `hyperresearch repair`), and structured claim extraction (`hyperresearch claims ingest`) pipeline inside `artifacts/hyperresearch_vault`, we executed a systematic literature sweep across four active FuturaMAX R&D frontiers:

1. **Frontier A (`Query A`)**: *802.11ac airtime fairness, AQL, CoDel bufferbloat, and MAC-aware TCP pacing*
   - Primary Sources Ingested:
     - **Zhou et al. (2026)**, *AirBBR: MAC-Aware Airtime Fairness for BBR via TCP ACK-based RTT Inference* (`10.2139/ssrn.7434484`, OpenAlex `W7211942885`).
     - **Høiland-Jørgensen / Sensors (2018)**, *A Responsible Airtime Approach for True Time-Based Fairness in Multi-Rate WiFi Networks* (`10.3390/s18113658`).
     - **Flow-CoDel (2025)**, *Per-flow active queue management for balanced delay and drops in bufferbloat mitigation* (`10.1007/s44354-025-00012-z`).
2. **Frontier B (`Query B`)**: *AD9361 4096-QAM / 1024-QAM EVM, phase noise, and TDD turnaround calibration*
   - Primary Sources Ingested:
     - **EuMC / EuMIC (2019)**, *4096-QAM Microwave Transmitter Providing Efficiency Exceeding 50% and EVM Below 1%* (`10.23919/eumc.2019.8910819`, `10.23919/eumic.2019.8909666`).
     - **OFC (2018)**, *Experimental and Numerical Comparison of Probabilistically-Shaped 4096-QAM and Uniformly-Shaped 1024-QAM/4096-QAM* (`10.1364/ofc.2018.m3c.5`).
3. **Frontier C (`Query C`)**: *Outdoor PtMP TDMA scheduling, hidden-terminal detection, and adaptive RTS/CTS*
   - Primary Sources Ingested:
     - **Hidden Terminal Detection in Wide-Area 802.11 Wireless Networks (2012)** (`https://hdl.handle.net/10289/6419`).
     - **Towards Application Layer TDMA in Wi-Fi Networks (2016)** (`http://hdl.handle.net/10138/230771`).
4. **Frontier D (`Query D`)**: *MIMO chain imbalance, asymmetric transmit antenna selection, and front-end mitigation*
   - Primary Sources Ingested:
     - **Rice University (2013)**, *Coordination and Interference in 802.11 Networks: Inference, Analysis and Mitigation* (`http://hdl.handle.net/1911/71994`).
     - **Tampere University (2011)**, *Digital Front-End Signal Processing with Widely-Linear Signal Models in Radio Devices* (`https://trepo.tuni.fi/handle/10024/114867`).

---

## 2. Five Concrete Hardware-Executable Mechanisms & Untested Parameter Mutations

### Mechanism M1 — `AirBBR` + `Responsible Airtime` Dynamic DRR Weight Controller (`mac80211` `airtime_weight` & `AQL`)
- **Paper Provenance**: `10.2139/ssrn.7434484` (*AirBBR*, 2026) + `10.3390/s18113658` (*Responsible Airtime*, 2018).
- **Physical Insight**:
  - `AirBBR` proves a two-regime airtime pacing law: for small station counts ($N \le 2$), standard airtime-fraction allocation suffices; for larger contending station counts ($N \ge 3$), applying a multiplicative $(N-1)/N$ reduction triggered only when a station exhibits elevated packet loss/retries curbs weak-station airtime waste by **18.6%**, recovering **+10.0%** aggregate 802.11ac goodput and cutting average RTT by **-12.0%**.
  - `Responsible Airtime` (`10.3390/s18113658`) proves that `mac80211`'s Deficit Round Robin (DRR) scheduler must penalize stations for their CSMA/CA contention and retry airtime overhead ($1 + \alpha \cdot \text{PER}_i$).
- **Hardware-Executable Law on OpenWrt `LAP-120` (`phy0-ap0`)**:
  $$W_i(t) = \max\left(64,\ \text{round}\left(W_{\text{contract}, i} \cdot \left(\frac{N_{\text{busy}} - 1}{N_{\text{busy}}}\right)^{\mathbb{I}(N_{\text{busy}} \ge 3 \land \text{PER}_i \ge 0.10)} \cdot \frac{1}{1 + 2.5 \cdot \text{PER}_i}\right)\right)$$
  applied via:
  ```sh
  iw dev phy0-ap0 station set <CPE_MAC> airtime_weight <W_i>
  ```
  alongside our regime-switched AQL ceilings (`900/1500 us` for $N_{\text{busy}} \le 1$; `1850/3700 us` for $N_{\text{busy}} \ge 2$).

---

### Mechanism M2 — `PB-021` EVM-vs-Retry Hidden-Node Classifier & Zero-Overhead Adaptive RTS/CTS
- **Paper Provenance**: `https://hdl.handle.net/10289/6419` (*Hidden Terminal Detection in Wide-Area 802.11 Wireless Networks*, 2012) + `PB-021` (`rx_ppdu_end` 16-pilot EVM).
- **Physical Insight**:
  - Always-on RTS/CTS wastes `44..60 us` per TXOP when only 1 CPE is active (`active_busy_cpes == 1`), whereas disabling RTS/CTS under multi-CPE hidden-node contention causes catastrophic A-MPDU collisions.
  - By comparing `PB-021` per-pilot EVM (`stream0_mean_evm_db`, `stream1_mean_evm_db` on received preambles) against `mcs_retry_pct`:
    - **Case 1 (Hidden-Node Collision)**: `active_busy_cpes >= 2` AND `mcs_retry_pct >= 12.0%` AND `max(stream0_evm, stream1_evm) <= -20.0 dB` (received signal quality is clean, so retries are caused by collisions, not weak SNR) $\rightarrow$ **Enable RTS/CTS (`iw phy phy0 set rts 512`)**.
    - **Case 2 (Weak-SNR / Single-CPE)**: `active_busy_cpes == 1` OR (`mcs_retry_pct < 8.0%`) $\rightarrow$ **Disable RTS/CTS (`iw phy phy0 set rts off`)** to reclaim full TXOP efficiency.

---

### Mechanism M3 — Dual-Trigger Asymmetric Transmit Antenna Selection (`PB-021` Pilot EVM + Chain RSSI Hysteresis)
- **Paper Provenance**: `http://hdl.handle.net/1911/71994` (2013) + `https://trepo.tuni.fi/handle/10024/114867` (2011) + FuturaMAX Wave 8 (`PBM5-R28`) & Stage 20 (`ClosedLoopChampionSwitcher`).
- **Physical Insight**:
  - When Fresnel obstruction or cross-polarization creates $\ge 5.0\text{ dB}$ chain imbalance, 2-stream spatial multiplexing splits power equally ($-3\text{ dB}$ per chain) and suffers 32%–42% PER on the weaker stream.
  - Triggering `AsymmetricChainMaskRescue` (`txchainmask = best_chain in {1, 2}`, `rxchainmask = 3`) on $\Delta_{\text{eff}} = \max(|\text{RSSI}_0 - \text{RSSI}_1|, |\text{EVM}_0 - \text{EVM}_1|) \ge 5.0\text{ dB}$ (with exit hysteresis $\le 3.0\text{ dB}$) concentrates $+3\text{ dB}$ PA power onto the clean chain while retaining 2-antenna Maximum Ratio Combining (MRC) on receive.

---

### Mechanism M4 — `AD9361` LTU Early-Symbol Phase-Noise Guard & Power/Symbol Balance Co-Tuning
- **Paper Provenance**: `10.23919/eumc.2019.8910819` (*EuMC 2019*) + `10.1364/ofc.2018.m3c.5` (*OFC 2018*).
- **Physical Insight**:
  - `4096-QAM` requires composite RMS EVM $< 1.0\%$ ($<-40\text{ dB}$). During TDD TX/RX turnaround on the `AD9361` agile transceiver, LO phase settling and PA thermal transient degrade EVM on the first OFDM symbols of each burst.
- **Hardware-Executable Knobs on `LTU` (`ame_core`)**:
  - Verified Champion foundation: `sched_mcs_limit_symbol_begin=14` + `change_ssd_pause_flag=1` + `sched_max_agg_cnt=8`.
  - Newly identified untested incremental mutation for LTU PtMP:
    ```sh
    echo 1 > /sys/module/ame_core/parameters/power_Balance_adjust
    echo 2 > /sys/module/ame_core/parameters/dl_ul_Symbol_adjust
    ```

---

### Mechanism M5 — Host-Bounded AQL ($\le 1.85\text{ ms}$) + Xtensa Target-Side TDMA (`0x9064` `PB-040`) Hybrid Architecture
- **Paper Provenance**: `http://hdl.handle.net/10138/230771` (*Towards Application Layer TDMA in Wi-Fi Networks*, 2016) + FuturaMAX `PB-010/011` & `PB-040`.
- **Physical Insight**:
  - Host-layer TDMA over commercial 802.11 NICs fails whenever lower-layer driver/firmware queues buffer $>2\text{ ms}$ of frames (`24,000 us` stock `ath10k` AQL).
  - Bounding `aql_txq_limit` to `900..1850 us` satisfies the $<2\text{ ms}$ lower-layer queue ownership gate, while our `PB-040` surgical Xtensa RAM patch (`WMI_ATH_POLL_CMDID = 0x9064` $\rightarrow$ `0x009b5c02`) provides sub-$50\ \mu\text{s}$ target-enforced TDMA slot timing inside `AR9888v2` RAM.
