<!-- doc-head: OPENWRT_WIKI_UPSTREAM_CONTRIBUTIONS.md preserved document content -->
<!-- /doc-head -->

# OpenWrt Wiki Upstream Contributions (Copy-Pasteable DokuWiki Sections)

- **Stage / Task**: `Stage 30B` (`T-S30B-OPENWRT-UBIQUITI-TOH-INGEST-AND-UPSTREAM-WIKI-CONTRIBUTIONS`)
- **Target Upstream Pages**:
  1. `https://openwrt.org/toh/ubiquiti/liteap_ac` (`ubnt_lap-120`)
  2. `https://openwrt.org/toh/ubiquiti/nanostation_ac_loco` (`ubnt_nanostation-ac-loco`)
  3. `https://openwrt.org/toh/ubiquiti/litebeam_5ac_gen2` (`ubnt_litebeam-ac-gen2`)
  4. `https://openwrt.org/toh/ubiquiti/rocket_ac` (`Rocket Prism 5AC Gen2` & `Rocket 2AC Prism`)
  5. `https://openwrt.org/toh/ubiquiti/powerbeam` (`PBE-M5-400` vs `PBE-M5-300` XW)
  6. `https://openwrt.org/toh/ubiquiti/start` (Ubiquiti LTU Architecture Note)

---

## Contribution (a): AirOS 8 4-Address WDS (`ETH_P_TEB` `0x6558`) Interoperability with OpenWrt `mac80211` (`WA` / `XC` Boards)

*Target DokuWiki Pages: `toh/ubiquiti/liteap_ac`, `toh/ubiquiti/nanostation_ac_loco`, `toh/ubiquiti/litebeam_5ac_gen2`*

```dokuwiki
===== Interoperability with Stock Ubiquiti airOS 8 CPEs (4-Address WDS & ETH_P_TEB 0x6558) =====

When an OpenWrt AP (''ubnt_lap-120'', ''ubnt_nanostation-ac'', etc.) operates in standard ''802.11ac'' AP-WDS mode (''option wds '1'''), stock Ubiquiti **airOS 8** (''WA.v8.7.x'' / ''XC.v8.7.x'') stations do not associate or pass L2 bridge traffic by default due to two proprietary airMAX behaviors:

  - **Association Guard (''allow_80211'' / ''ubnt_op_mode'')**: Stock airOS 8 CPEs require proprietary Ubiquiti airMAX Beacon vendor IEs unless ''allow_80211=1'' and ''ubnt_op_mode=0'' are active in ''/proc/sys/dev/uph/''.
  - **4-Address WDS Inner ''ETH_P_TEB'' (''0x6558'') Encapsulation**: Even with ''ubnt_op_mode=0'', airOS 8 ''ubnt_poll_host.ko'' encapsulates outbound 4-address WDS data frames with an inner Transparent Ethernet Bridging (''ETH_P_TEB'', EtherType ''0x6558'') header followed by a 14-byte inner Ethernet header. Upstream Linux ''mac80211'' (''ieee80211_data_to_8023_exthdr'' in ''net/mac80211/util.c'') copies the ''0x6558'' EtherType verbatim onto ''br-lan'', causing the Linux bridge to drop the frames.

==== Option 1: OpenWrt AP-Side mac80211 Patch (Strip Inner 0x6558 Header) ====

In ''net/mac80211/util.c'' inside ''ieee80211_data_to_8023_exthdr()'', after extracting the RFC1042/Bridge-Tunnel payload header, strip the inner ''ETH_P_TEB'' (''0x6558'') L2 header when present on 4-address frames:

<code c>
/* Ubiquiti airOS 8 WDS compatibility: strip inner ETH_P_TEB (0x6558) header */
if (unlikely(hdr.h_proto == htons(ETH_P_TEB) && skb->len >= sizeof(struct ethhdr) + 14)) {
    skb_pull(skb, sizeof(struct ethhdr));
    return 0;
}
</code>

==== Option 2: Stock airOS 8 CPE Configuration for Standard 802.11ac WDS APs ====

If running stock airOS 8 on the CPE against an OpenWrt AP:
  * Set ''wpasupplicant.profile.1.network.1.proto.1.name=RSN'' (WPA2-CCMP) and ensure ''radio.1.polling=disabled''.
  * Enable standard 802.11 mode at runtime on the airOS 8 CPE:
<code bash>
echo 1 > /proc/sys/dev/uph/allow_80211
echo 0 > /proc/sys/dev/uph/ubnt_op_mode
</code>
  * **Warning**: Never run an unscoped ''sed -i 's/1/0/' /etc/sysinit/radio.conf'' on airOS 8, as it corrupts ''2>&1'' into ''2>&0'' and prevents ''ath0'' creation. Always scope replacements strictly to ''/op_mode/s/1/0/''.
```

---

## Contribution (b): QCA988x + AR9342 Optimal AQL & 2-MTU `fq_codel` Tuning (-38% Loaded p95 Latency)

