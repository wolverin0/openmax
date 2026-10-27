<!-- doc-head: STAGE32B_OPENWISP_CENTRAL_CONTROLLER_AND_HYBRID_BRIDGE.md continuation 1 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE32B_OPENWISP_CENTRAL_CONTROLLER_AND_HYBRID_BRIDGE.md) | Part 1/3
<a id="prepared-controller-compose"></a> [Prepared controller Compose](STAGE32B_OPENWISP_CENTRAL_CONTROLLER_AND_HYBRID_BRIDGE_CONTINUATION_0248f07ca7_002.md#prepared-controller-compose) | <a id="local-usage"></a> [Local usage](STAGE32B_OPENWISP_CENTRAL_CONTROLLER_AND_HYBRID_BRIDGE_CONTINUATION_0248f07ca7_002.md#local-usage) | <a id="verification-and-retained-findings"></a> [Verification and retained findings](STAGE32B_OPENWISP_CENTRAL_CONTROLLER_AND_HYBRID_BRIDGE_CONTINUATION_0248f07ca7_002.md#verification-and-retained-findings) | <a id="research-state-and-decision"></a> [Research state and decision](STAGE32B_OPENWISP_CENTRAL_CONTROLLER_AND_HYBRID_BRIDGE_CONTINUATION_0248f07ca7_002.md#research-state-and-decision)

<!-- stage822a-payload-begin -->

OpenWISP 26.09 API contracts govern controller inventory, templates and monitoring.
Eight profiles include the source-reported Stage31A Champion v8.
Stock devices remain hybrid inventory/telemetry targets without a native OpenWrt backend.
Templates hold ordered profile data; radio execution and rollback remain unqualified.
Fresh scoped pytest:56 passed; independent review PASS_WITH_LIMITS, zero open blockers.


# Stage32B: OpenWISP central controller and hybrid bridge

Task: T-S32B-CODEX-OPENWISP-CONTROLLER-BRIDGE-AND-TEMPLATE-PACK.

## Prespecified scope and acceptance

Parent deliverable: external controller, telemetry and safe experiment orchestration
in the original artifacts/2026-09-20-forward-plan.html and the control-authority
boundary in docs/BENCH_PLAN.md. The operator explicitly prioritizes this additive
integration; this does not resume any RF experiment or change E2 acceptance.

Question: can the existing eight Golden Profiles and observed hybrid-device data be
represented through real OpenWISP APIs without inventing a stock configuration
backend, losing command order, imputing telemetry or claiming a qualified rollback?

Existing evidence: inspected controller/openwisp_netjson_rollback_agent.py,
controller/multiradio_golden_profile_applicator.py and the Champion ledger.
The existing exporter is OpenWISP-inspired; its custom layers and watchdog assertions
are not independent proof of native schema compatibility or exact restoration.
The current profile source and ledger agree at inspection, including S31A-R1.

Minimum missing evidence: an explicit REST/transport contract, eight source-bound
native NetJSON file templates, truthful stock telemetry conversion, a complete
versioned controller Compose definition, fixture verification with the requested
test module, independent review and Command Center regeneration.

Stop after these software deliverables. No controller API writes, device registration,
container launch, SSH, radio access, firmware export, flash or live profile application
is performed by this task. Construction/import/default CLI must remain offline.

Architecture review follows new-app-grill and STACK-DECISION-FRAMEWORK.md using the
operator's explicit Python/OpenWISP/Docker selection. This extends the existing Python
controller; there is no new product, frontend, provider, global configuration or
device-side daemon.

## Delivered behavior

The new controller/openwisp_controller_api_bridge.py provides a standard-library
OpenWISPClient, an offline eight-profile template exporter and a stock telemetry
translator. Importing the module and running its default CLI never contacts a
controller or a radio. Existing controller source and the live ledger are not edited.

The client supports user-token authentication, device and template listing/detail/
creation/update/deletion, inventory registration, idempotent template synchronization,
template assignment that preserves existing configuration/context, binary configuration
downloads, device-metric listing, DeviceMonitoring ingestion and the native OpenWrt
registration/checksum/download/status protocol. A generic scoped request method also
supports GET/POST/PUT/PATCH/DELETE under the documented API roots.

All mutations require an explicitly constructed allow_writes=True client. HTTPS
certificate verification is retained; optional HTTP is confined to an explicit
localhost development exception. Credentials never cross an HTTP redirect or a
pagination origin/resource boundary. Pagination retains organization filters and
has page/object/byte limits. GET retries are bounded; writes are never automatically
retried. A lost write response reports ambiguous_write rather than asserting success.
Partial template-sync failures retain completed profile/id/action receipts and the
failed profile ID; they do not invent a transactional rollback.

## Actual upstream contract

The implementation targets the documented OpenWISP 26.09 API and Docker release
26.09.1. Research resolved the 1.3 source branches to controller
78be3e9d25e7a322e66ef776f11c147c29cfff8a, monitoring
5dcc9589948043d9a1455402a1c4664f04506acd and netjsonconfig
9b32477620348bf86976dfe0fef67f5ac335b9fd. These source references are not a claim
about the exact dependency digests installed inside an unlaunched container.

| Operation | Wire contract |
| --- | --- |
| User authentication | POST /api/v1/users/token/; subsequent Authorization: Bearer token |
| Inventory and templates | Singular /api/v1/controller/device/ and /api/v1/controller/template/; detail adds UUID/ |
| Assign templates | PATCH device detail with nested config; preserve existing template IDs, backend, context and configuration |
| Rendered configuration | GET device/{uuid}/configuration/ returns archive bytes |
| Monitoring ingestion | POST /api/v1/monitoring/device/{uuid}/?key=device_key; no user Bearer substitution |
| Observation time | Optional monitoring query time uses UTC DD-MM-YYYY_HH:MM:SS.ffffff |
| Native OpenWrt registration | POST form to /controller/device/register/ with organization secret/name/MAC/backend; response is text with UUID/key |
| Native agent polling/status | /controller/device/checksum/{uuid}/, download-config/{uuid}/ and report-status/{uuid}/; device key in query/form |

Sources: [controller REST reference](https://openwisp.io/docs/26.09/controller/user/rest-api.html),
[controller serializers](https://github.com/openwisp/openwisp-controller/blob/78be3e9d25e7a322e66ef776f11c147c29cfff8a/openwisp_controller/config/api/serializers.py),
[native agent views](https://github.com/openwisp/openwisp-controller/blob/78be3e9d25e7a322e66ef776f11c147c29cfff8a/openwisp_controller/config/controller/views.py)
and [monitoring views](https://github.com/openwisp/openwisp-monitoring/blob/5dcc9589948043d9a1455402a1c4664f04506acd/openwisp_monitoring/device/api/views.py).

Native device configuration uses netjsonconfig.OpenWrt. The similarly named
netjsonconfig.OpenWisp targets legacy OpenWISP 1.x firmware; it is not a generic
airOS/LTU backend. Hybrid stock airOS8/airOS6/LTU/airFiber registration therefore
creates an inventory device without an OpenWrt config. It neither installs an agent
nor assigns an incompatible template. Native OpenWrt registration creates a native
configuration but does not assign a Golden Profile automatically. Inventory registration
reuses an existing exact organization/MAC identity and rejects duplicate identities.

## Eight templates and Champion v8 cutoff

The local pack is artifacts/openwisp_templates/manifest.json plus one JSON REST
template payload for each profile:

- af4x_invictus
- ltu_lite_amesoc
- r2ac_prism_ap
- r5ac_prism_sta
- pbm5_xw_weak_ota
- openwrt_lap120_ptp_1cpe_champion
- openwrt_lap120_ptmp_multicpe_champion
- ltu_ptmp_3unit_sector_champion

Each template is type generic, backend netjsonconfig.OpenWrt, default=false and
required=false. The offline organization is null; sync_templates supplies the
explicit target organization. Stable names FMX <profile_id>, an ownership note and
an exact payload comparison make repeated syncs idempotent. Unowned collisions
or duplicate template names stop synchronization; unrelated templates are not pruned.

The template config is a native DeviceConfiguration containing exactly one file:
/tmp/futuramax/<profile_id>.json with mode 0600. Its contents are JSON source data:
the complete profile, ordered apply/rollback/verify command references, a value hash
and indexed layer annotations. There are no executable scripts, hooks, init files,
UCI changes or automatic command execution. The stock profiles are centrally stored
references for the external bridge, not native stock firmware configurations.
See the [NetJSON file schema](https://github.com/openwisp/netjsonconfig/blob/9b32477620348bf86976dfe0fef67f5ac335b9fd/netjsonconfig/schema.py).

The exporter parses literal GoldenRadioProfile declarations without executing them
and compares all nine profile fields with the ledger. The manifest retains both
observed input hashes and all eight source vectors. An independently reviewed code
constant fixes this Stage32B cutoff to profile-set SHA256:

f6bcc464f137894f1bf93d6201b1b41b808002981485f36aee654153b4849875.

This anchor prevents a coherently rehashed forged profile/template/manifest from
silently replacing the approved values. New champions require an intentional reviewed
pack revision. File checksums additionally reject changed artifact bytes. These
mechanisms do not turn source-reported benchmark labels into new physical acceptance.

Both OpenWrt profiles retain S31A-R1. The PtMP source includes AQL VO600/1200,
VI1200/2400, BE/BK1500/3000, threshold5000, AP fq_codel quantum3028/10ms/50ms,
memory_limit4mb and station weights720/512/112. The source-reported asymmetric
CPE quantum1514 is not replaced by the AP quantum. No value is retuned here.
Command order is preserved; grouping commands by layers would change that order.

The older Stage31A watchdog is not invoked. Its default rollback commands, early
ping commit and lack of captured-state/independent-watchdog proof do not qualify
exact restoration. runtime_dispatch_allowed=false, rollback_runtime_verified=false
and physical_acceptance=false remain explicit in the new package.

## Telemetry translation

translate_stock_telemetry accepts family airos8/airos6/ltu/openwrt, a bounded mapping
and an explicitly timezone-aware observation timestamp. Supported feeds include
status.cgi-like host/wireless dictionaries, mca-status key=value text, station lists
<!-- stage822a-payload-end -->
