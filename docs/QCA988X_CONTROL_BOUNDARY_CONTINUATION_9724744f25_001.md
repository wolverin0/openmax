<!-- doc-head: QCA988X_CONTROL_BOUNDARY.md continuation 1 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](QCA988X_CONTROL_BOUNDARY.md) | Part 1/3
<a id="2c-so-the-host-estimates--and-the-estimate-has-a-cliff"></a> [2c. So the host estimates — and the estimate has a cliff](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_002.md#2c-so-the-host-estimates--and-the-estimate-has-a-cliff) | <a id="2d-what-this-actually-means-for-futuramax"></a> [2d. What this actually means for FuturaMAX](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_002.md#2d-what-this-actually-means-for-futuramax) | <a id="3-aggregation-a-coarse-host-control-exists-confirmed-in-code-settles-c03"></a> [3. Aggregation: a coarse host control exists. CONFIRMED in code. (settles C03)](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_002.md#3-aggregation-a-coarse-host-control-exists-confirmed-in-code-settles-c03) | <a id="consolidated-boundary-table"></a> [Consolidated boundary table](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_002.md#consolidated-boundary-table) | <a id="what-changed-versus-wave-1"></a> [What changed versus wave 1](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_002.md#what-changed-versus-wave-1) | <a id="4-wave-2-2026-09-20--the-ct-debugfs-controls-read-from-source"></a> [4. Wave 2 (2026-09-20) — the CT debugfs controls, read from source](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_002.md#4-wave-2-2026-09-20--the-ct-debugfs-controls-read-from-source) | <a id="4a-spectral-is-a-build-option-we-did-not-enable--confirmed"></a> [4a. Spectral is a BUILD option we did not enable — CONFIRMED](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_002.md#4a-spectral-is-a-build-option-we-did-not-enable--confirmed) | <a id="4b-set_rates-is-the-wrong-knob--confirmed"></a> [4b. `set_rates` is the wrong knob — CONFIRMED](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_003.md#4b-set_rates-is-the-wrong-knob--confirmed) | <a id="4c-set_rate_override-is-wave-2-territory--confirmed"></a> [4c. `set_rate_override` is Wave-2 territory — CONFIRMED](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_003.md#4c-set_rate_override-is-wave-2-territory--confirmed) | <a id="4d-ratemask-ct-is-the-real-supervisory-hook--confirmed-with-a-gap"></a> [4d. `ratemask-CT` is the real supervisory hook — CONFIRMED, with a gap](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_003.md#4d-ratemask-ct-is-the-real-supervisory-hook--confirmed-with-a-gap) | <a id="4e-unexplained-about-our-specific-unit"></a> [4e. Unexplained, about our specific unit](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_003.md#4e-unexplained-about-our-specific-unit) | <a id="open-and-needing-hardware"></a> [Open, and needing hardware](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_003.md#open-and-needing-hardware)

<!-- stage822a-payload-begin -->

Exact AR9888 descriptors document capture and rich metadata, not working CSI export.
Normal host API limitations do not prove universal physical impossibility.
The public UTF selection is an incomplete build graph, not an accepted target image.
Historical source/firmware findings below retain their original narrower scope.
No new hardware or target execution; operational capture remains UNKNOWN.


## 2026-10-24 current source-bound correction

**CONFIRMED descriptor contract:** exact AR9888/v2 headers document
`bb_capture_channel`, `bb_captured_channel`, `txbf_h_info`, EVM and timestamps.
`bb_length` describes conditioned baseband-debug length; it is not established as
the channel/H-dump length. **UNKNOWN:** activation, memory format, calibrated CSI
and exact installed-firmware export. See the [audited synthesis](../knowledge/QCA988X_PHYSICAL_BOUNDARY_2026.md) and its
pinned manifest/ranges for both requested commits.

**REFUTED as a universal inference:** absence of a normal ath10k CSI/scheduler API
proves that CSI or polling is impossible in silicon. Historical “CSI is REFUTED,”
“can never report actual airtime,” or “replacement rate control is dead” wording
must be read within the examined normal host/firmware interface, not as a statement
about every target implementation. The exact descriptor path and retained Ubiquiti
target-image research justify investigation, not an accepted open replacement.
Shared ADC/waveform ABIs do not prove exact-target handlers or arbitrary IQ.
No hardware was contacted; E2 and all physical/recovery gates remain unchanged.

The historical text below is retained byte-for-byte as dated evidence. This
correction supersedes its universal present-tense interpretations only.

---

# QCA988x control boundary — what the host can actually do


Stock WA8/XC8 and four-generation PtMP confirmed by run17/run25/run8.
Original dated benchmarks/static findings keep their hardware and firmware scope.
No new performance, TDMA/GPS, relay, production or E2 acceptance follows.
Current authoritative state and source receipts are linked below.


## October22 evidence alignment - current bench scope

The accepted exact-device receipts supersede any universal present-tense reading
of older incompatibility or topology statements below: run17 establishes stock
WA.v8.7.25 Loco195 bidirectional association with the held LAP-120 OpenWrt AP;
run25 adds stock XC.v8.7.25 Rocket198 concurrently (61.031s authorization,
64/64 radio-qualified pings each); FMX-0016 run8 adds SXT OpenWrt/ath9k and
stock airOS6 M5 concurrently (60.5s,64/64 each,256 matched radio echo pairs).
All modified state was restored and the AP radio disabled. These are exact
bench compatibility results; they do not establish capacity, performance gain,
TDMA/GPS, all-revision support, physical relay or production acceptance.

Sources: [current state](CURRENT_STATE.md),
[run8 receipt](../artifacts/canary_panel1_guarida/root_four_cpe_result_20261022.json),
[Oct22 scoped evidence alignment](../artifacts/canary_panel1_guarida/fmx_docs_alignment_20261022.json).
Existing E2 remains `NOT_ACCEPTED` with its original gates. Original dated
measurements, failures, static control limits and firmware scopes remain
historical evidence, not permission to resume those recipes.
Control boundary: AP/Linux/hostapd RAM admission plus native stock CPE association. No QCA-firmware per-frame scheduler, new PHY or proprietary airMAX TDMA capability is established.



## Current physical evidence - D2 refresh October10

Exact LAP-120/Nano kernel6.6.110/CT022 module/config fingerprints recorded.
Two bounded reciprocal20-ping treatments delivered20/20 each; AP station
TX-duration increased12250/30296us and Nano12035/35658us. Firmware peer
TX/RX rates were populated. This supersedes a universal current reading of
October5's zero-field observation below, not that historical measurement.
Firmware peer RX-duration was772/86320 in one snapshot, then0 before/after
the reciprocal traffic. Its unit/reset/report semantics are UNKNOWN; do not
subtract arbitrary snapshots as calibrated airtime. Station TX-duration may
be a host estimate; internal last_tx_bitrate/source provenance and monitor
comparison remain missing. KEEP observed field visibility, not actual-airtime,
fairness, AQL or throughput improvement. No RF/queue/rate/firmware mutation.
Independent source/evidence review PASS_WITH_LIMITS, raw hashes freshly
checked. Module hashes differ between AP and Nano; host RX-duration is0 in
all snapshots. Negotiated AP TX width/rate changed in one pair; configured
power/width is inherited, not a new D2 measurement. Extra CPE RX traffic has
no proven source. These observations are not calibrated-airtime acceptance.
Evidence: research/raw/d2-peer-visibility-20261010.json in the owned night worktree.

Summary: source-verified answers to what the host can actually control on QCA988x under
ath10k-CT — rate control, airtime fairness, A-MPDU aggregation, spectral, and the CT debugfs knobs.
Keywords: ath10k-ct, HAS_RATE_CONTROL, airtime estimation, htt_max_amsdu_ampdu, spectral,
PACKAGE_ATH_SPECTRAL, set_rates, set_rate_override, ratemask-CT, Wave 1 vs Wave 2, peer stats.
Read when: judging whether any host-side technique is implementable on target hardware.
Current verdict: rate control is firmware-owned; airtime fairness runs on ESTIMATED airtime; a
coarse aggregation setter exists (unverified on HW); spectral is a build option we never enabled; set_rates is bcast/mcast only; set_rate_override is Wave-2; ratemask-CT is the real hook (§4). Status: CURRENT 2026-09-20.

> **SCOPE WARNING (added 2026-08-08).** This file describes the control boundary **under
> ath10k / OpenWrt**. It is not the boundary under stock airOS, which is materially wider —
> aggregation length, rate-control mode, Dynamic ACK, distance and per-AC EDCA are all
> exposed there. Read `knowledge/AIROS_CONTROL_SURFACE.md` before concluding that anything
> here is "blocked on the hardware". Several items below are blocked only on *this driver*.

## Method and evidence grade

Read directly from source, not from search results:

- mainline Linux `master`, fetched 2026-08-08 — `drivers/net/wireless/ath/ath10k/{mac.c,htt_rx.c,core.h,wmi.h}`, `net/mac80211/tx.c`, `include/net/mac80211.h`
- `github.com/greearb/ath10k-ct` @ HEAD, shallow clone 2026-08-08
- target firmware version taken from the NanoStation AC boot log: **`10.2.4-1.0-00037` api 5** (see `knowledge/HARDWARE_MATRIX.md`)

Grade **A** for "this is what the code does". Grade **B→UNVERIFIED** for "and the QCA988x
firmware honours it", which only hardware can settle. Each finding below says which it is.

---

## 1. Rate control is owned by firmware. CONFIRMED. (settles C02)

```c
/* drivers/net/wireless/ath/ath10k/mac.c:10079 (mainline) */
ieee80211_hw_set(ar->hw, HAS_RATE_CONTROL);
```

`HAS_RATE_CONTROL` tells mac80211 the device does its own rate selection, so mac80211 does
**not** attach a rate-control algorithm. There is no `rate_control_ops` and no reference to
minstrel anywhere in ath10k. `WMI_SERVICE_RATECTRL` exists in the WMI service bitmap for
every firmware generation (`wmi.h:109`).

**Minstrel-HT does not run on ath10k.** The mistral run's Tier-1 top recommendation
("Minstrel-HT tuning") is not implementable on this hardware. NeuRA / EDRA / IteRate, which
all replace or extend the mac80211 rate-control algorithm, have **no attachment point**.

What remains available to the host is *constraint*, not control:
`ath10k_mac_op_set_bitrate_mask` narrows the set of rates firmware may choose. ath10k-ct
adds `ratemask-CT` and `txrate-CT` firmware features (`ath10k-ct/ath10k/core.c:312,315`) —
the same feature strings that appear in the Ubiquiti QCA988x OpenWrt boot log, which
independently confirms CT firmware exposing them on this hardware family.

> **Design consequence.** Supervisory rate policy — excluding chronically bad MCS/NSS for a
> stationary CPE and letting firmware do microsecond retry — is the only viable rate-control
> shape. Any plan that "replaces the rate controller" is dead on QCA988x.

---

## 2. Airtime fairness runs on ath10k — but on an estimate that can degenerate. (settles C01)

This is the finding none of the seven external reports reached, and the split between them
was temporal, not factual.

### 2a. The 2017 statement is superseded

"Ending the Anomaly" (ATC'17) said ath10k lacked the required scheduling hooks. That was
true in 2017. Mainline ath10k now implements `wake_tx_queue` (`mac.c:8217` in ath10k-ct,
present in mainline) and feeds mac80211's TXQ scheduler. Four of the seven runs are quoting
a nine-year-old limitation as current; the grok run's "works on ath10k" is closer to today's
truth. **Neither is the useful answer.**

### 2b. QCA988x can never report *actual* airtime

<!-- stage822a-payload-end -->
