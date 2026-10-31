<!-- doc-head: STAGE12_LIVE_PBM5_219_220_BENCH_AUDIT.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Live PowerBeam M5 300 (`198.18.0.85` $\leftrightarrow$ `198.18.0.86` `XW.v6.3.2`) Bench Baseline & Polling/Aggregation Audit

**Task ID**: `T-PB-GEM1-13`  
**Status**: `AUDIT_COMPLETE` (`automatic_execution_allowed = False`)  
**Implementation**: [`tools/bench/probe_live_pbm5_ptp_pair.py`](../tools/bench/probe_live_pbm5_ptp_pair.py)  
**Artifact Report**: [`artifacts/autoresearch/pbm5_live_pair_219_220_audit_20261024.json`](../artifacts/autoresearch/pbm5_live_pair_219_220_audit_20261024.json)

---

## 1. Topology & Hardware Provenance (`EdgeSwitch 10XP Boca 3`)

| Unit Name | Management IP / Link-Local | Role | SysID / Firmware | SoC & Radio |
| :--- | :--- | :--- | :--- | :--- |
| **`PBM5-PTP-STA-219`** | `198.18.0.85` (`198.18.0.87`) | Station WDS (Boca 3 PoE) | `0xe4b5` / `XW.v6.3.2` | Atheros `AR9342` (`535 MHz` MIPS 74Kc) 2x2 5 GHz 802.11n |
| **`PBM5-PTP-AP-220`** | `198.18.0.86` (`198.18.0.88`) | Access Point WDS (RF-linked) | `0xe4b5` / `XW.v6.3.2` | Atheros `AR9342` (`535 MHz` MIPS 74Kc) 2x2 5 GHz 802.11n |

---

## 2. Diagnosed Stock `XW.v6.3.2` Bottlenecks

1. **`EXCESSIVE_ATH0_TXQUEUELEN` (`txqueuelen = 1000`, `qdisc = pfifo_fast`)**:
   - Stock `XW.v6.3.2` Linux 2.6.32 configures `ath0` with `txqueuelen=1000` (`>1.4 MB` of unmanaged L2 queueing above `ath_dev`), causing bidirectional RRUL `p99` latency to inflate to `46.5..48.2 ms` even on a clean `-51 dBm` (`CINR 42 dB`) link.
2. **`UNBOUNDED_80211N_AMPDUFRAMES_32` (`iwpriv ath0 get_ampduframes = 32`)**:
   - Stock `ampduframes=32` permits maximum-length 802.11n A-MPDUs (`mean_subframes_per_ampdu = 26.4..27.1`). Reducing `ampduframes=24` with `txqueuelen=180` and `HTB + SFQ limit 64` reduces `p99` latency from **`47.1 ms` to `15.57 ms` (`-66.9%`)** while increasing `20 MHz` goodput from **`52.27 Mbps` (`2.613 Mbps/MHz`) to `59.72 Mbps` (`2.986 Mbps/MHz`, `+14.25%`)**, reaching `PROMOTE` in [`RegressionGatekeeper`](../analysis/regression_gate/gatekeeper.py).

---

## 3. Verification

```powershell
pytest tests/test_probe_live_pbm5_ptp_pair.py -v
```
