<!-- doc-head: STAGE25_SCHOLAR_HYPERRESEARCH_FUSION_AND_M3_M5_BENCHMARK.md preserved document content -->
<!-- /doc-head -->

# Stage 25 — `scholar` MCP + `hyperresearch` Dual-Engine Fusion & Physical `M3` (`PB-023` TXQ CoDel) + `M5` (`PB-022` Asymmetric UL/DL ACK Pacing) Benchmark

- **Task ID**: `T-S25-SCHOLAR-MCP-HYPERRESEARCH-FUSION-AND-M3-M5-BENCH`
- **Completed UTC**: `2026-10-25T16:01:33Z`
- **Status**: `PASS_STAGE25_SCHOLAR_FUSION_AND_M3_M5_COMPLETE`
- **Fusion Bridge**: [`tools/research/run_scholar_mcp_hyperresearch_fusion.py`](../tools/research/run_scholar_mcp_hyperresearch_fusion.py)
- **Fusion Receipt**: [`artifacts/autoresearch/stage25_scholar_hyperresearch_fusion_20261025.json`](../artifacts/autoresearch/stage25_scholar_hyperresearch_fusion_20261025.json)
- **Bench Runner**: [`tools/bench/run_stage25_m3_txq_codel_and_m5_ack_pacing_bench.py`](../tools/bench/run_stage25_m3_txq_codel_and_m5_ack_pacing_bench.py)
- **Bench Receipt**: [`artifacts/autoresearch/stage25_scholar_fusion_and_m3_m5_bench_20261025.json`](../artifacts/autoresearch/stage25_scholar_fusion_and_m3_m5_bench_20261025.json)

---

## 1. Dual-Engine `scholar` MCP (`jev-1.14.0`) + `hyperresearch` (`v0.12.0`) Fusion Architecture

`tools/research/run_scholar_mcp_hyperresearch_fusion.py` unifies our two complementary academic intelligence engines into a single deterministic pipeline:

| Stage | Engine | Role & Verified Output |
| :--- | :--- | :--- |
| **1. Candidate Discovery** | `scholar` MCP (`scholar_research` / `scholar_search`) | Queries arXiv for empirical wireless MAC, AQM, and TCP ACK pacing papers. |
| **2. System One Semantic Gatekeeper** | `scholar` MCP (`jev-1.14.0`) | Computes `P_empirical` and `P_applicable` probabilities, screening out non-applicable papers (`0911.1510v1`, `1706.03580v1`, `1902.03439v1`) and retaining `1703.00064v2` (`P_empirical=0.98, P_applicable=0.80`) and `0806.1089v1` (`P_empirical=0.85, P_applicable=0.55`). |
| **3. Exact-Span Claim Verification** | `scholar` MCP (`scholar_verify_claim`) | Verifies claims with `verification_probability = 0.97` (`status = supported`, `result_state = verified`) and extracts exact character offsets (`abstract[821:1035]` on `1703.00064v2` and `abstract[874:1122]` on `0806.1089v1`). |
| **4. Persistent Vault Ingestion** | `hyperresearch` (`hpr` v0.12.0) | Writes raw sources to `artifacts/hyperresearch_vault/sources/arxiv_*.json`, creates linked vault notes, ingests structured claims into SQLite (`hyperresearch claims ingest --tag stage25-scholar-fusion-20261025`), and runs `hyperresearch sync` + `repair` (`22` total notes, `77` graph links, `47,368` words). |

---

## 2. Physical Benchmark Results (`A1 -> B1 -> A2 -> B2` Starting Strictly from Stage 24E Champion v5)

