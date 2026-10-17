<!-- doc-head: FuturaMAX architectural decisions and evidence boundaries -->
2026-10-17 (Stage 8): KEEP zero-fork pure-debugfs `controller/fmx_adaptive_controller.sh` (`SINGLE_STA_TURBO` <-> `MULTI_STA_ADAPTIVE`), KEEP `VHT40` (40 MHz) recommendation for mixed `802.11ac + 802.11n` downlink-heavy WISP sectors (`+13.1%` DL goodput, `2.26x` spectral efficiency, `21.2x` fewer TCP retransmits), REJECT `iw dev phy0-ap0 scan ... ap-force` on active production APs (`102.4 ms` firmware scan sawtooth), and KEEP the full Stage 8 bidirectional cross-layer stack (`+49.4%` sector DL, `39.1x` weak-station RTT reduction).
2026-10-17 (Stage 7): KEEP multi-station `AIRTIME_FAIRNESS` (`airtime_flags=3`), bounded PtMP aggregation (`2x32` / `1x16` + `AQL 1500/3000`), `WMM AC_VO DiffServ Deficit Bypass` (`ip dscp set ef` in `fmx_fastpath`), and multi-station Uplink `RTS/CTS 256B` threshold when stations are obstructed/attenuated.
October16: requested200M/300s observation hits actual CPE OOM and wpa_supplicant death; recovered association, trialFAIL, broadgoal PAUSED.
2026-10-15: scope technique verdicts to actual claims; preserve synthetic/physical and static/runtime boundaries.
E2 stays NOT_ACCEPTED; retain AP OOM, original load recipe and operator gates.
<!-- /doc-head -->

## October 17 — Stage 8 Closed-Loop Controller, Channel-Width & Sector Stack Decisions (`KEEP` / `REJECT`)

Based on physical Stage 8 measurements ([`artifacts/stage8_ptmp/stage8_adaptive_and_sector_results.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/stage8_ptmp/stage8_adaptive_and_sector_results.json), [`docs/STAGE8_ADAPTIVE_CONTROLLER_AND_SECTOR_SIM.md`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/STAGE8_ADAPTIVE_CONTROLLER_AND_SECTOR_SIM.md)):

1. **`KEEP` — Zero-Fork Pure-Debugfs Closed-Loop Adaptive Sector Controller ([`controller/fmx_adaptive_controller.sh`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/fmx_adaptive_controller.sh))**:
   - Eliminates the static trade-off between single-station peak burst (`109.35–118.67 Mbps` in `SINGLE_STA_TURBO` with `Agg 3x64, AQL 3000/6000`) and multi-station fairness/latency protection (`90.12 Mbps` total with `5.33–7.27 ms` median RTT across all 3 stations in `MULTI_STA_ADAPTIVE` with `Agg 1x16, AQL 1500/3000`, proportional ATF weights `768:256:128`).
   - Must read `/sys/kernel/debug/ieee80211/phy0/netdev:phy0-ap0/stations/<mac>/airtime` via POSIX shell built-ins (`read`) rather than forking `iw station dump` + `awk` every second on 533 MHz MIPS APs.
2. **`KEEP` — `VHT40` (40 MHz) Channel Width for Mixed `802.11ac + 802.11n` Downlink-Heavy WISP Sectors**:
   - On sectors serving a mix of `802.11ac` and legacy `802.11n HT40` (`airOS M5` / `MikroTik ath9k`) CPEs, `VHT40` delivers **`+13.1%` higher simultaneous Downlink goodput (`105.18` vs `92.98 Mbps`)**, **`+56.7%` higher `LiteBeam M5` Downlink speed (`40.06` vs `25.57 Mbps`)**, **`21.2x` fewer TCP retransmissions**, **`3.1x` lower loaded RTT (`8.3–9.4 ms` vs `26.2–27.9 ms`)**, and **`2.26x` higher spectral efficiency (`2.630` vs `1.162 bit/s/Hz`)** while freeing 40 MHz of spectrum for adjacent sectors. Retain `VHT80` only when `802.11ac` Uplink peak (`155.70` vs `118.09 Mbps`) or single-CPE `802.11ac` peak (`223 Mbps`) is the primary requirement.
3. **`REJECT` — Active Off-Channel `iw dev phy0-ap0 scan ... ap-force` on Live `ath10k-ct` PtMP APs**:
   - Off-channel `ap-force` scanning on an active `ath10k-ct` (`10.1-ct-8x-__fW-022`) AP vdev traps the QCA988x PCIe target firmware in a `102.4 ms` beacon-aligned scan loop that survives `wifi reload` and requires `rmmod ath10k_pci` or AP reboot. Trigger `spectral_scan_ctl` passively on the operating channel without `ap-force` scan, or run off-channel spectral sweeps from an OpenWrt CPE (`Loco 5AC`).
4. **`KEEP` — Full Stage 8 Cross-Layer Sector Stack for Bidirectional Peak-Hour Load**:
   - Combining `fmx_adaptive_controller.sh` + `ATF` + `AQL 1000/2000` + `WMM AC_VO DiffServ Bypass` + Station `RTS/CTS = 256B` + Gateway `CAKE diffserv4 nat ack-filter` increases sector Downlink goodput by **`+49.4%` (`30.26 -> 45.22 Mbps`)**, increases total bidirectional capacity by **`+13.7%` (`134.58 -> 153.01 Mbps`)**, and cuts weak-station (`MikroTik SXT`) loaded median RTT by **`39.1x` (`251.25 -> 6.43 ms`)**.

## October 17 — Stage 7 Multi-Station PtMP Architectural Decisions (`KEEP`)

Based on physical 3-station heterogeneous PtMP measurements ([`artifacts/stage7_ptmp/stage7_ptmp_3station_results.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/stage7_ptmp/stage7_ptmp_3station_results.json)):

1. **`KEEP` — `mac80211` Airtime Fairness (`airtime_flags = 3`) + Tightened `AQL` (`1500/3000 µs`) + Bounded PtMP Aggregation (`1x16` or `2x32`)**:
   - Prevents low-MCS / wall-attenuated `802.11n HT40` stations (`MikroTik SXT Lite5`, `Ubiquiti LiteBeam M5`) from inflating sector-wide latency (`4.06x` lower loaded latency and `10x` fewer TCP retransmissions on `NanoStation 5AC Loco`, `3.95x` lower median latency on `LiteBeam M5`).
2. **`KEEP` — `WMM AC_VO DiffServ Deficit Bypass` in `fmx_fastpath` (`ip dscp set ef` for interactive/control flows)**:
   - Exploits `mac80211`'s independent per-AC Deficit tracking (`Deficit: VO = +256 µs` vs `Deficit: BE = -67,099 µs`) so interactive packets destined for a rate-limited/wall-obstructed station bypass its own `AC_BE` deficit penalty box (`21.0x` median RTT reduction on `SXT Lite5`, `8.0x` on `LiteBeam M5`, `3.84x` p95 reduction on `Loco 5AC`).
3. **`KEEP` (Conditional on Multi-Station / Hidden-Node Contention) — Station-Side `RTS/CTS = 256B`**:
   - While `RTS/CTS` is unnecessary (`-3.4%` overhead) on a single-CPE line-of-sight link, on a multi-station sector with obstructed/attenuated clients (`N >= 2` active uplink transmitters with >8 dB SNR asymmetry or wall/foliage obstruction), enabling `rts 256` yielded **`+18.5%` higher aggregate sector Uplink goodput (`150.40 -> 178.17 Mbps`)** and **`3.07x` higher weak-station Uplink throughput (`1.97 -> 6.03 Mbps`)**.

## October16 current ? requested 200 Mbps observation stopped on actual CPE OOM

The broad E2/three-comparisons goal remains PAUSED at the operator's20:14UTC stop. The subsequent narrow request was one200Mbps/300s observation without the2s telemetry cutoff; the operator explicitly authorized reserve floors as warnings, retaining actualOOM/reboot/process-loss stops. No further load is active or planned without a new instruction.

CONFIRMED physical result: corrected caller2332407d ran trial5b3dfaa4e9354684b644207ba51c0971 at unchanged11dBm/channel36/80MHz. Reception stopped around110s;145.014s of native intervals were retained, including35s zero delivery. Those intervals contain924301200received bytes (50.991Mbps over145.014s); no complete native final/end result exists, so this is not a300s aggregate. Kernel logs confirm CPE globalOOM killed wpa_supplicant1436; the host did not reboot. The CPE radio reinitialized and reassociated; wpa_supplicant now has new process births. This is an actual failure under the tested indoor/NLOS conditions, not proof that geometry or firmware alone caused all losses.

Both radios passed30/30posthealth after stop. Owned endpoint/radio rules and Gateway lease were cleaned; Gateway CLEAN_RESTORED/rc0. Fresh independent readback five-minute-200m-post-oom-readback.json confirms association, unchanged boots/config hashes/persistedRF/VM sysctls, AP unchanged daemon births and CPE changed wpa_supplicant births with retainedOOM. Therefore operational recovery is observed, exact pre-test process identity is not restored. FAIL_PRESERVED_RESTORATION_REVIEW_REQUIRED remains unchanged. No switch/production access or firmware flash occurred.

Earlier failed attempts are retained: efc6 stopped around105s on a preventive reserve floor;0fdd stopped around190s because an over-broad guard treated dynamic zone boost/min as configuration change (noOOM). These guard errors were corrected only for this explicitly approved observation; original E2 admission/acceptance are unchanged. E2 and all three comparisons remain unaccepted.

Raw: research/raw/bench/2026-10-16/endpoint-5b3dfaa4e9354684b644207ba51c0971/{five-minute-result.json,events.jsonl,client.stream.jsonl}; post-readback and independent final-result review are alongside.

## October16 - active goal prioritizes physical results and autonomous execution

Adopt the user's activated attachment as the current objective: accepted E2,
three real comparisons and final measured configuration. This explicitly
supersedes the prior offline-only priority/bench parking. Necessary reversible
bench work is authorized without repeated permission; necessary reflashing
retains exact-image, backup, recovery and protected-partition requirements.

Keep the original stronger baseline/five-repetition criteria. A partial Linux
matrix or five-second diagnosis cannot become accepted E2. Diagnose and review
the OOM/accounting cause before lifting the runner's deterministic physical
failure block; do not bypass it with another wrapper or weaken acceptance.
The final-provider/stock-airOS research dependency is parked rather than made
a requirement for OpenWrt measurements. Do not start a new executor platform.

## October16 - park optional capture and preserve memory admission

The physical50M/5s run survives, butzero-event packet capture leaves sequence
accountingUNKNOWN. Park optional capture refinement; do not require it for an
independent guarded duration/memory question. E2 OOM gate remains enforced.

Do not lower4096/8192 load admission to accommodate CPE quiet3940pages.
Test one Linux PCP cache-cap treatment64 passively for20s with qualified native
detached restoration to original0. This changes allocation caching only and is
necessary evidence for acquisition blocked by headroom. No permanent policy,
OOM cure, baseline acceptance or future-load admission follows automatically.
A later30s run still needs the original fresh bilateral gates and independent
source review; the already-reviewed45s observer/33s client recipe supplies only
the instrument. Preserve all failed and negative outcomes.

## October16 - causal finding versus next-rate/RRUL prerequisites

Keep observedPCP->buddy redistribution as Linuxallocator evidence. Restore0;
do not adopt64 permanently or lowerload/abortfloors. RecurringAP/CPE admission
failure warrants onlyfixed20s role-bound headroompreparation before nextrate.
Pin unchanged181335 diagnostic privately so unrelatedrateCLI changes cannot
alterqualifiedrestoration. Qualifyeachroleunder currenthashes; priorFAIL stays
FAIL.50M/30s survival is scoped evidence, not E2 OOM-gate clearance.

