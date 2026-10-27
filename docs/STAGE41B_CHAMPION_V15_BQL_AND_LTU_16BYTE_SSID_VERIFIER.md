<!-- doc-head: Stage41B offline v15 queues and LTU SSID/calibration verifier -->
All five Stage44A rounds and both Stage43A tests/final state are bound to saved JSON.
R5 reports +7.140% GP/-3.618% p95/-12.863% p99; IPTV/voice jitter regressions remain.
Supplied profile keeps OpenWrt eth0=1000 and airOS8 Rocket queues256/budget600.
SSID guard counts exact UTF8 bytes before preparing any review-only INI fragment.
Board/intmode/IRQ plus ordered ABAB crystal/DCXO evidence are required, never inferred.
No device execution; native LTU acceptance UNKNOWN, OTA unqualified, E2 NOT_ACCEPTED.
<!-- /doc-head -->

# Stage41B Champion v15 and LTU beacon verifier

Task: `T-S41B-CODEX-STAGE44A-CHAMPION-V15-AND-STAGE43A-LTU-INTMODE1-VERIFIER`.
Parent: external-controller control authority and reproducible experiment
methodology in the [original forward plan](../artifacts/2026-09-20-forward-plan.html)
and [fixed Stage41B contract](BENCH_PLAN.md). This is one offline deliverable.
It does not resume parked acquisition or authorize changes to the current radios.

Implementation: [pure verifier](../controller/stage44a_champion_v15_and_ltu_beacon_verifier.py),
[tests](../tests/test_stage41b_champion_v15_and_ltu_verifier.py).
`audit_saved_sources()` reads only bounded local JSON through the existing
Stage40B reader, rejecting duplicate keys, nonfinite JSON and network/reparse paths.
Canonical SHA256 pins cover the complete two documents and each of five rounds.
These authenticate saved objects, not the origin or freshness of native measurements.
Individual semantic audits do not authenticate their callers' input.

## Saved Stage44A result

Each round retains A1/B1/A2/B2, for 20 saved windows. Means are recomputed from
two phase aggregates per arm, then rounded to three decimals as in the source.
The Pareto score is GP delta minus 0.35 times p95 RTT delta using unrounded
percentage deltas. It is an optimizer score, not an independent performance metric.
Raw receiver lost/total counts and percentages are cross-checked for all 40
IPTV/voice observations. This supplies no new raw RTT samples, uncertainty
intervals, repetitions, firmware identity or causal replication.

| Round | GP change | p95 RTT change | Pareto score | Saved decision |
| --- | ---: | ---: | ---: | --- |
| R1 uniform OpenWrt eth0=256 plus Rocket changes | -1.985% | +7.822% | -4.7223 | retain |
| R2 NAPI defer2/GRO100000ns | -1.423% | -8.851% | +1.6752 | retain |
| R3 weight48/TX bias2/budget300/8000us | -1.416% | -2.715% | -0.4664 | retain |
| R4 combined uniform queues and NAPI changes | -34.137% | -33.299% | -22.4818 | retain |
| R5 asymmetric queues, Champion v15 reported | +7.140% | -3.618% | +8.4063 | promote |

R5 GP32.998→35.354Mbps, p95 85.782→82.678ms and p99 97.689→85.123ms
(-12.863%). Target IPTV B1/B2 has 0/2846 and 0/2844 lost datagrams (0/5690
pooled); target voice has 0/600 and 0/599 (0/1199). Controls retain IPTV27/5699
and voice3/1198. Zero observed target loss is confined to these finite windows.
IPTV jitter worsens 1.601→2.014ms (+25.796%); voice worsens2.691→3.348ms
(+24.415%). Champion promotion is preserved as a source decision; uniform QoE
improvement and a newly independently accepted wireless champion are not claimed.

## Asymmetric queue boundary

`verify_asymmetric_profile` validates explicitly supplied AP/CPE interface
inventories. Dynamic AP_VLAN `phy0-ap0.staN` entries must be named individually
and all appear in queue and NAPI maps. No missing getter becomes zero.

| Endpoint/interface | Supplied v15 value |
| --- | --- |
| OpenWrt AP and CPE eth0 | tx_queue_len1000 |
| OpenWrt br-lan, AP/CPE WiFi, declared AP_VLAN children | tx_queue_len256 |
| OpenWrt lo and CPE br-wan | tx_queue_len1000, kept separate |
| airOS8 Rocket br0/ath0/eth0 | tx_queue_len256 |
| airOS8 Rocket netdev_budget / dev_weight | 600 / 64 |
| OpenWrt NAPI defer / GRO flush timeout | 0 / 0 |
| OpenWrt dev_weight RX/TX bias; budget/usecs | 64,1,1;600/20000 |

The verifier also preserves the saved TCP/FQ/AP-AQL, Rocket multicast vector
and M5 baseline fields. AP/CPE FQ memory limit is4194304, flows4096,
limit2048/1024 and quantum4542/1514 respectively. AP-AQL is VO300/600,
VI1200/2400, BE1500/3000, BK500/1000us. Complete CPE-AQL and native per-station
airtime getter values are absent; reported per-CPE weight labels do not fill
the empty `ap_station_airtime_weights` getter. Native identity and freshness
are also missing, so scalar profile match never qualifies the whole champion.

