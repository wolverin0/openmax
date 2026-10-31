<!-- doc-head: STAGE47B_BOCA7_LIVE_FLASH_AND_OTA_VERIFICATION.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 47B — Boca 7 (`LTU-Lite #2`) Live Flash & OTA Association Verification (`AP-PTMP(Run)` $\leftrightarrow$ `CPE-PTMP(Run)`)

- **Task ID**: `T-S47B-BOCA7-LIVE-FLASH-AND-OTA-ASSOCIATION-VERIFICATION`
- **Date**: `2026-10-26T00:09:30Z`
- **Verdict**: **CONFIRMED (`AP-PTMP(Run)` $\leftrightarrow$ `CPE-PTMP(Run)` OTA Link UP at 5500 MHz / 20 MHz, `Stations count: 1`, `SpectrumEfficient: 1535 / 1319`, Dual-Partition Flash Persisted `[%100]`)**

---

## 1. Executive Summary

Following the connection of **`LTU-Lite #2` (`PUBLIC_DEVICE_0043`)** on **`Boca 7` (`gi7`)**, we deployed the Stage 45B/47B persistent configuration (`SSID="FMX-LTU"`, `+15 dBm` conducted TX power / `28 dBm` EIRP, `autolink_en=1`, alternating `5500 5520 5500 5520` scan list) and committed it to both flash partitions via `cfgmtd -w -p /etc/` (`Storing Active[1] ... [%100]`, `Active->Backup[2] ... [%100]`).

Within **5.1 seconds** of restarting `ame_drv.sh` on `LTU-Lite #2` (`[ 6639.223536]` to `[ 6644.316280]`), `LTU-Lite #2` (`Boca 7`) matched the 7-byte `"FMX-LTU"` beacon from **`LTU-Lite #1` (`Boca 5`, `PUBLIC_DEVICE_0045`)**, completed SFN/CIR synchronization (`State[CIRE] -> [LOCK_DONE]`), negotiated Timing Advance (`TA=235`) and secondary timing alignment (`TA2_monitor_done_cpe(0)_shift(0)`), built hardware EAB super-queues (`AME_EAB_MakeSuperQueue cfg=00010001`), and entered **`CPE-PTMP(Run)`** (`now state 3`, `update air 0 => 3`).

---

## 2. Hardware Proof of the 16-Byte Beacon SSID Root-Cause Fix

### 2.1 Before (`"FuturaMAX-LTU-Bench"`, 19 bytes)
- `ame_core_beacon_update` (`0x007008`) copies at most 16 bytes into the hardware beacon buffer (`[s_beacon, #0x0e..0x1d]`), broadcasting `"FuturaMAX-LTU-Be"`.
- On the CPE, `slm_find_preferred_record` (`0x045e20`) printed `coming: [FuturaMAX-LTU-Be]` and failed `strcmp("FuturaMAX-LTU-Be", "FuturaMAX-LTU-Bench")`, never printing `preferred freq: 5500`.

### 2.2 After (`"FMX-LTU"`, 7 bytes) — Live Kernel `dmesg` on `LTU-Lite #2` (`Boca 7`)
```text
[ 6624.681410] [CFG] SYS.board_ssid = 0xae08
[ 6624.681497] [CFG] SYS.ssid = "FMX-LTU"
[ 6639.223536] [modem/5] cpeFsmCheckSFO(906): <cpeFsm> Valid beacon
[ 6639.223565] [slm/5] slm_find_preferred_record(488): coming: [FMX-LTU] bw 20, txfreq 5500, rxfreq 5500
[ 6639.223575] [slm/5] slm_find_preferred_record(524): preferred freq: 5500
[ 6644.025407] [modem/5] cpeFsmCheckCIREst(1113): <cpeFsm> cpeFsmCheckCIREst and SFN sync done
[ 6644.025436] [modem/5] EDSM_NextRun(125): State[CIRE] -> [LOCK_DONE]
[ 6644.026562] [modem/5] cpeFsmLockDone(1143): <cpeFsm> decode_sig_strength is 178
[ 6644.026584] [modem/5] cpeFsmLockDone(1146): <cpeFsm> LockDone
[ 6644.316280] [core/5] ame_core_ioctls_callback(2157): now state 3
[ 6644.356890] [eab/5] AME_EAB_MakeSuperQueue(5537): <eab> AME_EAB_MakeSuperQueue cfg=00010001 for 0(1).
[ 6644.360846] [core/5] ame_core_update_ta_cpe(1556): TA=235, ack(delay:range)=(-896:11805), data_ctrl=(-1075,11984)
[ 6644.361984] [core/5] ame_core_ptmp_cpe_range_update_ta(7682): TA applied: 235
```

