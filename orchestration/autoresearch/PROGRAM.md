# FuturaMAX `autoresearch` Program (`PROGRAM.md`)

This document adapts Andrej Karpathy's [`autoresearch`](https://github.com/karpathy/autoresearch) autonomous loop (`program.md` + immutable `prepare.py` + single mutable surface + `results.tsv` `keep/discard/crash`), multi-agent patterns from [`Awesome-Auto-Research-Tools`](https://github.com/handsome-rich/Awesome-Auto-Research-Tools) (`ARIS`, `CORAL`, `RD-Agent`), and our local **`scholar-mcp`** scientific verification engine (`ArXiv` + `OpenAlex` + `DuckDB HuggingFace Parquet` + `TypeSafe Jev` semantic predicates) to **FuturaMAX** (`802.11ac` / `QCA988x` / `ath10k-ct` / `airOS 8` / `OpenWrt 24.10.4` fixed wireless PtMP & PtP optimization).

---

## 1. Core Mapping: `karpathy/autoresearch` $\rightarrow$ `FuturaMAX`

| `karpathy/autoresearch` | `FuturaMAX` Equivalent | Role & Constraints |
| :--- | :--- | :--- |
| **`program.md`** | [`orchestration/autoresearch/PROGRAM.md`](PROGRAM.md) | Human-maintained research instructions, safety boundaries, and active optimization objective. |
| **`prepare.py` (Immutable Evaluator)** | [`fmx_autoresearch_harness.py`](fmx_autoresearch_harness.py) (`compute_fmx_objective`) + [`stage12_ptp_powerbeam_harness.py`](../../tools/bench/stage12_ptp_powerbeam_harness.py) | **READ-ONLY / IMMUTABLE** during an optimization loop. Enforces hardware identity pinning, RAM-only rollback guards, fixed-duration offered load (`iperf3` receiver goodput + simultaneous `ping` p50/p95/p99 latency + station drop counter), and scalar objective calculation. |
| **`train.py` (Single Mutable Surface)** | `MutableWirelessPolicy` JSON/profile | **ONLY** mutable surface per iteration: bounded RAM-only queuing/MAC parameters (`aql_txq_limit_ac_be`, `aql_threshold`, `codel_target_ms`, `codel_interval_ms`, `cake_bandwidth_mbps`, `rate_mask_vht_mcs`, `rts_threshold`, `coverage_class`). Never touches flash, calibration (`ART`), regulatory/DFS, or production without explicit operator gate. |
| **`val_bpb` (Lower is Better)** | **`fmx_loss`** (Lower is Better) | Scalar objective combining normalized throughput deficit, loaded `p95`/`p99` bufferbloat penalty, airtime unfairness (`1 - Jain`), and retry/PER penalty. |
| **`results.tsv`** | `artifacts/autoresearch/results.tsv` | Append-only TSV log (`commit`, `fmx_loss`, `goodput_mbps`, `p95_rtt_ms`, `jain_fairness`, `status`, `description`) with `keep`, `discard`, or `crash`. |
| **Literature Grounding** | **`scholar-mcp`** (`ScholarEngine`) | Before proposing a non-trivial MAC/AQM change, query `scholar-mcp` (`scholar_search` / `scholar_research` / `scholar_verify_claim`) to ground the hypothesis in peer-reviewed `802.11` / AQM / rate-control literature. |

---

## 2. Scalar Objective Definition (`fmx_loss` — Lower is Better)

Just as `autoresearch` minimizes `val_bpb` over a fixed 5-minute budget, FuturaMAX minimizes **`fmx_loss`** over a fixed physical or replay benchmark window (e.g. `3x 30s` paired repetitions):

$$\text{fmx\_loss} = w_{\text{tput}} \cdot \max\left(0, 1 - \frac{G_{\text{rx,mbps}}}{G_{\text{target,mbps}}}\right) + w_{\text{p95}} \cdot \frac{\max(0, \text{RTT}_{\text{p95,ms}} - \text{RTT}_{\text{baseline,ms}})}{\text{RTT}_{\text{budget,ms}}} + w_{\text{p99}} \cdot \frac{\max(0, \text{RTT}_{\text{p99,ms}} - \text{RTT}_{\text{baseline,ms}})}{\text{RTT}_{\text{budget,ms}}} + w_{\text{fair}} \cdot (1 - J_{\text{fairness}}) + w_{\text{ret}} \cdot \text{PER}$$

### Hard Disqualification Gates (`status = crash` or `discard`)
Per `AGENTS.md` Sections 4, 7, and 12.3, an iteration is **immediately rejected** (`crash` or `discard`, never `keep`) regardless of `goodput_mbps` if:
1. `restoration_verified == False` or `station_drops > 0` $\rightarrow$ **`crash`** (hardware session drop or incomplete restoration).
2. `packet_loss_pct > max_packet_loss_pct` (default `2.0%`) $\rightarrow$ **`discard`** (unacceptable packet loss).
3. `p99_rtt_ms > max_p99_rtt_ms` (default `150.0 ms` on bench, `250.0 ms` multi-vendor) $\rightarrow$ **`discard`** (optimizing throughput while materially worsening tail latency is forbidden by `AGENTS.md` Section 4).
4. `fmx_loss >= best_fmx_loss - min_improvement_delta` $\rightarrow$ **`discard`** (must beat the incumbent `best_fmx_loss` by at least `min_improvement_delta`, or tie `fmx_loss` while strictly reducing complexity).

---

## 3. The Autonomous Loop Protocol

When running an authorized bench optimization session (e.g., on the isolated `LAP-120` $\leftrightarrow$ `Loco195` / `Rocket198` bench or when the `2x PowerBeam 5AC` PtP bench is connected):

1. **Ground Hypothesis (`scholar-mcp`)**:
   - Query `scholar-mcp` for the specific mechanism under test (e.g. *"802.11ac airtime queue limits AQL FQ-CoDel bufferbloat"*, *"Wi-Fi rate adaptation hidden node RTS/CTS airtime fairness"*).
   - Extract concrete parameter relationships (`target`, `interval`, per-AC `aql_txq_limit`, `rts_threshold`).
2. **Propose Single Mutable Policy (`MutableWirelessPolicy`)**:
   - Change **one primary wireless/queueing knob** at a time (`AGENTS.md` Section 12).
   - Validate the policy against `MutableWirelessPolicy.validate_bounds()` (rejects out-of-range values, regulatory/DFS overrides, or flash writes).
3. **Arm RAM-Only Rollback Guard & Execute Fixed Benchmark**:
   - Arm the HUP-immune `/tmp` rollback watchdog on the bench radio(s) (`90–120s` lease).
   - Run the immutable benchmark harness (`prepare/evaluate`).
   - Collect receiver-only `goodput_mbps`, loaded `p50/p95/p99` RTT (`ms`), `packet_loss_pct`, `jain_fairness`, `retry_rate`, and `restoration_verified`.
4. **Evaluate & Record in `results.tsv`**:
   - Compute `ObjectiveEvaluation = compute_fmx_objective(obs, config, best_fmx_loss)`.
   - Append row to `results.tsv`.
   - If `decision == KEEP`: advance the incumbent policy baseline to the new policy.
   - If `decision in (DISCARD, CRASH)`: revert the mutable policy to the incumbent baseline and preserve the negative evidence in `results.tsv`.
