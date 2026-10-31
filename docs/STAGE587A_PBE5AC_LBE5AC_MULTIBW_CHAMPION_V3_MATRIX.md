<!-- doc-head: STAGE587A_PBE5AC_LBE5AC_MULTIBW_CHAMPION_V3_MATRIX.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 587A — Multi-Bandwidth (`VHT20` vs `VHT40` vs `VHT80` vs Stock `airOS 8` TDMA) Complete Live `PtP Champion v3` Comparison Matrix

## 1. Consolidated Multi-Bandwidth Live Hardware Matrix (`CONFIRMED`, attribution: `QCA firmware` + `ath10k` + `mac80211` + `Linux` + `hardware`)
- Consolidates all live measurements across `Stage 105A`, `Stages 425A..430A`, `Stages 487A..492A`, and `Stages 583A..586A` on the `PowerBeam 5AC Gen2` (`0xe3d6`, `198.18.0.45` Local AP on `Boca 3` $\leftrightarrow$ `198.18.0.46` Remote OTA STA on `MK1-251` `Boca 7`) and `LiteBeam 5AC Gen2` (`0xe4d6` / `0xe7f9`) sibling architecture:
  1. **Stock `airOS 8` TDMA (`WA.v8.7.25/11`, `20 MHz`)**: `19.20 Mbps` DL + `3.60 Mbps` UL = `22.80 Mbps` aggregate, `p50 = 1.96 ms`, `p95 = 7.56 ms`, `p99 = 10.68 ms`, `0.0%` `1472B` loss.
  2. **OpenWrt `24.10.4` Stock (`Arm A` Default, `20 MHz`)**: `9.67 Mbps` DL + `0.97 Mbps` UL = `10.64 Mbps` aggregate, `30.0%` `1472B` loss, `40.0%` IPTV `1316B` loss under Triple-Play load.
  3. **OpenWrt `FuturaMAX PtP Champion v2` (`VHT20`, `20 MHz`)**: **`15.04 Mbps` DL + `5.54 Mbps` UL = `20.58 Mbps` mean (`22.46 Mbps` peak in `B1` with `7.23 Mbps` UL = `+100.8%` vs airOS 8)**, `p50 = 1.589 ms` (`-18.9%`), `p95 = 2.676 ms` (`-64.6%`), `0.0%` `1472B` loss, and `0.0%` IPTV `1316B` loss under Triple-Play load (`+218.4%` concurrent bulk TCP).
  4. **OpenWrt `FuturaMAX PtP Champion v3` (`VHT40`, `40 MHz`, `bw=1`, `pktlog_filter=0x0` + `tcp_notsent_lowat=131072` + `PB-040`/`PB-050`)**: **`15.71 Mbps` DL + `8.47 Mbps` UL = `24.18 Mbps` mean (`25.47 Mbps` peak in `B1`: `16.96 Mbps` DL + `8.51 Mbps` UL, `0.0%` `1472B` loss)** — exceeding Stock `airOS 8` TDMA in both aggregate goodput (`+11.7%` peak / `+6.1%` mean) and uplink capacity (`+136.4%` peak / `+135.3%` mean).
  5. **OpenWrt `Stage 584A VHT80` (`80 MHz`, `bw=2`) & `Stage 585A` 3-Segment `SGMT` (`PB-040` + `PB-050`) Silicon Proof**: Verified `VHT80` (`80 MHz`) association (`12.27 Mbps`, `0.0%` `1472B` loss) and verified `athwlan=12b29d01` + physical baseband register `0x00029e00 = 0x13761320` on both `.241` and `.242` with `0` flash writes and `0.0%` `1472B` loss (`min = 6.244 ms`).

---

## 2. Artifacts & Verification
- Script: [`build_stage587a_pbe5ac_lbe5ac_multibw_champion_v3_matrix.py`](../tools/benchmarks/build_stage587a_pbe5ac_lbe5ac_multibw_champion_v3_matrix.py)
- Receipt: [`stage587a_pbe5ac_lbe5ac_multibw_champion_v3_matrix.json`](../artifacts/autoresearch/stage587a_pbe5ac_lbe5ac_multibw_champion_v3_matrix.json)
- Test: [`test_stage587a.py`](../tests/test_stage587a.py)
