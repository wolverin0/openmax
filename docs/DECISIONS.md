# FuturaMAX architectural decisions

Summary: durable decisions and their rationale, newest first. Required by AGENTS.md §14.
Keywords: decisions, ADR, custom firmware, OpenWrt, Stage 0, Stage 2, scope correction,
Cambium Elevate, retraction, autoresearch, D-0009. Read when: you are about to re-open a settled question, or need
to know why the project is shaped the way it is.
Current verdict: CUSTOM FIRMWARE project on OpenWrt 24.10.4/ath79, now running on the lab
LAP-120; install = dd-unlock (D-0007/8); Stage 3 = autonomous research loop with firmware work
deferred until a measured ceiling (D-0009). Status: CURRENT (2026-09-26).

## D-0013 — 2026-09-27 — Core Production Subsystems: Partition Safety, Cryptographic ART Hasher, Full-Spectrum Telemetry, and Autonomous Recovery Gates

**Decision.** Formally adopt and deploy the 20 core production software engines satisfying AGENTS.md §11 (P0/P1 Backlog) and §4 (Safety Envelope), verified by 66 unit tests passing across 19 suites:

1. **Hardware Safety & Flash Protection**:
   - `safety/protected_partitions/validator.py`: Enforces zero-trust partition immutability (`mtd0`, `mtd1`, `mtd4`, `mtd5`), 15.008 MB flash ceiling, and uImage header integrity.
   - `inventory/flash_map_validator/flash_validator.py`: Verifies MTD memory maps against canonical 16 MB SPI-NOR maps, pins 64 KB ART/EEPROM to `0x00ff0000`, and rejects out-of-bounds writes.
   - `inventory/calibration_hash/art_hasher.py`: Verifies 64 KB ART/EEPROM cryptographic SHA-256 hashes, extracts factory MAC addresses, and detects calibration drift or erased flash.
   - `inventory/board_probe/probe.py`: Automated fingerprinting parser extracting SoC, RAM, flash map, radio PCI ID (`168c:003c`), ath10k firmware release (`10.2.4-ct`), and GPS status.
   - `safety/recovery/health_check.py`: Non-invasive post-flash health monitor auditing kernel dmesg (oops, ath10k firmware crashes), RAM headroom (> 8 MB free), and interface readiness.

2. **Full-Spectrum Telemetry Collection**:
   - `telemetry/ath10k/debugfs_collector.py`: Parses `htt_tx_stats`, mac80211 AQL queues (`aql_tx_pending` vs `aql_limits`), and station dumps (`iw dev wlan0 station dump`), tracking instantaneous retries, discard rates, and chain imbalances.
   - `telemetry/airos/collector.py`: Collects and normalizes airOS `/status.cgi` and `wstalist` telemetry (airMAX TDMA polling quality/capacity, remote RSSI, CINR, airtime allocation) to enable 1:1 cross-stack comparisons.
   - `telemetry/spectral_fft/parser.py`: RelayFS TLV binary unpacker and sub-millisecond FFT classifier (23.4 µs/sample).

3. **Optimization, Spectrum, and Models**:
   - `controller/spectrum/conflict_graph.py`: Collocated sector conflict graph optimizing channel/width/power for APs at 21m rooftop canyon separation, avoiding DFS radar and adjacent interference.
   - `controller/models/cpe_history.py`: Stationary outdoor CPE profiler computing FSPL, theoretical vs measured RSSI, alignment tilt/foliage attenuation, and initial MCS ceilings.
   - `controller/optimizer/rate_bandit.py`: ADR-Bandit supervising `ratemask-CT` with Page-Hinkley drift detection.

4. **Workloads, Gating, and Orchestration**:
   - `workloads/traffic_generator.py`: Synthetic traffic generation for bulk DL/UL, interactive 60 pps, and mixed near-far streams.
   - `workloads/flent_orchestrator.py`: Multi-CPE benchmark orchestrator parsing iperf3 JSON and ping RTT distributions (p50/p95/p99) and Jain fairness.
   - `analysis/regression_gate/gatekeeper.py`: Autonomous A/B/A/B evaluator enforcing Decision D-0009 with Welch's t-test statistical significance.
   - `analysis/metrics/schema.py`: AGENTS.md §7 compliant metrics schema with JSON serialization.
   - `analysis/reports/generator.py`: Standardized markdown and JSON audit report generator for `/clawd/reports/`.
   - `orchestration/matrix/cabled_matrix_runner.py`: Tier 1 benchtop SMA attenuation matrix test runner mapping distance to FSPL.
   - `orchestration/power/smart_power.py`: Smart power-cycle controller with cool-down guards and PoE remote-reset pulsing for unattended u-boot TFTP recovery.
   - `orchestration/rollback/workflow.py`: Two-tier automated rollback manager (Tier 1 soft SSH sysupgrade -> Tier 2 hardware PoE TFTP push).