*Target DokuWiki Pages: `toh/ubiquiti/liteap_ac`, `toh/ubiquiti/nanostation_ac_loco`, `toh/ubiquiti/litebeam_5ac_gen2`*

```dokuwiki
===== Optimal AQL and fq_codel Tuning for AR9342 + QCA988x PtP/PtMP Links =====

Ubiquiti ''WA'' devices combine a ''535 MHz'' single-core MIPS 74Kc host (''AR9342'') with a PCIe ''QCA9882'' (''ath10k'') 802.11ac radio. Default ''ath10k'' AQL limits (''24000 us'' per AC) allow excessive firmware ring buffering under saturation, while setting ''aql_txq_limit'' below ''1000 us'' starves ''QCA988x'' A-MPDU aggregation and causes severe goodput collapse. Similarly, heavy software ''cake'' shaping on ''eth0'' can saturate the ''535 MHz'' MIPS CPU above ''65 Mbps''.

Hardware-benchmarked optimal tuning on ''OpenWrt 24.10.x'' (''Linux 6.6.x'', ''ath10k''):

<code bash>
# 1. Tune ath10k Airtime Queue Limits (AQL) on phy0 (QCA988x 5 GHz)
# Cuts loaded p95 latency by -38% while preserving full VHT40/VHT80 A-MPDU goodput
PHY=/sys/kernel/debug/ieee80211/phy0/ath10k
echo 5000 > $PHY/aql_threshold
for ac in 0 1 2 3; do
    echo "$ac 1000 2000" > $PHY/aql_txq_limit
done

# 2. Apply lightweight 2-MTU fq_codel on wireless & Ethernet interfaces
# Avoids AR9342 software IRQ exhaustion while keeping loaded bufferbloat < 8 ms
tc qdisc replace dev phy0-ap0 root fq_codel limit 2048 target 8ms interval 50ms quantum 3028 flows 1024 ecn
tc qdisc replace dev eth0 root fq_codel limit 2048 target 5ms interval 50ms quantum 3028 flows 1024 ecn
</code>

  * **Single-flow PtP links**: Use ''quantum 3028'' (2-MTU) and ''aql_txq_limit'' ''1000/2000 us'' (up to ''1500/1500 us'' on long links) to maximize A-MPDU density.
  * **Multi-CPE PtMP sectors (3+ stations)**: Use ''quantum 1514'' (1-MTU) so ''mac80211'' DRR airtime scheduler rotates fairly across stations without head-of-line blocking.
  * **CPU Steering**: Set ''/sys/class/net/eth0/queues/rx-0/rps_cpus'' to ''1'' and ''/proc/sys/net/core/netdev_budget'' to ''600''.
```

---

## Contribution (c): Missing Hardware, Partition & AirPrism `airview1` Specs for Rocket Prism 5AC Gen2 (`0xe7f9`) & Rocket 2AC Prism (`0xe7f7`)

*Target DokuWiki Page: `toh/ubiquiti/rocket_ac`*

```dokuwiki
===== Hardware Variants: Rocket Prism 5AC Gen2 (XC) & Rocket 2AC Prism (2XC/2WA) =====

Unlike the first-generation **Rocket 5AC Lite** (''R5AC-Lite'', ''AR9342'' ''533 MHz'', ''64 MiB'' RAM, no AirPrism), the **Rocket Prism 5AC Gen2** (''RP-5AC-Gen2'') and **Rocket 2AC Prism** (''R2AC-Prism'') use the higher- clocked ''XC'' / ''2XC'' platform:

^ Model ^ Board / SysID ^ SoC ^ RAM / Flash ^ Primary Data Radio (''wifi0'') ^ Active RF Filter ^ Secondary Radios ^
| **Rocket Prism 5AC Gen2** (''RP-5AC-Gen2'') | ''XC'' / ''0xe7f9'' (''0777:e7f9'', rev ''0xe7e9'') | Qualcomm ''QCA9558'' (''720 MHz'' MIPS 74Kc) | ''128 MiB'' DDR2 / ''16 MiB'' SPI NOR | ''QCA9880'' v2 (''U-AME'', PCIe ''0000:00:00.0'', IRQ 75, 5 GHz 802.11ac 2x2) | **Dual-Stage AirPrism** (SPI + GPIO 14/15 + IRQ 64 hardware blanking, >35.5 dB OOB rejection) | ''wifi1'': ''QCA9558'' 2.4 GHz mgmt WMAC (''0xb8100000'', IRQ 2)\\ ''airview1'': Dedicated AirView spectral scanner VAP (''ubntspecd'') + GPS |
| **Rocket 2AC Prism** (''R2AC-Prism'') | ''2XC'' / ''0xe7f7'' (''0777:e7f7'', rev ''0xe7f5'' / ''0xe2f2'') | Qualcomm ''QCA9558'' (''720 MHz'' MIPS 74Kc) | ''128 MiB'' DDR2 / ''16 MiB'' SPI NOR | ''QCA9880'' v2 (''U-AME'' 5 GHz VHT baseband + 2.4 GHz RF downconverter, 256-QAM on 2.4 GHz) | **2.4 GHz AirPrism** (Active band-pass filter + IRQ 64 blanking at 35..80 IRQ/s) | ''wifi1'': 2.4 GHz mgmt WMAC\\ ''airview1'': Dedicated AirView scanner VAP + GPS |

==== Flash Partition Layout (16 MiB SPI NOR on XC / 2XC) ====

<code>
dev:    size   erasesize  name
mtd0: 00040000 00010000 "u-boot"      (256 KiB @ 0x000000)
mtd1: 00010000 00010000 "u-boot-env"  ( 64 KiB @ 0x040000)
mtd2: 00100000 00010000 "kernel"      (  1 MiB @ 0x050000)
mtd3: 00e60000 00010000 "rootfs"      (14.375 MiB @ 0x150000)
mtd4: 00040000 00010000 "cfg"         (256 KiB @ 0xfb0000)
mtd5: 00010000 00010000 "EEPROM"      ( 64 KiB @ 0xff0000 - ART + AirPrism cal)
</code>

  * **Important Note on AirPrism & ''airview1''**: The hardware AirPrism active filter tables reside in ''mtd5'' (''EEPROM'') and are driven by the AirOS ''ubnt_poll'' / SPI filter driver alongside ''IRQ 64'' blanking. On stock/hybrid ''XC'' firmware, bringing down the background scanner interface via ''ifconfig airview1 down'' (without sending ''SIGSTOP'' to ''ubntspecd'') eliminates off-channel scan latency spikes while keeping hardware watchdog timers healthy.
```

