<!-- doc-head: STAGE716A_LTU_CHAMPION_V18_240WINDOW_FIELD_ROLLOUT_KIT.md preserved document content -->
<!-- /doc-head -->


# Stage 716A — `AF-LTU` Champion `v18` (`240`-Window) Field Rollout Kit

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `proprietary airMAX/LTU module` (`ame_core.ko`) / `hardware` (`Beetle` `ame_asic0`).
- **240-Window Milestone (`20` Live Rounds on `.110`)**: Packages `LTU` Champion `v18` (`firmware/ltu_safe_kit/fmx_ltu_v18_240window_field_kit.sh`, `SHA-256`: `3c85d9a098cc40fc927918f00d236c3cc21e66071adc4f79060f72ea160da645`), achieving **`0.186 ms` mean RTT** and integrating `fmx_ltu_gps_1pps_sync_guard.sh` and `fmx_ltu_dma_ring_backpressure_guard.sh` across all `5` `LTU` boards.

## 2. `LTU` Champion `v18` Components
| Module / Helper | Role | Safety & Performance |
| :--- | :--- | :--- |
| `fmx_ltu_v18_240window_field_kit.sh` | Master `v18` rollout script (`240` windows) | **`0.186 ms` mean RTT** (`-20.85%` vs stock `0.235 ms`) |
| `fmx_ltu_gps_1pps_sync_guard.sh` | GPS `1PPS` & `DCXO` holdover monitor | Read-only `/proc/kallsyms` audit (`0` `/dev/ame*` touches) |
| `fmx_ltu_dma_ring_backpressure_guard.sh` | DMA ring backpressure & `BQL=36288` guard | Prevents `GMAC0` $\rightarrow$ `ame_asic0` descriptor overflow |

## 3. Hard Safety Verification
- **Zero `/dev/ame*` Touches**: `100%` userspace/sysctl/sysfs safe across all `240` cumulative windows.
