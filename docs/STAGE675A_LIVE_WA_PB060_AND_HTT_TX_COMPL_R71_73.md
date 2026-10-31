<!-- doc-head: STAGE675A_LIVE_WA_PB060_AND_HTT_TX_COMPL_R71_73.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 675A — Live `WA` `PB-060` TXOP/Retry Guard & `HTT` TX Completion Coalescing (`R71..R73` = `296` Cumulative Windows)

- **Status**: `CONFIRMED`
- **Attribution**: `QCA firmware` + `ath10k` + `mac80211` + `Linux` + `hardware`
- **Protocol**: Counterbalanced `A1 -> B1 -> A2 -> B2` (`12` new live windows; `296` cumulative `WA` windows)
- **Safety Boundaries**: `198.18.0.45` & `198.18.0.46` untouched (`touched_241_or_242 = false`); `0` flash writes (`RAM-only` `/tmp/firmware-2-pb060.bin`, `fw_checksums`: `92363606` / `12b29d01`).

## 1. Executive Summary (`R71..R73`)
In `Stage 675A` ([`run_stage675a_live_wa_pb060_and_htt_tx_compl_r71_73.py`](../tools/bench/run_stage675a_live_wa_pb060_and_htt_tx_compl_r71_73.py)), we staged `/tmp/firmware-2-pb060.bin` (`SHA-256: a49160ff008390a34e43145bc56f6b8d047f8e02433aff20f965b6f2874ef52f`) and the runtime helpers `/tmp/fmx_qca_htt_tx_compl_guard.sh` and `/tmp/fmx_qca_txbf_stbc_ldpc_guard.sh` on both `AP .20` and `CPE .250`, then executed rounds `R71..R73`:

| Round | Hypothesis Tested | Arm A Goodput / `p50` RTT | Arm B Goodput / `p50` RTT | Delta (`GP` / `p50` / `Pareto`) | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`S675A-R71`** | Target `PB-060` + `fmx_qca_htt_tx_compl_guard.sh` + `TSQ` (`262144` vs `131072`) | `68.982 Mbps` / `26.827 ms` | `67.883 Mbps` / **`16.550 ms`** | `-1.59%` GP / **`-38.31%` `p50`** / `-0.70%` Pareto | `RETAIN_ARM_A` (`TSQ=262144`) |
| **`S675A-R72`** | `net.core.netdev_budget` (`300` vs `600`) under 16-stream saturation | `70.879 Mbps` / `18.141 ms` | **`75.134 Mbps`** / **`16.831 ms`** | **`+6.00%` GP** / **`-7.22%` `p50`** / **`+2.92%` Pareto** | **`PROMOTE_ARM_B`** (`budget=600`) |
| **`S675A-R73`** | Near-Field `TxBF/STBC/LDPC` Guard (`rts=2346` vs `rts=off`) | **`72.001 Mbps`** / **`10.972 ms`** | `68.967 Mbps` / `21.334 ms` | `-4.21%` GP / `+94.44%` `p50` / `-0.17%` Pareto | `RETAIN_ARM_A` (`rts=2346`) |

## 2. Key Physical-Layer & Kernel Findings
1. **NAPI Poll Budget (`netdev_budget=600` in `S675A-R72`)**: Raising `net.core.netdev_budget` from `300` to `600` on `AR9342` (`535 MHz` MIPS74Kc) under 16-stream bidirectional saturation (`8 DL + 8 UL` + `IPTV` + `VoIP`) lifted mean goodput from `70.879 Mbps` to **`75.134 Mbps` (`+6.00%`, peak `75.398 Mbps` in `B2`)** while lowering `p50` RTT by **`-7.22%` (`16.831 ms`)** and reducing `VoIP` jitter from `2.487 ms` to **`1.930 ms`**.
2. **`TSQ` vs `HTT` TX Completion (`S675A-R71`)**: Tightening `tcp_limit_output_bytes` to `131072` (`128 KB`) cut `p50` RTT by **`-38.31%` (`16.550 ms` vs `26.827 ms`)** (`B2` hit `10.796 ms`), whereas `262144` (`256 KB`) preserved `+1.59%` higher bulk TCP goodput (`68.982 Mbps`).
3. **Near-Field `rts_threshold=2346` (`S675A-R73`)**: Keeping `rts_threshold=2346` (`Arm A`) achieved **`72.001 Mbps`** (`A1 = 74.235 Mbps`) and **`10.972 ms` `p50` RTT (`A1 = 9.297 ms`)**.

## 3. Artifacts & Verification
- **Receipt**: [`stage675a_live_wa_pb060_and_htt_tx_compl_r71_73.json`](../artifacts/autoresearch/stage675a_live_wa_pb060_and_htt_tx_compl_r71_73.json)
- **Pytest**: [`tests/test_stage675a.py`](../tests/test_stage675a.py)
