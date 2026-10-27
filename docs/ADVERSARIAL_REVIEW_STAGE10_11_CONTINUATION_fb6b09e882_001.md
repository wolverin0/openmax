<!-- doc-head: ADVERSARIAL_REVIEW_STAGE10_11.md continuation 1 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](ADVERSARIAL_REVIEW_STAGE10_11.md) | Part 1/3
<a id="f05--high-the-prism-algorithm-tests-the-full-channel-interval"></a> [F05 — HIGH: the prism algorithm tests the full channel interval](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f05--high-the-prism-algorithm-tests-the-full-channel-interval) | <a id="f06--high-the-purported-hsr-spigpio-sequence-is-misattributed"></a> [F06 — HIGH: the purported HSR SPI/GPIO sequence is misattributed](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f06--high-the-purported-hsr-spigpio-sequence-is-misattributed) | <a id="f07--medium-spectral-filtering-and-hybrid-mode-need-narrower-claims"></a> [F07 — MEDIUM: spectral filtering and hybrid mode need narrower claims](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f07--medium-spectral-filtering-and-hybrid-mode-need-narrower-claims) | <a id="detailed-findings--stage-11b-ltu-4096-qam-ofdma-and-architecture"></a> [Detailed findings — Stage 11B: LTU 4096-QAM, OFDMA and architecture](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#detailed-findings--stage-11b-ltu-4096-qam-ofdma-and-architecture) | <a id="f08--critical-the-published-flash-map-contradicts-the-actual-dtb"></a> [F08 — CRITICAL: the published flash map contradicts the actual DTB](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f08--critical-the-published-flash-map-contradicts-the-actual-dtb) | <a id="f09--high-meaningful-4096-qam-software-exists-a-qualified-ptmp-unlock-is-unproven"></a> [F09 — HIGH: meaningful 4096-QAM software exists; a qualified PtMP unlock is unproven](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f09--high-meaningful-4096-qam-software-exists-a-qualified-ptmp-unlock-is-unproven) | <a id="f10--high-rate-mapping-is-wrong-and-ceiling-is-not-fixed-modulation"></a> [F10 — HIGH: rate mapping is wrong, and ceiling is not fixed modulation](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f10--high-rate-mapping-is-wrong-and-ceiling-is-not-fixed-modulation) | <a id="f11--high-ofdma-parsing-and-notch-interpretation-are-overstated"></a> [F11 — HIGH: OFDMA parsing and notch interpretation are overstated](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f11--high-ofdma-parsing-and-notch-interpretation-are-overstated) | <a id="f13--medium-higher-layer-ideas-are-portable-the-actuator-is-not-automatic"></a> [F13 — MEDIUM: higher-layer ideas are portable; the actuator is not automatic](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f13--medium-higher-layer-ideas-are-portable-the-actuator-is-not-automatic) | <a id="audit-of-reddit-readme-and-propagated-public-claims"></a> [Audit of Reddit, README and propagated public claims](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#audit-of-reddit-readme-and-propagated-public-claims) | <a id="f12--high-the-current-public-post-is-not-ready-to-publish"></a> [F12 — HIGH: the current public post is not ready to publish](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#f12--high-the-current-public-post-is-not-ready-to-publish) | <a id="f14--low-reproducibility-and-documentation-hygiene"></a> [F14 — LOW: reproducibility and documentation hygiene](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#f14--low-reproducibility-and-documentation-hygiene) | <a id="concrete-corrections-and-bench-verification-checklist"></a> [Concrete corrections and bench verification checklist](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#concrete-corrections-and-bench-verification-checklist) | <a id="immediate-documentarysource-corrections"></a> [Immediate documentary/source corrections](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#immediate-documentarysource-corrections) | <a id="stage-10-isolated-bench-acceptance-after-separate-authorization"></a> [Stage 10 isolated bench acceptance, after separate authorization](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#stage-10-isolated-bench-acceptance-after-separate-authorization) | <a id="xc-airprism-acceptance-after-separate-authorization"></a> [XC AirPrism acceptance, after separate authorization](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#xc-airprism-acceptance-after-separate-authorization) | <a id="ltu-acceptance-only-if-separately-approved-as-a-lab-experiment"></a> [LTU acceptance, only if separately approved as a lab experiment](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#ltu-acceptance-only-if-separately-approved-as-a-lab-experiment) | <a id="final-disposition"></a> [Final disposition](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#final-disposition)

<!-- stage822a-payload-begin -->

Two critical defects prevent approval of the published operational recipes.
Static evidence confirms useful code paths but does not qualify XC interop or LTU RF operation.
Source documents remain unchanged; findings include reproducible evidence and closure criteria.
No radio access, target execution, flashing, network probing or RF testing was performed.


# Adversarial review — Stage 10, Stage 11A, Stage 11B and public claims

Date: 2026-10-18. Parent: `FMX-0015` / Stage 10 and the Stage 11 offline firmware investigation. Scope: `ADVERSARIAL_REVIEW_BRIEF.md`, the three named engineering reports, their unpacked firmware, `REDDIT_POST.md`, and corresponding claims in README, CURRENT_STATE, RESEARCH_LEDGER and DECISIONS. Initial repository HEAD: `e94703a`; the existing dirty checkout was preserved. The audit used the working files, whose hashes are recorded in the evidence manifest.

## Executive verdict and severity table

**DO NOT PUBLISH OR DEPLOY THE CURRENT RECIPES AS QUALIFIED.** The review found two critical defects: an ELF relocation survives the proposed MIPS NOP patch, and the LTU NAND partition map contradicts the held device trees. The XC board decoder and HSR attribution contain substantial errors. The LTU binaries contain meaningful 4096-QAM and OFDMA implementation paths, but the claim that the WebUI is their only gate is not established. Several public statements describe static findings as working hardware capabilities.

This is a completed offline audit, **not** an acceptance of the implementation, a rejection of every reported bench measurement, or authorization for a live test. No SSH, ping, radio contact, target execution, flash, production mutation or external publication occurred during this audit.

Labels used throughout:

- **CONFIRMED**: directly reproduced from the held bytes, symbols, relocations, scripts or document text. This label is explicitly static unless stated otherwise.
- **INFERRED**: engineering consequence supported by those observations, without a matching physical measurement.
- **UNKNOWN**: necessary evidence is missing or the relevant execution path was not exhaustively resolved.
- **REFUTED**: the specific claim conflicts with direct evidence. It does not imply that every related feature is absent.

| ID | Severity | Finding / affected decision | Evidence status |
| :--- | :--- | :--- | :--- |
| F01 | **CRITICAL** | The alleged NOP retains `R_MIPS_26`; the module loader rewrites it. The published patch is not a relocation-safe NOP. | CONFIRMED defect; actual runtime consequence UNKNOWN |
| F02 | **HIGH** | Cron switches modes using file existence and association text, without image identity, transaction checks or bounded recovery. | CONFIRMED omissions; outage scenarios INFERRED |
| F03 | **HIGH** | Complete transparent bridging and generic-AP compatibility lack the actual AP patch and frame-level evidence; 14/18-byte and WDS claims conflict. | CONFIRMED contradiction; full interop UNKNOWN |
| F04 | **HIGH** | XC board layout/sysids/radio counts are materially wrong; the supplied decoder output is not a trustworthy hardware matrix. | REFUTED entries/layout |
| F05 | **HIGH** | AirPrism selector checks channel edges, not just center frequency; published port algorithm can choose a different filter. | REFUTED algorithm; RF damage to performance INFERRED |
| F06 | **HIGH** | Claimed HSR attach/GPIO instructions are not at the cited addresses; SPI use does not identify a filter bus. | REFUTED attribution; actual HSR transport UNKNOWN |
| F07 | **MEDIUM** | Spectral-filter GPIO/IRQ exists; universal 5 GHz scanner identity, precise blanking behavior and timing are unproven. | CONFIRMED path; hardware timing UNKNOWN |
| F08 | **CRITICAL** | LTU NAND map would identify part of U-Boot as EEPROM/configuration; container sizes and HPS partition numbering also disagree. | REFUTED map; destructive use would be hazardous |
| F09 | **HIGH** | `4096-QAM is gated ONLY in UI` and a working PtMP unlock exceed the evidence; kernel hardware guards and mode-dependent paths exist. | CONFIRMED code paths/guards; working RF unlock UNKNOWN |
| F10 | **HIGH** | LTU rate-code table and quoted WebUI entries are wrong. Ceiling, fixed-rate request and actual transmitted modulation are conflated. | REFUTED mapping/quotation |
| F11 | **HIGH** | `ofdma_subbands` parses a number, not a binary string; RX register mask is presented as proven interference-notching operation. | REFUTED input semantics; RF behavior UNKNOWN |
| F12 | **HIGH** | Reddit/README/ledger promote unqualified operation, safety, compatibility and static discoveries to proven wins. | CONFIRMED publication blockers |
| F13 | **MEDIUM** | Portability and hidden CLI contracts overstate QCA control and misdescribe `mix_mcs`/`cpe_mcs`. | REFUTED CLI details; implementation portability conditional |
| F14 | **LOW** | Broken local links, stale artifact paths, incorrect sizes/offset types and missing raw experiment pointers obstruct reproduction. | CONFIRMED |
| S01 | **CONFIRMED SOLID** | Exact held XC patch-site instructions, matching WA 8.7.25 neighborhoods, and the three replacements' file-byte changes are reproducible. | Static; does not resolve F01 |
| S02 | **CONFIRMED SOLID** | `prism` GPIO selector, `hsr` capability parameter, dual-radio records, and a spectral-filter IRQ path exist. | Static; no complete HSR pin map |
| S03 | **CONFIRMED SOLID** | LTU AMEIMG parts, `amesoc3`/AD9361 description, Rocket Arria 10 companion images, 4096-related tables/functions, and OFDMA hooks exist. | Static; FPGA/RF qualification missing |

Counts: **2 CRITICAL, 9 HIGH, 2 MEDIUM, 1 LOW**, plus the three scoped positive findings above.

## Evidence, method and reproducibility

Evidence directory: [`artifacts/adversarial_review_stage10_11/`](../artifacts/adversarial_review_stage10_11/).

| Artifact | Purpose |
| :--- | :--- |
| [`manifest.json`](../artifacts/adversarial_review_stage10_11/manifest.json) | Actual input paths, lengths, SHA-256 and MD5; audited-document hashes |
| [`elf_probe.py`](../artifacts/adversarial_review_stage10_11/elf_probe.py) | Read-only ELF disassembly with relocation symbol/section annotations; executable addresses handled separately from relocatable section offsets |
| [`collect_evidence.py`](../artifacts/adversarial_review_stage10_11/collect_evidence.py) | Reproduce the principal static checks from held files |
| [`patch_sites.json`](../artifacts/adversarial_review_stage10_11/patch_sites.json) | Original instructions, relocation annotations, WA/XC context comparison and proposed-splice hashes |
| [`selected_disassembly.json`](../artifacts/adversarial_review_stage10_11/selected_disassembly.json) | Module-loader behavior, prism selector, real/claimed HSR sites, LTU guards/setters/parse paths |
| [`xc_boards.json`](../artifacts/adversarial_review_stage10_11/xc_boards.json) | Corrected board record stride, sysids, radio counts, capability words and HSR parameters |
| [`prism_table.json`](../artifacts/adversarial_review_stage10_11/prism_table.json) | Six original 44-byte entries as big-endian words, preserving their order |
| [`containers.json`](../artifacts/adversarial_review_stage10_11/containers.json) | Container part boundaries, names, sizes, payload hashes and LTU embedded-MD5 checks |
| [`dtb_properties.json`](../artifacts/adversarial_review_stage10_11/dtb_properties.json) | DTB architecture, peripheral and partition properties from the actual containers |
| [`validation.json`](../artifacts/adversarial_review_stage10_11/validation.json) | Passing offline provenance/consistency checks and final report hash; no hardware acceptance |

Reproduction from repository root, with the existing Python `capstone` and `pyelftools` dependencies:

```powershell
python artifacts/adversarial_review_stage10_11/collect_evidence.py
python artifacts/adversarial_review_stage10_11/validate_evidence.py
python artifacts/adversarial_review_stage10_11/elf_probe.py artifacts/firmware_re_xc_ltu/xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko --start 0x7800 --size 0x40
```

The WA comparison uses a read-only extraction of `lib/modules/2.6.32.68/ubnt_poll_host.ko` from held `firmware/WA.8.7.25.squashfs`, saved in the audit directory. `collect_evidence.py` records that file when present. The XC kernel is decompressed from the held XC container; it is never booted. Proposed patch hashes are calculated on a bytearray, not installed anywhere.

No target binary was executed. Native parsing/disassembly was used because no fresh FuturaMAX GitNexus index was available; the optional scoped MemoryMaster lookup did not return usable evidence. Neither was used as proof. Existing extracted summaries were treated as hypotheses and checked against their source bytes. The review did not decompile the FPGA fabric, prove the whole reachable call graph, validate vendor signatures, or reproduce RF/soak results. A matching embedded payload MD5 is an integrity observation, not authentication.

## Detailed findings — Stage 10: WA stock airOS 8 interoperability

### F01 — CRITICAL: a retained ELF relocation invalidates the NOP claim

**CONFIRMED:** the held WA and XC 8.7.25 modules are MIPS big-endian relocatable ELF files. Their `.text` begins at file offset `64`. The XC 8.7.25 module is `189880` bytes, MD5 `5b26b076967befe129f669096539ae21`; WA is the same size, MD5 `7c76c8ced16cab0ce9ca680ce9c94e51`. The old XC 8.7.4-cs module is `186560` bytes, MD5 `4103f9d0a2fdbf312d93a68b10647bca`.

| Site | 8.7.25 file / `.text` offset | XC 8.7.4-cs file / `.text` offset | Original -> proposed word | Static semantics |
| :--- | :--- | :--- | :--- | :--- |
| Beacon-miss call | `30784` / `0x7800` | `30072` / `0x7538` | `0c000000` -> `00000000` | `jal` relocated to `ubnt_poll_host_sta_bmiss_ind`; proposed zero still has relocation |
| Timer branch | `31816` / `0x7c08` | `31104` / `0x7940` | `14400006` -> `10000006` | Conditional `bnez v0` becomes unconditional branch over a panic path; delay slot is NOP |
| AP validity return | `41976` / `0xa3b8` | `40916` / `0x9f94` | `0002102b` -> `24020001` | Boolean conversion becomes `v0 = 1`; normal return/stack cleanup follows |

The first site retains **`R_MIPS_26`**, referencing `ubnt_poll_host_sta_bmiss_ind` at `.text+0x167c` in 8.7.25. The `dd` splice copies the relocation section unchanged. Zeroing the instruction's four file bytes does not remove this relocation.

The exact XC kernel loader confirms the consequence. At raw offsets `0xa99c..0xa9b8` / virtual addresses `0x8000c99c..0x8000c9b8`, it reads the word, keeps its top six opcode bits, inserts the relocated target's low 26 bits, and writes it back. The REL wrapper at `0x8000c9cc` supplies the original low-26-bit addend. The normal same-region case is equivalent to:

```text
loaded_word = (file_word & 0xfc000000)
            | (((symbol_address >> 2) + encoded_addend) & 0x03ffffff)
```

For a zeroed word, the opcode stays zero but the target bits are populated. **REFUTED:** the resulting instruction is guaranteed to remain `nop`. Its actual decoded instruction depends on the loaded symbol address; it may trap or alter machine state when that path runs. **UNKNOWN:** the exact in-memory word and whether the reported bench exercised it. A successful `insmod` or short throughput test does not settle a latent beacon-miss path. The loader evidence here is the exact XC build; WA has the same relevant relocation hazard, but its loader/in-memory outcome needs separate verification rather than assumed equivalence.

The 96-byte neighborhoods around all three held WA/XC 8.7.25 sites are byte-identical. Their complete `.text` sections differ in five bytes elsewhere. Thus **CONFIRMED** local instruction parity, **UNKNOWN** exact source-tree identity and whole-system semantic equivalence. The older held XC image also has the three expected instruction shapes; unavailable WA revisions are not individually certified.

The published WA splice's resulting MD5 reproduces as `3f2e756225bf67947abcc5dd46bccd9d`. Hypothetical XC results are `c36e694868da56bfec0c0fa3182ac748` for 8.7.25 and `306fa8f5d0e67a5464af2cac929d1684` for 8.7.4-cs. These hashes reproduce the **defective proposal**, not an approved module.

**Corrections to the brief:** WA offsets `30748` and `31780` are not the displayed 8.7.25 patch sites; they contain subtraction instructions. `0x10000018` is not the correct replacement at `41976`: it would branch out of the tiny return function instead of returning `1`, skipping its normal epilogue. The Stage 10/11A table's `24020001` is correct for that third site's intended operation. Also, three four-byte replacements change only **six differing bytes** here; the engineering report's “6-byte / 3-instruction” description is defensible. Reddit's “3-byte patch” is not.

**Required correction:** withdraw the “NOP”/safe-universal-patch assertion until a relocation-aware design is independently checked, with preimage hash, relocation invariants, bounded disassembly and eventually loaded-memory verification on an authorized isolated bench. This audit does not implement a replacement or authorize installing one.

### Remaining watchdog, reconnect and DFS paths

**CONFIRMED:** the second patch bypasses a path with a relocation to `panic`, not a directly identified `80211_Stop` call. The nearby computation uses a jiffies-derived quantity multiplied by `1000` and compares against `30001000`; time units must be interpreted with the exact kernel timer context/HZ. That branch alone is not proof that every timeout is disabled.

The held `umac.ko` retains distinct `mlme_sta_swbmiss_timer_start`, `mlme_sta_swbmiss_timer_restart`, `mlme_sta_swbmiss_timer_enable`, `mlme_sta_bmiss_ind`, `ieee80211_mlme_recv_csa` and `ieee80211_process_csa_ecsa_ie` paths. **UNKNOWN:** whether every re-association, WPA rekey, driver restart or DFS/CSA transition preserves hybrid configuration. The patch does not remove these functions, and finding them does not prove that they necessarily re-enable polling. Re-running the vendor configuration generator can replace the edited volatile radio/wireless/supplicant files. This is a specific reapplication hazard to test, not an observed live failure.

`allow_80211=1` is a supplicant configuration input, not an instruction added to `ubnt_poll_host.ko`. Existing reported WPA2 association supports one observed setup; it does not establish that this key overrides every later scan/rekey/configuration path.

### F02 — HIGH: persistence is not a transactional fail-safe

Evidence: Stage 10 sections 3B and 5, especially the actual cron command. Its behavior is visible without executing it:

| Trigger/failure | What the published command does | Implication |
| :--- | :--- | :--- |
| New/unknown firmware | Chooses by file size; every size other than the two old cases falls into the 8.7.25 offsets | INFERRED corruption risk even for a valid but different ELF; size is not identity |
| Partial `dd`/awk output, full `/tmp`, interrupted creation | Writes directly to the final `/tmp/uph.ko` path | CONFIRMED no atomic publication or complete-output/preimage hash validation |
| Failed bind mount, module stop/start or module load | Continues through semicolon-separated commands; error output is partly suppressed | CONFIRMED no checked rollback transaction; file existence can disagree with loaded state |
| `/tmp/uph.ko` exists but wrong module remains loaded | Marker is treated as the mode indicator | CONFIRMED marker is not module identity, association health or datapath health |
| Slow AP reboot, lawful CAC, temporary RF fade, failed authentication | Each minute with `Not-Associated`, toggles patched/unpatched state according to marker existence | INFERRED oscillation and interrupted recovery; no AP identity or stability window |
| Associated but unusable customer traffic | `iwconfig` lacks `Not-Associated` | CONFIRMED no end-to-end datapath watchdog |
| Long-running/overlapping invocation | No lock or single-flight state | INFERRED concurrent lifecycle/mount race |

The doc's two recipes differ: one installs once then forces a lab channel/SSID on non-association; the later one toggles modes. They must not share a blanket “universal production safety” label. The latter's one-minute observation is not a measured three-minute dead-man guarantee. Restoring scripts with `ubntconf` is not proof of exact loaded-module, RF, bridge and service-state restoration.

**REFUTED for this displayed recipe:** the brief's asserted repeated `sleep 180 -> cfgmtd` flash-wear loop is not in the command under audit. The final cron loop contains no repeated `cfgmtd`; the installation step separately persists configuration. `/tmp/up_p.ko` is also not its marker; it uses `/tmp/uph.ko`. Do not manufacture a measured flash-wear defect from a stale version. The real installation still writes configuration flash, so “without touching flash” is misleading when applied to the entire installation.

**Required correction:** exact firmware/module allowlist, fail closed on unknown identities, verified atomic artifact creation, single-flight ownership, explicit mode/loaded-state readback, checked lifecycle steps, bounded recovery and a health definition beyond association. Keep a hardware recovery route. A file existence check is not that route.

### F03 — HIGH: the bridging claim lacks the decisive implementation and packets

**CONFIRMED contradiction:** the brief/Reddit describe `skb_pull(...,18)` and WDS enabled; Stage 10 describes removal of **14** bytes after an `ETH_P_TEB` check and explicitly configures stock `radio.1.wds.status=disabled` / `iwpriv ath0 wds 0`. Its AP is additionally patched. These are materially different framing/configuration claims.

The referenced AP `mac80211.ko` with MD5 `6c869e80d4748753727192be08b7bbe6`, the 21-instruction diff/source implementation and matching raw frame captures were not located in the scoped audit inputs. **UNKNOWN:** the actual edits, safe buffer access, correct metadata updates and complete receive-path coverage. A prose pseudocode is not executable evidence of changes across `fast_rx`, normal data and A-MSDU paths.

An outer Ethernet header is 14 bytes; 802.11 Address4 is a separate 6-byte MAC-address field. An additional VLAN tag would make a particular Ethernet framing 18 bytes, but it is not a universal WDS rule. `0x6558` identifies a transparent-Ethernet payload type; its presence alone does not establish a GRE header or the claimed RFC-1701 wire format. Inspect the exact frame before choosing a removal count.

**INFERRED conditional behavior:** if the actual packet is an outer Ethernet header followed by a complete inner Ethernet frame, removing exactly that outer header can preserve inner ARP, IPv6 and VLAN tags. It does not prove that the stock station forwards multiple customer MACs in both directions or uses the claimed 3/4-address path. `skb->len >= 28` alone also does not prove the necessary bytes are linear/writable, that cloned SKBs are handled, or that MAC/network/checksum/VLAN metadata remains consistent. No definite memory-safety exploit is claimed without the patch.

**UNKNOWN acceptance:** both-direction unicast with multiple customer MACs; ARP request/reply; DHCP discover/offer/renew; IPv6 ND/RA and multicast; IGMP/MLD behavior; 802.1Q and QinQ; minimum/maximum frames and MTU; fragmented/A-MSDU receive handling; checksum/GRO/fast-path behavior; and ordinary unencapsulated clients remaining unaffected. Endpoint-local `iperf` and ping do not certify a transparent customer Ethernet bridge.

The AP-side custom decoder is also a direct reason that “any standard AP / MikroTik / Cambium / Mimosa” cannot be concluded from this single OpenWrt arrangement. State exact tested AP software and frame handling, then qualify other vendors separately.

## Detailed findings — Stage 11A: XC Rocket Prism and AirPrism

### F04 — HIGH: the published board layout and hardware matrix are not faithful to the ELF

**CONFIRMED from `ubnthal.ko`:** the table resides at `.data+0x570`, with **12000-byte** records, not `.rodata` records of 4016 bytes. Board sysid is at `+0x2d1c`; radio count is the byte at `+0xcc`, not a word at `+0x768`. Per-radio stride is **3780** bytes. Capability words are at board `+0xf6c + radio_index*3780`; the first HSR parameter is at `+0xf8c`. The cap-name table is at `.data+0x94`. `ubnthal_get_radios_count` and `ubnthal_get_radio_bus` provide independent instruction evidence for the offsets/stride.

The supplied `xc_boards_radios_complete.json` does not reliably decode that radio layout. Some apparent “chip type” data includes the actual radio-count field. There are 34 records, including repeated sysids/BOM variants, not 34 distinct model names reconstructed by invention.
<!-- stage822a-payload-end -->
