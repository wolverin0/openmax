<!-- doc-head: STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md complete-content router and exact original backup -->
<!-- /doc-head -->

# STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE: complete document

All substantive text is preserved in the continuation pages below, in original order.
These pages form this document; this router changes no acceptance claim.
[Exact original bytes](../artifacts/documentation/stage822a/fa15300e2006cf82f8640f193277f8c44758be86995e2561e568cc107373226c/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md.original.txt) (SHA-256 `fa15300e2006cf82f8640f193277f8c44758be86995e2561e568cc107373226c`).

## Complete content
- [Part 1/2](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md)
- [Part 2/2](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_002.md)

## Original section routes
<a id="october23-current-result-native-ltu-probe-restored-rocket-inventory-captured"></a> [October23 current result: native LTU probe restored; Rocket inventory captured](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#october23-current-result-native-ltu-probe-restored-rocket-inventory-captured)
<a id="october23-historical-d2-observation-before-operator-physical-confirmation"></a> [October23 historical D2 observation before operator physical confirmation](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#october23-historical-d2-observation-before-operator-physical-confirmation)
<a id="october22-evidence-alignment---current-bench-scope"></a> [October22 evidence alignment - current bench scope](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#october22-evidence-alignment---current-bench-scope)
<a id="stage-11b--static-reverse-engineering-of-ubiquiti-ltu-aflturocket-242--afltu-242-dual-soc-sdr-architecture-4096-qam-12x-code-paths--ofdma-subband-hooks"></a> [Stage 11B — Static Reverse Engineering of Ubiquiti `LTU` (`aflturocket-2.4.2` & `afltu-2.4.2`): Dual-SoC SDR Architecture, `4096-QAM` (`12X`) Code Paths & `OFDMA` Subband Hooks](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#stage-11b--static-reverse-engineering-of-ubiquiti-ltu-aflturocket-242--afltu-242-dual-soc-sdr-architecture-4096-qam-12x-code-paths--ofdma-subband-hooks)
<a id="1-executive-summary--epistemic-status"></a> [1. Executive Summary & Epistemic Status](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#1-executive-summary--epistemic-status)
<a id="2-exact-ameimg-container-parts--dtb-nand-partition-map-f08-remediated"></a> [2. Exact `AMEIMG` Container Parts & DTB NAND Partition Map (`F08` Remediated)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#2-exact-ameimg-container-parts--dtb-nand-partition-map-f08-remediated)
<a id="a-ameimg-container-parts-containersjson--0-trailing-bytes-all-15-payload-md5s-verified"></a> [A. `AMEIMG` Container Parts (`containers.json` — 0 Trailing Bytes, All 15 Payload MD5s Verified)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#a-ameimg-container-parts-containersjson--0-trailing-bytes-all-15-payload-md5s-verified)
<a id="b-primary-amesoc3-nand-flash-partition-map-dtb_propertiesjson--static-dtb-evidence"></a> [B. Primary `amesoc3` NAND Flash Partition Map (`dtb_properties.json` — Static DTB Evidence)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#b-primary-amesoc3-nand-flash-partition-map-dtb_propertiesjson--static-dtb-evidence)
<a id="3-corrected-ltu-modulation--rate-code-table-f10-remediated"></a> [3. Corrected `LTU` Modulation & Rate-Code Table (`F10` Remediated)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#3-corrected-ltu-modulation--rate-code-table-f10-remediated)
<a id="4-non-destructive-live-bench-test-plan-for-ltu-lite--ltu-rocket-f09f11-f13-remediated"></a> [4. Non-Destructive Live Bench Test Plan for `LTU-Lite` & `LTU-Rocket` (`F09–F11`, `F13` Remediated)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_001.md#4-non-destructive-live-bench-test-plan-for-ltu-lite--ltu-rocket-f09f11-f13-remediated)
<a id="5-physical-lab-bench-qualification-results-on-ltu-lite-2026-10-21"></a> [5. Physical Lab Bench Qualification Results on `LTU-Lite` (`2026-10-21`)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_002.md#5-physical-lab-bench-qualification-results-on-ltu-lite-2026-10-21)
<a id="51-step-1-results--live-hardware-nand-partition-map--capability-bits-confirmed"></a> [5.1 Step 1 Results — Live Hardware, NAND Partition Map & Capability Bits (`CONFIRMED`)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_002.md#51-step-1-results--live-hardware-nand-partition-map--capability-bits-confirmed)
<a id="52-step-2-results--live-4096-qam-12x-0x1f-kernel--scheduler-activation-confirmed"></a> [5.2 Step 2 Results — Live `4096-QAM` (`12X`, `0x1f`) Kernel & Scheduler Activation (`CONFIRMED`)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_002.md#52-step-2-results--live-4096-qam-12x-0x1f-kernel--scheduler-activation-confirmed)
<a id="53-step-3-results--live-ofdma-subband-mask--persistence-hooks-confirmed"></a> [5.3 Step 3 Results — Live `OFDMA` Subband Mask & Persistence Hooks (`CONFIRMED`)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_002.md#53-step-3-results--live-ofdma-subband-mask--persistence-hooks-confirmed)
