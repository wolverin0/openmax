<!-- doc-head: 1073A offline PtP cohort provenance bundler for the regression gatekeeper -->
<!-- /doc-head -->

# Stage 1073A: PtP cohort provenance and gatekeeper bundler

Scope: `SYNTHETIC_SELFTEST`. Offline, pure stdlib, no SSH, no device. It proves nothing about any radio.

Module: `tools/autoresearch/ptp_cohort_provenance_and_gatekeeper_bundler.py`.
Receipt: `artifacts/autoresearch/stage1073a_ptp_cohort_provenance_bundler.json`.

## What it does

Takes raw `uclient-fetch` stderr and `ping` output from a PowerBeam .241/.242 PtP window and writes
hash-bound per-window JSON receipts plus a `replication_receipt.json`, shaped to satisfy
`analysis.regression_gate.gatekeeper.validate_run_provenance` and `validate_holdout_evidence`.
`analysis/regression_gate/gatekeeper.py` is imported, never edited.

## Public API

- `build_window_receipt(raw_fetch_text, raw_ping_text, *, run_id, arm, block_index, is_sentinel, session_id, peer_id, window_start_s, window_end_s, channel_width_mhz, applied_config_readback, evidence_root, evidence_state)`
  writes `windows/<run_id>.json` under `evidence_root` and returns the bound `RunMetrics`.
- `build_replication_receipt(discovery, holdout, candidate_fingerprint, frozen_plan, evidence_root, path)`
  writes a `BENCH_REPLICATED` receipt binding `[{run_id, raw_sha256}]` for both datasets.

Optional keywords: `firmware_resets` (default 0) and `extra_fields` (merged top-level, cannot override contract keys).

## Derivation rules (parsed, never supplied)

- Bytes: one `Download completed (N bytes)` line. Duration: `elapsed=X s` / `in X sec`, else a `H:MM:SS` token.
- `goodput_mbps = receiver_bytes*8/duration/1e6`; the parsed duration must be within 1% of the window length.
- Ping: summary `N packets transmitted, M packets received`; one `time=X ms` per reply, count must equal received.
- `p95`/`p99`: nearest rank, `ordered[ceil(f*received)-1]`. `loss_pct = 100*(sent-received)/sent`.
- Single-peer PtP: `jain_fairness=1.0`, `worst_peer_goodput_mbps=goodput`, `expected_peers=[peer_id]`.
- `applied_config_sha256` is the sha256 of the canonical JSON of `applied_config_readback`.
- `raw_sha256` is the sha256 of the exact receipt bytes on disk; writes are NUL-checked (3 tries).

## Fail-closed behaviour

Missing or duplicate byte/summary lines, latency count mismatch, duration/window mismatch, a readback
width that differs from `channel_width_mhz`, an unsafe `run_id`, a frozen plan created at or after the first
discovery window, or a candidate outside the frozen family all raise `ValueError`.

## Limits

It binds and arithmetic-checks bytes. It cannot prove an instrument was honest or that the device ran the
configuration. Multi-peer fairness needs per-peer fetches (not implemented).
Verification lives in Stage 1074A: `docs/STAGE1074A_PTP_COHORT_BUNDLER_SELFTEST.md`.
Any KEEP or PROMOTE verdict produced from fixtures is on isolated synthetic data, never physical promotion.
