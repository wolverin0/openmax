#!/usr/bin/env python3
"""
Unit tests for Stage 40C — Champion v10 Direct mac80211 `aqm` (`fq_quantum=3028`, `fq_memory_limit=4194304`)
& `AC_BE=1500/3000` (`aql_threshold=5000`) Integration into the OpenWISP IPTV NetJSON Template.
Task ID: T-S40C-GEM2-POP-CMAF-MICROCACHE-AND-CHAMPION-V10-AQM-NETJSON-INTEGRATION
"""

from __future__ import annotations

import json

from controller.multiradio_golden_profile_applicator import FORBIDDEN_TOKENS
from controller.wisp_iptv_ptmp_sector_optimizer import (
    build_default_wmm_ac_vi_qos_config,
    export_openwisp_iptv_netjson_template,
    load_empirical_stage36a_champion_v10_evidence,
    render_openwrt_iptv_ac_vi_qos_and_dms_script,
)


def test_stage36a_r1_vs_r2_empirical_evidence_loaded() -> None:
    ev = load_empirical_stage36a_champion_v10_evidence()
    r1 = ev["s36a_r1_ac_be_1000_2000_refuted"]
    r2 = ev["s36a_r2_champion_v10_promoted"]

    # S36A-R1 (AC_BE=1000/2000, thresh=4000) lost -6.225% goodput because 2-MTU (3028B) TCP frames need ~1450 us
    assert r1["round_id"] == "S36A-R1"
    assert r1["goodput_delta_pct"] == -6.225
    assert r1["claim_status"] == "REFUTED"

    # S36A-R2 (Stage 36A Champion v10: AC_VI=1200/2400, AC_BE=1500/3000, thresh=5000 + direct mac80211 aqm)
    assert r2["round_id"] == "S36A-R2"
    assert r2["goodput_delta_pct"] == 2.513
    assert r2["p95_rtt_delta_pct"] == -3.375
    assert r2["p99_rtt_delta_pct"] == -8.990
    assert r2["iptv_loss_pct"] == 0.0
    assert r2["decision"] == "PROMOTE_NEW_CHAMPION"
    assert r2["claim_status"] == "CONFIRMED"


def test_champion_v10_direct_mac80211_aqm_and_ac_be_1500_3000_in_script_and_netjson() -> None:
    cfg = build_default_wmm_ac_vi_qos_config()
    assert cfg.ac_vi_aql_low_us == 1200
    assert cfg.ac_vi_aql_high_us == 2400
    assert cfg.ac_be_aql_low_us == 1500
    assert cfg.ac_be_aql_high_us == 3000
    assert cfg.ac_bk_aql_low_us == 500
    assert cfg.ac_bk_aql_high_us == 1000
    assert cfg.global_aql_threshold_us == 5000
    assert cfg.fq_codel_quantum_bytes == 3028
    assert cfg.fq_memory_limit_bytes == 4194304

    script = render_openwrt_iptv_ac_vi_qos_and_dms_script(cfg)
    assert 'echo fq_quantum 3028 > "${PHY_DIR}/aqm"' in script
    assert 'echo fq_memory_limit 4194304 > "${PHY_DIR}/aqm"' in script
    assert 'echo "1 1200 2400" > "${PHY_DIR}/aql_txq_limit"' in script
    assert 'echo "2 1500 3000" > "${PHY_DIR}/aql_txq_limit"' in script
    assert 'echo 5000 > "${PHY_DIR}/aql_threshold"' in script

    tpl = export_openwisp_iptv_netjson_template(cfg)
    assert tpl["champion_version"] == "Stage 36A Champion v10 (M16b_IPTV_AC_VI_MAC80211_AQM)"
    assert tpl["profile_sha256"].startswith("a0a3ef9ebd0be07e")

    profile_json = json.loads(tpl["config"]["files"][0]["contents"])
    apply_cmds = profile_json["apply_commands"]
    assert "echo fq_quantum 3028 > /sys/kernel/debug/ieee80211/phy0/aqm" in apply_cmds
    assert "echo fq_memory_limit 4194304 > /sys/kernel/debug/ieee80211/phy0/aqm" in apply_cmds
    assert "echo 5000 > /sys/kernel/debug/ieee80211/phy0/aql_threshold" in apply_cmds
    assert "echo '1 1200 2400' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit" in apply_cmds
    assert "echo '2 1500 3000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit" in apply_cmds
    assert "echo '3 500 1000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit" in apply_cmds

    for token in FORBIDDEN_TOKENS:
        assert token not in json.dumps(tpl)
