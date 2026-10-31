<!-- doc-head: STAGE756A_LIVE_WA_84ROUND_344WINDOW_MILESTONE_R81_84.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 756A — Live `WA` `84`-Round (`344`-Window) Milestone & `WA Champion v13` Promotion (`R81..R84`)

- **Status**: `CONFIRMED`
- **Attribution**: `QCA firmware` + `ath10k` + `mac80211` + `Linux` + `hardware`
- **Protocol**: Counterbalanced `A1 -> B1 -> A2 -> B2` (`16` new live windows; **`336` RF windows / `344` cumulative windows with E2E**)
- **Safety Boundaries**: `198.18.0.45` & `198.18.0.46` untouched (`touched_241_or_242 = false`).

## 1. Executive Summary (`R81..R84` — `84` Counterbalanced Rounds Completed!)
In `Stage 756A` ([`run_stage756a_live_wa_84round_344window_milestone_r81_84.py`](../tools/bench/run_stage756a_live_wa_84round_344window_milestone_r81_84.py)), we executed rounds `R81..R84` (`344` cumulative windows) and validated **`WA Champion v13`** head-to-head against Stock `OpenWrt 24.10.4`:

| Round | Hypothesis Tested | Arm A Goodput / `p50` RTT | Arm B Goodput / `p50` RTT | Delta (`GP` / `p50` / `Pareto`) | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`S756A-R81`** | Asymmetric `AP/STA FQ Quantum` (`3028/1514` vs `4542/3028`) | `67.341 Mbps` / `29.285 ms` | **`68.097 Mbps`** / **`17.392 ms`** (`B2=12.330 ms`) | `+1.12%` GP / **`-40.61%` `p50`** / **`+16.33%` Pareto** | **`PROMOTE_ARM_B`** (`4542/3028`) |
| **`S756A-R82`** | `ag71xx eth0 BQL` (`36288/600` vs `24192/400`) | `61.046 Mbps` / `19.671 ms` | **`61.061 Mbps`** / **`17.809 ms`** (`p95=43.874 ms`) | `+0.02%` GP / **`-9.47%` `p50`** / **`+21.48%` Pareto** | **`PROMOTE_ARM_B`** (`24192/400`) |
| **`S756A-R83`** | `TCP Compressed SACK` (`250us/16` vs `100us/8`) | **`64.125 Mbps`** / `23.119 ms` | `62.629 Mbps` / **`18.413 ms`** | `-2.33%` GP / `-20.36%` `p50` / `-2.07%` Pareto | `RETAIN_ARM_A` (`250us/16`) |
| **`S756A-R84`** | **`344`-Window `WA Champion v13` vs Stock `OpenWrt 24.10.4`** | `55.117 Mbps` / `84.835 ms` | **`64.052 Mbps`** / **`28.741 ms`** (`p95=87.589 ms`) | **`+16.21%` GP** / **`-66.12%` `p50`** / **`+210.02%` Pareto** | **`PROMOTE_ARM_B`** (**`WA Champion v13`**) |

## 2. Key Findings (`R81..R84`)
- **Asymmetric `AP/STA FQ Quantum` (`4542 B` / `3028 B` in `S756A-R81`)**: Scaling `AP fq_quantum=4542` (`3 MTU`) and `STA fq_quantum=3028` (`2 MTU`) reduced under-load `p50` RTT by **`-40.61%` (`17.392 ms` vs `29.285 ms`)** and `VoIP` jitter from `4.023 ms` to **`2.587 ms`** while lifting goodput to **`68.097 Mbps`** (`+16.33%` Pareto).
- **Tighter `eth0 BQL` (`24192 B / 400 ms` in `S756A-R82`)**: Cut `p95` RTT by **`-36.81%` (`43.874 ms` vs `69.427 ms`)** and `p50` RTT by **`-9.47%` (`17.809 ms`)** (`+21.48%` Pareto).
- **`S756A-R84` Head-to-Head (`WA Champion v13` vs Stock)**: Achieved **`+16.21%` higher goodput (`64.052 Mbps` vs `55.117 Mbps`)**, **`-66.12%` lower `p50` RTT (`28.741 ms` vs `84.835 ms`)**, **`-39.91%` lower `p95` RTT (`87.589 ms` vs `145.767 ms`)**, and **`1.453 ms` `VoIP` jitter (`0.0%` loss)** (`+210.02%` Pareto).

## 3. Artifacts & Verification
- **Receipt**: [`stage756a_live_wa_84round_344window_milestone_r81_84.json`](../artifacts/autoresearch/stage756a_live_wa_84round_344window_milestone_r81_84.json)
- **Pytest**: [`tests/test_stage756a.py`](../tests/test_stage756a.py)
