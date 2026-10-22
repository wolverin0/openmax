<!-- doc-head: FMX0016 four-CPE multi-generation PtMP and telemetry PASS -->
Run8: WA8/XC8/SXT ath9k/airOS6 M5 simultaneously authorized for60.5s.
All four64/64 pings passed;256 radio request/reply pairs;41 station samples.
Four ping streams overlap62.801s; AP5180MHz/20MHz/0dBm/AR andWDS enabled.
Exact AP/Rocket and original open legacy profiles/hashes/IPv4/routes restored.
Guards ended; owned RAM files removed; no flash/commit/cfgmtd/reboot/module work.
<!-- /doc-head -->

## October22 - Keep FMX-0016 exact four-CPE RAM fixture; task complete

Run8 confirms simultaneous WPA2 authorization for60.5s across stock WA8/XC8,
OpenWrt ath9k SXT and stock airOS6 M5. Each passed64/64 pings, radio-paired,
with41 per-station samples; four-stream overlap62.801s. Exact restoration
passed on every modified device. Evidence is the requested
`artifacts/canary_panel1_guarida/root_four_cpe_result_20261022.json`.

KEEP: reuse held firmware/modules, AP5180MHz/20MHz/0dBm/AR and APWDS1.
Keep legacy original3-address station mode. Use SXT uncommitted encryption/key
deltas and one owned stock M5wext supplicant with private tmpfs config/logs.
Both legacy guards remain240s, restore on signal/EXIT/timeout, and are verified
open over RF before AP radio-off. Preserve all management IPv4/routes and
config/protected hashes. Remove only exact hash/PID-bound ended temporary
files; preserve prior unrelated evidence. No persistent crypto configuration.

KEEP explicit XC discovery as the working admission procedure: disabled
network, acknowledged volatile cache flush/SCAN, observed exact target BSSID/
frequency/SSID/CCMP, IE clear,1s settle and enable. Do not require raw vendor
IE bytes from a stock BSS API that does not export them. Preserve negative
attempts and keep formal four-client/radio/restoration criteria unchanged.
This is a working exact recipe, not a universal causal timing proof.

The proof is limited to four exact hardware/firmware instances, low-rate
traffic, AP station telemetry and two legacy self-reports. No cooperative
relay/optimizer, TDMA/GPS, performance gain, larger-sector or production
acceptance follows. Existing E2/other parked gates are unchanged. LAP stays
OpenWrt with radio off; stock return remains cancelled. The operator's
requested FMX-0016 acquisition is complete; no further RF task was started.

## October22 - Keep guarded stock WA/XC interoperability recipe; close FMX0015-R18

Evidence: run25 holds both stock WA/XC CPEs authorized with WDS for61.031s,
64/64 qualified radio pings each (59.197s overlap), and WA survival over a
2.031s API IE re-pulse with8/8 matched radio pairs. Exact restore passed for
AP and Rocket, including original hashes, rules and ordered IPv4/routes.
The accepted receipt and preserved negatives are linked in BENCH_PLAN and
`artifacts/canary_panel1_guarida/root_multi_cpe_result_20261022.json`.

KEEP: reuse the existing mac80211-patched LAP image; AP WDS only in the RAM
window; stock CPE modules; Rocket network0 configured only with volatile
wpa_cli. Preserve br0 and198 management membership, isolate only the two
specified eth0/ath0 FORWARD transit directions, and remove only owned rules.
Permit at most4 readiness blocks, still exactly one AP plus only its expected
same-MAC WDS AP/VLAN children. Require complete wireless request/reply pairs
on each child to distinguish data traffic from the shared Ethernet path.

KEEP the observed late-enable recipe (target1.7s into2s discovery pulse),
with API-clear before normal dual observation. This is a bounded measured
compatibility result, not proof of a universal firmware timing mechanism.
Do not generalize two exact CPE/firmware instances into all-airOS8, sector
capacity, TDMA/GPS or performance acceptance. OTA IE timing remains pending.

The final guard captures/restores full IPv4 address order/routes because R24
stock runtime promoted its existing169.254 address. Retain the initial
failed comparison/repair; the fresh successful restoration is separate evidence.
198 stays onbr0; no bridge-port removal, persistent config write, flash,
reboot or module change was used. LAP stock return remains cancelled and
OpenWrt remains installed with radio off. This requested task is complete;
prior E2 and other parked experiment gates are unchanged.

## October22 03:18 UTC - Both ends associate; isolate missing WPA exchange

Run14: same AP associated/unauthorized result and exact restored radio/config.
A bounded passive AP VAP capture started03:09:52.523UTC before Auth03:10:00.497;
zero EAPOL frames, terminated when the restored interface disappeared. This is
INCONCLUSIVE for EAPOL transmission: held exact driver_nl80211.c can use the
netlink control port for EAPOL, outside that VAP packet socket. No runtime path
claim or credential/cipher change follows from zero. PCAP private inrun14_eapol.

Run15: native stock-CPE status sampling scheduled after broadcast-clearACK+12s
captures SCANNING, then four consecutive1s4WAY_HANDSHAKE samples with target
18:e8:29:74:55:a2 / FuturaMAX-LAB / CCMP / WPA2-PSK, then SCANNING again. This
independently confirms CPE association plus AP get_clients association, with
WPA authorization still incomplete. Native MIB yielded no counters; preserve
that missing measurement. AP failed original7s gate; exact radio/config,
emptydeltas andguardended/no errors, Ethernet management/known_hosts restored.
Evidence root_goal_run15_cpe_live_wpa_20261022.json, referenced wired receipt
and root_goal_direct_association_20261022_run15/receipt.json. No status1 claim
from older logs is applied to these current successful association exchanges.

Run16 changes only measurement: already-installed CPE tcpdump onath0,
nonpromiscuous, EtherType0x888e, standard decoded text/nohex, snap128/max16packets,
15s, scheduled via same wired route at broadcast-clearACK+12s. Own matching
childPID/start is checked before SIGINT; no CPE files/config/software mutations.
All existing AP timing/radio/IE/association/stability/traffic/restore gates stay.
Fixed recipe root_goal_direct_run16_plan_20261022.json; stop on first gate
failure or complete acceptance, restore both paths, retain failed evidence.

## October22 03:09 UTC - AP association confirmed; capture WPA handshake directly

Run13 repeated run12 timing with only retention of existing per-CPE get_clients
responses. Thirty observations show auth=true/assoc=true/authorized=false/aid1
from03:01:52.371UTC; auth/assoc becamefalse4.000s later. This confirms AP-side
association, not CPE-side association/authorization, traffic or60s stability.
Exact radio/config restoration, emptydeltas, guardended and no cleanup errors.
Evidence root_goal_direct_association_20261022_run13/receipt.json and
root_goal_direct_run13_result_20261022.json. Do not carry historic status1
interpretations into this run. AP data establishes a different remaining gap.

Private read-only comparison of AP configured key and stock-CPE WPA network
computes PMKs only in memory: sameSSID/PMK=true, CPE RSN/WPA-PSK/CCMP. No key
or key hash persisted/printed. First comparison failed remote command parsing
and is preserved; corrected trailing newline yields PASS with Ethernet route
and temporary known_hosts cleanup verified. See root_goal_private_pmk_comparison
_v2_20261022.json and referenced wired receipt. RF remainedOFF throughout.

Next fixed run14 retains run12 timing and all acceptance/restore gates. Existing
AP tcpdump captures only EtherType0x888e for this exact peer, without monitor or
promiscuous mode, max64packets/snap512/100s. Foreground shell bounds capture and
signals only its own matching PID/start; no daemon restart/install/targetfiles.
This distinguishes missing EAPOL reply from later handshake failure. No old
log diagnosis, agents, CPE changes, cipher/WDS changes or new firmware features.
Fixed acquisition: root_goal_direct_run14_plan_20261022.json. Stop at first
failed mandatory gate or full existing acceptance; retain PCAP privately.

## October22 02:59 UTC - Run12 executed; ordered IE withdrawal confirmed at API level

Result: INCOMPLETE_DIRECT_ASSOCIATION / NO_AUTHORIZED_ASSOCIATION_WITHIN_7S,
exit1. First target broadcast observed02:58:25.904671UTC; sleep0.5s then empty
vendor_elements APIack02:58:26.447172UTC, with NO snapshot before clear. Two
nonbroadcast CPE probes did not trigger another clear. Auth observed
02:58:50.103596UTC,23.656424s after empty acknowledgement. This completes the
operator timing treatment but does not prove byte/order timing over the air.
No stability samples or bidirectional traffic acceptance. Exact wireless hash
f8e679e4639fc5c26b6c96d646e1e56b57fb58064a75eb215c34ad0462285a6a restored;
empty RAMdeltas, radioOFF, independentguardended, cleanup_errors empty.
Evidence: root_goal_direct_association_20261022_run12/receipt.json and
root_goal_direct_run12_result_20261022.json under artifacts/canary_panel1_guarida.

The composite7s gate alone does not distinguish missing association from
association without WPA authorization: its intermediate get_clients flags
were not preserved. Minimum next diagnostic is to retain those existing
live AP per-CPE responses during the unchanged ordered acquisition. No old
log diagnosis or subagents; no new firmware/RF/config/IE/cipher changes.
The parent association/bidirectional/60s outcome remains NOT_ACCEPTED.

## October22 02:58 UTC - Run12 fixed acquisition recipe (operator)

Parent FMX0015 / forward-plan PhaseB/C / direct OpenWrt LAP to original airOS
Loco195 remains the active deliverable. Run11 advertised no discovery IE and
ended NO_AUTH_WITHIN_75S_OBSERVATIONAL_NEGATIVE; exact radio/config restore and
debug-level/RAM cleanup passed. This does not establish association behavior.

The operator selected a precise timing treatment, superseding log diagnosis:
discovery_present/TRIAL_IE=True; first ubus probe from fc:ec:da:c2:54:0a with
target ff:ff:ff:ff:ff:ff, exact interface and5180MHz; sleep0.5s, then call
set_elements(empty) immediately WITHOUT a snapshot. Unicast probes do not
trigger withdrawal. Pre-withdrawal Auth cannot satisfy the ordered recipe.
Auth wait75s; authorization7s; same60s stability and30s bidirectional callback.
Work deadline210s, cleanup through230s, independent radio-off guard240s,
subscription205s. Guard identity/owned scripts/exact restore checks retained.
The frozen base numeric TTL and pinned hash chain were updated only for this
explicit bounded duration. Original source bytes are preserved as.pre-run12.
No debug proxy, target log analysis, subagents, firmware flash, persistent
configuration or CPE software/configuration changes occur in this treatment.

Fixed plan and bindings: artifacts/canary_panel1_guarida/
root_goal_direct_run12_plan_20261022.json. Stop at PASS across existing gates
or preserve the first failed gate and restore. No prior run is rescored.

## October22 02:09 UTC - Association rejection localized; minimum diagnostic acquisition

Parent FMX0015 / forward-plan PhaseB/C / operator direct-link goal remains active.
Run6 retained exact native-format PtP discoveryIE after Auth; Auth01:59:37.298UTC,
then NO_AUTHORIZED_ASSOCIATION_WITHIN_7S. AP radio/config exact-restored,
RAMdeltaempty/guardended/no errors. This rejects the simple withdrawal-only
hypothesis for this bounded run; no association/traffic/stability acceptance.

Fresh pinned CPE log query020136Z (route cleanupPASS) proves successful Auth RX,
Association Requests TX, and repeated Association Response status1 for R5/R6.
The earlier R4-tail exchange had successful AssocResp then AP-originated deauth
about1s later; clock correlation remains inferred, no prior failure is rescored.
Evidence root_goal_cpe_after_run6_auth_logs_20261022.json and
root_goal_direct_association_20261022_run6/receipt.json. Radio power/reception
alone cannot explain the observed explicit status1; no power/RSN/WDS change is
justified yet. Exact WA hooks reviewed do not prove a proprietaryAuthResponse
requirement; old script label on_auth_rx0x9bf0 was wrong (actual0x8a9c/96B).

Exact local hostapd source has status1 paths for malformed/SSID/WMM/rates and
ubus handler rejection. A normal CLI subscriber returns0 and does not itself
prove rejection; assoc notification occurs AFTER check_assoc_ies. The next
minimum missing datum is the actual reject reason for this MAC/AssocReq, with
continued notifications. No speculative protocol patch or CPE mutation follows
from generic status1. Vendor-element API source confirms same conf bytes feed
beacons/probe responses; OTA byte/order qualification remains separate.

Necessary support only: existing compiled same-build hostapd_cli is present
locally; target has no installedCLI/socat/socket module. Stage that held tool
in an exclusive owned /tmp directory, query original loglevel, enable DEBUG
without show_keys, perform one same-metadata/RF guarded direct window, restore
original level BEFORE frozen radio-off, remove owned binary/directory exactly.
All commands remain bounded; DEBUG restore failure cannot suppress radio-off
and prevents acceptance. No firmware/config commit, daemon restart or protected
partition change. Local helper receives separate review before target staging.
This is required to identify the parent failure, not a new research platform.
Original Auth45s/assoc7s/stable60s/bidirectional/155+20s/180s-guard gates stay.

## October22 01:58 UTC - Auth confirmed; KEEP discovery timing treatment admitted

FMX0015 / forward-plan PhaseB/C / operator direct-link goal remains active.
Run4 native metadata failed fixed45sAuth observation. Run5 raw native CPE scan
and wpaBSS id4 confirm reception of FuturaMAX-LAB/BSSID18:e8:29:74:55:a2 at5180,
level-72dBm/age6, WPA2-PSK-CCMP. Loaded network0 and file matchSSID/RSN/CCMP.
Run5 Auth01:51:25.940UTC, IE withdrawal01:51:28.222, then failure to authorize
association within7s. No traffic/stability acceptance. AP exact radio/config
restored and guard ended, no cleanup errors; CPE wired queries restored routes.
Evidence run5/receipt.json, root_goal_direct_scan_run5_cpe_20261022.json,
root_goal_run5_ap_auth_diag_20261022.json, root_goal_cpe_supplicant_networks_20261022.json.
AP logs contain an earlier Auth+associated event near run4 tail, timing inferred;
neither failed run is rescued. The alternative unicast-key hypothesis is refuted
for reviewed WA beacon callers: NULLsecondMAC selects broadcast fallback.

Prospective run6 changes one timing intervention: retain SAME native PtP IE
through Auth/association/stability, testing whether withdrawal blocked selection.
Auth<=45s, authorized<=7s, continuous>=60s plus bidirectional wireless traffic,
same5180/20/0dBm,155s treatment/20s restore/independent180s guard remain required.
Full restoration clears IE/radio exactly. No new firmware/flash/Rocket branch.
Pinned AP readback found br-lan MAC75/LL75, distinct from radioBSSID74. Oldcallback
ping74 was unassigned and its FDB74 check false-negative for valid bridge75.
V2 corrects ping/FDB tobridge75 while retaining independent radioBSSID74 check.
Six disposable acceptance/fail-closed fixtures pass; this is tool validation only.
Independent KEEP+callbackV2 review SHAea5e4122c48b6d2043ea29d171adf98f443e706db6c285703fa0e362e92c2a8c
binds current source/helper/callback/native receipt. No acceptance criteria lowered.

## October22 01:44 UTC - In-window visibility negative; native metadata trial fixed

Parent FMX0015 / forward-plan PhaseB/C / operator direct-link goal remains active.
Run3 reused the reviewed V2 radio/IE unchanged, adding an independent wired CPE
cache query while discovery was present. AP discovery01:40:33, CPE query01:40:46-
01:41:03, AP end01:41:21UTC. CPE remained SCANNING; scan_results target-filter and
BSS18:e8:29:74:55:a2 were empty. This is a native CPE visibility/selection negative,
not proof that no RF reached its antenna. NoAuth within45s again; AP config/radio
and guard restored exactly, no cleanup errors. CPE query also restored its wired
route and removed temporary public-host file. No scan trigger/config mutation.
Evidence root_goal_direct_association_20261022_run3/receipt.json,
root_goal_direct_scan_run3_cpe_20261022.json, wired receipt014046Z.

Existing generator failed to decode the measured WA IE because its HMAC argument
order was wrong. Failure and alternate-prototype evidence remain preserved.
HMAC-SHA1(key=broadcast MAC,data=BSSID) now decodes native protocol9/BSSID+MAC,
capability0x1e, extra0, hostnameLiteAP AC, SSIDubnt. Reconstructing all60 bytes
is exact against the selected IE repeated32 times in held PCAP6d119dbc... .
This validates the advertising format on our WA capture; it does not validate
OpenWrt OTA insertion/order, CPE association, airMAX scheduling or datapath.
Candidate independent source comparison reports identical code+relocations for
WA/XC beacon/insert/parse functions; PtP branch emits capability1, not0x11.
Root model receipt root_goal_ie_model_validation_20261022.json; exact provenance
and separate operational review bind the next run before RF.

Prospective run4: replace only discovery metadata00156d with the reconstructed
002722 layout, matching BSSID18:e8:29:74:55:a2, FuturaMAX hostname,
SSIDFuturaMAX-LAB and native PtP capability1; withdraw after observed Auth.
Same reviewed image, AP0/WDS policy, original unmodified CPE, legal5180/20/0dBm,
45sAuth/7sauthorized/>=60sstable, bidirectional wireless counters+ping,155s budget,
20s restoration reserve and independent180s guard. No new firmware/flash/Rocket
work. Stop this treatment on first failed criterion, preserve evidence and
verify exact restoration. This is a minimum discovery compatibility treatment
for the direct-link deliverable, not a new feature or performance claim.

## October22 01:32 UTC - First direct RF result: probes, no authentication

Parent remains FMX0015 / forward-plan PhaseB/C and operator direct-link goal.
Native boot completed01:21:04UTC, PASS_STEP1C_BENCH_FULL_IMAGE_BOOT_RADIO_OFF_OWN_STOCK_RETURN_PENDING,
receipt root_goal_direct_link_cycle_20261022_native_install/receipt.json SHA
ff6fdbac93c279ad55468e0165767de0f05dddd79db21c7bd3ce1f38a1ac0f92.
Fresh OpenWrt boot a7b3bd59-3ea0-40b7-9e7c-f040c555c9c8, host-key pin and
radio-disabled state were independently bound before acquisition. Bench image
and all installation/return gates remained unchanged; own-stock return is owed.

Run1 failed BEFORE radio/guard at command-vtimeout (rc127). The image lacks that
applet; it is not a wireless result. Read-only native ubus -t1 listen terminated
in1.032s/exit0. A minimal V2 uses that existing timer for subscribe; prior source,
failed receipt and first fake-fixture mismatch remain preserved. Nine fixtures
and independent reviewc5d0809446e15ce3d5ce09080a9bc84b87e667e97a8dca4c7787562c17d248c8
accepted this exact V2; this is enabling validation, not association evidence.

Measured run2,01:27:56-01:28:58UTC:
- Guarded AP phy0-ap0, ifindex4, BSSID18:e8:29:74:55:a2,5180MHz/20MHz/0dBm.
- Discovery IE API acknowledged; actual OTA IE content/order remains pending.
- Subscriber recorded45 probe events, including3 from exact CPEfc:ec:da:c2:54:0a
  on5180 at-43/-41/-41dBm. No Auth event arrived in the fixed45s observation.
- Decision: bounded observational negative, NO_AUTH_WITHIN_45S_OBSERVATIONAL_NEGATIVE;
  no stock-CPE association, bidirectional traffic or60s stability acceptance.
- AP restored radioOFF, original config hash, empty RAM deltas and ended guard,
  with no cleanup errors. No CPE/Rocket configuration or module mutation occurred.
Evidence: root_goal_direct_association_20261022_run2/receipt.json and
its auth_listener.jsonl, private under the existing canary artifact folder.

CPE read-only post-window diagnostic013116Z passed with complete wired cleanup:
state SCANNING, native wpa_cli/control socket available, no target in the cached
scan queried roughly two minutes after the window. Cache expiry is unresolved;
this does not prove the CPE failed to receive the AP. Earlier012930Z log query
endedrc2 from a trailing-newline/semicolon composition after collecting logs;
its failure is preserved and temporary route cleanup passed. Corrected rstrip
query passed. Logs yielded no candidate-rejection reason; no debug/config knob
was changed. Fresh stock runtime remained accepted, not wireless behavior.

Next decisive diagnosis: compare the existing trial discovery IE with held
exact-stock protocol evidence and/or query the CPE scan while the AP is present.
Any further window must state its changed hypothesis/instrumentation, keep the
same legal RF/identity/180s guard and stock-CPE boundaries, preserve this failure,
and complete exact restoration. Reuse the already booted image; no new flash or
Rocket refinement is justified. Full native stock return remains mandatory.


## October22 01:13 UTC - EdgeRouter restored; direct bench execution resumed

Operator reported the EdgeRouter10XP had been disconnected and was booting.
LAP SSH returned at01:06:11UTC. Fresh pinned/authenticated stock readback
root_step1c_lap_after_native_ram_v3_20261021_3/receipt.json
(SHAa5d278843b73ba388c958fcdce6a93c5d2c9d8b4a559ed7f081650b2191694c0)
passed: boot67aec177-313e-4e88-9392-9dda253c0401, raw partitions0/1/2/3/5 exact,
strict cfgV2 reciprocal-role state, runtime/inittab, native watchdog and wired
management all accepted. Current evidence refutes an unbootable LAP at this time.
The prior unreachability records remain valid observations, not brick evidence.

