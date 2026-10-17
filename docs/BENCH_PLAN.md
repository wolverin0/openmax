# Bench plan — autonomous execution from 2026-10-05

Summary: the ordered, checkbox-tracked work plan for the physical bench (LAP-120 + NanoStation loco
on OpenWrt, SXT Lite5 + LiteBeam M5 as 802.11n foreign/slow stations, ES-10XP switch). Executed by the
Claude pane without operator babysitting; operator items are marked **[OP]** and are the ONLY things
that wait on a human. Keywords: FMX-0007 baseline, FMX-0008 AQL, C1 spectral, C6 anomaly, C7
interference, ath9k mixed stack, SXT, LiteBeam M5, bench runner tools/bench/bench.py.
Read when: resuming bench work, or checking what was measured vs planned. Results land in
`research/raw/bench/<date>/` + `docs/CURRENT_STATE.md` addenda. Status: ACTIVE.

<!-- doc-head: Actual CPE OOM during requested 200 Mbps observation; broader work paused -->
October16: 300s observation stops on CPE globalOOM; process restarted/association recovered; E2 and comparisons unaccepted.
2026-10-15: operator authorizes corpus-wide synthesis, local installation and literature search.
2026-10-10: notebook READY recovered; E2 physical intake exposes AP hostapd OOM under200Mbps; restored.
Use FMX_CPE_VIA_AP=1 for Nano access via AP; legacy disruptive routines refuse it.
Only the authoritative active course is executable; older ACTIVE entries are history.
<!-- /doc-head -->

## October16 current ? requested 200 Mbps observation stopped on actual CPE OOM

The broad E2/three-comparisons goal remains PAUSED at the operator's20:14UTC stop. The subsequent narrow request was one200Mbps/300s observation without the2s telemetry cutoff; the operator explicitly authorized reserve floors as warnings, retaining actualOOM/reboot/process-loss stops. No further load is active or planned without a new instruction.

CONFIRMED physical result: corrected caller2332407d ran trial5b3dfaa4e9354684b644207ba51c0971 at unchanged11dBm/channel36/80MHz. Reception stopped around110s;145.014s of native intervals were retained, including35s zero delivery. Those intervals contain924301200received bytes (50.991Mbps over145.014s); no complete native final/end result exists, so this is not a300s aggregate. Kernel logs confirm CPE globalOOM killed wpa_supplicant1436; the host did not reboot. The CPE radio reinitialized and reassociated; wpa_supplicant now has new process births. This is an actual failure under the tested indoor/NLOS conditions, not proof that geometry or firmware alone caused all losses.

Both radios passed30/30posthealth after stop. Owned endpoint/radio rules and Gateway lease were cleaned; Gateway CLEAN_RESTORED/rc0. Fresh independent readback five-minute-200m-post-oom-readback.json confirms association, unchanged boots/config hashes/persistedRF/VM sysctls, AP unchanged daemon births and CPE changed wpa_supplicant births with retainedOOM. Therefore operational recovery is observed, exact pre-test process identity is not restored. FAIL_PRESERVED_RESTORATION_REVIEW_REQUIRED remains unchanged. No switch/production access or firmware flash occurred.

Earlier failed attempts are retained: efc6 stopped around105s on a preventive reserve floor;0fdd stopped around190s because an over-broad guard treated dynamic zone boost/min as configuration change (noOOM). These guard errors were corrected only for this explicitly approved observation; original E2 admission/acceptance are unchanged. E2 and all three comparisons remain unaccepted.

Raw: research/raw/bench/2026-10-16/endpoint-5b3dfaa4e9354684b644207ba51c0971/{five-minute-result.json,events.jsonl,client.stream.jsonl}; post-readback and independent final-result review are alongside.

## October16 authoritative current - physical baseline and three comparisons goal

Operator activated the attached goal on October16: obtain a reproducibly
measured bench configuration, accept E2, compare three evidence-led adjustments
and apply/verify the best measured configuration. The full objective remains
active until all four deliverables and required independent acceptance exist.
This supersedes RE1 priority/bench parking below. Firmware analysis is parked;
it is not a prerequisite for physical measurements.

Authority: autonomous bench inspection, implementation, repairs, tools,
measurements and reversible configuration changes with bounded execution,
recovery and restoration. Necessary firmware reinstalls require exact model,
image, backup and proven recovery first. Production, purchases, unrelated
equipment, protected partitions and regulatory/security weakening remain
outside scope. No renewed permission by attempt count or helper checkpoint.

Parent E2/FMX-0007 / original September20 forward-plan baseline deliverable.
Question: which measured bottleneck limits the current bench, and which three
individual adjustments help or fail under equivalent conditions?
Existing evidence: E2 NOT_ACCEPTED, prior OOM/accounting failures preserved,
50M/30s duration now survives under original restored allocator policy, but
full E2 is unaccepted. Minimum next evidence is fresh bilateral admission and
one guarded100M/30s exposure; later200M/TCP/RRUL still need their own evidence.
Prior OOM/accounting failures stay preserved; no baseline gate has been lifted.

Completion requirements remain the stricter original E2 contract: five valid
blocks of TCP1/4 and UDP50/100/200 both directions30s plus canonical RRUL60s
(55 cells), with loaded latency p50/p95/p99, receiver goodput, loss/jitter,
retries/MCS, CPU/memory and stability. Preserve original RF/identity/memory
and restoration gates. A5s diagnostic, partial nine-cell runner, source review
or synthetic result does not accept E2. The baseline runner's unresolved-OOM
block stays enforced until evidence and independent review justify a source
change. RRUL/Linux endpoint admission remains missing enabling work.

Then compare three adjustments selected from measured evidence, one variable
at a time, alternating treatment order, at least five repetitions per condition
to preserve the plan's requirement above the goal's minimum three. Report
variability and use the best measured configuration; if all three fail, restore
the accepted baseline and retain the reproducible negative results.

### Current executable checkpoint - October 16, 17:59 UTC

Parent deliverable: E2 / FMX-0007, followed by three measured comparisons and
verification of the final configuration. E2 remains NOT_ACCEPTED. The original
55 cells, required repetitions, metrics and independent acceptance still apply.

Scope excludes switch 10.10.100.90 from all access and actions because exclusive
bench ownership is unconfirmed. The earlier certificate request is obsolete.
Work uses only the identified AP (.1.2), CPE (.1.3), PC and Gateway (.100.179).
No switch, production, SSH security or persistent regulatory changes occurred.

Measured evidence:
- 50 Mbps / 30 seconds survived the fixed diagnostic.
- 100 Mbps / 30 seconds (f73c6876) completed: receiver 62.433 Mbps, reported
  UDP loss 37.421%, jitter 0.140 ms. Both 45-second observation streams, cleanup
  and 30 post-health probes passed. No OOM or identity/configuration change.
  Independent review f110ebea accepts scoped acquisition and survival only.
- 200 Mbps / 30 seconds (e91a8cf6) failed after 10.875 seconds: CPE observation
  age reached 2035 ms, exceeding the unchanged 2000 ms limit. No complete client
  JSON or valid goodput. AP/CPE partial streams contained 14/13 samples, with
  minimum free pages 4172/4124 and available memory 9148/9188 KiB; no OOM seen.
  Independent review c97546db preserves FAIL. Cleanup and 30 post-health probes
  passed; later exact PID/birth/boot checks verified both observers exited.

The 200 Mbps timing audit shows no pending controller queue. The last CPE sample
had local duration 449 ms and transport age bound 118 ms; the next sample did
not arrive before expiry. The cause between remote acquisition and SSH delivery
is UNKNOWN. Earlier 7e01 observation failure and fdcf preflight failure remain
preserved; neither is rescued by the later 100 Mbps result.

Current state after restoration: original PCP fraction 0, min_free_kbytes 8192,
watermark_boost_factor 15000, Normal min 2048 and boost 0; RF 11 dBm / 80 MHz.
Full hashes, boots and service identities remain unchanged. Late AP admission
values were 4108 pages / 8892 KiB available; CPE 4019 / 8768. CPE fails the
original 4096-page load admission floor. No new load is authorized by that read.
The separate CPE recovery 993af24 failed its first post-write check and stays
FAIL; restoration succeeded. AP recovery 96f20c completed. The later independent
original-policy admission enabled the single 200 Mbps attempt above; accounting
sums never substituted for actual available memory or load admission.

Next decisive action: passive five-second profiling of the existing observer's
snapshot phases on both radios, using the exact fc21 source, added timestamps
and the original loop and safety checks. No RF/load/configuration change. Keep
shared observer source unchanged until evidence justifies a minimal repair.
Idle profiling cannot establish the cause under load. Preserve failures; do not
relax freshness or repeat 200 Mbps without a changed diagnostic hypothesis.

Necessary RRUL preparation may proceed independently within the same E2 goal:
canonical Flent profile and fixed data ports are reviewed; netserver passive
qualification 4ebf04d passed with zero clients and verified cleanup. Radio guard
c1bb887 passed source review and native nft check-only validation, but still
needs native route/restoration qualification. Extend the existing Gateway lease
with an explicit RRUL profile and exact 13 INPUT rules, preserving the default
iperf lease. Require source review and passive qualification before use. No
RRUL traffic or baseline OOM gate clearance has occurred.

The acquisition history below preserves earlier hypotheses, failures and
superseded next-step text; it is an audittrail, not additional active commands.

Latest100M/30s7e01c5 FAILED afterabout19s client time with
ObservationError:latest observation expired; client stopped immediately. No
nativecompleteJSON/goodput claim. PartialAP23/CPE21samples show noOOM/boost,
minAP4146pages/9044KiB,CPE3779/8132. ExactRF/network/endpoint restoration and
30/30posthealth complete; observerpartial/initialexit-unverified failures kept.
Lateindependentreadback17:16UTC verifies both exactobserverbirths exited,
originalPCP0 andradio locksabsent. This does not rescue the failed cell.

Next decisive missing evidence is WHICH role/sample/transport/control-queue
age violated2s, not another unchanged100M retry or looserfreshness. Existing
failure omitted per-receipt timings; heldidle14ticks/s andunderload44.4AP/
19.9CPEticks/s show accountedobservercost but do NOT prove failure cause.
Minimum necessary instrumentation: boundedin-memory per-receipt timing audit,
explicitfailedrole/latestage, persistedonlyAFTERownedclientstops toavoid adding
liveI/O. No observer/RF/load/admission/freshness/deadline changes. Source review
andregression fixtures required, thenONEsame100M diagnostic toidentifycause,
onlyif freshadmission (existingrole-bound PCPpreparation ifrequired). Preserve
firstfailure andallcurrentpreimages. Broaderobserveroptimization staysparked
until timings identify a concrete need; no generictool/platform rewrite.

Necessary RRUL endpoint nativepreparation whiletiming source isreviewed:
ONE passiveGatewaynetserver qualification from privatelystaged source54ad315
pluspinnedbase55aeb (independentroot source-reviewed,17fixturesPASS). Bindonly
192.168.1.170:5205 underindependentGNUtimeout60s, readREADY/freshstatus/owned
parentPGID, then taggedSTOP andverifyallownedprocesses/listener exit. No client,
UDP/TCPdata generation, firewall/route/RF/globalconfiguration writes. This
qualifies lifetime/listener0workers only;11worker/data-path proof staysmissing.

### Historical acquisition trail within this goal

Fresh intake October16: pinned Gateway.179 SSH/identity/enp1s0.170 verified;
Gateway can ping the expected CPE.3 MAC3/3. Initial manual PC AP probes failed
because they omitted the required explicit.1.155 source on the SkipAsSource
alias. Corrected -b/-S.1.155 yields pinned AP SSH and3/3 ping. Existing bench
transport already binds correctly; no AP outage or code repair is established.
Gateway->CPE->AP existing local SSH also confirms exact boards/boots and2/2
radio ping. PC retains original.100.155/.1.155 addresses. Bench switch.90
MAC74:83:c2:15:2a:8b answers2/2 using a temporary, restored10.10.100.155 alias.
First switch probe failed before address readiness; preserve that qualification
failure, not as switch unreachability. Proper Preferred-state probe succeeded.
The switch browser reaches a certificate privacy barrier after source-address
selection was corrected. Its manual validation request is now OBSOLETE because
normal AP access works; operator was informed, temporary alias removed and
addresses reverified. No certificate bypass, port/power change or radio write.

Executed normal passive capture99d66d5ef32d4e09a22a7bf6cf8a4565: control and
cleanup PASS, no traffic. An initial postreadback serialization failure and
later native status readback/serviceRunning state are retained; mutex-held
restoration and final service-only readback confirm Stopped, no owned PIDs,
no filters or active capture. Independent runtime closure pending.
Read-only bilateral20s idle observation7fe6d7ca97664feab4c3f569afeedcef passes:
21 samples/role, stable boots/service births, no OOM, VM unchanged, boost0;
AP Normal4481pages/MemAvailable9956KiB, CPE4221/9888. This is not load readiness
or E2 acceptance. Next one changed-instrumentation50M/5s recipe requires source
rebind and all fresh run-time gates; retain baseline OOM block.

Active bounded work: minimum ready.json PermissionError repair in existing
bridge/tests, independent source review and passive capture qualification.
Root owns integration/live execution/docs, corpus_audit bridge/tests only,
evidence_audit independent acceptance; no new workers or executor platform.
Keep snapshots and results under research/raw/bench/2026-10-16, preserving
previous attempts under2026-10-15. If access remains blocked, continue only
necessary unblocked acquisition preparation; never claim the goal complete.

October16 executed continuation: one repaired50M/5s RF-as-is diagnosticdd66
completed with31,191,600 receiver bytes vs31,320,000 sender bytes,49.895Mbps,
no OOM, unchanged identities/VM/RF and30/30 posthealth. Actual PermissionError
recovered in16ms/two reads. Independent result review PASS_WITH_LIMITS for
transmission/survival5s only; no baseline OOM-gate release. Capture emitted
zero packet events despite valid application data, so independent sequence
accounting remains UNKNOWN. Preserve it and PARK optional capture refinement;
it is not a universal prerequisite for the independent duration/memory question.
CPE final3940 Normal pages/8764KiB available is below4096 admission; require
new naturally sufficient fresh samples, never cache flushing/lowered thresholds.

Next bounded question: does the same50M reverse UDP condition survive the
original30s duration with complete bilateral observation? Primary change is
duration5->30; omit the parked optional capture and keep all original memory,
identity,11dBm RF-as-is/15of15, source-path, client-deadline and cleanup gates.
Minimum necessary enabling delta: existing observer finite maximum84s (for
30s pre/post coverage and later60s RRUL), existing one-cell diagnostic fixed
30s/client deadline33s/observation45s. Independent review required before
execution. This is duration qualification, not E2 acceptance or a new platform.
Stop the cell on an existing abort; preserve failed admission/result and choose
the next evidence-led repair without restarting unchanged failures.

Necessary headroom investigation before30s: quiet CPE remains3940 Normal
pages/8764KiB available after cleanup, so another load is currently inadmissible.
Held same-run snapshots show MemFree16884->15760KiB while per-CPU pagelist
count459->990pages; its high limit is2560pages (10MiB). Slab/anonymous/file
changes are small; buddy+PCP arithmetic rises1000KiB. This is compatible with
redistribution into PCP, not proof of a memory leak or proof no leak exists.
Runtime confirms vm.percpu_pagelist_high_fraction=0, Normal managed14030pages,
batch3, socketsUDPmem0. Held Linux6.6.110 source says0 derives high from the
low watermark;64 yields max(14030/64,4*3)=219pages on one CPU. The write changes
all CPE zones/CPUs and does not immediately drain PCP; later frees apply it.

Fixed passive question: does ONE CPE-only20s0->64->0 cache-policy treatment
return enough pages to the general allocator without changing the existing
memory protection policy? Layer: Linux allocator, not radio firmware or MAC.
No RF/load, drop_caches, min_free/watermark or threshold changes. Beforewrite
require exact original0, expected board/boot/build/service/RF,8192/15000,
boost0/min2048/noOOM and original abort floor. Arm an independent tagged,
boot/PID/birth-bound restoration path first; keep finite treatment/cleanup
deadlines and exclusive ownership, preserve foreign changes rather than
overwrite them. Observe PCP/count/high/batch/buddy, memory and identities;
restore0 on completion/abort and verify original policy/high/batch and health.
Runtime has setsid/ucode; timeout is ABSENT, so never assume that executable.

Acceptance: numeric limit219 and observed buddy/PCP response, complete safe
restoration, KEEP/REJECT/INCONCLUSIVE for the causal hypothesis. No automatic
OOM cure, E2 acceptance, permanent tuning or future-load admission follows.
If no headroom recovers in20s, retain that result without escalating/repeating
unchanged. Even a positive passive result requires fresh4096/8192 admission
and independently reviewed30s qualification. This support change is necessary
because actual acquisition is blocked; do not develop a generic VM optimizer.

Independent necessary RRUL path question while the no-load memory probe is
reviewed: can existing WSL reach the AP from required PC.1.155 source? A no-write
single SSH-banner connection times out; AP has only.1/24 and10.99/24 routes.
Current host.1.155 alias is SkipAsSource=true, while.100.155 is primary. Test
ONE temporary Windows source-selection treatment true->false->true for12s,
with identity/MAC/interface checks, native detached20s restoration armed before
write and finally restoration/readback. No IP/route/firewall/RF change. One WSL
TCP22 banner socket is wired management only, not a traffic/load measurement.
Observe actual AP socket source and restore source flag. Stop if no correction;
preserve negative result rather than opening broad routes or source exceptions.

Wired RRUL source-selection result3849 NEGATIVE: even while.1.155 source flag
was false, WSL TCP22 still timed out; no AP matching socket. Do not infer that
changing this flag repairs WinNAT. Parent emitted restoration marker; final
independent readback confirms original.1.155true/.100.155false, owned guardian
PID absent. Guardian terminal receipt is missing; preserve timeout/CLI progress
pipe-pressure hypothesis as an instrument failure, not successful independent
restoration qualification. First attempt0eb5 failed before launch due cmd.exe
length; retained preimage. No RF load or route/firewall change. PARK this route
assumption; actual WinNAT source/path diagnosis remains needed for RRUL only,
not for the already executable native-Windows30s single-cell diagnostic.

PCP native qualifier8392291 FAIL_PRESERVED, no policy write: outer WindowsSSH
termination leaves the CPE qualifier controller alive. Independent setsid guard
survives and emits CLEAN_RESTORED|...|DEADLINE, which does NOT meet the fixed
CONTROLLER_LOST acceptance. Root then observes exact controller4425/birth5336107,
verifies boot+QUALIFY_ALIVE cmdline, TERM-cleans only that process, verifies exit,
guardian absent, fraction0 and lock absent. Retain failed result and cleanup.

Changed necessary qualifier hypothesis: SSH disconnect is not controller death.
Use a finite2s native qualifier controller (10x200ms ALIVE) instead of an infinite
loop; still terminate outerSSH after firstALIVE and demand independent guardian
CONTROLLER_LOST before its deadline plus exact owned exits. This tests survival
of guardian across actual outer transport closure and native controller exit,
without requiring transport loss to send a remote signal. No64 or load; no old
failure reclassified, no deadline accepted as success. Re-review source delta
and finite/no-policy fixture before one new native qualifier. Treatment20s and
existing identity/memory/CAS/restoration gates remain unchanged.

PCP finite qualifier7b846a8 PASS: actual outerSSH closure, native controller
self-exit, independent guardianCONTROLLER_LOST, knob0/lockabsent and both tagged
births exited. Independent runtime reviewe5fb0d confirms exactsource/identity.

ONE actual20s passive treatment91ac32c PASS_PASSIVE_ONLY_NOT_LOAD_READY:
22samples, initial3556freepages/7236KiB/PCP1334. Fraction64 high219 produces
first4883freepages/PCP40; later4634/11548KiB/PCP101. Restore0/high2560 verified,
post4634pages/11548KiB/PCP289, sameboots/config/services/RF/8192/15000/boost0,
noOOM. This confirms controllable PCP redistribution on this exact CPE; it is
not an OOM cure or accepted baseline. Independent causal-result review pending.

Next decisive action remains the ALREADY fixed/reviewed30s50M reverse-UDP
RF-as-is11dBm qualification. The allocator policy has been restored to0; do
not keep64 or perform another cache treatment for this cell. All fresh bilateral
4096/8192 admission,3072/4096abort, identity/service/VM/boost/RF/15of15 and
30of30posthealth checks apply. Source review47101e0 binds unchanged artifacts.
Failure or success remains duration/survival evidence only; no E2 gate release.

30s50M duration qualification3e1344/endpoint44a71ef completed rc0, failureNone,
cleanup[] and launcherCOMPLETED_NOT_E2_ACCEPTED. Receiver187,544,400bytes over
30.002321s (50.007971Mbps), sender187,611,600bytes; native reported0lost/3outoforder.
46samples each radio over45s; minAP4022pages/8124KiB, CPE3794/8188, noOOM.
Allocator policy0 restored before the cell and never changed during it.
Posthealth/identity restoration complete; independent result review pending.
This answers duration at50M only, not100/200, TCP, canonicalRRUL or baseline.

Next bounded rate question: same30s/50M recipe versus explicit100M (later200M
only after its own fresh decision), one variable offeredrate. Minimum fixedrate
selection in existing diagnostic/launcher, preserving5s50/30s50 and original
memory/RF/observer/source/cleanup gates. Preserve pre-rate sources and require
exact recipe review before any100/200 exposure. No automatic ramp or retry.

RRUL route diagnosis while source repair proceeds: originalOct10 AP capture
proves ICS once translated WSL172.22.65.24:59665 toPC.100.155:55335, with noAP
return route. Current tuple stillUNKNOWN; a source-port filter cannot survive
NAT reliably. Observe ONE new wired TCP SYN to unused APport62109 using passive
tcpdump onbr-lan, filter destinationonly, onepacket, independent native8s
birth/boot-bound capture cleanup, noRF/config write. This singleclosed-port
connect separates arrival/source/return evidence; timeout is retained. After
observation verify capture/guard owned exits. Do not repeat the failed flag
toggle, broadenroutes or addforwarding rules before actualtuple evidence.

