# QCA988x airMAX AC Custom-Stack Research Briefing

## Executive summary

- **CONFIRMED — Tier 1:** Your highest-value immediate experiment is **not switching from ath10k-CT to upstream ath10k; it is rebuilding ath10k-CT with spectral enabled**. Both OpenWrt 24.10 and current OpenWrt source wire `PACKAGE_ATH_SPECTRAL` to `ATH10K_SPECTRAL`, require the Atheros debug option, and select kernel `RELAY`; the ath10k-CT package separately propagates that into `CONFIG_ATH10K_SPECTRAL=y`. The CT driver itself contains the spectral WMI/relay implementation. Therefore the absence of every `spectral_*` entry on your otherwise-populated ath10k debugfs is strong evidence that your image was built without the spectral option, not evidence that QCA988x or ath10k-CT fundamentally cannot do FFT capture. URL: `https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/kernel/mac80211/ath.mk`; `https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/kernel/ath10k-ct/Makefile`; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/spectral.c`. citeturn23view0turn25search0 fileciteturn41file0L2-L2 fileciteturn24file0L2-L2

- **CONFIRMED — Tier 1:** `set_rates` is the wrong control for your supervisory data-rate work. In ath10k-CT it sets **management/broadcast/multicast fixed rates on a VDEV** through WMI; it is not the normal unicast data-rate controller. The source itself directs normal rate-control constraints to the ordinary mac80211/`iw` bitrate mechanism. URL: `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/debug.c`; `https://www.candelatech.com/ath10k-ug.php`. citeturn26view2 fileciteturn30file0L2-L2

- **CONFIRMED — Tier 1:** `set_rate_override` is much more interesting, but on **QCA988x Wave 1 it is only partially implemented**. The debugfs control is VDEV-wide and advertises fields for TPC, SGI, MCS, NSS, preamble, retries, dynamic bandwidth, bandwidth and RIX; however the current CT source explicitly says only Wave 2 has full support, while the QCA988x descriptor path carries the fixed rate/retry information available to Wave 1. It is therefore unsuitable as a documented per-subscriber AP control, and you should not assume its `tpc`, `sgi`, `bw` or `dynbw` fields work on QCA988x merely because the parser accepts them. URL: `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/debug.c`; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/htt_tx.c`. fileciteturn30file0L2-L2 fileciteturn31file0L2-L2 fileciteturn32file3L56-L66

- **CONFIRMED — Tier 1:** `ratemask-CT` is the cleanest existing hook for an outer-loop controller that leaves the firmware rate algorithm running. It extends the peer-association WMI message with **rate-disable masks**, specifically to give the host finer control over which rates firmware may use; CT documents it from firmware v15 onward. The missing piece is a documented, low-latency **per-peer runtime** userspace API: the feature exists at the WMI peer-association layer, but ordinary `iw ... set bitrates` is not documented by CT as a per-peer scheduler API. URL: `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/core.h`; `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt`. citeturn26view0 fileciteturn36file0L2-L14

- **CONFIRMED — Tier 1:** `htt_max_amsdu_ampdu` is a **radio/HTT-wide aggregation ceiling**, not a per-peer setting. Current CT source validates A-MPDU at **1–64 subframes** and A-MSDU at **1–31 subframes** and records firmware defaults of **64 A-MPDU / 3 A-MSDU**. The command is sent as one HTT aggregation configuration for the radio. No source located provides QCA988x p95/p99 latency measurements from changing it, making this one of the highest-priority empirical sweeps for your hardware. URL: `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/htt_tx.c`; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/debug.c`. fileciteturn33file0L2-L2 fileciteturn34file0L2-L2 fileciteturn35file0L2-L16

- **CONFIRMED — Tier 2:** There **is a CT Wave-1 Release 23 newer than Release 22**. Candela's current release notes put Release 23 first and describe one change: an attempted fix for a scanning crash by preventing `probe_timer` re-arm. Candela does **not** date Release 23 in those notes. An OpenWrt issue log from December 2025 additionally shows a QCA988x hw2.0 binary identifying as `10.1-ct-8x-__fW-023-23ea9f8e`, but that is Tier-4 corroboration rather than vendor release metadata. Meanwhile, current OpenWrt's CT-firmware Makefile still declares package version `2023.04.04` with a fixed QCA988x binary hash, so an OS upgrade should not be assumed to deliver 023 automatically. URL: `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt`; `https://github.com/openwrt/openwrt/issues/21243`; `https://github.com/openwrt/openwrt/blob/main/package/firmware/ath10k-ct-firmware/Makefile`. citeturn26view0 fileciteturn22file0L2-L6

- **CONFIRMED — Tier 1:** ath10k-CT **driver development is still active**, even though QCA988x firmware feature development is sparse. OpenWrt 24.10 tracks CT source dated **2024-07-30** and builds its 6.10 driver tree; current OpenWrt `main` tracks CT commit `fcbdb70…` dated **2026-07-31** and builds the 7.2 tree. That July 2026 CT commit explicitly pulls upstream stable fixes and additional guard logic. URL: `https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/kernel/ath10k-ct/Makefile`; `https://github.com/openwrt/openwrt/blob/main/package/kernel/ath10k-ct/Makefile`; `https://github.com/greearb/ath10k-ct/commit/fcbdb70debc261f9df6734bbb76d81cdc88e0e26`. citeturn21view0 fileciteturn41file0L2-L6 fileciteturn40file0L2-L6

- **CONFIRMED — Tier 2:** There is a concrete reason to leave the 24.10 series, but at present it is **maintenance/security lifecycle, not a demonstrated QCA988x latency win**. OpenWrt 25.12 moved to Linux 6.12 with a substantially newer backported mac80211/cfg80211 stack, and OpenWrt states that 24.10 security updates stop **after September 2026**. I found no controlled QCA988x experiment proving that 25.12 by itself lowers p95/p99 or improves airtime fairness versus your 6.6 baseline. URL: `https://github.com/openwrt/openwrt/releases`. citeturn22search7

- **REFUTED — Tier 1:** The visible `tpc` argument in `set_rate_override` is **not evidence of usable per-peer TX-power control on QCA988x**. The debugfs documentation says full override support is Wave 2 only, while the QCA988x-specific TX path uses its Wave-1 rate/retry mechanism. Candela's documented CFR/CSI facilities are likewise aimed at later Wave-2 devices rather than QCA988x. URL: `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/debug.c`; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/htt_tx.c`; `https://www.candelatech.com/ath10k-ug.php`. citeturn26view2 fileciteturn30file0L2-L2

- **INFERRED — Tier 1/2:** The best architecture for your stated objectives is therefore **mac80211/AQL/FQ queue control on the host + CT telemetry + a slow supervisory rate-mask loop**, not an attempt to emulate airMAX polling through host scheduling alone. The public QCA988x path still lacks a demonstrated hard-deadline host-to-air primitive or a public, buildable radio-firmware toolchain; SDR/FPGA systems such as openwifi show what true MAC programmability looks like, but they are different hardware. URL: `https://github.com/open-sdr/openwifi`; `https://www.candelatech.com/ath10k-10.1.php`; `https://github.com/greearb/ath10k-ct`. citeturn24search12turn26view1turn22search0

## Tier-one findings — questions one through five

### Question 1: ath10k-CT status and capability drift

**Finding: current driver drift is real; Wave-1 firmware drift is small**

`OpenWrt 24.10's ath10k-CT package is pinned to CT source 2024-07-30, commit ac71b14…, using the ath10k-6.10 tree; current OpenWrt main is pinned to CT source 2026-07-31, commit fcbdb70…, using ath10k-7.2.` | **CONFIRMED** | **Tier 1** | `https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/kernel/ath10k-ct/Makefile`; `https://github.com/openwrt/openwrt/blob/main/package/kernel/ath10k-ct/Makefile` | **ath10k-CT driver; all supported CT devices, including QCA988x** | **Your exact 24.10 software is roughly two years behind current CT driver source even though the radio firmware is nearly static. A driver-only backport is therefore a sensible experiment independently of changing OpenWrt release.** fileciteturn41file0L2-L6 fileciteturn40file0L2-L6