Parent remains FMX0015 / forward-plan PhaseB/C and operator direct-link goal.
Fresh cycle root_goal_direct_link_cycle_20261022 reuses the frozen boot/return
engines and identical bench image773f2e28c97ff920f83fdabf19be286dccfc85a2fe2f9a53412fda3d14f42858.
Baselineef54b0a1c2de138893ba7e947197e4dfc439548dded38df3881069e662c390cd,
profile0e3e5346eaa7c77771a86c57846dbee47ab8598aed26c4398d6c2caf39918570,
writer79665551041668b1ef3635ad6e07b6ffefb529148140c91346da3d2fa963f437.
Only nonce/three RAM path macros changed; reverse substitution equals the frozen
writer core. Independent operational review12d677ffcc129111c0602122da5c2247233563a347dcdd529597f6de04b4c972
accepted30 exact bindings including fresh stock callback route and standing bench
authority. First nc callback attempt failed before any flash because applet was
absent; preserved failure, reused the existing nonce-bound ephemeral wget route,
then received PASS_PINNED_LAP_TARGET_AND_CALLBACK_ROUTE. No reserve is lowered.

Prospective direct acquisition is fixed before RF: same BSSID/ifindex,
5180MHz/20MHz/0dBm; Auth observation up to45s, authorization up to7s, continuous
association>=60s, AP-to-CPE ping and a<=30s wired-management callback for reverse
wireless ping. AP station connected-time/counters and CPE ath0 counters/FDB must
prove the wireless datapath; management SSH alone cannot pass. Total treatment
budget155s with20s reserved for restoration, independent radio-off guard180s.
Existing Window controls restore IE/radio/config and verify ended guard; full
own-stock return remains mandatory after the cycle. Runtime Auth notification
is observational and does not guarantee RF frame ordering. Both source helpers
receive separate independent review before RF. No Rocket acquisition is resumed.


## October22 01:03 UTC - Goal blocked audit: authenticated LAP management unavailable

The same concrete execution blocker persisted across three consecutive goal
turns. Latest read-only rechecks at01:02:45 and01:03:33UTC timed out on SSH for
192.168.1.20 and both known LAP IPv6 addresses. Receipts:
root_goal_lap_access_recheck2_20261022.json and
root_goal_lap_access_recheck3_20261022.json. The original probes, Ubiquiti
exact-MAC discovery and local DHCP/MAC lookup remain preserved. The operator
confirmed power/LAN connection; no physical cause or device damage is inferred.

The CPE's independent wired route and stock runtime are qualified at01:00UTC.
No authenticated route to the LAP is currently available to take a fresh baseline,
boot the bench image, execute the direct link experiment or verify restoration.
The pending external action is to establish/test the LAP injector LAN path with
a known-good cable/port or direct management link while preserving PC Internet.
There is no active process or experiment guard to wait on. Further identical
probes or helper work cannot establish the requested radio outcome.

Goal status is BLOCKED, not complete. Preserve the full requested association,
bidirectional wireless traffic and>=60s stability scope. A restored LAP path
unblocks fresh identity/baseline and the fixed direct recipe below; no further
generic bench authorization is needed. Independent OTA IE validation remains
pending separately. No AP/CPE RF/config/flash/reboot operation ran in these
three goal turns.


## October22 00:55 UTC - Direct association goal resumed; current management evidence

Parent: FMX0015 / original forward-plan PhaseB/C. The operator's new goal in
pasted-text-1.txt prioritizes association, bidirectional traffic and stability,
with autonomous continuation under existing bench authority. Independent OTA IE
acceptance remains INCOMPLETE and is tracked separately; its receiver limitation
is not a general prerequisite for this direct link experiment.

Fresh CPE Ethernet management succeeded via pinned Omarchy gateway and its
existing 180s-expiring IPv6 route. Receipt root_wired_recovery_20261022T005122Z.json
is PASS_WIRED_SSH_RESTORED, exit0, temporary address and public known-host file
removed; existing routes matched afterward. CPE identity is e7fa/WA.v8.7.25,
boot d66cd71d-8d38-4469-8832-45c9438a5252. Stock module MD5s are unchanged,
there are no bind mounts, user cron and its job are disabled, SSID is
FuturaMAX-LAB and ptpmode is1. It is unassociated. This is management evidence,
not wireless traffic acceptance. No AP/CPE mutation occurred in this check.

Current LAP access differs from the last completed restoration receipt:
root_step1c_lap_after_native_ram_v3_20261021_2/receipt.json records a connection
timeout before capture and zero writes. Known IPv4 and both known IPv6 addresses
also timed out. The operator confirmed power and LAN connection. Read-only
exact-MAC Ubiquiti discovery received no replies on either local subnet; this
alone cannot distinguish a path/filter problem from device availability.
The gateway's192.168.1.20 resolves to the CPE MAC, so it must not be used as a
LAP endpoint. Evidence: root_goal_direct_link_reachability_20261022.json,
root_goal_direct_link_gateway_readonly_20261022.json,
root_goal_ap_gateway_route_readonly_20261022.json and
root_goal_lap_mac_discovery_20261022.json, all under the existing canary artifact
folder. LAP live health is UNKNOWN; historical stock restoration remains valid
at its recorded time. A direct cable check is pending, preserving PC Internet.

Fixed next direct recipe after LAP management is recovered:
1. Capture fresh exact LAP identity/config/protected baseline; reuse the reviewed
   bench-only image and frozen boot/own-stock-return engines with new attempt
   paths and bindings. Do not reuse consumed outputs or locks.
2. Reuse Window.arm() with its independent180s radio-off watchdog and verified
   BSSID/ifindex,5180MHz/20MHz/0dBm/regulatory readback. Keep CPE stock and its
   wired management independent. Stop on identity, guard or restoration failure.
3. Use the existing supplied discovery IE and AP-side Auth notification for the
   exact CPE MAC; remove trial IE with set_vendor_elements plus update_beacon
   without restarting the VAP. Record event/action times. The100ms fail-open
   notification is not an RF-ordering guarantee; the trial is observational.
4. Require AP authenticated/associated/authorized state AND matching CPE BSSID,
   continuous association>=60s, and successful traffic in each direction over
   the wireless path. Correlate AP station/CPE ath0 counters and prove routes;
   CPE SSH over Ethernet does not satisfy this criterion. AP WDS=0 versus CPE
   WDS-enabled is an explicit diagnostic variable if association succeeds but
   data fails; do not modify CPE firmware/configuration to obtain acceptance.
5. Preserve each negative result, restore the guarded window and verify the
   mandatory own-stock return. A successful helper or API does not close goal.


Further current evidence at01:00UTC: the ARP-only exact-MAC lookup covered the
local192.168.100.0/24 candidates and found no LAP/Rocket match; it opened no
service sessions and does not prove device damage or a physical disconnect.
Artifact: root_goal_lap_dhcp_mac_lookup_20261022.json.

The second bounded CPE readback, root_wired_recovery_20261022T010009Z.json, passed
with exit0 and complete temporary-route cleanup. Its stock-runtime markers show
ubnt_op_mode=1, is_ubnt_ptp=1, uph_wifi0/enable=1, no allow_80211 override, no
user crontab and no patch/pending-write flags. Stock module files and zero bind
mounts were reconfirmed. No association/traffic/stability acceptance follows.

Independent read-only review by candidate_safety confirmed the first current CPE
receipt/cleanup, the gateway192.168.1.20 CPE MAC, and LAP live UNKNOWN. No radio,
flash or firmware-return operation ran in this goal turn. All local probe and
wired-management processes completed; no experiment guard is active. The goal
remains active, awaiting recovery of authenticated LAP Ethernet management.

Minimum missing execution evidence now is authenticated LAP management, followed
by the above physical link trial. Keep the goal active; do not restart the parked
Rocket capture work or broaden firmware research.


## October21 23:31 UTC - Native restoration complete; receiver prerequisite unresolved

**CONFIRMED:** LAP120 own-stock return completed23:29:53UTC, exit0,
PASS_LAP120_OWN_STOCK_RETURN_EXACT_RAW_AND_STATE_V2. Fresh baselinefd4852b5,
raw firmware/protected bytes, native config state and wired management passed.
Receipt: artifacts/canary_panel1_guarida/root_step1c_direct_interop_cycle_20261021_return_own_stock_after_cache/receipt.json,
SHA8b5224285d97af8dcf210e25d91c9a2be7f58efef7f7931b4f4d10091e536566.
The first return failed before handoff/sysupgrade because MemFree17728KiB was
below17768KiB required. Its receiptf525f0e3 remains unchanged. One reuse of the
existing clean-page-cache route raised MemFree to33100KiB; original memory gate,
stock package, identity/protected/config checks and return engine stayed intact.
No reduction of reserve or retry after a partially executed return occurred.

**CONFIRMED:** Rocket16 native restoration completed23:22:16UTC with boot
5c4298a9-7934-413c-aa1c-d4eb2d245683. Native banks/config/persistent files,
protected firmware/modules and absence of monitor passed. Receipt6d3ac9cdcd03b2b12dd85b2b2d533fb0fb3e700cc52c346a88caf4bde61c4709.
Both radios are stock again; this cycle made no CPE195 mutations or production
access. No running acquisition, experiment guard or flash/return process remains.

Independent saved-evidence review confirmed both restorations: 38 LAP captures,
five exact raw partitions and cfgV2 with only reciprocal bank-role bytes changed;
Rocket protected/module hashes, both config CRCs, 120-key maps and persistent
files matched intake. Review did not perform a new live health probe.
Artifact: artifacts/canary_panel1_guarida/root_step1c_direct_interop_review_20261021_final_restoration_review.json,
SHAff805c858041045158f1d82a826fb350884c499550c05228e1b5d62ce375986f.
IE control and stock-CPE association remain INCOMPLETE.

**Measured negative:** with the same OpenWrt AP5180/20/0dBm, native Rocket
preseed reached5180. Active WPA recipe retained module refs2 and stopped.
Reusing the already-tested owned WPA pause released refs0 and created monitor,
but monitor readback reverted5165; strict frequency gate stopped before PCAP or
IE change. Acquisitionv2 receipt177148a345fe2cace40a0ca36e33ce3b853d210d2c6c9aa1c44e9adae8fe6542
has no phases or captures. The held/live OpenWrt phy listing has no5165/5810 in
its current channel list. This rejects these acquisition recipes, not the radio's
permanent capability or the overall interoperability hypothesis.

**INFERRED:** scan activity contributed to retained references; reference owner
was not identified. **UNKNOWN:** actual management-IE add/remove over the air,
auth-to-association timing and stock-CPE association on OpenWrt. They remain
INCOMPLETE; boot, hostapd API availability and restoration are enabling evidence.

Decision: park this CAP route and further native-driver refinements. The active
parent remains FMX0015 / forward-plan PhaseB/C. Minimum external dependency is
an independent5GHz receiver that can demonstrably capture the AP on a common
supported legal channel. Operator availability question is pending; no permission
is inferred from silence and no operator pause is claimed. After a receiver is
available, qualify target Beacon/ProbeResponse reception, then execute the fixed
absent/present/absent IE recipe and only then the stock-CPE association step.
Do not automatically replay old helpers, broaden firmware work or claim success.


## October21 23:24 UTC - Return memory gate preserved; existing cache route reused

Receiver V2 negative: confirmed5180 STA, owned WPA pause, refcount0/unload and
monitor creation succeeded; monitor readback5165 rejected before PCAP/IE. Live
OpenWrt phy listing has no5165/5810 channel, so no direct existing AP frequency
match. First channel-list parser missed decimal MHz; its empty extraction is
preserved and raw6692-byte phy output is authoritative. Rocket16 stock restoration
passed23:22:16. LAP return attempt failed before handoff/sysupgrade (both0),
MemFree17728KiB versus the unchanged package+reserve gate. Failed receiptf525f0e3
is preserved. Reuse only the existing clean-page-cache repair with fresh boot,
SSH key, paths, receipt hashes and .setup binding to the frozen wrapper; do not
lower memory floors or rewrite old output. Parent IE/association stays incomplete.

## October21 23:17 UTC - OpenWrt boot accepted; receiver transition negative

Direct cycle boot completed PASS23:11UTC: exact image773f, protected partitions,
board/runtime and radio-off gates passed. Native receipt91a3af0cad16123706fdc8f448a9f366bea9975be89c8dc1436c1900d20d2203.
Fresh SSH key97c35b differs from historicald678. First acquisition caller stopped
before connection/RF at the explicit pin gate; source/failure preserved as
.attempt1. The existing pinned connection body was copied with this exact new
key and acquisition additionally pins the native receipt; independent v2 review
78227322 accepted this delta. No TOFU or authentication-before-pin was added.

Acquisition23:14:39-58: AP5180/20/0dBm/BSSID18:e8:29:74:55:a2/ifindex4 passed.
Rocket native STA reached5180 at1dBm after one observed second. After ath0destroy,
ubnt_poll_host refcount remained2 for samples0..3; gate rejected before rmmod,
monitor creation, PCAP or any IE phase. No RX or interop claim follows. AP exact
RAM deltas reverted, radioOFF and guard ended. Rocket normal reboot requested.
Restoration15 early SSH timeout is preserved; after wired reachability returned,
completion passed23:16:39, boot1fb60a26-fed1-4327-a801-444bcee37b40, native firmware/
config/persistent/module checks exact. Root remains sole writer.

Offline comparison confirms an existing WPA SIGSTOP/identity/T-state block
previously allowed refs0 and monitor creation (then at5165, still exit1).
Decision: reuse that block only AFTER confirmed5180 preseed and BEFORE detach,
with the already-used PID/start-bound CONT in the reboot guard. Retain the
refs0 gate and3s bound. This combination is unmeasured; no forced unload, wait
extension or unchanged retry. Only bounded comparison with existing recipes
is in scope: decide whether an existing pause/quiesce step explains retained
references after the newly confirmed native preseed. Do not invent another
reverse-engineering branch or repeat unchanged. Keep parent IE acceptance and
LAP own-stock-return obligation; a receiver blocker does not accept association.


## October21 23:05 UTC - Minimum existing OpenWrt path prepared

Parent FMX0015 / original forward-plan PhaseB/C remains management-IE control
before stock-CPE association. Native AP retuning is parked. V14 did not reach
Rocket preseed; the changed question is whether the native Rocket5180 recipe
receives the already-proven OpenWrt AP5180/20/0dBm. Reuse image773f2e28 and
frozen boot/return engines, fresh baselinefd4852b5 from APV3 native captures,
and exclusive execution namespaces. Local GCC build and5fixture checks pass;
initial WSL timeout is preserved. Callback route passed23:03:40UTC, exact
stock host key/MAC and fresh nonce verified over wired IPv4 source155.

Minimum acquisition is one180s-guarded radio window: AP on and readback before
Rocket preseed; capture3s each absent/present/absent phase with stable BSSID and
ifindex; restore AP radio off and Rocket native state. Stop at any guard,
identity/channel mismatch or missing receive evidence; preserve the failure.
No further native driver reverse engineering follows automatically. Actual
Beacon and ProbeResponse IE appearance/removal remain the acceptance, followed
by the separate stock-CPE association test. API success, boot and local checks
are not OTA or interoperability acceptance. The frozen own-stock-return route
remains mandatory. Its historical reserve shortage is not silently repaired or
rescored; the existing clean-page-cache route is separate if needed.


## October21 22:58 UTC - V14 bounded negative; return to existing OpenWrt route

V14 executed22:51:54-57. AP1dBm readback passed, then native ath0 mode11ACVHT20
returned private ioctl8BF2 Invalid argument, exit255. No chanbw/frequency
setter, Rocket preparation, capture or IE change followed. Both guards
requested normal reboot. This is a qualified negative for this native mode
setter/recipe; it does not disprove5180 reception or interoperability.

Rocket14 restoration passed22:53:24, boot30bd0524-92c7-46db-8dfc-99e756927a27.
Receipt4f926f5b15a285845c0f1b894bada583c46e6e448292acb8e402ef202e3d1715.
APV2attempt2 verified raw/config then rejected valid signed Tx-Power=-4dBm.
Preserve that failure. V3 only adds signed-power parsing and observational
bounds, with five offline regression cases and independent delta acceptance.
V3 readonly attempt1 passed all native firmware/config/persistent/watchdog/
prescan/wired checks; APboot247214c0-4ba0-4f34-8d0c-aed823979c8d, mainRF5165/
center5175/VHT40/-4dBm. No historical RF restoration or cause is asserted.

Parent FMX0015 PhaseB/C remains. Native AP retuning is now parked as optional
support; do not investigate another driver order. Reuse the exact existing
bench OpenWrt image773f2e... and its proven boot/own-stock-return engines.
Prepare only fresh single-use output/profile bindings needed by those engines,
without modifying their historical receipts/locks. Existing AP5180/20/0dBm
window and hostapd IE methods are the relevant next control path; keep fixed
OTA/association acceptance and full native return. No automatic acceptance
from image boot, API acknowledgments, static review or stock-only captures.


## October21 22:51 UTC - Continuity correction and fresh V14 admission

The prior pause was the coordinator's inference, not an explicit operator stop.
Retain the course correction against helper/driver drift while continuing the
original authorized objective under sections12.1-12.3. A peer relayed operator
frustration at inactivity; this does not expand authority or relax any gate.
Fresh root_step1c_v14_resume_readonly_20261021.json verifies unchanged LAP and
Rocket boot IDs, config hashes, AP5235/5225/VHT40/14 context and exact Rocket
WPA/specd identities. Execute the already independently admitted V14 recipe
once, preserve its result, and complete both native restoration checks. No
new driver analysis, helper branch or change of acceptance is authorized by
this continuity correction.


## October21 21:16 UTC - Operator course correction: stop support drift

The operator challenged the duration and action count of the capture/channel
investigation. Coordinator acknowledges poor prioritization: receiving32 stock
Beacons does not demonstrate the requested OpenWrt/stock-CPE interoperability.
V14 final local admission exists but it was NOT_EXECUTED. No active capture,
guard or device mutation remains; both tested units have native restoration
receipts. Existing failed trials and static reviews remain preserved.

Further capture helpers, channel reverse engineering and verifier expansion
are stopped for reassessment. The existing peer was sent an explicit cease-
analysis instruction; a queued transport receipt is not proof it stopped.
Next decision must compare the shortest existing interoperabilty test paths,
reuse working tools, and explain why any acquisition prerequisite is essential
to the parent question before another experiment. No new platform or driver
branch is justified by the current evidence. IE-control and stock-CPE association
remain incomplete; production and other hardware safety boundaries stay intact.


## October21 21:14 UTC - Exact native state restored; V14 frozen before execution

AP verifier V2 completed21:14:05 with PASS_LAP_STOCK_FIRMWARE_CONFIG_NATIVE_
CONTEXT_AFTER_REBOOT. Receipt dcd32c330f0230b99fc1d0518920bcc1e7b833a49ac5f2200affd7c473202506.
All five non-config RAW partitions, runtime/inittab/board, both config banks
and live persistent tree match the accepted own baseline. RAW mtd4 also equals
that baseline, with stable brackets. Watchdog258/start257/FD3, native DFS
parentchain and wired ping passed. This closes V13 native restoration together
with Rocket13; AP RF differs from historical5810/19 and is explicitly recorded
as5235/center5225/40MHz/14dBm. Its selection mechanism remains UNKNOWN.

V14 source CAP b422912d0dd73a21d0a1890faf3dd9733ce04f410091ac1c905c0d8907cb496b;
runner66af2ffd7d1d2440f4e72c866bbd9a46456d90d0e51abce9a8a1d4f17b7d0d89.
Runner pins the fresh restoration receipts and APboot720aa03a/current5235/
5225/14 context separately. Both180s guards precede any RF change. AP requests
1dBm at current40MHz, verifies1, changes to20MHz, rechecks1 and5235/5235,
then requests5180 and requires5180/5180/VHT20/1. Rocket native STA must report
5180/1 before its original-module passive monitor recipe; monitor type802,
noath0,5180/1 are required after preparation and at capture start/end.
One10s/1000frame management capture; one failed gate stops progression.
No explicit scan, DFS/regulatory modification, persistent save or flash.
Complete final independent source admission before execution. Both normal
reboots and native checks (Rocket14 and APV2 attempt2) remain mandatory.


## October21 21:07 UTC - V13 early power failure and V14 positive-power hypothesis

Parent remains FMX0015 PhaseB/C management-IE control before stock-CPE
association with OpenWrt. V13 ran21:02:20-22 and preserved failure
AP_RF_CONTEXT_power_zero_verified. Native AP request txpower0 returned off,
while AP5810/center5820/VHT40 remained. No width/channel setter, Rocket radio
preparation or capture followed. Both independent guards requested normal
reboot. This is not successful0dBm control and not an RX5180 measurement.

Rocket restoration13 passed21:03:37: changed boot21b7aeec-162d-4709-b3bd-
c1cec384c69b; native CRCs, config maps, persistent files, protected bytes and
original modules exact. AP verifier attempt1 hit startup connection failure;
attempt2 reached stock identity but rejected ath1 type802. Preserve both.
Fresh pinned read-only AP evidence shows boot720aa03a-1f50-43ce-b1dd-
208fe5afee68, exact active/running cfg MD55050a8186ee08d7e8739965e94da855b,
Master5235/center5225/VHT40/Tx14, and ath1 Monitor11NAHT20 on wifi1.
The exact held stock dfsprescan script creates this secondary monitor;
baseline health already contains its native processes. Full AP restoration
is still pending a corrected independently reviewed read-only validator.
Do not reinterpret native DFS monitoring as an experiment-created ath9.

