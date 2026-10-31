<!-- doc-head: Stage864A refreshed passive Guarida activity; TDMA slot denominator unverified -->
Read-only observations establish activity, not application capacity or slot efficiency.
<!-- /doc-head -->

# Stage864A: passive audit PARTIAL

Parent: authorized861..866 queue; question: what native evidence supports Guarida
spectral efficiency and TDMA slot usage? Attribution: external controller and
proprietary airMAX component. Application goodput and slot utilization UNKNOWN.

The saved2026-10-27 captures identify Panel2-Guarida .82 and Panel3-Guarida .83,
both LiteAP AC, airOS8.7.25. Current station lists had7 and3 entries respectively.
These are current observations, not proof that historical22/6 rosters disappeared
during this task; no historical-to-current MAC comparison or outage causality exists.

| Observation | Panel2 .82 | Panel3 .83 |
| --- | ---: | ---: |
| Center MHz / configured width MHz |5805 /20|5755 /20|
| Passive bracketing seconds |5.11|5.18|
| AP WLAN RX+TX interface activity Mbps |4.934|2.252|
| Interface activity per MHz, bit/s/Hz |0.2467|0.1126|

Rates use two `mca-status` byte readbacks bracketed by target uptime and unchanged
boot ID, width and center. SSH acquisition overhead is inside the interval.
These are short passive L2 activity proxies, not unique delivered application
bytes, saturated capacity, performance gains or an OTA benchmark.
Native `airTime` fields are retained as observations without assuming their
denominator is occupied TDMA slots. The polling flag alone cannot supply slots.
Missing native slot counters remain missing; no lifetime-counter ratio is invented.

No AirMagic/AirView scan was triggered. No panel setting, power, frequency,
width, station, core, PoE or backbone port was changed. Unsupported read commands
retain their own exits. Wireless-key lines are removed from collected output.

`python tools/autoresearch/run_stage864a_guarida_panel2_panel3_airmagic_and_slot_audit.py --inspect`
performs bounded reads and a5-second passive interval per panel; exit2 records
partial acceptance. Without `--inspect`, it makes no device connection.

Evidence: [receipt](../artifacts/autoresearch/stage864a_guarida_panel2_panel3_airmagic_and_slot_audit.json).
Next: independently decode a native slot denominator and synchronize delivered
application bytes with RF width before accepting spectral/slot efficiency.
