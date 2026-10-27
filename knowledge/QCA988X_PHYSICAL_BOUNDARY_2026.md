<!-- doc-head: Audited QCA988x physical-boundary source synthesis -->
PB-000 separates exact descriptor contracts, build inclusion and physical capability.
The exact AR9888/v2 headers describe capture, H-info, EVM and timing metadata.
The public AR9888 UTF build graph is incomplete; no build or boot is accepted.
Shared ADC/waveform ABIs do not prove an AR9888 implementation or host-IQ TX.
Raw samples, writable mapper/pilot/FEC and calibrated CSI export remain UNKNOWN.
This delivery is static analysis only; E2 remains NOT_ACCEPTED.
<!-- /doc-head -->

# QCA988x physical boundary — audited 2026-10-24

Authority: [source audit](../research/physical_boundary/source_audit.md),
[per-file hash manifest](../research/physical_boundary/source_manifest.json) and
[evidence delta](../research/physical_boundary/evidence_delta_2026-10-24.md).
The [unaltered report](../research/raw/operator-unrecorded/operator-unrecorded-391b2361/openMAX_QCA988x_physical_boundary_research_2026-10-24.md)
is a research input; its conclusions are not automatically acceptance evidence.
Its 112607 bytes hash to
`391b2361b0097b69a3e5fc526f620bc2253b0e87ba1df077139f00310c2ad843`.
Provider/model and generation times are **UNKNOWN**; the intake timestamp is distinct.

## Four different boundaries

| Boundary | Source-supported answer | Limit of that answer |
|---|---|---|
| Ubiquiti software/scheduler | **CONFIRMED**, retained project research identifies role-specific target images and proprietary polling code. | It does not provide an open replacement or measured scheduler timing. [Held firmware analysis](RADIO_FIRMWARE_ANALYSIS.md), [datapath](../docs/UMAC_DATAPATH.md). |
| Qualcomm production firmware | **CONFIRMED**, normal ath10k delegates time-critical rate behavior and exchanges WMI/HTT with the target. | Replacing mac80211 rate control does not replace target policy; a host command is not proof of per-frame execution. [Control boundary](../docs/QCA988X_CONTROL_BOUNDARY.md). |
| Standard implementation | **CONFIRMED**, exact `series_bw` descriptors select standard legacy/HT/VHT encodings and coding options. | No free-form constellation/FEC interface is described there; reserved/common fields do not certify extra silicon modes. [AR-RATE]. |
| Physical RF/baseband/silicon | **CONFIRMED as documentation**, exact-family descriptors describe channel capture and rich receive metadata. | Actual enablement, memory format, QCA9882 board behavior and calibrated export remain **UNKNOWN**. Header presence is not a hardware measurement. [AR-RX], [AR-TX]. |

## What the new exact-family sources establish

| Claim | Label and precise conclusion | Missing discriminator |
|---|---|---|
| `bb_capture_channel` / `bb_captured_channel` | **CONFIRMED descriptor contract**: request/status fields describe channel capture following a valid packet and firmware-readable channel-dump memory. [AR-TX], [AR-RX]. | Exact installed-image producer, trigger, address, lifetime and repeatable packet-correlated output. |
| `txbf_h_info` | **CONFIRMED descriptor contract**: the receive layout identifies H-information debug content. [AR-RX]. | Framing, dimensions, scaling and usable complex channel estimates on the exact board. |
| `bb_length` | **CONFIRMED descriptor contract** for baseband debug data, with its documented preamble condition. It is **UNKNOWN** whether it measures the channel/H dump. [AR-RX]. | Trace and decode its association with actual captured bytes. |
| compressed V / SVD | **CONFIRMED descriptor contract** for pointer/DMA and SVD-related processing. [AR-TX]. | Runtime enablement, readable V data and utility on a deployed two-chain board. |
| EVM / timestamps | **CONFIRMED fields** in the exact receive descriptor; field names and units are source-bound. [AR-RX]. | Calibration, preservation through the target/HTT path and measured precision. |
| `TARGET=AR9888` UTF | **CONFIRMED build selection**, but the pinned public graph lacks required AR9888 device support. A complete reproducible target build/boot remains **UNKNOWN**. [UTF-MAKE], [UTF-COMPOSE], source audit. | Exact toolchain/core configuration, missing device/library/include/linker dependencies, a known-good binary and independent recovery qualification. |
| `ADCCAPTURE` | **CONFIRMED shared ABI**, not an independently proved AR9888 handler. Extended generated dispatch and nullable callbacks do not establish implementation. [ADC], source audit. | Exact linked registration/implementation or independently qualified target behavior. |
| `GENWAVEFORM` | **CONFIRMED shared ABI**: request selects an index and PHY; I/Q arrays belong to the response. **REFUTED** as evidence of host-supplied arbitrary-IQ transmission through this request. [WAVE]. | Exact AR9888 implementation and meaning of returned samples. |
| ath10k UTF control | **CONFIRMED host source path**, with firmware, build and state prerequisites. Start requires the normal target to be OFF; stop does not itself restore normal WLAN. [TM], [TM-ABI]. | Exact binary/board compatibility, captured exchanges and repeated normal-firmware restoration. |
| BMI / coredump | **CONFIRMED host source mechanisms** for bounded reads and declared QCA988x dump regions. [BMI], [DUMP]. | They do not prove safe arbitrary live reads, a complete map or the channel-dump address. |

