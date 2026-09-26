

===== TURN 1 [ASSISTANT] =====

Deep Research has started working on your briefing. It will first present its research plan, then continue with the source-anchored investigation and final report.

===== TURN 2 [ASSISTANT] =====

Not really. This Deep Research pass did not uncover “many” arXiv papers with usable real-hardware data. It was much stronger on source code, Candela/OpenWrt/kernel internals, spectral scan, aggregation, and rate-control hooks than on the academic literature.

In the finished report, the only arXiv paper it actually retained as verified real-hardware evidence for the TDMA/deterministic-MAC section was SRT-WiFi / RT-WiFi, arXiv:2203.10390, using an SDR testbed. It explicitly left timing figures for things such as hMAC, WiSHFUL/ORCA and ath9k TDMA as UNKNOWN because it hadn't verified the papers strongly enough. SRT-WiFi paper

We did already have a better academic starting set from the earlier FuturaMAX research in August. That work had surfaced real-hardware studies including PNOFA on Qualcomm 802.11ac hardware, hMAC/ath9k-hmac, WiLDNet, airtime-scheduling work such as Ending the Anomaly, aggregation/A-MPDU experiments, and ath10k timing/rate-statistics material. Importantly, those weren't all arXiv papers, and much of the hardware was ath9k, IPQ4019, SDR, etc.—not QCA988x, so they are useful primarily for techniques and experiment design rather than transferable performance numbers.

So I think there is a significant research layer still missing from what we just did: a targeted search specifically for papers with real hardware measurements, rather than another general web search. The filters should be something like: 802.11ac OR ath10k OR QCA OR TDMA OR polling OR deterministic WiFi OR airtime scheduler OR aggregation OR rate control, then require the full text to contain things such as testbed, prototype, hardware, AP model, chipset, latency percentile, throughput, microseconds, experiments, and aggressively reject simulation-only papers.

And this connects directly with the arxiv-complete dataset we were discussing: that dataset would be excellent for doing this systematically instead of hoping Google/Deep Research finds the right papers. We could search all ~3M papers for propositions like “implemented on commodity Wi-Fi hardware and measured latency”, “modified ath9k/ath10k MAC behavior”, or “real testbed with scheduled channel access”. That could easily surface papers this research pass missed.

===== TURN 3 [USER] =====

Do it so we can add it. The whole point is to Get the latest rhings people has been able to achieve with the ac /tech related the the ubiquiti a radios and chips, and take it even further with auto research method from Karpathy making automate Tests with cpes and aps to achieve even better results than the provided by ubiquiti 

===== TURN 4 [ASSISTANT] =====

Yes. This second pass materially changes the research picture. We found two 2026 results that should absolutely be added to the main report, and one of them is almost exactly the experiment architecture you were describing.

The two most important additions are:

1. August 2026: real QCA9880 spectral data at huge scale.
2. May 2026: IteRate, an autonomous AI system that actually invents, deploys, tests and iterates Wi-Fi control algorithms on real radios.

That means the idea of combining the best published 802.11ac work with a Karpathy-style autonomous physical-radio research loop is not speculative anymore. Pieces of it have now been demonstrated independently; our opportunity is to combine them on QCA988x fixed PtMP, where the physical environment is actually much easier to learn because links are stationary.

Addendum: real-hardware research we should incorporate

I am downgrading non-peer-reviewed real-hardware preprints to Tier 4 under your evidence scheme, since your Tier 3 specifically requires peer review.

Work	Finding	Evidence	Applicability to us
WiFiSpectralJam, Aug 2026	CONFIRMED — Tier 4, real-hardware preprint. A Raspberry Pi CM4 + Qualcomm Atheros QCA9880 + ath10k spectral scan produced 14.52 GB, 96,090 files and 522,771,130 ordered FFT/spectral observations, including benign RF, RF-chamber and controlled HackRF interference.	WiFiSpectralJam
	Same QCA988x Wave-1 family. Not our board and not ath10k-CT, but this is extremely strong evidence that QCA9880 spectral capture is practically useful, not merely a dormant driver feature.
