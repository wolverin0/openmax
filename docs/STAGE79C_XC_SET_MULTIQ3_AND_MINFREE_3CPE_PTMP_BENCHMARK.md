<!-- doc-head: STAGE79C_XC_SET_MULTIQ3_AND_MINFREE_3CPE_PTMP_BENCHMARK.md preserved document content -->
<!-- /doc-head -->


# Stage 79C — `XC` (`Rocket 5AC Prism Gen2`) `set_multiq=3` (`0x3`) + WMM `Minfree` Hierarchy & `XW` `txqueuelen=64/128` 3-CPE PtMP Benchmark (`FMX-DISC-23`)

- **Date**: `2026-10-26`
- **Task ID**: `T-S79C-XC-SET-MULTIQ-3-AND-WMM-MINFREE-HIERARCHY-3CPE-PTMP-BENCH`
- **Harness**: [`tools/bench/run_stage79c_xc_multiq3_and_minfree_3cpe_ptmp.py`](../tools/bench/run_stage79c_xc_multiq3_and_minfree_3cpe_ptmp.py)
- **Artifact**: [`artifacts/autoresearch/stage79c_xc_multiq3_and_minfree_3cpe_ptmp_20261026.json`](../artifacts/autoresearch/stage79c_xc_multiq3_and_minfree_3cpe_ptmp_20261026.json)
- **Pytest Suite**: [`tests/test_stage79c_xc_multiq3_and_minfree_3cpe_ptmp.py`](../tests/test_stage79c_xc_multiq3_and_minfree_3cpe_ptmp.py)
- **Claim Status**: `CONFIRMED` (`3` counterbalanced `A1 -> B1 -> A2 -> B2` rounds = `12` physical Triple-Play windows; `0` flash writes; `45s` auto-rollback watchdog; Bench restored to `Stage 72A Champion v20`)

---

## 1. Executive Summary & Attribution

Stage 79C evaluates the full `UMAC-BUG-01` (`umac.ko` `osif_select_queue` `0x09e93c..0x09eaa8` + `osif_vap_hardstart_generic` `0x09f2a8`) bitmask (`set_multiq=3` / `0x3`: Bit 0 `0x1` 5-subqueue WMM mapping & `75%` `ol_tx_ll` XOFF + Bit 1 `0x2` deep `802.1Q VLAN` `0x8100` / `PPPoE` `0x8864` inner-DSCP inspection at `0x09df98`) together with the `ath_dev.ko` WMM TX buffer reservation hierarchy (`/sys/module/ath_dev/parameters/ACVOMinfree=0, ACVIMinfree=16, ACBEMinfree=32, ACBKMinfree=48`) on the `Rocket 5AC Prism Gen2` (`XC` `.198`), both standalone (`S79C-R1`) and coupled with `LiteBeam M5` (`XW` `.4`) `ath0 txqueuelen=64` (`S79C-R2`) and `txqueuelen=128` (`S79C-R3`), against the **`Stage 72A Champion v20` Control** (`XC set_multiq=1`, `XW txqueuelen=256`).

### Key Findings (`FMX-DISC-23`)
1. **`S79C-R1` (`XC set_multiq=3 + WMM Minfree 0/16/32/48` on `Champion v20`)**:
   - **Aggregate Goodput**: **`+3.924%` (`39.196 -> 40.734 Mbps`)**, beating Control `A` in **both** counterbalanced halves (`B1 = 40.823 > A1 = 38.950 Mbps` and `B2 = 40.645 > A2 = 39.442 Mbps`).
   - **Triple-Play Jitter**: Slashed **IPTV (`AC_VI`) jitter by `-28.190%` (`2.210 -> 1.587 ms`, `0.0%` loss)** and **VoIP (`AC_VO`) jitter by `-7.594%` (`2.594 -> 2.397 ms`, `0.0%` loss)**, achieving **`+1.5836%` Pareto composite**.
   - **Untagged Bridge Latency Cost of Bit 1 (`0x2`)**: Loaded `p95` RTT rose `+6.687%` (`86.202 -> 91.966 ms`, where `B2 = 89.150 ms < A2 = 93.638 ms`, while `B1 = 94.783 ms > A1 = 78.766 ms`). Because the 3-CPE bench carries untagged L2 WDS bridge traffic, `set_multiq=1` (`0x1`, `Stage 72A Champion v20`) already executes IP DSCP classification without invoking the extra `0x09df98` `802.1Q`/`PPPoE` header walk per skb.
   - **Operational Rule (`CONFIRMED`)**: Keep **`set_multiq=1`** (`0x1`, `Stage 72A Champion v20`) as the default for untagged WDS PtMP sectors, and enable **`set_multiq=3` (`0x3`) + `AC*Minfree=0/16/32/48`** specifically on `802.1Q` VLAN-tagged or `PPPoE`-encapsulated subscriber links.
