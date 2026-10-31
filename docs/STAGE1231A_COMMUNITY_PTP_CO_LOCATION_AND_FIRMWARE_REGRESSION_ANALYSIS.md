<!-- doc-head: Stage 1231A forum analysis of the 117 Ubiquiti community threads: per-firmware-version regression/rollback direction (airOS 8.5.12-8.7.25, 6.1.9, 6.3.x, LTU 1.1.1-2.4.2) and PtP/co-location/guard-band/GPS-sync patterns tied to binary facts; forum claims unverified, honest zeros for 8.7.25 and LTU 2.4.2 -->
# Stage 1231A - Community PtP, co-location and firmware regression analysis

Status: offline, `live_devices_touched=false`, no network. All thread content is `FORUM_REPORTS_UNVERIFIED_BY_LIVE_HARDWARE`;
binary refs are `CONFIRMED_STATIC_BINARY` facts from `artifacts/research/ubiquiti_community_kb_v2_reconciled_1230a.json` (Stage 1230A) or v1 root causes (`HYPOTHESIS`).
Data: `artifacts/verification/stage1231a_ptp_colocation_forum_analysis.json` (per-version rows, per-pattern rows, thread ids and URLs).

## 1. Method

- Version scan: a thread counts for a version when a digit/dot-bounded regex matches `fw_versions_mentioned`, title, `symptom_summary` or `community_workaround`. airOS versions are scoped to `airmax_ac`/`airmax_m` threads, LTU versions to `ltu` threads. Counts are THREADS, not version mentions.
- Direction (REG regression reported, TO rollback advised to this version, AWAY rollback advised away from it, GOOD fixed/good/quiet reported) is assigned only where the thread text says so; every other mention is `none`. Each label is one poster's statement.
- Co-location: vocabulary pass over the full cached text (co-location, same tower, adjacent, separation, isolation, GPS/sync, guard, side by side), then each hit thread was read. Keyword counts alone were not used.
- Supplementary check: a full-text scan of the cached raw responses for 8.7.14, 8.7.25 and 2.4.2 found the same threads as the KB fields (2, 0, 0).

## 2. Per-version table

| Version | Threads | via fw list | text only | Symptom distribution | REG | TO | AWAY | GOOD |
| :--- | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| airOS 8.5.12 | 21 | 20 | 1 | dfs 14, m5_on_ac 3, eth 2, stall 2 | 0 | 11 | 0 | 3 |
| airOS 8.7.0 | 17 | 17 | 0 | dfs 11, eth 2, m5_on_ac 2, stall 2 | 5 | 0 | 0 | 2 |
| airOS 8.7.1 | 36 | 35 | 1 | dfs 13, stall 12, eth 5, m5_on_ac 4, ptmp 2 | 3 | 8 | 0 | 2 |
| airOS 8.7.11 | 12 | 12 | 0 | stall 6, eth 2, m5_on_ac 2, dfs 1, ptmp 1 | 2 | 0 | 2 | 1 |
| airOS 8.7.14 | 2 | 0 | 2 | eth 1, stall 1 | 1 | 0 | 0 | 1 |
| airOS 8.7.25 | 0 | 0 | 0 | - | 0 | 0 | 0 | 0 |
| airOS 8.7.15 | 4 | 4 | 0 | stall 2, dfs 1, ptmp 1 | 1 | 0 | 1 | 0 |
| airOS 8.6.2 | 6 | 6 | 0 | dfs 4, m5_on_ac 1, stall 1 | 2 | 0 | 0 | 0 |
| airOS 6.1.9 | 6 | 6 | 0 | dfs 3, m5_on_ac 2, stall 1 | 1 | 0 | 0 | 2 |
| airOS 6.3.x | 16 | 16 | 0 | m5_on_ac 6, stall 6, dfs 4 | 4 | 1 | 0 | 0 |
| LTU 1.1.1 | 1 | 1 | 0 | ltu_mod 1 | 1 | 0 | 0 | 0 |
| LTU 2.3.x | 8 | 8 | 0 | ltu_storm 6, ltu_atpc 1, ltu_udp 1 | 5 | 0 | 0 | 0 |
| LTU 2.4.2 | 0 | 0 | 0 | - | 0 | 0 | 0 | 0 |
| LTU 2.2.x | 9 | 9 | 0 | ltu_storm 6, ltu_atpc 1, ltu_udp 1, other 1 | 2 | 0 | 0 | 0 |
| LTU 2.1.0 | 14 | 14 | 0 | ltu_storm 7, ltu_atpc 4, ltu_udp 2, ltu_mod 1 | 0 | 0 | 0 | 0 |

The 6.3.x row aggregates 6.3.0/2/5/6/10 (thread counts 3/10/1/9/1). Other class names as in KB v1 (eth = ethernet 100M-to-10M, ptmp = single-CPE rate collapse).

## 3. Direction evidence per version (title + URL)