Minimum changed hypothesis V14: request1dBm, require exact positive1dBm
before and after each AP width/channel change and each Rocket STA/monitor
stage, including capture start/end. This is a prospective new recipe;
never accept off as0 or1, and do not call1 a proven physical minimum.
Reuse the180s guards, immutable config/regulatory checks, original modules,
finite native STA5180 observation and10s/1000frame passive acquisition.
Starting AP RF must be freshly pinned after native restoration; native RF
variation after reboot is distinct from intentional treatment context.
Stop at any failed gate, preserve result, and verify both normal stock
restorations. No flash or persistent write is part of this diagnostic.
Navigation: GitNexus exposes no FuturaMAX index; exact local paths and held
firmware sources are used, without indexing generated research artifacts.


## October21 20:58 UTC - Measured stock RX and frozen native5180 decision

Parent remains FMX0015 PhaseB/C, management-IE control before stock-CPE
association with the OpenWrt AP. V12 resolves receiver capability in stock
context: PCAP6d119dbc... contains1000 complete records,32 target Beacons and
zero ProbeResponses. Independent parse found32 different sequence numbers.
Actual packet span3.251567s reached the1000-frame ceiling before10s. Capture
reported1000/1010filter/0kernelDrops; this does not mean every received frame
was saved. FCS was not declared/verified. AP5810/center5820/VHT40/Tx19 and
monitor5810/802/noSTA matched before/after. Desired mode stayedAUTO.

Selected beacon metadata is preserved separately: DS/HT primary162 and
Prism itemDID0x30044,status0,len4,value162 in every target Beacon. The observed
stock vendor IE uses OUI002722, not the supplied00156d test IE. These are
received protocol bytes, not a controlled IE comparison or calibrated RF
measurement. Rocket restoration12 passed20:49:47, boot49e23295-e2e6-4ae8-ba70-
8c5e6aa69fba; native banks/maps/files/protected/original modules exact. LAP was
not mutated. The decoder's historical pattern-mismatch counters are expected
for stock vendor IEs and are not the verdict for this RX-only diagnostic.

V13 asks whether the confirmed receiver can operate at5180 using an existing
native AP before another OpenWrt flash. Minimum new treatment: independent
180s guards on BOTH radios before RF changes. AP: request0dBm and verify at
old5810/VHT40; change native mode/bandwidth20 and reverify0dBm and5810 BEFORE
retune; one freq5.18G followed by Master5180/center5180/VHT20/0dBm checks.
All config files and native regulatory settings remain byte-exact. Any failed
power/context gate aborts without advancing to the next RF change.

Rocket: native WPA/specd remain running with exact PID/start identity. Set
and verify0dBm before narrowing ath0's channel list to5180. Read back exact
allowed list. No explicit scan command; observe up to11 times over10s for
native Managed5180/0dBm. This is not association acceptance. Only then perform
the reviewed original-module monitor recipe, require MON802/noSTA/5180/0dBm,
and take one passive management capture with unchanged10s/1000frame bounds.
AP snapshots bracket the capture; receiver end check and offline decoder
remain mandatory. Same target-Beacon/ProbeResponse positive/INCONCLUSIVE
interpretation, now in stock5180 context. Both normal guarded reboots and
full native restoration (APattempt1, Rocket13) close the treatment.

Park at the first failed gate and preserve it. No guessed driver order,
patched module, custom MAC work, Loco mutation, persistent write or flash.
This necessary acquisition step does not accept IE control/OpenWrt association.
Two exact sources are prepared, independently reviewed before execution;
the AP postreboot validator is prepared separately and must also pass review.

## October21 20:49 UTC - Frozen V12 matched-channel RX acquisition and interpretation

Question: does original Rocket monitor receive management frames from the
existing stock AP when both report the same primary5810? This resolves a
necessary receiver-capability uncertainty without AP mutation or flash.

One fixed treatment uses V10's original-module/native-daemon-running recipe,
with desired/requested and required reported5810. It records get_mode before
and after UP; no COMMIT. Three pinned read-only AP snapshots require same
native boot, BSSID18:e8:29:74:55:a2, primary5810/center5820, VHT40, Tx19 and
unchanged config. Rocket must show Monitor802/noath0/5810 before capture and
after export. One10s passive management capture uses existing limits1000
records, snap2048, buffer64KiB and total2064024bytes. No injection or AP/CPE
association attempt. Capture stop preserves output when the owned process
has disappeared normally; reused identity must never be signaled.

Reuse root_step1c_ie_pcap_analysis_20261021.py decode_segment only, whose strict
container/header/complete-frame/IE parser classifies exact target TA+BSSID.
Do not use the three-phase IE verdict on stock traffic. At least one complete
valid target Beacon or ProbeResponse supports CONFIRMED_RX_IN_STOCK_CONTEXT;
report FCS and drop-counter limitations explicitly. Zero target frames or
malformed/unsupported input remains INCONCLUSIVE, not proof of inability.
All historical failures remain separate. Always request Rocket's guarded
normal reboot and verify full restoration12. The AP remains read-only.
Independent source review precedes execution of the two new pinned scripts.

## October21 20:44 UTC - V11 negative, complete restoration and actual stock-pair state

V11 ran20:34:21-23: module refcount0, original unload/reload, MON802/noath0,
flags0x1043 at first observation, one COMMIT rc0. Both before/after getters
reported5810. Bitrate changed0 to450 but this is not RF/receive evidence.
Native WPA650/start2970 and specd661/start3118 remained S. Preserve failure
MONITOR_OR_FREQUENCY_MISMATCH. No AP or PCAP used. Restoration11 passed
20:35:47, bootdf93bb99-a784-4bce-9c95-f4c8e29676a9, both native bank CRCs/maps,
persistent files, protected regions and original modules exact; no monitor.

Further exact-source review excludes reset overwriting desired on this OL
path: the three registered reset callbacks are no-ops, and reset type2 does
not reset each VAP. No mode/slot overwrite was found in reviewed monitor
branches. Desired-channel cause remains UNKNOWN; do not repeat setter order
based on that refuted reset hypothesis. Native get_mode reads desired mode,
but no native CLI getter of the desired-channel slot is yet established.

Fresh pinned read-only pair snapshot is
root_step1c_native_pair_channel_readonly_v3_20261021.json. LAP stock boot
28f414ba-9a05-4be1-bab7-6b49ea909003 reports AP5810, center5820, VHT40 and
Tx19dBm; Rocket reports SCANNING5830/no association. A historical peer-delete
line cannot establish association. Initial stale IPv4/ethernet-IPv6 routes
timed out; observed native bridge IPv6 endingfe74:55a2 succeeded with exact
stock SSH identity. These route failures did not mutate either device.

Minimum next question: can original Rocket monitor receive complete target
Beacons at all when its reported channel matches the currently transmitting
stock AP? Existing V8 captured zero with AP5180 versus monitor5165, so that
mismatched-channel result does not answer this question. Prefer one bounded
matched-channel passive capture with read-only AP snapshots, mandatory Rocket
normal reboot/restoration12, and independent recipe review over new AP retune,
WPA configuration or another flash. This diagnostic would not qualify5180,
IE control or OpenWrt interoperability, and would not rescore old failures.

## October21 20:34 UTC - Source-bound COMMIT hypothesis and frozen V11 acceptance

Parent remains FMX0015 PhaseB/C: management-IE control for an OpenWrt AP and
association by an unmodified stock CPE. The missing prerequisite is a qualified
stock receiver at5180; V10 measured5810. No AP, PCAP or IE changes are in V11.

Correct ELF symbol/relocation review of UMACec1df9... binds SIWFREQ98990..98dfc,
COMMIT9aa08..9aab8, and monitor start33d60..33e40. COMMIT requires UP|RUNNING,
then osif_vap_init routes monitor to wlan_mlme_start_monitor. That function
reads the same desired slot as getter106c and setter177c; at33ddc it calls
ieee80211_set_channel, whose dbc indirect call reaches the driver callback.
It ignores that result, so successful command return is insufficient evidence.

V11 keeps V10's original-module and native-running-daemon recipe. After UP,
record the pre-COMMIT getter and at most four interface-flag observations
separated by three one-second waits. Require actual UP|RUNNING, MON802 and
no ath0 before exactly one iwconfig ath9 commit. Acceptance is the separately
marked post-COMMIT Monitor802/getter5180/noath0 plus unchanged native-process
identity. Any failed gate stops. Always request the existing guarded normal
stock reboot, then complete native/protected/module/persistent restoration11.
No patched module, global-mode override, forced unload or persistent write.
Independent review precedes execution. A reported channel does not prove RX.

## October21 20:25 UTC - V10 measured result and corrected static-analysis boundary

V10 ran20:21:22-24. The first module reference sample was zero; one original
poll unload/reload completed. Monitor802 reported5810MHz (center5810), despite
AUTO,20MHz,list5180,freq5.18G before UP. WPA652/start3071 and specd690/start3248
were S afterward. Preserve MONITOR_OR_FREQUENCY_MISMATCH: this treatment did not
qualify5180 and does not test whether a nonzero count would drain. No AP or
PCAP was used. Full stock restoration10 passed20:22:47, boot
596eb944-fab3-4c67-aba5-13b04cc6f55f, native/protected/module/persistent checks exact.

Independent static review found that the helper labeled92f0c..93118 SIWFREQ,
but those offsets fall inside ieee80211_ioctl_getparam in exact UMACec1df9... .
Its ELF symbol section filter uses st_other(index4) instead of st_shndx(index5).
Therefore exclude that mislabeled export from frequency-setter conclusions.
The minimum active work is to bind the actual setter and monitor-start path
against exact symbol/relocation data before selecting another RF treatment.
Do not repeat a setter-order guess, reinterpret historical success as current
qualification, or leave restoration marked pending: both radios are stock now.


## October21 20:19 UTC - V9 reference gate stopped safely; bounded drain hypothesis

V9 ran20:15:36-38. Native WPA651/start2987 and specd662/start3142 were S.
After removing ath0, ubnt_poll_host showed refcount2, so the existing gate
stopped before rmmod, insmod or monitor creation. It did not measure monitor
frequency. The exact historical14058 output contains no visible insmod error,
but rmmod return code remains unknown because that script silenced it. Do not
infer a successful reload, a failed reload, or the owner of those two references.

Rocket restoration9 passed20:17:16: original modules/protected regions, both
native banks, config and persistent files exact; no monitor. Boot
af13eb87-a521-4b15-af33-5a15d223cbbe. LAP remains own stock and is not involved.

Minimum changed hypothesis: native users may release module references
asynchronously after STA destruction. One V10 sample uses at most four
read-only refcount observations separated by three one-second waits. Only
actual zero permits the original single rmmod; a nonzero/invalid count aborts.
There is no forced unload, repeated unload, arbitrary delay until green or
acceptance reduction. All original identity/process/RAM/guard/RF-order gates
remain. This is still one reported-channel check with mandatory stock reboot
and restoration10, not an AP, PCAP, IE or association experiment. Independent
review and a bounded-count fixture precede execution.


## October21 20:12 UTC - Exact historical source reveals one isolated process-state difference

The bounded full transcript extraction links write14055, run14057 and Monitor
5180 output14058 to source0721050fef22f5f7616fe3722e2e4fe04e024b56b533d51b1d9d81b427976e20.
The prior missing source/command link is now resolved. Loaded-module provenance
before that historical sequence remains unknown. Safe extraction artifact:
`artifacts/canary_panel1_guarida/rocket198_first5180_safe_commands_20261021.json`.

The exact historical recipe contains no WPA STOP/CONT/TERM/DISCONNECT. Root V2
used the same RF order but suspended WPA before deleting STA. V6/V7 native
DISCONNECT attempts stopped at the STA preseed gate before any monitor existed;
they do not answer this process-state difference. No cause is inferred yet.

Minimum next treatment: Rocket only, native WPA and specd left running, same
original-module unload/reload with refcount zero, AUTO/channel-list/frequency
request before monitor UP, all identity/boot/PID/memory/guard gates retained.
Require ath0 absent, actual Monitor type802 and reported5180. One attempt, no
AP enable, PCAP, IE change, patched module, global-mode change or injection.
Stop at the first failed gate and perform guarded stock reboot plus complete
restoration9 regardless of channel outcome. A positive getter alone is not RX
or the parent IE/association acceptance. Independent review precedes execution.


## October21 20:06 UTC - Own-stock return completed; preserve the actual research gap

LAP own-stock return completed20:03:57 with
PASS_LAP120_OWN_STOCK_RETURN_EXACT_RAW_AND_STATE_V2. Receipt
`artifacts/canary_panel1_guarida/root_step1c_bench_cycle_20261021_return_own_stock_after_cache/receipt.json`
SHA25605d7b34e134c9ae0598721b67250ad80fcede0da5e78824a46e80e637aa66383.
The cache preparation yieldedMemFree32880KiB against unchanged17768KiB requirement.
The original driver independently rechecked memory before/after upload, validated
and decoded the exact16121856-byte own image92a5986b..., and sent one sysupgrade.
Transport exit246 was preserved; later complete stock verification settled it.

Raw partitions0,1,2,3,5 match the own baseline exactly; native config v2 passed
active/running maps, both bank trees, headers, persistent metadata/content and
validated padding. Native bank roles swapped reciprocally; raw config-partition
bytes are therefore NOT equal, as explicitly allowed by the frozen v2 criterion.
Stock watchdog ownership, management callback, board, binaries and inittab passed.
No force, automatic flash retry or power action occurred. The earlier memory
preflight failure remains unchanged. Rocket restoration8 was already fully
verified; no Loco195 mutations occurred during the Rocket attempts.

Research decision remains INCONCLUSIVE/NOT_ACCEPTED: no qualified observer RX,
Beacon/ProbeResp IE appearance-removal, or OpenWrt-to-stock-CPE association.
A ten-second tcpdump log with zero frames plus missing PCAP is not evidence of
physical impossibility. Do not repair or repeat that helper merely to obtain a
green acquisition receipt.

Minimum next evidence is a bounded reconstruction of the historical first
MON5180 success: exact command arguments plus the actual loaded-module and
initialization state before that success. The held summary has14054 STA5165/
MON5165 then14058 MON5180, but stores tool names without arguments/source hashes.
Earlier patched poll/opmode0 evidence does not establish continuity or cause.
A current script that reloads a disk path does not prove which module bytes
were resident at the historical success. Two fresh-stock observations that
differ from it do not reproduce that unknown initial state.

A local read of only the corresponding full-transcript entries is active; stop
that extraction if the exact records cannot be resolved. No new RF window,
firmware cycle, speculative setter or production action is scheduled without
new evidence establishing a distinct necessary treatment. The original goal
remains FMX0015 Phase B/C; device restoration alone does not accept that goal.


## October21 19:58 UTC - RX diagnostic inconclusive; complete the own-stock return

Parent remains FMX0015 Phase B/C, OpenWrt AP management-IE control and stock-CPE
association. The separate prospective diagnostic ran19:52:14-39. Rocket monitor802
reported5165MHz; AP readiness verified5180/VHT20/0dBm. tcpdump log reports
PRISM_HEADER, zero captured/received-by-filter/dropped packets and a24-byte file.
After SIGINT, an awk read raced the exiting PID4155. The strict stderr guard
stopped export; no local PCAP and no final AP snapshot exist. Preserve the original
exit1 as FAILED_ACQUISITION / RX_INCONCLUSIVE. This neither proves reception
nor impossibility, and does not rescue frequency, IE or association acceptance.
Independent evidence review agrees no unchanged repeat is warranted.

AP restoration passed with radio off, exact wireless file, empty UCI deltas and
ended guard. Rocket restoration8 passed19:54:07: native both-bank CRCs/keymaps,
persistent files, protected regions and original modules exact; monitor absent;
new boot95592726-f2a0-4785-bb8b-c5f9090e0121. The known192.168.100.198 address
was restored in RAM only; native stock still retains its original address.

The required LAP own-stock return was attempted19:54:23 and stopped BEFORE
upload, directory creation or handoff: MemFree15704KiB versus required17768KiB.
The package is9804856bytes and the unchanged reserve8192KiB. Original receipt
root_step1c_bench_cycle_20261021_return_own_stock/receipt.json is preserved as
FAIL_BEFORE_OWN_STOCK_HANDOFF, sysupgrade_requests0, handoff_attemptedfalse.
LAP remains the candidate with radio off until the actual return succeeds.

Minimum necessary recovery: one pinned identity/boot/radio-off-gated sync and
drop_caches1, then apply the original memory_guard to fresh measurements.
Sync may perform ordinary dirty-page writeback; cache release does not change
flash acceptance or substitute Cached/MemAvailable for measured MemFree.
Only if that original guard passes, reuse the frozen return driver with a new
exclusive output directory. No force, reserve reduction or automatic retry.
This recovery is under independent source review before execution.


## October21 19:47 UTC - Prospectively separate RF reception from reported frequency

V7 confirmed native DISCONNECTED, then STA frequency stayed5520 despite list5180.
The gate stopped before destroying ath0. Full guarded stock reboot/native/protected
restoration passed (after_capture7), boot62f4506a-b713-4135-b379-c50b2143d3cb.
The native-disconnect/preseed route does not qualify frequency; preserve its FAIL.

Parent remains FMX0015 Phase B/C IE control. Per outcome-first priority, stop
guessing additional frequency setters. Independent review admits one distinct
passive-RX diagnostic: reuse known monitor creation, record its actual getter,
require ModeMonitor/type802, no remaining STA, owned WPA STOP, and all original
identity/guard/RAM limits; then arm the unchanged AP5180/VHT20/0dBm/regulatory
window for a single10s target-filtered capture. No IE toggle, injection, association
command, global-mode/regulatory change or CPE mutation. AP off and Rocket stock
reboot/native restoration remain mandatory.

Fixed diagnostic criterion: a complete valid received Beacon with TA=BSSID
18:e8:29:74:55:a2 during the verified AP-ready window establishes reception of
that AP despite the discrepant getter. Record Prism/channel and DS/HT/VHT IEs
without assuming agreement. Zero target Beacons is INCONCLUSIVE, not impossibility.
This DOES NOT qualify receiver-reported5180, rescue V2-V7, or accept the original
Beacon/ProbeResp IE appearance-removal experiment or stock-CPE association.


## October21 19:41 UTC - Native DISCONNECT confirmed; BusyBox parser fixed

V6 returned native OK and four observed DISCONNECTED states, but unsupported
BusyBox grep-x made the poll fail before STOP, preseed, destroy or AP changes.
This is a helper compatibility failure, not a failed radio preseed. Preserve
stdout/stderr and exit1. Stock reboot and complete native/protected restoration
passed (after_capture6), bootc0de0df2-b1fc-4bdb-bf7f-9e5e68f3de37.
The only behavioral V7 repair uses supported grep-q with anchored BRE for the
exact state line. Same physical hypothesis, gates and restoration; refreshed
boot/process/output bindings. Add negative actual-option regression before use.


## October21 19:36 UTC - Separate native scan state from channel-list setting

V5 measured ath0 Managed/5685MHz before and after the single frequency request;
athchans-g showed only5180. The gate stopped before detach/down/destroy, so no
monitor or AP mutation occurred. Guarded stock reboot and native/protected/config
checks passed (after_capture5), bootcd5c09cc-ffab-4131-a376-68ffddc55659. Preserve FAIL.
Fresh read-only wpa_cli status shows SCANNING; /usr/sbin/wpa_cli and its existing
/var/run/wpa_supplicant/ath0 socket are present. Exact held native CLI implements
DISCONNECT; no ABORT_SCAN support was found, and none will be invented.

Same parent FMX0015 IE-control measurement. Minimum next hypothesis: ask the
running native WPA once to disconnect, require exact OK and observed DISCONNECTED
with at most3 sleeps/four reads, then revalidate exact process ownership before
applying STOP/STA preset and separate5180 gates. SSH/socket limits and the180s
guard bound uncertainty; the poll is not a strict3s wall-clock deadline. This
measures whether stopping active scanning allows tuning; it does not assume that
WPA state proves firmware scan cancellation. Reject on state/frequency failure
and perform the existing guarded stock reboot. No new mode/global/regulatory,
persistent-config, CPE, fallback setter or retry changes. Independent review
checks this exact delta; OTA/association remain INCOMPLETE until physical evidence.


## October21 19:29 UTC - Verify STA frequency before monitor inheritance

Parent remains FMX0015 / forward-plan Phase B/C management-IE control and stock
CPE association. V4 explicit11ACVHT20 also returned5165MHz. V2 already used the
exact AUTO/chanbw20/athchans5180/freq5.18G/UP order cited by the operator and AGY;
therefore an order-only explanation is REFUTED by that attempt. No AP was armed
in any Rocket attempt. Preserve all failures. V4 first restoration SSH connect
timed out during reboot; a separate completion passed both native CRC/keymaps,
all persistent bytes/metadata, protected partitions and original modules.

Fresh stock readout: ubnt_op_mode1/is_ubnt_ptp1, wifi0 chanbw20, ath0 AUTO, channel
list beginning5165; no mode/global/regulatory change. Historical AGY success
followed other radio treatments, so its self-contained reproducibility is unproven.
New operator hypothesis: monitor inherits radio state established while ath0 is
STA. After WPA STOP, before ath0 down/destroy, set radio width20, restrict ath0
channel list5180, request ath0 frequency5.18G once, wait1s, and require observed
Managed/5180. Only then destroy/reload/create and independently require monitor
5180. Instrument before/after STA and exact monitor block so a STA5180 string
cannot accidentally satisfy the monitor gate. Other V4 controls and guards stay.
Stop on either stage failure; no repeated setter, umac global-mode mutation,
persistent change or CPE mutation. Qualified mode inheritance remains UNKNOWN
until actual observed values; it is enabling evidence, not IE or association PASS.


