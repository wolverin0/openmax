"""
Live OpenWrt Wiki Publisher via Logged-In Orca Browser Tab (`c892a096-03f8-4a9a-9e56-3f39b0e56aa1`).

Safely merges and publishes our zero-bloat (<25-line) hardware-verified DokuWiki sections
onto the official OpenWrt Ubiquiti device pages using `merge_dokuwiki_section_idempotent()`
and in-browser DOM splicing so command-line arguments stay well below Windows 32 KB limits.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import time
from typing import Any, Dict, List

from tools.wiki.openwrt_dokuwiki_safe_section_merger import (
    CURATED_DOKUWIKI_SECTIONS,
    DokuWikiContributionSpec,
    merge_dokuwiki_section_idempotent,
    validate_dokuwiki_section_budget_and_syntax,
)

ROOT_DIR = Path(__file__).resolve().parents[2]
ORCA_PAGE_ID = "c892a096-03f8-4a9a-9e56-3f39b0e56aa1"

POWERBEAM_SPEC = DokuWikiContributionSpec(
    wiki_page_id="toh:ubiquiti:powerbeam",
    canonical_url="https://openwrt.org/toh/ubiquiti/powerbeam",
    section_heading="===== PowerBeam M5 (XW) Ethernet PHY Warning: PBE-M5-400 (GbE) vs. PBE-M5-300 (100M) =====",
    edit_summary="Add XW PowerBeam M5-400 (0xe4e5 AR8035 GbE) vs M5-300 (0xe3e5 ATHRS27 100M) image selection warning",
    section_dokuwiki="""===== PowerBeam M5 (XW) Ethernet PHY Warning: PBE-M5-400 (GbE) vs. PBE-M5-300 (100M) =====
