
# openMAX Physical-Boundary Research Report  
## QCA988x/Peregrine programmability, hidden interfaces, firmware, information capacity, external measurement, and autonomous experimentation

**Evidence freeze:** 2026-10-24  
**openMAX repository snapshot reviewed:** commit `0cce9cf76d990861fbd8a78d1f9dfa357df5b369` (2026-10-23)  
**Exact Qualcomm-derived AR9888/Peregrine source snapshot used:** `SpaceExplorationTechnologies/starlink-wifi@1d585ee8909bf7bab4391c0c52d8a9d44137b3bb`  
**Linux source snapshot used:** `torvalds/linux@5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f`  
**Primary hardware scope:** Ubiquiti QCA9882/QCA988x hw2.0 Wave-1 devices on WA/XC platforms.  
**Cross-chip rule:** facts from QCA9888, QCA9984, IPQ4019, ath9k, ath11k/12k, MediaTek, Intel, Broadcom, SDR, or FPGA are explicitly marked and are never silently transferred to QCA988x.

---

## How to read this report

Each material conclusion is tagged:

- **CONFIRMED** — exact source code, exact-family descriptor/register evidence, firmware-binary evidence, or openMAX hardware measurement.
- **INFERRED** — supported by architectural lineage or cross-chip implementation, but not proven on QCA9880/QCA9882.
- **UNKNOWN** — the public evidence does not establish the answer.
- **REFUTED** — contradicted by exact-family evidence.

Source IDs such as `[Q11]` resolve to full URLs in **Source ledger**. A claim that depends on multiple facts carries multiple source IDs. Performance numbers are not transferred across chipsets.

---

# 1. Executive findings — direction-changing only

1. **CONFIRMED — QCA988x/Peregrine has an internal baseband channel-capture path.** The exact `AR9888/v2` RX descriptor contains `bb_captured_channel`, documented as indicating that the baseband captured a channel dump that firmware can read from “channel dump memory.” The matching TX descriptor exposes `bb_capture_channel`, which requests capture for a good RX packet. This is the strongest newly identified route to CSI/channel-matrix data on the exact architecture. It does **not** prove that stock ath10k exports the memory, nor establish its address or format. `[Q11][Q12]`

2. **CONFIRMED — exact-family RX metadata is substantially richer than normal ath10k exposes.** The same descriptor family carries per-pilot/per-stream EVM fields, TSF and sub-microsecond-related timestamps, `txbf_h_info`, baseband-debug length, and capture status. The current practical boundary is therefore at least partly an export/firmware/datapath boundary, not a demonstrated absence of measurements in silicon. `[Q11][R16]`

3. **REFUTED — “TDMA/polling is locked out by the hardware” is too strong.** Ubiquiti’s exact-family target images contain and execute proprietary AP/STA/PTP polling logic, with role-specific QCA target binaries and proprietary WMI commands. The correct claim is: **normal ath10k host APIs do not expose the target scheduler**. `[R19][R20][R03]`

4. **CONFIRMED — a public Qualcomm-derived tree contains exact-family factory/test firmware source and an explicit `TARGET=AR9888` build path.** The Makefiles select `utf`, `utfsetup`, calibration, test-command, WMI host-interface, and device libraries for AR9888/Peregrine. This is not the production WLAN target source, and this investigation did not yet reproduce a complete build; it is nevertheless exact-family target code rather than a later-chip analogy. `[Q01][Q02][Q03]`

5. **CONFIRMED — the exact AR9888 UTF/TCMD surface is broad.** It includes continuous TX/RX, frame/TX99/TX100/sine/offset-tone modes, RX/PER/EVM statistics, direct register access, OTP/eFuse operations, PAPRD/DPD/calibration, chain masks, scrambler/AIFS/aggregation controls, and 5/10 MHz half-/quarter-rate modes. These are factory/test primitives; they are not automatically safe or available in production firmware. `[Q03][Q04][Q05][Q06]`

6. **UNKNOWN — raw time-domain ADC capture on QCA988x remains unresolved.** Qualcomm’s shared TLV2 command set defines `ADCCAPTURE` with a 2048-complex-sample response and `GENWAVEFORM` with a 2048-complex-sample response. However, both are behind an extended-command build path, and a Peregrine-specific implementation/registration has not yet been located. `GENWAVEFORM` accepts a waveform index, not host-supplied arbitrary IQ samples. `[Q07][Q09][Q10]`

7. **CONFIRMED — production TX descriptors expose only standard OFDM/HT/VHT rate encodings.** The exact `series_bw` layout selects preamble, standard MCS/rate, NSS, LDPC, STBC, SGI, chain mask, TPC, PPDU duration, symbol count, and aggregation parameters. No arbitrary constellation identifier or programmable FEC polynomial appears in this descriptor. That is strong negative evidence against a trivial “hidden MCS11/4096-QAM bit,” but not proof that no deeper baseband table exists. `[Q13]`

8. **INFERRED — QCA988x is best modeled as a firmware-orchestrated, hardware-accelerated 802.11 PHY, not as a hidden general SDR.** Exact-family register maps show many parameterized baseband blocks—AGC, channel/pilot masks, timing, correlation thresholds, LDPC scaling/latency, FFT scaling, DC/IQ calibration—but the public interfaces overwhelmingly select/configure fixed hardware functions. No evidence was found for host-defined subcarrier constellations, arbitrary pilot sequences, arbitrary FFT sizes, or arbitrary TX sample streaming. `[Q14][Q13][Q03]`

9. **CONFIRMED — modifying target firmware is physically feasible; an open reproducible production build is not yet available.** Ubiquiti ships multiple role-specific modified targets for the exact family, and Candela Technologies states that it modified Qualcomm Wave-1 target firmware obtained under NDA. openMAX has extracted and structurally decoded Ubiquiti SGMT images, but has not yet demonstrated a clean-room rebuild and safe deployment of a modified production target. `[R13][R19][C01]`

10. **CONFIRMED — deterministic sub-millisecond scheduling cannot be assumed from Linux/user-space control.** hMAC shows useful queue gating on ath9k with coarse slots while preserving hardware CSMA; SRT-WiFi obtains approximately microsecond-class synchronization and ~100–200 µs slots by putting timers, queues, and TX triggering in FPGA logic. For QCA988x, the high-value path is target-firmware/PCU timing, not pretending that WMI/Netlink is a real-time air interface. `[P09][P10][R18]`

11. **CONFIRMED — the highest-probability performance headroom is MAC/firmware policy, not a novel PHY.** openMAX has already measured meaningful gains from RTS/CTS in a hidden-node uplink case, while the exact family proves target-owned scheduling, retry/rate/aggregation and rich CCA/test controls. These are reachable before arbitrary waveform capability is established. `[R02][R04][R07][R08][R19]`

12. **POSSIBLE/UNKNOWN — internal 2×2 channel-capacity estimation may be achievable without replacing the radio.** The exact channel-dump/H-info path could expose per-tone complex channel information. If it cannot be exported, a phase-coherent dual-channel SDR can estimate the 2×2 channel from 802.11 training fields independently. `[Q11][Q12][Q15][E03][T02]`

13. **CONFIRMED — full 80 MHz, 2×2 observation requires equipment above B210/bladeRF-class bandwidth.** A B210 supplies two coherent channels but only up to 56 MHz real-time bandwidth; X310-class systems with suitable wideband daughterboards or N320/N321-class systems can cover 80 MHz with margin and two channels. A calibrated WLAN vector signal analyzer remains the metrology reference for EVM. `[E01][E02][E03][E06]`

14. **CONFIRMED — openMAX’s autonomous-science layer must be corrected before it is allowed to select winners.** The current metrics schema derives `goodput_per_mhz` using a hard-coded 40 MHz denominator; the gatekeeper’s stated p99→p95→fairness→goodput hierarchy is not fully implemented, treats A/B/A/B blocks as independent groups, uses very small samples, and does not explicitly model temporal RF drift or repeated-search multiplicity. An autonomous optimizer would otherwise optimize a mis-normalized/noisy objective. `[R23][R24]`

15. **UNKNOWN — the ordinary 802.11ac boundary may ultimately be the real silicon boundary.** The decisive tests are now well-defined: channel-dump activation, exact UTF feature enumeration, ADC/sample-memory verification, one safe target-firmware modification, and mapper/FEC/pilot table discovery. If those gates fail under exact-family evidence, openMAX should treat the PHY as standard 11ac and concentrate on scheduler/policy/measurement rather than continue speculative hidden-mode searches. `[Q11][Q13][Q14]`

---

# Repository-derived baseline: what is already settled

The repository is not a speculative bring-up project. At the reviewed snapshot it contains a working OpenWrt 24.10/Linux 6.6/ath10k-CT path, production-like sector operation, multi-vendor AP/CPE interoperability, reversible airOS8 comparison and rollback methods, spectral capture, adaptive-controller infrastructure, and extensive WA/XC/LTU reverse engineering. `[R01][R02][R06][R07][R08][R09][R10][R11][R12]`

Material existing results that this report treats as settled unless contradicted:

| Existing result | Status here | Why it matters | Evidence |
|---|---|---|---|
| AC/N/AP coexistence and multi-vendor PTMP operation are real | **CONFIRMED** | openMAX already has a heterogeneous physical testbed, not a synthetic topology | `[R02][R06]` |
| RTS/CTS materially improved one simultaneous hidden-node uplink workload | **CONFIRMED, workload-specific** | proves MAC-policy headroom; not transferable as a universal gain | `[R02][R04]` |
| WMI rate-mask dispatch can succeed while live reassociation ignores the intended restriction | **CONFIRMED** | host command success is not proof of target actuation | `[R08][R03]` |
| Spectral capture is operational | **CONFIRMED** | useful interference oracle, but spectral FFT bins are not CSI | `[R02][R16]` |
| Forced AP scan can produce a persistent sawtooth fault requiring PCIe reset | **CONFIRMED** | scanning/testmode requires hard safety interlocks | `[R02][R04]` |
| Stock airOS8 interoperability and rollback are practical | **CONFIRMED** | enables controlled A/B against the proprietary scheduler | `[R09]` |
| Ubiquiti target binaries contain role-specific polling functions and WMI opcodes | **CONFIRMED** | proves target-firmware scheduling on the same architecture | `[R19][R20]` |
| LTU uses a different AD9361/FPGA/dual-SoC architecture | **CONFIRMED** | 4096-QAM/OFDMA evidence from LTU must not be transferred to QCA988x | `[R11]` |
| Current host lacks exact Wave-1 airtime telemetry and target scheduler control | **CONFIRMED for the current stack** | motivates target/descriptor instrumentation | `[R03][R21]` |

## Corrections to older or overly broad project conclusions

| Prior formulation | Corrected formulation | Label | Evidence |
|---|---|---|---|
| “TDMA is blocked by hardware.” | Normal ath10k lacks the scheduler interface; exact-family Ubiquiti target firmware executes proprietary polling. | **REFUTED as stated** | `[R19][R20]` |
| “QCA988x has no CSI.” | Production ath10k exports no CSI API, but exact AR9888 descriptors define channel-dump capture and TXBF H-info paths. Activation/export remain unknown. | **REFUTED as a silicon claim** | `[Q11][Q12][R16]` |
| “There is no public target firmware source.” | No public production WLAN target source is known, but exact AR9888 factory/test target source is public. | **REFUTED as stated** | `[Q01][Q02][Q03]` |
| “Spectral data can substitute for CSI.” | Spectral data estimates energy versus frequency/time; it does not recover the per-stream complex channel matrix. | **REFUTED** | `[R16][T02]` |
| “A payload pattern or CW mode implies arbitrary waveform generation.” | Payload bytes enter the standard PHY; CW/sine/test-tone modes are fixed generators. No host-IQ injection is established. | **REFUTED** | `[Q03][Q05][Q10]` |



# 2. QCA988x programmability map

## Best publicly supportable block diagram

```text
Antenna / Ubiquiti FEM / filters / AirPrism (XC)
        │
        ▼
RF PA/LNA/mixers/PLL ── ADC/DAC ── digital front end / calibration
        │
        ▼
packet detect / AGC / CCA / correlators / timing / channel estimation
        │
        ▼
FFT/IFFT / OFDM framing / pilots / equalizer / MIMO / STBC / beamforming
        │
        ▼
mapper-demapper / BCC-Viterbi / LDPC / interleaver / scrambler
        │
        ▼
PCU/OLE/crypto / retry series / aggregation / Block ACK / TSF / queues
        │
        ▼
Xtensa target firmware: scheduler, rate control, peer state, calibration,
WMI service dispatch, HTT datapath, timers, recovery and debug
        │
        ▼
Copy Engines / PCIe ── ath10k / mac80211 / Linux ── host policy & userspace
```

“Owner” below means the component that appears to make the time-critical decision, not the only component that can configure it.

