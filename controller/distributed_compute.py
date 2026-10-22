"""Deterministic Idle-Window Distributed Compute Controller & Fleet Economics Engine.

Implements Section 5 of `docs/OPENMAX_MASTER_RESEARCH_PROMPT.md` and the companion
control-plane for `controller/fmx_micro_worker.c`:

1. Multi-gate CPE eligibility evaluator (`evaluate_cpe_eligibility`):
   - Rejects Sector APs (`role != "CPE"`) so PtMP TDMA/AQL scheduling is never jittered.
   - Enforces nocturnal idle window (`02:00–07:00` local time by default).
   - Enforces hard free-RAM floor (`free_ram_kb >= 16384` kB = 16 MB).
   - Enforces customer traffic preemption threshold (`customer_kbps <= 64.0` kbps).
   - Enforces sector airtime threshold (`sector_airtime_pct <= 25.0` %).
   - Enforces sector loaded latency threshold (`rtt_p95_ms <= 15.0` ms).
   - Enforces per-sector active worker concurrency limit (`active_sector_workers < max_sector_workers`).
   - Enforces hard lease TTL expiration (`now_epoch <= issued_at_epoch + lease_ttl_sec`).

2. Cryptographic Job Manifest Signer & Verifier (`SignedJobManifest`):
   - Fixed allowlisted integer opcodes only (`OP_INT_MONTE_CARLO`, `OP_FNV1A_HASH_SWEEP`,
     `OP_RF_HISTOGRAM_DIGEST`); arbitrary shell commands are structurally impossible.
   - Canonical JSON HMAC-SHA256 signing and constant-time verification (`hmac.compare_digest`).

3. Bit-Exact Reference Verifier for `fmx_micro_worker.c` (`verify_worker_shard`):
   - Reproduces the 32-bit `xorshift32` PRNG and integer kernels from `fmx_micro_worker.c`
     so the NOC controller can spot-check completed shards for bit-flips or tampering.

4. Quantitative Fleet Compute & Power Economics Model (`FleetEconomicsCalculator`):
   - Models the 1,800-device WISP fleet (`AR9342` MIPS 74Kc 535 MHz, `QCA9558` MIPS 74Kc 720 MHz,
     `LTU amesoc3` Dual-Core Cortex-A9) at 5% and 10% duty cycles vs a NOC server.
   - Classifies candidate workloads into `GO`, `CONDITIONAL_GO`, or `NO_GO`.
"""

from __future__ import annotations

import dataclasses
from dataclasses import asdict, dataclass
from enum import Enum, IntEnum
import hashlib
import hmac
import json
import math
import time
from typing import Any, Dict, List, Optional, Tuple


# Mandatory Safety Constants (matching controller/fmx_micro_worker.c)
DEFAULT_WINDOW_START_HOUR: int = 2
DEFAULT_WINDOW_END_HOUR: int = 7
MIN_FREE_RAM_KB: int = 16384          # 16 MB hard minimum free/reclaimable RAM
DEFAULT_MAX_CUSTOMER_KBPS: float = 64.0
DEFAULT_MAX_SECTOR_AIRTIME_PCT: float = 25.0
DEFAULT_MAX_RTT_P95_MS: float = 15.0
DEFAULT_MAX_SECTOR_WORKERS: int = 8
MAX_DUTY_CYCLE_PCT: int = 20
DEFAULT_LEASE_TTL_SEC: int = 90
MAX_LEASE_TTL_SEC: int = 180
SLICE_PERIOD_MS: float = 50.0
GUARD_CHECK_SLICES: int = 3           # 3 * 50ms = 150ms (< 200ms hard preemption gate)
MAX_PREEMPTION_LATENCY_MS: float = 200.0


class WorkerOpCode(IntEnum):
    """Fixed compiled C opcodes supported by `/tmp/fmx_micro_worker`."""

    OP_INT_MONTE_CARLO = 1
    OP_FNV1A_HASH_SWEEP = 2
    OP_RF_HISTOGRAM_DIGEST = 3


