<!-- doc-head: STAGE34C_OPENWRT_WIKI_MERGER_AND_OPENWISP_DASHBOARD_PANEL.md preserved document content -->
<!-- /doc-head -->

# Stage 34C: OpenWrt DokuWiki Safe Section Merger & OpenWISP/UISP Command Center Panel

- **Task ID**: `T-S34C-GEM2-OPENWRT-WIKI-SAFE-DIFF-PUBLISHER-AND-OPENWISP-UI-PANEL`
- **Wiki Merger Module**: [`tools/wiki/openwrt_dokuwiki_safe_section_merger.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/wiki/openwrt_dokuwiki_safe_section_merger.py)
- **Command Center Builder**: [`tools/build_command_center_html.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/build_command_center_html.py)
- **Generated Receipt**: [`artifacts/autoresearch/stage34c_openwrt_dokuwiki_merger_and_openwisp_panel_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage34c_openwrt_dokuwiki_merger_and_openwisp_panel_20261025.json)
- **Unit Test Suite**: [`tests/test_stage34c_openwrt_wiki_merger.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage34c_openwrt_wiki_merger.py)

---

## 1. Idempotent DokuWiki Safe Section Merger (`<= 25` Lines Budget)

[`tools/wiki/openwrt_dokuwiki_safe_section_merger.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/wiki/openwrt_dokuwiki_safe_section_merger.py) provides deterministic, syntax-validated DokuWiki merging across five upstream OpenWrt Table of Hardware (ToH) pages:

| DokuWiki Page ID | Canonical OpenWrt URL | Section Lines / Budget | Edit Summary |
| :--- | :--- | :---: | :--- |
| **`toh:ubiquiti:liteap_ac`** | `https://openwrt.org/toh/ubiquiti/liteap_ac` | `15 / 25` | `Add verified AirOS 8 4-addr WDS ETH_P_TEB (0x6558) interop & AR9342+QCA9882 AQL/fq_codel tuning (-38% p95 RTT)` |
| **`toh:ubiquiti:nanostation_5ac_loco`** | `https://openwrt.org/toh/ubiquiti/nanostation_ac_loco` | `14 / 25` | `Clarify 535 MHz AR9342 clock, 0xe7fa caldata 0x2292, and optimal STA/AP AQL + fq_codel tuning` |
| **`toh:ubiquiti:litebeam_5ac_gen2`** | `https://openwrt.org/toh/ubiquiti/litebeam_5ac_gen2` | `14 / 25` | `Add U-Boot 0x82000000 LZMA load note, 0xe7f9 caldata 0x13b5, and optimal AQL/fq_codel tuning` |
| **`toh:ubiquiti:rocket_5ac_prism`** | `https://openwrt.org/toh/ubiquiti/rocket_ac` | `11 / 25` | `Document XC/2XC QCA9558 720 MHz, 128 MiB RAM, 3-radio (wifi0+wifi1+airview1), and AirPrism IRQ 64 specs` |
| **`toh:ubiquiti:start`** | `https://openwrt.org/toh/ubiquiti/start` | `4 / 25` | `Clarify Ubiquiti LTU Cyclone V SoC + ame_core FPGA architecture and PowerBeam M5-400 vs M5-300 Ethernet PHY split` |

### Safety Invariants Verified
1. **Strict 25-Line Budget (`MAX_SECTION_LINES = 25`)**: [`validate_dokuwiki_section_budget_and_syntax()`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/wiki/openwrt_dokuwiki_safe_section_merger.py#L120-L152) rejects any section exceeding 25 lines, missing a valid DokuWiki heading (`===== ... =====`), containing unbalanced `<code>...</code>` blocks, or containing malformed table rows (`^` / `|`).
2. **Idempotent Merging**: [`merge_dokuwiki_section_idempotent()`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/wiki/openwrt_dokuwiki_safe_section_merger.py#L155-L234) inserts before trailing footers (`===== External links =====` / `{{page>...}}`) with guaranteed blank-line separation after tables on the first pass (`INSERTED_NEW_SECTION`), updates in-place if an older section with the same heading exists (`UPDATED_EXISTING_SECTION`), and returns `UNCHANGED_IDEMPOTENT` (`changed=False`, empty unified diff) on repeated passes.

---

## 2. Executive Command Center Panel Integration

[`tools/build_command_center_html.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/build_command_center_html.py#L814-L885) now renders the dedicated **`OpenWISP NetJSON & Dual UISP NMS Fleet Control`** section inside [`artifacts/dashboard/FUTURAMAX_COMMAND_CENTER.html`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/dashboard/FUTURAMAX_COMMAND_CENTER.html), displaying:
- All 8 OpenWISP `NetJSON` `DeviceConfiguration` SHA-256 checksums and `RAM_ONLY_ZERO_FLASH_WRITES` status,
- Live Dual UISP (`udapi-bridge` AES-256-GCM) + OpenWISP coexistence readiness, and
- All 5 OpenWrt ToH DokuWiki contribution targets with their line-budget counters (`<= 25` lines) and edit summaries.
