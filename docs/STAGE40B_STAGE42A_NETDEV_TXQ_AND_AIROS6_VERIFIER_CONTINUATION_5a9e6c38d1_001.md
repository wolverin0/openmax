<!-- doc-head: STAGE40B_STAGE42A_NETDEV_TXQ_AND_AIROS6_VERIFIER.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

[Document router](STAGE40B_STAGE42A_NETDEV_TXQ_AND_AIROS6_VERIFIER.md) | Part 1/2
<a id="ltu-busybox-and-binary-patch-semantics"></a> [LTU BusyBox and binary-patch semantics](STAGE40B_STAGE42A_NETDEV_TXQ_AND_AIROS6_VERIFIER_CONTINUATION_5a9e6c38d1_002.md#ltu-busybox-and-binary-patch-semantics) | <a id="api-checks-and-completion"></a> [API, checks and completion](STAGE40B_STAGE42A_NETDEV_TXQ_AND_AIROS6_VERIFIER_CONTINUATION_5a9e6c38d1_002.md#api-checks-and-completion)

<!-- stage822a-payload-begin -->

Audits four requested Stage42A and two Stage40A rounds,24 reported A1/B1/A2/B2 windows.
R1/R2 Stage42A queue getters remain1000; R2 lacks the M5 peer and is not a sysfs64 trial.
Stage40A separates route uncertainty, raw-ping fields, composite latency and weighted goodput.
LTU splice arithmetic is conditional; emitter/build/deployed-binary proof remains UNKNOWN.
Focused fixtures78PASS,exit0; preserved failures and independent-review disposition in validation.
No hardware SSH, radio/service/script/patch/flash execution or new physical acceptance.


# Stage40B: Stage42A netdev TXQ and airOS6 evidence verifier

Task `T-S40B-CODEX-STAGE42A-AIROS6-UNPOLLED-AND-NETDEV-TXQ-STARVATION-VERIFIER`
supports the original forward-plan external-controller control-authority and
reproducible-experiment deliverables. The fixed contract is in
[BENCH_PLAN.md](BENCH_PLAN.md). The question is what the saved observations
establish, without accessing hardware or executing a saved recipe.

Implemented [verifier](../controller/stage42a_netdev_txq_and_airos6_verifier.py)
and [unit tests](../tests/test_stage40b_stage42a_verifier.py) use standard-library
data processing, literal AST inspection and disposable fixtures. Neither the
deployer nor either bench runner is imported or executed. Existing accepted
verifiers and live operational scripts are unchanged.

## Inputs, authentication and scope

Requested inputs:

- [Stage42A JSON](../artifacts/autoresearch/stage42a_m24_m25_airos6_mcast_and_txq_bench_20261025.json),
  whose `rounds` is a list. Canonical S42A-R1..R4 hashes bind16 saved windows.
- [Stage40A JSON](../artifacts/autoresearch/stage40a_ltu_persistent_poststart_and_24ghz_bench_20261025.json),
  whose `rounds` is a dictionary. Canonical S40A-R1/R2 hashes bind8 windows;
  the LTU persistent-poststart receipt has its own canonical binding.

Narrow supporting sources are the Stage42A runner, Stage40A runner,
[Stage40A report](STAGE40A_LTU_PERSISTENT_POSTSTART_AND_24GHZ_TRIPLE_PLAY_BENCHMARK.md)
and the deployer's two literal poststart strings. Their observed file hashes,
the six round hashes and test/review history are recorded in
[validation](../artifacts/autoresearch/stage40b_stage42a_validation_20261025.json).

The Stage42A file was appended with R5 during this task. The requested four
rounds did not change. Extra rounds are listed as `unassessed_round_ids`;
they neither replace the requested cohort nor silently enter its conclusions.
The initial whole-file SHA256 was
`1bcf67852c67c90e971c1d274f17a169edd7ac7321f98e5160ba5205d5803c3e`;
a later observed whole-file SHA256 after R5 was
`73dbcd4ac6a68875d9d3ebeb14cf040218d82e34e1434717ad89d4e569011d25`.
Canonical round hashes, rather than the mutable file envelope, govern scope.

The source calls A1/B1/A2/B2 counterbalanced. These are four saved phase
aggregates, with two observations per arm, not24 independent pairs, randomized
order, a pooled latency distribution or a causal confidence interval. Saved
decision labels and successful ingestion are distinct from physical acceptance.

## Stage42A: actual getters and results

| Round | Attempt and saved effective AP/Loco queue lengths | Goodput A to B, Mbps | Delta | Mean phase p95 delta | Qualification |
| --- | --- | --- | --- | --- | --- |
| R1 | ip-link attempt128; every saved queue remains1000 | 44.523 to40.807 | -8.346% | -11.684% | Compound M5 poll/br0, backlog and early-retrans treatment; queue change not observed. |
| R2 | ip-link attempt256; every saved queue remains1000 | 45.703 to45.062 | -1.403% | -6.524% | M5 has zero goodput/ping count, no effective airtime entry and empty M5 state throughout. |
| R3 | Direct sysfs128 observed on AP and Loco | 43.682 to43.835 | +0.350% | +2.378% | Backlog2000 and early-retrans4 accompany the queue change. |
| R4 | Direct sysfs256 observed on AP and Loco | 45.254 to43.895 | -3.003% | +29.472% | Backlog2000 accompanies the queue change; early-retrans stays3. |

The consigna's R1 -8.352% and R2 sysfs64/-4.535% do not match these requested
source objects. No sysfs64 experiment is present in their four rounds. R1's
saved target poll vector is `txop_params="15 5"`, `no_ack_rate="1 -1"`,
`no_auto_prio=1`, versus `"0 0"`, `"0 -1"`,0 in its controls. Its target IPTV
loss is13/5690 datagrams (saved mean phase percentage0.2285%); voice is0/1198.
Those compound results do not isolate the poll controls as the cause of the
goodput penalty. The runner's BusyBox ip-link parser-error explanation is a
source report; unchanged queue getters establish non-effect, not the exact
parser failure by themselves.

R2 is not a qualified three-CPE comparison: M5 is absent in every saved window.
Its per-peer weight256 is a fallback/default-like field, not an effective
128 readback; the AP's actual airtime map omits the M5 MAC. The runner reports
an expired guard, but there is no native event timeline proving that cause.
Counting three peer records or reusing their labels cannot repair this gap.

R3 voice loss is26/1199 in A and26/1200 in B. Saved mean phase percentages are
2.1685% and2.1666%, respectively. The roughly2.17% target loss already exists
in controls and must not be attributed wholly to128. R3 target IPTV loses5/5694
(mean phase0.0877%). R4 IPTV is0/5685; voice is7/1199 (mean phase0.5839%).
Percentages averaged across phases are kept separate from ratios of total
lost/total datagrams. Zero IPTV loss does not establish zero voice loss.

All four saved decisions are `RETAIN_CURRENT_CHAMPION`, with no promoted
candidate. **V13 is retained within these four decisions.** This establishes
neither a universal queue-starvation law nor that1000 is globally optimal or
that a current live three-CPE sector is accepted. The varying baselines and
R2's missing M5 prevent a clean cross-round queue-only comparison.

## Netdev, mac80211 and airOS6 boundaries

The OpenWrt controls save AP `br-lan`, `phy0-ap0` and two dynamic AP_VLAN names,
and Loco `br-lan`/`phy0-sta0`, at1000. Interface names must be captured, not
filled from a fixed `.sta1` assumption. The raw parser binds an explicit
inventory to `/sys/class/net/<name>/tx_queue_len` headers and rejects duplicate,
missing, extra, malformed or out-of-range entries. Zero is parseable as a
kernel queue value; it does not match the observed1000 baseline.

Netdev `tx_queue_len` is a device parameter, separate from mac80211 FQ/AQL
and QCA firmware queues. Linux6.6.110 exposes it through a dedicated sysfs
attribute/setter; a saved sysfs value does not establish actual occupancy or
lower-layer scheduling causality. See the primary
[netdev sysfs implementation](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/net/core/net-sysfs.c).

The audit checks the available v13 fields: AP/Loco quantum4542/1514,
memory4194304, fq_limit2048/1024, flows4096, TCP notsent8192/output98304/
CA105/SS140 and AP AQL VO300/600,VI1200/2400,BE1500/3000,BK500/1000,threshold5000.
If supplied, CPE AQL must be VO300/600,VI1200/2400,BE900/1500,BK500/1000 and
threshold4000. Present-but-invalid values fail the available-field check;
missing CPE AQL fields remain explicit gaps. Integers are typed, so300.0 or
boolean values do not become valid readbacks through Python equality.

These historical getters do not provide full native qualification: CPE AQL
is missing, child airtime readbacks are absent, and there are no bound module/
boot/netns/ifindex epochs, native flow traces or post-window stability records.
In the current R3/R4 runner, AP/Loco getters are acquired before each load
window. M5 state is cached from setup and may come from an early-return constant
dictionary; it is not reacquired for each window. `unpolled_compatible=True`
therefore means only that supplied coordinates match the clean vector;
`polling_mode_independently_proven` remains false. The three-peer completeness
flag checks saved positive indicators, not native identity authentication.

The runner describes airOS6 XW.v6.3.22/Linux2.6.32.68 as lacking bridge snooping
paths. Saved R1 `multicast_fast_leave`/querier strings are empty; there is no
exact vendor kernel config or qualified ENOENT capture in the requested JSON.
Consequently CONFIG_BRIDGE_IGMP_SNOOPING is **UNKNOWN**, not confirmed disabled
by these empty strings. Upstream2.6.32's bridge Kconfig itself does not expose
that option, and the vendor may differ. See the primary
[Linux2.6.32 bridge Kconfig](https://raw.githubusercontent.com/gregkh/linux/v2.6.32/net/bridge/Kconfig).
The optional configuration parser only classifies explicit `=y` or
`# ... is not set`; duplicate/unsupported stanzas fail. Its classification
still does not authenticate an exact vendor build.

## Stage40A: route and metric audit

| Saved metric | R1 A to B | R2 A to B |
| --- | --- | --- |
| Bulk TCP, Mbps | 95.084 to90.7805 (-4.526%) | 33.5785 to28.1575 (-16.144%) |
| QoE-weighted goodput, Mbps | 94.437 to90.409 (-4.265%) | 34.6065 to30.070 (-13.109%) |
| Physical aggregate field, Mbps | 97.357 to93.0535 | 35.859 to30.434 |
| Loaded-ping p95 field, ms | 9.9125 to7.6145 (-23.183%) | 15.572 to7.724 (-50.398%) |
| Composite p95 field, ms | 11.5415 to9.1465 (-20.751%) | 32.7325 to37.425 (+14.336%) |
| Decision | RETAIN_CURRENT_CHAMPION | RETAIN_CURRENT_CHAMPION |

R1 is labelled Rocket2AC/NanoM2 at2.4GHz, but the current runner sends bulk,
IPTV and voice to `LTU2_IPV4=198.18.0.118`. Its ping stream combines NanoM2
and LTU destinations. The requested records do not qualify a load path confined
to the2.4GHz RF link. R2 uses LTU at5500MHz, not a second Rocket2AC trial.
Route/interface captures would be needed before asserting RF-path causality.

For R1, composite p95 equals the loaded-ping field plus1.5 times the sum of
IPTV/voice jitter. R2 uses0.4 times a separate AMES p95 plus0.6 times loaded
ping, plus the same jitter term. QoE goodput multiplies aggregate goodput by
<!-- stage822a-payload-end -->
