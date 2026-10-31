<!-- doc-head: Stage1182A offline co-site peer buddy that classifies tower anomalies into self-interference, PoP power or weather, or single radio hang and emits recommend-only AQM hints -->
<!-- /doc-head -->

# Stage1182A - On-tower peer buddy and anomaly disambiguator

Evidence class `ON_TOWER_PEER_BUDDY_DISAMBIGUATOR_MODEL`. Offline and simulated, `live_devices_touched=false`. The module in `tools/uisp/on_tower_peer_buddy_and_anomaly_disambiguator.py` has no network code and never writes to a device.

## Concept

Panel1 `.84`, the local PoP switch, can see sibling APs and the PtP STA at Guarida. When several of them degrade, the pattern separates a shared cause from a single bad radio.

## Public API

- `disambiguate(observation) -> {classification, rationale, confidence}`.
- `aqm_feed_forward(upstream_ptp_capacity_drop_pct) -> {recommend_only, suggested_action, rationale, ...}`.
- `main()` with `--write-receipt`.

Observation keys: `affected_radios` (list or count, required), `pop_radios` or `pop_radio_count`, `airtime_spike`, `power_event`, `weather`, `backhaul_capacity_drop_pct`, `peers_also_degraded` (list, count or bool).

## Classification rules (evaluated in order)

1. `power_event` or `weather` set: `POP_POWER_OR_WEATHER_EVENT` (0.95 if every PoP radio is affected, else 0.85).
2. All PoP radios affected, no airtime spike: `POP_POWER_OR_WEATHER_EVENT` (0.75).
3. All PoP radios affected with airtime spike: `CO_SITE_SELF_INTERFERENCE` at low confidence (0.55).
4. Two or more degraded radios plus airtime spike: `CO_SITE_SELF_INTERFERENCE` (0.85).
5. Exactly one degraded radio, peers healthy: `SINGLE_RADIO_HANG` (0.8).
6. Fallback, several degraded without spike or flag: `CO_SITE_SELF_INTERFERENCE` (0.4).

No affected radio raises `ValueError`.

## AQM feed-forward

With `keep = 1 - drop/100`, the hint is `target_ms = max(1, 5*keep)` and `limit_packets = max(256, round(1024*keep))` for fq_codel. The result always has `recommend_only=true`. A drop of 0 returns action `none`. Values outside 0..100 raise `ValueError`.

## Commands

```powershell
python tools/uisp/on_tower_peer_buddy_and_anomaly_disambiguator.py --write-receipt
python -m pytest tests/test_stage1182a_peer_buddy.py
```

Receipt: `artifacts/autoresearch/stage1182a_on_tower_peer_buddy_disambiguator.json`, written with 3 write/read-back attempts and a NUL check. Claim id `FMX-STAGE1182A-ON-TOWER-PEER-BUDDY-AND-ANOMALY-DISAMBIGUATOR`.

## Limits

Thresholds and confidences are heuristic model values, not fitted to field data. The AQM numbers are a starting hint for an operator and are not applied automatically.
