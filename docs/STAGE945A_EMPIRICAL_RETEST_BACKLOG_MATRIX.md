<!-- doc-head: Stage 945A empirical retest backlog - receipts declared CONFIRMED but only SIMULATED_MODEL_ONLY/UNKNOWN; offline, no live evidence -->

# Stage 945A - Empirical Retest Backlog Matrix

- **Evidence class**: `RETEST_BACKLOG_MATRIX` (offline; `live_devices_touched=false`)
- **Sources**: `stage887a` per-receipt classes, `stage888a` integrity flags, the untested-variables roadmap
- **Receipt**: `artifacts/autoresearch/stage945a_empirical_retest_backlog_matrix.json`
- **Builder**: `tools/verify/build_stage945a_empirical_retest_backlog_matrix.py`

## Provenance classes (kept separate)

| Class | Meaning here |
| :--- | :--- |
| CONFIRMED_LIVE_HARDWARE | physical bench capture with hardware attribution; not in this backlog |
| CONFIRMED_STATIC_BINARY | byte/container-level analysis; runtime execution still untested; not in this backlog |
| SIMULATED_MODEL_ONLY | model/simulation output; must never be cited as live |
| UNKNOWN | no provenance signal; needs an A10 fiche before any live citation |

## Backlog size

- **backlog_total**: `338` (matches 888A `declared_confirmed_but_not_physically_confirmed_count=338`)
- SIMULATED_MODEL_ONLY declared CONFIRMED: `40` (888A: `40`)
- UNKNOWN declared CONFIRMED: `298`
- Also on the roadmap: `123`
- Rows stored in JSON: `200` (cap `200`)

## Highest-priority rows

Priority: simulated-but-CONFIRMED first, then roadmap overlap, then the rest.

| Receipt | Class | Roadmap tags | Suggested measurement |
| :--- | :--- | :--- | :--- |
| `stage653a_pb040_pb050_pb060_triple_patch_pareto.json` | SIMULATED_MODEL_ONLY | PB-40, PB-60 | replay the Pareto knee point on a bench pair; compare to the model prediction |
| `stage447a_wmi_0x9044_50us_hardware_retry_pareto.json` | SIMULATED_MODEL_ONLY | kw:wmi | per-peer retry/rate readback (debugfs) under A/B load, counters diffed |
| `stage515a_ltu_dcxo_gps_vs_tcxo_4096qam_cfo_pareto.json` | SIMULATED_MODEL_ONLY | kw:ltu | A/B/A/B OTA iperf3 + p95 RTT on a matched LTU pair, 3 repeats |
| `stage656a_nsga3_pareto_pb060_txop_tid_sched_and_vht40.json` | SIMULATED_MODEL_ONLY | PB-60 | replay the Pareto knee point on a bench pair; compare to the model prediction |
| `stage658a_guarida_32cpe_pb060_voip_iptv_bulk_sim.json` | SIMULATED_MODEL_ONLY | PB-60 | A10 provenance fiche: raw capture hashes, extractor, readback, baseline; then one A/B/A/B bench run |
| `stage663a_guarida_tower_v6_pb060_and_amsdu_7935b_pareto.json` | SIMULATED_MODEL_ONLY | PB-60 | replay the Pareto knee point on a bench pair; compare to the model prediction |
| `stage690a_ptp_vht40_vs_vht80_near_field_isi_sim.json` | SIMULATED_MODEL_ONLY | kw:ptp | single-link iperf3 goodput + p95 RTT, A/B/A/B, 3 repeats |
| `stage724a_ptmp_mixed_openwrt_vs_airos8_amsdu_airtime_sim.json` | SIMULATED_MODEL_ONLY | kw:ptmp | multi-CPE sector goodput + Jain fairness, A/B/A/B |
| `stage837a_simpy_ptp_vht40_vs_vht80_thermal_and_rain_fade_model.json` | SIMULATED_MODEL_ONLY | kw:ptp | single-link iperf3 goodput + p95 RTT, A/B/A/B, 3 repeats |
| `stage442a_ground_up_5pillars_combined_pareto.json` | SIMULATED_MODEL_ONLY | - | replay the Pareto knee point on a bench pair; compare to the model prediction |

## Rules

- A row leaves the backlog only after a bench retest with raw hashes, extractor, readback and baseline.
- Roadmap tags are filename-based matches (stage id, PB id, keyword); they are hints, not proof of coverage.
- Suggested measurements are keyword-derived defaults; the owning author refines them.
- Nothing here changes any receipt; 887A/888A remain the source of truth.