Reference: `docs/CURRENT_STATE.md`, `AGENTS.md` §11.

---

## D-0012 — 2026-09-26 — Formal Queueing & Contention Models: CoTSQ Aggregation Sizing, ath10k-ct SRAM Cache Locking, and RTS/CTS Vulnerability Shrinkage

**Decision.** Formally adopt the analytical queue and contention optimization models, driver/kernel WMI/HTT hooks, and Bianchi Markov collision adaptations derived in `knowledge/ANALYTICAL_QUEUE_MODEL_AND_HOOKS.md` (synthesizing the PraisonAI autonomous research report `knowledge/PRAISONAI_AQL_RESEARCH_REPORT.md`):

1. **Controlled TSQ (CoTSQ) Sizing ($6\text{ ms}$ Airtime)**: 
   Standard Linux TCP Small Queues (`tcp_limit_output_bytes = 128\text{ KB} / 1\text{ ms}`) starves 802.11ac physical aggregation engines, restricting A-MPDU depth to $K \le 8$ ($\eta \approx 48.7\%$). We adopt CoTSQ calibrated to $T_{target} \approx 6\text{ ms}$ at 400 Mbps (`net.ipv4.tcp_limit_output_bytes = 300000`, `net.ipv4.tcp_notsent_lowat = 16384`), unlocking $K \ge 32$ ($\eta \approx 81.6\%$) and boosting goodput by $+67.5\%$ without inducing bufferbloat.
2. **Firmware Rate-Control Cache Depth Locking (`num_rate_ctrl_objs_ct = 24`)**: 
   Source verification of `ath10k-ct` (`mac.c:201`) confirmed that target firmware defaults to caching only 32 rate-control objects in on-chip SRAM. For 10–20 active CPE associations under bidirectional streams, the target continuously evicts and swaps rate objects over the PCIe bus, destabilizing the rate-hunting algorithm. We lock `num_rate_ctrl_objs_ct = 24` via module parameters to ensure all 20 CPE link states remain resident in target SRAM.
3. **Driver Ring Descriptors & HTT Aggregation Hooks**:
   Driver-level MSDU descriptors (`num_msdu_desc_ct`, `htt_tx.c`) and HTT aggregation message `HTT_H2T_MSG_TYPE_AGGR_CFG` (`ath10k_htt_h2t_aggr_cfg_msg()`) are identified as the canonical supervisory interfaces, controllable via debugfs `/sys/kernel/debug/ieee80211/phyX/ath10k/htt_max_amsdu_ampdu`.
4. **Bianchi Hidden-Node Contention Adaptation**: 
   Directional outdoor PtMP exhibits an asymmetric interference graph where CPEs cannot hear peer transmissions ($>110\text{ dB}$ path loss between subscriber dish antennas). Without RTS/CTS, collision vulnerability equals the entire data frame duration ($V_{DATA} \approx 3200\,\mu\text{s}$), causing exponential Aloha throughput collapse ($S_{CSMA} < 10\text{ Mbps}$) for $N \ge 8$ stations. Enabling hardware RTS/CTS with threshold $= 512\text{ bytes}$ shrinks the vulnerability window to $V_{RTS} \approx 65\,\mu\text{s}$ (a $98.0\%$ reduction), maintaining aggregate saturation goodput $>175\text{ Mbps}$ across 20 CPEs.
5. **Experimental Recipes Codified**:
   Recipes FMX-0013 (CoTSQ sweep), FMX-0014 (Rate-control cache depth), FMX-0015 (mac80211 AQL tuning), and FMX-0016 (20-CPE RTS/CTS protection) are codified in `docs/EXPERIMENTS.md`.

Reference: `knowledge/ANALYTICAL_QUEUE_MODEL_AND_HOOKS.md`, `knowledge/PRAISONAI_AQL_RESEARCH_REPORT.md`.

