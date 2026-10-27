<!-- doc-head: Stage526A saved PB040/PB050 checksums and static vendor SGMT boundaries -->
Endpoint-specific saved text is not proof of loaded payload, patch acceptance or ABI.
<!-- /doc-head -->

# Stage526A

Parent: fixed525A..530A offline RE1/control-boundary queue in BENCH_PLAN.
Run `python tools/autoresearch/build_stage526a_xtensa_ram_canary_pb040_pb050_abi_auditor.py`.
No producer import, decoder/helper re-execution, target/network/subprocess action,
firmware payload export, patch construction, flash or regulatory change occurs.

## Saved endpoint differences

| Source | Diagnostic checksums firmware-N / athwlan | SHA256 path evidence | Limit |
| --- | --- | --- | --- |
|403 AP |912bcb63 /278d2d76 |/lib and/tmp candidate8d50c1ce... |Saved consistency, no native acquisition chain |
|403 CPE |3e4cf97f /477a6960 |/lib stock398e4380...;/tmp candidate8d50c1ce... |Does not support both ends patched |
|507 AP/CPE |92363606 /12b29d01 |Only/tmp candidatea49160ff... |No/lib SHA or bind/reload/loaded-byte chain |

The strict parser requires complete expected checksum and exact canonical SHA paths.
Duplicate entries, truncated hex, unexpected hash paths, controls, missing fields or
mismatches yield UNKNOWN, never PASS. Raw ignored log lines are not echoed.
Matching text means CONSISTENT_SAVED_READBACK only, not a runtime or ABI verdict.
Neither a filename checksum nor a/tmp SHA proves the currently executing payload.
403/507 record strings from check=False stdout; actual native exit codes are absent.
Exact stock/patched CT payload bytes are not supplied by these pinned receipts.
This is not a claim that such files are absent from every repository or device.

## Register and counterfactual boundary

403 claims a0x13721320->0x13761320 INI shadow. R43 windows retain configured
values only; the helper serializes cfg and drops ap_extra_readback/cpe_extra_readback.
No raw reg_value getter is retained in the PB040 block. Furthermore producer403
directly writes reg_addr0x29e00/reg_value for each arm, so even a genuine matching
getter could not isolate the SGMT patch as its cause. Canary log/payload proof is absent.
R50 simultaneously changes nf_cal_period30->120 and active_fw_stats_poll0->1;
the diagnostic snapshot is taken before trials. No patch-only counterfactual exists.

## Address domains and held static proof

507 reports CT.data vaddr0x0040c140, file offset0x3b1d, .lit4 vaddr0x00980754
and2000->4000ms. They remain distinct reported domains and units, not a patch recipe.
The held Stage17 airOS8.5.12 vendor UMAC46525dc6... has AP segment2 at0x0040d140,
4096 bytes away from the claimed CT address. It is not the CT firmware-2.bin build.
Root's pinned bounded decode metadata has four payloads,309464 decoded bytes,
container55e9c94a.../251681B, matching the old vendor spec. This build rechecks the
actual UMAC container slice, decoder hash and metadata, without repeating decoding
or serializing payload bytes. Metadata consistency is STATIC_ROOT_DECODING_NOT_CT_ABI.
The saved host fullrea BMIFastDownload relocation summary names BMILZStreamStart
and BMILZData. It proves neither native execution nor a0x29e00 write intrinsic.
The external helper hash is reported by its saved receipt, not reverified here.
Named g_rc globals or hardcoded candidate grids do not establish offsets/types/ABI.
No offset is transplanted between vendor/CT images; native ABI acceptance stays false.

Inputs, producer source, old spec, held UMAC/decoder and saved static proof are hashed.
Current bytes are not authenticated historical executed source. Missing native
boot/build/payload/exit/acquisition provenance remains missing. E2 NOT_ACCEPTED.
Decision: KEEP qualified contradiction audit; no new hardware result or RF gain.