RF Jamming Dataset, IEEE ComMag 2024	CONFIRMED — Tier 3. Peer-reviewed predecessor used QCA9880 + ath10k, with HT20, HT40 and VHT80 measurements. Five ML classifiers achieved >90% jamming-detection accuracy on the experimental dataset.	IEEE paper
	QCA9880 specifically. This should replace the previous report's overly cautious impression that useful Wave-1 FFT evidence was scarce.
IteRate, May 2026	CONFIRMED — Tier 4, real-hardware preprint. AI agents formulate hypotheses, generate eBPF Wi-Fi controllers, compile them, deploy them OTA, collect per-frame telemetry, analyze results and iterate without a human. Tested on 58 real nodes / five workloads; reported 21% faster page loads, 7% higher video QoE and 21% higher peak throughput versus Minstrel.	IteRate
	Hardware is MediaTek/mt76, not QCA988x. Therefore its rate-control implementation is not portable, but its autonomous-research architecture is almost exactly what we want.
ORCA / RateMan, MobiCom 2024	CONFIRMED — Tier 3. Provides kernel→userspace telemetry/control, a remote daemon, Python control, and per-station resource management on real OpenWrt radios. It uses debugfs/relayfs, precisely the architectural pattern that fits our limited AP CPU/RAM.	ORCA repository
	Existing implementation focuses on mac80211 host-controlled drivers including mt76/ath9k functionality, not a validated QCA988x solution. We should steal the architecture, not blindly port the RA implementation.
WiFi-CUTS, IEEE TCOM 2026	CONFIRMED — Tier 3. Cascaded unimodal Thompson-sampling bandits were tested on real 802.11ac. Reported ≥7%, average 15%, up to 37% throughput improvement over Minstrel-HT in medium/high-SNR shielding-box experiments; ≥18.2% OTA; and much faster initial convergence.	WiFi-CUTS metadata
	Exact test NIC is UNKNOWN from the sources I could verify. More importantly, QCA988x doesn't run Minstrel. But the bandit formulation is highly applicable to selecting rate masks / aggregation / policies around firmware RC.
2025 ORCA DQN experiments	INFERRED — Tier 6. Freifunk's GSoC work built a real AP↔STA RF-isolated testbed with a programmable RF attenuator, collected packet-level telemetry, trained DQN policies, and then deployed the policy live through RateMan.	Final GSoC report
	Community/project report, so not proof of superior performance. But its lab methodology is exactly how we should build controlled QCA988x training data.
PNOFA, 2021	CONFIRMED — Tier 3. Implemented an external frame-aggregation controller on Qualcomm IPQ4019 Wave-2 802.11ac despite closed firmware. In its tested scenarios it improved average UDP throughput 17% and TCP 13% versus Qualcomm firmware aggregation.	PNOFA paper
	Different Qualcomm chip, not QCA988x. But strategically important: closed firmware did not prevent useful outer-loop aggregation control.
Quick & Plenty, 2021	CONFIRMED — Tier 3. Real 802.11ac experiments showed that regulating offered load to maintain a target aggregation level can simultaneously suppress AP queueing and preserve throughput; one demonstrated operating point was about 2 ms one-way delay at ~500 Mb/s on a 3SS MCS9 link.	Paper
	Different hardware. The useful idea is aggregate occupancy as a feedback signal, which fits perfectly with per-CPE pacing plus AQL.
Ending the Anomaly, 2017	CONFIRMED — Tier 3. Real testbed work behind modern Linux Wi-Fi queueing showed roughly an order-of-magnitude reduction in loaded latency and near-perfect airtime fairness in its tested setup.	USENIX paper
	Already partially incorporated into our Linux-6.6 argument. It remains important as a baseline, not a new 2026 discovery.
hMAC	CONFIRMED — Tier 4, prototype/preprint. On ath9k, software TX queues were gated into TDMA-like slots while hardware CSMA/CA remained active. Published source uses configurable slots; example configuration uses 20 ms slots.	hMAC source
	ath9k only. It supports trying host-side “soft polling” eventually, but does not establish hard TDMA timing on ath10k/QCA988x.