Currenttuple CONFIRMED by passivebbcb9f7 capture: APbr-lan receives SYN
192.168.100.155:50570->192.168.1.2:62109; conntrack haszero reply packets.
Wiredconnecttimesout. Capture/independent8s guard both exit0/ownedEXITED,
noRF/configwrite. This matches the held historical ICS source/return failure.

Next ONE bounded wired return-path treatment: add onlyAP route
192.168.100.155/32 via192.168.1.155 devbr-lan proto99 metric49137 under tagged,
boot-bound native setsid12s lease, preexistingrouteabsent, trap/TTL restoration,
foreignpreserve and exactpostabsence. Keep Windowsaliases/flags/firewall and
all radio/RF untouched. OneWSL TCP22 bannerconnect then verify return works;
no testload orRFmeasurement. This route is only the prospectiveRRUL control
path prequalification; later full data path still needs fixedexactportNAT/
Gatewayrules/endpoint admission and source reviews. Preserve failure if no reply.

Headroom before100: actual30s50 finalAP4022/8124/PCP1568, CPE3770/8092/PCP1003;
bothfail fresh4096/8192. Extend onlyexistingpassivePCPprobe exactAP/CPErole,
with immutable181335diagnosticdependency toavoid unrelatedrateCLIqualification
churn. Same20s/64/219/restore0/noRF/noOOM/floors; qualify eachrolebeforewriting.
No permanent64, threshold reduction or automatic100/200 exposure follows.

## October16 historical RE1 result - native rate data path, parked by goal above

Parent RE1 / original firmware control-boundary deliverable supporting E4.
Question: does the native rate command update peer state consumed by packet
preparation? Answer: CONFIRMED_STATIC_CONDITIONAL, with original-byte-backed
object identity, guarded rate-record consumption and downstream packet-budget
use. Actual transmitted rates, runtime context and RF benefit remain UNKNOWN.
This supersedes the receiver-only and unresolved-reader checkpoints below.

- [x] Complete9972fc beyond the previous400-row export and bind table callers.
- [x] Prove entry+1c contains the allocated peer pointer; qualify management
  route and context-retargeting exceptions for the threshold reader.
- [x] Trace direct consumer98f224 from queue+44 through output rate/flag/count
  fields to992674/9926f8 packet preparation and final indirect4065ac handoff.
- [x] Bind host authorization to901f wire parameter3 and target internal8;
  verify9020 association mapping and case8 flags/mode conditions independently.
- [x] Qualify producer count: fallback1 is known; general1..6 invariant is
  UNKNOWN. Six serialized entries do not prove that separate count bound.
- [x] Check missing provider coverage and bounded bootstrap routes; preserve
  unresolved words, candidate failures, prior truncation and prelaunch failures.
- [ ] Resolve final provider from matching original-stock runtime evidence:
  words40657c,4065a8,4065ac,4065b0, their target bytes, core/address context and
  initialization state; supporting4000f8/400100/400138 require same qualification.
- [ ] Demonstrate actual rate choice and repeatable RF effect under a separately
  authorized guarded experiment. No runtime or performance acceptance here.

Results and exact evidence bindings:
research/raw/reverse/2026-10-16-applied/NATIVE_RATE_CONTROL.md and
native-rate-control-chain.json. Original source unchanged; direct IDA/Ghidra
used, with independent PASS_WITH_LIMITS reviews. No device access, target-code
execution, security-state change or firmware modification occurred.

Next decisive action is intake of an existing correctly identified stock dump,
or selection/authorization of a bounded read-only acquisition from a suitable
stock lab unit. No matching runtime material has been established by this
offline work. A CT dump/zero pointers cannot answer the stock-provider question.
Do not restart broad held-image scans or optional helper work to conceal this
dependency. This leaves RE1 PARTIAL_STATIC; E2 stays parked and NOT_ACCEPTED.
Stock flashing, security changes and RF work retain their separate gates.

## October16 historical checkpoint - native receiver, superseded above

Historical continuation after operator correction: the previous result was a
checkpoint, not a reason to stop. Parent RE1 question remains whether the
native rate command changes a peer state actually consumed by the data path.
Existing evidence is the callback/write chain and candidate reader9972fc.
Minimum missing static evidence: reader table40db14 consumers and argument
provenance linking its context to the lookup entry+1c used by the writer.
Execute held-source table/caller tracing and complete the previously truncated
function before declaring that route blocked. RF stays parked. Park only the
specific branch whose required bytes/context cannot be resolved from held
artifacts; continue other executable work for the same RE1 decision.

Applied the tools to actual held WA8.7.25 bytes; no second tools catalogue.
New result: dispatcher0x9a9550 handles9044 through state+10c; setter9a9a14,
API initializer9a9a24 and registration99d320 bind callback99d034 under the
pre-existing LITBASE9bb001 hypothesis. The callback constructs a six-byte key,
uses held lookup989a7c and projects payload fields with hardware loops6/2.
It reaches98f6dc, passing context+68/source/26 to an indirect helper, then
98f75c writes context+8a through a rate-code/flag-dependent branch.
This narrows the old target-consumer gap. It does not prove target execution,
safe command injection, policy units or a CT-compatible patch.

Original bytes preserved;974 instructions checked in18 bounded functions.
Independent flow/lookup review PASS_WITH_LIMITS. Ghidra pseudocode omitted
hardware loop repetitions; assembly controls the field interpretation.
Byte25 of the26-byte projected record has no explicit initializer established.
Indirect helper semantics/runtime pointers and downstream TX reader remain
unknown. Preserve first import failure and REA MIPS rejection.
Receipt: research/raw/reverse/2026-10-16-applied/native-rate-receiver.json.
Private reproducible runs: firmware/build/re1-applied-20261016/ghidra-01..09.

Executed the bounded reader/provider follow-up: function0x9972fc reads its
first argument+0x8a and uses it in an optionally capped threshold comparison.
The only held exact pointer to this function is0x40db14; no direct CALL8 match
was found. Caller/object identity is unresolved: the same offset alone cannot
link this candidate to the command's peer context or prove TX semantics.
The function's output stops at400 instruction rows; preserve that limitation.
Receipt: research/raw/reverse/2026-10-16-applied/native-rate-reader-frontier.json.
Provider slots4000f8/400100/400138 are absent from the four current AP regions
and the16streams in the earlier retained-source survey. Missing evidence is
the correct-state pointer words, their resolved target bytes and caller/object
binding. This does not prove ROM residence or absence of other initializers.
Keep RE1 PARTIAL_STATIC: no firmware patch is justified by this result alone.
No device operation is implied; E2 remains parked and NOT_ACCEPTED.

## October16 executed - apply available reverse tools to native rate control

Operator explicitly rejects another research evaluation and directs use of
the useful tools in https://x.com/hanakoxbt/status/2110849274774970486.
Parent: RE1 / original firmware control-boundary deliverable, supporting E4.
Question: where does the matching held radio image receive and apply the
188-byte native rate schedule sent as WA0x9044 /2WA0x9045?
Existing: original host serializer/producer and exact embedded SGMT images;
the target consumer is not established by those host facts.
Minimum new evidence: matched sender/container identity, literal/dispatch
candidate and bounded original-byte-qualified target control/data flow.
Use working IDA and Ghidra directly, with selected useful upstream capabilities;
no installation catalogue, no duplicate known-sender qualification as result.
Stop at a new byte-backed consumer/control boundary or exact missing runtime
dependency after the concrete path is exhausted. Preserve ambiguity and all
failed tool attempts. Private imports allowed; no firmware execution/RF/flash.
REA's IDA adapter rejected MIPS; native IDA connected to the original-hash
umac module, so direct analysis continues without weakening REA admission.

## October16 completed - planning correction after operator feedback

Operator: "creo que no tenemos bien planeadas las cosas, por eso insisto en
cosas nuevas". This is a strategy review, not authority to resume RF work.
The seven-link assessment below is complete. Current deliverable is the
original firmware-control-boundary decision connected to E2/E3: identify what
we can actually change, what evidence supports it, and what measurement would
justify keeping it. No new backlog, tool platform or blanket prerequisite.

Observed planning failures:
1. Necessary acquisition repairs became the active objective; successive
   failures did not consistently trigger a decision about the shortest path
   to an interpretable experiment. Clean restoration was reported more often
   than a research answer. E2 is still unaccepted.
2. airOS/airMAX static reverse engineering and OpenWrt/CT testing were discussed
   as though they formed a demonstrated implementation chain. They do not:
   command namespaces, firmware consumers and host APIs are stack-specific.
3. A large technique catalogue and custom build existence were insufficiently
   connected to one hypothesis, one effective control and one acceptance rule.

Decision map from existing evidence (no new runtime claim):

| Candidate or finding | Actual change/control | Missing decisive evidence | Present decision |
|---|---|---|---|
| RE1 command0x9064 and0x17/0x1e layouts | Static proprietary airOS host transport; not an OpenWrt CT setter | Target consumer/runtime context and a justified equivalent public hook | Do not inject or translate command IDs; no direct CT patch derived |
| GRO host receive processing | Custom Linux path; historical install, seed goodput/latency tradeoff | Valid paired same-build physical comparison, current kernel identity if used | No KEEP; do not describe seed throughput as an accepted gain |
| AQL/TXQ | Existing mac80211/driver path, distinct from calibrated airtime fairness | Effective hook and interpretable latency/goodput comparison on exact stack | Preserve planned E3 after E2; no new algorithm now |
| Global aggregation ceiling | Existing CT host interface plus our input guard; not per-CPE adaptive scheduling | Valid physical response and benefit under fixed conditions | Safety guard is implementation evidence; performance benefit unaccepted |
| Own airMAX-equivalent scheduler | No demonstrated implementation/control chain | Stage4 primitives and downstream runtime evidence | Park; new reverse UI does not satisfy these gates |

Execution contract going forward:
- Keep OpenWrt as the existing lab platform; this does not select it as the
  final product or abandon the stock-airMAX hybrid route. No stack migration
  or flash is implied by this review.
- Before another acquisition repair, name the exact research decision it
  unlocks, the evidence the current failure invalidates and the simplest
  existing acquisition route. Instrumentation required only by the duplicate
  UDP accounting question must not become a universal gate for other work.
  Existing E2 safety/measurement gates remain intact; do not relabel diagnostics
  as an accepted baseline or silently switch the original E2 recipe.
- Before any new firmware/driver change, fill the chain: observed limitation
  -> source/control on the exact stack -> one change -> effective readback
  -> controlled comparison -> KEEP/REJECT/INCONCLUSIVE. If a link is unknown,
  the task is to resolve that specific link, not to build the proposed feature.
- A support failure returns to the parent decision before further repair.
  Unlimited repair authorization stays valid; it is not a priority argument.
- A future tool or paper is adopted only for a named missing link in this map.
  Static bytes can establish packing/call paths, not physical timing or gains.

Planning outcome: no reviewed reverse finding currently justifies a new CT
firmware patch. The next offline RE decision is narrower: does the held corpus
contain an exact matched host/receiver pair capable of establishing reception
and application of a per-peer rate restriction? Start with existing provenance
and accepted survey coverage, not another decompilation of the known sender.
Only inspect a receiver path if its build/platform/hash match is established
and it was not already exhausted. Output: a static intervention candidate, or
UNKNOWN with the exact missing receiver/segment/context. A negative inventory
ends that branch; no fabricated provider, new frontend or unchanged reanalysis.
This is separate from the physical path: interpretable E2 on the existing
stack, then planned E3. Before physical resumption reconcile failed acquisition
with the original recipe and choose the minimum necessary measurement path;
capture-helper repair is not automatically next. This review resumes no device.

## October16 completed - operator-directed reverse-tool review; RF acquisition parked

Parent: original firmware control-boundary deliverable / RE1. Operator supplied
seven reverse-engineering links and asked their practical relevance. Question:
do they supply a new usable route for held MIPS32BE modules or rawQCA firmware?
Existing evidence: qualified Ghidra/SGMT imports and host0x9064 path; downstream
runtime provider/context remains unresolved. Minimum evidence for this review:
actual post content, pinned primary code/docs and installed-provider admission.
Stop at a grounded tool-fit decision; no new target execution or RF experiment.

- [x] Seven links assessed, with pinned primary sources and code-level APK review.
- [x] Live REA6.5.0 session inventory: installed, idle, Ghidra detected; Windows
  provider excludes our MIPS ELF route. This does not limit Ghidra itself.
- [x] Selected APK ELF readers reject ELF32BE; Eleven is an optional workbench.
- [x] Adopt evidence/oracle/differential methods; no new scheduler, trace or gain.

Result: research/raw/reverse/2026-10-16-links/REVIEW.md. No additional tool
installation or repeated known-path RE1 check is necessary for this decision.
A further RE1 step needs a new consumer/provider evidence source or justified
distinct-build comparison; missing runtime addresses remain UNKNOWN.

Latest RF-as-is attempt d9410ae01a0347b78340891b1ac77d19 passed15/15 stability
but aborted after client launch on ready.json PermissionError. Incomplete
client/capture evidence leaves receiver accounting UNANSWERED; retain failure.
Post-abort readback confirms owned observers/root/watchdog exited, PktMon
stopped, network restored and30/30 health both ways. Infra acknowledged release
at02:30:57UTC. Capture repair and RF acquisition parked during this review;
no active load runner. E2 remains NOT_ACCEPTED with all original gates.
No operator physical action is required for the completed link assessment.

## October16 02:18UTC historical - receiver accounting at existing11dBm

Operator rejects the proposed wired-comparator/cable-change branch: remain
focused on radios. No cable change, loopback experiment or wired comparator
will be executed. Parent remains E2/FMX-0007 receiver-accounting diagnosis.
Question remains whether repeated iperf sequences appear at receiver NDIS.

The changed-order attempt8bb2f2fd158a44fea53b5b54bb67d35a failed BEFORE
observer/capture/client: settled pings14/15 in both directions at0dBm,
RSSI AP-67/CPE-60..-59. Preserve FAIL and missing APseq5/CPEseq4. Cleanup
verified; original11dBm restored,30/30 posthealth both directions, same
boot/service births/nine hashes/firmware/VM/no OOM. Independent receipt:
capture-stability-failure-review-8bb2f2fd.json. No unchanged RF retry.

Minimum changed hypothesis: the imposed minimum-power condition may contribute
to instability; existing11dBm is a diagnostic condition with demonstrated
posthealth, not a proven cure. Reuse the explicit October7 RF-as-is diagnostic
authority in DECISIONS.md, now necessary to the active accounting question.
Independent authority review confirms this scoped use; it does not approve
the old baseline. Execute at most ONE50Mbps5s reverseUDP1200B exposure with
the existing receiver capture, only after new source review and fresh gates.
Read and preserve actual11dBm/80MHz; NO RF power write in setup or cleanup.
RSSI is a recorded covariate without the old-55 ceiling for this diagnostic.
Require15/15 settled pings, exact single peers, unchanged bilateral two-sample
4096page/8192KiB admission and3072page/4096KiB abort,boost0/min2048,
no OOM/identity drift, fresh Gateway/capture and all deadlines/cleanup.
Restore only owned network state; verify unchanged11dBm and30/30 posthealth.
No further reboot or memory-policy change. Park load if any gate fails;
retain capture completeness UNKNOWN and the original accounting invariant.
E2 baseline and unresolved-OOM gates remain NOT_ACCEPTED and unchanged.
This section supersedes the0dBm diagnostic recipe below, not its evidence.

## October16 earlier execution - instrumented receiver accounting acquisition

02:07UTC update: one CPE fresh-state action917cd209 completed; early memory
admission failed3906->3506 pages, then the planned30/30 bilateral health
recovered4821 without another reboot or VM change. Independent review
cpe-capture-fresh-state-result-review.json permits only conditional acquisition.
Attempt0079cb4439214c96a5c9fc6fbb321973 stopped BEFORE client launch because
Gateway status acquired in parallel with native capture setup expired before
capture readiness. Preserve FAIL, zero client output and partial observers.
Capture restored; both owned observer PIDs subsequently confirmed EXITED,
watchdog absent/PktMonStopped, full restoration and health recorded in
endpoint-34bcce05212c44b797742407854ca19a. Minimum necessary repair: request
the single fresh Gateway status AFTER capture readiness. Keep2s age,12s
admission,20s observation and every RF/memory/cleanup gate unchanged.
Delayed6s capture fixture reproduces old failure; repaired28 fixtures pass,
including stale2.1s refusal. Independent source rebind is required before one
changed-order acquisition. This is not RF performance evidence or permission
for a reboot loop. Parent question and stop conditions below remain unchanged.

Operator explicitly requests continued execution after the administrative fix.
Parent remains E2 / FMX-0007, forward-plan baseline deliverable. Question:
are repeated iperf sequence occurrences present at the Windows receive NDIS
point, or only in application accounting? Existing50M failure is preserved.
Minimum missing evidence is a source-reviewed bounded receiver capture with
correlation metadata and the unchanged5s cell. First qualify native capture
control/format passively (3s, exact bench UDP filter, no generated traffic),
then review helper and the single fresh-state preparation needed for memory
admission. This is changed instrumentation, not an unchanged retry.

Root owns integration, plan and execution; corpus_audit owns only new capture
helper/watchdog; evidence_audit independently reviews fresh-state recipe and
then capture source. No new worker launches. Native capture will preserve
ETL/text/stats and fail closed on missing ownership, coverage or identity.
The4096-page admission remains unchanged. No load until capture readiness and
all existing gates pass. A fresh-state action must be specifically justified
and bounded by the existing reviewed recovery protocol; no reboot loop, no
cache-flushing or threshold reduction. Stop the cell on any original abort,
preserve failures, restore and independently assess the result. Baseline
acceptance remains separate and NOT_ACCEPTED.

Acquisition interpretation fixed before execution: CLEAN_RESTORED describes
capture control and cleanup only. Native circular ETL wrap is not yet proven
absent; retain completeness UNKNOWN/wrap_verified false unless the actual
record independently establishes coverage. Positively observed repeated
iperf sequences across deduplicated NDIS packet identities remain usable as
scoped positive evidence. Missing repeats do not establish absence, a unique
packet total or valid unique goodput. The original iperf invariant stays active.

Fresh-state method: one CPE-only software reboot through the existing reviewed
cpe_fresh_boot_memory.py (source97c26c4e... bound in the independent receipt),
after capture qualification/review. Changed acquisition needs a qualified
initial state; prior fresh-state evidence makes recovery plausible, not
assured. Keep AP untouched, original VM/config/build/RF, one submission even
on timeout,180s boot/90s association,quiet20s then20s observation. Require
result review,30/30 health and complete unchanged gates before any load.
If this preparation fails, preserve failure and do not reboot again to chase
a pass. Source-bound method review: capture-fresh-state-recipe-review.json.

## October16 01:53UTC - native watchdog qualified; CPE preparation next

Passive native control qualification is complete after two preserved failures:
8afa rejected historical project-ancestor reparse attributes before driver start;
a951 proved watchdog death coupled to the SSH controller, then exact owned
capture/filter were recovered and Stopped verified. Stage exact reviewed
sources locally on C:, archive raw artifacts back, and create only the owned
watchdog through existing administrative WMI with per-process breakaway.
No security policy, account, scheduled task or persistent service change.

Normal-stop receipt4e4b passed. New WMI controller-kill receipte08ab2a592174b8b82cc1a75ecf6f952
passed: watchdog survived controller termination, stopped at15.9386384s,
CLEAN_RESTORED/errors[], no foreign state, artifacts retained, final watchdog
absent and PktMonStopped. These are capture-control findings, not RF acceptance.
Fresh read-only preflight14dbf1b57f644d22bc33dfa14a9fef2d passed; one CPE-only
fresh-state treatment remains the next action after runtime review. Infra
coordination is extended until02:20UTC; root will release earlier at cleanup.

## October16 current decision - scoped50M survival, accounting unresolved

Independent physical review is complete: cpe-50mbps-result-independent-review.json,
SHA256658f313bc4f4f7d9fb7ae710695a19102e088f546ae42f61ef6831b6a6b51a2e.
Preserve FAIL_PRESERVED_NOT_ACCEPTED. Both radios supplied21samples/20s,
boost0/min2048, no OOM/boot/full-service-birth change, unchanged nine hashes,
firmware, VM and RF; cleanup/owned exit and bilateral30/30 health passed.
This supports only observed survival of the configured5s exposure. APminimum
4922pages/available11608KiB; CPEminimum4095pages/available9256KiB stayed above
the3072page/4096KiB abort limits. FinalCPE4071pages/16284KiB is25pages/100KiB
below4096-page NEW admission. Park additional RF; no repeated reboot or gate
waiver. Positive post-DNAT counter read was not acquired after validator refusal.

Primary-source accounting review is complete: iperf-50mbps-accounting-review.json,
SHA256a76f4122c5e8213048e7b6fe5d1f2cc10c16e37da810011709f407edb8a6a652.
ESnet3.22 receiver bytes count every read; receiver packets means maximum
sequence ID, and out_of_order also includes repeated IDs. Loss accounting can
be decremented by these arrivals. Excess765600B equals638 full-size datagrams;
simple unique reordering alone cannot explain it if counters/1200B lengths are
correct. Duplicate delivery is plausible, but its existence/origin on the wire
is UNKNOWN without independent sequence evidence. Both binaries report3.22;
exact binary/source equivalence remainsUNKNOWN. Neither loss0 nor apparent
receiver51.3Mbps is valid zero-loss/unique-goodput evidence here.

Next decisive evidence remains a bounded receiver capture for E2 / FMX-0007.
Administrative access is now CONFIRMED, not an outstanding operator action.
At01:18:44UTC the existing pinned SSH route PC -> nodo02.159 -> this Windows
PC.155 ran the owned inventory-only probe with administrator enabled. PktMon
started, all three inventory/filter/status commands returned0, no filters or
active capture existed, and the driver was restored to Stopped. No security,
credential, installation or persistent configuration changes were required.
Receipts: pktmon-admin-channel-execution.json and
pktmon-elevated-capability-probe.json. Earlier ERROR5 and both canceled normal
RunAs attempts remain preserved; pktmon-runas-retry-outcome.json records the
second attempt. Do not mistake the local medium token for absence of an
already configured administrative channel.

