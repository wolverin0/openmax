<!-- doc-head: STAGE697A_PBE5AC_DYNAMIC_PHY_AND_SGMT_LOADER_V4.md preserved document content -->
<!-- /doc-head -->


# Stage 697A — Dynamic `phy*` Wiphy Index & RAM `SGMT` Bind-Mount Loader (`PtP Champion v4`)

- **Claim Status**: `CONFIRMED`
- **Attribution**: `external controller` + `QCA firmware` + `ath10k` + `mac80211`
- **Hardware**: `Ubiquiti PowerBeam 5AC Gen2` (`0xe3d6`) & `LiteBeam 5AC Gen2` (`0xe4d6 / 0xe7f9`)

## 1. Architecture & Engineering Purpose
When `ath10k_pci.ko` is unloaded and reloaded in RAM (`rmmod ath10k_pci && modprobe ath10k_pci`) to inject the 3-segment patched `QCA9882` Xtensa `SGMT` firmware (`/tmp/firmware-2-pb050.bin`, `athwlan = 12b29d01`), the Linux `mac80211` subsystem increments the wiphy index (`phy0 -> phy1 -> phy2`), renaming all virtual interfaces (`phy2-ap0`, `phy2-ap0.sta1`, `phy2-sta0`).
Additionally, stepping between `VHT40`/`VHT80` and `VHT20` requires a full `wifi down; sleep 2; wifi up` cycle to force a fresh `WMI_PEER_ASSOC_CMDID` with updated `peer_phymode`.

`Stage 697A` packages both protections into:
1. [fmx_pbe5ac_dynamic_phy_and_sgmt_loader.sh](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_dynamic_phy_and_sgmt_loader.sh):
   - Dynamically resolves `PHY_DIR=$(dirname $(ls -d /sys/kernel/debug/ieee80211/phy*/ath10k | head -n1))`.
   - `load-sgmt`: Bind-mounts `/tmp/fmx_xtensa_pb050` over `/lib/firmware/ath10k/QCA988X/hw2.0` (`0` flash writes) if `athwlan != 12b29d01`.
   - `switch-bw`: Enforces `wifi down; sleep 2; wifi up` on channel-width changes with `45s` Non-DFS / `120s` DFS watchdog bounds.
2. [99-fmx-wa-ptp-champion-v4](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-ptp-champion-v4):
   - Applies `0x00029e00 = 0x13761320` (`PB-040`), `pktlog_filter = 0x0`, `nf_cal_period = 120`, `fq_quantum = 300`, `aql_txq_limit = 1500/2000` (BE), `tcp_notsent_lowat = 131072`, `multicast_to_unicast = 1`, and asymmetric VHT LGI (`pream=3, sgi=0`).

## 2. Verification & Artifacts
- Builder Script: [build_stage697a_pbe5ac_dynamic_phy_and_sgmt_loader_v4.py](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/firmware/build_stage697a_pbe5ac_dynamic_phy_and_sgmt_loader_v4.py)
- JSON Artifact: [stage697a_pbe5ac_dynamic_phy_and_sgmt_loader_v4.json](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage697a_pbe5ac_dynamic_phy_and_sgmt_loader_v4.json)
- Pytest: [test_stage697a.py](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage697a.py)
