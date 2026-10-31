<!-- doc-head: STAGE62A_PBE5AC_IRQ33_SPECTRAL_STORM_AND_REMOTE_OTA_OPENWRT_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 62A: PowerBeam 5AC Gen2 Ground-Up `IRQ 33`/`IRQ 2` Spectral Dissection, 571-Knob Catalog WEXT/UMAC Benchmark & Staged Hybrid OTA OpenWrt Kit

- **Stage / Ticket**: `Stage 62A` (`T-S62A-PBE5AC-IRQ33-SPECTRAL-STORM-SUPPRESSION-571KNOB-CATALOG-AND-REMOTE-OTA-SQUASHFS-REPACK`)
- **Date**: `2026-10-26`
- **Target Hardware**:
  - `198.18.0.45` (`198.18.0.8`, `PUBLIC_DEVICE_0038`, `PBE-5AC-Gen2` `0xe3d6`, `WA.v8.7.11` AP)
  - `198.18.0.46` (`198.18.0.74`, `PUBLIC_DEVICE_0037`, `PBE-5AC-Gen2` `0xe3d6`, `WA.v8.7.11` Remote OTA STA)
- **Artifacts & Tools**:
  - [`tools/bench/run_stage62a_pbe5ac_irq33_571knob_and_ota_image_bench.py`](../tools/bench/run_stage62a_pbe5ac_irq33_571knob_and_ota_image_bench.py)
  - [`tools/deploy/build_remote_ota_prebaked_openwrt_images.py`](../tools/deploy/build_remote_ota_prebaked_openwrt_images.py)
  - [`artifacts/autoresearch/stage62a_pbe5ac_irq33_571knob_and_ota_image_bench_20261026.json`](../artifacts/autoresearch/stage62a_pbe5ac_irq33_571knob_and_ota_image_bench_20261026.json)
  - [`firmware/openwrt/pbe5ac_gen2_ptp_kit/pbe5ac_remote_ota_prebaked_manifest_20261026.json`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/pbe5ac_remote_ota_prebaked_manifest_20261026.json)
  - [`tests/test_stage62a_pbe5ac_irq33_and_ota_image.py`](../tests/test_stage62a_pbe5ac_irq33_and_ota_image.py)

---

## 1. Five-Pillar Ground-Up Dissection (`IRQ 33` vs `IRQ 2` & 571-Knob Catalog)

1. **Pillar A — Ground-Up Interrupt & Binary Attribution (`CONFIRMED`)**:
   - Inspecting `/proc/interrupts` and running processes on `.241` and `.242` revealed `/bin/ubntspecd -w -t -a -i wifi1 -j airview1 -m 4 -f` driving the secondary 2.4 GHz `AR9342` AHB radio (`wifi1` / `airview1` on `IRQ 2`).
   - **Critical Hardware Separation (`CONFIRMED`)**:
     - When the 5 GHz link is idle, pausing `ubntspecd` and bringing down `wifi1`/`airview1` cuts `IRQ 2: wifi1` to `0.0/sec` (`-100%`) and drops `IRQ 33: ATH GPIO ath-spectral-filter` to `~114/sec`.
     - However, during active 5 GHz `QCA9882` (`wifi0`) Triple-Play RF transfer (`S62A-R1`), `IRQ 33` fires at `1,680.9/sec` on AP and `1,739.4/sec` on STA even when `wifi1`/`airview1` are completely down (`IRQ 2 = 0.0/sec`), proving `IRQ 33` (`ath-spectral-filter` GPIO) is hardware-coupled to the 5 GHz `wifi0` AirPrism active-RX path (`attribute: hardware / proprietary airMAX module`).
     - Furthermore, dynamically toggling `ifconfig wifi1 down` / `up` on a live bridge (`br0`) triggers Linux bridge/netdev state transitions that degrade Bulk TCP (`-21.28%`) and raise `p95` RTT (`+75.93%` -> `DISCARD`).
2. **Pillar A + C — 571-Knob Catalog WEXT/UMAC Breakthrough (`S62A-R2` -> `KEEP`)**:
   - Pulling the `WA` WEXT/UMAC parameters from `orchestration/autoresearch/firmware_knob_candidates.json` (`wa_8_7_25_wext_set_multiq_b85c` -> `iwpriv ath0 set_multiq 1`, `iwpriv wifi0 aggr_swretry 6`, `iwpriv wifi0 nonaggr_swretry 8`, `umac.enable_tx_tcp_cksum=1`, `net.core.netdev_budget=800`, `tcp_limit_output_bytes=98304`) on top of `S60A-R3` (`AC_BE cwmin=3, cwmax=6`, `RPS=1`, `tx_queue_len=192`) delivered a massive improvement across all 3 Triple-Play classes.