CurrentICSsource100.155 and successfulAPreturnroute establish wired return-path
cause. Discard unprovenSkipAsSource fix andinvalidoriginal-port filter inference.
BusyBoxdisplay omitsproto evenwhenadd/del useproto99; validate exactdest/via/
interface/metric plusboot/tag ownership, preserveforeignchanges andverifyabsence.
FutureRRULuses exactcontrol/data/ICMP NAT andsameGateway.1.155 sourceboundary;
noglobalnetworkchange. Source/endpoints are necessary acquisition support only.

Operator question October16 about10.10.100.90: exclusive lab ownership is
UNCONFIRMED. HistoricalOctober5 documentation lists ES-10XP bench radio ports
and an officeLAN uplink; it does not prove absence of production use. Exclude
this switch from further browsing/probes/configuration/power/port actions in
this goal. Priorchecks were connectivity/read-only web opening, no certificate
acceptance or switchwrites. Old browser-certificate request is obsolete; no
operator action needed there. Benchgoal remains scoped to already-identified
APfmx-ap1(.1.2), CPEfmx-cpe1(.1.3), PC and authorized Gatewayendpoint. No switch
access or sharedproduction remediation is a prerequisite for these experiments.

## October16 historical - qualified downstream chain, authorization preserved

The entry/peer/queue bridge and direct98f224 consumer now supersede the earlier
unresolved-reader checkpoint. Adopt static rate/flag flow into packet-budget
preparation, conditional on recorded address context. Final4065ac handoff is
not proof of hardware rate choice; require its matching initialized pointer,
destination bytes and runtime state before extending that claim.

Wire901f parameter3 maps normal authorization to internal8; do not confuse
internal8 with a wire parameter or promote authorization to an optimization
knob. No change to authorization, regulatory control or command admission is
authorized by this result. Six copied rates do not prove the dynamic count's
1..6 invariant. Preserve UNKNOWN rather than fabricate a bound or vulnerability.

The original-byte view controls over Ghidra's omitted hardware-loop iterations
and incorrect default literal aliases. Independently checked evidence supports
numeric/static flow, not proprietary code reuse or a CT command translation.
Park only the final-provider dependent branch for exact missing stock-runtime
material; do not repeat image scans or start unrelated tools. E2 remains parked.
Evidence: research/raw/reverse/2026-10-16-applied/NATIVE_RATE_CONTROL.md.

## October16 historical - receiver-only decision superseded above

Direct Ghidra analysis now supplies a new native9044 target callback/registration
and context-update chain. Adopt it conditionally on the recorded static address
context; do not claim LITBASE/runtime registration or radio obedience proved.
Ghidra's pseudocode collapses hardware loops in this target. Their original
instructions establish six and two iterations; do not implement a one-element
parser from that pseudocode. The final26-byte helper call has only25 explicitly
initialized projection bytes established, so its last byte remains UNKNOWN.
The helper's memcpy interpretation is inferred until its provider is qualified.
No CT command translation, firmware modification or flash follows automatically.
Candidate9972fc/997465 is a threshold reader at the same offset, not yet a
confirmed TX consumer: require caller/object identity before joining these
flows. Missing indirect pointer words in held artifacts do not prove ROM.

## October16 - explicit research-to-implementation chain

Operator feedback identifies poor planning as the reason to keep seeking new
approaches. Accept the concrete diagnosis: acquisition tooling displaced the
research question, and proprietary RE was not visibly linked to OpenWrt changes.
Keep one chain in BENCH_PLAN: limitation, exact-stack control, one change,
effective readback, comparative measurement and decision. Do not substitute
custom build existence, parser tests or restoration receipts for that chain.
The current evidence does not justify translating airOS commands into CT or
starting a new custom scheduler. Preserve OpenWrt lab continuity and the hybrid
product option; no flash/stack selection follows from this planning review.

## October16 - reverse-tool selection follows exact target support

Use the operator's seven-link review to assess capability, not to start another
tool-installation branch. REA is already installed; detected Ghidra does not
override its Windows provider's MIPS exclusion. Keep the existing qualified
Ghidra/ELF/SGMT route. Upstream Linux MIPS support is conditional on exact ABI,
ISA and relocation admission; it is not proof our held module imports there.
Eleven remains optional UI; selected apk-reverse readers cannot replace our
ELF32BE ET_REL mapping. Adopt independent oracles and exact source/address
provenance, without inferring target behavior from synthetic tests.

No new evidence from these links resolves the downstream runtime provider.
Park new imports and repeated known-path qualification unless they answer a
new bounded research question. No proprietary scheduler transplantation.
Latest capture d9410ae0 failed; preserve original warnings and later cleanup
proof separately. E2 remains NOT_ACCEPTED; no new RF attempt during this review.

## October16 02:18UTC - RF-as-is diagnostic reuse is necessary and scoped

Retain14/15 stability failure at0dBm and clean30/30 posthealth at restored11dBm;
the difference motivates a hypothesis, not a causal conclusion. Reuse the
operator's October7 RF-as-is diagnostic authority for the active receiver
accounting question. Historical0dBm/-55 baseline qualification stays unchanged.
One new diagnostic may preserve existing11dBm without ANY RF power writes;
RSSI becomes a recorded covariate. Keep15/15 stability, bilateral memory gates,
identities, regulator controls, capture/endpoint deadlines and full cleanup.
Independent review confirms existing authority, but source/runtime checks
remain necessary. No E2 acceptance, unresolved-OOM waiver or further reboot.
Operator rejected the proposed wired comparator: park it; no cable request,
loopback run or unrelated endpoint project. PCs remain external load endpoints
so radio-generated benchmark CPU is excluded from the forwarding measurement.

## October16 earlier decision - scoped50M survival, accounting unresolved

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

## October15 continuation - management recovery and fixed AP state diagnostic

E2 / FMX-0007 remains NOT_ACCEPTED. Fresh independent wired controls returned
AP30/30 and CPE30/30, while PC->Gateway was27/30 with RTT6..826ms. A separate
short Gateway->router interval returned40/40 and max120.989ms; that good
interval does not clear the intermittent management failure. Gateway AR9287 /
ath9k power save is already off; three cached same-SSID BSSIDs share channel1.
Later HT-to-legacy beacon disconnect/roaming is recorded, but original outage
causality is UNKNOWN. Infra has accepted the bounded endpoint-management
recovery task; root does not concurrently operate Gateway.

AP-only20s/21-sample observation stayed3980Normalpages/15920KiB, below the
unchanged4096-page admission. No OOM or service-birth change occurred. Paired
PCP growth accounts arithmetically for2152 of2200KiB of buddy-free decline;
48KiB remains unattributed in that comparison. This is not leak diagnosis or
permission to add PCP to the gate. Held6.6.110 code does not establish a local
PCP drain through stat_refresh; no useful owned-file cleanup was found.

Decision: after independently qualified management recovery, reuse ONE reviewed
AP software-reboot comparison, with fixed firmware/config/RF/VM, bounded
recovery and unchanged CPE identity/births. BENCH_PLAN fixes the treatment,
admission and stop criteria before execution. A failed fresh-state admission
parks50M; no repeated reboots until green. No reboot or new load was executed
for these read-only findings. Review is preparation, not wireless acceptance.

Evidence: research/raw/bench/2026-10-15/management-recovery-qualification-current.json,
gateway-wifi-driver-diagnosis.json, gateway-wifi-latency-correlation.json,
ap-memory-owned-artifact-census.json, ap-only-headroom-observer-derivation.json,
ap-headroom-pcp-decision-review.json and gateway-infra-recovery-request.json.

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


# FuturaMAX architectural decisions

### 2026-10-15 - Native capability evidence and scoped Linux endpoint lease

A non-admin process token is not a substitute for the native operation's
actual result. The operator-directed PC alias succeeded and is read back;
do not ask the operator to repeat an action already completed here.

The Linux endpoint retains the external forwarding path through AP DNAT5204,
Nano and Gateway Ethernet5201. Reuse the pinned radio guard/cell/restoration
implementation; use explicit Linux PID/startticks/socket/binary ownership.
The Gateway network lease owns only `.1.155/32 via .1.3` and source-specific
tcp/udp5201 INPUT rules. No persistent UFW/global install/SSH weakening or
VM changes. A root-owned fresh status permits non-root attachment without
passing a sudo password between lanes or storing it. Cooperative TTL is not
a SIGKILL or power-loss guarantee. The original down/UDP200 OOM recipe and
RRUL remain excluded from the nine-cell partial block, never relabeled as
full baseline acceptance. Missing legitimate Gateway sudo is an external
credential dependency; the exact local launcher is the minimum operator step.

### 2026-10-15 - Treat Gateway as a new external endpoint requiring real readiness

Gateway Omarchy behind Nano replaces the old Windows notebook implementation,
not its experimental role. Keep frozen E2 traffic/validity/restoration criteria.
A private Linux build and loopback qualification do not satisfy the old Windows
native-observation-v2 contract; implement and independently review actual Linux
binary/process/interface ownership before acquisition. Preserve source-specific
admission and the explicit return route. Do not reuse an unrelated open port
or alter SSH forwarding to bypass the Gateway's access restrictions.

Retain original failed netperf build and AP low-headroom/late-snapshot evidence.
The factor0 diagnostic stays separate from safe partial cells and never becomes
baseline acceptance. No route/firewall/VM/RF mutation is authorized by a PASS
label on private builds. The operator's temporary source-alias choice is recorded
in BENCH_PLAN; execution/readback remains required.



### 2026-10-15 - Evidence-scoped literature transfer; no acceptance from labels

Use the AutoResearchClaw synthesis/matrix as a qualified research crosswalk,
not an accepted hardware capability catalogue. CONFIRMED may mean a source
hook exists; it does not imply receiver obedience, runtime timing or target
performance. All expected numeric FuturaMAX gains remain UNKNOWN until
repeatable exact-build experiments. Native AX/BE PHY capabilities cannot
be inferred from an algorithm; software window scheduling without those PHY
features remains a separately gated unknown rather than universal impossibility.

Keep Stage1 external queueing/telemetry as plausible mechanisms preserving
airMAX, and Stage2/3 AQL/rate/aggregation as hook-qualified experiments after
baseline acceptance. CoTSQ's target-family historical evidence concerns
sender-local TCP and a temporal-budget patch, not arbitrary AP forwarding.
Stage4 remains NOT_PASSED; held RE1 serializers and CT register zeros do not
establish stock-airOS providers or deterministic TX authority.

Supersede October12 broad PASS claims: preserve synthetic fixtures as harness
evidence and three reported live seeds as unaccepted observations. Do not
convert reduced load into proven RF efficiency, hardcoded Jain into fairness,
or unchecked cleanup into restoration acceptance. Keep E2 NOT_ACCEPTED and
the prior AP OOM. Sources, hashes, independent review and exact remaining
experiments are in `research/autoresearchclaw/`; this decision authorizes no
device write, flashing, production change or automatic parked-task resumption.

### 2026-10-10 - Preserve an actual load-survival failure, not helper blame

Verified notebook traffic5201/5205 and auxiliary status5202, fresh READY and
unchanged processes after failure. UDP200 triggered AP kernel OOM killing
hostapd; fixed-stack baseline stability is not accepted even after successful
restoration. Keep the failed load and original acceptance. Neither reduce
offered load to obtain a pass nor mutate VM/queue policy without a justified,
reviewed changed-hypothesis treatment. Read-only watermark evidence narrows
diagnosis but does not establish its root pressure source or a safe fix.
This belongs to Linux/AP resource survival, not a proven QCA firmware defect.