`The 2026-07-31 CT commit is primarily an upstream-stable/bug-fix synchronization and explicitly mentions additional guard logic; it is not presented as a new QCA988x MAC feature release.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/commit/fcbdb70debc261f9df6734bbb76d81cdc88e0e26` | **ath10k-CT driver** | **Expect robustness and kernel-integration changes before expecting a new scheduler or QCA988x feature set.** citeturn21view0

`Candela's current Wave-1 release notes contain Release 23 above Release 22. The sole Release-23 item in those notes is an attempted scan-crash fix: make probe_timer ignore re-arm.` | **CONFIRMED** | **Tier 2** | `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt` | **CT 10.1 Wave-1 firmware, which covers QCA988x** | **There is a newer firmware family than your `__fW-022`, but there is no documented scheduler/rate-control/aggregation breakthrough in its release note. Upgrade it first for an A/B stability check, not because there is evidence it will transform PtMP performance.** citeturn26view0

`The official Release-23 notes do not state a release date, complete binary build identifier, or a detailed regression/fix list beyond the probe_timer scan-crash item.` | **UNKNOWN** | **Tier 2** | `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt` | **CT Wave-1 firmware** | **Do not assign a date or assume 023 incorporates undocumented MAC changes.** citeturn26view0

`Current OpenWrt main still declares ath10k-ct-firmware package version 2023.04.04 and a fixed QCA988x firmware hash.` | **CONFIRMED** | **Tier 1** | `https://github.com/openwrt/openwrt/blob/main/package/firmware/ath10k-ct-firmware/Makefile` | **OpenWrt packaging / QCA988x CT firmware** | **A system upgrade and a radio-firmware upgrade are separate variables. Preserve that separation in your experiments.** fileciteturn22file0L2-L6

`A December-2025 OpenWrt issue log reports QCA988x hw2.0 running `10.1-ct-8x-__fW-023-23ea9f8e`.` | **INFERRED** | **Tier 4** | `https://github.com/openwrt/openwrt/issues/21243` | **QCA988x hw2.0 + CT firmware** | **This establishes a practical lead for a 023 binary/build identifier, but an issue log is weaker evidence than Candela's own release artifacts and should not be used as the authoritative release manifest.**

#### `set_rates`

`set_rates controls fixed VDEV management, broadcast and multicast rates. The implementation stores the chosen management/broadcast/multicast rate and sends it with ath10k_wmi_vdev_set_param().` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/debug.c` | **ath10k-CT, including QCA988x** | **Do not use it as your subscriber unicast-rate supervisor; it is useful instead for controlling airtime consumed by management/broadcast traffic.** fileciteturn30file0L2-L2

`The write is a WMI VDEV parameter operation when the VDEV is active; if the VDEV is down or on another band, the source stores the value for later application.` | **CONFIRMED** | **Tier 1** | same URL | **ath10k-CT** | **Its control latency includes a host-to-firmware WMI operation, unlike the host-side descriptor override path below.** fileciteturn30file0L2-L2

`A source-backed numerical upper bound on command-to-air update latency for set_rates on QCA988x was not found.` | **UNKNOWN** | **Tier 1/2 search** | same URL | **QCA988x** | **Measure rather than assume a control-loop period.**

#### `set_rate_override`

`The debugfs help describes set_rate_override as applying specified TX-rate parameters to all DATA frames on one VDEV. It explicitly states that only Wave 2 CT firmware has full support and that Wave 1 has only partial support.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/debug.c` | **ath10k-CT; QCA988x is the Wave-1 case** | **On an AP with many subscribers sharing one VDEV, this is not the per-peer steering interface you ultimately want.** fileciteturn30file0L2-L2

`Accepted parser fields are tpc, sgi, mcs, nss, pream, retries, dynbw, bw, rix and active; they are stored in the ath10k_vif object.` | **CONFIRMED** | **Tier 1** | same URL | **ath10k-CT** | **The scope is VDEV state, not a MAC-address/peer object.** fileciteturn31file0L2-L2

`The parser performs kstrtol() but does not implement per-field semantic bounds checks before assigning the values into the VDEV override fields.` | **CONFIRMED** | **Tier 1** | same URL | **ath10k-CT** | **Treat malformed/out-of-range inputs as unsafe experiment parameters; use only documented values and verify what the readback reports.** fileciteturn31file0L2-L2

`For QCA988x/QCA9887-class Wave-1 devices, the CT TX path has a dedicated rate-control override encoding path rather than the full Wave-2 override machinery.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/htt_tx.c` | **QCA988x specifically** | **This is why accepting `tpc=` or `bw=` in debugfs must not be confused with hardware support for those controls.** fileciteturn32file3L56-L66

`Current CT source intentionally avoids applying the override to small DATA packets in the relevant native-Wi-Fi path so that ARP/DHCP-like traffic remains under normal firmware handling; the threshold in the inspected code is 400 bytes.` | **CONFIRMED** | **Tier 1** | same URL | **ath10k-CT data TX path; QCA988x path included** | **An outer-loop test using only ICMP/short UDP probes can therefore give a false impression that the override is not working. Test both <400-byte and >400-byte MSDUs.** citeturn21view3

`Writing set_rate_override changes host VDEV state; the per-packet TX construction path consumes that state. No separate set-rate WMI transaction is visible in this override write path.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/debug.c`; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/htt_tx.c` | **ath10k-CT** | **This makes it potentially much faster to update than a firmware configuration transaction.** fileciteturn31file0L2-L2 fileciteturn32file3L56-L66

`The first eligible descriptor built after the write should observe the new host-side state.` | **INFERRED** | **Tier 1** | same URLs | **ath10k-CT** | **This is the control-loop model worth testing. It is an inference from code flow, not a guaranteed timing specification.**

`A hard microsecond/millisecond command-to-air bound for set_rate_override on AR9342+QCA988x is not documented.` | **UNKNOWN** | **Tier 1/2 search** | same URLs | **exact baseline** | **Timestamp it experimentally before designing any scheduler around it.**

#### `ratemask-CT`

`ratemask-CT denotes support for an extended peer-association command containing an array of rate-disable masks, explicitly intended to let the host exert finer control over which rates firmware may choose. The source identifies this as CT firmware v15+ functionality.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/core.h` | **ath10k-CT firmware/driver; includes QCA988x Wave 1** | **This is almost exactly the primitive needed for a learned outer loop: constrain the action space while retaining firmware RC inside that envelope.** fileciteturn36file0L2-L14

`Release 15 says arbitrary rate masks can disable all but selected rate families and were intended to support subsets of HT/VHT rates, while explicitly noting that those subsets had not yet been tested at introduction.` | **CONFIRMED** | **Tier 2** | `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt` | **CT Wave-1 firmware v15+** | **The primitive is documented, but old release-note confidence around arbitrary HT/VHT subsets was limited. Your 022 is much newer, yet an exhaustive current mask-validity table was not found.** citeturn26view0

