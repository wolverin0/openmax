<!-- doc-head: Stage 1202A zero-false-positive bilateral observability pipeline, 2-round confirmation gate over 1181A/1182A/1183A, recommend-only, offline model -->

# Stage 1202A - Zero-FP Bilateral Observability Pipeline

Offline model, no devices touched. Extends Stage 59A (`docs/STAGE59A_ZERO_FALSE_POSITIVE_WISP_RF_OBSERVABILITY_AND_GUARIDA_PLAN.md`):
an anomaly is confirmed only after 2 consecutive AP-local rounds (5 probes each).

## Files

- Module: `tools/uisp/zero_false_positive_bilateral_observability_pipeline.py`
- Test: `tests/test_stage1202a_zero_fp_pipeline.py`
- Receipt: `artifacts/verification/stage1202a_zero_fp_bilateral_observability_pipeline.json`

## API

`run_pipeline(snapshot, graph=None)` returns `anomalies`, `aqm_feed_forward`, `pwo_cards`.
Snapshot: `{"rounds": [[signal, ...], ...]}`, oldest round first. A signal carries `site`
plus radio/PtP fields; `probes_positive` (default 5) must reach the quorum of 3 of 5.

## Classifications

| Class | Trigger | Backend |
| :--- | :--- | :--- |
| POP_WIDE_POWER_OR_SWITCH_EVENT | all PoP radios down, power/weather flag | `disambiguate` (1182A) |
| UPSTREAM_PTP_BACKHAUL_CONGESTION | PtP capacity drop 20% or more | `aqm_feed_forward` (1182A) |
| BILATERAL_COLLOCATED_CHANNEL_COLLISION | observed channel vetoed at either tower | `evaluate_channel_change` (1181A) |
| SINGLE_SECTOR_RF_INTERFERENCE | one sector degraded, peers healthy | `disambiguate` |
| SINGLE_CPE_ALIGNMENT_OR_FOLIAGE_DROP | one CPE only | rule |

## Zero-FP gate

The trailing streak of a (site, classification) pair must be 2 or more rounds at the last
round. A one-round blip or a gap (`[s], [], [s]`) stays `zero_fp_confirmed=False`
(candidate) and emits no AQM hint and no PWO card.

## Safety

Every card comes from `bridge_recommendation` (1183A): `auto_approve` false, width 20 MHz,
6 WirelessExperimentGates, data sources `ac2_devices` and NMS `/devices?siteId`.
The 1200A simulator is imported defensively; the receipt records `simulator_1200a_present`.

## Limits

Model only: thresholds (quorum 3, drop 20%) are placeholders until field data tunes them.
The topology comes from `DEFAULT_GRAPH` in 1181A; Edificio Principal is not in that graph.
