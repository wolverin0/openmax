<!-- doc-head: STAGE509A_LIVE_WA_MK1_251_E2E_V9_STRESS.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 509A — Live `WA` + `MikroTik MK1-251` End-to-End 4-Class DiffServ QoE Stress `v9` (`S509A-E2E-R5`)

- **Claim Classification**: `CONFIRMED`
- **Subsystem Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `Linux`, `external controller` (`MikroTik RB750Gr3 MK1-251` Boca 7), `hardware`
- **Safety Boundaries**: `198.18.0.45` and `198.18.0.46` untouched (`touched_241_or_242 = false`).

---

## 1. End-to-End Topology & `A1 -> B1 -> A2 -> B2` Results (`S509A-E2E-R5`)

Path: `CPE .250 (PBE-5AC-Gen2)` $\leftrightarrow$ `5 GHz 4-Addr WDS` $\leftrightarrow$ `AP .20 (LBE-5AC-Gen2)` $\leftrightarrow$ `Switch` $\leftrightarrow$ `Boca 7 MikroTik MK1-251 (.251)`.

| Metric | Arm A (`Stock OpenWrt 24.10.4`) | Arm B (`56-Round WA Champion v9` + `PB-050`) | Delta |
| :--- | :--- | :--- | :--- |
| **Mean Total Goodput** | `56.549 Mbps` (`A1=55.834`, `A2=57.264`) | **`68.749 Mbps`** (`B1=69.125`, `B2=68.373`) | **`+21.57%`** |
| **RF Under-Load `p50` RTT** | `92.957 ms` (`A1=95.189`, `A2=90.725`) | **`34.321 ms`** (`B1=32.450`, `B2=36.192`) | **`-63.08%`** |
| **RF Under-Load `p95` RTT** | `151.160 ms` | **`84.701 ms`** | **`-43.97%`** |
| **`MK1-251` E2E `p50` RTT** | `72.530 ms` (`A1=77.874`, `A2=67.186`) | **`8.740 ms`** (`B1=9.614`, `B2=7.865`) | **`-87.95%`** |
| **Multi-Objective Pareto Score** | `0.2326` | **`0.8111`** | **`+248.71%`** (`PROMOTE_ARM_B`) |

---

## 2. Artifacts & Verification

- JSON Receipt: [`stage509a_live_wa_mk1_251_e2e_v9_stress.json`](../artifacts/autoresearch/stage509a_live_wa_mk1_251_e2e_v9_stress.json)
- Runner: [`run_stage509a_live_wa_mk1_251_e2e_v9_stress.py`](../tools/benchmarks/run_stage509a_live_wa_mk1_251_e2e_v9_stress.py)
- Test Suite: [`test_stage509a.py`](../tests/test_stage509a.py)
