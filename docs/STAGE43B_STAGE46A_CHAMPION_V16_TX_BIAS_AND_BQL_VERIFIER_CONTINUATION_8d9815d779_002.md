<!-- doc-head: STAGE43B_STAGE46A_CHAMPION_V16_TX_BIAS_AND_BQL_VERIFIER.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE43B_STAGE46A_CHAMPION_V16_TX_BIAS_AND_BQL_VERIFIER.md) | Part 2/2
<a id="stage43b-stage46a-champion-v16-tx-bias-and-bql-verifier"></a> [Stage43B Stage46A Champion v16 TX bias and BQL verifier](STAGE43B_STAGE46A_CHAMPION_V16_TX_BIAS_AND_BQL_VERIFIER_CONTINUATION_8d9815d779_001.md#stage43b-stage46a-champion-v16-tx-bias-and-bql-verifier) | <a id="result-source-promotion-retained-research-evidence-inconsistent"></a> [Result: source promotion retained, research evidence inconsistent](STAGE43B_STAGE46A_CHAMPION_V16_TX_BIAS_AND_BQL_VERIFIER_CONTINUATION_8d9815d779_001.md#result-source-promotion-retained-research-evidence-inconsistent) | <a id="why-r3-differs-from-stage44a-r3r4"></a> [Why R3 differs from Stage44A R3/R4](STAGE43B_STAGE46A_CHAMPION_V16_TX_BIAS_AND_BQL_VERIFIER_CONTINUATION_8d9815d779_001.md#why-r3-differs-from-stage44a-r3r4) | <a id="exact-linux66110-mechanism"></a> [Exact Linux6.6.110 mechanism](STAGE43B_STAGE46A_CHAMPION_V16_TX_BIAS_AND_BQL_VERIFIER_CONTINUATION_8d9815d779_001.md#exact-linux66110-mechanism) | <a id="dynamic-dqlbql-versus-a-default-static-clamp"></a> [Dynamic DQL/BQL versus a default static clamp](STAGE43B_STAGE46A_CHAMPION_V16_TX_BIAS_AND_BQL_VERIFIER_CONTINUATION_8d9815d779_001.md#dynamic-dqlbql-versus-a-default-static-clamp) | <a id="endpoint-budget-policy-and-remaining-getter-gaps"></a> [Endpoint budget policy and remaining getter gaps](STAGE43B_STAGE46A_CHAMPION_V16_TX_BIAS_AND_BQL_VERIFIER_CONTINUATION_8d9815d779_001.md#endpoint-budget-policy-and-remaining-getter-gaps)

<!-- stage822a-payload-begin -->
These class labels and ceilings encode the task's supplied bench policy.
They are not authenticated CPU probes or a universal hardware limit.
`verify_cpu_budget_ceiling` requires four explicit unique identities/classes
and positive integer budgets at or below those policy ceilings; unknown class,
missing endpoint or M5 budget600 fails. The champion-profile guard separately
requires the exact default600/300 values. Generic netdev_budget is a per-CPU
NET_RX cycle packet/time budget, as described in
[Linux sysctl net documentation](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/Documentation/admin-guide/sysctl/net.rst).
CPU frequency alone does not define an inherent600/300 ceiling.

R6 raises M5 budget600 under declared dynamic BQL and reports GP+3.487%,
p95+8.839%, IPTV jitter+66.230% and voice jitter+12.728%. That supports retaining
300 within this policy, without proving an AR934x-wide causal law. R2's current
helper and R6's helper both avoid iwpriv protmode; R6 text's historical assertion
that R2 reset the VAP cannot be verified from this source revision. More
importantly, the helper's exception path fabricates expected-looking readbacks.
A matching saved M5 dictionary therefore does not exclude collection failure.

The supplied v16 guard checks AP/CPE queues, full available NAPI/TCP sysctls,
FQ/AP-AQL, Rocket queues/budget/multicast vector and M5 queue/budget/vector fields.
OpenWrt eth0 remains1000; br-lan/WiFi/declared AP_VLAN children256; Rocket
br0/ath0/eth0256 and budget600; M5 queues256 and budget300. Loopback/br-wan
values stay separate. Dynamic interfaces must be explicitly inventoried.
NAPI defer/GRO fields are absent here and remain UNKNOWN; no zeros are invented.
Complete CPE AQL/threshold, empty station-airtime getters, driver/build/CPU
identity and same-window freshness remain unqualified. Matching supplied
profile fields never accepts the whole native champion.

## Software verification and stop boundary

All requested behavior is pure local parsing, arithmetic and supplied-policy
validation. The source disagreements are research findings, not failing unit
tests to hide or data to repair. Fresh final focused pytest: **248 passed in
1.00s, exit0**, with identical module hashes before/after. Run1 retained245PASS/
1FAIL from a test expectation based on the declared8000us rather than the
pinned20000us getter. That fixture assumption was corrected without modifying
source data. Run2 retained248PASS; run3 binds the final comparison metadata
assertions and raw-jitter-overflow/uint64 regressions to the frozen module.
Independent review identified the raw-jitter nonfinite parser gap, repaired
before final acceptance. All earlier results remain in validation; no unchanged
failed experiment was retried or research criterion relaxed.
Focused test receipts, implementation/source
hashes and independent review are retained in validation. Existing physical
bench tests and scripts are not imported or run. Final software counts and the
frozen review govern closure; native/physical acceptance remains UNKNOWN,
E2 NOT_ACCEPTED. No physical operator action is required for this offline task,
and no new experiment or next task is started.
<!-- stage822a-payload-end -->