class WorkloadVerdict(str, Enum):
    """Economic & technical feasibility verdict for a workload class."""

    GO = "GO"
    CONDITIONAL_GO = "CONDITIONAL_GO"
    NO_GO = "NO_GO"


@dataclass(frozen=True)
class HardwareProfile:
    """Hardware capability profile for a WISP radio family."""

    family_id: str
    soc: str
    isa_abi: str
    clock_mhz: int
    cores: int
    has_hw_fpu: bool
    total_ram_mb: int
    typical_free_ram_kb: int
    kernel_version: str
    libc: str
    coremark_100pct: float
    int_mc_msteps_per_s_100pct: float
    fp64_mflops_100pct: float
    idle_power_w: float
    full_load_delta_power_w: float


# Confirmed Hardware Matrix Profiles (`docs/DISTRIBUTED_COMPUTE_FEASIBILITY.md` §2)
HARDWARE_PROFILES: Dict[str, HardwareProfile] = {
    "airos8_wa_ar9342": HardwareProfile(
        family_id="airos8_wa_ar9342",
        soc="AR9342",
        isa_abi="mips_74kc_be_o32_softfloat",
        clock_mhz=535,
        cores=1,
        has_hw_fpu=False,
        total_ram_mb=64,
        typical_free_ram_kb=20480,
        kernel_version="2.6.32.68",
        libc="uClibc-0.9.33.2",
        coremark_100pct=1420.0,
        int_mc_msteps_per_s_100pct=42.0,
        fp64_mflops_100pct=8.5,
        idle_power_w=3.8,
        full_load_delta_power_w=2.4,
    ),
    "airos8_xc_qca9558": HardwareProfile(
        family_id="airos8_xc_qca9558",
        soc="QCA9558",
        isa_abi="mips_74kc_be_o32_softfloat",
        clock_mhz=720,
        cores=1,
        has_hw_fpu=False,
        total_ram_mb=128,
        typical_free_ram_kb=61440,
        kernel_version="2.6.32.68",
        libc="uClibc-0.9.33.2",
        coremark_100pct=1910.0,
        int_mc_msteps_per_s_100pct=56.0,
        fp64_mflops_100pct=11.4,
        idle_power_w=5.5,
        full_load_delta_power_w=3.0,
    ),
    "openwrt2410_ath79": HardwareProfile(
        family_id="openwrt2410_ath79",
        soc="AR9342/QCA9558",
        isa_abi="mips_24kc_be_musl_softfloat",
        clock_mhz=535,
        cores=1,
        has_hw_fpu=False,
        total_ram_mb=64,
        typical_free_ram_kb=24576,
        kernel_version="6.6.110",
        libc="musl-1.2.4",
        coremark_100pct=1450.0,
        int_mc_msteps_per_s_100pct=43.0,
        fp64_mflops_100pct=8.8,
        idle_power_w=3.8,
        full_load_delta_power_w=2.4,
    ),
    "ltu_amesoc3_cpe": HardwareProfile(
        family_id="ltu_amesoc3_cpe",
        soc="Ubiquiti amesoc3 (Dual Cortex-A9)",
        isa_abi="armv7l_le_eabihf_vfpv3",
        clock_mhz=900,
        cores=2,
        has_hw_fpu=True,
        total_ram_mb=256,
        typical_free_ram_kb=112640,
        kernel_version="3.14.65",
        libc="uClibc/glibc-eabihf",
        coremark_100pct=5400.0,
        int_mc_msteps_per_s_100pct=170.0,
        fp64_mflops_100pct=900.0,
        idle_power_w=6.2,
        full_load_delta_power_w=3.6,
    ),
}


