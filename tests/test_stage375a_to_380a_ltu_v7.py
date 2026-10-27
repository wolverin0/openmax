from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage375a_to_380a_ltu_v7_end_to_end() -> None:
    receipt_paths = [
        REPO_ROOT / "artifacts" / "autoresearch" / "stage375a_live_ltu110_round9_smp_hrtimer.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage376a_ltu_rocket_arria10_fpga_mailbox_re.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage377a_ltu_subband_cinr_puncturing_re.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage378a_ltu_subband_puncturing_pareto.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage379a_ltu_9round_champion_v7_receipt.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage380a_ltu_v7_verification_receipt.json",
    ]
    for p in receipt_paths:
        assert p.exists(), f"Missing receipt {p}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["status"] == "CONFIRMED"
        assert audit_stage_receipt_5pillars(data)["compliant"] is True

    doc_paths = [
        REPO_ROOT / "docs" / "STAGE375A_LIVE_LTU110_ROUND9_SMP_HRTIMER.md",
        REPO_ROOT / "docs" / "STAGE376A_LTU_ROCKET_ARRIA10_FPGA_MAILBOX_RE.md",
        REPO_ROOT / "docs" / "STAGE377A_LTU_SUBBAND_CINR_PUNCTURING_RE.md",
        REPO_ROOT / "docs" / "STAGE378A_LTU_SUBBAND_PUNCTURING_PARETO.md",
        REPO_ROOT / "docs" / "STAGE379A_LTU_9ROUND_CHAMPION_V7.md",
    ]
    for dp in doc_paths:
        assert dp.exists(), f"Missing doc {dp}"
        lines = dp.read_text(encoding="utf-8").splitlines()
        assert len(lines) < 220, f"{dp} exceeds 220 lines"
        assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1

    champ_sh = REPO_ROOT / "firmware" / "ltu_safe_kit" / "rc.poststart_ltu_safe_champion.sh"
    sh_txt = champ_sh.read_text(encoding="utf-8")
    assert "\r\n" not in sh_txt
    assert "/dev/ame" not in sh_txt
    assert "kernel.sched_rt_runtime_us=980000" in sh_txt
    assert "kernel.sched_min_granularity_ns=1500000" in sh_txt
    assert "net.ipv4.tcp_autocorking=0" in sh_txt
