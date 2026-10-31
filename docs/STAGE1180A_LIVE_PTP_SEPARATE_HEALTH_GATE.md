<!-- doc-head: 1180A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# Separate-health live PtP bench and software gate

Gate: BLOCKED_OTA_HEALTH; software: PASS; physical: BLOCKED_OTA_HEALTH.

Tests collected/executed: 219/219; skipped: 0.
This gate executes local tests and replays source-bound receipts; it performs no radio operations.
The snapshot precedes readiness validation, collection and pytest, and must remain identical afterward.
Software acceptance requires every collected test to execute successfully without skips or deselection.
Physical acceptance additionally requires twelve verified v17 lifecycle actions and all eighteen real pairs.
A/A veto, missing windows, missing real counts, source drift or failed independent OTA health blocks acceptance.
Historical source integrity uses preserved archive paths; current acceptance requires the current frozen sources.
The unchanged RegressionGatekeeper retains paired bootstrap/sign-flip/Sidak and measured candidate loss veto.
Ping measures ICMP; interface RX bytes/time measures service, not TCP payload goodput.
A genuine PROMOTE only covers this bench protocol; production acceptance remains UNKNOWN.