| Component | Apparent current owner | Programmability class | Known interface/evidence | Certainty | openMAX opportunity |
|---|---|---|---|---|---|
| Ubiquiti antenna, filters, PA/LNA and external FEM | Fixed board hardware; GPIO/filter state may be host/target controlled | Fixed analog topology; calibrated gains/switches | XC board/AirPrism reverse engineering; AR9888 radio/calibration code `[R10][Q03][Q06]` | **CONFIRMED** for board topology; exact analog limits partly **UNKNOWN** | Measure real linearity/noise figure/EVM; optimize legal power/filter-state policy, not topology in software |
| RF synthesizer, mixers and transceiver analog | RF hardware plus target calibration | Parameterized hardware | Channel setup, gain indices, PAPRD/DPD, NF and thermal test controls in UTF `[Q03][Q04][Q05]` | **CONFIRMED** | Calibration experiments; characterize power/EVM/PAPR trade-off |
| ADC/DAC | Fixed converters with calibration/control | Fixed hardware; calibration parameterized; sample access unknown | IQ/ADC calibration registers; common `ADCCAPTURE` ABI; fixed test tones `[Q09][Q14][Q03]` | Converter existence/control **CONFIRMED**; raw sample capture on AR9888 **UNKNOWN** | Highest-value hidden-interface gate; establish sample RAM and capture route |
| Digital front end | Baseband hardware configured by target | Parameterized hardware | Enable-DFE/common TLV command; DC/IQ, slope, magnitude, weighting and filter controls `[Q07][Q14]` | **CONFIRMED** for controls; algorithms mostly **UNKNOWN** | Controlled impairment compensation; likely not replaceable with arbitrary DSP |
| FFT/IFFT | Baseband hardware | Fixed accelerator with limited parameters | FFT-scaling control and standard bandwidth/rate modes `[Q14][Q03]` | **CONFIRMED** parameterized block | Prove supported width/timing combinations; no evidence for arbitrary FFT size |
| OFDM framing and preambles | PCU/baseband hardware, selected by descriptor/firmware | Standard-template selection | `preamble_type`, PPDU duration/symbol count and VHT/HT fields in exact descriptors `[Q13]` | **CONFIRMED** | Scheduler can choose frame structure/aggregation; novel preambles not established |
| Subcarrier mapping | Baseband hardware | Apparently fixed standard mapping | Standard MCS descriptor and channel/pilot mask controls, no arbitrary subcarrier map found `[Q13][Q14]` | Standard mapping **CONFIRMED**; deeper LUT **UNKNOWN** | Search BB RAM/register tables; otherwise treat as fixed |
| Pilot generation | Baseband hardware | Standard pilot generation with tracking/masking controls | pilot-tracking and pilot-spur-mask fields `[Q14]` | **CONFIRMED** parameterization; arbitrary pilot values **UNKNOWN** | Debug/estimation tuning; learned pilots blocked absent a writable pilot table |
| Constellation mapper/demapper | Baseband hardware | MCS-indexed fixed modes on known TX path | exact rate field enumerates legacy/HT/VHT BPSK through VHT MCS9/256-QAM `[Q13]` | **CONFIRMED** for normal descriptor | Search hidden mapping RAM; no present basis for nonuniform QAM or 1024/4096-QAM |
| Channel estimation | Baseband hardware; firmware can request/read debug capture | Parameterized hardware plus hidden capture | `bb_capture_channel`, `bb_captured_channel`, channel-dump memory and TXBF H-info `[Q11][Q12]` | **CONFIRMED** primitive; format/export **UNKNOWN** | Top priority: recover per-tone H/CSI and rank/eigenvalues |
| Equalizer | Baseband hardware | Fixed accelerator with debug/parameter controls | EVM fields, channel/equalizer-related BB controls, H-info path `[Q11][Q14]` | **INFERRED/CONFIRMED by adjacent exact fields** | Export equalizer/channel state; learned equalizer replacement not currently reachable |
| AGC | Baseband hardware | Heavily parameterized | exact AGC control, NF, calibration and gain tables; UTF gain controls `[Q14][Q03]` | **CONFIRMED** | Safe shielded search over thresholds/gain policy; guard against saturation/desense |
| CCA and energy detection | Baseband hardware configured by target | Parameterized | UTF writes CCA thresholds and OFDM/self-correlator/find-signal thresholds `[Q03][Q14]` | **CONFIRMED** | High-value PTMP interference/hidden-node experiments; must preserve regulatory behavior |
| Packet detection and preamble correlators | Baseband hardware | Parameterized | exact timing/correlation thresholds and false-alarm controls `[Q03][Q14]` | **CONFIRMED** | Adapt false-alarm vs sensitivity policy in controlled conditions |
| BCC encoder / Viterbi decoder | Baseband hardware | Fixed code family; decoder parameters | traceback-depth/fine-timing controls and standard MCS coding selections `[Q14][Q13]` | **CONFIRMED** | Tune decoder parameters; no evidence for new convolutional polynomial |
| LDPC encoder/decoder | Baseband hardware | Fixed 11n/ac LDPC with scaling/latency parameters | descriptor LDPC selection; exact LLR-scaling and latency controls `[Q13][Q14]` | **CONFIRMED** | Validate when LDPC helps actual links; new LDPC matrices not established |
| Interleaver/deinterleaver | Baseband hardware | Apparently fixed by PHY mode | implied by standard HT/VHT hardware datapath; no writable table found `[Q13]` | **INFERRED** exact family | Search register/RAM symbols; assume fixed until evidence |
| Scrambler | Baseband hardware with test/firmware control | Parameterized seed/test behavior | UTF exposes scrambler controls/pattern modes `[Q03][Q04][Q05]` | **CONFIRMED** | Test instrumentation; not a capacity breakthrough by itself |
| MIMO spatial mapping | Baseband hardware | NSS/chain/beamforming modes parameterized | exact NSS, chain mask, STBC and TXBF descriptor fields `[Q12][Q13]` | **CONFIRMED** | Rank-aware policy if channel data recovered |
| STBC | Baseband/PCU | On/off per transmission | exact descriptor and UTF controls `[Q04][Q13]` | **CONFIRMED** | Link-specific reliability/airtime policy |
| Beamforming-related hardware | Baseband SVD/PCU plus firmware | Parameterized standard TXBF path | compressed-V pointer fetched by DMA and consumed by SVD; H-info debug flag `[Q11][Q12]` | **CONFIRMED** hardware path; production use on QCA9882 **UNKNOWN** | Recover H/V formats; possibly useful as channel oracle even if explicit BF is not deployed |
| PHY timing and symbol timing | Baseband/PCU hardware, firmware-selected modes | Standard timing plus fine controls | timing registers, SGI, half/quarter-rate modes and descriptor timestamps `[Q03][Q04][Q11][Q13][Q14]` | **CONFIRMED** | Quantify timer granularity; arbitrary symbol duration not established |
| TSF and timers | MAC/PCU hardware with firmware scheduling | Hardware counters, programmable target use | TSF/wall-clock/fractional timestamps; Ubiquiti target polling `[Q11][R19]` | **CONFIRMED** | Foundation for target-resident deterministic scheduler |
| Retry-series state machine | PCU plus target firmware | Firmware/descriptor programmable | per-bandwidth series, tries and rate fields; firmware-owned rate control `[Q12][Q13][R03]` | **CONFIRMED** | Recover per-peer retry policy and expose safe controls |
| Aggregation | PCU plus target firmware | Firmware/device/TID controls | AMPDU/AMSDU descriptor fields and current ath10k controls `[Q13][R21]` | **CONFIRMED** | Topology/latency-aware aggregate sizing |
| Block ACK | MAC/PCU plus target firmware | Standard hardware/firmware protocol | current openMAX boundary and descriptor/datapath evidence `[R03][R21]` | **CONFIRMED** standard engine | Export BA bitmap and loss burst structure; current host API is limited |
| MAC scheduler | Target firmware using PCU/queues/timers | Programmable target software over hardware primitives | role-specific airMAX target images, polling strings and WMI opcodes `[R19][R20]` | **CONFIRMED** | Highest-probability route to a modern topology-aware PTMP scheduler |
| Encryption/crypto | OLE/PCU hardware plus host/firmware key setup | Standard cipher acceleration | exact-family MAC/OLE register families and ath10k datapath `[Q13][R21]` | **CONFIRMED at block level** | Little direct capacity upside; preserve correctness/security |
| HTT | Target firmware + host driver | Software protocol with fixed hardware descriptors | upstream ath10k and Ubiquiti target/datapath analysis `[R19][R21][L01]` | **CONFIRMED** | Add metadata export; recognize/transport channel-dump/debug records |
| DMA and Copy Engines | Fixed hardware programmed by firmware/host | Ring/buffer programmable | CE register definitions, Linux ath10k transport and later CFR circular-DMA model `[Q15][L01]` | **CONFIRMED** | Export debug memory efficiently without per-packet WMI latency |
| Target CPU | Xtensa configurable core | Firmware programmable | SGMT target binaries; public target C; common-Xtensa decoding `[R19][R25][Q01]` | Xtensa **CONFIRMED**; exact core options **UNKNOWN** | Build exact toolchain/ISA profile and patch one safe handler |
| Target DRAM/RAM | Target memory | Firmware/data programmable | Linux coredump region `0x400000` length `0x50000`; BMI read/write `[L03][L04]` | **CONFIRMED** region; full map **UNKNOWN** | Memory snapshots, task/queue discovery, channel-dump search |
| ROM | Silicon ROM | Fixed, callable by target | SGMT loads RAM segments; exact ROM ABI/symbols not public `[R19][R25]` | **UNKNOWN** | Identify call targets and ROM stubs through differential RE |
| OTP/eFuse and calibration memory | One-time/fixed data plus board data | Read/write restrictions; factory commands | UTF OTP/eFuse commands, board data/OTP loading in ath10k `[Q04][Q06][L01]` | **CONFIRMED** | Read-only mapping first; never automate irreversible writes |
| Spectral/FFT monitor | Baseband hardware + firmware/WMI | Parameterized capture | openMAX operational spectral capture and ath10k support `[R02][R16]` | **CONFIRMED** | External-state/interference oracle; not a channel matrix |
| DFS/radar | Baseband detection + target firmware/regulatory policy | Parameterized within regulatory constraints | spectral/radar hardware families and firmware path `[R16][Q14]` | **CONFIRMED at subsystem level** | Diagnostics only; strict regulatory guardrails |
| Channel-dump/CFR-like memory | Baseband capture + target firmware readout | Triggerable hidden measurement primitive | exact `bb_capture_channel`/`bb_captured_channel`; later-chip CFR transport as lineage reference `[Q11][Q12][Q15]` | Primitive **CONFIRMED**, transport/format **UNKNOWN** | Single highest-value measurement-recovery target |
| Host Linux/mac80211 | Host CPU | Fully programmable outside target timing | OpenWrt/ath10k-CT, AQL/TXQ, controller and instrumentation `[R01][R07][R08]` | **CONFIRMED** | Experiment control, slow policy, queue gating and safety; not symbol/slot timing |

### Bottom line from the map

The evidence supports a three-layer boundary:

1. **Host-controllable now:** association, queues/AQL, slow policy, standard configuration, spectral scans, test orchestration, traffic shaping and some device-wide aggregation/rate constraints. `[R03][R07][R08]`
2. **Target-firmware controllable in principle:** polling/scheduling, peer queues, retry/rate policy, timer use, detailed calibration, test commands, descriptor construction and debug-memory export. `[R19][Q03][Q11][Q12]`
3. **Apparently hardwired/parameterized PHY:** FFT, standard preambles, mapper/demapper, FEC engines, channel estimator/equalizer, MIMO/STBC and RF converters. Many parameters exist, but arbitrary replacement of these algorithms is not evidenced. `[Q13][Q14]`

---

# 3. Hidden-interface catalogue

## 3.1 Boot, memory and diagnostic interfaces

| Interface | Phase | Capability found | Exact-family status | Safety/brick risk | Immediate next action |
|---|---|---|---|---|---|
| BMI target memory read/write | Pre-firmware boot | arbitrary bounded target-memory access; compressed/LZ transfer | **CONFIRMED QCA988x** `[L03]` | Medium; writes can prevent boot until reset | Build read-only memory-map dumper and immutable before/after hashes |
| BMI SOC register read/write | Pre-firmware boot | target/SOC register access | **CONFIRMED QCA988x** `[L03]` | High if writes touch clocks/reset/OTP | Read allowlist only; never autonomous writes initially |
| BMI execute-address | Pre-firmware boot | jump/execute target address | **CONFIRMED QCA988x** `[L03]` | High | Defer until exact ISA/ROM ABI and recovery are proven |
| Host-interest block | Boot handoff | board/cal/test-script, app-start, CPU-speed, failure-state, debug and OTA-test-script pointers/flags | **CONFIRMED QCA988x** `[L05]` | Low for reads, medium for writes | Snapshot every field under normal/UTF/Ubiquiti boots |
| Coredump | Crash/recovery | QCA988x DRAM dump at `0x400000` length `0x50000` plus register regions selected by driver | **CONFIRMED QCA988x** `[L04]` | Low | Intentionally trigger safe watchdog on sacrificial device; mine task names, queues, pointers |
| ath10k DIAG/register/memory helpers | Runtime/debug, build-dependent | bounded target memory/register access paths used by driver/debug | **CONFIRMED host support; exact availability build-dependent** `[L03][L04]` | Medium | Inventory debugfs/module config and disable writes outside lab |
| SGMT loader/container | Firmware load | Ubiquiti embedded target images decode into target memory segments | **CONFIRMED exact Ubiquiti QCA988x** `[R19][R25]` | High on malformed images | Complete record semantics, checksum and relocation map before modification |

## 3.2 ath10k testmode and UTF transport

| Interface | Capability | Evidence | Status |
|---|---|---|---|
| `ATH10K_TM_CMD_UTF_START/STOP` | stop normal WLAN, load `utf.bin`/`utf-2.bin`, initialize board/OTP and run factory firmware | `[L01][L02]` | **CONFIRMED QCA988x host path** |
| `ATH10K_TM_CMD_WMI` | send raw WMI command ID and payload through testmode; receive WMI events | `[L01][L02]` | **CONFIRMED** |
| `WMI_PDEV_UTF_CMDID` path | carry segmented UTF/TLV test messages and reassemble responses | `[L01][L02]` | **CONFIRMED** |
| legacy test TLV | older test command transport retained by ath10k | `[L01][L02]` | **CONFIRMED** |
| UTF event segmentation/reassembly | response fragments carry sequence/length metadata before netlink delivery | `[L01]` | **CONFIRMED** |

