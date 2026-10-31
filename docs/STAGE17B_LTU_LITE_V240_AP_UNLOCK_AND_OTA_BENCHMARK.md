<!-- doc-head: STAGE17B_LTU_LITE_V240_AP_UNLOCK_AND_OTA_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 17B — `LTU-Lite` (`afltu.v2.4.0` / `v2.4.2`) `AP-PtMP` (`SQ` Short-Queue Mode) & `AP-PtP` Dual-Lock Bypass + Separated LTU Benchmark

- **Task ID**: `T-S17B-LTU-LITE-V240-AP-UNLOCK-AND-SEPARATED-BENCH`
- **Status**: `CONFIRMED` on Live `LTU-Lite` (`PUBLIC_DEVICE_0046%27`, `LTU.afltu.v2.4.0`, EdgeSwitch 10XP `gi5`)
- **Receipt**: [`artifacts/autoresearch/stage17b_ltu_lite_v240_ap_unlock_and_ota_20261025.json`](../artifacts/autoresearch/stage17b_ltu_lite_v240_ap_unlock_and_ota_20261025.json)
- **Runner**: [`tools/bench/run_stage17b_ltu_lite_ap_and_separated_ota.py`](../tools/bench/run_stage17b_ltu_lite_ap_and_separated_ota.py)

---

## 1. Ground-Up Reverse Engineering: Why `v2.1.0` `LTU-Lite` AP Mode Stopped Working in `v2.4.0` / `v2.4.2` — And How We Unlocked Both `AP-PtMP` (`SQ`) and `AP-PtP`

In `LTU.afltu.v2.1.0`, setting `role=ap` in `/tmp/system.cfg` was sufficient to run an `LTU-Lite` (`board_ssid = 0xae08`) as a micro-sector PtMP AP (`ptmp_max_cpe = 4` `SQ` Short-Queue mode) for 3–4 nearby subscribers.

By disassembling `/lib/modules/3.14.65/ame_dev.ko` and `/bin/air_fpga` from `LTU.afltu.v2.4.0` / `v2.4.2`, we identified the **two hardware-ID checks** Ubiquiti added after `v2.1.0` and a critical flaw in how both checks read `board_ssid`:

1. **Lock 1 — Kernel Driver (`ame_dev.ko` `ame_config_handler` at `0x7fc..0x840`)**:
   - When `sys_mode == "normal"` (`[r8, #0x1c] == 1`) and `role == "ap"` (`[r8, #0x20] == 1`), `ame_config_handler` checks `[r8, #0x29c]` (`board_ssid` parsed from `/tmp/ame.cfg`) against `0xae05` (`LTU-Rocket`) and `0xae0e`.
   - If `board_ssid` is `0xae08` (`LTU-Lite`), it overwrites `[r8, #0x20] = 2` (`cpe`) and prints `*** PtMP Build force set XHD and LTU CPEs as CPE ****`.
2. **Lock 2 — Userspace Daemon (`/bin/air_fpga` `set_cfg_role` at `0x1b4c1c..0x1b4c6c`)**:
   - Checks `g_cfg.board_ssid` (`[0x26b938 + 0x17c]`) against `0xae05` and `0xae0e`. If not equal, it overwrites `g_cfg.role = 2` (`TYPE_CPE`).
3. **The Flaw (`LoadConfig` at `0x1b8c60` in `/bin/air_fpga`)**:
   - `LoadConfig` parses `/tmp/ame.cfg` **first**, and then executes:
     ```c
     if (g_cfg.board_ssid == 0) {
         // Only reads /proc/ubnthal if board_ssid was NOT set in /tmp/ame.cfg!
     }
     ```
   - Because `/usr/bin/ame_drv.sh` pre-populates `board_ssid = 0xae08` in `/tmp/ame.cfg`, changing `board_ssid = 0xae05` in `/tmp/ame.cfg` before `ame_drv.sh restart` satisfies **both Lock 1 (`ame_dev.ko`) and Lock 2 (`/bin/air_fpga`)** without touching flash or `/proc/ubnthal`!

### Verified Live Unlock Recipes on `LTU.afltu.v2.4.0` (100% RAM-Only)