`The public userspace mechanism documented by Candela remains ordinary `iw dev ... set bitrates`; I did not establish a supported API that independently changes a different mask for every associated AP peer at high rate.` | **UNKNOWN** | **Tier 1/2 search** | `https://www.candelatech.com/ath10k-ug.php`; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/mac.c` | **QCA988x AP PtMP** | **A small driver extension that exposes the underlying per-peer association mask may be more valuable than building a new rate algorithm.** citeturn26view2 fileciteturn37file0L2-L12

#### `txrate2-CT`

`txrate2-CT is a TX-status/reporting compatibility feature, not a rate-selection control. Current CT driver logic uses the flag when deciding whether a TX completion actually contains a valid reported rate; the Wave-1 issue is that not every frame later in an aggregate carries a useful rate report, which otherwise risks being interpreted as the zero rate-code/48-Mbit/s case.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/txrx.c`; `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt` | **CT Wave-1 / QCA988x TX-status path** | **Use it as a telemetry-quality indicator. It does not give your scheduler another knob.** citeturn26view0turn21view2

`Release 21 describes the corresponding firmware change as a new way to distinguish a missing TX-rate report from the all-zero representation that could otherwise look like 48 Mbit/s.` | **CONFIRMED** | **Tier 2** | `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt` | **CT Wave-1** | **Do not train an outer-loop controller on raw rate statistics without preserving this missing-vs-valid distinction.** citeturn26view0

#### `retry-gt2-CT`

`retry-gt2-CT is a capability marker answering whether firmware can safely handle a retry limit greater than two; it is not itself a retry-setting interface.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/core.h` | **ath10k-CT firmware/driver** | **Do not treat the advertised flag as evidence that changing retry depth dynamically is fully supported or latency-safe.** fileciteturn26file0L2-L11

`Release 21 fixed an assertion/crash when retries exceeded two.` | **CONFIRMED** | **Tier 2** | `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt` | **CT Wave-1** | **Your 022 is after this fix, so >2 no longer has the specifically documented old assert failure.** citeturn26view0

`The same Release-21 notes say the driver could configure software retries for aggregated/non-aggregated TIDs but did not actually exercise that facility at the time; they also say the author was uncertain whether firmware really handled the aggregate-retry value as expected.` | **CONFIRMED** | **Tier 2** | same URL | **CT Wave-1** | **There is not enough documentation to build a latency-sensitive retry controller around this without on-air validation.** citeturn26view0

#### `cust-stats-CT`

`cust-stats-CT literally advertises support for requesting CT custom statistics; it is a protocol/capability marker rather than a promise of arbitrary new per-peer counters.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/core.h` | **ath10k-CT** | **Treat individual debugfs counters as the API surface; do not infer counters that are not actually exported.** fileciteturn26file0L8-L11

`Your relevant CT source contains custom-stat handling behind debugfs surfaces including the extended PDEV and reorder-stat paths; some paths also defend against unexpectedly short Wave-1 firmware replies.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/debug.c` | **ath10k-CT, including Wave 1** | **For a controller, build against counters you can validate against packet captures rather than assuming firmware statistics are lossless ground truth.** citeturn24view3

### Question 2: spectral scan on QCA988x

`Upstream ath10k officially supports spectral FFT collection through debugfs/relayfs, with spectral_count, spectral_bins, spectral_scan_ctl and spectral_scan0.` | **CONFIRMED** | **Tier 2** | `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/spectral.html` | **ath10k 802.11ac devices; QCA988x is an ath10k-supported family** | **There is a supported software pipeline; this is not an ath9k-only feature.** citeturn25search0turn25search4

`ath10k-CT also carries a full spectral implementation using WMI spectral-enable/configuration commands and Linux relay output.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/spectral.c` | **ath10k-CT** | **You do not need to abandon CT's useful telemetry/rate hooks merely to obtain FFT samples.** fileciteturn24file0L2-L6

`The CT Kconfig requires ATH10K_DEBUGFS, selects RELAY and defaults ATH10K_SPECTRAL off.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/Kconfig` | **ath10k-CT** | **This directly explains how one can have an otherwise rich ath10k debugfs tree with no spectral entries.** fileciteturn23file0L2-L6

`OpenWrt 24.10 exposes this as PACKAGE_ATH_SPECTRAL; it depends on PACKAGE_ATH_DEBUG, selects KERNEL_RELAY, and maps to ATH10K_SPECTRAL.` | **CONFIRMED** | **Tier 1** | `https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/kernel/mac80211/ath.mk` | **your OpenWrt 24.10 build system** | **Rebuild your existing branch first; this changes one experimental variable rather than driver, kernel and firmware simultaneously.** citeturn23view0

`The 24.10 ath10k-CT package explicitly adds CONFIG_ATH10K_SPECTRAL=y when PACKAGE_ATH_SPECTRAL is selected.` | **CONFIRMED** | **Tier 1** | `https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/kernel/ath10k-ct/Makefile` | **ath10k-CT on OpenWrt 24.10** | **There is no package-level requirement to switch to upstream ath10k for this feature.** fileciteturn41file0L2-L6

For your 24.10 tree, the relevant build configuration is therefore:

```text
CONFIG_PACKAGE_MAC80211_DEBUGFS=y
CONFIG_PACKAGE_ATH_DEBUG=y
CONFIG_PACKAGE_ATH_SPECTRAL=y
```

`PACKAGE_ATH_SPECTRAL` selects the kernel relay infrastructure; the OpenWrt package then defines `CONFIG_ATH10K_SPECTRAL` for the CT module. | **CONFIRMED** | **Tier 1** | `https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/kernel/mac80211/ath.mk`; `https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/kernel/ath10k-ct/Makefile` | **exact build family** | **This is the first image I would build.** citeturn23view0 fileciteturn41file0L2-L6

Once present, the official ath10k acquisition sequence is:

```sh
ip link set dev wlan0 up
echo background > /sys/kernel/debug/ieee80211/phy0/ath10k/spectral_scan_ctl
echo trigger    > /sys/kernel/debug/ieee80211/phy0/ath10k/spectral_scan_ctl

# Generate/observe activity as appropriate; the upstream example uses a scan.
iw dev wlan0 scan

echo disable > /sys/kernel/debug/ieee80211/phy0/ath10k/spectral_scan_ctl
cat /sys/kernel/debug/ieee80211/phy0/ath10k/spectral_scan0 > /tmp/fft.dump
```

`Those controls and capture semantics are the documented upstream interface.` | **CONFIRMED** | **Tier 2** | `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/spectral.html` | **ath10k spectral interface** | **It produces a binary TLV stream suitable for your own spectrum-intelligence daemon.** citeturn25search0

`Allowed FFT lengths are 64, 128 and 256 bins.` | **CONFIRMED** | **Tier 2** | same URL | **ath10k spectral** | **You can explicitly trade sample footprint for frequency granularity.** citeturn25search0

`64-bin capture at 80-MHz channel width is known bad: the upstream driver considers those hardware samples bogus and refuses to report them.` | **CONFIRMED** | **Tier 1/2** | `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/spectral.html`; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/spectral.c` | **ath10k spectral, including CT copy** | **Do not use 80/64 in a channel-quality classifier.** citeturn25search0 fileciteturn24file0L2-L2

`The driver's own source contains an important calibration caveat: although hardware metadata says 20/40/80 MHz, experiments/plots led the implementation to label those FFT spans as 22/44/88 MHz. The source marks this with a TODO rather than treating the discrepancy as fully understood.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/spectral.c` | **ath10k/ath10k-CT FFT parser** | **Do not treat bin-center frequency or occupied-bandwidth estimates as laboratory-grade without calibrating against a signal generator.** fileciteturn24file0L2-L2

`Using the driver's 22-MHz interpretation, simple span/bin arithmetic gives approximately 343.75, 171.875 and 85.94 kHz/bin for 64/128/256 bins at nominal 20 MHz; these are bin spacings, not a proven effective resolution bandwidth or frequency-accuracy specification.` | **INFERRED** | **Tier 1 + arithmetic** | same source URL | **ath10k FFT output** | **Useful for storage/display planning; not sufficient for calibrated RF measurements.**

`The upstream documentation says spectral_count can be ignored by hardware/firmware in 20- and 40-MHz operation and appears more reliable in VHT80.` | **CONFIRMED** | **Tier 2** | `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/spectral.html` | **ath10k spectral path** | **Do not build your sample scheduler around an assumption of exact N-sample bursts.** citeturn25search0

`Background samples are documented as being returned while hardware is not busy transmitting/receiving.` | **CONFIRMED** | **Tier 2** | same URL | **ath10k spectral** | **Spectral sampling under saturated PtMP load will be biased by radio busy time; it is not an independent continuous RF instrument.** citeturn25search0

`A documented, deterministic FFT sample rate for QCA988x ath10k was not found. The ath9k documentation exposes explicit fft_period timing, but the ath10k interface documented here does not offer the corresponding deterministic timing control.` | **UNKNOWN** | **Tier 2** | `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/spectral.html`; comparison: `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath9k/spectral_scan.html` | **QCA988x/ath10k** | **Measure TSF deltas from actual records rather than assigning a nominal samples/s number.** citeturn25search0turn25search1

