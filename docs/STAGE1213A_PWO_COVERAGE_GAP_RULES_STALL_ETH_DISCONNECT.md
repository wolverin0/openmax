<!-- doc-head: Stage1213A offline recommend-only PWO rules for silent traffic stall, Ethernet speed/CRC flap and CPE disconnect storm with GPS TA drift, mapped to RC-04/10/12/17/18/19 -->
<!-- /doc-head -->

# Stage1213A - PWO coverage-gap rules: stall, Ethernet flap, disconnect storm

Evidence class `PWO_COVERAGE_GAP_RULES`. Offline, `live_devices_touched=false`, status CONFIRMED. Module `tools/uisp/pwo_coverage_gap_rules_stall_eth_disconnect.py`, receipt `artifacts/verification/stage1213a_pwo_coverage_gap_rules.json`, test `tests/test_stage1213a_coverage_gap_rules.py`.

Closes the three PWO coverage gaps named in Stage 1187A Sec5. `.ko` attributions are static RE or model, not live evidence. Every card has `recommend_only=True` and `auto_approve=False`.

## Rules
- `SILENT_TRAFFIC_STALL_WHILE_ASSOCIATED`: associated, RSSI at least -70 dBm, SNR at least 25 dB, and ping loss at least 20 percent or zero TX and RX byte progress. Root causes RC-04 `ubnt_poll_host_sta_bmiss_ind` and RC-10 `ieee80211_send_4addr_nullfunc`.
- `ETHERNET_LINK_SPEED_AND_CRC_FLAP`: speed history dropping to 100 or 10 Mbps, or FCS/CRC delta at least 100. Root cause RC-12 (no `.ko`, PHY/cable/PoE). Disambiguated from RF with `disambiguate()` of Stage 1182A when a `peer_observation` is given, else an RF health check.
- `CPE_DISCONNECT_STORM_AND_GPS_TA_DRIFT`: at least 5 CPE re-associations and at least 30 percent of CPEs. Root causes RC-17 `cpeFsmStop`, RC-18 `AME_SchedCheckActiveCPE`, RC-19 `send_map_enable`. GPS TA drift of 1 us or more is flagged in the evidence.

## API
- `evaluate_rules(telemetry)` returns the cards that fire (possibly none).
- `all_rule_ids()` returns the three ids above.
- `main --write-receipt` writes the receipt with a NUL self-check retried 3 times.

## Boundaries
Thresholds are modelled defaults, not field-calibrated. `whatsappbot-final` is not modified.
