<!-- doc-head: Stage1019A real BusyBox/queue admission and100 ICMP requests each direction; media campaign blocked -->
<!-- /doc-head -->

# Stage1019A — Native PowerBeam admission without iperf or stat

2026-10-27. Origin **CONFIRMED_LIVE_HARDWARE**, status
**BLOCKED_MEDIA_ENDPOINT_AND_RESTORER_ADMISSION**. Attribution: external SSH
controller, Linux/mac80211 getters and actual ICMP replies.

## Fresh physical acquisition

Both PowerBeam5ACGen2 radios report OpenWrt, channel40/control5200MHz,
center5200MHz and20MHz width. Native interface-to-PHY mappings select
`phy2-ap0` on.241 and `phy2-sta0` on.242; no PHY number was assumed.

| Native active-PHY getter | .241 AP | .242 STA |
| --- | ---: | ---: |
| AQM fq_quantum | 3028 | 1514 |
| AQM fq_limit | 8192 | 1024 |
| AQM fq_memory_limit | 4194304 | 4194304 |
| AQL VO low/high | 500/1000 | 500/1000 |
| AQL VI low/high | 1000/1500 | 1000/1500 |
| AQL BE low/high | 1500/2000 | 1500/2000 |
| AQL BK low/high | 1000/1500 | 1000/1500 |
| Separate BC/MC scalar | 50000 | 50000 |
| tcp_notsent_lowat | 131072 | 131072 |
| tcp_autocorking | 1 | 1 |

Stage1008A parses native AQM/AQL and preserves BC/MC separately. Stage1014A's
default asymmetric champion expectation returns **PROFILE_MISMATCH**; this is not
an application failure invented from missing tc. `default_qdisc=fq_codel` is a
kernel default; internal iTXQ quantum does not prove actual root-qdisc parameters.
Other readable PHY state is retained but not substituted for the active interface.
Before/after active queue policies, boot, channel and sysctls are identical.

## Predeclared idle test, not a Triple-Play A/A campaign

Four chunks of25 ICMP requests per direction, integer interval1s, were frozen
before collection and persisted individually. Both directions ran concurrently.

| Direction | Sent | Received | Lost |
| --- | ---: | ---: | ---: |
| .241→.242 | 100 | 99 | 1 |
| .242→.241 | 100 | 100 | 0 |

The loss occurred in the final .241 chunk. No sample was removed or retried.
Stage1015A's zero-loss idle prerequisite therefore fails. Raw reply arrays remain
available; missing replies do not become zero RTT. These management-address probes
do not establish an exclusive OTA data path or a mixed-workload capacity result.

## Capability and media boundaries

Native nc usage confirms client-only operation, without listen/UDP/exec options.
The initial multi-argument `command -v` exposed only nc; other false capability
fields mean **NOT_OBSERVED**, not proof that dd/cat/wget/uhttpd are absent.
Stage1020A adds an individually queried native capability snapshot and retains the
original adapter source/version. No listener, flow, configuration setter, iperf,
stat command, firmware operation or system-package installation was executed.

The requested objective **LATENCY_WITH_CAPACITY_NONINFERIORITY** and six pairs per
phase override the offline spec's CAPACITY objective/twelve discovery pairs. They
are recorded before data collection. A/A, discovery and holdout remain
**NOT_EXECUTED**, with null workload metrics and no gate verdict. Full media
acquisition also requires a real UDP endpoint beyond the bridge and a qualified
autonomous restoration mechanism; old failed rollback evidence is not reused.

[Receipt](../artifacts/autoresearch/stage1019a_live_powerbeam_busybox_triple_play.json),
[collector](../tools/autoresearch/run_stage1019a_live_powerbeam_busybox_triple_play.py),
[native evidence](../artifacts/verification/stage1019a/).
