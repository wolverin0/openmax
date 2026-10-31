<!-- doc-head: Stage 1012A consumer gate for Stages 1007A..1011A (host triple-play probe, OpenWrt 24.10 AQM/AQL parser, readiness audits); offline, fail-closed, evidence_class HOST_TRIPLE_PLAY_AND_OPENWRT2410_PARSER_GATE -->
<!-- /doc-head -->
# Stage 1012A - Host Triple-Play and OpenWrt 24.10 Parser Gate

Offline, fail-closed, localhost-only consumer gate for Stages 1007A..1011A. No device is touched.

## Artifacts

- Gate: `tools/verify/verify_stage1012a_host_triple_play_and_openwrt2410_parser_gate.py`
- Suite: `tests/test_stage1007a_to_1012a_suite.py`
- Receipt: `artifacts/autoresearch/stage1012a_host_triple_play_and_openwrt2410_parser_gate_receipt.json`

## Checks

1. Receipts 1007A..1011A exist, are not all-NUL, have `status == "CONFIRMED"`, `live_devices_touched is False`, a `five_pillar_compliance` block and pass `audit_stage_receipt_5pillars`.
2. Docs 1007A..1012A exist, are under 180 lines and start with a doc-head opening.
3. Functional: the 1008A parser (`tools/qca988x/openwrt2410_aqm_aql_busybox_parser.py`) returns `aql_txq_limit` rows VO 300/600, VI 1000/2000, BE 1500/3000, BK 500/1000 and raises on malformed input.
4. Functional: the 1007A probe (`workloads/host_driven_triple_play_socket_probe.py`) pointed at a closed 127.0.0.1 port with a 1 s timeout exits non-zero and writes no JSON.
5. The 1007A and 1008A unit tests pass via `python -m pytest`.
6. Every `readiness_verdict` in the 1009A..1011A `targets` arrays is in `{PRODUCTION_READY, CONDITIONALLY_READY, NOT_READY, NO_EVIDENCE}`. Set membership only: the gate never demands READY.

## Honesty boundary

The gate validates tooling and the shape and integrity of audit receipts. It does not turn a `NOT_READY` or `NO_EVIDENCE` verdict into readiness, and it makes no on-air claim.

## Run

`python tools/verify/verify_stage1012a_host_triple_play_and_openwrt2410_parser_gate.py` then `python -m pytest tests/test_stage1007a_to_1012a_suite.py -q`.

## Memory

Claim id `FMX-STAGE1012A-HOST-TRIPLE-PLAY-AND-PARSER-GATE`, scope `project:futuramax`.
