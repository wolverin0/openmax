<!-- doc-head: 829A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# Continuous ground-up finite offline queue

CONFIRMED: finite eight-item offline research/review queue with machine-readable blockers.

| Priority | Task | State |
| ---: | --- | --- |
| 10 | review_static_823_824 | READY_OFFLINE_REVIEW |
| 20 | audit_model_827 | READY_OFFLINE_REVIEW |
| 30 | review_pillar_gaps_828 | READY_OFFLINE_REVIEW |
| 40 | calibrate_from_accepted_rf_traces | BLOCKED |
| 50 | stock_airos_ap_side_interop | BLOCKED |
| 60 | verify_br1_zero_rogue_dhcp | BLOCKED |
| 70 | scholar_reactor_claim_verification | BLOCKED |
| 80 | memorymaster_remote_ingestion | BLOCKED |

Continuous means repeatable explicit rebuild when evidence changes. No daemon, waker or dispatcher exists.
Only local review tasks may become READY_OFFLINE_REVIEW; missing/failed/incompatible evidence blocks them.
Radio, AP migration, DHCP runtime capture, online scholar and remote MemoryMaster ingestion remain blocked.
Priorities order this research queue; they do not authorize operational actions.