### 2026-10-10 - Preserve the frozen recipe while resolving WSL source mismatch

Observed WSL ingress100.155 differs from admitted notebook lab source.155,
and AP lacks a return route. A route alone cannot satisfy notebook admission.
Critical review identifies exact-two-endpoint AP SNAT plus one return /32
inside existing owned TTL cleanup as minimal; no global WSL/Windows alias or
notebook-firewall changes. This needs explicit amendment of the frozen
counter-only/no-new-verdict recipe. Request that exact decision, not generic
continuation; do not mutate pending it or imply accepted E2. Notebook window/
READY and live WinNAT return evidence remain separate dependencies.
RE1.8 adopts only reviewed selected-table/host-stream facts and a qualified
negative; absent table words are not absent runtime/ROM initialization.

### 2026-10-10 - Keep peer visibility separate from calibrated airtime

Two reciprocal D2 checks prove visible station TX-duration deltas and firmware
peer rate snapshots on the preserved per-end builds. They do not prove real
on-air duration: host RX-duration is zero, firmware peer RX-duration is
inconsistent, module hashes differ between ends, and negotiated AP TX
width/rate changed. Preserve those limits and unknown extra-traffic sources.
KEEP field visibility; calibrated airtime remains INCONCLUSIVE. Independent
source/evidence review PASS_WITH_LIMITS; raw hashes freshly checked by root.
Do not use this result to accept E2, fairness or an AQL performance gain.

### 2026-10-10 - Preserve bootstrap branching and resume physical baseline

Operator whole-plan continuation supersedes RE1 priority parking only; retain
E2 gates and prerequisite order. Actual first guarded E2 attempt failed before
load at WSL source probe and restored exactly; repair its transport with new
evidence, without promoting that attempt or repeating it unchanged.
RE1.7 accepts only original-byte-backed host branch order and dynamic
board-relative byte patches. Bootstrap download/execution is conditional;
successful selector4 can bypass it. Host0x1234 and SGMT BEGINADDR0x983c00
must stay separate. Neither proves missing control-slot initialization or
target obedience. Preserve decompiler warning, unchecked BMI read/write
results, runtime board base and buffer byte-order uncertainty. Do not infer
ROM absence or patch live firmware from this static subset.

### 2026-10-10 - Separate host interface, stored image bytes and runtime authority

RE1.6 demonstrates native interactive MCP and a byte-checked nine-input host
rate-override branch. Host ro readback reads host-object fields; do not treat
this branch alone as a fresh target query or firmware-obedience acceptance.
The held bootstrap blob joins AP/PTP/STA in the static coverage inventory;
all four exclude the conditional indirect slots. Their absence from files is
not evidence that ROM or initialization cannot provide them. LITBASE remains
a register hypothesis, never an invented memory value. Keep duplicate ELF
local names resolved by actual relocation indices and reused oracles pinned.
Independent source/evidence delta review PASS_WITH_LIMITS; adopt only the
demonstrated host/static subset. Preserve candidate-only download pseudocode/
type warning and all physical/RF gates. Exact runtime control remains UNKNOWN.

### 2026-10-10 - Complete upstream Ghidra MCP; separate analysis edits from device writes

Operator explicitly corrected the earlier MCP parking decision and authorized
finishing integration. That earlier stop is superseded, not a newly discovered
hardware or licensing limitation. Reuse the already built upstream bridge and
decompiler: a small process launcher, private persistent copies of qualified
Ghidra projects, and exactly one MCP registration in each applicable Codex
configuration. Permit ordinary analysis annotations/types/functions while
excluding scripts, execution, debugger/emulation, export/import and destructive
tools from the client allowlist. Server authentication, file-root containment
and script disablement are separate controls, not read-only annotation hints.
The full HTTP catalog remains broader; no replacement server is built.
Actual MCP decompilation, AP bytes and annotation save/reload/restore pass,
with original hashes intact. Session catalog loading is a remaining client
step, not a reason to postpone setup. Do not change global hooks/rules merely
because their mismatch was diagnosed; continue safe authorized work under12.1.
Exact QCA context/runtime-control and RF acceptance limits remain unchanged.

### 2026-10-10 - Retain bounded headless artifact analysis; park broad MCP exposure

Actual ELF/MIPS and AP SGMT analysis now demonstrates useful native Ghidra
output read by agents. The compatible upstream bridge builds, but its
READ_ONLY annotations are hints; write/script/emulation routes are not thereby
disabled. Never started it or registered global MCP configuration. KEEP the
bounded offline artifact-analysis subset; do not build a replacement server
merely to finish this pilot. Independent re-review accepted this subset with
limits after one evidence-hygiene repair pass; first FAIL remains recorded.
Common-Xtensa syntax is partial evidence, not exact QCA qualification. Static
rate-bit packing agrees positionally with target extraction but does not prove
runtime semantics. Missing literal-base/ROM/indirect slots stop authoritative
downstream claims. Preserve original inputs, parsers and RF/recovery acceptance;
no80percent deletion, measured analysis speedup or wireless gain is established.
RE1's bounded pilot is closed, not the firmware-control research question.
Next target evidence request is in the receipt; device acquisition remains
a separate operator-gated exact-build/recovery task. E2 is still unaccepted.

### 2026-10-10 - Prioritize a qualified AI-assisted analysis workbench

Operator approved RE1 as priority1 in the existing BENCH_PLAN. Reuse established
Ghidra loaders/decompiler and compatible bounded read-only agent access rather
than rewrite FuturaMAX or automatically adopt REA. REA main's restricted MIPS
ET_EXEC profile rejects our held ET_REL modules; Xtensa is not admitted.
Qualify direct native Ghidra and headless integration on actual artifacts.
Allow only task-local dependencies/import databases; retain public artifact
hashes, independent byte/decoder oracles, unknown memory/ISA context and failed
results. Park E2/RF work without lowering its acceptance. The baseline freeze
now has this explicitly approved offline exception; all device/protected/
regulatory/signature and proprietary-code-copying boundaries remain unchanged.
Keep/replace/park existing analysis components only after demonstrated utility;
the operator's proposed80percent reset is not an established discard metric.

### 2026-10-09 - Freeze bounded E2 intake; reject old READY

KEEP minimum fixed five-block acquisition using existing radio/iperf guards,
not a new durable orchestrator or tuning loop. Dynamic RRUL uses one exact
temporary controller /32 per block, normal administrator token and independently
reviewed parent/TTL/ownership cleanup. Source verification is counter-only
inside the existing owned/TTL-cleaned NAT table; no broad DNAT or firewall change.
Completion requires restoration and settled posthealth even after failed loads.
Keep failed fixtures, actual board/QCA/component fingerprints and two-peer
topology; do not call those fingerprints a complete firmware image hash.
Operator launch acknowledgement is not endpoint acceptance: current status
is the old iperf-only helper, so require the approved package's Netperf identity
before this intake. No loaded ACK or optional tuning prerequisite.

### 2026-10-09 - Qualify real RRUL rather than substitute iperf

KEEP actual Flent2.3.0/netperf2.7.1 for the named E2 workload. Minimal native
Win32 TCP ephemeral-bind compatibility resolved the observed primitive
failure; source and failures are archived. Actual native and cross-OS
concurrent RRUL are locally qualified, independently reviewed.

This is external-controller/Windows/Linux acquisition support, not a
mac80211/ath10k/QCA/airMAX change or measured RF gain. Notebook and radio
acceptance remain separate. Extend the existing protected one-copy helper
only as required; no new orchestrator, global install or security weakening.
Dynamic netperf sockets require exact-program/source/interface firewall
scope on the notebook, not broad AP forwarding. Control -L alone does not
bind upstream data listeners. Freeze direct exact /32 route ownership,
WSL observed source, watchdog/cleanup and RF gates before radio load.

KEEP repaired existing notebook package for operator handoff after independent
offline approval. Netserver cleanup must retain handles, verify birth/path,
stop parent first and reject survivors after bounded child sweeps; port
provider uncertainty must reject startup. Preserve the first failed ZIP,
not a retry-until-green rewrite of evidence. Package qualification does not
attest notebook execution, UAC/firewall behavior or physical radio performance.

### 2026-10-09 - Compare published scalar representation and advance baseline

The public QCA9880 CSV omits FFT vectors/TSF/width, so it cannot validate
per-bin or timing equivalence. Actual frequency-filtered scalar comparison
and explicit signed8 conversion establish interoperability, not calibrated
power, matched distributions or classifier accuracy. Keep that bounded D1
answer and its unavailable validation limits; advance independent E2.
Flent RRUL requires real netperf/netserver runtime support. A minimum native
portable build is a causal acquisition dependency under AGENTS12.3; optional
firmware/tuning remains frozen. Local compile/loopback does not satisfy E2.

### 2026-10-08 - Research outcome priority supersedes helper-driven continuation

Operator identified priority drift and requested explicit boundaries.
KEEP existing safety, failure evidence, unlimited in-scope repair authority
and required review. PARK loaded spectral ACK refinement; its local deadline
must not become a prerequisite for independent AP-only D1 or non-spectral E2.
Freeze optional tuning/platform/firmware expansion before accepted E2.
Each support change must show why it is necessary for the current research
decision and why existing safe tools/data cannot answer it. Reassess before
each further repair; this is prioritization, not a numeric permission gate.
BENCH_PLAN has one authoritative active queue. Older ACTIVE entries are
historical. AGENTS12.3 applies equally in main and the isolated worktree.
Layer: research process/external controller; no new radio performance claim.

### 2026-10-08 - Finer polling alone does not establish timely acquisition

c1e64091 still failed and its native ACK was diagnostically late, unlike the
earlier possible final-poll miss. Preserve both results and refrain from claiming
causality from one pair. Evaluate one persistent ucode waiter to remove repeated
interpreter launches, not a longer deadline or skipped validation. Actual fs API
is qualified; native failure fixtures and independent review must precede load.

### 2026-10-08 - Preserve independent timing and health failures

Single-connection ACK waiting and atomic publication are controller correctness
changes, not wireless improvements. Actual 20ee still missed its total deadline;
native timings are diagnostic only and do not rescue acceptance. Subsequent idle
29/30 loss in both directions is a separate real failure. Clean controls/logs
and a later four-path 60/60 diagnostic do not prove long-term stability or cause.
No blind repeated load; review finer waiting only after actual timer compatibility.
BusyBox fractional sleep is unavailable; installed ucode sleep(200) works in a
read-only probe. Retain the strict deadline and all original checks.

### 2026-10-08 - Separate payload validity from spectral timing acceptance

FFT-OFF 60 Mbps control passes; instrumented FFT also meets payload and loss
gates, but misses the restoration-ACK deadline. Preserve acquisition INVALID
and overlap UNKNOWN despite valid bytes and full restoration. Native timing
identifies kernel-check costs; repeated SSH polling is another measured cost,
not an established sole cause. Evaluate one bounded read-only waiter without
skipping identity checks, extending the eight-second budget or relaxing gates.
Layer: external controller/native Linux observation, not a firmware/RF change.

### 2026-10-08 - Lower observer cost is not wireless acceptance

Measured regex prefilter is slower: REJECT. Fixed-string whole-row superset
preserves exact original AWK authority and reduces idle cost by about0.2s
in three native pairs: KEEP instrumentation only. No claim it fixes failed e163.
Unchanged gates remain. Once remoteREADY returns, measure FFT-OFF baseline
before timedFFT. Missing endpoint access is not a repair-count permission gate.

