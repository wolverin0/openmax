<!-- doc-head: STAGE42B_STAGE47B_LTU_OTA_1024QAM_AND_POSTSTART_VERIFIER.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

[Document router](STAGE42B_STAGE47B_LTU_OTA_1024QAM_AND_POSTSTART_VERIFIER.md) | Part 2/2
<a id="stage42b-stage47b-ltu-ota-1024-qam-claim-and-poststart-verifier"></a> [Stage42B Stage47B LTU OTA, 1024-QAM claim and poststart verifier](STAGE42B_STAGE47B_LTU_OTA_1024QAM_AND_POSTSTART_VERIFIER_CONTINUATION_73c6a5a44d_001.md#stage42b-stage47b-ltu-ota-1024-qam-claim-and-poststart-verifier) | <a id="saved-association-evidence"></a> [Saved association evidence](STAGE42B_STAGE47B_LTU_OTA_1024QAM_AND_POSTSTART_VERIFIER_CONTINUATION_73c6a5a44d_001.md#saved-association-evidence) | <a id="saved-data-plane-metrics-and-their-limits"></a> [Saved data-plane metrics and their limits](STAGE42B_STAGE47B_LTU_OTA_1024QAM_AND_POSTSTART_VERIFIER_CONTINUATION_73c6a5a44d_001.md#saved-data-plane-metrics-and-their-limits) | <a id="flash-persistence-is-not-a-standalone-cold-boot"></a> [Flash persistence is not a standalone cold boot](STAGE42B_STAGE47B_LTU_OTA_1024QAM_AND_POSTSTART_VERIFIER_CONTINUATION_73c6a5a44d_001.md#flash-persistence-is-not-a-standalone-cold-boot) | <a id="held-firmware-generation-chain"></a> [Held firmware generation chain](STAGE42B_STAGE47B_LTU_OTA_1024QAM_AND_POSTSTART_VERIFIER_CONTINUATION_73c6a5a44d_001.md#held-firmware-generation-chain)

<!-- stage822a-payload-begin -->
the actual Stage47B boot generated the correct two files remains UNKNOWN.
Static-file hashes are retained in validation. No firmware binary was executed.

## Routing: same switch versus standalone PoE

The scripts add the same192.168.100.x/24 management address on both br0 and br1,
and add198.18.0.84/.55 on br0. Comments describe eth0.1/eth0.2/ath0 membership;
comments are not bridge-port readbacks. The10.10.111.x addresses are attempted
on ath0, but the artifact contains no `ip route`, policy-rule, neighbor,
bridge/VLAN or wired-port isolation capture.

Linux may answer ARP for an address assigned to another interface, depending
on configuration. Disabling global arp_filter/rp_filter does not isolate an
RF path; interface-specific settings also matter. This follows the official
[Linux IP sysctl documentation](https://docs.kernel.org/networking/ip-sysctl.html#arp-filter-boolean),
not an assumption about the exact running LTU kernel. Wired br0 reachability,
an ath0 IP label, low ping or a role=Run label alone cannot identify the medium.

`verify_routing_separation` checks explicitly supplied per-radio boot/device
identity, complete declared interface inventories, canonical IPv4 addresses,
bridge-master graph, direct main-table ath0 routes with correct source/peer,
reachable reciprocal MAC neighbors and explicit flow device binding. Any
198.18.0.147/24 address on a non-ath0 interface fails this conservative policy.
The policy covers its declared topology only; it is not a complete Linux FIB
or policy-routing interpreter and cannot authenticate inventory completeness.

For SAME_SWITCH, even internally consistent snapshots return
UNQUALIFIED_SAME_SWITCH. For STANDALONE_POE, all declared wired data interfaces
must have carrier=false, including eth0; an ath0 bridge master is allowed only
within the supplied unambiguous graph. Passing these fixture predicates returns
SUPPLIED_STANDALONE_CONSISTENT with native_ota_path_qualified=false. Physical
LAN isolation and a real two-endpoint flow/capture are still missing.

## Cold-boot evidence validator and acceptance gap

`verify_cold_boot_evidence` checks one unit at a time: exact MAC, distinct old/new
boot IDs, native build/evidence hashes, persisted poststart hash equal to the
frozen literal, explicit power-cycle and no-wired-data flags, observed hook,
exit0 and final readback after the last driver start. Ordered same-boot events
must cover COLD_BOOT→CONFIG_GENERATED→POSTSTART_EXECUTED→FINAL_READBACK.
Both generated paths need same-boot hashes and observed-after-poststart flags.
Final supplied readback must have FMX-LTU, correct role/ath0 address,5500/20MHz,
power15 and one peer; CPE additionally needs preferred SSID and alternating
scan list. The AP need not declare that CPE scan recipe.

These are necessary supplied-evidence consistency predicates, not a proof that
the code deterministically restores every possible cold boot. A passing fixture
always keeps native_authenticated, deterministic_restore_proven,
relocation_accepted and native_dispatch_allowed false. The actual source lacks
this evidence and remains BLOCKED/UNKNOWN for cold-boot standalone acceptance.
No native poststart changes or device-ready replacement scripts are produced.

To qualify relocation later requires identified builds/modules and persisted
poststart/config readbacks for both units, fresh unattended cold-boot logs with
generated config contents/order and final SSID/address/association, plus physical
wired-data isolation and reciprocal source-bound route/neighbor/bridge/flow
evidence over ath0. This is a missing-evidence list, not authorization to collect
it. No physical operator action is required to finish this offline audit.

## Verification disposition

Fresh focused pytest: **252 passed in0.39s, exit0**. The initial250PASS/exit0
is preserved; it used the earlier module revision. The final run covers two
added missing-field regressions after `master`/`via` became explicitly required.
No failed pytest attempt occurred. An existing pytest_asyncio fixture-scope
deprecation warning is unrelated. Both revision-bound receipts are in validation.
Independent review corrected the report's overstatement about persisted
preferred-SSID and identified the same missing-field guard gap, now repaired.
Independent review remains separate from implementation. Source/report/literal
integrity, software acceptance and physical acceptance are separate results.
Only the new pure test path is executed. No existing physical benchmark tests,
target runners or deployment imports are used. Final counts and the frozen
independent review govern closure; no next task or live acquisition is started.
<!-- stage822a-payload-end -->
