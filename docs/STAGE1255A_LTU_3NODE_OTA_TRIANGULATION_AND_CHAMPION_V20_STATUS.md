<!-- doc-head: Stage 1255A one-shot passive read-only 3-path LTU OTA triangulation (Lite#1 .110 / Lite#2 jump / Rocket via LAP-120+Loco+ES-10XP) vs the 96A baseline, command allowlist, evidence limits, and what the repo receipts say about LTU champion v20 -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 1255A - LTU 3-node OTA triangulation (passive) and champion v20 status

- Evidence class: `PASSIVE_READ_ONLY_OBSERVATION`. This is NOT controlled live readiness evidence and promotes nothing.
- Probe: [`tools/bench/probe_stage1254a_ltu_3node_ota_triangulation.py`](../tools/bench/probe_stage1254a_ltu_3node_ota_triangulation.py)
- Receipt: [`artifacts/verification/stage1254a_ltu_3node_ota_triangulation_receipt.json`](../artifacts/verification/stage1254a_ltu_3node_ota_triangulation_receipt.json) (`generated_at` 2026-10-27T17:31:33Z, mode `live`)
- Run: once, 19.9 s of the 90 s budget, no retry (the Path B timeout is explained by the observed Lite#1 state, not a transient).

## 1. Observed state per path vs the Stage 96A baseline (`CONFIRMED_LIVE_HARDWARE`, passive reads)

Baseline = [`docs/STAGE96A_LIVE_LTU_TOPOLOGY_AND_SMP_BENCHMARK.md`](STAGE96A_LIVE_LTU_TOPOLOGY_AND_SMP_BENCHMARK.md) (2026-10-26).

| Path | Verdict | Observed evidence | vs 96A |
| :--- | :--- | :--- | :--- |
| A - LTU-Lite #1 `198.18.0.63` (direct) | `REACHABLE_NO_ASSOC` | SSH ok. `af get role`=`cpe-ptmp`, `state`=`Reset`, `remotelinks`=`TOTAL LINKS: 0`, 5500 MHz, `powerout`=13, `antennagain`=13; `ath0` operstate up / carrier 1; uptime 13094 s (about 3.6 h); ES-10XP shows its MAC on `gi5`. | DIVERGES: 96A recorded `AP-PTMP(Run)` 5500 MHz. |
| B - LTU-Lite #2 `PUBLIC_DEVICE_0043` (jump .110 -> `198.18.0.72:22`) | `UNREACHABLE` | `direct-tcpip` open failed: `Timeout opening channel`. No command reached Lite#2 (0 commands on Path B). | Consistent with "0 associations / not reachable over the air" at 96A. |
| C - LTU-Rocket `PUBLIC_DEVICE_0050` (LAP-120 `.20` -> Loco 5AC `198.18.0.67`) | `REACHABLE_NO_ASSOC` | Both SSH hops ok (LAP-120 uptime ~5.7 d, Loco ~2.8 d). `ip -6 neigh show dev br-lan` returned 0 entries, so no neighbour for `PUBLIC_DEVICE_0051`. Rocket MAC absent from the ES-10XP table. | Consistent with "no sign of the Rocket"; weak (see 3). |
| ES-10XP REST (`PUBLIC_DEVICE_0052%29`) | ok | `mac-table`: 324 entries. Lite#1 MAC on `gi5`; Lite#2 MAC on `gi7`; Rocket MAC on no port. | `gi7` carries a Lite#2 row although 96A recorded `gi7` DOWN (see 3). |

Reconciliation (`triangulation` in the receipt; recomputed offline once, see 5):
- `lite1_ap_online`: `DIVERGES_FROM_96A` (role is `cpe-ptmp`, state `Reset`, 0 links).
- `lite2_offline`: `INDETERMINATE` (jump unreachable, but a Lite#2 FDB row exists on `gi7`; row type/age were not recorded).
- `rocket_unpowered`: `CONSISTENT_WITH_96A` only as absence of evidence (empty neighbour table, MAC not in FDB).
- `ap_links_vs_lite2_jump`: `COHERENT` (0 AP links and Lite#2 not reachable over `ath0`).
- Lite#1 holds a `PERMANENT` neighbour/ARP entry `198.18.0.72 -> PUBLIC_DEVICE_0043` on `ath0` (flags `0x6`). Static entries are NOT liveness; the receipt lists it under `static_or_failed_bench_entries`, and `lite1_sees_macs` is `[]`.

Interpretation (`INFERRED`): Lite#1 booted about 3.6 h before the probe (13:53Z) with `role=cpe-ptmp` and `powerout`/`antennagain` 13 instead of the AP and thermal-guard values of the earlier RAM-only stages (17B, `antennagain 26`, `powerout 0`), so the RAM AP unlock was not re-applied. We did not read `rc.poststart`, so the cause is UNKNOWN. With Lite#1 not an AP, no OTA path to Lite#2 is expected.

## 2. Command allowlist and what was actually issued

- All commands are exact strings in `ALLOWLIST` (14 LTU reads, 1 LAP-120 read, 3 Loco reads). `validate_plan()` runs before any socket opens and `run_ssh_read()` re-validates each command.
- LTU reads: `/bin/af get role|state|remotelinks|frequency|powerout|antennagain`, `cat /proc/uptime`, `cat /sys/class/net/ath0/{operstate,carrier,address}`, `cat /sys/class/net/eth0/{address,carrier}`, `cat /proc/net/arp`, `ip neigh show`.
- Loco reads: `cat /proc/uptime`, `cat /sys/class/net/br-lan/address`, `ip -6 neigh show dev br-lan`. LAP-120: `cat /proc/uptime`.
- Rejected (tested, 31 negative cases): any redirect/pipe/chain/backtick/`$(`, `tee`, `sed`, `cfgmtd`, `mtd`, `dd`, `flash`, `reboot`, `restart`, `insmod`, `rmmod`, `sysctl`, `iwpriv`, `ifconfig`, `af set`, `echo`, `/dev/`, `iperf`, `ping`, file ops, `amecli`, trailing-space variants, and unlisted `af get` keys.
- REST: one `POST /api/v1.0/user/login` (token exchange only, changes no device state, counted as `auth_only_posts=1`) and one `GET /api/v1.0/tools/mac-table`. The contract said "REST GET only"; the login POST is unavoidable for the token, exactly as in 96A/98B.
- Targets allowed: `.110`, `198.18.0.72`, `.20`, `198.18.0.67` / `198.18.0.47`, ES-10XP link-local; `.241`, `.242`, any `*.84` are rejected by `validate_targets()`.
- Executed (derived from the ledger, not asserted): 18 SSH commands (14 Path A, 0 Path B, 1 LAP-120, 3 Loco) + 2 REST requests. `writes=0`, `dev_ame_opens=0`, `flash_writes=0`.
- Not covered by the allowlist logic: whether `/bin/af get ...` opens `/dev/ame*` internally. The contract permits `af get`; the count above counts command text only (`UNKNOWN` for binary internals).

## 3. Limits (read before using the numbers)

- Passive != readiness. Nothing here measured throughput, latency, or an A/B, and a single snapshot cannot show a link that comes and goes.
- SSH host keys are not verified (neighbour convention); only sha256 fingerprints are recorded. Credentials come from the shared loader and are never serialized (a leak check against the receipt text passed).
- Empty `ip -6 neigh` on Loco means no IPv6 traffic to the Rocket recently; it does not prove the Rocket is unpowered. 96A says the Rocket is wireless-only; Stage 17B says it sits on the Loco 5AC LAN port. Those two statements conflict, so the Path C meaning of "associated" (live neighbour on Loco `br-lan`) is `INFERRED` from 17B.
- The `gi7` Lite#2 FDB row: the first parse kept only mac/port/vlan, so entry type and age are not in the receipt (probe fixed for future runs: `bench_mac_rows`). The 96A "`gi7` DOWN, Lite#2 not on switch" claim is itself weak: in `run_stage96a_...audit_edgeswitch_10xp` the CLI-limit fallback hardcodes `gi7_down = True` and `ltu2_on_sw = False`. Treat the 96A gi7 state as unobserved in that branch. 98B separately records a historical Lite#2 FDB row on `0/7`.
- `af get state` for an AP without stations reads `Idle`, not `Run` (Stage 15/16 receipts show `state: Idle` with `TOTAL LINKS: 0`), so `state` alone is not an association signal; the probe uses `remotelinks`.

## 4. What the repo's own receipts say about LTU champion v20 (no new measurements)

Read: [`STAGE761A`](STAGE761A_LIVE_LTU110_ROUND22_264WINDOW_AUTORESEARCH.md), [`STAGE764A`](STAGE764A_LTU_22ROUND_264WINDOW_CHAMPION_V20.md), [`STAGE766A`](STAGE766A_LTU_264WINDOW_V20_AND_SQUASHFS_V20_GATE.md), [`STAGE774A`](STAGE774A_LTU_CHAMPION_V20_264WINDOW_ZERO_DHCP_KIT.md), [`STAGE935A`](STAGE935A_PBE_LTU_FAIL_CLOSED_KITS.md), [`STAGE937A`](STAGE937A_V23_ACTIVE_SOURCE_SHA256_MANIFESTS.md), the 761A/764A JSON receipts and the 766A gate receipt.

- Claimed (`CONFIRMED` in those docs): 22 campaigns / 66 A1-B1-A2-B2 rounds / 264 windows, all on `198.18.0.63`; stock mean RTT 0.231 ms vs v20 0.184 ms (-21.7 % in 774A); `zero_dev_ame_touches=true`; zero rogue DHCP; 180 WA/XC/XW v20 SquashFS images (765A).
- Scope of that evidence: single node `.110`. No Lite#1 <-> Lite#2 OTA peer and no Rocket in those windows; the docs read do not say what the RTT is measured against. v20 therefore has no OTA evidence in these receipts (SIMULATED/other classes aside, `UNKNOWN` for OTA). The OTA numbers in 96A (paired p50 5.295 ms / p95 7.085 ms, `Stage 63B`) are a different stack.
- On-disk status today (hashes computed this session):
  - `firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh` sha256 `edf58be7c1335da3d6e1daf3200ee63acf503e0c52dacf7ec7270480165aba4a`, 23 lines: a retired-actuator stub (`PLANNED_RETIRED`, apply/verify/rollback exit 65). The 764A receipt/doc pin `c6e6499d8cc7af8f0dbdc4db5e8c7052deaa42af45a444871d9585653aec226c`: MISMATCH (recorded both, flagged).
  - `firmware/ltu_safe_kit/fmx_ltu_v20_264window_zero_dhcp_kit.sh` has the same sha256 `edf58be7...` (identical stub). The 774A doc pins `395c397fae42ec7024621e41d170e4816760d908539f543bda39795aaae514ae`: MISMATCH.
  - `firmware/ltu_safe_kit/ltu_5board_universal_manifest_v20.json` sha256 `911f7eefb734135d181500f0d7fb5b2615badc0ebd7fcb4558bb3440b225261e` (present; not compared to any prose hash).
  - 935A: 42 active entrypoints = 2 native transactions + 40 retired legacy actuators; original bytes retained privately. Static-source provenance is not hardware acceptance; "Physical acceptance, LTU native compatibility and runtime performance: UNKNOWN".
- Net status of v20: a historical, `.110`-only measurement claim whose activating script is retired in the v23 source boundary. The native replacement (`fmx_ltu_runtime_transaction.sh`, transient `tx_queue_len` / `netdev_max_backlog` only) is a different, much smaller thing, with hardware acceptance `UNKNOWN`.
- Internal contradiction to resolve: 764A/761A say IRQ 52 (`ame_asic0`) is `smp_affinity=2` (CPU1); 96A pins IRQ 52 (`AME.mrx`) on CPU0 and IRQ 63/92 on CPU1. Both are labelled `CONFIRMED`.

## 5. Probe public API (for tests) and one deviation

- Pure: `validate_commands`, `validate_rest_requests`, `validate_targets`, `validate_plan`, `build_plan`, `plan_commands`, `forbidden_tokens_in`, `parse_af_status`, `parse_uptime`, `parse_neigh`, `parse_arp`, `find_neigh`, `macs_seen`, `is_dynamic_entry`, `static_bench_entries`, `bench_relevant`, `parse_es_mac_table`, `es_ports_for_macs`, `es_entries_for_macs`, `verdict_for_ltu_path`, `verdict_for_rocket_path`, `build_triangulation`, `classify_ledger_entry`, `derive_counts`, `build_receipt`, `dry_run_paths`, `rederive_from_recorded`.
- Verdict enum `VERDICTS`: `REACHABLE_ASSOCIATED`, `REACHABLE_NO_ASSOC`, `UNREACHABLE`, `BLOCKED_NO_CREDENTIAL`, `NOT_ATTEMPTED`. An SSH auth rejection maps to `BLOCKED_NO_CREDENTIAL` (one attempt per hop, no retry).
- Network (lazy `paramiko` import): `run_live`, `run_path_a_and_b`, `run_path_c`, `run_es10xp_mac_table`, `run_ssh_read`, `load_credentials`.
- Deviation: after the live run the derivation was corrected (PERMANENT/failed neighbour entries had been counted as MAC sightings, and unrelated LAN hosts were in the neighbour dump). The receipt was re-derived offline from its own recorded observations via `rederive_from_recorded` (no new network traffic; the note is in `notes`). Raw observations are unchanged.

## 6. Next safe steps (all need explicit operator choice; none taken here)

1. Decide whether to power Lite#2 and the Rocket for a controlled bench session. Do not infer power from the `gi7` FDB row; read the `gi7` link state from the ES-10XP before any plan.
2. Read-only follow-up that needs no new authorisation beyond this one: compare `/etc/persistent/rc.poststart` content on `.110` (cat only) with the persisted 96A fix to explain `cpe-ptmp` after the reboot.
3. Before any v20 claim is reused: re-pin or retire the 764A/774A hashes against the stub, and reconcile the IRQ 52 CPU0/CPU1 contradiction.
4. Any OTA A/B for v20 needs a powered, associated pair and a gated runner (unified runner, Stage 964A); this passive probe cannot substitute for it.
