<!-- doc-head: Stage 1121A offline command-plan builder and capture parser for monitoring a production LB5AC/PBE5AC PtP link; no live claim -->

# Stage 1121A - PtP Production LB5AC/PBE5AC Canary Monitor

Module: `tools/autoresearch/ptp_production_lb5ac_pbe5ac_canary_monitor.py`
Test: `tests/test_stage1122a_ptp_canary_monitor_fault_matrix.py`
Receipt: `artifacts/autoresearch/stage1121a_ptp_production_lb5ac_pbe5ac_canary_monitor.json`

## What it is
- Pure stdlib and 100% offline. It never touches a device and makes no live claim.
- `build_plan(*, phy, iface, peer_host, root="")` returns the read-only argv steps the live lane runs.
- `evaluate(capture, thresholds=None)` parses the returned text and returns `{verdict, checks, failures, metrics}`.
- Capture keys: `station_dump`, `aqm`, `aql_txq_limit`, `survey_dump`, `ping_summary`.
- `aqm` and `aql_txq_limit` reuse `parse_aqm` / `parse_aql_txq_limit` from `tools/qca988x/openwrt2410_aqm_aql_busybox_parser.py`.
- Evidence class: `COMMAND_PLAN_AND_PARSER_SELFTEST`.

## Ping
- Integer interval only: `ping -c 20 -i 1 -W 2 <peer>`. Fractional `-i 0.x` is a 1025A finding.
- p99 is nearest-rank over the `time=` samples; without samples the `max` of the rtt line is used.

## Thresholds (operator-given, overridable)
- Packet loss greater than 2% -> `ROLLBACK_REQUIRED`.
- p99 RTT greater than 40 ms -> `ROLLBACK_REQUIRED`.
- Chain imbalance (abs chain0 - chain1) greater than 6 dB -> `ROLLBACK_REQUIRED`.
- Soft ranges -> `DEGRADED`: loss above 0 up to 2%, p99 25-40 ms, chain 3-6 dB.
- Missing or unparsable captures -> `DEGRADED` (never silently `HEALTHY`).

## DFS CAC
- A `radar` / `CAC` / `DFS` marker in `survey_dump` is a regulatory channel-availability wait.
- It yields `DEGRADED` with reason `DFS_CAC` and is NOT an automatic rollback.

## Run
- `python tools/autoresearch/ptp_production_lb5ac_pbe5ac_canary_monitor.py` writes the receipt (all-NUL self-check, 3 retries, LF).
- Fault matrix: see `docs/STAGE1122A_PTP_CANARY_MONITOR_FAULT_MATRIX.md`.