## What remains unresolved

**UNKNOWN:** raw ADC/time-domain capture on AR9888; arbitrary TX samples; writable
constellation, pilot or FEC tables; a reproduced open production-target build; exact
target timer jitter; calibrated internal CSI; useful channel-dump memory export.
The evidence above does not settle those questions. A standard rate descriptor is
negative evidence for a trivial new-MCS selector, not proof about every deeper table.
[AR-RATE], [ADC], [WAVE], [source audit](../research/physical_boundary/source_audit.md).

**INFERRED:** later-chip CFR transport may suggest an export architecture or a candidate
packing format. It cannot supply Peregrine command IDs, handler availability or decoding
semantics. QCA9888/QCA9984, LTU and SDR findings retain their different-chip scope.
[Report Q15/A01](../research/openMAX_QCA988x_physical_boundary_research_2026-10-24.md).

**REFUTED as a universal inference:** “normal CSI API absent, therefore CSI physically
impossible” and “host scheduler API absent, therefore polling impossible in silicon.”
The old [CSI verdict](SPECTRAL_AND_CSI_ANALYSIS.md) is superseded to that extent by
the exact descriptor contracts and existing target-image research. Working CSI export
and an open scheduler are still **UNKNOWN**. [AR-RX], [AR-TX], [held target evidence](RADIO_FIRMWARE_ANALYSIS.md).

## Decision and next discriminator

**KEEP** these audited source leads and qualified negatives. All work here belongs to
offline external-controller analysis of source code; no radio was contacted, firmware
built/loaded, test command transmitted or hardware capability accepted.
Other Phase0 workstreams remain owned by their assigned agents; this A/B delivery does
not accept their ladder, oracle, reverse-engineering tools or campaign.

The next physical campaign is **PARKED** in this task. Before a separately authorized
UTF qualification, require exact sacrificial identity and calibration hashes, a known-good
binary/board-data match, independently proved recovery, an exact command allowlist,
timeouts, full byte capture, health checks and repeated normal-firmware restoration.
`UTF_START`, a generic WMI payload, or command-ID naming alone is not a read-only
capability probe. Missing prerequisites are blockers, not an invitation to probe.
[TM], [TM-ABI], [existing recovery boundaries](../safety/recovery/FMX-0002_recovery_runbook.md).

[AR-RX]: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h
[AR-TX]: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/tx_ppdu_start.h
[AR-RATE]: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/include/AR9888/v2/hw/mac_descriptors/series_bw.h
[UTF-MAKE]: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/target/Makefile
[UTF-COMPOSE]: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/target/utf/Makefile
[ADC]: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/common/tlv2p0/include/cmdAdcCaptureHandler.h
[WAVE]: https://github.com/SpaceExplorationTechnologies/starlink-wifi/blob/1d585ee8909bf7bab4391c0c52d8a9d44137b3bb/dl/wlan/halphy_tools/common/tlv2p0/include/cmdGenWaveformHandler.h
[TM]: https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/testmode.c
[TM-ABI]: https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/testmode_i.h
[BMI]: https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/bmi.c
[DUMP]: https://github.com/torvalds/linux/blob/5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f/drivers/net/wireless/ath/ath10k/coredump.c
