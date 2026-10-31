<!-- doc-head: STAGE69B_PROMETHEUS_GRAFANA_ZERO_FALSE_POSITIVE_DEPLOYMENT.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

[Document router](STAGE69B_PROMETHEUS_GRAFANA_ZERO_FALSE_POSITIVE_DEPLOYMENT.md) | Part 2/2
<a id="stage69b--stage77c-prometheus--grafana-rf-integration"></a> [Stage69B / Stage77C Prometheus / Grafana RF integration](STAGE69B_PROMETHEUS_GRAFANA_ZERO_FALSE_POSITIVE_DEPLOYMENT_CONTINUATION_59a9bad134_001.md#stage69b--stage77c-prometheus--grafana-rf-integration) | <a id="target-services-and-boundary"></a> [Target services and boundary](STAGE69B_PROMETHEUS_GRAFANA_ZERO_FALSE_POSITIVE_DEPLOYMENT_CONTINUATION_59a9bad134_001.md#target-services-and-boundary) | <a id="input-and-producer-contract"></a> [Input and producer contract](STAGE69B_PROMETHEUS_GRAFANA_ZERO_FALSE_POSITIVE_DEPLOYMENT_CONTINUATION_59a9bad134_001.md#input-and-producer-contract) | <a id="verdict-and-freshness-contract"></a> [Verdict and freshness contract](STAGE69B_PROMETHEUS_GRAFANA_ZERO_FALSE_POSITIVE_DEPLOYMENT_CONTINUATION_59a9bad134_001.md#verdict-and-freshness-contract) | <a id="extended-ltu-evidence"></a> [Extended LTU evidence](STAGE69B_PROMETHEUS_GRAFANA_ZERO_FALSE_POSITIVE_DEPLOYMENT_CONTINUATION_59a9bad134_001.md#extended-ltu-evidence) | <a id="stage-77c-multi-generation-champion-v20-ptp-v6-and-xw-mcs0-evidence"></a> [Stage 77C multi-generation Champion v20, PtP v6 and XW MCS0 evidence](STAGE69B_PROMETHEUS_GRAFANA_ZERO_FALSE_POSITIVE_DEPLOYMENT_CONTINUATION_59a9bad134_001.md#stage-77c-multi-generation-champion-v20-ptp-v6-and-xw-mcs0-evidence) | <a id="staging-on-the-existing-stack"></a> [Staging on the existing stack](STAGE69B_PROMETHEUS_GRAFANA_ZERO_FALSE_POSITIVE_DEPLOYMENT_CONTINUATION_59a9bad134_001.md#staging-on-the-existing-stack)

<!-- stage822a-payload-begin -->
```yaml
rule_files:
  - /etc/prometheus/rules/prometheus_fmx_alerts.yml
scrape_configs:
  - job_name: futuramax_rf
    scrape_interval: 30s
    scrape_timeout: 5s
    static_configs:
      - targets: ['198.18.0.149:9118']
```

Mount [rules](../deploy/observability/prometheus_fmx_alerts.yml) read-only.
Validate the complete host configuration and rule file with its matching `promtool`
before a controlled reload; retain the previous config and rule file for rollback.
Import [dashboard JSON](../deploy/observability/grafana_fmx_rf_command_center_dashboard.json)
into existing Grafana; select its Prometheus datasource. UID is `fmx-rf-command-center`.
Export an existing dashboard with that UID before replacement, or choose a new UID.
Dashboard filters preserve exporter instance, hardware generation, AP and link.
Existing Alertmanager notification routing is not modified by this package.

## Validation and acceptance

```sh
python -m pytest -q -o addopts= tests/test_stage69b_prometheus_grafana_observability.py
promtool check rules deploy/observability/prometheus_fmx_alerts.yml
```

Local tests use synthetic evidence and disposable loopback HTTP, with no radio/native collector.
Promtool semantic tests exercise positive firing, healthy suppression, stale/future evidence,
missing diagnostics, peer isolation and all eight bug predicates.
Exact executed results, source hashes and independent review are recorded in
[Stage69B validation](../artifacts/verification/stage69b_validation_20261026.json).
Production delivery still needs authorized producer activation, actual host scrape/rule health,
dashboard import/rendering and receiver acceptance. No such live acceptance is claimed here.

References: [Prometheus negotiation](https://prometheus.io/docs/instrumenting/content_negotiation/),
[rule testing](https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/),
[OpenMetrics specification](https://github.com/prometheus/OpenMetrics/blob/main/specification/OpenMetrics.md).
<!-- stage822a-payload-end -->
