<!-- doc-head: ADVERSARIAL_REVIEW_BRIEF.md preserved document content -->
<!-- /doc-head -->

# Adversarial Engineering Audit Brief — Stages 10 & 11 (Stock airOS 8 Interop, XC AirPrism RE, LTU 4096-QAM & OFDMA RE, and Public Summary)

## Role & Stance
You are an independent **Adversarial Principal Wireless & Embedded Systems Reviewer** (`gpt-6-astra`, `xhigh` reasoning effort).
Your job is NOT to rubber-stamp our findings. Your job is to **rigorously challenge, stress-test, cross-check against the unpacked firmware binaries/strings/symbols on disk, and try to falsify or find hidden failure modes** in our latest reverse-engineering and bench results.

## Safety & Operational Boundaries (HARD RULES)
1. **DO NOT SSH into, ping, or touch any live network radio (`10.10.100.*` or `192.168.1.*`)**. All verification must be performed strictly offline against the repository files, git history, and the unpacked firmware artifacts in `artifacts/firmware_re_xc_ltu/`.
2. Every critique or verification point must label claims as `CONFIRMED`, `INFERRED`, `UNKNOWN`, or `REFUTED` based on direct binary/rootfs/code evidence.

---

## Scope & Files to Audit

### 1. Stage 10 — Stock `airOS 8` (`WA.v8.5.12` / `WA.v8.7.25`) Interop & Revert (`FMX-0015`)
- **Primary Doc**: `docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md`
- **Adversarial Questions to Investigate**:
  1. Verify the 3-site RAM patch to `ubnt_poll_host.ko` (`offset 30748`, `31780`, `41976` on `WA.v8.7.25`) and `allow_80211=1`. Are there any background watchdog timers, re-association paths, DFS channel-switch paths (`CSA`), or `ubnt-Poll` state-machine resets in `ubnt_poll_host.ko` or `umac.ko` that could re-enable polling or drop the data path after hours/days of uptime?
  2. Audit the `ETH_P_TEB` (`0x6558`) 4-address WDS Transparent Ethernet Bridging strip (`skb_pull(skb, 18)`) vs standard `802.11` 3-address/4-address framing when `ptpmode=disabled` (`wds=enabled`) is used on the stock CPE against an OpenWrt `ath10k` AP (`wds=1`). What happens to multicast/broadcast ARP, IPv6 ND, DHCP, or VLAN-tagged (`802.1Q`) frames across that boundary?
  3. Audit the `cron.1.job.1.cmd` persistence mechanism on standard (non-`-cs`) `WA.v8.7.25`: what happens if `insmod` fails, if `/tmp/up_p.ko` is corrupted, or if the operator upgrades firmware later? Are there any failure modes where the fallback loop (`sleep 180` -> `cfgmtd -w -p /etc/`) could wear flash or trigger at the wrong time during a slow AP boot?

### 2. Stage 11A — `XC` (`Rocket Prism 5AC Gen2` & `PrismStation 5AC`) AirPrism & Dual-Radio Reverse Engineering
- **Primary Doc**: `docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md`
- **Unpacked Firmware & Evidence on Disk**:
  - `artifacts/firmware_re_xc_ltu/xc_8725_rootfs/` (extracted `XC.v8.7.25` rootfs)
  - `artifacts/firmware_re_xc_ltu/xc_874cs_rootfs/` (extracted `XC.v8.7.4-cs` rootfs)
  - `artifacts/firmware_re_xc_ltu/xc_fw_headers_summary.json`
  - `artifacts/firmware_re_xc_ltu/xc_boards_radios_complete.json`
  - `artifacts/firmware_re_xc_ltu/xc_dual_radio_hsr_vmlinux.json`
  - `artifacts/firmware_re_xc_ltu/xc_hsr_spi_and_uboot.json`
- **Adversarial Questions to Investigate**:
  1. Cross-check the `ubnt_poll_host.ko` binary in `artifacts/firmware_re_xc_ltu/xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko` (`189,880` bytes) and `xc_874cs_rootfs` (`186,560` bytes). Verify the exact instructions at offsets `30784`, `31816`, and `41976` (and `30072`, `31104`, `40916` for `8.7.4-cs`). Are the register usages (`$v0`, `$s0`, etc.) and branch targets 100% identical in semantics to `WA`, or could patching offset `41976` (`0x10000018`) skip something critical in `XC`?
  2. Audit the **AirPrism (`prism` + `hsr`)** claims against the actual extracted binaries (`vmlinux`, `ath_dev.ko`, `umac.ko`, `ubnthal.ko`):
     - Which board sysids (`0xe7f9` Rocket Prism 5AC Gen2 vs `0xe7e8`/`0xe7f8` Gen1) actually instantiate the `hsr` SPI bit-banged driver vs the `ubnt_prism_hook` GPIO (`13..16`) selector vs a PCIe/internal filter? Does `Rocket Prism 5AC Gen2` (`0xe7f9`) use `hsr` SPI (`GPIO 11/12/13/15`), `ubnt_prism_hook` (`GPIO 13..16`), or something else? Look closely for any GPIO pin conflict between `13..15` in `hsr` vs `13..16` in `prism`!
     - What is the exact risks/impact if an OpenWrt port leaves AirPrism uninitialized or mis-tuned?

