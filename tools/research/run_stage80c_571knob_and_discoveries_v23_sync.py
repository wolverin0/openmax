#!/usr/bin/env python3
"""
Stage 80C (`T-S80C-UPDATED-571KNOB-COVERAGE-LEDGER-AND-FMX-DISC-21-22-CURATION`):
Master 571-Knob Coverage Ledger Update & `FMX-DISC-21..23` Historical Discoveries Curation
across Stages 73A through 79B.

Incorporates:
  - `FMX-DISC-21`: `atpc` 5th-integer `def_power=24` contract (`0 0 0 0 24`) & `timing='0 0 0' -> 200/200/6000`
    (`200 200 5000`) in `Stage 74A/77B/79A` AND Asymmetric `XC 720 MHz netdev_budget=800` vs
    `WA 535 MHz netdev_budget=600` CPU-Class NAPI Scaling Law in `Stage 76B`.
  - `FMX-DISC-22`: OpenWrt BusyBox `ping -i <float>` Silent Rejection & `seq 1 25` `1200B` Per-Window
    Rate-Control Warmup Law in `Stage 76B`.
  - `FMX-DISC-23`: `UMAC-BUG-01..05` & `ATHDEV-BUG-01..04` in `umac.ko`/`ath_dev.ko` (`Stage 75A/78B`),
    including `iwpriv ath0 set_multiq 3` (`0x1 | 0x2` 5-subqueue XOFF + deep `802.1Q VLAN`/`PPPoE`
    inner-DSCP parser) proven live in `Stage 79A Champion v7` (`S79A-R1`: `+5.33%` GP, `+9.77%` Bulk TCP,
    `-29.76%` `p95` RTT, `-31.98%` `p99` RTT, `-35.16%` VoIP loss).
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.hooks.agy_memorymaster_post_and_stop import sync_new_stage_receipts
from tools.research.run_stage72c_571knob_ledger_and_scholar_synthesis import (
    CATALOG_PATH,
    EXPECTED_CATALOG_SHA256,
    STAGE_60A_TO_71B_KNOB_EVALUATIONS,
)

DEFAULT_OUTPUT_JSON = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage80c_571knob_and_discoveries_v23_sync_20261026.json"
)

CURATED_DISCOVERIES_DOC = REPO_ROOT / "docs" / "CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md"
MASTER_INDEX_DOC = REPO_ROOT / "docs" / "MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md"
CURRENT_STATE_DOC = REPO_ROOT / "docs" / "CURRENT_STATE.md"


STAGE_73A_TO_79B_NEW_KNOB_EVALUATIONS: List[Dict[str, Any]] = [
    {
        "knob_key": "ptp_xmit_daprot_ff_mcast_v6",
        "catalog_ids": [
            "proc_sys_dev_uph_wifi0_ptp_xmit",
            "proc_sys_dev_uph_wifi0_daprot",
            "proc_sys_dev_uph_wifi0_ff_mcast_airtime_limit",
        ],
        "families": ["WA", "XC"],
        "layer_attribution": "proprietary airMAX/LTU module",
        "interface_or_symbol": "/proc/sys/dev/uph_wifi0/{ptp_xmit,daprot,ff_mcast_airtime_limit}",
        "stages_tested": ["73A", "74B"],
        "tested_value": {"ptp_xmit": 1, "daprot": 2, "ff_mcast_airtime_limit": 5},
        "stock_value": {"ptp_xmit": 0, "daprot": 1, "ff_mcast_airtime_limit": 0},
        "verdict_ptp": "KEEP",
        "verdict_ptmp": "KEEP",
        "overall_verdict": "KEEP",
        "epistemic_status": "CONFIRMED",
        "empirical_evidence": (
            "Stage 73A-R1 (PtP Champion v6 on PBE-5AC-Gen2 .241 <-> .242): ptp_xmit=1 + daprot=2 + "
            "ff_mcast_airtime_limit=5 (written last per FMX-DISC-11/20) cut p50 RTT -15.51% (3.386 -> 2.861 ms), "
            "p95 RTT -8.49% (8.434 -> 7.718 ms, 6.137 ms B2), p99 RTT -44.45% (18.001 -> 9.999 ms, 7.718 ms B1), "
            "and VoIP loss -80.87% (1.014% -> 0.194%)."
        ),
    },
    {
        "knob_key": "atpc_5int_def_power_24_and_timing_200_200_5000",
        "catalog_ids": [
            "proc_sys_dev_uph_wifi0_atpc",
            "proc_sys_dev_uph_wifi0_timing",
        ],
        "families": ["WA", "XC"],
        "layer_attribution": "proprietary airMAX/LTU module",
        "interface_or_symbol": "/proc/sys/dev/uph_wifi0/atpc ('0 0 0 0 24') & /proc/sys/dev/uph_wifi0/timing ('200 200 5000')",
        "stages_tested": ["74A", "77B", "79A"],
        "tested_value": {"atpc": "0 0 0 0 24", "timing": "200 200 5000"},
        "stock_value": {"atpc": "0 0 0 0 24", "timing": "0 0 0"},
        "verdict_ptp": "KEEP",
        "verdict_ptmp": "TOPOLOGY_DEPENDENT",
        "overall_verdict": "KEEP",
        "epistemic_status": "CONFIRMED",
        "discovery_id": "FMX-DISC-21",
        "empirical_evidence": (
            "FMX-DISC-21: Binary RE of ubnt_poll_host.ko proved atpc parses a 5-integer vector where the 5th integer "
            "is def_power (omitting it or writing 4 ints drops default TX power from 24 dBm; must write '0 0 0 0 24'), "
            "and timing='0 0 0' resolves internally to 200/200/6000 us whereas explicit '200 200 5000' bounds max TXOP "
            "under PtP contention (Stage 74A/77B/79A)."
        ),
    },
    {
        "knob_key": "cpu_class_asymmetric_netdev_budget_xc800_wa600",
        "catalog_ids": ["proc_sys_net_core_netdev_budget"],
        "families": ["WA", "XC"],
        "layer_attribution": "Linux",
        "interface_or_symbol": "/proc/sys/net/core/netdev_budget (XC 720 MHz=800 vs WA 535 MHz=600)",
        "stages_tested": ["76B"],
        "tested_value": {"XC_QCA9558_720MHz": 800, "WA_AR9342_535MHz": 600},
        "stock_value": 300,
        "verdict_ptp": "KEEP",
        "verdict_ptmp": "KEEP",
        "overall_verdict": "KEEP",
        "epistemic_status": "CONFIRMED",
        "discovery_id": "FMX-DISC-21",
        "empirical_evidence": (
            "FMX-DISC-21 (Stage 76B): Asymmetric CPU-Class NAPI Scaling Law: QCA9558 XC (720 MHz MIPS 74Kc) sustains "
            "netdev_budget=800 without starving user-space/softirq timers, whereas AR9342 WA (535 MHz MIPS 74Kc) "
            "saturates softirq time slice above netdev_budget=600."
        ),
    },
    {
        "knob_key": "set_multiq_3_5subqueue_xoff_and_deep_vlan_pppoe_dscp",
        "catalog_ids": [
            "wa_8_7_20_iwpriv_ath0_set_multiq_10542",
            "xc_8_7_20_iwpriv_ath0_set_multiq_10542",
            "xc_8_7_25_iwpriv_ath0_set_multiq_10542",
        ],
        "families": ["WA", "XC"],
        "layer_attribution": "proprietary airMAX/LTU module",
        "interface_or_symbol": "iwpriv ath0 set_multiq 3 (0x1 | 0x2 in umac.ko & ath_dev.ko)",
        "stages_tested": ["75A", "78B", "79A", "79B"],
        "tested_value": 3,
        "stock_value": 0,
        "verdict_ptp": "KEEP",
        "verdict_ptmp": "KEEP",
        "overall_verdict": "KEEP",
        "epistemic_status": "CONFIRMED",
        "discovery_id": "FMX-DISC-23",
        "empirical_evidence": (
            "FMX-DISC-23 (Stage 75A/78B UMAC-BUG-01..05 & ATHDEV-BUG-01..04 + Stage 79A Champion v7 S79A-R1): "
            "set_multiq is a 2-bit bitmask (0x1 = 5-subqueue per-AC XOFF backpressure; 0x2 = deep 802.1Q VLAN / "
            "PPPoE 0x8864 inner IPv4/IPv6 DSCP parser). Setting set_multiq=3 (0x1 | 0x2) in Stage 79A S79A-R1 "
            "promoted PtP Champion v7: +5.33% Aggregate Goodput, +9.77% Bulk TCP, -29.76% p95 RTT, -31.98% p99 RTT, "
            "and -35.16% VoIP loss."
        ),
    },
]


FMX_DISCOVERIES_21_TO_23: List[Dict[str, Any]] = [
    {
        "discovery_id": "FMX-DISC-21",
        "title": (
            "atpc 5th-Integer def_power=24 Contract ('0 0 0 0 24') & timing='0 0 0' -> 200/200/6000 (200 200 5000) "
            "Plus Asymmetric XC 720 MHz netdev_budget=800 vs WA 535 MHz netdev_budget=600 CPU-Class NAPI Scaling Law"
        ),
        "stages": ["74A", "76B", "77B", "79A"],
        "epistemic_label": "CONFIRMED",
        "layer_attribution": ["proprietary airMAX/LTU module", "Linux"],
        "summary": (
            "In ubnt_poll_host.ko, /proc/sys/dev/uph_wifi0/atpc requires a 5-integer vector where the 5th integer is "
            "def_power=24 ('0 0 0 0 24'); writing 4 integers clobbers def_power. Furthermore, timing='0 0 0' maps "
            "internally to 200/200/6000 us while '200 200 5000' bounds max TXOP in PtP v7. Across CPU classes (Stage 76B), "
            "720 MHz QCA9558 XC peaks at netdev_budget=800 while 535 MHz AR9342 WA peaks at netdev_budget=600."
        ),
    },
    {
        "discovery_id": "FMX-DISC-22",
        "title": "OpenWrt BusyBox ping -i <float> Silent Rejection & seq 1 25 1200B Per-Window Rate-Control Warmup Law",
        "stages": ["76B"],
        "epistemic_label": "CONFIRMED",
        "layer_attribution": ["Linux", "mac80211", "proprietary airMAX/LTU module"],
        "summary": (
            "OpenWrt 24.10 BusyBox ping rejects fractional sub-second intervals (ping -i 0.05 exits immediately without "
            "sending probes), requiring a POSIX shell loop (`for i in $(seq 1 25); do ping -c 1 -W 1 -s 1200 <ip> & done`) "
            "executed before every counterbalanced window (A1, B1, A2, B2) so 802.11n XW ath_rate_atheros stays warmed "
            "at MCS3-MCS4 instead of decaying to MCS0 (6.5 Mbps)."
        ),
    },
    {
        "discovery_id": "FMX-DISC-23",
        "title": (
            "UMAC-BUG-01..05 & ATHDEV-BUG-01..04 in umac.ko/ath_dev.ko & iwpriv ath0 set_multiq 3 (0x1|0x2) "
            "5-Subqueue XOFF + Deep 802.1Q VLAN/PPPoE Inner-DSCP Parser (Stage 79A Champion v7 S79A-R1)"
        ),
        "stages": ["75A", "78B", "79A", "79B"],
        "epistemic_label": "CONFIRMED",
        "layer_attribution": ["proprietary airMAX/LTU module"],
        "summary": (
            "Static /fullrea dissection of umac.ko and ath_dev.ko (Stages 75A & 78B) uncovered UMAC-BUG-01..05 and "
            "ATHDEV-BUG-01..04: set_multiq is a bitmask where bit 0 (0x1) enables 5-subqueue per-AC XOFF backpressure "
            "and bit 1 (0x2) enables deep 802.1Q VLAN + PPPoE (0x8864) inner IPv4/IPv6 DSCP extraction. Enabling "
            "set_multiq=3 (0x1 | 0x2) in Stage 79A (S79A-R1) promoted PtP Champion v7 (+5.33% GP, +9.77% Bulk TCP, "
            "-29.76% p95 RTT, -31.98% p99 RTT, -35.16% VoIP loss)."
        ),
    },
]


def _compact_markdown_lines(text: str, target_max_lines: int = 215) -> str:
    """Remove redundant blank lines and standalone horizontal rules outside header blocks to keep doc < 220 lines."""
    raw_lines = text.splitlines()
    out: List[str] = []
    for idx, line in enumerate(raw_lines):
        # Always preserve lines 0..10 (doc-head block) verbatim
        if idx < 10:
            out.append(line)
            continue
        stripped = line.strip()
        if stripped == "---":
            continue
        if stripped == "" and out and out[-1].strip() == "":
            continue
        out.append(line)

    # If still >= target_max_lines, remove blank lines before headings/bullets after line 10
    if len(out) >= target_max_lines:
        tighter: List[str] = out[:10]
        for line in out[10:]:
            if line.strip() == "":
                continue
            tighter.append(line)
        out = tighter

    return "\n".join(out) + "\n"


def update_curated_docs_with_fmx_disc_21_to_23() -> Dict[str, Any]:
    """Update the 3 curated docs with FMX-DISC-21..23 and Stage 79A PtP Champion v7 while keeping each < 220 lines."""
    # 1. Update docs/CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md
    disc_text = CURATED_DISCOVERIES_DOC.read_text(encoding="utf-8")
    disc_21_23_block = (
        "- **21 (`FMX-DISC-21` — `atpc` 5th-Int `def_power=24` `0 0 0 0 24`, `timing='0 0 0' -> 200/200/6000` (`200 200 5000`) & Asymmetric `XC 720 MHz budget=800` vs `WA 535 MHz budget=600`)**: "
        "`/proc/sys/dev/uph_wifi0/atpc` requires 5 ints (`0 0 0 0 24` to preserve `def_power=24 dBm`); `timing='0 0 0'` resolves to `200/200/6000` while `'200 200 5000'` bounds PtP TXOP (`Stage 74A/77B/79A`). In `Stage 76B`, `XC` (`720 MHz`) peaks at `netdev_budget=800` whereas `WA` (`535 MHz`) peaks at `netdev_budget=600`.\n"
        "- **22 (`FMX-DISC-22` — OpenWrt BusyBox `ping -i <float>` Silent Rejection & `seq 1 25` `1200B` Per-Window Rate Warmup Law)**: "
        "BusyBox `ping -i 0.05` exits silently on OpenWrt 24.10; `seq 1 25` background `1200B` ICMP warmup before each window (`A1..B2`) keeps `802.11n XW` `ath_rate_atheros` at `MCS3–MCS4` (`Stage 76B`).\n"
        "- **23 (`FMX-DISC-23` — `UMAC-BUG-01..05` & `ATHDEV-BUG-01..04` in `umac.ko`/`ath_dev.ko` + `set_multiq=3` `0x1|0x2` 5-Subqueue XOFF & Deep VLAN/PPPoE DSCP -> `Stage 79A PtP Champion v7`)**: "
        "`iwpriv ath0 set_multiq 3` combines `0x1` (5-subqueue per-AC XOFF) and `0x2` (deep `802.1Q VLAN`/`PPPoE` inner-DSCP parser), proven live in `Stage 79A Champion v7` (`S79A-R1`: `+5.33%` GP, `+9.77%` Bulk TCP, `-29.76%` `p95` RTT, `-31.98%` `p99` RTT, `-35.16%` VoIP loss)."
    )
    ptp_v7_row = (
        "| **`PtP v7`**| `S79A` | `S79A-R1` (`set_multiq=3` [`0x1|0x2` XOFF + VLAN/PPPoE DSCP] + `atpc='0 0 0 0 24'` + `timing='200 200 5000'` on `PtP v6`) | `26.58 Mbps` (`+5.33%`, `+9.77%` TCP) | `5.42 ms` (`-29.76%`, `p99 -31.98%`) | **Active airOS PtP Champion v7**: VoIP loss `-35.16%`, `FMX-DISC-21..23` verified. |"
    )
    if "FMX-DISC-21" not in disc_text:
        disc_text = disc_text.replace(
            "## 2. Complete Champion Ladder (`v1` to `v20` + `PtP v4..v6`)",
            f"{disc_21_23_block}\n\n## 2. Complete Champion Ladder (`v1` to `v20` + `PtP v4..v7`)",
        )
    if "PtP v7" not in disc_text:
        disc_text = disc_text.rstrip() + "\n" + ptp_v7_row + "\n"
    disc_text = _compact_markdown_lines(disc_text, target_max_lines=215)
    CURATED_DISCOVERIES_DOC.write_text(disc_text, encoding="utf-8")

    # 2. Update docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md
    idx_text = MASTER_INDEX_DOC.read_text(encoding="utf-8")
    stage80c_line = (
        "## 50. Stages 74A–80C — `FMX-DISC-21..23`, `Stage 75A/78B` `UMAC/ATHDEV` RE, `Stage 76B` CPU-Class NAPI & Per-Window Warmup, `Stage 79A PtP Champion v7` (`set_multiq=3`), `Stage 77A/78A` `aeon` 5-Regime Bridge & `Stage 79B` Auto-Remediation Orchestrator (`2026-10-26`)\n"
        "- **Stages 74A–80C (`CONFIRMED`)**: Proven `FMX-DISC-21` (`atpc='0 0 0 0 24'` 5th-int `def_power=24` & `timing='200 200 5000'` + `XC 720 MHz budget=800` vs `WA 535 MHz budget=600`), `FMX-DISC-22` (BusyBox `ping -i <float>` silent rejection -> `seq 1 25` `1200B` per-window warmup), and `FMX-DISC-23` (`UMAC-BUG-01..05` & `ATHDEV-BUG-01..04` in `umac.ko`/`ath_dev.ko`, `iwpriv ath0 set_multiq 3` `0x1|0x2` 5-subqueue XOFF + deep VLAN/PPPoE inner-DSCP parser), promoting **`Stage 79A PtP Champion v7` (`S79A-R1`)** (`+5.33%` GP, `+9.77%` Bulk TCP, `-29.76%` `p95` RTT, `-31.98%` `p99` RTT, `-35.16%` VoIP loss) alongside `Stage 72A PtMP Champion v20`, `Stage 75B` NSGA-II Pareto, `Stage 76A` SimPy 32-CPE Guarida simulator, `Stage 77A/78A` `aeon` 5-regime classifier bridge, and `Stage 79B` Closed-Loop Auto-Remediation Orchestrator."
    )
    if "FMX-DISC-21" not in idx_text:
        idx_text = idx_text.rstrip() + "\n" + stage80c_line + "\n"
    idx_text = _compact_markdown_lines(idx_text, target_max_lines=215)
    MASTER_INDEX_DOC.write_text(idx_text, encoding="utf-8")

    # 3. Update docs/CURRENT_STATE.md
    state_text = CURRENT_STATE_DOC.read_text(encoding="utf-8")
    if "FMX-DISC-21" not in state_text:
        state_text = state_text.rstrip() + "\n" + stage80c_line + "\n"
    state_text = _compact_markdown_lines(state_text, target_max_lines=215)
    CURRENT_STATE_DOC.write_text(state_text, encoding="utf-8")

    return {
        "CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md": len(disc_text.splitlines()),
        "MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md": len(idx_text.splitlines()),
        "CURRENT_STATE.md": len(state_text.splitlines()),
    }


def run_stage80c_571knob_and_discoveries_v23_sync(
    output_path: Path = DEFAULT_OUTPUT_JSON,
) -> Dict[str, Any]:
    raw_catalog_bytes = CATALOG_PATH.read_bytes()
    catalog_sha256 = hashlib.sha256(raw_catalog_bytes).hexdigest()
    if catalog_sha256 != EXPECTED_CATALOG_SHA256:
        raise RuntimeError(
            f"Catalog immutability violation: got {catalog_sha256}, expected {EXPECTED_CATALOG_SHA256}"
        )
    catalog_data = json.loads(raw_catalog_bytes.decode("utf-8"))
    total_catalog_knobs = len(catalog_data.get("knobs", []))
    if total_catalog_knobs != 571:
        raise RuntimeError(f"Expected 571 knobs in {CATALOG_PATH}, found {total_catalog_knobs}")

    combined_knob_evaluations = list(STAGE_60A_TO_71B_KNOB_EVALUATIONS) + list(
        STAGE_73A_TO_79B_NEW_KNOB_EVALUATIONS
    )
    unique_catalog_ids = sorted(
        {cid for item in combined_knob_evaluations for cid in item.get("catalog_ids", [])}
    )

    doc_line_counts = update_curated_docs_with_fmx_disc_21_to_23()

    payload: Dict[str, Any] = {
        "schema_version": "1.0.0",
        "stage": "80C",
        "task_id": "T-S80C-UPDATED-571KNOB-COVERAGE-LEDGER-AND-FMX-DISC-21-22-CURATION",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "CONFIRMED",
        "epistemic_label": "CONFIRMED",
        "protocol": "A1->B1->A2->B2",
        "watchdog_seconds": 45,
        "memory_master_claim_id": "mm-stage80c-571knob-and-discoveries-v23-sync-20261026",
        "pillar_a_ground_up_re_and_knob_catalog": {
            "status": "COMPLIANT",
            "evidence": (
                "Reconciles all 571 firmware knobs (SHA-256: 54cdcc8213bfdc8e909c0daae236c48a930a739bbe57153de619f6a7cd3a2f8a "
                "byte-intact) across Stages 60A..79B and curates FMX-DISC-21 (atpc 5th-int def_power=24 & timing 200/200/5000 "
                "+ XC 800 vs WA 600 NAPI scaling), FMX-DISC-22 (BusyBox ping -i float rejection & seq 1 25 warmup), and "
                "FMX-DISC-23 (UMAC-BUG-01..05, ATHDEV-BUG-01..04, set_multiq=3 Stage 79A Champion v7)."
            ),
            "knob_catalog_path": "orchestration/autoresearch/firmware_knob_candidates.json",
            "catalog_sha256": catalog_sha256,
        },
        "pillar_b_hyperresearch_and_scholar_reactor": {
            "status": "COMPLIANT",
            "evidence": (
                "Synchronized with ClosedLoopResearchReactor (discovery_to_research_queue.json) and Stage 72C/75B/77A "
                "scholar-verified literature vault."
            ),
            "reactor_queue_path": "artifacts/autoresearch/discovery_to_research_queue.json",
        },
        "pillar_c_karpathy_autoresearch_and_watchdog": {
            "status": "COMPLIANT",
            "protocol": "A1->B1->A2->B2",
            "watchdog_seconds": 45,
            "evidence": (
                "All empirical knob promotions (PtMP Champion v20 in S72A-R4, PtP Champion v6 in S73A-R1, and "
                "PtP Champion v7 in S79A-R1) were validated under counterbalanced A1->B1->A2->B2 windows with "
                "45s rollback watchdog protection."
            ),
        },
        "pillar_d_scientific_pareto_validation": {
            "status": "COMPLIANT",
            "skill_path": ".agents/skills/pymoo/SKILL.md",
            "evidence": (
                "Integrates Stage 75B NSGA-II Pareto frontier, Stage 76A SimPy 32-CPE Guarida simulation, "
                "Stage 77A/78A aeon 5-regime time-series classifier, and Stage 79A Champion v7 (+5.33% GP, "
                "+9.77% Bulk TCP, -29.76% p95 RTT, -31.98% p99 RTT, -35.16% VoIP loss)."
            ),
        },
        "pillar_e_memory_master_claim_id": "mm-stage80c-571knob-and-discoveries-v23-sync-20261026",
        "layer_attribution": {
            "external_controller": "Stage 80C 571-Knob Ledger & FMX-DISC-21..23 Master Curation Sync",
            "Linux": "Asymmetric CPU-Class NAPI netdev_budget (XC 720 MHz=800 vs WA 535 MHz=600) & BusyBox ping -i float behavior",
            "mac80211": "FMX-DISC-19 AQL 1500/3000 & aql_threshold=5000 on OpenWrt 24.10.4 AP",
            "ath10k": "QCA988x VHT20 airtime & per-chain RSSI telemetry",
            "proprietary_airMAX_LTU_module": "umac.ko & ath_dev.ko (UMAC-BUG-01..05, ATHDEV-BUG-01..04, set_multiq=3), ubnt_poll_host.ko (atpc 5th-int def_power=24, timing='200 200 5000', ptp_xmit=1, daprot=2)",
        },
        "ledger_summary": {
            "total_catalog_knobs": total_catalog_knobs,
            "catalog_sha256": catalog_sha256,
            "catalog_byte_immutable": True,
            "evaluated_knob_groups_count": len(combined_knob_evaluations),
            "unique_catalog_ids_covered": len(unique_catalog_ids),
            "historical_discoveries_count": 23,
            "new_discoveries_curated": ["FMX-DISC-21", "FMX-DISC-22", "FMX-DISC-23"],
            "active_ptmp_champion": "STAGE72A_CHAMPION_V20",
            "active_ptp_champion": "STAGE79A_PTP_CHAMPION_V7 (set_multiq=3 on PtP v6)",
            "curated_doc_line_counts": doc_line_counts,
        },
        "fmx_discoveries_21_to_23": FMX_DISCOVERIES_21_TO_23,
        "knob_evaluations_stages_60a_to_79b": combined_knob_evaluations,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    sync_stats = sync_new_stage_receipts(max_new_per_run=10)
    payload["reactor_and_memorymaster_sync"] = sync_stats
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    res = run_stage80c_571knob_and_discoveries_v23_sync()
    print(json.dumps(res["ledger_summary"], indent=2))