**Implication:** ath10k already contains the transport required to run an exact-family diagnostic firmware and exchange opaque command payloads. The main missing pieces are a known-good AR9888 UTF binary/build, command dictionary, and a read-only bring-up protocol. `[L01][Q01][Q02]`

## 3.3 Exact AR9888 TCMD/ART capabilities

The following are exact AR9888/Peregrine build paths or exact-family headers, not later-chip assumptions. `[Q01][Q03][Q04][Q05][Q06]`

| Capability family | Discovered functions/fields | Label | openMAX relevance |
|---|---|---|---|
| Continuous TX | sine, CW/offset tone, frame, TX99, TX100, CLPC/PSAT-related modes; rate, power, packet size/count, duty, chain, antenna, bandwidth and gain controls | **CONFIRMED** | EVM/PA/linearity characterization; not arbitrary IQ |
| Continuous RX | continuous/promiscuous receive, filter control, chain masks, packet/rate counters | **CONFIRMED** | PER/sensitivity and hidden-mode detection |
| TX rate and coding | legacy/HT/VHT rate masks, SGI, STBC, LDPC, preamble, retries, aggregation, AIFS and scrambler controls | **CONFIRMED** | exact controlled PHY/MAC matrix |
| 5/10 MHz modes | half-rate and quarter-rate enumerations and target code paths | **CONFIRMED** | prove whether two exact-family endpoints can operate 10/5 MHz |
| RX statistics | total/good/CRC/PHY/security errors, per-rate/SGI counts, RSSI per chain, EVM per stream | **CONFIRMED** | direct receiver-quality oracle |
| Register access | `TCMD_SET_REG` and Qualcomm ART register operations | **CONFIRMED** | read/controlled-write BB/RF archaeology |
| OTP/eFuse | read/write/test/control operations | **CONFIRMED interface** | read-only mapping; writes are irreversible/high risk |
| Calibration | PAPRD/DPD, gain tables/indices, DAC gain, PA configuration, noise floor, thermal and hardware calibration | **CONFIRMED** | characterize implementation loss and power backoff |
| Test payloads | all-zero/all-one, alternating, PN7/PN9/PN15, user patterns and bit-error comparison | **CONFIRMED** | BER/test reproducibility; payload bits still traverse standard PHY |
| MAC/PCU control | DMA/interrupt/PCU setup, channel setup, ANI, aggregation and filters | **CONFIRMED** | understand which “MAC” functions are firmware-orchestrated |
| Bluetooth/coexistence hooks | BT/coexistence test fields in shared command headers | **CONFIRMED in header; board applicability varies** | low priority for 5 GHz fixed WISP |
| Regulatory/board controls | regulatory domain and EEPROM/modal data structures | **CONFIRMED** | calibration provenance; do not bypass legal limits |

## 3.4 Shared Qualcomm TLV2 command catalogue

These commands appear in the shared Qualcomm manufacturing framework. They are **not all proven to be compiled into AR9888 UTF**. The evidence label is therefore split.

| Command/family | Known ABI/function | Exact QCA988x implementation? | Evidence and implication |
|---|---|---|---|
| `REGREAD` / `REGWRITE` | target register read/write | **POSSIBLE; family framework confirmed** | `[Q07][Q08]`; exact handler/build must be enumerated |
| `MEMREAD` / `MEMWRITE` | bounded target memory read/write, up to 256 bytes per operation in visible implementation | **POSSIBLE** | `[Q07][Q08]`; could expose channel/sample memory |
| TX / RX / TXSTATUS / RXSTATUS | standardized TLV manufacturing operations | **POSSIBLE; overlapping exact TCMD exists** | `[Q07][Q03]` |
| HWCAL / OTP / DPD | hardware calibration, OTP and predistortion operations | **POSSIBLE; exact-family analogues confirmed** | `[Q07][Q03][Q04]` |
| PCIe configuration | manufacturing PCIe setup | **UNKNOWN exact build** | `[Q07]` |
| Regulatory commands | regulatory/board programming | **UNKNOWN exact build** | `[Q07]`; high compliance risk |
| DPD loopback/training | predistortion characterization | **UNKNOWN exact build** | `[Q07]`; useful for PA model if present |
| AGC-to-power / LM / NF read | receive-chain calibration and noise-floor operations | **UNKNOWN exact build** | `[Q07]` |
| `ADCCAPTURE`, command ID 59 in the shared dictionary | request capture by length/PHY/ADC/mode; response has 2048 I/Q pairs | **UNKNOWN on AR9888** | `[Q07][Q09]`; decisive raw-IQ gate |
| `GENWAVEFORM`, command ID 61 | takes waveform index and PHY ID; response carries 2048 I/Q pairs | **UNKNOWN on AR9888; not host-IQ TX** | `[Q07][Q10]` |
| `ENABLEDFE` | enable/configure digital front end | **UNKNOWN exact build** | `[Q07]` |
| `PHYDBGDUMP` | symbolic system command for PHY debug dump | **UNKNOWN; implementation not located** | `[Q07]`; search exact link map and handlers |
| command dictionary/parameter reflection | structured parameter dictionaries for manufacturing commands | **CONFIRMED framework** | `[Q07]`; allows automated ABI generation once build inclusion is known |

## 3.5 Exact descriptor-only debug capabilities

| Primitive | What exact headers say | What remains unknown | Priority |
|---|---|---|---|
| `bb_capture_channel` | TX/PCU descriptor requests BB channel capture after a good receive packet | which packet path sets it, capture lifetime and memory location | **P0** |
| `bb_captured_channel` | RX PPDU completion reports that a channel dump was captured; firmware can read channel-dump memory | dump format, dimensions, chain ordering, scaling and export | **P0** |
| `txbf_h_info` | RX packet data includes H information for TXBF debug | payload framing, H precision and whether available on QCA9882 board configuration | **P0** |
| `bb_length` | length of baseband debug information | whether it accompanies H/channel dump and how HTT strips/copies it | **P0** |
| EVM fields | per-pilot/per-stream EVM words in PPDU completion | calibration/scaling and what stock firmware preserves | **P1** |
| TSF/wall-clock/location timestamps | multiple timing domains including fractional-microsecond-related timestamp | exact clock frequency on device and wrap/offset semantics | **P1** |
| compressed-V pointer and SVD path | descriptor points to compressed V fetched by DMA and consumed by baseband SVD | whether Wave-1 production enables it and how V is encoded | **P1** |

Evidence: `[Q11][Q12]`.

## 3.6 Ubiquiti proprietary target interfaces

| Platform family | Command/interface | Evidence | Status |
|---|---|---|---|
| WA/XC | polling command around WMI opcode `0x9064` | Ubiquiti module/firmware tracing `[R19][R20]` | **CONFIRMED exact deployment stack** |
| WA/XC | native rate-schedule command around `0x9044` | `[R19][R20]` | **CONFIRMED exact deployment stack** |
| 2WA/2XC variants | corresponding polling/rate opcodes around `0x9070` and `0x9045` | `[R19][R20]` | **CONFIRMED for those families** |
| airOS hidden controls | `polling_ff_flex`, `dur`, `dl_ratio` and related role configuration | `[R20]` | **CONFIRMED reversible control path** |
| firmware strings | `UBNT_POLL_MEM_ALLOC`, `ubnt-poll`, `ubnt_set_power_range` | `[R19]` | **CONFIRMED target functionality markers** |
| role-specific images | `ptp`, `ptmp_ap`, `ptmp_sta` target binaries | `[R19]` | **CONFIRMED** |

## 3.7 Cross-chip CFR reference—useful but not proof

A later Qualcomm ath10k/QSDK implementation adds WMI CFR service discovery, per-peer capture configuration, an HTT `CFR_DUMP_COMPL_IND` path, a host DMA circular buffer and relayfs export. It supplies an engineering template for how Qualcomm moved channel estimates from BB memory to the host. The service is tied to WMI 10.4/later targets and is **not proof that Peregrine firmware implements the same command/event IDs**. `[Q15][A01]`

The later format’s complex-tone packing—small exponent plus signed real/imaginary components—is useful as a recognition hypothesis when inspecting an unknown Peregrine dump, but must remain **INFERRED** until an exact dump is decoded. `[A01]`



# 4. Firmware-research map

## 4.1 Known firmware families

| Firmware family | Target/source status | Distinguishing evidence | What it proves |
|---|---|---|---|
| Qualcomm upstream Wave-1 `10.1`/`10.2` binaries | binary distributions through ath10k firmware repositories | upstream driver/API families `[L01][C01]` | normal production baseline |
| Candela Technologies Wave-1 | modified target firmware; source obtained under NDA, not public | CT documentation and openMAX deep dive `[C01][R13]` | third party can modify exact-family target |
| Ubiquiti `ptmp_ap`, `ptmp_sta`, `ptp` | role-specific SGMT-embedded binaries | sizes, strings, opcode tracing and role differences `[R19][R20]` | exact-family proprietary polling is target-resident |
| Qualcomm-derived AR9888 UTF | public target C/build system for test firmware | explicit `TARGET=AR9888`, Peregrine includes and TCMD/ART source `[Q01][Q02][Q03]` | exact-family factory firmware can be rebuilt if dependencies/toolchain are completed |
| OEM/QSDK derivatives | mixed host/target binaries and manufacturing trees | public OEM GPL/source trees `[Q01][Q15]` | lineage, interfaces and test tooling |
| Later Wave-2 CFR firmware | source/patch interfaces for later ath10k targets | WMI 10.4 CFR service and HTT event `[Q15]` | implementation template only |

## 4.2 Loading and execution chain

1. The host identifies QCA988x hardware, obtains board/calibration data and target firmware, and uses BMI before normal firmware operation. BMI supports memory/register access and executable transfer. `[L01][L03][L05]`
2. Firmware is loaded into target memory; after `BMI_DONE`, normal WMI/HTT services are established and BMI is no longer the ordinary control path. `[L01][L03]`
3. Ubiquiti packages target segments inside its SGMT container; openMAX has extracted and qualified common Xtensa instruction regions but has not identified the exact Xtensa core configuration. `[R19][R25]`
4. UTF testmode deliberately shuts down the normal WLAN target and loads a test target, preserving board/OTP setup and using raw WMI/test messages for control. `[L01][L02]`

## 4.3 What is known about the target processor and binary

| Topic | Best current answer | Label | Evidence/next discriminator |
|---|---|---|---|
| ISA family | Xtensa configurable processor | **CONFIRMED** | target binaries/public build and common-instruction qualification `[Q01][R25]` |
| Exact Xtensa core/extension set | not established | **UNKNOWN** | identify configuration headers/toolchain, illegal-opcode behavior or vendor `.xtensa` metadata |
| Endianness/instruction decoding | common Xtensa decoding is productive on selected regions | **CONFIRMED, incomplete** | `[R25]` |
| Executable container | Ubiquiti SGMT with multiple loadable segments/records | **CONFIRMED** | `[R19][R25]` |
| Production symbol table | stripped/not publicly available | **CONFIRMED for examined images** | mine strings, call graphs and cross-version signatures `[R19]` |
| Public exact target source | factory/test UTF yes; production WLAN no | **CONFIRMED** | `[Q01][Q02][Q03][C01]` |
| Target DRAM | Linux dump region starts at `0x400000`, length `0x50000` | **CONFIRMED for driver coredump map** | `[L04]`; not necessarily the whole address space |
| Host-interest base | `0x00400800` family definitions with boot/debug/test fields | **CONFIRMED** | `[L05]` |
| ROM/RAM split and ROM ABI | not mapped | **UNKNOWN** | classify branch targets outside loaded segments; compare UTF and production |
| Relocations | SGMT record semantics partly recovered; complete relocation model not proven | **UNKNOWN/PARTIAL** | `[R19][R25]` |
| Compression | loader/container details vary; no universal statement established | **UNKNOWN/PARTIAL** | trace image parser and compare loaded memory |
| Signature enforcement | no conclusive public proof either way | **UNKNOWN** | change one inert byte/segment checksum on sacrificial hardware with recovery |
| Checksums | container/record validation not fully mapped | **UNKNOWN** | differential mutations and loader traces |
| Board-data dependency | board/calibration/OTP are part of boot/test initialization | **CONFIRMED** | `[L01][L05][Q06]` |

## 4.4 What can currently be modified with evidence

| Layer | Modification status | Confidence |
|---|---|---|
| OpenWrt/Linux/userspace/controller | routinely modifiable and deployed by openMAX | **CONFIRMED** `[R01][R02][R07][R12]` |
| ath10k/ath10k-CT host driver | modifiable; current project has patches, instrumentation and control experiments | **CONFIRMED** `[R03][R08][R13]` |
| WMI/HTT host protocol handlers | modifiable; raw/testmode transports exist | **CONFIRMED** `[L01][L02][R21]` |
| Ubiquiti module configuration/hidden keys | reversible controls recovered | **CONFIRMED** `[R20]` |
| Exact-family UTF target | source-level modification appears feasible once build dependencies/toolchain are completed | **POSSIBLE, high confidence** `[Q01][Q02][Q03]` |
| Production target binary patch | technically plausible; vendors have done it, but openMAX has not yet demonstrated its own safe patched target | **POSSIBLE, not yet proven in project** `[R19][C01]` |
| New production target from source | no public complete source/build | **UNKNOWN/NOT CURRENTLY AVAILABLE** `[C01][R13]` |
| Baseband microcode/tables below target C | access and format not established | **UNKNOWN** `[Q14]` |

