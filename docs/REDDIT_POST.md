# Reddit Post Drafts (for r/wisp, r/networking, r/openwrt)

> **Instructions**: Pick the version matching the subreddit you want to post in. Keep the tone completely human, humble, and direct. Do not add emojis or marketing buzzwords.

---

## Option 1: Tailored for r/wisp

**Suggested Title:**  
*Trying to squeeze every last drop out of old airMAX AC gear with OpenWrt and an automated rooftop testbed (looking for input / collaborators)*

**Post Body:**

Hey everyone,

Like pretty much everyone running a fixed wireless network, I have hundreds of Ubiquiti airMAX AC radios (LiteBeam Gen2, LAP-120, LAP-GPS, Loco AC) deployed on customer roofs, plus dozens sitting on shelves in the warehouse. 

We all know the situation: Ubiquiti essentially put airMAX AC into maintenance mode years ago. All the vendor R&D is going into Wave 60GHz and LTU. That’s fine for greenfield deployments, but in the real world, you can’t just rip and replace 500 CPEs on rural towers when trees and distance dictate 5 GHz. Millions of these radios are going to stay on rooftops for years.

Meanwhile, the software running on them hasn't fundamentally evolved since 2017–2018. If a CPE link gets slightly noisy or misaligned, stock airOS does dumb things—like running up to 30 frame retries by default, which burns dozens of milliseconds of airtime and drags down the whole AP sector. On top of that, loaded bufferbloat easily hits 2,000+ ms during heavy uploads.

Over the last few weeks, I’ve been researching what the actual physical ceiling of this QCA9880 / AR9342 hardware is if we run modern open-source networking on it (OpenWrt 24.10, Candela Technologies ath10k-ct, mac80211 AQL, CAKE, and dynamic rate-masking).

Full disclosure: I’m an everyday WISP operator. I run towers, climb roofs, crimp cables, and configure MikroTik/airMAX gear. I am NOT a Linux kernel hacker or an RF engineer with a Ph.D. So I've been using AI tools (Claude, Codex, NotebookLM) to comb through Linux wireless kernel trees, academic preprints (like MIT’s IteRate paper and TU Berlin’s hMAC), and old mailing list threads to understand what the chip can actually do.

We’ve already documented a bunch of interesting architectural facts that I rarely see discussed in WISP groups:

1. **The 30-Retry Sector Killer:** Upstream Qualcomm firmware enforces up to 30 retries per frame. On an outdoor link during an RF fade, a single client trying to send packets can freeze the AP channel for 50–100ms. Candela Technologies (ath10k-ct) drops this down to 4 retries, which immediately reclaims a massive chunk of airtime.
2. **The Bufferbloat vs Aggregation Trap (CoTSQ):** Default Linux TCP Small Queues (TSQ = 1 ms) tries to kill bufferbloat by limiting socket queues to 1–2 packets. But 802.11ac *needs* 32 to 64 packets in the queue to build a full A-MPDU aggregate. Starving the aggregation engine drops throughput by up to 10x because 90% of the airtime is spent on PHY headers and preambles. Bumping the queue budget to 6 ms keeps aggregates full while keeping loaded ping under 40 ms.
3. **The Wave-1 Airtime Cliff:** QCA9880 doesn't have hardware airtime reporting (that only started in Wave 2 chips). So Linux mac80211 has to *estimate* airtime based on peer stats. If peer stats aren't reporting properly, mac80211 assumes EVERY station transmits at 6 Mbps, which completely breaks airtime fairness and penalizes fast clients.
4. **Why Pure TDMA is Blocked on Open QCA988x:** We looked into whether we could build open TDMA like airMAX. The short answer on QCA9880 is no—the chip runs closed Xtensa firmware, can't cancel in-flight packets across PCIe, and has PCIe interrupt jitter. BUT a hybrid stack on OpenWrt (AQL + 6ms CoTSQ + Dynamic RTS/CTS to stop hidden nodes + Deficit Round-Robin airtime fairness) gets you 80-90% of the stability with open telemetry and zero vendor lock-in.

### The Testbed Setup
I'm not doing this in a metal warehouse (metal walls act like an echo chamber with delay spreads that ruin 5 GHz tests). We're setting up:
- **Tier 1:** Benchtop SMA coaxial attenuator matrix (30–40 dB pads + splitters) for 100% clean, interference-free algorithmic sweeps.
- **Tier 2:** 2 APs on our main WISP office building pointing 21 meters across the street to 10–20 CPEs scattered on my residential roof. This gives real line-of-sight, real outdoor air, and clean far-field RF without receiver saturation.
- **Unattended Recovery:** I automated PoE injectors with relays to trigger U-Boot `urescue` TFTP recovery remotely so we never have to climb a ladder to press a reset button if an image bricks.

