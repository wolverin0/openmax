<!-- doc-head: Stage 1122A offline fault matrix proving the 1121A PtP canary monitor verdicts; no live claim -->

# Stage 1122A - PtP Canary Monitor Fault Matrix

Test: `tests/test_stage1122a_ptp_canary_monitor_fault_matrix.py`
Subject: `tools/autoresearch/ptp_production_lb5ac_pbe5ac_canary_monitor.py`
Receipt: `artifacts/autoresearch/stage1122a_ptp_canary_monitor_fault_matrix.json`

## What it is
- Pure stdlib pytest, 100% offline; fixtures are offline test text. No device touched, no live claim.
- Matrix rows: `{scenario, injected, expected_verdict, observed, pass}`. Evidence class `CANARY_FAULT_MATRIX`.
- Receipts carry no `session_id` starting `SYNTHETIC-`.

## Thresholds under test
- Loss above 2%, p99 above 40 ms, chain imbalance above 6 dB -> `ROLLBACK_REQUIRED`.
- Soft ranges (loss 0-2%, p99 25-40 ms, chain 3-6 dB) -> `DEGRADED`.

## Scenarios
- Healthy link -> `HEALTHY`.
- Chain imbalance 8 dB -> `ROLLBACK_REQUIRED` (`CHAIN_IMBALANCE`).
- DFS radar CAC in survey -> `DEGRADED` (`DFS_CAC`); DFS CAC is a regulatory wait, not a rollback.
- Bufferbloat p99 60 ms -> `ROLLBACK_REQUIRED` (`P99_RTT`).
- Packet loss 5% -> `ROLLBACK_REQUIRED` (`PACKET_LOSS`).

## Run
- `python -m pytest tests/test_stage1122a_ptp_canary_monitor_fault_matrix.py -q`
- `python tests/test_stage1122a_ptp_canary_monitor_fault_matrix.py` writes the receipt.
