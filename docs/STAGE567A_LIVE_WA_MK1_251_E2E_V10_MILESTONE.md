<!-- doc-head: STAGE567A_LIVE_WA_MK1_251_E2E_V10_MILESTONE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 567A — Live `WA` + `MikroTik MK1-251` End-to-End 4-Class DiffServ QoE Stress `v10` (`S567A-E2E-R6`)

- **Claim Classification**: `CONFIRMED`
- **Subsystem Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `Linux`, `external controller` (`MikroTik RB750Gr3 MK1-251` Boca 7), `hardware`
- **Safety Boundaries**: `198.18.0.45` and `198.18.0.46` untouched (`touched_241_or_242 = false`); `0` flash writes.

---

## 1. End-to-End Topology & `A1 -> B1 -> A2 -> B2` Results (`S567A-E2E-R6`)

Path: `CPE .250 (PBE-5AC-Gen2)` $\leftrightarrow$ `5 GHz 4-Addr WDS` $\leftrightarrow$ `AP .20 (LBE-5AC-Gen2)` $\leftrightarrow$ `Switch` $\leftrightarrow$ `Boca 7 MikroTik MK1-251 (.251)`.

| Metric | Arm A (`Stock OpenWrt 24.10.4`) | Arm B (`63-Round WA Champion v10` + `PB-050`) | Delta |
| :--- | :--- | :--- | :--- |
| **Mean Total Goodput** | `62.100 Mbps` (`A1=60.511`, `A2=63.689`) | **`69.945 Mbps`** (`B1=69.697`, `B2=70.192`) | **`+12.63%`** |
| **RF Under-Load `p50` RTT** | `86.358 ms` (`A1=90.231`, `A2=82.484`) | **`26.581 ms`** (`B1=30.336`, `B2=22.825`) | **`-69.22%`** |
| **`MK1-251` E2E `p50` RTT** | `86.358 ms` | **`26.581 ms`** | **`-69.22%`** |
| **Decision** | Baseline | **`PROMOTE_ARM_B`** | **4-Class DiffServ Verified (`CS0`, `AF21`, `AF41`, `EF`)** |

---

## 2. Artifacts & Verification

- JSON Receipt: [`stage567a_live_wa_mk1_251_e2e_v10_milestone.json`](../artifacts/autoresearch/stage567a_live_wa_mk1_251_e2e_v10_milestone.json)
- Runner: [`run_stage567a_live_wa_mk1_251_e2e_v10_milestone.py`](../tools/autoresearch/run_stage567a_live_wa_mk1_251_e2e_v10_milestone.py)
- Test Suite: [`test_stage567a.py`](../tests/test_stage567a.py)
