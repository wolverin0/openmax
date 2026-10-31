<!-- doc-head: STAGE176A_WA_SQUASHFS_V6_R18_CHAMPION_BAKE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 176A — `WA` SquashFS `v6` (`hsqs`) Full Re-Bake with `R16..R18 + E2E-R1` (`76`-Window) Universal Champion (`T-S176A-WA-SQUASHFS-V6-R18-CHAMPION-BAKE`)

- **Claim Status**: `CONFIRMED`
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `hardware` (`AR9342` `535 MHz` MIPS 74Kc + `QCA9882` `64 MB` DDR2 RAM `WA` family, `QCA9558` `128 MB` `XC` family, and `AR9342`/`AR7241` `XW`/`XM` family)
- **Live Hardware Safety Gate**: `CONFIRMED` (`live_radios_241_242_20_250_touched = False`, `0` flash writes)
- **Memory-Master Claim**: `<memorymaster-id>` (`155117`, `scope="project:futuramax"`)

## 1. Executive Summary (`Stage 161A..163A` `R16..R18 + E2E-R1` Winners Propagated into SquashFS `v6`)

`Stages 161A..163A` completed rounds `R16..R18` plus end-to-end validation `E2E-R1` (`76` live counterbalanced `A1 -> B1 -> A2 -> B2` windows on `LiteAP AC` `.20` $\leftrightarrow$ `NanoStation 5AC Loco` `.250` $\leftrightarrow$ `Rocket 5AC Prism Gen2` `.198` $\leftrightarrow$ `LiteBeam M5` `.254` $\leftrightarrow$ `MK1-251` `198.18.0.66`), promoting three orthogonal kernel/PHY winners on top of the `Stage 145A` `R1..R15` champion:

| Round | Promoted Knob(s) | Live Measured Delta (`CONFIRMED`) | Subsystem Mechanism |
| :--- | :--- | :--- | :--- |
| **`R16` (`Stage 161A`)** | `FMX_DISTANCE_M=300` (`iw phy phy0 set distance 300`, `uci set wireless.radio0.distance=300`) | **`+13.68%` Goodput**, **`-15.88%` `p95` RTT**, **`+14.12%` Pareto** | Sets `QCA988x` ACK timeout & slot timing precisely for short/medium WISP cells without inflating contention slot overhead (`coverage_class=0`). |
| **`R17` (`Stage 162A`)** | `net.ipv4.tcp_pacing_ca_ratio=110`, `net.ipv4.tcp_pacing_ss_ratio=150`, `FMX_FQ_INITIAL_QUANTUM=3028` | **`+7.42%` 8-flow TCP Goodput**, **`-5.86%` `p50` RTT**, **`+6.91%` Pareto** | Smooths TCP congestion-avoidance (`110%`) and slow-start (`150%`) burst injection into `mac80211` `fq_codel` (`2×MTU` initial quantum). |
| **`R18 + E2E-R1` (`Stage 163A`)** | `FMX_PACKET_STEERING=1` (`rps_cpus=1` across `eth0`/`br-lan`/`phy*-*`), `FMX_FLOW_OFFLOADING=1`, `net.netfilter.nf_conntrack_max=16384` | **`-20.38%` E2E `p50` RTT**, **`-25.78%` E2E `p95` RTT**, **AP CPU idle `6.24% -> 12.11%` (`1.94x`)** | Enables `nftables` L3/L4 software flowtable fastpath and uniform softirq steering on `AR9342`/`QCA9558`. |

## 2. Propagated Scripts Across All Four Hardware Families

1. **[`firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-universal-champion`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-universal-champion)**:
   - Embeds all `R1..R18 + E2E-R1` (`76`-window) parameters (`FMX_MIN_FREE_KBYTES=4096`, `FMX_AQL_THRESHOLD=4000`, `FMX_AP_FQ_QUANTUM=3028`, `FMX_STA_FQ_QUANTUM=1514`, `FMX_FQ_LIMIT=1024`, `FMX_FQ_MEM_LIMIT=3145728`, `FMX_BQL_MIN=4542`, `FMX_BQL_MAX=36288`, `FMX_BQL_HOLD=600`, `FMX_DISTANCE_M=300`, `FMX_TCP_PACING_CA_RATIO=110`, `FMX_TCP_PACING_SS_RATIO=150`, `FMX_FQ_INITIAL_QUANTUM=3028`, `FMX_PACKET_STEERING=1`, `FMX_FLOW_OFFLOADING=1`, `FMX_NF_CONNTRACK_MAX=16384`).
