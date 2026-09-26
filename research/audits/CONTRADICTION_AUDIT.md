# FuturaMAX contradiction and portability audit (R6, wave 1)

Summary: 16 substantive disagreements between the six external Deep Research runs, each
with the disputed fact, who said what, why it is load-bearing, and how to settle it.
Keywords: contradiction, cross-model disagreement, fabricated precision, evidence grade,
airtime scheduler, rate control ownership, aggregation control, QCA9888, OpenWrt baseline.
Read when: you are about to treat any cross-model agreement as truth, or before promoting
any wave-1 claim to CONFIRMED. Current verdict: NO wave-1 claim may be promoted yet.
Status: CURRENT. Generated 2026-08-08 from research/extracted/*/report.md. Hand-written.

## How to read this file

Six models were given the same prompt (`inputs/prompts/external-deep-research-prompt.md`)
and returned the same 11-section template. That makes them directly comparable, which is
the only reason this audit is possible. It also makes their agreement **worthless as
evidence**: they searched the same public web with the same seed list, so agreement mostly
measures shared priors, not shared verification. Only 51 of 535 cited URLs were cited by
more than one run, so even the source sets barely overlap.

Conflict severity:

- **BLOCKING** — a downstream engineering decision is different depending on the answer.
- **MATERIAL** — changes an effect size or an evidence grade, not the decision.
- **HYGIENE** — a factual slip that discredits the run it appears in.

`run` codes: `cg`=chatgpt, `go`=google, `qw`=qwen, `gl`=glm, `gk`=grok, `mi`=mistral.

## The one thing every run agrees on

All six independently conclude that **QCA988x is a firmware-offload architecture and that
a custom microsecond PtMP MAC above stock firmware is blocked or near-blocked**, and all
six rank host-side queueing/AQL plus external slow-loop optimization as the highest-value
transferable work. This is the strongest signal wave 1 produced. It is still only
`INFERRED` for the exact target hardware until R3 verification and E0/E2 experiments run,
because five of the six reach it by citing the same handful of documents.

---

## BLOCKING conflicts

### C01 — Can the mac80211 airtime-fairness scheduler run on ath10k?

| Position | Runs | What they say |
|---|---|---|
| **No** | cg, gl, go, (mi implicitly) | "Ending the Anomaly" implemented its airtime scheduler on ath9k *because* "the ath10k driver lacks the required scheduling hooks". gl quotes the paper directly; go lists it as blocker #7; cg lists it as blocker #4. |
| **Yes** | gk | "AQL + airtime fairness ... Implemented in mac80211 + ath10k. Demonstrated on QCA hardware"; and separately "deficit round-robin preferred over virtual-time for stability with AQL on ath10k — CONFIRMED in OpenWrt trees". |

**Why it is blocking.** Airtime fairness is the #1 or #2 ranked candidate in five of six
runs. If it cannot run on ath10k, the near-term plan collapses to AQL + upstream shaping
only, and near/far fairness has to be approximated from the qdisc layer instead of enforced
at the radio.

**Likely resolution — temporal, not factual.** The ATC'17 statement is from 2017. The AQL
work landed 2019–2020 and *did* target ath10k. Both positions can be simultaneously true at
different kernel versions. Do not record either as CONFIRMED; record the *version* at which
each becomes true.

**How to settle:** read the ATC'17 paper section verbatim, then read current
`net/mac80211/tx.c` / `ieee80211_txq_may_transmit` and ath10k's `wake_tx_queue` + airtime
reporting path in the exact kernel OpenWrt ships for `ath79`. This is a source-reading task,
not a search task. Owner: W03/W07.

### C02 — Who selects the transmit rate on ath10k: mac80211 Minstrel-HT, or QCA firmware?

| Position | Runs | What they say |
|---|---|---|
| **Firmware** | cg, go, gl, gk, qw | gl is explicit: "On stock OpenWrt with ath10k, Minstrel-HT is NOT the active rate controller — rate adaptation runs inside the closed QCA firmware." gk cites `WMI_SERVICE_RATECTRL`. |
| **Minstrel-HT** | mi | "Minstrel-HT is the default rate adaptation algorithm in Linux for 802.11n/ac WLANs, **including ath10k**" — graded **CONFIRMED**, and then used to rank "Minstrel-HT tuning" as its Tier-1 top recommendation. |

**Why it is blocking.** mi's entire top-ranked recommendation is invalid if the majority is
right. Five-to-one plus a direct mechanism (firmware rate control service bit) says mi is
wrong. Flagging rather than silently discarding, per the no-silent-deletion rule.

**How to settle:** `WMI_SERVICE_RATECTRL` presence in ath10k WMI service bitmap for
QCA988x firmware; whether mac80211 registers a rate-control ops struct for ath10k. Source
reading, one hour. Owner: W05.

### C03 — Can the host control A-MPDU aggregation length on QCA988x?

This is the single most consequential unresolved question in wave 1, because PNOFA is the
strongest adjacent-hardware result anyone found and this is its portability gate.

| Position | Runs | What they say |
|---|---|---|
| **No host knob** | gl | "aggregation size and Block ACK window are controlled by QCA firmware, not exposed as host-controllable knobs on ath10k (no debugfs aggregation control found)". |
| **Yes, CONFIRMED** | go | "`ath10k-ct` provides direct WMI/debugfs hooks to restrict max A-MPDU size" — graded **CONFIRMED**, expected gain 15–30%. |
| **Enough telemetry, DEMONSTRATED** | gk | "Block ACK / A-MPDU telemetry via HTT — enough visibility for user-space aggregation optimizers (PNOFA-style)". |
| **UNKNOWN** | cg, mi | cg: "no documented arbitrary A-MPDU-length API equivalent to PNOFA's requirement ... The CT `wmi-block-ack-CT` feature is encouraging but does not by itself prove that control." mi lists it as an explicit UNKNOWN. |

**Why it is blocking.** A four-way split with one run claiming CONFIRMED and one claiming
the opposite. go supplies no locator for its claim. cg is the only run that names the
concrete artifact (`wmi-block-ack-CT` in an OpenWrt boot log) and correctly refuses to
promote it.

**How to settle:** grep ath10k-ct sources for the WMI/debugfs aggregation setters; read the
CT user guide; then a physical Block-ACK observability test (experiment 3 in cg's list).
Until then the answer is **UNKNOWN**. Owner: W06 + E2.

### C04 — Is there any real measurement of OpenWrt vs airMAX on a loaded PtMP sector?

| Position | Runs | What they say |
|---|---|---|
| **No such experiment exists** | cg, mi | cg blocker #20: "no credible published experiment found here demonstrates OpenWrt/ath10k on these exact CPE/AP models beating airMAX AC TDMA in a many-CPE outdoor sector ... treat as a negative evidence gap, not silently filled by adjacent Wi-Fi papers." mi lists the comparison as UNKNOWN. |
| **Yes, and here are the numbers** | go | Three separate figures: "throughput collapses by 40–70%, latency ... from <10 ms to >250 ms"; "sector capacity drops by 50–75% compared to stock airOS 8"; and a table row "Ping under load: **8 ms → 280 ms**; Sector throughput: **−55%** regression", 30-CPE sector, graded **CONFIRMED (Negative result)** — sourced to "OpenWrt / Reddit Reports". |

**Why it is blocking.** This is the project's central question. go's numbers, if real, would
nearly settle it. They are graded CONFIRMED against a forum/Reddit citation with no link,
no device, no date, and three mutually inconsistent magnitudes (−40–70%, −50–75%, −55%)
inside one document.

**Verdict: REJECT go's figures outright.** They violate the quality gate "no percentage gain
without baseline, hardware, conditions, and metric" and "no adjacent-hardware or unverified
community result labeled CONFIRMED". Record the *question* as the top experiment (this is
cg's experiment #1 and gk's experiment #1), not the numbers. Owner: E2/E3, not research.

---

## MATERIAL conflicts — effect sizes that do not match their own sources

A consistent pattern: **go and mi supply rounder, larger, more quotable numbers than cg for
the same experiments**, and cite the same papers. Where cg gives methodology (trial counts,
confidence intervals, exact baselines) and the others give a bare percentage, prefer cg
pending R3 verification against the paper PDF.

### C05 — hMAC hidden-node result

- cg: aggregate **4.2 → 8.8 Mbit/s**; the starved link **1.2 → ~5.5 Mbit/s**; AR9280/ath9k, 2 APs + 3 STAs, error bars = standard error.
- go: **12 → 28 Mbps (+133%)**, "2-link hidden node topology".

Same paper, different numbers and a different topology. Settle from the TU Berlin PDF.

### C06 — WiLDNet

- cg: 65 km link, simultaneous bidirectional TCP **0.68±0.39 → 5.51±0.07 Mbps**, 10×30 s, 11 Mbps PHY, Click shim on commodity Atheros; overall paper reports 2–5×.
- gl: "2–5× ... on long-distance links (50–100 km), MadWifi".
- go: "20 km long-distance outdoor link, TCP goodput **5 → 23 Mbps (+360%)**, zero collision losses", hardware **AR5212**, driver **FreeBSD / MadWifi**.
- gk: "km-scale, 2–5×".

go's row is wrong in a checkable way: **MadWifi is a Linux driver, not FreeBSD**, and WiLDNet
(NSDI'07) is a Linux/Click system. Treat go's WiLDNet row as unreliable.

### C07 — PNOFA effect size

- cg and gk agree: **up to +29%, mean +17%** vs the proprietary Qualcomm aggregator, IPQ4019 Google Wifi, 10 randomized interleaved 30 s trials per algorithm.
- go: **+18% to +32%** "on links with 10–25% subframe error rate".
- gl: reports it as "within **97%** of statistically optimal" (a different metric, not in conflict — this is the trace-evaluation result, which cg also reports).

cg+gk converge with full methodology; prefer +29% max / +17% mean.

### C08 — GPS Sync effect size (all vendor-grade)

Four different numbers circulate: cg "240 vs 124 Mbps" (vendor) and a field report of
"26–38 ms → 10–12 ms" with modulation recovering to 256-QAM; gl "20% higher TCP throughput
vs competing products" (vendor); mi "**90% higher throughput**" attributed to the UISP GPS
Sync FAQ. None is research-grade. mi's 90% is the most extreme and the most weakly located.
Do not carry any of these into knowledge files as an effect size — carry the *mechanism*
(co-located sectors TX/RX simultaneously → frequency reuse) and mark magnitude UNKNOWN.

### C09 — NeuRA

- cg: **+14% and +16%** average throughput vs Minstrel HT in two stationary prototype tests, 95% CIs non-overlapping, baselines 58.3 and 159.7 Mbps; trace evaluation up to +24%/mean +16%.
- go: "rate prediction error **−40%**; goodput **+15% to +25%**".

go's "−40% prediction error" appears in no other run and is not a metric cg reports.

### C10 — IteRate arXiv identifier

cg cites `arxiv.org/abs/2605.02542`; go cites `arxiv.org/abs/2605.02508`. Both cannot be the
same paper. Attribution also differs: gl says MIT CSAIL / James Lynch; cg says "Lynch et
al."; go says "IteRate Research Team". Settled mechanically by the link check
(`research/normalized/link_check.jsonl`) plus reading the abstract page.

---

## HYGIENE failures — checkable factual slips

### C11 — Target SoC identity

- cg, gl (and the OpenWrt device pages both cite): **AR9342**, MIPS 74Kc, ~535 MHz, 64 MiB RAM, 16 MiB flash.
- go: "**QCA9563/XC/WA board series**", "MIPS 74Kc **@ 750 MHz**", and builds a CPU-budget argument on it ("caps routing throughput at ~120–150 Mbps").

Different SoC, different clock. go's CPU-headroom conclusions inherit the error. Owner: W01,
and settled definitively by physical inventory (cg experiment #2).

### C12 — NanoStation 5AC radio: QCA988x or QCA9888?

- cg: NanoStation AC Loco = AR9342 + **QCA988X**.
- gl's own source ledger: "OpenWrt Wiki — NanoStation AC (AR9342, **QCA9888**)" while listing "NanoStation AC loco (QCA988X)".

**QCA9888 is 802.11ac Wave 2, QCA988x is Wave 1.** If any target CPE is actually QCA9888,
its firmware generation (10.4 vs 10.2.4), telemetry surface and CT feature set all differ —
several wave-1 blockers in this audit would not apply to it. This is the highest-value
single item for W01 and it is resolvable from the OpenWrt device pages plus a physical PCI
ID read.

### C13 — QCA988x wave and firmware CPU

- mi's control-boundary diagram labels QCA988x/QCA9882 as "2x2 MIMO, 802.11ac **Wave 2**". It is Wave 1.
- go describes the radio firmware CPU as a "**Tensilica Xtensa ARM** CPU" and elsewhere as "closed binary **ARM** firmware". Xtensa is not ARM; the document contradicts itself.

Neither slip changes a conclusion, but both lower the trust weight of the run they appear in.

### C14 — "OpenWrt cannot boot on Ubiquiti AC gear"

gl quotes: "Openwrt for instance can't yet boot on ubiquiti AC gear because the u-boot code
isn't available" — and lists it as **BLOCKER #4**. gl's *own* source ledger then links four
OpenWrt device pages for LiteAP AC, NanoStation AC, NanoStation AC loco and LiteBeam 5AC
Gen2, and its positive finding #19 says all four are OpenWrt-supported.

The quote is stale (pre-2019). A blocker contradicted by the same document's own evidence.
**Reject.**

### C15 — The airMAX "ASIC that accelerates the scheduler"

- gl blocker #3 asserts airMAX AC uses "a proprietary ASIC [that] provides hardware acceleration capabilities to the airMAX scheduler" — sourced to `netwifiworks.com`, a reseller product page.
- cg: "no primary evidence located that identifies a separately programmable 'airMAX accelerator'", marked UNKNOWN.

A reseller marketing page cannot establish a silicon-level architectural claim that, if
true, is one of the strongest arguments against ever matching airMAX. Downgrade to UNKNOWN
and route to W02 (FCC filings, teardowns, GPL releases). Note the adjacent real thing:
airPrISM is a marketed Ubiquiti feature but is associated with Rocket AC Prism, not
necessarily with LiteAP/LiteBeam/NanoStation.

### C16 — Spectral scan availability on QCA988x

cg, gl and gk all cite the ath10k spectral documentation (64/128/256 bins, with documented
20/40 MHz sample-count and 80 MHz 64-bin defects). go says "128-bin" only. mi lists
"Availability of spectral FFT interference classification on QCA988x via ath10k" as
**UNKNOWN**.

This is not a real dispute — it is a coverage gap in mi and an imprecision in go. The
documented interface settles it. Worth recording because it demonstrates that a model
answering UNKNOWN is sometimes just under-searched, and its UNKNOWN must not be averaged
against three CONFIRMEDs into a false "disputed" status.

---

## Resolution log (updated as conflicts are settled against primary sources)

Five of the sixteen are now settled. All five were settled by opening a primary source, not
by weighing model opinions.

### C10 — RESOLVED 2026-08-08. cg correct, go's citation points at an unrelated paper.

Link check + arXiv title harvest:

- `arxiv.org/abs/2605.02542` → **"IteRate: Autonomous AI Synthesis of In-Kernel eBPF Wi-Fi Rate Control Algorithms"** (cited by cg) ✅
- `arxiv.org/abs/2605.02508` → **"Unravelling the complex structure of the Fe II emission region in Type 1 active galactic nuclei"** (cited by go) ❌

go's IteRate citation resolves to an **astrophysics paper**. Not a typo that lands on
nothing — a live URL for entirely unrelated work, which is exactly the failure mode a
reachability-only check would have passed. Recorded because it is the clearest single piece
of evidence that go's citations cannot be trusted without opening them.

### C11 — RESOLVED 2026-08-08. cg/gl correct; go's SoC and clock are both wrong.

NanoStation AC boot logs (OEM and OpenWrt) both report `SoC: Atheros AR9342 rev 2`,
`CPU0 revision is: 0001974c (MIPS 74Kc)`, `Clocks: CPU:535.000MHz`. Not QCA9563, not
750 MHz. go's CPU-headroom argument ("caps routing throughput at ~120–150 Mbps") is built
on the wrong part and must not be carried forward. See `knowledge/HARDWARE_MATRIX.md`.

### C12 — RESOLVED 2026-08-08. cg correct; gl's ledger row is wrong.

`ath10k_pci 0000:00:00.0: qca988x hw2.0 target 0x4100016c chip_id 0x043222ff sub 0777:e7fb`,
firmware `10.2.4-1.0-00037`. NanoStation AC is **QCA988X Wave 1**, not QCA9888 Wave 2. The
wave-1 blockers in this audit do apply to it. **This does not extend to LAP-GPS**, which
remains unverified and is the AP the project actually depends on.

### C13 — RESOLVED (partial). mistral's "Wave 2" label is wrong; go's firmware-CPU description is self-contradictory.

Settled by the same boot log for the wave question. The Xtensa-vs-ARM point stands as an
internal inconsistency in go and needs no external source.

### C14 — RESOLVED 2026-08-08. Reject gl's blocker #4.

OpenWrt boots on this exact device; the page carries a complete OpenWrt 4.9.109 boot log
with working `ath10k_pci`. gl's quoted claim is stale and was already contradicted by gl's
own source ledger.

### C01, C02, C03 — RESOLVED 2026-08-08 from source. See `knowledge/QCA988X_CONTROL_BOUNDARY.md`.

- **C02 — firmware owns rate control.** `ieee80211_hw_set(ar->hw, HAS_RATE_CONTROL)` in
  ath10k `mac.c`; no `rate_control_ops`, no minstrel reference anywhere in the driver.
  **mistral refuted**; its Tier-1 top recommendation is not implementable.
- **C01 — both sides were wrong, and the split was temporal.** The ATC'17 limitation is
  superseded (ath10k has `wake_tx_queue` and feeds the TXQ scheduler), so grok is closer to
  current truth. But `WMI_SERVICE_REPORT_AIRTIME` is mapped **for the 10.4 generation only**,
  so QCA988x can never report actual airtime; the scheduler runs on an estimate from
  `last_tx_bitrate`, which is populated solely by the HTT peer-stats path — and **falls back
  to assuming 6 Mbps for every frame** when peer stats are absent. Nobody in wave 1 found this.
- **C03 — the code answer sits between all four positions.** `htt_max_amsdu_ampdu` debugfs in
  ath10k-ct issues an HTT AGGR_CFG message, so **glm's "no control exists" is refuted**; but
  it is device-wide, not per-peer, so **google's "CONFIRMED direct hooks, 15–30%" overclaims**.
  chatgpt's UNKNOWN was appropriately cautious. Whether the firmware honours it is UNVERIFIED.

### Still open and on the critical path

**C01** (airtime scheduler on ath10k), **C02** (who owns rate control), **C03** (A-MPDU
control) and the **LAP-GPS row of the hardware matrix**. C01–C03 are settled by reading
ath10k/mac80211/ath10k-ct source, not by more searching. The LAP-GPS question needs physical
hardware.

### New conflict opened by primary evidence

**C17 — airOS does not run ath10k, and no run noticed.** The OEM boot log shows
`ath_pci: 10.1.467 (Atheros/multi-bss)` (the QCA vendor `ol_ath` offload driver) plus the
proprietary `ubnthal` and `ubnt_poll_host` modules. All six runs framed the comparison as
"airMAX firmware vs ath10k". It is actually **`ol_ath` + `ubnt_poll_host` vs `ath10k` +
`mac80211`** — two different driver stacks, not one stack with a different scheduler. Every
portability judgement in wave 1 was made against a stack description that does not match the
device. Severity: **BLOCKING** for W02/W03 framing. See `knowledge/HARDWARE_MATRIX.md`.

## What this audit changes

1. **No wave-1 claim may be promoted to CONFIRMED on the strength of model agreement.**
   Promotion requires a primary source opened and read at R3.
2. **Per-run trust weighting for wave 2 triage** (a prioritisation heuristic for reading
   order, not an evidence grade): cg is the only run that consistently supplies baselines,
   trial counts and statistics and that explicitly refuses to promote unproven claims; gl is
   the most source-dense and best at negative evidence; gk is concise and broadly consistent
   with cg; qw is prose-only but aligned; mi is honest about UNKNOWNs but has two hygiene
   failures and one blocking error; **go has the most quotable numbers and the weakest
   locators, and is the source of every rejected figure in this audit.**
3. **Four questions are now the research critical path** — C01, C02, C03, C12. All four are
   settled by reading primary sources and one physical inventory, not by more model runs.
4. **Wave 2 must not re-run the wave-1 prompt.** Six runs of the same prompt produced one
   consensus and sixteen disagreements; a seventh would add a seventh opinion, not evidence.
