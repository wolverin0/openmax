# QCA988x control boundary — what the host can actually do

Summary: source-verified answers to the three questions that gate every FuturaMAX candidate
technique — who owns rate control, whether mac80211 airtime fairness works, and whether the
host can control A-MPDU aggregation — on QCA988x with firmware 10.2.4.
Keywords: ath10k, HAS_RATE_CONTROL, WMI_SERVICE_REPORT_AIRTIME, peer stats, last_tx_bitrate,
htt_max_amsdu_ampdu, HTT AGGR_CFG, airtime estimation, 6 Mbps fallback, ath10k-ct.
Read when: judging whether any host-side technique is implementable on target hardware.
Current verdict: rate control is firmware-owned (CONFIRMED); airtime fairness runs but on
ESTIMATED airtime that degenerates without peer stats (CONFIRMED); a coarse aggregation
setter exists (CONFIRMED in code, UNVERIFIED on hardware). Status: CURRENT 2026-08-08.

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
| Spectral FFT | hardware → ath10k | debugfs, documented defects | B |
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

## Open, and needing hardware

1. Does QCA988x 10.2.4 honour `HTT AGGR_CFG`, and at what granularity?
2. Are peer stats populated on this firmware, and is `last_tx_bitrate` non-zero per station?
3. How far does estimated airtime diverge from monitor-captured airtime across the rate spread?
4. Does the OpenWrt-shipped **ath10k-ct** driver carry the airtime path at all? Its `ath10k/`
   tree showed no `register_airtime` / AQL references while mainline does. If CT lags
   mainline here, the standard "use ath10k-ct on QCA988x" advice may **cost** the airtime
   scheduler. Verify per shipped OpenWrt version before recommending CT. **Open.**