2. **[`firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-pbe5ac-ptp-ap-241`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-pbe5ac-ptp-ap-241) & [`99-fmx-pbe5ac-ptp-sta-242`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-pbe5ac-ptp-sta-242)** (plus `99-fmx-pbe5ac-ptp`, `99-fmx-pbe5ac-ptp-ap`, `99-fmx-pbe5ac-ptp-sta`):
   - Propagated `wireless.radio0.distance='300'`, `network.globals.packet_steering='1'`, `firewall.@defaults[0].flow_offloading='1'`, `iw phy phy0 set distance 300`, `rps_cpus=1`, `tcp_pacing_ca_ratio=110`, `tcp_pacing_ss_ratio=150`, and `nf_conntrack_max=16384`.
3. **[`firmware/openwrt/xc_family_universal_kit/99-fmx-xc-universal-champion`](../firmware/openwrt/xc_family_universal_kit/99-fmx-xc-universal-champion)**:
   - Propagated `FMX_XC_DISTANCE_M=300`, `FMX_XC_TCP_PACING_CA_RATIO=110`, `FMX_XC_TCP_PACING_SS_RATIO=150`, `FMX_XC_FQ_INITIAL_QUANTUM=3028`, `FMX_XC_PACKET_STEERING=1`, `FMX_XC_FLOW_OFFLOADING=1`, and `FMX_XC_NF_CONNTRACK_MAX=16384` into the `128 MB` RAM `XC` kit and regenerated `sysupgrade-overlay-xc-universal-v1.tar.gz`.
4. **[`firmware/openwrt/xw_xm_family_universal_kit/99-fmx-xw-xm-ath9k-champion`](../firmware/openwrt/xw_xm_family_universal_kit/99-fmx-xw-xm-ath9k-champion)**:
   - Propagated `FMX_DISTANCE_M=300`, `FMX_TCP_PACING_CA_RATIO=110`, `FMX_TCP_PACING_SS_RATIO=150`, `FMX_FQ_INITIAL_QUANTUM=3028`, `FMX_PACKET_STEERING=1`, `FMX_FLOW_OFFLOADING=1`, and `FMX_NF_CONNTRACK_MAX=16384` into the `64 MB` `XW` / `32 MB` `XM` `ath9k` kit.

## 3. SquashFS `v6` (`hsqs`) Rootfs Re-Bake & Image Verification

On build VM `198.18.0.62` (`mksquashfs 4.6.1`, `-comp xz -b 256k -no-xattrs -all-root`), [`tools/firmware/bake_stage176a_to_178a_v6_and_cfg.py`](../tools/firmware/bake_stage176a_to_178a_v6_and_cfg.py) re-baked the `AP` and `STA` SquashFS `v6` (`hsqs`) rootfs images and updated:
- **`4` `PowerBeam 5AC Gen2` (`0xe3d6`) Kit Images** in [`firmware/openwrt/pbe5ac_gen2_ptp_kit/`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/) (`factory-ap-241.bin`, `factory-sta-242.bin`, `sysupgrade-ap-241.bin`, `sysupgrade-sta-242.bin`).
- **`16` `WA` Universal Kit Images (`4` primary boards × `factory/sysupgrade` × `AP/STA`)** in [`firmware/openwrt/wa_universal_kit_v34/`](../firmware/openwrt/wa_universal_kit_v34/) (`powerbeam-5ac-gen2`, `litebeam-5ac-gen2`, `lap-120`, `nanostation-ac-loco`), plus the `30` `sysid`-retagged `factory.bin` manifest entries in [`artifacts/autoresearch/stage143a_wa_15sysid_factory_emitter_receipt.json`](../artifacts/autoresearch/stage143a_wa_15sysid_factory_emitter_receipt.json).

## 4. Verification Receipt & Tests
- **Receipt**: [`artifacts/autoresearch/stage176a_wa_squashfs_v6_r18_champion_bake.json`](../artifacts/autoresearch/stage176a_wa_squashfs_v6_r18_champion_bake.json)
- **Builder**: [`tools/firmware/bake_stage176a_to_178a_v6_and_cfg.py`](../tools/firmware/bake_stage176a_to_178a_v6_and_cfg.py)
- **Pytest Suite**: [`tests/test_stage176a_to_178a_v6_bake_and_cfg.py`](../tests/test_stage176a_to_178a_v6_bake_and_cfg.py)
