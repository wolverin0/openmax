<!-- doc-head: STAGE27_R2AC_PRISM_AND_NANOLOCO_M2_24GHZ_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 27 — Physical 2.4 GHz `NanoStation Loco M2` (`gi2`) ↔ `Rocket 2AC Prism` (`gi8`) Discovery & Incremental Champion Benchmark (`T-S27-NANOLOCO-M2-AND-R2AC-PRISM-24GHZ-LINK-AND-CHAMPION-BENCH`)

- **Experiment ID**: `STAGE27-R2AC-PRISM-AND-NANOLOCO-M2-24GHZ-BENCH-20261025`
- **Date (UTC)**: `2026-10-25T16:45:04Z`
- **Status**: `CONFIRMED` on physical 2.4 GHz bench (`EdgeSwitch 10XP` `gi2` ↔ `gi8`)
- **Primary Receipt**: [`artifacts/autoresearch/stage27_r2ac_prism_and_nanom2_24ghz_20261025.json`](../artifacts/autoresearch/stage27_r2ac_prism_and_nanom2_24ghz_20261025.json)
- **Benchmark Runner**: [`tools/bench/run_stage27_r2ac_prism_and_nanom2_24ghz_bench.py`](../tools/bench/run_stage27_r2ac_prism_and_nanom2_24ghz_bench.py)

---

## 1. Physical Discovery & Cross-Port Qualification (`Boca 2 / gi2` ↔ `Boca 8 / gi8`)

| Parameter | `NanoStation Loco M2` (`Boca 2 / gi2`) | `Rocket 2AC Prism` (`Boca 8 / gi8`) |
| :--- | :--- | :--- |
| **Model / Board** | Ubiquiti `NanoStation Loco M2` (`LocoM2`) | Ubiquiti `Rocket 2AC Prism` (`R2AC`, `sysid=0xe7f5`) |
| **Firmware** | `XM.ar7240.v6.1.12.33003.171208.1656` | `2XC.qca955x.v8.7.11` (`Linux 2.6.32.68`) |
| **MAC Addresses** | `eth0`: `PUBLIC_DEVICE_0044` · `ath0`: `PUBLIC_DEVICE_0077` | `eth0/br0`: `PUBLIC_DEVICE_0042` |
| **IPv4 Addresses** | LAN: `198.18.0.50` · WLAN: `198.18.0.133` | Primary: `198.18.0.65` · Alias (RAM): `198.18.0.75/24` |
| **2.4 GHz Channel & Mode** | `2444 MHz` (Channel 37, `20 MHz` Master AP, ESSID `"Guardar-EXT"`) | `2412 MHz` (Channel 1, `20 MHz`, `AirPrism` Active Filter `IRQ 64`) |
| **Observed OTA Signal on `R2AC`** | **`-59 dBm`** (`Noise = -87 dBm`, `SNR = 28 dB`, `Quality = 37/94`) | Active `AirPrism` blanking (`IRQ 64`: `22..28/s`) |
| **Cross-Port L2/L3 Ping (`gi8 -> gi2`)** | **`0.310 – 0.453 ms`** (`0.0%` packet loss across all 8 sub-phases) | Open TCP ports on `.1.20`: `22` (`SSH-2.0-dropbear`), `80`, `443` |

---

## 2. Incremental Champion-as-Baseline Results (`A1 -> B1 -> A2 -> B2`)

Starting strictly from `A = GOLDEN_PROFILES["r2ac_prism_ap"]` (`Champion A`, NOT Stock):

| Round ID | Baseline (`A`) | Candidate (`B`) | Goodput `A -> B` (`Δ%`) | `p50` RTT `A -> B` | `p95` RTT `A -> B` (`Δ%`) | Cross-Port `gi2` Ping | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S27-R2AC-R1`** | `r2ac_prism_ap` Champion (`airview1 up`, `cms_bias=0`) | `r2ac_prism_ap` + `airview1 down` + `cms_bias=6` + `voip_bias=6` + `sta_rx_rssi_th=-82` | `27.062 -> 28.470 Mbps` (**`+5.20%`**) | `2.058 -> 1.817 ms` (**`-11.71%`**) | `23.680 -> 15.165 ms` (**`-35.96%`**) | `0.331 – 0.453 ms` (`0%` loss) | **`PROMOTE_NEW_CHAMPION`** (`+17.79%` Pareto) |
| **`S27-R2AC-R2`** | `S27-R2AC-R1` Winner (`br0 txqueuelen=1000`, `tcp_dsack=0`) | `S27-R2AC-R1` Winner + `br0 txqueuelen=256` + `tcp_sack=1` + `tcp_dsack=1` + `tcp_window_scaling=1` + `tcp_fin_timeout=15` | `27.026 -> 27.430 Mbps` (**`+1.50%`**) | `2.351 -> 1.697 ms` (**`-27.82%`**) | `19.488 -> 16.012 ms` (**`-17.84%`**) | `0.310 – 0.344 ms` (`0%` loss) | **`PROMOTE_NEW_CHAMPION`** (`+7.74%` Pareto) |

### Key Causal Mechanisms Proven
1. **Adjacent-Channel `uph_wifi0` Bias & `airview1` Quiescing (`S27-R2AC-R1`)**: With `NanoStation Loco M2` transmitting right next to the `Rocket 2AC Prism` on `2444 MHz` at `-58..-59 dBm`, setting `uph_wifi0/cms_bias=6`, `voip_bias=6`, and `sta_rx_rssi_th=-82` alongside `ifconfig airview1 down` reduced `p95` tail latency by **`-35.96%` (`23.680 -> 15.165 ms`)**, reduced `p50` RTT to **`1.817 ms`** (`1.424 ms` in `B2`), and increased stream goodput by **`+5.20%` (`27.062 -> 28.470 Mbps`, reaching `29.654 Mbps` in `B1`)**.
2. **Bridge Queue Bounding & SACK/DSACK (`S27-R2AC-R2`)**: Bounding `br0 txqueuelen=256` (matching `ath0` and `eth0`) and enabling `tcp_sack=1`, `tcp_dsack=1`, `tcp_window_scaling=1`, and `tcp_fin_timeout=15` on top of the `S27-R2AC-R1` winner cut `p95` RTT by an additional **`-17.84%` (`19.488 -> 16.012 ms`)** and reduced `p50` RTT by **`-27.82%` (`2.351 -> 1.697 ms`)** while adding **`+1.50%` goodput**.
3. **Promoted to Golden Profile Ledger**: Both `S27-R2AC-R1` and `S27-R2AC-R2` are promoted into `GOLDEN_PROFILES["r2ac_prism_ap"]` in [`controller/multiradio_golden_profile_applicator.py`](../controller/multiradio_golden_profile_applicator.py) and left active in RAM on `198.18.0.65` (`persistent_flash_writes: false`).
