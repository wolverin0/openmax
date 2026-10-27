"""
FuturaMAX OpenWISP 26.09 + Dual-UISP Central Management Web Portal (NMS Bridge Module)
======================================================================================
Re-exports all portal builders, REST API payload builders, and HTTP handlers from
`tools.serve_openwisp_dual_nms_live`.
"""
from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.serve_openwisp_dual_nms_live import (
    OPENWRT_TOH_LINKS,
    PORTAL_HTML_OUT,
    STAGE34A_JSON,
    STAGE35A_JSON,
    OpenWispDualNmsHandler,
    build_iptv_and_capacity_ceiling_api_payload,
    build_openwisp_dual_nms_registry,
    build_openwisp_portal_html,
    build_stage47c_guards_and_24ghz_m18_api_payload,
    export_openwisp_bql_eth0_r5ac_txq256_champion_v15_netjson_template,
    export_openwisp_sysfs_txq256_champion_v14_netjson_template,
    export_openwisp_tx_bias_2_dynamic_bql_champion_v16_netjson_template,
    main,
)

__all__ = [
    "OPENWRT_TOH_LINKS",
    "PORTAL_HTML_OUT",
    "STAGE34A_JSON",
    "STAGE35A_JSON",
    "OpenWispDualNmsHandler",
    "build_iptv_and_capacity_ceiling_api_payload",
    "build_openwisp_dual_nms_registry",
    "build_openwisp_portal_html",
    "build_stage47c_guards_and_24ghz_m18_api_payload",
    "export_openwisp_bql_eth0_r5ac_txq256_champion_v15_netjson_template",
    "export_openwisp_sysfs_txq256_champion_v14_netjson_template",
    "export_openwisp_tx_bias_2_dynamic_bql_champion_v16_netjson_template",
    "main",
]

if __name__ == "__main__":
    main()
