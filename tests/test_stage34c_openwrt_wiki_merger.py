from pathlib import Path
import pytest

from tools.build_command_center_html import build_html
from tools.wiki.openwrt_dokuwiki_safe_section_merger import (
    CURATED_DOKUWIKI_SECTIONS,
    MAX_SECTION_LINES,
    generate_stage34c_wiki_and_panel_receipt,
    merge_dokuwiki_section_idempotent,
    validate_dokuwiki_section_budget_and_syntax,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
STAGE34C_JSON = (
    ROOT_DIR
    / "artifacts"
    / "autoresearch"
    / "stage34c_openwrt_dokuwiki_merger_and_openwisp_panel_20261025.json"
)
STAGE34C_DOC = ROOT_DIR / "docs" / "STAGE34C_OPENWRT_WIKI_MERGER_AND_OPENWISP_DASHBOARD_PANEL.md"


def test_stage34c_all_5_curated_sections_within_25_line_budget():
    expected_pages = {
        "toh:ubiquiti:liteap_ac",
        "toh:ubiquiti:nanostation_5ac_loco",
        "toh:ubiquiti:litebeam_5ac_gen2",
        "toh:ubiquiti:rocket_5ac_prism",
        "toh:ubiquiti:start",
    }
    assert set(CURATED_DOKUWIKI_SECTIONS.keys()) == expected_pages

    for page_id, spec in CURATED_DOKUWIKI_SECTIONS.items():
        res = validate_dokuwiki_section_budget_and_syntax(spec.section_dokuwiki)
        assert res["valid"] is True
        assert res["line_count"] <= MAX_SECTION_LINES, f"{page_id} exceeded 25-line budget"


def test_stage34c_budget_and_syntax_validator_rejects_violations():
    too_long = "===== Heading =====\n" + "\n".join(f"line {i}" for i in range(30))
    with pytest.raises(ValueError, match="25-line budget"):
        validate_dokuwiki_section_budget_and_syntax(too_long)

    unbalanced_code = "===== Heading =====\n<code bash>\necho 1\n"
    with pytest.raises(ValueError, match="Unbalanced <code>"):
        validate_dokuwiki_section_budget_and_syntax(unbalanced_code)

    broken_table = "===== Heading =====\n| col1 | col2 \n"
    with pytest.raises(ValueError, match="Malformed DokuWiki table"):
        validate_dokuwiki_section_budget_and_syntax(broken_table)


def test_stage34c_idempotent_merge_and_table_preservation():
    raw_page = (
        "====== Ubiquiti LiteAP AC ======\n"
        "^ SoC ^ AR9342 ^\n"
        "| Flash | 16 MiB |\n"
        "===== External links =====\n"
        "  * https://ui.com\n"
    )
    first = merge_dokuwiki_section_idempotent(raw_page, "toh:ubiquiti:liteap_ac")
    assert first["action"] == "INSERTED_NEW_SECTION"
    assert first["changed"] is True
    assert "@@" in first["unified_diff"]
    # Verify table precedes a blank line before our inserted heading, and External links remains at end
    merged_text = first["merged_text"]
    assert "| Flash | 16 MiB |\n\n===== AirOS 8 WDS" in merged_text
    assert merged_text.strip().endswith("* https://ui.com")

    # Second pass must be strictly idempotent (no duplicate section, no diff)
    second = merge_dokuwiki_section_idempotent(merged_text, "toh:ubiquiti:liteap_ac")
    assert second["action"] == "UNCHANGED_IDEMPOTENT"
    assert second["changed"] is False
    assert second["unified_diff"] == ""
    assert second["merged_text"] == merged_text


def test_stage34c_receipt_and_command_center_panel():
    receipt = generate_stage34c_wiki_and_panel_receipt()
    assert receipt["stage"] == "34C"
    assert receipt["pages_count"] == 5
    assert receipt["all_idempotent_verified"] is True
    assert STAGE34C_JSON.exists()
    assert STAGE34C_DOC.exists()

    html_path = build_html()
    html_text = html_path.read_text(encoding="utf-8")
    assert "OpenWISP NetJSON & Dual UISP NMS Fleet Control" in html_text
    assert "DUAL UISP AES-256-GCM + OPENWISP READY" in html_text
    assert "toh:ubiquiti:liteap_ac" in html_text
    assert "toh:ubiquiti:rocket_5ac_prism" in html_text
