<!-- doc-head: Stage 482A SimPy + pymoo NSGA-II Evaluation of Pillar 5 32-CPE Cooperative Differential Fault Classification & Airtime Rescue -->
Evaluates Pillar 5's `< 48 KB` C Edge Micro-Worker (`controller/fmx_micro_worker.c`) across Guarida's exact 3-panel / `32`-CPE topology under simultaneous rain fade, localized neighborhood Wi-Fi interference, and single-CPE wet-foliage polarization imbalance.
<!-- /doc-head -->

# Stage 482A — `SimPy` + `pymoo` `NSGA-II` Evaluation of Pillar 5 `32`-CPE Cooperative Differential Fault Classification & Airtime Rescue

- **Epistemic Status**: `CONFIRMED` (`SimPy` + `pymoo` `NSGA-II` multi-objective optimization anchored on `Guarida` `32`-CPE radiography)
- **Attribution**: `external controller` (`controller/fmx_micro_worker.c` `< 48 KB` C edge agent + differential spatial correlator)
- **Script**: [`run_stage482a_cooperative_32cpe_edge_micro_worker_pareto.py`](../tools/sim/run_stage482a_cooperative_32cpe_edge_micro_worker_pareto.py)
- **JSON Receipt**: [`stage482a_cooperative_32cpe_edge_micro_worker_pareto.json`](../artifacts/autoresearch/stage482a_cooperative_32cpe_edge_micro_worker_pareto.json)

---

## 1. Why Single-CPE Threshold Alerting Generates False Positives During Rain Fade

In Guarida's **3-panel / `32`-CPE** topology (`Panel1-Guarida` `4` CPEs, `Panel2-Guarida` `22` CPEs, `Panel3-Guarida` `6` CPEs), three distinct physical impairments often overlap simultaneously:
1. **Sector-Wide Rain / Humidity Attenuation**: All `22` CPEs on `Panel2` drop CINR by `3–5 dB` simultaneously while keeping balanced chains (`|chain0 - chain1| < 2 dB`). Uncoordinated monitors fire `14+` false-positive "CPE alignment degraded" alerts per frame.
2. **Localized Neighborhood Wi-Fi Cluster (`3` adjacent homes)**: `3` geographically adjacent CPEs experience simultaneous `rx_phy_err` and pilot EVM degradation while the other `19` CPEs on the same sector remain clean.
3. **Single-CPE Wet-Foliage Polarization Imbalance (`>= 6.0 dB` chain $\Delta$)**: Individual CPEs (such as `MONZON_Thomas` `-18.3 dB` chain delta in `Stage 419A`) suffer deep cross-polar cancellation on one chain and must be clamped to **`NSS=1 CDD SGI=0`** before they drag down sector airtime.

---

## 2. `SimPy` + `NSGA-II` Pareto Results (`32` CPEs Under Simultaneous Rain + Cluster + Foliage Faults)

| Policy / Architecture | Quorum (`CPEs`) | Chain $\Delta$ Clamp | `32`-CPE Goodput (`Mbps`) | `p99` Latency (`ms`) | `32`-CPE Jain Fairness | False-Positive Alert Rate | Fault Classification Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Uncoordinated Single-CPE Baseline** | N/A | Static | `423.25 Mbps` | `85.74 ms` | `0.8827` | `43.75%` | `33.33%` |
| **Pillar 5 Cooperative `32`-CPE Champion** | **`3`** | **`5.1 dB`** | **`772.88 Mbps` (`+82.61%`)** | **`16.25 ms` (`-81.05%`)** | **`0.9779`** | **`0.0%` (`0` false truck rolls)** | **`100.0%`** |
