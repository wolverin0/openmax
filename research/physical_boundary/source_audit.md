<!-- doc-head: Pinned AR9888 and Linux source audit with applicability limits -->
Direct source inspection covers the requested AR9888 descriptor, UTF and host paths.
Every file has a pinned commit, SHA256, license note, symbols and applicability.
Descriptor contracts do not certify operational silicon, CSI export or target execution.
AR9888 build dependencies are missing; shared callback wrappers do not prove handlers.
UTF state, transport-version and coredump limits correct report overstatements.
No device contacted, external source vendored, firmware built or other workstream accepted.
<!-- /doc-head -->

# PB-000 source audit — 2026-10-24

Task `T-PB-CODEX-01`, Workstreams A/B only. Branch `main`; starting commit
`0cce9cf76d990861fbd8a78d1f9dfa357df5b369`. This is independent inspection of the
report's source chain, not a reproduction of its hardware claims. No new commit,
push, device contact or firmware build is part of this delivery.

The [source manifest](source_manifest.json) is authoritative for full hashes,
canonical raw-file line numbers, exact-family applicability and licensing. The
two bounded source-audit receipts are [AR9888](../../artifacts/pb_phase0_codex_20261024/starlink_audit.json)
and [Linux](../../artifacts/pb_phase0_codex_20261024/linux_audit.json).
External source was fetched as data into temporary caches outside Git; no downloaded
code was executed. HTTPS commit pinning is not a signature verification or proof of
the installed OpenWrt/ath10k-CT source revision. GitNexus had no matching current
FuturaMAX index, so this audit used exact paths and live source text.

## Repositories and reproduction

