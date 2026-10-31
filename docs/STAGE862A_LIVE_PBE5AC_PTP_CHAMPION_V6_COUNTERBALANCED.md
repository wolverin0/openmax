<!-- doc-head: Stage862A three-round benchmark contract withheld without verified v5/v6 treatments -->
Twelve windows are planned; zero windows executed.
<!-- /doc-head -->

# Stage862A: benchmark BLOCKED

Parent: the authorized861..866 FMX-0011 bench queue.
Question: does Quad-Patch v6 improve v5 under matched OTA Triple-Play load?
Result: UNKNOWN, NOT_ACCEPTED; Stage806A supplied no PB070 binary.
Attribution: external controller and QCA firmware.

The script records three rounds of A1,B1,A2,B2 with v5 as A and v6 as B.
These are planned records, each explicitly NOT_EXECUTED. All throughput,
latency, IPTV loss, VoIP jitter and gain fields remain null.
Fixed ABAB order is not randomized; future analysis must account for time drift.

`python tools/autoresearch/run_stage862a_live_pbe5ac_ptp_champion_v6_counterbalanced.py --execute`
returns2 and records the blocker; it generates no traffic and changes no radio.
This is an acquisition contract/prerequisite gate, not a completed live runner.

Required evidence before execution: exact v5/v6 native hashes and patch bytes,
verified OTA path without management-switch bypass, identical bandwidth/center/
power/load/duration, concurrent bulk TCP+IPTV+VoIP receiver measurements,
raw exits and radio deltas, boot epochs, a45-second watchdog and exact restore.
Sequential DL/UL transfer sums cannot substitute for simultaneous load.
Unit tests validate refusal and evidence shape; they cannot prove a wireless gain.

Evidence: [receipt](../artifacts/autoresearch/stage862a_live_pbe5ac_ptp_champion_v6_counterbalanced.json).
Next: resolve861's native PB070 and baseline identity before acquiring windows.
