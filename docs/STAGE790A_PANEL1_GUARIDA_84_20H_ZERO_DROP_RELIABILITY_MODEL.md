<!-- doc-head: Stage790A Panel1 saved-time and packet reconciliation with conditional Poisson reliability -->
WDS connected snapshots, cumulative queue drops and hypothetical zero-event bounds stay separate.
<!-- /doc-head -->

# Stage790A

Parent: fixed787A..792A offline RE1 support in BENCH_PLAN.
Run `python tools/sim/run_stage790a_panel1_guarida_84_20h_zero_drop_reliability_model.py`.
Reads immutable local files only; no network, producer, shell, radio or load execution.

## Actual scope of saved observations

678 /before_telemetry/stations and /after_telemetry/stations contain three matching
MACs and connected times72265->72267,72261->72264,72146->72149 seconds.
The saved execution elapsed3.869s. Its producer defines zero_drop by equal MAC
sets and at least3 stations. This is snapshot membership, not20h outage surveillance.
The raw station dump connected times72267/72263/72148s span20.0411..20.0742h;
20.07 is a rounded longest-link value, not the exact minimum of all three links.
Association timers and low-time-resolution snapshots do not exclude brief WDS
dataplane interruptions or all intermediate reconnects. No boot/event-log epoch,
packet continuity capture or detection probability is available. Join by MAC;
saved prose/alias assignments conflict, so they are not authoritative identity joins.

The raw678 dump totals40,482,795 TX packets,500,366 retries,2,473 TX failed,
32,586 RX drop misc. Those are cumulative counters with unproven common reset
epochs and distinct semantics, not measured loss probabilities or WDS disconnects.
Consequently zero packet drops is not supported by these saved fields.

683 /stations_per_tid has3*8 queue rows with39,405,365 TX packets (39.405365M),
1,412 TID0 CoDel drops,30 marks, zero other TID drops/overlimit/backlog. Its
producer contains the full24-row dictionary as literals, sums it, and declares
20.12h literally. We compare the literal data with the JSON without executing it.
Pillar prose instead says39,343,195, an internal headline discrepancy. These rows
are a saved literal-data ledger, not a fresh sysfs trace. Do not pool their count
with678 TX packets or pair20.07h with39.41M as a single validated exposure.
Intentional CoDel queue drops and WDS link failures are different outcomes.

## Prespecified conditional reliability sensitivity

Illustration only: suppose0 detected WDS events over T=20.07 AP-hours and
a homogeneous Poisson event rate lambda, with independent known detection q.
P(Nobserved=0)=exp(-lambda*T*q). One-sided95% upper lambda=-ln(.05)/(T*q).
Lower survival over h hours is exp(-lambda_upper*h); lower MTBF=1/lambda_upper.
Evaluate q={.1,.5,1} and h={1,24,168}. q=0 gives no finite identifiable upper rate.
These are conditional frequentist model bounds, not probability that the true
rate lies in an interval or proof of future reliability. Detection sensitivity,
homogeneity, event independence and complete surveillance are unverified here.
Actual q is UNKNOWN; no empirical outage bound or MTBF acceptance is produced.
Packet counts supply no independent WDS-trial denominator. Correlated CPEs share
an AP and channel; summing three connection ages does not triple AP exposure.
Nonzero failure-count intervals are outside this zero-event model's contract.
KEEP the conditional tool; sustained zero-outage physical acceptance remains UNKNOWN.
