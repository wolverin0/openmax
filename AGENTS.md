# FuturaMAX Project Guide

## 1. Mission

FuturaMAX is an R&D project to determine how much additional real-world performance, spectral efficiency, PtMP capacity, latency stability, fairness, and operational intelligence can be extracted from existing Ubiquiti airMAX AC hardware through software, firmware, drivers, MAC behavior, scheduling, rate control, aggregation, queueing, RF optimization, telemetry, and automated experimentation.

This project does NOT attempt to turn 802.11ac hardware into Wi-Fi 6/7 or add PHY capabilities the silicon does not possess.

Primary hardware:
- Ubiquiti LiteAP GPS / LAP-GPS APs
- LiteBeam 5AC Gen2 CPEs
- NanoStation 5AC / Loco 5AC CPEs

LTU is outside the main scope.

The central question is:

> What is the best fixed-wireless system this existing AC hardware can physically execute when optimized specifically for stationary outdoor PtMP links, known topology, known distances, known plans, historical per-CPE behavior, and control of both AP and CPE?

## 2. Engineering principles

Never assume:
- airOS is optimal.
- OpenWrt is automatically better.
- AI automatically beats Ubiquiti.
- losing airMAX TDMA is acceptable.
- a paper's reported gain transfers directly to QCA988x.
- a knob is controllable until verified on the exact hardware.

Every important claim should be labeled:
- CONFIRMED
- INFERRED
- UNKNOWN
- REFUTED

The goal is not to prove FuturaMAX beats airMAX. The goal is to discover the truth.

A hybrid outcome that keeps airMAX TDMA while adding better telemetry, queueing, spectrum intelligence, pacing, optimization, and per-CPE control is a valid success.

## 3. Current research baseline

Treat these as starting assumptions to verify experimentally.

High confidence:
- LiteBeam 5AC Gen2 and important LiteAP AC-family revisions use an AR9342-class host with a QCA988x-class 5 GHz radio.
- OpenWrt supports important devices in this family.
- ath10k communicates with QCA98xx firmware through WMI/HTT.
- substantial MAC/rate behavior is firmware-offloaded on QCA988x.
- standard ath10k does not expose the same direct host-controlled per-frame unicast rate selection as ath9k/minstrel.
- modern mac80211 provides per-station TXQ, airtime scheduling, FQ mechanisms, and AQL.
- QCA988x exposes spectral FFT data through ath10k.
- QCA988x coverage-class support can program slot/ACK/CTS timing.
- Ubiquiti publicly described airMAX AC as using proprietary TDMA acceleration/custom silicon at the platform level.
- ordinary OpenWrt does not reproduce airMAX TDMA or GPS sync by configuration alone.

Unknowns that must be measured:
- exact airMAX accelerator role in LAP-GPS/LBE/Loco revisions.
- exact LAP-GPS OpenWrt target/revision requirements.
- queue depth hidden below mac80211/ath10k.
- accuracy and timing resolution of MCS/retry/TX-completion telemetry.
- direct control of A-MPDU length.
- usefulness and speed of per-peer rate-mask updates.
- per-peer TX-power control.
- usable CSI extraction.
- bounded host-triggered TX timing.
- access to LAP-GPS timing under OpenWrt.
- ability of an open/custom stack to match airMAX under hidden-node PtMP load.

## 4. Non-goals and hard safety boundaries

Do not:
- implement AX/BE-only PHY features.
- bypass firmware signatures or secure boot.
- copy proprietary airMAX code.
- defeat licenses or access controls.
- disable DFS or regulatory controls.
- exceed legal EIRP.
- modify calibration/ART/factory/MAC-address partitions.
- flash production radios before lab recovery is proven.
- optimize only speedtest while materially worsening p95/p99 latency or stability.

Protected by default:
- bootloader
- calibration/ART
- factory data
- MAC-address storage
- board-data partitions

Every flash workflow must include:
- exact board/image matching
- size validation
- checksum
- health check
- watchdog
- power-cycle recovery
- TFTP/bootloader recovery or equivalent
- post-boot rollback path

## 5. Repository structure

Preferred structure:

