<!-- doc-head: Stage 1097A offline PtP canary pre/post-flight command-plan builder and capture verifier (PowerBeam 5AC Gen2, LiteBeam 5AC Gen2); no live claim -->

# Stage 1097A - PtP Canary Pre/Post-Flight Verifier

Module: `tools/autoresearch/ptp_canary_pre_and_post_flight_verifier.py`
Receipt: `artifacts/autoresearch/stage1097a_ptp_canary_pre_and_post_flight_verifier.json`

## What it is
- Pure stdlib, offline. It never touches a device and never runs a command.
- `build_plan(role, *, phy, iface, peer_host, root="")` returns argv lists for the live lane (role `pre` or `post`).
- `verify(pre_capture, post_capture, expected)` parses text captures the live lane returns and gives `{ok, verdict, checks, failures}`.
- Captures are parsed offline: this stage makes no live claim about any radio.

## Checks and provenance
- mtd invariance: `sha256sum /dev/mtdblock0 /dev/mtdblock1 /dev/mtdblock5` (block devices; raw `/dev/mtdN` short-reads on OOB). Check is pre == post only. There is NO reference hash in the repo for these radios, and none is invented. Change gives `FAIL_MTD_CHANGED`.
- AQL/AQM/scalars: numeric `aql_txq_limit` rows 0..3 plus `BC/MC 50000`, `fq_limit 2048`, `fq_memory_limit 4194304`, `fq_quantum 1514`, `tcp_notsent_lowat 131072`, `default_qdisc fq_codel`. Reuses `parse_aqm` and `validate_readback` (numeric rows are mapped to the named-AC form first). Missing BC/MC gives `FAIL_BCMC_MISSING`.
- WDS 4addr/AP_VLAN: an interface matching `^phy\d+-ap0\.sta\d+$` must be in `net_list`, AP role only. The name pattern is operator-pattern-derived (project memory), not a capture.
- Packet loss: BusyBox summary (format as in Stage 906A `loaded ICMP lost 1/20`). Plan uses integer `-i`/`-W` only (fractional ping is a 1025A finding). 0 loss means received == transmitted and transmitted >= 20; fewer probes give `INSUFFICIENT_PROBES`, loss gives `FAIL_LOSS`.
- MCS floor: parsed from `station_dump` `tx bitrate`. The floor is a PARAMETER (`mcs_floor_mbps`), default None gives `SKIPPED_NO_FLOOR`. No Mbps value is invented.

## Verdicts
`PASS`, `FAIL_MTD_CHANGED`, `FAIL_BCMC_MISSING`, `FAIL_MCS_DEGRADED`, `FAIL_LOSS`, `INSUFFICIENT_PROBES`, `SKIPPED_NO_FLOOR`, `ROLLBACK_TRIGGERED` (post capture key `rollback_triggered`), plus `FAIL_AQM_AQL_MISMATCH`, `FAIL_WDS_MISSING`, `FAIL_CAPTURE_MALFORMED`.
