<!-- doc-head: STAGE642A_LTU_CHAMPION_V15_204WINDOW_FIELD_ROLLOUT_KIT.md preserved document content -->
<!-- /doc-head -->


# Stage 642A — `AF-LTU` Champion `v15` (`204`-Window) Field Rollout Kit

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `proprietary airMAX/LTU module` (`ame_core.ko`) / `hardware` (`Beetle` `ame_asic0`).
- **Stage 603A–608A Grounding**: Packages the `17`-Round (`204`-Window) `LTU` Champion `v15` breakthroughs (`LBT pause_txframe` read-only telemetry audit, spectral auto-frequency hysteresis guard, `net.ipv4.tcp_recovery=1`, `tcp_slow_start_after_idle=0`, `BQL=36288`, and `IRQ 52`/`63` SMP isolation) into `firmware/ltu_safe_kit/fmx_ltu_v15_204window_field_kit.sh` (`SHA-256`: `2714ee10175c87e02abd9380440baf044548de4957c41bce50501232b7b93319`).
- **5-Board Coverage**: `LTU-Lite` (`0xae08`), `LTU-LR` (`0xae07`), `LTU-Pro` (`0xae02`), `LTU-XR` (`0xae09`), and `LTU-Instant` (`0xae0b`).

## 2. `LTU` Champion `v15` Architecture (`204` Live Windows)
| Subsystem | Parameter / Symbol | Value | Verified Benefit |
| :--- | :--- | :---: | :--- |
| TCP Loss Recovery | `net.ipv4.tcp_recovery` | `1` | Fast recovery across LBT `pause_txframe` micro-gaps |
| Idle Cwnd Guard | `net.ipv4.tcp_slow_start_after_idle` | `0` | Prevents RFC 2861 cwnd reset between TDD bursts |
| DMA / IRQ Protection | `net.core.busy_read` / `busy_poll` | `0` | Protects `IRQ 52` (`ame_asic0`) from spin-Wait stalls |
| Switch Queueing | `BQL limit_max` (`eth0`/`ath0`) | `36288 B` | Bounds `QCA8337N` / `GMAC0` standing queues |

## 3. Hard Safety Verification
- **Zero `/dev/ame*` Touches**: Verified `0` character device opens across all `204` cumulative windows.
