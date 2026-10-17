"""FuturaMAX Closed-Loop Production Daemon.

Stage 1 Stock-airOS & OpenWrt production supervisor that runs continuous
monitoring, analytical forecasting, RF advisories, dynamic bufferbloat pacing,
and canary trial rollback guards.

Integrated Architecture:
1. Telemetry Ingestion: Interfaces with AirOSLiveSSHPoller / OpenWrtLiveSSHPoller.
2. Capacity & Saturation Forecasting: Evaluates sector airtime against the 85% CSMA/CA cliff
   and identifies bottleneck CPEs causing airtime drag.
3. Station Link Auditing & RF Advisories: Audits chain imbalances, receiver desensitization,
   low SNR, and retries, generating actionable RF advisories.
4. Closed-Loop Pacing: Dynamically adapts host CAKE shaper bandwidth and throttles
   hardware A-MPDU aggregation depth (HTT Type 5) when loaded latency spikes.
5. Canary Trial Execution & Auto-Rollback: Stages configuration changes and automatically
   rolls back if p95 latency degrades > 20% or goodput drops > 10%.
6. Status Snapshot: Exposes structured JSON-serializable status for CLI dashboards and monitoring.
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import threading
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

from controller.advisory_mode import (
    AuditSeverity,
    CanaryManager,
    CanaryTrial,
    CPEAuditRecord,
    RFAdvisory,
    SectorAdvisor,
    calculate_jains_fairness,
)
from controller.capacity_forecasting import (
    DEFAULT_AIRTIME_CLIFF_PCT,
    CapacityForecastResult,
    SectorCapacityForecaster,
    SubscriberDemand,
)
from controller.pacing_controller import (
    PacingAction,
    PacingConfig,
    PacingController,
)

logger = logging.getLogger("futuramax.daemon")


@dataclass
class DaemonConfig:
    """Configuration for FuturaMAXDaemon."""

    sector_id: str = "sector-ap-01"
    radio_type: str = "airos"  # "airos" or "openwrt"
    host: str = "192.168.1.20"
    channel_freq_mhz: int = 5500
    channel_width_mhz: int = 20
    poll_interval_s: float = 2.0
    airtime_limit_pct: float = DEFAULT_AIRTIME_CLIFF_PCT
    canary_duration_ticks: int = 5
    dry_run: bool = True
    pacing_config: Optional[PacingConfig] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.pacing_config:
            d["pacing_config"] = self.pacing_config.to_dict()
        return d


@dataclass
class DaemonCycleReport:
    """Summary of a single closed-loop tick execution."""

    tick_index: int
    timestamp: str
    poller_connected: bool
    station_count: int
    airtime_demand_pct: float
    is_exhausted: bool
    bottlenecks_detected: int
    critical_stations_count: int
    actionable_advisories_count: int
    shaper_bandwidth_mbps: float
    pacing_throttled: bool
    canary_status: Optional[str]
    alerts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FuturaMAXDaemon:
    """Continuous Closed-Loop Sector Supervisor and Optimizer."""

    def __init__(
        self,
        config: Optional[DaemonConfig] = None,
        poller: Optional[Any] = None,
        capacity_forecaster: Optional[SectorCapacityForecaster] = None,
        sector_advisor: Optional[SectorAdvisor] = None,
        pacing_controller: Optional[PacingController] = None,
        canary_manager: Optional[CanaryManager] = None,
        rollback_hook: Optional[Callable[[str, Any], None]] = None,
    ):
        self.config = config or DaemonConfig()
        self.rollback_hook = rollback_hook

        # Initialize or assign poller
        self.poller = poller or self._init_poller()

        # Core intelligence engines
        self.capacity_forecaster = capacity_forecaster or SectorCapacityForecaster(
            default_bw_mhz=self.config.channel_width_mhz,
            airtime_limit_pct=self.config.airtime_limit_pct,
        )
        self.sector_advisor = sector_advisor or SectorAdvisor()

        p_cfg = self.config.pacing_config or PacingConfig(dry_run=self.config.dry_run)
        self.pacing_controller = pacing_controller or PacingController(config=p_cfg)

        self.canary_manager = canary_manager or CanaryManager(
            max_acceptable_goodput_drop_pct=-10.0,
            max_acceptable_latency_increase_pct=20.0,
            max_acceptable_fairness_drop=0.15,
        )

        # Internal state
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.start_time: Optional[float] = None

        self.cycle_count = 0
        self.last_snapshot: Optional[Any] = None
        self.last_forecast: Optional[CapacityForecastResult] = None
        self.last_advisory_report: Optional[Dict[str, Any]] = None
        self.last_pacing_action: Optional[PacingAction] = None
        self.last_cycle_report: Optional[DaemonCycleReport] = None

        # Canary trial state
        self.active_canary_trial: Optional[CanaryTrial] = None
        self.canary_trial_ticks = 0
        self.canary_trial_samples: List[Dict[str, Any]] = []
        self.completed_canary_trials: List[CanaryTrial] = []

        # System alerts
        self.alerts: List[str] = []

    def _init_poller(self) -> Any:
        """Instantiate appropriate telemetry poller based on radio_type."""
        if self.config.radio_type == "openwrt":
            from telemetry.openwrt.live_ssh_poller import OpenWrtLiveSSHPoller, OpenWrtPollerConfig

            return OpenWrtLiveSSHPoller(OpenWrtPollerConfig(host=self.config.host))
        else:
            from telemetry.airos.live_ssh_poller import AirOSLiveSSHPoller, AirOSPollerConfig

            return AirOSLiveSSHPoller(AirOSPollerConfig(host=self.config.host))

    def _extract_subscriber_demands(
        self,
        stations: Dict[str, Any],
    ) -> List[SubscriberDemand]:
        """Convert telemetry station records into SubscriberDemand objects."""
        demands: List[SubscriberDemand] = []
        for mac, s in stations.items():
            d = s.to_dict() if hasattr(s, "to_dict") else dict(s)
            cpe_id = d.get("device_name", d.get("cpe_id", mac))
            mcs = d.get("mcs") if d.get("mcs") is not None else 7
            nss = d.get("nss") if d.get("nss") is not None else 2
            bw = d.get("bandwidth_mhz") if d.get("bandwidth_mhz") is not None else self.config.channel_width_mhz
            short_gi = bool(d.get("short_gi", False))

            retries = float(d.get("tx_retries", 0) or 0)
            pkts = float(d.get("tx_packets", 0) or 0)
            retry_pct = (retries / pkts * 100.0) if pkts > 0 else float(d.get("retry_pct", 2.0) or 2.0)

            # Determine demand from explicit throughput metric or fall back to plan concurrency
            offered_load = None
            if d.get("offered_load_mbps") is not None:
                offered_load = float(d["offered_load_mbps"])
            elif d.get("expected_throughput_kbps"):
                offered_load = float(d["expected_throughput_kbps"]) / 1000.0

            demands.append(
                SubscriberDemand(
                    cpe_id=cpe_id,
                    plan_name="Standard_25M",
                    mcs=int(mcs),
                    nss=int(nss),
                    bandwidth_mhz=int(bw),
                    short_gi=short_gi,
                    retry_pct=round(retry_pct, 2),
                    offered_load_mbps=offered_load,
                    active=True,
                )
            )
        return demands

    def _extract_bufferbloat_metrics(
        self,
        snapshot: Any,
        forecast: CapacityForecastResult,
    ) -> Dict[str, Any]:
        """Extract or approximate bufferbloat loaded latency stats from telemetry."""
        summary = getattr(snapshot, "summary", None)
        if isinstance(summary, dict):
            p50 = float(summary.get("p50_latency_ms", summary.get("avg_latency_ms", 3.0)) or 3.0)
            p95 = float(summary.get("p95_latency_ms", summary.get("max_latency_ms", 8.0)) or 8.0)
            gp = float(summary.get("total_throughput_mbps", forecast.aggregate_goodput_mbps) or 50.0)
            loss = float(summary.get("packet_loss_pct", 0.0) or 0.0)
        elif hasattr(summary, "avg_latency_ms"):
            p50 = float(getattr(summary, "avg_latency_ms", 3.0) or 3.0)
            p95 = float(getattr(summary, "p95_latency_ms", p50 * 2.2) or (p50 * 2.2))
            gp = float(getattr(summary, "total_throughput_mbps", forecast.aggregate_goodput_mbps) or 50.0)
            loss = float(getattr(summary, "packet_loss_pct", 0.0) or 0.0)
        else:
            # Baseline estimation from sector airtime saturation
            base_lat = 2.0
            if forecast.is_exhausted:
                # Bufferbloat latency cliff when airtime > 85%
                excess = forecast.total_airtime_demand_pct - 85.0
                p50 = base_lat + excess * 0.5
                p95 = p50 * 3.5
            else:
                p50 = base_lat
                p95 = base_lat * 2.0
            gp = forecast.aggregate_goodput_mbps
            loss = 0.0

        return {
            "p50_ms": round(p50, 2),
            "p95_ms": round(p95, 2),
            "p99_ms": round(p95 * 1.5, 2),
            "bloat_p95_ms": round(max(0.0, p95 - p50), 2),
            "goodput_mbps": round(gp, 2),
            "loss_pct": round(loss, 2),
        }

    def _extract_spectral_data(self, snapshot: Any) -> Dict[int, Dict[str, Any]]:
        """Extract spectral scan frequency data if available in snapshot."""
        rep = getattr(snapshot, "spectral_report", None)
        if not rep:
            return {}

        d = rep.to_dict() if hasattr(rep, "to_dict") else dict(rep)
        freq = int(d.get("frequency_mhz", self.config.channel_freq_mhz))
        return {
            freq: {
                "noise_floor_dbm": d.get("noise_floor_dbm", -95.0),
                "peak_interference_dbm": d.get("peak_interference_dbm", -95.0),
                "channel_occupancy_pct": d.get("channel_occupancy_pct", 10.0),
                "dfs_radar_detected": d.get("dfs_radar_detected", False),
            }
        }

    def start_canary_trial(
        self,
        parameter_name: str,
        old_value: Any,
        new_value: Any,
        baseline_metrics: Optional[Dict[str, Any]] = None,
    ) -> CanaryTrial:
        """Stage and initiate a live canary configuration trial."""
        if baseline_metrics is None:
            # Construct baseline from latest tick
            gp = self.last_forecast.aggregate_goodput_mbps if self.last_forecast else 50.0
            lat = 10.0
            if self.last_cycle_report:
                lat = 15.0 if self.last_cycle_report.pacing_throttled else 8.0
            baseline_metrics = {
                "goodput_mbps": gp,
                "latency_p95_ms": lat,
                "resets": 0,
            }

        trial = self.canary_manager.stage_canary(
            parameter_name=parameter_name,
            old_value=old_value,
            new_value=new_value,
            before_metrics=baseline_metrics,
        )
        self.active_canary_trial = trial
        self.canary_trial_ticks = 0
        self.canary_trial_samples = []

        logger.info(
            "Staged canary trial %s for %s (%s -> %s)",
            trial.trial_id,
            parameter_name,
            old_value,
            new_value,
        )
        return trial

    def _process_active_canary_tick(
        self,
        forecast: CapacityForecastResult,
        bb: Dict[str, Any],
        stations: Dict[str, Any],
    ):
        """Sample performance during canary trial and trigger evaluation when duration ends."""
        if not self.active_canary_trial:
            return

        self.canary_trial_ticks += 1
        per_sta_gp = [
            float(getattr(s, "tx_rate_mbps", 0.0) or 10.0) for s in stations.values()
        ] or [bb["goodput_mbps"]]

        self.canary_trial_samples.append(
            {
                "goodput_mbps": bb["goodput_mbps"],
                "latency_p95_ms": bb["p95_ms"],
                "per_station_goodputs": per_sta_gp,
                "resets": 0,
            }
        )

        if self.canary_trial_ticks >= self.config.canary_duration_ticks:
            # Compute average after_metrics
            avg_gp = sum(s["goodput_mbps"] for s in self.canary_trial_samples) / len(self.canary_trial_samples)
            avg_lat = sum(s["latency_p95_ms"] for s in self.canary_trial_samples) / len(self.canary_trial_samples)
            after_metrics = {
                "goodput_mbps": round(avg_gp, 2),
                "latency_p95_ms": round(avg_lat, 2),
                "per_station_goodputs": per_sta_gp,
                "resets": 0,
            }

            trial = self.canary_manager.evaluate_canary(self.active_canary_trial, after_metrics)

            if trial.decision == "REVERT":
                alert_msg = (
                    f"CANARY ROLLBACK TRIGGERED on {trial.parameter_name}: {trial.decision_reason}. "
                    f"Reverting {trial.new_value} -> {trial.old_value}"
                )
                self.alerts.append(alert_msg)
                logger.warning(alert_msg)

                if self.rollback_hook:
                    try:
                        self.rollback_hook(trial.parameter_name, trial.old_value)
                    except Exception as e:
                        logger.error("Error executing rollback hook: %s", e)
            else:
                logger.info("CANARY ACCEPTED: %s", trial.decision_reason)

            self.completed_canary_trials.append(trial)
            self.active_canary_trial = None
            self.canary_trial_ticks = 0
            self.canary_trial_samples = []

    def tick(self) -> DaemonCycleReport:
        """Execute one complete closed-loop optimization cycle synchronously."""
        self.cycle_count += 1
        ts = dt.datetime.now(dt.timezone.utc).isoformat()
        cycle_alerts: List[str] = []

        # 1. Telemetry Ingestion
        if hasattr(self.poller, "poll_cycle"):
            snapshot = self.poller.poll_cycle()
        elif callable(self.poller):
            snapshot = self.poller()
        else:
            snapshot = self.poller

        self.last_snapshot = snapshot
        stations = getattr(snapshot, "stations", {})
        if isinstance(stations, list):
            stations = {getattr(s, "mac", f"sta-{i}"): s for i, s in enumerate(stations)}

        poller_state = getattr(snapshot, "connection_state", "CONNECTED")
        connected = "CONNECTED" in str(poller_state).upper()

        # 2. Capacity & Saturation Forecasting
        demands = self._extract_subscriber_demands(stations)
        forecast = self.capacity_forecaster.forecast_sector_capacity(demands)
        self.last_forecast = forecast

        if forecast.is_exhausted:
            alert = (
                f"Sector airtime exhaustion cliff exceeded: {forecast.total_airtime_demand_pct:.1f}% "
                f"(limit {self.config.airtime_limit_pct:.1f}%)"
            )
            cycle_alerts.append(alert)

        for b in forecast.bottlenecks:
            alert = f"Bottleneck CPE {b.cpe_id}: {b.diagnosis_reason} ({b.inefficiency_ratio:.1f}x drag)"
            cycle_alerts.append(alert)

        # 3. Station Link Auditing & RF Advisories
        spectral_data = self._extract_spectral_data(snapshot)
        advisory_rep = self.sector_advisor.generate_full_advisory_report(
            stations=stations,
            current_freq_mhz=self.config.channel_freq_mhz,
            current_width_mhz=self.config.channel_width_mhz,
            spectral_data=spectral_data,
        )
        self.last_advisory_report = advisory_rep

        if advisory_rep.get("critical_stations"):
            alert = f"Critical RF stations detected: {', '.join(advisory_rep['critical_stations'])}"
            cycle_alerts.append(alert)

        # 4. Closed-Loop Pacing
        bb_metrics = self._extract_bufferbloat_metrics(snapshot, forecast)
        pacing_action = self.pacing_controller.evaluate(stations, bb_metrics)
        self.last_pacing_action = pacing_action

        if pacing_action.is_throttled:
            cycle_alerts.append("Bufferbloat active: A-MPDU aggregation throttled to lower queue residency")

        # 5. Process Active Canary Trial (if staged)
        canary_status = self.active_canary_trial.status if self.active_canary_trial else None
        if self.active_canary_trial:
            self._process_active_canary_tick(forecast, bb_metrics, stations)

        # 6. Build Cycle Report
        report = DaemonCycleReport(
            tick_index=self.cycle_count,
            timestamp=ts,
            poller_connected=connected,
            station_count=len(stations),
            airtime_demand_pct=forecast.total_airtime_demand_pct,
            is_exhausted=forecast.is_exhausted,
            bottlenecks_detected=len(forecast.bottlenecks),
            critical_stations_count=len(advisory_rep.get("critical_stations", [])),
            actionable_advisories_count=advisory_rep.get("actionable_advisories_count", 0),
            shaper_bandwidth_mbps=pacing_action.shaper_bandwidth_mbps,
            pacing_throttled=pacing_action.is_throttled,
            canary_status=canary_status,
            alerts=cycle_alerts,
        )
        self.last_cycle_report = report

        # Keep alerts bounded in memory
        self.alerts.extend(cycle_alerts)
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

        return report

    def get_status_snapshot(self) -> Dict[str, Any]:
        """Expose structured state snapshot for CLI dashboards, monitoring, or API."""
        now = time.time()
        uptime = round(now - self.start_time, 1) if (self.start_time and self.running) else 0.0

        poller_state = "DISCONNECTED"
        if self.last_snapshot:
            poller_state = str(getattr(self.last_snapshot, "connection_state", "CONNECTED"))

        fc = self.last_forecast
        adv = self.last_advisory_report or {}
        pa = self.last_pacing_action

        # Format bottleneck CPE summaries
        bottleneck_summary = []
        if fc:
            for b in fc.bottlenecks:
                bottleneck_summary.append(
                    {
                        "cpe_id": b.cpe_id,
                        "drag_factor": b.inefficiency_ratio,
                        "airtime_pct": b.airtime_consumed_pct,
                        "reason": b.diagnosis_reason,
                    }
                )

        return {
            "sector_id": self.config.sector_id,
            "running": self.running,
            "uptime_seconds": uptime,
            "cycle_count": self.cycle_count,
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "radio_type": self.config.radio_type,
            "poller_state": poller_state,
            "channel_freq_mhz": self.config.channel_freq_mhz,
            "channel_width_mhz": self.config.channel_width_mhz,
            "station_count": fc.subscriber_count if fc else 0,
            "airtime_demand_pct": fc.total_airtime_demand_pct if fc else 0.0,
            "airtime_headroom_pct": fc.remaining_airtime_headroom_pct if fc else 100.0,
            "is_exhausted": fc.is_exhausted if fc else False,
            "potential_goodput_gain_mbps": fc.potential_goodput_gain_mbps if fc else 0.0,
            "bottlenecks": bottleneck_summary,
            "critical_stations": adv.get("critical_stations", []),
            "warning_stations": adv.get("warning_stations", []),
            "actionable_advisories_count": adv.get("actionable_advisories_count", 0),
            "top_advisories": adv.get("advisories", [])[:3],
            "pacing": {
                "shaper_bandwidth_mbps": pa.shaper_bandwidth_mbps if pa else 0.0,
                "is_throttled": pa.is_throttled if pa else False,
                "active_station_actions": len(pa.station_actions) if pa else 0,
            },
            "active_canary": self.active_canary_trial.to_dict() if self.active_canary_trial else None,
            "last_canary_decision": (
                self.completed_canary_trials[-1].to_dict() if self.completed_canary_trials else None
            ),
            "recent_alerts": self.alerts[-5:],
        }

    def start(self, background: bool = False):
        """Start daemon execution."""
        if self.running:
            return

        self.running = True
        self.start_time = time.time()
        self._stop_event.clear()

        if background:
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            logger.info("FuturaMAXDaemon started in background thread.")
        else:
            self._run_loop()

    def stop(self):
        """Stop daemon execution gracefully."""
        self.running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)
        logger.info("FuturaMAXDaemon stopped.")

    def _run_loop(self):
        """Internal daemon polling and optimization loop."""
        while not self._stop_event.is_set():
            try:
                self.tick()
            except Exception as e:
                logger.error("Exception during daemon tick: %s", e, exc_info=True)
                self.alerts.append(f"Daemon tick error: {e}")

            self._stop_event.wait(self.config.poll_interval_s)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="FuturaMAX Closed-Loop Optimization Daemon")
    parser.add_argument("--host", default="192.168.1.20", help="AP Management IP (default: 192.168.1.20)")
    parser.add_argument("--radio-type", choices=["airos", "openwrt"], default="airos", help="Radio OS type")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Poll interval in seconds (default: 2.0s)")
    parser.add_argument("--channel-width", type=int, default=20, choices=[20, 40, 80], help="Channel width in MHz")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Run without applying actual RF/qdisc mutations")
    parser.add_argument("--ticks", type=int, default=0, help="Run N ticks and exit (0 = run indefinitely)")
    parser.add_argument("--status-json", action="store_true", help="Print status snapshot as JSON on exit")

    args = parser.parse_args()

    cfg = DaemonConfig(
        host=args.host,
        radio_type=args.radio_type,
        poll_interval_s=args.poll_interval,
        channel_width_mhz=args.channel_width,
        dry_run=args.dry_run,
    )

    daemon = FuturaMAXDaemon(config=cfg)
    logger.info("Starting FuturaMAXDaemon (host=%s, radio=%s, interval=%.1fs, dry_run=%s)", cfg.host, cfg.radio_type, cfg.poll_interval_s, cfg.dry_run)

    if args.ticks > 0:
        for i in range(args.ticks):
            rep = daemon.tick()
            print(f"[Tick #{rep.tick_index}] Stations: {rep.station_count} | Airtime: {rep.airtime_demand_pct:.1f}% | Shaper: {rep.shaper_bandwidth_mbps:.1f} Mbps | Bottlenecks: {rep.bottlenecks_detected}")
            if i < args.ticks - 1:
                time.sleep(cfg.poll_interval_s)
    else:
        try:
            daemon.start(background=False)
        except KeyboardInterrupt:
            daemon.stop()

    if args.status_json:
        print(json.dumps(daemon.get_status_snapshot(), indent=2))


if __name__ == "__main__":
    main()
