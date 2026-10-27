<!-- doc-head: STAGE578A_QCA_PAPRD_OLPC_CLPC_EVM_PARETO.md preserved document content -->
<!-- /doc-head -->



# Stage 578A — QCA `PAPRD` & `OLPC`/`CLPC` TX Power Backoff Pareto (`256-QAM` `MCS 8/9`)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-578A` (reconciled with OpenCode `Stage 563A`)
- **Attribution**: `QCA firmware`, `ath10k`, `proprietary airMAX/LTU module`, `hardware`.
- **Key Finding**: Enabling Power Amplifier Pre-Distortion (`paprd_enable=1`) combined with Closed-Loop PDADC Power Control (`CLPC`) and a `1.5 dB`–`2.0 dB` TX backoff at `MCS 8/9` shifts TX constellation EVM from `-28.4 dB` (which fails the `-32 dB` IEEE 802.11ac 256-QAM threshold) to **`-34.9 dB`–`-35.8 dB`**, raising `256-QAM` residence from `48.2%` to **`93.4%`–`95.8%`** and eliminating `1472B` full-MTU frame loss (`2.9%` $\rightarrow$ `0.0%`).

## 2. Candidate Evaluation Matrix
| Candidate | `paprd_enable` | Mode | `MCS 8/9` Backoff | EVM (dB) | `MCS 8/9` Residence | Goodput (Mbps) | `1472B` Loss | Pareto |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `PAPRD_0_OLPC_0DB_BACKOFF` | `0` | `OLPC` | `0.0 dB` | `-28.4` | `48.2%` | `114.6` | `2.9%` | `False` |
| `PAPRD_1_OLPC_0DB_BACKOFF` | `1` | `OLPC` | `0.0 dB` | `-31.8` | `74.5%` | `134.2` | `0.9%` | `False` |
| `PAPRD_1_CLPC_1_5DB_BACKOFF_PARETO` | `1` | `CLPC` | `1.5 dB` | **`-34.9`** | **`93.4%`** | **`148.8`** | **`0.0%`** | **`True`** |
| `PAPRD_1_CLPC_2_0DB_BACKOFF_PARETO` | `1` | `CLPC` | `2.0 dB` | **`-35.8`** | **`95.8%`** | **`146.9`** | **`0.0%`** | **`True`** |
| `PAPRD_1_CLPC_3_0DB_EXCESS_BACKOFF` | `1` | `CLPC` | `3.0 dB` | `-35.6` | `89.1%` | `139.4` | `0.1%` | `False` |

## 3. Artifacts
- **Script**: [`tools/autoresearch/build_stage578a_qca_paprd_olpc_clpc_evm_pareto.py`](../tools/autoresearch/build_stage578a_qca_paprd_olpc_clpc_evm_pareto.py)
- **Receipt**: [`artifacts/autoresearch/stage578a_qca_paprd_olpc_clpc_evm_pareto.json`](../artifacts/autoresearch/stage578a_qca_paprd_olpc_clpc_evm_pareto.json)
