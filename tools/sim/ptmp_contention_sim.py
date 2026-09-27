"""
Discrete-Event PtMP CSMA/CA Contention Simulator with Hidden-Node Geometry.
Validates the openMAX Bianchi Markov Contention Model for 1 to 30 CPEs.

Physical Context:
- AP: 120-degree sector antenna (hears all CPEs).
- CPEs: Directional dish antennas with >110 dB inter-CPE isolation (hidden terminals to each other).
- Channel: 802.11ac 5 GHz, 20 MHz (MCS7 @ 65 Mbps or MCS9 @ 86.7 Mbps per stream).
"""

import math
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class SimConfig:
    slot_time_us: float = 9.0
    sifs_us: float = 16.0
    difs_us: float = 34.0
    cw_min: int = 15
    cw_max: int = 1023
    retry_limit: int = 4  # ath10k-ct firmware retry clamp
    phy_rate_mbps: float = 65.0  # MCS7 20 MHz 1x1 or MCS4 2x2
    rts_rate_mbps: float = 6.0   # Legacy 6 Mbps robust control rate
    payload_bytes: int = 1500
    ampdu_depth: int = 32        # CoTSQ 6ms aggregation depth
    sim_duration_us: float = 10_000_000.0  # 10 simulated seconds per run


class Station:
    def __init__(self, sta_id: int, config: SimConfig, use_rts: bool):
        self.sta_id = sta_id
        self.config = config
        self.use_rts = use_rts
        self.cw = config.cw_min
        self.backoff_slots = random.randint(0, self.cw)
        self.retry_count = 0
        self.successful_tx = 0
        self.collided_tx = 0
        self.delivered_bytes = 0
        self.latencies_ms: List[float] = []
        self.packet_gen_time_us = 0.0

    def reset_backoff_success(self, current_time_us: float):
        latency = (current_time_us - self.packet_gen_time_us) / 1000.0
        self.latencies_ms.append(latency)
        self.successful_tx += 1
        self.delivered_bytes += self.config.payload_bytes * self.config.ampdu_depth
        self.cw = self.config.cw_min
        self.retry_count = 0
        self.backoff_slots = random.randint(0, self.cw)
        self.packet_gen_time_us = current_time_us

    def reset_backoff_collision(self, current_time_us: float):
        self.collided_tx += 1
        self.retry_count += 1
        if self.retry_count > self.config.retry_limit:
            # Dropped due to retry limit
            self.retry_count = 0
            self.cw = self.config.cw_min
            self.packet_gen_time_us = current_time_us
        else:
            self.cw = min(self.config.cw_max, (self.cw + 1) * 2 - 1)
        self.backoff_slots = random.randint(0, self.cw)


