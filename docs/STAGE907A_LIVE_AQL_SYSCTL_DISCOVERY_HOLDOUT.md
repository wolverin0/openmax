<!-- doc-head: Stage907A transient PowerBeam AQL/sysctl experiment, independent watchdog proof and disjoint holdout -->
<!-- /doc-head -->

# Stage907A — AQL/sysctl discovery and independent holdout

2026-10-27. Physical execution requires clean Stage906A and native rollback proof.
Only the bench `.242` STA is eligible for transient setters; no production panel,
firmware, interface role, RF channel, service, flash or protected partition is changed.

## Predeclared profile and workload

| Field | A baseline | B candidate |
| --- | --- | --- |
| mac80211 AQL BE low/high | 1500 / 2000 | 2000 / 4000 |
| Linux tcp_autocorking | 1 | 0 |
| Other AC limits / BC-MC | Native snapshot | Identical |
| Radio | Native5200MHz/VHT20 | Identical |

Resolve the actual managed interface and PHY every time. Read/write AQL through
`/sys/kernel/debug/ieee80211/phy*/aql_txq_limit`, not an invented ath10k child file.
This is a joint two-knob profile test: individual causal effects are not separable.

Each window: one existing4MiB HTTP object,2s settling,20 idle ICMP requests at1s.
Goodput is actual receiver bytes divided by the complete observed window. Idle RTT
does not stand in for loaded latency, sector capacity or a new universal champion.
Six fixedAB discovery blocks and six independent fixedAB holdout blocks are frozen
before acquisition. Allocation is not randomized; one physical link limits generality.
One predeclared hypothesis, paired_block gate, single-step Sidak, max_loss_pct0.

## Transaction and native proof

Before any setter: compare native boot/kernel/board/interface/PHY/AQL/sysctl/BQL/
pktlog/channel against the frozen baseline. Arm traps and a HUP-ignored target-side
45s watchdog with separate stdio. Before load: verify the actual applied candidate.
Every B window snapshots all four AC rows and sysctl, restores on exit/error, compares
exact native snapshots and requires the controller's fresh restored-baseline readback.
Only private `/tmp/fmx-s907-*` files and owned child PIDs may be cleaned.

The separate probe deliberately SIGKILLs the controlling shell after verified B
application. Only an autonomous watchdog restore exit0, exact native baseline after
45s and successful private-RAM cleanup qualify the probe. A local shell fixture or
parent EXIT trap is insufficient. Failed proof blocks the AB campaign.

The AB CLI also replays the six zero-loss A/A pairs and checks the wrapper/campaign
revision and current baseline against the restored probe. No boolean bypass exists.

## Holdout acceptance

Discovery and holdout have separate dataset/session/epoch/block/run IDs, normalized
receipt paths, raw hashes and non-overlapping times. Holdout needs an independent
hash-bound review receipt listing actual discovery/holdout run hashes, candidate
fingerprint and the original frozen plan. The real gate decides; no forced KEEP.
Safety rejection and insufficient improvement remain valid negative outcomes.

[Script](../tools/autoresearch/run_stage907a_live_aql_sysctl_discovery_holdout.py),
[receipt](../artifacts/autoresearch/stage907a_live_aql_sysctl_discovery_holdout.json),
[rollback proof](../artifacts/verification/stage905a_to910a/rollback_probe.json).
Final measured outcomes and restoration evidence are added after acquisition.
