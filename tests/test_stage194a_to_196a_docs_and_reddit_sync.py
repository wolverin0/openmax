"""Source-bound public documentation and actual local browser contracts."""
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re

import pytest
from playwright.sync_api import sync_playwright
from tools.wiki import render_reddit_public_copy as renderer

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ("GUIA_UNIVERSAL_POWERBEAM_LITEBEAM_OPENMAX.md", "REDDIT_REPLY_FIRMWARE_TESTERS_WA_FAMILY.md")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.discovery_ids, self.columns, self.summary_parts = [], [], {"en":[],"es":[]}
        self.language, self.depth, self.in_header = None, 0, False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("data-discovery"):
            self.discovery_ids.append(a["data-discovery"])
        if tag == "th":
            assert a.get("scope") == "col"
            self.in_header = True
        if tag == "div":
            if a.get("id") in ("post-en","post-es"):
                self.language, self.depth = a["id"][-2:], 1
            elif self.language:
                self.depth += 1
        if tag == "br" and self.language:
            self.summary_parts[self.language].append("\n")
    def handle_endtag(self, tag):
        if tag == "th": self.in_header = False
        if tag == "p" and self.language: self.summary_parts[self.language].append("\n\n")
        if tag == "div" and self.language:
            self.depth -= 1
            if self.depth == 0: self.language = None
    def handle_data(self, text):
        if self.language: self.summary_parts[self.language].append(text)
        if self.in_header: self.columns.append(text)


@pytest.mark.parametrize("name", (*GUIDES,"REDDIT_POST.md"))
def test_markdown_documents_are_compact_with_only_initial_paired_header(name):
    text = (ROOT/"docs"/name).read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.startswith("<!-- doc-head:")
    assert text.count("<!-- doc-head:") == text.count("<!-- /doc-head -->") == 1


def test_full_catalogue_contains_exactly42_distinct_sequential_findings():
    page = Page(); page.feed((ROOT/"docs/reddit_post_copy.html").read_text(encoding="utf-8"))
    expected = [f"FMX-DISC-{i:02d}" for i in range(1,43)]
    assert page.discovery_ids == expected
    md = (ROOT/"docs/REDDIT_POST.md").read_text(encoding="utf-8")
    assert re.findall(r"^\| (FMX-DISC-\d+) \|",md,re.M) == expected
    assert page.columns == ["ID","Finding","Layer","Evidence limit"]


@pytest.mark.parametrize("language", ("en","es"))
def test_copyable_summaries_are_exactly_synced_between_markdown_and_html(language):
    page = Page(); page.feed((ROOT/"docs/reddit_post_copy.html").read_text(encoding="utf-8"))
    blocks = re.findall(r"```text\n(.*?)\n```", (ROOT/"docs/REDDIT_POST.md").read_text(encoding="utf-8"),re.S)
    expected = blocks[0 if language=="en" else 1]
    actual = "".join(page.summary_parts[language]).strip()
    # Formatting whitespace between paragraphs does not belong to copied content.
    assert actual.replace("\n\n\n","\n\n") == expected
    assert len(expected) < 10000
    assert "+13.68%" in expected and "+68%" in expected and "+90%" in expected
    assert "-25.78%" in expected and "UNPROVEN" in expected
    assert "999" in expected and "samples=1" in expected
    assert "76" in expected and "72" in expected and "Stage138" in expected


@pytest.mark.parametrize("name", GUIDES)
def test_guides_keep_ptp_data_gate_conditional_and_public_images_out_of_unattended_ota(name):
    text = (ROOT/"docs"/name).read_text(encoding="utf-8").lower()
    for token in ("stage138","fmx-disc-42","radio.1.ptpmode=0","air os" if "air os" in text else "airos","sta", "offline"):
        assert token in text
    assert "eapol" in text and ("arp" in text or "ipv4" in text)
    assert "192.168.1.20" in text and "watchdog" in text
    assert "public_release_v4" in text and "sha256sums.txt" in text
    for token in ("13.68","68","90","25.78","999","samples=1"):
        assert token in text
    assert "unproven" in text or "sin probar" in text
    assert "iperf3 -j" not in text
    assert not re.search(r"\b(?:192\.168\.100\.\d+|192\.168\.15\.\d+|10\.10\.\d+\.\d+)\b", text)
    assert not re.search(r"^\s*(?:fwupdate|sysupgrade\s+-F|mtd\s+write)\b",text,re.M)