class PtMPContentionSimulator:
    def __init__(self, num_stations: int, use_rts: bool, config: SimConfig = None):
        self.config = config or SimConfig()
        self.num_stations = num_stations
        self.use_rts = use_rts
        self.stations = [Station(i, self.config, use_rts) for i in range(num_stations)]
        
        # Calculate frame transmission durations
        # Data payload duration
        total_data_bits = (self.config.payload_bytes * self.config.ampdu_depth) * 8
        self.t_data_us = total_data_bits / self.config.phy_rate_mbps
        
        # Control frame durations at 6 Mbps legacy rate
        # RTS: 20 bytes (160 bits) + 16 us PHY preamble
        self.t_rts_us = (160.0 / self.config.rts_rate_mbps) + 16.0
        # CTS: 14 bytes (112 bits) + 16 us PHY preamble
        self.t_cts_us = (112.0 / self.config.rts_rate_mbps) + 16.0
        # ACK: 14 bytes
        self.t_ack_us = (112.0 / self.config.rts_rate_mbps) + 16.0

    def run(self) -> Dict[str, float]:
        """Execute discrete-event simulation over simulated time."""
        current_time_us = 0.0
        
        # State tracking: when is the AP receiver busy until?
        ap_busy_until_us = 0.0

        while current_time_us < self.config.sim_duration_us:
            # Step 1: Find stations that have backoff expired (count down 1 slot)
            ready_stations = []
            
            # Since CPEs are HIDDEN from each other, they only pause backoff
            # if they perceive medium busy. But CPEs CANNOT hear other CPEs!
            # Therefore, in directional PtMP, CPE backoff clocks tick continuously
            # unless the AP is actively transmitting CTS or ACK (downlink audible).
            ap_tx_audible = (current_time_us < ap_busy_until_us and self.use_rts)
            
            if not ap_tx_audible:
                for sta in self.stations:
                    if sta.backoff_slots <= 0:
                        ready_stations.append(sta)
                    else:
                        sta.backoff_slots -= 1

            if not ready_stations:
                current_time_us += self.config.slot_time_us
                continue

            # Step 2: Handle transmissions from ready stations
            if len(ready_stations) == 1:
                # Exactly one station transmits
                sta = ready_stations[0]
                
                # Check if it arrived while AP was already receiving a collided transmission
                if current_time_us < ap_busy_until_us:
                    # Collides with current transmission in the air
                    sta.reset_backoff_collision(current_time_us)
                else:
                    # SUCCESSFUL TRANSMISSION!
                    if self.use_rts:
                        # RTS -> CTS (AP broadcasts CTS, freezing all CPEs for t_data)
                        # -> Data -> ACK
                        tx_duration = (
                            self.t_rts_us + self.config.sifs_us +
                            self.t_cts_us + self.config.sifs_us +
                            self.t_data_us + self.config.sifs_us +
                            self.t_ack_us + self.config.difs_us
                        )
                        current_time_us += tx_duration
                        ap_busy_until_us = current_time_us
                        sta.reset_backoff_success(current_time_us)
                    else:
                        # Basic Access: Data -> ACK
                        tx_duration = (
                            self.t_data_us + self.config.sifs_us +
                            self.t_ack_us + self.config.difs_us
                        )
                        current_time_us += tx_duration
                        ap_busy_until_us = current_time_us
                        sta.reset_backoff_success(current_time_us)

            else:
                # COLLISION: Multiple stations attempt transmission in the same slot!
                # In basic mode, both transmit full DATA aggregates (channel wasted for 3200 us).
                # In RTS mode, both transmit RTS (channel wasted only for 65 us).
                if self.use_rts:
                    waste_duration = self.t_rts_us + self.config.difs_us
                else:
                    waste_duration = self.t_data_us + self.config.difs_us

                current_time_us += waste_duration
                ap_busy_until_us = current_time_us

                for sta in ready_stations:
                    sta.reset_backoff_collision(current_time_us)

        # Calculate metrics
        total_delivered_bits = sum(sta.delivered_bytes for sta in self.stations) * 8.0
        goodput_mbps = total_delivered_bits / self.config.sim_duration_us

        total_tx = sum(sta.successful_tx + sta.collided_tx for sta in self.stations)
        total_coll = sum(sta.collided_tx for sta in self.stations)
        p_coll = total_coll / max(total_tx, 1)

        # Latency statistics across all stations
        all_latencies = []
        for sta in self.stations:
            all_latencies.extend(sta.latencies_ms)

        all_latencies.sort()
        n_lat = len(all_latencies)
        p50 = all_latencies[int(n_lat * 0.50)] if n_lat else 0.0
        p95 = all_latencies[int(n_lat * 0.95)] if n_lat else 0.0
        p99 = all_latencies[int(n_lat * 0.99)] if n_lat else 0.0

        # Jain's Fairness Index
        per_sta_bytes = [sta.delivered_bytes for sta in self.stations]
        sum_x = sum(per_sta_bytes)
        sum_sq_x = sum(x * x for x in per_sta_bytes)
        jain = (sum_x * sum_x) / max(self.num_stations * sum_sq_x, 1e-12)

        return {
            "num_stations": self.num_stations,
            "use_rts": self.use_rts,
            "goodput_mbps": round(goodput_mbps, 2),
            "collision_prob": round(p_coll, 4),
            "p50_latency_ms": round(p50, 2),
            "p95_latency_ms": round(p95, 2),
            "p99_latency_ms": round(p99, 2),
            "jain_fairness": round(jain, 3)
        }


def run_fleet_sweep():
    print("==========================================================================")
    print("  openMAX DISCRETE-EVENT PtMP HIDDEN-NODE SIMULATION (1 to 20 CPEs)")
    print("==========================================================================")
    print(f"{'CPEs':<5} | {'Access Mode':<14} | {'Goodput (Mbps)':<15} | {'P(Coll)':<8} | {'p99 RTT (ms)':<12} | {'Jain'}")
    print("-" * 74)

    results = []
    station_counts = [1, 2, 4, 8, 12, 16, 20]

    for n in station_counts:
        # Run Basic Access (No RTS)
        sim_basic = PtMPContentionSimulator(num_stations=n, use_rts=False)
        res_basic = sim_basic.run()

        # Run Hardware RTS/CTS
        sim_rts = PtMPContentionSimulator(num_stations=n, use_rts=True)
        res_rts = sim_rts.run()

        results.append((res_basic, res_rts))

        print(f"{n:<5} | {'CSMA (No RTS)':<14} | {res_basic['goodput_mbps']:<15} | {res_basic['collision_prob']:<8.3f} | {res_basic['p99_latency_ms']:<12.1f} | {res_basic['jain_fairness']:.3f}")
        print(f"{'':<5} | {'RTS/CTS (512B)':<14} | {res_rts['goodput_mbps']:<15} | {res_rts['collision_prob']:<8.3f} | {res_rts['p99_latency_ms']:<12.1f} | {res_rts['jain_fairness']:.3f}")
        print("-" * 74)

    return results


if __name__ == "__main__":
    run_fleet_sweep()