Independent capture review: pktmon-receiver-capture-review.json, SHA256
beae95bbb1d99440b9fff97e71febb1613bf92c0b76c05aca915e3bde44c9857,
FEASIBLE_WITH_REQUIRED_CORRECTIONS_PREPARATION_ONLY. Retain ETL, detailed
metadata/hex text and statistics; a component-filtered pcapng is insufficient.
Resolve the physical Miniport anew after driver start and deduplicate capture
appearances by capture epoch/PktGroupId/PktNumber before iperf sequence IDs.
This can identify repeated delivery at the observed NDIS point; it alone
cannot prove where duplication originated or that it existed on the wire.
The corrected proposal retains a20s watchdog and explicit capture-loss and
circular-overwrite checks. No capture or new traffic was executed.

One fresh read-only snapshot after administrative recovery confirms AP4872
free pages and CPE4071 (MemAvailable9160KiB), boost0/min2048, unchanged boots,
association and no current-boot OOM. See post-admin-readonly-radio-gates.json.
CPE remains25pages/100KiB below4096-page admission: preserve the fixed RF park,
failed50M accounting and E2 NOT_ACCEPTED. The next acquisition requires both
the corrected bounded capture implementation/review and a separately justified
fresh radio state satisfying the unchanged gate; no automatic repeat/reboot,
threshold reduction or further generic permission request is implied.

## October16 00:55UTC - fixed50M cell executed, traffic accounting FAILED

One reviewed reverseUDP50Mbps/5s/1stream/1200B cell executed after full runtime
prechecks; native client exited0. Attempt2eca9572c21a478c9d30c8df82500a07,
endpointd4d85a4e85304f8ca81c69bd1f050047. Validator correctly retained
FAIL_PRESERVED_NOT_ACCEPTED: receiver32155200bytes exceeds sender31389600bytes.
Native summary also reports receiver25750packets versus sender26158 and
out_of_order2447. Duplication, reordering and counter semantics remain under
bounded primary-source analysis; these counters do not establish valid goodput.
Do not waive the invariant, rescue the failed cell or repeat unchanged load.

Restoration completed with cleanup_problems[]; original11dBm/routes/endpoints
restored, launcher rootCLEAN_RESTORED/rc0 and all three tagged stopmarkersrc0.
Launcher correctly remainsFAIL_PRESERVED because runner returned1. Independent
physical review is checking memory/identity/health separately; any bounded
survival finding must retain the traffic-accounting failure. E2 NOT_ACCEPTED.

Parent question remains50M exposure behavior. Minimum next evidence: explain
native UDP summary counters using exact matching iperf source and held server
report, then identify whether a targeted acquisition change is necessary. No
further radio treatment is active. This is required result diagnosis, not a
new optimization branch. Receipt directory research/raw/bench/2026-10-15.

## October16 00:49UTC - AP fresh-state comparison acquired, load still pending

Infra original-association handoff met the predeclared two-minute criterion:
Gateway120/120, router120/120, five pinned SSH reads0.953..4.766s, unchanged
boot/BSSID. High latency remains (p95433ms/max724ms); no cause/cure established.
Root independently checked the raw evidence and a fresh full radio preflight.
Gateway ownership returned to FuturaMAX; no temporary Wi-Fi window is active.

Exactly ONE AP software reboot then completed bounded recovery,20s quiet,
20s bilateral observation and final snapshots. AP boot80919885-3835-4ee1-b99c-
cf78468d4ca8; CPE boot/full service births and all nine build/config hashes,
firmware/RF11/36/VHT80 and VM8192/15000 stayed unchanged. No OOM was observed.
AP free15920KiB before ->22924KiB final; CPE17296KiB. The observed AP20s
interval had boost2048/min4096 despite higher free memory: preserve this real
watermark transition; it did NOT meet loaded admission during that interval.

The single already-planned post-reboot health check at00:48:24..00:49:02UTC
returned AP30/30,CPE30/30,Gateway30/30(max133ms). Fresh snapshots AP22964KiB /
available14280KiB and CPE17296/10172KiB both show boost0/min2048 again. No VM
write, repeated reboot or repeated health-until-green occurred. Physical result
review remains pending before any50M cell; the loaded caller independently
requires the original freshness/memory/identity/RF gates at actual acquisition.

Receipts: ap-fresh-boot-14ca460d97964e578b731ccf1f135536/result.json;
radio-idle-observation-97547b6a20734bae91d0bf3a0e913b94/result.json;
ap-fresh-boot-continuation-health.json;gateway-handoff-ap-preflight-acceptance.json.
All under research/raw/bench/2026-10-15. E2 remains NOT_ACCEPTED.

## Management handoff criterion fixed October16 00:40UTC before qualification

Infra owns endpoint recovery. For a bounded management handoff require120 PC
pings to Gateway over two minutes at1Hz, zero loss and no1s timeout, with the
PC/router control simultaneous; five distributed pinned SSH hostname/boot
reads must all finish within5s. Record p95/max and actual BSSID; there was no
historical Wi-Fi p95 threshold and this does not claim indefinite stability.
Existing stream<=2s freshness,8s setupACK,10s snapshot and RF30/30 gates remain.

If a measured-better alternative requires temporary retention, use only the
reviewed endpoint-only mechanism with independent local restoration and a
maximum20min window; communicate exact start/deadline before handoff and
restore early on completion/failure. No persistent/profile/global change.
A recovered original association may qualify instead. Root revalidates at
use; no automatic E2 acceptance or load on a merely successful launch.
Orca instruction receipt msg_bf8f4bdd2764; independent AP recipe review now
PASS_WITH_LIMITS in ap-fresh-boot-continuation-review.json, SHA256
88ba813f51f02c6995f5866911a1a52f281c2fe17e07d8b2c5372bb2402e31d1.
The one review finding (missing20s quiet) was repaired before any AP action;
prior source is preserved in ap-fresh-boot-quiet-derivation.json.

## Fixed continuation - AP fresh state after management recovery

Parent E2 / FMX-0007: determine whether ONE fresh AP state restores the
unchanged admission floor before the SAME 50Mbps/5s reverse UDP diagnostic.
This supersedes the earlier no-reboot next-step note only for this bounded
changed-state comparison. Infra owns Gateway recovery; wait for its evidence
and stable pinned management before any AP treatment.

Evidence: fresh AP-only 20s/21-sample idle observation stayed3980Normalpages /
15920KiB, below4096pages. Paired PCP accounting explains2152 of2200KiB of the
fall arithmetically, but does not establish a leak, usable budget or safe drain.
No useful owned-file cleanup or proven local-PCP idle/stat_refresh drain exists.
Decision review: ap-headroom-pcp-decision-review.json (October16UTC).

Reuse ap_fresh_boot_memory.py with a current source-bound independent review.
Exactly one AP software reboot,180s wired recovery,90s CPE reassociation,
20s quiet then20s bilateral observation. Preserve CPE boot/full daemon births,
nine hashes, firmware version, RF11/36/VHT80 and VM8192/15000. No CPE reboot,
VM change, cache deletion, flash or automatic load. The caller's PASS means
fresh-state comparison only; require fresh bilateral30/30 health and ordinary
loaded preflight separately. Fresh pre-cell BOTH-role Normalfree>=4096pages,
MemAvailable>=8192KiB,boost0/min2048 and all existing source/TTL/cleanup gates
remain unchanged. No currentboot OOM is allowed.

Stop/park: if one fresh state or required prechecks still fail, preserve the
negative result and park50M; no repeated reboot until green and no lower floor.
If all gates pass, execute exactly the already reviewed50M/5s cell and restore;
review actual evidence before choosing another exposure. E2 is NOT_ACCEPTED.

## Active continuation - October15 management recovery for E2

Parent E2 / FMX-0007 fixed50M/5s diagnostic remains pending. Operator again
requires execution through available diagnosis, not a status-only stop.
Question: can management availability be recovered with an existing safe
endpoint path or minimal bounded endpoint-only treatment while keeping
independent wired radio observation and all RF/memory gates intact?
Known: Gateway direct Wi-Fi ping is unstable while PC/router control is<1ms;
AR9287/ath9k has power saveoff and PCIpoweron. Kernel records an HT-to-legacy
beacon-mode disconnect at18:58:49 followed by roaming between two BSSIDs.
That event does not prove the earlier18:56 timeout cause or explain all latency.

Minimum missing evidence: current cached AP alternatives, bounded event/latency
correlation and feasibility of a temporary recovery with exact restoration.
Use existing tools; no new orchestration platform or baseline bypass. First
read only; record a concrete treatment and review before any mutation. No
production AP/router configuration, firmware, credential or CPE VM change.
Stop only for a proved external dependency/material decision or specific
uncovered authority after completing the necessary reviewable preparation.

## October15 follow-up - management Wi-Fi path isolated

Operator confirms Gateway remains on the PC management Wi-Fi and connected
by Ethernet to NanoLoco. Read-only checks at23:18UTC confirm correct routing:
PC192.168.100.155 is reached directly over Gatewaywlp2s0/.100.179; Ethernet
is .1.170/24, and its default route has lower priority (metric20100 versus
Wi-Fi600). No current evidence that the Nano path diverted management replies.
GatewayWi-Fi is2412MHz/40MHz with power_saveoff; current boot is unchanged.

Concurrent controls: PC->router.100.1 ten/ten replies all<1ms;
Gateway->same router explicitly over wlp2s0 ten/ten replies15.411..978.578ms,
mean498.043ms. PC->Gateway earlier eight probes had7replies,2..649ms.
During the short Gateway control, station TX packet counter grew29 and TX
retry counter54; this is raw counter movement, not a packet-loss percentage.
Signal samples varied -70 to -57/-58dBm; no single RSSI explains the cause.
GatewayCPUload0.18 and MemAvailable1450268KiB do not suggest observed host
resource exhaustion. Root cause among adapter/AP/RF conditions remainsUNKNOWN.

Conclusion: management latency/loss is reproducible without the benchmark,
localized to the Gateway Wi-Fi access path by these controls. Both interfaces
being connected is not itself evidence of a routing conflict. No configuration,
RF treatment, VM write, new benchmark or acceptance-gate change was performed.
The earlier radio-memory and health blockers remain separate and unaccepted.
Receipts in research/raw/bench/2026-10-15: gateway-management-explanation-live.json,
gateway-management-path-isolation.json and pc-management-router-control.json.
Next: resolve management Wi-Fi instability before any further loaded diagnostic;
then recheck radio health/headroom under the existing fixed recipe.

## Current blocker - October15 50Mbps preparation aborted before load

E2 / FMX-0007 remains NOT_ACCEPTED. Attempt089d5ab1 / endpointcffc4719
FAILED before observers/client: CPE wired iw/route inspection timed out via
Gateway. Subsequent Gateway SSH/banner attempts and three PC ICMP requests
failed. No50Mbps throughput or memory-under-load result exists for this attempt.

The existing endpoint confirmed TAGGED_STOP/CleanupVerified; radios reported
restoration verified. Launcher later reconnected, sent all tagged stop markers,
and received rootCLEAN_RESTORED/rc0 with matching identity. This confirms
cleanup, not experiment acceptance. Original CPE posthealth/final snapshot
failed and are retained. Separate late health read found AP29/30 and CPE29/30
(ping rc0 does not satisfy30/30). Gateway answered30/30 but RTT3..771ms,
mean248ms; another SSH read then timed out at22:00:59UTC. Management stability
is therefore unresolved. A later NetworkManager reassociation at21:58:49..52
is confirmed, but does not establish the cause of the earlier21:56 outage.

Late readback shows both radios11dBm, associated, no OOM, VM8192/15000.
AP Normalfree4012pages/16048KiB is below the4096page/16384KiB admission;
CPEfree4532pages/18128KiB. Both retain boost0/min2048pages. Do not lower gates,
repeat the load, change VM, reboot again or infer that reconnect means stable.

Exact next action: restore a reliable Gateway management path, verify bilateral
30/30 health and fresh allocation headroom, then reassess the SAME fixed50M/5s
recipe below. No new load currently runs. The operator was asked whether the
Gateway is still powered/connected; current instability is an external dependency,
not an exhausted repair count. Root has made no Wi-Fi configuration changes.
Receipts under `research/raw/bench/2026-10-15/`: `cpe-low-load-launch-089d5ab14dbe49659405fba3e3cca852.json`,
`cpe-50mbps-postfailure-health-089d5ab1.json`, `gateway-transient-access-089d5ab1.json`
and `gateway-management-link-089d5ab1.json`. Failed acquisition and later
restoration/health evidence remain distinct.
Independent review `cpe-50mbps-failure-independent-review.json`
SHA2563b6dbebbb9fbeef77bc7745edfa644880f8cf9300b805ff960349e6dcdb2a395
confirms39events with no observer/client; exact later snapshot comparison
matches boots/full daemon births, nine hashes, VM/RF/firmware and no OOM.
Its conclusion is FAIL_PRESERVED_BEFORE_LOAD_LATE_HEALTH_FAILED; no retry now.

## October15 measured result - 10Mbps short interval survived

E2 / FMX-0007 remains NOT_ACCEPTED. Attemptfac963f9 / endpointc5dfabea
completed ONE reverse UDP10Mbps/5s/1200B cell. Receiver6255600bytes,
5213packets over5.001992s =10.004974Mbps, native reported loss0 and jitter
0.108822ms. Sender6262800bytes/5219packets over5.009673s differs by six
packets/7200bytes; preserve count/window discrepancy, no zero-loss claim.

Both radios produced21samples over20s with Normalboost0/min2048pages,
unchanged boots/full daemon births, VM8192/15000 and no new OOM. AP free/
available16404/9872KiB stayed flat; CPE18128..18140/10840..10848KiB.
RF0dBm and15/15 precheck passed. Restoration verified11dBm, exact routes/
NAT, tagged endpoint stop, rootCLEAN_RESTORED/rc0,30/30 posthealth and
nine identity hashes per radio plus firmware version. Independent review
PASS_WITH_LIMITS: `research/raw/bench/2026-10-15/cpe-10mbps-result-independent-review.json`
SHA2565c3b059cf889ed08c28caadb0cb325dfcf8b28531968f0a739dedaff797cbe6b.

Next decisive diagnostic is ONE50Mbps/5s with only rate changed, fixed in
BENCH_PLAN before implementation. This probes historical failure rate with
shorter exposure; it neither proves30s survival nor cures the earlier OOM.
No baseline reopening or automatic ramp follows from this result.

## Pending stable access and headroom - fixed50Mbps short memory diagnostic

Parent E2 / FMX-0007; original forward-plan link baseline. Question: does the
historically failing50Mbps rate survive a five-second interval with current
fresh-boot state and unchanged VM8192/15000? Accepted scoped1M and10M cells
show no OOM, daemon loss or watermark boost. Missing evidence is ONE50Mbps/5s
interval; this cannot answer30s survival or establish E2 baseline acceptance.
Independent physical reviewer recommends this bounded next diagnostic.

Fixed BEFORE implementation/acquisition: reverse UDP50Mbps,5s,1stream,1200B;
Gateway->CPE->wireless->AP->PC. Only offered rate changes from10M. Preserve
exact10M source/review bytes and results. Keep temporary0dBm, RSSI<=-55dBm,
15/15 precheck,20s bilateral wired observer, Normalboost0/min2048pages both
before and during load, admissionfree>=4096pages/available>=8192KiB,
abortfree<=3072pages/available<=4096KiB,2s freshness,5s native/client8s bound.
All boot/full daemon birth/config hash/VM/firmware identity checks and exact
11dBm/routes/NAT/endpoint/root cleanup plus30/30 posthealth remain required.

Stop/park on any gate refusal, changed watermark, floor, missing stream,
identity or transport failure; preserve failure and restore. AP admission
margin was20KiB; never lower threshold to obtain a run. No automatic ramp,
extra cells, VM writes, reboot, flash or baseline in this recipe. Acceptance
is this single diagnostic with independent review; E2 remains NOT_ACCEPTED.

## Completed second load level - October15 fixed10Mbps memory diagnostic

Parent E2 / FMX-0007. Question: does a tenfold increase from the accepted
single1Mbps/5s diagnostic introduce sampled memory pressure or daemon loss?
The1Mbps cell had flat sampled MemFree16404/18140KiB, no OOM and complete
restoration. It does not answer prior50/100Mbps failures. Independent reviewer
finds ONE10Mbps/5s diagnostic defensible under existing section12.2 authority.

Fixed BEFORE implementation/acquisition: reverse UDP10Mbps,5s,1stream,1200B;
Gateway->CPE->wireless->AP->PC, same temporary0dBm/RSSI<=-55/15pings recipe,
VM8192/15000 and build unchanged,20s bilateral wired observer. Preserve prior
1Mbps source bytes, review and raw results. Strengthen the guard: admission
AND monitoring require Normalboost0 and min2048pages; abort any transition
because the earlier CPE failure had boosted min16384KiB. Keep existing
admissionfree>=4096pages/available>=8192KiB and abortfree<=3072/available<=4096,
freshness2s, native5s/client8s bounds and every cleanup/identity/hash check.

Acceptance only this single diagnostic plus independent review, never E2
baseline acceptance. Stop/park on any changed watermark, floor/stream/identity/
transport failure; restore and preserve evidence. AP current admission margin
is only20KiB, so a fresh gate may refuse; do not lower it. No ramp loop, extra
cells, reboot, VM write or revised failure acceptance in this recipe.



## October15 measured result - one bounded loaded interval survived

E2 / FMX-0007 remains NOT_ACCEPTED. Attemptc806b09c / endpointcf98af6b
completed ONE reverse UDP1Mbps/5s/1200B cell (Gateway->CPE->AP->PC).
Native receiver:626400bytes/522packets,1.0006666Mbps over5.007862s,
reported loss0 and jitter0.34085ms. Sender627600bytes/523packets differs
by one datagram; do not erase that tail/count difference or claim a repeated
zero-loss benchmark. This is a scoped survival observation, not a performance gain.

Both radios produced21samples over20s with unchanged boots/full daemon births,
no OOM and unchanged VM8192/15000. Sampled AP MemFree16404KiB/available9872KiB
and CPE18140/10848KiB were flat. The RF treatment passed the inherited0dBm,
RSSI<=-55dBm and15/15 precheck. Restoration verified11dBm, exact route/NAT
cleanup, endpoint exit, Gateway CLEAN_RESTORED/rc0,30/30 posthealth and final
configuration/module/kernel-note hashes and firmware version unchanged.

Failures1f3f0491 (observer abort before load) and7fd8f4cc (Gateway freshness
rejection before RF/load) remain failed. Minimal repairs were independently
reviewed and natively qualified: scope ucode global errors to each dmesg call;
measure Gateway request age after taggedGO on an established pinnedSSH.
Neither repair weakens freshness/memory thresholds or reopens the baseline.

Actual receipt: `research/raw/bench/2026-10-15/endpoint-cf98af6bd7c14885bc64c8e0836be834/low-load-result.json`.
Independent physical review PASS_WITH_LIMITS is recorded in
`research/raw/bench/2026-10-15/cpe-low-load-result-independent-review.json`.
Next question under the same
E2 diagnosis: does one fixed10Mbps/5s cell preserve headroom? Assess this
changed load independently, strengthen abort on any Normal-zone watermark
boost/minimum transition, and retain all original safety/restoration gates.
No unattended ramp or VM treatment is authorized by this diagnostic result.



## Completed first load level - October15 minimal CPE loaded-memory diagnostic

Attempt7fd8f4cc / endpointcba7c917 FAILED before RF guards, observers or client.
Repaired observer had already passed21samples/20s per radio, preserved in9137c706.
The next Gateway combined status had age0.7903s plus whole SSH elapsed1.422s,
exceeding the unchanged2s freshness bound. Terminal cleanup was likewise rejected
for age1.3996s+SSH1.906s; the independent root process stream nevertheless reported
CLEAN_RESTORED with exact identity, zero cleanup errors and rc0. Keep both failures;
this is transport/acquisition evidence, not a loaded-memory measurement.

Necessary minimal repair: in the standalone diagnostic only, establish pinned
SSH with the already-qualified transport-ready/GO handshake, then measure the
request/receipt interval from GO. Remote record age still applies and the same
2s bound must reject late/missing data. Record setup separately with its own8s
bound; never assume zero transport time. Do not change root guard, main baseline
runner, VM, RF method or memory/freshness thresholds. Review exact delta and
negative fixtures before another single cell. The original baseline stays blocked.


Attempt1f3f0491 / endpoint3d8808fd FAILED BEFORE CLIENT: RF gate and15/15
stability passed, but AP observer aborted atseq3 with dmesg error/empty/truncated.
No iperf client was started. Both radios restored11dBm, exact route/NAT/network
cleanup verified, final boots/full daemon births/hashes/VM unchanged and no OOM;
a delayed read confirms both owned observer PIDs exited. Partial streams remain
FAIL. AP sampled MemFree16452KiB; CPE19760->19676KiB before closure.

Necessary support repair reassessment: loaded acquisition still requires valid
bilateral OOM observation; no simpler already-qualified substitute exists.
An AP read-only controlled probe confirms fs.error is global/sticky: an unrelated
missing proc read makes a subsequent successful11477-byte dmesg/rc0 appear to
have ENOENT. Clearing that prior global error before popen returns the same valid
output/errornull. Original abort cause is INFERRED, not established retroactively.
Minimal repair scopes error state to the dmesg operation and retains read/close/
null/truncation rejection. Preserve old sources/failure; independently review and
qualify the repaired20s idle stream before another single diagnostic attempt.
Do not relax admission/abort thresholds or use this as baseline acceptance.


Parent: E2 / FMX-0007 in the original forward plan. Question: after fresh boots,
does a tiny fixed forwarding load preserve both radios' memory headroom and
wireless processes under the unchanged VM/build and existing low-power RF recipe? Existing evidence: the
prior CPE OOM at UDP100/50 persists as failure; new quiet endpoints show stable
free18120/19548KiB and unchanged daemons. Minimum missing evidence is ONE
instrumented loaded interval, not another idle poll or full baseline retry.

