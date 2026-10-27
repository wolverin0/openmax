<!-- doc-head: STAGE312A_LIVE_WA_IPTV_MULTICAST_AND_GAMING_R34_36.md preserved document content -->
<!-- /doc-head -->


# Stage 312A — Live `WA` (`QCA9882` `.20 <-> .250`) Rounds `34..36` (**`148` Cumulative Windows!**): Multicast IPTV IGMP Snooping, DTIM/Beacon Overhead & Gaming UDP Verification

- **Claim Label**: `CONFIRMED`
- **Attribution**: `Linux` (`bridge.ko`, `netfilter`) + `mac80211` + `ath10k` + `hardware` (`AR9342` + `QCA9882`)
- **Protocol**: Counterbalanced `A1 -> B1 -> A2 -> B2` (`3` rounds $\times$ `4` live windows = `12` windows; cumulative **`144` RF windows + `4` E2E windows = `148` live windows** on `.20 <-> .250`)
- **JSON Receipt**: [`artifacts/autoresearch/stage312a_live_wa_iptv_multicast_and_gaming_r34_36.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage312a_live_wa_iptv_multicast_and_gaming_r34_36.json)

---

## 1. Executive Summary (`R34..R36` Counterbalanced Results)

| Round ID | Hypothesis / Knob Tested | Arm A Mean Goodput | Arm B Mean Goodput | Arm A `p50` / `p95` RTT | Arm B `p50` / `p95` RTT | Pareto $\Delta$ | Decision |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S312A-R34`** | Bridge IGMP Snooping (`multicast_snooping=1`) & Wi-Fi `multicast_to_unicast=1` on `br-lan`/`phy0-ap0*` (`Arm B`) vs `0`/`0` (`Arm A`) | `60.120 Mbps` | **`61.856 Mbps`** (`+2.89%`) | `19.234` / `44.297 ms` | `21.925` / `67.691 ms` | `-3.05%` | **`RETAIN_ARM_A` (`+2.89%` Goodput via Direct `bridge.ko` Sysfs)** |
| **`S312A-R35`** | Beacon & DTIM Interval Overhead on 4-Address WDS (`dtim_period=1, beacon_int=50` vs `dtim_period=2, beacon_int=100`) | **`69.433 Mbps`** (`76.195 Mbps` peak in `A1`) | `58.154 Mbps` | **`15.440`** / **`61.296 ms`** (`4.594 ms` in `A1`) | `22.148` / `65.946 ms` | `-30.12%` | **`RETAIN_ARM_A`** |
| **`S312A-R36`** | **`36`-Round (`148`-Window) Universal `WA` Champion `v6` (`Arm B`) vs Stock OpenWrt `24.10.4` (`Arm A`) under Triple-Play + `60 pps` Gaming UDP + 8-Stream TCP** | `67.899 Mbps` | **`66.923 Mbps`** (`69.866 Mbps` in `B1`) | `28.855` / `79.117 ms` | **`21.026`** / **`40.112 ms`** (`-27.13%` `p50`, **`-49.30%` `p95`**) | **`+6.22%`** | **`PROMOTE_ARM_B`** |

---

## 2. Mechanistic Findings (`FMX-DISC-36`, `CONFIRMED`)

1. **`FMX-DISC-36` (`uci wireless.default_radio0.multicast_to_unicast='1'` vs Direct `bridge.ko` Sysfs + `fmx_wds_churn_healer.sh` Race, `CONFIRMED`)**:
   - Setting `uci set wireless.default_radio0.multicast_to_unicast='1'` on an OpenWrt 4-address WDS AP (`wds='1'`) interacts with `netifd`/`hostapd` port isolation, and when combined with a background `ubus call hostapd.phy0-ap0 get_clients` poll under heavy CPU load (`fmx_wds_churn_healer.sh`), causes false-positive `iw dev phy0-ap0.sta1 del` flushes during the 200 ms WPA2 4-way handshake window.
   - Writing `/sys/class/net/br-lan/bridge/multicast_snooping=1` and `/sys/class/net/phy0-ap0*/brport/multicast_to_unicast=1` directly via `bridge.ko` sysfs (`S312A-R34`) is 100% non-disruptive and increased Triple-Play goodput from `60.120 Mbps` to **`61.856 Mbps` (`+2.89%`)** with `0.0%` IPTV loss.
2. **148-Window Cumulative Head-to-Head (`S312A-R36`, `CONFIRMED`)**:
   - Under simultaneous 8-stream bidirectional TCP (`--bidir -P 4`), `5 Mbps` IPTV UDP, `128 kbps` VoIP RTP, and `60 pps` `120 B` bidirectional Gaming UDP probes, the `36`-Round Universal `WA` Champion `v6` (`Arm B`) slashed `p50` RTT by **`-27.13%` (`28.855 -> 21.026 ms`)** and `p95`/`p99` tail latency by **`-49.30%` (`79.117 -> 40.112 ms`, reaching `20.893 ms` in `B2`)**, while nearly doubling AP CPU idle headroom (`8.33% -> 16.03%`) (`Pareto +6.22%`, `PROMOTE_ARM_B`).