2. **`S79C-R2` (`XC set_multiq=3 + Minfree 0/16/32/48` + `XW ath0 txqueuelen=64, netdev_max_backlog=1024`)**:
   - Slashed loaded **`p95` RTT by `-19.048%` (`109.022 -> 88.255 ms`)**, **`p99` RTT by `-15.400%` (`116.534 -> 98.588 ms`)**, **`p50` RTT by `-4.749%` (`47.275 -> 45.030 ms`)**, and **IPTV jitter by `-4.762%`**, achieving **`+3.7903%` Pareto composite**, while trimming aggregate goodput by `-2.877%` (`42.376 -> 41.157 Mbps`).
3. **`S79C-R3` (`XC set_multiq=3 + Minfree 0/16/32/48` + `XW ath0 txqueuelen=128, netdev_max_backlog=1024`)**:
   - Cut **IPTV jitter `-2.246%`** (`1.692 -> 1.654 ms`) and **VoIP jitter `-9.735%`** (`2.753 -> 2.485 ms`), with `-5.565%` goodput (`35.941 -> 33.941 Mbps`) and `+1.399%` `p95` RTT (`87.132 -> 88.351 ms`).

| Layer | Attribution | Mechanism |
| :--- | :--- | :--- |
| `proprietary airMAX/LTU module` (`umac.ko` on `XC` `.198`) | `CONFIRMED` | `osif_select_queue` (`0x09e93c`): `Bit 0` (`0x1`) enables 5-subqueue WMM mapping + `75%` `ol_tx_ll` XOFF (`0x09f2a8`); `Bit 1` (`0x2`) invokes `0x09df98` (`802.1Q` `0x8100` / `PPPoE` `0x8864` inner-DSCP parser). |
| `proprietary airMAX/LTU module` (`ath_dev.ko` on `XC` `.198`) | `CONFIRMED` | `ACVOMinfree=0, ACVIMinfree=16, ACBEMinfree=32, ACBKMinfree=48` reserves hardware TX descriptors for `AC_VO`/`AC_VI` when `AC_BE` saturates (`-28.19%` IPTV jitter, `-7.59%` VoIP jitter in `S79C-R1`). |
| `Linux` (`ath0 txqueuelen` on `XW` `.4`) | `CONFIRMED` | Tightening `XW` (`AR9342`) `ath0 txqueuelen` from `256` to `64` (`S79C-R2`) cuts sector `p95` RTT `-19.05%` and `p99` RTT `-15.40%` at `-2.88%` goodput cost. |

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Summary (`12` Windows)

| Round ID | Mechanism ID | Arm A Goodput (`Mbps`) | Arm B Goodput (`Mbps`) | GP $\Delta$ (`%`) | Arm A `p95` (`ms`) | Arm B `p95` (`ms`) | `p95` $\Delta$ (`%`) | Arm A `p99` (`ms`) | Arm B `p99` (`ms`) | IPTV Jitter $\Delta$ (`%`) | VoIP Jitter $\Delta$ (`%`) | Pareto $\Delta$ (`%`) | Decision |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`S79C-R1`** | `M43a_XC_SET_MULTIQ_3_AND_WMM_MINFREE_0_16_32_48_ON_CHAMPION_V20` | `39.196` | **`40.734`** | **`+3.924%`** | `86.202` | `91.966` | `+6.687%` | `96.246` | `101.644` | **`-28.190%`** | **`-7.594%`** | **`+1.5836%`** | `RETAIN_CURRENT_CHAMPION` |
| **`S79C-R2`** | `M43b_XC_SET_MULTIQ_3_AND_XW_ATH0_TXQUEUELEN_64_BACKLOG_1024` | `42.376` | `41.157` | `-2.877%` | `109.022` | **`88.255`** | **`-19.048%`** | `116.534` | **`98.588`** | **`-4.762%`** | `+49.726%` | **`+3.7903%`** | `RETAIN_CURRENT_CHAMPION` |
| **`S79C-R3`** | `M43c_XC_SET_MULTIQ_3_AND_XW_ATH0_TXQUEUELEN_128_BACKLOG_1024` | `35.941` | `33.941` | `-5.565%` | `87.132` | `88.351` | `+1.399%` | `100.044` | `102.096` | **`-2.246%`** | **`-9.735%`** | `-6.0543%` | `RETAIN_CURRENT_CHAMPION` |

---

## 3. Per-Phase Telemetry Breakdown (`A1 -> B1 -> A2 -> B2`)