## 4.5 High-value firmware subsystems to reconstruct

1. **WMI command/event dispatch tables** — especially Ubiquiti opcodes and UTF raw message routing. `[R19][R20][L01]`
2. **HTT RX completion/descriptor stripping** — locate where `bb_captured_channel`, EVM, timestamps and H-info are discarded or copied. `[Q11][R21]`
3. **Channel-dump allocator/readout** — search references to the capture bits, `bb_length`, BB debug SRAM and DMA copies. `[Q11][Q12]`
4. **Scheduler tasks/timers** — Ubiquiti polling task, TSF compare/timer callbacks, peer grants, DL/UL ratio and queue selection. `[R19][R20]`
5. **Rate/retry construction** — target-owned rate control, retry-series descriptors, native-rate-schedule command and per-peer state. `[Q12][Q13][R03][R19]`
6. **Aggregation/BA logic** — AMPDU construction, BA bitmap processing, retry queues and per-peer limits. `[R21][Q13]`
7. **Calibration and CCA control** — exact safe boundaries between factory test values and normal runtime calibration. `[Q03][Q14]`
8. **Crash task table and debug strings** — mine coredumps for task names, queue heads, timer lists and WMI service structures. `[L04]`

---

# 5. “Can we change the PHY?” decision tree

```text
START
│
├─ Can we safely boot exact AR9888 UTF and issue read-only commands?
│    ├─ NO → repair toolchain/image/board-data path; no PHY claims yet.
│    └─ YES
│
├─ Can standard rate/coding/width controls be selected and observed OTA?
│    ├─ YES → rate-table / LDPC-BCC / STBC / SGI / 5-10 MHz experiments are reachable.
│    └─ NO → command/build mismatch; map actual TCMD ABI.
│
├─ Does exact target expose channel-dump/H-info memory?
│    ├─ YES → recover H, EVM, rank and channel-capacity measurements.
│    └─ NO → use external coherent SDR; keep CSI path UNKNOWN/negative.
│
├─ Does exact AR9888 implement ADCCAPTURE or another sample-RAM dump?
│    ├─ YES → raw-RX experiments and learned/offline receivers become possible.
│    └─ NO → raw time-domain RX on-chip is unavailable through known interfaces.
│
├─ Is there a host- or firmware-writable mapper/pilot/subcarrier/FEC table?
│    ├─ YES → prove its semantics with one reversible, standard-compatible mutation.
│    │        ├─ constellation table → geometric/probabilistic shaping experiments
│    │        ├─ pilot/subcarrier table → pilot/waveform optimization
│    │        └─ FEC table → new coding experiments
│    └─ NO → treat mapper/pilots/FEC as fixed silicon.
│
├─ Can target accept host-supplied complex TX samples or arbitrary symbol vectors?
│    ├─ YES → QCA988x can serve as a constrained waveform engine; characterize rate/bandwidth.
│    └─ NO → fixed tones and payload patterns are test generators, not arbitrary waveform TX.
│
└─ Can target scheduler program sub-ms transmit grants using TSF/PCU timers?
     ├─ YES → custom deterministic PTMP MAC is a realistic primary research branch.
     └─ NO → use coarse host queue gating; retain hardware CSMA and avoid “fine TDMA” claims.
```

## Gate-by-gate answer today

| Proposed change | Current answer | What is already possible | Missing proof needed |
|---|---|---|---|
| Rate table / retry series | **YES, standard rates; target-owned details partly opaque** | standard MCS/rate masks, retry descriptors, Ubiquiti native schedule interface `[Q13][R19]` | prove deterministic per-peer/per-frame actuation under custom target |
| Constellation points | **UNKNOWN; no evidence of writable mapper** | select standard BPSK/QPSK/16/64/256-QAM via MCS `[Q13]` | mapper LUT/RAM or arbitrary symbol/IQ injection |
| FEC selection | **YES for BCC vs standard LDPC; NO evidence for a new code** | LDPC selection and decoder-scaling/latency controls `[Q13][Q14]` | writable parity/check matrices or software decoder insertion |
| Pilots | **UNKNOWN for arbitrary pilots** | tracking/masking/debug controls `[Q14]` | writable pilot sequence/location table |
| FFT/subcarrier layout | **YES for standard widths plus exact 5/10 MHz test modes; arbitrary layout UNKNOWN** | 5/10/20/40/80-related standard modes and FFT scaling `[Q03][Q04][Q14]` | FFT-size/subcarrier-map table or sample-level path |
| Symbol timing | **YES for standard GI and half/quarter modes; arbitrary timing UNKNOWN** | SGI and timing registers `[Q03][Q13][Q14]` | demonstrate a nonstandard symbol period interoperating with a modified peer |
| Raw IQ RX | **POSSIBLE/UNKNOWN** | exact channel dump; shared ADC-capture ABI `[Q09][Q11]` | Peregrine handler, sample RAM address and validated sample stream |
| Arbitrary TX waveform | **NO current evidence** | fixed tones/CW and standard framed payloads `[Q03][Q05]` | API that consumes host-provided complex samples or symbol vectors |
| Custom MAC | **YES in target firmware in principle** | Ubiquiti polling proves exact-family execution; host queue gating also possible `[R19][P09]` | open build/patch and measured timing/jitter |

### Decision rule

Do not invest major effort in learned constellations, learned pilots or new FEC on QCA988x until one of three primitives is proven:

1. writable mapper/pilot/FEC tables;
2. raw complex sample injection/capture at usable rates; or
3. a replaceable baseband microcode stage.

Absent those, the implementable “learned PHY” space collapses to **policy learning over standard modes**, while the implementable innovation space remains large at MAC/scheduler/queue/retry/CCA level. `[Q13][Q14][P08]`

---

# 6. Research-paper implementability matrix

The result column reports the paper’s own environment. It is not a prediction for QCA988x.

| Work/technique | Hardware evidence | Reported result or purpose | Required primitive | QCA988x primitive today | Worth testing? |
|---|---|---|---|---|---|
| Dörner et al., learned end-to-end communications OTA `[P01]` | off-the-shelf SDR OTA | learned transceiver operated over an unsynchronized real channel, near a practical baseline in the reported setup | arbitrary complex TX/RX and trainable receiver | **NO/UNKNOWN** | **Only after raw IQ TX/RX gate** |
| OFDM autoencoder `[P02]` | primarily simulation | joint end-to-end OFDM optimization under channel/oscillator impairments | programmable mapper, pilots and receiver | **UNKNOWN/NO current path** | **Not yet** |
| PAPR/ACLR-constrained learned OFDM `[P03]` | simulation/theory | learns waveforms under spectral and PAPR constraints | arbitrary high-dimensional waveform or subcarrier symbols | **NO current evidence** | **No, unless sample injection found** |
| CP-free neural OFDM receiver `[P04]` | real-time/OTA prototype work | learned receiver can replace explicit conventional stages in its platform | frequency-domain grid or raw IQ at receiver | **UNKNOWN** | **Potential offline oracle after capture** |
| StructNet-CE/online learned channel estimation `[P05]` | OTA pilots/real hardware in paper | online structured channel estimation | raw pilot/subcarrier observations | channel dump **POSSIBLE**, raw grid **UNKNOWN** | **Yes after channel dump** |
| Neural MU-MIMO receiver `[P06]` | hardware-in-loop/conformance-oriented | learned multiuser MIMO detection | full time-frequency receive grid and calibrated multi-antenna data | **NO current export** | **External SDR only** |
| DeepRx OTA validation `[P07]` | SDR/OTA | neural receiver validated over real channels | frequency-domain resource grid/IQ | **UNKNOWN on-chip** | **External/offline experiment** |
| Probabilistic/geometric shaping | mostly simulation, optical or SDR depending work | reduce shaping gap under suitable coding and SNR | programmable symbol distribution/mapper and matching decoder | standard mapper only **CONFIRMED** | **No until mapper gate** |
| Neural FEC decoding | FPGA demonstrations exist in other domains/platforms | replace/augment decoder | soft LLR access plus high-throughput accelerator | LDPC/Viterbi are fixed BB; LLR export absent | **No on QCA988x; external study only** |
| IteRate autonomous rate control `[P08]` | 58-node MediaTek/OpenWrt testbed | reported gains over Minstrel for five workloads | per-frame telemetry and in-kernel per-frame rate actuation | telemetry/actuation blocked by target-owned RC | **Yes as architecture; first add hooks** |
| hMAC hybrid TDMA/CSMA `[P09]` | Atheros ath9k COTS testbed | per-link/TID queue gating; hidden-node throughput improvement in reported test | host/driver queue pause/resume and coarse synchronization | **YES** through host queues/AQL with adaptation | **Yes, baseline now** |
| SoftMAC `[P11]` | commodity Atheros/MadWifi | replaces much of standard MAC while keeping standard RF PHY | SoftMAC device and direct low-MAC control | QCA988x is FullMAC/offload relative to ath9k | **Conceptual only** |
| Soft-TDMAC `[P12]` | commodity 802.11 testbed | microsecond-scale network synchronization claimed, TDMA scheduling | direct driver/hardware control and external sync | host timing likely insufficient; target may help | **Use as design reference** |
| WiLDNet `[P13]` | real long-distance commodity Wi-Fi deployment | reported 2–5× versus conventional 802.11 in its deployment via TDMA, bulk ACK and adaptive loss recovery | custom MAC, bulk ACK/FEC/retry control | target firmware needed for clean implementation | **High-value architecture reference** |
| Det-WiFi `[P14]` | commodity 802.11 multihop implementation | deterministic multihop TDMA design | driver-level timing and topology schedule | coarse host version possible; fine timing uncertain | **Medium** |
| SRT-WiFi `[P10]` | Zynq/AD936x SDR/FPGA testbed | sub-millisecond slots and tight synchronization in reported system | FPGA timers, queues, trigger and open PHY/MAC | target PCU/timers may provide subset | **Yes as timing target, not portable gain** |
| openwifi `[P15]` | Zynq + AD9361 full-stack FPGA/SDR | open PHY/low-MAC, CSI/IQ, time slicing and parameter control | FPGA/SDR full access | **NO**, different hardware class | **Excellent external oracle/reference** |
| openwifi CSI fuzzer `[P16]` | FPGA/SDR real implementation | applies artificial channel response before TX | writable per-subcarrier complex response | **UNKNOWN/no evidence** | **A direct falsification target for mapper access** |
| Wireless MAC Processor/WMP `[P17]` | programmable MAC engine research | software-defined state machines over hardware MAC commands | programmable low-MAC instruction engine | no such public ISA on QCA988x | **Use to structure target scheduler API** |
| WiSHFUL `[P18]` | heterogeneous test/control framework | unified control plane across radio platforms | stable platform-specific primitives | host/UTF/WMI primitives can be wrapped | **Yes for experiment orchestration** |
| ORCA/openwifi slicing `[P19]` | Zynq/AD9361 demo | full-stack time slices | FPGA low MAC/PHY | target scheduler only possible analogue | **Architecture reference** |
| GR-WiFi 802.11n/ac MIMO `[P20]` | GNU Radio simulation and real-world experiments | open SU/MU-MIMO 802.11 platform | wideband coherent SDR and software PHY | external, not on-chip | **Useful external receiver/transmitter oracle** |

## Implementability conclusion

- **Reachable now:** learned/optimized rate policy at a slower granularity, queue gating, topology-aware admission, RTS/CTS policy, aggregation/retry policy, CCA/correlator tuning in a shielded environment, safe multi-objective search. `[R07][R08][P08][P09]`
- **Reachable after target patching:** fine scheduler, per-peer retry/rate descriptors, descriptor metadata export, channel-dump transport. `[Q11][Q12][R19]`
- **Blocked pending a hidden primitive:** learned constellations, learned pilots, custom FEC, arbitrary waveform optimization and neural on-chip receiver replacement. `[Q13][Q14]`

---

# 7. Physical-limit framework

## 7.1 Do not compare only against vendor MCS tables

For every run, report at least:

\[
\eta_{\text{goodput}} = \frac{G_{\text{application}}}{B} \quad \text{bits/s/Hz}
\]

\[
\eta_{\text{PHY}} = \frac{R_{\text{nominal PHY}}}{B}
\]

\[
\eta_{\text{MAC}} = \frac{G_{\text{application}}}{R_{\text{nominal PHY}}}
\]

The third quantity isolates losses below application goodput but above the nominal PHY rate. The first permits fair 5/10/20/40/80 MHz comparison. The current `RunSample` fallback must not divide every run by 40 MHz. `[R23]`

## 7.2 Airtime decomposition

For each delivered payload block:

\[
T_{\text{total}} =
T_{\text{preamble}} +
T_{\text{data}} +
T_{\text{SIFS}} +
T_{\text{ACK/BA}} +
T_{\text{contention}} +
T_{\text{scheduler idle}} +
T_{\text{retries}} +
T_{\text{processing/queueing}}
\]

Measure or infer:

- preamble/symbol airtime from decoded PPDU;
- payload bytes and aggregation depth;
- BA/ACK airtime;
- contention/backoff and CCA busy time;
- retry count and retry airtime;
- queueing/host delay;
- scheduler gaps and grant utilization.

The optimization target should include **airtime per delivered bit**, not only throughput, because an apparent gain can steal airtime from weak peers or increase tail latency.

## 7.3 Shannon-style references

For a single ideal Gaussian channel:

\[
C = B\log_2(1+\mathrm{SNR})
\]

For a calibrated \(N_t \times N_r\) MIMO channel matrix \(H\), equal power and known noise:

