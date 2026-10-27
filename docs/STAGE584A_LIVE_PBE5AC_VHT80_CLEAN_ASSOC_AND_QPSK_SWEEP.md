<!-- doc-head: STAGE584A_LIVE_PBE5AC_VHT80_CLEAN_ASSOC_AND_QPSK_SWEEP.md preserved document content -->
<!-- /doc-head -->



# Stage 584A — Live `PowerBeam 5AC Gen2` (`.241 <-> .242`) `VHT80` (`80 MHz`, `bw=2`) Clean `wifi down/up` Association & Asymmetric `QPSK` Sweep

## 1. Objective & Physical/Firmware Mechanism (`CONFIRMED`, attribution: `QCA firmware` + `mac80211` + `hardware`)
- With `.242` (`FMX-PBE5AC-STA-242`) unlocked to `htmode='VHT80'` capability and clean `wifi down; sleep 2; wifi up` avoiding `WMI_PEER_ASSOC_CMDID` `peer_phymode` desynchronization, Stage 584A evaluates `VHT80` (`80 MHz`, `Channel 40 / 5200 MHz`, `center1: 5210 MHz`, `bw=2`) live on `.241 <-> .242` with a 45-second autonomous rollback watchdog.
- Sweeps `bw=2` (`80 MHz`) asymmetric `QPSK` (`VHT-MCS 1` `1/2` and `VHT-MCS 2` `3/4`, `pream=3`, `sgi=0`, `pktlog_filter=0x0`) across:
  1. `vht80_ap_nss1_mcs1_sta_nss1_mcs1` (`AP 58.5 Mbps / STA 58.5 Mbps` `1x1`): `0.0%` `1472B` loss
  2. `vht80_ap_nss2_mcs1_sta_nss1_mcs1` (`AP 117.0 Mbps 2x2 / STA 58.5 Mbps 1x1`): **`DL = 7.11 Mbps` + `UL = 3.59 Mbps` = `10.70 Mbps` (`0.0%` `1472B` loss)**
  3. `vht80_ap_nss2_mcs2_sta_nss1_mcs2` (`AP 175.5 Mbps 2x2 / STA 87.8 Mbps 1x1`): **`DL = 6.50 Mbps` + `UL = 5.77 Mbps` = `12.27 Mbps` (`0.0%` `1472B` loss)**
- Cleanly restores `.241 <-> .242` to `VHT20` via `wifi down; sleep 2; wifi up` and verifies `0.0%` `1472B` full-MTU packet loss (`p50 = 2.215..3.636 ms`) post-restore.

---

## 2. Artifacts & Verification
- Script: [`run_stage584a_live_pbe5ac_vht80_clean_assoc_and_qpsk_sweep.py`](../tools/benchmarks/run_stage584a_live_pbe5ac_vht80_clean_assoc_and_qpsk_sweep.py)
- Receipt: [`stage584a_live_pbe5ac_vht80_clean_assoc_and_qpsk_sweep.json`](../artifacts/autoresearch/stage584a_live_pbe5ac_vht80_clean_assoc_and_qpsk_sweep.json)
- Test: [`test_stage584a.py`](../tests/test_stage584a.py)