---

## 2. Counterbalanced 12-Window Over-The-Air Benchmark Results (`198.18.0.8 -> 198.18.0.74`)

| Round | Candidate Treatment | Arm A Goodput (Mbps) | Arm B Goodput (Mbps) | Goodput $\Delta$ | Bulk TCP $\Delta$ | Arm A `p50`/`p95` (ms) | Arm B `p50`/`p95` (ms) | AP `IRQ 2` (`/sec`) | Karpathy `fmx_loss` (`A -> B`) | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S62A-R1`** | `ubntspecd` pause + `wifi1`/`airview1` interface down | `25.352` | `21.837` | `-13.86%` | `-21.28%` | `2.455` / `4.483` | `2.570` / `7.887` | `107.7 -> 0.0` (`-100%`) | `0.0705 -> 0.2133` | **`DISCARD`** (`CONFIRMED`) |
| **`S62A-R2`** | **571-Knob Catalog WEXT/UMAC (`set_multiq=1`, `aggr_swretry=6`, `nonaggr_swretry=8`, `enable_tx_tcp_cksum=1`, `budget=800`)** | `20.328` | **`25.615`** | **`+26.01%`** | **`+33.09%`** | `2.433` / `6.889` | `2.521` / `7.438` | `0.0 -> 0.0` | **`0.1803 -> 0.1235`** | **`KEEP` (`Stage 62A Champion v4`)** |
| **`S62A-R3`** | Combined `wifi1 down` toggle + 571-Knob Catalog | `21.309` | `15.543` | `-27.06%` | `-35.41%` | `2.560` / `4.836` | `2.838` / `8.059` | `0.0 -> 0.0` | `0.1466 -> 0.2956` | **`DISCARD`** (`CONFIRMED`) |

- **Flash Persistence Receipt (`CONFIRMED`)**:
  - `S62A-R2` (`Stage 62A PowerBeam 5AC Gen2 PtP Champion v4`) persisted to `/etc/persistent/rc.poststart` + `cfgmtd -w -p /etc/` on both `198.18.0.45` (`CFGMTD_RC=0`) and `198.18.0.46` (`CFGMTD_RC=0`).

---

## 3. Staged Hybrid Interop (`airOS 8` AP $\leftrightarrow$ `OpenWrt` STA First) + Pre-Baked OTA OpenWrt Kit

Per `AGENTS.md` §2 & §14.6:
1. **Binary Layout Verification (`0xe3d6` `ubnt_powerbeam-5ac-gen2`)**:
   - `factory.bin`: UBNT `OPEN` header, uImage at `0x10c`, SquashFS `hsqs` v4.0 at `0x280184` (`8,389,004` bytes, fits `fwupdate.real`).
   - `sysupgrade.bin`: uImage at `0x0`, SquashFS `hsqs` v4.0 at `0x280000` (`8,388,612` bytes).
2. **Step 1 — Hybrid `airOS 8` AP (`.241`) $\leftrightarrow$ `OpenWrt 24.10.4` STA (`.242`) Enabler**:
   - [`enable_airos8_ap_hybrid_80211_for_openwrt_sta.sh`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/enable_airos8_ap_hybrid_80211_for_openwrt_sta.sh) (`SHA-256: 5fbf2d00...`) sets `allow_80211=1` + `op_mode=0` (`uph.ko` CSMA/CA WDS admission) + `iwpriv ath0 wds 1` on `.241` BEFORE flashing remote `.242` Over-The-Air, so `.242` associates to `.241` while `.241` is still on `airOS 8.7.11`.
3. **Step 2 — Embedded Automatic Rollback Watchdog (`/usr/sbin/fmx_ptp_rollback_watchdog.sh`)**:
   - Embedded inside both `sysupgrade-overlay-pbe5ac-ptp-sta-242.tar.gz` (`SHA-256: 233f6844...`) and `sysupgrade-overlay-pbe5ac-ptp-ap-241.tar.gz` (`SHA-256: 3f75581c...`) alongside `/etc/uci-defaults/99-fmx-preconfig` and `/etc/rc.local` (`180s` peer ping timeout -> automatic WDS/channel fallback scan).
