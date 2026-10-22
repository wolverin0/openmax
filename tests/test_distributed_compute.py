"""Unit tests for `controller/distributed_compute.py` and `controller/fmx_micro_worker.c`.

Verifies:
1. Deterministic idle-window (`02:00–07:00`) and multi-gate CPE eligibility (`free_ram_kb >= 16384`,
   `customer_kbps <= threshold`, `sector_airtime_pct <= threshold`, `rtt_p95_ms <= threshold`,
   AP role exclusion, sector concurrency cap, kill switch, and lease TTL expiration).
2. HMAC-SHA256 job manifest signing, canonical serialization, tamper detection, opcode allowlisting,
   and lease expiration checks.
3. Explicit duty-cycle slice scheduling and `< 200 ms` customer traffic preemption ceiling.
4. Bit-exact integer kernel simulation (`OP_INT_MONTE_CARLO`, `OP_FNV1A_HASH_SWEEP`,
   `OP_RF_HISTOGRAM_DIGEST`) and C source safety audit (`controller/fmx_micro_worker.c`).
5. Quantitative fleet compute & power economics (`1,800`-device fleet at 5% and 10% duty cycle
   vs NOC server) and workload `GO / CONDITIONAL_GO / NO_GO` classifier.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path
import unittest

from controller.distributed_compute import (
     CPETelemetrySnapshot,
    DEFAULT_LEASE_TTL_SEC,
    FleetEconomicsCalculator,
    HARDWARE_PROFILES,
    MAX_PREEMPTION_LATENCY_MS,
    MIN_FREE_RAM_KB,
    WorkerOpCode,
    WorkloadVerdict,
    compute_slice_schedule,
    create_signed_job_manifest,
    evaluate_cpe_eligibility,
    is_within_idle_window,
    simulate_c_worker_kernel,
    verify_signed_job_manifest,
    verify_worker_shard,
)


class TestIdleWindowAndEligibilityGate(unittest.TestCase):
    """Test nocturnal idle window and all CPE/sector safety gates."""

    def setUp(self) -> None:
        self.healthy_snapshot = CPETelemetrySnapshot(
            cpe_id="loco5ac-0xe7fa-01",
            role="CPE",
            local_hour=3,
            free_ram_kb=20480,
            customer_kbps=12.5,
            sector_airtime_pct=14.0,
            rtt_p95_ms=4.2,
            active_sector_workers=2,
            kill_switch_active=False,
            lease_issued_at_epoch=1000.0,
            lease_ttl_sec=90,
            now_epoch=1045.0,
        )

    def test_idle_window_boundaries(self) -> None:
        """Verify 02:00-07:00 window includes 02..06 and excludes 00, 01, 07..23."""
        self.assertFalse(is_within_idle_window(1))
        self.assertTrue(is_within_idle_window(2))
        self.assertTrue(is_within_idle_window(4))
        self.assertTrue(is_within_idle_window(6))
        self.assertFalse(is_within_idle_window(7))
        self.assertFalse(is_within_idle_window(14))
        # Wrap-around window (e.g. 23:00 to 05:00)
        self.assertTrue(is_within_idle_window(23, 23, 5))
        self.assertTrue(is_within_idle_window(0, 23, 5))
        self.assertFalse(is_within_idle_window(5, 23, 5))
        with self.assertRaises(ValueError):
            is_within_idle_window(24)

    def test_healthy_cpe_passes_all_gates(self) -> None:
        """Verify an idle CPE inside 02:00-07:00 with >=16MB free RAM passes."""
        res = evaluate_cpe_eligibility(self.healthy_snapshot)
        self.assertTrue(res.eligible)
        self.assertEqual(res.reasons, ())
        self.assertFalse(res.preemption_required)
        self.assertLess(res.preemption_ceiling_ms, MAX_PREEMPTION_LATENCY_MS)

    def test_ap_role_strictly_rejected(self) -> None:
        """Verify Sector APs are never eligible for batch compute."""
        ap_snap = dataclasses.replace(self.healthy_snapshot, role="AP")
        res = evaluate_cpe_eligibility(ap_snap)
        self.assertFalse(res.eligible)
        self.assertIn("ROLE_NOT_CPE_AP_EXCLUDED", res.reasons)
        self.assertTrue(res.preemption_required)

    def test_outside_time_window_rejected(self) -> None:
        """Verify daytime hour (e.g. 19:00 peak) is rejected and triggers preemption."""
        day_snap = dataclasses.replace(self.healthy_snapshot, local_hour=19)
        res = evaluate_cpe_eligibility(day_snap)
        self.assertFalse(res.eligible)
        self.assertTrue(any("OUTSIDE_IDLE_WINDOW" in r for r in res.reasons))
        self.assertTrue(res.preemption_required)

    def test_free_ram_floor_enforced(self) -> None:
        """Verify free_ram_kb < 16384 (16 MB) fails closed."""
        at_floor = dataclasses.replace(self.healthy_snapshot, free_ram_kb=MIN_FREE_RAM_KB)
        self.assertTrue(evaluate_cpe_eligibility(at_floor).eligible)

        below_floor = dataclasses.replace(self.healthy_snapshot, free_ram_kb=MIN_FREE_RAM_KB - 1)
        res = evaluate_cpe_eligibility(below_floor)
        self.assertFalse(res.eligible)
        self.assertTrue(any("FREE_RAM_BELOW_FLOOR" in r for r in res.reasons))
        self.assertTrue(res.preemption_required)

    def test_customer_traffic_preemption(self) -> None:
        """Verify customer_kbps > threshold immediately triggers preemption."""
        busy_cpe = dataclasses.replace(self.healthy_snapshot, customer_kbps=64.5)
        res = evaluate_cpe_eligibility(busy_cpe)
        self.assertFalse(res.eligible)
        self.assertTrue(any("CUSTOMER_TRAFFIC_ACTIVE" in r for r in res.reasons))
        self.assertTrue(res.preemption_required)

    def test_sector_airtime_and_rtt_gates(self) -> None:
        """Verify high sector airtime (>25%) or p95 RTT (>15ms) blocks compute."""
        busy_sector = dataclasses.replace(
            self.healthy_snapshot, sector_airtime_pct=28.0, rtt_p95_ms=19.5
        )
        res = evaluate_cpe_eligibility(busy_sector)
        self.assertFalse(res.eligible)
        self.assertTrue(any("SECTOR_AIRTIME_HIGH" in r for r in res.reasons))
        self.assertTrue(any("RTT_P95_HIGH" in r for r in res.reasons))
        self.assertTrue(res.preemption_required)

    def test_lease_ttl_expiration_and_kill_switch(self) -> None:
        """Verify expired lease TTL and active kill switch halt execution."""
        expired = dataclasses.replace(
            self.healthy_snapshot, lease_issued_at_epoch=1000.0, lease_ttl_sec=90, now_epoch=1091.0
        )
        res_exp = evaluate_cpe_eligibility(expired)
        self.assertFalse(res_exp.eligible)
        self.assertIn("LEASE_TTL_EXPIRED", res_exp.reasons)
        self.assertTrue(res_exp.preemption_required)

        killed = dataclasses.replace(self.healthy_snapshot, kill_switch_active=True)
        res_kill = evaluate_cpe_eligibility(killed)
        self.assertFalse(res_kill.eligible)
        self.assertIn("KILL_SWITCH_ACTIVE", res_kill.reasons)
        self.assertTrue(res_kill.preemption_required)


class TestHMACJobManifestSecurity(unittest.TestCase):
    """Test cryptographic HMAC-SHA256 signing and verification of job manifests."""

    def setUp(self) -> None:
        self.secret = b"fmx-noc-hmac-secret-key-2026-test-only"

    def test_valid_manifest_signing_and_verification(self) -> None:
        """Verify a properly signed manifest validates cleanly before lease expiry."""
        manifest = create_signed_job_manifest(
            job_id="job-mc-001",
            shard_id=7,
            cpe_id="loco5ac-0xe7fa-01",
            opcode=WorkerOpCode.OP_INT_MONTE_CARLO,
            seed=0x12345678,
            iterations=50000,
            secret_key=self.secret,
            duty_pct=10,
            lease_ttl_sec=DEFAULT_LEASE_TTL_SEC,
            issued_at_epoch=2000,
        )
        ok, reason = verify_signed_job_manifest(manifest, self.secret, now_epoch=2050)
        self.assertTrue(ok)
        self.assertEqual(reason, "VALID")

    def test_tampered_manifest_rejected(self) -> None:
        """Verify modifying any manifest field invalidates the HMAC-SHA256 signature."""
        manifest = create_signed_job_manifest(
            job_id="job-mc-001",
            shard_id=1,
            cpe_id="loco5ac-0xe7fa-01",
            opcode=WorkerOpCode.OP_FNV1A_HASH_SWEEP,
            seed=42,
            iterations=10000,
            secret_key=self.secret,
            duty_pct=5,
            issued_at_epoch=2000,
        )
        tampered_iters = dataclasses.replace(manifest, iterations=999999)
        ok, reason = verify_signed_job_manifest(tampered_iters, self.secret)
        self.assertFalse(ok)
        self.assertEqual(reason, "HMAC_SIGNATURE_MISMATCH")

        ok_wrong_key, reason_key = verify_signed_job_manifest(manifest, b"wrong-key")
        self.assertFalse(ok_wrong_key)
        self.assertEqual(reason_key, "HMAC_SIGNATURE_MISMATCH")

    def test_manifest_lease_expiry_and_opcode_bounds(self) -> None:
        """Verify expired manifests and invalid opcodes/duty cycles are rejected."""
        manifest = create_signed_job_manifest(
            job_id="job-rf-002",
            shard_id=3,
            cpe_id="ltu-lite-0xae08-04",
            opcode=WorkerOpCode.OP_RF_HISTOGRAM_DIGEST,
            seed=99,
            iterations=4096,
            secret_key=self.secret,
            duty_pct=10,
            lease_ttl_sec=60,
            issued_at_epoch=5000,
        )
        ok, reason = verify_signed_job_manifest(manifest, self.secret, now_epoch=5061)
        self.assertFalse(ok)
        self.assertEqual(reason, "MANIFEST_LEASE_EXPIRED")

        with self.assertRaises(ValueError):
            create_signed_job_manifest(
                job_id="bad-op",
                shard_id=0,
                cpe_id="cpe1",
                opcode=99,  # Not in allowlist
                seed=1,
                iterations=100,
                secret_key=self.secret,
            )

        with self.assertRaises(ValueError):
            create_signed_job_manifest(
                job_id="bad-duty",
                shard_id=0,
                cpe_id="cpe1",
                opcode=WorkerOpCode.OP_INT_MONTE_CARLO,
                seed=1,
                iterations=100,
                duty_pct=50,  # Exceeds 20% hard cap
                secret_key=self.secret,
            )


class TestWorkerKernelAndCSourceSafety(unittest.TestCase):
    """Test bit-exact worker kernel verification, slice schedule, and C source invariants."""

    def test_duty_cycle_slice_schedule_and_preemption_gate(self) -> None:
        """Verify 5% and 10% slice schedules meet the <200ms preemption requirement."""
        s5 = compute_slice_schedule(5)
        self.assertEqual(s5["work_ms"], 2.5)
        self.assertEqual(s5["sleep_ms"], 47.5)
        self.assertEqual(s5["preemption_check_interval_ms"], 150.0)
        self.assertTrue(s5["meets_200ms_preemption_gate"])

        s10 = compute_slice_schedule(10)
        self.assertEqual(s10["work_ms"], 5.0)
        self.assertEqual(s10["sleep_ms"], 45.0)
        self.assertTrue(s10["meets_200ms_preemption_gate"])

    def test_deterministic_c_worker_kernels(self) -> None:
        """Verify deterministic xorshift32 kernels and bit-flip rejection."""
        for opcode in (
            WorkerOpCode.OP_INT_MONTE_CARLO,
            WorkerOpCode.OP_FNV1A_HASH_SWEEP,
            WorkerOpCode.OP_RF_HISTOGRAM_DIGEST,
        ):
            _, accum = simulate_c_worker_kernel(opcode, seed=1234567, iterations=2048)
            self.assertTrue(
                verify_worker_shard(
                    opcode=opcode, seed=1234567, iterations=2048, reported_accum=accum
                )
            )
            self.assertFalse(
                verify_worker_shard(
                    opcode=opcode, seed=1234567, iterations=2048, reported_accum=accum ^ 1
                )
            )

    def test_c_micro_worker_source_invariants(self) -> None:
        """Verify `controller/fmx_micro_worker.c` exists and contains no shell execution."""
        c_path = Path(__file__).resolve().parent.parent / "controller" / "fmx_micro_worker.c"
        self.assertTrue(c_path.is_file(), f"Missing C worker source at {c_path}")
        src = c_path.read_text(encoding="utf-8")
        self.assertIn("CLOCK_MONOTONIC", src)
        self.assertIn("nanosleep", src)
        self.assertIn("/proc/meminfo", src)
        self.assertIn("/proc/net/dev", src)
        self.assertIn("16384UL", src)
        # Ensure no shell/process execution calls exist in code
        for forbidden in ("system(", "popen(", "execl(", "execvp(", "execve("):
            self.assertNotIn(forbidden, src)


class TestFleetEconomicsAndWorkloadClassifier(unittest.TestCase):
    """Test quantitative 1,800-device fleet economics and workload GO/NO-GO rules."""

    def test_fleet_5pct_and_10pct_economics_vs_noc_server(self) -> None:
        """Verify 10% duty cycle doubles 5% throughput and NOC server wins per watt."""
        eval_5 = FleetEconomicsCalculator.evaluate_fleet(duty_pct=5)
        eval_10 = FleetEconomicsCalculator.evaluate_fleet(duty_pct=10)

        self.assertEqual(eval_5["active_cpes"], 1402)
        self.assertAlmostEqual(
            eval_10["effective_aggregate_coremark"],
            eval_5["effective_aggregate_coremark"] * 2.0,
            places=0,
        )
        # 1,403 CPEs at 10% duty cycle equal ~8.7 modern server cores for integer work
        self.assertGreater(eval_10["equivalent_modern_server_cores_int"], 5.0)
        self.assertLess(eval_10["equivalent_modern_server_cores_int"], 12.0)
        # NOC server is dramatically more energy-efficient (Gsteps/Wh) than rooftop MIPS
        self.assertGreater(
            eval_10["noc_server_energy_efficiency_gsteps_per_wh"],
            eval_10["fleet_energy_efficiency_gsteps_per_wh"] * 4.0,
        )
        # Verify hardware matrix includes all 4 target families
        self.assertEqual(
            set(HARDWARE_PROFILES.keys()),
            {
                "airos8_wa_ar9342",
                "airos8_xc_qca9558",
                "openwrt2410_ath79",
                "ltu_amesoc3_cpe",
            },
        )

    def test_workload_classifier_verdicts(self) -> None:
        """Verify GO vs CONDITIONAL_GO vs NO_GO workload classification."""
        # Crypto / LLM -> NO_GO
        v_llm, _ = FleetEconomicsCalculator.classify_workload(
            requires_fpu_or_simd=True,
            required_ram_mb=64.0,
            payload_io_kb_per_min=10.0,
            requires_edge_vantage_point=False,
            is_crypto_mining_or_llm=True,
        )
        self.assertEqual(v_llm, WorkloadVerdict.NO_GO)

        # Dense FP64 -> NO_GO (no FPU on MIPS 74Kc)
        v_fp, _ = FleetEconomicsCalculator.classify_workload(
            requires_fpu_or_simd=True,
            required_ram_mb=0.5,
            payload_io_kb_per_min=2.0,
            requires_edge_vantage_point=False,
        )
        self.assertEqual(v_fp, WorkloadVerdict.NO_GO)

        # Edge RF / Network Probing -> GO
        v_edge, _ = FleetEconomicsCalculator.classify_workload(
            requires_fpu_or_simd=False,
            required_ram_mb=0.2,
            payload_io_kb_per_min=4.0,
            requires_edge_vantage_point=True,
        )
        self.assertEqual(v_edge, WorkloadVerdict.GO)

        # Integer Monte Carlo / Conflict-Graph Shards -> CONDITIONAL_GO
        v_mc, _ = FleetEconomicsCalculator.classify_workload(
            requires_fpu_or_simd=False,
            required_ram_mb=0.25,
            payload_io_kb_per_min=1.0,
            requires_edge_vantage_point=False,
        )
        self.assertEqual(v_mc, WorkloadVerdict.CONDITIONAL_GO)


if __name__ == "__main__":
    unittest.main()
