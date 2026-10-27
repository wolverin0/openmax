from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage299a_to_304a_ltu_v4_end_to_end() -> None:
    receipt_paths = [
        REPO_ROOT / "artifacts" / "autoresearch" / "stage299a_live_ltu110_round6_voip_jitter.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage300a_ltu_aes_crypto_offload_re.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage301a_ltu_thermal_tcxo_iq_cal_re.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage302a_ltu_thermal_rainfade_hysteresis_pareto.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage303a_ltu_6round_champion_v4_receipt.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage304a_ltu_v4_verification_receipt.json",
    ]
    for p in receipt_paths:
        assert p.exists(), f"Missing receipt {p}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["status"] == "CONFIRMED"
        assert audit_stage_receipt_5pillars(data)["compliant"] is True

    doc_paths = [
        REPO_ROOT / "docs" / "STAGE299A_LIVE_LTU110_ROUND6_VOIP_JITTER.md",
        REPO_ROOT / "docs" / "STAGE300A_LTU_AES_CRYPTO_OFFLOAD_RE.md",
        REPO_ROOT / "docs" / "STAGE301A_LTU_THERMAL_TCXO_IQ_CAL_RE.md",
        REPO_ROOT / "docs" / "STAGE302A_LTU_THERMAL_RAINFADE_HYSTERESIS_PARETO.md",
        REPO_ROOT / "docs" / "STAGE303A_LTU_6ROUND_CHAMPION_V4.md",
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
    assert "net.ipv4.udp_rmem_min=16384" in sh_txt
    assert "target 2000us interval 40000us ecn" in sh_txt
