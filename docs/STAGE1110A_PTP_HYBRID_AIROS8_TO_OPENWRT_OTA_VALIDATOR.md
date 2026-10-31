<!-- doc-head: Stage 1110A offline command-plan and readback validator for PtP hybrid airOS 8 AP to OpenWrt STA and full OpenWrt v17 cutover; no live claim -->

# Stage 1110A - PtP Hybrid airOS 8 to OpenWrt OTA Validator

Module: `tools/autoresearch/ptp_hybrid_airos8_to_openwrt_ota_validator.py`
Test: `tools/autoresearch/test_ptp_hybrid_ota_validator_selftest.py`
Receipt: `artifacts/autoresearch/stage1110a_ptp_hybrid_airos8_to_openwrt_ota_validator.json`

## What it is
- Pure stdlib, offline. It builds read-only command plans and validates text captures; it runs nothing.
- `build_step1_plan(...)`, `build_step2_plan(...)`, `validate_step(capture, expected) -> {ok, verdict, checks, failures}`.

## Step 1: Hybrid airOS 8 AP and OpenWrt STA (WDS)
- airOS readback: `cat /tmp/system.cfg | grep -E '(allow_80211|op_mode|agg_SW_limit|cwmin|cwmax|txqueuelen)'`.
- Expected Hybrid Mode values: `allow_80211=1`, `op_mode=0`, `agg_SW_limit=50000`, `cwmin=3`, `cwmax=7`, `txqueuelen=256`.
- Knobs are matched by the last dotted key segment; the key prefixes are operator-pattern-derived, not captured.
- OpenWrt side: the Stage 1014A parser (`tools/qca988x/validate_wa_tcless_statless_profile_readback.py`).
- The legacy `firmware/openwrt/pbe5ac_gen2_ptp_kit/enable_airos8_ap_hybrid_80211_for_openwrt_sta.sh` is retired and carries no knobs.

## Step 2: Full OpenWrt AP and OpenWrt STA v17 cutover
- Plan: v17 kit `--dry-run` and `--verify` (never `--apply`), plus 1097A pre/post-flight argv lists.
- Validation delegates to the Stage 1097A verifier in `tools/autoresearch/ptp_canary_pre_and_post_flight_verifier.py`.

## Verdicts
- Step 1: `PASS`, `FAIL_AIROS_HYBRID_KNOBS`, `FAIL_OPENWRT_READBACK`, `FAIL_CAPTURE_MALFORMED`.
- Step 2: the 1097A verdicts; without an MCS floor parameter the result is `SKIPPED_NO_FLOOR`.

## Evidence
- `evidence_class` is `OTA_VALIDATOR_COMMAND_PLAN`; fixtures are synthetic and operator-pattern-derived; no live claim.
- Claim id: `FMX-STAGE1110A-PTP-HYBRID-AIROS8-OTA-VALIDATOR`.
