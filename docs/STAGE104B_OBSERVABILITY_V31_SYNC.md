<!-- doc-head: Stage 104B Prometheus/OpenMetrics & Grafana Zero-False-Positive Suite v31 Sync (Stages 102D, 102E, 103A, 103D, 103E, 103F; kept <180 lines) -->
Synchronizes Prometheus/OpenMetrics exporter, Zero-False-Positive alerts, and Grafana RF Command Center dashboard (`v31`, 53 panels) with Stages `102D..103F`.
Every metric and alert rule is anchored to live-bench counterbalanced `A1 -> B1 -> A2 -> B2` artifacts.
<!-- /doc-head -->

# Stage 104B — Observability v31 Synchronization (`T-S104B-OBSERVABILITY-V31-S102D-CSA-S102E-LTU-TAIL-GUARD-SYNC`)

- **Claim Status**: `CONFIRMED`
- **Attribution**: `external controller`, `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`
- **Canonical Paths**:
  - Exporter: [`tools/telemetry/fmx_prometheus_exporter.py`](../tools/telemetry/fmx_prometheus_exporter.py) & [`tools/observability/fmx_prometheus_exporter.py`](../tools/observability/fmx_prometheus_exporter.py)
  - Alerts: [`deploy/observability/prometheus_fmx_alerts.yml`](../deploy/observability/prometheus_fmx_alerts.yml) & [`tools/observability/prometheus_fmx_alerts.yml`](../tools/observability/prometheus_fmx_alerts.yml)
  - Dashboard (`v31`, `53` panels): [`deploy/observability/grafana_fmx_rf_command_center_dashboard.json`](../deploy/observability/grafana_fmx_rf_command_center_dashboard.json) & [`tools/observability/grafana_fmx_rf_command_center_dashboard.json`](../tools/observability/grafana_fmx_rf_command_center_dashboard.json)
  - Verifier & Receipt: [`tools/verify/verify_stage104b_observability_v31_sync.py`](../tools/verify/verify_stage104b_observability_v31_sync.py) · [`artifacts/autoresearch/stage104b_observability_v31_sync.json`](../artifacts/autoresearch/stage104b_observability_v31_sync.json)

---

## 1. Synchronized Bench Evidence (`Stages 102D..103F`)

| Stage | Hardware / Scope | Champion Knobs & Telemetry Invariants | Empirical Bench Anchor (`A1 -> B1 -> A2 -> B2`) |
| :--- | :--- | :--- | :--- |
| **`Stage 102D`** | `OpenWrt WA` (`ap-lbe-112`) + `MK1-251` Boca 7 VLAN `107` | IEEE 802.11h `chan_switch` (`bcn_count=5`, `block_tx=0`, `3/3` station retention across `5200 <-> 5180 MHz`) | `CONFIRMED`: `-37.94%` `WA -> MK1` loaded `p95` RTT (`25.188 -> 15.631 ms`), `-71.88%` RTT jitter (`4.687 -> 1.318 ms`), `0.0%` loss |
| **`Stage 102E` / `103F`** | `AF-LTU` (`LTU-Rocket` `.151` <-> `LTU-Lite` `.152` + `LTU-Lite-2` `.250`) | `sched_mcs_limit_symbol_end=59`, `sched_max_agg_cnt=8`, `multi_ack_enable=1`, `LDPC iteration=12`, `ofdma_subbands_mask=0xff`, `netdev_budget=640`, `dev_weight=80`, `tcp_limit_output_bytes=196608` | `CONFIRMED`: `-50.28%` IPTV jitter (`0.891 -> 0.443 ms` in `S102E`) and `-57.96%` (`0.685 -> 0.288 ms` in `S103F`), `-7.23%` `gmac0` loaded `p95` RTT (`7.443 -> 6.905 ms`) |
| **`Stage 103A`** | `OpenWrt WA` + `airOS 8 WA/XC` (`ubnt_poll_host.ko`) | `uph_wifi0`: `swr_limit=2`, `ff_mcast_airtime_limit=10`, `sta_priority_enabled=1`, `ptp_xmit=1`, `noack_mode=0`, `set_multiq=1` (`FMX-DISC-34`) | `CONFIRMED`: `-41.93%` `WA -> MK1` loaded `p95` RTT (`15.729 -> 9.134 ms`), `-52.45%` RTT jitter (`3.142 -> 1.494 ms`) |
| **`Stage 103D`** | `OpenWrt WA` (`192.168.1.112`) <-> `MK1-251` RFC 2544 (`64B`/`512B`/`1518B`) | `CAKE diffserv4` (`4` active tins: Bulk/BestEffort/Video/Voice) + `overhead 28 mpu 64 nat` (`FMX-DISC-35`) | `CONFIRMED`: `-27.27%` `64B` loaded `p99` RTT (`33.0 -> 24.0 ms`), `-58.59%` `64B` VoIP jitter (`3.671 -> 1.520 ms`), `116.588 Mbps` (`1518B` sector goodput) |
| **`Stage 103E`** | `PowerBeam 5AC Gen2` (`.241 <-> .242`) -> `MK1-251` E2E | `ebtables` L2 whitelist (`192.168.1.251`) + `set_multiq=1` + `ptp_xmit=1` (`FMX-DISC-36`) | `CONFIRMED`: `-37.90%` `.242 -> MK1` loaded `p50` RTT (`8.175 -> 5.077 ms`), `-19.86%` loaded `p95` RTT (`18.149 -> 14.544 ms`), `-14.37%` VoIP jitter (`0.286 -> 0.245 ms`) |
| **`Stage 103F`** | `Rocket 2AC Prism` (`2XC` `.129`, Boca 8) PtMP MultiQ | `swr_limit=2`, `ptp_xmit=1`, `ff_cap_rep=2`, `umac max_peers=32`, `umac vow_config=1`, `set_multiq=3`, `cabq_maxdur=5` (`FMX-DISC-37`) | `CONFIRMED`: `257.571 Mbps` median / `263.295 Mbps` peak TCP + `18.798 Mbps` UDP, `-25.11%` loaded `p95` RTT (`8.489 -> 6.357 ms`), `-26.00%` loaded `p99` RTT (`10.038 -> 7.428 ms`) |

