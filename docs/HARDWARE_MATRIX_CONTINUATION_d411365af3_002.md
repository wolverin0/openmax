<!-- doc-head: HARDWARE_MATRIX.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](HARDWARE_MATRIX.md) | Part 2/2
<a id="october22-evidence-alignment---current-bench-scope"></a> [October22 evidence alignment - current bench scope](HARDWARE_MATRIX_CONTINUATION_d411365af3_001.md#october22-evidence-alignment---current-bench-scope) | <a id="futuramax-hardware-matrix"></a> [FuturaMAX hardware matrix](HARDWARE_MATRIX_CONTINUATION_d411365af3_001.md#futuramax-hardware-matrix) | <a id="evidence-grades-used-here"></a> [Evidence grades used here](HARDWARE_MATRIX_CONTINUATION_d411365af3_001.md#evidence-grades-used-here) | <a id="matrix--all-six-models-measured-on-live-hardware-2026-08-08-grade-a"></a> [Matrix — all six models measured on live hardware 2026-08-08 (Grade A)](HARDWARE_MATRIX_CONTINUATION_d411365af3_001.md#matrix--all-six-models-measured-on-live-hardware-2026-08-08-grade-a) | <a id="grade-a-detail-nanostation-ac-s1--2017-era-boot-logs"></a> [Grade-A detail: NanoStation AC (S1) — 2017-era boot logs](HARDWARE_MATRIX_CONTINUATION_d411365af3_001.md#grade-a-detail-nanostation-ac-s1--2017-era-boot-logs) | <a id="board-identity"></a> [Board identity](HARDWARE_MATRIX_CONTINUATION_d411365af3_001.md#board-identity) | <a id="radio-as-seen-by-openwrtath10k-grade-a"></a> [Radio, as seen by OpenWrt/ath10k (Grade A)](HARDWARE_MATRIX_CONTINUATION_d411365af3_001.md#radio-as-seen-by-openwrtath10k-grade-a) | <a id="flash-layout-and-protected-partitions-grade-a"></a> [Flash layout and protected partitions (Grade A)](HARDWARE_MATRIX_CONTINUATION_d411365af3_001.md#flash-layout-and-protected-partitions-grade-a) | <a id="what-stock-airos-actually-runs-grade-a--the-most-valuable-discovery"></a> [What stock airOS actually runs (Grade A) — the most valuable discovery](HARDWARE_MATRIX_CONTINUATION_d411365af3_001.md#what-stock-airos-actually-runs-grade-a--the-most-valuable-discovery)

<!-- stage822a-payload-begin -->
(`noack_mode`), airMAX Priority (`Station priority ... no-auto`), and ATPC.

Consequences that change the research plan:

- The proprietary boundary is a **host kernel module**, not (only) opaque radio firmware.
  `ubnt_poll_host` and `ubnthal` are the artifacts to characterise in W02 — and they are
  far better search handles than "airMAX TDMA".
- **airOS and OpenWrt do not share a driver.** Every airOS-vs-OpenWrt comparison is
  `ol_ath 10.1.467 + ubnt_poll_host` versus `ath10k + mac80211`, changing two layers at
  once. Any A/B experiment must say so; "same hardware" is not "same stack".
- Radio firmware is loaded in **`Mode: PTP`** with a 215408-byte image, distinct from the
  ath10k `firmware-6.bin` path. Whether the airOS radio firmware differs from stock
  QCA 10.2.4 is now a concrete, answerable question.
- `Ubiquiti U-AME chipset detected` — **SUPERSEDED by the 2026-08-08 live sweep.** It was
  the only lead toward the disputed "airMAX ASIC" claim (C15); the sweep found it on all six
  units including plain CPEs, so it is a fleet-wide identifier, not a premium-hardware
  accelerator marker. See `knowledge/AIRMAX_ARCHITECTURE.md` section 3.
- airOS carries its own spectral module (`ath_spectral 2.0.0`, `HAL_CAP_SPECTRAL_SCAN:
  Capable`) but logs `SPECTRAL: No ADVANCED SPECTRAL SUPPORT`. Spectrum telemetry may be
  reachable **without leaving airOS** — which would fit the airOS-first architecture
  decision far better than flashing OpenWrt.

## What this table corrected

| Was claimed | By | Reality (Grade A) |
|---|---|---|
| NanoStation AC uses **QCA9888** (Wave 2) | glm source ledger | **QCA988X** Wave 1 |
| Target SoC is **QCA9563 @ 750 MHz** | google | **AR9342 @ 535 MHz** |
| QCA988x is 802.11ac **Wave 2** | mistral | Wave 1 |
| OpenWrt "can't boot on Ubiquiti AC gear, u-boot unavailable" | glm blocker #4 | Refuted — full OpenWrt boot log on this device |

## Open hardware questions after the sweep

Closed by the 2026-08-08 collection: LAP-GPS identity, per-model radio generation, GPS
presence, flash layout, and the QCA9888-vs-QCA988x question.

Still open:

1. **Extract and compare the per-mode radio firmware images** (PTP ~214 KB, PTMP-AP ~250 KB,
   PTMP-STA ~233 KB) against stock QCA 10.2.4. Highest-value remaining W02 item — see
   `AIRMAX_ARCHITECTURE.md` section 1. (gap G08, promoted)
2. **`DAPROT`** — an `ubnt_poll_host` parameter present on all six units, absent from the
   2017 boot log, and unmentioned by any research run. Meaning UNKNOWN.
3. **Non-standard channel widths.** `radio.1.chanbw=10,20,30,40,50,60,80` exposes 30/50/60 MHz.
   Can ath10k/OpenWrt reach them, and can airOS be driven to them per-link?
4. **FCC ID `SWX-LAPGPS`** — internal photos would independently settle whether any
   accelerator silicon exists, without relying on marketing pages.
5. Whether `raw-mode` (advertised by stock ath10k firmware on this chip) is usable.
6. Board revision variation *within* a model — one unit per model was sampled, not one per
   revision.

## Standing safety rule

Never write `u-boot`, `u-boot-env` or `EEPROM`. Never modify calibration/ART or board data.
Lab units only, recovery proven first. This is not advice — it is the project constraint
recorded in MemoryMaster and it is now backed by the exact partition map above.
<!-- stage822a-payload-end -->
