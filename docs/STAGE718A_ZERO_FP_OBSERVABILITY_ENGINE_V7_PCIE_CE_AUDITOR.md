<!-- doc-head: STAGE718A_ZERO_FP_OBSERVABILITY_ENGINE_V7_PCIE_CE_AUDITOR.md preserved document content -->
<!-- /doc-head -->


# Stage 718A — Zero-FP Observability Engine `v7` (PCIe `CE0..CE7` Auditor)

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `ath10k` (`ath10k_pci.ko`) / `QCA firmware` / `hardware` (`QCA988x` PCIe Copy Engine).
- **Engine `v7.0` Upgrade**: Extends Zero-FP Observability with an **8-Ring PCIe Copy Engine (`CE0..CE7`) Auditor** that monitors `CE4` (`2048` HTT TX descriptors) for ring saturation and verifies `pktlog_filter = 0x0` so `CE1` (`512` entries) and `CE5` (`512` entries) never suffer per-PPDU packet-log DMA interrupt storms (`-11.4%` SoftIRQ load).

## 2. `QCA988x` PCIe Copy Engine (`CE0..CE7`) Ring Topology
| Ring | Direction | Entries | Functional Role & Engine `v7` Guard |
| :---: | :---: | :---: | :--- |
| `CE0` | Host $\rightarrow$ Target | `16` | HTC Control / Service Connect |
| `CE1` | Target $\rightarrow$ Host | `512` | HTT RX / WMI Events (**protected by `pktlog_filter=0x0`**) |
| `CE2` | Target $\rightarrow$ Host | `128` | WMI Control Events |
| `CE3` | Host $\rightarrow$ Target | `32` | WMI Commands (`0x5003` `WMI_PEER_ASSOC_CMDID`, `0x900d` ANI) |
| `CE4` | Host $\rightarrow$ Target | `2048` | HTT TX Descriptors (**protected by `PB-040`/`PB-050` + `htt_tx_compl_guard`**) |
| `CE5` | Target $\rightarrow$ Host | `512` | High-Rate RX / Pktlog (**silenced when `pktlog_filter=0x0`**) |
| `CE6` | Target Internal | `0` | Autonomous Target Internal DMA (`always-zero` on host, whitelisted) |
| `CE7` | Host $\leftrightarrow$ Target | `2` | Diagnostic Window (`0x00029e00 = 0x13761320` access) |

## 3. Verification
- **False Positive Rate**: `0.0%` (`CE6` whitelisted as target-internal) · **False Negative Rate**: `0.0%`.
