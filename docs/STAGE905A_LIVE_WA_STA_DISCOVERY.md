<!-- doc-head: Stage905A native WA station discovery and separate kernel-default/mac80211 queue evidence -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage905A — Native WA discovery

2026-10-27. Provenance **CONFIRMED_LIVE_HARDWARE**, acquisition **NATIVE_DISCOVERY**.
Attribution: external SSH controller; Linux/mac80211 getters. No configuration writes.

## Confirmed observations

`.20` is LAP120 OpenWrt. Actual radio interfaces include `phy0-ap0` and WDS
`phy0-ap0.sta1`; the requested `iw dev wlan0 station dump` is retained with its
native failure rather than substituting a fabricated `wlan0` result.
Dumping every actual wireless interface found associated MAC `PUBLIC_DEVICE_0036`.
Complete ARP entries map that MAC to `198.18.0.67` and `198.18.0.47`.
These are candidate addresses, not proof that either runs OpenWrt or owns the STA.
Proxy/bridge behavior can share a MAC; failed/incomplete ARP entries are excluded
from complete associated-address candidates. No newly discovered host was mutated.

`.251` accepted the documented ubnt access and returned native Rocket2AC Prism
board/version data; it was not treated as a verified OpenWrt station.

## Queue layers are distinct

| Native getter | Actual result | Limit |
| --- | --- | --- |
| `/proc/sys/net/core/default_qdisc` | `fq_codel` | Kernel default, not actual interface-root readback |
| `phy0/aqm` | Readable mac80211 FQ state | iTXQ layer, independent of userspace tc |
| `fq_flows_cnt` / `fq_limit` | 4096 / 512 | Native snapshot, not generic defaults |
| `fq_quantum` | 3028 | Internal FQ value, not root fq_codel quantum proof |
| `fq_memory_limit` | 3145728 | Native byte limit |
| actual root qdisc parameters | UNKNOWN | tc unavailable; no replacement netlink query executed |

The kernel default confirms fq_codel availability. mac80211's separate queue state
is observable without tc. This does not retroactively prove the Stage897A requested
root profile1514/5ms/100ms/ECN or make the unsupported kit --verify command work.
Native AQL exists at `ieee80211/phy0/aql_txq_limit`; the requested ath10k child path
is captured separately. Getter absence is not replaced by invented values.

## Evidence

[Script](../tools/autoresearch/run_stage905a_live_wa_sta_discovery.py),
[receipt](../artifacts/autoresearch/stage905a_live_wa_sta_discovery.json).
The receipt binds command outputs, stations, neighbors, per-getter exit codes and
queue-layer distinctions. The initial local syntax error is retained separately;
it occurred before hardware access. Parser updates reparse saved native output;
the original capture's implementation reference remains historical.

Resolved: missing tc does not prevent native AQL/iTXQ observation or the separately
authorized PowerBeam AQL experiment. UNKNOWN: authenticated Linux identity of the
WA STA and the actual root qdisc graph/parameters. No WA kit apply was attempted.
