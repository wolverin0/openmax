<!-- doc-head: STAGE42B_STAGE47B_LTU_OTA_1024QAM_AND_POSTSTART_VERIFIER.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

[Document router](STAGE42B_STAGE47B_LTU_OTA_1024QAM_AND_POSTSTART_VERIFIER.md) | Part 1/2
<a id="routing-same-switch-versus-standalone-poe"></a> [Routing: same switch versus standalone PoE](STAGE42B_STAGE47B_LTU_OTA_1024QAM_AND_POSTSTART_VERIFIER_CONTINUATION_73c6a5a44d_002.md#routing-same-switch-versus-standalone-poe) | <a id="cold-boot-evidence-validator-and-acceptance-gap"></a> [Cold-boot evidence validator and acceptance gap](STAGE42B_STAGE47B_LTU_OTA_1024QAM_AND_POSTSTART_VERIFIER_CONTINUATION_73c6a5a44d_002.md#cold-boot-evidence-validator-and-acceptance-gap) | <a id="verification-disposition"></a> [Verification disposition](STAGE42B_STAGE47B_LTU_OTA_1024QAM_AND_POSTSTART_VERIFIER_CONTINUATION_73c6a5a44d_002.md#verification-disposition)

<!-- stage822a-payload-begin -->

Stage47B JSON/report and a captured revision of both poststart literals are bound offline.
Saved per-radio association sequences are consistent; AP/CPE uptime clocks stay separate.
Only CPE flash progress is captured; both-endpoint cold-boot/standalone persistence is unproved.
Held2.4.2 boot invokes ubntconf/plugins; exact running generator/build/readbacks are missing.
Same-switch reachability and ath0 addresses do not independently isolate the RF data path.
Pure verifier/tests only; native dispatch false, physical UNKNOWN, E2 NOT_ACCEPTED.


# Stage42B Stage47B LTU OTA, 1024-QAM claim and poststart verifier

Task `T-S42B-CODEX-STAGE47B-LTU-OTA-1024QAM-AND-16BYTE-SSID-VERIFIER`.
Parent: control authority and reproducible experiment methodology in the
[original forward plan](../artifacts/2026-09-20-forward-plan.html) and
[fixed Stage42B contract](BENCH_PLAN.md). All work is local and offline.
No radio, SSH, WSL, native target, deployment script, module or flash command
is executed. The original saved artifact/report/scripts are preserved.

[Verifier](../controller/stage47b_ltu_ota_link_and_poststart_verifier.py),
[focused tests](../tests/test_stage42b_stage47b_ltu_ota_verifier.py),
[validation](../artifacts/autoresearch/stage42b_validation_20261025.json),
[poststart literal freeze](../artifacts/autoresearch/stage42b_poststart_source_freeze_20261025.json).
The source JSON and report are canonical/raw-byte bound respectively. The
freeze records parent Python source SHA256, exact literal text and per-literal
SHA256. A later template revision is not silently substituted. Existing source
changed during initial inspection and again after the focused tests. This
captured revision governs the audited predicates; subsequent template changes
are explicit drift, not automatically accepted replacements. Its identity on
either deployed radio remains UNKNOWN.

## Saved association evidence

CONFIRMED within the saved transcript: matching FMX-LTU, AP/CPE Run roles,
one reciprocal peer,5500MHz/20MHz,15dBm conducted power,13dBi gain and reported
28dBm EIRP. Numeric fields are checked against common-info and peer MAC text.
SSID is7 exact UTF8 bytes; the reused guard rejects over16 bytes, controls and
surrogates without truncation or normalization. The saved after-state is
stronger than Stage43A's historical zero-peer snapshot; it does not authenticate
the new capture's acquisition or establish current radio health.

| Radio clock | Required ordered events |
| --- | --- |
| CPE | SYS.ssid FMX-LTU; Valid beacon; coming FMX-LTU/20/5500; preferred5500; CIRE/SFN sync; CIRE→LOCK_DONE; LockDone; state3; TA235; TA applied235 |
| AP | EAB superqueue; TA0→235; TA2 trigger; TA2 done/shift0; user1; ath0 clears NOCARRIER; air0→3 |

All required events must occur exactly once with strictly increasing timestamps
inside their own clock domain. Duplicate/missing/reordered events fail closed.
The two CPE arrays share one ordered trace; AP timestamps are never compared
with CPE uptime. Clock synchronization, shared boot identity and cross-radio
event timing are absent from the artifact.

Beacon6639.223536→state3 6644.316280 is **5.092744s**. SSID configuration
6624.681497→state3 is **19.634783s**. The source report's phrase "5.1 seconds
of restarting" uses beacon detection as its origin; the actual restart event
is missing. No restart-to-association latency is established.

The producer0x007008 `[s_beacon,#0x0e..0x1d]` and consumer0x045e20 `strcmp`
mechanism is recorded in the source metadata/report. Exact ELF identity,
instruction bytes, ABI and16-byte C terminator behavior are not supplied here.
Shortening the SSID, changing the scan recipe and changing power co-occur;
isolated causal attribution to any one is INCONCLUSIVE. The policy bounds input
bytes without claiming native buffer safety. The alternating list is reported
as5500/5520/5500/5520, not a captured time series of DCXO code/calibration quality.

## Saved data-plane metrics and their limits

| Source summary | Value |
| --- | --- |
| DL mean / peak interval | 61.4 /79.1Mbps;14 retransmits |
| UL mean / peak interval | 41.9 /42.4Mbps;11 retransmits |
| Ping min / mean / max | 3.160 /5.250 /7.822ms; reported0% loss |
| AP/CPE reported ath0 addresses | 198.18.0.61/24 and198.18.0.72/24 |
| SpectrumEfficient AP/CPE | 1535 /1319 |

The verifier checks finite numbers, min≤mean≤max, peak≥mean and integer
retransmits.61.4+41.9=103.3Mbps and103.3/20=5.165 are consistent arithmetic.
Without shared directional workload timing,103.3 is a sum of directional means,
not demonstrated simultaneous aggregate throughput. Raw iperf receiver intervals,
ping attempts/replies, routes, bridge ports and source/device bindings are
absent. Reported0% loss has no saved denominator. An independent1535/1319
to1024-QAM/NSS map is also absent, so the 1024-QAM MIMO label remains reported,
not independently decoded or accepted by this verifier.

## Flash persistence is not a standalone cold boot

The JSON stores **only LTU2's** cfgmtd progress text: Storing Active[1]100%,
then Active→Backup[2]100%. It has no AP cfgmtd receipt, command exit status,
persisted file hash/readback, partition integrity comparison, power cycle or
fresh boot_id. Common-info contains Reboot0 and driver restart counts10/3;
driver restarts do not prove a cold boot. The report's table claiming both
endpoints100% and its unconditional remote-relocation statement exceed the
saved evidence. The original `ready_for_remote_relocation=true` is retained as
a source claim; `native_relocation_accepted` remains false.

The frozen poststart literals at the capture cutoff are:

| Literal | UTF8 SHA256 | Significant supplied behavior |
| --- | --- | --- |
| LTU1_RC_POSTSTART | 58cf59d1968bd107b37883f48f338e2144db8fc80be264a5465a5b4998e73fb2 | existing-file SSID edits; conditional restart; ath0 address/keeper attempts |
| LTU2_RC_POSTSTART | d234783df13dac748db8f6e0378ab671c3cde7a32952d127e67b5868db518fb6 | existing-file SSID/preferred-SSID edits; live SSID; alternating scan; address/keeper attempts |

These are exact known snapshots, not a general shell interpreter. Mutated or
unknown scripts require a new review and are rejected by the static classifier.
Python source extraction accepts literal constants via AST and never imports
or executes the deployment module.

Both scripts edit only existing /tmp/ame.cfg,/tmp/ame.ini,/etc/ame.ini. Most
sed substitutions do not insert a missing key; CPE's preferred-SSID fallback
still depends on an existing matching SSID line. Both load the INI only if
/tmp/ame.cfg exists. Neither creates that file or writes/validates
/etc/sysinit/ame_program.conf. A subsequent driver restart can consume regenerated
configuration; the scripts do not read back the final config/build identity.
The AP has no unconditional live `amecli ssid` fallback. AP fixed5500 operation
does not itself require CPE-style alternating scanning.

The captured deployment function separately edits system.cfg SSID keys,
invokes ubntconf and writes cfgmtd before invoking live poststart. Stage45B
then performs additional live repairs. Those later live operations can explain
a working snapshot without proving the stored boot recipe. Preferred-SSID is
handled later in existing-file/live edits, without generated cold-boot readback.
A parent template
hash or line count is not the deployed rc.poststart hash.

Many commands suppress errors with `|| true`; the active marker is created
before health qualification and exit0/done markers can follow failures. The
new5s ath0 keepers retry address adds but do not prove success, carrier, SSID,
routing or reboot persistence. Their marker does not prove the loop survived.

A subsequent source revision was observed after the test cutoff: parent SHA256
dfb5b0a593695a55067d191e4eed99c3b48e806179919cefe7faa0c8327ff5f4.
Its only literal changes add reciprocal permanent-neighbor restoration attempts
after ath0 address assignment and inside the keepers. Later AP/CPE literal
hashes are90703d1fe8037121ed0ee29ea4bb5933edd46d16f8b4bafb809985f0f74ae310
and33b3c048a60914be7ca2bb542b97aa006c45e429e8237ea83d074394d608b996.
This intends to restore neighbor state; it does not add config generation,
flash readbacks or cold-boot evidence. A permanent entry is not a measured
reachable peer. This revision is not substituted into the frozen classifier
or the REACHABLE-neighbor fixture policy, and native acceptance stays UNKNOWN.

## Held firmware generation chain

The held **LTU2.4.2** tree supplies static context, not exact Stage47B runtime
identity. Under `artifacts/firmware_re_xc_ltu/ltu_extracted/afltu_2.4.2/rootfs_extracted`:

| File | Static boundary |
| --- | --- |
| init:335–364,406–410 | reads active/backup config and derives system.cfg; invokes ubntconf |
| usr/etc/rc.d/rc.funcs:32–36,83–100 | sources /etc/sysinit/$plugin.conf, runs plugin_start; plugin startup precedes the poststart hook, with /usr/lib/cs and /etc/poststart gates |
| bin/ame_drv.sh:5,263–264,340 | defaults AME_CFG=/tmp/ame.cfg; start loads the existing file into INI and brings ath0 up; stop brings ath0 down |

Held bin/ubntconf is a zero-byte extraction placeholder. Nonempty ubntbox has
strings for /tmp/ame.cfg,`%s/ame_program.conf` and an ame_drv.sh-start template.
These support intended generated targets; strings do not establish generator
control flow, exact output contents or successful native regeneration. Thus
"ame_drv.sh regenerates /tmp/ame.cfg" is REFUTED for this held script. Whether
<!-- stage822a-payload-end -->
