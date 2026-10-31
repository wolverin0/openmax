<!-- doc-head: Stages1224A/1225A passive bilateral diagnostics with corrected static MIPS/ARM proof boundaries -->
<!-- /doc-head -->

# Stages1224A and1225A ? Passive diagnosis, no device control

The detector uses saved Stage1190A/1191A evidence and independently reads the named ELF bytes.
It opens no network, SSH or device API and exports no apply/deauth/restart/timer-write action.

## Discovery identities

The historical bare DISC27/DISC28 identifiers already name other findings and remain unchanged.
New aliases are `FMX-DISC-27@Stage1190A/free-node-stall` and
`FMX-DISC-28@Stage1191A/ltu-timer-asymmetry`.

## Important correction to the silent-stall premise

`ubnt_poll_host.ko` is ELF32 MIPS big endian. `check_sta` compares a raw120000000 literal
against a scaled jiffies-derived age. The no-wrap interpretation is120000 ticks;
an elapsed120000ms threshold would require exactkernelHZ1000, which is not established.
No unconditional120-second firmware timeout alarm is emitted.

Both the timeout/unauthorized path and the successful lookup path call `ieee80211_free_node`.
The paired stock `umac.ko` exposes an atomic reference increment in `_ieee80211_find_node`
and decrement in `ieee80211_free_node`; only the last-reference path targets the destructor.
Calling `free_node` does not establish deletion of an associated station.
Association teardown, peer notification and a resulting silent stall remain UNKNOWN here.

The passive evaluator can flag sustained AP-absent/STA-associated state with no byte progress
under explicitly observed offered traffic. It requires a stable bilateral identity, boot IDs,
channel, counters and bounded collection skew. Reboots, counter resets, idle links, missing
fields and short windows yield UNKNOWN. Its default120000ms observation window is an analyst
policy, explicitly distinct from the unresolved firmware timebase.
A candidate is a diagnostic observation; it is never a calibrated alarm or PWO authorization.

## LTU timer asymmetry

Two exact LTU2.4.2 binaries are covered, with full64-character computed SHA256 values.
AF-LTU timer objects are `.data+0x12d8`/`0x12dc`; Rocket uses`0x12f4`/`0x12f8`.
Initialized little-endian values1 and90 give a parameter ratio90, not a measured recovery ratio.
The timer unit, scheduling cadence, current runtime settings and causal4x/6x persistence remain UNKNOWN.
The evaluator uses reported vendor labels, never numeric MCS ordinal assumptions, and excludes
explicit power/ceiling limits. It describes intermittent-interference/low-label observations;
it cannot identify the timer mechanism as their cause or validate zero false positives.

## Offline use

`python tools/uisp/fmx_disc27_28_silent_stall_and_ltu_90x_hysteresis_detector.py`

`--samples capture.json --detector stall` or`--detector ltu` evaluates supplied capture rows.
Missing evidence never becomes healthy, calibrated, physical-ready or authorized-to-write.
The receipt binds source receipts, binaries, exact symbols, relocation targets and scalar bytes.
No native samples or performance results are synthesized by the builder.

[Receipt](../artifacts/verification/stage1224a_fmx_disc27_28_detector.json)
[Detector](../tools/uisp/fmx_disc27_28_silent_stall_and_ltu_90x_hysteresis_detector.py)