\[
C = B\log_2\det\left(I_{N_r} + \frac{\rho}{N_t}HH^{H}\right)
\]

These are upper bounds under explicit assumptions, not predictions of Wi-Fi throughput. Interference may be impulsive, structured, non-Gaussian or receiver-dependent; packetization, pilots, guard intervals, coding, PA distortion and protocol overhead remain outside the ideal bound. `[T01][T02]`

## 7.4 EVM and implementation gap

When residual impairment is approximately additive and uncorrelated:

\[
\mathrm{SNR}_{\text{EVM}} \approx \frac{1}{\mathrm{EVM}_{\mathrm{rms}}^2}
\]

Use this only as an approximation; phase noise, channel-estimation error, PA nonlinearity and interference can violate the assumption. `[T03][E06]`

A useful implementation-gap diagnostic is:

\[
\Gamma = \frac{\mathrm{SNR}}{2^{\eta}-1}
\]

where \(\eta\) is the achieved coded or goodput spectral efficiency under a clearly stated denominator. Track \(\Gamma\) versus MCS, power, range, interference and aggregation.

## 7.5 Estimating 2×2 capacity without stock CSI

### Route A — internal channel dump

1. trigger `bb_capture_channel`;
2. verify `bb_captured_channel`;
3. locate dump memory and `bb_length`;
4. establish dimensions and chain/tone ordering;
5. calibrate complex scaling using a cabled known channel;
6. compare against a coherent external receiver;
7. compute per-tone singular values/eigenvalues and outage/ergodic summaries.

This route is **POSSIBLE/UNKNOWN**. `[Q11][Q12]`

### Route B — external coherent 2-channel SDR

Capture both receive chains with a shared clock/LO, decode the VHT training fields, estimate \(H_k\) per subcarrier, calibrate channel imbalance and compute:

- singular values of each \(H_k\);
- condition number/rank;
- per-tone SNR/noise covariance;
- capacity upper-bound distribution;
- correlation over time and peer geometry.

This route is **CONFIRMED feasible in principle with suitable SDR**, independent of QCA988x firmware. `[E03][P20][T02]`

### Route C — indirect production metrics

If neither capture route is available, use EVM/RSSI/PER/rate/retry statistics only as a lower-resolution surrogate. Do **not** label the result “CSI” or a measured MIMO capacity.

## 7.6 Measurement protocol

Every candidate configuration should be tested with:

1. immutable binary/config hashes;
2. randomized paired A/B/A/B or Latin-square order;
3. a sentinel baseline repeated through the run;
4. link/environment covariates: channel, noise floor, spectral occupancy, RSSI/EVM, temperature, peer set and offered load;
5. multiple links spanning near/far, clean/interfered and rank-1/rank-2 channels;
6. independent holdout replication on a different time block/day;
7. p50/p95/p99 latency, goodput, delivered airtime, loss, retry airtime, fairness and worst-peer service;
8. block/bootstrap or paired inference that preserves temporal pairing;
9. correction or alpha budgeting for repeated autonomous trials;
10. a predeclared rollback/safety envelope.

Shannon capacity should be plotted as a reference band only after calibrated bandwidth, noise and channel assumptions are documented. `[T01][T02][R15]`



# 8. Top 20 experiments

Scales: information gain (IG) 1–5; difficulty 1–5. “Brick risk” assumes a sacrificial radio with proven recovery. Effort is active engineering effort, not elapsed calendar time.

| Rank | Experiment and branch eliminated | IG | Diff. | Brick risk | Equipment | Effort | Automatically runnable? | Acceptance / falsification criterion |
|---:|---|---:|---:|---|---|---|---|---|
| 1 | **Activate exact channel dump:** set/request `bb_capture_channel`, receive a valid packet, inspect `bb_captured_channel`, `bb_length`, and target memory diffs | 5 | 4 | Medium | sacrificial QCA988x pair; optional logic/SDR | days–weeks | Partly | Success: repeatable packet-correlated memory blob. Failure after exact descriptor path and exhaustive mapped memory sharply weakens internal-CSI branch |
| 2 | **Boot exact AR9888 UTF read-only:** build or obtain a known-good `utf.bin`; run GET_VERSION/status and no-write commands through ath10k testmode | 5 | 3 | Medium | sacrificial radio, serial/recovery | days | Yes after validation | Success: stable command/response and normal-firmware recovery; failure isolates build/toolchain/board-data mismatch |
| 3 | **Enumerate UTF command support:** probe dictionary with non-destructive capability/status requests, log accepted/unsupported IDs and event schemas | 5 | 3 | Low–Medium | UTF bench | days | Yes | Produces exact AR9888 capability bitmap; resolves shared-TLV versus compiled-target ambiguity |
| 4 | **Determine whether `ADCCAPTURE` exists:** locate handler in link map/binary or issue bounded request with RF terminated/cabled | 5 | 4 | Medium | UTF bench, attenuator/load | days–weeks | Partly | Success: sample buffer changes with tone/frequency/phase; unsupported/absent handler closes raw-IQ path through this ABI |
| 5 | **Recover pre-stripped RX descriptors:** instrument target/HTT/host to copy raw `rx_ppdu_end` including EVM, timestamps and capture bits | 5 | 4 | Medium | QCA pair | weeks | Yes after patch | Success: exact descriptor values correlate with external packets; determines whether host loss is only stripping |
| 6 | **Compile public AR9888 UTF from source and compare:** reconstruct toolchain/includes, produce binary, compare section layout/strings to known UTF artifacts | 5 | 5 | Medium | build host, sacrificial radio | weeks | Mostly | A booting one-line-modified target proves open target-build capability |
| 7 | **One safe target-firmware mutation:** add a no-op WMI/test command or altered debug string, preserve behavior, boot/recover repeatedly | 5 | 5 | High | sacrificial device, serial/JTAG if available | weeks | No initially | This is the production-research inflection point: custom target code execution is proven or loader/toolchain blockers are isolated |
| 8 | **Locate/decode channel-dump SRAM:** memory-diff scans triggered by known cabled channels, packet widths and chain masks; test later-CFR packing hypotheses | 5 | 5 | Medium | coherent SDR desirable | weeks | Partly | Decode must predict phase/amplitude changes under known cable/attenuator configurations |
| 9 | **Probe `txbf_h_info` and compressed-V/SVD paths:** trigger sounding/beamforming-compatible frames and inspect data/debug payloads | 4 | 5 | Medium | QCA pair + monitor/SDR | weeks | Partly | Success exposes H or V matrices; absence may be firmware-mode-specific, not silicon refutation |
| 10 | **5/10 MHz exact-family loop:** force half-/quarter-rate on both endpoints in a shielded/cabled setup; capture spectrum, timing, MCS/PER | 4 | 3 | Low–Medium | two QCA devices, SDR/VSA | days | Yes | Proves mode is operational beyond factory TX; quantify goodput/MHz rather than raw goodput |
| 11 | **Descriptor-versus-rate-control experiment:** inject standard retry/rate series in target/test path and determine whether firmware/PCU honors or overwrites each field | 4 | 4 | Medium | QCA pair | days–weeks | Yes | Maps exact actuation boundary for autonomous rate/schedule policy |
| 12 | **Measure target scheduler timer resolution:** use Ubiquiti polling or a minimal target timer callback; observe grant/TX edge jitter externally | 5 | 4 | Medium | SDR or fast VSA/logic trigger | days–weeks | Yes | Establishes whether sub-ms custom slots are physically credible |
| 13 | **Trace proprietary poll WMI end to end:** host module→WMI opcode→target handler→queue/timer/descriptor side effects, using differential memory/coredump snapshots | 5 | 5 | High | stock airOS sacrificial AP/CPE | weeks | Partly | Produces scheduler call graph and state object layout |
| 14 | **Coarse hMAC-style queue gating baseline:** randomized 10/20/50 ms per-peer/TID host queue gates while hardware CSMA remains active | 3 | 2 | Low | current OpenWrt sector | days | Yes | Establishes the maximum available without target timing and a fair comparison for later firmware MAC |
| 15 | **Sub-ms target-resident one-link scheduler prototype:** once timer/queue functions are mapped, gate a single peer with fixed slots and external timing validation | 5 | 5 | High | sacrificial pair + SDR | weeks | Partly | Success requires bounded jitter, no hidden CSMA leakage outside slot, and clean rollback |
| 16 | **CCA/correlator response surface in a shielded interferer setup:** vary one allowlisted threshold at a time under controlled desired/interferer levels | 4 | 3 | Medium | shield box/couplers, signal source or second TX | days–weeks | Yes | Identify Pareto frontier of sensitivity, false alarm, collision and exposed-node behavior |
| 17 | **LDPC/BCC/STBC/SGI controlled matrix:** fixed attenuation/interference, external EVM/PER, exact airtime and retry accounting | 3 | 2 | Low | attenuators/couplers; VSA optional | days | Yes | Quantifies real implementation gap and when each standard primitive helps |
| 18 | **Internal-versus-external 2×2 H validation:** compare decoded channel dump with coherent SDR channel estimates over cabled known matrices and OTA links | 5 | 4 | Low once capture works | dual-channel coherent SDR | days–weeks | Yes | Correlation in complex amplitude/eigenvalues validates internal CSI semantics |
| 19 | **PA/PAPR/linearity map using fixed UTF tones/patterns:** sweep legal power/gain/calibration states and measure EVM, ACLR, compression and thermal drift | 3 | 3 | Medium | calibrated VSA/spectrum analyzer, attenuators | days | Yes | Separates channel limit from transmitter implementation loss |
| 20 | **Autonomous safe search pilot:** after metric/gate fixes, optimize only reversible MAC policy on a cabled/shielded multi-link bench with holdout replication | 4 | 3 | Low under constraints | existing bench | weeks | Yes | Candidate must beat sentinel on paired holdout without violating p99/fairness/safety constraints |

## Recommended execution order

The first campaign should be **1 → 2 → 3 → 5 → 4 → 6 → 7**. Those experiments eliminate the largest branches:

- whether hidden channel measurement is real and exportable;
- whether the exact test firmware can be controlled;
- whether common TLV commands are actually compiled for Peregrine;
- whether openMAX can execute its own target code.

Do not start arbitrary-PHY research before those gates.

---

# 9. Top reverse-engineering targets

| Priority | Exact target | Search keys / functions / regions | Why it matters |
|---:|---|---|---|
| 1 | exact AR9888 RX/TX descriptor handling | `bb_capture_channel`, `bb_captured_channel`, `bb_length`, `txbf_h_info`, `cv_ptr`, compressed V | direct route to H/CSI and hidden debug memory `[Q11][Q12]` |
| 2 | channel-dump SRAM and control registers | “channel dump memory,” BB capture mode, PCU/BB descriptor request, memory writes after RX PPDU | identifies address, format and lifetime |
| 3 | HTT RX completion conversion | raw PPDU-end copy/strip functions, RX indication builders, debug-extension lengths | determines where rich hardware metadata disappears `[R21][Q11]` |
| 4 | AR9888 UTF link/build graph | `TARGET=AR9888`, `tcmd_utf`, `commonUTF`, `wmiHostIF`, `utf_cal`, linker scripts and Xtensa config | shortest path to custom target execution `[Q01][Q02]` |
| 5 | `ADCCAPTURE` registration/implementation | command ID 59, `registerADCCAPTUREHandler`, `ADCCAPTUREOpFunc`, sample RAM, ADC IDs | resolves raw IQ capture `[Q07][Q09]` |
| 6 | `GENWAVEFORM` implementation | command ID 61, waveform index table, returned IQ meaning | determine whether it generates, captures or describes internal test waveforms `[Q10]` |
| 7 | `PHYDBGDUMP` | enum, handler registration, response ABI, PHY debug memory | could expose BB state/sample memory `[Q07]` |
| 8 | BMI host-interest test hooks | `hi_test_apps_related`, `hi_ota_testscript`, app start, failure-state, debug-log pointers | may reveal factory script/bootstrap mechanisms `[L05]` |
| 9 | Ubiquiti polling handlers | WMI `0x9064`/`0x9070`, strings `UBNT_POLL_MEM_ALLOC`, `ubnt-poll`, grant/timer callbacks | reconstruct exact scheduler `[R19][R20]` |
| 10 | Ubiquiti native-rate-schedule handlers | WMI `0x9044`/`0x9045`, rate-series/peer objects | expose per-peer rate/retry schedule `[R19][R20]` |
| 11 | Ubiquiti role-image diff | `ptmp_ap` vs `ptmp_sta` vs `ptp`, cross-version function signatures | isolates scheduler/task differences from common WLAN code `[R19]` |
| 12 | target task/timer registry | task names, timer-wheel/list heads, TSF compare, watchdog and callback tables in coredump | foundation for deterministic target scheduler `[L04]` |
| 13 | rate-control implementation | peer stats, probe tables, retry-series builders, `HAS_RATE_CONTROL`, WMI rate masks | host-to-target actuation boundary `[R03][Q13]` |
| 14 | AMPDU/BA processing | delimiter construction, BA bitmap, retry queue, per-TID/per-peer aggregate limits | latency/fairness/retry optimization `[R21]` |
| 15 | BB register write sites in UTF and production | CCA, AGC, timing, pilot/channel masks, LDPC scaling, FFT scaling | classify safe runtime-versus-factory controls `[Q03][Q14]` |
| 16 | coredump/cross-version pointer signatures | DRAM `0x400000..0x44ffff`, known string xrefs, queue object patterns | bootstraps semantic memory map `[L04]` |
| 17 | SGMT validation path | record parser, length/checksum/signature branches, load addresses, entry point | enables safe binary modification `[R19][R25]` |
| 18 | exact Xtensa core configuration | build-system config, compiler flags, `.xtensa.info`, coprocessor opcodes, exception cause | avoids incorrect disassembly/patches `[R25]` |
| 19 | board/OTP/caldata schema | QC98xx modal data, chain/power tables, board selection and OTP flags | separates board calibration from silicon capability `[Q06][L01]` |
| 20 | later CFR implementation for semantic matching only | `WMI_SERVICE_CFR_CAPTURE_SUPPORT`, peer CFR config, HTT type `0x32`, DMA circular buffer | template for a new Peregrine export path, not an opcode transplant `[Q15]` |

