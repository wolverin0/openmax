<!-- doc-head: QCA988X_CONTROL_BOUNDARY.md continuation 3 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](QCA988X_CONTROL_BOUNDARY.md) | Part 3/3
<a id="2026-10-24-current-source-bound-correction"></a> [2026-10-24 current source-bound correction](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#2026-10-24-current-source-bound-correction) | <a id="qca988x-control-boundary--what-the-host-can-actually-do"></a> [QCA988x control boundary — what the host can actually do](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#qca988x-control-boundary--what-the-host-can-actually-do) | <a id="october22-evidence-alignment---current-bench-scope"></a> [October22 evidence alignment - current bench scope](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#october22-evidence-alignment---current-bench-scope) | <a id="current-physical-evidence---d2-refresh-october10"></a> [Current physical evidence - D2 refresh October10](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#current-physical-evidence---d2-refresh-october10) | <a id="method-and-evidence-grade"></a> [Method and evidence grade](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#method-and-evidence-grade) | <a id="1-rate-control-is-owned-by-firmware-confirmed-settles-c02"></a> [1. Rate control is owned by firmware. CONFIRMED. (settles C02)](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#1-rate-control-is-owned-by-firmware-confirmed-settles-c02) | <a id="2-airtime-fairness-runs-on-ath10k--but-on-an-estimate-that-can-degenerate-settles-c01"></a> [2. Airtime fairness runs on ath10k — but on an estimate that can degenerate. (settles C01)](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#2-airtime-fairness-runs-on-ath10k--but-on-an-estimate-that-can-degenerate-settles-c01) | <a id="2a-the-2017-statement-is-superseded"></a> [2a. The 2017 statement is superseded](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#2a-the-2017-statement-is-superseded) | <a id="2b-qca988x-can-never-report-actual-airtime"></a> [2b. QCA988x can never report *actual* airtime](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#2b-qca988x-can-never-report-actual-airtime) | <a id="2c-so-the-host-estimates--and-the-estimate-has-a-cliff"></a> [2c. So the host estimates — and the estimate has a cliff](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_002.md#2c-so-the-host-estimates--and-the-estimate-has-a-cliff) | <a id="2d-what-this-actually-means-for-futuramax"></a> [2d. What this actually means for FuturaMAX](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_002.md#2d-what-this-actually-means-for-futuramax) | <a id="3-aggregation-a-coarse-host-control-exists-confirmed-in-code-settles-c03"></a> [3. Aggregation: a coarse host control exists. CONFIRMED in code. (settles C03)](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_002.md#3-aggregation-a-coarse-host-control-exists-confirmed-in-code-settles-c03) | <a id="consolidated-boundary-table"></a> [Consolidated boundary table](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_002.md#consolidated-boundary-table) | <a id="what-changed-versus-wave-1"></a> [What changed versus wave 1](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_002.md#what-changed-versus-wave-1) | <a id="4-wave-2-2026-09-20--the-ct-debugfs-controls-read-from-source"></a> [4. Wave 2 (2026-09-20) — the CT debugfs controls, read from source](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_002.md#4-wave-2-2026-09-20--the-ct-debugfs-controls-read-from-source) | <a id="4a-spectral-is-a-build-option-we-did-not-enable--confirmed"></a> [4a. Spectral is a BUILD option we did not enable — CONFIRMED](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_002.md#4a-spectral-is-a-build-option-we-did-not-enable--confirmed)

<!-- stage822a-payload-begin -->
ath10k". **That inference was wrong in its cause.** The wiring is:

- `package/kernel/mac80211/ath.mk:46` —
  `config-$(CONFIG_PACKAGE_ATH_SPECTRAL) += ATH9K_COMMON_SPECTRAL ATH10K_SPECTRAL ATH11K_SPECTRAL`
- `ath.mk:111-114` — `config PACKAGE_ATH_SPECTRAL` · `depends on PACKAGE_ATH_DEBUG` ·
  `select KERNEL_RELAY`
- `package/kernel/ath10k-ct/Makefile:91-93` —
  `ifdef CONFIG_PACKAGE_ATH_SPECTRAL` → `CT_MAKEDEFS += CONFIG_ATH10K_SPECTRAL=y`

ath10k-CT itself ships the spectral WMI/relay implementation (`ath10k-7.2/spectral.c`). So the
missing entries mean **our stock image was built without `PACKAGE_ATH_SPECTRAL`** — not that
QCA988x or ath10k-CT cannot do FFT. **Switching to upstream ath10k is not required.**

### 4b. `set_rates` is the wrong knob — CONFIRMED

`ath10k-7.2/debug.c:1441` states it in the help text itself:
*"This is to set fixed bcast, mcast, and beacon rates. Normal rate-ctrl …"*
It is a VDEV-wide management/broadcast/multicast rate setter over WMI. Any plan that used
`set_rates` as the supervisory **unicast** data-rate hook is void.

### 4c. `set_rate_override` is Wave-2 territory — CONFIRMED

`ath10k-7.2/debug.c:1635`: *"Only wave-2 CT firmware has full support. Wave-1 CT firmware has
at least …"*. Our QCA988x is **Wave 1**. The parser accepts `tpc=`, `sgi=`, `mcs=`, `nss=`,
`pream=`, `retries=`, `dynbw=`, `bw=` — **acceptance is not execution**. Do not treat a
successful write as evidence the field took effect; that is precisely the class of error that
cost this project a night on the flash verification.

### 4d. `ratemask-CT` is the real supervisory hook — CONFIRMED, with a gap

`ath10k/core.h:648` — `ATH10K_FW_FEATURE_CT_RATEMASK = 33`. It extends the **peer-association**
WMI message with rate-disable masks, so the host constrains *which* rates firmware may pick while
the firmware algorithm keeps running underneath. That is exactly the outer-loop architecture
AGENTS.md §9 wants.

**The gap (UNKNOWN):** no documented, low-latency **per-peer runtime** userspace API was found —
the feature lives at peer-assoc time, and `iw ... set bitrates` is not documented by CT as a
per-peer scheduler interface. Whether a mask can be updated per-station, live, at useful rates is
now an experiment, not an assumption.

### 4e. Unexplained, about our specific unit

**4e — MEASURED 2026-10-05 on the live FuturaMAX link (LAP-120 AP, CT FW022, ath10k-ct 2024.07.30):** peer stats are NOT populated (Peer RSSI 0, RX duration 0, TX rate 0/6000) and mac80211 station airtime is 0 us RX / 0 us TX. The airtime-fairness scheduler therefore has no input on this stack until airtime reporting is enabled (open: CT feature flag / `enable_extd_tx_stats` / htt-mgt variant). Evidence: `research/raw/bench/2026-10-05/ct-debugfs-220848.txt`.


Our firmware `10.1-ct-8x-__fW-022` does **not** advertise peer-fixed-rate, although CT release
notes say the feature was enabled. Cause UNKNOWN. Worth resolving before designing around it.

## Open, and needing hardware

1. Does QCA988x 10.2.4 honour `HTT AGGR_CFG`, and at what granularity?
2. Are peer stats populated on this firmware, and is `last_tx_bitrate` non-zero per station?
3. How far does estimated airtime diverge from monitor-captured airtime across the rate spread?
4. Does the OpenWrt-shipped **ath10k-ct** driver carry the airtime path at all? Its `ath10k/`
   tree showed no `register_airtime` / AQL references while mainline does. If CT lags
   mainline here, the standard "use ath10k-ct on QCA988x" advice may **cost** the airtime
   scheduler. Verify per shipped OpenWrt version before recommending CT. **Open.**


Historical dated document summary (retained from prior header):

2026-10-17 (Stages 7-9): CONFIRMED on live 3-station bench (`LAP-120` QCA9882 AP, `10.1-ct-8x-__fW-022`): (1) `htt_max_amsdu_ampdu` (`1x8`, `1x16`, `2x32`, `3x64`), `aql_txq_limit`, `airtime_flags=3`, and per-station `airtime_weight` are honoured in real time by `mac80211`/`ath10k-ct`; (2) writing to `stations/<mac>/airtime` resets kernel airtime/deficit counters; (3) `spectral_scan0` emits Type-3 TLV FFT frames (`618.7 KB / 6,653 frames`), but `iw dev phy0-ap0 scan ... ap-force` on an AP vdev leaves `10.1-ct-8x-__fW-022` firmware in a persistent `102.4 ms` beacon-aligned scan sawtooth until module reload/reboot; (4) `FMX-0009` (`ATH10K_DBG_BUFFER` `0x2002`): `iw dev phy0-ap0 set bitrates ...` multi-rate masks send `WMI_PEER_ASSOC_CMDID` (`reassoc=true`) with updated rate bitmaps (`0x0F0F`, `0x000F`, `0xFFF0`), but `10.1-ct-8x-__fW-022` ignores `reassoc=true` rate-set narrowing on already-associated peers (`REFUTED` as live runtime fast-loop MCS clamp).
October10 exact-peer bytes/rates and station TX-duration counters are now visible.
Firmware RX-duration is inconsistent across snapshots; calibrated airtime remains UNKNOWN.
Older firmware/source and October5 observations remain scoped historical evidence.
<!-- stage822a-payload-end -->