### Why I'm Posting
We are calling this research project **openMAX**, and we opened up the entire project as a public research hub:
https://github.com/wolverin0/openmax

There is zero monetization here, no crypto, no paid courses. Just an open repository of hardware notes, driver findings, recovery runbooks, and experiment plans.

Because this was researched with the help of AI agents, I want human eyes on this:
- If you're a kernel / OpenWrt dev who knows ath10k or mac80211, are our control boundary assumptions solid? Did we miss anything on `ratemask-CT`?
- If you're a fellow WISP operator with spare LiteBeams or NanoStations on your shelves, would you be interested in running our read-only inventory scripts to map out hardware revisions, or testing safe sysctl/CAKE queue tweaks?

Check out the repo, tear apart our docs, and let me know what you think.

---

## Option 2: Tailored for r/openwrt or r/networking

**Suggested Title:**  
*openMAX: Extracting maximum PtMP performance from QCA9880 (airMAX AC) under OpenWrt — architecture findings and call for peer review*

**Post Body:**

Hi all,

I run a fixed wireless ISP and have a huge fleet of legacy Ubiquiti airMAX AC radios (QCA9880 / AR9342 MIPS 74Kc platform). As vendor support has slowed down to favor newer proprietary silicon, we’re investigating how far this ubiquitous hardware can be pushed using OpenWrt 24.10, modern queue management, and the `ath10k-ct` driver under an open project we're calling **openMAX**.

We’ve spent the past few weeks analyzing kernel source trees (`mac80211`, `ath10k`, Candela Technologies forks), firmware binaries, and academic literature (Hassani & Leith on CoTSQ, Gringoli on paced aggregation, Høiland-Jørgensen on Airtime Fairness).

I’m an operator, not a kernel engineer, so I’ve been using LLM agents as research assistants to cross-reference code paths and preprints. To ensure we aren't chasing hallucinations or overclaiming, we established a strict verification matrix and published our findings in an open GitHub knowledge hub.

A few notable findings we’d appreciate feedback or sanity-checks on:

1. **Unicast Rate Control Boundary:**
   `ath10k` sets `HAS_RATE_CONTROL`, completely bypassing mac80211 rate controllers (Minstrel-HT does not run). Rate control is strictly firmware-owned on QCA988x. However, `ath10k-ct` exposes `ATH10K_FW_FEATURE_CT_RATEMASK` over WMI, which allows host-side supervisory rate bounding (excluding chronic high-loss MCS states for stationary CPEs).
2. **Bufferbloat vs Aggregation (Controlled TSQ):**
   Standard Linux TCP Small Queues (1 ms / 2 pkts) starves 802.11ac aggregation engines by failing to maintain 32–64 frames in the queue when a TXOP opens. Increasing the TSQ budget to 6 ms resolves the starvation, restoring 300+ Mbps TCP goodput while keeping loaded latency under 40 ms.
3. **The `last_tx_bitrate` Airtime Estimation Fallback:**
   QCA9880 Wave-1 firmware lacks `WMI_SERVICE_REPORT_AIRTIME`. Linux mac80211 must estimate airtime based on `arsta->last_tx_bitrate`, which depends entirely on `HTT_T2H_MSG_TYPE_PEER_STATS`. If peer stats drop, mac80211 defaults to assuming 6 Mbps for all frames, which degrades airtime fairness into flat packet fairness.
4. **Hardware Retry Limits:**
   Qualcomm's stock firmware enforces 30 retries (`0x1e`), which causes massive airtime starvation across outdoor sectors during momentary client fades. Candela Technologies firmware clamps this to 4 retries, significantly improving sector resilience.
5. **Memory Constraints on MIPS 74Kc:**
   Running standard `kmod-ath10k-ct` on 64MB/128MB RAM devices frequently triggers OOM panics under heavy multi-client saturation. The `kmod-ath10k-ct-smallbuffers` variant is necessary to stabilize the ring memory footprint.

We’ve documented all of this in detail along with our physical testbed layout (2 APs + 20 CPEs across a 21m building canyon, plus bench SMA attenuators) and automated TFTP `urescue` recovery scripts:
https://github.com/wolverin0/openmax

We'd love input from anyone with deep ath10k, mac80211, or fixed wireless experience:
- Has anyone successfully updated `ratemask-CT` dynamically per-peer at runtime without re-associating?
- Are there subtle race conditions in `ath10k_update_per_peer_tx_stats` under OpenWrt 24.10 that we should watch out for?

All documentation, logs, and tools are MIT-licensed and open in the repository. Feedback, critique, and PRs are very welcome.