## October21 19:21 UTC - Post-UP timing rejected; explicit VHT20 mode next

V3 repeated5165MHz in both Frequency and Center1-Freq after a single post-UP
request plus1s, so timing alone did not qualify5180. No AP mutation/PCAP.
Guarded stock reboot and native/protected/config restoration passed; latest
boot5b1ada86-090e-4821-b05b-2d68a45e67ed. Original V3 failure remains preserved.
Minimum new hypothesis for the same FMX0015 IE measurement: substitute only
monitor mode AUTO with explicit11ACVHT20, as present in held AGY sources; retain
all other tuning, request count, frequency gate and restoration limits. Source
precedent is not RF proof; cause of5165 remains UNKNOWN. Stop before AP on any
mode/frequency error. No extra retry/setter, stock CPE mutation or persistent write.


## October21 19:17 UTC - Rocket monitor admitted; tune-after-UP hypothesis

Parent remains FMX0015 / forward-plan Phase B/C AP management-IE control and
unmodified stock-CPE association. Rocket V1 failed ordinary rmmod with EBUSY
after stopping WPA and specd. The original cause remains UNKNOWN. V2 kept specd
running, checked poll refcount0 and successfully reloaded the original module
and created monitor ath9/type802. It nevertheless reported5165MHz after the
pre-UP5180 request, so acquisition stopped before any AP mutation. Preserve both
failed receipts; neither contains an OTA capture.

Each attempt completed its guarded normal stock reboot. Fresh restoration
receipts after_capture1 and after_capture2 verify both native CRC/keymaps, all
persistent file bytes/metadata, protected partitions and original modules.
Latest Rocket boot6ee31e20-c535-4d69-ac1e-60736ddcb82c; .198 restored in RAM via
pinned wired IPv6, native .1.20 retained. No flash/config persistence was requested.

Independent source comparison found the AGY preset uses the same pre-UP order;
repeating it adds no evidence. Minimum next treatment moves the single frequency
setter immediately after UP and waits one second before reading; source precedent
exists for post-UP tuning but does not prove runtime success. Fixed acceptance
remains monitor/type802 at5180, same AP BSSID/ifindex and absent/present/absent exact
IE in Beacon and ProbeResp. Stop on mismatch, guard/reboot and verify restoration.
All other watchdog, native/identity and acquisition bounds remain unchanged.
Association and mandatory LAP own-stock return remain outstanding.


## October21 18:59 UTC - Independent Rocket observer replaces Loco monitor acquisition

Parent remains FMX0015 / forward-plan Phase B/C: AP management-IE control and
association of an unmodified stock CPE. V3 and V4 monitor failures remain failed.
V4 captured the kernel rejection after ath0 deletion; exact held WA/XC modules
confirm the poll hook rejects monitor WMI type4 when the registered radio state
is nonzero. The same error string also exists in the offload path; it does not
identify the legacy driver. See root_step1c_poll_hook_static_review_20261021.json.

V4 AP immediate teardown check failed RADIO_VAP_REMAINS. A separate pinned,
read-only completion confirmed no VAP, radio disabled, exact config, empty RAM
deltas and ended guard; the original failure is preserved. Loco normal reboot
returned boot d66cd71d-8d38-4469-8832-45c9438a5252. Complete native-bank read
verified CRCs, config maps and persistent files (only two directory mtimes differ).
Two unchanged-checker observations passed at332.09 and456.95s, delta124.86s:
original module, no custom cron/bind, protected hashes and stable native services.
This is restoration evidence, not physical power-cycle or RF acceptance.

Operator/Antigravity now ceded Rocket198 exclusively to Codex. Fresh pinned SSH
intake matches XC8.7.25/sysid e7e9, stock module hashes and the supplied boot.
/proc/sys/dev/uph_wifi0 exists with enable1; absence of wifi0 in the parent
/proc/sys/dev/uph listing did not establish an empty registry. The changed
hypothesis is original-module reload without registration on the Rocket only.
Loco remains a stock STA. Rocket .198 is RAM-only; both native config banks retain
.1.20. Pinned IPv6 wired access was independently qualified for reboot recovery.

Fixed acquisition: one bounded AP window at5180/VHT20/0dBm; vendor IE absent,
exact operator-supplied dd1900156d0107000102030000000000270007e602040000000000
present, then absent; same BSSID/ifindex throughout. Separate independent Rocket
PCAP segments avoid cross-device clock assumptions. Require untruncated target
Beacon and ProbeResp evidence in each phase; absent ProbeResp remains INCOMPLETE.
No firmware patch, persistent write, or Loco monitor mutation is part of this
measurement. Rocket normal reboot and AP off restoration are required afterward.
LAP own-stock return remains mandatory after bounded acquisition/association.
Stop/park on unsafe recovery or a qualified missing RF observer; retain failures.


## October21 18:19 UTC - Native CPE restoration accepted after normal reboot

Parent FMX0015 / forward-plan Phase B/C remains AP management-IE control and
unmodified-stock-CPE association. One native user-scope cron disable was persisted;
a fresh read-only completion verified the write despite the final redundant raw
export transport failure. No second cfgmtd write was requested. One normal stock
reboot followed; this is NOT a physical power-cycle recovery qualification.

The first byte-exact observer failed because raw4 changed. A separate complete
read recovered all32 chunks and validated both CRCs and both133-key configuration
maps against the disabled candidate. Both banks preserve all persistent file
bytes and metadata. Only the active archive's two directory mtimes differ
(persistent and persistent/https:5 to4 seconds); the original exact-tree failure
is preserved. The cause of the raw rewrite remains UNKNOWN; do not claim the
shutdown script saves unconditionally. Independent review accepted this separate
logical-state qualification without rescoring either failed receipt.

Fresh observations1 and2 under root_step1c_cpe_user_disabled_observation_v3_*
passed the unchanged checker, same boot and uptime delta>=120s: cron absent,
original polling module/no bind, stock protected partitions, identical config
keymap/raw4, canonical shutdown entries and stable crond/WPA/ubntspecd identities.
This establishes restored native CPE state, not RF interoperability.

Minimum remaining measurement: one reviewed sole-monitor capture with fresh
boot/PID/ifindex/hash bindings and phase/exit diagnostics before guarded reboot.
Do not repeat an uninstrumented failure. AP stays bounded at5180/VHT20/0dBm and
returns radio-off; reverify CPE after the treatment. Independent Beacon/ProbeResp
IE control and association remain INCOMPLETE. LAP own-stock return is mandatory
at the end of this bounded acquisition; future firmware qualification remains a
release requirement from the section below.


## October21 - Operator requirement: qualify compatibility before firmware upgrades

The operator explicitly asks whether the system will keep working across newer
firmware releases. Current exact-version/hash guards provide rejection of unknown
builds; they do NOT demonstrate forward compatibility. Preserve this distinction.

Release requirement for the FMX0015 AP/stock-CPE outcome: keep CPE firmware and
modules vendor-stock, with no version-specific binary offsets or legacy custom
cron as a product dependency. Maintain tested hardware-revision/AP-build/CPE-
firmware tuples. A new airOS or OpenWrt/hostapd build remains UNQUALIFIED until the
same management-IE, authentication/association, reconnect/reboot, persistent-config
and performance/stability checks pass on the bench. Source-level AP integrations
must be rebuilt/reviewed when their dependencies change. Test absence/reactivation
of legacy CPE jobs and restore paths explicitly across an upgrade.

Unknown builds must not receive unqualified experimental mutations. Future rollout
requires a qualified canary and a usable return to the last accepted image/config;
backup existence alone does not qualify rollback. No automatic production upgrade
or compatibility guarantee follows from this requirement. This is an explicit
future release criterion, not a new prerequisite that parks the current baseline.

## October21 17:48 UTC - CPE cold boot exposed native cron-generation defect

V2 short-command staging passed. Sole-monitor execution reached the armed reboot
guard, then failed before exporting frames; no phase-specific error survived its
RAM-only logs. The CPE rebooted and wired access returned. AP restoration passed.
The independent postboot validator FAILED: the identical custom cron regenerated
and bind-mounted a patched polling module despite job.status=disabled. Config
key/value maps are unchanged; firmware/protected raw0/1/2/3/5 hashes match. Do not
claim clean stock or resume RF acquisition from this failed restoration.

Exact native ubntbox analysis confirms job-status lookup on a schedule-only list,
which falls back to enabled. The user-scope status is read from the full config.
Minimum repair: disable ONLY cron.1.status for the sole custom-job user, retaining
all other configuration and native cfgmtd validation. Root holds the exact job's
RAM mutex; preserve it until cache acknowledgement and the guarded clean boot.
Require cold-boot native user-crontab absence/emptiness, original module/no bind,
unchanged protected state and no reactivation over two cron intervals. Failed
postboot and capture receipts remain failures. LAP radio off; own return pending.

## October21 17:30 UTC - Sole-monitor transport rejected before execution

The paired sole-monitor attempt sent9027 bytes and SSH closed before any command
output. Fresh wired diagnosis proves the same boot, ath0 ifindex and WPA process;
the owned remote directory is absent and no new radio action appears in dmesg.
AP radio/config restoration passed. No sole-monitor treatment or CPE reboot is
claimed. Failed artifacts remain under root_step1c_sole_acquisition_20261021.

The minimal necessary repair stages the unchanged reviewed treatment in exclusive
RAM using short verified chunks before the AP window, then executes a short path.
No chunk or treatment is retried after ambiguous delivery. Capture, boot guard,
independent stock postboot acceptance and mandatory LAP own-stock return remain.
Parent decision and Beacon/ProbeResp acceptance are unchanged.

## October21 17:04 UTC - Paired passive capture negative; sole-monitor intake accepted

The8s wifi0 capture with measured5180/VHT20/0dBm AP on returned0 matching frames;
capture, local export, exact state, owned cleanup and wired-route restoration
all passed. AP returned to radio-off/config unchanged. Receipt:
root_step1c_main_capture_ap_on_20261021/receipt.json under canary_panel1_guarida.

Minimum remaining evidence requires a sole main-radio monitor. Fresh wired
intake matches held cron-OFF native config, own protected partitions and current
inittab; all six raw partition hashes recorded, dangerous shutdown flags absent.
Prospective treatment: independent timed stock reboot before station detachment,
exact WPA suspension, sole monitor on5180, bounded receive/export, stock reboot
restoration. Verify bridge management identity before detaching the station port.
No persistent configuration/module/firmware change on the CPE. Accept logical
stock identity/config/protected state after a new boot; old PIDs and ifindices
are expected to change. Stop on identity or restoration failure. RF IE acceptance
is unchanged. LAP own-stock return is still pending.

## October21 16:55 UTC - Follow measured driver limit, preserve simple capture route

Reject further concurrent-VAP retries on this runtime: exact driver reports one
supported VAP. Prioritize passive wifi0 acquisition paired with actual OpenWrt
AP-on before replacing the station. Exact UMAC mode ioctl only validates an
already-matching mode, so down/mode-monitor/up is not a supported conversion.
A sole-monitor treatment, if necessary, must prospectively define its own
restoration including changed ifindices or cleanboot; never reinterpret the
failed concurrent attempt as success. RF frame acceptance is unchanged.

## October21 16:34 UTC - Use the booted bench image for the pending control test

The reviewed773f2e28 image boot passed with radio disabled and exact protected
state. Continue the bounded observer/IE acquisition on this boot, then perform
the mandatory own-stock return. A separate flash just to recreate the same
unmeasured radio window is unnecessary. Use0dBm for receiver qualification;
retain countryAR/channel36/VHT20 and verify effective regulatory state. No
performance or unmodified-client acceptance follows from the successful boot.

## October21 16:24 UTC - Reuse qualified management paths

Keep CPE on Omarchy: its existing wired route is sufficient. Test passive main
wifi0 capture before changing mode. Preserve frozen LAP stock IPv4 source binding
and candidate IPv6 identity checks; fresh stock callback/link-local evidence
removes the reason for a new transport implementation. The operator's14:21 bench
authorization covers necessary reviewed bench cycles; no renewed per-step ask.
It does not relax protected-partition, recovery or production boundaries.

## October21 14:27 UTC - Stock preparation executed and verified

CPE195 cleanup V2 passed: one native cfgmtd status-only write, active persisted
job disabled, sole runtime cron entry removed and existing crond notification
consumed. Same WPA process and association were retained; protected partitions,
module bytes, mounts and inittab matched. No CPE reboot. The first attempt stopped
before mutations because its ls parser rejected padded columns; both receipts
are preserved, with actual-output regression in the corrected16-test fixture.

LAP120 then completed one normal stock reboot and fresh strict acquisition:
PASS_ONE_STOCK_REBOOT_AND_STRICT_BASELINE, exit0. The expected RAM LAB profile and
generated inittab disappeared. Live/running config now matches persisted stock;
all five raw firmware/protected partitions and runtime binaries match, canonical
inittab restored and strict V2 comparison passes. No LAP cfgmtd or firmware flash.
Fresh baseline receipt SHA256:
`dc53a3577616bff743c01cc34a6ad8870f9768ea3c035f3486548879259dc29c`.

Next within the now-authorized bench work: direct wired access to CPE195 after
the operator's proposed cable move to10XP, then verify whether the primary5GHz
radio can serve as a temporary monitor for AP-only IE qualification. The failed
auxiliary capture does not prove the NanoLoco is unsuitable. Main-monitor support
is advertised by exact stock CLI; concurrency and useful received frames remain
unmeasured. Restore/clean-boot the CPE before claiming unmodified-client results.
In parallel, prepare only fresh bench-image boot/return bindings to the proven
engines. No production operations; no OpenWrt acceptance or improvement claimed.

**Operator authorization,21Oct14:21 UTC:** all necessary isolated bench tests
are authorized. Continue reviewed cfgmtd/reboot/flash steps without asking for
renewed permission for each action. Exact target, recovery, regulatory and
protected-partition safeguards remain; production is outside this authorization.
The initial CPE cleanup stopped before any write on a BusyBox ls-spacing parser
bug; its failure is preserved and a narrow corrected attempt is being prepared.

## October21 14:09 UTC - Park unqualified observer; preserve exact preparation gate

Keep auxiliary capture V2 as INCOMPLETE/NO_FRAMES_CAPTURED despite successful
restoration. Do not infer absence of Beacons or a hardware capability limit from
that negative acquisition. Park this observer path pending new evidence; missing
RF observation blocks IE acceptance, not independent stock-state preparation.

Resolve LAP volatile-state drift by one explicitly authorized normal stock
reboot rather than cfgmtd. Before losing AP association, disable the CPE's known
custom cron using its independently reviewed status-only native configuration
write and runtime notification. Preserve all other CPE state and verify it.
The first helper cannot claim a pristine loaded module; the second must reject
firmware/reset/save shutdown flags and reacquire the unchanged strict baseline.
Both require exact user authority; neither permits OpenWrt flashing. Keep old
single-use locks and failed evidence unchanged.

## October21 13:38 UTC - Preserve persisted stock and explicit volatile state

Retain the fresh live-state acquisition as INCOMPLETE. The narrower persisted-only
V2 comparison passes, with five RAW partitions and three runtime binaries equal
to the qualified baseline; it is not a substitute for the failed live-state
check. Resolve the deliberate RAM LAB configuration and generated inittab
duplicates explicitly in the prospective admission/return recipe. Do not issue
cfgmtd just to make a pre-existing validator accept a temporary state.

Accept the bench image only as a local preparation artifact: two changed config
files, radio disabled, exact extracted inventory preservation and unchanged
kernel/tail. Retain the user's explicit flash/reboot confirmation gate. Existing
airview1 is the preferred bounded capture candidate after its Prism DLT result;
require actual frames and restoration evidence before relying on it for IE tests.

## October21 12:52 UTC - Admit measured wired management only

Latest operator confirmation establishes current physical bench recovery
availability. Resume reversible preparation without requesting that fact again.
Use a bench-only candidate: the held image's production SSID/IP are inappropriate
for this acquisition. Preserve working flash/return cores, qualify exact new
bindings, and present the concrete irreversible operation at the existing gate.

Accept the explicit Ethernet-scoped pinned SSH receipt125207 as authenticated
management of the running Loco195, with temporary state restored. It resolves
the missing wired management dependency; it does not establish power-cycle or
failed-boot recovery, pristine CPE state, Step1C or final interoperability.
Preserve all failed acquisitions. Keep server forwarding policy unchanged; the
successful path uses Omarchy's ordinary SSH client with strict isolated pinning.
Park further transport refinement. Resume the parent AP control/timing question
before selecting a bounded radio treatment or changing CPE configuration.

The bounded control review identifies reusable hostapd IE APIs but no qualified
RF/auth ordering barrier. Test the existing AP control first; do not create a
new custom-auth implementation before that control is measured. The19Oct normal
LAP cycle does not prove failed-boot recovery or authorize a new destructive
attempt. Operator recovery availability is now confirmed; use the fixed
prospective test in root_step1c_control_boundary. Legacy CPE cron preparation
still requires its exact guarded recipe before the dependent AP trial.

## October21 04:28 UTC - Accept explicit handoff and retain recovery gate

Accept AGY's explicit handoff `msg_a570c761f5ac` as coordination ownership,
not evidence of a successful experiment or current synchronized device health.
Codex is the sole prospective device writer. Preserve the failed access probes;
do not change radio state while independent wired recovery is unavailable.
Ask only for local Omarchy diagnostics needed to resolve access. Continue the
bounded review of whether Step1C has an implementable AP control, rather than
repeating the failed treatment or treating static analysis as acceptance.

## October21 04:18 UTC - FMX0015 continuation boundaries

Continue the operator-authorized bench objective with AGY as the current device
writer and Codex as read-only reviewer/coordinator. A provider block does not
justify hiding operations or bypassing controls. If AGY cannot proceed, preserve
its latest state and transfer ownership before Codex makes any device changes.

Retain Step1B as `NEGATIVE_OR_INCOMPLETE_RESTORED`. Treat Step1C's static theory
as unverified on the exact target until module provenance and physical evidence
support it. Require the prospective recipe and restoration path before a new
treatment. Ethernet carrier/MAC learning alone is not independent recovery, and
an existing CPE cron is incompatible with claiming a pristine zero-touch setup.
The final deliverable still requires an OpenWrt AP and unmodified stock CPE with
association and bidirectional IP; an intermediate stock-AP test cannot close it.

## October20 22:34 UTC - Gemini incident review; STA61 clarified by operator

Operator requested forensic review of the Gemini session after the whole
Guarida POP lost service, specifically asking whether its STA or PoE was touched.
The operator confirms10.10.100.61 is the STA. This review is complete for the
incident window19:00-19:30:42ART; actual service recovery remains NOT ACCEPTED.

47 command invocations, script bodies, task logs and transcript outputs reviewed.
Confirmed: AP84 mutating trial launched19:03:19, failed with timeout and no proven
restoration. An accidental import19:05:31 retried the CPE connection but failed
before further writes. Panel83 killall dbclient attempted19:16:53, outcome unknown.
Router1 queries were print-only; STA61 first query failed local shell parsing,
second failed TCP connection before authentication. No STA61 config/reboot or
PoE write was found in this bounded incident window. Older19Oct bench ES10XP90
PoE operations are separate evidence, not a current Guarida power-cycle receipt.

AP60 logs confirm peer61 Airmax carrier lost. They do not prove power loss,
OOM or watchdog reboot. Device log clock is unsynchronized; dmesg993271 is the
AP60 monotonic timestamp, not STA61 uptime. Loss of the operator-confirmed PTP
entry explains downstream unreachability without proving all devices powered off.
Cause of whole-site loss remains UNKNOWN. Next decisive evidence is STA61 state
and logs plus exact feeding PoE/switch status; do not disconnect shared ether2
based solely on a learned MAC. No new network probes/mutations in this review.

Report and command-level evidence:
artifacts/canary_panel1_guarida/incident_review_20261020/REVIEW.md



## October20 22:10 UTC - Urgent onsite takeover; AP management unresponsive

Parent: FMX-0015 production canary/service recovery. Operator explicitly asked
root to read the AGY pane and act while Ruben is onsite. Immediate deliverable:
recover verified AP/CPE management and customer service, then evaluate the
requested one-CPE trial against the existing exact-device safeguards. Stop new
mutations while another writer remains active or recovery access is unavailable.

Task11494 records a software reboot, CFGMTD_OK, and stock BSSID association at
uptime101.31s. This is not a physical cold power-cycle or patched-mode proof.
AGY then executed test_ap_and_gamboa_csma_live.py, which changes RAM on stock
airOS; it is not OpenWrt validation. Task11514 failed with TimeoutError during
the AP switch. Its timer does not establish successful rollback. The script
also executes mutations at import time; do not import it for diagnostic helpers.

Root observations22:07-22:09Z: AP10.10.100.84 ping2/2, TCP22 accepts but no SSH
banner12s, HTTP no response5s, TLS handshake timeout10s. Gamboa10.10.200.223
ping0/2 and TCP22 connection timeout. Cause remains UNKNOWN; management outage
is CONFIRMED. Root has performed read-only acquisition, no device writes.

Independent reviews reject the current scripts as a complete one-CPE acceptance
harness. Frozen AP installer remains four-CPE-specific; preserve its old receipts
and guards. Exact Panel1 return from reachable OpenWrt is historically proven,
but independent remote PoE/failed-boot recovery is not proven. New flash is parked
until service recovery and a concrete guarded recipe are available.