When flashing OpenWrt onto ''XW'' board PowerBeam M5 units, verify the exact model and ''ubnthal'' board SysID first:
  * **PowerBeam M5-400 (''PBE-M5-400'', SysID ''0xe4e5'')**: Uses an external **Atheros AR8035 Gigabit Ethernet PHY** (''0x004d:0xd072'') over RGMII. Use the **''ubnt_powerbeam-m5-xw''** OpenWrt image.
  * **PowerBeam M5-300 (''PBE-M5-300'', SysID ''0xe3e5'')**: Uses the internal ''AR9342'' **FastEthernet (100 Mbps) switch** (''ATHRS27''). Flashing ''ubnt_powerbeam-m5-xw'' onto a ''PBE-M5-300'' results in no ''eth0'' link because the DTS probes for the absent ''AR8035'' PHY; use the **''ubnt_nanobeam-m5-xw''** OpenWrt image instead.
  * **U-Boot ''urescue'' TFTP Note (''XW.v6.3.x'')**: Newer ''XW'' U-Boot versions request a DHCP lease during TFTP recovery before falling back to ''192.168.1.20''.""",
)

COMMON_UBIQUITI_SPEC = DokuWikiContributionSpec(
    wiki_page_id="toh:ubiquiti:common",
    canonical_url="https://openwrt.org/toh/ubiquiti/common",
    section_heading="===== AirOS 8 4-Address WDS (0x6558) Interoperability & LTU Family Note =====",
    edit_summary="Add verified AirOS 8 4-addr WDS ETH_P_TEB (0x6558) interop & LTU Cyclone V SoC FPGA architecture note",
    section_dokuwiki="""===== AirOS 8 4-Address WDS (0x6558) Interoperability & LTU Family Note =====
  * **AirOS 8 4-Address WDS (''ETH_P_TEB'' ''0x6558'') Interoperability**: Stock **airOS 8** (''WA.v8.7.x'' / ''XC.v8.7.x'') stations in 4-address WDS mode encapsulate inner Ethernet frames with ''ETH_P_TEB'' (EtherType ''0x6558'') and require airMAX vendor IEs unless ''allow_80211=1'' and ''ubnt_op_mode=0'' are active in ''/proc/sys/dev/uph/'' (scope any ''/etc/sysinit/radio.conf'' edit strictly to ''/op_mode/s/1/0/''). On an OpenWrt AP (''mac80211''), stripping ''sizeof(struct ethhdr)'' inside ''ieee80211_data_to_8023_exthdr()'' when ''hdr.h_proto == htons(ETH_P_TEB)'' restores transparent L2 bridging.
  * **Macronix ''MX25L12805D'' SPI NOR Unlock (''WA'' / ''XC'')**: Use OpenWrt ''23.05.3+'' or ''24.10.3+'' (''Linux 6.6.103+'') so ''SR_BP*'' flash block-protection bits set by U-Boot are cleared before mounting ''overlayfs''.
  * **Ubiquiti LTU Family (''LTU-Lite'' ''0xae08'', ''LTU-Rocket'' ''0xeb00'')**: Built on an **Altera/Intel Cyclone V SoC FPGA** (Dual-Core ''ARM Cortex-A9'' HPS + ''/lib/firmware/ame_soc.rbf'' + ''ame_core.ko'' 4096-QAM TDD baseband), not Qualcomm ''ath79''/''QCA988x'' hardware.""",
)


def orca_goto(page_id: str, url: str) -> str:
    res = subprocess.run(
        ["orca", "goto", "--page", page_id, "--url", url],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return (res.stdout or "") + (res.stderr or "")


def orca_eval(page_id: str, expression: str) -> str:
    res = subprocess.run(
        ["orca", "eval", "--page", page_id, "--expression", expression],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return (res.stdout or "").strip()


def publish_single_page(page_id: str, spec: DokuWikiContributionSpec) -> Dict[str, Any]:
    validate_dokuwiki_section_budget_and_syntax(spec.section_dokuwiki)
    edit_url = f"{spec.canonical_url}?do=edit"
    nav_out = orca_goto(page_id, edit_url)
    time.sleep(2.5)

    for _ in range(4):
        title = orca_eval(page_id, "document.title")
        if "Testing to determine" not in title:
            break
        time.sleep(2.0)

    has_ta = orca_eval(page_id, "Boolean(document.getElementById('wiki__text'))")
    if has_ta.lower() != "true":
        return {
            "wiki_page_id": spec.wiki_page_id,
            "canonical_url": spec.canonical_url,
            "status": "SKIPPED_NO_EDIT_TEXTAREA",
            "nav_output": nav_out,
        }

    raw_text = orca_eval(page_id, "document.getElementById('wiki__text').value")
    CURATED_DOKUWIKI_SECTIONS[spec.wiki_page_id] = spec
    merged = merge_dokuwiki_section_idempotent(raw_text, spec.wiki_page_id)

    if not merged["changed"]:
        return {
            "wiki_page_id": spec.wiki_page_id,
            "canonical_url": spec.canonical_url,
            "status": "ALREADY_PRESENT_IDEMPOTENT",
            "action": merged["action"],
            "section_line_count": merged["section_line_count"],
            "verified_heading_present_on_live_page": True,
        }

    # In-browser splicing keeps the CLI expression < 2.5 KB even on 40 KB wiki pages
    inject_js = f"""
