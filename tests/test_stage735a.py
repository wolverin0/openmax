import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "re" / "dissect_stage735a_ubnt_poll_ul_polling_and_activity_aging_re.py"
RECEIPT = REPO_ROOT / "artifacts" / "autoresearch" / "stage735a_ubnt_poll_ul_polling_and_activity_aging_re.json"
DOC = REPO_ROOT / "docs" / "STAGE735A_UBNT_POLL_UL_POLLING_AND_ACTIVITY_AGING_RE.md"


def test_stage735a_execution_and_receipt():
    res = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert RECEIPT.exists()
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "735A"
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0


def test_stage735a_activity_aging_profiles():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    profiles = {p["profile_id"]: p for p in data["aging_profiles_comparison"]}
    c3000 = profiles["Candidate_10ms_67_33_Aging_3000ms"]
    c1500 = profiles["Champion_10ms_67_33_Aging_1500ms"]
    assert c1500["wasted_empty_poll_airtime_per_frame_us"] < c3000["wasted_empty_poll_airtime_per_frame_us"]
    assert c1500["effective_active_sta_ul_payload_us"] == 1865.4


def test_stage735a_doc_constraints():
    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    doc_heads = [l for l in lines if "<!-- doc-head:" in l]
    assert len(doc_heads) == 1
