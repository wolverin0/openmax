<!-- doc-head: Public ready-to-flash .bin firmware images and field-installable scripts for Stock airOS 8 and OpenWrt 24.10.4 PtP and PtMP radios -->
Ready-to-flash `.bin` images (`factory.bin` & `sysupgrade.bin`) with the OpenMAX Champion pre-baked in SquashFS, plus standalone `.sh` kits for Stock `airOS 8` and vanilla `OpenWrt 24.10.4`.
<!-- /doc-head -->

# openMAX Public Field Kits (`PtP` & `PtMP`) — Ready-to-Flash `.bin` Images & Standalone `.sh` Scripts

## 1. Ready-to-Flash `.bin` Firmware Images (Recommended 1-Step Install — Everything Pre-Baked)

You do **NOT** need to manually install OpenWrt and then run a patch script. Our pre-built **`.bin` firmware images** published in [**GitHub Releases (`v24.10.4-openmax-champion`)**](https://github.com/wolverin0/openmax/releases/tag/v24.10.4-openmax-champion) already bake everything directly into the SquashFS rootfs (`WA`, `XC` Active AirPrism, `XC` Passive, and `XW` M5):
- **`OpenWrt 24.10.4` (`r28959-29397011cc`, Linux 6.6.110)**
- **Patched `mac80211.ko`**: 21-instruction `ETH_P_TEB (0x6558)` decapsulation + 13-instruction 4addr WDS event fix for Stock `airOS 8` AP <-> `OpenWrt` WDS bridge interoperability.
- **Built-in 64 MB RAM Protection**: `fq_memory_limit = 4194304` (4 MiB cap, `fq_overmemory = 0`), `min_free_kbytes = 4096`, and `oom_score_adj = -900` on `hostapd`/`wpa_supplicant`.
- **Built-in Hybrid WDS Admitter (`openmax-admitter`) & Zero Rogue DHCP**: Bridges `phy*-ap0.sta*` automatically and disables rogue LAN DHCPv4/v6/RA on `br-lan`.
- **Pre-Tuned Champion (`openwrt-24.10.4-<board>-{factory,sysupgrade}-{ap,sta}.bin`)**: Pre-configured out of the box with `AQL 3000/6000`, `fq_quantum=3028` (AP) / `1514` (STA), `BQL=4542`, 7 TCP/socket `sysctl` keys, and the 45-second auto-rollback watchdog.

### How to Flash the `.bin` Directly (1 Step):
1. **From Stock Ubiquiti `airOS 8` / `airOS 6`:** Download the **`*-factory*.bin`** for your board (`lap-120`, `litebeam-5ac-gen2`, `powerbeam-5ac-gen2`, `nanostation-ac-loco`, `xc-*`, `xw-*`) from [**GitHub Releases**](https://github.com/wolverin0/openmax/releases/tag/v24.10.4-openmax-champion) and flash it directly:
   ```sh
   scp openwrt-24.10.4-<board>-factory-ap.bin ubnt@<RADIO_IP>:/tmp/fwupdate.bin
   ssh ubnt@<RADIO_IP> "/sbin/fwupdate.real -m"
   ```
2. **From an Existing `OpenWrt` Radio:** Download the **`*-sysupgrade*.bin`** for your board and run:
   ```sh
   scp openwrt-24.10.4-<board>-sysupgrade-ap.bin root@<RADIO_IP>:/tmp/
   ssh root@<RADIO_IP> "sysupgrade -v /tmp/openwrt-24.10.4-<board>-sysupgrade-ap.bin"
   ```

---

## 2. Standalone `.sh` Scripts (When You Don't Want to Reflash a `.bin`)

This directory also contains two self-contained POSIX `sh` scripts for two specific cases where you are **not** flashing our pre-baked `.bin`:

1. **[`airos8_ptp_ptmp_tuned_champion.sh`](airos8_ptp_ptmp_tuned_champion.sh)** — **For radios staying on Stock Ubiquiti `airOS 8` (`v8.5.12 – v8.7.25`)**:
   - No firmware flashing required (`-74.4%` loaded p95 RTT reduction on Stock `airOS 8`).
   - Tightens `eth0`/`ath0`/`br0` TX queues (`1000 -> 192`), raises MIPS NAPI budget (`300 -> 600`), bounds A-MPDU subframes (`32 -> 24`), configures hardware WMM EDCA for Voice/Video, and strips unconsumed `ath_pktlog` / `vow_extstats` CPU overhead.
2. **[`openwrt24_ptp_ptmp_champion.sh`](openwrt24_ptp_ptmp_champion.sh)** — **For radios that already flashed vanilla upstream `OpenWrt 24.10.4` from `downloads.openwrt.org` (or to switch between `--role ptp`, `--role ptmp-ap`, and `--role ptmp-cpe` in live RAM without reflashing)**:
   - Supports `--role ptp` (`BQL limit_max=8192`), `--role ptmp-ap` (`fq_quantum=4542`), and `--role ptmp-cpe` (`fq_quantum=1514`).
   - Caps `mac80211` `fq_memory_limit` at `4 MiB`, configures per-AC `AQL` airtime limits (`VO 300/600`, `VI 1000/2000`, `BE 1500/3000`, `aql_threshold=5000`), sets `htt_max_amsdu_ampdu="2 64"`, and applies the **Wave 338 per-key `sysctl` loop** (`vm.min_free_kbytes=4096`, `tcp_limit_output_bytes=65536`, `tcp_notsent_lowat=8192`, `netdev_max_backlog=2048`).

### Option A: Tune Stock `airOS 8` (Zero Flashing)
```sh
scp firmware/public_field_kits/airos8_ptp_ptmp_tuned_champion.sh ubnt@<RADIO_IP>:/tmp/
ssh ubnt@<RADIO_IP> "sh /tmp/airos8_ptp_ptmp_tuned_champion.sh --apply-ram"
# Persist across reboots (/etc/persistent/rc.poststart + cfgmtd -w -p /etc/):
ssh ubnt@<RADIO_IP> "sh /tmp/airos8_ptp_ptmp_tuned_champion.sh --persist"
```

### Option B: Apply/Update Champion Knobs on Vanilla `OpenWrt 24.10.4`
```sh
scp firmware/public_field_kits/openwrt24_ptp_ptmp_champion.sh root@<RADIO_IP>:/tmp/
ssh root@<RADIO_IP> "sh /tmp/openwrt24_ptp_ptmp_champion.sh --persist --role ptp"
```

See **[`docs/BENCHMARK_3WAY_AIROS_STOCK_VS_TUNED_VS_OPENWRT_CHAMPION.md`](../../docs/BENCHMARK_3WAY_AIROS_STOCK_VS_TUNED_VS_OPENWRT_CHAMPION.md)** for the full 3-way hardware benchmark measurements comparing **Stock `airOS 8`** vs **Tuned `airOS 8`** vs **`OpenWrt 24.10.4` Champion**.
