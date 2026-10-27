<!-- doc-head: STAGE277A_LIVE_WA_NFTABLES_DSCP_CLASSIFIER.md preserved document content -->
<!-- /doc-head -->



# Stage 277A — Lightweight `nftables` WMM DSCP Classifier (`99-fmx-wmm-dscp-qos`) for WISP Triple-Play

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `T-S277A-LIVE-WA-NFTABLES-DSCP-CLASSIFIER`
- **Deliverable**: [`firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wmm-dscp-qos`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wmm-dscp-qos)
- **Receipt**: [`artifacts/autoresearch/stage277a_live_wa_nftables_dscp_classifier.json`](../artifacts/autoresearch/stage277a_live_wa_nftables_dscp_classifier.json)

---

## 2. Architecture & IEEE 802.11e / `mac80211` `ieee80211_select_queue()` Mapping (`CONFIRMED`)

Customer CPE routers frequently strip or zero out DSCP (`TOS=0x00`), causing VoIP RTP, DNS, gaming UDP, and IPTV streams to collide with multi-connection TCP downloads inside `TID 0` (`AC_BE`). `99-fmx-wmm-dscp-qos` installs a lightweight `nftables` `postrouting` mangle chain (`table inet fmx_wmm_qos`) compatible with `firewall4` `flow_offloading=1`:

| Traffic Class | Match Criterion in `inet fmx_wmm_qos` | DSCP Set | `mac80211` TID & Hardware AC | Champion AQL Limit (`low/high`) |
| :--- | :--- | :--- | :--- | :--- |
| **VoIP / RTP / Gaming / DNS** | `udp dport/sport { 53, 123, 5060, 5203 }` or `ip protocol udp meta length <= 220` | **`ef` (`0x2e`)** | **`TID 6` (`AC_VO`)** | `300 / 600 us` |
| **ICMPv4 / ICMPv6 Probes** | `ip protocol icmp` / `ip6 nexthdr icmpv6` | **`cs6` (`0x30`)** | **`TID 7` (`AC_VO`)** | `300 / 600 us` |
| **IPTV / Live Video UDP** | `udp dport/sport { 1234, 5004, 5202 }` | **`af41` (`0x22`)** | **`TID 4 / 5` (`AC_VI`)** | `1000 / 2000 us` |
| **Interactive Web / TCP** | Default policy (`ct bytes <= 64 MB`) | **`cs0` (`0x00`)** | **`TID 0` (`AC_BE`)** | `1500 / 3000 us` |
| **Heavy Bulk Scavenger** | `ip protocol tcp ct bytes > 67108864` (`> 64 MB`) | **`cs1` (`0x08`)** | **`TID 1` (`AC_BK`)** | `500 / 1000 us` |

---

## 3. Live Bench Verification (`S276A-R30`, `CONFIRMED`)
- With all traffic generated unmarked (`-S 0x00`), activating `inet fmx_wmm_qos` (`Arm B`) steered `300` VoIP packets/window into `TID 6` (`AC_VO`), `1,403–1,416` IPTV packets/window into `TID 4` (`AC_VI`), and `10–12` ICMP probes/window into `TID 7` (`AC_VO`), improving goodput (`59.289 -> 60.345 Mbps`), cutting VoIP jitter by **`-16.25%`** (`2.056 -> 1.722 ms`), and reducing under-load `p50` RTT by **`-12.34%`** (`18.073 -> 15.843 ms`, `12.003 ms` in `B1`) with `< 0.5%` CPU difference.
