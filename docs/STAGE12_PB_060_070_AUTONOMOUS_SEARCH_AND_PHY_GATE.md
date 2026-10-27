<!-- doc-head: STAGE12_PB_060_070_AUTONOMOUS_SEARCH_AND_PHY_GATE.md preserved document content -->
<!-- /doc-head -->

# Stage 12 — PB-060 & PB-070 Autonomous Search & Custom-PHY Eligibility Gate

**Workstream**: Phase 0 Physical-Boundary Program (`PB-060` & `PB-070`)  
**Status**: `OFFLINE_CONTROLLER_READY` (`automatic_execution_allowed = False`)  
**Implementation**: [`controller/pb_060_070_autonomous_search_and_phy_gate.py`](../controller/pb_060_070_autonomous_search_and_phy_gate.py)  
**Artifact Report**: [`artifacts/qca988x/pb_060_070_pilot_and_verdict.json`](../artifacts/qca988x/pb_060_070_pilot_and_verdict.json)

---

## 1. Gate PB-060: Safe Autonomous MAC/PHY Holdout Search Pilot

Gate **PB-060** implements the disciplined closed-loop optimizer over allowlisted L1/L2 parameters (`channel_width_mhz`, `tx_power_dbm`, `ldpc_enabled`, `stbc_enabled`, `sgi_enabled`, `rts_threshold_bytes`, `aql_be_limit_us`):

1. **Canonical Fingerprinting & Deduplication**:
   - Every [`SearchCandidateConfig`](../controller/pb_060_070_autonomous_search_and_phy_gate.py#L41-L69) computes a canonical SHA-256 fingerprint (`fingerprint()`) over its parameter payload, automatically skipping duplicate trials (`CAND_02_DUPLICATE_OF_CAND_01`).
2. **Strict Safety & Regulatory Envelope Gate**:
   - `validate_candidate_safety_envelope()` rejects any candidate outside allowlisted channel widths (`{5, 10, 20, 40}` MHz), legal TX power (`[3, 23]` dBm), RTS thresholds (`{256, 512, 2347}`), or AQL limits (`[2000, 8000]` $\mu\text{s}$) before execution (`CAND_04_ILLEGAL_TX_POWER_30DBM` rejected).
3. **Mandatory Negative-Control Injection & Holm-Šidák Holdout Replication**:
   - Every search campaign includes an injected `is_negative_control=True` A/A null arm (`CAND_00_NEG_CTRL_AA`), verifying `negative_control_false_positives == 0`.
   - Family-wise error rate across $M$ non-control hypotheses is controlled via Šidák adjustment ($\alpha_{\text{adj}} = 1 - (1 - \alpha)^{1/M}$).
   - **Two-Stage Promotion**: Candidates passing discovery (`KEEP_FOR_REPLICATION`) must also pass paired A/B/A/B evaluation on an **unseen holdout time-block** (`holdout_replicated=True`) to achieve `PROMOTE`. Overfitted candidates (`CAND_03_20MHZ_SGI_NO_HOLDOUT`) are automatically downgraded to `REJECT_FAILED_HOLDOUT_REPLICATION`.

---

## 2. Gate PB-070: Custom Constellation / Learned-PHY Eligibility Gate

Gate **PB-070** (`evaluate_pb070_custom_phy_gate`) enforces the hard 3-condition prerequisite gate before any custom constellation or learned-waveform experiment is allowed on QCA988x hardware:

| Condition | Requirement | Current QCA988x Status |
| :--- | :--- | :--- |
| **Condition 1** | Writable constellation mapper/pilot/FEC table OR continuous raw TX/RX IQ injection (`PB-023`) | `False` (802.11ac mapper/demapper & BCC/LDPC are fixed in baseband silicon; `0x9070` is diagnostic snapshot only) |
| **Condition 2** | Verified modified QCA988x target execution (`PB-040`) | `False` (`PB-011`/`PB-040` offline SGMT BCL-LZ77 re-pack proven; live target execution awaits physical bench) |
| **Condition 3** | External calibrated VSA/SDR waveform & EVM verification | `False` (unexecuted) |

- **Current Verdict**: `LOCKED_CONCENTRATE_ON_MAC_AND_POLICY` (`custom_phy_waveform_claims_allowed = False`).
- Engineering effort remains 100% focused on where QCA988x provides real, measurable leverage: sub-20 MHz (`5/10 MHz`) width adaptation, LDPC/STBC/CCA response surfaces, target/host TDMA & ACK-clocked scheduling, and closed-loop QoE policy.

---

## 3. Verification

```powershell
pytest tests/test_pb_060_070_autonomous_search_and_phy_gate.py -v
```