---

## 2. Exported OpenMetrics Families (`v31`)

1. **`stage102d_csa` (`openwrt_wa`)**:
   - `fmx_s102d_csa_evidence_available`, `fmx_s102d_csa_bcn_count`, `fmx_s102d_csa_block_tx`, `fmx_s102d_csa_station_retention_count`, `fmx_s102d_csa_wa_mk1_p95_rtt_ms`, `fmx_s102d_csa_wa_mk1_jitter_ms`, `fmx_s102d_csa_sector_goodput_mbps`, `fmx_s102d_csa_profile_compliant`.
2. **`stage102e_ltu_tail_guard` (`ltu`)**:
   - `fmx_s102e_ltu_tail_guard_evidence_available`, `fmx_s102e_ltu_sched_mcs_limit_symbol_end`, `fmx_s102e_ltu_sched_max_agg_cnt`, `fmx_s102e_ltu_multi_ack_enable`, `fmx_s102e_ltu_ldpc_iteration`, `fmx_s102e_ltu_ofdma_subbands_mask`, `fmx_s102e_ltu_netdev_budget`, `fmx_s102e_ltu_dev_weight`, `fmx_s102e_ltu_tcp_limit_output_bytes`, `fmx_s102e_ltu_iptv_jitter_ms`, `fmx_s102e_ltu_gmac0_p95_rtt_ms`, `fmx_s102e_ltu_lite2_ota_sync_staged`, `fmx_s102e_ltu_tail_guard_compliant`.
3. **`stage103a_uph_knobs` (`openwrt_wa`, `airos8_wa`, `airos8_xc`)**:
   - `fmx_s103a_uph_evidence_available`, `fmx_s103a_uph_swr_limit`, `fmx_s103a_uph_ff_mcast_airtime_limit`, `fmx_s103a_uph_sta_priority_enabled`, `fmx_s103a_uph_ptp_xmit`, `fmx_s103a_uph_noack_mode`, `fmx_s103a_uph_set_multiq`, `fmx_s103a_uph_wa_loaded_p95_rtt_ms`, `fmx_s103a_uph_wa_rtt_jitter_ms`, `fmx_s103a_uph_profile_compliant`.
4. **`stage103d_diffserv4_rfc2544` (`openwrt_wa`)**:
   - `fmx_s103d_diffserv4_evidence_available`, `fmx_s103d_diffserv4_tins_active`, `fmx_s103d_diffserv4_overhead_bytes`, `fmx_s103d_diffserv4_mpu_bytes`, `fmx_s103d_wa_mk1_64b_p50_rtt_ms`, `fmx_s103d_wa_mk1_64b_p99_rtt_ms`, `fmx_s103d_voip_64b_jitter_ms`, `fmx_s103d_sector_goodput_mbps`, `fmx_s103d_diffserv4_compliant`.
