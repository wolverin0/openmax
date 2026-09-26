# FuturaMAX — standing research prompt for ChatGPT / deep research

Summary: copy-paste prompt that keeps FuturaMAX current on QCA988x/ath10k, OpenWrt/mac80211 queueing,
TDMA-on-COTS-WiFi, real-hardware literature, and autonomous radio research. Keywords: research
prompt, ath10k-CT, QCA988x, AQL, rate mask, ratemask-CT, spectral, TDMA, PtMP, IteRate, autoresearch,
Tier 1.5 real-hardware papers, deep research, citation rules.
Read when: starting a research wave, or before pasting anything into an external model. Rules:
paste the PROMPT block verbatim; refresh BASELINE and the "already in hand" list whenever the lab
stack or knowledge/REAL_HARDWARE_LITERATURE.md changes; every claim needs a resolvable primary URL or UNKNOWN. Status: CURRENT (2026-09-20).

---

## How to use this

1. Paste everything inside the `=== PROMPT ===` fence into ChatGPT (deep research mode preferred).
2. Before pasting, re-check **BASELINE** against `docs/CURRENT_STATE.md` — a stale baseline makes the
   model research hardware we do not have. This is the highest-value edit to this file.
3. Save the returned report into `research/raw/<provider>/<date>/` and register it before citing it.
4. **Do not promote anything from the report into `docs/` without checking the primary source yourself.**

### Why the guardrails exist (real failures from earlier waves)

- A cited paper on rate adaptation **resolved to an article about active galactic nuclei**.
- One run asserted the target SoC was QCA9563 @ 750 MHz. It is not.
- OpenWrt-vs-airMAX performance figures were graded **CONFIRMED against "Reddit reports"**.
- **All six research runs described the wrong software stack** — they analysed ath10k when stock airOS
  actually runs the QCA vendor `ol_ath`/`umac` offload driver plus proprietary Ubiquiti modules.

Cross-model agreement is *not* evidence: of 535 sources across six runs, only 51 were cited by more
than one run. Treat consensus between models as correlated error, not corroboration.

---

=== PROMPT ===

You are a research analyst for an embedded-wireless engineering project. Produce a rigorous,
source-anchored briefing. Prefer depth and verifiability over breadth. Do not pad.

## Project

We build **custom firmware/software for Ubiquiti airMAX AC hardware** for **stationary outdoor
point-to-multipoint (PtMP) fixed-wireless** links, where we control both ends and know distances,
topology and per-subscriber history. We are NOT trying to add Wi-Fi 6/7 PHY features the silicon
lacks, and we are NOT tuning the vendor configuration file. The deliverable is our own stack.

Our objective is to beat the vendor's frozen 2017-era scheduler on **loaded latency (p95/p99),
fairness, airtime efficiency, goodput/MHz and spectrum intelligence** — not necessarily on peak
speedtest throughput.

## BASELINE — the exact system we run (do not research other hardware)

- **Radio SoC:** Qualcomm Atheros **QCA988x hw2.0 "Wave 1"** (PCI 0777:e8e5), 2x2:2, 5 GHz only.
- **Host SoC:** Atheros **AR9342** @535 MHz, 64 MB RAM, 16 MB NOR flash (some units QCA955x @720 MHz).
- **Now running:** **OpenWrt 24.10.4** (r28959), target **ath79/generic**, **Linux 6.6.110**.
- **Driver:** **ath10k-CT** (Candela Tech), `kmod-ath10k-ct-smallbuffers`.
- **Radio firmware:** `10.1-ct-8x-__fW-022-ecad3248`, advertising: `wmi-10.x`, `has-wmi-mgmt-tx`,
  `mfp`, `txstatus-noack`, `ratemask-CT`, `txrate-CT`, `txrate2-CT`, `tx-rc-CT`, `get-temp-CT`,
  `cust-stats-CT`, `retry-gt2-CT`, `beacon-cb-CT`, `wmi-block-ack-CT`. `max-sta 128`, `raw 0`,
  htt-ver 2.1, 16 vdevs / 127 peers / 256 tids.
- **ath10k debugfs surface present:** `set_rates`, `set_rate_override`, `htt_max_amsdu_ampdu`,
  `peer_stats`, `peers`, `pktlog_filter`, `enable_extd_tx_stats`, `fw_stats`, `pdev_ext_stats`,
  `sta_tid_stats_mask`, `rx_reorder_stats`, `tpc_stats`, `ratepwr_table`, `powerctl_table`,
  `ct_special`, `quiet_period`, `ani_enable`, `nf_cal_period`, `cal_data`.
- **Absent in this build:** any `spectral_scan*` entry (no spectral FFT exposed).
- **Vendor stack for comparison:** airOS runs Linux **2.6.32** with the QCA vendor `ol_ath`/`umac.ko`
  offload driver (NOT ath10k) plus proprietary `ubnthal` and `ubnt_poll_host` modules, and **custom
  QCA988x radio firmware containing a polling MAC** (`ubnt-poll` symbols) absent from stock QCA
  firmware. That radio firmware has been byte-identical since ~2017.

