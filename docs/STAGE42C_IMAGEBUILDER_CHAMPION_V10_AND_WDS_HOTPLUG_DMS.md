<!-- doc-head: STAGE42C_IMAGEBUILDER_CHAMPION_V10_AND_WDS_HOTPLUG_DMS.md preserved document content -->
<!-- /doc-head -->

# Stage 42C: OpenWrt 24.10.4 ImageBuilder Champion v10 First-Boot AQM & Dynamic 4-Addr WDS Hotplug DMS Integration

## 1. Executive Summary (`CONFIRMED`)

- **Task ID**: `T-S42C-GEM2-IMAGEBUILDER-CHAMPION-V10-AND-IPTV-FIRSTBOOT-INTEGRATION`
- **Module Upgraded**: [`firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py)
- **Generated Manifest**: [`artifacts/autoresearch/stage42c_imagebuilder_champion_v10_manifest_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage42c_imagebuilder_champion_v10_manifest_20261025.json)
- **OpenWrt Baseline**: `24.10.4` (`ath79/generic`, Linux `6.6.110`)

## 2. Critical Hardware Findings Embedded into Every OpenWrt Image

### 2.1 Dynamic 4-Address WDS `phy0-ap0.staN` Hotplug DMS (`files/etc/hotplug.d/net/99-futuramax-wds-dms`)

In Stage 35A (`M15_5GHz` Champion v9) and Stage 36A (`S36A-R2` Champion v10), live physical bench testing on `LAP-120` $\leftrightarrow$ `NanoStation 5AC Loco` revealed a critical Linux `mac80211` / `hostapd` behavior:
- When a 4-address WDS station (`wds=1` OpenWrt CPE or stock `airOS 8` CPE via the 71-byte `ETH_P_TEB` `0x6558` patch) associates or re-associates to `hostapd`, Linux creates a dedicated per-station bridge port `phy0-ap0.staN` (e.g., `phy0-ap0.sta1`, `phy0-ap0.sta2`) and enslaves it to `br-lan`.
- Every newly created `phy0-ap0.staN` port initializes with `/sys/class/net/br-lan/brif/phy0-ap0.staN/multicast_to_unicast = 0`, even if the parent `phy0-ap0` port had `multicast_to_unicast = 1`.
- Consequently, without an event-driven hotplug hook, any CPE power-cycle or RF re-association silently drops Directed Multicast-to-Unicast (DMS), causing multicast IPTV traffic to revert to `6 Mbps` basic-rate broadcast or fail to convert to per-station VHT MCS8 (`144–173 Mbps`) unicast A-MPDU frames.

[`render_hotplug_99_futuramax_wds_dms()`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py#L340-L398) embeds `files/etc/hotplug.d/net/99-futuramax-wds-dms` (mode `0755`) into every generated OpenWrt image so that on any `ACTION=add` or `ACTION=ifup` event matching `phy0-ap0*`, `wlan0*`, or `br-lan`:
1. `/sys/class/net/br-lan/bridge/multicast_snooping` and `multicast_querier` are enforced to `1`.
2. All `/sys/class/net/br-lan/brif/phy0-ap0*` ports (base and dynamic `.sta*` WDS ports) immediately receive `multicast_to_unicast=1`, `multicast_fast_leave=1`, and `hairpin_mode=0` (with a 3-attempt bounded retry to handle asynchronous `hostapd` bridge enslavement).

### 2.2 Stage 36A Champion v10 First-Boot `mac80211` AQM & AQL Guard (`files/etc/uci-defaults/98-futuramax-champion-v10-aqm`)

In Stage 36A (`artifacts/autoresearch/stage36a_live_iptv_ac_vi_ptmp_bench_20261025.json`):
- **S36A-R1 (`REFUTED`)**: Tightening `AC_BE` AQL limits to `1000/2000 us` (`aql_threshold=4000 us`) caused a **`-6.225%` TCP goodput regression** because 2-MTU (`3028 B`) frames require `~1450 us` of airtime and were starved of multi-frame A-MPDU aggregation.
- **S36A-R2 (`CONFIRMED` Champion v10)**: Preserving `AC_BE=1500/3000 us` (`aql_threshold=5000 us`) + `AC_VI=1200/2400 us` while writing directly to `mac80211`'s internal FQ-CoDel AQM via `/sys/kernel/debug/ieee80211/phy0/aqm` (`echo "fq_quantum 3028" > /sys/kernel/debug/ieee80211/phy0/aqm` and `echo "fq_memory_limit 4194304" > /sys/kernel/debug/ieee80211/phy0/aqm`) achieved **`+2.513%` TCP goodput (`91.097 Mbps`)**, **`-3.375%` p95 RTT (`54.714 ms`)**, **`-8.990%` p99 RTT (`62.063 ms`)**, and **`0 / 3980` (`0.00%`) IPTV packet loss** in `tid4_ac1`.

[`render_uci_defaults_98_futuramax_champion_v10_aqm()`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py#L401-L460) embeds `files/etc/uci-defaults/98-futuramax-champion-v10-aqm` across all 4 device targets (`fq_quantum 3028` on AP targets `ubnt_lap-120` and `ubnt_rocket-prism-5ac-gen2`; `fq_quantum 1514` on CPE targets `ubnt_nanostation-ac-loco` and `ubnt_litebeam-ac-gen2`).

### 2.3 Embedded Overlay File Inventory per Target Image

| Overlay Path | Mode | Purpose |
| :--- | :--- | :--- |
| `files/etc/hotplug.d/net/99-futuramax-wds-dms` | `0755` | Dynamic 4-addr WDS `phy0-ap0.sta*` `multicast_to_unicast=1` + `multicast_fast_leave=1` enforcement |
| `files/etc/uci-defaults/98-futuramax-champion-v10-aqm` | `0755` | Stage 36A Champion v10 `/sys/kernel/debug/ieee80211/phy0/aqm` (`fq_quantum`, `fq_memory_limit`) + per-AC AQL (`AC_VI 1200/2400`, `AC_BE 1500/3000`, `thresh 5000`) |
| `files/etc/hotplug.d/net/99-futuramax-champion-v8` | `0755` | Runtime interface AQL/TCP/NAPI/qdisc tuning on `ifup` |
| `files/usr/sbin/fmx_uisp_ws_reporter` | `0755` | Dual-NMS Ubiquiti UISP `udapi-bridge` AES-256-GCM telemetry reporter |
| `files/usr/sbin/fmx_netjson_watchdog` | `0755` | Self-reverting RAM watchdog for OpenWISP `test_script` |
| `files/etc/init.d/fmx_uisp_reporter` | `0755` | `procd` service wrapper for UISP coexistence daemon |
| `files/etc/config/openwisp` | `0600` | Zero-touch OpenWISP agent config with `test_config '1'` |
| `package/kernel/mac80211/patches/subsys/999-futuramax-ubnt-wds-strip-eth-p-teb-0x6558.patch` | `0644` | 71-byte `ETH_P_TEB` (`0x6558`) 4-addr WDS decapsulation patch (`19a8fde6...`) |