SmartLA	CONFIRMED — Tier 3. SARSA-based link adaptation was evaluated over a 26-node 802.11ac testbed for four months, including static and mobile conditions.	SmartLA paper
	Older and chipset unspecified in the evidence retrieved, but relevant to using long-duration link history—which our fixed WISP links give us in abundance.
The two findings that change our direction most

WiFiSpectralJam changes the spectral-scan question considerably. We now have published QCA9880 data showing ath10k spectral measurements at enormous scale. The earlier report correctly identified CONFIG_ATH10K_SPECTRAL as the likely reason your entries are absent, but we can now go much further: enable spectral on our radios, reproduce their parser/features, feed their public QCA9880 dataset into our development pipeline, and then collect a Futura-specific QCA988x dataset under our antenna/front-end/channel conditions.

IteRate changes the “AI research” idea even more. Somebody has essentially demonstrated the scientific loop we were envisioning: AI → hypothesis → code → real radio → telemetry → analysis → next hypothesis. The critical difference is that IteRate controls a MediaTek radio where rate control is host-programmable. QCA988x rate control remains firmware-owned, so copying IteRate literally would be wrong. Our AI needs to optimize the control surface around firmware RC: allowed rate sets, queueing, pacing, aggregation, airtime allocation, spectral/channel policy, and potentially per-peer fixed rate once we expose that WMI primitive.

There is a minor source conflict on IteRate's exact MediaTek designation: retrieved full-text mirrors describe MT76x02/MT76x8-class hardware differently. That does not affect our applicability conclusion: it is mt76/MediaTek rather than ath10k/QCA988x.

What I think we should actually build

INFERRED — supported by IteRate + Autoresearch + ORCA: don't make the AI modify arbitrary firmware every run. Build an immutable experimental laboratory, and give the research agent a tightly constrained mutable policy.

Karpathy's Autoresearch works because prepare.py and evaluation are fixed, the agent modifies one bounded target, each run has a fixed budget, the metric is mechanically evaluated, improvements are retained and regressions reverted. Its default setup runs fixed five-minute trials and records every experiment in results.tsv.

Our equivalent should look conceptually like:

radio-autoresearch/
    program.md             # what the researcher is trying to improve

    bench/                 # IMMUTABLE to the research agent
        topology.yaml
        traffic.py
        measurement.py
        evaluator.py
        safety.py

    policy/                # MUTABLE
        controller.py
        parameters.yaml

    nodes/
        ap-agent
        cpe-agent

    knowledge/
        papers/
        prior-experiments/
        hardware-capabilities.json

    runs/
        2026-.../
            config.json
            raw-telemetry.parquet
            summary.json

    results.tsv

ORCA independently validates the idea of keeping the intelligence off the embedded radio: its remote daemon exposes high-rate telemetry/control from OpenWrt nodes to a more powerful Python controller rather than forcing Python/ML onto the AP itself.

For your 535 MHz / 64 MB AP, that is particularly attractive.

What the agent should initially be allowed to change

I would deliberately constrain the first generation to:

Per-CPE pacing / queue policy / FQ parameters.

htt_max_amsdu_ampdu within its source-verified valid range.

Rate-mask strategy, once we expose a safe per-peer interface around ratemask-CT.

Peer-fixed-rate, only if we establish that 023 advertises/supports it on our QCA988x.

Spectral-driven channel/interference policies.

AQL/queue operating point.

Driver/FW combinations as categorical experiments: CT-2024 vs CT-2026, FW022 vs FW023.

Eventually, host-side airtime credits / TXQ gating to investigate soft polling.

I would specifically exclude per-peer TX power, arbitrary retries, and unknown Wave-1 set_rate_override fields initially because the first research pass did not establish their semantics sufficiently.

And I would not let the agent use VDEV-wide set_rate_override as though it were per-CPE control.

The benchmark needs to be harder to cheat than Autoresearch

A neural-network training metric is deterministic enough that Karpathy can ask “is val_bpb smaller?”. RF is not.

For every candidate, I would run:

BASELINE A
CANDIDATE B
BASELINE A
CANDIDATE B