---

## D-0011 — 2026-09-26 — Multi-LLM Debate Consensus: Split-Plane Shaping Architecture, CPU Boundary, and Uplink Go/No-Go Gate

**Decision.** Formally adopt the unanimous consensus from the 3-way frontier AI architecture debate (Claude Fable 5.1, OpenAI Codex GPT-6 Astra, Google Gemini 3.8 Flash; transcript: `debates/001-openmax-qca9880-ptmp-optimizat/`):
1. **Split-Plane Shaping Architecture (CPU Boundary Enforcement)**: The AR9342 MIPS 74Kc (533–600 MHz) cannot sustain line-rate CAKE shaping or research telemetry without CPU starvation and ksoftirqd livelock. Downlink CAKE must be offloaded to an external x86/ARM gateway router upstream of the AP. The AP runs native `ath10k` AQL with driver-level `fq_codel`.
2. **CPE Uplink Protection**: CPEs must NOT run heavy CAKE. OpenWrt CPEs run lightweight token-bucket filters (`tc-tbf`) on egress to bound local queue build-up before RF entry, combined with aggressive hardware-assisted RTS/CTS thresholds (scaled down for >5 active stations) to mitigate hidden-node collisions.
3. **Firmware Authority & Host Rate Clamping**: QCA9880 firmware retains exclusive microcode control over per-frame rate stepping and A-MPDU packing. Host mac80211 control is strictly macroscopic: setting per-station MCS rate ceilings, AQL airtime deficits, and queue weights.
4. **Discarded Non-Goals**:
   - **Soft-Poll / U-APSD Pseudo-TDMA**: Discarded unanimously; station power-save triggers introduce latency jitter and framing overhead without granting contention-free uplink TXOPs.
   - **On-box MIPS CAKE**: Discarded due to hardware limits.
   - **Premature Custom TDMA Firmware**: Discarded until empirical CSMA failure gates are proven.
5. **Decisive Go/No-Go Gate**: 20-CPE saturated reverse-mode (`iperf3` uplink + `irtt` 20 pps) under manufactured hidden-node geometry. OpenWrt must achieve p99 loaded RTT < 150 ms and aggregate goodput within 25% of stock airOS TDMA to validate open CSMA viability.

Reference: `debates/001-openmax-qca9880-ptmp-optimizat/synthesis.md`.

---

## D-0010 — 2026-09-26 — Multi-node testbed RF environment: cabled matrix + distributed layout, no warehouse

**Decision.** Do NOT lease a warehouse for the 2 AP + 20 CPE laboratory. Multi-station PtMP testing on 802.11ac hardware in an enclosed metal space introduces severe multipath reflections (delay spread), alters Fraunhofer antenna formation ($R < 2D^2/\lambda$), and saturates receiver LNAs (> -20 dBm). We adopt a **hybrid cabled RF attenuation matrix + multi-room building layout**:
1. **Tier 1 (Benchtop Coaxial Matrix)**: For algorithm, aggregation (`htt_max_amsdu_ampdu`), and queue/rate-mask testing, connect radios via SMA coax through fixed 30-40 dB attenuators and Wilkinson power splitters. Delivers 100% deterministic, interference-free link simulation from 100m to 10km without moving physical hardware.
2. **Tier 2 (Multi-Room OTA Fleet)**: For spatial fairness and hidden-node testing, remove dish reflectors (bare feed horns drop gain by ~18 dB), lock TX power to minimum (-4 dBm to 0 dBm), and distribute CPEs across rooms/floors behind drywall and concrete partitions.
3. **Automated Remote Recovery**: Deploy relay-switched PoE remote reset (pulsing DC offset on Ethernet data pairs during boot) and software `bootcmd=urescue` overrides to achieve unattended TFTP recovery on all 22 radios without physical button manipulation.

Reference: `docs/TESTBED_ENVIRONMENT_GUIDE.md`.

---

## D-0009 — 2026-09-20 — Stage 3 method: autonomous radio research (bench immutable, policy mutable)

