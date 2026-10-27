<!-- doc-head: STAGE32B_OPENWISP_CENTRAL_CONTROLLER_AND_HYBRID_BRIDGE.md continuation 2 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE32B_OPENWISP_CENTRAL_CONTROLLER_AND_HYBRID_BRIDGE.md) | Part 2/3
<a id="stage32b-openwisp-central-controller-and-hybrid-bridge"></a> [Stage32B: OpenWISP central controller and hybrid bridge](STAGE32B_OPENWISP_CENTRAL_CONTROLLER_AND_HYBRID_BRIDGE_CONTINUATION_0248f07ca7_001.md#stage32b-openwisp-central-controller-and-hybrid-bridge) | <a id="prespecified-scope-and-acceptance"></a> [Prespecified scope and acceptance](STAGE32B_OPENWISP_CENTRAL_CONTROLLER_AND_HYBRID_BRIDGE_CONTINUATION_0248f07ca7_001.md#prespecified-scope-and-acceptance) | <a id="delivered-behavior"></a> [Delivered behavior](STAGE32B_OPENWISP_CENTRAL_CONTROLLER_AND_HYBRID_BRIDGE_CONTINUATION_0248f07ca7_001.md#delivered-behavior) | <a id="actual-upstream-contract"></a> [Actual upstream contract](STAGE32B_OPENWISP_CENTRAL_CONTROLLER_AND_HYBRID_BRIDGE_CONTINUATION_0248f07ca7_001.md#actual-upstream-contract) | <a id="eight-templates-and-champion-v8-cutoff"></a> [Eight templates and Champion v8 cutoff](STAGE32B_OPENWISP_CENTRAL_CONTROLLER_AND_HYBRID_BRIDGE_CONTINUATION_0248f07ca7_001.md#eight-templates-and-champion-v8-cutoff) | <a id="telemetry-translation"></a> [Telemetry translation](STAGE32B_OPENWISP_CENTRAL_CONTROLLER_AND_HYBRID_BRIDGE_CONTINUATION_0248f07ca7_001.md#telemetry-translation)

<!-- stage822a-payload-begin -->
or wstalist, normalized interfaces/resources, and the held scalar stock/LTU phase
fields. It does not fetch those feeds or install a collector.

| Observed input | Output and meaning |
| --- | --- |
| uptime, local_time | Native general integer seconds; device clock is not inferred from ingestion time |
| Three load averages plus positive cpus | Native resources.load/cpus; OpenWISP derives a load-based percentage, not measured CPU utilization |
| Complete memory total/free/buffered/shared | Native resources.memory byte integers; total must be positive and values must be consistent |
| Complete RX/TX byte pair | Native interface cumulative counters; integer text is parsed without a float round-trip |
| Seven native wireless identity/RF fields | Native wireless only if all are observed; no default channel, country, mode, noise, SSID or power |
| Complete native client flags | Native clients only when the required fields are observed; an explicit empty list remains observed zero |
| Signal/noise, rates, goodput, RTT, loss, LTU frequency/width | Typed futuramax.metrics entries with units, scope and source field paths |

Unknown values are omitted and identified under futuramax.missing_fields. Boolean
numbers, NaN/Infinity and ambiguous status encodings are rejected or explicitly
omitted. PHY rates are not application goodput; SSH stream throughput is separate;
raw RSSI-chain values and HTTP durations are not silently converted to other units.
No healthy/associated state or zero packet loss is invented.

The extension preserves station scope, measurement time and provenance. OpenWISP's
built-in writer handles native traffic/load/memory/association metrics. Custom
radio/goodput/RTT entries remain raw normalized data until an actual server-side
extractor and chart registration are implemented. custom_charts_configured=false
states that limit; accepting a payload is not proof of chart ingestion.
See [the exact monitoring schema](https://github.com/openwisp/openwisp-monitoring/blob/5dcc9589948043d9a1455402a1c4664f04506acd/openwisp_monitoring/device/schema.py)
and [the built-in writer](https://github.com/openwisp/openwisp-monitoring/blob/5dcc9589948043d9a1455402a1c4664f04506acd/openwisp_monitoring/device/writer.py).

## Prepared controller Compose

orchestration/deploy/docker-compose.openwisp-futuramax.yml declares eleven services:
PostGIS, Redis, InfluxDB1.8, postfix, dashboard, API, websocket, Celery, monitoring
Celery, beat and nginx. OpenWISP images use tag26.09.1. Database/time-series/media/
private/static/certificate/SSH volumes are named and isolated by the Compose project.
Nginx alone publishes loopback18080/18443. No host network, privileged mode,
NET_ADMIN, TUN, OpenVPN, RADIUS or firmware-upgrader service is enabled.

It follows the [official release topology](https://github.com/openwisp/docker-openwisp/blob/26.09.1/docker-compose.yml).
Celery uses the ordinary Compose network with CELERY_SERVICE_NETWORK_MODE empty
instead of the upstream optional VPN container. Monitoring remains enabled.
DEV_MODE/DEBUG_MODE are false; self-signed local TLS still requires explicit client
trust, never verify=false. Image tags are version references, not immutable digests.

An inline Compose config replaces the upstream initializer that otherwise creates
admin/admin. It creates an initial administrator only when no superuser exists,
requires an explicitly supplied password of at least20 characters and does not
reset existing accounts. It does not seed default SSH credentials, VPNs or template
assignments. This bounded bootstrap is necessary for a deployable definition;
no such initialization was executed here.

Required private environment names:
OPENWISP_DJANGO_SECRET_KEY, OPENWISP_DB_PASSWORD, OPENWISP_REDIS_PASSWORD,
OPENWISP_INFLUXDB_PASSWORD, OPENWISP_INFLUXDB_ADMIN_PASSWORD and
OPENWISP_ADMIN_PASSWORD. Use URL-safe Redis credentials. Optional domain/admin
identity variables are documented directly in the Compose interpolation fields.
No secret values, deployment host, DNS changes or production placement were selected.

## Local usage

Offline regeneration:

    python -m controller.openwisp_controller_api_bridge

This writes the eight templates and manifest under artifacts/openwisp_templates.
An explicit --ledger or --output-dir supports a different local input/output
location; mismatched/unapproved profile values still fail closed.

After a separately authorized controller deployment, an operator-controlled Python
caller can construct OpenWISPClient with base URL/user token and allow_writes=True,
then use sync_templates(load_template_pack(), organization_uuid), register_device
or post_monitoring. The three credential classes are distinct: user Bearer token,
organization registration secret and per-device key. They are never embedded in
the template artifacts or API error text. No online CLI action runs implicitly.

Compose validation requires the six variables, but can use process-local dummy
values with config --quiet; that action neither launches Docker services nor
establishes functional API acceptance. Actual deployment/registration and device
applications remain separately authorized work.

## Verification and retained findings

The requested module was executed under the unchanged machine-wide heavy-job guard,
with PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 and no operator override:

    python -m pytest tests/test_stage32b_openwisp_bridge.py -q -p no:cacheprovider

Fresh result: **56 passed, 0 failed, 0 errors, 0 skips; exit0; 0.26s**.
JUnit receipt: C:/_tmp/systemp/s32b_pytest_run1_20261025.xml. These are fixtures,
fake HTTP and disposable local files; they never register a device or start a service.

The first60-second normal resource wait expired before the child started at
1.3..1.7GB free RAM, below the2GB floor. The operator's command fragment ='1'
lacked a variable name, so clarification was requested instead of inferring an
override. Memory later recovered to3.34GB; the normal guard ran the first actual
test invocation successfully, making that exception unnecessary.

Docker Compose5.6.1 config --quiet passed with synthetic process-local secrets,
exit0. An initial successful parse warned that configs.mode is ignored outside
Swarm; removing that unsupported field produced a fresh exit0 without warnings.
YAML and inline-bootstrap syntax were also checked; no image was pulled or launched.

Independent review preserved a failing source/provenance probe:
C:/_tmp/systemp/fmx_s32b_bridge_review_ly__84gp/initial_counterexamples.json
(SHA25617b2e7d8081adae54e6e10c9d1c0a0e8eebc8c977b6456e69fbfd0e045438147).
It showed self-consistent source forgery, zero-total memory, omission of observed
empty clients and integer-text rounding. The reviewed changes add the independent
profile-set anchor, native resources validation, explicit zero-client preservation
and direct integer parsing; regression cases are in the56 passed tests.

Static review also corrected draft test fixtures: A is valid UUID hex, native
attachment needs a backend/config, and idempotent registration first queries existing
inventory. These were not failed pytest runs; no earlier executed test result was
discarded or relabelled.

Independent final review: **PASS_WITH_LIMITS, zero open material blockers**.
It executed64 new lightweight protocol/schema/provenance checks and explicitly reused
the owner's56-test result by hash, without presenting that as an independently
executed pytest run. Receipt:
C:/_tmp/systemp/fmx_s32b_bridge_accepted_wpv9jf0q/independent_bridge_review.json,
SHA256 fecd1f2ff4cc833c716280e69e80158943bbd37c1c86e18b73ecba4b606a5530.
It binds the final bridge, test file, Compose definition, manifest and all eight
templates. JUnit SHA256:
18ca5e8abfbdf353837d30a4c58c24daa8cf8d60fd9e6fb1de27bec464f5795a.

Reviewed bridge SHA256:
40bd97de4428c7eb94b62e968d42c40c02f7629e3685fc2a5be38f366ff7e9b4;
test SHA256:
923af47a252495a5c7bb1780bcd25f1cd6141b365c60e442cc90fea2dc42e730;
Compose SHA256:
d421e5c0bc8311ee4d3fb831923cd1a37915c087aa48ec0f3b871c55446072b8;
manifest SHA256:
6f17a107e9ed2b2279a544974b710639a477f1848353c2bd6448d9541db58498.

The Command Center receives one Stage32B report-card entry linking the bridge,
template manifest, Compose, tests and this report, with explicit fixture/runtime
limits. The first required direct-script invocation failed with ModuleNotFoundError
at an existing controller import: running a script from tools/ did not place the
repository root on Python's import path. A minimal process-local ROOT path insertion
fixed that route; the same requested Python command then completed with exit0 and
wrote artifacts/dashboard/FUTURAMAX_COMMAND_CENTER.html. The failed invocation is
retained; no bridge test, source profile or acceptance condition was changed.
An additional generated-artifact check found the shared HTML had subsequently lost
new report cards. A fresh in-process build immediately contained Stage32B and all
five links. The existing live server imports its builder once, so a concurrent
cached writer is a plausible cause; its process state was not inspected or changed.
To retain a reviewable result independently of that shared-file race, the verified
fresh output is also saved as
artifacts/dashboard/FUTURAMAX_COMMAND_CENTER_STAGE32B.html. This is static output
verification, not browser acceptance or a claim that a live server reloaded.
No live interoperability or rollback acceptance is claimed.

## Research state and decision

External-controller representation is implemented and locally fixture-tested.
KEEP the REST bridge and inactive source-bound template package. Stock-native
configuration, custom charts, exact runtime restoration and any RF improvement
<!-- stage822a-payload-end -->