Fixed recipe BEFORE acquisition: retained failing up direction, UDP1Mbps,5s,
1stream,1200-byte datagrams, explicit iperf -R: Gateway->CPE->wireless->AP->PC.
PC initiates the TCP control session through AP DNAT; CPE transmits the data.
No bulk connectivity probe, opposite-direction cell, ramp, VM/build change
or reboot. Preserve the existing RF safety recipe: temporary0dBm on both
radios, fresh RSSI<=-55dBm and15/15 stability pings before load, restore11dBm.
This corrects the pre-implementation no-RF-write and direction shorthand,
which conflicted with the inherited safety contract; no acquisition preceded
the correction. The precheck pings are traffic, but not a bulk load. Compose existing
reviewed endpoint/network cleanup and qualified bilateral wired observer;
keep the baseline runner's KNOWN_CPE_OOM_UNRESOLVED gate intact. This narrow
diagnostic is authorized by section12.2 and the existing E2 diagnosis plan;
independent review of exact implementation must precede device I/O.

Before starting the owned client require at least two fresh complete samples
per radio, unchanged boot/full daemon births, no OOM in either fresh boot,
VM8192/15000, Normal free>=4096pages and MemAvailable>=8192KiB. During the
single cell abort on Normal free<=3072pages or MemAvailable<=4096KiB, new OOM,
identity/policy change, stale/missing observation, transport/parser failure.
Observe for20s total and retain native5s client bound plus a local deadline.
One-Hz observation cannot guarantee prevention of subsecond OOM.

Acceptance: exact offered-load command and endpoint result retained; complete
fresh bilateral observations around the cell; no OOM/boot/daemon change;
owned client/observers exit; tagged endpoint/network/radio route cleanup and
settled health with original hashes/config/firmware verified. PASS means
only this diagnostic survived; E2 stays NOT_ACCEPTED and no automatic ramp.
Stop/park: any failure preserves evidence, stops owned work and restores;
review the changed evidence before another treatment. Any VM/security/PoE
exception needs its own authority; no such action is proposed here.

## October15 measured result - fresh boots and quiet memory

E2 / FMX-0007 remains NOT_ACCEPTED. One AP software reboot and one CPE
software reboot restored larger idle headroom, with unchanged configuration,
RF11dBm/channel36/VHT80, VM8192/15000, nine on-disk identity hashes per radio
and reported firmware version. AP's first post-reboot CPE snapshot timed out:
that FAIL remains preserved; a later read-only followup passed without another
reboot. Loaded-module byte identity remains UNKNOWN where build ID is absent.

CONFIRMED: CPE comparison707c6652 passed, with AP boot/full daemon births
unchanged. CPE MemFree13748 before reboot versus20060KiB final; a1652KiB
post-reboot-to-final drawdown remains unattributed. In the later quiet interval
fb8380f8, MemFree was18120->18120KiB AP and19548->19548KiB CPE across
30.13/30.14s. MemAvailable11108->11112KiB AP and12096->12096KiB CPE.
Normal free4530/4887pages, min2048, high3072, boost0. Full daemon births and
boots were unchanged, dmesg contained no OOM, and wireless-interface data
RX/TX counters did not increase. Wired management traffic did occur.

INCONCLUSIVE: these endpoints do not exclude intermediate drops, establish
absence of a leak, attribute the earlier drawdown to the observer, or establish
loaded survival. Quiet and observer intervals differ in boot age/instrumentation.
Independent quiet review PASS_WITH_LIMITS; evidence lives under
`research/raw/bench/2026-10-15/quiet-memory-independent-review.json`,
`cpe-fresh-boot-state-independent-review.json`, and `ap-fresh-boot-state-finding.json`.



## Completed quiet interval - October15 quiet memory interval

CPE fresh-boot comparison707c6652 completed with unchanged AP identities,
settings and no new OOM. CPE final MemFree20060KiB vs13748 before reboot;
its post-reboot snapshot21712?final20060KiB drawdown is not explained by the
small observed Cached/Slab/Anon deltas. No leak/consumer/cure is established.
Next minimum diagnostic under the same E2 parent: ONE persistent wired SSH
session per radio, no1Hz observer, native shell snapshots only at start/end
of a30s quiet interval. Read uptime/meminfo/zoneinfo/netdev/sockstat/daemon
births/dmesg; hold all VM/RF/build settings and do not reboot or start load.
Record complete reads and unchanged boot/daemons/OOM, plus memory/network
counter deltas. Compare to retained observer intervals with boot-settling and
collector differences explicit; do not claim causal equivalence or a leak.

## Completed CPE state comparison - October15 CPE fresh-boot memory comparison

Parent E2 / FMX-0007 remains NOT_ACCEPTED. The single AP software reboot
recovered over wired SSH and CPE association. Its first post-reboot CPE
snapshot timed out and remains FAIL_PRESERVED. After the AP settled, a new
read-only interval completed21 samples/radio over20s and final identity/hash/
policy/RF/OOM checks passed; no second reboot was performed. AP MemFree was
10884KiB before versus18712KiB at final followup, MemAvailable5256?11692KiB.
This is a state difference, not proof of a leak, allocation cause or load cure.
See `research/raw/bench/2026-10-15/ap-fresh-boot-state-finding.json`.

Next single changed-state diagnostic: ONE software reboot of the CPE using
its independently verified wired Gateway path, with the AP left running.
This remains the same E2 memory question under section12.2 and the authorized
lab recovery workflow; it does not grant VM, flash, physical-power or load
changes. The CPE experienced both OOM kills, so its fresh-state comparison is
still missing even after the AP result. Reuse the reviewed AP recipe, swap
only the reboot target/survival roles, and preserve its180s SSH/90s association
limits, hashes, fixed RF11dBm/channel36/VHT80 and VM8192/15000. Allow20s quiet
settling after association before collecting the same20s idle observation.

Acceptance requires a changed CPE boot, unchanged AP boot and wireless process
births, same configuration/kernel-note/module hashes and radio firmware version,
no new OOM and complete fresh observation with owned processes exited. A failed
recovery stops after the single submission; no second reboot or PoE action.
Loaded-byte module identity remains UNKNOWN where sysfs provides no build ID;
on-disk hashes and observed runtime identities are the explicit evidence scope.
The original load failure and known-CPE-OOM barrier remain intact regardless
of idle-memory improvement. After this comparison, decide the minimum safe
next treatment from the measured headroom; do not retry the failed baseline.

## Completed AP state comparison - October15 AP fresh-boot memory comparison

Parent E2 / FMX-0007 remains NOT_ACCEPTED. The bilateral idle observer now
completes21 samples over20s per radio (receipt5774bce4); no new OOM, boot or
wireless-daemon identity change, SSH exits0 and both owned processes exited.
Mean snapshot duration is166ms AP /216ms CPE, RSS peaks1396/1416KiB; this is
fresh idle observation, not negligible loaded overhead or baseline acceptance.
AP Normal free2724pages remains below the existing AP-only diagnostic floor
of3072pages. CPE free3708pages does not resolve its two loaded OOM failures.

Next bounded question: is the AP's reduced idle headroom persistent after a
fresh software boot, or dependent on accumulated runtime state? Perform ONE
AP-only software reboot under the existing authorized lab recovery workflow
and section12.2, after confirming independent wired management for both radios,
unchanged build/config and matching persisted/current RF settings. Capture
pre/post memory and the same20s idle observer. This is not a cold/power-cycle
experiment and does not change firmware, VM policy, RF configuration or load.

Acceptance of this diagnostic requires a changed AP boot ID, same pinned
identity/build/config/policy/RF settings, re-associated CPE, unchanged CPE boot
and wireless process births, and complete fresh idle observation with no new
OOM and both observers exited. Permit up to180s for AP SSH recovery and90s
for association; failure preserves evidence and stops this treatment without
a second reboot, force reboot, PoE action, firmware change or gate release.
An idle-memory increase is only an observed state difference, not leak proof
or permission to retry baseline. The known CPE OOM and AP factor0 authority
remain separate unresolved gates. No generic 'continue' is needed for this
already-authorized bounded lab diagnosis; new VM/physical-power actions still
require their specific authority.

## Completed support step - October15 continued E2 memory diagnosis

Operator explicitly requires continuous execution of the existing plan, not
ending at a diagnosis or helper checkpoint. Parent remains E2 / FMX-0007.
Question: can we observe both radios' memory and wireless-process survival
without adding enough observer pressure to invalidate the next acquisition?
Existing evidence: two confirmed CPE OOM kills; the second occurred with
instantaneous boost0/free7180kB below min8192kB. Live sysctl init selects8192
for managed memory56120kB; CPE tmpfs uses400kB. No proof of a leak or a remedy.

Minimum necessary support: reuse the memory/identity invariants in one bounded
read-only observer per radio; add wpa_supplicant and OOM-change detection,
which were absent from the failed block. First qualify observer cost for20s
without test load. Preserve absent VM counters as UNKNOWN, use conservative
kernel-log change evidence, and retain the full-load execution block. No new
platform, source build, VM policy write or RF/load retry is implied.

In parallel, reconcile held exact-build provenance and existing October10/11
allocator findings with the new CPE failure; do not repeat completed AP
research or attribute another module's buffers to this CPE. Then select the
minimum next diagnostic from the evidence. Stop/park only dependent physical
work if its actual authority, recovery or headroom gate cannot be satisfied;
complete all safe diagnosis/integration/review that remains necessary first.


## Current checkpoint - October15 E2 physical block rejected: CPE OOM

Parent: E2 / FMX-0007 external-endpoint baseline. Question: can the fixed
Linux-endpoint recipe sustain the safe partial baseline without wireless
process failure? Result: **QUALIFIED_NEGATIVE_CPE_OOM; E2 NOT_ACCEPTED**.
This checkpoint supersedes earlier credential/readiness/retry instructions.

The operator-provided credential is securely stored and verified in the vault
item documented below. PC source alias and Gateway route/admission worked.
Bilateral 0dBm RF checks passed; the exact source/DNAT rule counted four initial
connection packets. Block `bf908481fcb448cc9d35da695d1ef6bb` completed two cells,
then up/UDP50 failed with control connection reset. None is accepted baseline.

CONFIRMED: the CPE kernel killed hostapd PID1434 and wpa_supplicant PID1435.
INFERRED uptime/UTC alignment places those kills during up/UDP100 and up/UDP50.
The intervening down/TCP4 result is contaminated by the prior OOM. First OOM:
Normal free11988kB, boost8192kB, min16384kB. Second: free7180kB, boost0kB,
min8192kB; no swap. Removing boost alone is NOT a demonstrated remedy.
The exact pressure mechanism remains UNKNOWN. This is Linux allocation and
wireless userspace survival evidence, not a firmware-performance improvement.

Restoration verified: both radios11dBm, owned routes/NAT removed, Gateway
route/firewall CLEAN_RESTORED, owned server stopped without restart, both
radios30/30 posthealth replies and unchanged build/config fingerprints.
These checks do not undo the OOM or rescue the measurements. All failed
support attempts and raw physical observations are preserved.

Containment: `KNOWN_CPE_OOM_UNRESOLVED` blocks runner CLI, direct acquire()
and all four launch wrappers before credential/device I/O.60 local fixtures
and four instrumented wrapper checks PASS; independent containment review
found no blocker. These validate containment only. No background runner.

Next decisive evidence: a bounded CPE memory diagnosis must establish
allocation headroom and stable wireless daemons before another baseline.
Read-only/offline diagnosis remains authorized. The AP-specific factor0
experiment does not authorize CPE VM writes; retain its separate gates and
the original recovery requirements. No VM policy was changed in this block.
E3 remains WAIT_E2. Stop further baseline load until this failure is resolved.

Evidence: `research/raw/bench/2026-10-15/gateway-cpe-oom-finding.json`,
`gateway-cpe-oom-independent-review.json`,
`gateway-cpe-oom-allocation-context.json` and
`gateway-cpe-oom-containment-validation.json` in that same directory.


### October15 follow-up - CPE memory diagnosis before further load

A new read-only observation without test traffic found MemAvailable7792-7800kB
and stable hostapd/wpa_supplicant PID/start identities across10.22s (three
samples). This short interval does not establish load headroom or exclude a
leak. Selected VM event counters were absent: UNKNOWN, not zero. The exact
origin of VM8192/15000 is unresolved by the checked sysctl files and scoped
repository search. No VM change or new RF load.

Next: resolve the exact-build kernel/driver memory budget; require both-radio
OOM/daemon survival checks and bounded abort/restoration; then qualify a short
low-load diagnostic before resuming repetitions. Any CPE VM treatment retains
its existing authority boundary. E2 NOT_ACCEPTED. Receipt:
`research/raw/bench/2026-10-15/gateway-cpe-memory-next-decision.json`.

### October15 combined status transport repair

The canonical-format lease reached READY and withdrew/restored successfully.
The adapter then failed before any radio mutation because root status age
0.7128s plus conservative SSH receipt1.313s exceeded the unchanged2s limit.
Receipt d09064a074be4e8085c99b5f174eff85 retains INCOMPLETE_NOT_ACCEPTED;
endpoint tagged stop, radio baseline check and root CLEAN_RESTORED all passed.
The minimum next change combines the two independently hash-verified status
reads in one pinned SSH invocation, recomputing both ages at remote completion
and retaining the full receipt bound. No threshold relaxation, RF load,
heartbeat-frequency increase or unchanged retry. Fixture and independent
review precede a fresh lease. This support change exists only to acquire E2.

### October15 live route/rule serialization correction

The next guarded attempt applied its exact lease but refused verification:
iproute2 rendered a host route without /32 and mapped protocol99 to openr;
iptables serialized options in canonical source/destination/interface order.
Its failed cleanup receipt is preserved. An immediate ownership-checked
recovery used numeric protocol output, exact source/destination/MAC interface,
metric49016 and unique comment; deleted only the owned two rules and route,
then read back empty exact state (gateway-exact-normalization-recovery.json).
No radio load or RF mutation occurred. The minimum repair for parent E2 reads
numeric route protocols, recognizes the exact host/32 and uses canonical
iptables ordering. Real-output regression and independent review precede a
fresh-tag attempt; no acceptance criterion or network scope is relaxed.

### October15 live network lease identity correction

First sudo guard refused before any mutation because iproute2 IPv4 address
JSON omits link MAC on the real Gateway. Separate link JSON confirmed the
expected MAC. Minimal parser fix joins exact interface/positive ifindex,
retains IPv4/up/source-admission checks, and passed independent root review
plus25 fixtures after the new real-output regression first failed. The
original NO_MUTATION receipt is retained. Retry uses a fresh tag/private
directory and a new six-file hash-bound review; no unchanged retry or gate
relaxation. Parent remains the safe E2 nine-cell block.

### October15 credential dependency resolved by operator

The operator supplied the Gateway account/sudo credential and explicitly
requested durable secure storage and continuation. Stored and read back in
Vaultwarden item `Infra Gateway NV55C omarchygwy - ggorbalan sudo`, ID
`b21468d1-3cae-48a5-8a3d-19f8c6325283`; pinned-host `sudo id -u` returned0.
Only this pointer belongs in project documents. Read the exact vault item
through the documented bw-ensure procedure; do not ask again or use nodo02's
credential. No password rotation, sudoers or SSH security change occurred.
The previous missing-credential checkpoint is superseded. Resume the reviewed
bounded Gateway lease and safe E2 block with the original RF/restoration gates.
Receipt: `research/raw/bench/2026-10-15/gateway-credential-pointer.json`.


## Authoritative active course - 2026-10-10

### October15 explicit execution correction - source alias applied

Operator explicitly orders this session to add the PC IP and advance. Direct
`New-NetIPAddress` succeeded despite the Python process reporting non-admin;
the previous privilege inference was wrong. `.1.155/24`, SkipAsSource=true,
ActiveStore is now Preferred on physical NIC27; original`.100.155` remains.
Pinned direct AP SSH bound to`.1.155` now succeeds.

Parent remains E2 safe external-endpoint acquisition. Minimum missing support
is the Linux endpoint ownership adapter and a bounded Gateway return-route/
source-admission lease, replacing the old Windows notebook implementation.
Reuse the reviewed radio guard, RF gate, cell acquisition and restoration;
do not start a new optimization branch. New files are limited to the Linux
iperf supervisor, exact Gateway network lease and their integration/tests.
Independent fixture/method review is required before live use. Gateway sudo
actually rejects the read-only route/rule checks with password-required;
the existing Infra access-handoff thread was asked for the documented
credential item/pointer only, never a password. Do not alter sudoers or SSH
forwarding. No unchanged UDP200 down cell or factor0 policy write is included.

Progress: PC alias and direct pinned AP/CPE access PASS. Fresh AP sample577ms
still has Normal free2667 pages: factor0 remains blocked independently. Real
Gateway Linux supervisor launch/status/tagged-stop PASS with owned cleanup;
no RF traffic. Infra confirms no verified sudo credential pointer exists.
The exact900s route/admission launcher is staged in the private Gateway run
directory recorded by gateway-network-lease-staged.json; it has not run.
No password is requested over chat or copied between lanes. Next executable
physical block uses nine safe30s cells, fixed original block1 seed20261010,
with original bilateral0dBm RF/health gates and post-restoration fingerprints.
Independent integration review PASS_WITH_LIMITS (six-file hash bindings);
local sudo launch still precedes acquisition. See gateway-continuation-summary.json
and gateway-six-file-execution-review.json under research/raw/bench/2026-10-15/.

Stop/park on unavailable legitimate sudo access, identity/source-admission
failure, RF/peer/build mismatch or incomplete cleanup. Run the safe cells
when these actual prerequisites pass; do not require a generic admin token
for an operation whose native capability has already been demonstrated.

### October15 physical continuation - Gateway behind NanoLoco

Current result: NOT_READY. Private runtime and loopback preparation completed;
see `research/raw/bench/2026-10-15/gateway-readiness-summary.json`. The selected
Windows alias is not yet observed. Gateway needs privileged exact return-route
and source-specific port5201 admission before the Linux adapter can be
qualified on the actual data path. No radio workload or VM/RF change occurred.

Operator confirms Gateway Ethernet connects to NanoLoco5AC and LAP120 is on
the network, and directs continuation. Parent: E2 / FMX-0007 external-endpoint
baseline. Question: can this actual topology acquire the declared safe cells
with verified endpoint identity, radio health and exact restoration?

Read-only observations: Gateway `.1.170` reaches Nano `.1.3`; Nano is the
expected OpenWrt24.10.4 board and associates with expected LAP120 BSSID.
AP identity was read through Nano; its presented SSH fingerprint matches the
existing Windows pin. Both radios remain11dBm/5180MHz/80MHz, VM8192/15000.
Windows `.100.155` lacks the frozen `.1.155` secondary address and this session
is not elevated. Gateway lacks iperf3/netperf; its SSH forwarding is prohibited
and that restriction remains intact. Ordinary nested SSH commands work.

Minimum enabling work: build pinned traffic tools inside a private Gateway
directory, qualify loopback only, and adapt the endpoint identity contract
without fabricating the old Windows READY response. The operator was given
the exact temporary Windows alias command; no alias was added here. Check
fresh AP Normal-zone headroom before any load: observed MemFree10684kB is
not itself a successful memory gate. Preserve failures in
`research/raw/bench/2026-10-15/`.

Stop/park: absent privileged source setup, endpoint ownership/binding,
build/peer/RF/headroom or exact-restoration proof prevents acquisition. Do not
run the unchanged OOM cell, mutate VM policy, lower thresholds or claim E2
acceptance. Private tool compilation is support work only. Continue remaining
safe readiness work while the explicit Windows topology action is pending.

### October15 operator continuation - coordination transfers from AGY

16:20UTC access amendment: Infra identified Gateway `omarchygwy`/`ggorbalan`
at Wi-Fi`.100.179`, distinct from nodo02`.159`. Own pinned SSH read-only
check passed; Ethernet currently`.1.170/24` rather than the guide's older
`.100.174`. The endpoint-identity question below is resolved by this receipt:
`research/raw/session-continuity/2026-10-15/omarchygwy-ssh-readonly-162014.json`.
Traffic topology/recipe and fresh E2/RF/headroom gates remain unverified.
No live factor-0 authority, load or host/network mutation follows from access.

The operator directs the project to continue in this Codex conversation after
AGY quota exhaustion. Recent AGY visible history and night-worktree current
state were recovered read-only; details and evidence are in
`docs/SESSION_CONTINUITY_2026-10-15.md`.

One active deliverable: E2 readiness and its existing qualified diagnostic,
not more generic RE1 helpers or a second literature run. Night-worktree
`research/raw/e2-memory-diagnostic-review-repair-20261015.json` closes the
offline method-review gap as PASS_WITH_LIMITS after preserving initial FAIL.
The actual endpoint/topology remains unresolved: ask which Omarchy and how
it is connected, then prepare the exact route/recipe and required gates.
Do not infer approved AP factor-0 writes, traffic or alternate-host topology
from this coordination transfer. The night plan's explicit treatment gate
and all E2 acceptance criteria remain. E2 NOT_ACCEPTED; E3 WAIT_E2.

### October15 operator task - AutoResearchClaw evidence synthesis (offline deliverables complete)

Parent: original forward-plan firmware/control-boundary research and E2/FMX-0007
baseline interpretation (experiment identifier FMX-0007). Question: which prior
and 2024-2026 literature techniques are executable on the exact QCA988x/AR9342
stacks, given RE1 static findings and the October12 physical receipts?
Existing evidence: sources/link registry, all extracted reports, audit ledgers,
night-worktree IDA closure and UMAC_DATAPATH, October12 benchmark files.
Minimum missing evidence: complete hashed corpus inventory and deduplication,
fresh reproducible literature search, claim-level crosswalk to actual control
boundaries, quantitative bench reanalysis, and independently checked synthesis.
Use the requested AutoResearchClaw clone in tools/research/AutoResearchClaw,
an isolated Python environment, and its direct literature APIs if appropriate.
Outputs: research/autoresearchclaw/ master synthesis, classified JSON/Markdown
technique matrix and complete run receipts. This task authorizes local research
installation/analysis, not a new physical treatment or device access.
Stop at verified artifacts with explicit coverage/missing-evidence limits;
retain E2 NOT_ACCEPTED and all custom-MAC/production/recovery gates. No wireless
gain may be inferred from literature, successful installation or static code.

