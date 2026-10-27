#!/usr/bin/env python3
"""Pytest suite for Stage 349A — Closed-Loop Asymmetric Chain-Mask Rescue Daemon."""

from __future__ import annotations

import json

from tools.firmware.build_stage349a_chain_imbalance_rescue_daemon import (
    ARTIFACT_OUT,
    DAEMON_SCRIPT_OUT,
    AsymmetricChainRescueController,
    ChainSample,
    build_stage349a_report,
)


def test_stage349a_daemon_script_and_artifact() -> None:
    report = build_stage349a_report()
    assert DAEMON_SCRIPT_OUT.exists()
    assert ARTIFACT_OUT.exists()
    loaded = json.loads(ARTIFACT_OUT.read_text(encoding="utf-8"))
    assert loaded["stage"] == "349A"
    assert loaded["memory_master_claim_id"] == "mm-9ce7"
    assert loaded["daemon_script"]["rx_antenna_mask_preserved"] == 3
    script_txt = DAEMON_SCRIPT_OUT.read_text(encoding="utf-8")
    assert "set bitrates vht-mcs-5 1:0-9" in script_txt
    assert "set bitrates vht-mcs-5 1:0-9 2:0-9" in script_txt
    assert "set antenna 3 3" in script_txt
    assert report["goodput_rescue_gain"]["net_rescue_gain_mbps"] > 30.0


def test_stage349a_hysteresis_state_machine() -> None:
    ctrl = AsymmetricChainRescueController(iface="wlan0", phy="phy0")
    # 1st imbalanced sample -> still holds until 2 consecutive samples
    r1 = ctrl.step(ChainSample(0, -52.0, -59.0, 1400, 15.0, 2))
    assert r1["state"] == "MIMO_2X2_VHT_NSS2"
    # 2nd imbalanced sample (>= 6 dB and > 500 B frame) -> switches to SIMO_TX_2X2_MRC_RX
    r2 = ctrl.step(ChainSample(2, -52.0, -59.5, 1400, 16.0, 2))
    assert r2["state"] == "SIMO_TX_2X2_MRC_RX"
    assert r2["active_vht_nss_max"] == 1
    assert r2["rx_antenna_mask"] == 3
    assert "iw dev wlan0 set bitrates vht-mcs-5 1:0-9" in r2["commands"]

    # Hysteresis band (4.5 dB is between 3 dB and 6 dB) -> must NOT flap back to 2x2
    r3 = ctrl.step(ChainSample(4, -52.0, -56.5, 1400, 2.0, 1))
    assert r3["state"] == "SIMO_TX_2X2_MRC_RX"

    # 3 consecutive samples < 3 dB -> restores MIMO_2X2_VHT_NSS2
    ctrl.step(ChainSample(6, -52.0, -54.0, 1400, 1.5, 1))
    ctrl.step(ChainSample(8, -52.0, -53.8, 1400, 1.4, 1))
    r6 = ctrl.step(ChainSample(10, -52.0, -53.5, 1400, 1.2, 1))
    assert r6["state"] == "MIMO_2X2_VHT_NSS2"
    assert r6["active_vht_nss_max"] == 2
    assert "iw dev wlan0 set bitrates vht-mcs-5 1:0-9 2:0-9" in r6["commands"]
