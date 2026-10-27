<!-- doc-head: STAGE410A_SUB20MHZ_NLOS_PROFILE.md preserved document content -->
<!-- /doc-head -->


# Stage 410A — `PB-030` Sub-20 MHz (`5 MHz` Quarter-Rate / `10 MHz` Half-Rate) Channel Profile (`fmx_sub20mhz_nlos_profile.sh`)

- **Status**: `CONFIRMED`
- **Attribution**: `ath10k`, `QCA firmware`, `mac80211`, `hardware`
- **Deliverable**: [`firmware/openwrt/common/fmx_sub20mhz_nlos_profile.sh`](../firmware/openwrt/common/fmx_sub20mhz_nlos_profile.sh) (`sha256: 56a73b9d33c6aef2...`)

## 1. First-Principles Sub-20 MHz OFDM Numerology (`PB040-SUB20MHZ-PLL-DIV`) (`CONFIRMED`)
Under severe foliage/NLOS conditions, standard `20/40/80 MHz` OFDM fails due to (1) insufficient Power Spectral Density (`PSD`) above thermal noise (`kTB`) and (2) inter-symbol interference (`ISI`) when multipath reflections exceed the `400/800 ns` Guard Interval (`GI`):

| Channel Mode | PLL Clock Divider | PSD / Noise-Floor Gain (`dB`) | OFDM Symbol (`µs`) | Guard Interval (`GI`) | Max Delay Spread (`c · GI`) | Slot / SIFS (`µs`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`20 MHz` (Full Rate)** | `1x` | `0.00 dB` | `4.0 µs` | `800 ns` (`400 ns` SGI) | `240 m` | `9 µs` / `16 µs` |
| **`10 MHz` (Half Rate)** | `1/2x` | **`+3.01 dB`** | `8.0 µs` | **`1,600 ns`** | **`480 m`** | `13 µs` / `32 µs` |
| **`5 MHz` (Quarter Rate)** | `1/4x` | **`+6.02 dB`** | `16.0 µs` | **`3,200 ns`** | **`960 m`** | `21 µs` / `64 µs` |

## 2. Automated `slot_time` / `ack_timeout` / `distance` Scaling (`CONFIRMED`)
Because `ath10k`/`mac80211` computes `ack_timeout` in `20 MHz` clock ticks, `fmx_sub20mhz_nlos_profile.sh` automatically scales `EFF_DISTANCE_M` (`2x` for `10 MHz`, `4x` for `5 MHz`) and disables RTS/CTS (`iw phy set rts off`) so hardware ACK timers never expire prematurely during `8..16 µs` stretched symbols.