Result: complete requested available-corpus ingestion (600 source records,
69 files), 36 direct-client queries (108 backend pairs accounted), 1,146
candidate groups and a 24-technique matrix with explicit target gains UNKNOWN.
Primary/source reviews distinguish fulltext, metadata and retrieval failures.
Independent final synthesis review is PASS_WITH_LIMITS; see
`research/autoresearchclaw/evidence_audit/FINAL_SYNTHESIS_REVIEW.md` and
`research/autoresearchclaw/DELIVERY_VALIDATION.json` for artifact closure.
October12 synthetic-source matches and unaccepted live seeds supersede broad
PASS claims; RE1 is scoped static only. E2 remains NOT_ACCEPTED and no device
runner was started. This closes the requested offline mission; historical
Whole-plan continuation below remains context, not automatic device authority
from this synthesis. Exact next experiments/gates remain in the master/plan.


### Whole-plan continuation - October10 operator instruction

Keep the outcome active across helper checkpoints. Resume E2 readiness now;
the previous RE1 priority/parking is superseded by this explicit continuation,
not by automatic resumption. E2/E3/E4 acceptance and all safety gates stand.
Initial AP/notebook outage and old-helper rejection were resolved by the
operator. New Netperf READY1213b1a4 was verified; guarded E2 then failed at
the WSL source probe before load, with exact restoration and30/30 posthealth.
The independent iperf-only intake then stopped at notebook5202 preflight,
before mutation. Latest endpoint90abaaae... still records ICMP2/2 but no
status response. Current helper-window state is the external dependency;
WSL startup separately returned Wsl/Service/WSAETIMEDOUT. E2 NOT_ACCEPTED.
Independent D2 reciprocal field-visibility checks completed; see receipt
in the owned night worktree. No physical experiment runner remains active.

Independent RE1.7 question while E2 is physically blocked: does the held
host download/bootstrap sequence establish an initialization provider for
the missing406414/406564/406568 control table, or leave it runtime-dependent?
Existing: four held maps exclude those slots; download pseudocode is candidate
only and warns about type propagation. Minimum missing evidence: original
ELF/relocation-backed selector, fast-download and conditional execution order;
independent review before adopting semantics. Reuse the held umac import and
existing ELF tools. Stop at a static answer/qualified negative or when only
new target execution/register/memory acquisition can decide the question.
This supports the original firmware control-boundary deliverable; no device
access, physical OTP/calibration read, new firmware feature or RF claim.

### RE1.8 bounded held-table followup while E2 awaits notebook window

Parent: original firmware control-boundary deliverable / RE1.7 next static
evidence, not an optimization branch. Endpoint0a3d6272... freshly confirms
ICMP2/2 with no notebook5202 status; no live experiment handle to wait on.
Previous goal turn made measured D2/static progress, not just a status update.
Question: do the original AR9888 host-interest table and BMI address/stream
encoders prove a static write destination covering406414/406564/406568?
Existing: selector order qualified, maps omit slots, runtime board base unknown.
Minimum missing evidence: original ELF symbol/relocation-backed table words,
bounded host-interest address selection and existing BMI transport fields.
Reuse held ELF and existing Ghidra export tools; no device acquisition,
target execution, new dependencies, MCP allowlist changes or RF writes.
Stop at a qualified static answer plus independent delta review. Do not claim
ROM/provider absence from file-table absence; return to E2 if READY recovers.
- [x] RE1.8 original350 instructions/80 declared changes,90 table words and
  six relocated jump entries qualified; no selected-table slot overlap.
  Host stream13/14 and248-byte chunks only, not target wire/decoder/entry proof.
  Independent delta review PASS_WITH_LIMITS; root24 static fixtures PASS.
  Receipt re1-host-interest-20261010.json. No new provider established; park
  optional enforcement refinements and return to E2 source-path repair.

### RE1.6 completed bounded continuation - held-image control-boundary evidence

Parent: RE1 / the preserved control-boundary research, not E2 acquisition.
Question: can the held AP/PTP/STA containers or the host command caller supply
the missing downstream pointer/context evidence or narrow the host rate ABI?
Existing: command0x9064 and positional packing checked; AP indirect slots and
runtime LITBASE unresolved. Native session MCP now connects and decompiles.
Minimum missing evidence: fresh original-hash-bound maps for every held role,
bounded literal/initializer candidates, and caller/field provenance where found.
Reuse SGMT/load-overlay oracles and live Ghidra; no replacement workbench.
Acceptance: byte/address-backed static answer or a precisely scoped negative;
independent review before adopting new semantic claims. No RF claim.
Park when the next decisive step requires new device memory/register acquisition
or target execution; do not infer missing pointers or automatically resume E2.
- [x] RE1.6: held AP/PTP/STA/bootstrap pointer coverage and host caller/readback trace.
- [x] RE1.6: independent source/evidence delta review PASS_WITH_LIMITS; root13 guards PASS.
  Adopt host-only interface/readback and four-blob static coverage, not runtime
  enforcement. All four maps exclude pointer slots; only three role images
  have the base literal. Bootstrap is compressed SGMT, not invented gap fill.
 55 original-checked instructions,10 declared relocation changes; original
  selector resolved by actual symbol index. Candidate-only BMI inspection is
  preserved with its type warning and original relocation producer/offsets.
  Receipt research/raw/re1-control-boundary-20261010.json. Exact AP core/context,
  runtime LITBASE and indirect pointer/object bytes remain the next decisive
  evidence. Held/public exact evidence allowed; fresh device acquisition needs
  its separate lab/recovery authority. No automatic E2 resumption or RF gain.

Latest operator correction (October10): finish installing and connecting
Ghidra MCP, rather than stop at exported artifacts. RE1.5 is PASS_NATIVE_SESSION:
45 actual session tools loaded; connection, exact host metadata and native
decompilation verified after restart. Earlier independent source/evidence review
passed after one record repair; root executed the fresh native-session checks.
This supersedes the earlier MCP parking/no-global-agent-setup limitation only
for this integration: one Ghidra MCP entry in the active Orca Codex configuration
and its standard CLI configuration, isolated copied Ghidra projects, normal
analysis annotations allowed, scripts/debugger/emulation/device execution
excluded from the agent allowlist. Originals and prior failures remain intact.
No radio, flash, protected-partition or RF authority changes. Inspect active
rules/hooks as requested; do not disable or rewrite global hooks without an
explicit instruction to change them. Root cause and exact acceptance belong
here, not in another backlog.

- [x] RE1.5: upstream bridge installed in private venv; owned headless startup,
  actual stdio MCP metadata/function discovery/decompilation, analysis annotation
  persistence, constrained Codex tools, original hash and process cleanup checks.
  Actual MIPS decompilation contains command0x9064; AP mapped bytes read; saved
  comment reloads and its restoration is re-read. Final owned PIDs181008/89892
  exited. Unauthenticated metadata denied.45 catalog-validated tools enabled;
  both configs preserve every unrelated value. Codex now owns the live upstream
  bridge/backend; no separate durable research runner was started.
- Rule inspection: project12.1 explicitly requires continued authorized work;
  the MCP/global-config stop was coordinator-authored and is now superseded.
  Active Serena PreToolUse reminder denies repeated raw reads/searches despite
  Serena being disabled, a real navigation mismatch but not a reason to abandon
  implementation. No observed hook denial of installation or registration.

Operator October 10 approval: prioritize the AI-assisted firmware-analysis
pilot proposed in chat, appending it to this existing plan rather than creating
another backlog. This is a bounded offline exception to the earlier firmware
research freeze, not permission to flash, execute target code or tune radios.
The September 20 deliverables and their unaccepted results remain preserved.
This section is the ONLY active execution queue; all older ACTIVE/next entries
below are historical, superseded instructions. Safety and evidence remain binding.

| Order | Deliverable and acceptance | State |
|---|---|---|
| **1 / RE1** | Offline AI-assisted firmware-analysis pilot: exact-file loader/ISA qualification, independently checked known control paths, one consequential unknown or its evidence-backed limit, and adoption decision. | **DONE_SCOPED_STATIC / PASS_WITH_LIMITS**; qualified downstream negative; no RF/performance claim |
| D1 / FMX-0010 | AP-only spectral corpus: hashed raw provenance, strict complete-record decoding, per-bin distributions/plots by matching profile, published QCA9880 dataset comparison, explicit sanity and ML-usability limits. | Corpus and actual scalar comparison DONE; per-bin external validation UNAVAILABLE, ML readiness NOT_CONFIRMED |
| D2 | Usable per-station peer/airtime statistics on exact stack. | Negative observation recorded; usable reporting NOT_CONFIRMED |
| E2 / FMX-0007 | Fixed-topology/build iperf3 + Flent RRUL baseline, p50/p95/p99, goodput, retries, MCS distribution; >=5 repetitions, variability and validity/restoration evidence. | NOT_ACCEPTED; guarded attempt restored after WSL failure; independent iperf intake blocked by absent notebook5202 status, despite ICMP |
| E3 / FMX-0008 | Paired A/B/A/B AQL comparison against accepted E2; distinguish AQL from unsupported airtime reporting. | WAIT_E2; existing conclusion INCONCLUSIVE |
| E4 / F | Aggregation/pacing/rate-envelope and autonomous optimization. | DEFERRED until prerequisite measurements accepted |

### Priority 1 / RE1 - AI-assisted firmware-analysis pilot

- Parent question: can an established decompiler plus bounded agent access
  replace repetitive manual analysis and reveal actionable QCA988x/airMAX
  control boundaries? Layer: external analysis workbench observing Linux host
  modules and proprietary radio-firmware bytes; no hardware control change.
- Existing evidence: held WA8.5.12 image/module hashes, host serializers,
  validated SGMT maps and reviewed AP/PTP/STA parser cases. Preserve parsers,
  regression tests, failed results, safety/recovery and RF baselines as oracles.
  LITBASE0x9bb001 and unmapped indirect slots are still UNKNOWN at runtime.
- Architecture: reuse Ghidra's loaders/decompiler and a current compatible
  headless outputs read by agents; MCP only if its read-only scope is enforced.
  No new UI, research service or universal orchestrator.
  Runtime/cache/projects stay under ignored firmware/build/re1-20261010.
  Native Windows is a permissible fallback for unavailable WSL; never restart
  shared WSL/Docker/services to make this pilot work. No global agent setup.
- [x] RE1.0: freeze input/tool hashes, exact ELF roles/ISA/ABI, supported loader
  and processor profiles, owned runtime and cleanup. Test the actual modules,
  not just a source-built x86 demo. REA main's ET_EXEC MIPS lane rejects our
  ET_REL umac.ko; Xtensa is not admitted. This is a scoped incompatibility,
  not a reason to modify artifact headers or weaken upstream admission.
- [x] RE1.1: independently reproduce the host command0x9064/word transform,
  serializer header and subtype0x17/0x1e positional layouts from original
  bytes, mapped relocations and bounded Ghidra instruction/decompiler output.
  Check original module hash before/after. Pseudocode alone is not acceptance.
- [x] RE1.2: qualify Xtensa import/selected instruction families and SGMT load
  order on the actual AP target. Compare bounded known blocks with an
  independent decoder. Common-ISA support is not exact QCA-core qualification;
  unknown extensions, contexts, memory/ROM and indirect calls remain explicit.
- [x] RE1.3: investigate one unresolved queue/rate/scheduling control path
  downstream of0x17 or0x1e. Every new semantic claim needs original byte/address
  and dataflow provenance. Missing pointer contents/ROM may yield a qualified
  negative result and precise next evidence request; do not invent values,
  copy proprietary implementations or inject private commands into radios.
- [x] RE1.4: independent review of exact inputs, mappings, known-path checks,
  unknowns and original-byte preservation; adopt/reject the demonstrated tool
  subset and record manual effort/time, failures and available model cost.
  No claimed speedup percentage without comparable observations.
- Stop/park: a rejected architecture blocks that target only. Continue the
  compatible host lane; do not build a generic replacement workbench. Stop
  when progress requires device execution, new memory acquisition, licensing,
  production access or a safety exception and request only that new authority.
- Scope: static public/sanitized held artifacts only; no radios/SSH, load,
  routes/firewall/power/RF changes, emulator/debugger, firmware execution,
  protected partitions, signature bypass or global dependency/config changes.
  Bridge script/debug/patch/write capabilities remain unexposed. Local import
  auto-analysis and private database creation are allowed, not target execution.
- Executed result: native ELF/MIPS loader reproduced five host functions and
  the known command/header/subtype layouts. Four final AP SGMT regions imported;
  80 fresh Ghidra instruction bytes/mnemonics/lengths agree with explicitly
  reused hash-bound ESP32 evidence. Three additional real consumer/lookup
  windows were inspected with common ISA only. Exact core/LITBASE stay UNKNOWN.
  Host rate packing uses low4 shifted1, bits0x20/0x40 and normalized bit0;
  target lookup extracts matching bit positions. No semantic rate ABI proved.
  Slots0x406414/0x406564/0x406568 are absent from the supplied image: qualified
  negative for complete downstream authority. No pointer values invented.
  Receipt: research/raw/re1-pilot-20261010.json; rerun tools/research/ghidra.
  KEEP bounded headless artifact reads; broad MCP bridge built but never
  started because read-only annotations are hints, not enforced capability.
  Original module hashes unchanged; six fail-closed fixtures PASS; no RF.
  WSL timeout, class-loader/relocation/PowerShell failures retained. Initial
  user.home-only launch used default Windows Ghidra log/cache; subsequent
  runs explicitly isolate settings/cache/temp; no global paths cleaned.
  First independent FAIL retained; evidence-hygiene repair pass1 executed and
  final re-review PASS_WITH_LIMITS.20 relocation field masks and both original jump-table
  targets checked; before/after hashes, commands, script/tool fingerprints,
  missing-evidence request, model cost and effort limits recorded in receipt.
  Optional bridge repair is parked, not a
  prerequisite to static findings; no claimed speedup or80percent retirement.
- Closure: RE1.0/1 PASS, RE1.2 PASS_WITH_LIMITS, RE1.3 qualified negative,
  RE1.4 independent adoption PASS_WITH_LIMITS. Adopt only the demonstrated
  headless/static subset. Exact QCA core/LITBASE/ROM/runtime authority UNKNOWN.
  Next firmware evidence: held/public exact context and indirect-table/object
  contents listed in the receipt. Device register/RAM/ROM acquisition needs a
  separately approved exact-build lab/recovery workflow. Do not manufacture
  missing values or automatically resume E2; its existing endpoint/acceptance
  blocker and operator gates remain. No durable/background runner is active.
- Owner: coordinator integrates; at most two bounded supporting workers and
  independent review under the standing budgets. No recursive agent trees.
- Following RE1: return to the preserved D1/D2/E2/E3 order only after recording
  the pilot decision. E2 still needs its genuine endpoint and original physical
  acceptance; this pivot does not convert earlier support tests into RF proof.

### D1 answer and remaining limits

- Question: is our Wave-1 FFT output structurally sound and comparable to the
  published QCA9880 data, and what can it support without invented calibration?
- Existing evidence: historical idle 30,000 frames/2.79 MB (buffer-full/censored),
  empty historical loaded capture, and Oct8 valid 16-frame manual bursts.
- Minimum next action: hash and strictly parse archived captures using the
  existing decoder; archive distributions separately by capture/profile.
  COMPLETED offline: `artifacts/spectral-corpus-20261008/` in the isolated
  worktree contains hashed manifest, CSV and SVG from 30,016 actual records.
  Historical idle: 29,767 at5180 +233 at5200 MHz, 6.519883s TSF span,
  21 all-zero frames; full relay remains censored. Manual16: 3.121ms only.
  Empty loaded file is NO_DATA. Exact historic build/mode needs provenance
  verification before cross-build comparisons; captures were not pooled.
  Actual public CC BY4.0 version6 CSV was acquired and compared in
  `artifacts/spectral-reference-20261009/`: 5180MHz local29767/reference698
  records, 5200MHz233/661; all eight exported fields parsed. Source-pinned
  signed8 conversion preserves canonical values. External per-bin/TSF/width
  equivalence is UNAVAILABLE in that CSV schema. Internal framing and scalar
  interoperability CONFIRMED; general ML readiness NOT_CONFIRMED.
- Acceptance: publish reproducible corpus manifest and sanity analysis; compare
  actual primary external data only after verifying schema/profile/license.
  Structural sanity alone is PARTIAL, not classifier or general ML acceptance.
- Stop/park condition: unusable/censored data or unavailable external dataset
  is an explicit gap, not a reason to repair loaded ACK. If needed, qualify the
  smallest guarded AP-only capture; if D1 is externally blocked, keep it
  INCOMPLETE and advance independent E2 work.
- Boundaries: no notebook/load/ACK prerequisite for offline or AP-only D1.
  Never pool 64/128 bins or different channel/build profiles. No calibrated
  per-bin dBm, independent-replicate, representativeness or classifier claim
  from correlated bursts or a full relay buffer.
- Owner: coordinator integrates and interprets; bounded workers may support
  this same deliverable. No independent optimization branch.

### Active E2 card

- New physical result e2-e101cfdb...: current notebook run stayed READY with
  unchanged iperf/netserver identities and Restarts0. RF0dBm/80MHz and
  bilateral stability passed; first30s UDP50 down sample received47.38Mbps
  with p95 RTT29.508/30.985ms. Next UDP200 down reset the control connection.
  Exact AP kernel log at uptime6609 records global OOM killing hostapd1408;
  reassociation followed. No completed block; E2 NOT_ACCEPTED, current-stack
  load stability FAIL for this treatment. Do not rerun unchanged or lower the
  declared load to call E2 accepted. All owned routes/NAT/power restored,
 30/30 bilateral settled health and frozen build/config checks passed.
  Runner137172 exited; no background experiment remains. Read-only diagnosis:
 64MiB physical RAM, managed56120kB; OOM normal-zone free12252kB below
  boosted min16384kB (boost8192), current min_free_kbytes8192 and
  watermark_boost_factor15000. This establishes the kernel action, not which
  buffer/allocator caused pressure or a proved fix. No VM/queue tuning applied.
  Next decisive missing evidence is a reviewed safe memory-pressure remedy
  or explicit frozen-stack negative decision; retain separate pending WSL
  recipe amendment. Helper relaunch/window action is no longer required.
  Curated receipt research/raw/e2-ap-oom-20261010.json; no wireless gain claim.

- October10 renewed readiness: approved helper run1e87ea5b... freshly reports
  READY, Restarts0, Errornull and pinned Netperf5205. Nano TCP connections to
  5201/5202/5205 all exit0; status5202 is auxiliary HTTP, not a traffic port.
  Endpoint83d8519e... supersedes the notebook-outage blocker, not its unknown
  historical cause. Resume already approved independent five-block iperf-only
  acquisition with unchanged guards/recipe; do not apply the pending WSL SNAT
  amendment. Question, acceptance and stop conditions remain those below:
  repeatable external traffic measurements, five restored blocks, preserve
  any failure and stop on invalid health/build/RF/lease. RRUL stays NOT_RUN,
  E2 NOT_ACCEPTED and E3/E4 gated until full required evidence is acquired.

- Third consecutive goal-turn blocker audit: fresh endpoint800ab82f... still
  has notebook ICMP2/2 and wget5202 rc4. Guard amendment remains unanswered.
  Prior goal turns made D2/static and source-path progress; current check does
  not change acquisition readiness. No live runner/reviewer remains. E2 is
  NOT_ACCEPTED, E3/E4 gated, bounded RE1 scope reviewed/closed with runtime
  limits. No further decisive step is executable without notebook window/
  READY and the exact recipe decision. Record product goal BLOCKED, not
  complete; retain its full objective and resume on resolved external inputs.
  Current launcher still uses2h wall-clock deadline; outage cause UNKNOWN,
  so do not replace the approved bundle or infer expiry from old memory.

- Current decisive diagnosis: instrumented endpoint0767e462... captured three
  WSL-to-AP SYNs from controller192.168.100.155, not lab alias192.168.1.155;
  AP has no return route to100.155. Netperf pin freshly preserved. WSL is
  intermittently responsive, not declared stable. Notebook5202 remains absent.
  Critical method review identifies a minimum repair but requires an operator
  amendment of the frozen counter-only/no-new-verdict clause: AP-only SNAT
  between exact controller100.155 and notebook.170, normalized to.155, plus
  one100.155/32 return route via.155/br-lan in the same tag/lock/TTL lifecycle.
  Exact amendment requested asynchronously; no implementation/execution yet.
  do not change global WSL/Windows aliases or broaden notebook firewall.
  First long-context Fable review failed at provider API before assessment;
  Fresh bounded routing review completed on enabled Fable/high, session909415b7,
  read-only, no subagents; source/normalized counters, same-adapter attestation
  and exact extra-route cleanup required. No review process remains active.
  No device/network/RF mutation. Receipt e2-wsl-source-path-20261010.json.

- D2 independent refresh physically executed:20/20 ICMP each direction;
  exact-peer TX-duration increments AP12250/30296us and Nano12035/35658us.
  Firmware peer TX/RX rate fields nonzero. RX duration was772/86320 in an
  initial snapshot, then0/0 before and after reciprocal traffic: unqualified
  as a cumulative/calibrated counter. Bytes include SSH/control. No queue,
  power, rate or firmware change; all boot/build/config/AQL fingerprints stable.
  Receipt d2-peer-visibility-20261010.json; FIELD_VISIBILITY_CONFIRMED, not
  fairness, calibrated airtime, E2 acceptance or a wireless improvement.

- Partial intake e2-b974b721... stopped at notebook status preflight, before
  route/radio mutation or load. Correct Nano source192.168.1.3 and direct
  br-lan route verified; packet trace shows three5202 SYNs, no reply, while
  notebook ICMP2/2 passes. Helper-window state requested, not an unchanged
  rerun. Runtime expiration/listener/firewall cause remains UNKNOWN.
  Independent D2 refresh while this endpoint dependency is blocked: newly
  booted exact stack now reports nonzero per-peer TX duration during low-rate
  control traffic. Question: does a bounded20-ping exchange increment usable
  per-peer bytes/packets/TX-duration, and are firmware peer/rate stats populated?
  Reuse existing read-only Trial event recorder and station parser; before/after
  exact-peer snapshots, frozen boot/build, no power/rate/queue change. Stop at
  observed field deltas/qualified negative; no calibrated-airtime or fairness
  acceptance without independent timing validation. Return to E2 on READY.

