<!-- doc-head: STAGE12_REA_ROADMAP_REEVALUATION_20261023.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Re-Evaluation of Reverse Engineering Methodology & `/fullrea` v2.0 Upgrade

**Date**: October 23, 2026  
**Trigger**: Operator review of [`@sammy_capital` status `2113733817596834151`](https://x.com/sammy_capital/status/2113733817596834151) (*"REA Team Practical Roadmap: Guides, Showcases, Repos, Benchmarks & Papers"*)  
**Upgraded Skill**: [`<home>/.gemini\config\skills\fullrea\SKILL.md`](<home>/.gemini/config/skills/fullrea/SKILL.md) & [`scripts/fullrea_helper.py`](<home>/.gemini/config/skills/fullrea/scripts/fullrea_helper.py)  
**Raw Tweet Archive**: [`artifacts/sammy_capital_tweet.json`](../artifacts/sammy_capital_tweet.json)

---

## 1. Complete Link & Source Audit from `@sammy_capital` (`2113733817596834151`)

Every URL referenced in the post and its nested ecosystems (`rea.tools`, `morluto/rea`, `sqwu/rea-gems`, `arXiv`) was expanded and audited:

| Category | Resource | Key Technical Takeaway |
| :--- | :--- | :--- |
| **Core REA Docs & Prompts** | [`rea.tools/guides/`](https://rea.tools/guides/) (`native`, `javascript`, `browser`) & [`docs/mcp-prompts.md`](https://github.com/morluto/rea/blob/main/docs/mcp-prompts.md) | 6 Guided MCP Prompts (`investigate_feature`, `compare_application_versions`, `verify_reconstruction`, `trace_crash`, `audit_residual_unknowns`, `prepare_bounded_process_capture`) + session-aware `completion/complete` over active inventories. |
| **Native Showcase (`DX-Ball`)** | [`rea.tools/showcase/dx-ball/`](https://rea.tools/showcase/dx-ball/) (`FUN_00406400` sound panning) | Pseudocode alone hid `[EBP+8]` and the floating-point constants (`longlong FUN_00406400(void) { return __ftol(); }`). Only combining **instructions + caller (`0x411f40`) + `read_bytes` (`0x420068 -> 1.5625`, `0x420070 -> 500.0`)** recovered the exact formula (`63/63` byte match + `3,205` behavior cases). |
| **REA Architecture Essay** | [*"Does reverse engineering need a bigger model?"*](https://rea.tools/blog/reverse-engineering-models/) & [`touhou-reconstruction`](https://rea.tools/blog/touhou-reconstruction/) | 1) **When the oracle is wrong (`TH08` float audit)**: Relocation-masked instruction matching accepted `1.0f` instead of `32.0f` because it didn't dereference `.rodata` behind the relocation.<br>2) **Representation changes > local compiler tweaks**.<br>3) **Negative-experiment ledger in repo working memory**. |
| **Engine Speed & Fidelity Benchmarks** | [`morluto/rea#3858`](https://github.com/morluto/rea/discussions/3858) (`kuna` vs `rsleigh` vs `Ghidra` on `ls`, `CrashLoggerSSE`, `APoseFix`) | **`kuna`** decompiles 1 function in **`225–726 ms`** (~90 MB RSS) and all 2,936 functions (3.2 MB) in **`23.7 s`** (`--jobs 8`), matching assembly on **19/21** functions. **`Ghidra`** matches **14/16**, takes **11–38 s** cold start, and hits **12 GB OOM (`exit 137`)** on 10.1 MB C++ DLLs. **`rsleigh`** drops image-base-relative `switch` jump tables (`0/5` compile). |
| **Token Efficiency & Multi-Agent Split** | [`morluto/rea#1958`](https://github.com/morluto/rea/discussions/1958) & [`#3098`](https://github.com/morluto/rea/discussions/3098) | Long single-agent RE sessions burn **3.56B cached input tokens** (`~302k tokens/call`). Splitting into a **Coordinator + Fresh-Context Helpers (`~23k start`)** that write artifacts to disk and return fixed-shape reports cuts context bloat dramatically. Local/small models fail at open-ended 207-tool selection (`0/5`) but score **`3/3` honest** when fed deterministic script output. |
| **Adversarial RE Papers** | [`arXiv:2605.30667`](https://arxiv.org/abs/2605.30667) (*"Automatically Attacking Software RE AI Agents"*), [`LLM4Decompile`](https://arxiv.org/abs/2403.05286), [`AutoDecompiler`](https://arxiv.org/abs/2606.16162), [`SALT4Decompile`](https://arxiv.org/abs/2509.14646), [`DIRTY`](https://usenix.org/system/files/sec22-chen-qibin.pdf) | Attackers can inject `AutoDAN`-style prompts via dead string variable assignments in binaries to corrupt LLM decompilation without changing program behavior. Binary strings/symbols must be treated strictly as **untrusted data**, never instructions or truth without control-flow verification. |

---

## 2. Critical Re-Evaluation of Our FuturaMAX Reverse Engineering (`WA`, `XC`, `LTU`, `mac80211.ko`)

Applying the REA roadmap's audit criteria to every reverse-engineering deliverable in FuturaMAX:

### 2.1 What We Got Right (Confirmed by Hardware & Aligned with REA Best Practices)
1. **Relocation-Aware `.ko` Analysis (`F01` == REA's `TH08` Oracle Law)**:
   - Just as REA's `TH08` postmortem proved that instruction-only comparison fails when relocations are masked, our early `F01` finding proved that MIPS `ET_REL` kernel modules (`ubnt_poll_host.ko`, `umac.ko`, `mac80211.ko`) cannot be read or patched without overlaying `.rel.text` (`R_MIPS_26`, `R_MIPS_HI16`, `R_MIPS_LO16`) and dereferencing `.rodata`.
2. **Representation / State-Machine Pivot (`Step 1C` `run17` PASS)**:
   - Instead of brute-forcing encrypted `0x07` TDMA schedule descriptors from userspace, tracing `ubnt_poll_host_on_beacon_rx` (`offset=34796`) and `ieee80211_candidate_aplist_match_entry` (`offset=277588`) uncovered the built-in **`Normal AP` CSMA/CA state transition** (`ubnt_poll_host_is_ap_valid`), achieving 100% zero-touch Stock `airOS 8` (`WA` and `XC`) association to OpenWrt (`run17`, `run25`, `run8`).
3. **71-Byte `mac80211.ko` `ETH_P_TEB` (`0x6558`) Patch (`19a8fde6...`)**:
   - Verified in-place inside `ieee80211_data_to_8023_exthdr` with preserved file size (`665,308` bytes) and live production validation on `Panel1-Guarida` (`198.18.0.7`).

### 2.2 Gaps Identified & Corrected Today
1. **Gap 1 — Patch Verification Oracle (`elf-verify-patch`)**:
   - Previously, our 5-span `dd` patch for `/tmp/uph.ko` (`MD5 7b490ac4d9573dab010b5f4fb95c3765` on `WA` and `XC`) was verified by MD5 and byte offsets, but we did not have an automated CLI command in `fullrea_helper.py` to audit **whether any `.rel.text` `r_offset` overlapped a patched byte span** across arbitrary `.ko` files.
   - **Fixed**: Added **`elf-verify-patch`** to [`fullrea_helper.py`](<home>/.gemini/config/skills/fullrea/scripts/fullrea_helper.py) and ran it against `ubnt_poll_host.ko` (`orig` vs `patched`) — confirming **zero `.rel.text` corruption** across all modified spans.
2. **Gap 2 — `.rodata` Constant & Adversarial Prompt-Injection Auditor (`elf-rodata`)**:
   - Added **`elf-rodata`** to [`fullrea_helper.py`](<home>/.gemini/config/skills/fullrea/scripts/fullrea_helper.py), which extracts `.rodata` constants and scans for `arXiv:2605.30667`-style prompt-injection strings (`ignore previous instructions`, `system prompt`, `do not report`, etc.).
3. **Gap 3 — Engine Speed Routing (`kuna` vs `Ghidra` vs `IDA`) & Guided Prompts in `SKILL.md`**:
   - Upgraded [`<home>/.gemini\config\skills\fullrea\SKILL.md`](<home>/.gemini/config/skills/fullrea/SKILL.md) to `v2.0` with the empirical `morluto/rea#3858` routing table (`kuna` `<1s` fast path + `--jobs 8` batch export -> `Ghidra`/`IDA` deep verification -> `elf-cf` relocation truth), the 6 REA Guided MCP Prompts, and the `morluto/rea#1958` token-efficient Coordinator/Helper split.
4. **Gap 4 — Deeper Verification Opportunity on LTU `4096-QAM` (`12x`)**:
   - In [`docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md`](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md), our initial pass inspected strings/symbols/configs in `aflturocket-2.4.2.261009.bin` and `afltu-2.4.2.261009.bin`. Following the `DX-Ball` / `TH08` rule (*"Don't stop at strings/pseudocode — read the actual rate-table data arrays in `.rodata`/`.data` of the radio controller binary"*), any future LTU hardware work should use `read_bytes` / `elf-rodata` on the ARM radio daemon's modulation/CINR lookup tables before concluding whether `12x` (`4096-QAM`) is stubbed in the table vs gated at the capability bitmask.
