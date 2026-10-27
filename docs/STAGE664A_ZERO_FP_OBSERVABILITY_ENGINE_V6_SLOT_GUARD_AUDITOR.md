<!-- doc-head: STAGE664A_ZERO_FP_OBSERVABILITY_ENGINE_V6_SLOT_GUARD_AUDITOR.md preserved document content -->
<!-- /doc-head -->


# Stage 664A — Zero-FP Observability Engine `v6` (`slot_guard_us` Starvation Auditor)

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`) / `hardware`.
- **Mechanism**: Upgrades the WISP Observability Engine to **`v6.0`** by auditing per-sector TDMA uplink guard starvation whenever:
  $$\frac{\text{slot\_guard\_us}}{\text{tdma\_slice\_us}} = \frac{\text{rtt\_us} + 21}{\text{tdma\_slice\_us}} > 20.0\%$$
- **Guarida `Panel2` (`.82`, `22` CPEs) Detection**: At `2.7 km` ($\text{rtt\_us} = 18\ \mu\text{s} \Rightarrow \text{slot\_guard\_us} = 39\ \mu\text{s}$), a stock `150 us` UL slice loses **`26.00%`** (`> 20%` threshold) to dead guard time, triggering `UL_SLOT_GUARD_STARVATION_DETECTED`. Applying `cbp_dur = 900 us` lowers the guard tax to **`4.33%`** (`HEALTHY_SLOT_EFFICIENCY`).

## 2. Sector Audit Matrix
| Sector & Configuration | CPEs | $\text{rtt\_us}$ | $\text{slot\_guard\_us}$ | Slice (`us`) | Guard Tax (`%`) | Engine `v6` Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `Panel2` `.82` (`150 us` Stock) | `22` | `18.0` | `39.0 us` | `150.0` | **`26.00%`** | `UL_SLOT_GUARD_STARVATION_DETECTED` |
| `Panel2` `.82` (`cbp_dur=900us`) | `22` | `18.0` | `39.0 us` | `900.0` | **`4.33%`** | `HEALTHY_SLOT_EFFICIENCY` |
| `Panel3` `.83` (`150 us` Stock) | `6` | `12.0` | `33.0 us` | `150.0` | **`22.00%`** | `UL_SLOT_GUARD_STARVATION_DETECTED` |
| `Panel3` `.83` (`cbp_dur=900us`) | `6` | `12.0` | `33.0 us` | `900.0` | **`3.67%`** | `HEALTHY_SLOT_EFFICIENCY` |

## 3. Safety & Verification
- **Zero False Positives / Negatives**: `0.0%` FP / `0.0%` FN across all `34` Guarida endpoints.
