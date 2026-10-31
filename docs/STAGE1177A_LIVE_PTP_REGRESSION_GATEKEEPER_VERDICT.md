<!-- doc-head: 1177A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# Source-bound real RegressionGatekeeper verdict replay

Local verdict replay: BLOCKED_OTA_HEALTH.

Validated windows: {'AA_CONTROL': 12, 'AB_DISCOVERY': 5, 'AB_HOLDOUT': 0}; complete18-pair dataset: False.
A/A actual verdict: INCONCLUSIVE: Temporal baseline drift of 141.7% exceeds 25.0% threshold (gpm drift=141.7%, p99 drift=103.2%).
Discovery: NOT_EVALUATED_INCOMPLETE; holdout: NOT_ACQUIRED.

The actual unchanged RegressionGatekeeper supplies paired bootstrap, sign-flip and Sidak decisions.
Three complete six-pair cohorts and independent source/hash/session/time bindings are required.
Loaded probe loss remains its observed value, including partial replies with ping exit0.
A/A may reject or remain inconclusive on QoE; that is not a substitute for a separate link-alive guard.
A/A admission requires all twelve true losses zero, positive service, full-range p99/service drift at most25 percent, and the healthy null decision.
Candidate loss veto and all statistical thresholds remain unchanged; PROMOTE is never forced.
The current baseline-health loss veto may still yield INCONCLUSIVE after collection is unblocked.
Missing fresh Stage1176 data produces BLOCKED, not imported historical or synthetic certification.
Finalized partial cohorts retain every source-bound row; incomplete phases have no invented statistical decision.
Independent OTA health failure blocks promotion even when loaded ICMP replies or earlier windows were valid.
No collector import, SSH, device operation or deployment occurs in this replay builder.
