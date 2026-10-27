<!-- doc-head: Stage355A qualified AirSelect-inspired frequency coordination model -->
Bounded synthetic SimPy queues and finite pymoo fronts are not vendor firmware or RF results.
<!-- /doc-head -->

# Stage355A

Parent: offline RE1/control-boundary hypotheses after353/354.
Run `python tools/sim/build_stage355a_airselect_hopping_evasion_pareto.py`.
The dedicated JSON retains240 runs:10 policies,3 seeds,4 family strata and2 scenarios.
WA,XC,XW and a mixed three-peer stratum are modeled separately, never ranked globally.

The [vendor airOS6 M-series guide](https://dl.ui.com/guides/airOS/airOS_6_UG.pdf)
describes a frequency list, hop interval and advance announcements, with timing-drift
concerns. Pages11/21 and full PDF hash are cached. This source does not qualify
AirSelect on WA/XC airOS8, nor does it expose a vendor announcement wire format.
This is an AirSelect-inspired coordination experiment, not reverse-engineered TDD.

## Fixed conceptual model

One terminating SimPy process advances800 one-millisecond ticks. Six bounded fluid
queues represent DL/UL for three peers. Arrivals, stale interference observations,
handoff messages and service are modeled without any network or target executor.
Three abstract channels C0/C1/C2 carry quiet or rotating synthetic interference.
Family rate/switch-time presets are explicit UNMEASURED assumptions.
Every direction shares a synthetic70/30 TDD frame. Clock-skew sensitivity can
misalign peer/AP directions. AP and peers cannot serve during switch guards or
channel mismatch. Missed announcements incur scan/reacquisition blackout.
Static, reactive and coordinated alternatives share fixed seeded inputs.
The clock_skew_ms parameter is a fixed phase offset, not oscillator ppm drift.
Hop lead, switch guards, peer retunes and lost notices affect service; quiet
scenarios may favor staying put. Observations are delayed, not a future oracle.
Control delivery takes5ms; peers start tuning at max(AP-hop time, message receipt),
then pay ONE family retune duration. A missed notice incurs60ms scan wait followed
by ONE retune. Reactive AP changes occur before that tick's fluid service; future
coordinated changes are scheduled at their announced boundary. An overlap guard
rejects a hop inside an interval whose service was already charged.
Scanning and announcement airtime are not charged separately; this remains an
explicit model limitation, not a measurement or vendor protocol characteristic.

Offered bits=delivered expected bits+overflow drops+outstanding backlog.
Finite horizon/event/queue limits and no service while mismatched are enforced.
This is expected fluid service, not exact packets, PHY PER or TCP/BA recovery.
Completed-chunk p95 excludes unfinished chunks; undelivered-at-horizon includes
backlog and is not packet loss. Both limitations remain next to the objectives.

pymoo ranks all finite policies separately in each family/scenario. It minimizes
negative mean goodput, mean per-run completed-chunk p95, and horizon-undelivered
fraction. No completion maps to the800ms horizon penalty. A mean of percentiles
is not a pooled percentile, and three seeds do not validate physical performance.
No AirSync compatibility, sub20 enablement, legal RF frequency, DFS/CAC bypass,
PLL setting or firmware support is inferred. Regulatory eligibility and actual
control/announcement APIs remain UNKNOWN. Decision: KEEP offline model only.
