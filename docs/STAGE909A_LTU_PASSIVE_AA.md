<!-- doc-head: Stage909A bounded passive LTU CPU and IRQ63 observations without controlled traffic -->
Missing telemetry is unknown; passive sampling cannot establish zero false positives.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage909A: passive observation only

Question: can CPU1 IRQ63, CPU and network counter changes be read safely on
the LTU bench without traffic generation, configuration or device-node access?
Attribution: external controller, Linux and proprietary LTU telemetry.

Executed unchanged collector on 2026-10-27:
`python tools/autoresearch/run_stage909a_ltu_passive_aa.py --collect-passive`.
The live run used the documented credential; no secret was retained in evidence.
Without that flag it writes only a local NOT_COLLECTED plan.

Target:198.18.0.63; username ubnt; documented narrow credential pointer.
Six A/A_REPEAT bookkeeping pairs each contain two observations; each observation
contains two snapshots separated by3 seconds. Total24 SSH reads, each requested
with a10-second deadline. Pair labels do not make unoffered background traffic
a controlled A/A experiment or independent replication.

Allowed readbacks: whitelisted board name/sysid, firmware version, mca-status,
boot ID, uptime, /proc/stat, /proc/net/dev and /proc/interrupts. No proprietary
device node, configuration/secret file, ioctl, mmap, write, register access,
remote file/script installation, module reload, ping or load generator is used.
Unavailable native status fields remain absent rather than synthesized.

Every raw snapshot is saved locally with actual SSH stderr/exits, UTC timestamps,
client monotonic brackets and collector epoch. Deltas require both clocks to
advance with unchanged target boot and collector epoch. CPU1 IRQ63 is mapped
using the actual CPU header, not a hardcoded second numeric column. Missing
CPU1/IRQ63, changed descriptor, counter reset/wrap or clock failure gives null.
Observed zero delta is distinct from a missing counter. CPU/interface deltas
are passive activity only, with no inferred receiver goodput or QAM capability.
SSH telemetry itself contributes interface traffic and CPU overhead.

Receipt status is always PASSIVE_OBSERVATION_ONLY. The statistical gate remains
NOT_APPLICABLE_NOT_CONTROLLED_WORKLOAD; zeroFalsePositive stays UNKNOWN;
controlled_aa_valid and promotion_eligible remain false. Exit0 only indicates
all24 SSH reads completed. Failed reads produce exit2 with partial evidence.

Result artifact: artifacts/autoresearch/stage909a_ltu_passive_aa.json.

## Fresh native execution

Collector exit code: 0. Acquisition: CAPTURED.
Native snapshots: 24/24 successful SSH transports;
12/12 windows expose comparable counter intervals.
Provenance: CONFIRMED_LIVE_HARDWARE; applies only to actual native observations.
Observed aggregate CPU busy range: 30.47% to 40.70%; background load and SSH overhead are included.
CPU1 IRQ63 native delta: 0 to 0 over 12 observable intervals.
No controlled A/A result, packet-loss estimate, application goodput or zero-FP acceptance follows.
[Receipt](../artifacts/autoresearch/stage909a_ltu_passive_aa.json) binds raw native captures.
[Execution log](../artifacts/verification/stage909a/execution.json) retains exact argv and exit.
All device configuration, services, protected storage and device nodes were outside the executed commands.
