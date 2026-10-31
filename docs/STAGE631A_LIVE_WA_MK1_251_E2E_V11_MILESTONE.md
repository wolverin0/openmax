<!-- doc-head: STAGE631A_LIVE_WA_MK1_251_E2E_V11_MILESTONE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 631A — Live `WA` + `MikroTik MK1-251` End-to-End 4-Class DiffServ QoE Stress `v11` (`S631A-E2E-R7`)

- **Claim Classification**: `CONFIRMED`
- **Subsystem Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `Linux`, `external controller` (`MikroTik RB750Gr3 MK1-251` Boca 7), `hardware`
- **Safety Boundaries**: `198.18.0.45` and `198.18.0.46` untouched (`touched_241_or_242 = false`); `0` flash writes.

---

## 1. End-to-End Topology & `A1 -> B1 -> A2 -> B2` Results (`S631A-E2E-R7`)

Path: `CPE .250 (PBE-5AC-Gen2)` $\leftrightarrow$ `5 GHz 4-Addr WDS` $\leftrightarrow$ `AP .20 (LBE-5AC-Gen2)` $\leftrightarrow$ `Switch` $\leftrightarrow$ `Boca 7 MikroTik MK1-251 (.251)`.

| Metric | Arm A (`Stock OpenWrt 24.10.4`) | Arm B (`70-Round WA Champion v11` + `PB-050`) | Delta |
| :--- | :--- | :--- | :--- |
| **Mean Total Goodput** | `58.639 Mbps` (`A1=60.383`, `A2=56.895`) | **`70.098 Mbps`** (`B1=71.435`, `B2=68.761`) | **`+19.54%`** |
| **RF Under-Load `p50` RTT** | `66.717 ms` (`A1=65.415`, `A2=68.019`) | **`23.198 ms`** (`B1=29.162`, `B2=17.234`) | **`-65.23%`** |
| **`MK1-251` E2E `p50` RTT** | `66.717 ms` | **`23.198 ms`** | **`-65.23%`** |
| **Decision** | Baseline | **`PROMOTE_ARM_B`** | **4-Class DiffServ Verified (`CS0`, `AF21`, `AF41`, `EF`)** |

---

## 2. Artifacts & Verification

- JSON Receipt: [`stage631a_live_wa_mk1_251_e2e_v11_milestone.json`](../artifacts/autoresearch/stage631a_live_wa_mk1_251_e2e_v11_milestone.json)
- Runner: [`run_stage631a_live_wa_mk1_251_e2e_v11_milestone.py`](../tools/autoresearch/run_stage631a_live_wa_mk1_251_e2e_v11_milestone.py)
- Test Suite: [`test_stage631a.py`](../tests/test_stage631a.py)
