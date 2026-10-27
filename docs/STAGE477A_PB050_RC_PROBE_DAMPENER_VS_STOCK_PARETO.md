<!-- doc-head: STAGE477A_PB050_RC_PROBE_DAMPENER_VS_STOCK_PARETO.md preserved document content -->
<!-- /doc-head -->



# Stage 477A — `SimPy` + `pymoo` (`NSGA-II`) Evaluation of `PB050-RC-PROBE-DAMPEN` vs Stock `QCA988x`

- **Claim Status**: `CONFIRMED` in Discrete-Event Simulation + Multi-Objective `NSGA-II` Optimization (`live_devices_touched = False`).
- **Subsystem Attribution**: `QCA firmware` (`QCA988x` Xtensa `_rate_find_rc` @ `0x0099d1c0` & `_rate_Input_tx_status` @ `0x0099dc64`).
- **Generator & Receipt**:
  - [`run_stage477a_pb050_rc_probe_dampener_vs_stock_pareto.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/sim/run_stage477a_pb050_rc_probe_dampener_vs_stock_pareto.py)
  - [`stage477a_pb050_rc_probe_dampener_vs_stock_pareto.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage477a_pb050_rc_probe_dampener_vs_stock_pareto.json)
  - [`test_stage477a.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage477a.py)

---

## 1. Physical Mechanism Modeled from Disassembled Xtensa Code

In both OpenWrt `10.1.467-ct` (`0x0098a3d8`) and Stock `airOS 8` `10.2.4` (`0x0098a015`), `WMI_PEER_ASSOC_CMDID` overwrites `g_rc_probe_pkt_threshold = 32` (`movi.n a9, 32`) and `g_rc_probe_period_ms = 5000`. Under a near-field reflection or multipath selective-fading channel where `MCS 7` (`64-QAM 5/6`, `585 Mbps` PHY) is stable (`~4.8%` MPDU PER) but `MCS 8/9` (`256-QAM`, `702/780 Mbps` PHY) suffers severe inter-symbol interference (`38%–82%` PER and frequent `XRETRY`):
1. **Aggressive Upward Probing**: Every `32` packets (~2 A-MPDUs), `_rate_find_rc` (`0x0099d1c0`) forces an upward probe PPDU at `MCS 8`.
2. **XRETRY Poisoning of the Serving Rate**: When the probe PPDU or a short fading burst triggers `XRETRY`, `_rate_Input_tx_status` (`0x0099e65c`) adds `g_default_xretry_per_penalty = 30` (`clamped at 80`) to the PER estimate, pushing it across `g_rc_rate_max_per_thr = 65` (`0x0099e956`) and causing unnecessary downshifts to `MCS 6` / `MCS 5`.

`PB050-RC-PROBE-DAMPEN` (built in Stage 474A) patches `SGMT` binaries so that:
- `g_rc_probe_pkt_threshold = 512` (16x less frequent packet-driven upward probing),
- `g_rc_probe_period_ms = 15000` (3x longer timer-driven probing),
- `g_default_xretry_per_penalty = 12` (requires multiple consecutive `XRETRY` events before forcing a downshift),
- `g_rc_rate_max_per_thr = 72` (wider transient fading tolerance before stepping down MCS).

---

## 2. Counterbalanced Multi-Seed `SimPy` + `pymoo` (`NSGA-II`) Results

Across 4 independent seeds (`477..480`, `12,000 ms` per run):

| Profile | `probe_pkt_thr` | `probe_period_ms` | `xretry_penalty` | `max_per_thr` | Goodput (Mbps) | `p99` Latency (ms) | Probe Overhead (%) | MCS Downshifts | `fmx_loss` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stock `10.2.4` / OpenWrt Assoc Override** | `32` | `5000` | `30` | `65` | Baseline (lower) | Higher (`> 3.0 ms`) | `~50.0%` | Frequent | Higher |
| **OpenWrt `10.1.467-ct` Static `.data` Init** | `64` | `256` | `30` | `65` | Intermediate | Intermediate | `~33.3%` | Frequent | Intermediate |
| **`PB050-RC-PROBE-DAMPEN` (Stage 474A)** | **`512`** | **`15000`** | **`12`** | **`72`** | **`+122.86 Mbps` (`+44.15%`)** | **`-9.19%` reduction** | **`~4.3%`** | **Minimal** | **`-0.5193` delta** |

All exact numeric metrics and the top-10 `NSGA-II` Pareto front solutions are recorded in [`stage477a_pb050_rc_probe_dampener_vs_stock_pareto.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage477a_pb050_rc_probe_dampener_vs_stock_pareto.json).
