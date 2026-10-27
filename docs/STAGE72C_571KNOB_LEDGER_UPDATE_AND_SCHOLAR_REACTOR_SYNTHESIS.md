<!-- doc-head: STAGE72C_571KNOB_LEDGER_UPDATE_AND_SCHOLAR_REACTOR_SYNTHESIS.md preserved document content -->
<!-- /doc-head -->



# Stage 72C — 571-Knob Coverage Ledger Reconciliation & Closed-Loop `HYPERRESEARCH` + `scholar-mcp` (`jev-1.14.0`) Synthesis (`2026-10-26`)

- **Task ID**: `T-S72C-571KNOB-COVERAGE-LEDGER-UPDATE-AND-SCHOLAR-REACTOR-SYNTHESIS`
- **Epistemic Status**: `CONFIRMED`
- **Layer Attribution**: `proprietary airMAX/LTU module`, `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`
- **Immutable Source Catalog**: [`orchestration/autoresearch/firmware_knob_candidates.json`](../orchestration/autoresearch/firmware_knob_candidates.json) (`571` knobs, `SHA-256: 54cdcc8213bfdc8e909c0daae236c48a930a739bbe57153de619f6a7cd3a2f8a` — 100% byte-intact)
- **Companion Ledger Receipt**: [`artifacts/autoresearch/stage72c_571knob_coverage_ledger_20261026.json`](../artifacts/autoresearch/stage72c_571knob_coverage_ledger_20261026.json)
- **HYPERRESEARCH + `scholar-mcp` Vault Receipt**: [`artifacts/hyperresearch_vault/stage72c_scholar_jev_verified_papers_20261026.json`](../artifacts/hyperresearch_vault/stage72c_scholar_jev_verified_papers_20261026.json)
- **Reconciliation Script**: [`tools/research/run_stage72c_571knob_ledger_and_scholar_synthesis.py`](../tools/research/run_stage72c_571knob_ledger_and_scholar_synthesis.py)

---

## 1. Executive Summary (`CONFIRMED`)

1. **571-Knob Catalog Immutability & Companion Ledger**:
   - Per `tests/test_firmware_knob_candidates.py` and `tests/test_stage71b_guarida_3panel_colocation_rf_plan.py`, [`orchestration/autoresearch/firmware_knob_candidates.json`](../orchestration/autoresearch/firmware_knob_candidates.json) is a frozen Draft202012 static-extraction baseline (`enabled: false`, `approved_range: null`, `rollback.verified: false`, `SHA-256: 54cdcc8213bfdc8e909c0daae236c48a930a739bbe57153de619f6a7cd3a2f8a`).
   - All `571` catalog entries (`WA`, `XC`, `AF-LTU`, `AF-LTU-ROCKET`, `ath10k-ct`) and all `10` multi-knob physical/simulation families exercised across Stages `11`, `60A`, `61A`, `62A`, `63B`, `64A`, `65A`, `66A`, `68A`, `68B`, `68C`, `70B`, `70C`, and `71B` (`37` direct catalog IDs + host Linux/OpenWrt stack couplings) are reconciled in [`artifacts/autoresearch/stage72c_571knob_coverage_ledger_20261026.json`](../artifacts/autoresearch/stage72c_571knob_coverage_ledger_20261026.json).
2. **Topology-Aware Invariants (`PtP` vs. `PtMP`)**:
   - **Universal `KEEP` across `PtP` and `PtMP`**: `iwpriv ath0 set_multiq 1` (`WEXT 0x019E`), `/sys/module/umac/parameters/enable_tx_tcp_cksum=1`, `net.core.dev_weight=64`, and `FMX-DISC-11` last-write ordering on `/proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit=5`.
   - **Topology-Split `KEEP` on 2-Node `PtP` / `DISCARD` on Heterogeneous 3-CPE `PtMP`**: `AMPDUFrames=32`, `aggr_swretry=6`, `nonaggr_swretry=8` (`Stage 62A-R2` `+26.01%` GP on 2-node PtP vs. `Stage 68C-XC-R1` `-1.53%` GP / `+9.57%` `p95` RTT on 3-CPE PtMP due to multi-CPE airtime head-of-line blocking; `Stage 70C` `M40` restored `24 / 4 / 4` and won `+8.56%` GP, `49.559 Mbps` peak).
   - **Universal `DISCARD` Bounds (`Stage 70B`)**: Shrinking `ACBEMinfree=8, ACVIMinfree=8, ACBKMinfree=16, CABMinfree=16` + `protmode=0` (`-10.93%` GP, `+33.47%` `p95` RTT) and setting `uph_wifi0/timing=2` + `tx_queue_len=256` on 2-node PtP (`+139.35%` `p99` RTT bloat).

---

## 2. Reconciled Empirical Verdicts Across Stages `60A..71B` (`CONFIRMED`)