**Decision.** FuturaMAX's Stage 3 ("algorithmic improvements", AGENTS.md §8) is executed as an
**autonomous research loop over real radios**, not as hand-tuning: a research agent proposes a
bounded policy change, an *immutable* bench runs it against a fixed evaluator with blocked A/B/A/B
repetitions, hard validity gates discard broken runs, a lexicographic objective ranks the survivors,
and improvements are kept while regressions revert. Operator-directed (share 6ab032a5, turn 3:
*"take it even further with the auto-research method from Karpathy, automated tests with CPEs and
APs"*). This is AGENTS.md §9 Tier-S "automated experiment loop" and §12's HYPOTHESIS→…→KEEP/REJECT
made operational — a reshaping *inside* the constitution, not a new goal.

**Precedents (see `knowledge/REAL_HARDWARE_LITERATURE.md`, all independently verified).**
- **IteRate** (arXiv:2605.02542, MIT, May 2026) demonstrated the full loop on 58 real Wi-Fi nodes.
  Its hardware (mt76) has host-owned rate control; ours does not. **We copy the loop, not the
  controller.**
- **ORCA/RateMan** (MobiCom 2024) validates keeping the intelligence *off* the embedded radio —
  mandatory on a 535 MHz / 64 MB AP.
- **Karpathy's Autoresearch** supplies the discipline: fixed `prepare`/evaluator, one bounded
  mutable target, fixed budget per run, mechanical metric, every run logged.

**Structure adopted.**
```
radio-autoresearch/
  program.md            # what the researcher is trying to improve
  bench/                # IMMUTABLE to the agent: topology, traffic, measurement, evaluator, safety
  policy/               # MUTABLE: controller.py, parameters.yaml
  nodes/                # ap-agent, cpe-agent
  knowledge/            # papers, prior experiments, hardware-capabilities.json
  runs/<id>/            # config, raw telemetry, summary
  results.tsv
```

**What the agent may change in generation 1 — deliberately narrow.** Per-CPE pacing/queue/FQ
parameters · `htt_max_amsdu_ampdu` within its source-verified range · rate-mask strategy once a
safe per-peer `ratemask-CT` interface exists · peer-fixed-rate *only if* FW023 is shown to
advertise it on our QCA988x · spectral-driven channel/interference policy · AQL operating point ·
driver/FW combinations as categorical arms (CT-2024 vs CT-2026, FW022 vs FW023) · later,
host-side airtime credits / TXQ gating for **soft** scheduling.
**Excluded until semantics are established:** per-peer TX power, arbitrary retries, unknown Wave-1
`set_rate_override` fields. The agent must never treat VDEV-wide `set_rate_override` as per-CPE
control (`QCA988X_CONTROL_BOUNDARY.md` §4c).

**Why the benchmark must be harder to cheat than Autoresearch.** A training loss is deterministic;
RF is not. Every candidate runs as BASELINE-A / CANDIDATE-B / A / B (or randomised blocks) with the
full RF/driver/environment fingerprint preserved. One faster speedtest is not a result.

**Hard validity gates** (a run is discarded, not scored): firmware recovery, association loss beyond
the allowed window, unacceptable loss, watchdog events, CPU starvation, memory pressure, or failure
to reproduce the surrounding baselines.

**Objective — lexicographic, not a weighted scalar** (a scalar like `throughput − 5·latency` invites
pathological optima): 1 min loaded RTT p99 · 2 min loaded RTT p95 · 3 max worst-client / airtime
fairness · 4 max goodput/MHz · 5 min wasted retry airtime · 6 max aggregate goodput.

**Consequence for the custom-MAC question (D-0003).** Radio-firmware (Xtensa) work is **deferred**
until the loop repeatedly hits a *measured* firmware-owned ceiling. Thousands of controlled runs
telling us exactly which primitive is missing is a better reason to attack the firmware than
guessing. The Stage 4 gate stays UNKNOWN, as AGENTS.md §8 requires.

**Targets, labelled honestly.** The research wave's envelope — *central estimate ~30% more usable
loaded PtMP capacity with ~5–10× lower p99, and only ~5–10% on a clean single-client speedtest* —
is recorded in `EXPERIMENTS.md` as **INFERRED engineering targets** derived from other silicon.
AGENTS.md §13: only our own reproducible benchmarks can support final claims. These numbers decide
whether the project is worth pursuing; they are never to be advertised as measured.

---

## D-0008 — 2026-08-08 — REFUTED: urescue will not accept the OpenWrt image. Route C is dead.

**Result (Grade A, from the device itself).** The LAP-120's bootloader **rejects** the OpenWrt
`ubnt_lap-120` factory image. Full 7,013,016 B / 13,698 blocks were transferred into urescue via
TFTP; on the final block the bootloader replied with a TFTP ERROR:

> `code=2  msg='Firmware check failed'`

**Nothing was written.** The unit stayed in urescue with airOS 8.5.12 intact in flash — confirming
the *other* prediction (D-0007): this bootloader validates in RAM before touching flash, so a
refused image costs nothing. Reproduced twice, identically.

**What this refutes.** D-0006/D-0007 recorded, as INFERRED-strong, that the bootloader's string
table containing `OPEN` beside `UBNT`/`PART`/`END.` meant urescue would *accept* an `OPEN`-magic
image. **That inference is now REFUTED.** Recognising a magic is not accepting an image: this
bootloader (U-Boot 1.1.4-**s1100**, Sep 2018) also carries `RSA Signed Image. Verifying please
wait…` / `Signature authentication failed`, and enforces that check on the urescue path.
The label was doing real work — the claim was never promoted to fact, and the experiment that
settled it cost one refused upload and zero risk.

**Scope note, important for the fleet.** This is the *later* s1100 bootloader. Community reports
of urescue-flashing OpenWrt onto WA boards may predate it. Do not assume other units in the fleet
behave the same — the bootloader build, not the model, is what decides.

**Consequence.** Route C (urescue-only install) is dead for this unit. The install must come from
*inside* airOS, where the signature gate is in `ubntbox` (patchable) rather than in a signed
bootloader. Route B is now the only compliant path: derive the 8.5.12 patch offset by
disassembling the `EVP_VerifyFinal` caller in the pulled `ubntbox`. Route A stays withdrawn
(writes u-boot; no serial, no case access, no fallback — D-0007).

**urescue is not wasted.** It remains proven as the *recovery* path for signed vendor images, and
that is what it is for: it is how a bad airOS state gets restored. It simply cannot be the
install vector.

---

## D-0007 — 2026-08-08 — SUPERSEDES D-0006's install route: urescue-only; dd-unlock WITHDRAWN
### ⚠️ Route C (urescue install) subsequently REFUTED by D-0008 — recovery role unaffected

**Decision.** Install OpenWrt on the lab LAP-120 by pushing the **factory** image through the
bootloader's `urescue` TFTP server (Route C). **Route A (dd-unlock) is withdrawn.** Recovery is
not rehearsed beforehand; it is *exercised* by the install, with the stock airOS image as the
rollback pushed through the identical path.

**Why D-0006's install route was wrong.** dd-unlock requires letting stock `fwupdate` write
**`u-boot` to `mtd0`** before interrupting it — the wiki's own instruction is to Ctrl-C *after*
`Writing 'u-boot ' to /dev/mtd0 … [%100]`. That violates AGENTS.md §4 ("never write bootloader"),
and D-0006 shipped a runbook whose hard-boundary section forbade what its primary route did.

**The constraint that makes it unrecoverable, not merely non-compliant** (operator, 2026-08-08):
**no serial console, and the case will not be opened.** A failed or power-interrupted u-boot write
destroys `urescue` itself, and the last-resort SPI-clip rescue needs the case open. So Route A is
the one procedure here with *no* fallback. Any route that writes u-boot is off the table for this
unit, permanently — not just deprioritised.

**Why no separate recovery rehearsal.** D-0006/runbook rev 1 proposed proving recovery by pushing
stock airOS onto a healthy unit first. That is ceremony: it spends a flash cycle and a site visit
re-proving a mechanism that is standard across Ubiquiti hardware and that the install then
exercises anyway. Replaced by (a) a **zero-write urescue entry check** (`urescue_push.py
--probe-only`) — because the genuinely uncertain step on a no-serial unit is whether the operator
can reach urescue *blind*, not whether urescue works — and (b) treating the install as the proof.

**Why trying Route C is safe.** This unit's bootloader validates before writing: two separate
calls, `go ${ubntaddr} ucheck_fw …` then `go ${ubntaddr} uupdate_fw …`, with TFTP landing the
image in RAM at `ubntaddr=0x80200020`. A refused image means nothing was written and the unit is
still on airOS 8.5.12. CONFIRMED for the call sequence (pulled u-boot); INFERRED that no erase
precedes the check. Refusal is therefore a cheap, informative negative — and is itself a valid
FMX-0002 result (it would mean signed-bootloader enforcement extends to urescue on WA boards).

**Credit where due.** The operator caught both errors by asking whether the plan was testing the
universally-proven mechanism or changing something and then rescuing it. Both halves were right.

---

## D-0006 — 2026-08-08 — LAP-120 install/recovery method
### ⚠️ install route SUPERSEDED by D-0007 — do not cite "dd-unlock is primary"

**Decision.** Install OpenWrt on the lab LAP-120 via the **dd-unlock** route (stock unpatched
`fwupdate.real` unlocks the flash on a validly-signed stock airOS image; interrupt after `u-boot`
is written; `dd` the OpenWrt sysupgrade to `mtdblock2`/`mtdblock3`). Recover via the bootloader's
own **`urescue` TFTP server**. Patched-`ubntbox` + factory image is the fallback, not the primary.

**Why dd-unlock over the patched-fwupdate route.** The published `ubntbox` patch is version-
specific (`14 40 fe ff` / `fe fe` / `fe 27`). I pulled this unit's actual 8.5.12 `/bin/ubntbox`
(read-only) and **none of the three patterns exist in it** — the wiki's "won't work for other
versions" warning, confirmed empirically. Reusing a published pattern would be a guess; deriving a
new one needs disassembly. dd-unlock never presents an unsigned image to fwupdate, so the whole
signature question is moot. This is the wiki's own recommended method for airOS 8.5.7+.

**Why urescue is the recovery anchor.** Confirmed present in the pulled live u-boot 1.1.4-s1100
(`urescue - start TFTP server and wait for firmware`), with fixed recovery IP 192.168.1.20. It
lives in the bootloader, so it survives a failed OS flash — the AGENTS.md §4 debrick guarantee.
Host-side push tool: `safety/recovery/urescue_push.py` (validates image magic + sha256 before
sending). Full runbook: `safety/recovery/FMX-0002_recovery_runbook.md`.

**Method for reaching this decision (matters for trust).** Every wiki claim was cross-checked
against artifacts read read-only from the exact unit — not accepted from the page alone. The
read-only probe (`inventory/board_probe/preflash_probe.py`) has an enforced write-primitive guard
and a "0 associated stations" abort so it can never run against a production radio.

**What is NOT yet decided / done.** FMX-0002's *demonstration* — physically power-cycling into
urescue and reflashing — is an operator action and remains open. Whether `urescue` accepts the
OpenWrt *factory* image directly (a urescue-only install) is INFERRED-strong from the bootloader's
`OPEN` magic-table entry and will be settled on serial during the recovery dry-run. No flash has
occurred; the unit is untouched at airOS 8.5.12 baseline.

---

## D-0005 — 2026-08-08 — Cambium Elevate is closed and irrelevant

**Decision.** Stop treating Elevate as a reference point. Two reasons, the second decisive:

1. **Factually inapplicable** — Elevate covered M-series (802.11n) only, never AC-generation
   radios (operator, 2026-08-08).
2. **Structurally irrelevant** — Elevate's only value was as an existence proof that a
   non-vendor stack can run on Ubiquiti hardware. **OpenWrt already does that on our exact
   devices**, with official profiles. A precedent is unnecessary for something we can boot.

**Correction to my own prioritisation.** I had listed "verify Elevate's AC coverage" as the
top open research question. It was not: the answer changes no decision. This is the same class
of error as citing a competitor's closed system when an open one is already in hand.

---

## D-0004 — 2026-08-08 — Scope correction: FuturaMAX is a custom firmware, not airOS tuning

**Decision.** All work targets building a custom firmware/software stack for airMAX AC
hardware. Configuration tuning of stock airOS is **out of scope** except where it produces a
measurement baseline (AGENTS.md Stage 1 explicitly permits airOS-preserving intelligence, but
that is a parallel track, not the goal).

**Why this needed stating.** An earlier session spent substantial effort probing and modifying
`/tmp/system.cfg` on airOS units — discovering the `cfgmtd` write path and 62 undocumented
`radio.*` keys. Interesting, and largely beside the point. The operator's framing:

> "we researched so much about new things test improvements of the AC chipsets/hardware, not
> to fine tune the Ubiquiti firmware"

The research corpus exists to find techniques worth **implementing in our own stack**. Tuning
the vendor's config file cannot deliver a 2017-frozen scheduler's replacement.

**Consequences.**
- `knowledge/AIROS_CONTROL_SURFACE.md` is demoted to a baseline/reference artifact. Its
  hidden-key finding stays recorded — it is real and may inform Stage 1 — but it is not a path.
- The `radio.*` hidden-key experiments (G25, G28, G29 follow-ons) drop in priority.
- Stage 2 (OpenWrt observability lab) becomes the active line of work.

---

## D-0003 — 2026-08-08 — RETRACTED: the custom-MAC "NO-GO"

**Decision.** The earlier NO-GO verdict is withdrawn. `knowledge/CUSTOM_MAC_GO_NO_GO.md`
returns to **UNKNOWN**, where AGENTS.md §8 requires it to stay until the eight Stage 4
criteria are measured.

**Why it was wrong.** It asked "can we replicate airMAX *on stock firmware*?" — never the
question. Finding Ubiquiti's scheduler inside their proprietary radio firmware describes what
*their* firmware does; it does not bound what *ours* can do. It also pre-empted a gate the
constitution defines as measurement-driven, using string analysis instead.

**Aggravating factor.** All control-boundary probing was done on **airOS**, which is the wrong
stack to evaluate. The Stage 4 criteria are properties of an OpenWrt/ath10k system.

**What replaces the verdict.** Nothing, yet — and that is correct. The gate is measured on
OpenWrt at Stage 2, not argued from firmware archaeology. See D-0005 for why no external
precedent is needed to justify proceeding.

---

## D-0002 — 2026-08-08 — OpenWrt 24.10.4 / ath79-generic is the custom-firmware vehicle

**Decision.** Build FuturaMAX on OpenWrt 24.10.4 (`ath79/generic`, Linux **6.6.110**).

**Rationale.**
- **Every target device has an official profile**: `ubnt_lap-120`, `ubnt_litebeam-ac-gen2`,
  `ubnt_nanostation-ac-loco`, `ubnt_nanostation-ac`, `ubnt_rocket-5ac-lite`,
  `ubnt_powerbeam-5ac-gen2`, `ubnt_rocket-5ac-lite`.
- The lab unit is a **LAP-120**, which maps exactly to `ubnt_lap-120` — factory and sysupgrade
  images both exist.
- Kernel 6.6 carries the entire body of post-2017 mac80211 work the research corpus is about:
  AQL, airtime fairness, per-station TXQ, FQ-CoDel. airOS runs **2.6.32** — a 2009 kernel.
  This is the single largest lever the project has and it comes free with the platform.
- It is a real build system: we can patch mac80211/ath10k and produce reproducible images.

**Rejected alternatives.**
- *Patch airOS* — no source, 2.6.32 kernel, signed images, and the scheduler is in firmware.
- *Write firmware from scratch* — no QCA target SDK; not reachable.
- *ath10k-ct as the base* — still an option **within** OpenWrt; deferred to a Stage 2
  comparison (upstream ath10k vs ath10k-ct) rather than decided now.

**Status.** Images downloaded and SHA-256 verified against OpenWrt's `sha256sums`:
`firmware/openwrt/openwrt-24.10.4-ath79-generic-ubnt_lap-120-squashfs-{factory,sysupgrade}.bin`.
**Not yet flashed** — recovery must be proven first (AGENTS.md §4).

---

## D-0001 — 2026-08-08 — AGENTS.md is the constitution; the handoff was a lossy summary

**Decision.** `AGENTS.md` (installed at repo root, byte-identical to
`FUTURAMAX_PROJECT_GUIDE.md`) is the primary source of truth. The
`handoffs/handoff-2026-08-08T12-57-03-a63934.md` R0–R9 research pipeline is **historical
context**, not the plan.

**Why.** The handoff omitted: that the goal is a custom firmware, the Cambium Elevate
precedent, the Stage 0–5 structure, the FMX-0001…0010 experiment list, the P0 implementation
backlog, and the repository layout. Working from it produced a research-evidence system when
the constitution asks for an experiment operating system.

**Consequence.** Repository restructured to the AGENTS.md §5 layout. Prior research artifacts
are retained under `research/` and `knowledge/` as inputs, not as the deliverable.