`Absolute amplitude/power accuracy of QCA988x FFT bins is not specified in the sources inspected. The ath10k record carries RSSI/noise/gain-related metadata, but its parser contains unresolved calibration assumptions.` | **UNKNOWN** | **Tier 1/2** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/spectral.c` | **QCA988x spectral** | **Use FFT primarily for comparative interference fingerprints/channel occupancy until you calibrate your own units.** fileciteturn24file0L2-L2

`The upstream documentation identifies FFT_eval as a userspace parser/visualizer and states that spectral_scan0 emits TLV binary data whose layout is defined by Linux's Atheros spectral-common structures.` | **CONFIRMED** | **Tier 2** | `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/spectral.html` | **ath10k** | **Your production stack can bypass plotting and parse the same TLVs into occupancy/interference features.** citeturn25search0

### Question 3: A-MPDU / A-MSDU control

`ath10k-CT's HTT aggregation configuration accepts max A-MPDU subframes from 1 through 64 and max A-MSDU subframes from 1 through 31; zero and values above those limits return EINVAL.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/htt_tx.c` | **ath10k-CT HTT path; QCA988x included** | **This gives you a bounded, reproducible experiment matrix instead of guessing at accepted values.** fileciteturn33file0L2-L2 fileciteturn34file0L2-L2

`The source records firmware defaults as A-MSDU=3 and A-MPDU=64.` | **CONFIRMED** | **Tier 1** | same URL | **ath10k-CT** | **Use 3/64 as the control arm, not whatever happens to be left from a previous debugfs write.** fileciteturn33file0L2-L2

`The configuration is sent with the HTT H2T AGGR_CFG message and stored in the radio's ath10k_htt object.` | **CONFIRMED** | **Tier 1** | same URL; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/debug.c` | **radio/HTT instance** | **It is a global radio-side aggregation ceiling, not a per-peer or per-TID latency policy.** fileciteturn34file0L2-L2 fileciteturn35file0L2-L16

`No source located reports controlled QCA988x measurements of p95/p99 loaded latency versus throughput while sweeping htt_max_amsdu_ampdu.` | **UNKNOWN** | **Tier 1–3 search** | implementation URL above | **QCA988x** | **This is a genuine evidence gap and a very good experiment for your project.**

`Because this knob is radio-global, a value that improves one weak/long subscriber can impose aggregation overhead/efficiency changes on every peer.` | **INFERRED** | **Tier 1** | same implementation URL | **QCA988x AP** | **The useful controller, if the sweep works, may need to choose a POP-wide compromise rather than per-subscriber values.**

### Question 4: upstream ath10k versus ath10k-CT

The relevant comparison for **your QCA988x Wave-1** is:

| Capability | upstream ath10k | ath10k-CT | Evidence / decision |
|---|---|---|---|
| QCA988x support | Yes. Linux documents QCA9880/QCA9882 hw2.0 support. | Yes; CT Wave-1 10.1 firmware and driver explicitly target the family. | **CONFIRMED, Tier 2.** `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k.html`; `https://www.candelatech.com/ath10k-10.1.php`. citeturn25search4turn26view1 |
| Spectral FFT | Yes when compiled with spectral/debugfs/relay support. | Yes; CT carries the same class of spectral implementation and OpenWrt can compile it. | **CONFIRMED, Tier 1/2.** `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/spectral.html`; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/spectral.c`. citeturn25search0 fileciteturn24file0L2-L6 |
| CT arbitrary rate masks | Upstream has standard bitrate-mask plumbing, but CT's extended rate-disable-mask firmware protocol is CT-specific. | Explicit `ratemask-CT` handling. | **CONFIRMED, Tier 1.** `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/core.h`. fileciteturn36file0L2-L14 |
| Per-packet/VDEV fixed-rate override | No equivalent CT-specific debugfs interface established. | `set_rate_override`, partial Wave-1 support. | **CONFIRMED for CT; UNKNOWN for any exact upstream equivalent, Tier 1.** `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/debug.c`. fileciteturn30file0L2-L2 |
| CT custom stats / extended PDEV / reorder hooks | Not the CT custom protocol. | Yes. | **CONFIRMED, Tier 1.** `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/core.h`. fileciteturn26file0L8-L11 |
| `txrate2-CT` status interpretation | No reason to understand a CT-only firmware contract unless specifically supported. | Explicit handling. | **CONFIRMED, Tier 1.** `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/txrx.c`. citeturn21view2 |
| Current exact-QCA988x PtMP stability winner | No rigorous contemporary head-to-head located. | No rigorous contemporary head-to-head located. | **UNKNOWN.** Do not substitute QCA4019/QCA9888 anecdotes for QCA988x evidence. |
| Current active maintenance | Upstream remains in Linux. | CT driver was updated July 2026 and current OpenWrt main follows that update. | **CONFIRMED, Tier 1.** `https://github.com/greearb/ath10k-ct/commit/fcbdb70debc261f9df6734bbb76d81cdc88e0e26`; `https://github.com/openwrt/openwrt/blob/main/package/kernel/ath10k-ct/Makefile`. citeturn21view0 fileciteturn40file0L2-L6 |

`For your stated priorities, spectral scan is not a reason to switch to upstream; CT-specific rate and telemetry hooks are concrete reasons to retain ath10k-CT while enabling spectral.` | **INFERRED** | **Tier 1/2** | sources in table | **exact project architecture** | **This gives you a richer experimental surface with fewer simultaneous changes.**

`Claims that upstream or CT is categorically "more stable under PtMP load" on QCA988x in 2025–2026 are unsupported by the evidence collected.` | **UNKNOWN** | **Tier 1–4 search** | relevant repositories/issues above | **QCA988x exact** | **Run your own long-duration A/B; do not import QCA4019/QCA9888 bug reports.**

### Question 5: OpenWrt 25.12 and newer wireless stack

`OpenWrt 25.12.0 moved the target kernels to Linux 6.12.71 and used cfg80211/mac80211 backports from kernel 6.18.7.` | **CONFIRMED** | **Tier 2** | `https://github.com/openwrt/openwrt/releases` | **OpenWrt 25.12** | **Moving from 24.10 changes both the base kernel and wireless subsystem by multiple upstream cycles.** citeturn22search7

`OpenWrt states it will not provide security updates for 24.10 after September 2026 and explicitly encourages migration to 25.12 before then.` | **CONFIRMED** | **Tier 2** | same URL | **your operating system** | **As of September 20, 2026, this is a concrete operational reason to prepare the migration even if radio performance is unchanged.** citeturn22search7

`I found no QCA988x-specific controlled measurement showing that the 25.12 mac80211 stack reduces p95/p99, changes AQL behavior beneficially, or improves airtime fairness relative to your 6.6.110 setup.` | **UNKNOWN** | **Tier 1–4 search** | `https://github.com/openwrt/openwrt/releases` | **QCA988x/ath10k-CT** | **Do not upgrade the production RF stack on an assumed performance gain. Benchmark it.**

`AQL's core purpose remains to keep excess buffering out of firmware/hardware so mac80211 FQ-CoDel can observe queueing delay; this mechanism predates Linux 6.6 rather than being a new 25.12 feature.` | **CONFIRMED** | **Tier 1** | `https://github.com/torvalds/linux/commit/3ace10f5b5ad94bdbd4b419dc9da2217d57720a9` | **mac80211/AQL** | **The principal queue-control feature you care about is already present in your 6.6 baseline.** citeturn24search3turn24search8

`A very recent 2026 patch series demonstrates large AQL/latency effects on ath11k/IPQ8074, including hardware-queue latency dropping dramatically when the driver actually exposes AQL control; this work is ath11k/IPQ8074, not ath10k/QCA988x, and the patch series was still under review.` | **CONFIRMED, cross-chip only** | **Tier 4** | `https://lkml.iu.edu/2609.1/01477.html` | **IPQ8074/ath11k — NOT your hardware** | **It reinforces the importance of verifying where the queue actually resides, but its measured gains must not be transferred to QCA988x.** citeturn24search10