or randomized blocked repetitions, and preserve the complete RF/driver/environment fingerprint.

The AI doesn't get to declare itself better because one speedtest was 8 Mb/s faster.

Hard validity gates

An experiment becomes invalid/discarded if it causes firmware recovery, association loss beyond the allowed window, unacceptable packet loss, watchdog events, CPU starvation, memory pressure, or fails to reproduce the surrounding baselines.

Then among valid experiments, I would use a Pareto / lexicographic objective rather than one naïvely weighted scalar:

1. minimize loaded RTT p99
2. minimize loaded RTT p95
3. maximize worst-client / airtime fairness
4. maximize useful goodput / MHz
5. minimize wasted retry airtime
6. maximize aggregate goodput

That is much harder for an autonomous agent to game than something like:

score = throughput - 5 * latency

which could find ridiculous pathological solutions.

The first autonomous research campaigns I would run

This is the order I'd use because every stage provides information needed by the next.

QCA988x spectral reproduction. Enable ATH10K_SPECTRAL while keeping CT/FW022 otherwise constant. Parse our output with the same conceptual feature pipeline used by the QCA9880 research. Compare our distributions with the published QCA9880 datasets. Then build our own labelled corpus with real WISP interference. The 2024/2026 QCA9880 literature gives us an unusually good external validation target.

Aggregation AutoResearch. Let the system autonomously sweep and then learn policies around A-MPDU/A-MSDU limits under different subscriber counts, RSSIs, rate distributions and traffic mixes. PNOFA shows that outer-loop control can outperform proprietary Qualcomm firmware aggregation even when the aggregation implementation itself is closed. Do not transfer its +17/+13% numbers to QCA988x.

Aggregation-aware pacing. Instead of blindly filling queues, learn the offered-load level at which each station retains enough aggregation efficiency without entering persistent queues. Quick & Plenty provides real-hardware evidence for precisely this throughput/latency tradeoff.

Per-subscriber rate-envelope bandit. Don't try to replace QCA firmware RC. Let it select packet rates, but have our outer controller choose the allowed rate mask. A fixed link might learn that MCS 8/9 cause enough retransmission airtime that banning them increases aggregate goodput and lowers p99. WiFi-CUTS strongly supports bandits as a candidate search method, but its Minstrel performance numbers cannot be carried over.

Contextual rate-envelope controller. Add subscriber history: distance, RSSI distribution, noise, retries, previous goodput, time-of-day interference, spectral features. SmartLA and the more recent learning work establish real-hardware precedent for learning from historical channel observations, though not on our chipset.

Weak-client / near-far experiments. One excellent client + one poor client, then 4, 8, 16 clients. Have the agent search queue, mask and aggregation policies that minimize p99 and airtime waste rather than allowing a weak station to consume disproportionate airtime.

Interference-aware control. Add known adjacent-channel and co-channel interferers in a shielded/cabled environment; correlate FFT signatures with packet retries and actual goodput. Ultimately let the controller predict whether it is better to stay, narrow/widen, or change channel. QCA9880 spectral-jamming work proves this feature space is ML-usable.

Only then: soft scheduled access. Experiment with per-station TXQ admission/credits and queue gating. hMAC proves that software queue gating can create hybrid slotting on ath9k, but because QCA988x firmware still owns final transmission/CSMA timing, we should call this soft scheduling, not TDMA, until measurements prove otherwise.

The particularly interesting twist with your WISP

INFERRED: your problem may actually be friendlier to autonomous optimization than IteRate's.

IteRate has ordinary changing Wi-Fi environments. Your stations are fixed installations. Their distance does not change, antennas normally do not move, topology is known, and you can accumulate weeks/months of per-CPE history.

So instead of asking:

“What rate should I use for an arbitrary station right now?”

we can learn things like:

“CPE 7 at 4.3 km with this RSSI/noise/retry/spectral history performs best when firmware is prohibited from MCS 8–9 during this interference regime, receives this airtime budget, and is paced to this queue/aggregation operating point.”

That's much closer to per-link system identification than generic Wi-Fi rate adaptation.

And because we control both AP and CPE, the agent can correlate observations from both ends, something most of this research cannot do.

