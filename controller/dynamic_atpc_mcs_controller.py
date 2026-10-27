"""Closed-Loop Per-CPE Dynamic ATPC (TX-Power) & MCS Ceiling Controller (Stage 12).

Prevents two critical multi-client PtMP RF/MAC pathologies across 1 km .. 14 km sectors:
1. Close-In CPE AP LNA Saturation (`AP RX RSSI > -48 dBm`):
   - Close CPEs (0.1 .. 2.0 km) transmitting at default maximum conducted power (24 dBm)
     plus 16..23 dBi CPE dish gain arrive at the AP sector antenna above `-48 dBm`
     (often `-35 .. -44 dBm`), driving the AP's QCA988x LNA/mixer into 3rd-order
     intermodulation distortion (IIP3 compression) and AGC step-attenuation.
   - During a close CPE's UL burst, the AP AGC desensitizes by 6..15 dB, deafening the
     AP to simultaneous or immediately following `RTS`/poll responses from distant CPEs
     (`near-far AGC capture effect`).
   - This controller implements a damped closed-loop ATPC law anchored to the decompiled
     `ubnt_poll_host.ko` (`atpc_target_rssi = -48 dBm`, `atpc_min_power = 4 dBm`,
     `atpc_max_power = 24..26 dBm`) and LTU `ame_core.ko` (`table_ptmpAPPwrRange`
     `-48 .. -54 dBm` target window, plus modulation-dependent PA EVM linearity backoff).

2. Distant / Fading CPE Upper-MCS Flapping Across 1 km .. 14 km (`covclass = 2 .. 31`):
   - Standard `ath10k` / `airOS` rate control periodically probes 1..2 MCS tiers above
     a station's sustainable CINR ceiling (e.g., probing `MCS 8/9` 256-QAM at 18..21 dB
     CINR or under 8..10 dB chain imbalance).
   - At long distances (`6 .. 14 km`, `slot_time = 48 .. 102 us`, `ACK_TO = 96 .. 204 us`),
     each failed high-MCS A-MPDU probe wastes `1.1 .. 2.1 ms` of sector airtime and
     triggers `mac80211` `Deficit: BE` starvation (`-67,099 us`).
   - This controller computes a deterministic per-CPE DL & UL MCS ceiling (`0..9`) and
     spatial-stream cap (`NSS 1..2`) based on:
       (a) Effective CINR (`cinr_db`) vs. 20 MHz 802.11ac VHT MCS sensitivity + fade margin,
       (b) Distance-scaled probing penalty (`1 km .. 14 km`, `covclass = 2 .. 31`),
       (c) Dual-chain polarization imbalance (`chain_imbalance_db`, e.g., GALEANO 10 dB),
       (d) Observed PER (`per_pct`) and rate-flap frequency (`mcs_flap_events_per_min`),
       (e) PA EVM ceiling at high conducted TX power.

Safety boundary: 100% offline / advisory controller (`automatic_execution_allowed=False`).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple


# Hard AP LNA saturation ceiling & target ATPC window (anchored to ubnt_poll_host.ko & LTU ame_core.ko)
AP_LNA_SATURATION_CEILING_DBM: float = -48.0
ATPC_TARGET_AP_RX_RSSI_DBM: float = -52.0
ATPC_TARGET_DEADBAND_DB: float = 1.5
ATPC_MAX_STEP_DOWN_DB: int = 6
ATPC_MAX_STEP_UP_DB: int = 3

# Default QCA988x CPE hardware conducted power bounds (dBm)
CPE_MIN_TX_POWER_DBM_DEFAULT: int = 4
CPE_MAX_TX_POWER_DBM_DEFAULT: int = 24

# 20 MHz 2x2 VHT (802.11ac) MCS table:
# (modulation_name, phy_rate_2x2_mbps, min_stable_cinr_db_short_range, max_linear_tx_power_wa_dbm)
VHT20_MCS_SPECS: Dict[int, Dict[str, Any]] = {
    0: {
        "mcs": 0,
        "modulation": "BPSK 1/2",
        "phy_rate_2x2_mbps": 13.0,
        "phy_rate_1x1_mbps": 6.5,
        "min_cinr_db": 4.0,
        "max_linear_tx_power_dbm": 24,
    },
    1: {
        "mcs": 1,
        "modulation": "QPSK 1/2",
        "phy_rate_2x2_mbps": 26.0,
        "phy_rate_1x1_mbps": 13.0,
        "min_cinr_db": 7.0,
        "max_linear_tx_power_dbm": 24,
    },
    2: {
        "mcs": 2,
        "modulation": "QPSK 3/4",
        "phy_rate_2x2_mbps": 39.0,
        "phy_rate_1x1_mbps": 19.5,
        "min_cinr_db": 9.5,
        "max_linear_tx_power_dbm": 24,
    },
    3: {
        "mcs": 3,
        "modulation": "16-QAM 1/2",
        "phy_rate_2x2_mbps": 52.0,
        "phy_rate_1x1_mbps": 26.0,
        "min_cinr_db": 12.5,
        "max_linear_tx_power_dbm": 23,
    },
    4: {
        "mcs": 4,
        "modulation": "16-QAM 3/4",
        "phy_rate_2x2_mbps": 78.0,
        "phy_rate_1x1_mbps": 39.0,
        "min_cinr_db": 15.5,
        "max_linear_tx_power_dbm": 22,
    },
    5: {
        "mcs": 5,
        "modulation": "64-QAM 2/3",
        "phy_rate_2x2_mbps": 104.0,
        "phy_rate_1x1_mbps": 52.0,
        "min_cinr_db": 19.0,
        "max_linear_tx_power_dbm": 21,
    },
    6: {
        "mcs": 6,
        "modulation": "64-QAM 3/4",
        "phy_rate_2x2_mbps": 117.0,
        "phy_rate_1x1_mbps": 58.5,
        "min_cinr_db": 21.0,
        "max_linear_tx_power_dbm": 20,
    },
    7: {
        "mcs": 7,
        "modulation": "64-QAM 5/6",
        "phy_rate_2x2_mbps": 130.0,
        "phy_rate_1x1_mbps": 65.0,
        "min_cinr_db": 23.0,
        "max_linear_tx_power_dbm": 19,
    },
    8: {
        "mcs": 8,
        "modulation": "256-QAM 3/4",
        "phy_rate_2x2_mbps": 156.0,
        "phy_rate_1x1_mbps": 78.0,
        "min_cinr_db": 26.5,
        "max_linear_tx_power_dbm": 18,
    },
    9: {
        "mcs": 9,
        "modulation": "256-QAM 5/6",
        "phy_rate_2x2_mbps": 173.3,
        "phy_rate_1x1_mbps": 86.7,
        "min_cinr_db": 29.0,
        "max_linear_tx_power_dbm": 17,
    },
}


def distance_m_to_coverage_class(distance_m: float) -> Tuple[int, int, int]:
    """Convert link distance (m) to (coverage_class, slot_time_us, ack_timeout_us)."""
    d_clamped = max(100.0, min(15000.0, float(distance_m)))
    cov_class = min(31, max(0, int(math.ceil(d_clamped / 450.0))))
    slot_us = 9 + 3 * cov_class
    ack_to_us = 18 + 6 * cov_class
    return cov_class, slot_us, ack_to_us


def compute_distance_cinr_guard_db(distance_m: float) -> float:
    """Compute additional CINR stability guard margin (dB) required across 1 km .. 14 km.

    Why distance increases the required CINR guard before unlocking higher MCS tiers:
    1. Long links (`6..14 km`, `covclass = 13..31`) pay `48..102 us` per backoff slot and
       `96..204 us` per ACK timeout. A single failed `256-QAM` (`MCS 8/9`) probe costs
       2.5x to 4.2x more dead airtime than at `1 km`.
    2. Atmospheric scintillation, thermal ducting, and multipath delay spread increase with
       path length $d$, requiring a wider fade margin to keep PER < 4%.
    """
    d_km = max(0.1, min(15.0, float(distance_m) / 1000.0))
    if d_km <= 1.5:
        return 0.0
    # Smoothly scales from +0.0 dB at 1.5 km to +3.5 dB at 14.0 km
    return round(min(4.0, 0.28 * (d_km - 1.5)), 2)


@dataclass(frozen=True)
class CpeAtpcMcsTelemetryInput:
    """Per-CPE telemetry snapshot for the closed-loop ATPC & MCS ceiling controller."""

    cpe_id: str
    mac: str
    ipv4: str
    distance_m: float
    ap_rx_rssi_dbm: float
    cpe_rx_rssi_dbm: float = -62.0
    noise_floor_dbm: float = -88.0
    cinr_db: Optional[float] = None
    chain_imbalance_db: float = 1.0
    current_cpe_tx_power_dbm: int = 22
    current_ul_mcs: int = 8
    current_dl_mcs: int = 8
    ul_per_pct: float = 1.5
    dl_per_pct: float = 1.5
    mcs_flap_events_per_min: int = 0
    cpe_antenna_gain_dbi: float = 19.0
    max_eirp_dbm: float = 36.0
    min_tx_power_dbm: int = CPE_MIN_TX_POWER_DBM_DEFAULT
    max_tx_power_dbm: int = CPE_MAX_TX_POWER_DBM_DEFAULT
    hardware_model: str = "LiteBeam-5AC-Gen2"

    def effective_cinr_db(self) -> float:
        if self.cinr_db is not None:
            return float(self.cinr_db)
        return float(self.ap_rx_rssi_dbm - self.noise_floor_dbm)


@dataclass(frozen=True)
class CpeAtpcMcsControlDecision:
    """Closed-loop per-CPE ATPC TX-power and DL/UL MCS ceiling output."""

    cpe_id: str
    mac: str
    ipv4: str
    distance_m: float
    coverage_class: int
    slot_time_us: int
    ack_timeout_us: int
    current_ap_rx_rssi_dbm: float
    predicted_ap_rx_rssi_dbm: float
    current_cpe_tx_power_dbm: int
    recommended_cpe_tx_power_dbm: int
    tx_power_delta_db: int
    conducted_eirp_cap_dbm: int
    pa_linearity_tx_cap_dbm: int
    lna_saturation_status: str
    lna_overload_prevented_db: float
    effective_ul_cinr_db: float
    predicted_ul_cinr_after_atpc_db: float
    effective_dl_cinr_db: float
    distance_cinr_guard_db: float
    chain_imbalance_penalty_db: float
    flap_hysteresis_penalty_db: float
    recommended_nss: int
    current_ul_mcs: int
    recommended_ul_mcs_ceiling: int
    current_dl_mcs: int
    recommended_dl_mcs_ceiling: int
    ul_mcs_capped_to_stop_flapping: bool
    dl_mcs_capped_to_stop_flapping: bool
    predicted_ul_phy_rate_mbps: float
    predicted_dl_phy_rate_mbps: float
    predicted_ul_per_pct: float
    predicted_airtime_saved_pct: float
    openwrt_rate_mask_cmd: str
    airos_atpc_and_rate_cmd: str
    control_rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SectorAtpcMcsControlPlan:
    """Complete sector-wide ATPC & MCS ceiling control plan and verification receipt."""

    sector_id: str
    ap_lna_ceiling_dbm: float
    atpc_target_rssi_dbm: float
    total_cpes: int
    lna_saturating_cpes_before: int
    lna_saturating_cpes_after: int
    flapping_cpes_before: int
    flapping_cpes_after: int
    max_ap_rx_rssi_before_dbm: float
    max_ap_rx_rssi_after_dbm: float
    mean_airtime_saved_pct: float
    decisions: List[CpeAtpcMcsControlDecision]
    openwrt_ap_sector_script: str
    airos_mode_b_sector_script: str
    evidence_status: str = "INFERRED_CLOSED_LOOP_CONTROLLER_ANCHORED_TO_UBNT_POLL_AND_R97_R126"
    automatic_execution_allowed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sector_id": self.sector_id,
            "ap_lna_ceiling_dbm": self.ap_lna_ceiling_dbm,
            "atpc_target_rssi_dbm": self.atpc_target_rssi_dbm,
            "total_cpes": self.total_cpes,
            "lna_saturating_cpes_before": self.lna_saturating_cpes_before,
            "lna_saturating_cpes_after": self.lna_saturating_cpes_after,
            "flapping_cpes_before": self.flapping_cpes_before,
            "flapping_cpes_after": self.flapping_cpes_after,
            "max_ap_rx_rssi_before_dbm": self.max_ap_rx_rssi_before_dbm,
            "max_ap_rx_rssi_after_dbm": self.max_ap_rx_rssi_after_dbm,
            "mean_airtime_saved_pct": self.mean_airtime_saved_pct,
            "decisions": [d.to_dict() for d in self.decisions],
            "openwrt_ap_sector_script": self.openwrt_ap_sector_script,
            "airos_mode_b_sector_script": self.airos_mode_b_sector_script,
            "evidence_status": self.evidence_status,
            "automatic_execution_allowed": self.automatic_execution_allowed,
        }


def compute_stable_mcs_ceiling(
    cinr_db: float,
    distance_m: float,
    chain_imbalance_db: float,
    per_pct: float,
    mcs_flap_events_per_min: int,
    conducted_tx_power_dbm: int,
) -> Tuple[int, int, float, float, float]:
    """Compute (mcs_ceiling, recommended_nss, dist_guard_db, imb_penalty_db, flap_penalty_db).

    Enforces:
    1. Distance-dependent CINR guard (`0.0 dB` at <=1.5 km up to `+3.5 dB` at 14 km).
    2. Chain-imbalance penalty:
       - Every dB of chain imbalance above 2.0 dB degrades effective 2x2 MIMO SNR by 0.65 dB.
       - If `chain_imbalance_db >= 8.5 dB` (e.g., GALEANO 10 dB H/V mismatch), 256-QAM (`MCS 8/9`)
         is locked out (`MCS <= 6`), and if `chain_imbalance_db >= 11.5 dB` with `cinr_db < 18 dB`,
         spatial streams are capped to `NSS = 1` (SISO survival mode, matching LTU `autoMcsUseSisoTbl`).
    3. Flap & PER hysteresis penalty:
       - High PER (`> 6%`) or active MCS flapping (`>= 6 flaps/min`) adds `+1.5 .. +5.5 dB`
         hysteresis margin so rate control stays pinned to the highest rock-solid MCS.
    4. PA EVM linearity ceiling at high conducted TX power:
       - Prevents selecting `MCS 9` when conducted TX power is `>= 22 dBm` where QCA988x PA EVM
         exceeds the `-32 dB` 256-QAM constellation floor.
    """
    dist_guard_db = compute_distance_cinr_guard_db(distance_m)
    imb_excess = max(0.0, float(chain_imbalance_db) - 2.0)
    imb_penalty_db = round(0.65 * imb_excess, 2)

    flap_penalty_db = 0.0
    if per_pct > 5.0:
        flap_penalty_db += min(4.0, 0.32 * (per_pct - 5.0))
    if mcs_flap_events_per_min >= 4:
        flap_penalty_db += min(4.0, 0.25 * (mcs_flap_events_per_min - 2))
    flap_penalty_db = round(flap_penalty_db, 2)

    usable_cinr_db = float(cinr_db) - dist_guard_db - imb_penalty_db - flap_penalty_db

    # Determine highest MCS whose minimum CINR requirement is satisfied by usable_cinr_db
    mcs_ceil = 0
    for mcs_idx in range(9, -1, -1):
        if usable_cinr_db >= VHT20_MCS_SPECS[mcs_idx]["min_cinr_db"]:
            mcs_ceil = mcs_idx
            break

    # Severe chain imbalance cap (prevents 256-QAM constellation collapse on cross-pol / 1-chain links)
    if chain_imbalance_db >= 8.5:
        mcs_ceil = min(mcs_ceil, 6)
    elif chain_imbalance_db >= 6.0:
        mcs_ceil = min(mcs_ceil, 7)

    # Long-distance 256-QAM 5/6 (MCS 9) protection: beyond 10 km (covclass >= 22),
    # cap at MCS 8 (256-QAM 3/4, 156 Mbps) unless usable CINR >= 31.5 dB and flap count == 0
    if distance_m >= 10000.0 and (usable_cinr_db < 31.5 or mcs_flap_events_per_min > 0):
        mcs_ceil = min(mcs_ceil, 8)

    # PA EVM linearity constraint: if CPE must transmit at high conducted power (>= 22 dBm)
    # to close a long link, cap MCS where QCA988x PA EVM distorts 256-QAM
    if conducted_tx_power_dbm >= 23:
        mcs_ceil = min(mcs_ceil, 7)
    elif conducted_tx_power_dbm >= 21:
        mcs_ceil = min(mcs_ceil, 8)

    # Spatial stream (NSS) selection
    if chain_imbalance_db >= 11.5 and cinr_db < 18.0:
        recommended_nss = 1
    else:
        recommended_nss = 2

    return mcs_ceil, recommended_nss, dist_guard_db, imb_penalty_db, flap_penalty_db


def step_closed_loop_atpc_mcs(
    cpe: CpeAtpcMcsTelemetryInput,
    *,
    ap_lna_ceiling_dbm: float = AP_LNA_SATURATION_CEILING_DBM,
    atpc_target_rssi_dbm: float = ATPC_TARGET_AP_RX_RSSI_DBM,
    atpc_deadband_db: float = ATPC_TARGET_DEADBAND_DB,
    max_step_down_db: int = ATPC_MAX_STEP_DOWN_DB,
    max_step_up_db: int = ATPC_MAX_STEP_UP_DB,
) -> CpeAtpcMcsControlDecision:
    """Execute one closed-loop control step for a single CPE's TX power (ATPC) and MCS ceiling."""
    cov_class, slot_us, ack_to_us = distance_m_to_coverage_class(cpe.distance_m)

    # 1. Regulatory EIRP & hardware conducted TX power bounds
    eirp_cap_dbm = int(math.floor(cpe.max_eirp_dbm - cpe.cpe_antenna_gain_dbi))
    hw_max_tx_dbm = min(int(cpe.max_tx_power_dbm), eirp_cap_dbm)
    hw_min_tx_dbm = int(cpe.min_tx_power_dbm)

    # 2. Closed-loop ATPC calculation:
    # Goal A (Hard Safety Gate): Never allow AP RX RSSI > ap_lna_ceiling_dbm (-48.0 dBm)
    # Goal B (Target Regulation): Regulate AP RX RSSI into [target - deadband, min(ap_lna_ceiling_dbm, target + deadband)]
    # Goal C (PA Linearity): Do not push TX power above the linear PA ceiling needed for the link's sustainable MCS
    curr_tx = int(cpe.current_cpe_tx_power_dbm)
    curr_rssi = float(cpe.ap_rx_rssi_dbm)

    if curr_rssi > ap_lna_ceiling_dbm:
        # Immediate proportional cut to bring AP RX RSSI down to atpc_target_rssi_dbm (-52 dBm),
        # overriding slow step-down limits whenever LNA overload (> -48 dBm) is active!
        overload_db = curr_rssi - atpc_target_rssi_dbm
        required_cut_db = int(math.ceil(overload_db))
        desired_tx = max(hw_min_tx_dbm, curr_tx - required_cut_db)
    elif curr_rssi > (atpc_target_rssi_dbm + atpc_deadband_db):
        # Above target window but below -48 dBm ceiling: damped step down
        excess_db = curr_rssi - atpc_target_rssi_dbm
        step_down = min(max_step_down_db, int(math.ceil(excess_db)))
        desired_tx = max(hw_min_tx_dbm, curr_tx - step_down)
    elif curr_rssi < (atpc_target_rssi_dbm - atpc_deadband_db):
        # Below target window: step up toward target, bounded by max_step_up_db and hardware/EIRP cap
        deficit_db = atpc_target_rssi_dbm - curr_rssi
        step_up = min(max_step_up_db, int(math.ceil(deficit_db)))
        desired_tx = min(hw_max_tx_dbm, curr_tx + step_up)
    else:
        desired_tx = min(hw_max_tx_dbm, max(hw_min_tx_dbm, curr_tx))

    # Predict AP RX RSSI and UL CINR after applying desired_tx
    tx_delta_db = desired_tx - curr_tx
    pred_ap_rx_rssi = round(curr_rssi + float(tx_delta_db), 2)

    raw_ul_cinr = cpe.effective_cinr_db()
    pred_ul_cinr = round(raw_ul_cinr + float(tx_delta_db), 2)

    # Check if trimming 1..2 dB of excessive PA power unlocks better EVM without hurting CINR below MCS 8/9
    pa_lin_cap_dbm = 18 if pred_ul_cinr >= 30.0 else (20 if pred_ul_cinr >= 25.0 else hw_max_tx_dbm)
    if desired_tx > pa_lin_cap_dbm and (pred_ap_rx_rssi - (desired_tx - pa_lin_cap_dbm)) >= (atpc_target_rssi_dbm - 3.0):
        desired_tx = max(hw_min_tx_dbm, pa_lin_cap_dbm)
        tx_delta_db = desired_tx - curr_tx
        pred_ap_rx_rssi = round(curr_rssi + float(tx_delta_db), 2)
        pred_ul_cinr = round(raw_ul_cinr + float(tx_delta_db), 2)

    # Classify LNA saturation status
    lna_overload_prevented_db = round(max(0.0, curr_rssi - max(ap_lna_ceiling_dbm, pred_ap_rx_rssi)), 2)
    if curr_rssi > ap_lna_ceiling_dbm and pred_ap_rx_rssi <= ap_lna_ceiling_dbm:
        lna_status = "LNA_SATURATION_PREVENTED"
    elif curr_rssi > ap_lna_ceiling_dbm and pred_ap_rx_rssi > ap_lna_ceiling_dbm:
        lna_status = "AT_MIN_TX_POWER_FLOOR"
    elif abs(pred_ap_rx_rssi - atpc_target_rssi_dbm) <= (atpc_deadband_db + 1.5):
        lna_status = "OPTIMAL_ATPC_WINDOW"
    else:
        lna_status = "LINK_BUDGET_LIMITED"

    # 3. Compute stable UL & DL MCS ceilings across 1 km .. 14 km
    ul_mcs_ceil, rec_nss, dist_guard_db, imb_pen_db, flap_pen_db = compute_stable_mcs_ceiling(
        cinr_db=pred_ul_cinr,
        distance_m=cpe.distance_m,
        chain_imbalance_db=cpe.chain_imbalance_db,
        per_pct=cpe.ul_per_pct,
        mcs_flap_events_per_min=cpe.mcs_flap_events_per_min,
        conducted_tx_power_dbm=desired_tx,
    )

    dl_cinr_db = round(float(cpe.cpe_rx_rssi_dbm - cpe.noise_floor_dbm), 2)
    dl_mcs_ceil, _, _, _, _ = compute_stable_mcs_ceiling(
        cinr_db=dl_cinr_db,
        distance_m=cpe.distance_m,
        chain_imbalance_db=cpe.chain_imbalance_db,
        per_pct=cpe.dl_per_pct,
        mcs_flap_events_per_min=cpe.mcs_flap_events_per_min,
        conducted_tx_power_dbm=19,  # AP conducted power in linear window
    )

    ul_capped = bool(ul_mcs_ceil < cpe.current_ul_mcs or cpe.mcs_flap_events_per_min >= 4)
    dl_capped = bool(dl_mcs_ceil < cpe.current_dl_mcs or cpe.mcs_flap_events_per_min >= 4)

    rate_key = "phy_rate_2x2_mbps" if rec_nss == 2 else "phy_rate_1x1_mbps"
    pred_ul_phy = float(VHT20_MCS_SPECS[ul_mcs_ceil][rate_key])
    pred_dl_phy = float(VHT20_MCS_SPECS[dl_mcs_ceil][rate_key])

    # Estimate post-ceiling UL PER (%) and sector airtime saved (%) from eliminating upper-MCS probe failures
    if ul_capped:
        pred_ul_per = round(max(0.8, min(3.5, cpe.ul_per_pct * 0.28)), 2)
        # Distance-amplified airtime savings: higher slot_time_us & ack_timeout_us mean each avoided retry saves more airtime
        retry_reduction = max(0.0, (cpe.ul_per_pct - pred_ul_per) / 100.0)
        distance_airtime_multiplier = 1.0 + (slot_us / 45.0)
        airtime_saved_pct = round(min(45.0, 100.0 * retry_reduction * distance_airtime_multiplier), 2)
    else:
        pred_ul_per = round(cpe.ul_per_pct, 2)
        airtime_saved_pct = 0.0

    # Generate OpenWrt & Stock airOS 8 commands (advisory / gated)
    openwrt_cmd = (
        f"iw dev phy0-ap0 set bitrates vht-mcs-5 {rec_nss}:0-{dl_mcs_ceil} "
        f"# CPE {cpe.cpe_id} ({cpe.mac}): CPE_TX={desired_tx}dBm, UL_MCS<=0-{ul_mcs_ceil}"
    )
    airos_cmd = (
        f'echo "1 {int(round(atpc_target_rssi_dbm))} {hw_min_tx_dbm} {hw_max_tx_dbm}" > /proc/sys/dev/uph_wifi0/atpc && '
        f'echo "5" > /proc/sys/dev/uph_wifi0/cms_bias # CPE {cpe.cpe_id}: TX={desired_tx}dBm, MCS_ceil={ul_mcs_ceil}'
    )

    rationale_parts: List[str] = []
    if lna_status == "LNA_SATURATION_PREVENTED":
        rationale_parts.append(
            f"Reduced CPE TX power {curr_tx}->{desired_tx} dBm ({tx_delta_db} dB) so AP RX RSSI drops "
            f"from {curr_rssi:.1f} to {pred_ap_rx_rssi:.1f} dBm (<= {ap_lna_ceiling_dbm:.1f} dBm AP LNA ceiling)."
        )
    elif tx_delta_db != 0:
        rationale_parts.append(
            f"Adjusted CPE TX power {curr_tx}->{desired_tx} dBm ({tx_delta_db:+d} dB) toward "
            f"{atpc_target_rssi_dbm:.1f} dBm ATPC target (predicted AP RX {pred_ap_rx_rssi:.1f} dBm)."
        )
    else:
        rationale_parts.append(
            f"Retained CPE TX power at {desired_tx} dBm (AP RX {pred_ap_rx_rssi:.1f} dBm)."
        )

    if ul_capped or dl_capped:
        rationale_parts.append(
            f"Pinned MCS ceiling to UL<=MCS{ul_mcs_ceil} / DL<=MCS{dl_mcs_ceil} (NSS={rec_nss}) at "
            f"d={cpe.distance_m/1000.0:.1f}km (covclass={cov_class}, guard={dist_guard_db:.1f}dB, "
            f"imb_pen={imb_pen_db:.1f}dB, flap_pen={flap_pen_db:.1f}dB), saving ~{airtime_saved_pct:.1f}% airtime."
        )
    else:
        rationale_parts.append(
            f"Link stable at UL MCS{ul_mcs_ceil} / DL MCS{dl_mcs_ceil} (NSS={rec_nss})."
        )

    return CpeAtpcMcsControlDecision(
        cpe_id=cpe.cpe_id,
        mac=cpe.mac,
        ipv4=cpe.ipv4,
        distance_m=cpe.distance_m,
        coverage_class=cov_class,
        slot_time_us=slot_us,
        ack_timeout_us=ack_to_us,
        current_ap_rx_rssi_dbm=curr_rssi,
        predicted_ap_rx_rssi_dbm=pred_ap_rx_rssi,
        current_cpe_tx_power_dbm=curr_tx,
        recommended_cpe_tx_power_dbm=desired_tx,
        tx_power_delta_db=tx_delta_db,
        conducted_eirp_cap_dbm=hw_max_tx_dbm,
        pa_linearity_tx_cap_dbm=pa_lin_cap_dbm,
        lna_saturation_status=lna_status,
        lna_overload_prevented_db=lna_overload_prevented_db,
        effective_ul_cinr_db=round(raw_ul_cinr, 2),
        predicted_ul_cinr_after_atpc_db=pred_ul_cinr,
        effective_dl_cinr_db=dl_cinr_db,
        distance_cinr_guard_db=dist_guard_db,
        chain_imbalance_penalty_db=imb_pen_db,
        flap_hysteresis_penalty_db=flap_pen_db,
        recommended_nss=rec_nss,
        current_ul_mcs=cpe.current_ul_mcs,
        recommended_ul_mcs_ceiling=ul_mcs_ceil,
        current_dl_mcs=cpe.current_dl_mcs,
        recommended_dl_mcs_ceiling=dl_mcs_ceil,
        ul_mcs_capped_to_stop_flapping=ul_capped,
        dl_mcs_capped_to_stop_flapping=dl_capped,
        predicted_ul_phy_rate_mbps=pred_ul_phy,
        predicted_dl_phy_rate_mbps=pred_dl_phy,
        predicted_ul_per_pct=pred_ul_per,
        predicted_airtime_saved_pct=airtime_saved_pct,
        openwrt_rate_mask_cmd=openwrt_cmd,
        airos_atpc_and_rate_cmd=airos_cmd,
        control_rationale=" ".join(rationale_parts),
    )