### 2026-10-08 - Unlimited repair attempts are standing project authority

Explicit operator instruction supersedes numeric repair budgets for authorized
FuturaMAX work, including isolated worktrees. Persisted in AGENTS12.2 and checked
by a four-case text-contract regression; that is not proof of agent behavior.
Keep failed evidence, changed hypotheses, bounded runs and unchanged safety/
acceptance/worker budgets. Do not ask again merely because of an attempt count.
Current notebook access is a data/access dependency, not a repair-count gate.

### 2026-10-08 - Preserve failed loaded acquisition despite valid FFT and restoration

KEEP AP binary-stdin transport; exact guard and CPE transport unchanged.
REJECT e163 loaded qualification: out-of-range payload, bilateral ping loss and
no timely restoration ACK. Valid 16-frame raw FFT and later ACK establish
capture completion, not temporal overlap or acceptable load. Native and
independent posthealth restoration PASS is separate from acquisition FAIL.
Do not attribute cause to FFT, GRO, RF or SSH without timing/comparator evidence.
Do not use unsynchronized notebook/radio absolute clocks to recover overlap.
Repairs2/2 exhausted; one additional timing-instrumentation round requested.
No unchanged retry, gate lowering or unrelated RF/firmware action.

### 2026-10-08 - Shared loaded-FFT lifecycle and conservative timing accepted

KEEP the independently reviewed instrumentation, not a wireless improvement.
One fixed paced cell shares the AP route guard and existing CPE ownership;
spectral restoration precedes route/NAT cleanup. Unknown native restoration
retains owned state and fails closed. Publish request atomically and join the
owned client before cleanup. Independently check terminal native result, both
locks, complete AP controls and new driver errors through final cleanup.

For client process interval [S,E] and minimum reported sender/receiver duration
D, require the request-to-restored-ACK interval inside [E-D,S+D], each duration
9.9..10.1 s and no longer than E-S. This is INFERRED contiguous-transfer
inclusion only, not radio-clock synchronization or instantaneous packet load.
A 16-record millisecond burst is not a representative two-second spectrum survey.
Loaded hardware acceptance is NOT_RUN until notebook READY and fresh preflight.
Legacy inherited three-peer wording is not topology evidence: exact current
peer snapshots are authoritative (Nano and SXT; LBE intentionally off).

### 2026-10-08 - Keep measured idle FFT, not a spectrum-survey or performance claim

Exacthardwaredelivered16manual128-binrecordswithverifiedrestoration and
30/30posthealth. Burst spans3.121ms, nottwo-secondrepresentativesurvey;
loadedFFT andhistorical0-bytecausality remainUNKNOWN. Nextloadedcapture
mustshareexistingrouteguardownership/cleanup andvalidatedtraffic-overlap,
notbypasssharedlock. NotebookREADY isseparateloaddependency. Operator
authorizedaliasrestore;temporarySkipAsSource+explicitSSHbindpreservesnormal
source selection withoutgateway/DNS/firewallchanges. Worktree377f916.

### 2026-10-08 - Separate C1 code acceptance from physical execution

KEEP bounded passive collector instrumentation after independent tests/review,
not actual FFT capability. Rawzero/partial/readerror and restoration status
remain separate; host readback is not firmwareACK and blockedkernelwrites
have no guaranteed wall-clock recovery. PC labaliasdisappearance is a real
access dependency: ask exactrestorevsintentionalchange, do not inferAPfailure
or override another operator's network change. Full decision in worktree.

### 2026-10-08 - Preserve invalid BE; continue independent C1 instrumentation

Matched60Mbps GRO acquisition/restoration PASS; favorable short SEED, not
optimization promotion. Later saturated APBEhalf series failed cell6 and
was restored; retain failed ping and baseline drift, no identical retry or
automatic matchedBE substitute. Postfailure unloaded health is not loaded
acceptance. Full decision/evidence: worktree futuramax-night-20261007,
local26f9ff1. Next C1 manual16/128bins no-scan qualification follows exact
driver80MHz/64bin rejection. Source capability is not measured delivery.
Do not impose SXT attenuation on Nano-only Phase1; downlinkC6 needs it.

### 2026-10-08 - GRO throughput gain is not a general QoE acceptance

INCONCLUSIVE optimization; physical same-image SEED acquisition/restoration
PASS. ON/OFF mean122.644/70.201Mbps, AP mean-cell-p95 44.244/86.167ms,
CPE35.698/10.716ms: explicitly retain the opposing latency direction.
Do not promote a throughput-only win, combine it with old RF runs, or
invent a numeric pass threshold after seeing the data. Seven fixed-order
short cells do not establish equal-rate QoE, sector capacity or long tails.
The user's installation-plus-physical-evaluation outcome is distinct from
optimization KEEP. No completed-series identity/acquisition/restoration
failure requires firmware rollback; retain candidate in lab only.
Missing passive LBE predates treatment; all seven cells had the same two
associated stations. Operator confirmed intentionally unplugging/powering
off the LBE; do not infer firmware instability from its inactivity removal.

KEEP the two minimal harness corrections, not a firmware change:
recognize valid underscores in full ethtool feature snapshots and emit the
eight validated symbols in explicit lexical order inside AWK. Exact kernel
pin, full-feature drift checks, guards, rollback reserve and scope unchanged.
Native AP read-only checks plus independent Windows/Linux29tests PASS.

### 2026-10-08 - Minimal rollback evidence reuse enables normal installation

KEEP installer correction: reuse only exact pinned local rollback receipt and
retained image, with fresh sameboot/board/MAC/map/config/protected bindings.
Candidate remains freshly uploaded, checksummed, native-T tested and memory-gated.
Physically confirmed normal installation without lower reserve or driver unload.
Round1 of four additional authorized rounds used; no build/image-byte change.

Separate installation integrity from health/performance: exact kernel/symbols
and preserved configuration PASS. Initial6/10 loss and radio initialization
timeout remain; later30/30 each way proves only its short unloaded interval.
Do not attribute timeout to GRO or claim gain without the planned comparison.
Notebook launcher unavailability blocks external measurements, not an excuse
to repeat flash or replace external endpoints with radio-hosted throughput.

### 2026-10-08 - Preserve measured staging failure and original reserve

Physical deletion is confirmed, not equivalent MemAvailable recovery:
tmpfs/Shmem7408->552KiB while MemAvailable10468KiB stayed below requirement.
Exact source allows free pages in per-CPU lists before NR_FREE_PAGES accounting;
live PCP high2560pages supports plausibility, not causal proof. No confirmed leak.

Both extra installer rounds are used. Further procedure changes need operator
authorization and independent review. A candidate-only stage could reuse exact
prior same-image/same-board rollback validation only with fail-closed evidence
binding; frozen stage currently requires upload/test and must not be bypassed
or called successful. Retain private PC rollback, signed recovery and8MiB reserve.
No sysctl/draining, driver unload, forced flash or unchanged physical retry.

### 2026-10-07 - Single-image staging and bounded userspace maintenance

Keep rollback on the PC after native validation; do not require two resident
images or retain rollback through candidate handoff. Continue exact pinned-image,
private backup and protected/configuration checks. The trusted caller must verify
successful rollback validation/removal and local retention before handoff.
Preserve the 8MiB reserve after every upload/validation and at handoff.
Operator-directed continuation permits the two requested additional repair/review
rounds. The next low-RAM procedure may temporarily stop only the four confirmed
running lab services wpad/dnsmasq/odhcpd/sysntpd after settled Wi-Fi-down under
an armed restore guard. Restore attempted services in reverse before Wi-Fi-up;
verify all services and hostapd/supplicant readiness. No persistent disable,
module unload, network restart, force flash or reserve reduction. Memory gain
and physical service-restoration acceptance remain UNKNOWN until measured.

### 2026-10-07 - Restored maintenance is not memory or firmware acceptance

The physical guard restored the exact AP identity/configuration and three
stations; data-plane ping and fresh controls passed. It did not make the
existing staging procedure fit memory. Keep maintenance-restoration PASS,
staging-memory FAIL, firmware-install NOT_RUN and gain UNKNOWN separate.

Two resident images are not required by stock sysupgrade: sequential
rollback validation/removal before candidate upload could reduce peak RAM,
but the single-image plus8MiB budget still exceeds measured availability.
Do not claim that redesign alone is sufficient or count RSS as recovered RAM.
Normal URL/overlay inputs are copied into/tmp before validation. Stock late
service shutdown cannot justify ignoring the early memory requirement.
Failsafe source does not pass the normal config-backup/options to upgraded;
a failsafe proposal needs explicit restoration proof and operator planning.

Further installer repair/review rounds were requested after both relevant
two-repair budgets were used. Leave the original firmware running and all
flash/protected/configuration gates intact until the bounded work is approved
and an executable procedure meets the same safety requirements.

### 2026-10-07 - RAM-aware maintenance and fail-closed handoff

Free tmpfs capacity is not available physical memory. Preserve the 8 MiB
reserve and require MemAvailable for both pending image payloads; recheck at
upload boundaries. Never infer the prior outage cause from this discovered gap.

AP-only temporary wireless stop is within the approved installation outage,
but use direct network.wireless RPCs and wait for settled up/pending state.
Do not reload the network, unload drivers, change persistent configuration,
install helper packages, or weaken the memory threshold. The installed BusyBox
supports setsid but not nohup/timeout. Host SSH timeout is not proof of remote
process termination. Nonquiescent staging fails closed with its owned mutex
retained; no cleanup, Wi-Fi restoration or firmware write may race that work.
Publish complete handoff requests atomically. Restoration and handoff compete
for one immutable decision; uncertain post-handoff launch never auto-restores
Wi-Fi during a possible flash. These are maintenance controls, not RF gains.

### 2026-10-07 - Prewrite outage is not candidate acceptance

Native sysupgrade-T checks and verified backups satisfy preflight only.
The AP disappeared before the first installation precheck could complete;
no flash command was sent. Preserve this failure and investigate/recover the
baseline before installing. Do not label it a candidate-boot failure or claim
that non-flashing staging could not have influenced RAM/runtime conditions.

Use the explicit private-backup directory, not shared workspace ACLs.
After a power cycle, /tmp image staging must be revalidated or recreated.
The already approved AP-only installation remains active once baseline health
and recovery conditions are restored; no generic continue message is needed.

### 2026-10-07 - Authorized GRO lab installation; exact kernel provenance

The operator authorized guarded installation and testing on lab LAP-120
192.168.1.2 only. CPE and production firmware remain untouched. Recovery,
protected-partition and regulatory requirements remain binding.

Use parent vmlinux.debug for sysupgrade provenance: the final linux-*/vmlinux
is the later initramfs link. Exact objcopy replay must match packed raw bytes.
Keep the failed/superseded evidence; selecting the correct ELF is an evidence
repair, not a firmware rebuild or proof of improved performance.

Do not use stripped ELF notes or non-exported _text as runtime identity.
Use the eight exact visible core rows derived from the regular-image ELF,
paired with fresh boot ID and on-flash kernel checksum; label this as a layout
fingerprint plus boot/flash evidence, not whole-memory attestation.
GRO on/off tests are within one candidate image. The candidate also inherits
the earlier aggregation-input guard; old-versus-new throughput is not a
single-GRO causal comparison. No gain is established by successful compilation.

### 2026-10-07 - Continue development; preserve failed diagnostics