`Current OpenWrt main uses a July-2026 ath10k-CT snapshot whereas the 24.10 branch remains on its July-2024 CT snapshot.` | **CONFIRMED** | **Tier 1** | `https://github.com/openwrt/openwrt/blob/main/package/kernel/ath10k-ct/Makefile`; `https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/kernel/ath10k-ct/Makefile` | **ath10k-CT** | **A controlled backport of the newer CT driver into your 24.10 test image is arguably a cleaner first experiment than jumping the entire OS.** fileciteturn40file0L2-L6 fileciteturn41file0L2-L6

**Decision:** **move off 24.10 for lifecycle reasons, but do not expect a free RF-performance win.** Before production migration, run the same deterministic PtMP workload on: current 24.10.4; 24.10.4 plus newer CT driver; and 25.12. This isolates driver drift from mac80211/kernel drift.

## Strategic and competitive findings — questions six through eleven

### Question 6: scheduled access / TDMA on commodity Wi-Fi

`openwifi provides an open-source, Linux/mac80211-compatible 802.11 full stack with the baseband implemented in FPGA/SDR hardware and publishes the FPGA hardware design, driver and software.` | **CONFIRMED** | **Tier 1** | `https://github.com/open-sdr/openwifi` | **FPGA/SDR — NOT QCA988x** | **It represents a genuinely programmable-MAC path where timing-critical behavior can live below the host/firmware boundary, but adopting it means changing radio hardware.** citeturn24search12

`SRT-WiFi/RT-WiFi research reports a real SDR-based testbed intended for deterministic real-time Wi-Fi and explicitly motivates the SDR implementation by limitations and maintenance difficulty of an earlier COTS-hardware RT-WiFi implementation.` | **CONFIRMED** | **Tier 3** | `https://arxiv.org/abs/2203.10390` | **SDR and prior COTS research; NOT QCA988x** | **The literature supports moving scheduling primitives close to the radio rather than attempting hard timing from a general-purpose host queue.** citeturn25academia27

`A source-verified timing-precision figure and host-to-air latency bound for hMAC, WiSHFUL/ORCA or an ath9k TDMA system was not established to the standard required by this briefing.` | **UNKNOWN** | **Tier 3 search** | no verified source retained | **other hardware** | **I will not import remembered figures without a verified paper.**

`No public work located here demonstrates deterministic/polled QCA988x access with a bounded host-to-air scheduling latency using stock/CT 10.1 firmware.` | **UNKNOWN** | **Tier 1–3 search** | `https://github.com/greearb/ath10k-ct`; `https://www.candelatech.com/ath10k-10.1.php` | **QCA988x exact** | **This is the key strategic gap.**

`Given that your accessible host controls ultimately feed a firmware-owned TX path and no hard-deadline primitive was found, reproducing airMAX-style deterministic polling solely in mac80211 userspace/host code is not supported by the public evidence.` | **INFERRED** | **Tier 1/2** | same URLs | **QCA988x + ath10k/CT** | **Concentrate on queue discipline, airtime allocation, rate envelopes and measurement unless/until radio firmware becomes modifiable.**

### Question 7: QCA988x firmware internals and replacement

`Candela describes its Wave-1 firmware as a modified Qualcomm/Atheros 10.1 firmware lineage and publishes binary releases/release notes rather than a public QCA988x firmware source tree.` | **CONFIRMED** | **Tier 2** | `https://www.candelatech.com/ath10k-10.1.php`; `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt` | **QCA988x/Wave-1 CT firmware** | **The existence of CT firmware proves modification is technically possible with the appropriate internal sources/tooling, not that an open rebuild path exists.** citeturn26view1turn26view0

`The public greearb/ath10k-ct repository is the host driver tree; it is not the buildable source for the QCA988x target firmware.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct` | **host ath10k-CT** | **Forking this repository will not let you implement an in-radio scheduler.** citeturn22search0

`Candela's Wave-1 documentation notes limitations around public firmware debugging/crash-decoding tooling tied to Qualcomm material rather than exposing a complete public firmware-development environment.` | **CONFIRMED** | **Tier 2** | `https://www.candelatech.com/ath10k-10.1.php` | **CT/QCA firmware** | **The public path stops well short of a reproducible firmware rebuild/debug cycle.** citeturn26view1

`A current, legally distributable public QCA988x firmware source tree + Xtensa toolchain + linker map + flash/load/debug procedure sufficient to rebuild 10.1 firmware was not found.` | **UNKNOWN** | **Tier 1–2 search** | same sources | **QCA988x exact** | **Do not put firmware replacement on the critical path of the near-term project.**

`The legal status of reverse-engineering/modifying proprietary QCA/Ubiquiti firmware depends on the code/artifacts used and jurisdiction; no project-specific legal conclusion is established here.` | **UNKNOWN** | **outside the technical evidence set** | N/A | **project** | **Treat technical feasibility and legal clearance as separate gates.**

### Question 8: per-peer TX power and CSI

`set_rate_override exposes a tpc field in its generic debugfs syntax but explicitly says only Wave-2 firmware has full override support.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/debug.c` | **ath10k-CT; QCA988x Wave 1 is partial** | **The mere presence of `tpc=` is not a QCA988x per-peer ATPC capability.** fileciteturn30file0L2-L2

`The QCA988x-specific descriptor override path does not establish the full Wave-2 TPC control path.` | **REFUTED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/htt_tx.c` | **QCA988x exact** | **Do not design subscriber ATPC around set_rate_override.** fileciteturn32file3L56-L66

`Candela documents rate/power table manipulation for Wave-1 devices, but this is radio/rate-table configuration rather than a documented instantaneous per-peer TX-power API.` | **CONFIRMED** | **Tier 2** | `https://www.candelatech.com/ath10k-ug.php`; `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt` | **Wave-1 CT firmware** | **Useful for calibration experiments, not equivalent to ATPC by subscriber.** citeturn26view2turn26view0

`A supported QCA988x per-peer TX-power/ATPC API was not established.` | **UNKNOWN** | **Tier 1/2 search** | sources above | **QCA988x exact** | **If ATPC matters, treat it as an experimental firmware-extension question, not an existing host-stack feature.**

`Candela's documented CFR/CSI facilities focus on later Wave-2 hardware; the inspected documentation does not establish QCA988x Wave-1 as a supported CFR/CSI target.` | **CONFIRMED regarding documented support; UNKNOWN regarding undocumented hacks** | **Tier 2** | `https://www.candelatech.com/ath10k-ug.php` | **CT stack** | **Do not budget QCA988x CSI as a deliverable on the basis of ath10k-CT's CSI-related code for other chips.** citeturn26view2

### Question 9: competing fixed-wireless PtMP systems

`A source-quality, mechanism-level comparison of current Cambium/Mimosa/Tarana implementations was not completed to the evidence standard of this report.` | **UNKNOWN** | **Tier 1–3 required** | N/A | **competitive systems** | **I am deliberately not filling this section with vendor claims or cross-generational marketing terminology.**

The practical conclusion is therefore **no competitive mechanism or numerical gain from those vendors is used anywhere else in this briefing**.

### Question 10: queueing and loaded latency

`The Linux AQL design exists specifically because firmware/hardware-offloaded 802.11ac devices can hold deep lower-layer queues invisible to mac80211 FQ-CoDel; AQL limits how much airtime is outstanding below mac80211 so the remaining backlog stays where FQ-CoDel can manage it.` | **CONFIRMED** | **Tier 1** | `https://github.com/torvalds/linux/commit/3ace10f5b5ad94bdbd4b419dc9da2217d57720a9` | **mac80211 architecture; directly relevant conceptually to ath10k** | **For your objective, the meaningful variable is not just qdisc configuration but where queued airtime actually resides.** citeturn24search3turn24search8

`A 2026 ath11k/IPQ8074 patch series measured a large loaded-latency reduction after making AQL actually control driver/hardware queue occupancy, while showing explicit throughput/latency tradeoffs as the AQL limit was tightened.` | **CONFIRMED, different chip/driver** | **Tier 4, real hardware** | `https://lkml.iu.edu/2609.1/01477.html` | **ath11k/IPQ8074, NOT QCA988x** | **The experimental method is valuable: sweep lower-layer airtime limits and simultaneously measure goodput, RTT and hardware/driver occupancy rather than assuming defaults are optimal.** citeturn24search10

