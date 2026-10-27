import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "re" / "dissect_stage609a_ubnt_poll_ul_slot_allocator_and_frame_efficiency_re.py"
RECEIPT = REPO_ROOT / "artifacts" / "autoresearch" / "stage609a_ubnt_poll_ul_slot_allocator_and_frame_efficiency_re.json"
DOC = REPO_ROOT / "docs" / "STAGE609A_UBNT_POLL_UL_SLOT_ALLOCATOR_AND_FRAME_EFFICIENCY_RE.md"


def test_stage609a_execution_and_receipt():
    res = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert RECEIPT.exists()
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "609A"
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0
    assert data["claim_classification"] == "CONFIRMED"


def test_stage609a_disassembly_and_live_netconf_math():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    p2 = data["live_netconf_comparison"]["panel2_guarida_82_fixed_10ms_50_50"]
    assert p2["down_dur_us"] == 4880
    assert p2["up_dur_us"] == 4370
    assert p2["cbp_dur_us"] == 180
    assert p2["ul_max_polled_stas_per_frame_0xfe"] == 5

    matrix = {row["config_id"]: row for row in data["frame_efficiency_matrix"]}
    c67 = matrix["Fixed_10ms_67_33_Candidate"]
    assert c67["down_dur_us"] == 6580
    assert c67["up_dur_us"] == 2670
    assert c67["ul_max_polled_stas_0xfe"] == 4
    assert c67["net_ul_payload_us"] == 2070
    assert c67["dl_gain_vs_current_50_50_pct"] == 34.84


def test_stage609a_doc_constraints():
    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    doc_heads = [l for l in lines if "<!-- doc-head:" in l]
    assert len(doc_heads) == 1
