<!-- doc-head: Evidence delta from the supplied physical-boundary report -->
Keep prior physical receipts distinct from newly inspected source contracts.
AR9888 descriptors and UTF selection are new exact-family source leads.
Shared commands and later-chip CFR remain outside proved AR9888 runtime capability.
Correct universal CSI, automatic UTF restoration and complete-build interpretations.
The original report and historical project text remain byte-preserved.
No physical performance, CSI export, target build or campaign is accepted here.
<!-- /doc-head -->

# Physical-boundary evidence delta — 2026-10-24

Task: `T-PB-CODEX-01`, Workstreams A/B / PB-000. Use the
[source audit](source_audit.md) and [hash manifest](source_manifest.json) for exact
paths, commits, line ranges, license notes and bounded negative searches.
The [synthesis](../../knowledge/QCA988X_PHYSICAL_BOUNDARY_2026.md) is the current
interpretation; the report's prose is an input, not independent evidence.

## Already established in openMAX

- **CONFIRMED in retained project evidence:** Ubiquiti role-specific target images
  differ from stock and contain proprietary polling markers. This predates the new
  report; no target was extracted or executed again here.
  [knowledge/RADIO_FIRMWARE_ANALYSIS.md](../../knowledge/RADIO_FIRMWARE_ANALYSIS.md).
- **CONFIRMED source boundary:** normal ath10k delegates rate control to firmware;
  host masks/queue policy are not a replacement target scheduler.
  [docs/QCA988X_CONTROL_BOUNDARY.md](../../docs/QCA988X_CONTROL_BOUNDARY.md).
- **CONFIRMED retained offline acceptance:** BM-BP has sealed saved-source results
  and 4282 executed passes, five held skips; it does not accept E2, RF range or a
  hardware coverage-class ceiling. Its seal was freshly verified before PB edits.
  [BM-BP final validation](../../artifacts/autoresearch/waves_bm_to_bp_20261024/final_validation.json),
  [PB before-state](../../artifacts/pb_phase0_codex_20261024/starting_snapshot.json).
- **UNKNOWN in this A/B task:** acceptance of concurrent metric/gatekeeper repairs,
  the experimental ladder, extraction tools and first physical campaign. Their
  assigned owners retain those files; current file presence is not independent acceptance.
  [Phase0 ownership brief](../openMAX_codex_physical_boundary_phase0_prompt.md),
  [task board](../../docs/MULTI_AGENT_TASK_BOARD.md).

## New exact-family source evidence

| Lead | Label | What changed | What did not become proved |
|---|---|---|---|
| AR9888/v2 capture request/status | **CONFIRMED descriptor contract** | `bb_capture_channel` and `bb_captured_channel` explicitly describe a channel-dump mechanism. | The exact board captures usable CSI, the memory address or normal-firmware export. |
| H/debug/EVM/timing metadata | **CONFIRMED fields** | `txbf_h_info`, debug length and rich PPDU metadata justify tracing the pre-export path. | A calibrated per-tone complex matrix, or that `bb_length` measures that matrix. |
| compressed-V/SVD | **CONFIRMED descriptor contract** | DMA/pointer and SVD semantics provide a specific static lead. | Usable beamforming/V output on installed QCA9882 firmware. |
| explicit AR9888 UTF selection | **CONFIRMED selection; incomplete graph** | The public target Makefile selects the family and lists UTF components. | A complete SDK, a reproduced binary, board compatibility or safe target execution. |
| exact standard rate-series layout | **CONFIRMED descriptor contract** | Standard modulation/coding parameters bound the documented normal TX interface. | A global proof that no hidden writable mapper/FEC table exists. |

Sources: pinned AR9888 `rx_ppdu_end.h`, `tx_ppdu_start.h`, `series_bw.h`, target
and UTF Makefiles in [source_manifest.json](source_manifest.json). These are source
contracts, not measurements from our hardware. Public availability does not confer a
license to redistribute every SDK file; proprietary/confidential notices are recorded
and external source contents remain outside this repository.

## Cross-chip inference kept separate

- **INFERRED only:** later QCA WMI10.4 CFR completion, DMA/relay export and candidate
  complex-tone packing could guide a new export design. No opcode or service is
  transferred to Peregrine as fact. [Raw report Q15/A01](../openMAX_QCA988x_physical_boundary_research_2026-10-24.md).
- **UNKNOWN on this target:** functionality inferred from QCA9888/QCA9984, ath9k,
  LTU, SDR or FPGA implementations. Similar names and common descriptor fields do
  not certify chain count, width, timing or new PHY modes.
  [Synthesis](../../knowledge/QCA988X_PHYSICAL_BOUNDARY_2026.md).

