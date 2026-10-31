<!-- doc-head: STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

[Document router](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md) | Part 2/2
<a id="october23-current-result-native-ltu-probe-restored-rocket-inventory-captured"></a> [October23 current result: native LTU probe restored; Rocket inventory captured](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#october23-current-result-native-ltu-probe-restored-rocket-inventory-captured) | <a id="october23-historical-d2-observation-before-operator-physical-confirmation"></a> [October23 historical D2 observation before operator physical confirmation](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#october23-historical-d2-observation-before-operator-physical-confirmation) | <a id="october22-evidence-alignment---current-bench-scope"></a> [October22 evidence alignment - current bench scope](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#october22-evidence-alignment---current-bench-scope) | <a id="stage-11b--static-reverse-engineering-of-ubiquiti-ltu-aflturocket-242--afltu-242-dual-soc-sdr-architecture-4096-qam-12x-code-paths--ofdma-subband-hooks"></a> [Stage 11B — Static Reverse Engineering of Ubiquiti `LTU` (`aflturocket-2.4.2` & `afltu-2.4.2`): Dual-SoC SDR Architecture, `4096-QAM` (`12X`) Code Paths & `OFDMA` Subband Hooks](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#stage-11b--static-reverse-engineering-of-ubiquiti-ltu-aflturocket-242--afltu-242-dual-soc-sdr-architecture-4096-qam-12x-code-paths--ofdma-subband-hooks) | <a id="1-executive-summary--epistemic-status"></a> [1. Executive Summary & Epistemic Status](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#1-executive-summary--epistemic-status) | <a id="2-exact-ameimg-container-parts--dtb-nand-partition-map-f08-remediated"></a> [2. Exact `AMEIMG` Container Parts & DTB NAND Partition Map (`F08` Remediated)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#2-exact-ameimg-container-parts--dtb-nand-partition-map-f08-remediated) | <a id="a-ameimg-container-parts-containersjson--0-trailing-bytes-all-15-payload-md5s-verified"></a> [A. `AMEIMG` Container Parts (`containers.json` — 0 Trailing Bytes, All 15 Payload MD5s Verified)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#a-ameimg-container-parts-containersjson--0-trailing-bytes-all-15-payload-md5s-verified) | <a id="b-primary-amesoc3-nand-flash-partition-map-dtb_propertiesjson--static-dtb-evidence"></a> [B. Primary `amesoc3` NAND Flash Partition Map (`dtb_properties.json` — Static DTB Evidence)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#b-primary-amesoc3-nand-flash-partition-map-dtb_propertiesjson--static-dtb-evidence) | <a id="3-corrected-ltu-modulation--rate-code-table-f10-remediated"></a> [3. Corrected `LTU` Modulation & Rate-Code Table (`F10` Remediated)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#3-corrected-ltu-modulation--rate-code-table-f10-remediated) | <a id="4-non-destructive-live-bench-test-plan-for-ltu-lite--ltu-rocket-f09f11-f13-remediated"></a> [4. Non-Destructive Live Bench Test Plan for `LTU-Lite` & `LTU-Rocket` (`F09–F11`, `F13` Remediated)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#4-non-destructive-live-bench-test-plan-for-ltu-lite--ltu-rocket-f09f11-f13-remediated)

<!-- stage822a-payload-begin -->

## 5. Physical Lab Bench Qualification Results on `LTU-Lite` (`2026-10-21`)

**Receipt**: [`artifacts/stage11_ltulite_bench_20261021.json`](<repo>/artifacts/stage11_ltulite_bench_20261021.json)
**Target Hardware**: `LTU-Lite` (`board.sysid=0xae08`, `board.rev=9`, `board.chip_rev=d`, `board.waferid=12`, `afltu.v2.4.0`, MAC `PUBLIC_DEVICE_0045`, connected on `ES-10XP` port `0/5` at `PUBLIC_DEVICE_0046%27`).

### 5.1 Step 1 Results — Live Hardware, NAND Partition Map & Capability Bits (`CONFIRMED`)
1. **Exact Match with DTB 13-Partition NAND Map**:
   - Live `/proc/mtd` confirmed all 13 NAND partitions (`erasesize = 0x00020000` / `128 KB`):
     - `mtd0`: `00080000` `"spl"`, `mtd1`: `00060000` `"uboot_env0"`, `mtd2`: `00060000` `"uboot_env1"`, `mtd3`: `00100000` `"uboot"`, `mtd4`: `000c0000` `"EEPROM"`, `mtd5`: `000c0000` `"cfg"`, `mtd6`: `00060000` `"dtb0"`, `mtd7`: `00500000` `"kernel0"`, `mtd8`: `02800000` `"rootfs0"`, `mtd9`: `00060000` `"dtb1"`, `mtd10`: `00500000` `"kernel1"`, `mtd11`: `02800000` `"rootfs1"`, `mtd12`: `02180000` `"reserved"`.
2. **Hardware Capability Bits (`hw_features`) — Zero Silicon Locks (`CONFIRMED`)**:
   - Reading `/sys/class/ame/ame_ctrl_dev/hw_features` on the physical `LTU-Lite` returned:
     ```json
     {"AMEX":0, "NO_AES":0, "NO_OFDMA":0, "NO_RS":0, "NO_LDPC":0, "NO_1024QAM":0, "NUMAES_1":0, "SISO_ONLY":0, "OBS_STUB":0, "YCTOP_STUB":0, "HFE_STUB":0}
     ```
   - **Conclusion (`CONFIRMED`)**: Neither `NO_LDPC` (`ame_check_hw_NoLDPC`) nor `NO_OFDMA` (`ame_check_hw_NoOFDMA`) is set on retail `LTU-Lite` (`0xae08`) hardware; both LDPC and OFDMA engines are physically enabled in silicon.

### 5.2 Step 2 Results — Live `4096-QAM` (`12X`, `0x1f`) Kernel & Scheduler Activation (`CONFIRMED`)
1. **Default PtMP State**:
   - `/sys/class/ame/ame_ctrl_dev/autoMcsCeiling` = `23` (`0x17`, `1024-QAM` `10X`).
   - `/sys/class/ame/ame_ctrl_dev/adj_mcs` = `0x20` (`auto`).
   - `/sys/class/ame/ame_ctrl_dev/autoMcs4096` = `10` ( writable `0/1/10`).
   - `/sys/kernel/debug/ame/sched_mcs` = `MIMO MCS:FB:1024Ql`.
2. **Live `4096-QAM` Activation in RAM/sysfs**:
   - Writing `echo 31 > /sys/class/ame/ame_ctrl_dev/autoMcsCeiling` succeeded (`rc=0`, readback `31`) and immediately transitioned `/sys/kernel/debug/ame/sched_mcs` from `MIMO MCS:FB:1024Ql` to **`MIMO MCS:FB:4096l`**.
   - Executing `/bin/af set automcsceil 4096qam` returned `Success: 'set automcsceil 4096qam'`, `/bin/af get automcsceil` reported **`4096qam (12x)`**, and `/sys/class/ame/ame_ctrl_dev/autoMcsCeiling` read `31`.
   - Setting `wireless.1.rate.mcs=5` in `/tmp/system.cfg` and running `/bin/ubntconf -c /tmp/system.cfg` generated `autoMcsCeiling = 31 ;max mcs` inside `/tmp/ame.cfg` in PtMP CPE mode (`wireless_mode = ptmp`).
   - Invoking `/usr/bin/ame_adj.sh mcs 4096l` (note: `ame_adj.sh mcs <level>` takes **2 arguments total**, whereas `cpe_mcs` on the AP takes 3–4 arguments) set `/sys/class/ame/ame_ctrl_dev/adj_mcs` = **`0x1f`** and `/usr/bin/ame_adj.sh mcs` reported **`4096qam LDPC 5/6`**.
   - Note on restoration: running `/usr/bin/ame_adj.sh mcs auto` resets `autoMcsCeiling` to `23` (from `/tmp/ame.cfg`) and `adj_mcs` to `0x20`, but the scheduler's cached fallback (`sched_mcs`) remains at `MIMO MCS:FB:4096l` until `echo 0x17 > /sys/class/ame/ame_ctrl_dev/adj_mcs` is issued prior to `echo 23 > autoMcsCeiling` + `echo 0x20 > adj_mcs`. All values were restored to exact baseline (`af get automcsceil = 1024qam (10x)`, `sched_mcs = MIMO MCS:FB:1024Ql`, `autoMcsCeiling=23`, `adj_mcs=0x20`, `autoMcs4096=10`).

### 5.3 Step 3 Results — Live `OFDMA` Subband Mask & Persistence Hooks (`CONFIRMED`)
1. **`ofdma_subbands` Numeric Bitmask (`CONFIRMED`)**:
   - Baseline `/sys/class/ame/ame_ctrl_dev/ofdma_subbands` = `0xff` (all 8 subbands enabled).
   - Writing `echo 254 > /sys/class/ame/ame_ctrl_dev/ofdma_subbands` updated the hardware subband mask to `0xfe`, and `echo 255 > /sys/class/ame/ame_ctrl_dev/ofdma_subbands` restored `0xff`.
   - `/sys/kernel/debug/ame/automcs` confirmed the per-subband DL measurement array (`FB`, `SB0..SB7`).
2. **Persistence Hook Verification (`cron` via `ubntconf`) (`CONFIRMED`)**:
   - Adding `cron.status=enabled`, `cron.1.status=enabled`, `cron.1.user=ubnt`, `cron.1.job.1.status=enabled`, `cron.1.job.1.schedule=* * * * *`, `cron.1.job.1.cmd=...` and running `/bin/ubntconf -c` invokes `Plugin: cron ... Done`, writes `/etc/crontabs/ubnt` and `/etc/sysinit/cron.conf`, and registers `null::respawn:/bin/crond -f -S` in `/etc/inittab` on stock `afltu` firmware without requiring `-cs` firmware.
   - Important `ubntconf` caveat: running `ubntconf -c` repeatedly on a live system without resetting `/etc/inittab` from `/usr/etc/inittab` appends duplicate respawn lines to `/etc/inittab`. Always copy `/usr/etc/inittab` to `/etc/inittab` before re-running `ubntconf -c` in live scripts, or persist via `/tmp/system.cfg` + `cfgmtd -w -p /etc/` so `ubntconf` runs once on boot.
3. **Live Baseband (`bbp`) & Frame (`frmcfg`) Telemetry via `/usr/www/ameeng.cgi` (`CONFIRMED`)**:
   - Invoking `/usr/www/ameeng.cgi` on the physical `LTU-Lite` (`40 MHz` channel width, `75.0%` duty cycle, `2.0 ms` frame length, `38` TX symbols, `118` RX symbols) confirmed that the baseband and frame calculator scale directly to **`12x` (`4096-QAM`)**:
     ```json
     "bbp": {
       "bw": 40,
       "currentMcs": "12x",
       "framelength": 89600,
       "sample_rate": 44.8
     },
     "frmcfg": {
       "frm_len": 2.0,
       "fft_size": 512,
       "ctrl_size": 80,
       "cz_len": 10,
       "duty_cycle": "75.0 %",
       "tx_symbol": 38,
       "rx_symbol": 118,
       "tx_rate_1x": 8960,
       "rx_rate_1x": 37760,
       "tx_rate_max": 107520,
       "rx_rate_max": 453120,
       "rate_max": 560640,
       "tx_rate_cur": 107520,
       "rx_rate_cur": 453120,
       "rate_cur": 560640
     }
     ```
   - Notice the exact math in `frmcfg`: `tx_rate_1x = 8,960 kbps` $\times 12 =$ **`107,520 kbps` (`107.52 Mbps` UL)** and `rx_rate_1x = 37,760 kbps` $\times 12 =$ **`453,120 kbps` (`453.12 Mbps` DL)**, yielding **`560.64 Mbps` aggregate capacity on a single `40 MHz` PtMP channel**!
4. **Why Connecting an `LTU-Rocket` (or Second LTU Unit) Completes Over-the-Air `4096-QAM` Verification**:
   - On the `LTU-Lite` (`board.sysid=0xae08`), `board.netmodes=6` (`CPE-PTP` + `CPE-PtMP`). Because LTU uses a proprietary SDR/FPGA waveform (`AD9361` + `ame_core.ko`), it can only establish an RF link with another LTU radio (an `LTU-Rocket` AP in PtMP mode or a second LTU CPE in PtP mode). Connecting an `LTU-Rocket` on the bench will allow measuring the live over-the-air `4096-QAM` (`12x`, `560.64 Mbps` @ `40 MHz`) constellation, EVM, LDPC BLER (`bler_rate`), and `iperf3` TCP/UDP throughput.
<!-- stage822a-payload-end -->
