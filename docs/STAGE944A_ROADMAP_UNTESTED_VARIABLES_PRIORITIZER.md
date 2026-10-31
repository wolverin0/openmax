<!-- doc-head: Stage 944A offline roadmap prioritizer: ranks untested variables from EXTENSIVE_UNTESTED_VARIABLES_AND_GROUND_UP_ROADMAP.md by need for real-hardware measurement, using stage887a/888a evidence classes; read before choosing next bench campaign -->

# Stage 944A - Roadmap Untested-Variables Prioritizer

- **Evidence class**: `ROADMAP_PRIORITIZATION` (offline; no radios, SSH or firmware touched; `live_devices_touched=false`)
- **Tool**: `tools/verify/build_stage944a_roadmap_untested_variables_prioritizer.py`
- **Receipt**: `artifacts/autoresearch/stage944a_roadmap_untested_variables_prioritizer.json`
- **Test**: `tests/test_stage944a_roadmap.py`
- **Items parsed/prioritized**: 26 / 26

## Heuristic

`priority_score = importance + evidence_gap`

- importance: roadmap section weight (1 discovery, 2 matrix variable, 3 execution queue) plus a queue-position bonus.
- evidence_gap: 3 if no related receipt or none is `CONFIRMED_LIVE_BENCH`; 1 if 1-2 live-bench receipts; 0 if 3 or more.
- Related receipts are found by keyword match on receipt filenames in stage887a (`per_receipt`).

## Evidence classes (kept separate)

- `CONFIRMED_LIVE_HARDWARE` (887a: `CONFIRMED_LIVE_BENCH`): measured on a physical radio.
- `CONFIRMED_STATIC_BINARY`: firmware/binary analysis only, no device execution.
- `SIMULATED_MODEL_ONLY`: SimPy/pymoo/analytic output; never counts as measurement.
- `UNKNOWN`: classifier had insufficient signal (73.3% of the corpus in stage888a).

## Limits (do not over-read)

- Filename keyword matching is coarse: broad keywords (e.g. `ltu`) can match unrelated live-bench receipts and lower a score; an item with no keyword match is scored as unevidenced, which may over-rank it.
- 887a is a first-pass triage, not a per-champion provenance fiche.

## Ranked items (top 15)

| # | Score | Evidence class | Item |
| :-: | :-: | :--- | :--- |
| 1 | 7.0 | UNKNOWN | S17B-R3: Split-Frequency (TX freq != RX freq on AD9361 SDR) under co-channel interference from 5180 MHz AC sec |
| 2 | 7.0 | SIMULATED_MODEL_ONLY | S17B-R4: High-order modulation (10X 1024-QAM vs 12X 4096-QAM) on matched v2.4.0 pair. |
| 3 | 5.0 | UNKNOWN | PB-030 Sub-20 MHz (5 MHz Quarter-Rate / 10 MHz Half-Rate): +3 dB / +6 dB SNR gain + 2x/4x OFDM symbol length f |
| 4 | 5.0 | UNKNOWN | Per-Peer 4-Series WMI Rate/Retry Table (0x9044 + series_bw LDPC/STBC/SGI): Force hardware retry fallback from  |
| 5 | 5.0 | UNKNOWN | Independent Split-Frequency (TX != RX LO on AD9361 SDR): Test asymmetric TX/RX center frequencies to dodge asy |
| 6 | 5.0 | SIMULATED_MODEL_ONLY | AirSelect Frequency-Hopping TDD Coordination: Test rapid 2-channel coordinated hopping under pulsed interferen |
| 7 | 5.0 | UNKNOWN | Dynamic Per-CPE txchainmask Auto-Daemon (Stage 16B port): Closed-loop daemon that monitors per-chain RSSI delt |
| 8 | 5.0 | UNKNOWN | Asymmetric TDD Duty-Cycle (75/25, 67/33, 50/50) vs Cyclic Prefix (cp=4/8/16): Joint optimization of TDD split  |
| 9 | 4.5 | CONFIRMED_LIVE_BENCH(partial) | Stage 19 (T-S19-ROCKET-PRISM-AIRPRISM-AND-MODE-B-AP) — Rocket Prism 5AC Gen2 Active AirPrism + ubnt_poll AP Au |
| 10 | 4.25 | CONFIRMED_LIVE_BENCH(partial) | Stage 20 (T-S20-CLOSED-LOOP-ADAPTIVE-PHY-DAEMON) — Unified Closed-Loop Daemon Combining PB-060 Surrogate + Sta |
| 11 | 4.0 | UNKNOWN | Ubiquiti's Hidden WMI Tunnel (0x9064 vs 0x9070) & 51-Entry Xtensa Jump Table at 0x009b2037 (PB-010) |
| 12 | 4.0 | UNKNOWN | Asymmetric SIMO-TX / 2x2-MRC-RX (txchainmask=2, rxchainmask=3) + ubnt_ewma_delegate_on=1 on Tree-Obstructed Li |
| 13 | 4.0 | CONFIRMED_LIVE_BENCH | Stage 17B (T-S17B-LTU-LITE-OTA-SQ-AND-12X) — Live OTA LTU-Lite #1 AP -> LTU-Lite #2 CPE + LTU-Rocket: |
| 14 | 4.0 | CONFIRMED_LIVE_BENCH | S17B-R1: LTU-Lite PtP AP (wireless_mode=ptp, role=ap) vs LTU-Lite PtMP AP (wireless_mode=ptmp, role=ap, ptmp_m |
| 15 | 4.0 | CONFIRMED_LIVE_BENCH | S17B-R2: LTU-Lite Micro-AP Short-Queue (ptmp_max_cpe=4 SQ mode) vs full queue (ptmp_max_cpe=0). |

Full list with rationale and matched keywords is in the receipt JSON.
