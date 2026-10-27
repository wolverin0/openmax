<!-- doc-head: STAGE620A_GUARIDA_PANEL2_39US_SLOT_GUARD_AND_REQUEUE_ALERTER.md preserved document content -->
<!-- /doc-head -->


# Stage 620A — Guarida `Panel2` (`.82`) `39 us` Slot Guard & Requeue Alerter

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`) / `hardware`.
- **Stage 533A Grounding**: In `ubnt_poll_host.ko`, the per-CPE uplink TDMA guard interval obeys:
  $$\text{slot\_guard\_us} = \text{rtt\_us} + 21\ \mu\text{s}$$
  On `Panel2-Guarida` (`.82`, `22` CPEs up to `2.7 km`, $\text{rtt\_us} = 18\ \mu\text{s}$), $\text{slot\_guard\_us} = 39\ \mu\text{s}$, which consumes **`26.0%`** of a micro `150 us` uplink slice (`39 / 150 = 26%`), leaving only `111 us` for payload and triggering `deferred_list` requeue storms.
- **Amortization via `cbp_dur=900us`**: Expanding the contention-based burst period to `900 us` (`Stage 479A`/`547A`) amortizes the `39 us` guard tax from **`26.0%` down to `4.33%`**.

## 2. Guarida TDMA Guard-Tax Telemetry Matrix
| Sector | Max Range | $\text{rtt\_us}$ | $\text{slot\_guard\_us}$ | Tax @ `150 us` Slice | Tax @ `cbp_dur=900us` | Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `Panel2` (`.82`, `22` CPEs) | `2.7 km` | `18.0 us` | **`39.0 us`** | **`26.00%`** | **`4.33%`** | `WARN_150US_SLICE_26PCT_GUARD_TAX` |
| `Panel3` (`.83`, `6` CPEs) | `1.8 km` | `12.0 us` | `33.0 us` | `22.00%` | `3.67%` | `OPTIMAL_WITH_CBP900_COOP` |

## 3. Safety & Topology Compliance
- **Guarida `SG-01` Respected**: Zero touches to live tower or protected nodes.
