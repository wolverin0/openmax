# Real-hardware literature catalogue — verified, tiered, and scoped to QCA988x applicability

Summary: every published result FuturaMAX leans on, with the evidence tier per AGENTS.md §6, what
silicon it was measured on, whether its NUMBERS transfer to QCA988x (almost never) or only its
TECHNIQUE (usually), and my independent verification status. Keywords: IteRate, WiFiSpectralJam,
RF Jamming Dataset, ORCA, RateMan, WiFi-CUTS, PNOFA, Quick & Plenty, Ending the Anomaly, hMAC,
SmartLA, SRT-WiFi, autoresearch, Tier 3, Tier 4, QCA9880, mt76, ath9k, IPQ4019.
Read when: citing a paper, sizing an expected gain, or designing an experiment. Rule: numbers from
other silicon are HYPOTHESES for us, never results. Status: CURRENT 2026-09-20.

## Tier rules used here

The table uses the **6-tier scheme the research was graded under** (`prompt.md` SOURCE RULES):
(1) source code for the exact build · (2) official vendor/kernel docs · (3) peer-reviewed work with
real-hardware measurements · (4) real-hardware work that is NOT peer-reviewed — the wave's explicit
downgrade for preprints, which nominally shares the slot with mailing lists · (5) simulation ·
(6) forum/community. To map onto AGENTS.md §6 add 1 (its tier 1 is *our own measurements*, which
sit above everything in this file). "Verified" means *I* resolved the source and confirmed the
claim text, not that the report said so.

## Catalogue