@dataclass(frozen=True)
class CPETelemetrySnapshot:
    """Instantaneous CPE & parent-sector telemetry used by the eligibility gate."""

    cpe_id: str
    role: str                     # "CPE" or "AP"
    local_hour: int               # 0..23
    free_ram_kb: int              # MemFree + Buffers + Cached in kB
    customer_kbps: float          # Instantaneous ath0/eth0 traffic in kbps
    sector_airtime_pct: float     # Parent AP sector airtime utilization (0..100)
    rtt_p95_ms: float             # CPE-to-AP p95 ping RTT in ms
    active_sector_workers: int = 0
    kill_switch_active: bool = False
    lease_issued_at_epoch: Optional[float] = None
    lease_ttl_sec: int = DEFAULT_LEASE_TTL_SEC
    now_epoch: Optional[float] = None


@dataclass(frozen=True)
class EligibilityResult:
    """Structured result of evaluating the idle-window compute gate."""

    cpe_id: str
    eligible: bool
    reasons: Tuple[str, ...]
    preemption_required: bool
    preemption_ceiling_ms: float = GUARD_CHECK_SLICES * SLICE_PERIOD_MS

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cpe_id": self.cpe_id,
            "eligible": self.eligible,
            "reasons": list(self.reasons),
            "preemption_required": self.preemption_required,
            "preemption_ceiling_ms": self.preemption_ceiling_ms,
        }