`Those IPQ8074 numerical gains cannot be attributed to QCA988x.` | **REFUTED if transferred cross-chip** | **Tier 4** | same URL | **ath11k only** | **Use the methodology, not its numbers.** citeturn24search10

`No QCA988x-specific controlled CAKE/FQ-CoDel/AQL deployment dataset meeting the requested standard was found in this research pass.` | **UNKNOWN** | **Tier 3–4 search** | AQL implementation URL above | **QCA988x** | **Your own PtMP testbed is more decision-relevant than generic home-router bufferbloat results.**

### Question 11: supervisory rate control

`ratemask-CT provides a concrete mechanism for constraining firmware RC's allowable rates without replacing the firmware rate algorithm.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/core.h` | **QCA988x CT firmware** | **This maps naturally to a slow outer loop using distance, long-term PER/retry history, RSSI/noise and station-specific service objectives.** fileciteturn36file0L2-L14

`CT firmware also defines a peer-fixed-rate capability and Release 22 notes say that feature was enabled on January 17, 2021.` | **CONFIRMED as source/release-note capability** | **Tier 1/2** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/core.h`; `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt` | **CT firmware family** | **A small custom driver control path may be able to get closer to genuine per-peer supervision than the VDEV-wide debugfs override.** fileciteturn27file8L94-L104 citeturn26view0

`The WMI source contains a wmi_peer_fixed_rate_cmd keyed to VDEV/peer information.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/wmi.h` | **ath10k-CT protocol** | **This deserves source-level prototyping before attempting a new radio scheduler.** fileciteturn27file0L2-L11

`A peer-reviewed deployment study matching your exact proposed architecture — QCA988x firmware RC supervised by per-subscriber learned rate masks on fixed PtMP links — was not located.` | **UNKNOWN** | **Tier 3 search** | N/A | **exact project** | **Treat the outer loop as an engineering hypothesis to validate, not a literature-backed guaranteed gain.**

A conservative first controller should therefore change a peer's **allowed rate envelope much more slowly than packet-level RC operates**, and only on strong persistent evidence such as repeated high retry/PER excursions or stable link margin. That controller structure is **INFERRED**, not a sourced performance claim; its attraction is that it exploits `ratemask-CT` without trying to out-run firmware RC.

## What changed recently

**July 31, 2026 — ath10k-CT driver:**  
`Candela/greearb committed fcbdb70…, pulling upstream stable changes and bug fixes and specifically adding guard logic around recovery-sensitive paths.` | **CONFIRMED** | **Tier 1** | `https://github.com/greearb/ath10k-ct/commit/fcbdb70debc261f9df6734bbb76d81cdc88e0e26` | **ath10k-CT** | **This is the most concrete ath10k-CT development newer than your 24.10 driver snapshot.** citeturn21view0

`Current OpenWrt main has adopted that exact 2026-07-31 CT commit and builds the ath10k-7.2 CT source tree.` | **CONFIRMED** | **Tier 1** | `https://github.com/openwrt/openwrt/blob/main/package/kernel/ath10k-ct/Makefile` | **OpenWrt main + ath10k-CT** | **The current driver can be backported and tested separately from a radio-firmware change.** fileciteturn40file0L2-L6

**August–September 2026 — mac80211/AQL research activity:**  
`An ath11k series under review makes that driver participate in mac80211 AQL/airtime fairness and measures substantial hardware-queue latency changes on IPQ8074.` | **CONFIRMED, cross-chip** | **Tier 4** | `https://lkml.iu.edu/2609.1/01477.html` | **ath11k/IPQ8074 only** | **It is recent evidence that the host/firmware queue boundary remains performance-critical, but it is not an ath10k patch for you to cherry-pick.** citeturn24search10

**OpenWrt 25.12 series:**  
`25.12 moved to Linux 6.12 and a 6.18-derived mac80211/cfg80211 backport baseline; OpenWrt simultaneously announced that 24.10 will receive no security updates after September 2026.` | **CONFIRMED** | **Tier 2** | `https://github.com/openwrt/openwrt/releases` | **OpenWrt** | **Migration is now a lifecycle requirement even though the performance benefit on QCA988x remains unproven.** citeturn22search7

**Release 23 Wave-1 firmware:**  
`Candela's current release notes now contain Release 23, whose documented change is an attempted scan-crash fix.` | **CONFIRMED, date UNKNOWN** | **Tier 2** | `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt` | **QCA988x-class CT 10.1 firmware** | **A newer firmware exists, but the official note does not establish a mid-2025-or-later release date, so I do not classify it as a dated post-mid-2025 development.** citeturn26view0

**December 2025 corroboration:**  
`An OpenWrt issue log from December 2025 reports a QCA988x hw2.0 023 build, `10.1-ct-8x-__fW-023-23ea9f8e`.` | **INFERRED** | **Tier 4** | `https://github.com/openwrt/openwrt/issues/21243` | **QCA988x** | **This is evidence that a 023 binary was in circulation by then, but it is not authoritative release metadata.**

## Contradictions and evidence conflicts

**Peer-fixed-rate in Release 22 versus your advertised feature list.** Candela's Release-22 notes say “Enable peer fixed rate feature” on January 17, 2021, and current CT driver source defines `ATH10K_FW_FEATURE_PEER_FIXED_RATE`. Your exact 022 boot feature list, however, does **not** contain `peer-fixed-rate`, while a later 023 log reportedly does. | **CONTRADICTION — unresolved** | **Tier 1/2 versus exact observed baseline** | `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt`; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/core.h`; `https://github.com/openwrt/openwrt/issues/21243` | **QCA988x CT firmware** | **Trust your running feature bitmap over generic release notes. Do not use peer-fixed-rate until the firmware actually advertises it or you establish why your build omits the bit.** citeturn26view0 fileciteturn27file8L94-L104

**`set_rate_override` parser versus actual Wave-1 capability.** Debugfs accepts `tpc`, `sgi`, `mcs`, `nss`, `pream`, `retries`, `dynbw`, `bw`, `rix`, and `active`, which can make it look like all are actionable. The same help text says only Wave 2 has full support, and the QCA988x-specific TX path is materially narrower. | **CONTRADICTION resolved in favor of the device-specific TX implementation** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/debug.c`; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/htt_tx.c` | **QCA988x Wave 1** | **A parser field is not a hardware capability.** fileciteturn30file0L2-L2 fileciteturn32file3L56-L66

**Spectral “20/40/80 MHz” versus “22/44/88 MHz.”** Hardware metadata is nominally 20/40/80; ath10k's spectral parser explicitly says experiments/plots look more like 22/44/88 and substitutes those widths in emitted records. | **CONTRADICTION unresolved at RF-calibration level** | **Tier 1** | `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/spectral.c` | **ath10k spectral** | **Calibrate bin frequency against a known CW/tone source before using spectral output for quantitative interferer bandwidth/frequency estimates.** fileciteturn24file0L2-L2

**Retry configurability versus retry semantics.** CT Release 21 says software retry parameters exist, yet explicitly says the ath10k driver did not exercise them at that time and expresses uncertainty around aggregate retries; the same release fixed the >2 retry crash. | **CONTRADICTION/ambiguity unresolved** | **Tier 2** | `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt` | **Wave-1 CT firmware** | **`retry-gt2-CT` proves crash-safe capability evolution, not that retry-depth control is fully understood.** citeturn26view0

**“25.12 is newer” versus “25.12 is faster.”** OpenWrt unequivocally documents newer kernel/mac80211 components and the 24.10 EOL schedule; no exact-QCA988x controlled data found establishes a latency/goodput gain from the upgrade. | **REFUTED if "newer" is treated as proof of faster** | **Tier 2 plus evidence gap** | `https://github.com/openwrt/openwrt/releases` | **your baseline** | **Upgrade for lifecycle, benchmark for performance.** citeturn22search7

## UNKNOWNS

The following are **not established** by the public evidence collected and should be treated as experimental questions rather than assumptions:

- **UNKNOWN — exact provenance of Release 23:** authoritative release date, complete changelog beyond the one scan-crash item, exact currently recommended QCA988x community binary, and its canonical hash. Official source checked: `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt`. citeturn26view0