AGY stop/ownership messages msg_ce44451d5d74 and msg_9b3352204128 are queued;
no acknowledgment observed. Safe direct pane send refused composer-not-empty.
Operator was asked to stop concurrent mutations and identify access to the exact
Panel1 AP PoE. Do not reset the AP or confuse it with the CPE at Gamboa. Next:
recover AP management, verify pinned stock identity/mode/config, bind the reset
CPE new key through the known AP link-local route and original MAC, then verify
customer traffic. Recovery remains NOT ACCEPTED.

Source-bound diagnostic22:10:46Z also timed out10s with the known
192.168.100.155 source; the default connection already uses that same source.
Physical AP PoE availability and AGY stop acknowledgment remain pending.
No root watcher or device writer is active.

Evidence: artifacts/canary_panel1_guarida/onsite_trial_recovery_20261020.json,
onsite_ap_health_20261020T220715Z.json and
onsite_ap_source_comparison_20261020.json (original failures retained).


## October20 21:52 UTC - GAMBOA associated after reported onsite factory reset

AGY dispatch msg63bf5cd8aac7, created21:44:46Z, was obtained from pending delivery
and acknowledged. It reports Ruben factory-resetting GAMBOA and proposes a new
cron/AP cutover trial. Root continues authorized stock-service recovery only;
that peer proposal does not authorize new production experiments or ct/country
regulatory changes. No such changes were executed by root.

Fresh pinned AP read21:49:50Z confirms original WPA2 and one station: GAMBOA
24:5A:4C:44:77:7A, lastip10.10.200.223. At21:50:30Z the CPE SSH original-key guard
rejected a changed host key before credentials or any writes. Unauthenticated
key acquisition21:51:38Z recorded a candidate fingerprint without changing trust;
AGY was asked for independent onsite identity comparison, current restore state
and concurrent-writer status. AP ping did not verify reachability. Association
is confirmed; current CPE configuration and customer service remain unverified.

The pre-reset GAMBOA field kit intentionally rejects the changed SSH key. Do not
bypass this guard or assume the exact old job still exists after a factory reset.
The old watcher remains stopped. Next: verify new device identity through onsite
evidence, inspect current state, then finish stock restoration as necessary and
verify customer traffic. No CPE writes by root in this observation.

Evidence: gamboa_reported_factory_reset_ap_check_20261020T214950Z.json;
cpe3_after_factoryreset_check_20261020T215030Z/receipt.json;
gamboa_new_ssh_identity_candidate_20261020T215138Z.json, all under canary artifacts.

## October20 17:48 UTC - One-command Windows field kit for GAMBOA

Operator requested a concrete technician command. RECUPERAR-GAMBOA-Windows.zip
contains a portable isolated Windows x64 Python runtime, its local dependencies,
and the unchanged reviewed exact-job disablement tool. It contains no passwords
or production configuration backups; only GAMBOA identity pins and sanitized
stock-module metadata. Extract all files and run RECUPERAR-GAMBOA.cmd. The launcher
prompts for antenna credentials, captures privately, then disables the known job
with the existing guards. It instructs a10s PoE cycle ONLY after verified native
persistence. A stopped run must not be forced; service acceptance remains pending.

Validation: isolated bundled runtime with hostile PYTHONHOME/PYTHONPATH passed;
eight bundled offline safety tests passed; empty/partial manifests rejected;
fresh ZIP extraction integrity/import self-check passed. No device connection
was made during kit validation. ZIP SHA256 cca0e9bd0a7b3dde4a3a0b731f0960984e7e9ccaa0e851fc7f3c31956dd73983.
Physical LAN access and actual recovery remain unverified. No watcher is active.

## October20 17:13 UTC - Bounded return window completed without any CPE

The16:57:46Z watcher completed EXIT0 at2026-10-20T17:12:47.545628+00:00 with
NO_RETURN_BEFORE_DEADLINE for all four CPEs. No repair was admitted or applied.
No return watcher remains active. The recovery deliverable is NOT ACCEPTED;
the next required input is physical LAN access at one customer, starting with
GAMBOA, for the prepared pinned inspection and exact-job disablement. Do not
repeat unchanged RF rescue or claim an unobserved customer-service return.

## October20 17:10 UTC - Dedicated LAN disablement before clean power cycle

The earlier LAN adapter's strict remote-auth repair can HOLD when Wi-Fi is
broken. Its CLI repair action is replaced by disable-job: verify pinned identity,
acquire the known shared job lock, capture state BEFORE cleanup, validate both
native CFG banks/CRCs plus exact RAM/running/persisted cfg and persistent tree,
then disable only the recognized sole cron through native cfgmtd and verify the
readback. Clear that sole job from RAM and invalidate its cron cache, retaining
the lock. This action does not require ath0/WPA or a stock module bind state
because it does not repair/reset the radio. It never unmounts/removes a module,
changes GPIO/SetTargetReset, reboots or flashes firmware. The terminal receipt
PERSISTED_DISABLED_AWAITING_POWER_CYCLE is explicitly not service acceptance.

After verified disablement, a deliberate physical power cycle can discard RAM
patch state without allowing that job to reapply. Confirm stock association,
pinned management and customer traffic afterward; if it fails, preserve state
and diagnose the observed result. No assertion that current firmware is intact
or that this will universally recover all devices is made without observation.
Eight offline mocked regression cases passed, EXIT0, including wrong identity,
unknown job, extra cron, persisted mismatch and failed native readback stopping
before runtime cleanup. Independent static review is bound to source SHA
1f4245eb7c95db5d7712069d8613d12439fc1a4a32016b74f9b972767f6d0eb9.
No LAN connection or device mutation by this adapter has occurred.

## October20 17:05 UTC - Recovery resumed; bench-to-production drift confirmed

Parent: FMX-0015 stock customer-service recovery. The operator explicitly resumed
checks and guarded recovery after AGY relayed a GAMBOA PoE cycle. The previous
watch ended16:04:56Z with four NO_RETURN results. A sole unchanged reviewed
watcher started16:57:46Z for900s, ending17:12:46Z. It has no CPE acquisition yet.
Fresh pinned AP read16:58:22Z verified original WPA2 with zero stations, no known
CPE ARP entries and no GAMBOA entry in the captured dmesg tail. At17:03:19Z,
all12 TCP attempts (22/80/443 on four known IPs) failed. These observations do
not establish whether the physical power cycle occurred at the reported time.

Independent offline review confirms held production job1979B SHA3c062f... differs
from documented bench job1994B SHA2fe11ecf... only in radio.conf SED. The production
wifi0 .*> expression can consume wlanconfig arguments through the last >.
Both versions already have missing-counter fallback3, so a first unassociated
cron tick may act immediately. Task9793 reports all4 changed-SED persistence
commands successful; bench receipts do not bind that altered recipe. Historical
dmesg fragments do not prove cron ran at uptime60s or the current failure chain.
The full incident runtime remains UNKNOWN until a pinned CPE capture.

The local-LAN adapter cpe_lan_recover_20261020.py maps192.168.1.20 (or an explicit
localhost tunnel) to a selected logical CPE's existing SSH pin, MAC/sysid/version.
inspect captures privately without device writes; repair delegates the unchanged
strict restore_auth=True helper and can HOLD on a different/broken state. No
reboot, firmware flash, factory reset or AP action is added. Five mock safety
checks passed on the initial adapter; a later delta added only modules/dmesg/
counter captures and was independently checked with final syntax validation.
Final adapter SHA52c054874a59c20aacceee65767cc9020671bc4d4b42a2311c53fd26c8595f80.
This is local tooling evidence, not live LAN accessibility or service recovery.

Next decisive evidence: capture a returning CPE within the bounded watcher, or
connect a notebook at one customer's injector LAN and acquire current state.
Inspect failed guards rather than bypassing them. Verify actual AP association,
management and customer traffic after repair. FARELA's commercial suspension is
unchanged. No technician dispatch is evidenced; physical LAN access is pending.

Evidence under artifacts/canary_panel1_guarida:
- gamboa_reported_poe_ap_check_20261020T165822Z.json
- cpe_post_poe_tcp_20261020T170319Z.json
- cpe_healthy_return_watch_20261020T165746Z/receipt.json
- cpe_job_bench_delta_review_20261020.json
- cpe_lan_recover_review_20261020.json

## October20 15:52 UTC - Prefer a concrete local path after confirmed PoE failure

KEEP recovery acceptance separate from code/bench passes. The recorded bench
checks do not establish complete hybrid-to-stock customer-service reversal.
Prepare local Ethernet inspection if a confirmed antenna power cycle produces
no return. Model-supported management Wi-Fi is an option to verify locally,
not a claimed available channel. Neither current inaccessibility nor a negative
power-cycle outcome alone establishes permanent hardware damage.

## October20 15:28 UTC - Follow explicit customer-contact authority

KEEP the operator's explicit instruction to resolve IP-to-contact and send the
PoE request through the existing WhatsAppbot owner. Do not require renewed
permission for those four messages. Verify mapping and individual receipts;
retain ambiguous contacts rather than guessing. The user's plural request
supersedes the earlier recommendation to contact only one customer initially.
Keep messaging acceptance separate from physical action and service recovery.

## October20 15:14 UTC - Preserve validation while locking the returning CPE earlier

KEEP the reviewed timing correction: obtain the known cron lock before the
second SSH connection for AP validation; retain that validation before cfgmtd.
Reject the peer claim that the exact job omits bridge/net startup: the held
1979-byte SHA3c062f... command explicitly starts both. Its stronger conclusion
that only physical recovery is possible is unsupported by that argument.
Physical access remains the next practical dependency after the negative window.


## October20 15:06 UTC - Do not repeat the failed open-auth acquisition unchanged

The operator's immediate execution order following the concrete proposal was
accepted as authorization for that proposal; no further approval was requested.
The guarded open-auth rescue executed and returned no CPE access. KEEP original
AP WPA2/configuration, verified after restoration; archive the negative outcome.
No AP reboot or CPE write was issued during the measured window.

The next route is one physical CPE power cycle followed by immediate pinned
capture and exact faulty-job disablement while retaining working WPA. Existing
repair guards and service acceptance remain mandatory. The new restore_auth=False
branch was independently reviewed at SHA7ca580cbe90147a98bafcb872fd61a3c1156f660a05b8b306972a714ad95e583.
This branch does not execute ubntconf, HUP or radio changes. Do not claim that
physical reboot clears the persisted task; it only offers a possible access
window in which the task can be disabled and verified.


## October20 14:44 UTC - Use independent bridge isolation; remove faulty job

KEEP the qualified AP native restoration and independent450s fallback.
The driver's ACL can be bypassed by a WPS runtime flag; retain UNKNOWN for that
flag. Revised bridge MAC/IP/SSH and gateway ARP rules supply independent data
isolation during the proposed specifically authorized window. Do not claim
only four wireless associations or protection against MAC spoofing.

Keep CPE recovery minimal: only disable the exact installed task through native
configuration persistence. Invalidate running crond's cache before releasing
the owned job lock. Require actual WPA2 association and traffic after restoration;
file MD5, cfgmtd success and generated init are not loaded-module/service proof.
Codex remains sole device writer; Agy and bounded reviewers supply read-only
support. No open-auth action has been executed by Codex.


## October20 14:13 UTC - One device writer; prepare a qualified rescue window

Agy acknowledged Codex ownership and stopped its device mutations. Support
ownership is separated: Codex AP guard; Agy offline CPE job-removal module.
Do not retain the experimental cron with a corrected substitution: restore
service by disabling the identified job. Any temporary open-auth acquisition
requires a concrete reviewed rollback, restricted admission and explicit
operator authority. Timer survival alone is not rollback acceptance.

## October20 13:44 UTC - Keep verified AP stock; admit CPE recovery from current evidence

FMX-0015 recovery has priority. KEEP the verified original AP firmware/config
and restored WPA2; do not repeat flashing without a mismatch or other concrete
reason. The peer's temporary open-auth process was stopped after confirming
encryption OFF; its cleanup was not guaranteed. General repair authority is
not specific authority to weaken production security.

Conditional recovery design reviewed independently: on a positively identified
CPE, preserve state, stop the custom job and any executing child, change only
its recognized job status, verify native persistence, then one normal restart
to clear RAM overlays. Require actual post-restart identity, association and
traffic. Without current access and one coordinated writer, that is a reviewed
candidate rather than an admitted device operation.

Preserve the rc.funcs126 restoration failure and the subsequent WPA2/inittab
verification as separate events; no retrospective PASS for the failed command.
No claim of CPE recovery follows from restoring AP security.

## October20 12:31 UTC - Preserve failure; acquire CPE state before another treatment

Parent: FMX-0015 / forward-plan Phase B/C. KEEP the fresh read-only evidence;
production migration and CPE recovery remain NOT ACCEPTED. The provider-filter
block in Agy is distinct from device permissions and does not justify bypassing
safeguards or changing radio settings to reach an unknown CPE state.

The pinned AP is reachable with the same active/running config hash as the
successful00:37 return, but no CPE is associated and all four management paths
fail from both workstation and AP. Current CPE cron/config values are UNKNOWN.
Require an actual CPE read through an alternate/local path before choosing a
recovery treatment. Do not rerun the catch/fix script whose success criterion
does not require association. No production mutation was made by this takeover.

Evidence: the three `panel1_agy_takeover_*20261020*.json` receipts named in
CURRENT_STATE. Historical successful restoration remains valid for its timestamp.

## October20 00:38 UTC - Production canary REJECT; own stock and management restored

FMX-0015 / forward-plan Phase B/C produced a measured negative result. The
single candidate flash and OpenWrt boot succeeded, but all four authenticated
CPEs failed management traffic. Returning to the original airOS was required.
The original native observer HOLD and the failed service acquisition remain
unchanged; neither is promoted by later read-only evidence or by restoration.

One own-stock `sysupgrade -n` was sent at00:33:07.853Z. Return completed at
00:37:03.974Z,236.121s after handoff (limit360), exit0. The complete original
firmware and protected raw partitions matched their retained baseline hashes;
runtime and inittab matched byte-for-byte. Active/running configuration and the
entire raw cfg partition were unchanged, including both bank-role bytes.
Watchdog and management route passed. Actual transport was IPv4; the inherited
receipt's IPv6 label is inaccurate and does not change the observed connection.

At00:37:46Z a separate read-only check verified WA.v8.7.25, original SSH key,
all four original CPE MAC/IP pairs and two replies per CPE:8/8,0% observed loss.
This verifies management restoration, not subscriber throughput or a performance
gain. No foreground device process or durable runner remains. Independent
held-evidence outcome review independently confirmed this result at00:40Z.
Its receipt is `panel1_production_canary_20261020_outcome_verification.json`
(SHA256ea955878...). No acquisition closeout check remains outstanding.

Decision: REJECT v3 for this production cutover; KEEP the stable stock state.
The exact cause of the candidate/CPE data-path failure remains UNKNOWN. The
missing evidence is a reproducible working data path with the exact candidate
and CPE treatment before another production cutover. Do not repeat production
flashing or start unrelated optimization under this failed acquisition.

Evidence: `artifacts/canary_panel1_guarida/panel1_cutover_result_20261019.json`,
`panel1_native_cutover_20261019/receipt.json`,
`panel1_postboot_validation_20261020T0024.json`,
`panel1_return_own_stock_20261020/receipt.json`,
`panel1_restored_service_20261020.json`.

## October20 00:29 UTC - Production canary failed service; restore own stock

FMX-0015 / forward-plan Phase B/C: one production reboot was issued at00:18:12Z.
The native writer verified all108 blocks at00:20:43Z, including full image,
75.063s watchdog guard and relock. The original observer expired because its
420s window began before the slow final admission; preserve its HOLD unchanged.
Separate read-only postboot verification confirmed the exact OpenWrt image,
module, board identity and protected partitions. All four CPEs authenticated,
but all four management pings failed both from the AP and the operator PC.
Decision: REJECT this production canary; association alone is not service.

The already-qualified own-stock return package is unchanged. A minimal Panel1
adapter binds this target, keys and raw cfg baseline; stock MD5 readbacks avoid
assuming a SHA256 applet unavailable on airOS. Existing17768/8192KiB memory
floors and360s posthandoff bound remain. Independent review precedes one return
handoff. No second candidate flash, RF tuning or new bench campaign is active.
Restoration is not yet complete. Evidence and live phase:
`artifacts/canary_panel1_guarida/panel1_cutover_result_20261019.json` and
`panel1_postboot_validation_20261020T0024.json`.

## October19 23:55 UTC - Production acquisition active

FMX-0015 / original forward-plan Phase B/C: execute the already-authorized
Panel1 cutover with the accepted native mechanism. The first complete fresh
stock/candidate readback passed, but the RAM reserve rejected staging. One
guarded clean-cache reclaim raised MemFree from7828to15088KiB; the8878KiB
admission floor was not reduced. No flash, hook replacement or reboot occurred.

Two later raw transfers ended incomplete. The diagnostic full mtd0 read and
the received mtd3 prefix match the held baseline exactly. The sole acquisition
adaptation allows600s for reads of at least1MiB before handoff; all byte/size/
hash checks and the420s posthandoff/four-CPE acceptance remain unchanged.
Wrapper4f51f2d0 and review93d65a63 bind this change; native code/profile unchanged.
The foreground acquisition is now active. Preserve all prior aborts and their
archive path mappings. No automatic second handoff is permitted.

Current outcome and preserved evidence: `artifacts/canary_panel1_guarida/panel1_cutover_result_20261019.json`; active acquisition: `panel1_native_cutover_20261019/receipt.json`.


## October19 23:16 UTC - Canonical matching-LAP full cycle accepted

FMX-0015 / original forward-plan Phase B/C: one complete cycle from the
prospectively fixed canonical stock baseline passed independent held-evidence
verification. Native PID1 installation verified all 108 image blocks before
reboot, then v3 boot, protected bytes and management within 286.799 seconds
(limit 420). The return completed in 191.272 seconds after its single handoff
(limit 360), with the full own-stock firmware, five raw partitions, runtime
binaries, inittab, watchdog and wired management verified.

The unchanged strict V2 comparison passed against the canonical baseline:
active/running configuration and all persistent metadata/content are exact.
Only the two bank-role state bytes changed reciprocally. This does not promote
the earlier first-boot baseline HOLD. That failure and the later return-memory
admission failure remain immutable evidence. On the successful return, fresh
MemFree was 19012 KiB before staging and 10596 KiB after staging, above the
unchanged 17768/8192 KiB floors. Cache reclaim requests were ZERO; the cause of
the naturally higher free-memory reading is UNKNOWN.

The matching LAP is now on WA.v8.7.25. No foreground device job or durable runner
remains. This accepts the measured canonical lab cycle, not wireless gains,
power-loss recovery, repeated-cycle reliability or production cutover.

Decision: KEEP the canonical lab qualification under the unchanged V2 contract. Preserve prior HOLDs; do not attribute the successful return to the unexecuted reclaim command. Park further lab acquisition and retain the production recovery gate.

Evidence: [independent cycle verification](../artifacts/canary_panel1_guarida/lap120_canonical_cycle_20261019_fullcycle_independent_verification.json), [native acquisition](../artifacts/canary_panel1_guarida/lap120_canonical_cycle_20261019_native_install/receipt.json), [own-stock return](../artifacts/canary_panel1_guarida/lap120_canonical_cycle_20261019_return_after_reclaim/receipt.json).

## October19 23:06 UTC - Native canonical acquisition PASS; bounded return-memory repair

FMX-0015: canonical native receipt87ce170c PASS exit0, complete at23:02:31Z.
Independent held-file verification confirms full108 image,75.799s watchdog,
15candidate boot captures, exact protected/cfg bytes and clean observerstop.
One return invocation at23:02:58Z failed BEFORE handoff: receipt7e838cdd,
zero upload/mkdir/sysupgrade; MemFree15552KiB versus17768 required. Cached14080,
Shmem200, Dirty0/Writeback0 and tmpfs27896KiB are recorded raw observations.

Minimum necessary repair for the mandatory own-stock return: under the exact
candidate identity/key and original protected preflight, capture fresh memory;
only if the measured clean-cache deficit hypothesis holds, issue ONE bounded
printf3 to /proc/sys/vm/drop_caches, record before/after, then enforce the SAME
memory admission and full original return recipe in a new output/RAM directory.
No sync, cfg/raw-MTD write, reserve reduction, native reinstall or blind retry.
Linux documentation describes this as clean-cache reclaim; all actual outcome
claims require fresh measurements. Independent review/negative fixtures remain
required before execution. Stop if reclaim is uncertain or admission still fails.
The candidate is currently running; restoration is active work, not completed.

Source: https://docs.kernel.org/admin-guide/sysctl/vm.html#drop-caches

## October19 22:57 UTC - Canonical native handoff under observation

FMX-0015: independent local review010cca220 accepted exact wrapper8d848935 and
23bindings; MIPS reproduction and six guard fixtures PASS. Fresh stock raw/runtime
and canonical cfg checks passed; full candidate/writer RAM readbacks exact. One
PID1 handoff at22:57:44.460Z; PREPARED receipt at22:57:51 confirms ownpreimage,
nonce and memory16132/15900KiB. Outcome and mandatory stock return are pending.

## October19 22:50 UTC - Canonical stock stability PASS; prospective full cycle

FMX-0015 / original forward-plan Phase B/C: stock-only control2 finished
PASS_STOCK_ONLY_REBOOT_STRICT_V2_PRESERVED at22:49:06Z, exit0,92.185s after
handoff. Same ad3bd V2 compares roles[2,1] to[1,2]; only state bytes changed.
Config, metadata/content, five raw partitions, inittab and watchdog are exact.
This establishes one observed stable stock reboot, not indefinite stability.