- October10 physical continuation: new Netperf READY1213b1a4 verified; actual
  guarded attempt e2-eacb8015... passed RF0dBm/80MHz and15/15 stability, then
  failed WSL source probe before load. Exact restoration and bilateral30/30
  posthealth passed; preserve INCOMPLETE. Separate local WSL startup probe
  returned Wsl/Service/WSAETIMEDOUT; actual HTTP byte framing is correct.
  Root parks RRUL transport repair and executes the already permitted independent
  iperf portion: same five deterministic10-cell/30s blocks and frozen endpoint,
  builds, RF, leases and restoration; explicitly omit RRUL and its WSL-only
  source probe. This is PARTIAL_IPERF_ACQUIRED_E2_NOT_ACCEPTED, never accepted
  E2 or authority for E3. Minimal collector branch only; unchanged safety guards.
  Missing evidence stays five actual canonical RRUL acquisitions and review.

- Historical old-helper rejection55c33ed6/48323996 is superseded by actual
  Netperf READY1213b1a4 above. Do not request another package switch from
  that historical evidence. Current blocker is the absent5202 status endpoint;
  obtain current helper-window state. No physical experiment runner is active.
- Minimum guarded intake is ready/reviewed: e2_baseline_trial.py plus
  e2_controller_route.ps1, five bounded blocks below, normal PC admin/UAC.
  Controller source verification uses counter-only rules inside the original
  own/TTL-cleaned NAT table; no new daemon/table/verdict or broad translation.
  Freeze board/boot/module/QCA/config/AQL/two-peer roster, require same new
  notebook run/hashes; postfailure cleanup+settled30/30 precede success.
  Root17 affected fixtures and independent guard8/collector9 PASS offline.
  Next execute only once new Netperf READY is actually observed. Do not
  replace this gap with another legacy seed or relabel fixtures as RF results.

- Question: what repeatable throughput and loaded latency does the fixed
  AP/Nano configuration deliver with traffic generated outside the radios?
- Existing evidence is SEED / NOT_ACCEPTED; no tuning until a valid baseline.
- Fresh read-only readiness: both known boots/configurations preserved,
  AP/Nano30/30 idle pings. Notebook192.168.1.170 answers3/3 but its5202 status
  is unavailable (wgetrc4). Operator window state requested asynchronously.
- Missing support at E2 start: real Flent RRUL required netperf/netserver,
  absent in the old iperf-only helper. This causal dependency is now locally
  qualified and packaged below; it is no longer a runtime blocker.
- This support work is necessary for the named RRUL acceptance requirement.
  Stop/park if native portability is unresolved; document the dependency and
  continue the iperf3 portion only after fresh endpoint and RF qualification.
  Never label iperf3-only or on-radio generation as completed RRUL.
- Linux controller qualification completed with actual Flent2.3.0 canonical
  RRUL:8 TCP +3 UDP_RR +ICMP series, >=50 finite samples, local-only PASS
  independently reviewed. This does not accept the radio baseline.
- Native x86/x64 builds completed but first x86 TCP_STREAM failed10022;
  that failure and a stalled PowerShell qualifier INFRA_ERROR are preserved.
  The exact owned helper was stopped; no native survivors reported.
- Minimal Win32 ephemeral-bind compatibility resolved the primitive failure:
  all6 native modes PASS. Actual same-PC Linux-to-Windows x86 primitives3/3
  and canonical12-series concurrent RRUL also PASS, independently reviewed.
  No routes/firewall/RF/notebook changes. This qualifies local runtime only.
- Existing protected one-copy notebook integration completed with frozen
  netserver/control5205, exact-program/source dynamic-data firewall scope and
  owned parent/child cleanup. No alternate orchestrator.
  Source uses wildcard ephemeral data listeners; control -L is not sufficient.
  Fresh notebook status still unavailable; cause UNKNOWN, READY action pending.
- Frozen new package independently APPROVED for handoff:
  `artifacts/notebook-bundle-20261008-232936-0eab55527c5944a180850828efa57fbf/`,
  ZIP SHA70c527a4...; root/owner/independent26/26 offline PASS, x86/x64 and
  actual32-bit PowerShell package validation PASS. Previous ZIP remains
  BLOCKED with its late-child failure. No notebook deployment occurred.
  Current physical dependency: operator USB copy, Q-close old window and
  launch new START_FUTURAMAX.cmd with UAC, leaving READY. No background
  physical runner exists. Then freeze/check direct route/source and RF
  recipe below and execute the five bounded blocks.
- Acquisition recipe must freeze configuration, traffic durations, repetitions,
  telemetry and acceptance before execution; use existing guarded routes/power
  workflows, full restoration and health checks. No new wireless treatment.
- E2 requires >=5 repetitions; the legacy exactly3-repetition/30-cell iperf
  evaluator is not sufficient and must not be relabeled as accepted E2.
  Preserve its old contract; acquire5 bounded10-treatment blocks (TCP1/4,
  UDP50/100/200 Mbps both directions30s), actual60s canonical RRUL per block,
  same frozen build/80MHz/observed0dBm/RSSI<=-55 and stability/restoration.
  Never put all50 cells inside the old900s lease or silently extend its timer.
  Report sampled peer MCS, not per-frame firmware distribution. Direct exact
  controller notebook/32 routing and WSL observed source need a reviewed
  bounded owner guard before live RRUL. Physical endpoint READY remains gated.

### Parked support work and freezes

- Loaded 60 Mbps / 10 s spectral ACK repair: PARKED, not rejected or accepted.
  Persistent waiter local validation completed (worker: 43 focused and235
  affected Linux tests PASS); independent frozen review/physical validation
  NOT_RUN. Preserve source053eb270/test23d47a8c and all earlier failures.
  Do not execute another loaded cell automatically.
- Its eight-second gate remains unchanged for that experiment, but is NOT
  a prerequisite for D1 or E2. Last physical restoration/posthealth df5171a0
  PASS is historical evidence, not current-health proof.
- Optional GRO/BE/AQL tuning, new firmware, new orchestrators and custom-MAC
  expansion are frozen until accepted E2, except minimum safety/acquisition
  dependencies justified under AGENTS12.3.
- Report research answer / evidence / acceptance gap / next decisive action.
  Helper tests, repairs and policy changes are not wireless results.

## Current execution checkpoint - 2026-10-06

### Overnight continuation - 2026-10-07

- [~] 20:10 UTC finer per-launch waiter c1e64091 INVALID despite59.9505 Mbps,
  both12/12 and full restoration; native ACK itself late by diagnostic brackets.
- [x] Posthealth df5171a0 both30/30/exact controls+logs+boots/locks/READY PASS.
- [x] Installed ucode fs API/pins read-only qualification b4386194 PASS.
- [ ] ACTIVE: qualify one persistent ucode waiter in native disposable fixtures,
  independent review, then one changed-observer cell with unchanged gates.

- [~] 19:54 UTC single waiter/atomic ACK 20ee3271 still INVALID: 59.970 Mbps,
  both 12/12 and FFT16 valid, but strict eight-second ACK timeout. Restore PASS.
- [~] Posthealth 2e95d307 both29/30 FAIL; corrected log-comparison typo does not
  erase loss. Idle counters quiet; four-path f3726615 each60/60, cause UNKNOWN.
- [x] Actual ucode sleep(200) compatibility PASS0.21s; BusyBox0.2 unsupported.
- [ ] ACTIVE: bounded finer waiter, independent review, fresh full preflight
  and diagnostic interpretation before one changed-observer capability cell.

- [x] 19:38 UTC remote READY restored (d889f077); no operator access/files needed.
  FFT-OFF a77066d8 PASS 59.949 Mbps / both 12/12 / exact restoration.
- [~] Loaded 302df21f: 59.93 Mbps / both 12/12 and valid 16 FFT, but eight-second
  ACK missed. Acquisition INVALID / overlap UNKNOWN; full restoration PASS.
  Posthealth e0d76d86 PASS 30/30 each, exact boots/logs/controls, locks absent.
- [ ] ACTIVE: reduce repeated SSH polling with one bounded read-only native
  waiter; independent review then physical test. Keep all identity/load/timing
  gates. Prior missing-access and numeric-repair blockers below are historical.

- [x] 19:01 UTC unlimited repairs2dbabaf; timing+fixed-string fingerprint ready.
  Root229OK/203PASS26SKIP; worker225LinuxPASS; independentdelta4PASS.
  Actual idle old0.96..0.98s/fixed0.76..0.77s exacthash; regex1.52s REJECTED.
- [ ] Notebook /status unavailable617273ad... despite1Gb/ping3/3.
  Need lateststate.json/console.log, NOT more repair approval. No runner.
- [ ] FreshREADY -> one guarded60M/10s/1MiB FFT-OFF control -> interpret ->
  timedFFT if baseline valid -> restoration/posthealth. No gate relaxation.

- [x] Operator authorized UNLIMITED in-scope repairs; AGENTS12.2/main+WT,
  contract4PASS/independentreviewPASS. Numeric attempt limits no longer block.
- [x] Native timing instrumentation ready/reviewed; original load/acceptance
  gates unchanged. Idle read-only kernel fingerprint costs0.97..0.98s per call.
- [ ] Investigate equivalent cheaper fingerprint without losing exact validation.
- [ ] Loaded control/timedFFT wait for notebook remoteREADY: physical1Gb/ping3/3
  but TCP5202unreplied. Requested latestnotebookstate.json/console.log.
  This is an access dependency, NOT a request for repair authorization.

- [x] 15:11 UTC notebook READY verified (999 h); AP transport repaired2/2,
  source91c9d6f4/root215OK/independent52LinuxPASS, exact native guard unchanged.
- [~] Actual loaded C1 e163f80e...:16validFFT2512B observed, but acquisitionFAIL
  (49.709Mbps vs57..63, AP/CPE11/12ping, no timelyACK; overlapUNKNOWN).
  Three restoration layersPASS; posthealth30/30 each/sameboots+logs; lateACK
  exists but cannot rescue failedgates. Preserve allraw. No runner active.
- [ ] Operator authority pending: ONE extra bounded timing-instrumentation
  repair/measurement round beyond2/2. No unchangedretry or gate relaxation.

- [x] 13:36 UTC loaded C1 harness frozen and independently approved. Root
  212 OK (192 PASS / 20 POSIX skips); worker Linux 212 PASS; independent
  focused Linux 49 PASS. Native first failure and repair 1/2 preserved.
- [ ] Loaded C1 physical NOT_RUN: fresh notebook status failed rc=4,
  Operation not permitted (raw 5760e5c1...). Cause UNKNOWN; radios reachable.
  Operator: reopen existing START_FUTURAMAX launcher and leave READY.
  Then fresh preflight, exactly one reviewed paced cell, restoration and
  posthealth. No current runner; no retry of unchanged failed experiments.

- [x] 13:20UTC authorizedtemporarylabalias restored withSkipAsSource=true;
  benchSSHmustexplicitlybind192.168.1.155; othernetworksettingsunchanged.
- [x] C1idlemeasured16valid128bin/2512BFFT, exactrestore+posthealth30/30
  each. Burst3.121ms only, no performance/classifierclaim. Worktree377f916.
- [ ] ACTIVEone60MbpsloadedC1: composecapture/restoreintoexistingrouteguard
  andgateactualoverlap. NotebookREADYrequested; no loaduntilavailable.

- [x] 12:43UTC C1 collector implemented/reviewed offline, sourceead6ca73;
  independentLinux27PASS/affectedLinux119PASS, root162WindowsOK(10skip).
- [ ] LiveC1NOT_RUN: PC192.168.1.155alias absent, Ethernet2stillUp1Gbps
  only192.168.100.155. SSH failedbeforecommands; no spectralwrites.
  Awaitoperator exactaliasrestorevsintentionalchange decision, then fresh
  identity/nativecompat/health and guardedmanual16/128bins/2scapture.

- [x] 2026-10-08 matched60Mbps GRO7cells/168pings/restorationPASS;
  favorable shortSEED, no promotion. Subsequent saturatedBE failedcell6
  CPE11/12pings/defaultdrift; HALFnotaccepted,originalcontrolsrestored.
  Separateidle30sdeltaszero andposthealth30/30do not erase loadedfailure.
  Fullraw/docs/harnesses in isolatedfuturamax-night-20261007 commit26f9ff1.
- [ ] ACTIVE C1onchannelidle FFTmanual16/128bins withguardedrestore;
  noiwscan/RFchange/load. Exactdriverrejects80MHz64bins; preparingharness
  andindependentreviewbeforelive. NoidenticalfailedBEretry. Nano-only
  Phase1 doesnotneedidleSXTattenuation; downlinkC6specificallydoes.

- [ ] ACTIVE 2026-10-08 11:54 UTC: operator corrected premature milestone
  closure. Continue the existing plan, not only the last seven-cell test.
  Next equal-rate GRO SEED: same7states/10s/down1stream/1MiB; fixed TCP
  target60Mbps. Acquisition requires exact reported target and both actual
  payload rates57-63Mbps, not merely accepted CLI options. Existing identity,
  full-feature/control, loss and restoration gates remain unchanged.
  Fresh readiness f4b60931: same AP/CPE boots, Nano+SXT, no experiment locks,
  notebookREADY. LBE remains intentionally off. No new flash/RF/queue change.
- [ ] Then interpret matched-rate latency and examine the existing bounded
  AP BE queue comparison on the installed GRO image where evidence warrants;
  preserve one primary change and review before any live treatment.
  A completed cell/series is a checkpoint, not project completion.
  D-0009 promotion and experiments requiring different RF/topology remain gated.

- [x] 2026-10-08 11:20 UTC: normal installation + seven-cell same-image GRO
  physical evaluation completed. Raw518144fe... acquisition/restoration PASS;
  mean ON/OFF122.644/70.201Mbps, sampled pings168/168. AP mean-cell-p95
  44.244/86.167ms, CPE35.698/10.716ms: INCONCLUSIVE optimization, NOT KEEP.
  Equal-rate QoE/long stability/production promotion NOT_ACCEPTED.
  Same two peers throughout comparison; passive LBE absent BEFORE trial,
  operator confirmed intentionally unplugged/powered off. No unexplained
  firmware-related peer loss. PosthealthNano/AP30/30each,
  sameboots/dmesg, originalGROon/controls/routes restored. No runner active.
  Two harnesscompatibility repairs used; root29+independent29tests PASS.
- Next research question (not launched): equal-offered-rate latency with
  explicit acceptance and known peer roster. Preserve both preload failures
  and initial installloss/timeout. No automaticflashrollback criterion failed.

- 2026-10-08 01:40 UTC: round1 of four extra authorized installer rounds
  completed. Normal candidate-only upgrade succeeded; newboot e0f8e23f,
  kernel8bb582e3/symbols9ddba985 match,10hashes/services/3peers preserved.
  Root70LinuxPASS +independent38LinuxPASS; reserve8MiB unchanged.
  Initial6/10 ping +radio-init timeout retained. Later30/30 each way with
  unchangedcontrols andnonewdmesg is short unloaded health only.
- [ ] CURRENT external dependency: reopen existing notebook launcher to READY
  (requested). Then execute external_gro_trial seven on/off cells with pinned
  client and expected core-symbol SHA9ddba985125a5062a0adf09d06b98a9ca1918d93159854ac296f5f87c0de1460;
  analyze performance/latency/loss/stability and perform required restoration.
  Goal remains active/incomplete. No further approval or firmware retry needed.

- 2026-10-08 00:05 UTC: two extra installer rounds used; root61PASS plus
  independent fixtures. Four-service maintenance restored. Installation and
  instrumented diagnostic both fail memory-before-upload-candidate; no flash,
  candidate upload or handoff. Reserve8MiB unchanged. Diagnostic tmpfs7408->552KiB
  but available10468KiB <15401757B required. PCP accounting is plausible only.
  AP sameboot/config/protected/kernel/services/RF/all3peers restored; final
  ping10/10 does not erase earlier8/10 and9/10. No runner active.
- [ ] Operator decision: further bounded installer repair/review authorization.
  Candidate-only staging with prior exact rollback evidence requires binding
  and independent review. Do not bypass frozen helper, repeat unchanged,
  unload drivers, change sysctls or relax reserve.

- 23:32 UTC: operator directed continuation; use up to the two requested extra
  installer repair/review rounds. Extension round1 sequential stage plus guard
  tests49PASS; rollback stays on PC after remote validation/removal. Reserve8MiB
  unchanged; fresh memory7732KiB still insufficient. Four confirmed-running
  services may be reversibly paused under reviewed guard after Wi-Fi-down;
  measure and restore before uploads/flash qualification. No module unload,
  network restart, sysctl change or persistent service disable. No flash yet.

- 18:56 UTC: no-upload maintenance qualification PASS, all3original stations
  restored; kernel/config/protected/RF/features unchanged. Posthealth10/10
  AP-to-Nano ping, notebookREADY, AQL1/allAC5000/12000/BC50000/HTT3/64.
- Memory readiness FAIL: down11444224B vs two-image requirement22414906B.
  Single-image sequential requirement15401757B also does not fit. Do not
  lower8MiB reserve or repeat the same Wi-Fi treatment hoping for a pass.
- Stage and guard two-repair budgets used. Await requested up-to-two extra
  installer repair/review rounds; establish a measured normal low-RAM path
  and post-upload checks before restaging. Failsafe is not assumed to preserve
  configuration. No driver unload, force/direct flash or protection bypass.
- No flash occurred. No persistent guard/experiment runner remains active.
  Approved AP-only install/test objective remains pending these concrete
  memory/procedure/repair-authority constraints, not generic continue consent.

- 18:28 UTC: operator power-cycle/repoint completed and notebook reopened.
  Old AP kernel/protected/config hashes verified, new boot65ca1d7e, three
  stations and wired/watchdog health restored; fresh notebook READY.
- No new flash or upload: MemAvailable about11-12MiB is insufficient for
  two7,013,149-byte images plus8MiB reserve. Stage repair2 reproduced/fixed
  initial/preupload checks; independent postupload reserve check needs one
  extra repair authorization (requested). Do not lower the threshold.
- Verify the new owned AP-only wireless-maintenance guard using installed
  BusyBox capabilities (setsid yes; timeout/nohup absent). Quiescence unknown
  means retained operation mutex/manual recovery, no cleanup/up/flash race.
- Then execute already-approved AP-only install and postboot acceptance;
  run same-candidate GRO on/off with fresh notebook identity and controls.
  Repointing is a changed RF condition, not proof of improved firmware.

- 17:30 UTC: candidate/rollback native sysupgrade-T PASS; protected/config
  backups verified privately. All51 staging commands exit0. Physical recovery
  availability confirmed by operator. Corrected r2 artifact fully verified.
- FLASH NOT SENT: first installation precheck timed out. AP .2 has no ARP/
  SSH; switch/SXT remain UP. SXT also lost AP radio and AP10.99.0.1 ping0/2.
  Baseline outage cause UNKNOWN, not a candidate boot failure.
- Operator power-cycle requested: ONLY LAP120, 10seconds, no RESET.
  Next: baseline identity/health/protected hashes after return; revalidate
  volatile staged images, then authorized AP-only installation/postboot checks.
  Notebook launcher READY also pending. No persistent runner or flash active.

- 17:01 UTC: actual GRO firmware build EXIT0, zero build repairs. Operator
  approved guarded installation/testing ONLY on lab LAP-120 192.168.1.2.
  Physical RESET/power accessibility confirmation pending; no flash yet.
- Two collector repairs retained: UBNT factory PART reassembly and correct
  regular-image ELF selection. Root + independent objcopy replay now exact.
  Corrected r2 evidence collection underway; no firmware byte change.
- Runtime gate: fresh boot ID + actual flash kernel bytes + exact eight core
  symbols (expected SHA9ddba985...e1460), not stripped notes/non-exported _text.
  GRO harness23 tests PASS after real-fixture correction; old kernel rejected.
- Next ordered tasks: private protected/config backups; stock sysupgrade-T
  for candidate and rollback; physical recovery confirmation; AP-only install;
  postboot protected/config/identity/health checks; same-image GRO on/off seed.
  Notebook status now NOT_READY, so external load waits for launcher readiness.
  No automatic firewall/deadline changes; do not mutate production/CPE firmware.

- 15:52 UTC: resumed on explicit operator correction. Executed six path
  down/up diagnostics and five socket-buffer diagnostics. Last cell of each
  failed on link ping loss, was retained, and stopped its run; both restored
  all controls/routes/NAT. No retries. Raw245df... and87b... in ledger.
- Client 1MiB buffer requests applied; B68.958/69.681 Mbps did not remove
  observed near70 ceiling. Partial series remains INCONCLUSIVE.
- Active next task: build source-grounded legacy-ag71xx RX GRO candidate,
  after exact active-driver/config and ownership/flush checks. Do not patch
  inactive upstream ag71xx.c. Isolated copy only, two-repair new-variant
  budget, old builds/artifacts preserved. No flash or production changes.
- Endpoint harness: worker99 combined PASS, root fresh17path+13window+
  32endpoint PASS; independent raw restoration review PASS with failures
  retained. Offline work remains unblocked by notebook/RF limitations.

- 14:49 UTC: operator moved AP/reopened notebook. Completed the requested
  external-endpoint BE comparison: ABABABA, seven ten-second downlink TCP
  cells, 168/168 loaded pings. Default/half mean 68.110/69.307 Mbps;
  mean AP-side cell p95 81.083/91.606 ms. INCONCLUSIVE, defaults retained.
  Root fresh 15 harness tests PASS; worker combined 66 PASS. No live failures
  or retries. Exact restoration of all AC/station limits and AQL/HTT controls;
  own temporary routes/NAT removed, original 11 dBm/VHT80 unchanged.
  Evidence: endpoint-327a15bddc924263a4000d4b951b49ac in night raw/bench.
- The notebook stayed READY with one RunId. Its built-in two-hour deadline
  likely caused the earlier stop; previous run log absent, cause not proven.
  No launcher changes, clock changes or new firmware installation.
