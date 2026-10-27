"""Preflight Safety and Allowlist Verifier for the First Physical-Boundary Bench Campaign (Track 1 & Track 2).

Enforces Phase 0 Workstream F invariants before any sacrificial QCA988x bench execution:
1. Track 1 (PB-020 / PB-023): Exact AR9888 UTF Read-Only Qualification — enforces strict read-only
   TLV command allowlists, blocks TX/calibration/OTP/flash writes, requires 50-ohm RF termination
   or >= 50 dB coaxial attenuation, and mandates RAM-only target loading with proven recovery.
2. Track 2 (PB-021 / PB-022): Channel-Capture Path Qualification (bb_capture_channel,
   bb_captured_channel, bb_length, txbf_h_info) — enforces cabled coaxial attenuation (>= 50 dB),
   read-only descriptor/memory inspection, and blocks production devices.
3. Operator Gate Enforcement: Never authorizes hardware execution unless prerequisites PB-000,
   PB-001, and PB-010 are PASSED and operator_gate_approved is explicitly True.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from research.physical_boundary.ladder_schema import check_gate_readiness, load_ladder

PROTECTED_PARTITIONS: Tuple[str, ...] = (
    "u-boot",
    "u-boot-env",
    "art",
    "factory",
    "eeprom",
    "board-data",
)

TRACK1_READONLY_UTF_ALLOWLIST: Tuple[str, ...] = (
    "UTF_GET_VERSION",
    "UTF_GET_STATUS",
    "UTF_ENUM_CAPABILITIES",
    "UTF_READ_HOST_INTEREST",
    "UTF_QUERY_TLV_SUPPORT_ADCCAPTURE",
    "UTF_QUERY_TLV_SUPPORT_GENWAVEFORM",
    "UTF_QUERY_TLV_SUPPORT_PHYDBGDUMP",
    "UTF_READ_BB_CAPTURE_STATUS",
)

TRACK1_DESTRUCTIVE_UTF_BLOCKLIST: Tuple[str, ...] = (
    "UTF_CONT_TX",
    "UTF_TX_TONE",
    "UTF_WRITE_OTP",
    "UTF_WRITE_EFUSE",
    "UTF_WRITE_CALDATA",
    "UTF_COMMIT_ART",
    "UTF_FLASH_WRITE",
    "UTF_SET_REGULATORY_BYPASS",
)

TRACK2_CHANNEL_CAPTURE_FIELDS: Tuple[str, ...] = (
    "bb_capture_channel",
    "bb_captured_channel",
    "bb_length",
    "txbf_h_info",
    "compressed_v_svd",
)

FORBIDDEN_PRODUCTION_SUBNET_PREFIXES: Tuple[str, ...] = (
    "10.10.100.",  # Guarida / Almafuerte / production infrastructure
)
ALLOWED_SACRIFICIAL_BENCH_IPS: Set[str] = {
    "192.168.1.20",
    "192.168.1.21",
    "192.168.88.20",
    "192.168.88.21",
}


@dataclass(frozen=True)
class CampaignPreflightRequest:
    track_id: str                           # "TRACK_1_UTF_READONLY" or "TRACK_2_CHANNEL_CAPTURE"
    gate_id: str                            # "PB-020", "PB-021", "PB-022", or "PB-023"
    target_device_ip: str                   # Must be an isolated sacrificial bench IP
    execution_mode: str                     # Must be "cabled_bench"
    rf_terminated_50ohm: bool               # True if RF ports are terminated into 50-ohm dummy loads
    coaxial_attenuation_db: float           # Inline 5 GHz coaxial attenuation (dB)
    ram_only_target_load: bool              # Must be True (no SPI flash writes)
    touched_partitions: Tuple[str, ...] = ()
    serial_console_attached: bool = False
    tftp_recovery_verified: bool = False
    poe_power_relay_verified: bool = False
    requested_commands: Tuple[str, ...] = ()
    inspected_descriptor_fields: Tuple[str, ...] = ()
    passed_prerequisite_gates: Tuple[str, ...] = ("PB-000", "PB-001", "PB-010")
    operator_gate_approved: bool = False


@dataclass(frozen=True)
class CampaignPreflightVerdict:
    status: str                             # "REJECTED_UNSAFE" | "BLOCKED_PREREQUISITES" | "BLOCKED_AWAITING_OPERATOR_GATE" | "AUTHORIZED_FOR_BENCH_EXECUTION"
    track_id: str
    gate_id: str
    safe_to_stage_offline: bool
    authorized_for_hardware_execution: bool
    violations: Tuple[str, ...] = field(default_factory=tuple)
    unmet_prerequisites: Tuple[str, ...] = field(default_factory=tuple)
    summary: str = ""


def verify_campaign_preflight(request: CampaignPreflightRequest) -> CampaignPreflightVerdict:
    """Validates all safety, RF containment, command allowlist, prerequisite, and operator-gate rules."""
    violations: List[str] = []

    if request.track_id not in ("TRACK_1_UTF_READONLY", "TRACK_2_CHANNEL_CAPTURE"):
        violations.append(f"Unsupported track_id={request.track_id!r}.")

    # 1. Production network isolation check
    if any(request.target_device_ip.startswith(prefix) for prefix in FORBIDDEN_PRODUCTION_SUBNET_PREFIXES):
        violations.append(
            f"Target IP {request.target_device_ip} is in a forbidden production subnet; "
            f"only isolated sacrificial bench IPs {sorted(ALLOWED_SACRIFICIAL_BENCH_IPS)} are allowed."
        )
    elif request.target_device_ip not in ALLOWED_SACRIFICIAL_BENCH_IPS:
        violations.append(
            f"Target IP {request.target_device_ip} is not in ALLOWED_SACRIFICIAL_BENCH_IPS "
            f"{sorted(ALLOWED_SACRIFICIAL_BENCH_IPS)}."
        )

    # 2. Protected partition and RAM-only load checks
    if not request.ram_only_target_load:
        violations.append("ram_only_target_load must be True; persistent flash writes are forbidden.")

    for part in request.touched_partitions:
        norm_part = part.strip().lower()
        if any(p in norm_part for p in PROTECTED_PARTITIONS):
            violations.append(f"Protected partition touch forbidden: {part!r}.")

    # 3. Recovery harness verification
    if not (request.serial_console_attached and request.tftp_recovery_verified and request.poe_power_relay_verified):
        violations.append(
            "Sacrificial bench recovery harness incomplete: serial_console_attached, "
            "tftp_recovery_verified, and poe_power_relay_verified must all be True."
        )

    # 4. RF containment check
    if request.execution_mode != "cabled_bench":
        violations.append(
            f"First physical campaign requires execution_mode='cabled_bench', got {request.execution_mode!r}."
        )
    if request.track_id == "TRACK_1_UTF_READONLY":
        if not request.rf_terminated_50ohm and request.coaxial_attenuation_db < 50.0:
            violations.append(
                "Track 1 UTF read-only qualification requires 50-ohm RF termination or >= 50 dB coaxial attenuation."
            )
    elif request.track_id == "TRACK_2_CHANNEL_CAPTURE":
        if request.coaxial_attenuation_db < 50.0:
            violations.append(
                f"Track 2 channel-capture cabled pair requires coaxial_attenuation_db >= 50.0 dB, "
                f"got {request.coaxial_attenuation_db} dB."
            )

    # 5. Track-specific command and descriptor allowlists
    if request.track_id == "TRACK_1_UTF_READONLY":
        if not request.requested_commands:
            violations.append("Track 1 must specify at least one allowlisted read-only UTF command.")
        for cmd in request.requested_commands:
            if cmd in TRACK1_DESTRUCTIVE_UTF_BLOCKLIST or cmd not in TRACK1_READONLY_UTF_ALLOWLIST:
                violations.append(
                    f"Command {cmd!r} is not in TRACK1_READONLY_UTF_ALLOWLIST {TRACK1_READONLY_UTF_ALLOWLIST}."
                )
    elif request.track_id == "TRACK_2_CHANNEL_CAPTURE":
        if not request.inspected_descriptor_fields:
            violations.append("Track 2 must specify at least one target descriptor field to inspect.")
        for fld in request.inspected_descriptor_fields:
            if fld not in TRACK2_CHANNEL_CAPTURE_FIELDS:
                violations.append(
                    f"Descriptor field {fld!r} is not in TRACK2_CHANNEL_CAPTURE_FIELDS {TRACK2_CHANNEL_CAPTURE_FIELDS}."
                )
        for cmd in request.requested_commands:
            if cmd in TRACK1_DESTRUCTIVE_UTF_BLOCKLIST:
                violations.append(f"Destructive command {cmd!r} forbidden in Track 2.")

    if violations:
        return CampaignPreflightVerdict(
            status="REJECTED_UNSAFE",
            track_id=request.track_id,
            gate_id=request.gate_id,
            safe_to_stage_offline=False,
            authorized_for_hardware_execution=False,
            violations=tuple(violations),
            summary=f"REJECTED_UNSAFE: {len(violations)} safety/allowlist violation(s) detected.",
        )

    # 6. Check experimental ladder prerequisites
    gates = load_ladder()
    readiness = check_gate_readiness(
        request.gate_id,
        gates,
        passed_overrides=set(request.passed_prerequisite_gates),
    )
    unmet = tuple(readiness["unmet_prerequisites"])
    if unmet:
        return CampaignPreflightVerdict(
            status="BLOCKED_PREREQUISITES",
            track_id=request.track_id,
            gate_id=request.gate_id,
            safe_to_stage_offline=True,
            authorized_for_hardware_execution=False,
            unmet_prerequisites=unmet,
            summary=f"BLOCKED_PREREQUISITES: Gate {request.gate_id} has unmet prerequisites {list(unmet)}.",
        )

    # 7. Operator gate check (Phase 0 rule: never execute on hardware without explicit operator approval)
    if not request.operator_gate_approved:
        return CampaignPreflightVerdict(
            status="BLOCKED_AWAITING_OPERATOR_GATE",
            track_id=request.track_id,
            gate_id=request.gate_id,
            safe_to_stage_offline=True,
            authorized_for_hardware_execution=False,
            summary=(
                f"BLOCKED_AWAITING_OPERATOR_GATE: {request.track_id} ({request.gate_id}) passed all offline "
                f"safety and prerequisite checks; awaiting explicit operator gate approval before bench execution."
            ),
        )

    return CampaignPreflightVerdict(
        status="AUTHORIZED_FOR_BENCH_EXECUTION",
        track_id=request.track_id,
        gate_id=request.gate_id,
        safe_to_stage_offline=True,
        authorized_for_hardware_execution=True,
        summary=f"AUTHORIZED_FOR_BENCH_EXECUTION: {request.track_id} ({request.gate_id}) approved for cabled bench.",
    )
