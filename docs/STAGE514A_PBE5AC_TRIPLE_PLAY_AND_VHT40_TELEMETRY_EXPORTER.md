<!-- doc-head: Stage 514A Real-Time Telemetry Exporter for PBE-5AC-Gen2 / LBE-5AC-Gen2 PtP Links (VHT40 Unlock, Fraunhofer Regime & WMM Queue Drops) -->
Documents the real-time telemetry exporter (`build_stage514a_pbe5ac_triple_play_and_vht40_telemetry_exporter.py`) unifying Stage 487A's `VHT40` (`40 MHz`) STA capability unlock (`24.83 Mbps`, `0.0%` loss), Stage 481A's Fraunhofer near/far-field classifier, and Stage 488A's WMM `VO`/`VI`/`BE` Triple-Play telemetry.
<!-- /doc-head -->

# Stage 514A — `PBE-5AC-Gen2` / `LBE-5AC-Gen2` `VHT40` Capability Unlock & Triple-Play Telemetry Exporter

- **Epistemic Status**: `CONFIRMED` (`Stage 487A` `VHT40` `24.83 Mbps` live bench unlock + `Stage 488A` VoIP `0.0%` loss under load)
- **Attribution**: `QCA firmware` (`VHT` capability IE negotiation & `bw_idx=1` fixed-rate mask) · `mac80211` (`WMM` `AC_VO`/`AC_VI`/`AC_BE` queues)
- **Exporter Script**: [`build_stage514a_pbe5ac_triple_play_and_vht40_telemetry_exporter.py`](../tools/observability/build_stage514a_pbe5ac_triple_play_and_vht40_telemetry_exporter.py)
- **JSON Receipt**: [`stage514a_pbe5ac_triple_play_and_vht40_telemetry_exporter.json`](../artifacts/autoresearch/stage514a_pbe5ac_triple_play_and_vht40_telemetry_exporter.json)

---

## 1. Stage 487A `VHT40` (`40 MHz`) STA Capability Unlock Breakthrough

In Stage 427A, attempting `VHT40` (`40 MHz`) on `.241 <-> .242` failed association because the STA VHT capability configuration restricted channel-width negotiation. In **Stage 487A**, unlocking the STA `VHT80` capability advertisement (`sta_vht80_cap_unlock_verified: true`) enabled clean **`VHT40` (`40 MHz`, `bw_idx=1`) association** (`vht40_40mhz_associated: true`):

| Profile ID (`Stage 487A` Live Bench) | Mode / Width | AP DL / STA UL PHY | `64 B` Loss / `p50` | `1472 B` Loss / `p95` | DL / UL Goodput | Aggregate Goodput |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`vht20_ap_nss2_mcs3_sta_nss1_mcs2`** | `VHT20` (`20 MHz`) | `52.0 / 19.5 Mbps` | **`0.0%`** / `1.557 ms` | **`0.0%`** / `25.174 ms` | `15.23 / 7.23 Mbps` | `22.46 Mbps` |
| **`vht40_ap_nss2_mcs2_sta_nss1_mcs2` (Champion)** | **`VHT40` (`40 MHz`)** | **`81.0 / 40.5 Mbps`** | **`0.0%`** / `1.701 ms` | **`0.0%`** / **`24.602 ms`** | **`16.74 / 8.09 Mbps`** | **`24.83 Mbps` (`+10.55%`)** |
| **`vht40_ap_nss2_mcs3_sta_nss1_mcs2`** | `VHT40` (`40 MHz`) | `108.0 / 40.5 Mbps` | **`0.0%`** / `1.628 ms` | **`0.0%`** / `29.384 ms` | `10.81 / 9.96 Mbps` | `20.77 Mbps` |

---

## 2. Stage 488A WMM `AC_VO` (VoIP) Priority Protection Under Load

Under concurrent bulk load (`Stage 488A`), Stock (`Arm A`) suffered **`13.0%` VoIP (`64 B`) packet loss** with `p50 = 14.88 ms`, whereas Champion v2 (`Arm B`) reduced **VoIP packet loss to `0.0%` (`15/15` delivered)** and cut **`p50` latency by `-82.86%` (`14.88 ms -> 2.551 ms`)**. The exporter tracks `AC_VO`, `AC_VI`, and `AC_BE` queue drops alongside Fraunhofer distance (`< 6.20 m` near-field vs `>= 6.20 m` far-field) to dynamically pace `AC_VI` (`1316 B` IPTV) bursts so they never starve `AC_BE` or overflow `htt_max_amsdu_ampdu`.