---

# 10. External measurement equipment

## 10.1 What each class can prove

| Class / example | Relevant specs | What it can prove | What it cannot prove alone | Assessment |
|---|---|---|---|---|
| HackRF One | 1 MHz–6 GHz, half-duplex, up to 20 MS/s, 8-bit, one RF path `[E04]` | rough 20 MHz occupancy, packet timing, retransmission spacing, coarse spectrum | full-quality 40/80 MHz capture, calibrated EVM, 2×2 channel | inexpensive timing/debug accessory, not primary microscope |
| USRP B210 | 70 MHz–6 GHz, 2 coherent channels, up to 56 MHz real-time bandwidth `[E01]` | full 20/40 MHz IQ, 2×2 phase-coherent observations, preamble/timing/channel estimates | complete 80 MHz capture | minimum serious 20/40 MHz 2×2 platform |
| bladeRF 2.0 micro | roughly 47/70 MHz–6 GHz TX/RX, 2×2, ~56 MHz filtered bandwidth, 12-bit `[E05]` | similar 20/40 MHz dual-channel experiments | full 80 MHz and metrology-grade EVM | alternative low-cost coherent platform |
| USRP X310 + dual wideband daughterboards | two RF slots, up to 160 MHz baseband/channel, 14-bit ADC and 16-bit DAC on platform `[E02]` | full 80 MHz 2×2 capture/generation, FPGA triggering, shared clocks | calibrated VSA accuracy without characterization | strong research platform |
| USRP N320/N321 | 3 MHz–6 GHz, 2×2, up to 200 MHz/channel class, high-rate ADC/DAC and clocking `[E03]` | full 80 MHz 2×2 with margin, deterministic network/FPGA workflows | laboratory traceability without calibration | best turnkey SDR microscope among listed options |
| Signal Hound SM200C | 100 kHz–20 GHz, 160 MHz continuous IQ over 10GbE, 110 dB dynamic range `[E07]` | calibrated/wide occupancy, interference, single-channel IQ and timing | simultaneous phase-coherent 2×2 channel matrix | excellent calibrated single-channel observer |
| R&S/Keysight WLAN VSA | 160 MHz-class 802.11ac demodulation, EVM versus symbol/subcarrier, calibrated signal analysis `[E06][E08]` | transmitter truth: EVM, constellation, spectral mask, ACLR, phase error, impairment localization | cheap continuous 2×2 raw-research capture unless configured as multi-channel system | metrology reference |
| openwifi / GR-WiFi SDR | open FPGA/SDR PHY/MAC or GNU Radio 802.11n/ac MIMO `[P15][P20]` | independent packet decoder, CSI/IQ oracle, custom reference signals and adversarial test cases | facts about QCA988x internals | exceptionally useful external reference implementation |

## 10.2 Minimum specifications by question

| Question | Minimum credible setup |
|---|---|
| packet timing, slot boundaries, retransmission gaps at 20 MHz | ≥20 MS/s receiver with stable clock; HackRF can begin, B210 preferred |
| accurate EVM/constellation at 20/40 MHz | calibrated VSA or well-characterized ≥56 MHz 12-bit SDR with reference signal |
| full 80 MHz waveform capture | ≥100 MS/s practical complex stream and ≥80 MHz usable analog bandwidth; 12+ effective bits preferred |
| 2×2 MIMO channel matrix | two phase-coherent RX channels sharing LO/reference, calibrated amplitude/phase, simultaneous capture |
| compare internal channel dump to ground truth | dual-channel coherent SDR plus cabled 2×2 channel matrix/couplers/attenuators |
| characterize PA compression/PAPR/ACLR | calibrated attenuator/coupler chain and VSA/spectrum analyzer with sufficient dynamic range |
| prove exact scheduler timing | externally triggered or continuously recording IQ with sub-microsecond timestamp stability |

## 10.3 Non-negotiable bench accessories

- shield box or cabled RF path;
- high-quality fixed/step attenuators rated for 5 GHz;
- directional couplers/splitters and 50-ohm terminations;
- DC blocks where required;
- power meter or calibrated reference path;
- shared 10 MHz/PPS/LO where coherent capture is required;
- thermal logging;
- hard RF power limits and emergency firmware rollback.

These are part of the measurement instrument. Without them, a better SDR can still produce misleading EVM, phase and channel estimates.

## 10.4 Recommended acquisition sequence

1. **Use existing/low-cost SDR for timing first.**
2. **Acquire a dual-channel B210/bladeRF-class unit** if the immediate campaign is 20/40 MHz channel/timing.
3. **Move directly to N320/N321 or X310 + two wideband daughterboards** if full 80 MHz and 2×2 are core goals.
4. **Rent/borrow calibrated R&S/Keysight equipment** for milestone validation rather than assuming SDR amplitude/phase accuracy.
5. Add a Signal Hound-class analyzer if long-duration calibrated 160 MHz monitoring is more important than 2×2 coherence.

---

# 11. Hard limits already established

These are branches openMAX should stop re-litigating unless contradictory exact-family evidence appears.

1. **QCA9882 boards are physically 2T2R/2-stream devices.** Software cannot create additional RF chains. QCA9880 3×3 facts must not be assigned to QCA9882. `[H01][H02]`
2. **Normal exact TX descriptors enumerate standard legacy/HT/VHT rates through VHT MCS9/256-QAM.** There is no documented descriptor value for 1024-/4096-QAM or a free-form constellation. `[Q13]`
3. **LTU’s 4096-QAM/OFDMA/FPGA findings do not transfer to QCA988x.** The architectures are materially different. `[R11]`
4. **A host WMI call is not a symbol-time or microsecond scheduler.** WMI/PCIe/Linux can orchestrate and configure but cannot be assumed deterministic at PHY timescales. `[P09][P10][R03]`
5. **Spectral scan is not CSI.** It lacks the per-transmit/per-receive-stream complex channel matrix. `[R16][T02]`
6. **Payload patterns are not arbitrary IQ.** PN/user payloads still pass through the standard mapper/FEC/interleaver. `[Q05][Q13]`
7. **CW/sine/offset-tone generation is not an arbitrary waveform interface.** `[Q03][Q05]`
8. **The current live rate-mask path is not a reliable per-peer real-time actuator.** openMAX observed accepted dispatch with ineffective reassociation behavior. `[R08]`
9. **Current production ath10k has no normal API for channel dump/raw IQ.** Hidden hardware/test paths do not change that operational fact. `[R03][R16][L01]`
10. **RF converter resolution, sample rate, PA/LNA/filter topology and physical calibration range are hardware limits.** Their exact numerical ceilings remain partly unknown, but firmware cannot wish them away.
11. **Shared headers containing 160 MHz or four-stream fields do not prove QCA9882 supports those modes.** Generated descriptor families can include reserved/future/common fields. `[Q13]`
12. **Gains from unrelated papers cannot be added.** A 2× result from a long-distance TDMA paper plus a learned-PHY gain from SDR does not predict a combined QCA988x gain.
13. **5/10 MHz operation is not automatically a capacity increase.** It may improve range/interference selectivity while reducing absolute bandwidth; evaluate goodput/MHz and service objectives. `[Q03][Q04]`
14. **Shannon capacity is an upper bound under assumptions, not a throughput forecast.** `[T01][T02]`
15. **An AI optimizer cannot compensate for missing actuation or bad metrics.** It can only search the primitives and objective it is given. `[P08][R23][R24]`

---

# 12. Major UNKNOWNs

1. Exact Xtensa core configuration, extensions, toolchain version and ABI.
2. Complete QCA988x target memory map beyond known host-interest/coredump regions.
3. ROM entry points and which production functions execute from ROM.
4. Complete SGMT record semantics, checksums and any signature validation.
5. Whether a modified production target can be loaded safely with only software recovery.
6. Exact location, size and lifetime of the channel-dump memory.
7. Channel-dump format: tones, chains, streams, exponent/precision, ordering and calibration.
8. Whether `txbf_h_info` is available on QCA9882 production configurations and what its payload contains.
9. Whether compressed-V/SVD hardware is active/useful on the deployed Ubiquiti boards.
10. Whether stock/CT/Ubiquiti firmware strips channel/debug fields intentionally or never enables them.
11. Whether AR9888 UTF in the public tree is complete enough to rebuild without proprietary libraries/toolchain components.
12. Which shared TLV2 commands are compiled into the AR9888 target.
13. Whether `ADCCAPTURE` exists on AR9888 and captures time-domain ADC, post-DFE samples or another stage.
14. What `GENWAVEFORM` returns and whether its indexed waveforms are generated or captured.
15. Whether `PHYDBGDUMP` has a Peregrine implementation.
16. Whether any arbitrary sample/symbol TX RAM exists and is reachable.
17. Whether constellation points are held in writable ROM/RAM/LUT or fixed logic.
18. Whether pilot values/locations or interleaver permutations are writable.
19. Whether FEC matrices/polynomials are writable rather than fixed engines.
20. Actual scheduler timer granularity and jitter in production/UTF target context.
21. Exact Ubiquiti poll grant structure, synchronization mechanism and retransmission policy.
22. Semantics of the Ubiquiti native-rate-schedule WMI payload.
23. Per-peer aggregation/BA control opportunities below current host API.
24. Effective PCIe/CE/host CPU ceiling under high-rate 2×2/80 MHz production load.
25. Real ADC/DAC effective resolution, sample rates and available sample RAM.
26. Whether 5/10 MHz can form a complete bidirectional data link between two exact-family devices outside test TX/RX.
27. Which BB registers are safe to change during runtime rather than only during calibration.
28. Whether later CFR tone packing resembles Peregrine’s hidden dump.
29. How much of current sector loss is RF-channel limit versus implementation/MAC overhead.
30. Whether a modern target-resident scheduler can beat airMAX fairly across multiple real sectors and seasons.

Every one of these UNKNOWNs maps to an experiment or RE target above; none requires a speculative positive answer.



# 12A. Autonomous discovery architecture and statistical safeguards

## What to borrow from autoresearch and IteRate

Karpathy’s autoresearch pattern is valuable because it forces a small, fixed experiment budget, a single explicit metric, a keep/reject decision and a persistent log rather than open-ended agent narration. IteRate is more directly relevant: it couples hypothesis generation, code synthesis, deployment, fine-grained telemetry and OTA evaluation, but its key enabler is not “AI” alone—it adds the kernel hooks needed to observe and actuate rate control. `[A02][P08]`

For openMAX the analogous architecture should be:

```text
Evidence graph / prior experiments
        ↓
Hypothesis agent
        ↓
Capability checker: does the requested primitive actually exist?
        ↓
Safety compiler: allowlist, bounds, recovery and regulatory checks
        ↓
Experiment compiler: topology, traffic, A/B order, power, duration, hashes
        ↓
Deployment controller
        ↓
AP + CPE + external RF telemetry
        ↓
Paired statistical evaluator + drift detector
        ↓
accept / reject / inconclusive
        ↓
replication on holdout link/time block
        ↓
knowledge update and deduplication
```

## Required corrections before autonomous selection

| Current issue | Why it can produce a false discovery | Required correction |
|---|---|---|
| `goodput_per_mhz` fallback divides by 40 MHz | 20/80 MHz candidates are systematically mis-scored | make bandwidth mandatory in each sample or derive from immutable run metadata `[R23]` |
| Gatekeeper description includes p95 and fairness, implementation does not fully enforce them | optimizer can trade away fairness/tail quality while “passing” | encode an explicit lexicographic or constrained multi-objective decision `[R24]` |
| A/B/A/B blocks treated as independent groups | loses pairing and ignores temporal drift | paired/block model, period fixed effects or block bootstrap |
| very small sample counts accepted | unstable variance and inflated winner selection | minimum effective blocks based on power/noise; allow “inconclusive” |
| significance emphasized mainly for goodput | latency/fairness regressions may pass | confidence bounds for every hard constraint |
| no explicit repeated-search correction | thousands of candidates eventually create false positives | holdout replication, alpha spending/FDR or Bayesian posterior threshold |
| no sentinel baseline through long runs | environmental drift can look like candidate improvement | interleave immutable sentinel and model change points |
| reward can be dominated by one easy link | overfits to one topology | stratified objectives across weak/strong/hidden-node/rank conditions |
| no explicit experiment deduplication | agent rediscovers equivalent settings | canonical experiment fingerprint and semantic equivalence graph |
| raw register space is enormous | unsafe/destructive combinations | typed parameter schema, allowlists, monotonic bounds and staged unlocks |

## Noise and drift controls

1. **Randomized crossover:** candidate and baseline alternate in randomized blocks, not one long baseline then one long candidate.
2. **Sentinel packets/configuration:** a fixed control condition repeats every block to estimate drift.
3. **Environmental covariates:** spectrum occupancy, noise floor, temperature, RSSI/EVM, peer count and load are logged before and during each trial.
4. **Change-point detection:** pause/segment inference when the RF environment shifts.
5. **Hierarchical replication:** replicate across packets inside blocks, blocks inside days, and links/sectors as the true generalization units.
6. **Holdout:** the agent never sees at least one link/time block used for final confirmation.
7. **Negative controls:** occasionally deploy a known-equivalent configuration; an apparent gain estimates the false-discovery floor.
8. **Immutable provenance:** firmware, driver, config, board, calibration, traffic generator and analysis code hashes accompany every sample.

