<!-- doc-head: STAGE676A_LIVE_WA_77ROUND_312WINDOW_MILESTONE_R74_77.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 676A — Live `WA` `77`-Round (`312`-Window) Milestone & `WA Champion v12` Promotion (`R74..R77`)

- **Status**: `CONFIRMED`
- **Attribution**: `QCA firmware` + `ath10k` + `mac80211` + `Linux` + `hardware`
- **Protocol**: Counterbalanced `A1 -> B1 -> A2 -> B2` (`16` new live windows; **`312` cumulative windows** — crossing the **`300`-Window Milestone** in `S676A-R75`!)
- **Safety Boundaries**: `198.18.0.45` & `198.18.0.46` untouched (`touched_241_or_242 = false`).

## 1. Executive Summary (`R74..R77` — `300+` Window Barrier Broken!)
In `Stage 676A` ([`run_stage676a_live_wa_77round_312window_milestone_r74_77.py`](../tools/bench/run_stage676a_live_wa_77round_312window_milestone_r74_77.py)), we crossed the **`300`-window barrier** (`304` cumulative windows in `R75`, **`312` cumulative windows** in `R77`) and validated **`WA Champion v12`** head-to-head against Stock `OpenWrt 24.10.4`:

| Round | Hypothesis Tested | Arm A Goodput / `p50` RTT | Arm B Goodput / `p50` RTT | Delta (`GP` / `p50` / `Pareto`) | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`S676A-R74`** | Per-TID `AQL` Voice/Video (`VO=300/600, VI=1000/2000` vs `250/500, 750/1500`) | **`71.996 Mbps`** / `25.368 ms` | `69.421 Mbps` / `23.058 ms` | `-3.58%` GP / `-9.11%` `p50` / `-2.87%` Pareto | `RETAIN_ARM_A` (`VO=300/600, VI=1000/2000`) |
| **`S676A-R75`** | **`304`-Window Milestone!** `gro_flush_timeout=10us/tx_bias=1` vs `20us/tx_bias=2` | `71.002 Mbps` / `19.672 ms` | **`70.900 Mbps`** / **`13.164 ms`** | `-0.14%` GP / **`-33.08%` `p50`** / **`+4.96%` Pareto** | **`PROMOTE_ARM_B`** (`20000 ns` / `tx_bias=2`) |
| **`S676A-R76`** | `mac80211` `aql_threshold` (`3000 us` vs `4000 us`) | **`71.223 Mbps`** / **`13.810 ms`** | `71.593 Mbps` / `24.318 ms` | `+0.52%` GP / `+76.09%` `p50` / `-8.87%` Pareto | `RETAIN_ARM_A` (`aql_threshold=3000 us`) |
| **`S676A-R77`** | **`312`-Window `WA Champion v12` vs Stock `OpenWrt 24.10.4`** | `62.009 Mbps` / `59.395 ms` | **`76.546 Mbps`** / **`33.219 ms`** | **`+23.44%` GP** / **`-44.07%` `p50`** / **`+117.12%` Pareto** | **`PROMOTE_ARM_B`** (`WA Champion v12`) |

## 2. Headline Milestone Results (`S676A-R77`)
- **All-Time Record VHT20 Goodput (`78.513 Mbps` in `B1`, `76.546 Mbps` mean)**: In `S676A-R77`, `WA Champion v12` achieved **`78.513 Mbps` (`B1`)** and **`74.578 Mbps` (`B2`)** — a counterbalanced mean of **`76.546 Mbps` (`+23.44%` over Stock `OpenWrt 24.10.4` `62.009 Mbps`)** on a `20 MHz` (`VHT20` 2x2) channel!
- **Simultaneous Latency Collapse**: Under 16-stream bidirectional saturation, `WA Champion v12` reduced mean `p50` RTT by **`-44.07%` (`33.219 ms` vs `59.395 ms`, with `B1 = 17.776 ms`)** and `p95` RTT by **`-20.21%` (`119.597 ms` vs `149.895 ms`)**, with **`0.0%` packet loss** on both `VoIP` (`1.918 ms` jitter) and `IPTV`.

## 3. Artifacts & Verification
- **Receipt**: [`stage676a_live_wa_77round_312window_milestone_r74_77.json`](../artifacts/autoresearch/stage676a_live_wa_77round_312window_milestone_r74_77.json)
- **Pytest**: [`tests/test_stage676a.py`](../tests/test_stage676a.py)