- **UNKNOWN — exact rate-control update latency:** no documented worst-case command/write-to-air delay for `set_rate_override`, `ratemask-CT`, normal bitrate masks, or peer-fixed-rate on AR9342 + QCA988x. Sources: `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/debug.c`; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/htt_tx.c`.

- **UNKNOWN — runtime per-peer arbitrary rate mask API:** `ratemask-CT` is present at the peer-association protocol level, but I did not establish an existing supported userspace interface for fast independent per-peer mask updates on a single AP VDEV. Source: `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/core.h`. fileciteturn36file0L2-L14

- **UNKNOWN — why your 022 does not advertise peer-fixed-rate:** release notes say the feature was enabled, while your exact feature list omits it. Source: `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt`. citeturn26view0

- **UNKNOWN — QCA988x spectral sample rate:** no reliable maximum or deterministic FFT samples/s figure was established; 20/40-MHz `spectral_count` behavior is itself documented as problematic. Source: `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/spectral.html`. citeturn25search0

- **UNKNOWN — QCA988x spectral calibration:** effective RBW, frequency accuracy, amplitude linearity and absolute dBm accuracy are not specified by the inspected ath10k documentation; driver source itself contains unresolved 20/22, 40/44 and 80/88-MHz interpretation comments. Source: `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/spectral.c`. fileciteturn24file0L2-L2

- **UNKNOWN — aggregation/latency curve:** no credible published QCA988x p95/p99-versus-goodput sweep for `htt_max_amsdu_ampdu` was found. Implementation source: `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/htt_tx.c`. fileciteturn33file0L2-L2

- **UNKNOWN — current driver winner under PtMP:** no 2025–2026 controlled QCA988x loaded-PtMP comparison between upstream ath10k and ath10k-CT was found. Repositories: `https://github.com/greearb/ath10k-ct`; upstream overview `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k.html`. citeturn22search0turn25search4

- **UNKNOWN — performance reason for 25.12:** lifecycle reason is clear; exact p95/p99 or fairness improvement on this silicon is not. Source: `https://github.com/openwrt/openwrt/releases`. citeturn22search7

- **UNKNOWN — open QCA988x radio-firmware development path:** no verified public source/toolchain/linker-map/debug environment sufficient to rebuild the 10.1 target firmware was established. Sources: `https://www.candelatech.com/ath10k-10.1.php`; `https://github.com/greearb/ath10k-ct`. citeturn26view1turn22search0

- **UNKNOWN — hard scheduled-access bound:** no verified QCA988x host-to-air timing primitive giving deterministic polled/TDMA access was found. Open SDR systems exist, but they are different hardware: `https://github.com/open-sdr/openwifi`; `https://arxiv.org/abs/2203.10390`. citeturn24search12turn25academia27

- **UNKNOWN — QCA988x per-peer ATPC and CSI:** the generic CT surfaces do not establish either as a supported Wave-1 feature. Source: `https://www.candelatech.com/ath10k-ug.php`. citeturn26view2

- **UNKNOWN — competitive mechanisms and learned-rate literature:** I did not establish source-quality, current mechanism details for Cambium/Mimosa/Tarana or a deployment paper matching the proposed QCA988x outer-loop controller. No claims from those areas are used in the recommendations.

## Suggested experiments

**Spectral-enable-only image.** Build the **same OpenWrt 24.10.4 tree and same ath10k-CT/022 firmware**, changing only `CONFIG_PACKAGE_ATH_DEBUG=y`, `CONFIG_PACKAGE_ATH_SPECTRAL=y` and the already-required mac80211 debugfs support. OpenWrt maps this directly to `ATH10K_SPECTRAL` and `KERNEL_RELAY`. URL: `https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/kernel/mac80211/ath.mk`; `https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/kernel/ath10k-ct/Makefile`. citeturn23view0 fileciteturn41file0L2-L6  
**Question answered:** Is spectral missing solely because of build configuration, and does your exact 022 firmware respond to the WMI spectral commands?

Run 20/40/80 MHz captures at 64/128/256 bins where allowed. Record record-count/s, TSF delta distribution, CPU load, packet goodput, p95/p99 latency and FFT sample loss while RF utilization is swept from idle to saturation. Include a known CW generator or narrowband transmitter at several offsets if available. This directly resolves sample cadence and the driver's documented width/calibration ambiguity. URL: `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/spectral.html`; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/spectral.c`. citeturn25search0 fileciteturn24file0L2-L2

**Aggregation factorial.** With a fixed topology and either stable high-SNR links or rate-constrained stations, sweep:

```text
A-MSDU / A-MPDU
3 / 64   # documented firmware default/control
3 / 32
3 / 16
3 / 8
1 / 64
1 / 32
1 / 16
1 / 8
```

The source-enforced domains are A-MSDU 1–31 and A-MPDU 1–64. URL: `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/htt_tx.c`. fileciteturn33file0L2-L2

For each arm, run several interleaved replicates rather than all of one setting sequentially. Capture downstream and upstream separately; measure payload goodput/MHz, p50/p95/p99 probe RTT, packet loss, retries, airtime, aggregate sizes if pktlog exposes them, AR9342 CPU utilization and memory pressure.  
**Question answered:** Is part of the frozen vendor stack's loaded-latency disadvantage recoverable simply by capping aggregation depth, and where is your Pareto frontier between goodput and tail latency?

**`set_rate_override` scope and actuation-latency test.** Associate at least two subscribers to one AP VDEV. Generate 1500-byte UDP streams to both and use an independent monitor receiver. Alternate the VDEV override between two unmistakably separated valid MCS settings while recording the monotonic timestamp of each debugfs write and on-air transmission rates. Repeat with sub-400-byte and >400-byte traffic. The implementation is VDEV-scoped and current CT code has the small-frame exception. URL: `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/debug.c`; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/htt_tx.c`. fileciteturn30file0L2-L2 fileciteturn31file0L2-L2  
**Questions answered:** actual command-to-air latency; whether every subscriber on the AP VDEV changes together; which frame types/sizes bypass the override; and exactly which Wave-1 fields affect air behavior.

**Explicit Wave-1 field validation.** Holding all else fixed, independently toggle `sgi`, `tpc`, `dynbw`, `bw`, `rix`, MCS/NSS/preamble and retries. Validate with a monitor capture, calibrated power receiver where relevant, and ACK/retry statistics. The source says Wave-1 support is partial. URL: `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/debug.c`. fileciteturn30file0L2-L2  
**Question answered:** which accepted parser fields are actually effective on your exact QCA988x/022 build. This is especially important before definitively closing the door on TPC.

**Rate-mask actuation test.** Use ordinary `iw` bitrate-mask changes first, then inspect on-air rate selection and peer-association traffic. Perform the change while a peer remains associated and again across reassociation. `ratemask-CT` exists specifically as rate-disable data in the peer-association command. URL: `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/core.h`; `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt`. fileciteturn36file0L2-L14 citeturn26view0  
**Questions answered:** Does changing the mac80211 bitrate mask update an already-associated peer immediately on your build? What is the actuation delay? Is the effect really per-peer internally, or effectively per-interface through the current API?

**Peer-fixed-rate probe.** First do nothing except record the firmware feature bitmap on 022 and 023. If 023 advertises `peer-fixed-rate`, trace the driver's WMI path and expose the existing `wmi_peer_fixed_rate_cmd` through a minimal private netlink/debugfs test hook rather than abusing VDEV-wide `set_rate_override`. The capability and WMI structure are present in current CT source. URL: `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/core.h`; `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/wmi.h`. fileciteturn27file8L94-L104 fileciteturn27file0L2-L11  
**Question answered:** Is the latent CT per-peer fixed-rate primitive actually usable on QCA988x, and does it provide the missing per-subscriber control surface?

**Driver-only backport A/B.** Build the current CT July-2026 driver against your controlled OpenWrt test environment while leaving radio firmware and userspace configuration unchanged, then compare against the 24.10 CT July-2024 driver snapshot. The source versions are explicit in OpenWrt packaging. URL: `https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/kernel/ath10k-ct/Makefile`; `https://github.com/openwrt/openwrt/blob/main/package/kernel/ath10k-ct/Makefile`. fileciteturn41file0L2-L6 fileciteturn40file0L2-L6  
**Question answered:** Do two years of CT driver maintenance alter crash rate, TX completion behavior, stats correctness or tail latency without confounding kernel/mac80211 changes?