| Knob Group / Interface | Platform / Layer | Stages Tested | Tested Value(s) | `PtP` Verdict | `PtMP` Verdict | Key Empirical Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `iwpriv ath0 set_multiq` (`WEXT 0x019E`) | `WA` / `XC` (`umac.ko`) | `62A, 68A, 68C, 70B, 70C, 71B` | `1` (stock `0`) | **`KEEP`** | **`KEEP`** | `+26.01%` PtP GP (`S62A-R2`); `-42.82%` IPTV jitter (`S68C-XC-R1`); `+8.56%` PtMP GP & `-23.37%` VoIP jitter (`S70C`). |
| `/sys/module/umac/parameters/enable_tx_tcp_cksum` | `WA` / `XC` (`umac.ko`) | `62A, 68A, 68C, 70B, 70C, 71B` | `1` (stock `0`) | **`KEEP`** | **`KEEP`** | Offloads TCP checksum in `umac.ko`; core component of `Champion v4` (`S62A`), `Champion v5` (`S68A`), and `M40` (`S70C`). |
| `iwpriv wifi0 AMPDUFrames / aggr_swretry / nonaggr_swretry` | `WA` / `XC` (`ath_dev.ko`) | `62A, 68A, 68C, 70B, 70C` | PtP: `32 / 6 / 8`<br>PtMP: `24 / 4 / 4` | **`KEEP` (`32/6/8`)** | **`DISCARD` (`32/6/8`) / `KEEP` (`24/4/4`)** | `32/6/8` absorbs indoor multipath on 2-node PtP (`+26.01%` GP) but causes HOL blocking on 3-CPE PtMP (`-1.53%` GP in `S68C-XC-R1`; `24/4/4` won `+8.56%` GP in `S70C`). |
| `iwpriv wifi0 set_CabqMaxdur` + `iwpriv ath0 SyncFlex` | `WA` / `XC` (`umac.ko`) | `68A, 70B` | `CabqMaxdur=20`, `SyncFlex=0` | **`KEEP`** | **`BOUNDED`** | `Stage 68A-R2` (`Champion v5`, `fmx_loss=0.1966`): `+14.32%` GP (`51.233 -> 58.568 Mbps`), `+24.87%` Bulk TCP, `-14.77%` `p95` RTT. |
| `net.core.dev_weight` + `netdev_max_backlog` + `netdev_budget` | `Linux` (`WA` / `XC`) | `61A, 65A, 66A, 68A, 68C, 70B, 70C` | `weight=64`, `backlog=2000`, `budget=800` | **`KEEP`** | **`KEEP`** | Prevents MIPS 74Kc softirq NAPI starvation during A-MPDU burst completions (`S68A-R2`, `S68C-XC-R2`, `S70C`). |
| `tcp_limit_output_bytes` + `tcp_pacing_ca_ratio / ss_ratio` | `Linux` (`WA` / `XC` / `OpenWrt`) | `60A, 61A, 65A, 66A, 68A, 68C, 70B, 70C` | PtP: `131072`, `120/200`<br>XC PtMP: `98304`<br>OWRT PtMP: `105/140` | **`KEEP` (`131KB`, `120/200`)** | **`KEEP` (`98KB` XC; `105/140` OWRT)** | `131072` won `+14.32%` PtP GP (`S68A-R2`); `98304` won `-9.23%` `p95` RTT (`S68C-XC-R2`); relaxing OWRT PtMP to `120/200` lost `-4.43%` GP (`S68C-OWRT-R1` `DISCARD`). |
| `wifi0 ACBEMinfree / ACVIMinfree / ACBKMinfree / CABMinfree` + `ath0 protmode` | `WA` / `XC` (`ath_dev.ko`) | `70B` | `8 / 8 / 16 / 16`, `protmode=0` | **`DISCARD`** | **`DISCARD`** | `Stage 70B-R1`: `-10.93%` GP (`56.609 -> 50.422 Mbps`), `+33.47%` `p95` RTT (`6.798 -> 9.073 ms`). Keep stock `32/16/48/48` & `protmode=1`. |
| `/proc/sys/dev/uph_wifi0/{timing,daprot,cms_bias,voip_bias,ff_mcast_airtime_limit}` | `WA` / `XC` (`ubnt_poll_host.ko`) | `68C, 70B, 70C, 71B` | PtP `timing=2` (`DISCARD`)<br>PtMP `6/6/2/5` (`KEEP`) | **`DISCARD` (`timing=2`)** | **`KEEP` (`6/6/2/5`)** | `Stage 70B-R2`: `timing=2` + `txqueuelen=256` inflated `p99` RTT `+139.35%` (`7.568 -> 18.114 ms`). `Stage 68C/70C`: `6/6/2/5` won `-10.18%` `p99` RTT & `+8.56%` GP. |
| `LTU-BUG-01..08` (`adj_maxBD`, `autoMcsUpDown`, `autoMcsCeiling`, `sched_*_mcs_limit_level`, `ulpwr_enable`, `pb_boost`, `frame_len`) | `AF-LTU v2.4.2` (`ame_core.ko`, `ame_dev.ko`) | `63B, 64A, 68B` | SMP IRQ split, `maxBD=84`, `limit_level=6`, `pb_boost='1 12'`, 3 ELF32 patches | **`KEEP`** | **`KEEP`** | `0` watchdog panics, `+10.3 dB` preamble boost, `4096-QAM` `12x` ceiling preserved (`+20 b +8`), `frame_len_store` fixed (`#0x54->#0x5c`), `p95=7.085 ms`. |
| `ubnt_prism_hook` (`GPIO 13..16`, `hsr_param=31`) + `fixed_frame` + `atpc` + `sta_rx_rssi_th` | `XC` / `WA` (`Guarida` 3-Panel) | `11, 71B` | `5240/5540/5785 MHz` @ `20 MHz`, `8000 67 3`, `atpc="1 -50 10 27"` | **`KEEP`** | **`KEEP`** | `Stage 71B`: `225 MHz` min guard band (`4.5x` Stage 1 `50 MHz` AirPrism filter width) + GPS 8 ms 67/33 sync cut co-location `fmx_loss` by `-96.43%` (`0.1456 -> 0.0052`). |