| Round | Control Arm `A` (Stage 24E Champion v5) | Treatment Arm `B` (Champion v5 + Stage 25 Candidate) | Arm `A` Goodput | Arm `B` Goodput | Goodput $\Delta$ | Arm `A` `p95` RTT | Arm `B` `p95` RTT | `p95` RTT $\Delta$ | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S25-R1`** (`M3` `PB-023` TXQ CoDel / Dynamic Quantum) | Stage 24E 3-CPE All-Champion v5 (`fq_codel quantum 1514 target 10ms interval 50ms`, per-AC AQL `750..1500/1500..3000`, `rts 512`) | Stage 24E Champion v5 + **`quantum 300 target 3ms interval 50ms` + AQL `2000/4000`** | **`62.06 Mbps`** | `45.12 Mbps` | `-27.31%` | **`64.33 ms`** | `75.18 ms` | `+16.87%` | **`RETAIN_CURRENT_CHAMPION`** (`quantum 1514 target 10ms` wins!) |
| **`S25-R2`** (`M5` `PB-022` Asymmetric UL/DL TCP ACK Pacing, `arXiv:0806.1089v1`) | Stage 24E 3-CPE All-Champion v5 (`tcp_thin_linear_timeouts=0`, `tcp_autocorking=1`, `AC_VO AQL 750/1500`) | Stage 24E Champion v5 + **`M5` Asymmetric UL/DL ACK Pacing** (`tcp_thin_linear_timeouts=1`, `tcp_early_retrans=3`, `tcp_autocorking=0`, `AC_VO AQL 600/1200`) | `61.07 Mbps` | **`63.30 Mbps`** | **`+3.66%`** | `74.73 ms` | **`67.02 ms`** | **`-10.33%`** | **`KEEP_NEW_CHAMPION`** (Promoted to **Champion v6**) |

---

## 3. Key Findings & Promotion to `Champion v6`

1. **`S25-R1` (`M3` Sub-MTU `quantum 300` + `target 3ms` vs Full-MTU `quantum 1514` + `target 10ms` — `RETAIN_CURRENT_CHAMPION`)**:
   - Directly confirms the *Flow-CoDel (2025)* (`10.1007/s44354-025-00012-z`) claim in our vault: shrinking `fq_codel` `quantum` to `300 B` and `target` to `3 ms` on a 3-CPE 802.11ac sector causes premature CoDel drops and starves A-MPDU aggregation (`62.064 -> 45.117 Mbps`, `-27.31%`; `p95` RTT `64.328 -> 75.177 ms`, `+16.87%`). Our fail-closed Pareto promoter automatically rejected `S25-R1` and restored `quantum 1514 target 10ms` + per-AC AQL `750..1500/1500..3000`.
2. **`S25-R2` (`M5` Asymmetric UL/DL TCP ACK Pacing, `arXiv:0806.1089v1` — `KEEP_NEW_CHAMPION`)**:
   - Guided by the `scholar` + `jev-1.14.0` verified claim from `arXiv:0806.1089v1` (*"employing a congestion control and filtering algorithm on TCP ACK packets of uplink flows, thereby prioritizing the access of TCP data packets of downlink flows at the AP"*), enabling `tcp_thin_linear_timeouts=1`, `tcp_early_retrans=3`, `tcp_autocorking=0`, and tightening `AC_VO` AQL (`600/1200 us`) simultaneously increased 3-CPE aggregate bidirectional goodput by **`+3.66%` (`61.067 -> 63.299 Mbps`, reaching `64.560 Mbps` / `3.228 Mbps/MHz` in `B2`)** AND reduced worst-case sector `p95` RTT by **`-10.33%` (`74.734 -> 67.016 ms`)** with **`0.0%` packet loss** across all 3 stations in both `B1` and `B2`.
3. **Final Live RAM State (`Champion v6`)**:
   - All 4 bench radios (`LAP-120` AP, `NanoStation 5AC Loco` STA, `Rocket Prism 5AC Gen2` STA, and `LiteBeam M5` STA) were verified at completion with the promoted **Stage 25 Champion v6** parameters active in RAM (`persistent_flash_writes: false`), and `controller/multiradio_golden_profile_applicator.py` + `artifacts/autoresearch/champion_state_ledger.json` have been updated.
