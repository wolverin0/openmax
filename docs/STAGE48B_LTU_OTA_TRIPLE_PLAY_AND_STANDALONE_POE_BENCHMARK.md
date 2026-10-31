<!-- doc-head: STAGE48B_LTU_OTA_TRIPLE_PLAY_AND_STANDALONE_POE_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 48B — LTU Cold-Boot Standalone PoE Hardening, QCA8337N Port-5 Loop Elimination & OTA Triple-Play Benchmark

**Date**: 2026-10-25  
**Task ID**: `T-S48B-LTU-COLD-BOOT-STANDALONE-POE-HARDENING-AND-OTA-TRIPLE-PLAY-BENCH`  
**Artifact**: [`artifacts/autoresearch/stage48b_ltu_ota_triple_play_and_standalone_poe_20261025.json`](../artifacts/autoresearch/stage48b_ltu_ota_triple_play_and_standalone_poe_20261025.json)

---

## 1. Executive Summary & Field Verification

Following Stage 47B (`Boca 7` dual-partition flash persistence), the operator physically unplugged **`LTU-Lite #2` (`PUBLIC_DEVICE_0043`)** from `Boca 7` (`gi7`) and powered it on a **standalone PoE injector at a remote NLOS location** with zero Ethernet cable attached.

1. **Zero-Touch Cold-Boot Standalone PoE Association (`CONFIRMED`)**:
   - `LTU-Lite #2` cold-booted autonomously on the remote standalone PoE injector, executed `/etc/persistent/rc.poststart` from flash (`Active[1]`/`Backup[2]`), and associated Over-The-Air (`AP-PTMP(Run)` $\leftrightarrow$ `CPE-PTMP(Run)` at `5500 MHz / 20 MHz`, `SSID: FMX-LTU`, `Stations count: 1`).
2. **Root Cause & Permanent Elimination of `force_loop_flee(290)` (`cpeFsmStop`) (`CONFIRMED`)**:
   - In `cds_mac_mod` (`netmode=2`, router HFE mode), `QCA8337N` Port 5 (`eth0.2` / `br0`) is bridged in hardware to `fwdPort:2` (`ath0`), and both `br0` (`eth0.2`) and `ath0` share `MAC2` (`PUBLIC_DEVICE_0045` on `LTU-Lite #1`, `PUBLIC_DEVICE_0043` on `LTU-Lite #2`).
   - Any broadcast/multicast or `dnsmasq`/`udapi-bridge` packet egressing `br0` (`eth0.2`) enters `fwdPort:2` bearing the radio's own hardware MAC address, triggering `[add/4] ame_add_recv_data(886): <recv> Looping caught from fwdPort:2` and eventually `force_loop_flee(290): Loop flee bit set` (`cpeFsmStop`).
   - **Fix**: Both `/etc/persistent/rc.poststart` scripts in [`tools/bench/deploy_stage40a_ltu_poststart.py`](../tools/bench/deploy_stage40a_ltu_poststart.py) now tear down the `eth0.2`/`br0` Port-5 loop (`killall -9 dnsmasq udapi-bridge; brctl delif br0 eth0.2; ifconfig eth0.2 down; ifconfig br0 down; ssdk_sh portvlan member del 5 0; ssdk_sh portvlan member del 0 5`) and maintain `198.18.0.61/24` (`LTU1` `ath0`) $\leftrightarrow$ `198.18.0.72/24` (`LTU2` `ath0`) with `nud permanent` ARP entries via a background `.fmx_ath0_keeper` loop.
   - Persisted to `Active` and `Backup` flash partitions on **both** `LTU-Lite #1` (via `Boca 5` IPv6 `%29`) and remote `LTU-Lite #2` (Over-The-Air via 512-byte chunked Paramiko `direct-tcpip` SSH tunnel to `198.18.0.72:22`, `cfgmtd -w -p /etc/ -> [%100]`).
3. **AP Uplink RX Gain (`ulpwrtune -75`) for Remote NLOS CPE (`CONFIRMED`)**:
   - At the remote standalone PoE location (`remote signal: -77/-72 dBm` DL), `LTU-Lite #1` initially held `rxgain = 51.0 / 50.0 dB` (`ulpwrcfg = -51 51`), yielding an attenuated uplink reading of `-116/-107 dBm`.
   - Adding `/bin/af set ulpwrtune -75` (`ame_bbp_set_rxtarget(1745): NewGain(75,74) target -75`) raised AP LNA RX gain to `75.0 / 74.0 dB`, boosting received uplink signal by **+36 dB** to **`-83/-80 dBm`** (`-80/-78 dBm` peak).
