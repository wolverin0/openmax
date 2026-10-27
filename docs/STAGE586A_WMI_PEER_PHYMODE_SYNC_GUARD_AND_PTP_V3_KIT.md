<!-- doc-head: STAGE586A_WMI_PEER_PHYMODE_SYNC_GUARD_AND_PTP_V3_KIT.md preserved document content -->
<!-- /doc-head -->



# Stage 586A — `WMI_PEER_ASSOC_CMDID` Channel-Width Transition Guard (`fmx_wmi_peer_phymode_sync_guard.sh`) & `99-fmx-wa-ptp-champion-v3`

## 1. Root-Cause Remediation & Universal `WA` PtP Champion v3 Profile (`CONFIRMED`, attribution: `QCA firmware` + `mac80211` + `external controller`)
- Remediates the `OpenWrt 24.10.4` (`netifd`/`hostapd` + `ath10k-ct`) in-place `wifi reload` channel-width transition bug discovered in Stage 487A:
  - When `htmode` changes between `VHT80`, `VHT40`, and `VHT20`, `wifi reload` updates the PHY channel width in-place without tearing down the existing 802.11 peer association, leaving the `QCA9882` Xtensa target's `WMI_PEER_ASSOC_CMDID` `peer_phymode` out of sync with the PHY bandwidth.
  - [`fmx_wmi_peer_phymode_sync_guard.sh`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_wmi_peer_phymode_sync_guard.sh) enforces an explicit `wifi down; sleep 2; wifi up; sleep 12` lifecycle across `htmode` transitions and invokes [`99-fmx-wa-ptp-champion-v3`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-ptp-champion-v3) with the matching `bw_idx` (`0` for `VHT20`, `1` for `VHT40`, `2` for `VHT80`).
- Bakes into `99-fmx-wa-ptp-champion-v3` for `PowerBeam 5AC Gen2` (`0xe3d6`), `LiteBeam 5AC Gen2` (`0xe4d6` / `0xe7f9`), `NanoBeam 5AC Gen2` (`0xe3d8`), and `NanoStation 5AC` (`0xe7f8`):
  - `pktlog_filter=0x0`, `nf_cal_period=120`, `0x29e00=0x13761320`, `htt_max_amsdu_ampdu="3 64"`, `ani_enable=1`
  - `fq_quantum=300`, `aql_threshold=4000`, per-AC `aql_txq_limit` (`VO=500/1000`, `VI=1000/1500`, `BE=1500/2000`, `BK=1000/1500`)
  - `tx_queue_len=1000`, `eth0` BQL `limit_max=32768`, `tcp_notsent_lowat=131072`, `tcp_comp_sack_delay_ns=250000`, `tcp_early_retrans=4`
  - `multicast_to_unicast=1`, `multicast_snooping=1`
  - Bandwidth-aware asymmetric `VHT LGI` (`pream=3, sgi=0`) `set_rate_override` (`AP NSS2 MCS3 @ VHT20 / MCS2 @ VHT40+`, `STA NSS1 MCS2`).

---

## 2. Artifacts & Verification
- Builder & Deployer: [`build_stage586a_wmi_peer_phymode_sync_guard_and_ptp_v3_kit.py`](../tools/firmware/build_stage586a_wmi_peer_phymode_sync_guard_and_ptp_v3_kit.py)
- Helper Script: [`99-fmx-wa-ptp-champion-v3`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-ptp-champion-v3)
- Guard Script: [`fmx_wmi_peer_phymode_sync_guard.sh`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_wmi_peer_phymode_sync_guard.sh)
- Receipt: [`stage586a_wmi_peer_phymode_sync_guard_and_ptp_v3_kit.json`](../artifacts/autoresearch/stage586a_wmi_peer_phymode_sync_guard_and_ptp_v3_kit.json)
- Test: [`test_stage586a.py`](../tests/test_stage586a.py)
