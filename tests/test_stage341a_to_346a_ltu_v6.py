from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage341a_to_346a_ltu_v6_end_to_end() -> None:
    receipt_paths = [
        REPO_ROOT / "artifacts" / "autoresearch" / "stage341a_live_ltu110_round8_tfo_ecn.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage342a_ltu_short_queue_micro_ap_re.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage343a_ltu_ad9361_sdr_spi_registers_re.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage344a_ltu_sq_micro_ap_split_freq_pareto.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage345a_ltu_8round_champion_v6_receipt.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage346a_ltu_v6_verification_receipt.json",
    ]
    for p in receipt_paths:
        assert p.exists(), f"Missing receipt {p}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["status"] == "CONFIRMED"
        assert audit_stage_receipt_5pillars(data)["compliant"] is True

    doc_paths = [
        REPO_ROOT / "docs" / "STAGE341A_LIVE_LTU110_ROUND8_TFO_ECN.md",
        REPO_ROOT / "docs" / "STAGE342A_LTU_SHORT_QUEUE_MICRO_AP_RE.md",
        REPO_ROOT / "docs" / "STAGE343A_LTU_AD9361_SDR_SPI_REGISTERS_RE.md",
        REPO_ROOT / "docs" / "STAGE344A_LTU_SQ_MICRO_AP_SPLIT_FREQ_PARETO.md",
        REPO_ROOT / "docs" / "STAGE345A_LTU_8ROUND_CHAMPION_V6.md",
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
    assert "net.ipv4.tcp_fastopen=3" in sh_txt
    assert "net.ipv4.tcp_early_retrans=3" in sh_txt
    assert "net.ipv4.tcp_ecn=2" in sh_txt
