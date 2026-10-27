import json
from pathlib import Path

from tools.build_command_center_html import build_html
from tools.wiki.openwrt_dokuwiki_safe_section_merger import (
    MAX_SECTION_LINES,
    validate_dokuwiki_section_budget_and_syntax,
)
from tools.wiki.publish_openwrt_toh_via_orca import (
    COMMON_UBIQUITI_SPEC,
    POWERBEAM_SPEC,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
LIVE_RECEIPT_JSON = (
    ROOT_DIR / "artifacts" / "autoresearch" / "stage35_openwrt_wiki_live_publish_receipt_20261025.json"
)
STAGE35C_DOC = ROOT_DIR / "docs" / "STAGE35C_LIVE_OPENWRT_WIKI_UPSTREAM_PUBLICATION_REPORT.md"


def test_stage35c_live_publish_receipt_has_all_5_verified_pages():
    assert LIVE_RECEIPT_JSON.exists()
    data = json.loads(LIVE_RECEIPT_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "35-WIKI-PUBLISH"
    assert data["pages_attempted"] == 5
    assert data["pages_verified_live"] == 5

    expected_urls = {
        "https://openwrt.org/toh/ubiquiti/rocket_ac",
        "https://openwrt.org/toh/ubiquiti/nanostation_ac_loco",
        "https://openwrt.org/toh/ubiquiti/litebeam_5ac_gen2",
        "https://openwrt.org/toh/ubiquiti/powerbeam",
        "https://openwrt.org/toh/ubiquiti/common",
    }
    actual_urls = {r["canonical_url"] for r in data["results"]}
    assert actual_urls == expected_urls

    for item in data["results"]:
        assert item["verified_heading_present_on_live_page"] is True
        assert item["section_line_count"] <= MAX_SECTION_LINES


def test_stage35c_powerbeam_and_common_specs_valid_and_report_complete():
    for spec in (POWERBEAM_SPEC, COMMON_UBIQUITI_SPEC):
        res = validate_dokuwiki_section_budget_and_syntax(spec.section_dokuwiki)
        assert res["valid"] is True
        assert res["line_count"] <= MAX_SECTION_LINES

    assert STAGE35C_DOC.exists()
    doc_text = STAGE35C_DOC.read_text(encoding="utf-8")
    for url in (
        "https://openwrt.org/toh/ubiquiti/rocket_ac",
        "https://openwrt.org/toh/ubiquiti/nanostation_ac_loco",
        "https://openwrt.org/toh/ubiquiti/litebeam_5ac_gen2",
        "https://openwrt.org/toh/ubiquiti/powerbeam",
        "https://openwrt.org/toh/ubiquiti/common",
    ):
        assert url in doc_text
    assert "```diff" in doc_text


def test_stage35c_command_center_surfaces_5_live_openwrt_wiki_urls_and_badges():
    html_path = build_html()
    html_text = html_path.read_text(encoding="utf-8")
    assert "PUBLISHED LIVE ON OPENWRT.ORG ✓" in html_text
    assert "5/5 TOH WIKI PAGES LIVE ON OPENWRT.ORG" in html_text
    for url in (
        "https://openwrt.org/toh/ubiquiti/rocket_ac",
        "https://openwrt.org/toh/ubiquiti/nanostation_ac_loco",
        "https://openwrt.org/toh/ubiquiti/litebeam_5ac_gen2",
        "https://openwrt.org/toh/ubiquiti/powerbeam",
        "https://openwrt.org/toh/ubiquiti/common",
    ):
        assert url in html_text