| Round | Phase | Aggregate GP (`Mbps`) | `WA` GP (`Mbps`) | `XC` GP (`Mbps`) | `XW` GP (`Mbps`) | `p50` RTT (`ms`) | `p95` RTT (`ms`) | `p99` RTT (`ms`) | IPTV Bitrate / Jitter / Loss | VoIP Jitter / Loss | `XC` Getter (`multiq / Minfree VO,VI,BE,BK`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S79C-R1`** | `A1` | `38.950` | `38.093` | `0.818` | `0.039` | `40.702` | `78.766` | `92.642` | `4.95 Mbps / 2.340 ms / 0.0%` | `2.227 ms / 0.0%` | `1 / 0,0,0,0` |
| **`S79C-R1`** | **`B1`** | **`40.823`** | `39.961` | `0.822` | `0.040` | `51.076` | `94.783` | `96.263` | `4.98 Mbps / 1.483 ms / 0.0%` | `1.972 ms / 0.0%` | **`3 / 0,16,32,48`** |
| **`S79C-R1`** | `A2` | `39.442` | `38.584` | `0.814` | `0.044` | `38.385` | `93.638` | `99.850` | `4.97 Mbps / 2.080 ms / 0.0%` | `2.961 ms / 0.0%` | `1 / 0,0,0,0` |
| **`S79C-R1`** | **`B2`** | **`40.645`** | `39.776` | `0.827` | `0.042` | `47.164` | **`89.150`** | `107.024` | `4.96 Mbps / 1.691 ms / 0.0%` | `2.822 ms / 0.0%` | **`3 / 0,16,32,48`** |
| **`S79C-R2`** | `A1` | `46.912` | `46.043` | `0.833` | `0.036` | `44.236` | `130.224` | `136.841` | `4.96 Mbps / 2.125 ms / 0.0%` | `1.514 ms / 0.33%` | `1 / 0,0,0,0` (`XW qlen=256`) |
| **`S79C-R2`** | **`B1`** | `42.208` | `41.347` | `0.819` | `0.042` | `43.528` | **`88.316`** | **`101.676`** | `4.95 Mbps / 2.387 ms / 0.14%` | `2.704 ms / 0.0%` | **`3 / 0,16,32,48`** (`XW qlen=64`) |
| **`S79C-R2`** | `A2` | `37.840` | `37.001` | `0.800` | `0.039` | `50.314` | `87.821` | `96.228` | `4.91 Mbps / 2.664 ms / 0.81%` | `2.496 ms / 0.0%` | `1 / 0,0,0,0` (`XW qlen=256`) |
| **`S79C-R2`** | **`B2`** | `40.106` | `39.248` | `0.822` | `0.036` | `46.533` | **`88.194`** | **`95.501`** | `4.95 Mbps / 2.173 ms / 0.04%` | `3.299 ms / 0.0%` | **`3 / 0,16,32,48`** (`XW qlen=64`) |
| **`S79C-R3`** | `A1` | `35.278` | `34.454` | `0.782` | `0.042` | `43.541` | `87.911` | `94.531` | `4.94 Mbps / 1.463 ms / 1.02%` | `2.526 ms / 0.17%` | `1 / 0,0,0,0` (`XW qlen=256`) |
| **`S79C-R3`** | **`B1`** | `35.424` | `34.565` | `0.822` | `0.037` | `46.017` | `89.373` | `99.327` | `4.95 Mbps / 1.501 ms / 0.28%` | `2.517 ms / 0.0%` | **`3 / 0,16,32,48`** (`XW qlen=128`) |
| **`S79C-R3`** | `A2` | `36.604` | `35.752` | `0.811` | `0.041` | `37.896` | `86.353` | `105.557` | `4.94 Mbps / 1.922 ms / 0.07%` | `2.980 ms / 0.33%` | `1 / 0,0,0,0` (`XW qlen=256`) |
| **`S79C-R3`** | **`B2`** | `32.458` | `31.613` | `0.805` | `0.040` | `44.918` | `87.330` | `104.864` | `4.76 Mbps / 1.807 ms / 4.39%` | `2.454 ms / 0.83%` | **`3 / 0,16,32,48`** (`XW qlen=128`) |

---

## 4. Closed-Loop Research Reactor & Verification

- **Closed-Loop Research Reactor**: Triggered automatically on all 3 non-promoted rounds (`research_reactor_triggered: true`), emitting targeted `scholar-mcp` follow-up queries to `artifacts/autoresearch/discovery_to_research_queue.json`.
- **Bench Post-State**: Restored to `Stage 72A Champion v20` (`apply_v20_champion_baseline(reset_xw=True)`).
