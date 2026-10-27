<!-- doc-head: STAGE430A_PBE5AC_LBE5AC_WA_PTP_CHAMPION_V2_KIT.md preserved document content -->
<!-- /doc-head -->



# Stage 430A — Universal `WA` `PtP Champion v2` Kit (`PowerBeam 5AC Gen2`, `LiteBeam 5AC Gen2`, `NanoBeam 5AC Gen2`, `NanoStation 5AC`)

## 1. Overview & Supported `WA` Hardware Matrix
Packages the live-validated `Stage 425A..429A` `PtP Champion v2` configuration into [`firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-ptp-champion-v2`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-ptp-champion-v2) and synchronizes `/etc/hotplug.d/net/99-fmx-wa-universal-champion` across `.241` (`AP`) and `.242` (`STA`).

| Model | Ubiquiti Board `sysid` | SoC + Radio | Role Support |
| :--- | :---: | :--- | :--- |
| **`PowerBeam 5AC Gen2` (`PBE-5AC-Gen2`)** | `0xe3d6` | `AR9342` (`535 MHz`) + `QCA9882` `2x2` | `AP` (`4addr` WDS) / `STA` (`4addr` WDS) |
| **`LiteBeam 5AC Gen2` (`LBE-5AC-Gen2`)** | `0xe7f9` | `AR9342` (`535 MHz`) + `QCA9882` `2x2` | `AP` (`4addr` WDS) / `STA` (`4addr` WDS) |
| **`NanoBeam 5AC Gen2` (`NBE-5AC-Gen2`)** | `0xe3d5` | `AR9342` (`535 MHz`) + `QCA9882` `2x2` | `AP` (`4addr` WDS) / `STA` (`4addr` WDS) |
| **`NanoStation 5AC` (`NS-5AC`)** | `0xe7f8` | `AR9342` (`535 MHz`) + `QCA9882` `2x2` | `AP` (`4addr` WDS) / `STA` (`4addr` WDS) |

---

## 2. Consolidated `PtP Champion v2` Knobs (`CONFIRMED`)
- **Queue & Airtime Discipline (`mac80211` / `Linux`)**:
  - `fq_quantum = 300` (`/sys/kernel/debug/ieee80211/phy0/aqm/fq_quantum`)
  - `aql_txq_limit_low = 4000`, `aql_txq_limit_high = 12000`
  - `htt_max_amsdu_ampdu = "3 64"` (`/sys/kernel/debug/ieee80211/phy0/ath10k/htt_max_amsdu_ampdu`)
  - `eth0` `byte_queue_limits/limit_max = 32768`, `rps_cpus = 1`
- **IEEE 802.11ac VHT Long-GI & Asymmetric Spatial Stream Control (`QCA firmware` / `ath10k`)**:
  - `wireless.radio0.short_gi_20 = 0`, `short_gi_40 = 0`, `short_gi_80 = 0`
  - `wireless.default_radio0.disassoc_low_ack = 0`
  - **AP (`phy0-ap0`)**: `tpc=255 sgi=0 mcs=3 nss=1 pream=3 retries=10 dynbw=0 bw=0 active=1` (`2x2 VHT-NSS 2 MCS 3 LGI = 52.0 Mbps`)
  - **STA (`phy0-sta0`)**: `tpc=255 sgi=0 mcs=2 nss=0 pream=3 retries=10 dynbw=0 bw=0 active=1` (`1x1 VHT-NSS 1 MCS 2 LGI = 19.5 Mbps`)

---

## 3. Artifacts & Verification
- Builder & Live Sync Script: [`build_stage430a_pbe5ac_lbe5ac_wa_ptp_champion_v2_kit.py`](../tools/firmware/build_stage430a_pbe5ac_lbe5ac_wa_ptp_champion_v2_kit.py)
- Hotplug Script: [`99-fmx-wa-ptp-champion-v2`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-ptp-champion-v2)
- JSON Artifact: [`stage430a_pbe5ac_lbe5ac_wa_ptp_champion_v2_kit.json`](../artifacts/autoresearch/stage430a_pbe5ac_lbe5ac_wa_ptp_champion_v2_kit.json)
- Suite Test: [`test_stage430a_suite.py`](../tests/test_stage430a_suite.py)
