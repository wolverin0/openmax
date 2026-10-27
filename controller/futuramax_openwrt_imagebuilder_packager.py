"""
FuturaMAX OpenWrt 24.10.4 ImageBuilder Packager (Controller Bridge Module)
==========================================================================
Re-exports all ImageBuilder packaging functions, UCI-defaults generators,
and Stage 47C/48C/49C/50C Champion v16 (`S46A-R3`: `M29b_PURE_DEV_WEIGHT_TX_BIAS_2_AT_FULL_BUDGET_600`
setting `net.core.dev_weight_tx_bias=2` at full `net.core.netdev_budget=600`, preserving dynamic
kernel `dql` BQL and `/sys/class/net/eth0/tx_queue_len=1000` while setting `br-lan` and `phy0-ap0*`
to `256`) manifest generators from `firmware.openwrt.futuramax_openwrt_imagebuilder_packager`.
"""
from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from firmware.openwrt.futuramax_openwrt_imagebuilder_packager import *  # noqa: F401, F403
from firmware.openwrt.futuramax_openwrt_imagebuilder_packager import (  # noqa: F401
    STAGE47C_OUTPUT_JSON,
    STAGE48C_OUTPUT_JSON,
    STAGE49C_OUTPUT_JSON,
    STAGE50C_OUTPUT_JSON,
    generate_stage47c_imagebuilder_txq1000_manifest,
    generate_stage48c_imagebuilder_champion_v14_manifest,
    generate_stage49c_imagebuilder_champion_v15_manifest,
    generate_stage50c_imagebuilder_champion_v16_manifest,
    render_hotplug_99_futuramax_wds_dms,
    render_uci_defaults_98_futuramax_champion_v13_aqm,
    render_uci_defaults_98_futuramax_champion_v14_aqm,
    render_uci_defaults_98_futuramax_champion_v15_aqm,
    render_uci_defaults_98_futuramax_champion_v16_aqm,
)

STAGE47C_MANIFEST_JSON = STAGE47C_OUTPUT_JSON
STAGE48C_MANIFEST_JSON = STAGE48C_OUTPUT_JSON
STAGE49C_MANIFEST_JSON = STAGE49C_OUTPUT_JSON
STAGE50C_MANIFEST_JSON = STAGE50C_OUTPUT_JSON

if __name__ == "__main__":
    m47 = generate_stage47c_imagebuilder_txq1000_manifest()
    m48 = generate_stage48c_imagebuilder_champion_v14_manifest()
    m49 = generate_stage49c_imagebuilder_champion_v15_manifest()
    m50 = generate_stage50c_imagebuilder_champion_v16_manifest()
    print(f"Wrote Stage 47C ImageBuilder manifest to {STAGE47C_OUTPUT_JSON} (targets={len(m47['targets'])})")
    print(f"Wrote Stage 48C ImageBuilder Champion v14 manifest to {STAGE48C_OUTPUT_JSON} (targets={len(m48['targets'])})")
    print(f"Wrote Stage 49C ImageBuilder Champion v15 manifest to {STAGE49C_OUTPUT_JSON} (targets={len(m49['targets'])})")
    print(f"Wrote Stage 50C ImageBuilder Champion v16 manifest to {STAGE50C_OUTPUT_JSON} (targets={len(m50['targets'])})")