**Firmware 022 versus 023 A/B.** Keep driver/kernel identical. Test association churn, simultaneous scan/background spectral activity, long-duration PtMP load and radio recovery. Release 23's documented purpose is a scan-crash mitigation, so deliberately include repeated scan activity. URL: `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt`. citeturn26view0  
**Question answered:** Does 023 fix a problem you can reproduce, and does it change anything else observable in rate/status behavior despite its minimal published changelog?

**Queue-boundary test.** Under a fixed downstream overload, sample mac80211 backlog, per-station airtime/AQL state, firmware/HTT outstanding work and loaded probe RTT together. Then sweep whichever AQL thresholds your running mac80211 exposes while keeping traffic and rate constant. The AQL design exists specifically to constrain invisible lower-layer airtime backlog. URL: `https://github.com/torvalds/linux/commit/3ace10f5b5ad94bdbd4b419dc9da2217d57720a9`. citeturn24search3turn24search8  
**Question answered:** Is your p99 currently dominated by mac80211/FQ backlog, ath10k/HTT backlog, or firmware aggregation? Until you know this, scheduler work risks optimizing the wrong queue.

**Three-image 24.10-to-25.12 migration experiment.** Compare, on the same RF bench:

```text
A: OpenWrt 24.10.4 + current baseline CT driver/FW
B: OpenWrt 24.10.4 + newer CT driver + same FW
C: OpenWrt 25.12 + its wireless stack + same radio FW where practical
```

OpenWrt documents the 25.12 kernel/mac80211 transition and the 24.10 lifecycle deadline. URL: `https://github.com/openwrt/openwrt/releases`. citeturn22search7  
**Question answered:** whether any improvement comes from ath10k-CT itself or the newer kernel/mac80211 stack.

For every one of these experiments, report **p95 and p99 loaded latency alongside useful payload goodput/MHz, Jain-style subscriber fairness or your selected airtime-fairness metric, retry airtime and CPU/RAM consumption**. Do not select a winner from peak throughput alone; that would optimize a different objective than the one stated for this project.

## Source table

| Source URL | What it supports | Evidence tier | Exact applicability |
|---|---|---:|---|
| `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/debug.c` | `set_rates`; `set_rate_override` syntax, VDEV scope, partial Wave-1 support, host-side state; debugfs controls | **1** | ath10k-CT current source; QCA988x where device path permits |
| `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/htt_tx.c` | QCA988x override TX path; HTT aggregation command; 1–64 A-MPDU and 1–31 A-MSDU limits; 64/3 defaults | **1** | QCA988x/ath10k-CT and common HTT implementation |
| `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/txrx.c` | `txrate2-CT` TX-completion/rate-report handling | **1** | CT firmware/driver, especially Wave-1 status semantics |
| `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/core.h` | `ratemask-CT`, `cust-stats-CT`, `retry-gt2-CT`, peer-fixed-rate capability definitions | **1** | ath10k-CT protocol definitions |
| `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k/wmi.h` | `wmi_peer_fixed_rate_cmd` | **1** | CT WMI protocol |
| `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/Kconfig` | `ATH10K_SPECTRAL` dependencies: debugfs + relay | **1** | ath10k-CT current driver |
| `https://github.com/greearb/ath10k-ct/blob/fcbdb70debc261f9df6734bbb76d81cdc88e0e26/ath10k-7.2/spectral.c` | FFT parser, relay output, 64/128/256 handling, 80/64 rejection, 20/22–40/44–80/88 ambiguity, FFT metadata | **1** | ath10k-CT spectral path |
| `https://github.com/greearb/ath10k-ct/commit/fcbdb70debc261f9df6734bbb76d81cdc88e0e26` | July 31, 2026 driver maintenance/upstream stable synchronization | **1** | ath10k-CT driver |
| `https://github.com/greearb/ath10k-ct` | Public CT host-driver project; distinguishes host source from radio-firmware source | **1** | ath10k-CT |
| `https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/kernel/ath10k-ct/Makefile` | OpenWrt 24.10 CT snapshot date/commit/6.10 tree; CT spectral build propagation | **1** | your OpenWrt release family |
| `https://github.com/openwrt/openwrt/blob/main/package/kernel/ath10k-ct/Makefile` | Current OpenWrt main CT snapshot dated 2026-07-31; 7.2 tree; spectral wiring | **1** | current OpenWrt development |
| `https://github.com/openwrt/openwrt/blob/openwrt-24.10/package/kernel/mac80211/ath.mk` | `PACKAGE_ATH_SPECTRAL`, Atheros debug dependency, `KERNEL_RELAY`, `ATH10K_SPECTRAL` | **1** | OpenWrt 24.10 build system |
| `https://github.com/openwrt/openwrt/blob/main/package/kernel/mac80211/ath.mk` | Current equivalent spectral configuration | **1** | current OpenWrt |
| `https://github.com/openwrt/openwrt/blob/main/package/firmware/ath10k-ct-firmware/Makefile` | Current CT firmware package version/date and fixed QCA988x download/hash | **1** | OpenWrt CT radio-firmware packaging |
| `https://github.com/torvalds/linux/commit/3ace10f5b5ad94bdbd4b419dc9da2217d57720a9` | AQL design motivation and mechanism | **1** | mac80211 generally; conceptually relevant to ath10k |
| `https://www.candelatech.com/downloads/ath10k-fw-beta/release_notes.txt` | Release 23 scan-crash attempt; Release 22 changes; retry semantics; peer fixed rate; rate masks; rate-control history | **2** | CT 10.1 Wave-1 firmware |
| `https://www.candelatech.com/ath10k-10.1.php` | CT Wave-1/10.1 firmware lineage and release context | **2** | QCA988x-class CT firmware |
| `https://www.candelatech.com/ath10k-ug.php` | CT user-facing rate control, fixed-rate/debug facilities, power/CFR feature scope | **2** | ath10k-CT; chip limitations explicitly matter |
| `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/spectral.html` | Official ath10k spectral usage, FFT bin options, 80/64 issue, count issue, relay TLV, FFT_eval | **2** | upstream ath10k spectral interface |
| `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k.html` | Official ath10k/QCA988x device support context | **2** | upstream ath10k/QCA988x |
| `https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath9k/spectral_scan.html` | Contrast with ath9k's explicit FFT timing controls and calibrated-power discussion | **2** | **ath9k only; not transferred to QCA988x** |
| `https://github.com/openwrt/openwrt/releases` | OpenWrt 25.12 kernel/mac80211 versions and 24.10 EOL schedule | **2** | OpenWrt |
| `https://arxiv.org/abs/2203.10390` | SRT-WiFi real SDR testbed and deterministic-Wi-Fi architecture context | **3** | SDR/different hardware |
| `https://lkml.iu.edu/2609.1/01477.html` | 2026 real-hardware ath11k AQL/queue-control measurements | **4** | **IPQ8074/ath11k only; not QCA988x** |
| `https://github.com/openwrt/openwrt/issues/21243` | Corroborating 2025 report of QCA988x `__fW-023-23ea9f8e` | **4** | QCA988x report; not authoritative vendor metadata |
| `https://github.com/open-sdr/openwifi` | Open programmable FPGA/SDR 802.11 implementation | **1** for project/source existence | **different hardware; architectural comparison only** |

**Bottom line:** the next three engineering moves with the highest evidence-to-effort ratio are **enable spectral in the existing CT build, characterize `htt_max_amsdu_ampdu`, and experimentally determine the actuation/scoping behavior of `ratemask-CT` and peer-fixed-rate**. The evidence does **not** support spending the next cycle trying to recreate airMAX's polling MAC from host-side `set_rate_override`; the existing stack gives you much better near-term leverage in queue placement, aggregation depth, rate-envelope supervision and interference telemetry.