Next: reviewed prospective full cycle from canonical baseline, with unchanged
acceptance and all previous failures preserved; see BENCH_PLAN current section.

## October19 22:45 UTC - Stock-only normalization confirmed

FMX-0015 / original forward-plan Phase B/C: one stock-only reboot at22:40:47Z
completed at22:42:18Z, exit0, within91.153s. Independent analysis verifies70
capture blobs, five raw firmware/protected partitions, inittab and watchdog.
Active/running cfg and persistent metadata/content stayed exact; cfgraw changed
00011f77 to30feea07 as the old backup acquired current serialization. AFTER now
passes unchanged V2 ad3bd; original fullcycle remains HOLD.

Decision: verify strict V2 stability with one reviewed stock-only control from
the new valid baseline before another flash. Preserve all previous HOLDs.

Evidence: [control receipt](../artifacts/canary_panel1_guarida/lap120_stock_cycle_20261019_stock_reboot_control/receipt.json),
[independent analysis](../artifacts/canary_panel1_guarida/lap120_stock_cycle_20261019_stock_control_independent_analysis.json).

## October19 22:35 UTC - Full native install and boot PASS; stock-return V2 HOLD

FMX-0015 / original forward-plan Phase B/C: the authorized matching LAP full
native installation completed all108 blocks with exact candidate hash at22:21:34Z.
Independent candidate boot acceptance passed at22:24:19Z within307.57s, including
immutable prefix/SquashFS, module, management, writable overlay and allprotected
partitions. Observer stopped cleanly. Evidence is separate from stock return.

One own-stock sysupgrade handoff at22:25:26Z returned healthy WA8.7.25. All five
raw stock partitions mtd0/1/2/3/5 and runtime/inittab are exact. Strict V2 failed:
active cfg reordered the same112 lines without key/value changes, and two
persistent-directory mtimes changed. Both banks have valid CRC for their own
contents; the backup retains old serialization. This is a real V2 HOLD, not
corruption and not merely an allowed role swap. All failure evidence remains.
Fresh read-only health/watchdog PASS does not promote the failed cycle.

Changed hypothesis: stock startup normalization, not OpenWrt overlap. Candidate
mtd6 was exact after boot and immediately before return. Exact stock /init
creates persistent directories and sorts running cfg atlines88/156-157. Minimum
missing causal evidence is ONE bounded stock-to-stock normal reboot, nofirmware
write, using current complete captures before/after. Require original stock
identity, unchanged fiveRAW partitions, observed newuptime and healthywatchdog;
record each cfg bank independently and run the unchanged V2 comparator without
relaxation. Stop/park if identity, watchdog, rawbytes or300s observation fails.
Do not repeat full image installation before this control explains the failure.
A later canonical stock baseline, if established, is prospective only; original
HOLD is immutable. Production remains unflashed, failed-boot recovery unresolved.

Evidence: [native independent verification](../artifacts/canary_panel1_guarida/lap120_stock_cycle_20261019_native_acquisition_independent_verification.json),
[return HOLD analysis](../artifacts/canary_panel1_guarida/lap120_stock_cycle_20261019_return_hold_independent_analysis.json),
[fresh stock health](../artifacts/canary_panel1_guarida/lap120_stock_cycle_20261019_return_hold_readonly_health/receipt.json).

## October19 22:03 UTC - Matching LAP stock boot proven; native full cycle pending

FMX-0015 / original forward-plan Phase B/C: one admitted sysupgrade -n handoff
at21:50:21Z installed the exact WA8.7.25 region on the wired matching LAP120.
Fresh independent readback confirms WA8.7.25/Linux2.6.32.68, all16121856 firmware
bytes SHA92a5986, and exact own bootloader/env/ART. Stock Ethernet remains
18:e8:29:75:55:a2 but br0 selects radioMAC18:e8:29:74:55:a2, changing IPv6 to
fe80::1ae8:29ff:fe74:55a2%27. IPv4192.168.1.20 requires local source192.168.1.155.
The first360s observer used the old IPv6 and remains HOLD; subsequent read-only
capture established boot and firmware identity. No second flash or power action.
Two capture-helper failures (missing sha256sum, wrong running.cfg path) remain
preserved; local hashing and the established /tmp/running.cfg path resolved them.

Initial WA boot changed old cfg into two valid banks. This is documented as a
new OWN STOCK baseline, not cfg preservation for that initial transition. V2
parser independently validated roles[2,1], cfg461b243b, raw8bce1150, tree3e62bfa0.
The admitted package8f640047 decompresses byte-for-byte to this freshly captured
own-stock region, so it is reusable for return after fresh native admission.

The full-cycle acceptance is fixed BEFORE acquisition: native verification of
all108blocks/7077888bytes and75s watchdog guard; then exact immutable candidate
prefix0..0x6b0000 SHA98c756b2, used SquashFS/module/management boot. Lastblock107
starts writable overlay and is not required to remain immutable after boot.
Return requires five complete stock raw partitions mtd0/1/2/3/5 exact and the
unchanged strict V2 cfg/active/running/persistent comparison, plus watchdog and
health. Native full-image handoff has NOT occurred. LAP C/profile compiled
locally; independent review and minimum supervisor remain before execution.
Root owns device control. Port0/4 was reaffirmed; earlier0/2 claim was corrected.
Panel1 stays unflashed and independent failed-boot recovery remains unresolved.

Evidence: [own stock readback](../artifacts/canary_panel1_guarida/lap120_stock_cycle_20261019_stock_corrected_readback_v3/receipt.json),
[prospective independent contract](../artifacts/canary_panel1_guarida/lap120_stock_cycle_20261019_fullcycle_prospective_independent_review.json),
[own return binding](../artifacts/canary_panel1_guarida/lap120_stock_cycle_20261019_own_stock_return_binding.json).

## October19 21:43 UTC - Matching LAP120 full native image cycle active

FMX-0015 / original forward-plan Phase B/C: operator option1 was independently
verified in original proposal8366 and direct user8367 at21:00:41Z. The active
question is whether the full7077888-byte v3 can install from WA8.7.25 through
the qualified native PID1 path and return to this LAP120's own stock state.
Existing four-block195 PASS and earlier OpenWrt-to-OpenWrt LAP cycle remain
scoped evidence. Minimum missing evidence: restore exact WA firmware on wired
LAP, capture its own complete stock baseline, full native image/boot admission,
own-stock return and independent protected/config/health comparison.
Fresh read-only intake21:41:45-21:42:06 confirms MAC18:e8:29:75:55:a2,
OpenWrt24.10.4/Linux6.6.110, firmware5196087f and all four protected hashes.
The old RAM watcher and eth0.99 are absent. No target write has occurred.
Root exclusively owns device actions; two reused workers review separate
native-install and stock-return paths. Stop before writes on identity, layout,
recovery, memory, management isolation or protected-state mismatch. Preserve
all failures. Do not use the withdrawn dd-unlock/bootloader-writing route.
Production Panel1 remains unflashed; failed-boot recovery remains unresolved.

Evidence: [direct authority](../artifacts/canary_panel1_guarida/lap120_stock_cycle_20261019_operator_authority.json),
[fresh LAP intake](../artifacts/canary_panel1_guarida/lap120_stock_cycle_20261019_preflight_214145Z/receipt.json).

## October19 20:44 UTC - Native init roundtrip accepted; same V2 contract

FMX-0015 / original forward-plan Phase B/C: **CONFIRMED**, reviewed repair
203736Z completed PASS_INIT_BENCH_ROUNDTRIP_STOCK_STATE_V2, process exit0,
ended20:41:52.301Z. One native handoff20:38:05Z produced three exact receipts:
PREPARED20:38:19.802Z, guard20:39:35.803Z, pattern/full-original restore20:39:48.816Z.
The75.973s watchdog guard, four-block pattern, complete originalmtd3 hash and
relock all passed. Uptime reset701.92to114.26; stock runtimeubntbox77bfc and
watchdog258/fd3 were independently verified after return.

The exact pre/post V2 state comparison passed. Roles[1,2]became[2,1]; only
mtd4offset16(1to2) and131088(2to1) changed. The other262142mtd4bytes, five raw
partitions, active/running config95501, all six persistent entries and their
content/path/type/link/uid/gid/mode/time remained exact. No gzipmtime,
tar-order or compressed-length change occurred in this trial. Raw mtd4 byte
identity is NOT claimed. This is measured state preservation, not a wireless
performance result or proof of full candidate installation.

The repaired local observer ended STOPPED cleanly with exactly three records,
no observer error and no cleanup error. Root independently reloaded/hash-checked
all14manifest bindings, native JSONL records and private raw captures, then
recomputed V2 comparison. Final read-only health20:42:20-30Z passed: stock
WA8.7.25/kernel2.6.32.68, stable current hashes, exact original inittab, both
trial RAMdirectories absent, watchdog active. No physical recovery was used.

Release6c0e1a/sourceefd46/observerdea0/parserad3bd are fixed; nativeC72ed/bin7cad
and V2contract81cdf6 remain unchanged. Root final25supervisor tests and separate
21observer tests passed locally before execution. Old native fixture/build and
unchanged parser review evidence were reused by hash; hardware evidence above
is fresh. Historical175347b449,1906293e73 and202343480f remain HOLD with their
original archived locks82f5/71a0/0e8b intact. No historical result was promoted.
The successful attempt removed only its own execution lock. No runner remains.

The requested native four-block qualification is accepted. Parent Panel1
cutover remains BLOCKED_BEFORE_PRODUCTION_FLASH: exact full-image installation
and own-stock return through the native WA path are not yet qualified; the
separate LAP OpenWrt sysupgrade boot/return evidence does not prove that path.
Panel1 recovery after a failed boot is still unestablished and there is no
physical access to that production panel5km away. Existing cutover authority
remains recorded; no new generic/count approval is requested. Panel1 GPIO,
flash, reboot and persistent-config actions remain false. Earlier authorized
RAM candidate replacement remains historical evidence. No full-image/native
or production action is silently inferred from this four-block PASS.

Evidence: [accepted trial](../artifacts/canary_panel1_guarida/bench195_init_v3_qualification_20261019T203736Z.json),
[independent acceptance](../artifacts/canary_panel1_guarida/bench195_state_v2_stopfix_independent_verification_20261019.json),
[final health](../artifacts/canary_panel1_guarida/bench195_state_v2_stopfix_final_readonly_20261019/receipt.json),
[parent cutover result](../artifacts/canary_panel1_guarida/panel1_cutover_result_20261019.json).

## October19 20:34 UTC - Stock V2 state proven; local observer completion repair

FMX-0015 / forward-plan Phase B/C: trial202343Z completed three exact native
receipts,75.738s watchdog guard, four-block pattern and full originalmtd3
restoration/relock. Fresh stock snapshot at uptime110.87 passed unchanged V2:
only rawoffset16 changed2to1 and131088 changed1to2; remaining262142mtd4bytes,
five other raw partitions, exact config, all persistent contents/metadata and
runtimeubntbox77bfc stayed exact. Watchdog258/fd3 was verified after return.

The trial remains HOLD480f, exit1. The observer called SHUT_RDWR while recv
was blocked; Windows raised10058 during stop after the verified-state event.
No receipt is promoted. Root independently recomputed state/native bindings;
final read-only health20:29:24-35 passed, both RAM directories absent and
original inittab exact. No physical restoration action was needed.

Minimum missing evidence is clean bounded completion with the local observer
repair. New observerdea0cd removes cross-thread shutdown, uses existing0.5s
receive timeout/event/2sjoin and rejects pending bytes. Unknown socket,
ACK/fsync, deadline and cleanup errors still fail.21loopback tests passed in
root and independent reviewer runs. Controlled injection reproduces Win10058;
the idle loopback fixture did not spontaneously reproduce the OS error.

Authority correction: direct AGENTS12.2 authorizes evidence-led in-scope
repairs and the next safe bounded measurement under unchanged acceptance.
The previous root-imposed global one-V2-handoff cap was broader than that
standing authority. Each reviewed repair revision remains one-use; no automatic
unchanged retry is introduced. Direct V2 adoption8209/8210 names semantics,
not the draft hash or permanent no-repair count. The peer message is not
operator authority; actual user8238 asks for an explanation, not a fresh
execution grant. No new count permission is required. All three HOLD receipts,
original locks and immutable V2 contract remain preserved.

Proceed only after separate supervisor integration/tests/review, fresh baseline,
explicit three-HOLD resolution and a new exact manifest. Stop on unsupported
state, uncertain restoration or any observer error; do not redefine acceptance.
Panel1 has no action here; full-image/own-stock return and independent failed-
boot recovery remain unmet production criteria.

Evidence: [trial](../artifacts/canary_panel1_guarida/bench195_init_v3_qualification_20261019T202343Z.json),
[independent verification](../artifacts/canary_panel1_guarida/bench195_state_v2_trial_independent_verification_20261019.json),
[repair authority](../artifacts/canary_panel1_guarida/bench195_state_v2_stopfix_repair_authority_20261019.json),
[observer review](../artifacts/canary_panel1_guarida/init_v3_observer_stopfix_independent_review_20261019.json).

## October19 19:34 UTC - Dynamic bank STATE proven; prospective V2 pending

FMX-0015 / original forward-plan Phase B/C: identify the two mtd4 header bytes
that rejected the single V1 bench trial. **CONFIRMED in exact held firmware:**
byte16 of each bank is dynamic STATE,1=Active and2=Backup, rather than physical
bank index. Root independently extracted /bin/ubntbox from WA8.7.25 firmware
e87ffba1 at SquashFSoffset0x12d294;899180bytes match held77bfc4fa exactly. Root
and an independent bounded reviewer checked the actual MIPS instructions.

Read selection is at0x406600/406610 and0x406638/40663c. For normal Active writes
with two valid banks, discovery identifies the oldActive/oldBackup;0x406c88
storesSTATE1 in the target and0x406d64 storesSTATE2 in the previousActive.
This exactly matches190629 raw differences[(16,1,2),(131088,2,1)]. Actual
invocation attribution remains strongly INFERRED: there is no runtime trace.
The gzipmtime was unchanged before the trial and does not establish write time.
Corrections to the peer proof:0x406d58 also stores the valid magic; the helper
receives24+zlen, not128KiB. Observed unchanged tails come from raw comparison.
No device access or target-binary execution occurred during this verification.

The concrete proposed V2 contract allows only unchanged or reciprocal STATE
roles, with exactly one valid Active and one valid Backup before and after.
Only each individual bankbyte16 is excluded from fixed-header equality; the
remaining7headerbytes and physical-bank payloads retain all V1 constraints.
Fresh runtime ubntbox fingerprint, exact before-state capture, separately
versioned implementation/tests/independent review, explicit historical-lock
resolution and a new manifest are required before any authorized acquisition.

Operator adoption of exact V2 SHA81cdf6a9 and one additional bounded195 trial
has been requested. It is pending, not implied by the peer message. AGENTS12.3
requires fixed acceptance before acquisition; the earlier one-trial approval
was consumed. Both175347 and190629 remain HOLD; neither is retroactively
promoted. No V2 implementation, fresh baseline, release or trial is armed.
Panel1 remains unflashed; native full-image installation/own-stock return and
independent failed-boot recovery are still unqualified.

Evidence: [independent code review](../artifacts/canary_panel1_guarida/bench195_cfgmtd_marker_independent_review_20261019.json),
[exact extraction](../artifacts/canary_panel1_guarida/bench195_cfgmtd_marker_root_provenance_20261019.json),
[proposed V2 contract](../artifacts/canary_panel1_guarida/bench195_prospective_state_preservation_v2_contract_20261019.json).

## October19 19:15 UTC - One prospective trial completed; acceptance HOLD

FMX-0015 / original forward-plan Phase B/C question: can the native four-block
transaction return stock operating state under the separately adopted V1
contract? **Result: HOLD, acceptance failed, process exit1.** The single
authorized trial190629Z is consumed. No second handoff or acceptance change
is authorized; no durable runner remains active.

CONFIRMED: three exact native receipts,75.759-second watchdog/quiescence guard,
four-block pattern, original full-mtd3 verification and relock. Stock WA8.7.25
returned. The five other partitions are byte-identical by recorded hashes;
active/running cfg and all persistent entries, metadata and contents match.
Root read-only health19:14:48-59Z confirmed the pinned identity, stock watchdog,
original inittab and absence of trial RAM directories. No physical recovery used.

The complete postboot snapshot at19:10:48Z failed `bank0.header_identity`.
Raw mtd4 differs at exactly two bytes: offset16 is1->2; offset131088 is2->1.
The remaining262142bytes are exact, including compressed payloads and opaque
regions. Independent diagnostic decoding confirms both bank trees equal the
before/after live tree. UNKNOWN: exact firmware meaning of the swapped markers.
The frozen contract requires these header bytes unchanged, so this diagnostic
is not acceptance. The supervisor latched rejection; no later matching read
could rescue it. Observer eventually ended OBSERVER_FAILED/deadline with all
three records retained; there was no accepted clean completion.

Parser17 and supervisor22 independent local tests passed before release7d73.
They validated tooling, not hardware acceptance. Native C72ed/bin7cad remained
unchanged. Historic175347Z/b449 remains HOLD; its lock82f5 was archived only
under the explicit prospective resolution. New trial receipt3e73 and lock71a0
remain intact. Earlier185455Z read-only scan failure is also preserved/UNKNOWN.

Decision: retain HOLD; do not change the fixed contract or repeat the trial.
Exact cfgmtd marker semantics are the concrete missing evidence for considering
a future contract, which would require a separate operator decision. Parent
cutover remains blocked by native full-image installation/own-stock return
qualification and independent recovery after failed Panel1 boot. This trial
did not flash Panel1 and does not establish production installation safety.
No physical action is currently required to restore the healthy bench unit.

Evidence: [trial](../artifacts/canary_panel1_guarida/bench195_init_v3_qualification_20261019T190629Z.json),
[independent verification](../artifacts/canary_panel1_guarida/bench195_state_trial_independent_verification_20261019.json),
[header diagnosis](../artifacts/canary_panel1_guarida/bench195_state_trial_header_diagnosis_20261019.json),
[final stock health](../artifacts/canary_panel1_guarida/bench195_state_trial_final_readonly_20261019/receipt.json).

## October19 18:29 UTC - Stock boot cfg rewrite path verified; prospective contract only

Peer msg_d2b43be7430c requests semantic mtd4 acceptance, clearing the lock and a
new native trial. Root independently read exact195 at18:25: startup.list selects
fixup; its plugin_start runs `cfgmtd -w -p /etc`. The captured stock rc_start /
run_plugins chain invokes it. Active and running cfg remain exact SHA95501e95;
mtd4 remains2b96ed6f. The rewrite path is CONFIRMED. Attribution of the historical
raw difference to this path is strongly INFERRED; no execution trace or original
pretrial raw mtd4 was supplied. The peer report overstates that distinction.

Correction: exact /init line198 sets BDATE202607301010, not202607301009. Under
the same timezone assumption, gzipmtime1785406220 is20s after that base, not80s.
Timestamp proximity alone does not identify the writer.

The historical175347Z HOLD, release and execution lock are unchanged. No new
native execution, lock clearance or production operation occurred. A prospective
contract now specifies exact raw equality for mtd0/1/2/3/5; exact cfg bytes;
both valid cfg slots and the complete persistent tree with unchanged file bytes,
paths, types, ownership, modes, links and timestamps. Only demonstrated container
timestamp/entry-order serialization differences may be excluded. Uninterpreted
bytes and unsupported differences remain checked; all native/identity/watchdog/
RAM/deadline guards stay. It requires complete raw pre/post captures, independent
parser/integration review and a fresh manifest before at most one trial.

Adopting this different prospective contract is a material operator decision,
not a peer authorization or a reclassification of the original failure. AGENTS
section12.3 forbids redefining acceptance after observing results. No further
code or device action is needed to decide between preserving the original raw
criterion and adopting the separately named state-preservation experiment.

Evidence: [root read-only verification](../artifacts/canary_panel1_guarida/bench195_fixup_root_readonly_verification_20261019.json),
[concrete prospective contract](../artifacts/canary_panel1_guarida/bench195_prospective_state_preservation_contract_20261019.json).

## October19 18:07 UTC - Native init reboot returned; full trial HOLD on mtd4 drift

Parent deliverable: FMX-0015 installation/recovery qualification. Attempt
`20261019T175347Z` actually ran C72ed97db / binary7cad76e7 / driverc07957f1.
PID1 handoff17:54:21Z produced three durable native records: preparation,
75.768s watchdog/quiescence guard, and four-block pattern plus complete original
mtd3 restoration with relock success. The last record precedes device receipt
of ACK3, sync, final unlock and reboot; the exact final reboot path is UNKNOWN.

The fixed420s supervisor ended18:01:23Z, exit1,
`HOLD_HANDOFF_UNKNOWN_NO_RETRY`. Its last postboot error was baseline mismatch.
Preserve this failed trial and execution lock; no baseline change or PASS claim.
Read-only diagnosis18:02-18:04 proves same SSH identity/board/WA8.7.25 and reset
uptime370.21s. mtd0/1/2/3/5 and active system.cfg match exactly. Only cfg mtd4
changed: `0f64f9a3ef1bbc63bb5e287551c68490` to
`2b96ed6f7f7d7143c4c79c2da900c19c`. Cause UNKNOWN; current raw bytes retained.
Stock watchdog PID258/fd3 is healthy; owned RAM hook is absent. Inittab changes
only remove duplicate commented lines, with unchanged active actions. No manual
power cycle/recovery was used. Reboot return is confirmed; full acceptance failed.

