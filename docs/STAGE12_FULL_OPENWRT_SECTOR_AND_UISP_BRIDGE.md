# Stage 12 — Full Production Sector Cutover (`Panel1-Guarida` + `MONZON` + `GAMBOA`) & Native UISP (`udapi-bridge`) Bridge Specification

**Date**: 2026-10-23  
**Status**:
- **Part A (100% OpenWrt 24.10.4 Production Sector — AP + Active CPEs)**: **`CONFIRMED` (Live in Production)**
- **Part B (`udapi-bridge` UISP Native Agent over OpenWrt)**: **`CONFIRMED` Binary Architecture (`XC`/`WA` `v8.7.25`) · Ready for Bench Qualification on `Loco195`**

---

## 1. Executive Summary & Real-World Production Multipliers

On 2026-10-23, we completed the full migration of our first live production WISP sector (**`Panel1-Guarida`**, operating on a 20 MHz channel at `5240 MHz`, Channel 48) from Stock `airOS 8` (`WA.v8.7.25`, Linux `2.6.32.68`) to **100% OpenWrt 24.10.4 (`Linux 6.6.110`)** across both the sector Access Point and all active customer CPEs:

1. **`Panel1-Guarida` (`10.10.100.84`, `Ubiquiti LiteAP 120`, `0xe7f5`)**: Running OpenWrt 24.10.4 (`AP-WDS` `4addr: on`, `beacon_int=30`, `AQL = 2000/4000 µs`, patched `mac80211.ko` `19a8fde6...` stripping `ETH_P_TEB` `0x6558`, plus `panel1_admitter.sh` so any power-cycled or newly connected Stock `airOS 8` CPE associates with zero pre-staging).
2. **`MONZON-Stella-Maris` (`10.10.200.41`, `Ubiquiti NanoStation 5AC loco`, `0xe7fa`)**: Running OpenWrt 24.10.4 (`STA-WDS` `4addr: on` in `br-wan`, `fw4` NAT Masquerade + `flow_offloading=1`, `AQL = 2000/4000 µs`, LuCI HTTP/HTTPS WebUI, static DHCP lease preserving customer router `WR300` at `192.168.1.176`).
3. **`GAMBOA-Gabriela` (`10.10.200.223`, `Ubiquiti LiteBeam 5AC Gen2`, `0xe7f9`)**: Running OpenWrt 24.10.4 (`STA-WDS` `4addr: on` in `br-wan`, `fw4` NAT Masquerade + `flow_offloading=1`, `AQL = 2000/4000 µs`, LuCI HTTP/HTTPS WebUI, static DHCP lease preserving customer router `EC220-F5` at `192.168.1.169`).

### Measured Before vs. After Production Benchmark (`20 MHz` Channel 48, Same Physical Radios & Rooftops)

All measurements are preserved in:
- [`artifacts/canary_panel1_guarida/cpe_monzon_vs_gamboa_pre_openwrt_baseline_20261023.json`](../artifacts/canary_panel1_guarida/cpe_monzon_vs_gamboa_pre_openwrt_baseline_20261023.json)
- [`artifacts/canary_panel1_guarida/direct_sector_monzon_openwrt_vs_gamboa_airos_20261023.json`](../artifacts/canary_panel1_guarida/direct_sector_monzon_openwrt_vs_gamboa_airos_20261023.json)
- [`artifacts/canary_panel1_guarida/panel1_full_openwrt_sector_benchmark_20261023.json`](../artifacts/canary_panel1_guarida/panel1_full_openwrt_sector_benchmark_20261023.json)

