"""Workstream E3: AR9888 UTF Command Handler Tracer (`trace_utf_handlers.py`).

Traces TLV2/TLV1/TCMD command IDs from dictionary definition (`cmdRspParmsDict.h`,
`testcmd_ar988x.h`) -> auto-generated parser/dispatcher (`cmdAdcCaptureHandler.h`,
`cmdGenWaveformHandler.h`) -> target registration (`initCmdProcessTlv2()` in
`cmdProcessTlv2.c`) -> target handler implementation (`tcmd.c`, `cmdProcessTlv2.c`),
and classifies every command as:
- `EXACT_AR9888`
- `SHARED_ONLY`
- `NOT_FOUND`
- `CROSS_CHIP`
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.qca988x.fetch_pinned_sources import (
    STARLINK_WIFI_COMMIT,
    STARLINK_WIFI_REPO,
    get_pinned_source_by_id,
)

VALID_CLASSIFICATIONS = frozenset(
    {"EXACT_AR9888", "SHARED_ONLY", "NOT_FOUND", "CROSS_CHIP"}
)


@dataclass(frozen=True)
class UTFCommandTraceEntry:
    """Deterministic trace record for a TLV2, SYSCMD, or legacy TCMD command."""

    command_name: str
    command_id: int
    response_command_name: Optional[str]
    response_command_id: Optional[int]
    protocol_layer: str
    dictionary_source_id: str
    dictionary_path: str
    parser_header_path: Optional[str]
    registration_function: Optional[str]
    registered_in_ar9888_utf: bool
    target_handler_symbol: Optional[str]
    target_handler_source_id: Optional[str]
    target_handler_path: Optional[str]
    build_guard_condition: str
    non_destructive_read_only: bool
    classification: str
    evidence_label: str
    request_fields: List[str] = field(default_factory=list)
    response_fields: List[str] = field(default_factory=list)
    hardware_primitives_invoked: List[str] = field(default_factory=list)
    technical_notes: str = ""

    def __post_init__(self) -> None:
        if self.classification not in VALID_CLASSIFICATIONS:
            raise ValueError(
                f"Invalid classification {self.classification!r}; must be in {sorted(VALID_CLASSIFICATIONS)}"
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def parse_cmd_rsp_parms_dict_text(header_text: str) -> Dict[str, int]:
    """Parse `CMD_<NAME> = <ID>` and `SYSCMD_<NAME> = <ID>` from `cmdRspParmsDict.h`."""
    cmd_re = re.compile(r"^\s*((?:SYS)?CMD_[A-Z0-9_]+)\s*=\s*(\d+)\s*,", re.MULTILINE)
    return {m.group(1): int(m.group(2)) for m in cmd_re.finditer(header_text)}


def parse_init_cmd_process_tlv2_registrations(c_text: str) -> List[Dict[str, str]]:
    """Extract `register<CMD>Handler(<fn>)` and `initLM*Handler()` calls in `initCmdProcessTlv2()`."""
    reg_re = re.compile(
        r"^\s*(register[A-Z0-9_]+Handler|initLM[A-Za-z0-9_]+Handler)\s*\(\s*([A-Za-z0-9_]*)\s*\)\s*;",
        re.MULTILINE,
    )
    results: List[Dict[str, str]] = []
    for match in reg_re.finditer(c_text):
        results.append(
            {
                "registration_call": match.group(1),
                "handler_symbol": match.group(2) or match.group(1),
            }
        )
    return results


def build_ar9888_utf_command_traces() -> List[UTFCommandTraceEntry]:
    """Build the authoritative command-to-handler trace table across Q03, Q04, Q07, Q08, Q09, Q10."""
    q03 = get_pinned_source_by_id("Q03")
    q04 = get_pinned_source_by_id("Q04")
    q07 = get_pinned_source_by_id("Q07")
    q08 = get_pinned_source_by_id("Q08")
    q09 = get_pinned_source_by_id("Q09")
    q10 = get_pinned_source_by_id("Q10")

    return [
        UTFCommandTraceEntry(
            command_name="CMD_REGREAD",
            command_id=9,
            response_command_name="CMD_REGREADRSP",
            response_command_id=10,
            protocol_layer="TLV2_CMD",
            dictionary_source_id="Q07",
            dictionary_path=q07.path,
            parser_header_path="dl/wlan/halphy_tools/common/tlv2p0/include/cmdRegReadHandler.h",
            registration_function="registerREGREADHandler",
            registered_in_ar9888_utf=True,
            target_handler_symbol="regReadHandler",
            target_handler_source_id="Q08",
            target_handler_path=q08.path,
            build_guard_condition="Unconditional in commonUTF/cmdProcessTlv2.c (lines 147-176, registered at line 952)",
            non_destructive_read_only=True,
            classification="EXACT_AR9888",
            evidence_label="CONFIRMED",
            request_fields=["regaddress (A_UINT32, 4-byte aligned)"],
            response_fields=["status (A_UINT32)", "regvalue (A_UINT32)"],
            hardware_primitives_invoked=[
                "isValidReg(pParms->regaddress)",
                "hwMemRead32((A_UINT16)currentDevIndex, pParms->regaddress)",
                "wmi_tc_cmds_reply_event(utf_dev.wmi, cmdStreamLen, CMD_REGREADRSP, rCmdStream)",
            ],
            technical_notes=(
                "Safe non-destructive 32-bit register read in AR9888 UTF when regaddress is 4-byte aligned "
                "and passes isValidReg(). Can read PHY_BB_CHANINFO_CTRL (0x0000a370) and CHAN_TAB_B0/B1 "
                "(0x00009b00 / 0x0000ab00) in UTF testmode."
            ),
        ),
        UTFCommandTraceEntry(
            command_name="CMD_REGWRITE",
            command_id=11,
            response_command_name="CMD_REGWRITERSP",
            response_command_id=12,
            protocol_layer="TLV2_CMD",
            dictionary_source_id="Q07",
            dictionary_path=q07.path,
            parser_header_path="dl/wlan/halphy_tools/common/tlv2p0/include/cmdRegWriteHandler.h",
            registration_function="registerREGWRITEHandler",
            registered_in_ar9888_utf=True,
            target_handler_symbol="regWriteHandler",
            target_handler_source_id="Q08",
            target_handler_path=q08.path,
            build_guard_condition="Unconditional in commonUTF/cmdProcessTlv2.c (lines 179-207, registered at line 953)",
            non_destructive_read_only=False,
            classification="EXACT_AR9888",
            evidence_label="CONFIRMED",
            request_fields=["regaddress (A_UINT32, 4-byte aligned)", "regvalue (A_UINT32)"],
            response_fields=["status (A_UINT32)"],
            hardware_primitives_invoked=[
                "isValidReg(pParms->regaddress)",
                "hwMemWrite32((A_UINT16)currentDevIndex, pParms->regaddress, pParms->regvalue)",
                "wmi_tc_cmds_reply_event(utf_dev.wmi, cmdStreamLen, CMD_REGWRITERSP, rCmdStream)",
            ],
            technical_notes=(
                "Direct 32-bit register write in AR9888 UTF after isValidReg() validation."
            ),
        ),
        UTFCommandTraceEntry(
            command_name="CMD_MEMREAD",
            command_id=42,
            response_command_name="CMD_MEMREADRSP",
            response_command_id=43,
            protocol_layer="TLV2_CMD",
            dictionary_source_id="Q07",
            dictionary_path=q07.path,
            parser_header_path="dl/wlan/halphy_tools/common/tlv2p0/include/cmdMemReadHandler.h",
            registration_function="registerMEMREADHandler",
            registered_in_ar9888_utf=True,
            target_handler_symbol="memReadHandler",
            target_handler_source_id="Q08",
            target_handler_path=q08.path,
            build_guard_condition="Unconditional in commonUTF/cmdProcessTlv2.c (lines 68-102, registered at line 960)",
            non_destructive_read_only=True,
            classification="EXACT_AR9888",
            evidence_label="CONFIRMED",
            request_fields=[
                "memaddress (A_UINT32)",
                "numbytes (A_UINT16, up to 255 bytes per reply)",
                "valuetype (A_UINT8, alignment divisor: 1, 2, or 4)",
            ],
            response_fields=[
                "valuetype (A_UINT8)",
                "memaddress (A_UINT32)",
                "numbytes (A_UINT16)",
                "status (A_UINT32)",
                "memvalue (A_UINT8[256])",
            ],
            hardware_primitives_invoked=[
                "hwMemRead32((A_UINT16)currentDevIndex, pParms->memaddress + b - mem_offset)",
                "wmi_tc_cmds_reply_event(utf_dev.wmi, cmdStreamLen, CMD_MEMREADRSP, rCmdStream)",
            ],
            technical_notes=(
                "Safe non-destructive target memory read up to 255 bytes per TLV2 transaction without "
                "calling isValidReg(), enabling direct readout of target DRAM (0x00400000..0x0044ffff) "
                "and memory-mapped BB tables in UTF mode."
            ),
        ),
        UTFCommandTraceEntry(
            command_name="CMD_MEMWRITE",
            command_id=40,
            response_command_name="CMD_MEMWRITERSP",
            response_command_id=41,
            protocol_layer="TLV2_CMD",
            dictionary_source_id="Q07",
            dictionary_path=q07.path,
            parser_header_path="dl/wlan/halphy_tools/common/tlv2p0/include/cmdMemWriteHandler.h",
            registration_function="registerMEMWRITEHandler",
            registered_in_ar9888_utf=True,
            target_handler_symbol="memWriteHandler",
            target_handler_source_id="Q08",
            target_handler_path=q08.path,
            build_guard_condition="Unconditional in commonUTF/cmdProcessTlv2.c (lines 106-144, registered at line 959)",
            non_destructive_read_only=False,
            classification="EXACT_AR9888",
            evidence_label="CONFIRMED",
            request_fields=[
                "memaddress (A_UINT32)",
                "numbytes (A_UINT16)",
                "valuetype (A_UINT8)",
                "memvalue (A_UINT8[])",
            ],
            response_fields=[
                "numbytes (A_UINT16)",
                "valuetype (A_UINT8)",
                "memaddress (A_UINT32)",
                "status (A_UINT32)",
            ],
            hardware_primitives_invoked=[
                "hwMemRead32((A_UINT16)currentDevIndex, pParms->memaddress + b - mem_offset)",
                "hwMemWrite32((A_UINT16)currentDevIndex, pParms->memaddress + b - mem_offset, temp)",
                "wmi_tc_cmds_reply_event(utf_dev.wmi, cmdStreamLen, CMD_MEMWRITERSP, rCmdStream)",
            ],
            technical_notes="Read-modify-write target memory mutator in AR9888 UTF.",
        ),
        UTFCommandTraceEntry(
            command_name="CMD_ADCCAPTURE",
            command_id=59,
            response_command_name="CMD_ADCCAPTURERSP",
            response_command_id=60,
            protocol_layer="TLV2_EXTCMD",
            dictionary_source_id="Q07",
            dictionary_path=q07.path,
            parser_header_path=q09.path,
            registration_function="initADCCAPTUREOpParms / ADCCAPTUREOp",
            registered_in_ar9888_utf=False,
            target_handler_symbol=None,
            target_handler_source_id=None,
            target_handler_path=None,
            build_guard_condition="#ifdef USE_TLV2_EXTCMD in cmdAdcCaptureHandler.h; NOT registered in initCmdProcessTlv2() (cmdProcessTlv2.c)",
            non_destructive_read_only=False,
            classification="SHARED_ONLY",
            evidence_label="CONFIRMED",
            request_fields=[
                "length (A_UINT32)",
                "phyId (A_UINT8)",
                "adcId (A_UINT8)",
                "modeId (A_UINT8)",
                "pad[1] (A_UINT8)",
            ],
            response_fields=[
                "dataI[2048] (A_UINT16)",
                "dataQ[2048] (A_UINT16)",
                "status (A_UINT8)",
                "phyId (A_UINT8)",
                "pad[2] (A_UINT8)",
            ],
            hardware_primitives_invoked=[],
            technical_notes=(
                "TLV2 dictionary ID 59 and 2048-sample I/Q schema exist in shared tlv2p0 headers (Q07, Q09), "
                "guarded by #ifdef USE_TLV2_EXTCMD. However, commonUTF/cmdProcessTlv2.c (Q08) does not "
                "implement or register an ADCCAPTURE handler in the pinned AR9888 UTF tree."
            ),
        ),
        UTFCommandTraceEntry(
            command_name="CMD_GENWAVEFORM",
            command_id=61,
            response_command_name="CMD_GENWAVEFORMRSP",
            response_command_id=62,
            protocol_layer="TLV2_EXTCMD",
            dictionary_source_id="Q07",
            dictionary_path=q07.path,
            parser_header_path=q10.path,
            registration_function="initGENWAVEFORMOpParms / GENWAVEFORMOp",
            registered_in_ar9888_utf=False,
            target_handler_symbol=None,
            target_handler_source_id=None,
            target_handler_path=None,
            build_guard_condition="#ifdef USE_TLV2_EXTCMD in cmdGenWaveformHandler.h; NOT registered in initCmdProcessTlv2() (cmdProcessTlv2.c)",
            non_destructive_read_only=False,
            classification="SHARED_ONLY",
            evidence_label="CONFIRMED",
            request_fields=[
                "waveformIndex (A_UINT16)",
                "phyId (A_UINT8)",
                "pad[1] (A_UINT8)",
            ],
            response_fields=[
                "dataI[2048] (A_UINT16)",
                "dataQ[2048] (A_UINT16)",
                "status (A_UINT8)",
                "phyId (A_UINT8)",
                "pad[2] (A_UINT8)",
            ],
            hardware_primitives_invoked=[],
            technical_notes=(
                "TLV2 dictionary ID 61 and 2048-sample I/Q waveform buffer exist in shared tlv2p0 headers "
                "(Q07, Q10) under #ifdef USE_TLV2_EXTCMD, but no target handler is registered in "
                "initCmdProcessTlv2() (Q08) for AR9888. In AR9888 UTF, continuous waveform/tone generation "
                "instead uses tcmd_cont_tx_sine() / tcmd_cont_tx_cwtone() in tcmd.c (Q03)."
            ),
        ),
        UTFCommandTraceEntry(
            command_name="SYSCMD_PHYDBGDUMP",
            command_id=10009,
            response_command_name="SYSCMD_PHYDBGDUMPRSP",
            response_command_id=10010,
            protocol_layer="TLV2_SYSCMD",
            dictionary_source_id="Q07",
            dictionary_path=q07.path,
            parser_header_path="dl/wlan/halphy_tools/common/tlv2p0/include/sysCmdPhyDbgDump.h",
            registration_function="initPHYDBGDUMPOpParms / PHYDBGDUMPOp",
            registered_in_ar9888_utf=False,
            target_handler_symbol=None,
            target_handler_source_id=None,
            target_handler_path=None,
            build_guard_condition="SYSCMD enum in cmdRspParmsDict.h (ID 10009); NOT registered in AR9888 commonUTF/cmdProcessTlv2.c",
            non_destructive_read_only=True,
            classification="SHARED_ONLY",
            evidence_label="CONFIRMED",
            request_fields=[" dumpOption (A_UINT32)", "phyId (A_UINT8)"],
            response_fields=["data4k[4096] (A_UINT8)", "status (A_UINT8)", "phyId (A_UINT8)"],
            hardware_primitives_invoked=[],
            technical_notes=(
                "Defined in shared SYSCMD dictionary (ID 10009/10010) for 11ac Wave-2 / Beeliner / Cascade "
                "sysCmd dispatch, but not registered in AR9888 initCmdProcessTlv2() (Q08)."
            ),
        ),
        UTFCommandTraceEntry(
            command_name="CMD_NOISEFLOORREAD",
            command_id=102,
            response_command_name="CMD_NOISEFLOORREADRSP",
            response_command_id=103,
            protocol_layer="TLV2_CMD",
            dictionary_source_id="Q07",
            dictionary_path=q07.path,
            parser_header_path="dl/wlan/halphy_tools/common/tlv2p0/include/cmdNoiseFloorRead.h",
            registration_function="registerNOISEFLOORREADHandler",
            registered_in_ar9888_utf=True,
            target_handler_symbol="noiseFloorReadHandler",
            target_handler_source_id="Q08",
            target_handler_path=q08.path,
            build_guard_condition="Unconditional in commonUTF/cmdProcessTlv2.c (lines 791-947, registered at line 966)",
            non_destructive_read_only=False,
            classification="EXACT_AR9888",
            evidence_label="CONFIRMED",
            request_fields=["freq (A_UINT16)", "chainMask (A_UINT16)", "phyId (A_UINT8)"],
            response_fields=["nfValues[16] (A_UINT32)"],
            hardware_primitives_invoked=[
                "tcmd_get_channel(pParms->freq, wlanMode, 0, &chan, pParms->freq)",
                "whalReset(&chan, 0, WHAL_RESTORE_SW_SETTINGS, WHAL_RESET_CAUSE_FULL_RESET)",
                "OS_REG_READ(PHY_BB_AGC_CONTROL_ADDRESS) & PHY_BB_AGC_CONTROL_DO_NOISEFLOOR_MASK",
                "MS(OS_REG_READ(cca[ch_idx]), PHY_BB_CCA_B0_MINCCAPWR_0)",
            ],
            technical_notes=(
                "Executes a full PHY reset (`whalReset`) on the requested frequency before reading "
                "`PHY_BB_CCA_B0_MINCCAPWR_0` (`0x00009e1c`). Because it calls `whalReset()`, it is "
                "NOT a passive read-only status probe."
            ),
        ),
        UTFCommandTraceEntry(
            command_name="CMD_TXSTATUS",
            command_id=15,
            response_command_name="CMD_TXSTATUSRSP",
            response_command_id=16,
            protocol_layer="TLV2_CMD",
            dictionary_source_id="Q07",
            dictionary_path=q07.path,
            parser_header_path="dl/wlan/halphy_tools/common/tlv2p0/include/cmdTxStatusHandler.h",
            registration_function="registerTXSTATUSHandler",
            registered_in_ar9888_utf=True,
            target_handler_symbol="txStatusHandler",
            target_handler_source_id="Q08",
            target_handler_path=q08.path,
            build_guard_condition="Unconditional in commonUTF/cmdProcessTlv2.c (lines 331-371, registered at line 955)",
            non_destructive_read_only=True,
            classification="EXACT_AR9888",
            evidence_label="CONFIRMED",
            request_fields=["phyId (A_UINT8)", "stopTx (A_UINT8)", "needReport (A_UINT8)"],
            response_fields=[
                "totalPackets",
                "goodPackets",
                "underruns",
                "otherError",
                "excessRetries",
                "shortRetry",
                "longRetry",
                "byteCount",
                "rssi / rssic[3] / rssie[3]",
                "thermCal",
            ],
            hardware_primitives_invoked=[
                "txDataStatsReport(rIdx, pParms->stopTx, replyBuf)",
                "tlv2SendTxStatus(&utf_dev, pParms->phyId, numOfReports, replyBuf)",
            ],
            technical_notes=(
                "When called with stopTx=0, non-destructively reports UTF transmit counters and "
                "whalGetCurrentTemp() thermal calibration readout."
            ),
        ),
        UTFCommandTraceEntry(
            command_name="CMD_RXSTATUS",
            command_id=18,
            response_command_name="CMD_RXSTATUSRSP",
            response_command_id=19,
            protocol_layer="TLV2_CMD",
            dictionary_source_id="Q07",
            dictionary_path=q07.path,
            parser_header_path="dl/wlan/halphy_tools/common/tlv2p0/include/cmdRxStatusHandler.h",
            registration_function="registerRXSTATUSHandler",
            registered_in_ar9888_utf=True,
            target_handler_symbol="rxStatusHandler",
            target_handler_source_id="Q08",
            target_handler_path=q08.path,
            build_guard_condition="Unconditional in commonUTF/cmdProcessTlv2.c (lines 547-572, registered at line 957)",
            non_destructive_read_only=True,
            classification="EXACT_AR9888",
            evidence_label="CONFIRMED",
            request_fields=["phyId (A_UINT8)", "stopRx (A_UINT8)"],
            response_fields=[
                "totalPackets",
                "goodPackets",
                "otherError",
                "crcPackets",
                "decrypErrors",
                "rateBit",
                "rssi / rssic[3] / rssie[3]",
                "evm[3] (per-stream pilot EVM summary)",
                "badrssi / badrssic[3] / badrssie[3]",
                "badevm[3]",
            ],
            hardware_primitives_invoked=[
                "rxDataStatsReport(rIdx, replyBuf)",
                "tlv2SendRxStatus(&utf_dev, pParms->phyId, numOfReports, replyBuf)",
            ],
            technical_notes=(
                "Safe non-destructive RX statistics & per-chain RSSI/EVM readout when stopRx=0."
            ),
        ),
        UTFCommandTraceEntry(
            command_name="CMD_LMQUERY",
            command_id=76,
            response_command_name="CMD_LMQUERYRSP",
            response_command_id=77,
            protocol_layer="TLV2_CMD",
            dictionary_source_id="Q07",
            dictionary_path=q07.path,
            parser_header_path="dl/wlan/halphy_tools/common/tlv2p0/include/cmdLMQueryHandler.h",
            registration_function="initLMQueryHandler",
            registered_in_ar9888_utf=True,
            target_handler_symbol="LMQueryHandler",
            target_handler_source_id="Q08",
            target_handler_path=q08.path,
            build_guard_condition="Unconditional in commonUTF/cmdProcessTlv2.c (registered at line 963)",
            non_destructive_read_only=True,
            classification="EXACT_AR9888",
            evidence_label="CONFIRMED",
            request_fields=["lm_cmdId (A_UINT8)", "pad3[3] (A_UINT8)"],
            response_fields=["status (A_UINT8)", "lm_cmdId (A_UINT8)"],
            hardware_primitives_invoked=["initLMQueryHandler()"],
            technical_notes="Non-destructive Link-Maintenance (LM) state query registered in AR9888 UTF.",
        ),
        UTFCommandTraceEntry(
            command_name="TCMD_CONT_TX_ID",
            command_id=0,
            response_command_name="TCMD_CONT_TX_REPLY",
            response_command_id=0,
            protocol_layer="WMI_TCMD_LEGACY_AND_TLV",
            dictionary_source_id="Q04",
            dictionary_path=q04.path,
            parser_header_path=q04.path,
            registration_function="tcmd_parse_cmd -> processTLVPacket -> txCmdProcessor -> tcmd_cont_tx_cmd",
            registered_in_ar9888_utf=True,
            target_handler_symbol="tcmd_cont_tx_cmd",
            target_handler_source_id="Q03",
            target_handler_path=q03.path,
            build_guard_condition=(
                "Direct switch case TCMD_CONT_TX_ID in tcmd_parse_cmd (tcmd.c:1159-1174) is #if 0 disabled; "
                "active entry path is TC_CMD_TLV_ID (4) / TC_CMDS_ID (3) -> processTLVPacket -> txCmdProcessor -> tcmd_cont_tx_cmd"
            ),
            non_destructive_read_only=False,
            classification="EXACT_AR9888",
            evidence_label="CONFIRMED",
            request_fields=[
                "mode (TCMD_CONT_TX_OFF=0, SINE=1, FRAME=2, TX99=3, TX100=4, CWTONE=5, CLPCPKT=6)",
                "freq (A_UINT32)",
                "dataRate (A_UINT32)",
                "txPwr (A_INT32)",
                "antenna (A_UINT32)",
                "pktSz (A_UINT32)",
                "txChain (A_UINT32)",
                "bandwidth (A_UINT32)",
            ],
            response_fields=["TCMD_CONT_TX status/thermCal"],
            hardware_primitives_invoked=[
                "tcmd_cont_tx_sine(dev, freq, ...)",
                "tcmd_cont_tx_cwtone(dev, freq, gainIdx, chainmask)",
                "tcmd_cont_tx_clpcpkt(dev, freq, gainIdx, chainmask, dacGain, paCfg, tpcm)",
                "tcmd_cont_tx_data(dev, contTx, aifswait, disableContinuousTx, numPkts)",
                "waltest_tx(utf_dev.pdev, &utf_dev, tcmd_tx_complete_handler, NULL)",
            ],
            technical_notes=(
                "Provides the real AR9888 continuous sine (`TCMD_CONT_TX_SINE`), CW tone (`TCMD_CONT_TX_CWTONE`), "
                "CLPC packet (`TCMD_CONT_TX_CLPCPKT`), and framed TX99/TX100 generators in `tcmd.c` (`Q03`), "
                "invoked through TLV1/TLV2 `txCmdProcessor` rather than raw legacy `TCMD_CONT_TX_ID`."
            ),
        ),
        UTFCommandTraceEntry(
            command_name="TCMD_CONT_RX_ID",
            command_id=1,
            response_command_name="TCMD_CONT_RX_REPLY",
            response_command_id=1,
            protocol_layer="WMI_TCMD_LEGACY_AND_TLV",
            dictionary_source_id="Q04",
            dictionary_path=q04.path,
            parser_header_path=q04.path,
            registration_function="tcmd_parse_cmd -> processTLVPacket -> rxCmdProcessor -> tcmd_cont_rx_cmd",
            registered_in_ar9888_utf=True,
            target_handler_symbol="tcmd_cont_rx_cmd",
            target_handler_source_id="Q03",
            target_handler_path=q03.path,
            build_guard_condition=(
                "Direct switch case TCMD_CONT_RX_ID in tcmd_parse_cmd (tcmd.c:1175-1182) is #if 0 disabled; "
                "active entry path is TC_CMD_TLV_ID (4) / TC_CMDS_ID (3) -> processTLVPacket -> rxCmdProcessor -> tcmd_cont_rx_cmd"
            ),
            non_destructive_read_only=False,
            classification="EXACT_AR9888",
            evidence_label="CONFIRMED",
            request_fields=[
                "act (PROMIS=0, FILTER=1, REPORT=2, SETMAC=3, EPI=4, SET_ANT_SWITCH_TABLE=5)",
                "freq (A_UINT32)",
                "wlanMode (A_UINT32)",
                "rxChain (A_UINT32)",
            ],
            response_fields=["totalPkt", "okPkt", "crcErrPkt", "secErrPkt", "rssiInDBm", "evm0..2"],
            hardware_primitives_invoked=[
                "tcmd_cont_rx_begin(dev, act, ...)",
                "waltest_rx(utf_dev.pdev, &utf_dev, tcmd_rx_complete_handler, NULL)",
                "utfRxStop(&utf_dev)",
            ],
            technical_notes=(
                "When act == TCMD_CONT_RX_REPORT (2), reads accumulated RX packet/CRC/RSSI/EVM statistics "
                "without resetting the radio."
            ),
        ),
        UTFCommandTraceEntry(
            command_name="TCMD_SET_REG_ID",
            command_id=5,
            response_command_name=None,
            response_command_id=None,
            protocol_layer="WMI_TCMD_LEGACY",
            dictionary_source_id="Q04",
            dictionary_path=q04.path,
            parser_header_path=q04.path,
            registration_function=None,
            registered_in_ar9888_utf=False,
            target_handler_symbol=None,
            target_handler_source_id="Q03",
            target_handler_path=q03.path,
            build_guard_condition="Defined in testcmd_ar988x.h (TCMD_SET_REG_ID = 5), but omitted from switch(testCmdId) in tcmd_parse_cmd() (tcmd.c:1157-1231)",
            non_destructive_read_only=False,
            classification="NOT_FOUND",
            evidence_label="CONFIRMED",
            request_fields=[
                "testCmdId (A_UINT32 = 5)",
                "regAddr (A_UINT32)",
                "val (A_UINT32)",
                "flag (A_UINT16)",
            ],
            response_fields=[],
            hardware_primitives_invoked=[],
            technical_notes=(
                "Although `TCMD_SET_REG` and `TCMD_SET_REG_ID = 5` are declared in `dl/include/testcmd_ar988x.h` (`Q04`), "
                "`tcmd_parse_cmd()` in `tcmd.c` (`Q03`) only accepts `TC_CMD_TLV_ID` (`4`) and `TC_CMDS_ID` (`3`) "
                "and returns `A_ERROR` for `TCMD_SET_REG_ID`. Register reads/writes in AR9888 UTF must use TLV2 "
                "`CMD_REGREAD` (`9`) / `CMD_REGWRITE` (`11`) or `CMD_MEMREAD` (`42`) / `CMD_MEMWRITE` (`40`)."
            ),
        ),
    ]


def build_utf_handler_trace_summary() -> Dict[str, Any]:
    """Return a structured summary of all traced AR9888 UTF commands and classifications."""
    traces = build_ar9888_utf_command_traces()
    by_class: Dict[str, List[str]] = {k: [] for k in sorted(VALID_CLASSIFICATIONS)}
    for entry in traces:
        by_class[entry.classification].append(entry.command_name)

    non_destructive_commands = [
        entry.command_name for entry in traces if entry.non_destructive_read_only and entry.registered_in_ar9888_utf
    ]

    return {
        "schema_version": "1.0",
        "workstream": "E3_UTF_COMMAND_HANDLER_TRACER",
        "repository": STARLINK_WIFI_REPO,
        "commit": STARLINK_WIFI_COMMIT,
        "total_commands_traced": len(traces),
        "classification_counts": {k: len(v) for k, v in by_class.items()},
        "commands_by_classification": by_class,
        "safe_non_destructive_ar9888_utf_commands": non_destructive_commands,
        "key_conclusions": {
            "adccapture_id_59": (
                "SHARED_ONLY: Defined in cmdRspParmsDict.h (ID 59) and cmdAdcCaptureHandler.h (#ifdef USE_TLV2_EXTCMD), "
                "but NOT registered in AR9888 initCmdProcessTlv2() (cmdProcessTlv2.c)."
            ),
            "genwaveform_id_61": (
                "SHARED_ONLY: Defined in cmdRspParmsDict.h (ID 61) and cmdGenWaveformHandler.h (#ifdef USE_TLV2_EXTCMD), "
                "but NOT registered in AR9888 initCmdProcessTlv2(). Continuous sine/CW tone generation in AR9888 UTF "
                "is implemented via tcmd_cont_tx_sine() and tcmd_cont_tx_cwtone() in tcmd.c (Q03)."
            ),
            "phydbgdump_id_10009": (
                "SHARED_ONLY: Defined in cmdRspParmsDict.h (SYSCMD_PHYDBGDUMP = 10009), not wired in AR9888 commonUTF."
            ),
            "regread_regwrite_memread_memwrite": (
                "EXACT_AR9888: Unconditionally implemented and registered in commonUTF/cmdProcessTlv2.c "
                "(regReadHandler ID 9, regWriteHandler ID 11, memWriteHandler ID 40, memReadHandler ID 42)."
            ),
            "tcmd_set_reg_id_5": (
                "NOT_FOUND in dispatcher: Struct TCMD_SET_REG exists in testcmd_ar988x.h (Q04), but tcmd_parse_cmd() "
                "in tcmd.c (Q03) only dispatches TC_CMD_TLV_ID (4) and TC_CMDS_ID (3)."
            ),
        },
        "command_traces": [t.to_dict() for t in traces],
    }


if __name__ == "__main__":
    summary = build_utf_handler_trace_summary()
    print(
        json.dumps(
            {
                "total_commands_traced": summary["total_commands_traced"],
                "classification_counts": summary["classification_counts"],
                "safe_non_destructive_ar9888_utf_commands": summary[
                    "safe_non_destructive_ar9888_utf_commands"
                ],
            },
            indent=2,
        )
    )
