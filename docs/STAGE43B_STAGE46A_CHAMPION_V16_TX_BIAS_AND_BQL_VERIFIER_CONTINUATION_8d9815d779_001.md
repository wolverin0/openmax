<!-- doc-head: STAGE43B_STAGE46A_CHAMPION_V16_TX_BIAS_AND_BQL_VERIFIER.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE43B_STAGE46A_CHAMPION_V16_TX_BIAS_AND_BQL_VERIFIER.md) | Part 1/2
<a id="software-verification-and-stop-boundary"></a> [Software verification and stop boundary](STAGE43B_STAGE46A_CHAMPION_V16_TX_BIAS_AND_BQL_VERIFIER_CONTINUATION_8d9815d779_002.md#software-verification-and-stop-boundary)

<!-- stage822a-payload-begin -->

All6 Stage46A rounds24 windows and48 UDP observations are bound and audited offline.
Typed GP/RTT/jitter/Pareto reproduce;32 raw-jitter and22 loss/count disagreements remain.
Reported v16 promotion is preserved without independent native/QoE acceptance.
Linux TX bias scales qdisc packet quota, not the driver's ath10k NAPI weight directly.
Dynamic BQL/default endpoint budgets are guarded as this bench policy, not universal CPU law.
No SSH, hardware, target/config execution; physical UNKNOWN, E2 NOT_ACCEPTED.


# Stage43B Stage46A Champion v16 TX bias and BQL verifier

Task `T-S43B-CODEX-STAGE46A-CHAMPION-V16-TX-BIAS-2-AND-BQL-TRADEOFF-VERIFIER`.
Parent: external-controller control authority and reproducible experiment
methodology in the [original forward plan](../artifacts/2026-09-20-forward-plan.html)
and [fixed Stage43B contract](BENCH_PLAN.md). Work is entirely offline; no native
runner imports, SSH, radio, WSL, configuration, module, script or flash action.

[Verifier](../controller/stage46a_champion_v16_tx_bias_and_bql_verifier.py),
[focused tests](../tests/test_stage43b_stage46a_champion_v16_verifier.py),
[validation](../artifacts/autoresearch/stage43b_validation_20261025.json).
Complete Stage46A JSON, all6 round objects, exact report bytes and complete
Stage44A JSON are pinned. Integrity means identity of saved objects; it does
not authenticate acquisition, command exit status, build or native behavior.

## Result: source promotion retained, research evidence inconsistent

All A1/B1/A2/B2 phases are audited:24 windows and48 IPTV/voice observations.
Recomputed means use the source's three-decimal phase-aggregate convention.
Pareto is GP percent delta minus0.35 times p95 percent delta before percentage
rounding. It is an optimizer score, not a separate physical measurement.

| Saved round | GP change | p95 change | Pareto | Saved decision |
| --- | ---: | ---: | ---: | --- |
| R1 min3028/max24576/hold500 BQL | -0.977% | -5.597% | +0.9823 | retain |
| R2 M5 budget600 | -0.104% | -4.890% | +1.6077 | retain |
| R3 pure TX bias2/full budget600 | +3.489% | -6.291% | +5.6906 | promote v16 |
| R4 combined BQL/M5 budget/TX bias | -1.121% | -10.912% | +2.6979 | retain |
| R5 min4542/max65536/hold1000 BQL | -10.267% | +4.448% | -11.8242 | retain |
| R6 non-disruptive M5 budget600 | +3.487% | +8.839% | +0.3931 | retain |

Within typed phase fields, R3 reproduces39.642→41.025Mbps, p95
90.986→85.262ms, p99 95.257→89.434ms (-6.113%), IPTV jitter2.412→1.985ms
(-17.703%) and voice jitter2.689→2.549ms (-5.206%). R3 B1/B2 scalar getters
match the supplied v16 policy. These facts do not resolve the following conflicts.

The verifier finds **54 UDP layer disagreements**:32 jitter comparisons and22
typed percentage-versus-count comparisons, all in R1..R4. R5/R6 UDP fields and
receiver lines agree under the saved rounding precision. The original values
and lines are retained; no source corrections or preferred-layer substitution
are made. Tests must detect these findings, not declare the research data clean.

| Example | Typed/source claim | Saved counter/receiver evidence |
| --- | --- | --- |
| R1 IPTV jitter change | -70.136% | raw-line rounded arm means imply +31.008% |
| R3 B1 voice loss | 0.5% | typed counts and raw receiver both0/600 |
| R3 B2 IPTV loss | 0.2105% | typed counts and raw receiver both14/2847, about0.492% |
| R4 B1 IPTV loss | 0% | typed counts and raw receiver both92/2846, about3.23% |

R3 typed/raw IPTV jitter deltas are-17.703%/-36.452%; voice deltas are
-5.206%/-24.277%. These are alternative saved layers, not independent
replications. Pooled R3 counts are IPTV A48/5691 versus B14/5694 and voice
A1/1200 versus B0/1200. Typed mean voice percentages instead claim0.5009%
versus0.5834%. Counts agree with raw receiver count text, but this does not
authenticate their capture epoch or establish that the raw lines are definitive.

The original report also has different R3 per-window RTT/jitter values from the
current JSON. Its opening Stage44A v15 values (+5.342% GP/-3.516% p95) differ
from the pinned Stage44A R5 (+7.140%/-3.618%). R5/R6 hypothesis text mentions
earlier R1 p95+11.37% and R2 p95+17.90%, whereas current typed results are
-5.597% and-4.890%. These provenance disagreements are preserved; no historical
execution revision is reconstructed from labels alone.

Disposition: **INCONSISTENT_SAVED_EVIDENCE**. Source-reported promotion remains
visible, but native_promotion_accepted=false and raw_qoe_qualified=false.

## Why R3 differs from Stage44A R3/R4

| Treatment | OpenWrt TX bias | weight | budget / time | eth0 queue |
| --- | ---: | ---: | --- | ---: |
| S44A-R3 saved getter | 2 | 48 | 300 /20000us | 1000 |
| S44A-R4 saved getter | 2 | 64 | 600 /20000us | 256 |
| S46A-R3 | 2 | 64 | 600 /20000us | 1000 |

Pinned Stage44A R3 GP-1.416% and R4 GP-34.137% concern different compound
treatments. Stage44A R3/R4 declare8000/12000us, but both B1/B2 AP/CPE saved
getters show20000us. The declared time-slice changes are not verified; the
comparison preserves this mismatch explicitly. Stage46A R3 changes the supplied
TX-bias scalar while retaining full packet/time budgets, default BQL bounds
and eth0=1000. It avoids the declared compound changes, without proving the
historical application of every knob. Changing baselines, missing
timing/build traces and contradictory QoE layers prevent an isolated cross-round
causal explanation. No Ethernet ingress-tail-drop or firmware queue mechanism
can be inferred from tx_queue_len alone.

### Exact Linux6.6.110 mechanism

[sysctl_net_core.c](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/net/core/sysctl_net_core.c)
updates dev_tx_weight as dev_weight times dev_weight_tx_bias. At64×2 this is128.
[sch_generic.c](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/net/sched/sch_generic.c)
uses that value as a software qdisc dequeue packet quota. That multiplication
is CONFIRMED for the cited source, not for an identified running binary.

The statement "128 ath10k HTT completions per NAPI poll" is **REFUTED for this
upstream mechanism**. Driver poll budget comes from the NAPI instance's own
weight in [dev.c](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/net/core/dev.c).
[netdevice.h](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/include/linux/netdevice.h)
gives ordinary netif_napi_add its default64; the
[ath10k PCI path](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/drivers/net/wireless/ath/ath10k/pci.c)
registers that NAPI and passes the poll budget to HTT. The
[HTT completion implementation](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/drivers/net/wireless/ath/ath10k/htt_rx.c)
budgets RX delivery and accounts for pending TX-done FIFO work; it does not
turn the sysctl product into an ath10k completion count. Actual modified
driver/firmware behavior, AQL-credit timing and benefit remain UNKNOWN without
exact runtime identity and traces. `tx_bias_effect` makes the quota/driver-weight
distinction explicit; no driver NAPI multiplier is silently assumed.

## Dynamic DQL/BQL versus a default static clamp

BQL is Linux dynamic byte accounting integrated with a driver's queue/completion
path, not a separate silicon queue-capacity feature. The
[ag71xx source](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/drivers/net/ethernet/atheros/ag71xx.c)
reports queued/completed bytes and registers its own NAPI weight32. The
[DQL definitions](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/include/linux/dynamic_queue_limits.h),
[algorithm](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/lib/dynamic_queue_limits.c)
and [queue sysfs implementation](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/net/core/net-sysfs.c)
support the supplied default min0,max1879048192,hold1000ms and dynamic adaptation.
Current limit, bytes in flight, configured ceiling and physical DMA-ring depth
are distinct. A54250-byte snapshot does not prove54250 queued bytes or a
particular starvation/overbuffering event;1780 is not a universal optimal floor.

The v16 default guard rejects static min/max/hold overrides and accepts changing
current limits inside the default bounds. It checks each field as an explicit
unsigned integer, not a missing-as-zero fallback. The default choice preserves
the tested policy: R1 claims a jitter/GP tradeoff, but its raw-jitter disagreement
prevents accepting the claimed-70.136% benefit. R5 GP-10.267% and p95+4.448%
provide a negative saved result for another clamp. Neither result proves that
all manual BQL constraints are harmful on every device/workload.

There are **two further findings**: R5 CPE B1/B2 current limit3028 is below
configured minimum4542. Sysfs min/max setters update fields without immediately
clamping current limit; dql_completed subsequently clamps it. This can reflect
a transitional, non-atomic or stale snapshot, not an impossible kernel state.
Convergence, write/completion ordering and exact native epoch remain UNKNOWN.
The general audit retains the values and finding; the default-profile guard
does not admit that state as a qualified default snapshot.

## Endpoint budget policy and remaining getter gaps

| Declared endpoint/class policy | Default budget / ceiling |
| --- | ---: |
| LAP-120 / MIPS74Kc_560MHz | 600 |
| Loco5AC / MIPS74Kc_560MHz | 600 |
| R5AC-Prism / Scorpion | 600 |
| LiteBeamM5 / AR934x_400MHz | 300 |

<!-- stage822a-payload-end -->