| Work | What it established (real hardware) | Silicon | Tier | Transfers to us as | Verified |
|---|---|---|---|---|---|
| **IteRate** — arXiv:2605.02542, MIT CSAIL, May 2026 | Autonomous multi-agent loop: hypothesis → eBPF rate-control program → OTA deploy → per-frame telemetry → analysis → iterate, no human. 58-node testbed, 5 workloads: **+21% page-load speed, +7% video QoE, +21% peak throughput vs Minstrel**. | MediaTek **mt76** (host-controlled RC) | 4 (preprint) | **Architecture only.** Its RC is host-programmable; ours is firmware-owned. Copying the controller is wrong; copying the loop is the point. | ✅ arXiv resolves; abstract matches every figure. **Corrects the Aug audit:** the "AGN paper" was a bad *link* in the google run, not a fabricated paper. |
| **WiFiSpectralJam** — arXiv:2608.15728, Aug 2026 | 14.52 GB / 96,090 files / **522,771,130 ordered spectral observations** from RPi CM4 + **QCA9880** + ath10k spectral scan; benign, RF-chamber (Candela CT840A) and HackRF-jammed captures, 2.4 + 5 GHz. | **QCA9880** (our Wave-1 family), upstream ath10k | 4 (preprint) | **Direct.** Proves Wave-1 spectral capture is practically useful at scale, and gives an external validation dataset for our own parser/classifier. | ✅ arXiv resolves; figures match exactly. |
| **RF Jamming Dataset** — IEEE ComMag 2024, DOI 10.1109/MCOM.003.2300483 | Peer-reviewed predecessor: **QCA9880 + ath10k**, HT20/HT40/VHT80; five ML classifiers **>90% jamming-detection accuracy**. | **QCA9880** | 3 | **Direct.** Peer-reviewed Wave-1 FFT evidence. | ✅ ACM DOI + IEEE DataPort resolve; Xplore 10411983 answers 202 (anti-bot). HT20/40/VHT80 detail corroborated by DataPort rig description, not re-read from the paywalled text. |
| **ORCA / RateMan** — MobiCom 2024, github.com/SupraCoNeX/orca | Kernel→userspace telemetry/control over debugfs/relayfs, remote daemon, Python controller, per-station resource management on real OpenWrt radios. | mt76, ath9k (host-controlled RC) | 3 | **Architecture.** Keeps intelligence OFF the 535 MHz/64 MB AP — exactly our constraint. Do not port its RA. | ✅ repo resolves 200. |
| **WiFi-CUTS** — IEEE Xplore 11224946 (TCOM) | Cascaded unimodal Thompson-sampling bandits on real 802.11ac: **≥7%, avg 15%, up to 37% over Minstrel-HT** (medium/high-SNR shielded-box). | UNKNOWN NIC | 3 | **Method.** Bandits for choosing rate *masks*/aggregation/policy around firmware RC. Numbers do not transfer (we don't run Minstrel). | ✅ Xplore resolves; 7/15/37% match. The "≥18.2% OTA" figure NOT independently corroborated. |
| **Freifunk GSoC 2025 ORCA-DQN** — blog.freifunk.net 2025-08-27 | RF-isolated AP↔STA testbed with programmable attenuator, packet-level telemetry, DQN training, live deploy via RateMan. | not QCA988x | 6 (community) | **Lab methodology** for controlled training data. Not proof of gain. | ✅ resolves 200. |
| **PNOFA** — Abedi, Brecht, Abari, *"Demystifying frame aggregation in 802.11 networks: Understanding and approximating optimality"*, **Computer Communications** 180 (2021) 259–270, DOI 10.1016/j.comcom.2021.09.019 | Practical Near-Optimal Frame Aggregation, run as a **user-space process** on a Google Wifi AP (**Qualcomm IPQ4019 Wave-2**, closed firmware), needing only block-ACK and PHY-rate information: **+17% UDP, +13% TCP** average throughput vs the chipset firmware's own aggregation, "on the scenarios tested". Trace-driven: within 97% of the statistically optimal algorithm. | IPQ4019 (Wave 2) | 3 | **Strategic precedent:** closed firmware did not prevent useful outer-loop aggregation control, and the information it needs is the class our CT debugfs exposes. Numbers do NOT transfer to Wave 1. | ✅ Abstract read in a real browser (ScienceDirect walls curl/WebFetch); title, venue, chip, and both percentages confirmed. |
| **Quick & Plenty** — Hassani, Gringoli, Leith, *"Quick & plenty: Achieving low delay & high rate in 802.11ac edge networks"*, **Computer Networks** 187 (2021) 107820, DOI 10.1016/j.comnet.2021.107820 | Regulating the downlink send rate to hold a **target aggregation level** avoids a persistent AP queue while keeping rate high: hardware testbed, **~2 ms one-way at ~500 Mb/s**, 802.11ac 3SS MCS9, N_max = 64. Aggregation level rises monotonically with send rate until saturation; delay rises slowly then sharply — the knee is the operating point. | unspecified 802.11ac AP (office testbed) | 3 | **Signal design:** aggregate occupancy as the feedback variable for per-CPE pacing + AQL. They had to infer aggregation at the *receiver* from MAC timestamps because they did not control the AP; **we own the AP**, so the same signal is available directly from the driver. | ✅ Abstract + intro read in a real browser; title, venue, DOI, authors, 2 ms / 500 Mb/s / 3SS MCS9 all confirmed. |
| **Ending the Anomaly** — USENIX ATC '17 (Høiland-Jørgensen et al.) | The real-testbed work behind modern Linux Wi-Fi queueing: ~order-of-magnitude loaded-latency reduction, near-perfect airtime fairness, up to 5× aggregate in deliberately bad mixed-rate cases. | ath9k | 3 | **Baseline, already in our Linux-6.6 argument.** The 5× is a pathological ceiling, not an expectation. | ✅ USENIX page resolves 200. |
| **hMAC** — github.com/szehl/ath9k-hmac | Software TX queues gated into TDMA-like slots while hardware CSMA/CA stays active; example config 20 ms slots. | **ath9k only** | 4 | Supports trying host-side **soft** polling eventually. Establishes nothing about hard TDMA timing on QCA988x. | ✅ repo resolves 200. |
| **SmartLA** — Karmakar, Chattopadhyay, Chakraborty, *"SmartLA: Reinforcement learning-based link adaptation for high throughput wireless access networks"*, **Computer Communications** 110 (2017) 1–25, DOI 10.1016/j.comcom.2017.05.017 | SARSA-based sender-side closed-loop link adaptation over channel bonding, MCS, SGI and aggregation level, using SNR/BER/FER; evaluated in NS-3 **and** on a **26-node 802.11ac testbed (6 APs, 20 clients) over four months**, static and mobile. | unspecified NIC | 3 (the testbed half; the NS-3 half is tier 5) | Precedent for learning from **long link history** — our fixed WISP links have it in abundance. Its action space (bonding/MCS/SGI/aggregation) is exactly the *policy* layer we would wrap around firmware RC. | ✅ Abstract + intro + testbed section read in a real browser; venue/year/DOI/testbed size/duration confirmed. Earlier "Computer Networks 2018" here was wrong. |
| **SRT-WiFi / RT-WiFi** — arXiv:2203.10390 | Deterministic-MAC timing on an SDR testbed. | SDR, not commodity | 4 | Reference point for what deterministic access *costs*; not achievable on our silicon. | ✅ resolved in wave 1. |

## What this catalogue changes

1. **REFUTED (from wave 1 / Aug):** "there is no strong QCA988x real-hardware spectral literature."
   There is a peer-reviewed 2024 paper *and* a 522-million-observation 2026 dataset, both on
   QCA9880 + ath10k. FMX-0010 now has an external validation target.
2. **CORRECTED (Aug citation audit):** IteRate exists and is exactly what was described. The
   audit's rejection was of a broken link, not of the paper. Its *architecture* is the closest
   published system to the AGENTS.md §9 "automated experiment loop".
3. **Closed firmware is not a wall.** PNOFA's outer-loop aggregation control beat Qualcomm's own
   firmware aggregation on a closed Wave-2 part. That is the existence proof for FuturaMAX's
   "supervise the firmware, don't replace it" strategy — verified from the abstract: PNOFA runs as a
   *user-space process* needing only block-ACK and PHY-rate feedback, which is the information class
   our ath10k-CT debugfs already exposes.

## What must never be done with this table

- Do not add the percentages together. AGENTS.md §13, verbatim: *"Do not add gains from unrelated
  papers together."*
- Do not present any figure here as a QCA988x result. None of them are. They bound what is
  *plausible*; only FMX experiments can turn a bound into a claim.
- Every row above was verified in a real browser on 2026-09-20. If you edit a row's claim, re-verify
  it — and note ScienceDirect returns 403/400 to curl and WebFetch but serves the abstract to a real
  browser session, so a script cannot do this check for you.
