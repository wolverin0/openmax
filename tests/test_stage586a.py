import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage586a_files_and_schema():
    script = ROOT / "tools" / "firmware" / "build_stage586a_wmi_peer_phymode_sync_guard_and_ptp_v3_kit.py"
    helper = ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-wa-ptp-champion-v3"
    guard = ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "fmx_wmi_peer_phymode_sync_guard.sh"
    artifact = ROOT / "artifacts" / "autoresearch" / "stage586a_wmi_peer_phymode_sync_guard_and_ptp_v3_kit.json"
    doc = ROOT / "docs" / "STAGE586A_WMI_PEER_PHYMODE_SYNC_GUARD_AND_PTP_V3_KIT.md"
    assert script.exists()
    assert helper.exists()
    assert guard.exists()
    assert artifact.exists()
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
    data = json.loads(artifact.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 586A"
    assert data["status"] == "CONFIRMED"
    assert data["deployed_on_241_and_242"] is True
