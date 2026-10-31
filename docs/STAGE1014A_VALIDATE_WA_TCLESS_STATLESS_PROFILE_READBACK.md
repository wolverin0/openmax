<!-- doc-head: STAGE1014A WA champion profile tc-less/stat-less readback validator, offline, fail-closed -->
<!-- /doc-head -->

# Stage 1014A: WA tc-less, stat-less profile readback validator

Offline validator for REAL device readback text of the WA champion profile. It never
touches a device and never uses `stat` or `tc`.

## Files

- Module: `tools/qca988x/validate_wa_tcless_statless_profile_readback.py`
- Tests: `tools/qca988x/test_validate_wa_tcless_statless_profile_readback.py`
- Receipt writer: `tools/qca988x/stage1014a_receipt.py`
- Receipt: `artifacts/autoresearch/stage1014a_validate_wa_tcless_statless_profile_readback.json`
- Reused parser (Stage 1008A): `tools/qca988x/openwrt2410_aqm_aql_busybox_parser.py`

## Three readbacks (only these)

1. `/proc/sys/net/core/default_qdisc` (expect `fq_codel`)
2. phy-level `aqm` key/value rows (same format Stage 1008A parses)
3. phy-level `aql_txq_limit` (AC rows VO/VI/BE/BK)

## API

- `readback_commands(phy="phy0") -> list[str]`: three read-only `cat` strings. The phy name
  is a parameter because it renumbers (phy1/2/3) after a mac80211 module reload.
- `validate_readback(aql_text, aqm_text, default_qdisc_text, expected=None)` returns
  `{"ok", "profile_state", "checks", "failures", "provenance", "scope_limit"}`.

## Expected values

AQL low/high: VO 300/600, VI 1000/2000, BE 1500/3000, BK 500/1000; default_qdisc `fq_codel`.
Provenance: operator-reported champion values (Stage 929A/953A) + 140A/153A description
strings. The live lane may pass its own `expected` dict (keys `aql`, `default_qdisc`).

## profile_state

- `CHAMPION_APPLIED`: ok True, everything matches.
- `STOCK_NOT_APPLIED`: AQL is mac80211 stock 5000/12000 on every AC (not "malformed").
- `PROFILE_MISMATCH`: anything else that differs (AQL values or default_qdisc).
- Malformed aql/aqm text raises `ValueError` (fail-closed, never a silent pass).

## Scope limit

Without `tc`, the netdev-level fq_codel `quantum/target/interval` (set by the v14/v15 kits
via `tc qdisc replace`) are NOT readable: there is no sysfs mirror. The per-netdev
`netdev:wlanX/aqm` per-AC table is a different file and out of scope; do not feed it to
`parse_aqm`. The validator covers exactly the three readbacks above.

## Run

- `python -m pytest tools/qca988x/test_validate_wa_tcless_statless_profile_readback.py`
- `python -m tools.qca988x.stage1014a_receipt`