A very important correction to our earlier research

The earlier report said, in effect, that there was no strong QCA988x real-hardware spectral literature in hand.

That gap is now REFUTED.

There is:

a peer-reviewed 2024 IEEE paper using QCA9880 + ath10k spectral measurements, including HT20/HT40/VHT80 and controlled RF conditions;

and an August 2026 QCA9880 dataset containing over 522 million spectral observations.

That should be explicitly corrected in the master research document.

Likewise, our earlier strategic section should now include IteRate because it is probably the closest published system to your proposed “Karpathy Autoresearch, but the training environment is a bunch of physical APs and CPEs.”

Where this leaves the project

The resulting architecture is more interesting than simply writing a “better scheduler” once:

                      PAPER KNOWLEDGE
               QCA988x + WiFi research
                         │
                         ▼
                AUTONOMOUS RESEARCHER
             hypothesis → experiment
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
        AP control               CPE control
     queues / masks            telemetry / load
     aggregation                measurements
     spectral scan                  │
             │                       │
             └───────────┬───────────┘
                         ▼
                   REAL RF LINK
                         │
                         ▼
                  RAW TELEMETRY
                         │
                         ▼
       p99 / fairness / airtime / goodput/MHz
                         │
                    keep / discard
                         │
                         └────────► next hypothesis

INFERRED: this is now the direction I would prioritize over trying immediately to reverse-engineer and reproduce Ubiquiti's 2017 polling firmware. The published work gives us enough exposed levers to first determine experimentally how far QCA988x can be pushed without replacing the radio firmware at all.

Only when AutoResearch repeatedly hits a measurable firmware-owned ceiling do we have a scientifically defensible reason to attack the Xtensa firmware.

And that would be a much better outcome than guessing where the limit is: we'd have thousands of controlled experiments telling us exactly which missing primitive is holding us back.

===== TURN 5 [USER] =====

If youd have to estimate according to all advance entes and findings and tunnings, how much better if theoretically accurate, would we gain in network performance? 

===== TURN 6 [ASSISTANT] =====

If I had to put numbers on it today, using the real-hardware results we’ve now found and discounting heavily for the fact that most papers are not QCA988x, I would set the project target around this:

~20–40% more usable PtMP capacity in the same spectrum, while reducing loaded p95/p99 latency by roughly 5–10×.

And in particularly ugly cells—mixed rates, weak CPEs, congestion, bad aggregation choices, interference—I think 50%+ improvement in useful carried traffic is plausible, with 10×+ tail-latency improvements possible. I would not expect 50–100% higher clean single-client speedtest throughput.

That distinction is critical.

My estimated envelope
Metric vs current airOS/stock scheduling	Conservative	Realistic target	Exceptional/pathological case
Peak single-CPE throughput	0–5%	5–10%	~15%
Loaded aggregate PtMP goodput	+10%	+20–40%	+50–80%
Goodput/MHz	+10%	+20–35%	+50%+
p95 loaded latency	2–3× lower	4–8× lower	10×+
p99 loaded latency	3× lower	5–10× lower	10–20×+
Fairness / weak-client isolation	noticeable	very large	transformative
Retry/wasted airtime	−5%	−10–25%	−30%+
Interference resilience	small on clean channel	+10–30% usable capacity during interference	potentially much larger in avoidable interference
Extra gain from autonomous search over good manual tuning	2–5%	5–15%	20%+ in specific regimes

Those are INFERRED engineering targets, not published QCA988x results. I would use them to decide whether the project is worth pursuing, not advertise them as measured results.

Why I think +20–40% usable capacity is defensible

There are several independent places where we're leaving performance on the table.

1. Queueing + airtime scheduling alone can be enormous

The Linux airtime-fairness work demonstrated an order-of-magnitude reduction in latency under load, near-perfect airtime fairness, and—in deliberately bad mixed-rate scenarios—aggregate throughput improvements up to 5×.

I absolutely would not predict 5× for FuturaMAX.

That experiment exposes how bad the pathological ceiling can be. Our reasonable expectation should be much lower.

But it strongly supports expecting something like:

