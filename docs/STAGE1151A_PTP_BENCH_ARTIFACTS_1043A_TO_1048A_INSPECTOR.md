<!-- doc-head: 1151A offline inspector of 1043A-1048A PBE5AC PtP bench receipts, cohort completeness -->
<!-- /doc-head -->

# Stage 1151A PTP bench artifacts 1043A-1048A inspector

Offline, no SSH, no device. It inspects receipt files written by other lanes and reports their declared state verbatim.

## Files
- Tool: `tools/verify/verify_stage1043a_to_1048a_ptp_bench_artifacts.py`
- Receipt: `artifacts/verification/stage1151a_ptp_bench_artifacts_1043a_to_1048a_inspector.json`
- Tests: `tests/test_stage1151a_ptp_bench_artifacts_inspector.py` (SYNTHETIC tmp fixtures only)

## What is inspected
- `stage1043a..1048a` JSON in `artifacts/verification/`, `artifacts/autoresearch/`, `artifacts/benchmarks/` and `docs/STAGE1043A*.md` to `STAGE1048A*.md`.
- A missing `artifacts/benchmarks/` is reported as `benchmarks_dir_present: false`, never an error.
- Per stage: doc presence, receipt presence and path, the receipt own `status`, evidence class, live class, and a summary of recorded SSH actions, bench guard checks, A/A windows and failed gate checks.
- A `stage{N}a/` directory receipt (for example `aborted_campaign_receipt.json`) is listed under `supplementary_receipts` and does not count as the stage receipt.

## Honesty boundary
- Own receipt: `live_devices_touched: false`, `evidence_class: PTP_BENCH_ARTIFACT_INSPECTION`.
- `status: CONFIRMED` means the inspection completed, not that the cohort is complete. See `cohort_status`.
- Absent receipts are `receipt_present: false`; nothing is inferred or upgraded.

## Result on the real repo
- `cohort_status: INCOMPLETE`, 2 of 6 receipts present.
- Present: 1043A (`CONFIRMED_LIVE_HARDWARE`, two hosts, dry-run/apply/verify/rollback exit 0) and 1048A (`BLOCKED`, `CONFIRMED_STATIC_BINARY`).
- Missing: 1044A, 1045A, 1046A, 1047A. 1044A only has a supplementary `ABORTED_AA_LOSS` campaign receipt.

## Run
- `python tools/verify/verify_stage1043a_to_1048a_ptp_bench_artifacts.py`
- `python -m pytest -q tests/test_stage1151a_ptp_bench_artifacts_inspector.py`
