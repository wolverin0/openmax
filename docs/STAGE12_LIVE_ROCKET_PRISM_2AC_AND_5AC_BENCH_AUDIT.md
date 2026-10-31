<!-- doc-head: STAGE12_LIVE_ROCKET_PRISM_2AC_AND_5AC_BENCH_AUDIT.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Live Rocket 2AC Prism (`0xe2f2`, Boca 8) & Rocket 5AC Prism Gen2 (`0xe7e9`, Boca 6) Dual-Radio & AirPrism Bench Audit

**Task ID**: `T-PB-GEM1-14`  
**Status**: `AUDIT_COMPLETE` (`automatic_execution_allowed = False`)  
**Implementation**: [`tools/bench/probe_live_rocket_prism_2ac_5ac.py`](../tools/bench/probe_live_rocket_prism_2ac_5ac.py)  
**Artifact Report**: [`artifacts/autoresearch/rocket_prism_2ac_5ac_live_bench_audit_20261024.json`](../artifacts/autoresearch/rocket_prism_2ac_5ac_live_bench_audit_20261024.json)

---

## 1. Dual-Radio & AirPrism Hardware Matrix

| Attribute | Rocket 2AC Prism (`Boca 8`) | Rocket Prism 5AC Gen2 (`Boca 6`) |
| :--- | :--- | :--- |
| **Management Endpoint** | `198.18.0.89` / `PUBLIC_DEVICE_0059` | `198.18.0.64` (`PUBLIC_DEVICE_0060`) |
| **Board SysID / Firmware** | `0xe2f2` / `2WA.ar934x.v8.7.25` | `0xe7e9` / `XC.qca955x.v8.7.25` |
| **Host SoC** | Atheros `AR9342` (`535 MHz` MIPS 74Kc) | Qualcomm Atheros `QCA9558` (`720 MHz` MIPS 74Kc) |
| **Main Data Radio (`wifi0`)** | `QCA988x` 2.4 GHz Downconverted 2x2 VHT20/40 | `QCA9880` hw2.0 5 GHz 2x2 VHT10/20/30/40/80 |
| **AirView Scanner (`wifi1`)** | Dedicated 2.4 GHz Spectral FFT Radio | Dedicated 5 GHz Spectral FFT Radio + `GPIO 21` (`IRQ 64`) Blanking |
| **AirPrism Preselector** | 2.4 GHz Active Tunable Bandpass (`+34.0 dB` rejection) | 2-Stage 5 GHz Preselector via `GPIO 13, 14, 15, 16` (`+35.5 dB` rejection) |

---

## 2. Verified `Rocket Prism 5AC Gen2` (`0xe7e9`) GPIO `13..16` Preselector Matrix

Using the 6-entry `ubnt_prism_filters` table (`umac.ko` `.data + 0x1510`) and [`compute_airprism_gpio_state()`](../controller/openwrt_airprism_and_step1c_generator.py):

- **`5180 MHz` (`40 MHz` BW)**: Stage 1 Low-Band (`GPIO 15=0, GPIO 16=1`), Stage 2 Bypass (`GPIO 13=0, GPIO 14=0`).
- **`5500 MHz` (`20 MHz` BW)**: Stage 1 High-Band Narrow (`GPIO 15=1, GPIO 16=0`), Stage 2 Bypass (`GPIO 13=0, GPIO 14=0`).
- **`5765 MHz` (`20 MHz` BW)**: Stage 1 High-Band Narrow (`GPIO 15=1, GPIO 16=0`), Stage 2 U-NII-3 Sub-Band (`GPIO 13=0, GPIO 14=1`).
- **Paired A/B/A/B Blocker Evaluation**: Under a `+25 MHz` adjacent-channel interferer, engaging the matched AirPrism preselector (`Arm B`) improves `20 MHz` goodput from **`44.15 Mbps` (`2.208 Mbps/MHz`) to `71.55 Mbps` (`3.578 Mbps/MHz`, `+62.06%`)** and reduces `p99` latency from **`38.83 ms` to `11.25 ms` (`-71.0%`)**, achieving `PROMOTE`.

---

## 3. Verification

```powershell
pytest tests/test_probe_live_rocket_prism_2ac_5ac.py -v
```
