<!-- doc-head: Public field-installable scripts for Stock airOS 8 and OpenWrt 24.10.4 PtP and PtMP radios -->
Ready-to-run shell kits with dry-run, RAM-only test, persistence, live read-back verification, and rollback.
<!-- /doc-head -->

# openMAX Public Field Kits (`PtP` & `PtMP`) — Stock `airOS 8` & `OpenWrt 24.10.4`

This directory contains the two self-contained, dependency-free POSIX `sh` scripts so any WISP operator or lab tester can apply and verify the **openMAX** queue, airtime, BQL, and TCP tuning on their own Ubiquiti airMAX AC hardware (`PowerBeam 5AC Gen2`, `LiteBeam 5AC Gen2`, `NanoStation 5AC Loco`, `LiteAP 120/GPS`, `Rocket 5AC`):

1. **[`airos8_ptp_ptmp_tuned_champion.sh`](airos8_ptp_ptmp_tuned_champion.sh)** — **For radios still running Stock Ubiquiti `airOS 8` (`v8.5.12 – v8.7.25`)**:
   - No firmware flashing required.
   - Tightens `eth0`/`ath0`/`br0` TX queues (`1000 -> 192`), raises MIPS NAPI budget (`300 -> 600`), bounds A-MPDU subframes (`32 -> 24`) so VoIP/ICMP packets are not head-of-line blocked behind giant aggregates, configures hardware WMM EDCA for Voice/Video, and strips unconsumed `ath_pktlog` / `vow_extstats` CPU overhead.
2. **[`openwrt24_ptp_ptmp_champion.sh`](openwrt24_ptp_ptmp_champion.sh)** — **For radios migrated to `OpenWrt 24.10.4` (`Linux 6.6.x`)**:
   - Supports `--role ptp` (dedicated PtP backhaul with BDP-calibrated `BQL limit_max=8192`), `--role ptmp-ap` (sector AP with `fq_quantum=4542`), and `--role ptmp-cpe` (subscriber CPE with `fq_quantum=1514`).
   - Caps `mac80211` `fq_memory_limit` at `4 MiB` (preventing 64 MB RAM OOM crashes), configures per-AC `AQL` airtime limits (`VO 300/600`, `VI 1000/2000`, `BE 1500/3000`, `aql_threshold=5000`), sets `htt_max_amsdu_ampdu="2 64"`, and applies the **Wave 338 per-key `sysctl` loop** (`vm.min_free_kbytes=4096`, `tcp_limit_output_bytes=65536`, `tcp_notsent_lowat=8192`, `netdev_max_backlog=2048`).

---

## Quick Start (English)

### Option A: Tune Stock `airOS 8` (PtP or PtMP, Zero Flashing)
```sh
scp firmware/public_field_kits/airos8_ptp_ptmp_tuned_champion.sh ubnt@<RADIO_IP>:/tmp/
ssh ubnt@<RADIO_IP> "sh /tmp/airos8_ptp_ptmp_tuned_champion.sh --dry-run"
# Test in RAM first (reverts on reboot):
ssh ubnt@<RADIO_IP> "sh /tmp/airos8_ptp_ptmp_tuned_champion.sh --apply-ram"
# Persist across reboots (/etc/persistent/rc.poststart + cfgmtd -w -p /etc/):
ssh ubnt@<RADIO_IP> "sh /tmp/airos8_ptp_ptmp_tuned_champion.sh --persist"
```

### Option B: Tune `OpenWrt 24.10.4` (`ptp`, `ptmp-ap`, or `ptmp-cpe`)
```sh
scp firmware/public_field_kits/openwrt24_ptp_ptmp_champion.sh root@<RADIO_IP>:/tmp/
# For a PtP link (both AP and STA endpoints):
ssh root@<RADIO_IP> "sh /tmp/openwrt24_ptp_ptmp_champion.sh --apply-ram --role ptp"
# If verified, persist to /etc/hotplug.d/net/99-openmax-champion and /etc/rc.local:
ssh root@<RADIO_IP> "sh /tmp/openwrt24_ptp_ptmp_champion.sh --persist --role ptp"
```

---

## Guía Rápida (Español)

### Opción A: Optimizar `airOS 8` Stock (PtP o PtMP, sin flashear OpenWrt)
```sh
scp firmware/public_field_kits/airos8_ptp_ptmp_tuned_champion.sh ubnt@<IP_EQUIPO>:/tmp/
# Probar primero en memoria RAM (se revierte si se reinicia):
ssh ubnt@<IP_EQUIPO> "sh /tmp/airos8_ptp_ptmp_tuned_champion.sh --apply-ram"
# Hacer persistente en flash (/etc/persistent/rc.poststart + cfgmtd -w -p /etc/):
ssh ubnt@<IP_EQUIPO> "sh /tmp/airos8_ptp_ptmp_tuned_champion.sh --persist"
```

### Opción B: Optimizar `OpenWrt 24.10.4` (`ptp`, `ptmp-ap` o `ptmp-cpe`)
```sh
scp firmware/public_field_kits/openwrt24_ptp_ptmp_champion.sh root@<IP_EQUIPO>:/tmp/
# Para un enlace PtP (aplicar en ambos extremos AP y STA):
ssh root@<IP_EQUIPO> "sh /tmp/openwrt24_ptp_ptmp_champion.sh --apply-ram --role ptp"
# Persistir en /etc/hotplug.d/net/99-openmax-champion y /etc/rc.local:
ssh root@<IP_EQUIPO> "sh /tmp/openwrt24_ptp_ptmp_champion.sh --persist --role ptp"
```

See **[`docs/BENCHMARK_3WAY_AIROS_STOCK_VS_TUNED_VS_OPENWRT_CHAMPION.md`](../../docs/BENCHMARK_3WAY_AIROS_STOCK_VS_TUNED_VS_OPENWRT_CHAMPION.md)** for the full 3-way hardware benchmark measurements comparing **Stock `airOS 8`** vs **Tuned `airOS 8`** vs **`OpenWrt 24.10.4` Champion**.
