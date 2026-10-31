<!-- doc-head: Stage 1230A KB v2 reconciles the 117-thread Ubiquiti forum KB (1187A) with three static-binary docs (1190A, 1191A, 1214A): 11 binary facts, 25 root-cause actions, per-thread fact links, retired constants; offline, static facts only, forum symptoms unverified -->
# Stage 1230A - Community KB v2: binary reconciliation

Status: built offline, `live_devices_touched=false`, no network. Evidence classes used:
`CONFIRMED_STATIC_BINARY` (decompile facts), `FORUM_REPORTS_UNVERIFIED_BY_LIVE_HARDWARE` (threads),
`HYPOTHESIS`, `SIMULATED_MODEL_ONLY`, `CONFIRMED_LIVE_HARDWARE` (unchanged from v1, RC-09 only).
Artifact: `artifacts/research/ubiquiti_community_kb_v2_reconciled_1230a.json` (schema_version 2).
Input: `artifacts/research/ubiquiti_community_m_ac_ltu_field_issues_kb.json` (KB v1, Stage 1187A), left byte-identical.
Builder: a throwaway script kept outside the repo; its assertions are listed in section 6.

## 1. What changed versus 1187A

- KB v1 (schema 1, 117 threads, 25 root causes RC-01..RC-25) is deep-copied; nothing is dropped or edited,
  including the embedded RC text that still says "unreconciled" (RC-04) and "25 vs 60" (RC-13).
  Corrections are recorded in `root_cause_reconciliation[*].note`, not by rewriting v1 content.
- Added keys: `derived_from` (v1 path, sha256 `bd8f3773...d756`, 117 threads), `binary_facts` (11),
  `root_cause_reconciliation` (25 entries), per-thread `binary_fact_ids` (69 threads), `reconciliation_stats`.
- 1187A listed two open conflicts (its line 140). Stage 1214A settled both from the binaries; they are carried here as facts.
- Two things the 1187A schema already had are kept apart on purpose:
  `evidence_class` = how well the evidence supports the forum SYMPTOM; `mechanism_fact_class` = how well the BINARY FACT is established.
  Every RC fact from a decompile already had `mechanism_fact_class = CONFIRMED_STATIC_BINARY` in v1.
  So this stage upgrades NO evidence class: `evidence_class_upgrades = 0`. It adds, corrects and bounds facts.

## 2. Binary facts (all `CONFIRMED_STATIC_BINARY`; each string was matched against the doc text by the builder)