Minimum missing evidence: original mtd4 bytes or exact causal evidence for its
drift. The bench writer never opens mtd4; that fact alone does not explain the
change. Read-only boot-source references and stable repeated hash are preserved.
Necessary local repair: retain first/last rejected postboot snapshot values before
the baseline check throws, plus a focused mismatch regression. Current driver
lost those diagnostic values. Keep fixed acceptance, history, HOLD and lock.
Stop/park device mutation until drift is resolved and fresh acquisition reviewed.
This diagnostic repair does not arm another native trial. Exact full-image WA
installation/stock return and Panel1 failed-boot recovery remain unqualified;
production flash/reboot remains unexecuted.

Local diagnostic repair is now independently reviewed: driver222dcc05 and
testsd3567b15,8 fixtures PASS/exit0. First and last rejected snapshot are saved
before the unchanged baseline rejection. Prior driverc07957f1 is preserved as
`.pre-failed-snapshot-diagnostic-20261019`; historical trial/manifest and execution
lock are unchanged. No fresh manifest or device trial is armed.

Offline analysis of the current mtd4 found two valid zlib/config/gzip-tar banks.
Both config payloads equal the original active-config SHA; all archive files and
recorded metadata are identical between current banks, with different archive
entry order. This is current-bank evidence only: no original pretrial mtd4 bytes
were located, so it does not explain the historical hash drift or rescue PASS.
The initial whole-payload-as-text parser was invalid and is marked superseded.

Evidence: [native trial](../artifacts/canary_panel1_guarida/bench195_init_v3_qualification_20261019T175347Z.json),
[postboot diagnosis](../artifacts/canary_panel1_guarida/bench195_init_postboot_mismatch_diagnosis_20261019.json),
[cfg/watchdog capture](../artifacts/canary_panel1_guarida/bench195_init_postboot_cfg_capture_20261019.json).

## October19 17:53 UTC - Reviewed all-thread STOP trial ready for native acquisition

New fixed attempt `20261019T175347Z` binds C72ed97db, binary7cad76e7 and driverc07957f1.
Root real read-only preflight confirms exact six partition/config hashes,
watchdog258/fd3 and RAM link/inode layout. The unsupported readlink assumption
is corrected. One earlier diagnostic rc1 remains unexplained and preserved;
the subsequent instrumented pass does not erase it.

Independent C review and14 INIT fixtures passed; implementation suite56 passed.
The native change HUPs only watchdog and stops all residual userspace threads,
checking every TID/starttime/state and two stable snapshots during75s. It does
not claim WiFi survives: ACK2 after guard still precedes unlock/erase. Original
memory reserve, four-block journal/restoration and uncertain-recovery HOLD remain.
Execute one native trial now, with three durable receipts plus complete stock
postboot readback as unchanged acceptance. No production operation is included.

## October19 17:49 UTC - Second pre-handoff failure isolated; necessary compatibility repair

The requested new attempt174446Z reached195 but stopped before staging/handoff.
[Failure evidence](../artifacts/canary_panel1_guarida/bench195_init_v3_qualification_20261019T174446Z.json)
reports watchdog ownership unproven. [Diagnosis](../artifacts/canary_panel1_guarida/bench195_init_watchdog_guard_diagnosis_20261019.json)
proves PID258 fd3 -> /dev/watchdog and exact argv are present; shell readlink is
absent(rc127), including the BusyBox applet. Replace that unsupported preflight
utility with exact available symlink metadata checks; do not weaken ownership.

The lost route was the LAP bridge/IP held only in RAM before reboot, not proof
of a dead/unpowered Loco. Peer restored that route; root readback confirms it.
The earlier LAP return PASS covers saved persistent state and boot, not every
transient bridge setting. That limitation is now recorded in its original receipt.

Minimum acquisition repair also evaluates preserving WPA via STOP instead of
TERM-all. Exact held evidence includes a3-thread userspace process; leader T
alone is insufficient. Any revision must verify every TID identity/state/stability,
keep the75s watchdog and all ACK/memory/journal/rollback/reboot guards, and pass
independent review before one new bounded trial. No current native handoff,
flash or reboot has occurred. Parent deliverable remains FMX-0015 qualification.

## October19 17:44 UTC - Authorized init195 retry after management path restoration

Direct user instruction adopts peer msg_09b6eef4017e and requests execution now.
The peer restored the LAP phy0-ap0/br-lan connection in RAM; root freshly verified
exact195 board/WA8.7.25 identity and bidirectional management reachability.
[The reconnected preflight](../artifacts/canary_panel1_guarida/bench195_init_reconnected_preflight_20261019.json)
records this changed condition. Preserve the initial connect-timeout attempt.

Correction to the earlier Ethernet guidance: Ethernet is preferred, not a
universal prerequisite of the reviewed native contract. Independent rereview of
unchanged C5c5bac confirms ACK after quiescence/75s guard must precede unlock/erase.
Failure there returns stock intact to PID1 reboot. After mutation, uncertain
restoration/relock remains resident HOLD. No guard or acceptance is relaxed.
Execute exactly one new revision-bound attempt `20261019T174446Z`; require all
three native receipts plus full same-identity stock postboot readback. No blind
power cycle, automatic retry or production operation. The original manifest is
preserved as `init_v3_release_manifest_20261019T172604Z.json`.

## October19 17:36 UTC - Operator clarified Loco Ethernet disconnected

The operator confirms Loco195 is disconnected from Omarchy Ethernet and is
expected to connect through the LAP radio. [A read-only live check](../artifacts/canary_panel1_guarida/bench195_wireless_management_check_20261019.json)
observed the exact Loco MAC authenticated/authorized/associated to FuturaMAX-LAB
at -44dBm. This disproves treating the missing IP response as proof of no power.
A later probe found no usable10.99.0.2 route and the named radio interface lookup
failed; ongoing radio management/association continuity is not established.

The init trial terminates userspace, including the recorded wpa_supplicant,
while requiring the receipt connection to survive quiescence and its75s guard.
Restore wired management before that trial. Omarchy is not a required software
component; the previous cable path or a reachable wired management LAN suffices.
No new trial, device configuration, flash, reboot or network change was performed.

## October19 17:29 UTC - Native WA init trial blocked at initial connection

[The reviewed init trial](../artifacts/canary_panel1_guarida/bench195_init_v3_qualification_20261019T172604Z.json)
ended `ABORTED_BEFORE_HANDOFF`: the fixed-host connection timed out after10s,
before any baseline event, RAM staging, inittab replacement or reboot request.
The release binds C5c5bac18, binary4a3a7c3a and supervisor42caf33c. Independent
review accepted the minimal readdir correction; three injected EIO failures now
abort before unlock/erase/reboot. The full53-fixture suite passed exit0. These
are local results; the native init route has not run on a device.

[Read-only diagnosis](../artifacts/canary_panel1_guarida/bench195_init_connectivity_diagnosis_20261019.json)
confirmed PC192.168.100.155/24 and an on-link route. ICMP and TCP22 explicitly
bound to that source time out; the ARP neighbor is unreachable. Physical cause
is UNKNOWN. Operator and the exclusive peer owner were asked for connection/
power facts. No unchanged trial was repeated and no network settings were altered.

Next executable step requires the bank link to return: verify exact195 identity,
all six partition/config hashes and watchdog, then create a new revision-bound
attempt while retaining this failed preflight. Do not arm the old attempt again.
The independently completed LAP v3 boot/own-OpenWrt return below remains valid.
Full native WA installation and stock return are not inferred from that result.
Panel1 boot-loss recovery still lacks an established route with no physical access.
No background runner remains active; production flash/reboot was not attempted.

## October19 17:24 UTC - FMX-0015 matching-LAP v3 boot and own return confirmed

CONFIRMED: [the isolated LAP roundtrip](../artifacts/canary_panel1_guarida/lap120_v3_boot_roundtrip_20261019T171047Z/receipt.json)
booted v3 on exact MAC18:e8:29:75:55:a2. The entire kernel partition and all used
SquashFS bytes match v3. Root authentication, hostname, SSID, both management
addresses, fresh writable overlay and consumed defaults hook were verified.
`dnsmasq` and `odhcpd` are stopped and disabled. The radio reports AP mode.
The initial180s SSH poll failed and is preserved; a later same-MAC read-only
probe reached the boot without repeating the flash or physical recovery.

The complete own firmware backup was restored through native `sysupgrade -n`.
Original SSH identity returned. Kernel/SquashFS, all selected active configuration,
patched module, host keys, protected partitions and every overlay file hash match.
The whole firmware differs in exactly one64KiB eraseblock at relative8912896
(0x880000), inside writable overlay. Its cause is UNKNOWN; do not describe this
as a byte-exact full-flash restore. This qualifies OpenWrt sysupgrade on this LAP,
not the WA native installer, a production cutover or bootloader/TFTP recovery.

Next fixed trial: reviewed WA8.7.25 PID1 shutdown hook on Loco192.168.100.195.
Minimum question: can it quiesce mounted-rootfs consumers, disable the exact
watchdog with a75s survival guard, write/read/restore only mtd3 blocks180..183,
verify complete original mtd3, relock and reboot stock with all six partition
and configuration hashes unchanged? Require three durable TCP receipts plus
independent same-identity postboot readback. Preparation uses owned RAM files
and RAM inittab only. No automatic retry or power cycle after an uncertain
handoff. Any journal/rollback/reboot ambiguity stays HOLD for physical lab recovery.

The first hook revision was blocked offline because readdir EIO was treated as
clean EOF. Failing fixtures are preserved. The minimal correction is compiled;
independent rereview and supervisor admission are required before this trial.
Panel1 physical access remains unavailable, as explicitly clarified by the
operator; no production flash/reboot has been performed.

## October19 16:43 UTC - FMX-0015 v3 native roundtrip confirmed; shutdown qualification active

Direct operator clarification after this dispatch: Panel1 is 5 km from home and
physical RESET/access to the production panel is unavailable. Lab presence applies
to the bench only. Continue bench qualification; production recovery after lost
boot remains unestablished. Do not treat presence or authorization as recovery proof.

Operator dispatch msg_f72398a9d311 was adopted explicitly by the user. Dispatch
msg_2326f258b09b confirms exclusive ownership of Loco195, LAP1.2 and Panel1 and
physical presence at Guarida/lab. This is execution authority; it does not itself
measure isolation, a successful full boot, or recovery of an unbootable Panel1.

CONFIRMED: [the current v3 native trial](../artifacts/canary_panel1_guarida/bench195_v3_roundtrip_20261019T164032Z.json)
returned exit0, `BENCH_PATTERN_AND_RESTORE_VERIFIED`, four journaled blocks,
full-original-partition verification and relock_rc0. Current binary SHA256
`1562abac663295e393ce9882e5050f8c4a3a4f13932e85ce0110b80e6b3ed140`
and candidate SHA256 `2b34379d62cff6738e769c1dd613b6e82bd3b19092be936a54d1b55d416e69a5`
were fully read back before execution. All six partition hashes and configuration
matched afterward; uptime increased and no reboot occurred. The consumed input
and verified owned RAM writer/directory are cleaned. This is bounded mechanism
evidence, not full installation or candidate-boot acceptance.

CONFIRMED: [fresh stock shutdown capture](../artifacts/canary_panel1_guarida/bench195_v3_shutdown_probe_20261019T164307Z.json)
and [init/watchdog capture](../artifacts/canary_panel1_guarida/bench195_v3_init_watchdog_readonly_20261019.json)
bind the exact WA8.7.25 scripts and current processes. Vendor fwupdate reloads the
base inittab then enters normal shutdown; rc.stop sends TERM and explicitly HUPs
the watchdog before fwupdate.real. Actual inittab has respawns. PID1 and watchdog
are BusyBox; watchdog PID258 owns /dev/watchdog. Native full-install must account
for these consumers before replacing mounted rootfs. Never reuse rc.stop blindly:
it can write cfg and delete the RAM journal. No watchdog/service mutation was
performed by these probes.

Next decisive work remains within forward-plan Phase B/C: qualify the minimum
RAM shutdown/finalization path and exact v3 boot on isolated matching LAP, with
its recovery/return route explicit. Existing LAP recovery history is bound by
radio MAC/bootloader, but the retained whole-device backup is current OpenWrt,
not a private stock dump. Prepare valid sysupgrade metadata without force or
payload changes. Obtain physical L2/RF isolation and Panel1 RESET/recovery facts
before the dependent destructive steps; continue independent preparation.

## October19 15:31 UTC - Current FMX-0015 v3 verification and RAM staging complete

Parent: forward-plan Phase B/C installation and recovery. The operator-requested
v3 verification, Panel1 RAM replacement and writer update are complete.
[The consolidated v3 receipt](../artifacts/canary_panel1_guarida/panel1_v3_preparation_20261019.json)
binds independent image review, fresh LAP hashes, code/build/tests, staging and
native memory observations. The selected image is
`panel1_firmware_lap120_proven_v3_20261019.bin`, 7077888 bytes, SHA256
`2b34379d62cff6738e769c1dd613b6e82bd3b19092be936a54d1b55d416e69a5`.
It is staged at `/tmp/fmx-panel1-2b34379d62cf/candidate.bin`.

CONFIRMED: the complete kernel and padding through 0x290000 equal the held/live
LAP firmware. Init, console character5:1, modes, owners, symlinks and base wireless
modules are preserved. The four production configuration/auth/defaults paths and
mac80211 matching the captured active file are the declared adaptations. Xattrs
and hardlink topology were outside the comparison. This establishes the compared
base equivalence, not an exact v3 hardware boot, overlay reset or DHCP shutdown.

CONFIRMED: RAM replacement completed at 15:20 UTC with full byte readback equality.
The exact v2 temporary artifact was removed after verification; both local images
remain. MemFree was 9280 KiB afterward. Stock configuration and the same four CPE
identities matched before/after; uptime increased. No flash/configuration/GPIO or
reboot operation occurred. The initial staging attempt stopped before removal
because airOS lacks stat. Its preserved failure led to reviewed ls metadata parsing
with the same owner/mode/inode/link/size/path guards. Upload and command watchdogs
also bound SSH acknowledgement waits; no guard was relaxed.

The writer now pins v3 and its new path. The first new binary's memory-only trial
returned generic exit10 without consuming the image. Minimal diagnostic logging
was added; the independent source diff confirms unchanged guards and actions.
The current C SHA is `d90b20a1...15d9`, tests `61e6f3e6...c484`, and static MIPS
binary `1562abac...d140`. The 42-fixture suite and strict host/MIPS builds passed;
independent code and final receipt reviews accepted their bounded scope.

At 15:28 UTC, the diagnostic revision's memory-only trial passed with 8476 KiB free
before locking and 8308 KiB after, preserving the 8192 KiB reserve (margin116 KiB).
Candidate/configuration/four CPEs remained equal and the temporary binary was
removed. The initial exit10 remains UNKNOWN: this later PASS does not explain it
or guarantee future admission. Both observations are retained; no further retry
was performed. Memory-only mode did not open GPIO/MTD or execute the candidate.

Decision: KEEP the verified/staged v3 and its sampled memory result. Production
cutover remains BLOCKED_BEFORE_PRODUCTION_FLASH, with authorization already
recorded. Required parent evidence remains independent failed-boot recovery,
L2/RF isolation for bench use of the production identity, full matching-LAP v3
install/boot/own-stock return, and effective protection/final reboot policy. Any
eventual installation must pass fresh memory guards. Orca result msg_d21545519535
was acknowledged in msg_33097aa9dec3 at 15:34:05 UTC; agy confirmed reading all
linked receipts. Earlier entries are historical.

## October19 14:50 UTC - Historical FMX-0015 result: read-only qualification complete

Parent remains FMX-0015 / forward-plan Phase B/C installation and recovery. The
operator released LAP192.168.1.2 and requested the next safe qualification step.
Peer msg_271947f8beca confirmed no remote RESET, serial or urescue entry while the
operator is away, and bounded this step to image comparison, switch API reads and
the reviewed memory-only preflight. That step is complete; production remains
`BLOCKED_BEFORE_PRODUCTION_WRITE`. Authorization is recorded, not pending.

[The consolidated receipt](../artifacts/canary_panel1_guarida/lap120_readonly_qualification_20261019.json)
binds the fresh live acquisition, offline comparison, switch read and Panel1 result.
All seven backup files passed size/MD5/SHA checks and cover the full 16 MiB flash
without double-counting the overlay. Fresh live LAP firmware exactly matches the
held backup (`f6b53382...b63`). This backup contains current OpenWrt; it does not
prove an airOS stock-return procedure. No LAP device change was made.

**REFUTED: byte identity between the running LAP image and selected candidate.**
The kernel payloads differ (`819b50af...ca3e` vs `bf8bde71...ec5f`), as do ath10k,
cfg80211 and 198 common file contents. The live resolved mac80211 file does match
the candidate (`19a8fde6...c416`); the immutable SquashFS copy differs by 71 bytes,
consistent with the held patched-overlay record. The loaded-module byte identity
remains UNKNOWN: the build-id/srcversion reads yielded no identity. A file match
cannot substitute for booting the complete candidate, and differences alone do
not establish incompatibility. Exact candidate boot/rollback remains unqualified.

**CONFIRMED: direct PC IPv6 access to ES-10XP API and port 0/4 observation.**
Authentication and interfaces read returned HTTP200; port 0/4 was up at 1000-full
with 24 V PoE. No PoE/VLAN/configuration operation was performed. This proves the
observed connection, not physical path independence with the LAP powered off,
a power-cycle test, or entry into bootloader recovery.

**CONFIRMED: Panel1 memory-only preparation passed at 14:47 UTC (exit0).**
The reviewed low-RAM binary (`8b31b037...cf38`) reported 8800 KiB free before
locking and 8620 KiB after, retaining the 8192 KiB reserve with 428 KiB margin.
Candidate MD5 and configuration SHA stayed identical; the same four CPE records
remained and uptime increased 17.96 seconds. The only staging was a temporary
RAM binary, removed afterward. No GPIO/MTD/config write or reboot occurred.
This clears the sampled memory-preparation question, not full-process flash
residency or future admission; installation must recheck its guards.

Independent local receipt review accepted this bounded result; no second device
trial was performed. The switch interface MAC identifies its port, not the LAP.

The failed initial LAP reader (optional authorized_keys path absent) and the
unprivileged special-inode extraction failure remain recorded. Their changes
were limited to the readers. The prior 40 fixtures and native Loco four-block
roundtrip remain valid for their exact earlier revision and bounded scope;
they were not rerun or relabeled as a full candidate boot.

Decision: KEEP these measured results; park destructive qualification until a
usable independent recovery route and L2/RF isolation are present. The selected
candidate retains the production IP and RF identity. Remaining work is the exact
LAP install/boot/own-stock rollback, independent Panel1 recovery if OS management
never returns, and effective protection/final reboot policy. No safety exception,
flash, reboot, PoE toggle or wider network audit is implied by this checkpoint.
Orca result msg_fe6a23801e07 was received and its linked receipts read by agy,
confirmed in msg_acb2032a17b3 at 14:53:59 UTC.
Earlier dated sections below are historical evidence, not current instructions.

## October19 14:25 UTC - Historical FMX-0015 result: low-RAM bench PASS, cutover BLOCKED

Parent: FMX-0015 / forward-plan Phase B/C installation and recovery. The operator
asked to adapt the writer for low RAM, validate locally and on 192.168.100.195,
inspect the tower gateway read-only, and report through Orca. This bounded subtask
is complete. The production cutover remains `BLOCKED_BEFORE_PRODUCTION_WRITE`.

### Question, implementation and measured answer

Can the writer avoid a second 6.75 MiB preimage allocation while preserving undo of
all overwritten blocks? **CONFIRMED for local fixtures and the bounded native trial**:
`install_image_lowram` reuses the resident shared tmpfs candidate as an undo journal.
It copies each new block to a 64 KiB buffer, records the original block before erase,
and restores the entire recorded prefix on failure. Two 64 KiB buffers replace the
second full image allocation. The real 8192 KiB free-memory reserve after mlock remains.
This behavior belongs to the native userspace writer plus the existing airOS GPIO/MTD
interfaces; it is not a wireless improvement or a new kernel mechanism.

The source `41353394...f361`, tests `6090817a...1c28` and static MIPS binary
`8b31b037...cf38` are bound to
[the low-RAM qualification receipt](../artifacts/canary_panel1_guarida/fmx_flash_writer_lowram_qualification_20261019.json).
Fresh coordinator and independent fixture runs each passed 40 tests (exit 0).
Native memory preflight passed with 12464 KiB free before pinning and 11872 KiB
after pinning: 3680 KiB above the retained reserve, below the old 15104 KiB floor.
The preflight did not open MTD/GPIO or consume the candidate.

The actual bench is NanoStation 5AC loco `0xe7fa`, MAC `FCECDAC2540A`, not the LBE
initially named by the peer. Exact SSH/board/ABI/full-partition/tail pins were checked;
agy corrected its description and confirmed exclusivity in `msg_b52ba6e38e30`.
A single `bench195_lowram_roundtrip` wrote/read-verified a differing pattern in mtd3
blocks 180-183, restored all four, and verified the full original mtd3 SHA (exit 0).
All six partition MD5s and the configuration SHA matched their pre-test values.
Uptime advanced 60.02 seconds; stock WA.v8.7.25 remained running without reboot.
Owned temporary candidate/binary files and directory were removed after acceptance.
The independent final check audited these receipts and backups; it did not repeat
the physical measurement. The exact LAP candidate was never installed on this Loco.

### Preserved failures and limits