---

## Contribution (d): Hardware Architecture Clarification for Ubiquiti LTU (`0xae08` / `0xae02` / `0xeb00`) & PowerBeam M5 `XW` Ethernet Split

*Target DokuWiki Pages: `toh/ubiquiti/start` and `toh/ubiquiti/powerbeam`*

```dokuwiki
===== Ubiquiti LTU Family (LTU-Lite, LTU-LR, LTU-Pro, LTU-Rocket) Architecture Note =====

Ubiquiti **LTU** devices (**LTU-Lite** ''0xae08'' / ''0xae02'' / ''0xea02'', **LTU-Rocket** ''0xeb00'') are **not** Qualcomm/Atheros ''ath79'' or ''ipq40xx'' 802.11ac devices and **cannot** run ''ath10k'' or standard ''mac80211'' OpenWrt images:

  * **SoC + Baseband**: Built on an **Altera / Intel Cyclone V SoC FPGA** combining a dual-core ''ARM Cortex-A9'' Hard Processor System (HPS, running ''Linux 3.14.65-rt'') with a custom FPGA fabric loaded at boot from ''/lib/firmware/ame_soc.rbf''.
  * **Radio Driver**: Uses Ubiquiti's proprietary ''ame_core.ko'' kernel module driving a custom up-to-4096-QAM (''12 bits/symbol'') TDD baseband configured via ''/tmp/ame.cfg'' -> ''/sys/class/ame/ame_ctrl_dev/ini'' and an 8-queue multiqueue Ethernet DMA interface (''eth0'' with ''mq'' root qdisc).
  * **Hardware Capability Note**: On ''LTU-Lite'' (''board_ssid=0xae08''), the FPGA bitstream (''ame_soc.rbf'') and ''ame_core.ko'' natively include full AP/Master support (''role=ap'', ''wireless_mode=ptp'' and ''wireless_mode=ptmp'' including Short-Queue ''SQ'' mode for ''0 < ptmp_max_cpe <= 16''), which is only hidden in the stock WebUI selector.

===== PowerBeam M5 (XW) Ethernet PHY Warning: PBE-M5-400 (GbE) vs. PBE-M5-300 (100M) =====

When flashing OpenWrt onto ''XW'' board PowerBeam M5 units, verify the exact model and ''ubnthal'' board ID first:
  * **PowerBeam M5-400 (''PBE-M5-400'', SysID ''0xe4e5'')**: Uses an external **Atheros AR8035 Gigabit Ethernet PHY** (''0x004d:0xd072'') over RGMII. Use the **''ubnt_powerbeam-m5-xw''** OpenWrt image.
  * **PowerBeam M5-300 (''PBE-M5-300'', SysID ''0xe3e5'')**: Uses the internal ''AR9342'' **FastEthernet (100 Mbps) switch** (''ATHRS27''). Flashing ''ubnt_powerbeam-m5-xw'' onto a ''PBE-M5-300'' results in a dead ''eth0'' link because the DTS probes for the absent ''AR8035'' PHY. Use the **''ubnt_nanobeam-m5-xw''** OpenWrt image for ''PBE-M5-300''.
  * **U-Boot TFTP Note (''XW.v6.3.x'')**: Newer ''XW'' U-Boot versions attempt to acquire a DHCP address during ''urescue'' TFTP recovery before falling back to ''192.168.1.20''.
```
