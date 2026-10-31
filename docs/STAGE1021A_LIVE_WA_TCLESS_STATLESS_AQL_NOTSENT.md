<!-- doc-head: Stage1021A native tc/stat-free readbacks and immediate AQL/notsent apply/restore verified; workload and autonomous proof unresolved -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage1021A — Native WA readbacks and prepared rollback

2026-10-27. Native observation provenance **CONFIRMED_LIVE_HARDWARE**.
Benchmark/application acceptance **NOT_ACCEPTED**; A/A and A/B are **NOT_EXECUTED**.
Attribution: external controller acquisition, Linux/mac80211 getters.

## Two fresh reads on198.18.0.43

Both preflight SSH captures completed, three seconds apart. In that phase no stat,
tc, kernel setter, service change or workload was executed. Source and native stdout/stderr are
bound in the [receipt](../artifacts/autoresearch/stage1021a_live_wa_tcless_statless_aql_notsent.json).
Native LAP120 kernel6.6.110, boot<uuid>,
activephy0/APphy0-ap0 at5180MHz/VHT20. Before/after stable profile is identical.

| Getter | Actual value |
| --- | --- |
| default_qdisc | fq_codel |
| AQL VO low/high | 300/600 |
| AQL VI low/high | 1000/2000 |
| AQL BE low/high | 1500/2500 |
| AQL BK low/high | 500/1000 |
| separate BC/MC | 50000 |
| phy AQM limit / quantum | 512 /3028 |
| phy AQM memory limit | 3145728 |
| tcp_notsent_lowat | 8192 |

Stage1008 parses the complete actual native text, including the preserved BC/MC row.
Stage1014 returns **PROFILE_MISMATCH**: default comparison expects BEhigh3000.
This is a genuine value mismatch, not absence of stat/tc. The default validator
only parses AQM format; it does not validate AQM quantum/limit against a target.
Kernel default and mac80211 iTXQ do not prove interface-root qdisc parameters.
AQL is per access category, not per TID; no new champion is established here.

Associated station MACPUBLIC_DEVICE_0036 maps to complete ARP candidates
198.18.0.67 and198.18.0.47. A MAC/proxy match does not authenticate the
OpenWrt measurement peer or provide a host-side UDP receiver across the link.
No discovered address outside this stage's .20 lease was probed.

## Prepared transaction and one native immediate probe

[Generator](../tools/autoresearch/stage1021a_transaction.py) compares the native
baseline with Stage1014's declared target: BEhigh2500→3000 and notsent8192→131072;
VO/VI/BK stay equal. That target is operator-reported, not a measured winner.
Before writes it checks board/kernel/boot/interface/PHY and exact AQL/notsent.
Equal fields are skipped explicitly. Rollback inspects every AC and the sysctl,
attempts every differing field despite an earlier write error, and preserves all
return codes. Only exact fullAQL+BC/MC+notsent readback can establish restoration.
Write warnings remain visible even when the resulting state matches the snapshot.

Prepared modes: immediate rollback and a separate45s HUP-ignored autonomous watchdog
probe with intentional controlling-parent SIGKILL. PID/start-time guards are checked
again before KILL; polling stops on identity change. Wait only follows a dead/zombie
owned process. Bounded cleanup and exact private-RAM file removal are present.

Six disposable local-file fault fixtures plus two shell syntax checks passed:
normal, write-side-effect/error, failed BE, failed sysctl, continuation across ACs,
and equal-state/no-writes. No local fixture touches SSH, real sysctl or debugfs.
The first local verifier syntax failure was retained. This is **LOCAL_TESTED**,
not a native watchdog proof. [Evidence](../artifacts/verification/stage1021a/local_transaction_verification.json).

After coordinator review, exactly one immediate native transaction ran, without load:
BE1500/3000 and notsent131072 were read back while applied; then BE1500/2500 and
notsent8192 were restored. Both apply return codes were0. Rollback skipped equal
VO/VI/BK rows, restored BE and the sysctl with return0, and reported WRITE_ERRORS0.
Native command exit0, full restored state equals the original baseline, and the
private RAM directory was removed. A separate fresh SSH read independently confirmed
the restored AQL, BC/MC, sysctl, boot, interfaces/channel and AQM writable settings.
[Immediate proof](../artifacts/verification/stage1021a/immediate_native_probe.json)
binds exact program/stdin, pre/applied/post state and execution source. The first
driver compile error was local, before hardware, and is retained separately.

This verifies one transient application/restoration, not a measured champion or
capacity/latency benefit. No45s SIGKILL probe or A/A/A-B workload was executed.

## Remaining criteria

No qualified receiver/bridge host, no autonomous45s native rollback proof and no
measured A/A or A/B cohort exist. Goodput, latency, gate result and zero-FP claims
remain null/unqualified. Missing stat/tc is not used as a blocker for these getters.
[Collector](../tools/autoresearch/run_stage1021a_live_wa_tcless_statless_aql_notsent.py)
requires explicit --collect; imports do not access devices.
Its --reparse mode reconstructs preflight analysis only; retain the separate execution
proof and additive finalization metadata when auditing this final receipt.