## Shared ABI and unsupported claims

- **CONFIRMED shared ABI; UNKNOWN exact runtime:** `ADCCAPTURE` declares I/Q
  response storage, but an extended dispatch stub, a nullable callback and a success
  return without registration do not prove capture. The reviewed AR9888-relevant
  initialization does not register this operation. This is a bounded source negative,
  not a claim that all possible images lack it. [Source audit](source_audit.md).
- **REFUTED for the inspected request ABI:** `GENWAVEFORM` is evidence of a host-IQ
  upload API. Its request carries an index and PHY identifier; the I/Q vectors are
  response fields. Its actual AR9888 implementation remains **UNKNOWN**.
  [Source audit](source_audit.md), pinned `cmdGenWaveformHandler.h` in the manifest.
- **UNKNOWN:** raw ADC stage/format/rate, sample RAM, arbitrary waveform TX,
  writable constellation/pilot/FEC, complete production target source/build,
  exact ISA configuration and measured target timer jitter.
  [Synthesis](../../knowledge/QCA988X_PHYSICAL_BOUNDARY_2026.md).

## Corrections to older repository or report statements

| Earlier interpretation | Current label and correction | Evidence |
|---|---|---|
| “CSI-based optimization is REFUTED on target hardware.” | **REFUTED as a universal inference**; normal API absence remains, accessible calibrated CSI is **UNKNOWN**. | Exact capture/H descriptor contracts; [historical CSI text](../../knowledge/SPECTRAL_AND_CSI_ANALYSIS.md). |
| “QCA988x can never report actual airtime” / “replacement target policy is dead.” | **UNKNOWN as a universal silicon claim**. The retained statements describe normal examined firmware/host APIs, not every custom target implementation. | [Control-boundary dated correction](../../docs/QCA988X_CONTROL_BOUNDARY.md), [held target analysis](../../knowledge/RADIO_FIRMWARE_ANALYSIS.md). |
| “AR9888 UTF public source means a complete reproducible build.” | **UNKNOWN**. Family selection exists; required device/build dependencies are missing or unqualified. | Pinned build files and exact negative path inventory in [source audit](source_audit.md). |
| “UTF_START stops a running normal WLAN.” | **REFUTED for pinned Linux**. It requires OFF and rejects a busy target. | Pinned `testmode.c` in [manifest](source_manifest.json). |
| “UTF_STOP restores normal firmware.” | **REFUTED for pinned Linux**. It tears down UTF to OFF; normal restoration is a separate verified action. | Pinned `testmode.c`. |
| “Every WMI GET_VERSION-looking payload is a read-only status query.” | **REFUTED as a safety inference**. Netlink testmode command IDs and target payload IDs differ; version/data attributes alter interpretation. | Pinned `testmode.c`, `testmode_i.h`; [source audit](source_audit.md). |
| “Host ath10k discards all raw RX descriptor evidence.” | **REFUTED as a universal source statement**. A configured trace path can carry raw descriptor bytes; that does not export channel-dump memory. | Pinned `htt_rx.c` / `trace.h`; [source audit](source_audit.md). |
| “Coredump DRAM range is the full target memory map or a harmless live snapshot API.” | **UNKNOWN**. It is a declared driver dump region with mode/bus/recovery conditions. | Pinned `coredump.c`, BMI/diagnostic read path audit. |

## Intake and preservation

**CONFIRMED:** the original is 112607 bytes, SHA-256
`391b2361b0097b69a3e5fc526f620bc2253b0e87ba1df077139f00310c2ad843`.
The [intake record](../intake/manifest.json) points to
`research/raw/operator-unrecorded/operator-unrecorded-391b2361/openMAX_QCA988x_physical_boundary_research_2026-10-24.md`.
Provider/model, generation prompt and generation timestamps remain **UNKNOWN**.
The selective existing-intake extension preserves all seven prior records/raw primaries
exactly, fails closed if the selected source is absent, and has a disposable regression.
[Verification](../../artifacts/pb_phase0_codex_20261024/intake_verification.json),
[regression receipt](../../artifacts/pb_phase0_codex_20261024/intake_check_receipt.json).
Original failures and their changed diagnostic hypotheses are retained in the same
artifact directory. No generated manifest was hand-edited.

**Decision: KEEP** the audited leads and explicit UNKNOWNs. No hardware was contacted;
no wireless improvement, boot/build, physical acceptance or other agent's deliverable
is claimed. Complete PB-000 only after manifest/source validation, then continue the
already assigned Codex queue.