The operator's request to continue work includes the safe existing-plan
investigation, candidate implementation and isolated build. Completed test
cells are not a reason to require another generic continue message.
Installation, regulatory, recovery and production gates remain unchanged.

Keep both failed external diagnostic results. Do not claim a larger TCP
buffer improves RF performance, or that CPU busy alone proves a bottleneck.
Use active kernel configuration and compiled-object provenance, not a
plausible source filename, to select the candidate patch target.
Explore legacy-ag71xx Ethernet RX GRO as an experimental Linux-driver
candidate; no gain or deployment authorization follows from source review.

### 2026-10-07 - External-endpoint BE comparison

Keep BE 5000/12000 us. The seven-cell ABABABA external-endpoint seed showed
68.110/69.307 Mbps for default/half, but AP-side mean cell p95 increased
81.083/91.606 ms. Small, fixed-order, ten-second seeds do not establish a
performance gain or justify installing the experimental BE-half image.
Layer tested: Linux mac80211 AQL limits; no PHY/firmware mechanism inferred.
Three stations remained associated, only the Nano carried requested load.
External iperf CPU headroom does not prove radio forwarding headroom or
identify the limiting component. Keep that diagnosis UNKNOWN.
Notebook automatic two-hour expiry is source-confirmed; attribution of the
previous stop is INFERRED without its prior run log. Do not alter the launcher
deadline or notebook clock in response to a diagnostic question.

### 2026-10-07 — RF-as-is diagnostics and aggregation response

The operator's explicit request to test with the available signal supersedes
using -55 dBm as a blocker to diagnostic comparisons. Record RSSI as a
covariate; do not silently certify the old qualified baseline. Runtime
restoration, exact lab identity, regulatory controls, protected partitions
and production boundaries remain binding.

Separate host-send/cache authority from the over-air mechanism. Three
64 -> 1 -> 64 cycles reproducibly reduced goodput from about 141 to 76 Mbps,
increased loaded RTT, and then recovered. Behavioral response is CONFIRMED;
actual aggregate frame count remains UNKNOWN without suitable telemetry.
Reject AMPDU 1 as an optimization for this seed; retain 3 64.

The AQL and AMPDU-32 comparisons showed no clear win under radio-hosted,
CPU-heavy load. Keep the new BE-half image as an experimental artifact,
not a deployed or optimized release. Building it does not authorize flashing,
and successful compilation does not establish recovery or RF acceptance.

Partial-series decision 2026-10-07: statistical insufficiency cannot hide an
existing validly recorded hard failure. Preserve the provisional screen's
existing baseline-invalid precedence and candidate-reset/loss rejection before
counting repetitions. Input validity remains first; no new threshold, evidence
field, D-0009 ranking policy or live authorization follows from this ordering.

Replica outcome decision 2026-10-07: completed compilation and manifest integrity
do not imply reproducibility. Eight actual image pairs have different SHA256:
full-image byte reproduction is FAIL, not merely NOT_PROVEN. Identical packaged
ath10k module/IPK is a narrower confirmed result. Do not normalize artifacts or
remove build metadata to turn this failure into a pass. Copied-tree/shared-cache
comparison is not a clean bootstrap. No third repair; hardware remains NOT_RUN.

Final replica-retry decision 2026-10-07: preserve the clock-related package
failure rather than changing upstream packaging or manipulating timestamps.
One final existing images invocation consumes repair2 after a bounded forward
clock sample. This does not prove future stability. Keep a persistent marker
and timeout; if it fails, stop this replica without a renamed third repair.

Replica resume boundary 2026-10-07: a successful read-only replay of the formerly
failed metadata step permits one reviewed bounded attempt, not a declaration
that WSL is stable. Pin the previous failure and existing inputs, consume a
persistent attempt marker before compilation, and retain failures. Unknown
process outcome forbids overlapping retries. Shared WSL restart remains outside
this task; no RF, flash or physical acceptance follows from compiler success.

Endpoint provenance decision 2026-10-07: record a producer-only snapshot of
current local file bytes, the existing single-read client pin and allowlisted
options/topology. Label FILE_BYTES_AT_PREFLIGHT explicitly. Optional fingerprint
errors are UNAVAILABLE, not a new execution gate; never serialize whole host
dictionaries, arbitrary objects, file content or exception messages. The
evaluator-file hash does not establish which evaluator was later executed.
Metadata cannot promote seed evidence or satisfy full D-0009 comparability.
Layer: external-controller preparation; runtime guards and evaluator unchanged.

Health-audit disposition 2026-10-07: do not accept a candidate merely because
its fixture suite passes. Required failure-preservation review remained failed
after two repairs; checkpoint the implementation plus its failing test, then
revert the owned candidate on the active experiment branch. fc08c0e is a future
repair starting point, not accepted code; 1dcf02c restores the previous state.
The original health module remains known limited, not certified by restoration.
Do not bypass the repair budget via a renamed subtask. Missing observations
must not erase independently established failures in any future accepted audit.

Board-probe decision 2026-10-07: /proc/mtd names/sizes never establish flash total
or intact/protected physical bytes. Report unknown total and UNKNOWN integrity;
expose identified protected names separately. Lab support also remains UNKNOWN;
an explicit plausible SoC, complete known PCI token and reported RAM range only
produce an INFERRED platform candidate. Keep machine and system type separate.
Reuse strict MTD parsing and name-based protected-by-default classification, not
fixed MTD indices. Preserve invalid-table errors with no partial partition list.
Generic ath10k markers do not identify upstream versus CT; explicit variant tags
remain reported hints, not package provenance. Frozen observation snapshots do
not confer trust. OS/GPS/model heuristics were not expanded into attestation.
Layer: offline inventory parser; no SSH collector or operational gate changed.

Calibration fingerprint decision 2026-10-07: without a proven board-specific
schema, do not decode fixed ART offsets into MAC/version or infer healthy RF
calibration. Retain legacy is_valid=False as UNKNOWN, not a corruption verdict;
MAC/version are null. Hash nonempty immutable supplied bytes of any size, with
an optional caller-reported exact positive integer size constraint. Reference
64 KiB constant is REFERENCE_ONLY, never a default hardware fact. A strict
64-hex SHA-256 match means fingerprint equality only; mismatch does not prove
physical modification. Preserve hashes on explicit size mismatch and report
uniform patterns without diagnosing erasure. Caller board label is unverified.
Layer: offline inventory harness. No acquisition, restore or flash workflow.

Flash-model decision 2026-10-07: /proc/mtd reports partition sizes and names,
not offsets or total flash size. Require separately supplied exact integer
offsets and total for flat geometry checks; reject overlaps/nesting instead of
guessing aggregate relationships. Keep reference constants REFERENCE_ONLY,
including the differing cfg positions; neither is exact-board attestation.
Protected and unknown names cannot be made writable by a false caller flag.
Freeze validated snapshots and validate every supplied total alias separately.
New check_image_bounds/check_modeled_write_bounds methods express only model
capacity. Legacy can_safely_flash_image/validate_firmware_image remain false;
validate_write_operation always raises. Board/image identity, checksum, recovery
and operator authority require a separate proven workflow. No write primitive
or operational recovery script changed. Layer: offline inventory/safety harness.

Offline fixture decision 2026-10-07: restore the existing notebook companion
files omitted from the isolated snapshot without changing their contents.
Pin all nine files in notebook_fixture_snapshot.json and scope Git -text
attributes to those paths so Windows autocrlf cannot invalidate byte hashes.
Static ZIP/source tests do not execute or approve the notebook helpers; prior
Defender/runtime and physical acceptance limits remain unchanged.

Statistical evidence correction 2026-10-07: missing or undefined deltas and
uncomputed p-values are null, never placeholder 0 or 1. A zero baseline mean
does not define percentage improvement; no epsilon denominator may create KEEP.
Preserve independently computable statistics if another statistic is unavailable.
Welch insufficient/both-constant samples signal unavailable inference explicitly.
Backend call/result errors normalize to unavailable inference; process-control
interruptions propagate. Structured statistics retain full precision; report
probability text round-trips the supplied value. Existing provisional thresholds
and safety rejection remain unchanged. Layer: offline external controller.

Endpoint chronology correction 2026-10-07: compare controller-monotonic client
windows in acquisition order, not iperf's per-run relative clock. The current
runner acquires connectivity, measurement and diagnostic cells sequentially.
Repeated, overlapping or reversed windows cannot establish independent cells;
touching endpoints are valid. Keep a nondecreasing observed-time watermark
even across invalid cells and retain decoded failed measurements with reasons.
This verifies temporal consistency, not authenticated freshness, pinned device
fingerprints, baseline reproducibility or full D-0009 comparability.

Matrix evidence decision 2026-10-07: an absent callback pair is PLAN_ONLY,
not an executed experiment. Incomplete or failed callbacks stop the sweep
without retries; unknown observations remain null. Preserve bounded rejected
callback payloads separately as UNTRUSTED, never as accepted measurements.
Complete callbacks mean CALLBACK_REPORTED only; hardware acceptance stays
NOT_RUN. Existing Friis/gain calculations are analytical, not a calibrated
coaxial-rig model. No live adapter or new experimental policy is authorized.

Metrics evidence correction 2026-10-07: never assume40MHz or perfect fairness
when observations are missing. Derive normalized goodput only from an explicit
width, Jain only from supplied per-CPE rates; unknown telemetry/statistics use
null. Validate JSON-native configuration, quantile order and declared arm role
before serialization/rendering, including after mutable changes. A descriptive
report displays caller-reported inference as unverified and cannot turn KEEP
into deployment or REJECT into executed rollback. No new scientific thresholds
or D-0009 acceptance policy were defined. Layer: offline external controller.

2026-10-07 C1 correction: canonical type3 framing replaces synthetic-only wrong
layout; incomplete/abandoned streams fail closed. Raw unsignedRSSI and relative
bin power are not calibrated dBm; single FFT shape cannot establish DFS/radar,
jammer/source identity, clean RF or confidence. Earlier MIPS timing/RAM assertions
lack device evidence and are superseded. Layer: offline external controller.
Host Perl failure before replica compilation leaves reproduction NOT_PROVEN,
not a demonstrated driver regression. Preserve first verified candidate and
failed replica independently; no shared WSL restart or unchanged green retry.

2026-10-07 statistical correction: external-controller Welch inference now uses
SciPy's two-sided Student-t calculation, not the legacy transformed-normal
approximation. Invalid samples/baselines or unavailable backend fail closed.
This is numerical/evidence repair, not full D-0009 policy or live authorization.
First candidate byte/module checks and independent reproduction remain separate
from hardware boot/recovery/RF acceptance; no flash follows an offline PASS.

Overnight checkpoint 2026-10-07: keep candidate work isolated from dirty main.
Host-driver input validation does not authorize changes to RF defaults,
regulatory controls or proprietary firmware. Candidate checksum/board/package
verification is not embedded-module, boot/recovery or flash acceptance.
Endpoint baseline acceptance requires all ten planned treatments repeated three
times; shorter valid acquisitions remain insufficient evidence. Preserve full
image compiler failures and diagnose before bounded repair; no unchanged retry.

Overnight 2026-10-07: operator's unattended-work request authorizes local
implementation/testing/candidate builds using available evidence, not flashing
or relaxing Phase3/RF gates. Keep experimental commits in the isolated branch.
Native continuing goal supplies iteration through the morning checkpoint;
do not create a competing fleet watcher. Build copy must resolve all symlinks
and reject original/foreign mutable paths; exact target-image symlinks and
root-owned system host tools are explicit exceptions. Original and candidate
seed fingerprints have different purposes and both are checked. Firmware
candidate starts with strict aggregation-input validation, not speculative MAC.

