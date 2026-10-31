<!-- doc-head: Stage 1081A CURRENT_STATE Wave 11-12 sync; offline doc sync of Wave 10-12 state (v16/v17 kits, 1075A champion v17 correction, stale SHA256SUMS entry, 1073A/1074A bundler, readiness); read to see what this sync changed -->
<!-- /doc-head -->

# STAGE1081A: CURRENT_STATE Wave 11-12 sync

Status: CONFIRMED, evidence class DOC_SYNC, attribution external controller (offline doc sync), no live device touched.

Edited: `docs/CURRENT_STATE.md` (doc-head updated, section `## Wave 11-12 sync (Stage 1081A, 2026-10-27)` appended; no history deleted).
Receipt: `artifacts/autoresearch/stage1081a_current_state_v17_sync.json`; builder `tools/verify/build_stage1081a_1082a_doc_sync_receipts.py`.

## Synced facts

- Wave 10 (v16 kits): `firmware/openwrt/common/fmx_wa_v16_statless_tcless_busybox_kit.sh` and `firmware/openwrt/common/99-fmx-wa-universal-champion-v16`; v16 kit SHA256 manifests in `docs/STAGE1070A_V16_KIT_SHA256_MANIFESTS.md`, gate in `docs/STAGE1072A_PTP_SIMPY_AND_V16_SHA256_GATE.md`.
- Wave 11 (v17 Pareto kits): `firmware/openwrt/common/fmx_wa_v17_pareto_aqm_aql_busybox_kit.sh` (stat-less, tc-less; 1025A busybox-applet audit 0 findings, `docs/STAGE1052A_V17_KITS_1025A_ZERO_FINDINGS.md`); gate `docs/STAGE1054A_V17_PARETO_KITS_GATE.md`.
- CORRECTION (Stage 1075A): `firmware/openwrt/common/99-fmx-wa-universal-champion-v17` was corrected in Stage 1075A (fail-closed, tc-less; replaced_sha256 `651a64a9...` -> new_sha256 `ea704154...`; full values in `artifacts/autoresearch/stage1075a_champion_v17_fail_closed_upgrade.json`). Audit and restricted-path test: `docs/STAGE1076A_CHAMPION_V17_AUDIT_AND_RESTRICTED_PATH.md`.
- STALE CHECKSUM: the `firmware/openwrt/common/SHA256SUMS` entry for that script is STALE pending Codex #2 re-sign (1075A did not touch any SHA256SUMS). Baked v17 SquashFS images still carry the OLD (buggy) script until re-baked.
- Gatekeeper provenance bundler (Stages 1073A/1074A): `tools/autoresearch/ptp_cohort_provenance_and_gatekeeper_bundler.py` plus self-test `tools/autoresearch/test_ptp_cohort_provenance_bundler_selftest.py`; evidence class SYNTHETIC_SELFTEST. It proves gatekeeper arithmetic and verdict machinery only; it certifies nothing about any radio. Receipts `artifacts/autoresearch/stage1073a_ptp_cohort_provenance_bundler.json` and `artifacts/autoresearch/stage1074a_ptp_cohort_bundler_selftest.json`.
- Readiness matrix (Stage 1077A, `docs/STAGE1077A_PTP_AND_GUARIDA_PREROLLOUT_READINESS_MATRIX.md`): honest state is PowerBeam NOT_READY; LiteBeam NO_EVIDENCE; Panel3 NO_EVIDENCE; Panel2 NOT_READY. No `PRODUCTION_READY` claim; software tests are separate from physical acceptance.
- Scope: offline documentation sync only; no live device touched, no radio measurement added.