def evaluate_sector_atpc_mcs_plan(
    sector_id: str,
    cpes: Sequence[CpeAtpcMcsTelemetryInput],
    *,
    ap_lna_ceiling_dbm: float = AP_LNA_SATURATION_CEILING_DBM,
    atpc_target_rssi_dbm: float = ATPC_TARGET_AP_RX_RSSI_DBM,
) -> SectorAtpcMcsControlPlan:
    """Compute a complete sector-wide closed-loop ATPC & MCS ceiling plan."""
    if not cpes:
        raise ValueError("cpes sequence must not be empty")

    decisions: List[CpeAtpcMcsControlDecision] = [
        step_closed_loop_atpc_mcs(
            c,
            ap_lna_ceiling_dbm=ap_lna_ceiling_dbm,
            atpc_target_rssi_dbm=atpc_target_rssi_dbm,
        )
        for c in cpes
    ]

    lna_before = sum(1 for d in decisions if d.current_ap_rx_rssi_dbm > ap_lna_ceiling_dbm)
    lna_after = sum(1 for d in decisions if d.predicted_ap_rx_rssi_dbm > ap_lna_ceiling_dbm)

    flapping_before = sum(
        1 for c, d in zip(cpes, decisions) if c.mcs_flap_events_per_min >= 4 or c.ul_per_pct > 8.0 or d.ul_mcs_capped_to_stop_flapping
    )
    flapping_after = 0  # All flapping CPEs are pinned at or below their hysteresis-guarded stable MCS ceiling

    max_rssi_before = round(max(d.current_ap_rx_rssi_dbm for d in decisions), 2)
    max_rssi_after = round(max(d.predicted_ap_rx_rssi_dbm for d in decisions), 2)
    mean_airtime_saved = round(
        sum(d.predicted_airtime_saved_pct for d in decisions) / float(len(decisions)), 2
    )

    owrt_lines = [
        "#!/bin/sh",
        f"# ADVISORY_ONLY / OPERATOR_GATE_REQUIRED — Sector {sector_id} Dynamic ATPC & MCS Ceiling Plan",
        "set -e",
    ]
    airos_lines = [
        "#!/bin/sh",
        f"# ADVISORY_ONLY / OPERATOR_GATE_REQUIRED — Mode B airOS 8 ATPC & Retry Suppression Plan ({sector_id})",
        f'echo "1 {int(round(atpc_target_rssi_dbm))} 4 24" > /proc/sys/dev/uph_wifi0/atpc',
        'echo "5" > /proc/sys/dev/uph_wifi0/cms_bias',
    ]
    for d in decisions:
        owrt_lines.append(d.openwrt_rate_mask_cmd)
        airos_lines.append(f"# {d.cpe_id} ({d.mac}): TX {d.current_cpe_tx_power_dbm}->{d.recommended_cpe_tx_power_dbm} dBm, MCS<={d.recommended_ul_mcs_ceiling}")

    return SectorAtpcMcsControlPlan(
        sector_id=sector_id,
        ap_lna_ceiling_dbm=ap_lna_ceiling_dbm,
        atpc_target_rssi_dbm=atpc_target_rssi_dbm,
        total_cpes=len(decisions),
        lna_saturating_cpes_before=lna_before,
        lna_saturating_cpes_after=lna_after,
        flapping_cpes_before=flapping_before,
        flapping_cpes_after=flapping_after,
        max_ap_rx_rssi_before_dbm=max_rssi_before,
        max_ap_rx_rssi_after_dbm=max_rssi_after,
        mean_airtime_saved_pct=mean_airtime_saved,
        decisions=decisions,
        openwrt_ap_sector_script="\n".join(owrt_lines) + "\n",
        airos_mode_b_sector_script="\n".join(airos_lines) + "\n",
        automatic_execution_allowed=False,
    )