futuramax/
├── FUTURAMAX_PROJECT_GUIDE.md
├── docs/
│   ├── CURRENT_STATE.md
│   ├── HARDWARE_MATRIX.md
│   ├── QCA988X_CONTROL_BOUNDARY.md
│   ├── RESEARCH_LEDGER.md
│   ├── EXPERIMENTS.md
│   └── DECISIONS.md
├── inventory/
│   ├── board_probe/
│   ├── flash_map_validator/
│   └── calibration_hash/
├── firmware/
│   ├── openwrt/
│   ├── patches/
│   ├── profiles/
│   └── build/
├── telemetry/
│   ├── airos/
│   ├── ath10k/
│   ├── queue_trace/
│   └── spectral_fft/
├── workloads/
│   ├── bulk/
│   ├── interactive/
│   ├── mixed/
│   ├── near_far/
│   └── hidden_node/
├── orchestration/
│   ├── power/
│   ├── deploy/
│   ├── rollback/
│   └── matrix/
├── analysis/
│   ├── metrics/
│   ├── statistics/
│   ├── regression_gate/
│   └── reports/
├── controller/
│   ├── models/
│   ├── spectrum/
│   ├── optimizer/
│   └── api/
└── safety/
    ├── protected_partitions/
    ├── regulatory/
    └── recovery/

## 6. Source-of-truth hierarchy

When sources conflict:

1. measurements from our exact hardware revision
2. source code for the exact build
3. official hardware/driver documentation
4. peer-reviewed real-hardware research
5. upstream mailing-list discussions
6. simulations
7. community reports

Never convert inference into fact silently.

## 7. Experiment methodology

Every experiment must contain:
- experiment ID
- hypothesis
- exact hardware revision
- firmware/build hash
- configuration snapshot
- topology
- channel/width/EIRP
- attenuation/RF conditions
- offered-load trace
- primary metric
- secondary metrics
- repetitions
- treatment order/randomization
- rollback condition
- result
- confidence interval
- decision: KEEP / REJECT / INCONCLUSIVE

Core metrics:
- aggregate goodput
- per-CPE goodput
- goodput/MHz
- airtime per delivered bit
- MCS/NSS distribution
- retries/PER
- aggregate size/duration when observable
- p50/p95/p99 latency
- jitter
- packet loss
- Jain fairness
- CPU/RAM
- firmware resets
- reassociation time
- recovery after power loss

No performance claim is valid without repeatable physical measurements.

## 8. Development stages

### Stage 0 — Research operating system

Build first:
- hardware inventory
- reproducible build system
- recovery tooling
- telemetry
- workload generation
- experiment orchestration
- statistics
- regression gates
- automatic rollback

Do NOT start with a custom MAC.

### Stage 1 — Stock-airOS intelligence

Keep airMAX intact and add:
- per-CPE telemetry/history
- CAKE/FQ-CoDel at POP/core
- traffic pacing
- chain-imbalance diagnosis
- capacity forecasting
- spectrum history
- channel/width/power optimization
- advisory mode
- canary changes
- causal before/after analysis

### Stage 2 — OpenWrt observability lab

On isolated spare units:
- reproducible OpenWrt build
- upstream ath10k
- ath10k-ct comparison
- debugfs/tracepoints
- spectral FFT
- coverage-class timing
- TXQ/AQL
- queue visibility
- fixed-rate/rate-mask tests

### Stage 3 — Algorithmic improvements

Only after proving the control hook:
- adaptive A-MPDU
- per-CPE learned MCS/rate constraints
- retry-policy experiments
- adaptive RTS/CTS
- hidden-node detection
- CCA experiments in contained RF conditions
- slow-loop power/channel/width control
- cross-layer controllers

### Stage 4 — Custom MAC feasibility gate

Before TDMA, prove:
1. precise TX completion visibility
2. bounded lower-layer queue ownership
3. bounded TX release timing
4. AP/CPE clock synchronization
5. controllable ACK/retry interaction
6. management/beacon survival
7. safe missed-slot recovery
8. usable GPS/timing access if required

If these fail, do not force a custom MAC.

### Stage 5 — Custom PtMP MAC

Only if Stage 4 passes:
- centralized polling
- demand-based slots
- airtime-cost scheduling
- contract-aware scheduling
- latency deadlines
- dynamic DL/UL
- GPS-aligned sectors
- propagation-aware timing

