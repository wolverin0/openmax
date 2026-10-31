<!-- doc-head: Stage 1008A offline fail-closed parser for OpenWrt 24.10 mac80211 debugfs aql_txq_limit and aqm text; stdlib only; provenance = operator values + documented format -->
<!-- /doc-head -->
# Stage 1008A: OpenWrt 24.10 AQL/AQM debugfs parser

Offline, stdlib-only. No SSH, no network, no `stat`, no subprocess, no live device.

## Files
- `tools/qca988x/openwrt2410_aqm_aql_busybox_parser.py` parser plus CLI.
- `tools/qca988x/test_openwrt2410_aqm_aql_busybox_parser.py` pytest suite.
- `tools/qca988x/stage1008a_receipt.py` receipt writer with all-NUL self-check (3 retries).
- `artifacts/autoresearch/stage1008a_openwrt2410_aqm_aql_busybox_parser.json` receipt.

## Inputs parsed
`/sys/kernel/debug/ieee80211/phy0/aql_txq_limit`: header `AC<TAB>AQL limit low<TAB>AQL limit high`, then one row per AC, e.g. `VO 300 600`.

`/sys/kernel/debug/ieee80211/phy0/aqm`: header `access name value`, then rows such as `R fq_flows_cnt 4096`, `RW fq_quantum 300`.

## Output
- aql: `{"VO": {"low": 300, "high": 600}, "VI": ..., "BE": ..., "BK": ...}` always in VO, VI, BE, BK order.
- aqm: `{"fq_limit": {"access": "RW", "value": 8192}, ...}`.

## Fail-closed rules
ValueError on: wrong or missing header, unknown AC, missing or extra column, non-decimal numeric,
duplicate AC or key, missing AC row, unknown access flag, missing required aqm key
(`fq_flows_cnt`, `fq_limit`, `fq_quantum`), empty input. Nothing is dropped or guessed.

## Provenance
operator-reported AC values (Stage 929A/953A) + mac80211 debugfs tabular format; no raw debugfs dump stored in repo.

A last grep over `artifacts/autoresearch/firmware_knob_audit_20261024/`, the `lap120_loco195_r1*aql*` captures and
`artifacts/autoresearch/stage955a_live_panel1_three_cpe_readonly_audit.json` found only embedded description strings, not a raw
`aql_txq_limit` dump. The test fixtures are therefore synthetic: operator values VO 300/600, VI 1000/2000, BE 1500/3000, BK 500/1000
in the standard mac80211 layout. They are NOT a literal capture. The aqm fixture uses the documented mac80211 key set with
`fq_flows_cnt 4096`, `fq_limit 8192`, `fq_quantum 300` (values consistent with strings seen in repo captures); the other aqm
counters are 0 placeholders.

## Limits
- The kernel `aqm` file has no per-AC columns; per-AC airtime lives elsewhere and is not parsed here.
- Header strings are matched exactly after whitespace split; a kernel that changes them will be rejected, by design.
- Column layout taken from the standard mac80211 format; no local kernel source cache was inspected.

## Run
- `python -m pytest tools/qca988x/test_openwrt2410_aqm_aql_busybox_parser.py -q`
- `python -m tools.qca988x.stage1008a_receipt`
- `python tools/qca988x/openwrt2410_aqm_aql_busybox_parser.py aql FILE`
