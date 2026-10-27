<!-- doc-head: 773A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# WA v13 identity-bound transient queue kit

Default/inspect/dry-run returns PLANNED without getters or writes.
Explicit --apply requires --identity FILE and --state-dir ABSOLUTE_DIRECTORY.
Identity is eleven unique key=value records: ten exact getter fields and their SHA256 fingerprint.
Fingerprint input is the ten fields in receipt order, one UTF-8 value per line with final newline.
board_revision must be exposed by ubus system board; unavailable revision means refusal.
Snapshots cover four AQL ACs, pktlog_filter, BQL limit_max, complete supported root fq_codel
configuration/handle and all three sysctls. Unknown options, child qdiscs or auto handle0 refuse apply.
The qdisc remains fq_codel, with supported quantum/target/interval options; no switch to fq.
Errors trigger restoration/readback: FAILED_ROLLED_BACK or ROLLBACK_FAILED, never decorative success.
--rollback with the same identity/state-dir restores the retained snapshot idempotently.
No DHCP/UCI/service persistence, firmware patch loader or device access occurs during packaging.
344 windows,78.51/76.55Mbps and86.37% loaded-p50 reduction are imported historical claims only.
Actual radio behavior and runtime acceptance remain UNKNOWN.