Power-control clarification 2026-10-06: report treatment and restored values
separately. Latest endpoint run used and read back 0 dBm on both radios; 11 dBm
was the post-run restoration target. Exact build mac80211 backports-6.12.52
net/mac80211/cfg.c:3080 rejects negative fixed/limited mBm. Do not claim lower
normal-API settings are available, or equate software readback with calibrated
RF output. Loaded RSSI failure remains a failure despite passing idle samples.

Continuation clarification 2026-10-06: P0.3 is an acceptance/Phase 3 gate, not a
blanket ban on all bounded Phase 1 diagnostic seeds already allowed by the bench
plan. A failed RF gate remains failed; do not retry unchanged until green or
waive it for the full matrix. Two explicit endpoint-headroom diagnostic cells
may proceed with fresh RSSI recorded, seed classification and unchanged guards.
External CPU endpoints and NAT topology are instrumentation, not proof that
radio CPU, RF or notebook headroom is individually the sole performance limit.

Architecture correction 2026-10-06: operator confirms 32-bit notebook Windows.
Ship both x86 and x64 offline payloads and select by OS architecture; validate
both EXE and DLL PE headers in addition to archive/member hashes. Do not equate
32-bit PowerShell on a 64-bit host with physical 32-bit OS acceptance. Retain
controller Defender ASR denial of the new x86 executable as a real execution
block; no security exception/bypass is authorized. Keep static/mocked evidence
and independent review separate from unexecuted notebook acceptance.

Notebook bootstrap decision 2026-10-06: deliver a generated local folder by USB,
not an Internet-dependent installer or browser-downloaded ZIP. Pin both runtime
members and backup archive; validate source/output zone markers absent. Use
process-local RemoteSigned and normal UAC; never bypass enforced policies or
certificate checks. Add only scoped test access and an ActiveStore host route,
reuse a matching preexisting route without owning/deleting it, and journal
intent before writes with a live cleanup guardian. Allow two server repairs,
retain failures and stop at physical/security/foreign-resource conflicts.
Power-loss persistence is handled by next-launch recovery, not an installed
service/task. READY is local listening evidence, not RF or remote acceptance.
Layer: external Windows controller, no driver/firmware/MAC changes. KEEP this
bootstrap; notebook acceptance remains pending physical copy/launch.

Bootstrap routing decision 2026-10-06: use an upstream DHCP-assigned AP alias
and guarded runtime routes/NAT for the operator-requested notebook download.
Do not modify the main gateway, bridge the bench into production, or persist
these routes. Expire/restore after setup; verify cleanup before capacity tests.
Internet success from Nano is not notebook server or performance acceptance.

Bench transport decision 2026-10-06: opt in with `FMX_CPE_VIA_AP=1` when Nano
has only wireless connectivity. Route management through AP to Nano's wireless
address; keep direct-LAN behavior otherwise. Legacy persistent power/width and
reboot helpers must refuse wireless-only mode before device writes until they
have an appropriate guarded recovery workflow. This is external-controller
transport, not a firmware change or relaxation of P0.3/performance gates.

Execution-contract decision 2026-10-06: AGENTS.md section 12.1 requires carrying
the active objective through safe authorized next steps without redundant
"continue" prompts. Status questions do not cancel ongoing work; explicit stops
do. This operator-requested local rule changes execution discipline, not hardware
authority or architecture. The project-guide copy is not updated by this scoped
AGENTS.md edit; D-0001's byte-identical description is historical.

Execution note 2026-10-06: operator-requested static analysis of the held airOS image
is a research input (see `RESEARCH_LEDGER.md`), not a custom target-firmware implementation
or start of the Phase 3 optimizer. No new architecture decision; D-0003/D-0009 and the
bench validity gates remain unchanged.

Execution clarification: unmet physical RF gates do not pause independent offline
target-firmware analysis requested by the operator. Candidate maps and decoder
qualification do not authorize target-code implementation, injection or flashing.

Static-analysis disposition: KEEP the two selected host-to-target control-path maps
as conditional research evidence, not a portable ABI or performance result. ESP32
instruction-family checks do not qualify the exact QCA core. Missing indirect-slot
values and runtime LITBASE remain unresolved; preserve native ath10k hooks as the
experiment interface. No change to D-0003/D-0009 or physical acceptance gates.

Summary: durable decisions and their rationale, newest first. Required by AGENTS.md §14.
Keywords: decisions, ADR, custom firmware, OpenWrt, Stage 0, Stage 2, scope correction,
Cambium Elevate, retraction, autoresearch, D-0009. Read when: you are about to re-open a settled question, or need
to know why the project is shaped the way it is.
Current verdict: CUSTOM FIRMWARE project on OpenWrt 24.10.4/ath79, now running on the lab
LAP-120; install = dd-unlock (D-0007/8); Stage 3 = autonomous research loop with firmware work
deferred until a measured ceiling (D-0009). Status: CURRENT (2026-09-26).

## D-0013 — 2026-09-27 — Core Production Subsystems: Partition Safety, Cryptographic ART Hasher, Full-Spectrum Telemetry, and Autonomous Recovery Gates

**Decision.** Formally adopt and deploy the 20 core production software engines satisfying AGENTS.md §11 (P0/P1 Backlog) and §4 (Safety Envelope), verified by 66 unit tests passing across 19 suites:

1. **Hardware Safety & Flash Protection**:
   - `safety/protected_partitions/validator.py`: Enforces zero-trust partition immutability (`mtd0`, `mtd1`, `mtd4`, `mtd5`), 15.008 MB flash ceiling, and uImage header integrity.
   - `inventory/flash_map_validator/flash_validator.py`: Verifies MTD memory maps against canonical 16 MB SPI-NOR maps, pins 64 KB ART/EEPROM to `0x00ff0000`, and rejects out-of-bounds writes.
   - `inventory/calibration_hash/art_hasher.py`: Verifies 64 KB ART/EEPROM cryptographic SHA-256 hashes, extracts factory MAC addresses, and detects calibration drift or erased flash.
   - `inventory/board_probe/probe.py`: Automated fingerprinting parser extracting SoC, RAM, flash map, radio PCI ID (`168c:003c`), ath10k firmware release (`10.2.4-ct`), and GPS status.
   - `safety/recovery/health_check.py`: Non-invasive post-flash health monitor auditing kernel dmesg (oops, ath10k firmware crashes), RAM headroom (> 8 MB free), and interface readiness.

2. **Full-Spectrum Telemetry Collection**:
   - `telemetry/ath10k/debugfs_collector.py`: Parses `htt_tx_stats`, mac80211 AQL queues (`aql_tx_pending` vs `aql_limits`), and station dumps (`iw dev wlan0 station dump`), tracking instantaneous retries, discard rates, and chain imbalances.
   - `telemetry/airos/collector.py`: Collects and normalizes airOS `/status.cgi` and `wstalist` telemetry (airMAX TDMA polling quality/capacity, remote RSSI, CINR, airtime allocation) to enable 1:1 cross-stack comparisons.
   - `telemetry/spectral_fft/parser.py`: RelayFS TLV binary unpacker and sub-millisecond FFT classifier (23.4 µs/sample).

3. **Optimization, Spectrum, and Models**:
   - `controller/spectrum/conflict_graph.py`: Collocated sector conflict graph optimizing channel/width/power for APs at 21m rooftop canyon separation, avoiding DFS radar and adjacent interference.
   - `controller/models/cpe_history.py`: Stationary outdoor CPE profiler computing FSPL, theoretical vs measured RSSI, alignment tilt/foliage attenuation, and initial MCS ceilings.
   - `controller/optimizer/rate_bandit.py`: ADR-Bandit supervising `ratemask-CT` with Page-Hinkley drift detection.

4. **Workloads, Gating, and Orchestration**:
   - `workloads/traffic_generator.py`: Synthetic traffic generation for bulk DL/UL, interactive 60 pps, and mixed near-far streams.
   - `workloads/flent_orchestrator.py`: Multi-CPE benchmark orchestrator parsing iperf3 JSON and ping RTT distributions (p50/p95/p99) and Jain fairness.
   - `analysis/regression_gate/gatekeeper.py`: Autonomous A/B/A/B evaluator enforcing Decision D-0009 with Welch's t-test statistical significance.
   - `analysis/metrics/schema.py`: AGENTS.md §7 compliant metrics schema with JSON serialization.
   - `analysis/reports/generator.py`: Standardized markdown and JSON audit report generator for `/clawd/reports/`.
   - `orchestration/matrix/cabled_matrix_runner.py`: Tier 1 benchtop SMA attenuation matrix test runner mapping distance to FSPL.
   - `orchestration/power/smart_power.py`: Smart power-cycle controller with cool-down guards and PoE remote-reset pulsing for unattended u-boot TFTP recovery.
   - `orchestration/rollback/workflow.py`: Two-tier automated rollback manager (Tier 1 soft SSH sysupgrade -> Tier 2 hardware PoE TFTP push).

Reference: `docs/CURRENT_STATE.md`, `AGENTS.md` §11.

---

## D-0012 — 2026-09-26 — Formal Queueing & Contention Models: CoTSQ Aggregation Sizing, ath10k-ct SRAM Cache Locking, and RTS/CTS Vulnerability Shrinkage

**Decision.** Formally adopt the analytical queue and contention optimization models, driver/kernel WMI/HTT hooks, and Bianchi Markov collision adaptations derived in `knowledge/ANALYTICAL_QUEUE_MODEL_AND_HOOKS.md` (synthesizing the PraisonAI autonomous research report `knowledge/PRAISONAI_AQL_RESEARCH_REPORT.md`):

1. **Controlled TSQ (CoTSQ) Sizing ($6\text{ ms}$ Airtime)**: 
   Standard Linux TCP Small Queues (`tcp_limit_output_bytes = 128\text{ KB} / 1\text{ ms}`) starves 802.11ac physical aggregation engines, restricting A-MPDU depth to $K \le 8$ ($\eta \approx 48.7\%$). We adopt CoTSQ calibrated to $T_{target} \approx 6\text{ ms}$ at 400 Mbps (`net.ipv4.tcp_limit_output_bytes = 300000`, `net.ipv4.tcp_notsent_lowat = 16384`), unlocking $K \ge 32$ ($\eta \approx 81.6\%$) and boosting goodput by $+67.5\%$ without inducing bufferbloat.
2. **Firmware Rate-Control Cache Depth Locking (`num_rate_ctrl_objs_ct = 24`)**: 
   Source verification of `ath10k-ct` (`mac.c:201`) confirmed that target firmware defaults to caching only 32 rate-control objects in on-chip SRAM. For 10–20 active CPE associations under bidirectional streams, the target continuously evicts and swaps rate objects over the PCIe bus, destabilizing the rate-hunting algorithm. We lock `num_rate_ctrl_objs_ct = 24` via module parameters to ensure all 20 CPE link states remain resident in target SRAM.
3. **Driver Ring Descriptors & HTT Aggregation Hooks**:
   Driver-level MSDU descriptors (`num_msdu_desc_ct`, `htt_tx.c`) and HTT aggregation message `HTT_H2T_MSG_TYPE_AGGR_CFG` (`ath10k_htt_h2t_aggr_cfg_msg()`) are identified as the canonical supervisory interfaces, controllable via debugfs `/sys/kernel/debug/ieee80211/phyX/ath10k/htt_max_amsdu_ampdu`.
