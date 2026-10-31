<!-- doc-head: Stage 1187A maps community.ui.com airMAX AC/M and LTU field-issue threads (unverified forum reports) to our static .ko reverse engineering and PWO rules, offline -->
<!-- /doc-head -->

# Stage 1187A - Ubiquiti community field issues (airMAX AC/M, LTU) vs our .ko RE and PWO rules

- **KB**: [`artifacts/research/ubiquiti_community_m_ac_ltu_field_issues_kb.json`](../artifacts/research/ubiquiti_community_m_ac_ltu_field_issues_kb.json) (schema 1, generated 2026-10-27T16:42:34Z)
- **Scraper**: [`tools/research/ubiquiti_community_forum_scraper.py`](../tools/research/ubiquiti_community_forum_scraper.py); **tests**: `tests/test_stage1187a_ubiquiti_community_scraper_and_kb.py`
- **Scope**: forum reports are cross-referenced against modules `ubnt_poll_host.ko`, `ath10k_core.ko`, `mac80211.ko`, `eab_driver.ko`, `ame_core.ko` (plus `umac.ko`/`ame_dev.ko`/`ame_dfs.ko` where a doc names them) and the PWO rule files `rules/*.js`.
- **Offline-only**: no radio, no ssh/ping/curl to any local address, no write to any device or PWO. Only public `community.ui.com` / `community.svc.ui.com` were read (unauthenticated, <= 2 req/s, `futuraMAX-research/1.0`). Catalog entries are advisory and recommend-only.

## 1. Method and evidence classes

Threads were fetched live from the site's own public API, read (not classified on title alone), and stored as short paraphrases (<= 300 chars) with URL, dates, tags, firmware versions and a staff-reply flag. No user names, emails, IPs, MACs or serials. Each root cause carries one `evidence_class` meaning how well the evidence supports **the symptom**, plus `mechanism_fact_class` meaning how well the **binary fact** itself is established.

| Class | Meaning |
| :--- | :--- |
| `FORUM_REPORTS_UNVERIFIED_BY_LIVE_HARDWARE` | Every forum claim. Not reproduced on our hardware. |
| `CONFIRMED_STATIC_BINARY` | A Stage doc states the decompile/ELF finding and it directly explains the symptom. |
| `CONFIRMED_LIVE_HARDWARE` | A dated live receipt demonstrates the symptom (scope stated). |
| `SIMULATED_MODEL_ONLY` | SimPy/pymoo model; no binary or hardware receipt. |
| `HYPOTHESIS` | Plausible mechanism; binary fact may exist but does not directly prove the symptom. |

Catalog: 25 root causes = 21 HYPOTHESIS, 2 CONFIRMED_STATIC_BINARY, 1 CONFIRMED_LIVE_HARDWARE, 1 SIMULATED_MODEL_ONLY.

## 2. Thread counts (from the KB)

Total 117 threads: airmax_ac 58, airmax_m 9, ltu 50. Classes with 0 threads are reported as 0, not padded.

| Symptom class | Family | Threads |
| :--- | :--- | ---: |
| `ptmp_single_cpe_tx_rate_collapse` | airmax_ac+airmax_m | 6 |
| `silent_traffic_stall_while_associated` | airmax_ac+airmax_m | 17 |
| `dfs_false_trigger` | airmax_ac+airmax_m | 22 |
| `m5_on_ac_mixed_mode_airtime_starvation` | airmax_ac+airmax_m | 10 |
| `ethernet_100m_to_10m_negotiation_drop` | airmax_ac+airmax_m | 12 |
| `ltu_modulation_stuck_4x_6x` | ltu | 9 |
| `ltu_cpe_disconnect_storm` | ltu | 18 |
| `ltu_auto_frequency_atpc_glitch` | ltu | 9 |
| `ltu_udp_iptv_latency_spike` | ltu | 10 |
| `other_field_issue` | any | 4 |

## 3. Symptom -> threads -> root cause -> workaround -> PWO action