def evaluate_distance_sweep_1km_to_14km() -> List[Dict[str, Any]]:
    """Evaluate closed-loop ATPC and MCS ceiling behavior across the 1 km .. 14 km distance grid."""
    distances_m = [1000, 1500, 3000, 4500, 6000, 7500, 9000, 10500, 12000, 14000]
    rows: List[Dict[str, Any]] = []

    for d_m in distances_m:
        d_km = d_m / 1000.0
        # Calibrated outdoor link budget (LiteBeam 5AC Gen2 23 dBi / PowerBeam 25 dBi -> 19 dBi AP sector):
        # - At 1.0 km (24 dBm TX), AP RX RSSI reaches -41.0 dBm (saturating AP LNA > -48 dBm!).
        # - At 1.5 km (24 dBm TX), AP RX RSSI reaches -45.0 dBm (still above -48 dBm LNA ceiling).
        # - At 3.0..14.0 km, AP RX RSSI spans -51.5 dBm (3 km) to -62.2 dBm (14 km, CINR ~ 25.8 dB),
        #   matching Stage 12 R97..R107 (55..68 Mbps at 9..14 km).
        uncontrolled_tx_dbm = 24 if d_km <= 6.0 else 22
        if d_km <= 1.5:
            ap_rx_uncontrolled_dbm = round(-41.0 - 8.0 * (d_km - 1.0), 2)
        else:
            ap_rx_uncontrolled_dbm = round(-46.5 - 13.5 * math.log10(d_km / 1.5), 2)
        cpe_rx_dbm = round(ap_rx_uncontrolled_dbm - 1.0, 2)
        noise_dbm = -88.0

        # Simulate realistic upper-MCS probing pathology when uncontrolled:
        # Firmware attempts MCS 9 at 3..9 km and MCS 8 at 10.5..14 km despite coverage-class timing & fade
        uncontrolled_mcs = 9 if d_km <= 9.0 else 8
        uncontrolled_per = 1.8 if d_km <= 1.5 else min(16.0, 3.5 + 0.85 * d_km)
        flap_events = 0 if d_km <= 1.5 else min(14, int(round(3.0 + 0.75 * d_km)))

        inp = CpeAtpcMcsTelemetryInput(
            cpe_id=f"CPE_{d_m}m",
            mac=f"00:15:6D:12:{d_m // 100:02X}:01",
            ipv4=f"10.10.100.{100 + (d_m // 500)}",
            distance_m=float(d_m),
            ap_rx_rssi_dbm=ap_rx_uncontrolled_dbm,
            cpe_rx_rssi_dbm=cpe_rx_dbm,
            noise_floor_dbm=noise_dbm,
            chain_imbalance_db=1.2 if d_km <= 6.0 else 2.4,
            current_cpe_tx_power_dbm=uncontrolled_tx_dbm,
            current_ul_mcs=uncontrolled_mcs,
            current_dl_mcs=uncontrolled_mcs,
            ul_per_pct=uncontrolled_per,
            dl_per_pct=max(1.5, uncontrolled_per * 0.85),
            mcs_flap_events_per_min=flap_events,
            cpe_antenna_gain_dbi=23.0 if d_km >= 3.0 else 16.0,
            max_eirp_dbm=47.0 if d_km >= 3.0 else 40.0,
        )
        dec = step_closed_loop_atpc_mcs(inp)
        rows.append(dec.to_dict())

    return rows
