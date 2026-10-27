<!-- doc-head: Stage 886A A/A negative-control & hold-out identity protocol (A03 remediation); fail-closed validator + 7 adversarial self-tests all passing -->
# Stage 886A — A/A Negative-Control & Hold-Out Identity Protocol

- **Claim Status**: `CONFIRMED` (offline protocol + self-test)
- **Attribution**: `external controller (offline protocol + self-test)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage886a_post_audit_aa_control_protocol.json`
- **Tool**: `tools/verify/build_stage886a_post_audit_aa_control_protocol.py`
- **Evidence class**: `PROTOCOL_AND_SELFTEST`

## 1. Why
Audit finding A03: the PB060 campaign evaluator declared an A/A negative control and
an unseen hold-out mandatory, but did **not require** a measured control to exist, nor
that discovery and hold-out be identity-disjoint. The same list could be passed as both
arms, and promotion rested on a boolean `holdout_replicated=True`.

## 2. Fail-closed contract
A campaign may be promoted only if **all** hold:
1. **Negative control present & measured** — ≥ 2 A/A runs, each with measured data.
2. **Hold-out identity disjoint** — discovery vs hold-out run-ids *and* raw hashes
   must not overlap.
3. **Hold-out evidence is measured** — a replication record, never a bare boolean.
4. **Applied-config readback** — proof the candidate config was actually applied.
5. **On incompatible control improvement** — INVALIDATE the campaign; never omit the control.

## 3. Adversarial self-tests (all must be rejected except the valid case)
| Case | Expected | Result |
| :--- | :--- | :--- |
| valid_campaign | accept | ✅ |
| no_control | reject | ✅ |
| empty_control | reject | ✅ |
| same_dataset_both_arms | reject | ✅ |
| raw_hash_overlap | reject | ✅ |
| boolean_holdout | reject | ✅ |
| no_readback | reject | ✅ |

**7/7 self-tests pass** — the validator is fail-closed by construction.

## 4. Reproduce & limits
```sh
python tools/verify/build_stage886a_post_audit_aa_control_protocol.py
python -m pytest tests/test_stage885a_to_890a_suite.py -q
```
This is a protocol + reference validator, not a patch to the live evaluator
(`controller/pb_060_070_autonomous_search_and_phy_gate.py` is owned by another lane).
Wiring this contract into that evaluator is a separate, lane-owned change.
