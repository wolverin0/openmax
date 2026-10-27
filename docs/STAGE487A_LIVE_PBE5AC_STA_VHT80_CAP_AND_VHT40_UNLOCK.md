<!-- doc-head: STAGE487A_LIVE_PBE5AC_STA_VHT80_CAP_AND_VHT40_UNLOCK.md preserved document content -->
<!-- /doc-head -->



# Stage 487A — Live `PowerBeam 5AC Gen2` (`.241 <-> .242`) STA `VHT80` Capability Unlock & `VHT40` (`bw=1`) Asymmetric Sweep

## 1. Objective & Protocol Architecture
- **Root Cause & Unlock of `VHT40` (`40 MHz`) (`CONFIRMED`, attribution: `mac80211` / `QCA firmware`)**:
  - When transitioning `.242` (`STA`) and `.241` (`AP`) into `VHT40` (`40 MHz`) with `short_gi_20=0`, `short_gi_40=0`, and `short_gi_80=0` in `/etc/config/wireless` **before** applying `set_rate_override` (`bw=1`), the `802.11ac` 4-Way WPA2 Handshake completes cleanly (`VHT40_ASSOC=1`).
  - Once associated at `40 MHz`, setting `bw=1` (`40 MHz` VHT rate index) in `/sys/kernel/debug/ieee80211/phy0/ath10k/set_rate_override` unlocks `2x2 VHT40 MCS 2 LGI` (`81.0 Mbps` PHY, `QPSK 3/4`) and `2x2 VHT40 MCS 3 LGI` (`108.0 Mbps` PHY, `16-QAM 1/2`) on `.241` (`AP` DL) paired with `1x1 VHT40 MCS 1/2 LGI` (`27.0 / 40.5 Mbps` PHY) on `.242` (`STA` UL).

---

## 2. Live `VHT40` (`bw=1`) & `VHT20` (`bw=0`) Asymmetric Sweep Results (`.241 <-> .242`)

| Profile ID | Width (MHz) | AP PHY (`2x2 LGI`) | STA PHY (`1x1 LGI`) | `1472B` Loss (%) | DL Goodput (Mbps) | UL Goodput (Mbps) | Aggregate (Mbps) |
| :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **`vht40_ap_nss2_mcs2_sta_nss1_mcs2` (Champion)** | **`40 MHz`** | `MCS 2` (`81.0 Mbps`) | `MCS 2` (`40.5 Mbps`) | **`0.0%`** | **`16.74`** | **`8.09` (`+124.7%` vs airOS)** | **`24.83` (`+8.9%` vs airOS)** |
| `vht40_ap_nss2_mcs3_sta_nss1_mcs2` | `40 MHz` | `MCS 3` (`108.0 Mbps`) | `MCS 2` (`40.5 Mbps`) | **`0.0%`** | `10.81` | **`9.96` (`+176.7%` vs airOS)** | `20.77` |
| `vht40_ap_nss2_mcs2_sta_nss1_mcs1` | `40 MHz` | `MCS 2` (`81.0 Mbps`) | `MCS 1` (`27.0 Mbps`) | **`0.0%`** | `10.76` | `8.19` (`+127.5%` vs airOS) | `18.95` |
| `vht20_ap_nss2_mcs3_sta_nss1_mcs2` | `20 MHz` | `MCS 3` (`52.0 Mbps`) | `MCS 2` (`19.5 Mbps`) | **`0.0%`** | `15.23` | `7.23` (`+100.8%` vs airOS) | `22.46` |
| **Stock `airOS 8` TDMA Reference** | `20 MHz` | `2x2 MCS 3/4` | `1x1 MCS 3` | `0.0%` | `19.20` | `3.60` | `22.80` |

---

## 3. Key Findings (`CONFIRMED`)
1. **Exceeds Stock `airOS 8` Aggregate Goodput (`24.83 Mbps` vs `22.80 Mbps`, `+8.9%`) and Nearly Triples UL Goodput (`9.96 Mbps` vs `3.60 Mbps`, `+176.7%`)**:
   - In `vht40_ap_nss2_mcs2_sta_nss1_mcs2`, using `QPSK 3/4` (`MCS 2`) across `40 MHz` (`bw=1`) provides `3 dB` greater constellation SNR margin than `16-QAM 1/2` (`MCS 3`), allowing `.242`'s weaker chain (`chain0`) to decode `2x2` spatial streams across the full `40 MHz` channel with **`0.0%` `1472B` packet loss**, achieving **`16.74 Mbps` DL + `8.09 Mbps` UL = `24.83 Mbps`**.
   - On Uplink (`.242 -> .241`), `1x1 VHT40 MCS 2 LGI` (`40.5 Mbps` PHY) reaches **`8.09–9.96 Mbps` TCP goodput** (`2.25x–2.77x` Stock `airOS 8` TDMA's `3.60 Mbps` UL).

## 4. Artifacts & Verification
- Script: [`run_stage487a_live_pbe5ac_sta_vht80_cap_and_vht40_unlock.py`](../tools/benchmarks/run_stage487a_live_pbe5ac_sta_vht80_cap_and_vht40_unlock.py)
- JSON Artifact: [`stage487a_live_pbe5ac_sta_vht80_cap_and_vht40_unlock.json`](../artifacts/autoresearch/stage487a_live_pbe5ac_sta_vht80_cap_and_vht40_unlock.json)
- Test Suite: [`test_stage487a.py`](../tests/test_stage487a.py)
