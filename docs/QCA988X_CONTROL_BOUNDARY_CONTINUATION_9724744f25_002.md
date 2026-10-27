<!-- doc-head: QCA988X_CONTROL_BOUNDARY.md continuation 2 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](QCA988X_CONTROL_BOUNDARY.md) | Part 2/3
<a id="2026-10-24-current-source-bound-correction"></a> [2026-10-24 current source-bound correction](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#2026-10-24-current-source-bound-correction) | <a id="qca988x-control-boundary--what-the-host-can-actually-do"></a> [QCA988x control boundary — what the host can actually do](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#qca988x-control-boundary--what-the-host-can-actually-do) | <a id="october22-evidence-alignment---current-bench-scope"></a> [October22 evidence alignment - current bench scope](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#october22-evidence-alignment---current-bench-scope) | <a id="current-physical-evidence---d2-refresh-october10"></a> [Current physical evidence - D2 refresh October10](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#current-physical-evidence---d2-refresh-october10) | <a id="method-and-evidence-grade"></a> [Method and evidence grade](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#method-and-evidence-grade) | <a id="1-rate-control-is-owned-by-firmware-confirmed-settles-c02"></a> [1. Rate control is owned by firmware. CONFIRMED. (settles C02)](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#1-rate-control-is-owned-by-firmware-confirmed-settles-c02) | <a id="2-airtime-fairness-runs-on-ath10k--but-on-an-estimate-that-can-degenerate-settles-c01"></a> [2. Airtime fairness runs on ath10k — but on an estimate that can degenerate. (settles C01)](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#2-airtime-fairness-runs-on-ath10k--but-on-an-estimate-that-can-degenerate-settles-c01) | <a id="2a-the-2017-statement-is-superseded"></a> [2a. The 2017 statement is superseded](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#2a-the-2017-statement-is-superseded) | <a id="2b-qca988x-can-never-report-actual-airtime"></a> [2b. QCA988x can never report *actual* airtime](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_001.md#2b-qca988x-can-never-report-actual-airtime) | <a id="4b-set_rates-is-the-wrong-knob--confirmed"></a> [4b. `set_rates` is the wrong knob — CONFIRMED](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_003.md#4b-set_rates-is-the-wrong-knob--confirmed) | <a id="4c-set_rate_override-is-wave-2-territory--confirmed"></a> [4c. `set_rate_override` is Wave-2 territory — CONFIRMED](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_003.md#4c-set_rate_override-is-wave-2-territory--confirmed) | <a id="4d-ratemask-ct-is-the-real-supervisory-hook--confirmed-with-a-gap"></a> [4d. `ratemask-CT` is the real supervisory hook — CONFIRMED, with a gap](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_003.md#4d-ratemask-ct-is-the-real-supervisory-hook--confirmed-with-a-gap) | <a id="4e-unexplained-about-our-specific-unit"></a> [4e. Unexplained, about our specific unit](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_003.md#4e-unexplained-about-our-specific-unit) | <a id="open-and-needing-hardware"></a> [Open, and needing hardware](QCA988X_CONTROL_BOUNDARY_CONTINUATION_9724744f25_003.md#open-and-needing-hardware)

<!-- stage822a-payload-begin -->
```c
/* wmi.h — REPORT_AIRTIME is mapped for the 10.4 generation ONLY */
SVCMAP(WMI_10_4_SERVICE_REPORT_AIRTIME, WMI_SERVICE_REPORT_AIRTIME, len);
WMI_10_4_REPORT_AIRTIME = BIT(18),   /* "Firmware supports transmit airtime reporting" */
```

There is **no such mapping for the 10.x / 10.2.4 generation**. 10.4 is Wave 2 —
QCA9984/QCA9888/QCA4019. Target hardware runs `10.2.4-1.0-00037`, so
`WMI_SERVICE_REPORT_AIRTIME` is never set and firmware-reported airtime is unavailable.
**Grade A, structural, not a bug.**

### 2c. So the host estimates — and the estimate has a cliff

```c
/* mac.c:4361 ath10k_mac_update_airtime()
 * "...This is just a rough estimation because host driver has no knowledge of the
 *  actual transmit rate, retries or aggregation." */
if (test_bit(WMI_SERVICE_REPORT_AIRTIME, ar->wmi.svc_map))
        return airtime;                       /* 10.4 only — never taken on QCA988x */

if (arsta->last_tx_bitrate) {
        airtime = (pktlen * 8 * 10) / arsta->last_tx_bitrate;
        airtime += IEEE80211_ATF_OVERHEAD_IFS;
} else {
        airtime = (pktlen * 8 * 10) / 60;     /* <-- assumes 6 Mbps for EVERY frame */
        airtime += IEEE80211_ATF_OVERHEAD;
}
```

`last_tx_bitrate` is written in exactly one place —
`ath10k_update_per_peer_tx_stats()` (`htt_rx.c:3879`) — reached only from the HTT peer-stats
path (`HTT_T2H_MSG_TYPE_PEER_STATS`), gated on:

```c
/* core.h:1330 */
ATH10K_FLAG_PEER_STATS  &&  WMI_SERVICE_PEER_STATS
```

**If peer stats are not enabled, `last_tx_bitrate` stays 0 and every station's airtime is
computed as though it transmitted at 6 Mbps.**

That is the cliff, and it matters more here than in any indoor Wi-Fi deployment. A WISP
sector's entire airtime-fairness problem *is* rate diversity — a near CPE at MCS9 next to a
far CPE at MCS1. A uniform 6 Mbps assumption erases exactly the signal the scheduler exists
to act on, silently converting airtime fairness into something close to packet fairness —
the anomaly it was built to fix.

Even with peer stats on, the estimate ignores **retries and aggregation** (the code comment
says so) and on 10.2.4 the peer-stats event arrives roughly once per four PPDUs.

### 2d. What this actually means for FuturaMAX

| | Status |
|---|---|
| mac80211 TXQ + AQL usable on QCA988x | **CONFIRMED** (code path exists) |
| Airtime fairness scheduler attachable | **CONFIRMED** |
| Driven by *actual* airtime | **REFUTED** — 10.4-only service |
| Driven by a *usable* estimate | **CONDITIONAL** on peer stats being enabled and populated |
| Estimate accounts for retries/aggregation | **No**, by the author's own comment |

> **This converts a research question into a cheap, decisive experiment.** On a QCA988x
> sector: enable peer stats, confirm `last_tx_bitrate` is non-zero for every station, then
> compare estimated airtime against an independent monitor capture across the rate spread.
> If the estimate tracks reality, airtime fairness is real here. If stations sit at the
> 6 Mbps fallback, every airtime-fairness gain in the literature is unavailable on this
> hardware and the project should pace from the qdisc layer instead. Nothing else in the
> wave-1 candidate list has this ratio of decision value to cost.

---

## 3. Aggregation: a coarse host control exists. CONFIRMED in code. (settles C03)

Wave 1 split four ways. The code answer sits between all of them.

**Device-wide max A-MPDU/A-MSDU setter exists in ath10k-ct:**

```c
/* ath10k-ct/ath10k/debug.c:1935 */
debugfs_create_file("htt_max_amsdu_ampdu", ...)
  -> sscanf(buf, "%u %u", &amsdu, &ampdu)
  -> ath10k_htt_h2t_aggr_cfg_msg(&ar->htt, ampdu, amsdu);
```

A writable debugfs file issuing an HTT host-to-target **aggregation config** message. The
glm run's "no debugfs aggregation control found" is **wrong**.

**Per-TID aggregation enable/disable exists in mainline** via the nl80211 TID-config API
(`NL80211_TID_CONFIG_ATTR_AMPDU_CTRL` → `arg.aggr_control`, `mac.c:7123/7160`).

But note what these are *not*:

- `htt_max_amsdu_ampdu` is **per-device**, not per-peer — one setting for the whole sector.
- The TID control is **on/off**, not a length.
- Neither exposes **Block-ACK outcomes per aggregate**. Peer stats give aggregated
  `succ_pkts` / `failed_pkts` / `retry_pkts`, not BA bitmaps.

PNOFA needs per-link, per-moment A-MPDU length adaptation driven by Block-ACK delivery
ratios. **The length knob is coarser than PNOFA requires and the feedback channel is
aggregated rather than per-aggregate.** So:

- google's "CONFIRMED, direct hooks, 15–30% gain" — **overclaims**; the knob is device-wide.
- glm's "no control exists" — **wrong**; it exists.
- chatgpt's UNKNOWN — **appropriately cautious, now partially answered.**
- A PNOFA port is **not** blocked outright, but it must be redesigned around a device-wide
  knob and sampled feedback, and its published effect size cannot be assumed to carry.

**UNVERIFIED and only hardware can settle it:** whether QCA988x 10.2.4 firmware actually
honours `HTT AGGR_CFG`, and what its real granularity is.

---

## Consolidated boundary table

| Capability | Owner | Host access on QCA988x | Grade |
|---|---|---|---|
| Rate selection | **QCA firmware** | constrain only (bitrate mask, CT ratemask) | A |
| Retry chain | **QCA firmware** | none | A |
| Per-frame TX rate in completion | **QCA firmware** | absent; sampled peer stats only | A |
| Actual TX airtime | **QCA firmware** | **unavailable — 10.4 only** | A |
| Estimated airtime | ath10k | yes, from `last_tx_bitrate` (peer stats) | A |
| mac80211 TXQ / AQL | mac80211 | yes | A |
| Airtime-fairness scheduling | mac80211 | yes, quality bounded by §2c | A |
| Max A-MPDU/A-MSDU (device-wide) | ath10k-ct → HTT | `htt_max_amsdu_ampdu` debugfs | A (code) / UNVERIFIED (fw) |
| Per-TID aggregation on/off | mainline ath10k | nl80211 TID config | A (code) |
| Per-peer A-MPDU length | — | **not exposed** | A |
| Block-ACK bitmaps per aggregate | **QCA firmware** | not exposed | A |
| Spectral FFT | hardware → ath10k-CT | **build-time option**; absent from our image, not from the silicon | A (see §4) |
| `set_rates` (bcast/mcast/beacon rate) | ath10k-CT → WMI | VDEV-wide; **NOT the unicast data-rate control** | A (see §4) |
| `set_rate_override` | ath10k-CT → HTT desc | **Wave-2 only for full support**; partial on our Wave-1 | A (see §4) |
| `ratemask-CT` (rate-disable mask) | ath10k-CT → peer-assoc WMI | exists at WMI layer; **no documented per-peer runtime API** | A / UNKNOWN (see §4) |
| Coverage class / ACK timing | hardware registers | fragile register workaround | B |
| FQ-CoDel / CAKE / pacing | Linux qdisc | full | A |
| TDMA slot ownership | **QCA firmware** | none | A |

## What changed versus wave 1

| Wave-1 position | Source verdict |
|---|---|
| "Minstrel-HT is the rate controller on ath10k" (mistral, CONFIRMED) | **Refuted** — `HAS_RATE_CONTROL` |
| "ath10k lacks airtime scheduler hooks" (chatgpt, glm, google) | **Superseded** — hooks exist now |
| "AQL + airtime fairness works on ath10k" (grok, CONFIRMED) | **True but incomplete** — runs on an estimate with a 6 Mbps cliff |
| "No aggregation control on ath10k" (glm) | **Refuted** — `htt_max_amsdu_ampdu` |
| "Direct A-MPDU hooks, CONFIRMED 15–30%" (google) | **Overclaimed** — device-wide, effect size unsupported |
| "A-MPDU control UNKNOWN" (chatgpt) | **Partially answered** |

## 4. Wave 2 (2026-09-20) — the CT debugfs controls, read from source

Source: ChatGPT deep-research wave registered as `chatgpt-d3f52524` in
`research/intake/manifest.yaml`. **Every claim below was re-verified by me against the cited
file on `raw.githubusercontent.com`, not taken from the report.** Commit pin for all ath10k-CT
references: `fcbdb70debc261f9df6734bbb76d81cdc88e0e26`.

### 4a. Spectral is a BUILD option we did not enable — CONFIRMED

Last session concluded "no `spectral_scan*` in debugfs ⇒ FMX-0010 blocked, maybe needs upstream
<!-- stage822a-payload-end -->