The first read-only bench guard rejected the peer's incorrect LBE identity assumption;
its failed receipt remains. Review found an automatic second restore attempt and a
redundant re-unlock after bench relock failure. Both were corrected before hardware,
with regression tests; the rejected local binary and earlier fixture failure remain
recorded. No failed result was converted into a pass by repeating an unchanged run.
The original task6948 still proves only four blocks under the earlier writer.

This native result qualifies the bounded memory/journal mechanism, not a complete
candidate boot, active-rootfs overwrite, effective hardware relock, power-loss recovery
or production readiness. The final protection/reboot sequence remains unqualified.
The earlier Panel1 observation (9292 KiB MemFree) applies to the old full-buffer guard;
it is not proof that the new low-RAM guard passes or fails on production.

### Remaining parent criteria and next executable condition

The matching LAP 192.168.1.2 remains untouched. Per `msg_028c43127859`, it is the
EP-R6/VLAN99 jump host and the PC's sole path to the switch controlling its own PoE.
Its full cycle is parked until released; then establish its own backup/return recipe
and verified L2/RF isolation before booting the exact image with production IP/SSID.
Do not substitute the Loco result for this matching-LAP criterion.

Agy confirmed independent remote Panel1 recovery as **UNKNOWN** in `msg_66127aea9e72`.
The authorized read-only observation found default gateway 10.10.100.1 on br0 and ARP
18:fd:74:06:b0:cb, with four CPEs still present. This identifies a route/neighbor only;
it does not establish a PoE controller, usable port or recovery when Linux fails.
See [the parent cutover result](../artifacts/canary_panel1_guarida/panel1_cutover_result_20261019.json).
Production authorization is already recorded; no repeat approval is requested.
No hardware runner remains active for this coordinator. Historical entries below
are evidence, not instructions to resume parked work or relax these criteria.

<!-- doc-head: October19 exact updater GPIO mechanism and negative tail-block trial -->
Exact WA.v8.7.25 updater uses a GPIO/SPI chip-protection control plane outside MTD.
Bench192.168.100.195 erase/write returned success but changed-pattern readback failed.
All six final partition hashes and the original cleanmarker remain unchanged.
This bench task used no vendor unlock, bootloader write, RAM patch, reboot or production access.
Protection baseline/readback is missing; safe unlock and installation stay unqualified.
<!-- /doc-head -->

## October19 - FMX-0015 identify GPIO protection; retain failed write acceptance

KEEP the exact vendor control-plane finding: on this bench the absent sysfs
state node makes ubntbox use GPIO ioctl11 and local ubnthal flock_set. It changes
chip-wide SPI status protection and GPIO0 under the kernel SPI semaphore; no
u-boot data write is required by this mechanism. Ordinary MEMUNLOCK failure is
ignored, and the examined MTD wrappers have ordinary permission/range checks.

REJECT acceptance of the direct-char block180 trial: its erase/write calls
returned success but its changed pattern never appeared. The original marker
and all six full-partition hashes remained unchanged. Matching final original
digest is retained as preservation evidence, not a changed-block restore test.
The earlier negative ordinary-ioctl result remains valid and separate.

BLOCK vendor unlock until fresh SPI status and GPIO0 mux/OE/control/output
baseline can be obtained safely and exact protection restoration verified.
The reviewed setter has no status getter or verified return, overwrites fields,
and cannot preserve an unknown baseline by assumption. Do not issue another
flash trial, guess RAM fields, write bootloader data or infer installation
authority from this mechanism. Current silent-write cause remains UNKNOWN.
No production access or physical operator action follows from this result.
Receipt: [bounded result](../artifacts/canary_panel1_guarida/fwupdate_unlock_mechanism_20261019.json).

Independent coordinator review (gpt-6.1-sol/high) confirms the updater tail-call
association and chip-wide protection scope. No serialized status getter exists
in the inspected interface; the private reader is only called inside the setter
and contains an unbounded wait. A new in-kernel reader would need exact runtime
ABI/state binding and a separately authorized bench qualification; fixtures alone
cannot establish its hardware safety. No such instrument was built or loaded.

<!-- doc-head: Panel1 safety closure, recovered agy evidence and qualified negative MTD result -->
03:17 UTC production readback: stock AP, four CPEs, six partitions/config unchanged.
Full agy log confirms RAM-only approval; current coordinator performed device reads only.
Bench ordinary unlock is unsupported; flash hashes and original RAM flags reconciled.
Local fixes pass 68 tests; exact AP installation/restore remains unqualified.
<!-- /doc-head -->

## October 19, 03:27 UTC - Preserve remote-operation scope and block unqualified cutover

KEEP verified existing bench interop and the recovered full-session authorizations. Correct
screen-only approval claims and the all-passing L2-matrix implication. Preserve tagged VLAN
failure without applying it to the separately audited untagged routed production topology.

KEEP the external worker's negative ordinary-ioctl result and independent coordinator state
readback. Do not try updater `-o`/`-u`, the bootloader-writing legacy installer or guessed RAM
fields as a shortcut. Exact AP install/stock restore, candidate boot and CPE stock-mode return
remain acceptance gaps. Nobody onsite is an operator condition, not a request for a visit.
The existing remote recovery route needs proof; local helper tests cannot replace it.

The current coordinator has not written to devices. External authorized bench tmpfs/probe
operations are recorded separately. The explicit production cleanup question is still pending;
no timeout or generic status message is treated as approval for a new device action.

## October19 - FMX-0015 MTD capability negative, installation remains blocked

KEEP the fixed-address bench-only helper and exact original block acquisition.
REJECT using ordinary MEMLOCK/MEMUNLOCK as a qualified installation route on
this exact WA.v8.7.25 ath_flash implementation: native probes returned
EOPNOTSUPP for both kernel and rootfs, matching absent master callbacks.

Do not erase the proposed rootfs tail block when restoration/relock cannot be
qualified, guess a RAM field, modify shared chip protection or invoke the old
bootloader-writing updater. Existing partition writable flags do not explain
or cure the prior silent write. Retain that cause as UNKNOWN.

BLOCKED is the research result; no flash bytes changed, and no write/restore
success is claimed. New acquisition requires an evidenced reversible scoped
mechanism and recovery recipe. No production access, flash approval, unrelated
experiment resumption or physical operator action follows from this task.

<!-- doc-head: Panel1 safety preparation and complete agy session reconstruction -->
Offline recovery/health fixes pass 68 fixture tests; independent review is bounded to local code.
The exact held stock firmware region is prepared and hashed, not restore-tested.
Operator confirms nobody is onsite; qualify the existing remote plan from its actual evidence.
Full agy transcript confirms RAM-only approval; current coordinator performed device reads only.
<!-- /doc-head -->

## October 19 - Reuse actual remote bench proof; keep local safety fixes bounded

KEEP the existing AC1 evidence of reboot/authentication/datapath and 35-second AP-outage
survival; the four production CPE hooks match the documented 1994-byte command exactly.
Do not discard these tests or claim an unlocated receipt means an experiment never occurred.
The operator confirms nobody is onsite. Recover the complete agy session and qualify the
intended remote installation/recovery path against actual commands and receipts.

KEEP offline fixes that reject incomplete recovery/health evidence and pin exact payloads.
Their process-local locks and simulated adapters do not authorize unattended production
recovery. Keep the stock recovery artifact separate from factory/TFTP containers and from
restore acceptance. Original explicit device-write and irreversible-action approvals remain.
Do not deploy an untested replacement CPE hook merely because review found additional cases.

## October 18, 23:24 UTC - Preserve service; do not promote staging into flash authority

KEEP the stock production service and all successful/failed receipts. Gemini's RAM transfer
is confirmed, but an operator OK is not visible. Do not infer approval from a retry request,
successful copy, or the fact that another agent already wrote to the device.

PARK the v2 uploader: its reclaimable-memory estimate and removed post-copy raw-free floor
are unqualified. The actual successful samples also pass the original gates, so do not claim
that relaxing the threshold was necessary for that transfer. Do not rerun either uploader.

RECOMMEND exact cleanup of the retained 6.75 MiB candidate once specifically authorized;
preserve the local image and remove the remote directory only if empty. Verify memory,
absence, identity and the four-client roster afterward. No reboot is needed for cleanup.
The original explicit device-write gate remains active. Flash additionally requires the
exact installation/recovery path and independent qualification; no safety requirement is waived.

## October 18 ? Panel1 takeover: keep current service, separate staging from flash

KEEP the current stock service while preparing the explicitly requested canary. Fresh readback
confirms four associated CPEs and their hardened dormant hooks. Preserve old receipts even where
fresh evidence supersedes an earlier cron length or preparation state.

REJECT use of `install_openwrt_ddunlock.py --go` on this production AP: its lab-only guards
exclude this firmware/client state, and its vendor u-boot bytes differ from this AP's backup.
No permission to modify protected partitions or relax these guards is inferred from the handoff.
The direct-RAM lock method remains unqualified, not a ready replacement.

KEEP the locally corrected v2 candidate for review/staging only, with the existing AP credential
hash replacing blank root authentication. Independent content/mode verification is not a boot test.
KEEP a separate uploader whose authority is limited to its fixed tmpfs directory/file and exact
cleanup. First device write awaits operator OK; every irreversible operation requires fresh approval
as explicitly requested. Firmware rollback and physical recovery remain requirements before flash;
`fmx_watchdog.sh` only reverts tuning and cannot satisfy firmware recovery by itself.

Full evidence: [takeover record](../artifacts/canary_panel1_guarida/TAKEOVER_20261018.md).

## October 18 — Stage 10 Stock `airOS 8` (`5AC`, `WA.v8.5.12` & `WA.v8.7.25`) Interoperability, Rollback & Cold-Boot Persistence Decisions (`KEEP` / `REJECT`)

Based on physical Stage 10 measurements on the bench (`OpenWrt LAP-120 AP <-> Stock airOS 8.5.12 & 8.7.25 NanoStation 5AC Loco + Stock airOS 6.1.4 LiteBeam M5`):

1. **`KEEP` — 2-Sided Stock `airOS 8` (`5AC`) $\leftrightarrow$ OpenWrt AP Interoperability Architecture (`FMX-0015`)**:
   - Enables stock `airOS 8` (`WA.v8.5.12` and **`WA.v8.7.25`**) `5AC` CPEs to associate at full `802.11ac` (`VHT80` `526.5–650.0 MBit/s` / `VHT20` `173.3 MBit/s`), remain connected indefinitely, and pass `134.0–147.0 Mbps` TCP uplink, `78.8 Mbps` TCP downlink, `83.6–85.0 Mbps` UDP downlink, and `1.1–1.4 ms` avg RTT alongside stock `airOS 6` (`M5`) and `MikroTik` (`ath9k`) CPEs on a single OpenWrt AP:
     * **On OpenWrt AP (`mac80211.ko`, `MD5: 6c869e80d4748753727192be08b7bbe6`)**: Patch `ieee80211_rx_mesh_data` (`.text + 0x033c18..0x033c68`, 21 instructions) to strip the 14-byte outer `0x6558` (`ETH_P_TEB`) header and clear `skb->ip_summed` whenever `*(u16 *)(skb->data + 12) == 0x6558`. Persist directly in `/lib/modules/6.6.110/mac80211.ko` on `/overlay`.
     * **On Stock `airOS 8` CPE (`ubnt_poll_host.ko`)**: Patch 3 instruction words (`is_ap_valid` = `24020001`, `timer_30s` = `10000006`, `bmiss_2s` = `00000000`) dispatched automatically by module file size (`SZ=186528` for `8.5.12`, `SZ=186560` for `8.7.1–8.7.4`, `SZ=189880` for `8.7.22–8.7.25` across both `WA` and `XC`), and set `is_ubnt_ptp=0`, `addradio` mode `0`, and `wds=0`.
2. **`KEEP` — Universal `system.cfg` `cron.1.job.1.cmd` Cold-Boot Persistence on Stock `airOS 8` (`WA`/`XC` `8.5.12` through `8.7.25`, Bypassing `/sbin/uav`)**:
   - Because `/init` on `airOS 8` runs `/sbin/uav` before `/sbin/ubntconf` and deletes custom scripts in `/etc/persistent/` containing `mount` (`uav: Removing ... as potentially malicious`), and standard (non-`CS`) firmware builds ignore `/etc/persistent/rc.poststart`, persist the in-RAM `SZ=$(wc -c < $O)` + `dd` + `awk` module patcher directly inside `cron.1.job.1.cmd` in `/tmp/system.cfg` (`cfgmtd -w -p /etc/ -f /tmp/system.cfg`). Verified hands-free across cold reboots on both **`WA.v8.5.12`** and **`WA.v8.7.25`**.
3. **`REJECT` — AP-Only `airMAX AC` Beacon Vendor-IE Spoofing Without CPE `ubnt_poll_host.ko` Unlock**:
   - Even if an OpenWrt AP broadcasts Ubiquiti's `airMAX AC` vendor IE in its beacons so an unpatched `airOS 8` CPE passes `ubnt_poll_host_is_ap_valid`, the unpatched `airOS 8` CPE enters TDMA polling mode (`addradio` mode `1`), suppresses normal CSMA TX queues waiting for proprietary TDMA polls, and triggers a hard `80211_Stop` disconnect after 30 seconds (`0x00791c`). Therefore, the lightweight SSH `system.cfg` `cron` unlock on the `airOS 8` CPE is required and eliminates the need to flash custom firmware onto `5AC` CPEs.
4. **`KEEP` — Proven OpenWrt $\to$ Stock `airOS 8` (`WA.v8.5.12` -> `WA.v8.7.25`) Direct `mtd3` Rollback Recipe (`FMX-0002-REVERT`)**:
   - Extracting the `kernel` (`1,004,139 B` at `0x9f050000`) and `rootfs` (`11,927,552 B` at `0x9f150000`) partitions from official `WA.v8.5.12.40181.190213.1104.bin` into a contiguous `0x100000`-padded image and writing to `/dev/mtd3` (`firmware`) cleanly restores stock `airOS 8` in one reboot without touching `u-boot` or `ART`, after which `/sbin/fwupdate.real -m` upgrades cleanly to official **`WA.v8.7.25`**.
5. **`KEEP` — `WPA2-PSK (CCMP)` `allow_80211=1` Unlock & Strict Lab-Bench-First Qualification Policy (`Option A`)**:
   - Include `sed -i '/allow_80211/d;s/ap_scan=1/ap_scan=1\nallow_80211=1/' /etc/wpasupplicant_*.conf` and `echo 0 > /proc/sys/dev/uph_wifi0/enable` in `cron.1.job.1.cmd` so stock `airOS 8` (`WA.v8.7.25`) CPEs complete `WPA2-PSK (CCMP)` 4-way handshakes (`wpa_state=COMPLETED`) on both `VHT80` (`120.0 Mbps` UL / `79.5 Mbps` DL) and `VHT20` (`20 MHz`, `173.3 MBit/s` `VHT-MCS 8` 2x2, **`78.7 Mbps` TCP UL [`93.2 Mbps` peak, `0` retrans]** / **`63.6 Mbps` TCP DL [`74.2 Mbps` peak]**, **`3.94 bit/s/Hz` UL spectral efficiency**).
   - Keep production panels (`Panel1-Guarida` `10.10.100.84` and its 4 CPEs) 100% untouched on stock configuration (`NO_CRON_LINES` restored) until all lab bench rehearsals and AP rollback tests are completed and the operator explicitly schedules a field window.
6. **`KEEP` — Near-Future Expansion Track 1: `XC` Platform (`Rocket Prism 5AC Gen2` `RP-5AC-Gen2` & `PrismStation 5AC` `PS-5AC`) Bench Bring-Up (`Stage 11A`)**:
   - The operator has a physical `Rocket Prism 5AC Gen2` (`XC`, `board.sysid=0xe7e9`, `QCA9558 720 MHz`, `128 MB DDR2`, `QCA9880` main 5 GHz + `wifi1` AirView radio + hardware **AirPrism** active RF filter ASIC) ready to connect to the lab bench.
   - Pursue two parallel engineering tracks on the bench `Rocket Prism 5AC Gen2`:
     * **Track 1A (Stock `XC.v8.7.25` / `XC.v8.7.4-cs` Unlock & Hybrid Controller)**: Leverage the confirmed `189,880`-byte `ubnt_poll_host.ko` offset parity between `XC.v8.7.25` and `WA.v8.7.25` (`S1=30784, S2=30788, S3=31820, C3=10156, S4=41980`) while keeping Ubiquiti's native AirPrism filter daemon active on the `720 MHz QCA9558` host.
     * **Track 1B (OpenWrt `ath79` + AirPrism Filter Control Driver)**: Reverse-engineer the exact GPIO/SPI/register sequence that `XC.v8.7.25` uses to tune the AirPrism active filter when `center.1.freq` and `chanbw` change so an OpenWrt port on `RP-5AC-Gen2` retains full AirPrism adjacent-channel rejection.
7. **`KEEP` — Near-Future Expansion Track 2: Ubiquiti `LTU` (`LTU-Rocket` `aflturocket` & `LTU-Lite`/`LR`/`Pro` `afltu`) Firmware Modification & `4096-QAM` (`12x`) Unlock Investigation (`Stage 11B`)**:
   - Operator directive (2026-10-18): Expand FuturaMAX scope in the near future to include the **Ubiquiti LTU family** (`141` `LTU-Lite` CPEs and `5` `LTU-Rocket` APs in the operator's UISP fleet running `v2.4.1` / `v2.4.2`).
   - Specifically investigate why **`4096-QAM` (`12x` modulation)** — promised by Ubiquiti for 5+ years and visible as a disabled/locked option in the UI/firmware — was never enabled by Ubiquiti, determine whether the LTU custom silicon/FPGA/DSP tables in `aflturocket-2.4.2` and `afltu-2.4.2` contain the `12x` (`4096-QAM`) constellation/coding paths, and identify what modulation, scheduler, queue, and RF improvements can be unlocked on LTU hardware.

## October 17 — Stage 9 `20 MHz` (`VHT20`), `FMX-0009` Rate-Mask, `FMX-0013` `CoTSQ`, and `procd` Watchdog Decisions (`KEEP` / `REJECT`)

Based on physical Stage 9 measurements ([`artifacts/stage9_ptmp/stage9_ratemask_20mhz_and_pacing_results.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/stage9_ptmp/stage9_ratemask_20mhz_and_pacing_results.json), [`docs/STAGE9_20MHZ_RATEMASK_COTSQ_AND_PROCD.md`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/STAGE9_20MHZ_RATEMASK_COTSQ_AND_PROCD.md)):

1. **`KEEP` — `VHT20` (`20 MHz`) Channel Width for High-Density / Obstructed-CPE / Multi-Sector WISP Towers (`FMX-0010-20MHZ`)**:
   - On towers where spectrum reuse (`20 MHz` per sector across 17 sectors) or NLOS/obstructed `802.11n` CPEs govern performance, `VHT20` increases obstructed `MikroTik SXT Lite5` standalone DL by **`3.05x` (`20.15 -> 61.44 Mbps` at `MCS 14`)**, cuts its loaded median RTT by **`18.9x` (`72.10 -> 3.81 ms`)**, raises 3-station simultaneous Downlink **Jain fairness from `0.6867` (`80 MHz`) to `0.9531`**, and achieves **`3.342 bit/s/Hz` DL** (`2.88x` vs `VHT80`) and **`3.656 bit/s/Hz` UL** spectral efficiency with **`3.36–4.58 ms` loaded median RTT** across all 3 stations. Use **`VHT40` (`40 MHz`)** when higher raw sector Downlink capacity (`105.18–110.68 Mbps`) is required and 40 MHz of clean spectrum is available.
2. **`REJECT` — Runtime Multi-Rate `iw dev phy0-ap0 set bitrates ...` Clamping as a Live Fast-Loop Control Knob on `10.1-ct` (`FMX-0009`)**:
   - `ATH10K_DBG_BUFFER` (`0x2002`) hex dumps proved that while `ath10k-ct` translates `iw set bitrates` into `WMI_PEER_ASSOC_CMDID` (`reassoc=true`) with updated rate bitmaps (`0x0F0F`, `0x000F`, `0xFFF0`), the QCA988x `10.1-ct-8x-__fW-022` firmware ignores `reassoc=true` rate-set narrowing on already-associated peers and continues stepping up to the peer's original association IE ceiling. Use **Channel Width (`VHT40`/`VHT20`)**, **TX Power (`11–22 dBm`)**, and **AQL/Airtime Weights** instead.
3. **`KEEP` — OpenWrt CPE `CoTSQ` (`tcp_limit_output_bytes = 131072`) + Station Egress `fq_codel` (`quantum 300`, `target 5ms`, `interval 50ms`) (`FMX-0013`)**:
   - Increases 3-station simultaneous Uplink goodput to **`181.90 Mbps`** (`Loco 5AC` rises `+8.8%` from `130.40 -> 141.93 Mbps` with `0` TCP retransmits) while reducing `LiteBeam M5` `p99` loaded RTT by **`3.14x` (`49.6 -> 15.8 ms`)** and `MikroTik SXT` median RTT to **`5.58 ms`**.
4. **`KEEP` — Production OpenWrt `procd` Service ([`controller/futuramax.init`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/futuramax.init)) + Canary Rollback Watchdog ([`controller/fmx_watchdog.sh`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/fmx_watchdog.sh)) (`FMX-0014`)**:
   - Supervises `fmx_adaptive_controller.sh` and `fmx_watchdog.sh` with automatic respawn and automatic rollback to stock AQL/airtime defaults if `MemAvailable < 8192 kB` or `phy0-ap0` health fails.

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
