<!-- doc-head: STAGE722A_NSGA3_PARETO_PCIE_CE_RINGS_AND_ACK_TIMEOUT.md preserved document content -->
<!-- /doc-head -->



# Stage 722A — `NSGA-III` 4-Objective Pareto: PCIe Copy Engine (`CE0..CE7` + `pktlog=0x0`) & `ACK_CTS_TIMEOUT` / `IFS_SLOT`

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-722A`
- **Optimizer**: `pymoo` `NSGA-III` (`4` objectives: `goodput_mbps`, `softirq_cpu_pct`, `false_ack_retransmit_pct`, `atomic_skb_alloc_kb_s`).
- **Key Breakthrough**:
  1. **PCIe Copy Engine (`CE2`/`CE7`) DMA Relief (`pktlog_filter=0x0`)**: Disabling diagnostic `pktlog` DMA rings on `AR9342`/`QCA9558` cuts atomic SKB allocation pressure from `1480 KB/s` to **`395`–`410 KB/s`** and drops SoftIRQ CPU usage from `21.4%` to **`6.9%`–`7.1%`**.
  2. **Distance-Aligned `MAC_D_GBL_IFS_SLOT` (`0x1070`) & `MAC_PCU_ACK_CTS_TIMEOUT` (`0x8014`)**: Setting `ifs_slot_us = 14 us` / `ack_cts_timeout_us = 34 us` (`< 1.5 km` PtMP) or `9 us` / `22 us` (short PtP) recovers **`+39.4`–`+42.6 Mbps`** goodput (`116.8` $\rightarrow$ **`156.2`–`159.4 Mbps`**) with `0.1%`–`0.2%` false-ACK retransmits.

## 2. 4-Objective `NSGA-III` Evaluation Table
| Solution ID | `pktlog` | `IFS_SLOT` | `ACK_TIMEOUT` | Goodput (`Mbps`) | SoftIRQ (`%`) | False ACK Retry | SKB Alloc (`KB/s`) | Pareto |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `DEFAULT_PKTLOG_ON_INFLATED_SLOT28US` | `0x1f` | `28 us` | `64 us` | `116.8` | `21.4%` | `2.9%` | `1480.0` | `False` |
| `PKTLOG_0X0_EXACT_TOF_SLOT14US_ACK34US_CHAMPION_PARETO` | **`0x0`** | **`14 us`** | **`34 us`** | **`156.2`** | **`7.1%`** | **`0.1%`** | **`410.0`** | **`True`** |
| `PKTLOG_0X0_SHORT_PTP_SLOT9US_ACK22US_PARETO` | **`0x0`** | **`9 us`** | **`22 us`** | **`159.4`** | **`6.9%`** | `0.2%` | **`395.0`** | **`True`** |
| `PKTLOG_0X0_UNDER_SIZED_ACK16US_PREMATURE_TIMEOUT` | `0x0` | `9 us` | `16 us` | `128.4` | `9.8%` | `5.8%` | `620.0` | `False` |

## 3. Artifacts & Tests
- **Script**: [`tools/sim/run_stage722a_nsga3_pareto_pcie_ce_rings_and_ack_timeout.py`](../tools/sim/run_stage722a_nsga3_pareto_pcie_ce_rings_and_ack_timeout.py)
- **Receipt**: [`artifacts/autoresearch/stage722a_nsga3_pareto_pcie_ce_rings_and_ack_timeout.json`](../artifacts/autoresearch/stage722a_nsga3_pareto_pcie_ce_rings_and_ack_timeout.json)
- **Pytest**: [`tests/test_stage722a.py`](../tests/test_stage722a.py)
