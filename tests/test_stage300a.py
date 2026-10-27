from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S300A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage300a_ltu_aes_crypto_offload_re.json"
S300A_MD = REPO_ROOT / "docs" / "STAGE300A_LTU_AES_CRYPTO_OFFLOAD_RE.md"


def test_stage300a_ltu_aes_crypto_offload_re() -> None:
    assert S300A_JSON.exists()
    assert S300A_MD.exists()
    data = json.loads(S300A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "300A"
    assert data["safety_envelope"]["touched_dev_ame_nodes"] is False
    assert data["aes_encryption_engine_architecture"]["extracted_crypto_and_security_symbols_count"] > 10
    lines = S300A_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
