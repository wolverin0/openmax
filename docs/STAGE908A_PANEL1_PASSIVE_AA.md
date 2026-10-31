<!-- doc-head: Stage908A bounded passive Panel1 observations without a controlled AA workload -->
No false-positive rate or promotion can be inferred from these passive reads.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage908A: passive observation only

Question: which CPU, interface, IRQ and queue changes are observable on
Panel1-Guarida without generating traffic or changing configuration?
Attribution: external controller, Linux/mac80211/ath10k telemetry.

Executed unchanged collector on 2026-10-27:
`python tools/autoresearch/run_stage908a_panel1_passive_aa.py --collect-passive`.
The live run used the documented credential; no secret was retained in evidence.
Without that flag the CLI writes only a local NOT_COLLECTED plan.

Target:198.18.0.7; username root; documented narrow credential pointer.
Six bookkeeping pairs each contain A/A_REPEAT observations. Each observation
has two snapshots separated locally by3 seconds:24 SSH reads total, each
requested with a10-second deadline. Labels are not randomized treatments,
independent RF replicates or a controlled statistical A/A experiment.

Read-only sources: ubus board, boot ID, uptime, /proc/stat, /proc/net/dev,
/proc/interrupts, iw interface inventory, dynamically resolved PHY AQL/aqm.
No ping, offered load, remote file/script installation, setting, register,
module reload, flash or device-node access occurs. No secrets/configuration
files are requested. Actual SSH output/errors and per-command exits are saved.

Each snapshot is persisted locally before continuing. Source UTC timestamps,
client monotonic brackets and a collector epoch accompany target boot/uptime.
Positive deltas require unchanged host/boot/collector epoch and ordered clocks.
Missing/reset/wrapped counters and a changed IRQ owner stay UNKNOWN/null.
CPU busy uses explicitly exposed CPU tick counters. Interface byte rates are
passive L2 activity, not unique application goodput, capacity or throughput gain.
SSH telemetry contributes traffic and CPU overhead; this is not an idle baseline.
IRQ63 CPU1 delta is reported only when the actual CPU header and row expose it.

All receipts remain PASSIVE_OBSERVATION_ONLY. The inferential gate is
NOT_APPLICABLE_NOT_CONTROLLED_WORKLOAD; zeroFalsePositive is UNKNOWN;
controlled_aa_valid and promotion_eligible remain false, including full capture.
Exit0 means24 SSH acquisitions completed; it is not experimental acceptance.
Missing/failed transport yields exit2/PARTIAL_OR_UNAVAILABLE with raw evidence.

Result artifact: artifacts/autoresearch/stage908a_panel1_passive_aa.json.

## Fresh native execution

Collector exit code: 0. Acquisition: CAPTURED.
Native snapshots: 24/24 successful SSH transports;
12/12 windows expose comparable counter intervals.
Provenance: CONFIRMED_LIVE_HARDWARE; applies only to actual native observations.
Observed aggregate CPU busy range: 31.06% to 78.62%; background load and SSH overhead are included.
CPU1 IRQ63 delta is UNKNOWN: the required native CPU1/IRQ63 observation was not available.
No controlled A/A result, packet-loss estimate, application goodput or zero-FP acceptance follows.
[Receipt](../artifacts/autoresearch/stage908a_panel1_passive_aa.json) binds raw native captures.
[Execution log](../artifacts/verification/stage908a/execution.json) retains exact argv and exit.
All device configuration, services, protected storage and device nodes were outside the executed commands.