### 3. Stage 11B — `LTU` (`aflturocket-2.4.2` & `afltu-2.4.2`) `4096-QAM` (`12X`), `OFDMA`, and Dual-SoC Architecture
- **Primary Doc**: `docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md`
- **Unpacked Firmware & Evidence on Disk**:
  - `artifacts/firmware_re_xc_ltu/ltu_extracted/aflturocket_242_rootfs_squashfs/` (extracted `LTU-Rocket` rootfs)
  - `artifacts/firmware_re_xc_ltu/ltu_extracted/afltu_242_rootfs_squashfs/` (extracted `LTU-Lite/LR/Pro` rootfs)
  - `artifacts/firmware_re_xc_ltu/ltu_extracted/` (FIT headers, `socfpga` secondary rootfs/DTBs if extracted)
- **Adversarial Questions to Investigate**:
  1. **Stress-test the `4096-QAM` (`12X`, internal rate `31` / `0x1f`) unlock claim**:
     - Inspect `artifacts/firmware_re_xc_ltu/ltu_extracted/aflturocket_242_rootfs_squashfs/lib/modules/3.10.20-ubnt-mtk/ame_core.ko`, `/sbin/ubntconf`, `/usr/bin/ame_adj.sh`, and any FPGA bitstreams (`*.rbf`) or calibration scripts.
     - Even if `ubntconf` sets `autoMcsCeiling = 31` (`0x1f`) when `wireless.1.rate.mcs=5` (`12x`), are there **other** guards inside `ame_core.ko` (e.g., inside `AME_Scheduler_AutoMCS_*`, `bbp_rf_set_super4096`, `AME_Data_SendCapMsg`, CPE capability negotiation, channel bandwidth restrictions like `<= 50 MHz` vs `100 MHz`, or PtMP vs PtP mode checks in kernel space) that would still clamp PtMP modulation to `1024-QAM` (`29`) or reject `31`?
     - Why did Ubiquiti disable `4096-QAM` in the PtMP WebUI while leaving it in `ame_core.ko`? Check if there are EVM/phase-noise limits on the `AD9361` PLL, PA linearity backoff requirements (`txpower` table), or LDPC decoder throughput limits at wide bandwidths.
  2. **Stress-test the hidden `OFDMA` (`radio.1.ofdma_mode=0..3`) and `AD9361` split-frequency claims**:
     - Check `/sbin/ubntconf` and `ame_core.ko` for `ofdma_mode` and `ofdma_subbands`. Is `ofdma_mode` functional in firmware `v2.4.2`, or is it gated/stubbed or dependent on specific FPGA builds?
     - Verify why `LTU` capabilities (split TX/RX frequency, `10/30/50/60/100 MHz` widths, `4096-QAM`) are or are not portable to `QCA988x` (`airMAX AC`), and whether any higher-layer concepts (like `ofdma_subbands`-style spectral scoring or `ame_adj.sh`-style rate ceiling telemetry) ARE portable.

### 4. Public Communication & Documentation Accuracy Audit
- **Primary Docs**: `docs/REDDIT_POST.md`, `README.md`, `docs/CURRENT_STATE.md`, `docs/RESEARCH_LEDGER.md`
- **Adversarial Questions to Investigate**:
  1. Are there any statements in `docs/REDDIT_POST.md` or `README.md` that overstate what has been physically tested on the bench vs what is currently static reverse-engineering (`Stage 11A` and `Stage 11B`)?
  2. Are there any technical inaccuracies, broken/ambiguous claims, or safety caveats that should be tightened before publishing on Reddit?

---

## Required Output
1. Write a comprehensive, pull-no-punches adversarial audit report to:
   `docs/ADVERSARIAL_REVIEW_STAGE10_11.md`
   Structure it with:
   - **Executive Verdict & Severity Table** (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `CONFIRMED SOLID`)
   - **Detailed Findings on Stage 10 (`WA` Stock `airOS 8` Interop)**
   - **Detailed Findings on Stage 11A (`XC` Rocket Prism & AirPrism)**
   - **Detailed Findings on Stage 11B (`LTU` `4096-QAM`, `OFDMA`, and Dual-SoC Architecture)**
   - **Audit of `docs/REDDIT_POST.md` & Public Claims**
   - **Concrete Actionable Fixes / Bench Verification Checklist**
2. When finished writing `docs/ADVERSARIAL_REVIEW_STAGE10_11.md`, reply to the orchestration run (`orca orchestration send` / complete your task) with a concise summary of your key findings and severity ratings.