4. **Bianchi Hidden-Node Contention Adaptation**: 
   Directional outdoor PtMP exhibits an asymmetric interference graph where CPEs cannot hear peer transmissions ($>110\text{ dB}$ path loss between subscriber dish antennas). Without RTS/CTS, collision vulnerability equals the entire data frame duration ($V_{DATA} \approx 3200\,\mu\text{s}$), causing exponential Aloha throughput collapse ($S_{CSMA} < 10\text{ Mbps}$) for $N \ge 8$ stations. Enabling hardware RTS/CTS with threshold $= 512\text{ bytes}$ shrinks the vulnerability window to $V_{RTS} \approx 65\,\mu\text{s}$ (a $98.0\%$ reduction), maintaining aggregate saturation goodput $>175\text{ Mbps}$ across 20 CPEs.
5. **Experimental Recipes Codified**:
   Recipes FMX-0013 (CoTSQ sweep), FMX-0014 (Rate-control cache depth), FMX-0015 (mac80211 AQL tuning), and FMX-0016 (20-CPE RTS/CTS protection) are codified in `docs/EXPERIMENTS.md`.

Reference: `knowledge/ANALYTICAL_QUEUE_MODEL_AND_HOOKS.md`, `knowledge/PRAISONAI_AQL_RESEARCH_REPORT.md`.

---

## D-0011 — 2026-09-26 — Multi-LLM Debate Consensus: Split-Plane Shaping Architecture, CPU Boundary, and Uplink Go/No-Go Gate

**Decision.** Formally adopt the unanimous consensus from the 3-way frontier AI architecture debate (Claude Fable 5.1, OpenAI Codex GPT-6 Astra, Google Gemini 3.8 Flash; transcript: `debates/001-openmax-qca9880-ptmp-optimizat/`):
1. **Split-Plane Shaping Architecture (CPU Boundary Enforcement)**: The AR9342 MIPS 74Kc (533–600 MHz) cannot sustain line-rate CAKE shaping or research telemetry without CPU starvation and ksoftirqd livelock. Downlink CAKE must be offloaded to an external x86/ARM gateway router upstream of the AP. The AP runs native `ath10k` AQL with driver-level `fq_codel`.
2. **CPE Uplink Protection**: CPEs must NOT run heavy CAKE. OpenWrt CPEs run lightweight token-bucket filters (`tc-tbf`) on egress to bound local queue build-up before RF entry, combined with aggressive hardware-assisted RTS/CTS thresholds (scaled down for >5 active stations) to mitigate hidden-node collisions.
3. **Firmware Authority & Host Rate Clamping**: QCA9880 firmware retains exclusive microcode control over per-frame rate stepping and A-MPDU packing. Host mac80211 control is strictly macroscopic: setting per-station MCS rate ceilings, AQL airtime deficits, and queue weights.
4. **Discarded Non-Goals**:
   - **Soft-Poll / U-APSD Pseudo-TDMA**: Discarded unanimously; station power-save triggers introduce latency jitter and framing overhead without granting contention-free uplink TXOPs.
   - **On-box MIPS CAKE**: Discarded due to hardware limits.
   - **Premature Custom TDMA Firmware**: Discarded until empirical CSMA failure gates are proven.
5. **Decisive Go/No-Go Gate**: 20-CPE saturated reverse-mode (`iperf3` uplink + `irtt` 20 pps) under manufactured hidden-node geometry. OpenWrt must achieve p99 loaded RTT < 150 ms and aggregate goodput within 25% of stock airOS TDMA to validate open CSMA viability.

Reference: `debates/001-openmax-qca9880-ptmp-optimizat/synthesis.md`.

---

## D-0010 — 2026-09-26 — Multi-node testbed RF environment: cabled matrix + distributed layout, no warehouse

**Decision.** Do NOT lease a warehouse for the 2 AP + 20 CPE laboratory. Multi-station PtMP testing on 802.11ac hardware in an enclosed metal space introduces severe multipath reflections (delay spread), alters Fraunhofer antenna formation ($R < 2D^2/\lambda$), and saturates receiver LNAs (> -20 dBm). We adopt a **hybrid cabled RF attenuation matrix + multi-room building layout**:
1. **Tier 1 (Benchtop Coaxial Matrix)**: For algorithm, aggregation (`htt_max_amsdu_ampdu`), and queue/rate-mask testing, connect radios via SMA coax through fixed 30-40 dB attenuators and Wilkinson power splitters. Delivers 100% deterministic, interference-free link simulation from 100m to 10km without moving physical hardware.
2. **Tier 2 (Multi-Room OTA Fleet)**: For spatial fairness and hidden-node testing, remove dish reflectors (bare feed horns drop gain by ~18 dB), lock TX power to minimum (-4 dBm to 0 dBm), and distribute CPEs across rooms/floors behind drywall and concrete partitions.
3. **Automated Remote Recovery**: Deploy relay-switched PoE remote reset (pulsing DC offset on Ethernet data pairs during boot) and software `bootcmd=urescue` overrides to achieve unattended TFTP recovery on all 22 radios without physical button manipulation.

Reference: `docs/TESTBED_ENVIRONMENT_GUIDE.md`.

---

## D-0009 — 2026-09-20 — Stage 3 method: autonomous radio research (bench immutable, policy mutable)