100–300 ms p99 → 10–40 ms

rather than expecting:

250 Mbps → 1,250 Mbps.

Latency and consistency are where modern queueing pays disproportionately.

2. Aggregation alone has already given ~13–17% on closed Qualcomm firmware

PNOFA is especially interesting because it wasn't replacing the entire Qualcomm MAC.

They put an external controller around Qualcomm's closed firmware on an IPQ4019 802.11ac device and measured:

+17% UDP

+13% TCP

from better aggregation decisions.

Different Qualcomm silicon, therefore we cannot transfer those numbers directly to QCA988x.

But suppose we eventually get only half of that.

That's already ~6–9% useful throughput coming from one knob family.

And our objective is broader:

aggregation
+ queues
+ airtime allocation
+ pacing
+ rate envelopes
+ interference intelligence

The gains overlap, so we don't add them arithmetically, but there is clearly room.

3. Better rate decisions have repeatedly produced ~15–20% class improvements

The new WiFi-CUTS experiments on real 802.11ac hardware report an average 15% improvement, at least 18.2% OTA, and up to 37% under some tested conditions over Minstrel-HT.

Again:

we cannot run that algorithm directly, because QCA988x owns RC in firmware.

But our idea is actually slightly different.

Instead of telling QCA:

transmit this exact packet at MCS 6

we tell it:

For CPE-17, based on three weeks of observations, don't even consider MCS 8–9 right now.

And then let Qualcomm RC operate inside that safer envelope.

For fixed wireless, that could work extremely well because the station does not suddenly walk behind a concrete wall like a phone does.

The stationary CPE property is a huge advantage

This is the part I think is easy to underestimate.

A normal Wi-Fi controller needs to deal with:

user walks around
orientation changes
device moves
antenna changes
people obstruct path
roaming
battery behavior
hundreds of device models

We instead have:

CPE-381
distance = 6.82 km
antenna = fixed
azimuth = fixed
AP sector = fixed
hardware = known
historic RSSI = known
historic retries = known
historic MCS behavior = known
historic noise = known
weather/time correlations = learnable
interference profile = learnable

So the controller can eventually discover something very specific like:

CPE 381

Day:
MCS allowed 4–7
aggregation target 37
queue target 2.8 ms
airtime weight 0.83

18:00–23:00:
MCS allowed 3–6
aggregation target 29
airtime weight 0.91

When spectral classifier sees interferer class #4:
ban MCS 7
reduce aggregation
raise pacing constraint

That is a radically different problem from generic Wi-Fi.

Where the 5–10× latency estimate comes from

Quick & Plenty demonstrated real 802.11ac operation around 2 ms one-way latency at ~500 Mbps by deliberately maintaining enough queued data for aggregation without creating a persistent backlog.

And the Linux Wi-Fi queueing work measured about an order of magnitude reduction in loaded latency.

These two ideas are complementary:

don't starve aggregation → don't overfill the radio queue.

The old-school behavior is basically:

MORE QUEUE
   ↓
more packets ready
   ↓
good aggregation
   ↓
nice throughput benchmark
   ↓
300 ms latency

The intelligent version is:

just enough backlog
        ↓
efficient A-MPDU
        ↓
little persistent queue
        ↓
high goodput + low latency

That is probably one of our highest-value targets.

Example with an actual WISP sector

Imagine a 40 MHz AP currently behaves like this under evening traffic:

25 associated CPEs
15 active

Aggregate useful traffic:      220 Mbps
p95 latency under load:         85 ms
p99:                           210 ms

Weak CPE:
30% retry airtime

Fast CPE:
sometimes waits behind weak station

Speedtest with one CPE:
310 Mbps

I would consider this a credible FuturaMAX outcome:

Same AP
Same QCA988x
Same channel
Same bandwidth
Same antennas

Aggregate useful traffic:      275–310 Mbps
p95:                            15–25 ms
p99:                            25–50 ms

Weak CPE:
more appropriate rate envelope
less wasted airtime

Fast CPE:
isolated TXQ
proper airtime scheduling

Single-client speedtest:
320–335 Mbps

