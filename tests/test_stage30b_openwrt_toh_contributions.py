import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT_MD = ROOT / "artifacts" / "hyperresearch_vault" / "notes" / "openwrt_toh_ubiquiti_audit.md"
WIKI_MD = ROOT / "docs" / "OPENWRT_WIKI_UPSTREAM_CONTRIBUTIONS.md"
RECEIPT_JSON = ROOT / "artifacts" / "autoresearch" / "stage30b_openwrt_toh_audit_and_contributions_20261025.json"


def test_stage30b_files_exist_and_non_empty():
    for path in (AUDIT_MD, WIKI_MD, RECEIPT_JSON):
        assert path.exists(), f"Missing required deliverable: {path}"
        assert path.stat().st_size > 500, f"Deliverable too small: {path}"


def test_stage30b_toh_audit_covers_all_8_fleet_families():
    text = AUDIT_MD.read_text(encoding="utf-8")
    required_tokens = [
        "0xe8e5",            # LAP-120
        "0xe7fa",            # NanoStation 5AC Loco
        "0xe7f9",            # LiteBeam 5AC Gen2 & Rocket Prism 5AC Gen2
        "0xe7f7",            # Rocket 2AC Prism
        "0xe4e5",            # PowerBeam M5-400
        "0xe3e5",            # PowerBeam M5-300
        "0xe0a2",            # NanoStation Loco M2 XM
        "0xae08",            # LTU-Lite
        "0xeb00",            # LTU-Rocket
        "bebc7c08",          # board-2.bin CRC32
        "0x3e2d",            # LAP-120 pre-cal checksum
        "0x2292",            # NS-5ACL pre-cal checksum
        "0x13b5",            # LBE-5AC-Gen2 pre-cal checksum
        "MX25L12805D",       # 16 MiB SPI NOR flash
        "fwupdate.real",     # Stock downgrade/unlock mechanism
        "535.000 MHz",       # Measured AR9342 clock vs 533/560 MHz ToH claims
    ]
    for token in required_tokens:
        assert token in text, f"Missing expected hardware verification token '{token}' in {AUDIT_MD}"


def test_stage30b_dokuwiki_upstream_contributions_cover_all_4_topics():
    wiki = WIKI_MD.read_text(encoding="utf-8")
    # (a) AirOS 8 4-addr WDS ETH_P_TEB 0x6558
    assert "ETH_P_TEB" in wiki and "0x6558" in wiki
    assert "ieee80211_data_to_8023_exthdr" in wiki
    assert "allow_80211" in wiki and "ubnt_op_mode" in wiki
    # (b) QCA988x + AR9342 AQL 1000/2000 us & 2-MTU fq_codel quantum=3028 (-38% p95)
    assert "aql_txq_limit" in wiki and "1000 2000" in wiki
    assert "quantum 3028" in wiki and "-38%" in wiki
    # (c) Missing hardware/partition/AirPrism airview1 specs for RP-5AC-Gen2 (e7f9) & R2AC-Prism (e7f7)
    assert "QCA9558" in wiki and "airview1" in wiki
    assert "0xe7f9" in wiki and "0xe7f7" in wiki
    # (d) LTU Cyclone V SoC + ame_core FPGA baseband
    assert "Cyclone V" in wiki and "ame_core.ko" in wiki
    assert "0xae08" in wiki and "0xeb00" in wiki


def test_stage30b_receipt_json_schema_and_metrics():
    data = json.loads(RECEIPT_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "30B"
    assert data["task_id"] == "T-S30B-OPENWRT-UBIQUITI-TOH-INGEST-AND-UPSTREAM-WIKI-CONTRIBUTIONS"
    assert len(data["scraped_openwrt_toh_urls"]) >= 8
    assert len(data["fleet_toh_audit"]) == 8
    assert len(data["upstream_dokuwiki_sections"]) == 4

    section_ids = {s["section_id"] for s in data["upstream_dokuwiki_sections"]}
    assert section_ids == {
        "airos8_wds_eth_p_teb_0x6558",
        "qca988x_ar9342_aql_fq_codel",
        "rocket_prism_5ac_gen2_and_2ac_prism_specs",
        "ltu_cyclone_v_fpga_and_xw_eth_split",
    }

    aql_sec = next(
        s for s in data["upstream_dokuwiki_sections"]
        if s["section_id"] == "qca988x_ar9342_aql_fq_codel"
    )
    assert aql_sec["measured_impact"]["p95_latency_delta_pct"] == -38.0
    assert aql_sec["measured_impact"]["fq_codel_quantum_ptp_bytes"] == 3028