- Requested external BE comparison complete. Next experiment design:
  separate forwarding/CPU versus endpoint-path versus RF limits; current AP
  CPU about 87% does not alone identify the bottleneck. No active runner.

- 13:49 UTC — bounded RF-as-is cohort complete, superseding the early blocked
  handoff below. The operator explicitly requested experiments with the
  available signal; the historical -55 dBm screen did not block these seeds.
  No production, regulatory, protected-partition or flash authority was added.
- Four ABABABA comparisons completed: 7 cells each, 10 seconds, one TCP stream,
  downlink, unchanged 11 dBm/channel 36/VHT80. Results in the research ledger:
  AQL on/off, BE defaults/half, AMPDU 64/32, and AMPDU 64/1.
  All 28 cells and 672 loaded bilateral pings completed without recorded
  acquisition errors. Every run restored its controls and removed its own
  listener/lock. Existing AP servers on 5201/5202/5203 were untouched.
- No clear improvement appeared in the first three comparisons. AMPDU 1
  consistently reduced throughput to about 76 Mbps versus 141 Mbps at 64,
  and increased loaded latency. REJECT 1 as an optimization for this seed.
  The request has an observable response; actual aggregate frame count
  remains UNKNOWN because the getter reports driver cache.
- The experimental BE-half firmware was built, not flashed. Repair 1 completed
  at 13:41:58 UTC. Its initial EXIT=2, malformed IPK/control and exact fix are
  preserved. The fix exports four packaging variables to both shared recipe
  targets; it changed only the new build tree, not clocks or older artifacts.
  Root independently passed checksum checks and embedded-module extraction
  for all eight images. Artifact folder in the night worktree:
  `artifacts/aql-be-half-20261007T130201Z-838/`.
- Fresh root checks: 22 bench tests PASS; Linux 8 variant/packaging tests PASS.
  Windows: 6 PASS, 2 SKIP for the explicitly POSIX-only GNU make fixture.
  Its original Windows 2 ERROR result was preserved; assertions were unchanged.
  Worker Linux combined suite: 47 PASS. Five generated shell syntax checks PASS.
  Two earlier mock-dispatch failures were fixed in the fixture, not by weakening
  runtime checks. An initial syntax check failed on Windows text-pipe CRLF;
  the same generated shell passed when supplied as LF bytes.
- Firmware boot/RF acceptance and compiled-to-stripped equivalence: NOT_RUN.
  Binary reproducibility: NOT_PROVEN. No performance gain is claimed.
  The 28 physical cells used the existing installed firmware, not the new image.
- Next: restore the external traffic endpoint for capacity comparisons.
  Notebook ping works, HTTP 5202 fails and a bounded TCP 5201 probe timed out
  (remote EXIT=137). Do not disable its firewall or infer the specific cause.
  Candidate installation remains a separate authorized recovery workflow;
  do not auto-install a variant whose runtime counterpart showed no win.
- GitNexus had no FuturaMAX index; exact-path/source navigation was used.
  Dirty main work and the earlier handoff remain preserved.

- 09:22 UTC /06:22 Buenos Aires: early blocked handoff preparation, not the
  08:00 deadline or full objective completion. Required offline implementations
  and item1.7 have verified outcomes; independent scope audit identified no
  further mandatory offline implementation within the existing night plan.
  Remaining replica/health repairs need new retry-budget authority; RF/Phase3
  need qualified physical evidence. No unchanged retry or new policy thresholds.
  Both candidate integrity verifiers freshly PASS; full-image match remains0/8.
  Live process inspection found0 processes with cwd in either isolated build
  tree; no owned overnight Python/iperf process found on Windows. No runner is
  progressing in the background. Handoff: ../handoffs/handoff-2026-10-07T09-22-07-5c61dc.md.
  Finish the handoff before closing; do not mark physical/reproducibility work done.

- 09:13 UTC: item1.7 evidence reconciliation records23 archived TCP rows
  (7missingthroughput), AQL5states ABABA (3missingthroughput), and fresh offline
  rejection of the latest1/30-cell RF attempt. No second-radio blocker remains;
  loaded RF qualification/repetitions still do. Archives unchanged, no live work.
  C2 preparation freshly rechecked:10policy tests+4exact-C tests PASS,
  1986valid/37rejected inputs,8063assertions; host fixture only, not firmware/RF.

- 09:01 UTC: 6ee9cd0 preserves existing hard-failure reasons before statistical
  sample-count checks. Pre-fix4tests/12failures; post85 analysis/279 combined PASS;
  independent46tests/384edgecases/27sufficient-series parity PASS. Zero repairs.
  No new thresholds or full D-0009 claim. Continue only existing offline scope.

- 08:50 UTC: replica compiled-to-strip-to-IPK link PASS on a disposable copy;
  raw source module unchanged, portable proof rehashed. This closes only driver
  provenance, not0/8 image reproduction. No new build or retry.

- 08:47 UTC supersession: final image attempt completed EXIT0 at08:31:19.
  Collection and independent integrity review PASS, but byte reproduction FAIL:
  zero of eight image hashes match (all eight sizes match). Both IPK containers
  and all extracted packaged ath10k modules match exactly. Raw debug modules
  differ. No third repair/build. Preserve both immutable snapshots and failures.
  Read-only component diagnosis is in progress; no RF/boot/flash acceptance.
  Exact image pairs: research/raw/replica-byte-comparison-20261007.json.

- 08:20 UTC: module resume completed EXIT0 at08:00:47; first image attempt
  failed EXIT2 in logd packaging after an observed ~28-second clock regression.
  Failed log/control/incorrect IPK preserved. Source/config fingerprints unchanged.
  31 clock samples then showed zero backward intervals (forward adjustment
  observed, NOT future stability proof). Final repair attempt 2 is active:
  images1/reproduce, persistent one-shot marker, outer3600s timeout; exact log
  fmx-night-images-20261007T082027Z-107491.log. No third replica retry.

- 07:57 UTC: replica resume attempt 1 launched with reviewed runner 0d8c991,
  module-resume/jobs1/reproduce only. Prior failed log remains pinned; exact
  failed feeds feed_config step passed read-only before this attempt. Existing
  source/seed fingerprints passed. A persistent one-shot marker guards scoped
  clean and 3600-second compile timeout. Session still pending; follow-up log
  query failed Wsl/Service/WSAETIMEDOUT. Do not infer completion or start another
  attempt/images while outcome is unknown; no WSL restart authority.

- 07:39 UTC: endpoint producer provenance 9a3fafb records preflight byte hashes,
  pinned client evidence and allowlisted parameters, not loaded-code/firmware
  identity. Fresh 29 endpoint, 77 endpoint/evaluator and 275 combined PASS;
  independent review PASS with 18 checks, zero repairs. Three archived full
  evaluations/raw hashes unchanged, no accepted RF baseline. KEEP preparation.
  Continue existing offline experiment-contract work; full D-0009 comparability
  and reproducible second firmware build remain incomplete. No live operations.

- 07:21 UTC: health-audit candidate fc08c0e NOT ACCEPTED after both allowed
  repairs; final regression 21 tests, 20 PASS/1 FAIL. Known iw primary absence
  is lost when ifconfig is missing. Revert 1dcf02c preserves candidate history
  and restores prior files; fresh accepted suite269 PASS (not health approval).
  No third retry or relabeled subtask. Extra health repair needs operator
  budget authority; continue independent offline bench/control preparation.
- 07:01 UTC: board parser aee19ec/f265258 keeps geometry/integrity/support
  unknown; identified names and inferred platform candidate are separate.
  Seven pre-fix failures plus four PCI-token review failures corrected in
  repair 1. Final 14 focused, 49 shared, 269 combined PASS; independent PASS
  with 28 PCI checks. No live collector/recovery file changed or executed.
  Continue existing offline harness/control boundaries; RF/WSL limits unchanged.
- Offline continuation 352caa7: calibration hasher fingerprints supplied bytes
  without guessing MAC/version/physical validity. One pre-fix false-approval
  regression corrected; 11 focused, 255 combined and 1,602 reviewer checks PASS.
  No repair needed, real partition/backup access or live operations. KEEP.
  Next in existing Stage-0 inventory: board_probe observation/inference boundary.
  RF and shared-WSL limits unchanged; no new hardware action required tonight.
- 06:43 UTC: db2b1d1 hardens offline flash-map/protected-partition validators.
  Five original regressions reproduced, plus equal-total-alias review repair 1.
  Explicit flat reported geometry is bounds-only; legacy APIs never authorize
  flashing. Final 35 focused, 81 reviewer checks and 244 combined PASS. No live
  scripts changed or executed. KEEP offline harness; hardware/flash NOT_RUN.
  Continue unblocked offline work; no RF retry or shared-WSL recovery authority.
- 06:21 UTC: isolated fixture completeness 100e2ca resolves the 13 missing-file
  errors without weakening tests. Nine existing companion files byte-identical
  to main and pinned, fresh Git checkout verified. 100 full bench Python tests
  and 209 combined tests PASS; independent review PASS. No helper/binary/server
  executed; historical failed suite and physical/runtime limits remain explicit.

- 06:09 UTC: statistical evidence correction 0edfa28 plus review repair 053cde3.
  No invented p=0/p=1 or zero deltas; undefined baseline percentages remain
  INCONCLUSIVE. Preserve computed fields during backend failure. Full-precision
  results/report probabilities; 54 focused and 180 combined tests PASS with
  independent review PASS. Scientific thresholds and physical gates unchanged.

- 05:57 UTC: endpoint chronology correction 132c831 closes acceptance of
  repeated/overlapping/out-of-order client windows. Four pre-fix failures
  retained; 48 focused and 162 combined checks PASS; independent review PASS.
  All three archived evaluations and raw hashes unchanged. This is evidence
  consistency only, not full D-0009 comparability or authenticated freshness.
  Remaining preparation: inspect existing recorded identity/config evidence
  for defensible comparison inputs; do not create policy acceptance defaults.

- 05:50 UTC: offline matrix integrity corrected in isolated 7454f5d.
  No synthetic success; PLAN_ONLY and CALLBACK_REPORTED are separate from
  hardware acceptance NOT_RUN. Failed partial evidence retained as UNTRUSTED.
  Repair 1 reproduced reviewer failure; 28 focused and 91 combined tests PASS,
  independent review PASS. No live adapter or calibrated cabled rig was tested.
  Next existing-plan work: inspect D-0009 provenance/comparability inputs
  offline; do not invent acceptance thresholds or activate Phase 3.

- 05:32 UTC: offline metrics/report integrity corrected in isolated84d662d.
  Explicit bandwidth, missing-as-unknown, strict JSON/quantile/arm consistency;
  reports no longer infer promotion/rollback or policy PASS. Independent review
  PASS;38 focused and63 analysis tests PASS. Full D-0009 comparability/ranking
  remains open; this does not authorize Phase3 or any radio operation.

Operator is sleeping and declines further physical relocation. Work with the
existing evidence; do not make RF acceptance or Phase 3 dependents pass by
relaxing gates. Native continuing goal ACTIVE through 08:00 Buenos Aires;
no duplicate cron/watcher installed. No flashing, production changes, new RF
acceptance retries on the unchanged setup, or protected/regulatory changes.
Isolated implementation branch `experiment/fmx-night-20261007`, worktree
`../_worktrees/futuramax-night-20261007`, source snapshot commit `8b29adc`.
Main dirty work is preserved. Root owns integration/build and independent
review; two existing workers own disjoint endpoint evaluator and driver patch.

- [x] Baseline: endpoint guard 23 tests PASS; aggregation policy 10 tests PASS.
- 04:52 UTC: first candidate build and8image/embeddedmodule checks PASS.
  Independent second-copy reproduction and final artifact review ongoing.
  Offline statistical validity/Welch25tests+503comparisons PASS; no live policy.
- Overnight 04:16 UTC: evaluator 8ca668d (34 tests), exact-C guard c9dbc23
  (4 tests, 8063 assertions), verifier 9dfcf99 (Linux 28 tests) PASS in isolated
  worktree; module cross-compile EXIT=0. First full-image compile FAILED in
  util-linux GCC internal segfault; preserve log and diagnose before repair.
  No radio work or physical operator action needed for this offline step.
- 05:16 UTC superseding checkpoint: isolated candidate artifact review PASS;
  replica failed in host Perl before driver compile, reproducibility NOT_PROVEN.
  No restart/unchanged retry. C1 decoder3438b3a and independent review PASS:
  40focused/111affected tests; saved captures30000/357/0frames, no classifier/RF
  acceptance. Detailed evidence in isolated worktree docs at7960743; portable
  candidate/proof/failedlogs rehashed under its ignored firmware/build/ directory.
- [x] Phase 1 harness: offline evidence evaluator, receiver goodput, failed or
  partial matrix rejection, diagnostic seed classification, malformed-input tests.
- [x] C2 preparation: exact-C regression for aggregation-input narrowing,
  strict pre-narrowing validation candidate; no live policy experiment.
- [x] Isolated OpenWrt candidate build: no shared source/stamp writes or pkill; compile
  candidate module then package images, preserve first failure and build hashes.
- [x] Independent review plus source/patch/image provenance and safety checks.
- [ ] Independent build reproduction: host Perl/WSL failure; exact cause UNKNOWN.
- [ ] Morning checkpoint: exact commits, test/build results and remaining
  hardware limitations. No claim of performance gain from offline success.

Iteration metric is completed fixed acceptance checks for the above artifacts,
not simulated Mbps. Verification: focused unittest suites, extracted exact-C
regression, cross-compiler exit, image/hash/module checks; higher completion is
better, existing guard suites must remain green. Max two repair attempts per
subtask. Candidate commits stay isolated; no merge/push. This existing plan is
the durable queue; do not open a competing project backlog.

Latest run after operator turned Nano farther and closed doors:
`endpoint-8f65a1bc4749487b920634ee53956b26`. Both radios were commanded and
read back at **0 dBm during the experiment**, not 11 dBm. Idle RF passed:
AP [-59,-58,-58], Nano [-62,-62,-61]; stability 15/15 pings each. First
randomized cell (100 Mbps UDP uplink, 10 seconds) failed loaded RF: Nano
[-53,-53], AP [-62,-59]. Receiver goodput 73.531 Mbps, reported UDP loss
24.925%; link pings 11/12 each, maximum RTT 87.304/370.306 ms. Invalid sample,
not accepted capacity. Remaining 29 cells NOT_RUN; no unchanged retry.
Restoration PASS: **11 dBm only after the run**, exact owned routes/NAT absent,
2/2 health pings each. Independent raw review PASS for integrity, not acceptance.
Source check: build backports-6.12.52 net/mac80211/cfg.c:3080 rejects negative
fixed/limited mBm with EOPNOTSUPP. Zero is the minimum of this normal API;
software readback is not a calibrated measurement of radiated power.
Do not ask for physical changes on the mistaken premise that tests used 11 dBm.
Remaining physical RF adjustment request is pending; operator challenged power
handling, and the zero-power execution and API floor have now been verified.

ACTIVE after explicit operator continuation. Notebook live status READY, x86,
zero restarts/errors; address .170 and Nano wired link1000F confirmed. Guarded
external PC-to-notebook route verified with1MiB received eachdirection, exit0,
without SSH data tunneling. AP source-bound DNAT .2:5204->.170:5201 plus exact
temporary AP/Nano /32 routes; all removed and both11dBm/2pings verified on exit.
Fresh0dBm RSSI AP[-62,-61,-60], Nano[-63,-54,-63]: P0.3 FAIL, full performance
matrix NOT_RUN. Preserve the -54 sample; no retry-until-green. Asked operator
to turn Nano farther sideways with doors closed. Independent source reviewPASS,
18hermetic regressionsPASS; rawendpoint-7a98e077224b4a128c20285d34af055b.
Three associated stations remain; only Nano endpoint carried requested load.
Capacity acceptance and Phase3 remain gated. Notebook staysrunning.

- [x] Continued unblocked Phase 1 endpoint diagnostics: exactly two 10-second,
  single-stream TCP transfers, 70.92/59.56 Mbps down/up, SEED only. Notebook
  iperf process CPU 2.81/0.62%; transmitting radio whole-host CPU 86.91/85.10%.
  All 48 sampled link pings received; maximum loaded RTT 112.05/29.35 ms.
  Not a capacity result: RSSI too strong, one cell each, three associated peers,
  DNAT and radio telemetry overhead. Full endpoint-wide CPU not sampled.
- [x] Verified both guards exited, both 11 dBm restored, owned routes/NAT absent,
  two health pings per radio received; notebook remains READY.
- [ ] Physical RF adjustment requested. Then run fresh guarded P0.3/stability
  qualification and continue full endpoint matrix without another generic
  "continue" request. The existing acceptance gate is not a blanket prohibition
  of bounded diagnostic seeds; do not reinterpret diagnostic results as a pass.
  Evidence: endpoint-222bee30e0bf42c0bb8deb637c5c79cd. Runner tests: 23 PASS.

Latest bootstrap checkpoint: generated local folder
`artifacts/notebook-bundle-20261006-223901-cd0f2c630c564daf9acab9c5a242f8c5/FuturaMAX-Notebook`
replaces the incorrect x64-only bundle: notebook is x86, now selected automatically.
Hash/PE and 32-bit PowerShell tests PASS; actual x86 runtime BLOCKED on controller
by Defender, not bypassed. Notebook acceptance is still pending. [OP] Copy whole folder by USB,
double-click START_FUTURAMAX.cmd, approve UAC, keep READY window open. This
supersedes the manual online script; prior Internet guards are cleaned up.
Next: inspect notebook identity/status/listener; then execute the existing
guarded endpoint routing and synchronized performance plan when authorized.
Do not resume RF solely because the package build passed. Notebook/network/UAC
acceptance and endpoint throughput remain NOT_RUN.
Bounded repair record: one repair each for atomic JSON binding, PS5 BundleRoot
fallback and native ExitCode handling; first failures preserved in CURRENT_STATE
and local loopback artifact. No unchanged failed RF experiment retried.

**HISTORICAL PAUSE (superseded above):** operator said "I give up" after Windows download certificate-trust
failure. No further operator steps requested. Both temporary Internet guards
stopped and cleanup independently verified; radios remain at 11 dBm. Notebook
server/endpoint tests NOT_RUN. Older continuation items below require resumption.

- Operator resumed work after the instruction-only pause. Both doors closed,
  radios facing each other, 8 m apart; Nano has no direct LAN connection.
- [x] Combined closed-door/0 dBm runtime probe: AP -52 dBm, Nano -46 dBm;
  averages -51/-47. Eight pings each, no loss. Ten-second hold after sampling
  on each node avoided the earlier sample/restoration overlap. P0.3 NOT_MET.
- [x] Restored both radios to 11 dBm; independent follow-up readback plus 3/3
  pings each passed. No persistent configuration changes.
- [x] Runner transport repair: `FMX_CPE_VIA_AP=1` uses AP SSH forwarding to
  Nano `10.99.0.2`; default direct-LAN mode remains compatible. Legacy persistent
  power, channel-width and reboot operations refuse wireless-only mode before
  device commands because they do not have guarded recovery for this topology.
  Four offline tests PASS and live read-only SSH/ping verification PASS.
- [x] Operator turned Nano sideways. At 11 dBm: AP -53/Nano -47 dBm, 5/5
  pings each. Guarded 0 dBm: AP -62/Nano -64; AP lost the first of 8 pings,
  Nano received 8/8. Retain that transition loss, not a clean stability pass.
- [x] Settled follow-up at 0 dBm after 5 seconds: three samples each,
  AP -61/-61/-62, Nano -64/-64/-63 dBm; all 30 pings received, RTT
  1.299-3.269 ms. Sampled P0.3 met for this exact configuration only.
  Both radios restored to 11 dBm; independent readback and 2/2 pings each
  confirmed health. Future experiments must reapply guarded 0 dBm and recheck
  RSSI; the restored operating point is not asserted to meet P0.3.
- [ ] CPU-independent offered-load endpoints still required for performance
  acceptance; radio-hosted iperf seeds are not RF capacity measurements.
  Nano Ethernet carrier is 0 / br-lan NO-CARRIER. Operator asked whether an
  Ethernet laptop/PC is available at Nano's PoE LAN port; answer pending.
  Operator has spare equipment and requested justification/access explanation.
  External PC is not required for all tests; use it to separate test-generator
  overhead from forwarding. No remote access established or endpoints configured.
- [x] Direct-radio seed after fresh guarded 0 dBm gate: 10 s TCP, one stream,
  down/up 139.55/93.72 Mbps. AP CPU 86.7%/55.0%, CPE 67.0%/60.2%.
  Loaded ping down 8/8, up 7/8: retain loss and seed-only classification.
  Immediate restore 11 dBm, 2/2 pings each verified. Not an RF-capacity verdict.
- [x] Notebook attached at .170: Nano Ethernet carrier 1, 1000 Mb/s full duplex,
  ARP neighbor confirmed. Supersedes earlier carrier-0 checkpoint above.
- [ ] Notebook test-server setup: Windows confirmed; no remote access established.
  TCP 5201/22/5985 probes via Nano timed out (not proof of closed ports).
  `tools/bench/start_notebook_server.ps1` prepared and PowerShell syntax checked,
  not executed on notebook: pinned portable iperf 3.22 SHA256, exact NIC/IP check,
  temporary /32 return route via Nano, program/interface/source-scoped TCP/UDP
  5201 rules and finally cleanup. Operator must launch once in elevated PowerShell.
  Keep window open; use Ctrl+C for cleanup, not force-close. AP/controller forward
  routes still need guarded setup after service access is established.
  UPDATE: notebook has no Internet route; bootstrap is now offline-only and uses
  bundled `packages/iperf-3.22-win64.zip` with the same pinned checksum. Recopy
  complete updated bench folder to F:\bench. Seven local tests PASS; notebook
  rerun pending. Do not use the old standalone script staged on Nano.
- [ ] Isolated endpoint route: AP currently sends .170 to local br-lan because
  both wired sides use 192.168.1.0/24. Resolve before testing; do not benchmark
  an SSH tunnel or accidental local/Wi-Fi path as wireless forwarding capacity.