- **CONFIRMED source snapshot:** `SpaceExplorationTechnologies/starlink-wifi@1d585ee8909bf7bab4391c0c52d8a9d44137b3bb`. [Pinned commit](https://github.com/SpaceExplorationTechnologies/starlink-wifi/commit/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb).
- **CONFIRMED source snapshot:** `torvalds/linux@5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f`. [Pinned commit](https://github.com/torvalds/linux/commit/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f).

**CONFIRMED:** 49 required source files, 22 scoped claim records. Local cached bytes, sizes and symbol-range bounds were checked while assembling this manifest. For reproduction, fetch each manifest `source_url` into an external temporary directory and verify its `file_sha256` and byte count before inspecting symbols. A cache path is replaceable; the commit, URL, hash and metadata are the retained provenance. Missing files fail validation.

## Exact-family claim decisions

| ID | Label | Audited conclusion | Pinned source ranges |
|---|---|---|---|
| AR9888_UTF_SELECTION | **CONFIRMED**, static scope | TARGET=AR9888 selects UTF and associated target subtrees; it is a conditional source build selection, not a completed firmware build. | [TARGET=AR9888 / SUBDIRS L31-37](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/target/Makefile#L31-L37); [commonUTF device tcmd_utf testScriptIF wmiHostIF utf_cal L21-25](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/target/utf/Makefile#L21-L25); [device/AR9888 selection L23-27](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/target/utf/device/Makefile#L23-L27) |
| CAPTURE_REQUEST | **CONFIRMED**, static scope | Exact AR9888/v2 TX descriptor specifies a BB channel-capture request for a good receive packet. | [bb_capture_channel L512-514](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/tx_ppdu_start.h#L512-L514); [TX_PPDU_START_19_BB_CAPTURE_CHANNEL L1235-1241](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/tx_ppdu_start.h#L1235-L1241) |
| CAPTURE_COMPLETION | **CONFIRMED**, static scope | Exact AR9888/v2 RX descriptor specifies channel-dump completion and firmware-readable channel-dump memory; the comment allows PCU or firmware capture initiation. | [bb_captured_channel L169-174](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h#L169-L174); [RX_PPDU_END_19_BB_CAPTURED_CHANNEL L391-402](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h#L391-L402) |
| BASEBAND_DEBUG_LENGTH | **CONFIRMED**, static scope | bb_length is a byte length for baseband-debug PPDUs with BB-descriptor preamble values0x80..0xFF, not a documented generic CSI/H length. | [bb_length L179-183](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h#L179-L183); [RX_PPDU_END_20_BB_LENGTH L405-419](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h#L405-L419) |
| H_INFORMATION | **CONFIRMED**, static scope | txbf_h_info denotes packet data carrying H information for TXBF debug. | [txbf_h_info L155-157](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h#L155-L157); [RX_PPDU_END_18_TXBF_H_INFO L363-369](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h#L363-L369) |
| COMPRESSED_V_SVD | **CONFIRMED**, static scope | TX descriptor cv_ptr is a DMA pointer to compressed V consumed by BB SVD; cv_len specifies fetched octets and documents0..2047. | [cv_ptr L463-466](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/tx_ppdu_start.h#L463-L466); [cv_len L520-523](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/tx_ppdu_start.h#L520-L523); [CV_PTR L1146-1153](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/tx_ppdu_start.h#L1146-L1153); [CV_LEN L1251-1258](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/tx_ppdu_start.h#L1251-L1258) |
| EVM_METADATA | **CONFIRMED**, static scope | RX PPDU-end declares16EVM words; each documented pilot word contains EVM for streams0..3. | [evm_p0..evm_p15 L14-29](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h#L14-L29); [pilot/stream EVM descriptions L76-122](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h#L76-L122) |
| TIMESTAMPS | **CONFIRMED**, static scope | RX contract defines32-bit TSF and WLAN/BT timestamps plus8-bit fractional-location timestamp. WLAN/BT is described at1us resolution, without beacon updates; fractional clock80MHz/12.5ns is an example. | [tsf_timestamp / wb_timestamp / locationing_timestamp L124-143](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h#L124-L143); [timestamp masks L307-339](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h#L307-L339) |
| STANDARD_MCS_BOUNDARY | **CONFIRMED**, static scope | series_bw documents4-bit rate with2-bit preamble selector: OFDM,CCK,HT,VHT; VHT encoding is legal0..9 through256-QAM. Descriptor also exposes NSS,LDPC,STBC,SGI and TXBF. | [rate/nss/preamble_type and coding fields L24-43](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/series_bw.h#L24-L43); [rate and preamble enumerations L119-186](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/series_bw.h#L119-L186) |
| ADC_SHARED_ABI | **CONFIRMED**, static scope | Shared extended TLV2 dictionary defines ADCCAPTURE59/response60; request is length:uint32 plus phyId/adcId/modeId:uint8, response has2048uint16 I and2048uint16 Q plus status/phyId. | [CMD_ADCCAPTURE/CMD_ADCCAPTURERSP L130-133](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/common/tlv2p0/include/cmdRspParmsDict.h#L130-L133); [USE_TLV2_EXTCMD / parameter structs L3-31](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/common/tlv2p0/include/cmdAdcCaptureHandler.h#L3-L31); [extended shared dispatch entries L76-80](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/common/tlv2p0/cmdParser/cmdHandlerTbl.c#L76-L80) |
| ADC_REGISTRATION_BOUNDARY | **UNKNOWN**, static scope | No concrete AR9888 ADCCAPTURE callback registration was found in the reviewed target startup/dispatch/TCMD files. Shared generated wrapper initializes callbackNULL, calls only if nonNULL, and returnsTRUE even without a callback. | [registerADCCAPTUREHandler / ADCCAPTUREOp L32-57](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/common/tlv2p0/cmdParser/cmdAdcCaptureHandler.c#L32-L57); [initCmdProcessTlv2 L950-967](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/target/utf/commonUTF/cmdProcessTlv2.c#L950-L967) |
| GENWAVEFORM_INPUT | **CONFIRMED**, static scope | Shared GENWAVEFORM61/response62 request contains waveformIndex:uint16 and phyId:uint8 only. The2048I/Q arrays are response fields, not host-supplied sample input. | [CMD_GENWAVEFORM/CMD_GENWAVEFORMRSP L134-137](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/common/tlv2p0/include/cmdRspParmsDict.h#L134-L137); [request/response distinction L3-29](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/common/tlv2p0/include/cmdGenWaveformHandler.h#L3-L29); [request initialization L8-25](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/common/tlv2p0/cmdParser/cmdGenWaveformHandler.c#L8-L25); [callback boundary L28-51](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/common/tlv2p0/cmdParser/cmdGenWaveformHandler.c#L28-L51) |
| UTF_BUILD_COMPLETENESS | **UNKNOWN**, static scope | The published selected build graph is incomplete in the reviewed snapshot: device/Makefile selects AR9888 but its pinned parent listing contains only AR900B,common,Makefile; the AR9888 directory request returns404. Ancestor dl/wlan/Makefile and dl/Makefile raw requests also return404. | [AR9888 prerequisite L23-27](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/target/utf/device/Makefile#L23-L27); [ancestor Makefile recursion L63-64](https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/target/utf/Makefile#L63-L64) |
| LINUX-UTF-STATE | **CONFIRMED**, static scope | Report sections3.2 and4.2 inaccurately imply that UTF_START stops normal WLAN. It requires OFF and returns EBUSY when active. UTF_STOP ends in OFF; normal WLAN is not restored automatically. | [ath10k_tm_cmd_utf_start L336-441](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/testmode.c#L336-L441); [__ath10k_tm_cmd_utf_stop / ath10k_tm_cmd_utf_stop L443-492](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/testmode.c#L443-L492) |
| LINUX-UTF-ABI | **CONFIRMED**, static scope | Raw WMI and segmented TLV transports exist. API1 fallback forces10.1 operation versions, but the segmented path sends literal WMI_PDEV_UTF_CMDID while10x has its own command map. Generic segmentation is not a qualified exact-AR9888 exchange. | [ath10k_tm_cmd_tlv L550-627](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/testmode.c#L550-L627); [wmi_10x_cmd_map.pdev_utf_cmdid L303-310](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/wmi.c#L303-L310) |
| LINUX-VERSION-ALIAS | **CONFIRMED**, static scope | GET_VERSION queries the host testmode ABI, not target capabilities. Adding DATA changes command zero into TLV transmission. A future version-only allowlist must require DATA to be absent. | [ath10k_tm_cmd L629-659](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/testmode.c#L629-L659); [enum ath10k_tm_cmd L36-75](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/testmode_i.h#L36-L75) |
| LINUX-SEGMENT-GUARDS | **CONFIRMED**, static scope | The receiver checks minimum header size and the2048-byte accumulation cap. It does not compare current_seq with expected_seq or validate msgref and advertised total length. The5000-byte input policy can require20chunks although the segment count is four bits. No safe payload limit or robust session validation is established. No fuzzing, exploitation or device execution was performed. | [ath10k_tm_event_segmented L79-158](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/testmode.c#L79-L158); [ath10k_tm_cmd_tlv L550-627](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/testmode.c#L550-L627); [ATH10K_TESTMODE_VERSION_* / buffer constants L10-18](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/testmode_i.h#L10-L18) |
| LINUX-BMI-PHASE | **CONFIRMED**, static scope | BMI read_memory uses a distinct READ opcode,256-byte chunks, the done_sent EBUSY gate and HIF error propagation. Memory/register writes, execute and download are separate operations. This boot interface is not ordinary runtime firmware access and provides no experiment-specific address or register-side-effect allowlist. | [ath10k_bmi_read_memory L155-195](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/bmi.c#L155-L195); [BMI interface documentation / BMI_MAX_DATA_SIZE L12-40](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/bmi.h#L12-L40) |
| LINUX-COREDUMP | **CONFIRMED**, static scope | The QCA988X hw2 PCI table confirms DRAM at0x400000 with length0x50000, not the whole memory map. RAM dumping requires DEV_COREDUMP, the RAM mask bit, a matching target/hardware/bus tuple, allocated storage and successful diagnostic reads. The default mask omits RAM. Dumps can be partial; crash recovery and CE activity are not passive or proven health-preserving. | [qca988x_hw20_mem_regions L986-1017](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/coredump.c#L986-L1017); [ath10k_coredump_get_mem_layout / _ath10k_coredump_get_mem_layout L1450-1474](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/coredump.c#L1450-L1474); [ath10k_coredump_mask / module parameters L44-62](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/core.c#L44-L62); [ath10k_pci_fw_dump_work L1750-1779](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/pci.c#L1750-L1779) |
| LINUX-RX-EXPORT | **CONFIRMED**, static scope | The pinned source refutes an absolute claim that stock ath10k never exports raw RX descriptor bytes. An optional trace event copies the descriptor array, including version1 QCA988X PPDU metadata. One AMSDU path omits its first u32; a monitor AMSDU physical-address path traces the full descriptor. Ordinary SKB payload strips the descriptor and ordinary RX status does not export a full EVM/H matrix. | [qca988x_rx_desc_ops L135-138](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/htt.c#L135-L138); [ath10k_htt_rx_amsdu_pop L359-442](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/htt_rx.c#L359-L442); [ath10k_htt_rx_handle_amsdu_mon_32 L501-520](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/htt_rx.c#L501-L520); [TRACE_EVENT(ath10k_htt_rx_desc) L424-452](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/trace.h#L424-L452) |
| LINUX-CAPTURE-METADATA | **CONFIRMED**, static scope | Capture/H-info flags, BB debug length, EVM and timestamps are defined in the QCA988X host descriptor. Trace definitions do not prove firmware populates them, appended H data reaches the host, or channel memory address, format, CSI/IQ streaming and ADC capture are known. Existing descriptor tracing is a simpler export lead to assess before new instrumentation. | [RX_PPDU_END_* / rx_ppdu_end_common / rx_ppdu_end_qca988x L926-969](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/rx_desc.h#L926-L969); [txbf_h_info / bb_captured_channel / bb_length documentation L1259-1296](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/rx_desc.h#L1259-L1296) |
| LINUX-RUNTIME-DIAG | **CONFIRMED**, static scope | Conditional debugfs mem_value supports reads and writes, mode0600, ON/UTF state and mutex guards. The PCI reader uses CE/DMA with timeouts and completion checks; it still changes transport state and provides no experimental address allowlist. Source API presence is not installed-target availability. | [ath10k_mem_value_read L754-804](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/debug.c#L754-L804); [ath10k_mem_value_write / fops_mem_value L806-863](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/debug.c#L806-L863); [ath10k_pci_diag_read_mem L903-1008](https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/pci.c#L903-L1008) |

## Interpretation limits and corrections

**CONFIRMED:** the capture/H-info/EVM/timestamp fields are exact AR9888/v2
descriptor contracts. **UNKNOWN:** actual firmware population, QCA9882 board
enablement, channel-dump address/format/lifetime, H dimensions/scaling and calibrated
CSI export. `bb_length` has a documented baseband-debug preamble condition
`0x80..0xFF`; that is a different field from the two-bit TX `series_bw` preamble
selector. WLAN/BT timing is not demonstrated UTC wall-clock time, and the fractional
clock example is not a measured installed-device frequency. See the pinned ranges above.

**CONFIRMED:** normal `series_bw` enumerations select standard rates through VHT
MCS9 and standard coding options. **REFUTED for this interface:** a documented
arbitrary-constellation or higher-MCS selector. **UNKNOWN globally:** hidden writable
mapper/pilot/FEC tables. Common four-stream/160MHz schema text does not certify a
two-chain Wave1 board. Compressed V/SVD descriptor metadata is not arbitrary TX IQ.

**CONFIRMED shared ABI, UNKNOWN exact target:** the ADC and waveform declarations
are under the extended-command path. Shared generated callbacks initialize to NULL;
an operation wrapper may return TRUE without a concrete callback. That is not a
command-completion measurement. `GENWAVEFORM` request fields select an index/PHY;
I/Q arrays are response fields. **REFUTED for this request:** host-supplied arbitrary
IQ upload. The reviewed initialization lacks the ADC/waveform registrations; the
bounded searches below do not prove global absence.

**CONFIRMED host-source correction:** UTF start requires OFF; it does not tear down
an active WLAN. Stop returns OFF and requires a separate normal-firmware restoration
path. The no-DATA command-zero query reports host testmode ABI, not target capabilities;
with DATA the same command value selects TLV transmission. Segment transport exists,
but firmware API1/10.1 mapping and segmented command IDs must be qualified together.
The inspected receive assembler has incomplete sequence/session checks; no safe
generic target payload, limit or read-only allowlist is accepted by this audit.

**CONFIRMED:** BMI reads are boot-phase operations gated after BMI_DONE; diagnostic
runtime reads use separate mechanisms. The QCA988x hw2/PCI dump table names DRAM
`0x400000 + 0x50000`; it is not a complete map. RAM dump selection, exact hw/bus match,
buffer allocation and successful diagnostic reads are prerequisites. The default dump
mask does not request RAM. Crash/recovery and CE/DMA activity are not passive observation.
No intentional crash or memory/register operation was performed here.

**CONFIRMED source export refinement:** the configured raw RX descriptor trace is an
existing lead before new driver instrumentation. It does not by itself export appended
H data or separate channel-dump RAM, prove populated fields or establish CSI/raw ADC.

## Bounded build and negative evidence

**CONFIRMED selected build graph:** `halphy_tools -> target(TARGET=AR9888) -> utf -> {commonUTF, device, tcmd_utf, testScriptIF, wmiHostIF, utf_cal}`; device selection requires `common + AR9888`. Static libraries and prerequisites are in the manifest.

**UNKNOWN complete build:** the exact device parent listing includes AR900B/common/Makefile but not the selected AR9888 subtree. Pinned requests also lack the recursive ancestor Makefiles listed below. This identifies a public-SDK-fragment blocker, not proof that no external SDK can supply the missing dependencies. No make/compiler/linker was run; toolchain/core, libraries, linker scripts and a bootable binary remain unqualified.

- **UNKNOWN build prerequisite, absent in reviewed snapshot:** `dl/wlan/halphy_tools/target/utf/device/AR9888`.
- **UNKNOWN build prerequisite, absent in reviewed snapshot:** `dl/wlan/Makefile`.
- **UNKNOWN build prerequisite, absent in reviewed snapshot:** `dl/Makefile`.

- **UNKNOWN beyond bounded scope:** ADC callback registrations; pattern `registerADCCAPTUREHandler`, 21 explicitly listed files. Only shared generated definitions; no concrete target call found. Only downloaded reviewed source files; no whole-repository,link-object,ROM or runtime absence claim. Full paths and hits remain in the manifest.

- **UNKNOWN beyond bounded scope:** waveform callback registrations; pattern `registerGENWAVEFORMHandler`, 21 explicitly listed files. Only shared generated definitions; no concrete target call found. Only downloaded reviewed source files; no whole-repository,link-object,ROM or runtime absence claim. Full paths and hits remain in the manifest.

- **UNKNOWN beyond bounded scope:** extended-command macro enablement; pattern `(?:#\s*define\s+USE_TLV2_EXTCMD|[-/]D\s*USE_TLV2_EXTCMD)`, 21 explicitly listed files. No enablement definition found in reviewed Makefiles/source. Only downloaded reviewed source files; no whole-repository,link-object,ROM or runtime absence claim. Full paths and hits remain in the manifest.

- **UNKNOWN beyond bounded scope:** capture-field consumers within selected target source; pattern `bb_capture_channel|bb_captured_channel|txbf_h_info|bb_length`, 21 explicitly listed files. No field consumer found in the selected downloaded target/TCMD text. Only downloaded reviewed source files; no whole-repository,link-object,ROM or runtime absence claim. Full paths and hits remain in the manifest.


## License and provenance handling

**CONFIRMED from inspected notices:** the Linux subset uses its recorded SPDX
licenses. Several Qualcomm-derived SDK files carry all-rights-reserved or
confidential/proprietary markers; no permissive redistribution grant was established
for them. Public hosting alone is not treated as such a grant. The repository retains
paths, hashes, paraphrased conclusions and line metadata, not those source bodies,
firmware blobs or an external tree. Per-file exceptions and notes remain explicit.

## Acceptance boundary and next action

**KEEP** the source leads and qualified negatives. **UNKNOWN** remains for raw ADC,
arbitrary TX IQ, writable PHY tables, a reproducible complete UTF/production build,
actual target timer jitter and calibrated internal CSI. The [synthesis](../../knowledge/QCA988X_PHYSICAL_BOUNDARY_2026.md)
and [delta](evidence_delta_2026-10-24.md) record corrections without erasing history.

This accepts only A/B source work. It does not accept other agents' oracle, ladder,
reverse-engineering tools or physical campaign. No physical action is required to
complete this task. Future UTF start/stop must remain parked until exact sacrificial
identity, binary/board provenance, independently qualified recovery, an exact command
allowlist, byte capture, timeouts, health checks and normal-firmware restoration are
proved under separate authority. User instruction in this task forbids radio contact.
E2 stays NOT_ACCEPTED. After A/B verification, complete the board task and immediately
claim the next Codex READY task for saved-source waves.