| ID | Module (arch) | Fact | Doc | Link to symptom |
| :--- | :--- | :--- | :--- | :--- |
| BF-1190A-01 | `ubnt_poll_host.ko` (MIPS32 BE) | `ubnt_poll_host_check_sta` (0x1860) expires a peer at 120000 ms and calls `ieee80211_free_node`; NOT `ieee80211_kick_node`, NOT `ath_kickout_node_notify` | 1190A s5 | doc: `INFERRED` |
| BF-1190A-02 | same | `init_ptmp_netconf`: `idx = bw_mhz - 10`, `sltiu 0x1f`, table `.rodata+0x8a4`; 29-30 MHz -> `_ht30`; 11-28 and 31-39 MHz -> `_ht20`; 40 -> `_ht40`; 80 MHz / outside 10..40 -> `_ht20` default; no 80 MHz profile | 1190A s6 | selector confirmed, starvation `INFERRED` |
| BF-1190A-03 | same | `sta_remove_oldest` (capacity eviction) only in 8.7.25 builds; 8.7.4-cs and 8.7.11 have 120 s expiry with no capacity relief (8.7.11 label is `INFERRED` from a directory name) | 1190A s5, s7 | version-specific |
| BF-1190A-04 | same | Negative: 0 `mcs`/`1x`/`vht` tokens, no rate selector; a 1x lock is not produced or cleared by this module | 1190A s4, s10 | symptom `UNKNOWN` |
| BF-1190A-05 | same | 38 slot/guard sysctl names (`ff_guard_units`, `cbp_dur`, `down_dur`, `ff_frame_dur`, ...); names only | 1190A s8 | tunable surface only |
| BF-1191A-01 | `ame_core.ko` (ARM, LTU 2.4.2) | `mcsDnThreshold_timer = 1` (.data+0x12d8) vs `mcsUpThreshold_timer = 90` (.data+0x12dc): 90x asymmetry | 1191A s5 | doc: `INFERRED` |
| BF-1191A-02 | same | ATPC is spelled autopwr: 0 `atpc` hits, 38 autopwr symbols, `auto_pwr_decision` 5636 B at .text+0x24d74 | 1191A s3, s4 | none shown |
| BF-1191A-03 | same | `mcs_ceiling_toggle_txpwr` compares desired TX power with `get_mcs_max_pwr`: a power limit can impose an MCS ceiling | 1191A s6, s9 | mechanism only |
| BF-1191A-04 | same | Negative: 0 deauth/disconnect/aging/storm symbols, `transitions_recovered` 0, auto-MCS is not a state machine | 1191A s4, s7, s8 | storm unanswerable |
| BF-1214A-01 | `ubnt_poll_host.ko` | Missing-poll panic timer is ONE constant (patch site 0x07c08 on 8.7.25 builds): `(jiffies - uph_dev+0x288)*1000 >= 0x01c9c768` = 30,001,000, ~30 s if jiffies are ms (HZ inferred) | 1214A | supersedes 70A |
| BF-1214A-02 | `ame_core.ko` | `penaltyThreshold = 60` (0x3c; .data 0x12d2 CPE, 0x12ee AP) | 1214A | supersedes Stage 12 |

Offsets differ per build: the compare constant is at lui/ori text offsets 0x7bf8 (8.7.25) and 0x7930 (8.7.4-cs, 2XC 8.7.11) per
`artifacts/verification/stage1214a_binary_constants_reconciliation.json`; 0x07c08 is the 8.7.25 patch site only.
BF-1190A-01 and BF-1214A-01 are DIFFERENT timers in the same module (peer inactivity expiry vs missing-poll panic). Do not merge them.

## 3. Root-cause reconciliation (25 of 25)

Actions: strengthened 4, corrected 2, unchanged 19, new_hypothesis 0. No new RC was created: the check_sta and bandwidth
facts attach to existing RCs (RC-04, RC-01/02) because those RCs already name the functions or the symptom class.
`prev` = v1 `evidence_class`; `now` = reconciled; both columns are the symptom-link class. Mechanism class is in the JSON.
Rule kept for the gate: `unchanged` implies an empty `binary_fact_ids`. The two negative facts (BF-1190A-04, BF-1191A-04) are mentioned in the notes of RC-03/17/18 as context but are not linked, because a negative result narrows a hypothesis rather than strengthening it.