## What we already know — do NOT spend effort re-deriving these

- ath10k offloads rate control to firmware; there is no host minstrel for QCA988x.
- The kernel jump (2.6.32 → 6.6) is the project's largest lever: AQL, airtime fairness, per-station
  TXQ, FQ-CoDel/CAKE did not exist in the vendor's kernel.
- Ubiquiti's TDMA/polling lives partly inside the radio firmware, so it cannot be replicated by
  configuration on stock firmware.
- OpenWrt has official device profiles for our hardware and boots on it.
- (2026-09-20) Spectral is a build option (`PACKAGE_ATH_SPECTRAL` → `ATH10K_SPECTRAL`, selects
  `KERNEL_RELAY`), not a hardware limit. `set_rates` sets bcast/mcast/beacon rates only.
  `set_rate_override` has full support only on Wave-2 firmware. `ratemask-CT`
  (`ATH10K_FW_FEATURE_CT_RATEMASK`) extends peer-association with rate-disable masks.
- (2026-09-20) **Real-hardware literature already in hand — do NOT re-find, but DO report anything
  newer or contradicting:** IteRate (arXiv:2605.02542, autonomous eBPF RC loop, 58 mt76 nodes);
  WiFiSpectralJam (arXiv:2608.15728, 522M QCA9880 spectral observations); RF Jamming Dataset (IEEE
  ComMag 2024, QCA9880, >90% detection); ORCA/RateMan (MobiCom 2024); WiFi-CUTS (IEEE Xplore
  11224946, bandit RA, +7/15/37% vs Minstrel-HT); PNOFA (Comput. Commun. 2021, IPQ4019 outer-loop
  aggregation, +17% UDP/+13% TCP); Quick & Plenty (2021); Ending the Anomaly (ATC '17); hMAC
  (ath9k soft slotting); SmartLA (Comput. Commun. 2017); SRT-WiFi (arXiv:2203.10390).

## Our method, so you can target it

Stage 3 is an **autonomous radio-research loop** (Karpathy-Autoresearch discipline, IteRate-style
closed loop, ORCA-style off-radio intelligence): immutable bench + evaluator, one bounded mutable
policy, blocked A/B/A/B repetitions, hard validity gates, lexicographic objective (p99 → p95 →
fairness → goodput/MHz → retry airtime → aggregate). The controller works *around* firmware rate
control — allowed rate sets, queueing, pacing, aggregation, airtime allocation, spectral/channel
policy — not by replacing it. Findings that improve any of these components are the most valuable.

## RESEARCH QUESTIONS — ranked. Answer the top ones properly rather than all of them thinly.

**Tier 1 — directly unblocks our next experiments**

1. **ath10k-CT status and capability drift.** What has changed in Candela Tech's ath10k-CT driver and
   firmware for QCA988x in the last ~18 months? Specifically: what do `ratemask-CT`, `set_rates`,
   `set_rate_override`, `txrate2-CT`, `retry-gt2-CT` and `cust-stats-CT` actually control, what are
   their documented limits, update latency, and known bugs? Is there newer CT firmware than
   `10.1-ct-8x-__fW-022` for QCA988x, and what changed?
2. **Spectral scan on QCA988x.** How do we get spectral FFT working — which driver (upstream ath10k vs
   ath10k-CT), which firmware, which build flags (`CONFIG_ATH10K_SPECTRAL`, relayfs), and what is the
   real resolution/rate/accuracy on Wave 1? Any working capture and parsing toolchains.
3. **A-MPDU / aggregation control.** What does `htt_max_amsdu_ampdu` actually do on QCA988x firmware,
   is it per-device or per-peer, and has anyone measured latency/throughput effects of tuning it?
4. **Upstream ath10k vs ath10k-CT** for QCA988x in 2025–2026: feature-by-feature differences that
   matter for telemetry, rate control, spectral, per-peer stats, and stability under PtMP load.
5. **OpenWrt 25.12 / newer kernels:** what changed in mac80211 queueing, AQL, airtime fairness and
   ath10k since Linux 6.6 that would matter for us? Is there a concrete reason to move off 24.10.4?

**Tier 1.5 — real-hardware literature (this layer was MISSING from the first pass; run it as a
dedicated search, not as a by-product of a general one)**

5b. **Papers with real-hardware measurements** on 802.11ac / ath10k / QCA / TDMA / polling /
    deterministic Wi-Fi / airtime scheduling / aggregation / rate control. Require the full text to
    contain testbed, prototype, hardware, AP model, chipset, latency percentile, throughput,
    microseconds, or experiments — and **aggressively reject simulation-only papers**. For each:
    silicon, driver, what was measured, the number, and whether the *technique* (not the number)
    applies to firmware-owned rate control. Prioritise 2025–2026 and anything on QCA988x/QCA9880.
5c. **Autonomous / AI-driven experimentation on real radios** — anything in the IteRate /
    Autoresearch lineage: closed-loop systems that propose, deploy and evaluate wireless control
    policies on physical nodes. Architecture, validity gating, and how they avoid gaming the metric.

**Tier 2 — the strategic question (custom MAC feasibility)**

6. **TDMA / scheduled access on commodity 802.11 hardware.** State of the art for imposing
   deterministic or polled access on COTS Wi-Fi chips — academic and open-source. Include anything
   with *real hardware measurements*: TDMA-over-WiFi, SoftMAC/split-MAC work, ath9k/ath10k timing
   work, openwifi (SDR FPGA 802.11), WiSHFUL/ORCA, Wi-Fi TSN, 802.11 with firmware replacement.
   For each: what timing precision was achieved, on what silicon, and what host-to-air latency bound.
7. **QCA988x firmware internals.** Any public reverse-engineering, SDK availability, symbol maps, or
   alternative firmware for the QCA988x Xtensa target. Is there a usable path to modifying the radio
   firmware at all, legally and technically?
8. **Per-peer TX power / ATPC** and **CSI extraction** on ath10k/QCA988x — what is genuinely available
   versus what only exists on ath9k or Intel/Broadcom chips.

**Tier 3 — context and competitive**

9. **Fixed-wireless PtMP technique 2025–2026:** what Cambium (PMP/450, 802.11-based Elevate), Mimosa,
   Tarana and open projects do for scheduling, fairness, interference mitigation and latency in the
   same band. Only concrete technical mechanisms, not marketing claims.
10. **Queueing/latency research applicable to a WISP POP:** CAKE/FQ-CoDel deployment results,
    airtime-fair scheduling, L4S/ECN over wireless, bufferbloat measurement methodology.
11. **Rate control research** applicable when rate selection is firmware-owned: supervisory/outer-loop
    rate control, per-station rate masks driven by learned history, ML-assisted link adaptation with
    *real* deployment data.

## SOURCE RULES — mandatory, this is the part that has failed before

- **Every factual claim must carry a resolvable URL.** Before citing, confirm the URL actually resolves
  to the content you describe. A citation pointing at an unrelated paper is worse than no citation.
- **If you cannot find a source, write `UNKNOWN`.** Do not infer, extrapolate, or fill the gap with a
  plausible-sounding statement. An honest gap is a useful result.
- Prefer, in this order: **(1)** source code / commits / device-tree / driver source for an exact
  version, **(2)** official vendor or kernel documentation, **(3)** peer-reviewed work with *real
  hardware* measurements, **(4)** kernel/OpenWrt mailing lists and issue trackers, **(5)** simulation
  results, **(6)** forum/community reports.
- **Label every claim** `CONFIRMED` / `INFERRED` / `UNKNOWN` / `REFUTED`, and name the evidence tier
  (1–6) behind it. A forum post can never make something CONFIRMED.
- **Flag simulation-only results explicitly.** Do not let a simulated gain read as a measured one.
- **Do not aggregate gains across papers.** If three papers each claim +15%, that is not +45%.
- Where a claim is about our exact chip, say whether the evidence is for **QCA988x specifically**, for
  another ath10k chip (QCA9888/9984/4019), or for a different vendor entirely. Cross-chip claims are
  the most common way this research goes wrong.
- Distinguish **ath10k** from **ath10k-CT**, and both from the vendor **`ol_ath`/`umac`** stack. Earlier
  research waves conflated these and produced an entirely wrong picture.

## OUTPUT FORMAT

1. **Executive summary** — max 10 bullets, each an actionable finding, each with its label.
2. **Per-question sections** in the ranked order above. For each finding:
   `CLAIM | LABEL | EVIDENCE TIER | URL | chip/stack it applies to | why it matters to us`
3. **What changed recently** — anything new since mid-2025, dated.
4. **Contradictions** — where sources disagree, state both and which is better-evidenced. Do not
   silently pick one.
5. **UNKNOWNS** — an explicit list of what you could not establish. An empty section here is a red
   flag, not a success.
6. **Suggested experiments** — concrete tests runnable on the hardware in BASELINE, each with the
   specific question it would answer.
7. **Source table** — every URL used, with what it supports and its evidence tier.

Do not include: general Wi-Fi tutorials, vendor marketing copy, Wi-Fi 6/7 PHY features our silicon
cannot execute, consumer router advice, or anything about tuning the stock vendor configuration.

=== END PROMPT ===

---

## Maintenance

Update **BASELINE** whenever any of these change, or when research comes back aimed at the wrong
system: OpenWrt version, kernel version, driver (ath10k vs ath10k-CT), radio firmware string, the
debugfs entry list, whether spectral is present.

Log each wave in `research/intake/manifest.yaml` with provider, date and SHA-256 before citing it,
per the existing intake process.