| Production Metric (`20 MHz`, `5240 MHz`) | Stock `airOS 8.7.25` (Before) | **OpenWrt 24.10.4 + AQL + Flow Offload** (Now) | Improvement Multiplier (`x`) | Improvement (`%`) |
| :--- | :--- | :--- | :---: | :---: |
| **Unloaded Wireless Sector RTT (`AP <-> MONZON`)** | `22.58 ms` (`p50`) | **`1.93 ms` (`p50`)** / `4.47 ms` (`p95`) | **11.7x faster** | **-91.5% latency** |
| **Unloaded Wireless Sector RTT (`AP <-> GAMBOA`)** | `22.58 ms` (`p50`) / `98.77 ms` (`p95`) | **`2.42 ms` (`p50`)** / `14.90 ms` (`p95`) | **9.3x faster (`p50`) / 6.6x lower jitter (`p95`)** | **-89.3% latency / -84.9% jitter** |
| **Loaded Download Latency (`MONZON`)** | `24.67 ms` (`p50`) / `36.58 ms` (`p95`) | **`9.86 ms` (`p50`) / `10.65 ms` (`p95`)** (at **`69.37 Mbps`** TCP) | **3.4x lower loaded tail latency** | **-70.9% bufferbloat** |
| **Loaded Download Latency (`GAMBOA`)** | `31.49 ms` (`p50`) / `54.40 ms` (`p95`) | **`8.43 ms` (`p50`) / `32.70 ms` (`p95`)** (at **`36.52 Mbps`** TCP) | **3.7x lower loaded median latency** | **-73.2% bufferbloat** |
| **Loaded Upload Latency (`CPE -> AP`)** | `195–224 ms` (`p50`) *(due to airOS `tshaper` 127-packet SFQ queue)* | **`10.37 ms` (`GAMBOA`) / `16.64 ms` (`MONZON`) (`p50`)** | **12x to 18x lower upload lag** | **-91% to -94% upload lag** |
| **Usable 20 MHz Sector Capacity (TCP Goodput)** | `~35–45 Mbps` typical aggregate | **`69.80 Mbps` DL / `30.74 Mbps` UL** | **1.5x to 1.8x higher capacity** | **+50% to +80% more Mbps/MHz** |

---

## 2. Root-Cause Findings Proven During the Production CPE Cutover

1. **Why Stock `airOS 8` CPEs Suffer ~200 ms Upload Bufferbloat (`CONFIRMED`)**:
   - When traffic shaping (`tshaper`) is enabled in `airOS 8` (`1.575 Mbps` UL on `ath0`), `airOS` attaches an `htb` class backed by a **127-packet `sfq` queue (`limit 127p`)** on `ath0` with zero AQM (`dropped 7745, overlimits 453056` observed on `MONZON` prior to cutover). At `1.575 Mbps`, 127 packets of 1500 bytes equals **`967 ms` of worst-case standing queue**.
   - Replacing the CPE firmware with OpenWrt 24.10.4 (`fq_codel` + `AQL = 2000/4000 µs` at `/sys/kernel/debug/ieee80211/phy0/aql_txq_limit`) completely eliminates the wireless queue bloat inside the CPE (`10.37–16.64 ms` `p50` loaded RTT even at full `26–30 Mbps` wireless saturation).
2. **OpenWrt 24.10.4 CPE Router Architecture (`STA-WDS` + `br-wan` + `fw4` Flow Offload) (`CONFIRMED`)**:
   - Defining an empty-capable bridge `br-wan` (`option type 'bridge'`, `option bridge_empty '1'`) as the device for `interface 'wan'` (`proto 'static'`, `10.10.200.x/24`, gateway `10.10.200.1`) allows `netifd` to keep the static WAN IP and default route permanently bound while automatically enslaving `phy0-sta0` (`mode 'sta'`, `wds '1'`, `4addr: on`) into `br-wan`.
   - Enabling `option flow_offloading '1'` in `/etc/config/firewall` offloads established NAT/Masquerade flows in the Linux 6.6.110 kernel, keeping AR9342 CPU load negligible (`load average: 0.02`) during full `69.8 Mbps` TCP transfers.

---

## 3. Native UISP / UNMS Compatibility on OpenWrt (`udapi-bridge` Architecture)

### 3.1 Problem Statement
When an `airOS 8` radio is migrated to pure OpenWrt 24.10.4, Ubiquiti's userspace management agent (`/bin/udapi-bridge`) is no longer running. Consequently, the WISP's UISP controller (`wss://puntofutura.ddns.net:443`) marks the device as offline.

### 3.2 Binary Reverse-Engineering of `/bin/udapi-bridge` (`CONFIRMED`)
Static inspection of `/bin/udapi-bridge` (`606,816` bytes in `WA.v8.7.25` / `XC.v8.7.25`) confirms that UISP telemetry does **NOT** depend on the `2.6.32.68` kernel or `ubnt_poll_host.ko`. Instead, `/bin/udapi-bridge` is a self-contained userspace WebSocket + `EVP_aes_256_gcm` daemon that interacts with the local system through **7 narrow file/script interfaces**:

| Interface Required by `/bin/udapi-bridge` | Purpose in `airOS 8` | How OpenWrt 24.10.4 Provides It |
| :--- | :--- | :--- |
| **`/etc/board.info`** & **`/proc/ubnthal/board.info`** | Provides `board.sysid`, `board.hwaddr`, `board.device_id`, `board.model`, `board.shortname` | Restored byte-for-byte from each radio's pre-cutover backup into `/etc/board.info` (and bind-mounted/populated in `/tmp`). |
| **`/tmp/system.cfg`** & **`/tmp/running.cfg`** | Provides `unms.status=enabled`, `unms.uri=wss://...`, `resolv.host.1.name`, and network/wireless config keys | Restored from the radio's original pre-cutover `system.cfg` backup (containing the exact `unms.uri` AES key registered in UISP). |
| **`/usr/www/status.cgi`** | Executed by `mod_airos_status` to read JSON status (`host`, `wireless`, `interfaces`, `ntp`, `firewall`, `unms`) | Provided by a lightweight OpenWrt shell/ucode script `/usr/www/status.cgi` that formats live `ubus` / `iw dev phy0-ap0 info` / `iw dev phy0-sta0 link` / `/proc/uptime` / `/proc/meminfo` / `/sys/class/net/*` counters into the exact `airOS 8` `status.cgi` JSON schema. |
| **`/bin/wstalist`** (and `/tmp/stats/wstalist`) | Executed by `mod_airos_wstalist` to list associated stations (or AP peer on a STA) with `mac`, `signal`, `noisef`, `tx`, `rx`, `ccq`, `airmax` fields | Provided by a lightweight OpenWrt script `/bin/wstalist` that parses `iw dev phy0-ap0 station dump` (on APs) or `iw dev phy0-sta0 link` (on CPEs) and outputs the exact `wstalist` JSON array. |
| **`/bin/backupcfg`** | Executed by `mod_airos_backup_save` / `restore` when UISP requests a `.cfg` backup | Provided by a wrapper script `/bin/backupcfg` that packages `/tmp/system.cfg` with the `### PART ###` + `### PART SHA512 ###` wrapper. |
| **Standard Linux `/proc` & `/sys`** | `/proc/uptime`, `/proc/meminfo`, `/proc/stat`, `/sys/class/net/%s/*` | Natively present in OpenWrt `Linux 6.6.110`. |
| **`uClibc` Runtime Libraries (`~1.8 MB` compressed)** | `/lib/ld-uClibc.so.0`, `libc.so.0`, `libpthread.so.0`, `librt.so.0`, `libssl.so.1.1`, `libcrypto.so.1.1`, `libwebsockets.so.13`, `libjson-c.so.2`, `libcurl.so.4` | Co-installed alongside OpenWrt's `musl` libc in `/lib/` (zero filename collision because OpenWrt uses `/lib/ld-musl-mips-sf.so.1`, whereas `udapi-bridge` requests `/lib/ld-uClibc.so.0`). |

### 3.3 Implementation & Bench Qualification Plan (`FMX-0026`)
1. **Step 1 (Packaging)**: Bundle `/bin/udapi-bridge` + its `uClibc` shared libraries from `WA.v8.7.25` (`<1.8 MB` xz-compressed) + the OpenWrt translator scripts (`/usr/www/status.cgi`, `/bin/wstalist`, `/bin/backupcfg`).
2. **Step 2 (Bench Qualification on `Loco195`)**: Run the bundle on `Loco195` (OpenWrt 24.10.4) against a local mock WebSocket server and verify that `mod_getsysinfo_airos`, `mod_airos_status`, and `mod_airos_wstalist` serialize valid JSON without errors.
3. **Step 3 (Live Production Activation on `Panel1-Guarida`, `MONZON`, and `GAMBOA`)**: Deploy the bundle + each radio's original `/etc/board.info` and `/tmp/system.cfg` (`unms.uri`) so all 3 OpenWrt 24.10.4 radios appear **Online and green in UISP (`puntofutura.ddns.net`)** with live signal, bitrate, throughput, CPU/RAM, and client telemetry.