**airOS 8.5.12** (21 threads). In thread 32 the poster also says something in 8.5.12 raised DFS sensitivity while advising a downgrade to it: the thread is internally inconsistent.
- TO: [XC/WA firmware 8.6.2 DFS radar detection issues](https://community.ui.com/questions/XC-WA-firmware-8-6-2-DFS-radar-detection-issues/e6bd49bc-858d-4ec9-9bdf-735cd38f600f) - community: stay on 8.5.x after 8.6.2 DFS drops
- TO: [DFS Issues solved - Request input from Ubiquiti](https://community.ui.com/questions/DFS-Issues-solved-Request-input-from-Ubiquiti/8c327305-9b88-4685-ad70-bdcc5a007484) - poster fixed ~99% of DFS hits by rollback to 8.5.12 (AC)
- TO: [False DFS hits with 8.7.0?](https://community.ui.com/questions/False-DFS-hits-with-8-7-0/7301e8df-a674-42bc-9ea3-58ab841f8890) - downgrade to 8.5.12 kept radios on DFS channels
- TO: [DFS radar found](https://community.ui.com/questions/DFS-radar-found/a779403c-5c9b-4766-85ab-402d977a3295) - downgrade helps some
- GOOD: [DFS Crazyness Rocket Prism 5AC Gen2](https://community.ui.com/questions/DFS-Crazyness-Rocket-Prism-5AC-Gen2/c6d3bc2c-5c02-4dd5-8f7c-1d15d5dcee7c) - reply: runs 8.5.12 on all towers, 8.7 gave too many hits
- TO: [DFS issues, Rocket AC lite.  v8.7.0  and v8.7.1](https://community.ui.com/questions/DFS-issues-Rocket-AC-lite-v8-7-0-and-v8-7-1/6033f46f-e8b0-4b3d-bf2d-56eb498dbac0) - community: downgrade to 8.5.12 fixes
- TO: [False Radar Detect Events on 8.7.1](https://community.ui.com/questions/False-Radar-Detect-Events-on-8-7-1/2d56bbc4-4586-40a5-b4d8-dd9746e248d1) - community: last usable AP firmware
- TO: [DFS Hits causing issues - Everyone seeing this read here.](https://community.ui.com/questions/DFS-Hits-causing-issues-Everyone-seeing-this-read-here-/6fa2b45e-dbf3-44e5-882e-39d87fab17c4) - operators keep sites on 8.5.12
- TO: [RADAR detected on almost all channels right across network](https://community.ui.com/questions/RADAR-detected-on-almost-all-channels-right-across-network/325c89ea-aad0-47a8-a6a5-7bc5fd6c5aa3) - accepted answer: downgrade to 8.5.12 or non-DFS
- GOOD: [The evergreen false DFS radar hits problem on AirMax M...](https://community.ui.com/questions/The-evergreen-false-DFS-radar-hits-problem-on-AirMax-M-devices-XW-with-v6-x-x-firmwares/d7a151e4-57bb-4edc-b4d7-63b8a9f36b61) - quietest AC-side version for false DFS
- TO: [DFS crashes in summer months](https://community.ui.com/questions/DFS-crashes-in-summer-months/a5e6b20a-1efb-4e10-a78d-f5ed148a84ff) - no firmware workaround; community suggested 8.5.12
- TO: [Has anyone else experienced DFS hits 300+ miles from a...](https://community.ui.com/questions/Has-anyone-else-experienced-DFS-hits-300-miles-from-a-TWDR-site/0bc52f52-5eea-4517-9b31-6491271f6e64) - workaround text only: 8.5.12 on AC if DFS needed
- TO: [Help, Airmax radios connected to Airmax AC Access point...](https://community.ui.com/questions/Help-Airmax-radios-connected-to-Airmax-AC-Access-points-have-started-dropping-out/4335b655-166b-4aad-bdf1-7d14caa6c32b) - revert AP to 8.5.12 or update to 8.7.0
- GOOD: [Performance problem between M devices and AC Access Points](https://community.ui.com/questions/Performance-problem-between-M-devices-and-AC-Access-Points/5e5cd831-4602-4228-a564-d7629cdab94a) - reply: 8.5.12 worked well and avoided DFS problems

**airOS 8.7.0** (17 threads). Direction is split: regression for DFS, 'update to' for the mixed-mode drop thread.
- REG: [Powerbeam 5AC Gen2 / 8.7.0 stops passing traffic](https://community.ui.com/questions/Powerbeam-5AC-Gen2-8-7-0-stops-passing-traffic/341a3ebd-50c9-407c-ba57-0b633c281ab9) - stall; reply calls it a known 8.7.0 bug (false DFS hits)
- REG: [DFS hits with 8.7.0](https://community.ui.com/questions/DFS-hits-with-8-7-0/34eac566-8d93-48c3-a2ce-6ee6d8fa3dd6) - DFS hits with 8.7.0 (title)
- REG: [False DFS hits with 8.7.0?](https://community.ui.com/questions/False-DFS-hits-with-8-7-0/7301e8df-a674-42bc-9ea3-58ab841f8890) - false DFS hits with 8.7.0 (title)
- REG: [PowerBeam 5AC ISO gen2 PTP Link Drops (DFS Scan starts)](https://community.ui.com/questions/PowerBeam-5AC-ISO-gen2-PTP-Link-Drops-DFS-Scan-starts/8562afee-df72-4dc8-8038-e71fcfee42ba) - PtP link drops after DFS scan on 8.7.0
- REG: [DFS issues, Rocket AC lite.  v8.7.0  and v8.7.1](https://community.ui.com/questions/DFS-issues-Rocket-AC-lite-v8-7-0-and-v8-7-1/6033f46f-e8b0-4b3d-bf2d-56eb498dbac0) - DFS hits began on 8.7.0/8.7.1
- GOOD: [False DFS hits on firmware 8.7.5](https://community.ui.com/questions/False-DFS-hits-on-firmware-8-7-5/3ba28056-f7b5-497b-89a9-76a6f3e3f1a2) - community: stay on 8.7.0/8.7.1, last stable
- GOOD: [Help, Airmax radios connected to Airmax AC Access point...](https://community.ui.com/questions/Help-Airmax-radios-connected-to-Airmax-AC-Access-points-have-started-dropping-out/4335b655-166b-4aad-bdf1-7d14caa6c32b) - reply: update to 8.7.0

**airOS 8.7.1** (36 threads). 8.7.1 is a regression for DFS versus 8.5.12 but the most-advised rollback target for the stall threads versus 8.7.8-8.7.19. Thread 59 mentions it only in title/summary because its fw list is noise.
- TO: [Rocket Prism 5AC not passing traffic to the stations](https://community.ui.com/questions/Rocket-Prism-5AC-not-passing-traffic-to-the-stations/1f1e449f-6c4c-418d-a3e3-db5016247cad) - use 8.7.1
- TO: [Rocket 5AC Gen2 LAN traffic not passing](https://community.ui.com/questions/Rocket-5AC-Gen2-LAN-traffic-not-passing/6e6ce60e-86d2-4304-9e91-8747810bce35) - load 8.7.1
- TO: [Stations associated to AP - Rocket Prism 5AC but seeing...](https://community.ui.com/questions/Stations-associated-to-AP-Rocket-Prism-5AC-but-seeing-packet-loss-and-cannot-ping-stations-Stations/96d10b57-a5e2-4786-b012-0785779d6c2d) - try 8.7.1
- TO: [Rocket 5AC 40mhz AP, sometimes all clients stop passing...](https://community.ui.com/questions/Rocket-5AC-40mhz-AP-sometimes-all-clients-stop-passing-traffic-and-cant-be-pingd/f75c0eb6-bd23-4e29-9eec-1c8c630ef7bc) - try 8.7.1
- TO: [LiteAP GPS | WA.v8.7.14 - Clients connected, but no tra...](https://community.ui.com/questions/LiteAP-GPS-or-WA-v8-7-14-Clients-connected-but-no-traffic-flow/b7fea429-3567-47a1-9ddf-4d725896c4d0) - move APs back to 8.7.1
- REG: [DFS Crazyness Rocket Prism 5AC Gen2](https://community.ui.com/questions/DFS-Crazyness-Rocket-Prism-5AC-Gen2/c6d3bc2c-5c02-4dd5-8f7c-1d15d5dcee7c) - false radar after upgrade from 8.5.12 (Prism Gen2)
- REG: [DFS issues, Rocket AC lite.  v8.7.0  and v8.7.1](https://community.ui.com/questions/DFS-issues-Rocket-AC-lite-v8-7-0-and-v8-7-1/6033f46f-e8b0-4b3d-bf2d-56eb498dbac0) - DFS hits on 8.7.0/8.7.1
- REG: [False Radar Detect Events on 8.7.1](https://community.ui.com/questions/False-Radar-Detect-Events-on-8-7-1/2d56bbc4-4586-40a5-b4d8-dd9746e248d1) - false radar events on 8.7.1 (title)
- GOOD: [False DFS hits on firmware 8.7.5](https://community.ui.com/questions/False-DFS-hits-on-firmware-8-7-5/3ba28056-f7b5-497b-89a9-76a6f3e3f1a2) - stay on 8.7.0/8.7.1
- TO: [False DFS hits on 8.7.12](https://community.ui.com/questions/False-DFS-hits-on-8-7-12/f49c5584-fd7a-4639-8509-a091256acb48) - 8.7.1 calmer than 8.7.11/8.7.12
- TO: [LiteAP AC DFS loop.](https://community.ui.com/questions/LiteAP-AC-DFS-loop/8670faea-b05f-4f6b-b2b7-db53e89a309e) - test 8.7.1; later firmware worse for DFS
- TO: [Drop in throughput since upgrading to 8.7.8 on mixed pt...](https://community.ui.com/questions/Drop-in-throughput-since-upgrading-to-8-7-8-on-mixed-ptmp-rocket-prism/42e24039-aaa4-40d5-a312-2e56398eb96d) - downgrade AP to 8.7.1
- GOOD: [Problems with the Flexible NEW mode with AIRMAX MIX AC...](https://community.ui.com/questions/Problems-with-the-Flexible-NEW-mode-with-AIRMAX-MIX-AC-and-M/a8ed0e2b-3cb5-43c1-b51f-56049f553c5d) - APs on 8.7.1 with Flexible New were fine

**airOS 8.7.11** (12 threads).
- AWAY: [Rocket 5AC Gen2 LAN traffic not passing](https://community.ui.com/questions/Rocket-5AC-Gen2-LAN-traffic-not-passing/6e6ce60e-86d2-4304-9e91-8747810bce35) - poster on 8.7.11; community advises 8.7.1
- AWAY: [Rocket 5AC 40mhz AP, sometimes all clients stop passing...](https://community.ui.com/questions/Rocket-5AC-40mhz-AP-sometimes-all-clients-stop-passing-traffic-and-cant-be-pingd/f75c0eb6-bd23-4e29-9eec-1c8c630ef7bc) - community advises 8.7.1
- GOOD: [LiteAP GPS | WA.v8.7.14 - Clients connected, but no tra...](https://community.ui.com/questions/LiteAP-GPS-or-WA-v8-7-14-Clients-connected-but-no-traffic-flow/b7fea429-3567-47a1-9ddf-4d725896c4d0) - stations fine on 8.7.11; AP stall was on 8.7.14
- REG: [False DFS hits on 8.7.12](https://community.ui.com/questions/False-DFS-hits-on-8-7-12/f49c5584-fd7a-4639-8509-a091256acb48) - many DFS hits on 8.7.11/8.7.12
- REG: [Problems with the Flexible NEW mode with AIRMAX MIX AC...](https://community.ui.com/questions/Problems-with-the-Flexible-NEW-mode-with-AIRMAX-MIX-AC-and-M/a8ed0e2b-3cb5-43c1-b51f-56049f553c5d) - Flexible New on an 8.7.11 AP gave intermittent customer issues; 8.7.1 fine

**airOS 8.7.14** (2 threads). Exactly 2 threads, 0 via fw_versions_mentioned (both text-only); one regression claim and one fixed-in claim, each a single poster. Binary-only otherwise.
- REG: [LiteAP GPS | WA.v8.7.14 - Clients connected, but no tra...](https://community.ui.com/questions/LiteAP-GPS-or-WA-v8-7-14-Clients-connected-but-no-traffic-flow/b7fea429-3567-47a1-9ddf-4d725896c4d0) - title 'WA.v8.7.14': clients connected, no traffic; community says move APs back to 8.7.1
- GOOD: [5 Years later -- I think they fixed the 100 MB/second N...](https://community.ui.com/questions/5-Years-later-I-think-they-fixed-the-100-MB-second-Nanostation-Problem/3ac2933e-2a9c-4483-8424-0ce0ff17535e) - workaround text: poster says 8.7.14 seems to fix NanoStation 1000->100 Mbit drop

**airOS 6.1.9** (6 threads). Opposite directions by symptom: stall regression (XW AP) versus DFS-quiet reference (XW CPE).
- REG: [6.1.9 - stops passing traffic on XW boadrs](https://community.ui.com/questions/6-1-9-stops-passing-traffic-on-XW-boadrs/6acda552-4216-420b-ba3c-b36638102b41) - title: 6.1.9 stops passing traffic on XW boards; roll back to 6.1.6
- GOOD: [The evergreen false DFS radar hits problem on AirMax M...](https://community.ui.com/questions/The-evergreen-false-DFS-radar-hits-problem-on-AirMax-M-devices-XW-with-v6-x-x-firmwares/d7a151e4-57bb-4edc-b4d7-63b8a9f36b61) - quietest XW version for false DFS
- GOOD: [Drop in throughput since upgrading to 8.7.8 on mixed pt...](https://community.ui.com/questions/Drop-in-throughput-since-upgrading-to-8-7-8-on-mixed-ptmp-rocket-prism/42e24039-aaa4-40d5-a312-2e56398eb96d) - workaround text: XW to 6.1.9 seemed to fix the micro-pop AP

**airOS 6.3.x** (16 threads). 6.3.x is an aggregate of 6.3.0/2/5/6/10; per-sub-version counts are in the JSON.
- REG: [TDD Framing (Flexible new) stops passing traffic to/fro...](https://community.ui.com/questions/TDD-Framing-Flexible-new-stops-passing-traffic-to-from-stations/759a880e-e5d9-468d-bc68-723e8512126c) - 6.3.5 also hits legacy-to-legacy; downgrade to 6.3.2 fixes (community)
- REG: [LocoM5 freeze/lock up/stops passing traffic - ping watc...](https://community.ui.com/questions/LocoM5-freeze-lock-up-stops-passing-traffic-ping-watchdog-reboot-restores-connectivity/efc7b45c-323f-40ae-9dd5-3781aeefb66f) - Loco M5 freeze on 6.3.6; 'likely older than 6.3.6' (soft)
- TO: [M2 as AP with XW boards stops passing traffic to CPEs](https://community.ui.com/questions/M2-as-AP-with-XW-boards-stops-passing-traffic-to-CPEs/7943ba90-9274-44fe-a1a6-a437d9ed8f40) - 6.3.2 on AP may help (hedged)
- REG: [station traffic and pings stop until device is kicked f...](https://community.ui.com/questions/station-traffic-and-pings-stop-until-device-is-kicked-from-ap/d9f71c3d-fce1-445e-bcc7-5359147fec24) - XM 6.3.6 PtMP station stops passing traffic (soft)
- REG: [NanoStation M5 RADAR issues on firmware v6.3.10](https://community.ui.com/questions/NanoStation-M5-RADAR-issues-on-firmware-v6-3-10/e4045e8e-2cc3-4573-bde0-9732c33417e3) - NanoStation M5 radar issue on 6.3.10; notice quotes 6.3.10 pulled

**LTU 1.1.1** (1 threads). KB v1 lists 1.1.1 for 2 threads, but thread 59 is an airMAX AC thread (title XC.v8.7.1) so only 1 LTU thread is real.
- REG: [V1.1.1 rate tanked to 2x QPSK until rebooted](https://community.ui.com/questions/V1-1-1-rate-tanked-to-2x-QPSK-until-rebooted/268821cc-0029-4971-b81d-81b442dc2a02) - title: V1.1.1 rate tanked to 2x QPSK; staff: known bug fixed in 1.1.2 betas

**LTU 2.3.x** (8 threads). Thread 88 carries both a regression and a fixed-in-later-RC statement.
- REG: [LTU 2.3.0 Crash](https://community.ui.com/questions/LTU-2-3-0-Crash/6e8e12a1-5b94-4ee9-bc4c-7ac8be5b0ca2) - title: 2.3.0 crash; reply: latest 2.3.x RC fixed it
- REG: [LTU some clients disconnect 2.3.0](https://community.ui.com/questions/LTU-some-clients-disconnect-2-3-0/68b5e1f5-e486-43a0-8ac1-afa7118072a3) - after 2.3.0 CPEs connected but no traffic; known issue in release thread
- REG: [LTU Rocket v2.3.0 Dropouts](https://community.ui.com/questions/LTU-Rocket-v2-3-0-Dropouts/fa65148b-4b6a-4c8a-91de-a0d06449c630) - after update to 2.3.0 LTUs rebooting; going back stopped it
- REG: [Flapping problems on LTU Rocket](https://community.ui.com/questions/Flapping-problems-on-LTU-Rocket/6544ef76-cbee-4ab3-96a6-d98a40ce5b04) - 2.3.1 flapping, no confirmed root cause (soft)
- REG: [DFS hits causing customers to disconnect for 1-2 minute...](https://community.ui.com/questions/DFS-hits-causing-customers-to-disconnect-for-1-2-minutes-LTU-2-3-1-firmware/1c668f81-a199-4140-8826-cc287a41096c) - 2.3.1 DFS hits every few days, suspected false
- none: [High packet loss and limited/no connectivity on LTU-Lite](https://community.ui.com/questions/High-packet-loss-and-limited-no-connectivity-on-LTU-Lite/525e4545-ee1c-4ca1-9b5e-3020bfb9dad1) - 2.3.0 packet loss cured by swapping CPE (hardware, not firmware)

Reading the pattern (reports, not proof):
- DFS false hits cluster on 8.6.x, 8.7.0, 8.7.1 and 8.7.5-8.7.12, with 8.5.12 the repeated rollback target (11 TO entries); one thread claims 8.5.12 itself raised sensitivity.
- The stall class (traffic stops, clients still listed) names 8.7.1 as the rollback target against 8.7.8, 8.7.11, 8.7.14, 8.7.15 and 8.7.19, but 8.7.1 is itself a DFS-regression version: the advice flips with the symptom.
- 6.1.9 is a stall regression on XW APs and a DFS-quiet reference on XW CPEs. 6.3.5 and 6.3.10 draw rollback to 6.3.2 or 6.3.6.
- LTU 1.1.1 has a staff-confirmed bug fixed in 1.1.2 betas; 2.3.0/2.3.1 draw 5 regression reports (crash, no traffic, reboots, DFS hits).

## 4. Honest zeros (binary-only versions)

- airOS 8.7.25: 0 threads. The 1190A/1214A binaries are 8.7.25 builds (BF-1190A-01, -03, BF-1214A-01); the forum data says nothing about this version in the field.
- LTU 2.4.2 (and any 2.4.x): 0 threads. BF-1191A-01 and BF-1214A-02 come from 2.4.2 `ame_core.ko`; the newest LTU in the 117 threads is 2.3.2 (one thread).
- airOS 8.7.14: 2 threads, both text-only (0 in the fw list): one stall regression claim (title `WA.v8.7.14`) and one fixed-in claim (workaround: eth 1000-to-100 drop 'seems fixed'). Each is a single poster.
- No version regression can be tied to a binary fact: BF-1190A-03 (`sta_remove_oldest` only in 8.7.25 builds) is the only version-specific fact and 8.7.25 has no forum thread.

## 5. Co-location, guard band, GPS sync and PtP

Finding: No thread in the 117 is titled or framed as co-location. 10 distinct threads touch same-site interference: 6 discuss it as part of their argument (32 adjacent-AP co-existence; 50, 106, 90 frequency separation/sync; 37, 42 DFS-move collisions) and 4 only observe same-site behaviour (31, 44, 27, 23). GPS-sync threads: 9 (not all about interference). PtP threads: 5, none PtP-to-PtP co-location.

### CL-1 same_tower_adjacent_transmitter_dfs_susceptibility (6 threads)
- primary_discussion: [DFS Hits causing issues - Everyone seeing this read here.](https://community.ui.com/questions/DFS-Hits-causing-issues-Everyone-seeing-this-read-here-/6fa2b45e-dbf3-44e5-882e-39d87fab17c4) - operator thread blames co-existence of adjacent APs; compares 3x30 sector packs (susceptible) with horns (immune)
- observation_only: [False Radar Detect Events on 8.7.1](https://community.ui.com/questions/False-Radar-Detect-Events-on-8-7-1/2d56bbc4-4586-40a5-b4d8-dd9746e248d1) - identical radios on one tower, only one detects radar; no co-location analysis ; [[airMAX AC 8.7.15] DFS false positives](https://community.ui.com/questions/airMAX-AC-8-7-15-DFS-false-positives/543d61f8-5b6f-451e-ad17-ee1e56e25c38) - side-by-side APs, one affected; staff asks for a paired support-file comparison ; [False DFS hits on 8.7.12](https://community.ui.com/questions/False-DFS-hits-on-8-7-12/f49c5584-fd7a-4639-8509-a091256acb48) - two of several APs at one site get DFS hits at different times ; [DFS radar found](https://community.ui.com/questions/DFS-radar-found/a779403c-5c9b-4766-85ab-402d977a3295) - radar events began after a new AP was deployed on the same site; poster guesses reflection ; [XC/WA firmware 8.6.2 DFS radar detection issues](https://community.ui.com/questions/XC-WA-firmware-8-6-2-DFS-radar-detection-issues/e6bd49bc-858d-4ec9-9bdf-735cd38f600f) - short link pair at the same site fine on different frequencies; poster suspects nearby LTE antennas 5-10 m above
- Recurring causes: crowded same-band RF at the site; adjacent AP energy entering the receiver (antenna pattern dependent); reflections off site structures; non-airMAX emitters on the tower; firmware sensitivity change (claimed, unproven).
- Community remedies: antenna up/down-tilt to maximise isolation; shield kit or tower structure between adjacent transmitters; change or trade frequencies one AP at a time; move affected APs off DFS channels; downgrade to 8.5.12 (loses dynamic frequency move); send paired good/bad support files to staff.
- Binary tie `RC-05/RC-06/RC-07 (KB v1)` (HYPOTHESIS): DFS/radar and CCA-threshold names exist in 8.7.25 umac and in OpenWrt ath10k/mac80211 builds. Caveat: analogy only: no KB v2 binary fact covers stock airOS 8.5.x-8.7.15 radar detection, the firmware these posters ran.

### CL-2 channel_plan_and_frequency_separation_guard_band (3 threads)
- primary_discussion: [Drop in throughput since upgrading to 8.7.8 on mixed pt...](https://community.ui.com/questions/Drop-in-throughput-since-upgrading-to-8-7-8-on-mixed-ptmp-rocket-prism/42e24039-aaa4-40d5-a312-2e56398eb96d) - operator asks how much frequency separation is needed with 5 MHz between APs on 20 MHz widths; reply: way too close, put the other at 5700; also uses a TDMA filter ; [LTU Massive packet loss on "Excellent" link with 90% or...](https://community.ui.com/questions/LTU-Massive-packet-loss-on-Excellent-link-with-90percent-or-better/cf74b4bc-f4fa-4dc3-8d8c-76357fc0a324) - 4 sectors on one tower separated in frequency; one quadrant loses packets under load; reply suggests the same channel as the facing sector with GPS sync; poster asks whether LTU does CCA ; [Intermittent Issues LTU-Rocket to LTU-Lite Devices](https://community.ui.com/questions/Intermittent-Issues-LTU-Rocket-to-LTU-Lite-Devices/a17b9020-3eaa-481d-b709-da26b3cf8099) - two Rockets facing each other across a street; advice: avoid home-WiFi bands, fixed channels, 40 MHz; poster shut off one half of the site to test mutual interference
- Recurring causes: too little separation between co-site APs; default channels inside the home-WiFi band; reflections (water tower, roofs) mistaken for co-channel interference.
- Community remedies: widen frequency separation (example in thread: move one AP to 5700); fixed, planned channels instead of auto; GPS-sync co-sited fixed-frame radios and reuse a channel; TDMA filter setting (thread 50); turn off one site half to isolate the source.
- Binary tie `BF-1190A-05` (CONFIRMED_STATIC_BINARY): ubnt_poll_host exposes ff_guard_units and 37 other slot/guard sysctl names. Caveat: names only; no default or effect measured, and no thread cites these knobs.
- Binary tie `RC-01 (KB v1)` (HYPOTHESIS): forum 'TDMA filter 0-9' plausibly maps to the 0..9 retry-suppression levels (_retr_supression_levels, cms_bias). Caveat: name-level guess; thread 50 uses filter 2-3 to hold back poor clients, not to separate sites.
- Binary tie `RC-24 (KB v1)` (SIMULATED_MODEL_ONLY): SimPy tower model: unsynced 5/5 MHz guard 611.59 Mbps / 29.156 ms p99 vs GPS-synced 25/20 MHz 981.38 Mbps / 5.163 ms. Caveat: simulation only; the 5 MHz example in thread 50 is the same order as the simulated tight guard but this is not a measurement.

### CL-3 dfs_channel_move_landing_on_own_frequencies (3 threads)
- primary_discussion: [The evergreen false DFS radar hits problem on AirMax M...](https://community.ui.com/questions/The-evergreen-false-DFS-radar-hits-problem-on-AirMax-M-devices-XW-with-v6-x-x-firmwares/d7a151e4-57bb-4edc-b4d7-63b8a9f36b61) - after a DFS hit the AP never returns to its configured frequency, so frequencies end up overlapping other radios in the network ; [False DFS hits on 8.7.12](https://community.ui.com/questions/False-DFS-hits-on-8-7-12/f49c5584-fd7a-4639-8509-a091256acb48) - AP does not return to the DFS channel after the event and interferes with nearby backhauls
- observation_only: [Drop in throughput since upgrading to 8.7.8 on mixed pt...](https://community.ui.com/questions/Drop-in-throughput-since-upgrading-to-8-7-8-on-mixed-ptmp-rocket-prism/42e24039-aaa4-40d5-a312-2e56398eb96d) - a micro-pop AP moved off DFS sometimes ends up on the same frequency as the main AP
- Recurring causes: DFS hop without return to the planned channel; CPE scan lists not updated when the AP frequency changes (thread 39 warning).
- Community remedies: manual restore after each event; avoid DFS channels for affected APs; set a control-frequency list (thread 40, unresolved).
- Binary tie `RC-20 (KB v1)` (HYPOTHESIS): LTU auto_freq_* knobs and DFS hop; condition that triggers a hop not decompiled. Caveat: RC-20 is LTU 2.4.2; these threads are airMAX 6.x/8.x, so only a conceptual parallel.

### CL-4 gps_sync_as_remedy_or_diagnostic (9 threads, not strict co-location)
- sync_as_remedy: [LTU Massive packet loss on "Excellent" link with 90% or...](https://community.ui.com/questions/LTU-Massive-packet-loss-on-Excellent-link-with-90percent-or-better/cf74b4bc-f4fa-4dc3-8d8c-76357fc0a324) - suggested sync of co-sited fixed-frame radios to conserve spectrum ; [Intermittent Issues LTU-Rocket to LTU-Lite Devices](https://community.ui.com/questions/Intermittent-Issues-LTU-Rocket-to-LTU-Lite-Devices/a17b9020-3eaa-481d-b709-da26b3cf8099) - GPS time sync configured; interference not resolved in the thread
- sync_question: [DFS Crazyness Rocket Prism 5AC Gen2](https://community.ui.com/questions/DFS-Crazyness-Rocket-Prism-5AC-Gen2/c6d3bc2c-5c02-4dd5-8f7c-1d15d5dcee7c) - reply asks whether all APs are GPS-synced; poster's site mostly is; false radar persists
- sync_health_problem: [Rockets losing GPS sync, causing problems](https://community.ui.com/questions/Rockets-losing-GPS-sync-causing-problems/a2d232ee-5a96-4d21-8872-6363ff3e9236) - 10 Rockets on 2.1.0 lose satellite lock; an auto-frequency change then kicks all clients; reboot or restarting ustatsd regains lock for hours
- sync_wished_for: [Performance problem between M devices and AC Access Points](https://community.ui.com/questions/Performance-problem-between-M-devices-and-AC-Access-Points/5e5cd831-4602-4228-a564-d7629cdab94a) - operator wanted Fixed Frame GPS sync but Flexible Legacy was the only mode without M-CPE latency
- sync_toggle_diagnostic: [LTU Rocket Radio Section Disconnects Clients then reboots](https://community.ui.com/questions/LTU-Rocket-Radio-Section-Disconnects-Clients-then-reboots/4bbdb328-dd1e-4d18-8aa8-de9b445c6783) - GPS sync switched off while chasing Rocket reboots; both Rockets still rebooted after ~9 h (power/crash thread, not interference) ; [Starting today I have a few LTU Rocket radios that will...](https://community.ui.com/questions/Starting-today-I-have-a-few-LTU-Rocket-radios-that-will-randomly-reboot-multiple-times-Nothing-obvi/59bf8dd2-1630-4dc0-9253-6794f026905e) - one operator says reboots stopped after disabling GPS sync; thread is mainly cold-weather power draw ; [LTU Rocket -> AirFiber 5XHD Duplicate Ping + Packet Los...](https://community.ui.com/questions/LTU-Rocket-greater-AirFiber-5XHD-Duplicate-Ping-Packet-Loss-V2-2-0/16e26bb1-eb8b-4a7f-8773-e5b28c310043) - asked whether to disable GPS sync; resolved by not using an LTU Rocket as master for a 5XHD CPE ; [LTU Pro disconnects and come back after serveral minute...](https://community.ui.com/questions/LTU-Pro-disconnects-and-come-back-after-serveral-minutes-from-Rocket/ecb9bfbe-b73f-46cd-a7f1-d6d4d88ac519) - asks whether GPS positioning of two co-located CPEs matters; fixed by a quiet non-DFS channel
- Recurring causes: loss of GPS lock (satellites tracked 0); sync suspected as a side cause of reboots (unproven).
- Community remedies: restart GPS or reboot; ustatsd restart (temporary, per poster); disable sync as a test; fixed non-DFS channel.
- Binary tie `RC-19 (KB v1)` (HYPOTHESIS): LTU GPS 1PPS superframe lock and timing advance; co-sited sectors must share frame and duty cycle (names/RE of 2.4.2 ame_core). Caveat: no KB v2 binary fact adds to it; only 4 of 9 threads treat sync as an interference tool; no thread shows interference caused by missing sync.
- Binary tie `RC-20 (KB v1)` (HYPOTHESIS): thread 100: auto-frequency change kicks all clients when GPS is broken. Caveat: hop trigger and GPS dependence not decompiled; thread is on 2.1.0 not 2.4.2.

### CL-5 mixed_mode_width_and_profile_not_colocation (3 threads, not strict co-location)
- context: [AirOS 8.7.x - any way to force PtMP AC only mode on 20/...](https://community.ui.com/questions/AirOS-8-7-x-any-way-to-force-PtMP-AC-only-mode-on-20-40Mhz-instead-of-mixed-mode-due-to-high-latenc/f867b438-2698-4d45-99a5-9cbfda628c3d) - 8.7.x removed AC-only mode; mixed mode gives 20-40 ms latency under load ; [Compatibility AirMax AC + AimMax M in 40MHz](https://community.ui.com/questions/Compatibility-AirMax-AC-AimMax-M-in-40MHz/3e287606-ff46-467c-97cc-8fcb08c2df30) - M5 CPE will not join an AC AP at 40 MHz; reply: M CPEs lack LDPC, use 20 MHz ; [Drop in throughput since upgrading to 8.7.8 on mixed pt...](https://community.ui.com/questions/Drop-in-throughput-since-upgrading-to-8-7-8-on-mixed-ptmp-rocket-prism/42e24039-aaa4-40d5-a312-2e56398eb96d) - throughput fell on a mixed PtMP after 8.7.8; Flex New unusable; XW CPEs see DFS events
- Recurring causes: mixed AC and M CPEs on one AP; width choice for M CPEs.
- Community remedies: Flexible Legacy frame mode; 20 MHz width; AC radio as AP, M as station.
- Binary tie `BF-1190A-02` (CONFIRMED_STATIC_BINARY): ubnt_poll_host selects the PtMP profile by width: 40 MHz -> _ht40, 29-30 -> _ht30, 31-39 and 80 MHz -> _ht20 default. Caveat: no thread in the 117 names an 80 MHz or 31-39 MHz mixed-mode AP, so the ht20 fallback has NO direct forum counterpart; the 20 MHz advice maps to _ht20 only by coincidence of name.

### PTP-1 ptp_links_in_the_117
Only 5 of 117 summaries are explicitly PtP (stall, 2 DFS, ethernet, LTU modulation); the PtP remedies are fixed non-DFS channel (28), antenna gain/alignment (68), cable/ports (58). No PtP-to-PtP co-location thread exists.
- [Rocket 5AC Gen2 LAN traffic not passing](https://community.ui.com/questions/Rocket-5AC-Gen2-LAN-traffic-not-passing/6e6ce60e-86d2-4304-9e91-8747810bce35) (stall)
- [PowerBeam 5AC ISO gen2 PTP Link Drops (DFS Scan starts)](https://community.ui.com/questions/PowerBeam-5AC-ISO-gen2-PTP-Link-Drops-DFS-Scan-starts/8562afee-df72-4dc8-8038-e71fcfee42ba) (dfs)
- [NanoStation M5 RADAR issues on firmware v6.3.10](https://community.ui.com/questions/NanoStation-M5-RADAR-issues-on-firmware-v6-3-10/e4045e8e-2cc3-4573-bde0-9732c33417e3) (dfs)
- [Ethernet , Lan speed 1000mbps on AP side however on sta...](https://community.ui.com/questions/Ethernet-Lan-speed-1000mbps-on-AP-side-however-on-station-side-is-100mbps/ec9c3724-dbc2-452a-9bea-5cbf54b64dd6) (eth)
- [ltu problem on one side. impoaaible to reach 2x +](https://community.ui.com/questions/ltu-problem-on-one-side-impoaaible-to-reach-2x/f8ce6989-c0f9-4dbb-bffc-3054191525e2) (ltu_mod)

## 6. Evidence-class summary of the ties

| Forum pattern | Binary or model item | Class | Defensible? |
| :--- | :--- | :--- | :--- |
| Adjacent-AP DFS sensitivity (CL-1) | RC-05/06/07 DFS names (8.7.25 umac, OpenWrt) | HYPOTHESIS | analogy only, wrong firmware family |
| Frequency separation / guard band (CL-2) | BF-1190A-05 slot/guard sysctl names | CONFIRMED_STATIC_BINARY (names) | knobs exist; effect unmeasured |
| 'TDMA filter 0-9' (CL-2) | RC-01 retry-suppression levels 0..9 | HYPOTHESIS | name-level guess |
| Sync + wider guard (CL-2/4) | RC-24 SimPy tower model | SIMULATED_MODEL_ONLY | model, not measurement |
| GPS lock lost, auto-freq kicks clients (CL-4) | RC-19 / RC-20 | HYPOTHESIS | LTU 2.4.2 RE vs 2.1.0 reports |
| Width advice for M CPEs (CL-5) | BF-1190A-02 `_ht20` fallback | CONFIRMED_STATIC_BINARY (selector) | no thread uses 80 MHz or 31-39 MHz mixed mode: no forum counterpart |

## 7. What is still unproven

- Every symptom, version direction and remedy is an unverified forum report; none was reproduced on hardware, and one poster's rollback success is not a firmware defect.
- Thread counts show what the M/AC/LTU search surfaced, not field prevalence. A version in a fw list can be a changelog quote or an earlier firmware.
- No thread measures isolation, guard width or sync offset; co-location causes are poster opinion. Only thread 32 argues co-existence outright.
- No binary fact covers DFS or co-location behaviour of stock airOS 8.5.x-8.7.15; RC-05..RC-07 are analogy.
- ht20 fallback: confirmed as a selector, but unlinked to any forum thread; the starvation claim still needs a live slot trace (1190A gap).

## 8. Defects found in KB v1 and the source data (not fixed here)

- fw list noise: [Rocket 5AC Gen2 LAN traffic not passing](https://community.ui.com/questions/Rocket-5AC-Gen2-LAN-traffic-not-passing/6e6ce60e-86d2-4304-9e91-8747810bce35) lists 1.4.54, 1.19.4 on an `airmax_ac` thread (likely UISP/LTU version strings, not airOS).
- fw list noise: [Has anyone else experienced DFS hits 300+ miles from a...](https://community.ui.com/questions/Has-anyone-else-experienced-DFS-hits-300-miles-from-a-TWDR-site/0bc52f52-5eea-4517-9b31-6491271f6e64) lists 2.2.1 on an `airmax_ac` thread (likely UISP/LTU version strings, not airOS).
- fw list noise: [PowerBeam 5AC 500 ISO | XC.v8.7.1 in Client mode report...](https://community.ui.com/questions/PowerBeam-5AC-500-ISO-or-XC-v8-7-1-in-Client-mode-report-every-view-days-problems-with-interface-et/c4cd6533-f4f7-40e3-90e8-0a08bb4a9a24) lists 1.1.1, 1.19.4 on an `airmax_ac` thread (likely UISP/LTU version strings, not airOS).
- version in title/summary but absent from the fw list: [station traffic and pings stop until...](https://community.ui.com/questions/station-traffic-and-pings-stop-until-device-is-kicked-from-ap/d9f71c3d-fce1-445e-bcc7-5359147fec24) has 6.3.6 (symptom_summary); [LiteAP GPS | WA.v8.7.14 - Clients con...](https://community.ui.com/questions/LiteAP-GPS-or-WA-v8-7-14-Clients-connected-but-no-traffic-flow/b7fea429-3567-47a1-9ddf-4d725896c4d0) has 8.7.14 (title); [LiteAP GPS | WA.v8.7.14 - Clients con...](https://community.ui.com/questions/LiteAP-GPS-or-WA-v8-7-14-Clients-connected-but-no-traffic-flow/b7fea429-3567-47a1-9ddf-4d725896c4d0) has 8.7.14 (symptom_summary); [Rp-5ac-gen2 (AP) and Litebeam M5 (sta...](https://community.ui.com/questions/Rp-5ac-gen2-AP-and-Litebeam-M5-station-clients-dont-get-throughput/d33af6c4-6a91-4589-bead-0d5719da3906) has 6.1.7 (symptom_summary); [PowerBeam 5AC 500 ISO | XC.v8.7.1 in...](https://community.ui.com/questions/PowerBeam-5AC-500-ISO-or-XC-v8-7-1-in-Client-mode-report-every-view-days-problems-with-interface-et/c4cd6533-f4f7-40e3-90e8-0a08bb4a9a24) has 8.7.1 (title); [PowerBeam 5AC 500 ISO | XC.v8.7.1 in...](https://community.ui.com/questions/PowerBeam-5AC-500-ISO-or-XC-v8-7-1-in-Client-mode-report-every-view-days-problems-with-interface-et/c4cd6533-f4f7-40e3-90e8-0a08bb4a9a24) has 8.7.1 (symptom_summary).
- Brief totals such as 6.3.x = 23 and 2.3.x = 10 are version-mention sums; thread counts are 16 and 8. LTU 1.1.1 is 1 real thread, not 2 (the second is an airMAX thread).
- KB v1 `fw_versions_mentioned` was regex-extracted from full text, so it over-reports (quoted changelogs) and under-reports (title-only versions).

Related: `docs/STAGE1230A_COMMUNITY_KB_V2_BINARY_RECONCILIATION.md`, `docs/STAGE1187A_UBIQUITI_COMMUNITY_FORUM_M_AC_LTU_FIELD_ISSUES_AND_KO_ROOT_CAUSES.md`, `docs/STAGE1192A_BINARY_RE_TO_FIELD_SYMPTOM_SIGNATURES_MATRIX.md`.
