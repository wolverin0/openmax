<!-- doc-head: STAGE32C_OPENWRT_IMAGEBUILDER_AND_ZERO_TOUCH_PROVISIONING.md preserved document content -->
<!-- /doc-head -->

# Stage 32C: OpenWrt 23.05/24.10 ImageBuilder Overlay & Zero-Touch Provisioning Packager

- **Task ID**: `T-S32C-GEM2-OPENWRT-SYSUPGRADE-PATCH-PACKAGER-AND-TOH-VALIDATOR`
- **Module**: [`firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py)
- **Generated Catalog Receipt**: [`artifacts/autoresearch/stage32c_openwrt_imagebuilder_overlay_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage32c_openwrt_imagebuilder_overlay_20261025.json)
- **Unit Test Suite**: [`tests/test_stage32c_openwrt_imagebuilder.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage32c_openwrt_imagebuilder.py)

---

## 1. Architecture & Target Fleet Coverage

[`futuramax_openwrt_imagebuilder_packager.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py) synthesizes our hardware-verified OpenWrt Table of Hardware (ToH) audit ([`docs/OPENWRT_WIKI_UPSTREAM_CONTRIBUTIONS.md`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/OPENWRT_WIKI_UPSTREAM_CONTRIBUTIONS.md)), OpenWISP `NetJSON` self-reverting RAM watchdog ([`controller/openwisp_netjson_rollback_agent.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/openwisp_netjson_rollback_agent.py)), and multi-radio Champion Ledger ([`artifacts/autoresearch/champion_state_ledger.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/champion_state_ledger.json)) into a deterministic OpenWrt ImageBuilder overlay generator for four primary Ubiquiti AC hardware targets:

| Target Profile (`PROFILE=`) | Board / SysID (`ubnthal`) | SoC & Clock | Flash / RAM | Radio / Caldata Checksum | Default Golden Profile |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`ubnt_lap-120`** | `WA` / `0xe8e5` (`0777:e8e5`) | `AR9342` rev 2 (`535.0 MHz`) | `16 MiB` `MX25L12805D` / `64 MiB` | `QCA9882` (`caldata` `0x3e2d`, `board-2.bin` `bebc7c08`) | `openwrt_lap120_ptmp_multicpe_champion` |
| **`ubnt_nanostation-ac-loco`** | `WA` / `0xe7fa` (`0777:e7fa`) | `AR9342` rev 2 (`535.0 MHz`) | `16 MiB` `MX25L12805D` / `64 MiB` | `QCA9882` + `AR9340` (`caldata` `0x2292`, `board-2.bin` `bebc7c08`) | `openwrt_lap120_ptp_1cpe_champion` |
| **`ubnt_litebeam-ac-gen2`** | `WA` / `0xe7f9` (`0777:e7f9`) | `AR9342-BL1A` rev 3 (`535.0 MHz`) | `16 MiB` `MX25L12805D` / `64 MiB` | `QCA9882` + `AR9340` (`caldata` `0x13b5`, `board-2.bin` `bebc7c08`) | `openwrt_lap120_ptp_1cpe_champion` |
| **`ubnt_rocket-prism-5ac-gen2`** | `XC` / `0xe7f9` / `0xe7e9` | `QCA9558` (`720.0 MHz`) | `16 MiB` SPI NOR / `128 MiB` DDR2 | `QCA9880` (`wifi0` + Dual-Stage AirPrism + `IRQ 64`) + `wifi1` + `airview1` | `openwrt_lap120_ptmp_multicpe_champion` |

---

## 2. Generated Overlay Components (`files/` & `patches/`)

### 2.1 `files/etc/hotplug.d/net/99-futuramax-champion-v8`
Triggered automatically on `ACTION=add` or `ACTION=ifup`:
- **Per-AC AQL (`aql_txq_limit` & `aql_threshold`)**:
  - On AP profiles (`ubnt_lap-120`, `ubnt_rocket-prism-5ac-gen2`): applies Stage 25/31A per-AC limits (`AC_VO 600/1200 us`, `AC_VI 1200/2400 us`, `AC_BE 1500/3000 us`, `AC_BK 1500/3000 us`, `aql_threshold=5000`, `airtime_flags=7`, `rts=512`, `retry short 5 long 4`, `nf_cal_period=30`).
  - On STA/PtP profiles (`ubnt_nanostation-ac-loco`, `ubnt_litebeam-ac-gen2`): applies `900/1500 us` across `AC 0..3`, `aql_threshold=4000`, `rts=off`.
- **Stage 31A M9b Asymmetric DL/UL `fq_codel` Quantum**:
  - `phy0-ap0` / `wlan0`: `fq_codel limit 2048 target 10ms interval 50ms quantum 3028 flows 1024 memory_limit 4mb ecn` (2-MTU quantum preserves A-MPDU frame aggregation density on AP downlink).
  - `phy0-sta0`: `fq_codel limit 2048 target 10ms interval 50ms quantum 1514 flows 1024 memory_limit 4mb ecn` (1-MTU quantum eliminates uplink head-of-line blocking).
- **Stage 25 M5 + Stage 24C AirBBR TCP Pacing & NAPI Budget**:
  - Sets `tcp_limit_output_bytes=131072`, `tcp_notsent_lowat=16384`, `netdev_budget=600`, `tcp_pacing_ca_ratio=110`, `tcp_pacing_ss_ratio=150`, `tcp_thin_linear_timeouts=1`, `tcp_early_retrans=3`, `tcp_autocorking=0`, `tcp_sack=1`, `tcp_dsack=1`, `tcp_fin_timeout=15`, and `rps_cpus=1` on `eth0`/`br-lan`.
- **XC AirPrism Scanner Quiesce**:
  - Automatically brings `airview1` down (`ip link set dev airview1 down`) if present on `XC` Prism hardware.

### 2.2 `files/etc/config/openwisp` & `/usr/sbin/fmx_netjson_watchdog`
- Configures `openwisp-config` with `test_config '1'` and `test_script '/usr/sbin/fmx_netjson_watchdog'`.
- Marks `system.@led`, `network.loopback`, and `network.globals` as `unmanaged` and leaves `shared_secret` as a vault-injected placeholder (`__VAULT_INJECTED_OPENWISP_SHARED_SECRET__`).

### 2.3 71-Byte `ETH_P_TEB` (`0x6558`) `mac80211.ko` Binary & Source Patch Verifier
- [`verify_eth_p_teb_mac80211_patch()`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py#L288-L333) validates both:
  1. **Quilt Source Patch (`999-futuramax-ubnt-wds-strip-eth-p-teb-0x6558.patch`)**: Strips the inner `ETH_P_TEB` (`0x6558`) Ethernet header inside `ieee80211_data_to_8023_exthdr()` (`net/mac80211/util.c`) when `hdr.h_proto == htons(ETH_P_TEB)` and `skb->len >= sizeof(struct ethhdr) + 14`.
  2. **Compiled Binary Verification**: Confirms module path `/lib/modules/6.6.110/mac80211.ko`, patched size `665,308` bytes (`+71` bytes over unpatched `665,237` bytes), SHA-256 `19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416`, and big-endian `0x6558` immediate (`\x65\x58`).

### 2.4 Macronix `MX25L12805D` SPI-NOR Release Gate
- [`validate_openwrt_release_toh_safety()`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py#L162-L176) blocks ImageBuilder packaging on `23.05.0..23.05.2` and `24.10.0..24.10.2` where U-Boot's `SR_BP*` status-register block protection bits left `MX25L12805D` read-only (`overlayfs` `-EIO`), requiring `23.05.3+` or `24.10.3+` (`24.10.4` baseline).
