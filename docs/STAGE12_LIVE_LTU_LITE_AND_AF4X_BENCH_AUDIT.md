<!-- doc-head: STAGE12_LIVE_LTU_LITE_AND_AF4X_BENCH_AUDIT.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Live LTU-Lite (`Boca 5`, `afltu.v2.4.0`) & AirFiber 4X (`AF-4X`) PoE/Link Diagnostic Audit

**Task ID**: `T-PB-GEM1-15`  
**Status**: `AUDIT_COMPLETE` (`automatic_execution_allowed = False`)  
**Implementation**: [`tools/bench/probe_live_ltu_and_af4x.py`](../tools/bench/probe_live_ltu_and_af4x.py)  
**Artifact Report**: [`artifacts/autoresearch/ltu_lite_and_af4x_bench_audit_20261024.json`](../artifacts/autoresearch/ltu_lite_and_af4x_bench_audit_20261024.json)

---

## 1. Live `LTU-Lite` (`EdgeSwitch 10XP Boca 5`) Architecture & Interoperability Boundary

| Parameter | Verified Value |
| :--- | :--- |
| **Management Endpoints** | `198.18.0.84` / `PUBLIC_DEVICE_0046` (`MAC PUBLIC_DEVICE_0055`) |
| **Firmware & SoC** | `afltu.v2.4.0` (`amesoc3` ARM + Custom Non-802.11 OFDM FPGA/ASIC) |
| **Channel Widths & Max MCS** | `{10, 20, 30, 40, 50, 100}` MHz, `4096-QAM (12x, MCS 12)` |
| **802.11ac (`QCA988x`) Over-the-Air Interop** | `False` (Proprietary LTU physical layer; requires `LTU-Rocket` AP) |
| **FuturaMAX Integration Mode** | External BNG `CAKE` + `DSCP` Tin Mapping + Tower Conflict-Graph Spectrum Planner |

---

## 2. AirFiber 4X (`AF-4X`) 4-Pair PoE vs. EdgeSwitch 10XP 2-Pair PoE Diagnostic

- **Electrical Pinout Mismatch**:
  - The **EdgeSwitch 10XP (`ES-10XP`)** delivers 24V Passive PoE on **2 pairs only**: Pins `4, 5` (`+24V`) and Pins `7, 8` (`Return/GND`).
  - The **AirFiber 4X (`AF-4X`)** Invictus radio requires the **24V 1A 4-Pair Gigabit PoE Injector (`GP-B240-100` / `POE-24-24W-G`)**, which supplies `+24V` on Pins `1, 2, 4, 5` and `Return/GND` on Pins `3, 6, 7, 8` (`50%` lower loop resistance: `1.41 Ohm` vs `2.82 Ohm` on a `15 m` drop, preventing input bridge asymmetry and Invictus FPGA/PA surge brownout).
- **Remediation Checklist**:
  1. Insert a `24V 1A` **4-Pair** Gigabit PoE injector (`GP-B240-100`) on the `AF-4X` drop.
  2. Test forcing `100Mbps Full-Duplex` on the switch port to isolate Data Pair (`1,2` / `3,6`) vs Power Pair (`4,5` / `7,8`) magnetics.
  3. Check `198.18.0.50` during the first `5s` after power-on for `u-boot` TFTP recovery state.

---

## 3. Verification

```powershell
pytest tests/test_probe_live_ltu_and_af4x.py -v
```