So the salesperson looking only at Speedtest says:

“You gained 6%.”

But the operator has gone from:

220 → 300 Mbps usable cell capacity

and:

210 → 35 ms p99.

That's a 36% capacity improvement and ~6× tail-latency improvement.

That is a vastly better network.

And then spectrum intelligence adds something different

The QCA9880 spectral work we found matters here.

If our AP can continuously understand:

noise floor
interference occupancy
spectral shape
co-channel patterns
adjacent-channel energy
temporal interference

the optimizer can stop treating:

RSSI = -62

as sufficient knowledge about the link.

Two CPEs both at −62 dBm could have dramatically different optimal policies.

So imagine:

Sector A:
channel 5660
80% busy during evening
good RSSI
high retry rate

A naïve optimizer might start screwing with rates.

Our controller could learn:

PHY isn't the problem. Interferer X appears every ~4 ms on this channel.

And change channel/policy instead.

I wouldn't count this as a permanent +20%. On a clean POP it may give effectively zero throughput improvement.

On an interference-limited POP, it could be one of the biggest improvements.

That's why I put ~10–30% during meaningful interference rather than claiming it across the network.

AutoResearch is the multiplier, but not in the obvious way

IteRate's autonomous system produced, versus Minstrel:

21% faster webpage loads

7% higher video QoE

21% higher peak throughput

on its 58-node experimental environment.

I'm less excited about its exact 21% than about how it got there.

Imagine we have 10 meaningful controls, each with only 5 useful settings.

That's:

5¹⁰ = 9,765,625 combinations.

No network engineer is going to systematically test that space.

And ours isn't even static because policies can depend on:

subscriber
signal
traffic load
time
interference
retry rate
queue depth
aggregation state

AutoResearch doesn't magically make the PHY faster.

It finds combinations a human would never bother testing.

That's why I'd estimate an additional 5–15% beyond a well-engineered manually tuned FuturaMAX stack, rather than something silly like another +50%.

Where I think the ceiling probably sits

Without replacing Qualcomm firmware:

Level 1 — modern Linux stack
AQL
per-STA TXQs
FQ
airtime fairness
proper shaping

I would expect the biggest latency/fairness transformation here.

Level 2 — QCA-specific outer control
aggregation
rate masks
retry behavior where controllable
telemetry
per-link policies

This is where I'd expect another meaningful ~10–20% efficiency opportunity in difficult PtMP conditions.

Level 3 — learned controller
subscriber history
contextual policies
spectral state
automatic experimentation

Potentially another 5–15%, but primarily by finding regimes where static policies fail.

Level 4 — actual custom scheduled MAC

If eventually we reverse-engineer/replace enough QCA firmware to perform genuine deterministic AP polling:

UNKNOWN.

I deliberately would not include any performance gain for this in today's estimate.

It could be the thing that gets us substantially beyond the 20–40% envelope.

Or the offload architecture could make it not worth the engineering.

We need experiments.

So if you force me to give you one number

For a loaded real-world Futura WISP PtMP cell, once this project is mature:

~30% more useful network capacity

would be my central engineering estimate.

With simultaneously:

~5–10× better p99 loaded latency

and substantially better client-to-client fairness.

I would set project success thresholds roughly like this:

MINIMUM SUCCESS

+10–15% usable aggregate capacity
≥3× reduction in p99 latency
material improvement in fairness
VERY GOOD RESULT

+25–40% usable capacity
5–10× lower p99
10–25% less wasted airtime
excellent weak-client isolation
BREAKTHROUGH

+50% or more usable PtMP capacity
while keeping latency low
and without consuming additional spectrum

If we reach that last category without modifying the QCA988x radio firmware, then we have extracted an extraordinary amount from this hardware.

And the particularly interesting possibility is that we could use the autonomous test system across real deployed sectors as well as the lab, so every sector gradually becomes experimental evidence feeding better policies back into the stack. That is where I think this could ultimately become much more than “OpenWrt on Ubiquiti.”

If you want, I can:

Outline initial autonomous research steps

Describe the proposed experiment architecture

Detail the criteria for experiment validity and evaluation metrics