### 2.3 Live Kernel `dmesg` on `LTU-Lite #1` (`Boca 5` Master AP)
```text
[ 8975.623737] [eab/5] AME_EAB_MakeSuperQueue(5537): <eab> AME_EAB_MakeSuperQueue cfg=00010001 for 0(1).
[ 8975.635995] [core/5] ame_core_updateTA(1606): [UP] TA: 0->235
[ 8975.677755] [ctrl/5] ctrlMsgHandler(2201): CPE[0] TA applied, shift:0, now trigger TA2
[ 8975.681447] [bbp/5] ame_bbp_op_2ndTA(418): set_TA2_monitor_cpe(0)_symIdx(0)_sfn(6730742)
[ 8975.683453] [bbp/5] ame_bbp_op_2ndTA(372): TA2_monitor_done_cpe(0)_shift(0)_sfn(6730744)_notify(X)
[ 8975.691922] [core/5] ame_core_ioctls_callback(2083): now user 1
[ 8975.691952] ath0: clear __LINK_STATE_NOCARRIER
[ 8975.691976] [core/5] ame_core_set_air_status(753): update air 0 => 3
```

---

## 3. Live `amecli` Status on Both Units

| Metric | `LTU-Lite #1` (`Boca 5` Master AP) | `LTU-Lite #2` (`Boca 7` Station CPE) |
| :--- | :--- | :--- |
| **MAC Address** | `PUBLIC_DEVICE_0045` | `PUBLIC_DEVICE_0043` |
| **IPv4 (`br0` / `br1`)** | `198.18.0.63` / `198.18.0.84` | `198.18.0.118` / `198.18.0.140` |
| **Operational State** | **`AP-PTMP(Run)`** | **`CPE-PTMP(Run)`** |
| **SSID** | `FMX-LTU` (`NONE`) | `FMX-LTU` (`NONE`) |
| **Channel / Bandwidth** | `5500 MHz` / `20 MHz` | `5500 MHz` / `20 MHz` |
| **TX Power / Gain** | `15,15 dBm` / `13 dBi` (`28 dBm` EIRP) | `15,15 dBm` / `13 dBi` (`28 dBm` EIRP) |
| **Stations Count** | **`1`** | **`1`** |
| **SpectrumEfficient** | **`1535`** | **`1319`** |
| **AutoLink** | **`1`** | **`1`** |
| **Signal (Chain 0 / 1)** | `-33 / -36 dBm` (offset `12`) | `-35 / -36 dBm` (offset `0`) |
| **Timing Advance (`TA`)** | `235` (`TA2 shift: 0`) | `235` |
| **OTA Data-Plane IPv4 (`ath0`)** | `198.18.0.61/24` | `198.18.0.72/24` |
| **OTA ICMP Ping RTT (`ath0`)** | `3.160 / 5.250 / 7.822 ms` (`0%` loss) | `3.160 / 5.250 / 7.822 ms` (`0%` loss) |
| **OTA `iperf3` TCP Goodput (`20 MHz`)** | **DL `61.4 Mbps` avg (`79.1 Mbps` peak)** | **UL `41.9 Mbps` avg (`42.4 Mbps` peak)** |
| **Flash Persistence** | `Active[1]` & `Backup[2]` (`100%`) | `Active[1]` & `Backup[2]` (`100%`) |

---

## 4. Operator Readiness for Remote Relocation

`LTU-Lite #2` (`Boca 7`) is now **100% flashed, verified, and associated over the air (`CPE-PTMP(Run)`)**. It can be unplugged from `Boca 7` (`gi7`) at any time and relocated to the remote PoE power source; upon boot it will automatically execute `/etc/persistent/rc.poststart`, load `SSID="FMX-LTU"` + `+15 dBm` + alternating `5500/5520` scan list, and re-associate over the air to `LTU-Lite #1` (`Boca 5`).
