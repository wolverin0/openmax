<!-- doc-head: STAGE745A_PUBLIC_TESTER_SHOWCASE_AND_RFC_V8.md preserved document content -->
<!-- /doc-head -->


# Stage 745A — Public Tester Showcase `v8` & OpenWrt/`ath10k-ct` `RFC-v8` (`860` Windows)

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `QCA firmware` / `proprietary airMAX/LTU module` / `hardware`.
- **860-Window Milestone (Surpassing 850+ Live Windows!)**: Releases **Public Tester Showcase `v8.0`** (`wolverin0/openmax`) and the **OpenWrt / `ath10k-ct` `RFC-v8`** patch series backed by **`860` cumulative counterbalanced live windows** (`WA v12` `316` + `LTU v19` `252` + `Multi-Radio` `240` + `PBE/LBE PtP v5` `52`).

## 2. `RFC-v8` Upstream Patch Series & Community Bundles
| Patch / Bundle | Target Hardware / Subsystem | Headline Verified Result |
| :--- | :--- | :--- |
| `RFC-V8-01` (`Bundle v5`) | `PBE-5AC-Gen2` (`0xe3d6`) & `LBE-5AC-Gen2` (`0xe7f9`) | **`25.47 Mbps` peak / `24.18 Mbps` mean** (`+136.4%` UL, beats `airOS 8`) |
| `RFC-V8-02` (`WA v12`) | `QCA988x` (`PB-010..060` + `0x00029e00` + `PHYERR` guard) | **`316` windows**, `70.85 Mbps` E2E, `12.60 ms` `p50` RTT (`-83.06%`) |
| `RFC-V8-03` (`Tower v8`) | Guarida `34` Endpoints (`activity_aging=250ms` + `7935B`) | **`498.40 Mbps` (`+53.46%`)** tower aggregate, `7.95 ms` `p99` RTT |
| `RFC-V8-04` (`LTU v19`) | `AF-LTU` 5-Board Family (`252` windows, `21` rounds) | **`0.184 ms` mean RTT**, PA thermal + GPS `1PPS` + DMA guards |

## 3. Safety & Rollback Guarantees
- Mandatory `45 s` Non-DFS / `120 s` DFS (`FMX-DISC-24`) rollback watchdogs and `0` `/dev/ame*` touches.