def test_disc42_source_is_offline_and_not_a_flash_receipt():
    data = json.loads((ROOT/"artifacts/autoresearch/stage138a_ptp_sta_data_gate_verdict.json").read_text(encoding="utf-8-sig"))
    assert data["live_devices_touched"] is False
    assert data["simpy_ptp_data_gate_simulation"]
    assert data["pymoo_pareto_ota_sequence"]


def test_generated_documents_have_no_manual_drift():
    md,page = renderer.render()
    assert md == (ROOT/"docs/REDDIT_POST.md").read_text(encoding="utf-8")
    assert page == (ROOT/"docs/reddit_post_copy.html").read_text(encoding="utf-8")


def test_docs_stage_receipts_bind_current_source_and_output_bytes():
    for name in ("stage194a_tester_docs_and_ota_guide_v4_receipt.json", "stage195a_reddit_post_html_and_md_sync_receipt.json"):
        receipt = json.loads((ROOT/"artifacts/autoresearch"/name).read_text(encoding="utf-8-sig"))
        for key,record in receipt["outputs"].items():
            path=record.get("path",key)
            assert path.startswith("docs/")
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == record["sha256"]


def luminance(rgb):
    values=[int(v)/255 for v in re.findall(r"\d+",rgb)[:3]]
    values=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
    return sum(a*b for a,b in zip(values,(.2126,.7152,.0722)))


@pytest.mark.parametrize("theme",("light","dark"))
def test_actual_browser_headers_copy_payload_and_summary_budget(theme):
    evidence=ROOT/"artifacts/verification/stage196a_browser";evidence.mkdir(exist_ok=True,parents=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={"width":1280,"height":960},color_scheme=theme)
        errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
        # Browser-local clipboard stub; no system clipboard or external posting.
        page.add_init_script("""window.__copy=[];window.ClipboardItem=class{constructor(data){this.data=data;}};Object.defineProperty(navigator,'clipboard',{value:{write:async items=>{window.__copy=items;},writeText:async text=>{window.__copyText=text;}}});""")
        page.goto((ROOT/"docs/reddit_post_copy.html").as_uri())
        page.select_option("#theme",theme)
        assert page.locator("#discovery-table tbody tr").count()==42
        colors=page.locator("#discovery-table th").evaluate_all("els=>els.map(e=>({fg:getComputedStyle(e).color,bg:getComputedStyle(e).backgroundColor,scope:e.scope}))")
        for c in colors:
            high,low=sorted((luminance(c['fg']),luminance(c['bg'])),reverse=True)
            assert (high+.05)/(low+.05)>=4.5
            assert c['scope']=='col'
        for language,expected in (("en",renderer.SUMMARY_EN),("es",renderer.SUMMARY_ES)):
            lengths=page.locator('#post-'+language).evaluate("e=>({text:summaryText(e),markup:e.innerHTML})")
            assert lengths['text']==expected
            assert len(lengths['text'])<10000 and len(lengths['markup'])<10000
            page.click('[data-copy="post-'+language+'"]')
            copied=page.evaluate("async()=>await window.__copy[0].data['text/plain'].text()")
            assert copied==expected
        page.locator("#discovery-table").screenshot(path=str(evidence/(theme+'-table.png')))
        page.locator("#discovery-table thead").screenshot(path=str(evidence/(theme+'-headers.png')))
        page.screenshot(path=str(evidence/(theme+'-page.png')),full_page=True)
        assert errors==[]
        (evidence/(theme+'.json')).write_text(json.dumps({'theme':theme,'columns':colors,'contrast_min':min((max(luminance(c['fg']),luminance(c['bg']))+.05)/(min(luminance(c['fg']),luminance(c['bg']))+.05) for c in colors),'console_errors':errors,'clipboard':'stub only','external_posts':0},indent=2)+'\n')
        browser.close()
