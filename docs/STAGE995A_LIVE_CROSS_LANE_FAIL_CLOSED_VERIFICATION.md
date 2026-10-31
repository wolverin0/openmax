<!-- doc-head: Stage995A fresh unified native cross-lane verification; physical workload admission remains blocked -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage995A — Physical cross-lane fail-closed verification

2026-10-27. Provenance **CONFIRMED_LIVE_HARDWARE** for native observations;
overall **BLOCKED_FAIL_CLOSED**, deployment **NOT_ACCEPTED**.
Attribution: external controller acquisition; Linux/mac80211/native airOS getters.

## Executed runner and observations

A new unified **read-only admission** runner was implemented and executed.
It is not a claim that an older unified workload runner or the unfinished Stage953
multiflow draft was run. Command:

```text
python tools/autoresearch/run_stage995a_live_cross_lane_fail_closed_verification.py --collect --cleanup-runtime
```

Actual process exit2 reflects failed physical admission, not an SSH transport failure.
Twelve bounded SSH executions completed: eight identity/profile reads (before/after),
two runtime version/dependency checks and two exact private-RAM cleanup operations.
Per-getter failures remain in native stdout/stderr; whole-shell exit0 does not make
an unavailable getter valid. No pings, listeners, workloads or configuration setters.

| Node | Fresh native observation | Qualification |
| --- | --- | --- |
| .20 | LAP120 OpenWrt24.10.4/kernel6.6.110, AP5180MHz/VHT20 | Native AP confirmed |
| .251 | Rocket2AC Prism0xe2f2, airOS2XC.v8.7.11 | Not an OpenWrt WA STA |
| .241 | PowerBeam5ACGen2 OpenWrt AP5200MHz/VHT20 | Reciprocal peer MAC confirmed |
| .242 | PowerBeam5ACGen2 OpenWrt STA5200MHz/VHT20 | Reciprocal peer MAC confirmed |

PowerBeam AP/STA MACs are `PUBLIC_DEVICE_0038` and `PUBLIC_DEVICE_0037`.
Before/after complete stable profiles match on all three OpenWrt nodes. .251 is
explicitly inapplicable to the OpenWrt profile comparator, not a false equality.
PowerBeam BE1500/2000 and tcp_autocorking1 remain unchanged; notsent is131072 on both.
.20 has BE1500/2500, notsent8192 and mac80211 aqm quantum3028/limit512/memory3145728.
These are AQL **per AC**, not TID. Kernel default fq_codel and internal iTXQ values
do not identify the actual root qdisc or demonstrate a performance benefit.

## Runtime lifecycle and physical blockers

The prior Stage953 three-file official iperf runtime was hash/version/loader-verified
again on both radios. No file was in use in process mappings. Exactly iperf3,
libiperf.so.0 and libatomic.so.1 were removed from each known private directory;
both rmdir/absence checks returned0. No recursive deletion or system package change.
Native tool version proof is not traffic evidence; these files are now absent.

Admission blocks: WA20/.251 does not form a qualified OpenWrt pair; the historical
A/A had239/240 replies; the historical autonomous watchdog failed; no fresh admitted
multiflow A/A, discovery or disjoint holdout exists. Historical facts are hash-bound
and labelled reused. Manual recovery was verified separately and does not turn the
failed autonomous proof into success. All new goodput/RTT/jitter metrics remain null.

[Runner](../tools/autoresearch/run_stage995a_live_cross_lane_fail_closed_verification.py),
[receipt](../artifacts/autoresearch/stage995a_live_cross_lane_fail_closed_verification.json),
[execution and native replay](../artifacts/verification/stage995a/).
The initial local CLI-parenthesis error occurred before hardware access and is
preserved. Pure checks and hash/reparse verification qualify tooling, not RF efficacy.