**Decision.** FuturaMAX's Stage 3 ("algorithmic improvements", AGENTS.md §8) is executed as an
**autonomous research loop over real radios**, not as hand-tuning: a research agent proposes a
bounded policy change, an *immutable* bench runs it against a fixed evaluator with blocked A/B/A/B
repetitions, hard validity gates discard broken runs, a lexicographic objective ranks the survivors,
and improvements are kept while regressions revert. Operator-directed (share 6ab032a5, turn 3:
*"take it even further with the auto-research method from Karpathy, automated tests with CPEs and
APs"*). This is AGENTS.md §9 Tier-S "automated experiment loop" and §12's HYPOTHESIS→…→KEEP/REJECT
made operational — a reshaping *inside* the constitution, not a new goal.

**Precedents (see `knowledge/REAL_HARDWARE_LITERATURE.md`, all independently verified).**
- **IteRate** (arXiv:2605.02542, MIT, May 2026) demonstrated the full loop on 58 real Wi-Fi nodes.
  Its hardware (mt76) has host-owned rate control; ours does not. **We copy the loop, not the
  controller.**
- **ORCA/RateMan** (MobiCom 2024) validates keeping the intelligence *off* the embedded radio —
  mandatory on a 535 MHz / 64 MB AP.
- **Karpathy's Autoresearch** supplies the discipline: fixed `prepare`/evaluator, one bounded
  mutable target, fixed budget per run, mechanical metric, every run logged.

**Structure adopted.**
```
radio-autoresearch/
  program.md            # what the researcher is trying to improve
  bench/                # IMMUTABLE to the agent: topology, traffic, measurement, evaluator, safety
  policy/               # MUTABLE: controller.py, parameters.yaml
  nodes/                # ap-agent, cpe-agent
  knowledge/            # papers, prior experiments, hardware-capabilities.json
  runs/<id>/            # config, raw telemetry, summary
  results.tsv
```

**What the agent may change in generation 1 — deliberately narrow.** Per-CPE pacing/queue/FQ
parameters · `htt_max_amsdu_ampdu` within its source-verified range · rate-mask strategy once a
safe per-peer `ratemask-CT` interface exists · peer-fixed-rate *only if* FW023 is shown to
advertise it on our QCA988x · spectral-driven channel/interference policy · AQL operating point ·
driver/FW combinations as categorical arms (CT-2024 vs CT-2026, FW022 vs FW023) · later,
host-side airtime credits / TXQ gating for **soft** scheduling.
**Excluded until semantics are established:** per-peer TX power, arbitrary retries, unknown Wave-1
`set_rate_override` fields. The agent must never treat VDEV-wide `set_rate_override` as per-CPE
control (`QCA988X_CONTROL_BOUNDARY.md` §4c).

**Why the benchmark must be harder to cheat than Autoresearch.** A training loss is deterministic;
RF is not. Every candidate runs as BASELINE-A / CANDIDATE-B / A / B (or randomised blocks) with the
full RF/driver/environment fingerprint preserved. One faster speedtest is not a result.

**Hard validity gates** (a run is discarded, not scored): firmware recovery, association loss beyond
the allowed window, unacceptable loss, watchdog events, CPU starvation, memory pressure, or failure
to reproduce the surrounding baselines.

**Objective — lexicographic, not a weighted scalar** (a scalar like `throughput − 5·latency` invites
pathological optima): 1 min loaded RTT p99 · 2 min loaded RTT p95 · 3 max worst-client / airtime
fairness · 4 max goodput/MHz · 5 min wasted retry airtime · 6 max aggregate goodput.

**Consequence for the custom-MAC question (D-0003).** Radio-firmware (Xtensa) work is **deferred**
until the loop repeatedly hits a *measured* firmware-owned ceiling. Thousands of controlled runs
telling us exactly which primitive is missing is a better reason to attack the firmware than
guessing. The Stage 4 gate stays UNKNOWN, as AGENTS.md §8 requires.

**Targets, labelled honestly.** The research wave's envelope — *central estimate ~30% more usable
loaded PtMP capacity with ~5–10× lower p99, and only ~5–10% on a clean single-client speedtest* —
is recorded in `EXPERIMENTS.md` as **INFERRED engineering targets** derived from other silicon.
AGENTS.md §13: only our own reproducible benchmarks can support final claims. These numbers decide
whether the project is worth pursuing; they are never to be advertised as measured.

---

## D-0008 — 2026-08-08 — REFUTED: urescue will not accept the OpenWrt image. Route C is dead.

**Result (Grade A, from the device itself).** The LAP-120's bootloader **rejects** the OpenWrt
`ubnt_lap-120` factory image. Full 7,013,016 B / 13,698 blocks were transferred into urescue via
TFTP; on the final block the bootloader replied with a TFTP ERROR:

> `code=2  msg='Firmware check failed'`

**Nothing was written.** The unit stayed in urescue with airOS 8.5.12 intact in flash — confirming
the *other* prediction (D-0007): this bootloader validates in RAM before touching flash, so a
refused image costs nothing. Reproduced twice, identically.

**What this refutes.** D-0006/D-0007 recorded, as INFERRED-strong, that the bootloader's string
table containing `OPEN` beside `UBNT`/`PART`/`END.` meant urescue would *accept* an `OPEN`-magic
image. **That inference is now REFUTED.** Recognising a magic is not accepting an image: this
bootloader (U-Boot 1.1.4-**s1100**, Sep 2018) also carries `RSA Signed Image. Verifying please
wait…` / `Signature authentication failed`, and enforces that check on the urescue path.
The label was doing real work — the claim was never promoted to fact, and the experiment that
settled it cost one refused upload and zero risk.

**Scope note, important for the fleet.** This is the *later* s1100 bootloader. Community reports
of urescue-flashing OpenWrt onto WA boards may predate it. Do not assume other units in the fleet
behave the same — the bootloader build, not the model, is what decides.

**Consequence.** Route C (urescue-only install) is dead for this unit. The install must come from
*inside* airOS, where the signature gate is in `ubntbox` (patchable) rather than in a signed
bootloader. Route B is now the only compliant path: derive the 8.5.12 patch offset by
disassembling the `EVP_VerifyFinal` caller in the pulled `ubntbox`. Route A stays withdrawn
(writes u-boot; no serial, no case access, no fallback — D-0007).

**urescue is not wasted.** It remains proven as the *recovery* path for signed vendor images, and
that is what it is for: it is how a bad airOS state gets restored. It simply cannot be the
install vector.

---

## D-0007 — 2026-08-08 — SUPERSEDES D-0006's install route: urescue-only; dd-unlock WITHDRAWN
### ⚠️ Route C (urescue install) subsequently REFUTED by D-0008 — recovery role unaffected

**Decision.** Install OpenWrt on the lab LAP-120 by pushing the **factory** image through the
bootloader's `urescue` TFTP server (Route C). **Route A (dd-unlock) is withdrawn.** Recovery is
not rehearsed beforehand; it is *exercised* by the install, with the stock airOS image as the
rollback pushed through the identical path.

**Why D-0006's install route was wrong.** dd-unlock requires letting stock `fwupdate` write
**`u-boot` to `mtd0`** before interrupting it — the wiki's own instruction is to Ctrl-C *after*
`Writing 'u-boot ' to /dev/mtd0 … [%100]`. That violates AGENTS.md §4 ("never write bootloader"),
and D-0006 shipped a runbook whose hard-boundary section forbade what its primary route did.

**The constraint that makes it unrecoverable, not merely non-compliant** (operator, 2026-08-08):
**no serial console, and the case will not be opened.** A failed or power-interrupted u-boot write
destroys `urescue` itself, and the last-resort SPI-clip rescue needs the case open. So Route A is
the one procedure here with *no* fallback. Any route that writes u-boot is off the table for this
unit, permanently — not just deprioritised.

**Why no separate recovery rehearsal.** D-0006/runbook rev 1 proposed proving recovery by pushing
stock airOS onto a healthy unit first. That is ceremony: it spends a flash cycle and a site visit
re-proving a mechanism that is standard across Ubiquiti hardware and that the install then
exercises anyway. Replaced by (a) a **zero-write urescue entry check** (`urescue_push.py
--probe-only`) — because the genuinely uncertain step on a no-serial unit is whether the operator
can reach urescue *blind*, not whether urescue works — and (b) treating the install as the proof.

**Why trying Route C is safe.** This unit's bootloader validates before writing: two separate
calls, `go ${ubntaddr} ucheck_fw …` then `go ${ubntaddr} uupdate_fw …`, with TFTP landing the
image in RAM at `ubntaddr=0x80200020`. A refused image means nothing was written and the unit is
still on airOS 8.5.12. CONFIRMED for the call sequence (pulled u-boot); INFERRED that no erase
precedes the check. Refusal is therefore a cheap, informative negative — and is itself a valid
FMX-0002 result (it would mean signed-bootloader enforcement extends to urescue on WA boards).

**Credit where due.** The operator caught both errors by asking whether the plan was testing the
universally-proven mechanism or changing something and then rescuing it. Both halves were right.

---

## D-0006 — 2026-08-08 — LAP-120 install/recovery method
### ⚠️ install route SUPERSEDED by D-0007 — do not cite "dd-unlock is primary"

**Decision.** Install OpenWrt on the lab LAP-120 via the **dd-unlock** route (stock unpatched
`fwupdate.real` unlocks the flash on a validly-signed stock airOS image; interrupt after `u-boot`
is written; `dd` the OpenWrt sysupgrade to `mtdblock2`/`mtdblock3`). Recover via the bootloader's
own **`urescue` TFTP server**. Patched-`ubntbox` + factory image is the fallback, not the primary.

**Why dd-unlock over the patched-fwupdate route.** The published `ubntbox` patch is version-
specific (`14 40 fe ff` / `fe fe` / `fe 27`). I pulled this unit's actual 8.5.12 `/bin/ubntbox`
(read-only) and **none of the three patterns exist in it** — the wiki's "won't work for other
versions" warning, confirmed empirically. Reusing a published pattern would be a guess; deriving a
new one needs disassembly. dd-unlock never presents an unsigned image to fwupdate, so the whole
signature question is moot. This is the wiki's own recommended method for airOS 8.5.7+.

**Why urescue is the recovery anchor.** Confirmed present in the pulled live u-boot 1.1.4-s1100
(`urescue - start TFTP server and wait for firmware`), with fixed recovery IP 192.168.1.20. It
lives in the bootloader, so it survives a failed OS flash — the AGENTS.md §4 debrick guarantee.
Host-side push tool: `safety/recovery/urescue_push.py` (validates image magic + sha256 before
sending). Full runbook: `safety/recovery/FMX-0002_recovery_runbook.md`.

**Method for reaching this decision (matters for trust).** Every wiki claim was cross-checked
against artifacts read read-only from the exact unit — not accepted from the page alone. The
read-only probe (`inventory/board_probe/preflash_probe.py`) has an enforced write-primitive guard
and a "0 associated stations" abort so it can never run against a production radio.

**What is NOT yet decided / done.** FMX-0002's *demonstration* — physically power-cycling into
urescue and reflashing — is an operator action and remains open. Whether `urescue` accepts the
OpenWrt *factory* image directly (a urescue-only install) is INFERRED-strong from the bootloader's
`OPEN` magic-table entry and will be settled on serial during the recovery dry-run. No flash has
occurred; the unit is untouched at airOS 8.5.12 baseline.

---

## D-0005 — 2026-08-08 — Cambium Elevate is closed and irrelevant

**Decision.** Stop treating Elevate as a reference point. Two reasons, the second decisive:

1. **Factually inapplicable** — Elevate covered M-series (802.11n) only, never AC-generation
   radios (operator, 2026-08-08).
2. **Structurally irrelevant** — Elevate's only value was as an existence proof that a
   non-vendor stack can run on Ubiquiti hardware. **OpenWrt already does that on our exact
   devices**, with official profiles. A precedent is unnecessary for something we can boot.

**Correction to my own prioritisation.** I had listed "verify Elevate's AC coverage" as the
top open research question. It was not: the answer changes no decision. This is the same class
of error as citing a competitor's closed system when an open one is already in hand.

---

## D-0004 — 2026-08-08 — Scope correction: FuturaMAX is a custom firmware, not airOS tuning

**Decision.** All work targets building a custom firmware/software stack for airMAX AC
hardware. Configuration tuning of stock airOS is **out of scope** except where it produces a
measurement baseline (AGENTS.md Stage 1 explicitly permits airOS-preserving intelligence, but
that is a parallel track, not the goal).

**Why this needed stating.** An earlier session spent substantial effort probing and modifying
`/tmp/system.cfg` on airOS units — discovering the `cfgmtd` write path and 62 undocumented
`radio.*` keys. Interesting, and largely beside the point. The operator's framing:

> "we researched so much about new things test improvements of the AC chipsets/hardware, not
> to fine tune the Ubiquiti firmware"

The research corpus exists to find techniques worth **implementing in our own stack**. Tuning
the vendor's config file cannot deliver a 2017-frozen scheduler's replacement.

**Consequences.**
- `knowledge/AIROS_CONTROL_SURFACE.md` is demoted to a baseline/reference artifact. Its
  hidden-key finding stays recorded — it is real and may inform Stage 1 — but it is not a path.
- The `radio.*` hidden-key experiments (G25, G28, G29 follow-ons) drop in priority.
- Stage 2 (OpenWrt observability lab) becomes the active line of work.

---

## D-0003 — 2026-08-08 — RETRACTED: the custom-MAC "NO-GO"

**Decision.** The earlier NO-GO verdict is withdrawn. `knowledge/CUSTOM_MAC_GO_NO_GO.md`
returns to **UNKNOWN**, where AGENTS.md §8 requires it to stay until the eight Stage 4
criteria are measured.

**Why it was wrong.** It asked "can we replicate airMAX *on stock firmware*?" — never the
question. Finding Ubiquiti's scheduler inside their proprietary radio firmware describes what
*their* firmware does; it does not bound what *ours* can do. It also pre-empted a gate the
constitution defines as measurement-driven, using string analysis instead.

**Aggravating factor.** All control-boundary probing was done on **airOS**, which is the wrong
stack to evaluate. The Stage 4 criteria are properties of an OpenWrt/ath10k system.

**What replaces the verdict.** Nothing, yet — and that is correct. The gate is measured on
OpenWrt at Stage 2, not argued from firmware archaeology. See D-0005 for why no external
precedent is needed to justify proceeding.

---

## D-0002 — 2026-08-08 — OpenWrt 24.10.4 / ath79-generic is the custom-firmware vehicle

**Decision.** Build FuturaMAX on OpenWrt 24.10.4 (`ath79/generic`, Linux **6.6.110**).

**Rationale.**
- **Every target device has an official profile**: `ubnt_lap-120`, `ubnt_litebeam-ac-gen2`,
  `ubnt_nanostation-ac-loco`, `ubnt_nanostation-ac`, `ubnt_rocket-5ac-lite`,
  `ubnt_powerbeam-5ac-gen2`, `ubnt_rocket-5ac-lite`.
- The lab unit is a **LAP-120**, which maps exactly to `ubnt_lap-120` — factory and sysupgrade
  images both exist.
- Kernel 6.6 carries the entire body of post-2017 mac80211 work the research corpus is about:
  AQL, airtime fairness, per-station TXQ, FQ-CoDel. airOS runs **2.6.32** — a 2009 kernel.
  This is the single largest lever the project has and it comes free with the platform.
- It is a real build system: we can patch mac80211/ath10k and produce reproducible images.

**Rejected alternatives.**
- *Patch airOS* — no source, 2.6.32 kernel, signed images, and the scheduler is in firmware.
- *Write firmware from scratch* — no QCA target SDK; not reachable.
- *ath10k-ct as the base* — still an option **within** OpenWrt; deferred to a Stage 2
  comparison (upstream ath10k vs ath10k-ct) rather than decided now.

**Status.** Images downloaded and SHA-256 verified against OpenWrt's `sha256sums`:
`firmware/openwrt/openwrt-24.10.4-ath79-generic-ubnt_lap-120-squashfs-{factory,sysupgrade}.bin`.
**Not yet flashed** — recovery must be proven first (AGENTS.md §4).

---

## D-0001 — 2026-08-08 — AGENTS.md is the constitution; the handoff was a lossy summary

**Decision.** `AGENTS.md` (installed at repo root, byte-identical to
`FUTURAMAX_PROJECT_GUIDE.md`) is the primary source of truth. The
`handoffs/handoff-2026-08-08T12-57-03-a63934.md` R0–R9 research pipeline is **historical
context**, not the plan.

**Why.** The handoff omitted: that the goal is a custom firmware, the Cambium Elevate
precedent, the Stage 0–5 structure, the FMX-0001…0010 experiment list, the P0 implementation
backlog, and the repository layout. Working from it produced a research-evidence system when
the constitution asks for an experiment operating system.

**Consequence.** Repository restructured to the AGENTS.md §5 layout. Prior research artifacts
are retained under `research/` and `knowledge/` as inputs, not as the deliverable.

## October16 -100M survival does not clear E2 and lowbuddyblocks nextload

Keep f73c100M30s result as scopedtransmission/survival evidence, including
62.433Mbpsreceiver/37.421%UDP loss and unchangedfreshness/cleanup criteria.
Do not interpret native0OOM or fullobservation as acceptableperformance,
losslessaccounting, or fullbaseline. No automatic200M escalation.

Preserve originalloadadmission4096pages/8192KiB andabort3072/4096. Current
CPEquiet3035buddyfree/1836PCP/4784available blocksload and oldPCPprobeinitial
gate. Investigate a distinct no-loadrecovery contract using exactLinuxPCP
semantics; no source/runtime recoverychange untilrecorded andindependently
reviewed. This is minimumacquisitionsupport forE2, not optionaltuning.
No switch10.10.100.90access; uncertainWISPsharingcannotresolvefromoldinventory.