**`ptmp_single_cpe_tx_rate_collapse`** (6 threads)
- Threads: [Station capacity drop](https://community.ui.com/questions/Station-capacity-drop/bb99fc75-3afe-4ec2-922f-5d7302b799d4); [One LBE 5 AC Gen2 station with decent signal but huge capacity/link potential d…](https://community.ui.com/questions/One-LBE-5-AC-Gen2-station-with-decent-signal-but-huge-capacity-link-potential-drops/9418df8a-3c1a-4085-b9e0-e42124e70dd8); [AP Rocket 5AC Lite -> 1 Station Nanobeam 5AC real throughput issue (all other o…](https://community.ui.com/questions/AP-Rocket-5AC-Lite-greater-1-Station-Nanobeam-5AC-real-throughput-issue-all-other-ok/e3436f88-00ea-4067-af1a-c408eda7298f)
- Root causes: RC-01 `ubnt_poll_host.ko` HYPOTHESIS; RC-02 `ubnt_poll_host.ko` HYPOTHESIS; RC-03 `ubnt_poll_host.ko` HYPOTHESIS
- Community workaround: Re-align, lower width, cap max TX rate, reboot CPE. Binary view: Plausible fits (retry-suppression default off, ATPC target); no live receipt ties either to a single-CPE collapse.
- PWO: MAX_TX_RATE_FLAPPING, LOW_CCQ, ATPC_NOT_ENABLED, EXCESSIVE_TX_POWER: recommend-only.

**`silent_traffic_stall_while_associated`** (17 threads)
- Threads: [6.1.9 - stops passing traffic on XW boadrs](https://community.ui.com/questions/6-1-9-stops-passing-traffic-on-XW-boadrs/6acda552-4216-420b-ba3c-b36638102b41); [LOSS of connected clients on Rocket Prism 5ac in AP Mode](https://community.ui.com/questions/LOSS-of-connected-clients-on-Rocket-Prism-5ac-in-AP-Mode/605e48bd-2f9b-4307-840d-73c5d2070244); [TDD Framing (Flexible new) stops passing traffic to/from stations](https://community.ui.com/questions/TDD-Framing-Flexible-new-stops-passing-traffic-to-from-stations/759a880e-e5d9-468d-bc68-723e8512126c)
- Root causes: RC-04 `ubnt_poll_host.ko` HYPOTHESIS; RC-10 `mac80211.ko` HYPOTHESIS; RC-11 `ath10k_core.ko` HYPOTHESIS
- Community workaround: Reboot/power-cycle, firmware change, reassociate. Binary view: Only a poll-loss timer path (timeout unit unreconciled) and OpenWrt-only mac80211/ath10k paths; no stock stall mechanism shown.
- PWO: No stall rule exists (gap): propose a read-only ping-loss vs association rule; LOW_CCQ meanwhile.

**`dfs_false_trigger`** (22 threads)
- Threads: [DFS Hits causing issues - Everyone seeing this read here.](https://community.ui.com/questions/DFS-Hits-causing-issues-Everyone-seeing-this-read-here-/6fa2b45e-dbf3-44e5-882e-39d87fab17c4); [DFS hits with 8.7.0](https://community.ui.com/questions/DFS-hits-with-8-7-0/34eac566-8d93-48c3-a2ce-6ee6d8fa3dd6); [DFS Issues solved - Request input from Ubiquiti](https://community.ui.com/questions/DFS-Issues-solved-Request-input-from-Ubiquiti/8c327305-9b88-4685-ad70-bdcc5a007484)
- Root causes: RC-05 `other` HYPOTHESIS; RC-06 `ath10k_core.ko` HYPOTHESIS; RC-07 `mac80211.ko` HYPOTHESIS
- Community workaround: Move to a non-DFS channel, fixed channel, narrower width. Binary view: Agrees with our own DFS-channel outage audit; radar-detector internals of stock airOS are UNKNOWN.
- PWO: isDFSChannel / findBestChannel (prefers non-DFS): recommend-only.

**`m5_on_ac_mixed_mode_airtime_starvation`** (10 threads)
- Threads: [Flex NG - Major Airtime fairness issues (mixed devices)](https://community.ui.com/questions/Flex-NG-Major-Airtime-fairness-issues-mixed-devices/d55c4c70-b5c2-436c-b857-69e3cf517ff1); [Airtime issue](https://community.ui.com/questions/Airtime-issue/60069353-7a68-4c6b-a5fb-56d0a3dfbb82); [Compatibility AirMax AC + AimMax M in 40MHz](https://community.ui.com/questions/Compatibility-AirMax-AC-AimMax-M-in-40MHz/3e287606-ff46-467c-97cc-8fcb08c2df30)
- Root causes: RC-01 `ubnt_poll_host.ko` HYPOTHESIS; RC-02 `ubnt_poll_host.ko` HYPOTHESIS; RC-08 `mac80211.ko` HYPOTHESIS; RC-09 `mac80211.ko` CONFIRMED_LIVE_HARDWARE; RC-11 `ath10k_core.ko` HYPOTHESIS; RC-24 `other` SIMULATED_MODEL_ONLY
- Community workaround: Isolate M5 CPEs on their own AP, disable mixed mode, cap rates. Binary view: Best supported class: live OpenWrt bench shows slow M5 inflating latency and ATF/AQL fixing it; stock AC AP share is unmeasured.
- PWO: STATION_PRIORITY_IMBALANCE, HIGH_AIRTIME, AGGREGATION_SUBOPTIMAL: recommend-only; ATF/AQL advice only on OpenWrt.

**`ethernet_100m_to_10m_negotiation_drop`** (12 threads)
- Threads: [Ethernet , Lan speed 1000mbps on AP side however on station side is 100mbps ?](https://community.ui.com/questions/Ethernet-Lan-speed-1000mbps-on-AP-side-however-on-station-side-is-100mbps/ec9c3724-dbc2-452a-9bea-5cbf54b64dd6); [UISP eth0 connecting and disconnecting](https://community.ui.com/questions/UISP-eth0-connecting-and-disconnecting/2613315a-db48-49ca-8594-3b2f1f6ccd89); [Nanobeam Ethernet Speed Issue](https://community.ui.com/questions/Nanobeam-Ethernet-Speed-Issue/dbba02a9-d159-4172-9693-bceccff3a538)
- Root causes: RC-12 `other` HYPOTHESIS
- Community workaround: Replace cable/connector, change PoE injector or switch port. Binary view: Physical layer (cable, PoE, water) plus some firmware-dependent reports (8.5.12 downgrade, 8.7.14 fix); outside the five .ko. Our WA live audit showed gigabit and zero CRC errors.
- PWO: No PWO rule (gap): propose read-only link-speed/CRC rule.

**`ltu_modulation_stuck_4x_6x`** (9 threads)
- Threads: [V1.1.1 rate tanked to 2x QPSK until rebooted](https://community.ui.com/questions/V1-1-1-rate-tanked-to-2x-QPSK-until-rebooted/268821cc-0029-4971-b81d-81b442dc2a02); [ltu problem on one side. impoaaible to reach 2x +](https://community.ui.com/questions/ltu-problem-on-one-side-impoaaible-to-reach-2x/f8ce6989-c0f9-4dbb-bffc-3054191525e2); [LTU CPE - Gets stuck on 1X TX rate](https://community.ui.com/questions/LTU-CPE-Gets-stuck-on-1X-TX-rate/6c328f8c-9833-4e86-b95c-e881272e3db7)
- Root causes: RC-13 `ame_core.ko` CONFIRMED_STATIC_BINARY; RC-14 `ame_core.ko` CONFIRMED_STATIC_BINARY; RC-15 `ame_core.ko` HYPOTHESIS; RC-16 `ame_core.ko` HYPOTHESIS
- Community workaround: Improve alignment/CINR, narrower channel, remove interference, update firmware. Binary view: Matches: step-up gates are codeword pass-rate based; 12x is disabled at 60-100 MHz and MIMO-only (by design).
- PWO: LOW_CINR, LOW_SNR, EXCESSIVE_TX_POWER; fix getLTUCapabilities maxModulation (advisory).

**`ltu_cpe_disconnect_storm`** (18 threads)
- Threads: [LTU Rocket regularly crashing](https://community.ui.com/questions/LTU-Rocket-regularly-crashing/257b68b4-71c1-4404-ba6f-bb8e3ebef42d); [LTU Rocket crash. Clients unable to reconnect after](https://community.ui.com/questions/LTU-Rocket-crash-Clients-unable-to-reconnect-after/4ab17f92-920e-4404-be09-ac2ef9206479); [Starting today I have a few LTU Rocket radios that will randomly reboot multipl…](https://community.ui.com/questions/Starting-today-I-have-a-few-LTU-Rocket-radios-that-will-randomly-reboot-multiple-times-Nothing-obvi/59bf8dd2-1630-4dc0-9253-6794f026905e)
- Root causes: RC-17 `ame_core.ko` HYPOTHESIS; RC-18 `ame_core.ko` HYPOTHESIS; RC-19 `ame_core.ko` HYPOTHESIS; RC-23 `eab_driver.ko` HYPOTHESIS
- Community workaround: Reboot AP/CPEs, enable GPS sync, align frame/DL-UL split, firmware change. Binary view: GPS/TA and link-FSM reset paths are plausible but trigger conditions are not decompiled; eab_driver is absent.
- PWO: GPS_NOT_ENABLED, GPS_SYNC_MISALIGNED, TDD_FRAME_MISMATCH, HIGH_STATION_COUNT: recommend-only.

**`ltu_auto_frequency_atpc_glitch`** (9 threads)
- Threads: [LTU Rocket goes into DFS Lockout Mode and Station dis associates](https://community.ui.com/questions/LTU-Rocket-goes-into-DFS-Lockout-Mode-and-Station-dis-associates/29f61e2c-b079-42c7-9457-8eeb8693f935); [LTU permanent connection failure on frequency issues](https://community.ui.com/questions/LTU-permanent-connection-failure-on-frequency-issues/ccb9474a-b99f-49b0-9e9e-31d15899e2be); [LTU Auto Frequency discover](https://community.ui.com/questions/LTU-Auto-Frequency-discover/21fd1254-20e8-40d2-8199-61e162d81eab)
- Root causes: RC-16 `ame_core.ko` HYPOTHESIS; RC-20 `ame_core.ko` HYPOTHESIS; RC-21 `ame_core.ko` HYPOTHESIS
- Community workaround: Fix the frequency, disable auto-frequency/ATPC, pin TX power. Binary view: Knob set exists (auto_freq_*, autopwr_*, ame_dfs.ko); loop behaviour not recovered, no live receipt.
- PWO: isDFSChannel, LTU_SPLIT_FREQ_OPPORTUNITY, ATPC_NOT_ENABLED: recommend-only.

**`ltu_udp_iptv_latency_spike`** (10 threads)
- Threads: [LTU performance concerns (extra ping latency from devices behind CPE)](https://community.ui.com/questions/LTU-performance-concerns-extra-ping-latency-from-devices-behind-CPE/2411f360-074b-40e6-b040-992e79fbb1fc); [LTU ptmp and IPTV VLAN](https://community.ui.com/questions/LTU-ptmp-and-IPTV-VLAN/0710f2ff-8eee-45a9-a30c-7ea9bc72ba3f); [High packet loss and limited/no connectivity on LTU-Lite](https://community.ui.com/questions/High-packet-loss-and-limited-no-connectivity-on-LTU-Lite/525e4545-ee1c-4ca1-9b5e-3020bfb9dad1)
- Root causes: RC-18 `ame_core.ko` HYPOTHESIS; RC-22 `ame_core.ko` HYPOTHESIS; RC-23 `eab_driver.ko` HYPOTHESIS
- Community workaround: IGMP/multicast settings, shorter frame, QoS, firmware change. Binary view: Frame ladder and bcast/multicast symbol controls exist; nothing measures jitter; eab_driver DMA path unanalysable.
- PWO: LTU_FRAME_OPTIMIZATION, SUBOPTIMAL_FRAME_DURATION: recommend-only.

**`other_field_issue`** (4 threads)
- Threads: [LTU Output power only 20dbm](https://community.ui.com/questions/LTU-Output-power-only-20dbm/2511ced8-d954-4ecd-9630-3de845e1c387); [LTU rocket, LTU LR CPE  high  latency 8 -12ms](https://community.ui.com/questions/LTU-rocket-LTU-LR-CPE-high-latency-8-12ms/37a5d148-6f9f-4a99-a05c-dcec680c6204); [AIRFIBER 5x  HD  LTU  DISCONNECTS](https://community.ui.com/questions/AIRFIBER-5x-HD-LTU-DISCONNECTS/8e91a932-6a08-4d6a-ab06-b915057c3915)
- Root causes: RC-25 `other` HYPOTHESIS
- Community workaround: n/a Binary view: No binary mapping without a defined symptom.
- PWO: Manual triage; no rule.

## 4. Root-cause catalog (symbols verified against the cited docs)

| RC | Module | Symbol / function (short) | Classes | Evidence | Fact | Docs |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| RC-01 | `ubnt_poll_host.ko` | _retr_supression_levels (.rodata 0xea4); ubnt_poll_host_init_ptmp_net… | AD | HYPOTHESIS | C_STATIC_BINARY | 12-UPH |
| RC-02 | `ubnt_poll_host.ko` | ubnt_poll_host_set_sta_priority (0x7eb8); sta_priority sysctl; ubnt_p… | DA | HYPOTHESIS | C_STATIC_BINARY | 12-UPH |
| RC-03 | `ubnt_poll_host.ko` | ubnt_poll_host_set_ptmp_sta_atpc; atpc sysctl <en> <target_rssi> <min… | A | HYPOTHESIS | C_STATIC_BINARY | 12-UPH |
| RC-04 | `ubnt_poll_host.ko` | ubnt_poll_host_sta_bmiss_ind (.text+0x7800); missing-poll timer callb… | B | HYPOTHESIS | C_STATIC_BINARY | 10, 70A |
| RC-05 | `other` | umac.ko __param ubnt_radar_mode (WA 8.7.25 only); live dmesg 'Regular… | C | HYPOTHESIS | C_LIVE_HARDWARE | 12-WA, 282A |
| RC-06 | `ath10k_core.ko` | debugfs dfs_simulate_radar, dfs_block_radar_events, dfs_stats, quiet_… | C | HYPOTHESIS | C_STATIC_BINARY | 1087A, 1103A |
| RC-07 | `mac80211.ko` | ieee80211_radar_detected (0x4A794, exported); ieee80211_dfs_radar_det… | C | HYPOTHESIS | C_STATIC_BINARY | 1087A |
| RC-08 | `mac80211.ko` | ieee80211_txq_may_transmit (0x3c5a4); ieee80211_txq_airtime_check (0x… | D | HYPOTHESIS | C_STATIC_BINARY | 1031A, 1032A, 1158A |
| RC-09 | `mac80211.ko` | debugfs airtime_flags (AIRTIME_TX=0x1, AIRTIME_RX=0x2); aql_txq_limit… | D | C_LIVE_HARDWARE | C_LIVE_HARDWARE | 1104A, 7 |
| RC-10 | `mac80211.ko` | ieee80211_send_4addr_nullfunc; ieee80211_txq_remove_vlan; ieee80211_s… | B | HYPOTHESIS | C_STATIC_BINARY | 1086A |
| RC-11 | `ath10k_core.ko` | ath10k_htt_txrx_compl_task (0x2ac04); ath10k_htt_t2h_msg_handler (0x2… | BD | HYPOTHESIS | C_STATIC_BINARY | 1103A, 1157A |
| RC-12 | `other` | none: Ethernet PHY/MAC autonegotiation, cable pairs and PoE are outsi… | E | HYPOTHESIS | NONE | 282A, 283A |
| RC-13 | `ame_core.ko` | startThrd_4096 / stayThrd_4096 / mcsUpThrd_lowqam / mcsUpThrd_256 / m… | F | C_STATIC_BINARY | C_STATIC_BINARY | 12-UPH, 249A |
| RC-14 | `ame_core.ko` | autoMcsAllSisoTbl (.rodata 0xd378); autoMcsUseSisoTbl (0xd384); autoM… | F | C_STATIC_BINARY | C_STATIC_BINARY | 12-UPH |
| RC-15 | `ame_core.ko` | set_Param_mcs (adj-MCS setter AP 0x194648, CPE 0x18f510); autoMcsCeil… | F | HYPOTHESIS | C_STATIC_BINARY | 12-WA |
| RC-16 | `ame_core.ko` | mcs_txpwr_freq_ptp / af_ltu5_mcs_txpwr_freq (conducted-power tables);… | FH | HYPOTHESIS | C_STATIC_BINARY | 12-UPH, 544A |
| RC-17 | `ame_core.ko` | cpeFsmStop -> reset-with-setup(1) (.text+0x4db04 CPE); apply_config;… | G | HYPOTHESIS | C_STATIC_BINARY | 12-WA, 249A |
| RC-18 | `ame_core.ko` | AME_SchedCheckActiveCPE; AME_SchedAutoMCS; 'Top NQ CPE ... NtoS' / 'M… | GI | HYPOTHESIS | C_STATIC_BINARY | 438A |
| RC-19 | `ame_core.ko` | send_map_enable; cz_cross_frame_backoff_enable; czlen; GPS 1PPS super… | G | HYPOTHESIS | C_STATIC_BINARY | 186A, 190A |
| RC-20 | `ame_core.ko` | INI (RF) auto_freq_mode, auto_freq_list, smart_scan, prefer_work_freq… | H | HYPOTHESIS | C_STATIC_BINARY | 12-UPH, 189A |
| RC-21 | `ame_core.ko` | autopwr_en / autopwr_info / dlpwr_tune / ulpwr_tune / ulpwr_cfg (ame_… | H | HYPOTHESIS | C_STATIC_BINARY | 12-UPH, 544A |
| RC-22 | `ame_core.ko` | frame-duration immediates 2000/2500/4000/5000 us (45 sites); debugfs… | I | HYPOTHESIS | C_STATIC_BINARY | 12-UPH, 324A |
| RC-23 | `eab_driver.ko` | none: module absent (0 loose files; 0 of 209,121 tar members); DMA/IR… | GI | HYPOTHESIS | NONE | 1160A, 323A, 438A |
| RC-24 | `other` | SimPy + pymoo NSGA-III tower model (no binary) | D | SIM | SIM | 12-HN, 190A |
| RC-25 | `other` | n/a: unclassified field issue | O | HYPOTHESIS | NONE | 12-UPH |

Class letters: A single-CPE TX collapse, B silent stall, C false DFS, D M5-on-AC starvation, E ethernet 100M->10M, F LTU stuck modulation, G LTU disconnect storm, H LTU auto-freq/ATPC, I LTU UDP/IPTV latency, O other. Full objects (mechanism, workaround assessment, `safe_pwo_action`) are in the KB under `symptom_classes[*].ko_root_causes`.

## 5. Findings and discrepancies surfaced by the cross-reference

- **Wrong firmware base for most binaries.** `mac80211.ko` (backports 6.12.52) and `ath10k_core.ko` (ath10k-ct-smallbuffers 6.10, 600,808 B) are OpenWrt builds; no airOS `ath10k_core.ko` exists in the corpus (Stage 1087A, 1103A). Forum threads are mostly stock airOS 8.x/6.x (`umac.ko`, `ath_dev.ko`, `ubnt_poll_host.ko`), so ath10k/mac80211 rows are analogy only. Stages 1055A/1056A ("ath10k absent") are superseded by 1103A/1157A/1085A.
- **`eab_driver.ko` is absent** (0 loose files, 0 of 209,121 tar members; Stage 323A/438A/544A/1160A). Stage 186A labels `cds_mac_mod.ko` as `eab_driver`; unverified alias.
- **Unreconciled values**: missing-poll timer 30 s (Stage 10) vs 1,800,000 ms (Stage 70A); `penaltyThreshold` 25 (Stage 12) vs 60 (Stage 249A).
- **PWO vs binary**: `ltuRules.js:getLTUCapabilities` reports `1024 QAM` for non-Wave LTU although Stage 12 shows 4096-QAM (MCS 31) in LTU Rocket/Lite 2.4.2 `ame_core.ko`; PWO frame options 2/4/8 ms vs binary immediates 2/2.5/4/5 ms. Review, not a code change here.
- **PWO coverage gaps**: no rule for traffic stall, ethernet link speed/CRC, or CPE disconnect rate.

## 6. What forum evidence cannot prove

- A thread is one user's report: firmware, hardware, RF and cabling are unverified, and symptoms are classified by keyword plus a read of the text, not by reproduction.
- A workaround that worked for one poster is not shown to address the binary mechanism listed next to it; matching is by plausibility only.
- Thread counts measure what was searchable and relevant, not field prevalence or severity; accepted answers and staff replies are not proof of root cause.
- Static RE shows a mechanism exists, not that it fires on a given unit. Only RC with `CONFIRMED_LIVE_HARDWARE` rests on a bench receipt, and that one (Oct-2026, OpenWrt AP, airOS 6 M5 CPE) is not a stock airMAX AC AP.
- Ethernet negotiation, PoE and cabling are below the `.ko` layer: out of scope, not provable here.
- Nothing here authorizes a radio write. PWO actions stay recommend-only and gated by `PwoApprovalGate`.

## 7. Reproduce (offline)

```
python -m pytest tests/test_stage1187a_ubiquiti_community_scraper_and_kb.py -q
python tools/research/ubiquiti_community_forum_scraper.py build-kb --ltu <ltu.json> --curated <airmax.json>   # merges; keeps ko_root_causes
```

Refreshing the KB needs network (public API only); the test-suite does not.
