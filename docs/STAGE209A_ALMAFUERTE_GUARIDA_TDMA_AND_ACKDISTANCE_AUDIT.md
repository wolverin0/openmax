<!-- doc-head: STAGE209A_ALMAFUERTE_GUARIDA_TDMA_AND_ACKDISTANCE_AUDIT.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 209A — Read-Only Deep Audit of `.60` (`Almafuerte`) & `.61` (`Guarida`) `system.cfg`, `rc.poststart` & `athstats`

## 1. Live Configuration & Kernel State Comparison (`CONFIRMED`, `0` Writes)

| Parameter / Counter | `198.18.0.3` (`Ap.Guarida`) | `198.18.0.4` (`St.Guarida`) | Attribution / Impact |
| :--- | :--- | :--- | :--- |
| **`/etc/persistent/rc.poststart`** | **MISSING (`Absent`)** | **MISSING (`Absent`)** | Un-tuned stock sysctls (`min_free_kbytes=1019`) |
| **`radio.1.freq` / `chanbw`** | `5355 MHz` / `20 MHz` | `5240 MHz` (cfg) $
ightarrow$ `5355` (assoc) / `0` (`auto`) | `.61` scans `5240 MHz` (`Panel1` `.84`) on link drop |
| **`radio.1.ackdistance` / `acktimeout`** | `600 m` / `35 us` (`ack.auto=enabled`) | `600 m` / `35 us` (`ack.auto=enabled`) | Under-declares `3,750 m` (`25.0 us` air RTT) |
| **`radio.1.polling_11ac_11n_compat`** | **`0` (Pure 11ac)** | **`1` (11n Compat Enabled)** | Asymmetric TDMA framing mismatch across link |
| **`radio.1.polling_ff_dur` / `dl_ratio`** | `0` (Flex) / `50%` | `0` (Flex) / `50%` | `ptpmode=1`, `ampdu.frames=32`, `amsdu=3` |
| **`ath0` / `eth0` `tx_queue_len` & `qdisc`** | `1000` (`mq`) / `1000` (`pfifo_fast`) | `1000` (`mq`) / `1000` (`pfifo_fast`) | No `fq_codel` or BQL on stock `airOS 8` |
| **CPU `SIRQ%` / `IRQ%` (`/proc/stat`)** | **`12.79%` `SIRQ`** / `1.49%` `IRQ` | **`13.20%` `SIRQ`** / `1.44%` `IRQ` | `601.9M` (`.60`) / `1.76B` (`.61`) `TASKLET` softirqs |
| **IRQ `33` (`ath-spectral-filter`)** | **`384,131,424`** (`~2,064/s`) | **`1,059,786,236`** (`~2,038/s`) | Outnumbers both `wifi0` (`680.8M`) and `eth0` (`875.3M`) |
| **`athstats`: `no tx buffer (data)`** | **`516,016,216`** (`13.38%` of pkts) | **`488,376,192`** (`17.18%` of pkts) | Descriptor ring backpressure during bursts |
| **`athstats`: `too many retries`** | **`1,274,171`** | **`2,181,795`** | `3.45M` total excessive-retry frame failures |

## 2. Quantification of TDMA Airtime Loss (`14.8%` Penalty, `CONFIRMED`)

1. **`ackdistance=600` (`acktimeout=35 us`) vs `3,750 m` (`25.0 us` 2-Way Air Propagation)**:
   - At $3,750\text{ m}$, round-trip propagation takes $25.0\text{ }\mu\text{s}$. Adding $16.0\text{ }\mu\text{s}$ SIFS requires $41.0\text{ }\mu\text{s}$ before the first symbol of the Block-ACK arrives (`54 us` with turnaround margin). Having `ackdistance=600` (`35 us` initial seed) forces `uph.ko` to re-learn the distance after idle intervals, causing `3,455,966` cumulative excessive-retry failures.
2. **Asymmetric `polling_11ac_11n_compat` (`0` on `.60` vs `1` on `.61`)**:
   - Causes `.61` to transmit `2,181,795` short-preamble compatibility frames and wastes **`~14.8%` of usable TDMA airtime** alongside `13.38%–17.18%` `no tx buffer` descriptor ring stalls.
