<!-- doc-head: STAGE428A_LIVE_PBE5AC_GROUND_UP_RAM_CANARY_AND_RESCUE_DAEMON.md preserved document content -->
<!-- /doc-head -->



# Stage 428A — Live `PowerBeam 5AC Gen2` (`.241 <-> .242`) Ground-Up Rescue Daemon & WMI Hook Deployment

## 1. Objective & Closed-Loop Architecture
- **Objective**: Deploy and verify live on `.241` (`FMX-PBE5AC-AP-241`) and `.242` (`FMX-PBE5AC-STA-242`) the Ground-Up closed-loop daemons:
  1. [`fmx_chain_imbalance_rescue_daemon.sh`](../firmware/openwrt/common/fmx_chain_imbalance_rescue_daemon.sh) (`Stage 349A`): Polls per-chain RSSI (`chain0` vs `chain1`) every `2s` and clamps TX to `1x1 VHT-NSS 1` (`SIMO_TX_2X2_MRC_RX`) while keeping `2x2` MRC RX (`rx_ant=3`) whenever `|chain0 - chain1| >= 6 dB`.
  2. [`fmx_wmi_retry_and_hook_loader.sh`](../firmware/openwrt/common/fmx_wmi_retry_and_hook_loader.sh) (`Stage 409A`): Configures bounded HTT A-MSDU/A-MPDU aggregation, hardware retry limits (`iw phy phy0 set retry`), and exports `/tmp/fmx_wmi_state/wmi_retry_hook_state.json` (`WMI 0x9044` `PEER_RATE_RETRY_SCHED` & `WMI 0x9064` `FWHook`).

---

## 2. Live Deployment & Fault-Injection Verification (`CONFIRMED`)
- Both scripts were deployed to `/usr/sbin/fmx_chain_imbalance_rescue_daemon.sh` (`0755`) and `/usr/sbin/fmx_wmi_retry_and_hook_loader.sh` (`0755`) on `.241` and `.242` via [`run_stage428a_live_pbe5ac_ground_up_ram_canary_and_rescue_daemon.py`](../tools/benchmarks/run_stage428a_live_pbe5ac_ground_up_ram_canary_and_rescue_daemon.py).
- **Closed-Loop Fault Injection Test**:
  1. `.242` (`STA`) was intentionally reset to `active=0` (`MIMO_2X2_VHT_NSS2`), exposing it to the `9 dB` chain imbalance (`[-64, -55] dBm`).
  2. `fmx_wmi_retry_and_hook_loader.sh phy0 phy0-sta0 9` and `fmx_chain_imbalance_rescue_daemon.sh phy0-sta0 phy0` were invoked on `.242`, and `fmx_wmi_retry_and_hook_loader.sh phy0 phy0-ap0 5` on `.241`.
  3. Both nodes generated `/tmp/fmx_wmi_state/wmi_retry_hook_state.json` (`wmi_peer_rate_retry_cmdid = 0x9044`, `wmi_fwhook_cmdid = 0x9064`), restored `1x1 VHT-NSS 1 MCS 2 LGI` (`pream=3 nss=0 mcs=2 sgi=0`) on `.242`, and passed the post-rescue `1472B` full-MTU ping verification.

## 3. Artifacts & Verification
- Script: [`run_stage428a_live_pbe5ac_ground_up_ram_canary_and_rescue_daemon.py`](../tools/benchmarks/run_stage428a_live_pbe5ac_ground_up_ram_canary_and_rescue_daemon.py)
- JSON Artifact: [`stage428a_live_pbe5ac_ground_up_ram_canary_and_rescue_daemon.json`](../artifacts/autoresearch/stage428a_live_pbe5ac_ground_up_ram_canary_and_rescue_daemon.json)
- Test Suite: [`test_stage428a.py`](../tests/test_stage428a.py)