4. **Hardware EAB Ring Bufferbloat (`maxBD = 0x31`) vs. Stage 48B 2-Tier HTB + `fq_codel` + GEM Type-1 DSCP `32` Screener (`CONFIRMED`)**:
   - Under stock unshaped `fq_codel` (`S48B-R0-STOCK-QUEUE`), `ame_dev.ko` drains `ath0` immediately (`backlog 0b 0p, dropped 0`) into the FPGA's 49-descriptor EAB ring (`maxBD = 0x31`), causing **`65.04 ms` p50 / `74.34 ms` p95** loaded ping RTT under `28.95 Mbps` Triple-Play saturation.
   - Loading `/lib/modules/3.14.65/sch_htb.ko` + `/lib/modules/3.14.65/cls_u32.ko` on `LTU-Lite #1` and programming `/sys/class/ame/ame_ctrl_dev/dscp` (`dscp.4.value=32` for `TOS 0x80` = `CS4`) with a 2-tier HTB (`1:10` prio 1 for ICMP + VoIP `0xb8` + IPTV `0x80`, `1:20` prio 2 for Bulk TCP, `target 2ms interval 40ms`) reduced loaded ping p50 RTT by **-92.5%** (`65.04 ms` $\rightarrow$ **`4.85 ms`**) and loaded ping p95 RTT by **-82.7%** (`74.34 ms` $\rightarrow$ **`12.84 ms`**).

---

## 2. Counterbalanced 6-Trial Over-The-Air Triple-Play Benchmark (`198.18.0.61` $\rightarrow$ `198.18.0.72`)

| Profile | Trials | Mean Bulk TCP (`Mbps`) | Mean IPTV UDP (`Mbps`) | Mean IPTV Jitter (`ms`) | Mean VoIP Jitter (`ms`) | Mean VoIP Loss (`%`) | Loaded Ping p50 (`ms`) | Loaded Ping p95 (`ms`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S48B-R0-STOCK-QUEUE`** (Unshaped `fq_codel` + EAB `maxBD=0x31`) | 3 | `19.041` | `9.904` | `1.251` | `4.161` | `0.0%` | `65.037` | `74.339` |
| **`S48B-R1-CHAMPION-V1`** (2-Tier `sch_htb` + `cls_u32` + GEM DSCP `32` + `fq_codel 2ms/40ms`) | 3 | `15.892` | `8.867` | `1.251` | `4.303` | `0.0%` | **`4.847`** (**-92.5%**) | **`12.835`** (**-82.7%**) |

### Per-Trial Breakdown

- **Rep 1**:
  - `S48B-R0-STOCK-QUEUE`: Bulk=`18.721 Mbps`, IPTV=`9.952 Mbps` (`jitter=1.078 ms`, `loss=0.0%`), VoIP=`0.063 Mbps` (`jitter=4.112 ms`, `loss=0.0%`), Loaded Ping `p50=63.783 ms` / `p95=77.227 ms`.
  - `S48B-R1-CHAMPION-V1`: Bulk=`16.513 Mbps`, IPTV=`8.656 Mbps` (`jitter=1.507 ms`), VoIP=`0.063 Mbps` (`jitter=5.465 ms`, `loss=0.0%`), Loaded Ping `p50=4.421 ms` / `p95=21.911 ms`.
- **Rep 2**:
  - `S48B-R0-STOCK-QUEUE`: Bulk=`19.718 Mbps`, IPTV=`10.789 Mbps` (`jitter=1.602 ms`, `loss=0.0%`), VoIP=`0.063 Mbps` (`jitter=4.418 ms`, `loss=0.0%`), Loaded Ping `p50=65.064 ms` / `p95=73.613 ms`.
  - `S48B-R1-CHAMPION-V1`: Bulk=`17.598 Mbps`, IPTV=`6.901 Mbps` (`jitter=1.661 ms`, `loss=0.0%`), VoIP=`0.063 Mbps` (`jitter=3.753 ms`, `loss=0.0%`), Loaded Ping `p50=4.418 ms` / `p95=10.077 ms`.
- **Rep 3**:
  - `S48B-R0-STOCK-QUEUE`: Bulk=`18.685 Mbps`, IPTV=`8.972 Mbps` (`jitter=1.073 ms`, `loss=0.0%`), VoIP=`0.063 Mbps` (`jitter=3.953 ms`, `loss=0.0%`), Loaded Ping `p50=66.265 ms` / `p95=72.178 ms`.
  - `S48B-R1-CHAMPION-V1`: Bulk=`13.565 Mbps`, IPTV=`11.044 Mbps` (`jitter=0.584 ms`, `loss=0.305%`), VoIP=`0.063 Mbps` (`jitter=3.690 ms`, `loss=0.0%`), Loaded Ping `p50=5.702 ms` / `p95=6.518 ms`.
