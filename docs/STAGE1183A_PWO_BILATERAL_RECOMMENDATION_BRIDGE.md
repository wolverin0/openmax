<!-- doc-head: Stage 1183A offline PWO recommend-only bridge for the 1181A bilateral engine; ac2_devices + NMS, 6 gates, 20 MHz width guard, auto_approve always false -->
# Stage 1183A - PWO bilateral recommendation bridge

Offline contract adapter (no live calls, `live_devices_touched=false`). Module `tools/uisp/pwo_bilateral_recommendation_bridge.py`; test `tests/test_stage1183a_pwo_bridge.py`; receipt `artifacts/autoresearch/stage1183a_pwo_bilateral_recommendation_bridge.json`.

Source contract read (read-only): `whatsappbot-final/docs/subsystems/network-and-pwo.md`.

## API
- `bridge_recommendation(bilateral_eval) -> dict`: maps a 1181A `evaluate_channel_change` result (`allowed`, `vetoes`, `blast_radius_cpes`, `interference_cost`, `evaluated_ends`) to a PWO recommend-only payload.
- `main()` with `--write-receipt` runs allowed, vetoed and width-change fixtures and writes the receipt.

## Guarantees
- `auto_approve` is always `false`; `AutoApprovePredicate` stays unwired.
- `width_mhz` is always 20; a requested width change sets `width_guard_triggered` and yields NO-CHANGE.
- Any veto at either end yields a NO-CHANGE recommendation with the reason.
- `preflight_gates` lists the 6 WirelessExperimentGates (allow-list, per-AP cooldown, window 02:00-06:00 ART, site lock, 3 wet-runs/24h, health/cache-freshness) as to-be-checked by PWO.
- `data_sources`: `ac2_devices`, `NMS /devices?siteId` (via `unmsClientSiteId`). `forbidden_sources`: stale `equipment_inventory`, broken `/api/analytics/capacity`.

## Honesty
- The 1181A engine module was not present in `tools/uisp/` at build time; an inline fixture mirrors its output shape.
- Recommend-only: no PWO execution path is touched. `CONFIRMED_LIVE_HARDWARE` stays 0.