## Safe exploration

SafeOpt-style methods are relevant but do not make an unsafe search safe merely by naming a Gaussian process. Later work shows that practical SafeOpt confidence heuristics can violate safety when their assumptions are not justified. openMAX should use hard engineering bounds and staged privilege before statistical “safety.” `[A03][A04]`

Recommended privilege levels:

- **L0:** read-only telemetry.
- **L1:** reversible host policy within production-tested ranges.
- **L2:** reversible BB/UTF parameters in cabled/shielded setup.
- **L3:** target firmware modifications on sacrificial devices with serial recovery.
- **L4:** field trials after independent bench replication.
- **Never autonomous:** OTP/eFuse writes, regulatory bypass, uncontrolled continuous TX, unknown clock/reset/PA registers.

## Multi-objective acceptance

A candidate should be accepted only if:

1. no hard safety/regulatory limit is violated;
2. worst-link service and fairness stay above declared floors;
3. p99 latency/retry airtime do not exceed bounds;
4. goodput/airtime efficiency improves with uncertainty bound above zero;
5. the result replicates on a holdout block;
6. the binary/config is reproducible;
7. the gain survives a return-to-baseline test.

This prevents reward hacking such as starving the weak CPE, increasing TX power, suppressing retransmission accounting, or exploiting a measurement bug.

---

# 13. New technically defensible hypotheses

These are deliberately not generic parameter-tuning ideas. Each has a falsification route.

| # | Hypothesis | Why defensible | How to falsify |
|---:|---|---|---|
| 1 | **The exact Peregrine channel-dump memory contains per-tone complex channel estimates usable as CSI.** | exact descriptor explicitly reports channel capture and firmware-readable dump memory `[Q11][Q12]` | trigger capture under known cabled channels; if no repeatable complex response or only scalar/debug counters appear, reject |
| 2 | **Production/CT firmware still contains dormant channel-capture code even though ath10k does not expose it.** | descriptor hardware is exact-family and later Qualcomm targets export CFR `[Q11][Q15]` | binary xref/search plus forced descriptor bit; reject if all paths are compiled out and memory never changes |
| 3 | **`txbf_h_info` exposes an H matrix independently of the channel-dump buffer.** | exact RX descriptor documents H information for TXBF debug `[Q11]` | generate sounding-compatible traffic and inspect debug payload; reject after confirmed triggering with no H record |
| 4 | **`bb_length` is the byte count needed to parse an appended BB debug/H record that stock HTT discards.** | field is adjacent to exact debug indicators `[Q11]` | preserve raw RX completion and compare payload boundaries; reject if field never varies or maps to unrelated data |
| 5 | **Peregrine’s hidden channel format is an ancestor of later Qualcomm CFR exponent/real/imag tone packing.** | same vendor and function lineage; later implementation uses compressed complex tones `[Q15][A01]` | decode captured data under known phase rotations; reject if packing cannot reproduce observed channels |
| 6 | **`ADCCAPTURE` is compiled into an AR9888 manufacturing image even though its registration is absent from the visible target path.** | shared ABI and target manufacturing framework coexist `[Q07][Q09]` | enumerate commands/link symbols and issue safe request; explicit unsupported response plus no handler xref falsifies for that image |
| 7 | **`PHYDBGDUMP` is the intended public manufacturing route to the same BB debug/sample memory referenced by descriptors.** | symbolic command and exact descriptor debug memory are semantically aligned `[Q07][Q11]` | recover handler/response and correlate with capture; absence across exact builds rejects |
| 8 | **`GENWAVEFORM` returns internally generated reference samples used for calibration, not arbitrary TX samples.** | ABI accepts an index rather than samples `[Q10]` | compare responses across indices and RF states; host-selected sample injection failure supports, a writable table refutes |
| 9 | **The 5/10 MHz mode is a complete bidirectional PHY mode on QCA988x, not only a factory spectral mode.** | exact AR9888 mode values and channel/timing code exist `[Q03][Q04]` | run two exact-family UTF or patched peers; failure to decode after validated TX spectrum rejects |
| 10 | **Half/quarter rate changes clock/timing and filters while retaining the standard OFDM subcarrier count.** | typical Atheros lineage and exact mode naming, but not yet proven here | external IQ measures subcarrier spacing/symbol duration; contrary FFT/subcarrier count rejects |
| 11 | **There is no hidden rate-code value above VHT MCS9 in the normal `series_bw` descriptor.** | exact field enumeration ends at standard rates `[Q13]` | exhaust reserved values in shielded UTF with external VSA; a stable nonstandard constellation refutes |
| 12 | **LDPC LLR-scaling registers can reduce PER at a narrow SNR/interference range without changing the code.** | exact writable scaling/latency fields exist `[Q14]` | controlled cabled PER sweep; no statistically repeatable region rejects |
| 13 | **Forced phase/frequency correction controls can compensate systematic oscillator error between fixed CPE/AP pairs.** | exact baseband timing/phase controls exist `[Q14]` | external CFO/phase measurement and paired PER/EVM test; no improvement or instability rejects |
| 14 | **CCA/correlator controls can recover exposed-node airtime while preserving hidden-node protection when conditioned on topology.** | exact controls plus fixed topology knowledge `[Q03][Q14]` | controlled desired/interferer matrix; reject if gains always trade into unacceptable collision/loss |
| 15 | **Ubiquiti’s polling scheduler uses target TSF/descriptor timing rather than host-timed WMI grants.** | proprietary logic resides in target and exact descriptors carry time filters `[R19][Q12]` | external jitter measurement and handler trace; host-correlated high jitter would reject |
| 16 | **The `0x9044/0x9045` native-rate-schedule message conveys per-peer retry series close to `series_bw` layout.** | name/behavior and exact retry descriptor semantics align `[R19][Q13]` | decode payload against observed OTA rates; persistent mismatch rejects |
| 17 | **`UBNT_POLL_MEM_ALLOC` allocates a scheduler/grant ring in target DRAM that can be identified in a coredump.** | exact firmware string and known target DRAM dump `[R19][L04]` | compare polling off/on memory and xrefs; no allocation/object change rejects |
| 18 | **AP/STA/PTP Ubiquiti images share most WLAN code and differ in a small scheduler/task layer that can be isolated by cross-version diff.** | role-specific binaries and shared lineage `[R19]` | function-hash diff; broad unrelated divergence rejects the “small layer” claim |
| 19 | **Candela’s Wave-1 firmware retained dormant Qualcomm debug/channel capture handlers because it derives from 10.1 target source.** | CT modified exact target source `[C01][R13]` | string/service/behavior comparison against stock and UTF; absence rejects |
| 20 | **A controlled target crash contains task names, queue heads and timer objects sufficient to bootstrap scheduler RE.** | coredump DRAM and target debug infrastructure `[L04][L05]` | parse repeated dumps; absence of stable structures/strings rejects |
| 21 | **Normal target firmware strips rich PPDU fields before HTT rather than the hardware never producing them.** | exact hardware descriptor versus sparse host metadata `[Q11][R16]` | target instrumentation before HTT; if fields are zero at source, reject |
| 22 | **The compressed-V/SVD path can be used as a rank/channel-quality oracle even if explicit beamforming is disabled.** | exact DMA/SVD descriptor path `[Q12]` | trigger V generation and correlate singular/rank metrics with external H; no accessible output rejects |
| 23 | **Per-packet TPC/chain fields are physically honored below the host API.** | exact TX descriptor contains TPC/chain controls `[Q13]` | UTF/target descriptor injection plus VSA power/chain observation; overwrite/no effect rejects |
| 24 | **Fixed test tones and known payload patterns are sufficient to derive a PA nonlinearity model that improves legal-power EVM through calibration tables.** | UTF tone/pattern/gain/PAPRD controls `[Q03][Q05]` | fit on one set, test held-out powers/temperatures; no predictive improvement rejects |
| 25 | **External SDR can reconstruct airMAX grant timing and CPE synchronization without decoding proprietary control payload semantics.** | time-domain transmission edges and known topology are observable | capture multi-node OTA and cluster edges; inability to assign peers/slots rejects practical utility |
| 26 | **A 10–20 ms host queue-gated hybrid scheduler will outperform pure CSMA on the known hidden-node sector, but plateau below target polling.** | hMAC and openMAX hidden-node result `[P09][R02]` | randomized comparison; no gain rejects, matching fine scheduler refutes plateau |
| 27 | **A target-resident scheduler can use sub-ms slots with materially lower guard overhead than host queue gating.** | target timers/PCU plus SRT-WiFi placement lesson `[R19][P10]` | external timing; jitter/guard requirement comparable to host rejects |
| 28 | **The best scheduler is link-state/topology conditional rather than one static DL/UL ratio.** | fixed WISP topology varies in queues, hidden nodes and channel state; airOS exposes static ratio `[R20]` | holdout comparison against best static schedules; no robust gain rejects |
| 29 | **Per-peer aggregation policy can reduce p99 latency without losing sector goodput if BA/retry burst state is exposed.** | target owns aggregation/retry; current host granularity is coarse `[R21]` | target instrumentation and constrained controller; throughput loss or no tail gain rejects |
| 30 | **An autonomous controller can beat the frozen airMAX scheduler only after target-level observation and actuation are added.** | IteRate’s gains depend on fine hooks; current host lacks them `[P08][R03]` | compare host-only autonomous search versus target-hook search; no incremental gain rejects |
| 31 | **A “null” candidate will sometimes appear better under current gatekeeper because RF drift is not modeled.** | current independent-group test and small samples `[R24]` | run identical config under fake A/B labels repeatedly; false-positive rate above nominal confirms |
| 32 | **Correcting the 40 MHz normalization bug will change candidate rankings in mixed-width experiment history.** | hard-coded denominator `[R23]` | recompute with real widths; identical ranking rejects impact but bug remains |
| 33 | **The persistent forced-scan sawtooth is a target/PCIe state-machine failure that can be localized through coredump differences.** | reproducible fault requires reset `[R02][R04]` | before/after target memory and CE register comparison; no stable difference weakens |
| 34 | **Some “unsupported” capabilities are present in UTF but absent in production solely to reduce attack surface/size, not due to silicon.** | factory firmware has broader controls than production `[Q03][L01]` | same hardware responds under UTF but not production; opposite result rejects |
| 35 | **If channel dump, ADC capture, mapper tables and arbitrary TX all fail, the remaining physical headroom is overwhelmingly MAC/implementation gap rather than new signaling.** | exact descriptor/register evidence defines the plausible gates | completion of all four negative tests falsifies hidden-PHY branch and confirms this operational conclusion |

---

# 14. Five highest-value possible discoveries

## 14.1 Exact per-tone 2×2 channel dump is recoverable

**Why it changes the envelope:** It would give openMAX an internal channel oracle: rank, eigenvalues, frequency selectivity, link-specific beamforming information, true channel-capacity reference and far better autonomous-state input than RSSI. It could also expose whether apparently weak links are noise-limited, interference-limited or rank-deficient. `[Q11][Q12]`

**Falsification:** Trigger the exact descriptor path in a cabled known channel, scan all mapped BB/target memory and preserve raw PPDU completion. If no packet-correlated dump exists across validated modes, or the data contains no recoverable channel response under controlled phase/amplitude changes, reject.

## 14.2 Raw ADC/sample-RAM capture exists on Peregrine

**Why it changes the envelope:** Raw RX samples would permit offline receiver research, independent synchronization/channel estimation, neural receivers, impairment diagnosis and exact comparison of QCA hardware decisions with alternative algorithms—even if the on-chip receiver cannot be replaced. `[Q09]`

**Falsification:** Prove command enumeration and build inclusion, then issue bounded captures under terminated input, known tone and modulated input. Unsupported handler plus exhaustive no-sample-memory result across known test images rejects the accessible primitive.

## 14.3 openMAX can rebuild and safely execute modified exact target firmware

**Why it changes the envelope:** This unlocks scheduler/timer/queue/descriptor instrumentation and makes the target—not merely Linux—the experimental platform. It is prerequisite to a modern custom PTMP MAC. `[Q01][Q02][R19]`

**Falsification:** Reconstruct the exact UTF build first. If a one-line inert change cannot be compiled, loaded, executed and repeatedly recovered on sacrificial hardware after toolchain/board-data issues are resolved, the open rebuild route is blocked. Binary patching remains a separate path.

## 14.4 A writable mapper/pilot/FEC table or arbitrary symbol/IQ injection path exists

**Why it changes the envelope:** This is the gate from “better 802.11 policy” to genuinely new signaling—geometric shaping, learned pilots, alternate coding or waveform search. No current evidence establishes it. `[Q13][Q14]`

**Falsification:** Exhaust exact BB registers/RAM symbols, factory handlers and reserved descriptor modes. Attempt one reversible standard-compatible mapper/pilot mutation. If no writable table/path exists and only standard MCS/test tones are accepted, reject.

## 14.5 Target timers and PCU queues support a programmable low-jitter sub-ms PTMP scheduler

**Why it changes the envelope:** A scheduler designed with complete topology/queue/channel knowledge could attack the largest real outdoor PTMP losses—hidden nodes, near/far unfairness, guard overhead, retry storms and static DL/UL allocation—without changing the PHY. `[R19][P10]`