## Standing conditions (apply to every measurement)
- Bench distance 1–2 m, no attenuators → receiver overload is possible; every number is a SEED
  until repeated at ≥ -55 dBm (attenuators or physical separation, **[OP]** item P0.3).
- iperf3 on 535 MHz MIPS is CPU-bound around 150–200 Mbit/s TCP; UDP + multi-stream used to separate
  CPU from air. Say so wherever a number is quoted.
- A/B/A/B blocking (D-0009): every "knob" run is baseline / knob / baseline / knob, same duration.
- Never write u-boot / u-boot-env / EEPROM. Lab radios only.

## Phase 0 — prerequisites
- [x] P0.1 Both AC radios on the FuturaMAX image, link up, air hop routed (10.99.0.0/24). 2026-10-05
- [x] P0.2 Bench runner `tools/bench/bench.py` (status / tcp / udp / loaded-rtt / aql / spectral / sweep).
- [x] P0.3 Sampled 2026-10-06: 8 m, Nano sideways, both doors closed, temporary
  0 dBm both ends. All six settled aggregate RSSI samples <= -55 dBm. Must
  re-establish this configuration and validate at each actual load experiment.
- [x] P0.4 VERDICT 2026-10-06: LB5AC and loco M5 written off. Both were re-tested on ports 3/4 with other cables and factory-reset twice by the operator; result unchanged: PHY links at 100 Mbps with PoE, <10 frames ever received, nothing at 192.168.1.20, no urescue, no discovery reply. Bootloader never runs → only UART/SPI rescue could change this (ruled out: no serial). Not bench gear.
- [ ] P0.5 Credentials for the LiteBeam M5 (airOS 6, customer config) — try the operator's standard; else **[OP]**.

## Phase 1 — AC link baseline (FMX-0007 seed, FMX-0008, C1)
- [x] 1.1 Persistence: PASS 2026-10-05 21:51 — both rebooted, config intact, link re-formed unattended in 92 s (bench.jsonl kind=persist).
- [x] 1.2 Txpower sweep DONE 21:58 (3/7/11/15 dBm): RSSI -52/-48/-43/-41 dBm; TCP up/down 113/38?→ re-run 38/61, 117/73, 138/143, 143/140 Mbit/s. Plateau ≈140 at ≥11 dBm = CPU ceiling, not overload. **Operating point: 11 dBm both ends.**
- [x] 1.3 Throughput matrix DONE 22:05 (seed; several TCP cells lost to a runner race, re-run as 1b; UDP capped ~33 Mbit/s by iperf3 pps on this CPU = tool artifact). Uplink loaded RTT >> downlink (p95 40 ms, max 490 ms vs 10 ms) — the bufferbloat signature.
      Original item: Throughput matrix: TCP 1 and 4 streams, UDP 50/100/200 Mbit/s offered, both directions,
      widths 20/40/80 MHz, each with concurrent ping (loaded RTT) — 10 s runs, A/B/A/B where a knob is involved.
- [x] 1.4 FMX-0008 AQL A/B/A/B DONE 22:08 (down, 4 streams, 12 s): AQL on p50/p95 ≈ 28-33/39-42 ms; AQL off ≈ 40-50/50-63 ms with one 3.8 s max. Direction consistent across blocks; magnitudes inflated by CPE CPU saturation. SEED, repeat at 1 stream + attenuation.
      Original item: FMX-0008 AQL on/off A/B/A/B at 80 MHz, downlink saturated: loaded RTT p50/p95/p99, goodput.
- [~] 1.5 C1 spectral: historical idle capture30,000samples(2.79MB, bufferfull), loadedcapture0bytes. The earlier explanation that scans cannot run under saturation is UNPROVEN. Exact driver rejects80MHz/64bin records. On2026-10-08 manual128bin/no-scan idle capture delivered16validrecords. New loaded attempt e163 also produced16validrecords, but missed rate/loss/timing gates: loaded qualification remains NOT_ACCEPTED, overlap UNKNOWN. Restoration PASS. Further timing repair needs additional round authority (2/2 exhausted). Original saturated/background distribution comparison remains incomplete; do not repeat the legacy scan helper unchanged.
      Original item: C1: background spectral capture on the AP during a saturated downlink and during idle; archive + parse
      (sample count, bins, per-channel), compare distributions idle vs loaded.
- [x] 1.6 CT debugfs inventory captured → research/raw/bench/2026-10-05/ct-debugfs-220848.txt (see CURRENT_STATE for what it shows).
      Original item: CT debugfs inventory on the live link: fw_stats, peer stats (`last_tx_bitrate` non-zero?), ratemask
      presence; record what is actually observable (feeds QCA988X_CONTROL_BOUNDARY §4e).
- [x] 1.7 Results recorded2026-10-07 in `docs/EXPERIMENTS.md` and CURRENT_STATE: FMX-0007 SEED/NOT_ACCEPTED, FMX-0008 INCONCLUSIVE. Documentation complete; physical acceptance remains pending.

## Phase 2 — the 802.11n units (SXT Lite5, LiteBeam M5) as stations and stressors
- [x] 2.1 Inventory DONE (SXT: a/n only, 2 chains, RouterOS 6.35.4 factory → exported; M5: XW airOS 6.1.4 customer config, creds unknown)
      Original: Inventory both as-is (SXT RouterOS 6.35.4: wireless caps, bands; M5 airOS 6.1.4: board, radio, config) read-only.
- [x] 2.2 C6 seed DONE 22:32: anomaly reproduced — MCS-0 N station uploading 6 Mbit/s cuts the AC station from ~125 to ~33 Mbit/s (-74%) and p50 RTT 7→29-44 ms. Downlink variant (airtime fairness territory) needs the SXT attenuated → **[OP]**.
      Earlier: SXT on OpenWrt joined the AC AP (22:18); contention run done 22:24 (loco -30%, RTT x2 with a FAST N station); MCS-0-pinned slow-station run launched 22:26.
      Original: C6 "performance anomaly" seed: SXT (RouterOS station, 802.11n) joins the AC AP as a slow HT station
      alongside the loco; measure loco goodput and loaded RTT with/without the N station active (A/B/A/B);
      then with mac80211 airtime fairness weights changed on the AP (`iw station set airtime_weight`).
- [ ] 2.3 C7 interference seed: SXT and/or M5 as a foreign AP on the same/adjacent channel with its own traffic;
      spectral capture on the AC AP during it; AC link goodput/RTT impact (A/B/A/B).
- [x] 2.4 OpenWrt images BUILT 2026-10-05 22:07: `ubnt_litebeam-m5-xw` + `ubnt_nanostation-loco-m-xw` (generic tree → `firmware/openwrt/futuramax-r28959-spectral/`) and `mikrotik_routerboard-sxt-5nd-r2` (ath79/mikrotik → `firmware/openwrt/futuramax-r28959-mikrotik-sxt/`, sysupgrade sha256 b344cd19…). Caveat: loco M5 on port 7 may be XM (ath79/tiny) not XW — confirm sysid before flashing.
- [ ] 2.5 Flash plan per unit — researched 2026-10-05 22:12:
      - **LiteBeam M5 (XW, airOS 6.1.4):** OpenWrt wiki: GUI refuses FW < 6.1.3; path is TFTP-downgrade to XW 6.1.3 then TFTP the OpenWrt factory image (XW urescue accepts unsigned images). **BUT: OpenWrt 23.05+ on this board requires downgrading U-Boot to 1.1.4-s776** — a bootloader write, forbidden by AGENTS.md §4. → **[OP] decision:** waive §4 for this throwaway unit (it has no serial, same unrecoverable-on-failure risk) or keep it on airOS 6 as the foreign/N stressor for 2.3. Default: keep on airOS.
      - **SXT Lite5:** no wiki page; standard ath79/mikrotik path = RouterBOOT netboot (set `boot-device=try-ethernet-once-then-nand` over SSH, reboot, serve the initramfs-kernel via BOOTP+TFTP from this PC), then `sysupgrade` from the running initramfs. Fully remote, falls back to NAND if netboot fails. RouterOS license to be exported first. → execute after Phase 1 (needs a BOOTP/TFTP responder on the bench NIC).
      - **loco M5 (port 7):** silent like the LB5AC was on that port (3 frames) → suspect port 7/cable; **[OP]** move it to port 3 or 4 with another cable.
- [~] 2.6 Mixed-stack: SXT on ath9k is a station of the AC AP since 22:18; ath9k fixed-rate (`iw set bitrates`) works where ath10k cannot.
      Original: Mixed-stack tests: N units on OpenWrt/ath9k as stations of the AC AP; repeat 2.2 with ath9k host-side
      rate control visible; record what ath9k exposes that ath10k does not (hMAC lineage).

- [x] 2.7 FOUR-TECH CELL DONE 2026-10-06 11:51 (seed, 2 rounds A/B each direction, 12 s, 11 dBm, no attenuation): LAP-120 AP (ath10k-ct) + loco 5AC (ath10k-ct VHT80) + SXT Lite5 (ath9k OpenWrt HT40) + LiteBeam M5 (airOS 6.1.4 proprietary driver, HT40 MCS7 1-stream, bridge mode, traffic from the PC via alias 10.99.0.155 + Windows iperf3.exe). Alone down/up: loco 141/134-142, SXT 81/141-144, LBM5 66-68/92-93 Mbit/s. All three loaded: down 50+48+39 (Σ137, loco RTT p50 17-19 ms vs 5 alone), up 50-59+33-40+41-45 (Σ123-144, loco RTT p50 29-31 ms vs 8). Aggregate ≈ the AP's ~140 Mbit/s CPU ceiling in both directions, so the near-equal split is the CPU-bound iperf server, NOT an airtime-fairness result; repeat after attenuation and with UDP/pps-light traffic before reading anything into the split. Runner: tools/bench/fourtech.py.
      LiteBeam M5 config applied (airOS, saved with cfgmtd): SSID FuturaMAX-LAB, airMAX polling off, txpower 10 dBm, hostname fmx-n-lb5, br0 alias 10.99.0.4/24. The airOS bridge carries bench-LAN broadcasts over the air (harmless now: AP wlan is routed, not bridged) — keep in mind for airtime accounting.

## Phase 3 — autoresearch bench (D-0009), only after Phase 1 is repeated with attenuation
- [ ] 3.1 Freeze the bench harness (topology, traffic, metrics, validity gates) from the Phase 1 runner.
- [ ] 3.2 First mutable policy: AQL operating point + `htt_max_amsdu_ampdu`; lexicographic objective.

## Log
- 2026-10-05 21:58 plan written; Phase 1.1 started.
- 2026-10-05 22:07 1.1 PASS, 1.2 DONE (op point 11 dBm), 1.3 matrix done, 1.4 running, 2.4 images built (M5 XW, loco M5 XW, SXT).
- 2026-10-05 22:13 Phase 1 chain + 1b re-run DONE. 1b TCP (10 s, loaded RTT): VHT80 down1 62 Mbit p95 32 ms; down4 78 Mbit **p95 1118 ms, max 5170 ms**; up1 98 Mbit p95 17 ms; VHT40 down1 123 Mbit p95 22 ms; VHT20 down1 37 Mbit. Run-to-run spread is large (same cell 60-140 Mbit across runs) → every Phase-1 number stays a SEED; repeat as ≥3 A/B/A/B blocks after attenuation. SXT netboot in progress (BOOTP+TFTP OK, 6.76 MB in 4.3 s).
- 2026-10-05 22:26 SXT flashed to OpenWrt remotely (netboot+sysupgrade), joined as fmx-sta-n1; C6 contention seed done; MCS-0 slow-station run in progress.
- 2026-10-05 22:32 C6 anomaly reproduced (uplink hog variant). Autonomous queue now blocked on [OP] items: attenuation/spacing (P0.3, downlink C6, Phase-1 repeats), port-7 re-test of LB5AC + loco M5 (P0.4/2.5), LiteBeam M5 bootloader decision (2.5), M5 credentials (P0.5).
- 2026-10-06 00:05 PAUSED by operator. Bench state: fmx-ap1 LAP-120 192.168.1.2 (AP ch36 VHT80, 11 dBm, AQL on, wlink 10.99.0.1); fmx-cpe1 loco 5AC 192.168.1.3 (10.99.0.2); fmx-sta-n1 SXT 192.168.1.4 (10.99.0.3, rate mask reset); fmx-n-lb5 LiteBeam M5 192.168.1.5 (airOS 6.1.4 factory, ubnt/ubnt, station mode idle); loco M5 on port 4 silent/unknown; ES-10XP 10.10.100.90; PC aliases 192.168.1/10.10.100/192.168.88/192.168.11 .155 on "Ethernet 2".
  RESUME HERE: (1) loco M5 → urescue (reset held while plugging in), then `python safety/recovery/urescue_push.py --image firmware/openwrt/futuramax-r28959-spectral/openwrt-ath79-generic-ubnt_nanostation-loco-m-xw-squashfs-factory.bin --expect-sha256 ec5d56d9… --yes` without probing first; "Firmware check failed" ⇒ build the XM profile (ath79/tiny `ubnt_nanostation-loco-m`). (2) P0.3 attenuation → repeat Phase 1 as ≥3 A/B/A/B blocks (`tools/bench/bench.py matrix --no-udp`, `aql-ab`), then downlink C6 (`anomaly` with the SXT attenuated). (3) 2.3 interference seed with the LiteBeam M5 as an airOS-6 AP on ch36. (4) LB5AC re-test on port 3. Docs: CURRENT_STATE addenda 2026-10-05 21:55/22:15/22:25/22:32 hold the results.
- 2026-10-06 16:50 operator re-reset loco M5 + SXT; re-check: SXT fmx-sta-n1 back on OpenWrt (192.168.1.4, uptime 7 min), LiteBeam M5 airOS at .5, loco M5 still silent → P0.4 closed as dead. Bench stays parked per the 00:05 resume steps.
- 2026-10-06 11:51 four-tech cell measured (2.7). Bench now: 4 radios up, AP iperf3 servers on 5201/5202/5203, PC alias 10.99.0.155 on Ethernet 2, iperf3 3.22 installed on Windows (winget ar51an.iPerf3). Still blocked on P0.3 attenuation for anything beyond seeds.

### E2 necessary no-load recovery contract - October16 17:43 UTC

Question: recover safe buddyheadroom after100M withoutreboot/cacheflush or
changingload/abortcriteria. CurrentCPEbuddy3035pages/PCP1836/available4784KiB;
Linux6.6.110rmqueue_bulk subtractsNR_FREE_PAGES whenmoving buddytoPCP, while
free_unref_page_commit drains whenPCPcount exceedsreducedhigh. Bothheldsource
and earlierphysical20s treatments support redistribution, not anOOMcure.

Define a SEPARATE explicit RECOVERY_ONLY_NO_LOAD profile inexistingPCPtool.
Default20sprobe contract remains unchanged and its oldsource/preimages/results
reproducible. Initialrecovery-only eligibility requires originalboot/services,
noOOM, boost0/min2048, VM8192/15000, fraction0/high2560/batch3, exactoneCPU,
nonnegativecount<=2560, buddyfree>2560(512pages abovezone min),
MemAvailable>4096, buddyfree+PCP>=4096 and available+PCP*4>=8192. These sums
are accounting eligibility only, NOT measuredMemAvailable, loadadmission,
contiguity or a physicalreserve guarantee. Record both rawvalues and sums.

Arm existingexactboot/tag/PIDstart/session detachedguardian BEFOREintent/write;
explicitfraction0->64 lowershigh219. Every postwrite sample MUST pass existing
free>3072/available>4096, 2sfreshness, identity/VM/OOM checks andexactPCPhigh.
20s maximumtreatment/40s guardian; exactownedCAS64->0restore andfullposthash/
RF/daemon/boot/lock/ownedexit readbacks. Preserve all failures. No RF/load.
Sourcefixtures + independentreview + freshnativepassiveguardianqualification
required beforethisnewprofile. If it fails, retainnegative; do not repeat
unchanged or loweritsinitialeligibility. Park200untilactualfresh4096/8192
loadadmission under restored0 plusindependentreview. No permanent64decision.

### October16 17:50 UTC - preserve recoveryFAIL, independentlyadmit200M

CPE993af24 recoveryFAIL atseq1 preserved; onlyseq0fraction0numeric2999/4688
PCP2053 retained. Actual64sample failedbeforeemission; late-draindetailINFERRED.
RestorationPASS original0/high2560, originalboot/services/hash/RF/VM/noOOM,
exactownedexit/lockabsent; final5022pages/12780availablePCP87. Independent
resultreview7e4ec793 confirms no closureofrecovery or universal20sPASSgate.
AP96f20c recovery20sPASS/restore0. No unchangedrecoveryretry or supportrepair.

Independent freshbilateral fullsnapshot17:50 post-recovery-original-admission:
AP5123pages/12952KiBavailable,CPE4998/12684, sourceboundhashes/birth/boot/VM/RF
unchanged vs100Mfinal, noOOM, associated, fraction0both/locksabsent. Original
4096/8192loadadmission met withoutPCPsum. This is newadmission, NOT rescueofFAIL.
ExecuteONE200M30s original0policy reverseUDP/45sobserver/33sdeadline/11dBm
RF-as-is, source-onlyreviewb2f56a5f20bindings; same2s/3072/4096aborts and
15pre/30post/fullcleanup. Question: can currentoriginalpolicy safelysurvive
ratewhereearlierOOMoccurred, withobservedlossandmemorylimits recorded?
Stop/park onanyguardfailure; retainfailure andspecifictiming/memoryevidence.
No baselineOOMgate change orperformanceclaimbeforeindependentreview.

### E2 200M failure and minimum phaseprofiling - October16 17:57 UTC

Actual e91a8cf61bea4bb0ac668f00dc25c378/endpoint-e2d4e025846e4dcda97f883a6c413f8a
FAIL_PRESERVED. Clientstart220934.468, freshnessfailure220945.343 (10.875s);
CPElatest2035ms, no controllerqueue, lastseq12local449ms/transportbound118ms,
thenno newreaderline. AP14/CPE13partial, min4172/9148 and4124/9188, noheldOOM.
ClientJSON0; no validgoodput or complete30sexposure. Originalpartialobserver/
remoteexitunverified flags retained. Rootlease/restoration/30posthealthpassed;
lateexactPID/birth/bootownedexit verifiedboth,0fraction/locksabsent/samefull
identity. Independentreviewc97546db confirms acquisitionFAIL/noOOMobserved.
LateAP4108pages8892avail,CPE4019/8768; no newloadadmission. Causebetweenremote
acquisition/SSHreaderpathUNKNOWN, notexplainedbycontrollerqueuebacklog.

Necessarychangedhypothesis: which originalsnapshot phase costs time atidle,
and can instrumentation reduce itsowncost withoutlosingfullroster/OOM guards?
Minimum evidence passive5s phaseprofile BOTHroles fromexactfc21observer, ONLY
nowtimestamps andextraJSONphasefields; retainoriginal5sloop/2s/policy/boot/
service/OOM checks, no RF/configwrites/newexecutor. UseexistingpinnedWiredIO,
outerboundedtimeout, originalmemaborts; no devicehelperinstall. Separatepure
generator+fixtures underraw, sharedobserverunchangeduntilprofilingjustifies
repair. Idleprofilecannotprove loadedcausality. Stoponfailure; do not change
2sfreshness or repeat200M unchanged. Independentreviewbeforeloadedchanges.

Independent55cellenablingwork: extendexistingGatewaynetworklease explicit
RRULprofile while retainingdefault5201exact.13exactINPUTrules onlyTCP5205/
5210..17, UDP5218..20, ICMPecho-request, same.155/32source/.170destination/
enp1s0/returnrouteviaCPE. NoSSH/FORWARD/securitydefaultschanged; preimages and
old69c11review kept. Sourcefixtures+independentreview+nativepassivequalification
required, noRRULload. This support mustnotdisplace nextphysicaldecisiveprofile.

### Operator-requested five-minute200M diagnostic - 2026-10-16T20:17:50.183976+00:00

Operator explicitly requests ONE200MbpsUDP test for300seconds without the
2000ms telemetry-age abort. This is the only active scope; the larger goal
remains paused. Use existing pinned AP/CPE/Gateway and11dBm/channel36/80MHz,
original restoredVM/PCPpolicy and existing900s independent endpoint/network/radio
leases. No switch access. Reuse transport, snapshots andRF-as-is guards.
Record native5s iperfJSON intervals, slowhealth every10s and timedoutreads as
gaps rather than2s aborts. Retain actualOOM/identity/memory3072/4096aborts and
initial4096/8192admission, 310sownedclientdeadline, fullcleanup+30posthealth.
FreshpassivePCPredistribution restores0 beforeload; not a treatment underload.
This diagnostic cannot retrospectively pass failed30s runs or acceptE2.

### 2026-10-16 20:33 UTC ? approved single 300-second observational repeat

Operator explicitly approved one 200 Mbps/300 s repeat with reserve floors as warnings and actual OOM, reboot or daemon loss still fatal (user699146795). No 2-second telemetry-age abort. Initial 4096-page/8192-KiB admission remains; unchanged RF11 dBm/channel36/80 MHz and full identities remain required. Known imperfect ping delivery is recorded as diagnostic quality, not baseline acceptance. First 105-second interruption and AP29/30 posthealth failure remain preserved. AP passive cache recovery92e0be84714d478f92e7305c341c44e1 restored original policy; CPE fresh4940pages/11744KiB/noOOM. Final caller f93fcbc2a56ad52d10c2ae06193776aa011dbadc6315e992095f5c71c7c0ed99 independently source-reviewed. Stop after this single repeat and cleanup/report; broad E2/comparisons objective remains paused.

20:38 UTC correction: observational repeat0fdd59a93a5e469eaead6645856a9d94 stopped after190.012s of recorded UDP intervals because CPE dynamic zone boost rose2048pages/min4096 while configured8192/15000sysctls stayed unchanged. No OOM/boot/daemon change;30/30posthealth both andcleanup[] verified. PreserveFAIL. This was an over-broad reserve check inconsistent with the approved observation; warning-mode now records dynamic zone reserves as warnings too, actual OOM and configured policy drift remain fatal. Default recipe/admission unaffected. One corrected300-second run completes the same outstanding request, no baseline/comparisons resumed.