5. **`stage103e_pbe5ac_mk1_e2e` (`airos8_wa`, `openwrt_wa`)**:
   - `fmx_s103e_pbe_mk1_evidence_available`, `fmx_s103e_pbe_mk1_l2_whitelisted`, `fmx_s103e_pbe_mk1_set_multiq`, `fmx_s103e_pbe_mk1_ptp_xmit`, `fmx_s103e_pbe242_mk1_p50_rtt_ms`, `fmx_s103e_pbe242_mk1_p95_rtt_ms`, `fmx_s103e_pbe_mk1_voip_jitter_ms`, `fmx_s103e_mk1_btest_p95_ms`, `fmx_s103e_pbe_mk1_e2e_compliant`.
6. **`stage103f_r2ac_2xc_multiq` (`airos8_xc`)**:
   - `fmx_s103f_2xc_evidence_available`, `fmx_s103f_2xc_swr_limit`, `fmx_s103f_2xc_ptp_xmit`, `fmx_s103f_2xc_ff_cap_rep`, `fmx_s103f_2xc_umac_max_peers`, `fmx_s103f_2xc_umac_vow_config`, `fmx_s103f_2xc_set_multiq`, `fmx_s103f_2xc_cabq_maxdur`, `fmx_s103f_2xc_soc_bulk_tcp_mbps`, `fmx_s103f_2xc_loaded_p95_rtt_ms`, `fmx_s103f_2xc_multiq_compliant`.

---

## 3. Zero-False-Positive Alerts & Grafana Panels (`48..53`)

- **Alert Rules Added**:
  - `FMXStage102DVLAN107CSADrift`: Fires only when `fmx_s102d_csa_evidence_available == 1` and CSA parameters (`bcn_count < 5`, `block_tx != 0`, `station_retention < 3`) or loaded `p95` RTT (`> 22.0 ms`) drift.
  - `FMXStage102ELTUSuperframeTailGuardDrift`: Fires only when `fmx_s102e_ltu_tail_guard_evidence_available == 1` and `sched_mcs_limit_symbol_end != 59`, `sched_max_agg_cnt > 8`, `multi_ack_enable != 1`, `ldpc_iteration < 10`, or `netdev_budget < 640`.
  - `FMXStage103AWAXCUPHKnobsDrift`: Fires only when `fmx_s103a_uph_evidence_available == 1` and `swr_limit`, `ff_mcast_airtime_limit`, `sta_priority_enabled`, `ptp_xmit`, or `set_multiq` drift.
  - `FMXStage103DDiffServ4RFC2544Degraded`: Fires only when `fmx_s103d_diffserv4_evidence_available == 1` and `diffserv4_tins_active < 4`, `overhead_bytes != 28`, `mpu_bytes != 64`, or `64B` loaded `p99` RTT `> 30.0 ms`.
  - `FMXStage103EPBE5ACToMK1E2EDegraded`: Fires only when `fmx_s103e_pbe_mk1_evidence_available == 1` and L2 whitelist, `set_multiq`, `ptp_xmit`, or `.242 -> MK1` loaded `p95` RTT (`> 18.0 ms`) degrade.
  - `FMXStage103FR2AC2XCMultiQDrift`: Fires only when `fmx_s103f_2xc_evidence_available == 1` and `set_multiq < 3`, `swr_limit != 2`, `ff_cap_rep != 2`, `umac_vow_config != 1`, or loaded `p95` RTT `> 8.0 ms`.
- **Grafana Panels (`v31`, `53` total panels)**:
  - Panel `48`: Stage 102D — OpenWrt WA Channel Switch Announcement (`CSA 802.11h`)
  - Panel `49`: Stage 102E/103F — AF-LTU 80-Symbol `2.0 ms` Superframe Tail Guard (`symbol_end=59`, `LDPC=12`)
  - Panel `50`: Stage 103A — WA/XC `ubnt_poll_host.ko` (`uph_wifi0`) Knobs (`swr_limit=2`, `ff_mcast=10`, `sta_priority=1`)
  - Panel `51`: Stage 103D — OpenWrt WA `CAKE diffserv4` RFC 2544 Frame-Size Soak (`64B`/`512B`/`1518B`)
  - Panel `52`: Stage 103E — PowerBeam 5AC Gen2 (`.241 <-> .242`) -> `MK1-251` L2-to-L3 E2E Data Plane
  - Panel `53`: Stage 103F — Rocket 2AC Prism (`2XC` `.129` Boca 8) PtMP MultiQ (`set_multiq=3`, `swr_limit=2`)
