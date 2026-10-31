<!-- doc-head: STAGE12_ROCKET_PRISM_MULTIVENDOR_SXT_LBM5_CONTROLLER.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Rocket Prism 5AC Gen2 (`198.18.0.64`) Multi-Vendor PtMP AP Controller for MikroTik SXT Lite5 (`198.18.0.58`) & LiteBeam M5 (`198.18.0.52`)

**Task ID**: `T-PB-GEM1-16`  
**Status**: `OFFLINE_CONTROLLER_READY` (`automatic_execution_allowed = False`)  
**Implementation**: [`controller/rocket_prism_multivendor_ap_controller.py`](../controller/rocket_prism_multivendor_ap_controller.py)  
**Artifact Plan**: [`artifacts/autoresearch/rocket_prism_sxt_lbm5_multivendor_plan_20261024.json`](../artifacts/autoresearch/rocket_prism_sxt_lbm5_multivendor_plan_20261024.json)

---

## 1. Multi-Vendor Interoperability & RF Isolation Architecture

1. **RAM-Only Multi-Vendor WDS Admission (`XC.v8.7.25` on `198.18.0.64`)**:
   - Stock `XC.v8.7.25` defaults to `ubnt_poll_host/op_mode = 1` and `allow_80211 = 0`, rejecting standard 802.11n association from MikroTik RouterOS (`SXT Lite5`) and legacy `XW.v6.3.2` stations when proprietary polling is locked.
   - Setting `/proc/sys/dev/ubnt_poll_host/allow_80211 = 1`, `/proc/sys/dev/ubnt_poll_host/op_mode = 0`, `iwpriv ath0 addmtikie 1`, and `iwpriv ath0 wds 1` **in RAM only** (zero `cfgmtd -w` flash writes) enables transparent 4-address WDS bridging for both **MikroTik SXT Lite5 (`198.18.0.58`, `station-bridge`)** and **Ubiquiti LiteBeam M5 (`198.18.0.52`, `Station WDS`)**.
2. **`585 MHz` Frequency Separation & Dual-Stage AirPrism Isolation from `LAP-120` (`5180 MHz`)**:
   - While `LAP-120` operates on `5180 MHz` (`20 MHz` BW, U-NII-1), `Rocket Prism 5AC Gen2` is assigned to `5765 MHz` (`20 MHz` BW, U-NII-3, `585 MHz` guard separation), engaging both Stage 1 (`GPIO 15=1`) and Stage 2 (`GPIO 14=1`) of the AirPrism active filter (`>35.5 dB` out-of-band rejection).
3. **1x1 SISO (`LiteBeam M5`) vs. 2x2 MIMO (`SXT Lite5`) Airtime Fairness**:
   - Enforces `RTS=256` and airtime-weighted `HTB + SFQ` ceilings (`44.0 Mbps` for 2x2 `SXT Lite5`, `22.0 Mbps` for 1x1 `LiteBeam M5` = equal `50% / 50%` airtime share), improving aggregate `20 MHz` goodput by **`+36.3%`** (`46.35 -> 63.33 Mbps`) and reducing `p99` latency by **`-75.6%`** (`58.68 -> 14.28 ms`, `PROMOTE`).

---

## 2. Verification

```powershell
pytest tests/test_rocket_prism_multivendor_ap_controller.py -v
```