The requested phrase "hardware BQL" is narrowed: BQL is Linux dynamic byte
accounting integrated with a hardware driver's enqueue/completion path.
Linux6.6.110 [ag71xx source](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/drivers/net/ethernet/atheros/ag71xx.c)
contains `netdev_sent_queue` and completion accounting. The
[queue sysfs ABI](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/Documentation/ABI/testing/sysfs-class-net-queues)
defines dynamic current/minimum/maximum limits; the
[DQL implementation](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/lib/dynamic_queue_limits.c)
adjusts limits from production/completion history. This does not establish
the exact running build or a new silicon offload.

`validate_bql_evidence` requires supplied driver=`ag71xx`, interface=`eth0`,
an explicit `expected_queues` list matching all queue keys and nonnegative
integer `limit_min <= limit <= limit_max` with a positive maximum for each.
54250/1780 are reported snapshots, not pinned thresholds. Even valid supplied
evidence returns native_authenticated=false and hardware_offload_proven=false.
The saved Stage44A JSON has no actual driver/BQL readback. R1 combines Rocket
br0/budget with OpenWrt eth0 changes; R5 combines Rocket br0/budget changes and
uses another baseline. BQL interaction is INFERRED, without an isolated cause
or a universal optimal tx_queue_len law.

## LTU fail-closed admission contract

`validate_ssid` returns exact UTF8 bytes only for a nonempty string of1..16
bytes, with no NUL, controls, surrogates or line separators. It never slices,
normalizes, trims or silently shortens. Sixteen ASCII bytes, eight `é` or four
single-codepoint emoji fit; seventeen ASCII bytes, nine `é` or five emoji fail.
The historical `FuturaMAX-LTU-Be` is16 bytes; the longer proposed
`FuturaMAX-LTU-Bench` is rejected. Numeric board_ssid is distinct from network SSID.

`prepare_ini_candidate` calls this guard before handling readback/calibration
and before constructing bytes. It then rejects INI delimiter/quote/comment
ambiguity, validates supplied board_ssid0xae08, integer intmode1, GPIO_8 and
registered IRQ=true. All evidence needs explicit device_id/boot_id,
module_sha256 and evidence_sha256. Equal vermagic alone does not qualify ABI.

The calibration predicate requires a caller-declared pair of distinct positive
frequency integers and4..64 even observations alternating A,B,A,B. Every sample
needs sequence0..N-1, strictly increasing uint monotonic_ns, identical
device/boot/module identity, exact frequency_mhz and four matching freq_list
entries, crystal_locked=true, calibration_complete=true and finite nonnegative
DCXO before/after codes. An already calibrated oscillator may retain its code.
These are supplied fixture predicates; hashes and booleans do not authenticate
hardware, legal RF settings, acquisition freshness or actual calibration quality.

Only after all checks pass does the function return the exact review fragment
`ssid=<validated UTF8>\n`, its SHA256 and a binding of evidence/recipe.
It always returns native_dispatch_allowed=false, complete_native_ini=false
and native_buffer_termination_qualified=false. It writes nothing and has no
loader, callback, subprocess or SSH path. The fragment does not assert vendor
ame.ini syntax/ABI and is not a complete configuration. Existing native
`ame_ctrl_dev`/INI runners are untouched; they are not made safe by this module.

## What Stage43A can establish

Both saved common-info excerpts report AP-PTMP(Run),5500MHz/20MHz,
SSID `FuturaMAX-LTU-Be` and zero stations. Both dmesg excerpts contain
Board SSID0xae08 and crystal lock5500. There is no original input INI/SSID,
freq_list sequence, DCXO trace, direct intmode getter or GPIO8 IRQ proof.
Consequently those predicates stay UNKNOWN and no native INI is admitted.
Final remote_info has Total0/TOTAL LINKS0 and PING_111_NO_REPLY: OTA remains
unqualified. No current health statement follows from this historical state.

The producer `ame_core_beacon_update`0x007008 versus consumer
`slm_find_preferred_record`0x045e20 `strcmp` claim is operator-supplied context.
Exact instructions and bounded buffer/terminator behavior are not present in
the requested JSON or its report. The16-byte policy is conservative admission,
not proof that the native C buffer safely terminates at16 bytes.

The runner's first dmesg capture is not a synchronized new-log boundary.
Test2 changes LTU core/air_fpga and permits fallback; its saved JSON lacks
per-test module identity. Final Rocket symbols describe final state only.
Report test2 module-size assertions are not independently corroborated; the
LTU core file size3282052 in JSON differs from3282044 in report text.
Redirected `send_map`/`send_wr_fpga_reg_command` success returns can manufacture
software success; they do not prove FPGA programming. Patch metadata and
matching vermagic are not pre/postimage identity or ABI acceptance.

## Verification and disposition

Scoped pytest receipts, failed attempts if any, source hashes and independent
review are retained in
[Stage41B validation](../artifacts/autoresearch/stage41b_validation_20261025.json).
Only the new pure test path is executed; existing physical benchmark tests
and runner scripts are not imported or run. Crash recovery found no surviving
Stage41B local process; the saved module was resumed without device access.
Fresh focused pytest: **690 passed, exit0** in1.33s. The initial run retained
689PASS/1FAIL: the AST test mistook `re.compile` for builtin code compilation.
The test was corrected without changing the verifier or weakening its native
execution boundary. An existing pytest asyncio fixture-scope deprecation warning
was emitted; no unrelated suite or hardware bench was run. Independent review
found no initial blocker and corrected the documentation's unsupported
"regular file" wording. Final frozen review is linked from validation.
No physical operator action is needed for this offline deliverable. Missing
native/OTA evidence stays an explicit gap; no next experiment is started.
