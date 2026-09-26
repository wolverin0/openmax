# Read-only hardware inventory — airOS target units

Summary: exact commands to identify LAP-GPS, LiteBeam 5AC Gen2, NanoStation 5AC and Loco 5AC
without writing anything. Closes gap G04, the one gap no research can close.
Keywords: inventory, PCI ID, sysid, chip_id, ath10k firmware version, mtd map, ubnt_poll_host,
read-only, G04, LAP-GPS. Read when: you have physical or SSH access to a target radio.
Every command below is READ-ONLY. Nothing here writes flash, changes config, or reboots.
Status: CURRENT (2026-08-08). Run on spare/lab units first.

## Safety envelope

**Never** run `dd`, `mtd write`, `fwupdate`, `flashcp`, or anything touching `u-boot`,
`u-boot-env` or `EEPROM`. The `EEPROM` partition is Atheros radio calibration data — losing
it permanently degrades the radio and it is not recoverable from backup you do not have.

Everything below is `cat` / `dmesg` / `grep`. If a command is not in this file, it is not
authorised by this sheet.

## Connect

SSH must be enabled in airOS (Services → SSH Server). Default user `ubnt`.

```bash
ssh ubnt@<radio-ip>
```

## The one-shot collector

Paste this whole block. It prints a single labelled report you can copy back.

```sh
echo "===== FUTURAMAX INVENTORY $(date -u +%Y-%m-%dT%H:%M:%SZ) ====="

echo "--- 1. board identity (THE key line: sysid + board name) ---"
cat /proc/ubnthal/system.info 2>/dev/null
dmesg | grep -i "ubnthal.*board found"
dmesg | grep -i "Ubiquiti Networks.*board"

echo "--- 2. radio PCI identity (settles QCA988x vs QCA9888) ---"
dmesg | grep -iE "qca98|chip_id|TARGET TYPE|Radio:|PCIe WLAN"
cat /proc/bus/pci/devices 2>/dev/null | head
lspci -n 2>/dev/null

echo "--- 3. radio firmware version and load mode ---"
dmesg | grep -iE "ol_transfer_bin_file|firmware ver|FIRMWARE:|Download Firmware"

echo "--- 4. driver stack (expect ol_ath + ubnt_poll_host, NOT ath10k) ---"
dmesg | grep -iE "ath_pci:|ath_hal:|U-AME|ath10k"
lsmod

echo "--- 5. airMAX control module parameters (this is the proprietary boundary) ---"
dmesg | grep -i "ubnt_poll_host\|ubnt-poll-host"

echo "--- 6. SoC, clocks, memory ---"
cat /proc/cpuinfo
dmesg | grep -iE "SoC:|CPU revision|ath_sys_frequency|Clocks:|Determined physical RAM"
cat /proc/meminfo | head -3

echo "--- 7. flash map (record BEFORE anyone considers writing anything) ---"
cat /proc/mtd

echo "--- 8. airOS version ---"
cat /etc/version 2>/dev/null
cat /usr/lib/version 2>/dev/null

echo "--- 9. GPS presence (LAP-GPS only) ---"
dmesg | grep -i gps
ls -la /dev/gps* /dev/pps* 2>/dev/null
cat /proc/ubnthal/board.info 2>/dev/null | grep -i gps

echo "--- 10. spectral capability under stock airOS (gap G10) ---"
dmesg | grep -i "spectral\|SPECTRAL"

echo "===== END ====="
```

## What each block answers

| Block | Gap / conflict it closes |
|---|---|
| 1, 2 | **G04** — the silicon in each model. `sysid` + PCI subsystem ID are the machine-checkable identity; do not trust the label. |
| 2 | **C12** definitively per model — `qca988x` (Wave 1) vs `qca9888` (Wave 2) changes which firmware generation applies and therefore whether §2b of `QCA988X_CONTROL_BOUNDARY.md` binds. |
| 3 | Whether airOS radio firmware matches stock QCA 10.2.4 (**G08**). Record the byte length. |
| 4, 5 | **G05/G06** — confirms `ol_ath` + `ubnt_poll_host` on each model and captures the airMAX parameter set (polling, fixed-frame, `noack_mode`, station priority, ATPC). |
| 6 | **C11** per model — AR9342 @535 MHz vs anything else. |
| 7 | Protected-partition map before any experiment. Grade-A input to E0. |
| 9 | Whether GPS/PPS is exposed as a device node — bears directly on whether external GPS-disciplined timing is possible at all. |
| 10 | **G10** — if spectral is reachable under stock airOS, the top-ranked candidate becomes available **without giving up airMAX**. |

## Priority order

1. **LAP-GPS** — the AP, and the weakest row in the hardware matrix. Everything depends on it.
2. LiteBeam 5AC Gen2
3. Loco 5AC
4. NanoStation 5AC — already Grade A from published boot logs; use it to confirm the method
   reproduces before trusting results from the other three.

Run on **one spare unit per model**. Two units of the same model with different board
revisions can differ — record the full `sysid` string from block 1, not just the model name.

## After collecting

Save each unit's output verbatim to:

```
research/raw/hardware/<model>-<sysid>-<YYYY-MM-DD>.txt
```

Raw, unedited, one file per unit — same rule as the model reports. Then
`knowledge/HARDWARE_MATRIX.md` can be upgraded from Grade C to Grade A per row, and
`docs/CURRENT_STATE.md` critical-path item 4 closes.

## If SSH is unavailable

The airOS web UI exposes most of block 1/6/8 under **Main → Device** and the support-file
download (**System → Support Info**) contains `dmesg` and `/proc/mtd`. That support archive
is read-only to generate and is an acceptable substitute — save it verbatim to the same path.
