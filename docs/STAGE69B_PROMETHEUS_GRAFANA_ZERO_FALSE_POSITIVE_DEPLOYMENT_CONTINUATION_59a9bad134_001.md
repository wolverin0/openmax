<!-- doc-head: STAGE69B_PROMETHEUS_GRAFANA_ZERO_FALSE_POSITIVE_DEPLOYMENT.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

[Document router](STAGE69B_PROMETHEUS_GRAFANA_ZERO_FALSE_POSITIVE_DEPLOYMENT.md) | Part 1/2
<a id="validation-and-acceptance"></a> [Validation and acceptance](STAGE69B_PROMETHEUS_GRAFANA_ZERO_FALSE_POSITIVE_DEPLOYMENT_CONTINUATION_59a9bad134_002.md#validation-and-acceptance)

<!-- stage822a-payload-begin -->

Extends the existing Python telemetry pipeline; all device access stays in an authorized producer.
Fresh AP-local peer evidence gates RF verdicts, Champion v20/v6/XW MCS0 checks, and LTU-BUG-01..08 alerts.
Artifacts are prepared for the existing PUBLIC_TERM_0003 and NAS services, without deployment.


# Stage69B / Stage77C Prometheus / Grafana RF integration

Task: `T-S69B-HOMELAB-PROMETHEUS-GRAFANA-ZERO-FALSE-POSITIVE-EXPORTER-AND-RULES` / `T-S77C-PROMETHEUS-OPENMETRICS-EXPORTER-AND-GRAFANA-ZERO-FALSE-POSITIVE-SUITE`.
Parent: reproducible control-authority/observability work in [BENCH_PLAN](BENCH_PLAN.md).
Authority: [Stage59A](STAGE59A_ZERO_FALSE_POSITIVE_WISP_RF_OBSERVABILITY_AND_GUARIDA_PLAN.md)
and the [Stage61A producer](../tools/telemetry/run_stage61a_unified_multigen_deterministic_rf_collector.py).
Behavior belongs to the **external controller**; hardware/firmware claims remain unqualified.

## Target services and boundary

Use the operator's endpoints, overriding historical `.160`/`.206` references:

| Existing service | Requested endpoint | Integration |
| --- | --- | --- |
| PUBLIC_TERM_0003 Prometheus | `http://198.18.0.149:9090` | One additional scrape job and rule file |
| PUBLIC_TERM_0003 Grafana | `http://198.18.0.149:3400` | Import dashboard into existing datasource |
| NAS Uptime Kuma | `http://198.18.0.150:3001` | Dashboard link and qualified heartbeat permission metric |

These endpoints are configuration targets, **not live-verified deployments**.
No second Prometheus/Grafana, SSH, radio polling, credentials, configuration writes,
Kuma notification or automatic repair is performed by this exporter.
The previous collector imports SSH/vault/autopilot code; this service never imports it.

## Input and producer contract

The [exporter](../tools/telemetry/fmx_prometheus_exporter.py) reads an operator-owned
local JSON file. Its separately authorized producer writes a temporary sibling,
fsyncs it and atomically replaces the snapshot after a complete collection.
Collect on the AP, with **five AP-to-peer probes per round**, normally every60s;
do not central-ping CPEs through Core `.200`.
Retain the actual boot identity, station counters and measurement timestamp.
Producer ownership and OS file permissions establish trust; scope labels are declarations,
not cryptographic authentication of a radio, RF path or boot epoch.

Minimal schema (one observation per inventory link; sample values are a fixture):

```json
{
  "schema_version": 1,
  "observations": [{
    "link": "sector1-peer1", "generation": "openwrt_wa", "ap": "panel1",
    "peer_mac": "02:00:00:00:00:01", "boot_id": "actual-producer-read-boot-id",
    "timestamp_s": 1793000000, "probe_seq": 1,
    "survey_active_time_ms": 1000, "tx_packets": 100, "rx_packets": 200,
    "icmp_sent": 5, "icmp_rcvd": 5, "l2_associated": true,
    "probe_scope": "ap_local", "l2_scope": "station",
    "signal_dbm": -55, "chain0_dbm": -54, "chain1_dbm": -56,
    "avg_rtt_ms": 3.5
  }]
}
```

Generation values: `openwrt_wa`, `airos8_wa`, `airos8_xc`, `airos6_xw`, `ltu`.
For OpenWrt use the AP station/survey counters; for airOS8 WA/XC and airOS6 XW
normalize real peer `wstalist`/equivalent counters, not shared-interface totals.
For LTU, an advancing device uptime/boot source may supply the freshness counter,
but L2 packet progress must refer to the monitored peer, not unrelated Ethernet traffic.
Preserve a missing read as missing; never fill in healthy RSSI, RTT, queue or modulation defaults.

Stage61A `stage: "61A"` / `round1` / `round2` saved receipts are accepted by a pure adapter.
They lack explicit boot/scope provenance and remain UNKNOWN/unqualified even if dated now.
Hardcoded R2AC/LTU RSSI and ambiguous legacy `maxBD` values are excluded.
Legacy `live_2round_evaluations`, synthetic self-tests and embedded metric text are not trusted.
Stage61A does **not** yet produce every extended LTU field: missing bug evidence stays unavailable.
An independently authorized producer must supply the extended schema before production activation.

## Verdict and freshness contract

| State | Value | Meaning |
| --- | --- | --- |
| UP | 1 | Replies, or associated peer with positive station packet progress |
| PENDING | 0 | First complete failed round; no outage yet |
| DOWN | -1 | Two consecutive qualified failed rounds, both0/5 and no L2 progress |
| UNKNOWN | -2 | No baseline, stale/future/malformed input, missing link or unqualified counters |

The first observation establishes a baseline and never reports UP.
Sequence must increase exactly by1, both packet counters must be nondecreasing,
and hardware freshness must advance within the same identity/boot epoch.
Round spacing must be45..90s; observation age must be0..150s.
Restart, sequence gaps, reset, replay/freeze and read failures break the failure streak.
Repeated scrapes/file polls do not create rounds. Recovery establishes a new baseline.
Input is validated as a complete batch; an invalid member invalidates the snapshot.
Inventory can be fixed with repeated `--expected-link` arguments; omitted known links stay UNKNOWN.

`fmx_rf_kuma_push_allowed=1` is emitted only for fresh qualified UP.
No HTTP push to Kuma is implemented; a separate integration must respect this permission
and give UNKNOWN/no heartbeat its own monitoring-blindness treatment.
The freshness recording rule and exporter enforce150s independently.
The design suppresses specific false positives; **zero false positives is not a universal guarantee**.
The Stage59A `p^10` model assumes independent packet losses; burst loss violates that assumption.

## Extended LTU evidence

Place these optional fields inside each LTU observation's `ltu` object:

| Bug | Required diagnostic fields | Condition (still requires degraded service) |
| --- | --- | --- |
| LTU-BUG-01 | `irq63_cpu0_total`, `irq63_cpu1_total` in consecutive same-boot samples | CPU0 advances while CPU1 does not |
| LTU-BUG-02 | `bd_handle_once`, `loaded_stalls_observed` | Write-side RX drain budget is0 with explicit loaded stalls |
| LTU-BUG-03 | `auto_mcs_write_attempted`, `auto_mcs_oops_observed` | Attempt and explicit relevant Oops |
| LTU-BUG-04 | `expect_4096_qam`, `auto_mcs_ceiling`, `sched_mcs_ceiling_qam` | Expected4096, auto31, actual scheduler ceiling below4096 |
| LTU-BUG-05 | `rx_target_power_dbm`, `rx_target_power_expected_dbm`, `ulpwr_enabled`, `uplink_degraded` | Target at least20dB above expected with autogain enabled and degraded UL |
| LTU-BUG-06 | `pb_boost_expected`, `pb_boost_mode`, `pb_boost_gain_index` | Expected boost, mode1, gain index0 |
| LTU-BUG-07 | `ini_rx_target_pwr`, `ini_parse_error` | Negative encoded INI value and explicit parse error |
| LTU-BUG-08 | `shaping_expected`, `htb_active`, `cls_u32_loaded`, `under_load` | Expected shaping under explicit load with HTB or u32 missing |

Also provide `gmax_bd_ever` (integer or explicit `"0xa"` hex), `loaded_rtt_ms`,
and `loaded_loss_ratio` (0..1). Boolean fields must be JSON booleans.
`gMaxBDEver` is a **read/reset high-water gauge**, not a drain setting or cumulative counter.
Do not introduce an additional maxBD read in the HTTP path: it changes the measurement epoch.
Do not write maxBD, IRQ affinity, autogain, MCS, modules or shaping from monitoring.
A 4096-QAM ceiling is not proof of instantaneous4096-QAM transmission.
The valid negative live target in dBm is distinct from unsigned INI tenths encoding.
Bug evidence availability is explicit; absent evidence never becomes a healthy zero.
Alerts require fresh evidence, a matching diagnostic and either confirmed link degradation,
loaded RTT above50ms or loaded loss above1%; they identify candidates, not causal proof.

## Stage 77C multi-generation Champion v20, PtP v6 and XW MCS0 evidence

- **OpenWrt `WA` (`openwrt_v20`, Stage 72A Champion v20)**: Optional `openwrt_v20` dict (`bql_limit_min=4542`, `bql_limit_max=42392`, `bql_hold_time_ms=800`, `dev_weight_tx_bias=2`, `fq_quantum=1514|4542`, `fq_memory_limit=4194304`, `hostapd_oom_score_adj=-900`, `aql_threshold=5000`, `tsq_limit_bytes=98304`, `tx_queue_len=256`) emits `fmx_openwrt_v20_evidence_available` and `fmx_openwrt_v20_profile_compliant` (`FMXOpenWrtChampionV20Drift`).
- **airOS 8 `XC/WA` (`airos8_v6`, Stage 73A PtP Champion v6)**: Optional `airos8_v6` dict (`ptp_xmit=1`, `daprot=2`, `ff_mcast_airtime_limit=5`, `daprot_written_before_ff_mcast=true` per `FMX-DISC-11`/`FMX-DISC-20`, `cabq_maxdur=20`, `syncflex=0`, `netdev_budget=800`, `tsq_limit_bytes=98304|131072`, `set_multiq=1`, `enable_tx_tcp_cksum=1`) emits `fmx_airos8_v6_evidence_available` and `fmx_airos8_v6_ptp_profile_compliant` (`FMXAirOS8PtPChampionV6Drift`).
- **airOS 6 `XW` (`airos6_xw`, `FMX-DISC-18` `MCS0` warmup detector)**: Optional `airos6_xw` dict (`tx_phy_mbps`, `expected_min_tx_phy_mbps=26.0`, `warmup_completed`, `under_load`, `netdev_budget=300`, `txqueuelen=256`) emits `fmx_xw_mcs0_warmup_evidence_available` and `fmx_xw_mcs0_cold_rate_condition` (`FMXAirOS6XWMCS0ColdRate`).

## Staging on the existing stack

Run only after the authorized producer and host service owner are ready:

```sh
python3 tools/telemetry/fmx_prometheus_exporter.py \
  --input /var/lib/futuramax/rf.json --host 198.18.0.149 --port 9118 \
  --expected-link sector1-peer1
```

Run it as an unprivileged supervised service, read-only access to the producer directory,
private management-network ingress only. HTTP has no built-in authentication/TLS;
use existing host firewall/reverse proxy controls. Keep credentials out of labels/files.
`/healthz` is process liveness; `/readyz` returns503 until every known link is qualified UP.
`/metrics` remains200 with explicit unknown/invalid state. Readiness is not scrape availability.
Negotiation supports Prometheus0.0.4 and OpenMetrics1.0.0 with UTF-8 and `# EOF`.
`--once` emits local exposition without opening a listener.

Add to the **existing** Prometheus configuration (merge with existing keys):

<!-- stage822a-payload-end -->