**Falsification:** Implement the smallest one-link periodic gate in target context and observe with external IQ. If TX start jitter and uncontrolled CSMA require guards comparable to coarse host scheduling, or queue release cannot be tied to TSF/hardware timers, reject the fine-TDMA branch.

---

# Overall conclusion

The most defensible current model is:

- **The RF/PHY datapath is substantially fixed hardware, but richly parameterized.**
- **The MAC, rate/retry/aggregation policy, timers, descriptors and diagnostic exports are substantially target-firmware controlled.**
- **The exact silicon contains at least one hidden channel-capture primitive that normal ath10k does not expose.**
- **No evidence yet supports arbitrary waveform transmission, free-form constellations, custom pilots or custom FEC on QCA988x.**
- **The project’s next scientific milestone is not another host configuration sweep. It is a controlled proof or refutation of channel-dump access, exact UTF capability and custom target execution.**

If those gates are negative, openMAX will have proved that the exploitable boundary is a high-quality 802.11ac PHY plus a replaceable MAC/policy layer. If they are positive, the boundary moves—first toward internal channel measurement, then potentially toward target-resident deterministic scheduling, and only with much stronger evidence toward new physical signaling.


---

# Source ledger

The report uses compact source IDs in the body so that dense tables remain readable. URLs below are pinned where a stable commit exists. Tier labels follow the hierarchy requested in the brief; a source can support only the claim actually attributed to it.

## openMAX repository and measurements — principally Tier 1

- **[R01]** openMAX README, pinned snapshot: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/README.md
- **[R02]** Current project state: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/docs/CURRENT_STATE.md
- **[R03]** QCA988x control boundary: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/docs/QCA988X_CONTROL_BOUNDARY.md
- **[R04]** Experiment ledger: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/docs/EXPERIMENTS.md
- **[R05]** Decision ledger: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/docs/DECISIONS.md
- **[R06]** Stage 7 multivendor PTMP report: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/docs/STAGE7_MULTIVENDOR_PTMP_REPORT.md
- **[R07]** Stage 8 adaptive controller and sector simulation: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/docs/STAGE8_ADAPTIVE_CONTROLLER_AND_SECTOR_SIM.md
- **[R08]** Stage 9 20 MHz, ratemask, CoTSQ and procd: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/docs/STAGE9_20MHZ_RATEMASK_COTSQ_AND_PROCD.md
- **[R09]** Stage 10 stock airOS 8 interoperability and revert: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md
- **[R10]** Stage 11 XC, Rocket Prism and airPrism reverse engineering: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md
- **[R11]** Stage 11 LTU modulation, 4096-QAM and architecture reverse engineering: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md
- **[R12]** Stage 12 full OpenWrt sector and UISP bridge: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/docs/STAGE12_FULL_OPENWRT_SECTOR_AND_UISP_BRIDGE.md
- **[R13]** ath10k-CT firmware deep dive: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/knowledge/ATH10K_CT_FIRMWARE_DEEP_DIVE.md
- **[R14]** Knowledge-base QCA988x control boundary: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/knowledge/QCA988X_CONTROL_BOUNDARY.md
- **[R15]** Autonomous wireless research engine: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/knowledge/AUTONOMOUS_WIRELESS_RESEARCH_ENGINE.md
- **[R16]** Spectral and CSI analysis: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/knowledge/SPECTRAL_AND_CSI_ANALYSIS.md
- **[R17]** Real-hardware literature: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/knowledge/REAL_HARDWARE_LITERATURE.md
- **[R18]** Outdoor PTMP TDMA versus CSMA: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/knowledge/PTMP_OUTDOOR_TDMA_VS_CSMA.md
- **[R19]** Radio-firmware analysis: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/knowledge/RADIO_FIRMWARE_ANALYSIS.md
- **[R20]** airOS control surface: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/knowledge/AIROS_CONTROL_SURFACE.md
- **[R21]** UMAC datapath: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/docs/UMAC_DATAPATH.md
- **[R22]** New-experiment backlog: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/docs/OPENMAX_NEW_EXPERIMENTS.md
- **[R23]** Experiment metric schema: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/analysis/metrics/schema.py
- **[R24]** Autonomous regression gatekeeper: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/analysis/regression_gate/gatekeeper.py
- **[R25]** Xtensa qualification tooling and explicit limitations: https://github.com/wolverin0/openmax/blob/0cce9cf76d990861fbd8a78d1f9dfa357df5b369/tools/research/qualify_xtensa.py

## Exact Qualcomm-derived AR9888/Peregrine sources — Tier 1

All links below are pinned to `SpaceExplorationTechnologies/starlink-wifi@1d585ee8909bf7bab4391c0c52d8a9d44137b3bb`.

- **[Q01]** Target build selecting `AR9888`: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/target/Makefile
- **[Q02]** UTF target build composition: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/target/utf/Makefile
- **[Q03]** Exact target test-command implementation (`tcmd.c`): https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/target/utf/tcmd_utf/tcmd.c
- **[Q04]** AR988x test-command ABI: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/testcmd_ar988x.h
- **[Q05]** ART/UTF common definitions, rates and measurements: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/art_utf_common.h
- **[Q06]** QC98xx ART/UTF calibration and OTP definitions: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/art_utf_qc98xx.h
- **[Q07]** Qualcomm TLV2 command/response dictionary: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/common/tlv2p0/include/cmdRspParmsDict.h
- **[Q08]** Target TLV2 command processor, including bounded register/memory operations: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/target/utf/commonUTF/cmdProcessTlv2.c
- **[Q09]** Shared `ADCCAPTURE` ABI: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/common/tlv2p0/include/cmdAdcCaptureHandler.h
- **[Q10]** Shared `GENWAVEFORM` ABI: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/common/tlv2p0/include/cmdGenWaveformHandler.h
- **[Q11]** Exact AR9888 v2 RX PPDU-end descriptor, including channel-dump, H-info, EVM and timestamps: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h
- **[Q12]** Exact AR9888 v2 TX PPDU-start descriptor, including `bb_capture_channel` and compressed-V pointer: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/tx_ppdu_start.h
- **[Q13]** Exact AR9888 v2 series/rate descriptor: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/series_bw.h
- **[Q14]** Exact AR9888 v2 baseband register definitions: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/extra/hw/bb_lc_reg.h
- **[Q15]** Later-ath10k CFR host implementation, used only as labeled cross-chip lineage: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/qca/feeds/wlan-open/mac80211/patches/a00-917-ath10k-channel-state-information.patch

## Linux ath10k sources — Tier 1

All links below are pinned to Linux commit `5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f`.

- **[L01]** ath10k testmode loader and transport: https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/testmode.c
- **[L02]** ath10k testmode netlink ABI: https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/testmode_i.h
- **[L03]** Bootloader Messaging Interface implementation: https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/bmi.c
- **[L04]** ath10k crash-dump regions and machinery: https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/coredump.c
- **[L05]** target host-interest addresses: https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/targaddrs.h

## Vendor and hardware documentation — Tier 2

- **[C01]** Candela Technologies ath10k firmware page; exact Wave-1 chipset list and NDA-source modification statement: https://www.candelatech.com/ath10k.php
- **[H01]** Qualcomm QCA9880 product page: https://www.qualcomm.com/networking-infrastructure/products/qca9880
- **[H02]** SparkLAN QCA9882 2T2R module specification: https://www.sparklan.com/product/wpeq-257acn-qca9882-2t2r-ap-mode-module/

## Learned/programmable PHY and custom-MAC research

- **[P01]** Dörner et al., “Deep Learning-Based Communication Over the Air,” real SDR OTA — Tier 3/4: https://arxiv.org/abs/1707.03384
- **[P02]** Felix et al., “OFDM-Autoencoder for End-to-End Learning of Communications Systems” — Tier 5 for the reported comparison: https://arxiv.org/abs/1803.05815
- **[P03]** Goutay et al., “End-to-End Learning of OFDM Waveforms with PAPR and ACLR Constraints,” simulation — Tier 5: https://arxiv.org/abs/2106.16039
- **[P04]** Zhang et al., “Artificial Intelligence-aided Receiver for a CP-Free OFDM System,” including OTA prototype — Tier 3/4: https://arxiv.org/abs/1903.04766
- **[P05]** Li et al., “Learning to Estimate: A Real-Time Online Learning Framework for MIMO-OFDM Channel Estimation” — Tier 3/4: https://arxiv.org/abs/2305.13487
- **[P06]** Cammerer et al., “A Neural Receiver for 5G NR Multi-user MIMO,” hardware-in-loop — Tier 3/4: https://arxiv.org/abs/2312.02601
- **[P07]** Luostari et al., “Adapting to Reality: Over-the-Air Validation of AI-Based Receivers” — Tier 3/4: https://arxiv.org/abs/2408.04182
- **[P08]** Lynch et al., “IteRate: Autonomous AI Synthesis of In-Kernel eBPF Wi-Fi Rate Control Algorithms,” real 58-node testbed — Tier 4: https://arxiv.org/abs/2605.02542
- **[P09]** Zehl et al., “hMAC: Enabling Hybrid TDMA/CSMA on IEEE 802.11 Hardware,” ath9k real hardware — Tier 4: https://arxiv.org/abs/1611.05376
- **[P10]** Yun et al., “RT-WiFi on Software-Defined Radio: Design and Implementation” (SRT-WiFi), FPGA/SDR testbed — Tier 3/4: https://arxiv.org/abs/2203.10390
- **[P11]** Neufeld et al., “SoftMAC — Flexible Wireless Research Platform,” primary project bibliography/abstract: https://resili.net/softmac.html
- **[P12]** Djukic and Mohapatra, “Soft-TDMAC,” IEEE INFOCOM 2009: https://doi.org/10.1109/INFCOM.2009.5062104
- **[P13]** Patra et al., “WiLDNet,” real long-distance deployment, USENIX NSDI 2007 — Tier 3: https://www.usenix.org/conference/nsdi-07/wildnet-design-and-implementation-high-performance-wifi-based-long-distance
- **[P14]** Cheng et al., “Det-WiFi,” commodity AR9287/ath9k industrial testbed — Tier 3: https://doi.org/10.1155/2017/4943691
- **[P15]** openwifi full-stack FPGA/SDR source: https://github.com/open-sdr/openwifi
- **[P16]** Jiao et al., “Openwifi CSI fuzzer,” real FPGA/SDR implementation — Tier 3/4: https://arxiv.org/abs/2105.07428
- **[P17]** Tinnirello et al., “Wireless MAC Processors,” reflashed Broadcom commodity firmware — Tier 3: https://doi.org/10.1109/INFCOM.2012.6195488
- **[P18]** European Commission WiSHFUL project report: https://cordis.europa.eu/project/id/645274/reporting
- **[P19]** ORCA openwifi full-stack time-slicing demonstration: https://www.orca-project.eu/orcas-openwifi-demo/index.html
- **[P20]** Lin et al., “GR-WiFi: A GNU Radio based WiFi Platform with SU/MU-MIMO Capability,” real-world and simulation experiments — Tier 4: https://arxiv.org/abs/2501.06176

## External measurement equipment — official vendor sources, Tier 2

- **[E01]** Ettus USRP B210: https://www.ettus.com/all-products/ub210-kit/
- **[E02]** Ettus X300/X310 knowledge base: https://kb.ettus.com/X300/X310
- **[E03]** Ettus USRP N320: https://www.ettus.com/all-products/usrp-n320/
- **[E04]** Great Scott Gadgets HackRF One: https://greatscottgadgets.com/hackrf/one/
- **[E05]** Nuand bladeRF 2.0 micro: https://www.nuand.com/bladerf-2-0-micro/
- **[E06]** Rohde & Schwarz 802.11ac wideband signal-testing application note: https://www.rohde-schwarz.com/ca/applications/wlan-ieee-802.11ac-wideband-signal-testing_56279-42113.html
- **[E07]** Signal Hound SM200C: https://signalhound.com/products/sm200c-20-ghz-real-time-spectrum-analyzer-with-10gbe/
- **[E08]** Keysight 802.11ac design/test overview: https://www.keysight.com/us/en/assets/7018-03661/flyers/5991-1213.pdf

## Information-theoretic and measurement foundations

- **[T01]** Shannon, “Communication in the Presence of Noise”: https://doi.org/10.1109/JRPROC.1949.232969
- **[T02]** Telatar, “Capacity of Multi-antenna Gaussian Channels”: https://doi.org/10.1002/ett.4460100604
- **[T03]** Shafik et al., EVM-to-SNR relationship and limitations: https://eprints.soton.ac.uk/263126/

## Cross-chip lineage and autonomous experimentation

- **[A01]** Later Qualcomm CFR API/packing source, explicitly not exact QCA988x proof: https://android.googlesource.com/kernel/msm-modules/wlan-fw-api/+/refs/tags/android-11.0.0_r0.72%5E%21/
- **[A02]** Karpathy `autoresearch`: https://github.com/karpathy/autoresearch
- **[A03]** Sui et al., SafeOpt: https://proceedings.mlr.press/v37/sui15.html
- **[A04]** Fiedler et al., practical limitations of SafeOpt-style guarantees: https://arxiv.org/abs/2501.13697

---

## Evidence audit note

The most important new exact-family claims in this report—AR9888 target build support, factory/test controls, the channel-dump trigger/status path, rich RX metadata, standard-rate descriptor limits and parameterized baseband registers—derive from **Q01–Q14**, not from later QCA9888/QCA9984 assumptions. The CFR transport in **Q15/A01** is used only as a labeled architectural clue. Where an exact handler, memory address, binary format, writable table or real-hardware result could not be established, the report says **UNKNOWN** and converts the gap into an experiment.