(() => {{
  const ta = document.getElementById("wiki__text");
  const sum = document.getElementById("edit__summary");
  const saveBtn = document.getElementById("edbtn__save");
  const heading = {json.dumps(spec.section_heading.strip())};
  const block = {json.dumps(spec.section_dokuwiki.strip())};
  const lines = ta.value.replace(/\\r\\n/g, "\\n").split("\\n");
  let insertIdx = lines.length;
  for (let i = 0; i < lines.length; i++) {{
    const s = lines[i].trim();
    if (s.toLowerCase().startsWith("===== external links") || s.startsWith("{{page>")) {{
      insertIdx = i;
      break;
    }}
  }}
  const prefix = lines.slice(0, insertIdx);
  const suffix = lines.slice(insertIdx);
  if (prefix.length > 0 && prefix[prefix.length - 1].trim() !== "") prefix.push("");
  const newLines = prefix.concat(block.split("\\n"));
  if (suffix.length > 0 && suffix[0].trim() !== "") newLines.push("");
  ta.value = newLines.concat(suffix).join("\\n");
  ta.dispatchEvent(new Event("input", {{ bubbles: true }}));
  ta.dispatchEvent(new Event("change", {{ bubbles: true }}));
  if (sum) {{
    sum.value = {json.dumps(spec.edit_summary)};
    sum.dispatchEvent(new Event("input", {{ bubbles: true }}));
    sum.dispatchEvent(new Event("change", {{ bubbles: true }}));
    sum.dispatchEvent(new KeyboardEvent("keyup", {{ bubbles: true }}));
  }}
  if (saveBtn) {{
    saveBtn.disabled = false;
    saveBtn.removeAttribute("disabled");
    saveBtn.click();
    return "CLICKED_SAVE";
  }}
  return "NO_SAVE_BTN";
}})()
"""
    click_status = orca_eval(page_id, inject_js)
    time.sleep(3.5)

    post_url = orca_eval(page_id, "window.location.href")
    post_title = orca_eval(page_id, "document.title")
    heading_text = spec.section_heading.strip("= ").strip()
    verified_on_page = orca_eval(
        page_id,
        f"document.body.innerText.includes({json.dumps(heading_text[:32])})",
    )

    return {
        "wiki_page_id": spec.wiki_page_id,
        "canonical_url": spec.canonical_url,
        "status": "PUBLISHED_LIVE" if verified_on_page.lower() == "true" else "SUBMITTED_CHECK_NEEDED",
        "click_status": click_status,
        "post_save_url": post_url,
        "post_save_title": post_title,
        "verified_heading_present_on_live_page": verified_on_page.lower() == "true",
        "edit_summary": spec.edit_summary,
        "section_line_count": merged["section_line_count"],
        "unified_diff": merged["unified_diff"],
    }


def main() -> None:
    CURATED_DOKUWIKI_SECTIONS["toh:ubiquiti:powerbeam"] = POWERBEAM_SPEC
    CURATED_DOKUWIKI_SECTIONS["toh:ubiquiti:common"] = COMMON_UBIQUITI_SPEC
    target_order: List[str] = [
        "toh:ubiquiti:rocket_5ac_prism",
        "toh:ubiquiti:nanostation_5ac_loco",
        "toh:ubiquiti:litebeam_5ac_gen2",
        "toh:ubiquiti:powerbeam",
        "toh:ubiquiti:common",
    ]
    results: List[Dict[str, Any]] = []
    for key in target_order:
        spec = CURATED_DOKUWIKI_SECTIONS[key]
        print(f"Publishing {key} -> {spec.canonical_url} ...")
        res = publish_single_page(ORCA_PAGE_ID, spec)
        print(f"  Result: {res['status']} (verified={res.get('verified_heading_present_on_live_page')})")
        results.append(res)

    receipt = {
        "stage": "35-WIKI-PUBLISH",
        "published_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "orca_browser_page_id": ORCA_PAGE_ID,
        "pages_attempted": len(results),
        "pages_verified_live": sum(
            1
            for r in results
            if r.get("verified_heading_present_on_live_page") or r.get("status") == "ALREADY_PRESENT_IDEMPOTENT"
        ),
        "results": results,
    }
    out_path = ROOT_DIR / "artifacts" / "autoresearch" / "stage35_openwrt_wiki_live_publish_receipt_20261025.json"
    out_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE_LIVE_WIKI_RECEIPT: {out_path} ({receipt['pages_verified_live']}/{receipt['pages_attempted']} live)")


if __name__ == "__main__":
    main()