## 9. Highest-priority candidate techniques

Immediate / Tier S:
- per-CPE telemetry
- CAKE/FQ-CoDel
- pacing
- modern AQL/TXQ
- fixed-rate characterization
- rate-mask characterization
- coverage-class timing
- spectral FFT
- persistent spectrum database
- conflict-graph frequency planning
- joint channel/width/power optimization
- automated experiment loop
- rollback/recovery automation

Tier A:
- adaptive A-MPDU
- per-CPE learned rate model
- adaptive RTS
- hidden-node classifier
- measured-airtime correction
- interference classifier
- predictive channel selection
- contract-aware airtime scheduling

Moonshots:
- custom demand-based TDMA
- propagation-aware TDD
- custom GPS-aligned sectors
- deep QCA988x firmware work

## 10. First ten experiments

FMX-0001 — Board/revision inventory  
FMX-0002 — Repeated boot/recovery qualification  
FMX-0003 — Stock airMAX single-CPE baseline  
FMX-0004 — Stock airMAX 8-CPE mixed-MCS baseline  
FMX-0005 — Stock airMAX hidden-node baseline  
FMX-0006 — airOS + external CAKE/FQ-CoDel/pacing  
FMX-0007 — OpenWrt single-CPE baseline  
FMX-0008 — OpenWrt AQL/TXQ enabled vs disabled  
FMX-0009 — QCA988x fixed-rate/rate-mask authority  
FMX-0010 — QCA988x FFT capture and classifier validation  

## 11. First Codex implementation backlog

P0:
- create repository skeleton
- create hardware inventory schema
- create experiment schema
- implement board_probe
- implement flash_map_validator
- implement calibration/factory hash tool
- implement metrics schema
- implement experiment runner
- implement reproducible report generator
- implement protected-partition rules

P1:
- airOS telemetry collector
- OpenWrt telemetry collector
- smart power-cycle controller
- health checks
- rollback workflow
- iperf3/netperf/Flent orchestration

P2:
- ath10k debugfs/trace collector
- TXQ/AQL metrics
- spectral FFT parser
- fixed-rate/rate-mask tooling
- QCA988X_CONTROL_BOUNDARY.md

P3:
- spectrum/conflict-graph optimizer
- per-CPE model framework
- adaptive controllers

## 12. AI/Codex operating method

Codex is an engineering agent, not an oracle.

For every significant change:

HYPOTHESIS
→ CONTROL BOUNDARY / ASSUMPTION
→ MINIMAL CHANGE
→ INSTRUMENTATION
→ TEST
→ RESULT
→ KEEP / REJECT / INCONCLUSIVE
→ DOCUMENT

Rules:
- inspect before editing
- make one primary wireless change at a time
- add telemetry with the change
- never invent hardware results
- if hardware is unavailable, build the harness/fixture/parser needed for the next test
- update CURRENT_STATE.md, RESEARCH_LEDGER.md and DECISIONS.md after meaningful work
- explicitly say whether behavior belongs to:
  - external controller
  - Linux
  - mac80211
  - ath10k
  - QCA firmware
  - hardware
  - proprietary airMAX component
  - UNKNOWN

## 13. Definition of success

Any of the following can justify FuturaMAX:
- repeatable 10–20%+ aggregate-goodput improvement on representative sectors at equal/better latency and stability
- very large loaded-latency reductions with negligible goodput loss
- materially better goodput/MHz
- more subscribers at the same QoE
- better spatial reuse
- significantly better automatic diagnosis and spectrum planning

Do not add gains from unrelated papers together.

Only our own reproducible benchmarks can support final claims.

## 14. Session protocol

At the start of every Codex session:
1. read this file
2. read docs/CURRENT_STATE.md
3. read docs/DECISIONS.md
4. read docs/RESEARCH_LEDGER.md
5. inspect repository status and recent commits
6. continue from the highest-priority unblocked milestone

At the end of every session:
1. update CURRENT_STATE.md
2. update RESEARCH_LEDGER.md
3. record architectural decisions
4. list exact next experiments/tasks
5. identify any physical user action needed
6. leave the repository in a reproducible state