| RC | Action | Facts | prev -> now | Change |
| :--- | :--- | :--- | :--- | :--- |
| RC-01 | strengthened | 1190A-02, -05, -04 | HYPOTHESIS -> HYPOTHESIS | profile selector decoded; guard names; no module-side 1x lock |
| RC-02 | strengthened | 1190A-02, -05, -04 | HYPOTHESIS -> HYPOTHESIS | same selector for ptmp_netconf; slot tunables named |
| RC-03 | unchanged | - | HYPOTHESIS -> HYPOTHESIS | context only: BF-1190A-04 (no rate selector) bounds it but is not linked |
| RC-04 | corrected | 1214A-01, 1190A-01, -03 | HYPOTHESIS -> HYPOTHESIS | "30 s vs 30 min" resolved to ~30 s; check_sta 120 s added as distinct function |
| RC-05 | unchanged | - | HYPOTHESIS | no new fact |
| RC-06 | unchanged | - | HYPOTHESIS | OpenWrt ath10k analogy only |
| RC-07 | unchanged | - | HYPOTHESIS | OpenWrt mac80211 analogy only |
| RC-08 | unchanged | - | HYPOTHESIS | no new fact |
| RC-09 | unchanged | - | CONFIRMED_LIVE_HARDWARE | dated OpenWrt bench; untouched |
| RC-10 | unchanged | - | HYPOTHESIS | no new fact |
| RC-11 | unchanged | - | HYPOTHESIS | no new fact |
| RC-12 | unchanged | - | HYPOTHESIS | below the .ko layer |
| RC-13 | corrected | 1214A-02, 1191A-01 | CONFIRMED_STATIC_BINARY -> same | 25 -> 60; timers get offsets; "rate FSM" wording loose |
| RC-14 | unchanged | - | CONFIRMED_STATIC_BINARY | no new fact |
| RC-15 | unchanged | - | HYPOTHESIS | different function than BF-1191A-03 |
| RC-16 | strengthened | 1191A-03, -02 | HYPOTHESIS -> HYPOTHESIS | power loop coupled to MCS ceiling |
| RC-17 | unchanged | - | HYPOTHESIS | context only: BF-1191A-04 (no storm vocabulary) bounds it, not linked |
| RC-18 | unchanged | - | HYPOTHESIS | context only: BF-1191A-04 bounds it, not linked; trigger still UNKNOWN |
| RC-19 | unchanged | - | HYPOTHESIS | no new fact |
| RC-20 | unchanged | - | HYPOTHESIS | no new fact |
| RC-21 | strengthened | 1191A-02, -03 | HYPOTHESIS -> HYPOTHESIS | named autopwr functions; ceiling coupling |
| RC-22 | unchanged | - | HYPOTHESIS | no new fact |
| RC-23 | unchanged | - | HYPOTHESIS | `eab_driver.ko` absent again (0 loose, 0 members) |
| RC-24 | unchanged | - | SIMULATED_MODEL_ONLY | no receipt added |
| RC-25 | unchanged | - | HYPOTHESIS | unclassified |

Where the premise needed adjusting: a "HYPOTHESIS -> CONFIRMED" jump for the silent-stall or ht20 facts does not exist.
Their mechanism class was already `CONFIRMED_STATIC_BINARY` in v1 (RC-04, RC-01); the causal link to forum symptoms
stays HYPOTHESIS, and the source docs themselves grade it `INFERRED`.

## 4. Per-thread links (only genuinely affected classes)

| Symptom class | Threads linked | Facts linked |
| :--- | :--- | :--- |
| silent_traffic_stall_while_associated | 17 of 17 | 1190A-01, 1190A-03, 1214A-01 |
| ptmp_single_cpe_tx_rate_collapse | 6 of 6 | 1190A-02, -04, -05 |
| m5_on_ac_mixed_mode_airtime_starvation | 10 of 10 | 1190A-02, -05 |
| ltu_modulation_stuck_4x_6x | 9 of 9 | 1191A-01, -02, -03, 1214A-02 |
| ltu_auto_frequency_atpc_glitch | 9 of 9 | 1191A-02, -03 |
| ltu_cpe_disconnect_storm | 18 of 18 | 1191A-04 (negative fact) |
| dfs_false_trigger, ethernet_100m_to_10m_negotiation_drop, ltu_udp_iptv_latency_spike, other_field_issue | 0 of 48 | none (honest zero) |

Total 69 of 117 threads carry `binary_fact_ids`. A link means "this fact is in the same symptom class", not "this fact caused the thread".
Linking is by class, not by reading each thread against the fact; per-thread causality is not claimed anywhere.

## 5. Conflicts retired and surviving

- RETIRED: Stage 70A "30 min / 1,800,000 ms" for the poll timer (`docs/STAGE70A_UBNT_POLL_AND_UPH_FULLREA_BINARY_DISSECTION.md` line 99).
  The immediate 0x001b7740 is absent as lui/ori or raw word in all six builds; 1214A reads it as a unit error.
