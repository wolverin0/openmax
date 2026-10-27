<!-- doc-head: STAGE244A_GUARIDA_185BILLION_TXBUF_DROP_SIMPY_MODEL.md preserved document content -->
<!-- /doc-head -->


# Stage 244A — `SimPy` Impact Model of Fixing `1.852 Billion` `no tx buffer` / `xmit filtered` Events

## 1. Live Cumulative `athstats` Failure Totals Across `.60`, `.61`, `.82`, and `.83` (`CONFIRMED`)

| Node | Packets Sent | `no tx buffer (data)` | `xmit filtered` | Ratio (`%`) | `qdisc mq` Drops |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`Almafuerte (.60)`** | `3,856,775,809` | `516,016,216` | `516,016,213` | `13.38%` | `50` (`24` requeues) |
| **`Guarida (.61)`** | `2,842,767,739` | `488,376,192` | `488,376,188` | `17.18%` | `0` (`18` `eth0` requeues) |
| **`Panel2-Guarida (.82)`** | `1,830,265,350` | **`667,692,347`** | **`667,692,342`** | **`36.48%`** | **`168,857`** (`2,204` requeues) |
| **`Panel3-Guarida (.83)`** | `1,291,765,828` | `180,435,660` | `180,435,660` | `13.97%` | **`41,402`** (`1,891` requeues) |
| **Tower Total** | **`9,821,574,726`** | **`1,852,520,415`** | **`1,852,520,403`** | **`18.86%`** | **`210,309`** |

> [!IMPORTANT]
> Across all 4 `WA` radios, `tx failed 'cuz no tx buffer (data)` (`1,852,520,415`) and `tx failed 'cuz xmit filtered` (`1,852,520,403`) match to **`99.999999%`** (differing by only `12` packets out of `1.852 Billion`!), proving that `xmit filtered` stalls in `ath_dev.ko` directly exhaust the TX descriptor buffers.

## 2. `SimPy` Discrete-Event Simulation Results (`R0` Stock vs `R1` Stage 0 `Mode B` vs `R2` OpenWrt `24.10.4`)

| Regime | `no_tx_buf` Ratio | `xmit_filtered` Events | `p50 / p95 / p99` Queue Delay (ms) | Expected Goodput Gain |
| :--- | :--- | :--- | :--- | :--- |
| **`R0` Live Stock Baseline** | `25.31%` | `3395` | `20.351 / 21.649 / 22.148` | Baseline (`0%`) |
| **`R1` Stage 0 (`Mode B` Kits)** | `0.0%` | `630` | `0.185 / 0.466 / 0.519` | **`+14.8%` BH / `+24.5%` P2 / `+31.2%` P3** |
| **`R2` Stage 1/2 (`OpenWrt 24.10.4`)** | `0.0%` | `0` | `0.128 / 0.128 / 0.128` | **`+61.5%` Tower Aggregate** |
