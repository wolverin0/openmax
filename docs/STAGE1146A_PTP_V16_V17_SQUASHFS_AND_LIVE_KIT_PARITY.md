<!-- doc-head: Stage 1146A | parameter parity of SquashFS boot scripts vs v16/v17 live BusyBox kits | honest mismatch table incl. aql_threshold 24000 vs 12000 | offline -->
# Stage 1146A - PTP v16/v17 SquashFS and live kit parity

Tool: `tools/verify/audit_ptp_v16_v17_squashfs_and_live_kit_parity.py`.
Test: `tests/test_stage1146a_ptp_v16_v17_parity.py`.
Receipt: `artifacts/verification/stage1146a_ptp_v16_v17_squashfs_and_live_kit_parity.json`.
Offline static parse; no SSH, no device. `live_devices_touched=false`.

## Compared files

SquashFS boot scripts: `firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-pbe5ac-ptp` and
`firmware/openwrt/common/99-fmx-wa-universal-champion-v17`.
Live kits: `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v16_statless_tcless_busybox_kit.sh` and
`firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh`.

Knobs: `aql_txq_limit` per AC (VO/VI/BE/BK = idx 0..3), `aql_threshold`, `aqm` `fq_limit` / `fq_memory_limit` /
`fq_quantum`, `default_qdisc`, `tcp_notsent_lowat`. Every squashfs x kit pair yields one row per knob with
`{param, squashfs_value, kit_value, match, status}`; status is MATCH, MISMATCH or NOT_COMPARABLE (value absent on a side).

## Honesty rule

Divergences are flagged, never forced to parity. `parity_status` is FULL_PARITY, PARTIAL_PARITY or DIVERGENT;
CONFIRMED means the audit completed, not that parity holds.

## Result

Overall `parity_status`: PARTIAL_PARITY (40 rows: 10 match, 5 mismatch, 25 not comparable).

- `champion_v17` vs `v17_kit`: PARTIAL. All AQL ACs, aqm trio, `default_qdisc`, `tcp_notsent_lowat` match.
  MISMATCH `aql_threshold` 24000 vs 12000, marked `known_open_decision: true` (open decision, not resolved here).
- `champion_v17` vs `v16_kit`: PARTIAL. `default_qdisc` matches; the four AQL rows mismatch (v16 writes a uniform
  `1500 2000` on every AC; champion v17 uses `500 1000`, `1500 3000`, `3000 6000`, `1500 3000`). Real divergence of
  lineages (PtP champion AQL vs WA universal), not flagged as a known decision.
- `99-fmx-pbe5ac-ptp` is a retired legacy stub with no knob writes, so it is DIVERGENT (all rows NOT_COMPARABLE)
  against both kits.
- `tcp_notsent_lowat` in the champion script is applied by `sysctl -w` only on a live host (empty root).

Claim id: `FMX-STAGE1146A-PTP-V16-V17-KIT-PARITY-AUDIT` (not ingested).