- RETIRED: Stage 12 "penaltyThreshold = 25" (`..._CONTINUATION_dfb5467f5c_002.md` line 139), a transcription error; the byte is 0x3c = 60.
- SURVIVING: Stage 10 "~30 seconds" (it matches 0x01c9c768 if jiffies are ms) and Stage 249A "60". Stage 10's 35 s outage survival ran on a
  module patched at 0x7c08, so it never measured the unpatched timer (1214A caveat).
- Not conflicts: the 2000-jiffies (20 s) bmiss watchdog and the 2 s beacon-miss path are different timers.

## 6. Build assertions (re-runnable by Stage 1234A)

v1 sha256 identical before and after; v2 minus the added keys equals v1 (apart from schema_version, stage, generated_at);
thread ids and urls identical in order; every BF id referenced by a thread or RC exists; `affects_root_cause_ids` and
`binary_fact_ids` agree both ways; each linked thread's class is in the fact's `affects_symptom_classes`;
all fact strings are <= 300 chars; `tests/test_stage1187a_ubiquiti_community_scraper_and_kb.py` still passes (30 tests).

## 7. What is still unproven

- Every forum symptom stays `FORUM_REPORTS_UNVERIFIED_BY_LIVE_HARDWARE`. No thread was reproduced on hardware.
- These are static decompile facts. They show a mechanism exists in a build, not that it fires on a given unit.
- Silent stall: check_sta frees local state without a kick, but whether the peer is told is decided outside the module (1190A gap). Stage 70A/1214A add that a CPE with no polls panics after ~30 s, which is a reboot, not a silent stall.
- ht20 fallback: the selector is confirmed; that it equals "airtime starvation" needs a live slot trace (1190A gap).
- 90x hysteresis: the field values are exact; the link to the sticky 4x/6x lock is `INFERRED` and the timer units are not decoded.
- The 8.7.25-only `sta_remove_oldest` and the 8.7.14 / 8.7.25 forum silence mean no version-regression claim follows from these facts.
- HZ scaling of the 30 s figure is inferred. `eab_driver.ko` is absent, so no DMA-ring explanation is possible (RC-23).
- ARM/MIPS facts come from stock airOS and LTU 2.4.2 only; RC-06..RC-11 are OpenWrt builds and stay analogy.

## 8. Defects found in KB v1 and the source docs (not fixed here)

- RC-04 and RC-13 embedded text keeps the retired 30 min / 25 values; v1 is frozen, use v2 `root_cause_reconciliation`.
- RC-13 calls the auto-MCS logic a "rate FSM"; 1191A s8 finds no jump table and calls it a threshold-and-timer setter.
- `fw_versions_mentioned` is regex noise for some threads: UISP-style versions (1.4.x, 1.19.4) appear on airMAX threads, and one title "XC.v8.7.1" lacks 8.7.1 in the list. See Stage 1231A.
- 1191A prints `penaltyThreshold` at `.data+0x12d2` without saying it is the CPE build; 1214A supplies 0x12ee for the AP build.
- 1214A's evidence label `BINARY_CONSTANTS_RECONCILIATION` is outside the project's five classes; mapped here to `CONFIRMED_STATIC_BINARY`.
- `fw_versions_mentioned` also misses versions that appear only in a summary (thread with 6.3.6 and thread with 6.1.7 in their summaries); see Stage 1231A.

Related: `docs/STAGE1192A_BINARY_RE_TO_FIELD_SYMPTOM_SIGNATURES_MATRIX.md`, `docs/STAGE1239A_GUIA_MAESTRA_INTEGRACION_PWO_Y_CONCIENCIA_BILATERAL_ES.md` (Spanish guide, not duplicated), `docs/STAGE1231A_COMMUNITY_PTP_CO_LOCATION_AND_FIRMWARE_REGRESSION_ANALYSIS.md`.