@dataclass(frozen=True)
class SignedJobManifest:
    """Cryptographically signed, declarative batch job manifest for a CPE worker."""

    job_id: str
    shard_id: int
    cpe_id: str
    opcode: int
    seed: int
    iterations: int
    duty_pct: int
    lease_ttl_sec: int
    max_customer_kbps: int
    issued_at_epoch: int
    signature_hex: str

    def canonical_payload_bytes(self) -> bytes:
        """Return deterministic UTF-8 JSON bytes excluding `signature_hex`."""
        payload = {
            "cpe_id": self.cpe_id,
            "duty_pct": int(self.duty_pct),
            "issued_at_epoch": int(self.issued_at_epoch),
            "iterations": int(self.iterations),
            "job_id": self.job_id,
            "lease_ttl_sec": int(self.lease_ttl_sec),
            "max_customer_kbps": int(self.max_customer_kbps),
            "opcode": int(self.opcode),
            "seed": int(self.seed),
            "shard_id": int(self.shard_id),
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def is_within_idle_window(
    local_hour: int,
    window_start_hour: int = DEFAULT_WINDOW_START_HOUR,
    window_end_hour: int = DEFAULT_WINDOW_END_HOUR,
) -> bool:
    """Check whether `local_hour` (0..23) falls inside `[window_start_hour, window_end_hour)`."""
    if not (0 <= local_hour <= 23):
        raise ValueError(f"local_hour must be in 0..23, got {local_hour}")
    if window_start_hour == window_end_hour:
        return False
    if window_start_hour < window_end_hour:
        return window_start_hour <= local_hour < window_end_hour
    # Wrap-around midnight window (e.g., 23:00 to 06:00)
    return local_hour >= window_start_hour or local_hour < window_end_hour


def evaluate_cpe_eligibility(
    snapshot: CPETelemetrySnapshot,
    *,
    window_start_hour: int = DEFAULT_WINDOW_START_HOUR,
    window_end_hour: int = DEFAULT_WINDOW_END_HOUR,
    min_free_ram_kb: int = MIN_FREE_RAM_KB,
    max_customer_kbps: float = DEFAULT_MAX_CUSTOMER_KBPS,
    max_sector_airtime_pct: float = DEFAULT_MAX_SECTOR_AIRTIME_PCT,
    max_rtt_p95_ms: float = DEFAULT_MAX_RTT_P95_MS,
    max_sector_workers: int = DEFAULT_MAX_SECTOR_WORKERS,
) -> EligibilityResult:
    """Evaluate all safety gates to determine if a CPE can run or continue a batch slice."""
    reasons: List[str] = []
    preemption_required = False

    measurements = (snapshot.free_ram_kb, snapshot.customer_kbps,
                    snapshot.sector_airtime_pct, snapshot.rtt_p95_ms)
    lease = (snapshot.lease_issued_at_epoch, snapshot.now_epoch)
    if (any(not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0 for v in measurements)
            or type(snapshot.active_sector_workers) is not int or snapshot.active_sector_workers < 0
            or type(snapshot.lease_ttl_sec) is not int or not 1 <= snapshot.lease_ttl_sec <= MAX_LEASE_TTL_SEC
            or (any(v is not None for v in lease) and
                (any(not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0 for v in lease)
                 or snapshot.now_epoch < snapshot.lease_issued_at_epoch))):
        return EligibilityResult(snapshot.cpe_id, False, ('INVALID_OR_MISSING_TELEMETRY_OR_LEASE',), True)

    if snapshot.kill_switch_active:
        reasons.append("KILL_SWITCH_ACTIVE")
        preemption_required = True

    if snapshot.role.upper() != "CPE":
        reasons.append("ROLE_NOT_CPE_AP_EXCLUDED")
        preemption_required = True

    if not is_within_idle_window(snapshot.local_hour, window_start_hour, window_end_hour):
        reasons.append(
            f"OUTSIDE_IDLE_WINDOW({snapshot.local_hour:02d}h not in "
            f"{window_start_hour:02d}..{window_end_hour:02d}h)"
        )
        preemption_required = True

    if snapshot.free_ram_kb < min_free_ram_kb:
        reasons.append(f"FREE_RAM_BELOW_FLOOR({snapshot.free_ram_kb}kB < {min_free_ram_kb}kB)")
        preemption_required = True

    if snapshot.customer_kbps > max_customer_kbps:
        reasons.append(
            f"CUSTOMER_TRAFFIC_ACTIVE({snapshot.customer_kbps:.1f}kbps > {max_customer_kbps:.1f}kbps)"
        )
        preemption_required = True

    if snapshot.sector_airtime_pct > max_sector_airtime_pct:
        reasons.append(
            f"SECTOR_AIRTIME_HIGH({snapshot.sector_airtime_pct:.1f}% > {max_sector_airtime_pct:.1f}%)"
        )
        preemption_required = True

    if snapshot.rtt_p95_ms > max_rtt_p95_ms:
        reasons.append(f"RTT_P95_HIGH({snapshot.rtt_p95_ms:.2f}ms > {max_rtt_p95_ms:.2f}ms)")
        preemption_required = True

    if snapshot.active_sector_workers >= max_sector_workers:
        reasons.append(
            f"SECTOR_WORKER_CAP_REACHED({snapshot.active_sector_workers} >= {max_sector_workers})"
        )

    if snapshot.lease_issued_at_epoch is not None and snapshot.now_epoch is not None:
        effective_ttl = min(max(1, snapshot.lease_ttl_sec), MAX_LEASE_TTL_SEC)
        if snapshot.now_epoch > snapshot.lease_issued_at_epoch + effective_ttl:
            reasons.append("LEASE_TTL_EXPIRED")
            preemption_required = True

    return EligibilityResult(
        cpe_id=snapshot.cpe_id,
        eligible=(len(reasons) == 0),
        reasons=tuple(reasons),
        preemption_required=preemption_required,
    )


def _valid_manifest_fields(manifest: SignedJobManifest) -> bool:
    # Never truncate/coerce fields before authenticating: 5.9 must not sign as 5.
    ranges = {'shard_id': (0, 0xFFFFFFFF), 'opcode': (1, 3), 'seed': (1, 0xFFFFFFFF),
              'iterations': (1, 0xFFFFFFFFFFFFFFFF), 'duty_pct': (1, MAX_DUTY_CYCLE_PCT),
              'lease_ttl_sec': (1, MAX_LEASE_TTL_SEC), 'max_customer_kbps': (0, 0xFFFFFFFF),
              'issued_at_epoch': (0, 0x7FFFFFFFFFFFFFFF)}
    return (all(type(getattr(manifest, key)) is int and lo <= getattr(manifest, key) <= hi
                for key, (lo, hi) in ranges.items())
            and all(isinstance(v, str) and bool(v) for v in (manifest.job_id, manifest.cpe_id)))


def create_signed_job_manifest(
    *,
    job_id: str,
    shard_id: int,
    cpe_id: str,
    opcode: int,
    seed: int,
    iterations: int,
    secret_key: bytes,
    duty_pct: int = 5,
    lease_ttl_sec: int = DEFAULT_LEASE_TTL_SEC,
    max_customer_kbps: int = int(DEFAULT_MAX_CUSTOMER_KBPS),
    issued_at_epoch: Optional[int] = None,
) -> SignedJobManifest:
    """Create and HMAC-SHA256 sign a validated declarative job manifest."""
    if opcode not in (
        WorkerOpCode.OP_INT_MONTE_CARLO,
        WorkerOpCode.OP_FNV1A_HASH_SWEEP,
        WorkerOpCode.OP_RF_HISTOGRAM_DIGEST,
    ):
        raise ValueError(f"Unsupported or disallowed opcode: {opcode}")
    if seed <= 0 or seed > 0xFFFFFFFF:
        raise ValueError(f"seed must be a non-zero uint32, got {seed}")
    if iterations <= 0:
        raise ValueError(f"iterations must be positive, got {iterations}")
    if not (1 <= duty_pct <= MAX_DUTY_CYCLE_PCT):
        raise ValueError(f"duty_pct must be within 1..{MAX_DUTY_CYCLE_PCT}, got {duty_pct}")
    if not (1 <= lease_ttl_sec <= MAX_LEASE_TTL_SEC):
        raise ValueError(f"lease_ttl_sec must be within 1..{MAX_LEASE_TTL_SEC}, got {lease_ttl_sec}")
    if not secret_key:
        raise ValueError("secret_key must not be empty")

    unsigned = SignedJobManifest(
        job_id=job_id,
        shard_id=shard_id,
        cpe_id=cpe_id,
        opcode=int(opcode) if isinstance(opcode, WorkerOpCode) else opcode,
        seed=seed,
        iterations=iterations,
        duty_pct=duty_pct,
        lease_ttl_sec=lease_ttl_sec,
        max_customer_kbps=max_customer_kbps,
        issued_at_epoch=int(time.time()) if issued_at_epoch is None else issued_at_epoch,
        signature_hex="",
    )
    if not _valid_manifest_fields(unsigned):
        raise ValueError('Invalid integer bounds or job/CPE identity')
    sig = hmac.new(secret_key, unsigned.canonical_payload_bytes(), hashlib.sha256).hexdigest()
    return dataclasses.replace(unsigned, signature_hex=sig)


def verify_signed_job_manifest(
    manifest: SignedJobManifest,
    secret_key: bytes,
    *,
    now_epoch: Optional[int] = None,
) -> Tuple[bool, str]:
    """Verify HMAC-SHA256 signature, opcode allowlist, safety bounds, and lease TTL."""
    if not secret_key:
        return False, "EMPTY_SECRET_KEY"
    if not _valid_manifest_fields(manifest):
        return False, 'INVALID_MANIFEST_FIELDS'
    if manifest.opcode not in (
        WorkerOpCode.OP_INT_MONTE_CARLO,
        WorkerOpCode.OP_FNV1A_HASH_SWEEP,
        WorkerOpCode.OP_RF_HISTOGRAM_DIGEST,
    ):
        return False, f"DISALLOWED_OPCODE:{manifest.opcode}"
    if not (1 <= manifest.duty_pct <= MAX_DUTY_CYCLE_PCT):
        return False, f"DUTY_PCT_OUT_OF_BOUNDS:{manifest.duty_pct}"
    if not (1 <= manifest.lease_ttl_sec <= MAX_LEASE_TTL_SEC):
        return False, f"LEASE_TTL_OUT_OF_BOUNDS:{manifest.lease_ttl_sec}"
    if manifest.seed <= 0 or manifest.seed > 0xFFFFFFFF or manifest.iterations <= 0:
        return False, "INVALID_SEED_OR_ITERATIONS"

    expected_sig = hmac.new(
        secret_key, manifest.canonical_payload_bytes(), hashlib.sha256
    ).hexdigest()
    if (not isinstance(manifest.signature_hex, str) or len(manifest.signature_hex) != 64
            or any(c not in '0123456789abcdef' for c in manifest.signature_hex)
            or not hmac.compare_digest(expected_sig, manifest.signature_hex)):
        return False, "HMAC_SIGNATURE_MISMATCH"

    now_epoch = time.time() if now_epoch is None else now_epoch
    if not isinstance(now_epoch, (int, float)) or not math.isfinite(now_epoch):
        return False, 'INVALID_CURRENT_TIME'
    if now_epoch < manifest.issued_at_epoch:
        return False, 'MANIFEST_NOT_YET_VALID'
    if now_epoch > manifest.issued_at_epoch + manifest.lease_ttl_sec:
        return False, "MANIFEST_LEASE_EXPIRED"

    return True, "VALID"


def compute_slice_schedule(duty_pct: int, slice_period_ms: float = SLICE_PERIOD_MS) -> Dict[str, float]:
    """Compute explicit work/sleep durations per slice and worst-case preemption latency."""
    if not (1 <= duty_pct <= MAX_DUTY_CYCLE_PCT):
        raise ValueError(f"duty_pct must be in 1..{MAX_DUTY_CYCLE_PCT}, got {duty_pct}")
    work_ms = (slice_period_ms * float(duty_pct)) / 100.0
    sleep_ms = slice_period_ms - work_ms
    preemption_latency_ms = GUARD_CHECK_SLICES * slice_period_ms
    return {
        "duty_pct": float(duty_pct),
        "slice_period_ms": slice_period_ms,
        "work_ms": round(work_ms, 3),
        "sleep_ms": round(sleep_ms, 3),
        "preemption_check_interval_ms": round(preemption_latency_ms, 3),
        "meets_200ms_preemption_gate": preemption_latency_ms < MAX_PREEMPTION_LATENCY_MS,
    }


def simulate_c_worker_kernel(opcode: int, seed: int, iterations: int) -> Tuple[int, int]:
    """Bit-exact Python reference implementation of `run_kernel_step` in `fmx_micro_worker.c`.

    Returns `(final_rng_state, final_accum_uint32)`.
    """
    if opcode not in (
        WorkerOpCode.OP_INT_MONTE_CARLO,
        WorkerOpCode.OP_FNV1A_HASH_SWEEP,
        WorkerOpCode.OP_RF_HISTOGRAM_DIGEST,
    ):
        raise ValueError(f"Unsupported opcode: {opcode}")
    s = seed & 0xFFFFFFFF
    if s == 0:
        raise ValueError("seed must be non-zero")
    acc = 2166136261 if opcode == WorkerOpCode.OP_FNV1A_HASH_SWEEP else 0

    for _ in range(iterations):
        # xorshift32
        s ^= (s << 13) & 0xFFFFFFFF
        s ^= (s >> 17) & 0xFFFFFFFF
        s ^= (s << 5) & 0xFFFFFFFF

        if opcode == WorkerOpCode.OP_INT_MONTE_CARLO:
            x = s & 0xFFFF
            y = (s >> 16) & 0xFFFF
            if (x * x + y * y) <= 0xFFFFFFFF:
                acc = (acc + 1) & 0xFFFFFFFF
        elif opcode == WorkerOpCode.OP_FNV1A_HASH_SWEEP:
            acc ^= s & 0xFF
            acc = (acc * 16777619) & 0xFFFFFFFF
            acc ^= (s >> 8) & 0xFF
            acc = (acc * 16777619) & 0xFFFFFFFF
        else:
            acc = (((acc << 7) & 0xFFFFFFFF) | (acc >> 25)) & 0xFFFFFFFF
            acc ^= (s * 2654435761) & 0xFFFFFFFF

    return s, acc


def verify_worker_shard(
    *,
    opcode: int,
    seed: int,
    iterations: int,
    reported_accum: int,
) -> bool:
    """Verify that a worker's reported 32-bit accumulator matches the deterministic kernel."""
    _, expected_accum = simulate_c_worker_kernel(opcode, seed, iterations)
    return (reported_accum & 0xFFFFFFFF) == expected_accum


class FleetEconomicsCalculator:
    """Quantitative compute and power economics analyzer for the 1,800-radio fleet."""

    # Reference NOC server core (`Ryzen 9 7950X` / `EPYC 9124` 1C @ 100%, 16C @ 170W wall power)
    SERVER_COREMARK_PER_CORE: float = 36000.0
    SERVER_INT_MC_MSTEPS_PER_CORE: float = 680.0
    SERVER_FP64_MFLOPS_PER_CORE: float = 48000.0
    SERVER_POWER_PER_CORE_W: float = 170.0 / 16.0  # ~10.625 W/core under load

    @classmethod
    def evaluate_fleet(
        cls,
        *,
        ar9342_cpe_count: int = 1350,
        qca9558_cpe_count: int = 50,
        ltu_cpe_count: int = 250,
        availability_ratio: float = 0.85,
        duty_pct: int = 10,
        window_hours: float = 5.0,
    ) -> Dict[str, Any]:
        """Compute aggregate throughput, incremental power draw, and NOC server equivalence."""
        if not (1 <= duty_pct <= MAX_DUTY_CYCLE_PCT):
            raise ValueError(f"duty_pct must be in 1..{MAX_DUTY_CYCLE_PCT}, got {duty_pct}")
        if not (0.0 < availability_ratio <= 1.0):
            raise ValueError("availability_ratio must be in (0.0, 1.0]")

        duty_frac = float(duty_pct) / 100.0
        p_ar = HARDWARE_PROFILES["airos8_wa_ar9342"]
        p_xc = HARDWARE_PROFILES["airos8_xc_qca9558"]
        p_ltu = HARDWARE_PROFILES["ltu_amesoc3_cpe"]

        active_ar = int(round(ar9342_cpe_count * availability_ratio))
        active_xc = int(round(qca9558_cpe_count * availability_ratio))
        active_ltu = int(round(ltu_cpe_count * availability_ratio))
        total_active_cpes = active_ar + active_xc + active_ltu

        eff_coremark = duty_frac * (
            active_ar * p_ar.coremark_100pct
            + active_xc * p_xc.coremark_100pct
            + active_ltu * p_ltu.coremark_100pct
        )
        eff_int_msteps_s = duty_frac * (
            active_ar * p_ar.int_mc_msteps_per_s_100pct
            + active_xc * p_xc.int_mc_msteps_per_s_100pct
            + active_ltu * p_ltu.int_mc_msteps_per_s_100pct
        )
        eff_fp64_mflops = duty_frac * (
            active_ar * p_ar.fp64_mflops_100pct
            + active_xc * p_xc.fp64_mflops_100pct
            + active_ltu * p_ltu.fp64_mflops_100pct
        )

        # Waking MIPS 74Kc / Cortex-A9 + DDR controller every 50ms incurs a ~0.25W fixed
        # non-linear regulator/PLL/DRAM wake overhead in addition to linear dynamic CPU power,
        # yielding ~0.38W..0.50W/radio at 5%..10% duty cycle (0.4..1.0W across 5%..20%).
        wake_overhead_w = 0.25
        incremental_power_w = (
            active_ar * (wake_overhead_w + duty_frac * p_ar.full_load_delta_power_w)
            + active_xc * (wake_overhead_w + duty_frac * p_xc.full_load_delta_power_w)
            + active_ltu * (wake_overhead_w + duty_frac * p_ltu.full_load_delta_power_w)
        )
        nightly_energy_wh = incremental_power_w * window_hours
        nightly_int_tsteps = (eff_int_msteps_s * 1e6 * window_hours * 3600.0) / 1e12

        equivalent_server_cores_int = eff_coremark / cls.SERVER_COREMARK_PER_CORE
        equivalent_server_cores_fp64 = eff_fp64_mflops / cls.SERVER_FP64_MFLOPS_PER_CORE
        equivalent_server_power_w = equivalent_server_cores_int * cls.SERVER_POWER_PER_CORE_W

        fleet_gsteps_per_wh = (
            (nightly_int_tsteps * 1000.0) / nightly_energy_wh if nightly_energy_wh > 0 else 0.0
        )
        server_gsteps_per_wh = (
            (cls.SERVER_INT_MC_MSTEPS_PER_CORE * 3.6) / cls.SERVER_POWER_PER_CORE_W
        )

        return {
            "active_cpes": total_active_cpes,
            "active_breakdown": {
                "ar9342": active_ar,
                "qca9558": active_xc,
                "ltu_amesoc3": active_ltu,
            },
            "duty_pct": duty_pct,
            "window_hours": window_hours,
            "effective_aggregate_coremark": round(eff_coremark, 1),
            "effective_int_gsteps_per_s": round(eff_int_msteps_s / 1000.0, 3),
            "effective_fp64_mflops": round(eff_fp64_mflops, 2),
            "nightly_int_tsteps": round(nightly_int_tsteps, 2),
            "incremental_fleet_power_w": round(incremental_power_w, 1),
            "nightly_incremental_energy_kwh": round(nightly_energy_wh / 1000.0, 3),
            "equivalent_modern_server_cores_int": round(equivalent_server_cores_int, 2),
            "equivalent_modern_server_cores_fp64": round(equivalent_server_cores_fp64, 3),
            "noc_server_power_for_same_int_work_w": round(equivalent_server_power_w, 1),
            "fleet_energy_efficiency_gsteps_per_wh": round(fleet_gsteps_per_wh, 2),
            "noc_server_energy_efficiency_gsteps_per_wh": round(server_gsteps_per_wh, 2),
        }

    @staticmethod
    def classify_workload(
        *,
        requires_fpu_or_simd: bool,
        required_ram_mb: float,
        payload_io_kb_per_min: float,
        requires_edge_vantage_point: bool,
        is_crypto_mining_or_llm: bool = False,
    ) -> Tuple[WorkloadVerdict, str]:
        """Classify a candidate distributed workload into GO, CONDITIONAL_GO, or NO_GO."""
        if is_crypto_mining_or_llm:
            return (
                WorkloadVerdict.NO_GO,
                "Crypto mining and edge LLM inference are HARD NO-GO due to 64MB RAM, "
                "missing FPU/AES-NI, and negative power/economic ROI.",
            )
        if required_ram_mb > 2.0:
            return (
                WorkloadVerdict.NO_GO,
                f"Required RAM ({required_ram_mb:.1f} MB) exceeds safe 2.0 MB /tmp ceiling on 64 MB AR9342.",
            )
        if requires_fpu_or_simd:
            return (
                WorkloadVerdict.NO_GO,
                "MIPS 74Kc (AR9342/QCA9558) has no hardware FPU; soft-float is >50,000x slower than 1 server core.",
            )
        if payload_io_kb_per_min > 64.0:
            return (
                WorkloadVerdict.NO_GO,
                f"I/O rate ({payload_io_kb_per_min:.1f} KB/min) risks PtMP sector airtime contention.",
            )
        if requires_edge_vantage_point:
            return (
                WorkloadVerdict.GO,
                "High-value GO: leverages unique rooftop RF/network vantage points with tiny I/O and integer math.",
            )
        return (
            WorkloadVerdict.CONDITIONAL_GO,
            "Conditional GO: embarrassingly parallel integer/combinatorial batch job fits in /tmp RAM and tiny I/O.",
        )
