<!-- doc-head: STAGE79B_CLOSED_LOOP_AUTO_REMEDIATION_ORCHESTRATOR.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 79B — Closed-Loop Auto-Remediation Orchestrator & Guarida Canary Readiness Gate

- **Status**: `CONFIRMED`
- **Task ID**: `T-S79B-CLOSED-LOOP-AUTO-REMEDIATION-AND-GUARIDA-CANARY-READINESS-GATE`
- **Orchestrator Implementation**: [`run_stage79b_closed_loop_auto_remediation_orchestrator.py`](<repo>/tools/telemetry/run_stage79b_closed_loop_auto_remediation_orchestrator.py)
- **Receipt Artifact**: [`stage79b_closed_loop_auto_remediation_orchestrator_20261026.json`](<repo>/artifacts/autoresearch/stage79b_closed_loop_auto_remediation_orchestrator_20261026.json)
- **Unit Test Suite**: [`test_stage79b_closed_loop_auto_remediation.py`](<repo>/tests/test_stage79b_closed_loop_auto_remediation.py)

---

## 1. Architecture & Multi-Layer Attribution (`CONFIRMED`)

`Stage 79B` connects the `Stage 78A` live multi-generation `aeon` regime classifier bridge (`classify_all_multigen_links`, `classify_multigen_collector_window`) directly to our `Stage 29B/74A/74B` deploy packager ([`guarida_stage29b_deploy_packager.py`](<repo>/tools/deploy/guarida_stage29b_deploy_packager.py)) and our `45s` auto-rollback watchdog contract (`fmx_autoresearch_harness.py`) in deterministic dry-run / shadow-execution mode (`automatic_execution_allowed = False`, `live_devices_touched = False`).

- **Layer Attribution**:
  - `external controller`: `Stage 79B` Closed-Loop Auto-Remediation Orchestrator, pre-flight safety filter (`verify_stage79b_preflight_safety_filter`), and Uptime Kuma push gate.
  - `Linux`: Almafuerte BNG `sch_cake` queue tree (`46.0 Mbps` hierarchical CAKE) and `AF-LTU` Dual-Core Cortex-A7 RPS split (`eth0=2`, `eab0=1`).
  - `mac80211`: OpenWrt AP AQL (`AC_BE=1500/3000`, `aql_threshold=5000`, `FMX-DISC-19`).
  - `ath10k` / `hardware`: `QCA988x` `survey_active_time_ms` & `channel_busy_pct` telemetry and `XC` AirPrism Stage 1 pre-selector (`max_width <= 50 MHz`, `FMX-DISC-20`).
  - `proprietary airMAX/LTU module`: `umac.ko` (`set_multiq=3` `UMAC-BUG-01`), `ubnt_poll_host.ko` (`daprot=2`, `ff_mcast_airtime_limit=5`), and `AF-LTU` `ame_core.ko` (`rx_gain=low`, `tx_power_Auto=0`, `tx_power=24`, `max_tx_mod_idx=12`).

---

## 2. Five-Regime Closed-Loop Auto-Remediation Matrix (`CONFIRMED`)

| `aeon` Regime ID & Name | Action ID | `kuma_push_allowed` | `rf_mutation_blocked` | Key Invariants & Remediation Knobs (`45s` Watchdog Guarded) |
| :--- | :--- | :---: | :---: | :--- |
| `0: NORMAL_LOAD` | `NO_OP_KEEP_CHAMPION` | `True` | `False` | Keep active Champion (`Champion v20` / `PtP v6` / `LTU patch`); `0` RF commands emitted. |
| `1: CO_CHANNEL_INTERFERENCE` | `APPLY_STAGE71B_73A_AIRPRISM_50MHZ_AND_DAPROT2` | `True` | `False` | `FMX-DISC-20` AirPrism Stage 1 `max_width <= 50 MHz` (`iwpriv wifi0 chanbw 20`), `daprot=2`, `ff_mcast_airtime_limit=5`, `Stage 73A PtP v6` + `45s` rollback timer. |
| `2: BAD_APPLE_AIRTIME_HOG` | `APPLY_STAGE72A_75A_MULTIQ3_AQL_AND_BNG_CAKE` | `True` | `False` | `Stage 72A/75A` `set_multiq=3` (`UMAC-BUG-01`) + OpenWrt AP `aql_txq_limit` (`AC_BE=1500/3000`, `aql_threshold=5000` `FMX-DISC-19`) + Almafuerte BNG `sch_cake` isolation + `45s` rollback timer. |
| `3: LTU_BUG05_LNA_DEAFNESS` | `APPLY_STAGE63B_68B_LTU_LNA_AND_RPS_REMEDIATION` | `True` | `False` | `Stage 63B/68B` `rx_gain=low`, `tx_power_Auto=0`, `tx_power=24`, `max_tx_mod_idx=12`, `ulautogain 0`, `ulpwrtune -75`, RPS `eth0=2` / `eab0=1` + `45s` rollback timer. |
| `4: FROZEN_COLLECTOR_FALSE_ALARM` | `SUPPRESS_RF_FALSE_ALARM_RESTART_COLLECTOR_ONLY` | `False` | `True` | Hard-blocks all RF knob mutations (`rf_remediation_commands = []`); triggers local collector self-restart (`systemctl restart fmx-rf-collector.service`). |

---

## 3. Pre-Flight Safety Gate Verification (`CONFIRMED`)

- **Guarida Backbone Rule (`198.18.0.2` `ether2-sw-poe200`)**: `protects_ether2_sw_poe200 = True` across all 5 regime bundles; negative probe (`set ether2-sw-poe200 disabled=yes`) deterministically rejected (`all_safety_checks_passed = False`).
- **Protected Partitions (`mtd0`, `mtd1`, `mtd5`)**: `protects_mtd0_mtd1_mtd5 = True` across all 5 regime bundles; negative probe (`mtd write /tmp/bad.bin mtd5`, `dd if=/dev/zero of=/dev/mtd0`) deterministically rejected (`all_safety_checks_passed = False`).

---

## 4. Five-Pillar Compliance Summary (`5/5 PASS`)

- **Pillar A**: Synthesizes exact binary/module remediation knobs (`FMX-DISC-19`, `FMX-DISC-20`, `UMAC-BUG-01`, `LTU-BUG-05`).
- **Pillar B**: Synced to `ClosedLoopResearchReactor` (`discovery_to_research_queue.json`) and grounded in Dempster et al. (2020/2021) + Høiland-Jørgensen et al. (2016/2018).
- **Pillar C**: Enforces `45s` auto-rollback watchdog timers on all active RF remediations.
- **Pillar D**:Validated across all 5 live multi-generation links and 5 operational regimes (`0.0%` false-positive RF mutation rate).
- **Pillar E**: Durable MemoryMaster claim `mm-stage79b-closed-loop-auto-remediation-orchestrator-20261026` synced to `memorymaster.db`.
