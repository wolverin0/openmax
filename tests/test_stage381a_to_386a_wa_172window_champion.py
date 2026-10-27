"""Unified verification test suite for Stage 381A -> Stage 386A (42 Rounds / 172 Cumulative Windows)."""

from __future__ import annotations

from tests.test_stage381a import test_stage381a_ampdu_rts_autocorking_r37_to_r39_receipt
from tests.test_stage382a import test_stage382a_fwstats_rescue_v7_r40_to_r42_receipt
from tests.test_stage383a import test_stage383a_mk1_251_bidir_e2e_v7_receipt
from tests.test_stage384a import test_stage384a_panel1_guarida_v7_and_rcstats_receipt
from tests.test_stage385a import test_stage385a_cumulative_42round_172window_wa_champion_v7

__all__ = [
    "test_stage381a_ampdu_rts_autocorking_r37_to_r39_receipt",
    "test_stage382a_fwstats_rescue_v7_r40_to_r42_receipt",
    "test_stage383a_mk1_251_bidir_e2e_v7_receipt",
    "test_stage384a_panel1_guarida_v7_and_rcstats_receipt",
    "test_stage385a_cumulative_42round_172window_wa_champion_v7",
]
