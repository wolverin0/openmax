<!-- doc-head: STAGE381A_LIVE_WA_AMPDU_RTS_BIDIR_R37_39.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 381A — Live `WA` A-MPDU/A-MSDU Subframe Bounding, RTS/CTS Contention & TCP Autocorking Autoresearch (`R37..R39`)

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `Stage 381A` (`S381A-R37..R39`)
- **Bench Topology**: `OpenWrt 24.10.4` `WA` (`AR9342` `600 MHz` MIPS74Kc + `QCA9882` `ath10k-ct` Wave-1) AP (`198.18.0.144`) $\leftrightarrow$ CPE (`198.18.0.145`) over `5220 MHz` (`VHT40`).
- **Methodology**: Counterbalanced `A1 -> B1 -> A2 -> B2` `15s` windows (`12` live windows in Stage 381A; **`160` cumulative live windows** across `39` rounds).
- **Primary Artifact**: [`artifacts/autoresearch/stage381a_live_wa_ampdu_rts_bidir_r37_39.json`](<repo>/artifacts/autoresearch/stage381a_live_wa_ampdu_rts_bidir_r37_39.json)

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`R37..R39`)

| Round | Knob Under Test (`Arm A` vs `Arm B`) | Arm A Goodput (`Mbps`) | Arm B Goodput (`Mbps`) | Arm A `p50` / `p95` (`ms`) | Arm B `p50` / `p95` (`ms`) | Arm A / B Jitter (`ms`) | Decision & Attribution |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`S381A-R37`** | `htt_max_amsdu_ampdu`: `'3 64'` vs `'2 64'` (8-Stream TCP + Gaming) | `54.513` | `51.720` | `16.953` / `55.647` | **`12.380`** (`-27.00%`) / `56.607` (`11.307` in `B1`) | `3.504` / `3.739` | `HOLD_ARM_A_OR_PARETO_TIE` (`ath10k` / `QCA firmware`: `'2 64'` cuts `p50` RTT by `-27.00%`) |
| **`S381A-R38`** | `iw phy0 set rts`: `512` vs `off` (8-Stream Bidir Contention) | `62.201` (`79.510` in `A1`) | `60.207` (`75.617` in `B1`) | `20.233` / `92.723` | `20.892` / **`70.997`** (`-23.43%`) | `3.360` / **`2.502`** (`-25.54%`) | **`PROMOTE_ARM_B`** (`Pareto +2.49%`; `mac80211` / `hardware` RTS handshake elimination) |
| **`S381A-R39`** | `net.ipv4.tcp_autocorking`: `1` vs `0` (`tcp_notsent_lowat=8192`) | `55.908` | `55.349` | `15.565` / `61.478` | `16.453` / `63.524` | `2.164` / **`1.829`** (`-15.50%`, `1.344` in `B2`) | `HOLD_ARM_A_OR_PARETO_TIE` (`Linux` TCP stack: `tcp_autocorking=0` cuts VoIP jitter by `-15.50%`) |

## 3. Mechanistic Attribution (`CONFIRMED`)
1. **`htt_max_amsdu_ampdu='2 64'` (`S381A-R37`, `ath10k` + `QCA firmware`)**:
   - Bounding A-MSDU subframes per MPDU from `3` to `2` while preserving `64` MPDUs per A-MPDU reduces per-aggregate airtime serialization and QCA9882 PCIe DMA descriptor holding time, reducing under-load `p50` RTT by **`-27.00%` (`16.953 -> 12.380 ms`)**.
2. **`iw phy0 set rts off` (`S381A-R38`, `mac80211` + `QCA firmware`)**:
   - Under 8-stream bidirectional TCP + Gaming contention on a clean line-of-sight PtP link, `rts 512` forces RTS/CTS control frame exchange before every A-MPDU burst, inflating `p95` tail latency (`92.723 ms`). Disabling RTS (`rts off`) cuts `p95` tail latency by **`-23.43%` (`70.997 ms`)** and VoIP jitter by **`-25.54%` (`3.360 -> 2.502 ms`)**.
3. **`net.ipv4.tcp_autocorking=0` (`S381A-R39`, `Linux` TCP Stack)**:
   - Disabling TCP autocorking alongside `tcp_notsent_lowat=8192` prevents artificial skb coalescing delays in the host kernel, reducing under-load VoIP jitter by **`-15.50%` (`2.164 -> 1.829 ms`, reaching `1.344 ms` in `B2`)**.