- **Unlock `AP-PtMP` (`SQ` Short-Queue Micro-Sector Mode, `ptmp_max_cpe = 4`)**:
  ```sh
  sed -i 's/^board_ssid.*/board_ssid = 0xae05/' /tmp/ame.cfg
  sed -i 's/^role.*/role = ap/' /tmp/ame.cfg
  sed -i 's/^mode.*/mode = ap/' /tmp/ame.cfg
  sed -i 's/^;ptmp_max_cpe.*/ptmp_max_cpe = 4/' /tmp/ame.cfg
  sed -i 's/^ptmp_max_cpe.*/ptmp_max_cpe = 4/' /tmp/ame.cfg
  ame_drv.sh restart
  ```
  - **Live Hardware Verification (`PUBLIC_DEVICE_0046%27`)**:
    - `/bin/af get role` $\rightarrow$ **`ap-ptmp`**
    - `/bin/af get wiremode` $\rightarrow$ **`ptmp`**
    - `dmesg` $\rightarrow$ `AP_SYS_SM state transition INIT >>> SCAN_WAIT_UNLOCKED >>> RUN`, `StartRadio() [rx:5825 tx:5825] OK`!

- **Unlock `AP-PtP` Mode on `LTU-Lite` (`v2.4.0`)**:
  ```sh
  /bin/af set sysmode test
  /bin/af set wiremode ptp
  /bin/af set role ap
  ```
  - **Live Hardware Verification (`PUBLIC_DEVICE_0046%27`)**:
    - `/bin/af get role` $\rightarrow$ **`ap-ptp`**
    - `/bin/af get wiremode` $\rightarrow$ **`ptp`**

---

## 2. Separated LTU Topology Audit & Incremental Champion Benchmark (`A1 -> B1 -> A2 -> B2`)

| Unit | Connection / Port | Live Role / Mode | Thermal Guard | Status |
| :--- | :--- | :--- | :--- | :--- |
| **`LTU-Lite #1` (`PUBLIC_DEVICE_0045`)** | `ES-10XP` `gi5` (`Boca 5`, `UP`) — `PUBLIC_DEVICE_0046%27` | **`ap-ptmp` (`SQ` `ptmp_max_cpe=4`, `5825 MHz`)** | `antennagain=26`, `powerout=0` (`-26 dBm`) | **ONLINE & BENCHMARKED** |
| **`LTU-Rocket` (`PUBLIC_DEVICE_0050`)** | `NanoStation 5AC Loco` (`198.18.0.67`) `br-lan` — `PUBLIC_DEVICE_0051%br-lan` | `cpe-ptmp` (`5825 MHz`) | `antennagain=26`, `powerout=0` (`-26 dBm`) | **ONLINE via `Loco 5AC` LAN** |
| **`LTU-Lite #2` (`PUBLIC_DEVICE_0043`)** | `ES-10XP` `gi2` (`Boca 2`, `24V PoE Enabled`) | — | — | `GigabitEthernet2 is down` (RJ45 cable loosened when separating unit) |

### Incremental Autoresearch Rounds on Unlocked `LTU-Lite #1` (`ap-ptmp` `SQ` Mode)

| Round | Control Arm `A` (`ltu_lite_amesoc` Champion) | Treatment Arm `B` (Champion + Candidate Mutation) | Arm `A` Goodput | Arm `B` Goodput | Arm `A` `p95` RTT | Arm `B` `p95` RTT | `p95` $\Delta$ | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S17B-R1`** | `ltu_lite_amesoc` Champion in `ap-ptmp` `SQ` (`ptmp_max_cpe=4`) | Champion + `tcp_low_latency=1` + `tcp_notsent_lowat=16384` + `change_ssd_pause_flag=1` | `14.13 Mbps` | `13.88 Mbps` | `30.29 ms` | `31.24 ms` | `+3.13%` | **`RETAIN_CURRENT_CHAMPION`** |
| **`S17B-R3`** | `ltu_lite_amesoc` Champion in `ap-ptmp` `SQ` (`ptmp_max_cpe=4`) | Champion + `sched_mcs_limit_symbol_begin=14` + `send_map_enable=1` | `14.13 Mbps` | `14.12 Mbps` | `31.45 ms` | **`30.56 ms`** | **`-2.84%`** | **`PROMOTE_NEW_CHAMPION`** (`+0.89%` Pareto score, `0.0%` loss) |