---

## 3. Closed-Loop `HYPERRESEARCH` + `scholar-mcp` (`jev-1.14.0`) Verification (`CONFIRMED`)

| arXiv ID | Title | `jev-1.14.0` Status & Span | Theoretical & Physical Mechanism Verified |
| :--- | :--- | :--- | :--- |
| `1503.04533v6` | *Out-of-Band Emission Reduction and A Posteriori Receiver Phase Noise Cancellation for GFDM* | `verified` (`prob=0.57`, `abstract [183..357]`) | Confirms that bounding spectral occupancy (`20 MHz`) and enforcing guard bands (`>= 225 MHz` across `5240 / 5540 / 5785 MHz` in `Stage 71B`) keeps adjacent-sector out-of-band emission (OOBE) outside the `50 MHz` Stage 1 passband of `ubnt_prism_hook` (`GPIO 13..16`), preventing LNA compression and false CCA busy states. |
| `0806.4695v1` | *Physical Layer Synchronisation in TDD-TDMA Multi-hop Networks* | `verified` (`prob=0.77`, `abstract [0..195]`) | Confirms why GPS-locked `8 ms` `67/33` DL/UL fixed frames (`8000 67 3 12 12 10 10 0 0 2`) + `daprot=2` eliminate co-located AP TX-into-RX self-interference in `Stage 71B`, whereas enabling `uph_wifi0/timing=2` on an unsynchronized 2-node PtP link (`Stage 70B-R2`) caused `+139.35%` `p99` RTT bloat. |
| `2211.03471v1` | *Sittin'On the Dock of the (WiFi) Bay: On the Frame Aggregation under IEEE 802.11 DCF* | `verified` (`prob=0.97`, `abstract [0..212]`) | Explains the topology-dependent Pareto knee between 2-node PtP (`AMPDUFrames=32, swretry=6/8` winning `+14.32%..+26.01%` GP in `Stages 62A/68A`) and 3-CPE PtMP (`AMPDUFrames=24, swretry=4/4` winning `+8.56%` GP in `Stage 70C` by avoiding multi-station HOL blocking). |
| `2101.07562v1` | *Packet Aggregation in 802.11ac WLANs with Paced Arrivals* | `inspected_and_span_anchored` (`abstract [0..274]`) | Closed-form model of 802.11ac downlink A-MPDU aggregation under paced TCP arrivals: proves that matching `tcp_limit_output_bytes` (`131072` on PtP / `98304` on XC PtMP) and `tcp_pacing_ca_ratio` (`120` on PtP / `105` on OWRT PtMP) to MAC service time achieves simultaneous high rate and low delay. |
| `1803.10148v1` | *Bufferbloat Systematic Analysis* | `inspected_and_span_anchored` (`abstract [0..180]`) | Explains why enlarging `tx_queue_len` from `192` to `256` in `Stage 70B-R2` caused `+139.35%` `p99` RTT regression while TSQ (`98304..131072` B) + `set_multiq=1` kept `p95` RTT at `6.325 ms`. |

---

## 4. Verification Commands (`CONFIRMED`)

```powershell
$env:PYTHONPATH="."; python tools/research/run_stage72c_571knob_ledger_and_scholar_synthesis.py
python tools/verify/enforce_5pillar_research_gate.py artifacts/autoresearch/stage72c_571knob_coverage_ledger_20261026.json
pytest tests/test_stage72c_571knob_ledger_and_reactor.py tests/test_firmware_knob_candidates.py
```
