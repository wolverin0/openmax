"""PB-020 & PB-023 Runner: `utf_readonly_probe_harness.py`.

Implements:
1. PB-020 Read-Only UTF Boot, Allowlisted TLV2 Capability Enumerator & Watchdog Verifier:
   - Enforces `automatic_execution_allowed = False` and preflight safety invariants
     (sacrificial unit, 50-ohm termination / >=50 dB cabled attenuator, verified
     serial/TFTP recovery, and board-data SHA-256 lock).
   - Strictly enforces the read-only TLV2 command allowlist (`CMD_REGREAD=9`,
     `CMD_TXSTATUS=15`, `CMD_RXSTATUS=18`, `CMD_MEMREAD=42`, `CMD_LMQUERY=76`) and
     rejects mutating/OTP/reset commands (`CMD_REGWRITE=11`, `CMD_MEMWRITE=40`,
     `CMD_WRITECUSTOTPSPACE=26`, `CMD_COMMITOTPSTREAM=36`, `CMD_NOISEFLOORREAD=102`).
   - Evaluates >= 5 boot/probe/reload cycles with < 5.0s command timeout and <= 30.0s
     production WLAN reload watchdog.
2. PB-023 `ADCCAPTURE` (ID 59), `GENWAVEFORM` (ID 61) & `SYSCMD_PHYDBGDUMP` (ID 10009)
   Probe & Sample-RAM Tone-Correlation Validator:
   - Evaluates bounded cabled probes with a 3.0s hang watchdog,
   - Computes complex DFT tone SNR and correlation (`captured_iq_snr_tone_correlation`)
     on `dataI[2048]` / `dataQ[2048]` against an injected cabled test tone,
   - Classifies either `FALSIFIED_STANDARD_TLV2_ADC_ABI` (matching `Q08` static absence)
     or `VERIFIED_TONE_CORRELATED_SAMPLE_RAM`.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

PB020_READONLY_ALLOWLIST_CMD_IDS: Dict[int, str] = {
    9: "CMD_REGREAD",
    15: "CMD_TXSTATUS",
    18: "CMD_RXSTATUS",
    42: "CMD_MEMREAD",
    76: "CMD_LMQUERY",
}

PB020_FORBIDDEN_MUTATING_OR_RESET_CMD_IDS: Dict[int, str] = {
    11: "CMD_REGWRITE",
    14: "CMD_TX",
    17: "CMD_RX",
    20: "CMD_HWCAL",
    26: "CMD_WRITECUSTOTPSPACE",
    36: "CMD_COMMITOTPSTREAM",
    38: "CMD_SETREGDMN",
    40: "CMD_MEMWRITE",
    102: "CMD_NOISEFLOORREAD",  # Invokes whalReset() full PHY reset
}

PB023_EXTENDED_PROBE_CMD_IDS: Dict[int, str] = {
    59: "CMD_ADCCAPTURE",
    61: "CMD_GENWAVEFORM",
    10009: "SYSCMD_PHYDBGDUMP",
}

PB020_MAX_COMMAND_TIMEOUT_S = 5.0
PB020_MAX_WLAN_RELOAD_TIME_S = 30.0
PB020_MIN_REQUIRED_CYCLES = 5
PB023_MAX_COMMAND_TIMEOUT_S = 3.0


@dataclass(frozen=True)
class UTFBenchPreflightConfig:
    """Safety and hardware isolation prerequisites for PB-020 and PB-023."""

    unit_id: str
    is_sacrificial_bench_unit: bool
    is_production_network_device: bool
    rf_ports_terminated_50ohm_or_attenuated_50db: bool
    serial_and_tftp_recovery_verified: bool
    board_data_sha256: str
    utf_binary_sha256: str
    production_fw_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class UTFReadOnlyCycleRecord:
    """Telemetry from one UTF boot -> read-only TLV2 query -> WLAN reload cycle."""

    cycle_index: int
    utf_boot_succeeded: bool
    commands_attempted: List[int]
    command_statuses: Dict[int, int]  # cmd_id -> status (0 = OK)
    max_command_latency_s: float
    unexpected_rf_tx_detected: bool
    wlan_reload_succeeded: bool
    wlan_reload_recovery_time_s: float
    host_interest_debug_state_hex: str = "0x00000001"

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "command_statuses": {str(k): v for k, v in self.command_statuses.items()},
        }


@dataclass(frozen=True)
class PB023CommandProbeAttempt:
    """Bounded probe record for CMD_ADCCAPTURE (59), CMD_GENWAVEFORM (61), or SYSCMD_PHYDBGDUMP (10009)."""

    command_id: int
    command_name: str
    response_received: bool
    response_status: int
    elapsed_s: float
    sample_buffer_length_samples: int
    injected_tone_freq_mhz: float
    injected_tone_amplitude_dbfs: float
    captured_iq_snr_db: float
    captured_iq_snr_tone_correlation: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def verify_utf_bench_preflight(config: UTFBenchPreflightConfig) -> Dict[str, Any]:
    """Validate all PB-020 / PB-023 bench safety prerequisites before any testmode operation."""
    violations: List[str] = []
    if config.is_production_network_device:
        violations.append("FORBIDDEN_PRODUCTION_DEVICE_TARGET")
    if not config.is_sacrificial_bench_unit:
        violations.append("REQUIRES_SACRIFICIAL_BENCH_UNIT")
    if not config.rf_ports_terminated_50ohm_or_attenuated_50db:
        violations.append("REQUIRES_50OHM_TERMINATION_OR_50DB_ATTENUATOR")
    if not config.serial_and_tftp_recovery_verified:
        violations.append("REQUIRES_VERIFIED_SERIAL_AND_TFTP_RECOVERY")
    if len(config.board_data_sha256) != 64 or len(config.utf_binary_sha256) != 64:
        violations.append("MISSING_VALID_SHA256_PROVENANCE")

    return {
        "preflight_passed": len(violations) == 0,
        "automatic_execution_allowed": False,
        "violations": violations,
        "config": config.to_dict(),
    }


def validate_pb020_readonly_command_list(command_ids: Sequence[int]) -> None:
    """Raise ValueError if any command ID is outside the PB-020 read-only allowlist."""
    for cid in command_ids:
        if cid in PB020_FORBIDDEN_MUTATING_OR_RESET_CMD_IDS:
            name = PB020_FORBIDDEN_MUTATING_OR_RESET_CMD_IDS[cid]
            raise ValueError(
                f"Command {cid} ({name}) is forbidden in PB-020 read-only qualification."
            )
        if cid not in PB020_READONLY_ALLOWLIST_CMD_IDS:
            raise ValueError(
                f"Command {cid} is not in PB020_READONLY_ALLOWLIST_CMD_IDS: "
                f"{sorted(PB020_READONLY_ALLOWLIST_CMD_IDS)}"
            )


def evaluate_pb020_readonly_cycles(
    preflight: UTFBenchPreflightConfig,
    cycles: Sequence[UTFReadOnlyCycleRecord],
) -> Dict[str, Any]:
    """Evaluate PB-020 acceptance criteria and watchdog rollback conditions across >= 5 cycles."""
    pf_res = verify_utf_bench_preflight(preflight)
    if not pf_res["preflight_passed"]:
        return {
            "gate_id": "PB-020",
            "automatic_execution_allowed": False,
            "preflight": pf_res,
            "watchdog_rollback_triggered": True,
            "watchdog_action": "ABORT_PREFLIGHT_FAILED",
            "watchdog_reasons": pf_res["violations"],
            "qualification_verdict": "FAIL",
        }

    if len(cycles) < PB020_MIN_REQUIRED_CYCLES:
        raise ValueError(
            f"PB-020 requires >= {PB020_MIN_REQUIRED_CYCLES} cycles, got {len(cycles)}."
        )

    for c in cycles:
        validate_pb020_readonly_command_list(c.commands_attempted)

    watchdog_reasons: List[str] = []
    boot_successes = 0
    reload_successes = 0
    max_reload_s = 0.0
    max_cmd_s = 0.0
    supported_bitmap = 0
    supported_cmd_names: List[str] = []

    for c in cycles:
        if c.utf_boot_succeeded:
            boot_successes += 1
        else:
            watchdog_reasons.append(f"CYCLE_{c.cycle_index}_UTF_BOOT_FAILED")

        if c.unexpected_rf_tx_detected:
            watchdog_reasons.append(f"CYCLE_{c.cycle_index}_UNEXPECTED_RF_STATE")

        if c.max_command_latency_s > PB020_MAX_COMMAND_TIMEOUT_S:
            watchdog_reasons.append(
                f"CYCLE_{c.cycle_index}_CMD_TIMEOUT_{c.max_command_latency_s:.2f}S_GT_5S"
            )

        if (
            not c.wlan_reload_succeeded
            or c.wlan_reload_recovery_time_s > PB020_MAX_WLAN_RELOAD_TIME_S
        ):
            watchdog_reasons.append(
                f"CYCLE_{c.cycle_index}_WLAN_RELOAD_BREACH_{c.wlan_reload_recovery_time_s:.2f}S_GT_30S"
            )
        else:
            reload_successes += 1

        max_reload_s = max(max_reload_s, c.wlan_reload_recovery_time_s)
        max_cmd_s = max(max_cmd_s, c.max_command_latency_s)

        for cid, status in c.command_statuses.items():
            if status == 0:
                supported_bitmap |= 1 << cid
                cname = PB020_READONLY_ALLOWLIST_CMD_IDS.get(cid, f"CMD_{cid}")
                if cname not in supported_cmd_names:
                    supported_cmd_names.append(cname)

    n = len(cycles)
    boot_rate = boot_successes / n
    reload_rate = reload_successes / n
    watchdog_triggered = len(watchdog_reasons) > 0
    passed = (
        not watchdog_triggered
        and boot_rate == 1.0
        and reload_rate == 1.0
        and max_reload_s <= PB020_MAX_WLAN_RELOAD_TIME_S
    )

    return {
        "gate_id": "PB-020",
        "automatic_execution_allowed": False,
        "preflight": pf_res,
        "cycles_evaluated": n,
        "utf_boot_success_rate": round(boot_rate, 4),
        "wlan_reload_success_rate": round(reload_rate, 4),
        "max_command_latency_s": round(max_cmd_s, 3),
        "wlan_reload_recovery_time_s": round(max_reload_s, 3),
        "enumerated_tlv_command_bitmap": f"0x{supported_bitmap:020x}",
        "enumerated_supported_commands": sorted(supported_cmd_names),
        "watchdog_rollback_triggered": watchdog_triggered,
        "watchdog_action": (
            "UNLOAD_TESTMODE_AND_COLD_POWER_CYCLE_RECOVERY"
            if watchdog_triggered
            else "NONE"
        ),
        "watchdog_reasons": watchdog_reasons,
        "qualification_verdict": "PASS" if passed else "FAIL",
        "cycles": [c.to_dict() for c in cycles],
    }


def synthesize_adc_iq_tone_capture(
    num_samples: int = 2048,
    sample_rate_mhz: float = 80.0,
    tone_freq_mhz: float = 5.0,
    amplitude: float = 400.0,
    phase_rad: float = 0.3,
) -> Tuple[List[int], List[int]]:
    """Synthesize a 2048-sample signed I/Q capture (`dataI[2048]`, `dataQ[2048]`) at `tone_freq_mhz`."""
    data_i: List[int] = []
    data_q: List[int] = []
    for n in range(num_samples):
        theta = phase_rad + 2.0 * math.pi * (tone_freq_mhz / sample_rate_mhz) * n
        # Deterministic tiny quantization dither
        i_val = int(round(amplitude * math.cos(theta)))
        q_val = int(round(amplitude * math.sin(theta)))
        data_i.append(i_val)
        data_q.append(q_val)
    return data_i, data_q


def compute_iq_tone_correlation_and_snr(
    data_i: Sequence[int],
    data_q: Sequence[int],
    sample_rate_mhz: float = 80.0,
    expected_tone_freq_mhz: float = 5.0,
) -> Dict[str, float]:
    """Compute normalized complex tone correlation and in-band tone SNR (dB) on `dataI`/`dataQ`."""
    if len(data_i) != len(data_q) or len(data_i) == 0:
        raise ValueError("data_i and data_q must have equal non-zero length.")

    n_samp = len(data_i)
    total_energy = sum(float(i) ** 2 + float(q) ** 2 for i, q in zip(data_i, data_q))
    if total_energy <= 1e-12:
        return {
            "captured_iq_snr_tone_correlation": 0.0,
            "captured_iq_snr_db": -99.0,
            "rms_magnitude": 0.0,
        }

    # Project complex signal z[n] = I[n] + j Q[n] onto reference exp(-j 2*pi*(f/fs)*n)
    proj_re = 0.0
    proj_im = 0.0
    omega = 2.0 * math.pi * (expected_tone_freq_mhz / sample_rate_mhz)
    for idx, (i_val, q_val) in enumerate(zip(data_i, data_q)):
        c = math.cos(omega * idx)
        s = math.sin(omega * idx)
        # z * exp(-j*omega*n) = (i + j*q)*(c - j*s) = (i*c + q*s) + j*(q*c - i*s)
        proj_re += float(i_val) * c + float(q_val) * s
        proj_im += float(q_val) * c - float(i_val) * s

    tone_energy = (proj_re**2 + proj_im**2) / n_samp
    corr = math.sqrt(max(0.0, min(1.0, tone_energy / total_energy)))
    noise_energy = max(1e-9, total_energy - tone_energy)
    snr_db = 10.0 * math.log10(tone_energy / noise_energy)
    rms_mag = math.sqrt(total_energy / n_samp)

    return {
        "captured_iq_snr_tone_correlation": round(corr, 4),
        "captured_iq_snr_db": round(snr_db, 2),
        "rms_magnitude": round(rms_mag, 2),
    }


def evaluate_pb023_adccapture_and_genwaveform_probes(
    probes: Sequence[PB023CommandProbeAttempt],
) -> Dict[str, Any]:
    """Evaluate PB-023 probes and classify whether standard TLV2 ADC capture is supported or falsified."""
    if not probes:
        raise ValueError("At least one PB023CommandProbeAttempt is required.")

    watchdog_triggered = False
    watchdog_reasons: List[str] = []
    verified_adc_captures = 0

    for p in probes:
        if p.elapsed_s > PB023_MAX_COMMAND_TIMEOUT_S:
            watchdog_triggered = True
            watchdog_reasons.append(
                f"CMD_{p.command_id}_{p.command_name}_HANG_{p.elapsed_s:.2f}S_GT_3S"
            )
        if (
            p.command_id == 59
            and p.response_received
            and p.response_status == 0
            and p.sample_buffer_length_samples == 2048
            and p.captured_iq_snr_tone_correlation >= 0.90
        ):
            verified_adc_captures += 1

    if watchdog_triggered:
        outcome = "WATCHDOG_ROLLBACK_TRIGGERED_TARGET_HUNG"
        branch_decision = "UNLOAD_UTF_AND_POWER_CYCLE_RADIO"
    elif verified_adc_captures > 0:
        outcome = "VERIFIED_TONE_CORRELATED_SAMPLE_RAM"
        branch_decision = "UNLOCK_OFFLINE_NEURAL_RECEIVER_CAPTURE_BRANCH"
    else:
        outcome = "FALSIFIED_STANDARD_TLV2_ADC_ABI"
        branch_decision = (
            "CLOSE_STANDARD_TLV2_ADC_BRANCH__USE_PB021_CHAN_TAB_B0_B1_AND_MEMREAD_42"
        )

    return {
        "gate_id": "PB-023",
        "automatic_execution_allowed": False,
        "probes_evaluated": len(probes),
        "watchdog_rollback_triggered": watchdog_triggered,
        "watchdog_action": (
            "UNLOAD_UTF_AND_POWER_CYCLE_RADIO" if watchdog_triggered else "NONE"
        ),
        "watchdog_reasons": watchdog_reasons,
        "outcome_classification": outcome,
        "branch_decision": branch_decision,
        "probes": [p.to_dict() for p in probes],
    }


def build_pb_020_023_utf_probe_fixture() -> Dict[str, Any]:
    """Build the deterministic PB-020 & PB-023 qualification fixture artifact."""
    preflight = UTFBenchPreflightConfig(
        unit_id="SACRIFICIAL-BENCH-LAP120-LAB",
        is_sacrificial_bench_unit=True,
        is_production_network_device=False,
        rf_ports_terminated_50ohm_or_attenuated_50db=True,
        serial_and_tftp_recovery_verified=True,
        board_data_sha256="a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0",
        utf_binary_sha256="b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef01a",
        production_fw_sha256="19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416",
    )

    cycles = [
        UTFReadOnlyCycleRecord(
            cycle_index=idx + 1,
            utf_boot_succeeded=True,
            commands_attempted=[9, 15, 18, 42, 76],
            command_statuses={9: 0, 15: 0, 18: 0, 42: 0, 76: 0},
            max_command_latency_s=0.042 + idx * 0.003,
            unexpected_rf_tx_detected=False,
            wlan_reload_succeeded=True,
            wlan_reload_recovery_time_s=4.8 + idx * 0.2,
        )
        for idx in range(5)
    ]

    pb020_eval = evaluate_pb020_readonly_cycles(preflight=preflight, cycles=cycles)

    # Scenario A: Expected AR9888 UTF result based on Q08 static trace (IDs 59, 61, 10009 unregistered)
    probes_ar9888_expected = [
        PB023CommandProbeAttempt(
            command_id=59,
            command_name="CMD_ADCCAPTURE",
            response_received=False,
            response_status=0xFF,
            elapsed_s=0.25,
            sample_buffer_length_samples=0,
            injected_tone_freq_mhz=5.0,
            injected_tone_amplitude_dbfs=-12.0,
            captured_iq_snr_db=-99.0,
            captured_iq_snr_tone_correlation=0.0,
        ),
        PB023CommandProbeAttempt(
            command_id=61,
            command_name="CMD_GENWAVEFORM",
            response_received=False,
            response_status=0xFF,
            elapsed_s=0.25,
            sample_buffer_length_samples=0,
            injected_tone_freq_mhz=5.0,
            injected_tone_amplitude_dbfs=-12.0,
            captured_iq_snr_db=-99.0,
            captured_iq_snr_tone_correlation=0.0,
        ),
        PB023CommandProbeAttempt(
            command_id=10009,
            command_name="SYSCMD_PHYDBGDUMP",
            response_received=False,
            response_status=0xFF,
            elapsed_s=0.25,
            sample_buffer_length_samples=0,
            injected_tone_freq_mhz=5.0,
            injected_tone_amplitude_dbfs=-12.0,
            captured_iq_snr_db=-99.0,
            captured_iq_snr_tone_correlation=0.0,
        ),
    ]
    pb023_expected_eval = evaluate_pb023_adccapture_and_genwaveform_probes(
        probes_ar9888_expected
    )

    # Scenario B: Synthetic positive tone-correlation calibration check (proving the validator detects true ADC I/Q)
    synth_i, synth_q = synthesize_adc_iq_tone_capture(
        num_samples=2048,
        sample_rate_mhz=80.0,
        tone_freq_mhz=5.0,
        amplitude=420.0,
    )
    tone_stats = compute_iq_tone_correlation_and_snr(
        synth_i, synth_q, sample_rate_mhz=80.0, expected_tone_freq_mhz=5.0
    )

    return {
        "schema_version": "1.0",
        "task_id": "T-PB-GEM2-05",
        "gates_covered": ["PB-020", "PB-023"],
        "target_architecture": "QCA988x / AR9888 v2 (Peregrine)",
        "live_devices_touched": False,
        "automatic_execution_allowed": False,
        "pb_020_readonly_utf_qualification": pb020_eval,
        "pb_023_ar9888_expected_probe_evaluation": pb023_expected_eval,
        "pb_023_tone_correlation_validator_self_test": tone_stats,
    }


def write_pb_020_023_utf_probe_fixture_json(
    output_path: Path = Path("artifacts/qca988x/pb_020_023_utf_probe_fixture.json"),
) -> Dict[str, Any]:
    """Generate and write `artifacts/qca988x/pb_020_023_utf_probe_fixture.json`."""
    fixture = build_pb_020_023_utf_probe_fixture()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    return fixture


if __name__ == "__main__":
    out = Path("artifacts/qca988x/pb_020_023_utf_probe_fixture.json")
    fix = write_pb_020_023_utf_probe_fixture_json(out)
    print(
        json.dumps(
            {
                "artifact": str(out),
                "pb_020_verdict": fix["pb_020_readonly_utf_qualification"][
                    "qualification_verdict"
                ],
                "enumerated_supported_commands": fix[
                    "pb_020_readonly_utf_qualification"
                ]["enumerated_supported_commands"],
                "pb_023_expected_outcome": fix[
                    "pb_023_ar9888_expected_probe_evaluation"
                ]["outcome_classification"],
                "tone_validator_self_test_correlation": fix[
                    "pb_023_tone_correlation_validator_self_test"
                ]["captured_iq_snr_tone_correlation"],
            },
            indent=2,
        )
    )
