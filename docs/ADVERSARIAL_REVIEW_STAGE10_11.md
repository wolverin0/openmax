<!-- doc-head: Independent offline adversarial audit of Stage 10, XC AirPrism and LTU claims -->
Two critical defects prevent approval of the published operational recipes.
Static evidence confirms useful code paths but does not qualify XC interop or LTU RF operation.
Source documents remain unchanged; findings include reproducible evidence and closure criteria.
No radio access, target execution, flashing, network probing or RF testing was performed.
<!-- /doc-head -->

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

Selected corrected rows from [`xc_boards.json`](../artifacts/adversarial_review_stage10_11/xc_boards.json):

| Held board identity | Sysid | Radios | wifi0 caps | HSR parameter | Scope of confirmation |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `PBE-5AC-500-ISO` (two records) | `0xe3d5` | 2 | `0xace00814` | 0 | Neither prism bit 30 nor HSR bit 28; “single radio” is false for these records |
| `R5AC-PTP` | `0xe3f5` | 2 | `0xbce00814` | 171 | HSR bit set; prism bit clear |
| `R5AC-PTMP` (two variants) | `0xe3f5` | 2 | `0xbee00814` | 31 / 43 | Same sysid is insufficient to choose the variant |
| `PS-5AC` | `0xe7e6`, `0xe7e8` | 2 | `0xfce00814` | 31 | Both prism and HSR capabilities |
| `RP-5AC-Gen2` | `0xe7e7`, `0xe7e9` | 2 | `0xfce00814` | 31 | Both prism and HSR capabilities |

**REFUTED:** the brief's `0xe7f9 = Rocket Prism Gen2`; the report's `0xe7f8/e7f9/e7fa` mapping of these old Rocket records; and its blanket ISO single-radio table. `0xe7f9` is absent from this XC board table. The corrected evidence does support an ISO example without active prism/HSR capability, but not every model/revision and not the published list of attributes.

The second-radio capability values are `0x0c` on the selected Gen2 boards and `0x14` on the old Rocket/ISO records. The actual cap-name mapping describes 11n and chain-count capabilities; those words do not prove a universal dedicated 5 GHz scanner. Do not transplant a WA or similarly named product's sysid into an XC flash decision.

### F05 — HIGH: the prism algorithm tests the full channel interval

**CONFIRMED:** `umac.ko:ubnt_prism_hook` at `.text+0xac874` calls helper `.text+0xabeb0` using lower and upper channel edges derived from center and half-width. The helper requires:

```text
entry.stage == requested_stage
lower_channel_edge >= entry.start
upper_channel_edge <= entry.end
channel_width <= entry.maximum_width
```

**REFUTED:** the published center-only condition. Example: center `5240 MHz`, width `80 MHz` spans `5200..5280`. It does not fit the stage-1 `5150..5250` range, although its center does. The held code therefore reaches the wide entry where the published center-only algorithm would select the narrow bank.

The table is **six entries of 44 bytes**, not Reddit's “44-entry table.” Its original order is stage-1 low, stage-1 high, stage-2 low, stage-2 high, stage-1 fallback, stage-2 fallback. GPIOs 15/16 belong to stage 1 and 13/14 to stage 2. The code references `gpio_line_config` / `gpio_line_set`; do not substitute invented `ubnthal_gpio_Export` calls as a literal disassembly quotation.

**INFERRED risk:** a wrong/uninitialized RF filter state can attenuate the wanted signal, distort a wide channel, reduce selectivity or worsen blockers and EVM. **UNKNOWN:** power-on state, complete board routing, safe switching order, calibrated gain, rejection, insertion loss and the actual effect on an OpenWrt port. The report's quantitative `20–35 dB` penalty is not supported by a physical measurement here. A two-stage GPIO selector does not by itself prove the separate HSR chip, bus or programming protocol.

### F06 — HIGH: the purported HSR SPI/GPIO sequence is misattributed

Stage 11A attributes an `ubnthal_get_radio_cap(...,"hsr")` call and pin selection to `.text+0x8cb4c` / `0x8cbac..0x8cc2c`. **REFUTED by direct disassembly:** at `0x8cb4c` the instruction is `addiu a0,s1,0xd7c`; the following call is to local `.text+0x654d0`. The cited neighborhood contains data/checksum processing, not the stated capability call and GPIO exports.

The nearby `.data+0xd7c` string decodes to `board.sysid` with the repeating key bytes `81 93 e0 c4`, not the claimed single-byte XOR key `d6`. Security/board-validation strings and shared flash-SPI access cannot be relabeled a frequency-tuning protocol merely because the same controller is touched. The audit did not bypass or modify those checks.

A real call querying the `hsr` capability occurs around `.text+0xbbf64`, using the literal at `.rodata+0x15890`, and stores the result at a large driver-state offset (`+0x1e8c0`). The corrected HAL table independently confirms the capability values. **CONFIRMED:** HSR-related state is present. **UNKNOWN:** exact external chip identity, whether the relevant transport is the claimed SPI path or another host/firmware path, the meaning of all parameter bits, complete tuning transactions, and pins 11/12/17 or 11/12/13/15.

Consequently the brief's apparent GPIO 13–15 conflict is **UNKNOWN**, not a demonstrated electrical collision. It rests on an unverified HSR pin map. Do not resolve it by assuming pins are multiplexed, or port the purported sequence into a driver. Required evidence is a traced capability-consumer/tuning call chain and board-specific bus/pin confirmation. Existing SPI locking and error strings are insufficient.

### F07 — MEDIUM: spectral filtering and hybrid mode need narrower claims

**CONFIRMED:** `ath_dev.ko:ath_spectral_filter_init` at `.text+0x27c00` configures GPIO 21, requests IRQ 64 with a handler at `.text+0x27be0`, and uses the `ath-spectral-filter` identifier. This is meaningful evidence of a hardware-assisted spectral-filter interrupt path.

**UNKNOWN:** wire polarity, interrupt routing on each board, measured timing, whether it blanks every relevant FFT window, and whether the protected path is specifically the second radio's LNA rather than sample eligibility/control. The public “scanner never deafened” explanation and microsecond timing need actual hardware evidence.

Likewise, retaining the stock `umac` module plausibly preserves vendor tuning. It does not certify XC AP or STA hybrid operation, hostapd behavior, all channel changes, DFS, rekey or filter restoration. Shared patch offsets and a `polling=disabled` parser are insufficient for “works without changing a single byte” and “100% compatibility.” Stage 11 remains static until exact-board acceptance.

## Detailed findings — Stage 11B: LTU 4096-QAM, OFDMA and architecture

### F08 — CRITICAL: the published flash map contradicts the actual DTB

The actual trees are `ltu_extracted/aflturocket_2.4.2/rootfs_extracted` and `ltu_extracted/afltu_2.4.2/rootfs_extracted`, with modules under **`3.14.65`**. The brief's `_242_rootfs_squashfs` / `3.10.20-ubnt-mtk` paths do not identify these inputs.

**CONFIRMED:** held containers are `38918528` bytes (Rocket) and `24366210` bytes (CPE). They contain 10 and 5 AMEIMG parts. All 15 parsed payload MD5 values match the embedded values, and the parser consumes each entire file with **zero trailing bytes**. The documented `11,148/11,580`-byte outer signature footer is **REFUTED for these files**; this does not prove absence of every other integrity/authentication mechanism.

The primary part names are `spl`, `uboot`, `dtb`, `kernel`, `rootfs`, and their sizes differ from the report:

| Part | Rocket bytes | CPE bytes |
| :--- | ---: | ---: |
| spl | 524288 | 524288 |
| uboot | 318096 | 319344 |
| dtb | 6605 | 6554 |
| kernel | 3330408 | 3330408 |
| rootfs | 19398656 | 20185088 |

Both primary DTBs give the following NAND map; this table records **static DTB evidence only**, not an authorized flash recipe:

| Label | Start | Length |
| :--- | :--- | :--- |
| spl | `0x00000000` | `0x00080000` |
| uboot_env0 | `0x00080000` | `0x00060000` |
| uboot_env1 | `0x000e0000` | `0x00060000` |
| uboot | `0x00140000` | `0x00100000` |
| EEPROM | `0x00240000` | `0x000c0000` |
| cfg | `0x00300000` | `0x000c0000` |
| dtb0 | `0x003c0000` | `0x00060000` |
| kernel0 | `0x00420000` | `0x00500000` |
| rootfs0 | `0x00920000` | `0x02800000` |
| dtb1 | `0x03120000` | `0x00060000` |
| kernel1 | `0x03180000` | `0x00500000` |
| rootfs1 | `0x03680000` | `0x02800000` |
| reserved | `0x05e80000` | `0x02180000` |

**REFUTED:** Stage 11B's EEPROM at `0x00160000` and configuration at `0x00180000`. Both fall inside the actual DTB U-Boot range. Using that documentation for a write or restore could destroy boot code while believing the target was configuration/calibration. No such operation was performed here.

Other architecture corrections: Rocket's primary model is `AME SoC 3 LTU-Rocket Board`; the CPE model is `AME SoC 3 LTU Board`. The DTB's AD9361 SPI maximum is `0x02625a00` = **40 MHz**, not 20 MHz. The main GIC region is at `0xffffd000`, not the stated `0xf8f01000`.

**CONFIRMED SOLID:** dual Cortex-A9 / 256 MB primary descriptions, the `ame_ad9361` compatible node, and Rocket-only companion parts 5–9. The companion DTB identifies `altr,socfpga-arria10`, two CPUs and 128 MB RAM. The held `.rbf`/HPS boot/kernel/rootfs payload sizes in the report are mostly reproducible, including `5490084` bytes for part 5.

The HPS MTD numbering in the prose is also wrong: its DTB has intervening environment partitions before `core-rbf` and rootfs, plus redundant/factory partitions. Use the full recorded DTB rather than the claimed simple `mtd0..mtd5` sequence. **UNKNOWN:** exactly which baseband/aggregation/DSP work the opaque FPGA fabric performs, and whether it implements the claimed “channel stitching” explanation for 100 MHz. A companion FPGA's presence does not prove that explanation.

### F09 — HIGH: meaningful 4096-QAM software exists; a qualified PtMP unlock is unproven

The Rocket `ame_core.ko` under review is `3318764` bytes, MD5 `92d1e1e3babacf57f291e7af774892c3`. CPE `ame_core.ko` differs (MD5 `12ba72a3fb0875439e05be32dcc1d630`); AP offsets must not be applied mechanically to it.

The following are **CONFIRMED static observations**:

1. Rocket `ubntbox` has the MCS bound check around VA `0x40284`; its table at **VA** `0xd4b28` (file offset `0xccb28`) is `[7,11,15,19,23,31]`. Configuration value 5 can translate to internal ceiling 31 in the inspected path. No `ptpmode` check was found in that local validation/serialization block.
2. `AME_Scheduler_AutoMCS_GetPtmpDLCeiling` at `.text+0x735ac` accepts 31 in its validation and has a fallback to global `system_config+0x174`. This is positive evidence against an unconditional 1024-QAM clamp in **that function**.
3. `ame_bbp_set_autoMcsCeiling` at `0x196af0` stores the requested ceiling and invokes power/backoff machinery. Setting a ceiling is not forcing each transmission to that rate; the setter also selects the automatic-MCS path.
4. `autoMcsUseSisoTbl` and `autoMcsOthersTbl` contain `(31,1)`. `autoMCS_get_rate_table` at `0x156098` branches on SISO, operating configuration, training state and board identifiers (`0xae05`/`0xae0e`). The inspected non-SISO paths select seven-entry tables containing 31; the SISO branch selects five entries. This supports a real MIMO table entry, not a universal operational guarantee.
5. `bbp_rf_set_super4096` at `0x1766bc` reads/changes RF state and reaches `ame_rfic_req(0x56,...)`. Its symbol name and register actions support a specialized path, not a measured low-EVM profile or confirmed calibration quality.
6. `startThrd_4096 = 97` and `stayThrd_4096 = 90` are present. Their exact units and conversion to the report's `38–42 dB CINR` are **UNKNOWN**.

The kernel has additional guards. `ame_bbp_set_Param_mcs` at `0x194648` calls `ame_check_hw_NoLDPC` on a path covering code 31, and rejects unsupported cases; it also has a `NoRS` path for the RS code range. Backoff behavior is conditional on configuration/mode fields, including checks at `system_config+0x20` and `+0x10`. The actual values on each board, peer capability negotiation, width-dependent limits, training behavior and FPGA support were not established by this audit.

Therefore **REFUTED as a complete description:** “only WebUI/Lua validation exists.” **UNKNOWN:** whether those other guards block 4096 on a particular supported PtMP pair. No universal PtMP clamp to 29 was identified in the examined paths, and the report must not invent one. Code **29 is RS 1024-QAM**; LDPC 1024-QAM is **23**. The brief's bare “1024 = 29” is incomplete.

**UNKNOWN:** why Ubiquiti disabled the UI option, whether historical releases had the same behavior, AD9361 EVM/phase-noise margin in this board, PA headroom, LDPC throughput limits at a given width, and sustained net benefit. Marketing motive cannot be inferred from strings. A complete answer requires tracing peer capability consumers/FPGA status and then an authorized isolated RF test, not bypassing hardware or regulatory checks.

The honest replacement claim is: **“Firmware v2.4.2 contains 4096-QAM-related rate tables, configuration paths and RF-driver routines; a configuration ceiling of 31 is accepted in inspected paths. Usable PtMP 4096-QAM and its limits remain unverified.”**

### F10 — HIGH: rate mapping is wrong, and ceiling is not fixed modulation

The actual `ame_adj.sh` mapping and the `ubntconf` table agree on the following six LDPC codes. The script labels these named modulation entries as 5/6; that label alone is not a measured PHY coding implementation.

| Config MCS | Actual modulation / nominal UI label | LDPC code | RS code from script |
| :---: | :--- | :---: | :---: |
| 0 | QPSK; `1X` SFBC or `2X` depending on NSS selection | `0x07` | `0x19` |
| 1 | 16-QAM / `4X` | `0x0b` | `0x1a` |
| 2 | 64-QAM / `6X` | `0x0f` | `0x1b` |
| 3 | 256-QAM / `8X` | `0x13` | `0x1c` |
| 4 | 1024-QAM / `10X` | `0x17` | `0x1d` |
| 5 | 4096-QAM / `12X` | `0x1f` | `0x1e` |

**REFUTED:** Stage 11B's extra QPSK row at config 1, shifted 16/64/256-QAM labels, duplicate config 4 mapping, and mixed coding-rate assignments. The WebUI snippet shown as extracted code similarly shifts labels/values. The actual `getAvailableDataRates` offers `0@0` for QPSK+SFBC and `0@1` for 2X QPSK, then `1@1` through `5@1`. The 12X entry's `disabled:t` is real; the surrounding quoted table must be corrected.

`ame_adj.sh mcs 4096l` writes the fixed/adjusted-MCS interface (`adj_mcs`), not merely `autoMcsCeiling`. Per-CPE and global operations also differ. These are not interchangeable ways of measuring a working “unlock.” Net spectral efficiency additionally depends on coding, pilots, framing, guard intervals, retransmissions and scheduler airtime; `12X` is not a measured 12 bit/s/Hz payload guarantee.

### F11 — HIGH: OFDMA parsing and notch interpretation are overstated

**CONFIRMED:** `ame_dev.ko:ofdma_subbands_store` at `.text+0x1154c` calls `simple_strtol` with base 0 and truncates to an unsigned byte (`uxtb` at `0x11568`) before invoking its hook. Thus the literal string **`11111111` is decimal 11,111,111 and becomes `0xc7`**, not `0xff`. It is not an eight-character binary-string parser. Leading-zero and prefixed-number behavior must be treated as numeric parsing, not a visual bit map.

`ame_core:ame_bbp_set_ofdma_subbands` at `0x1979c4` complements the byte into `system_config+0x10a`, then reaches `bbp_mrx_band_ofdma_subbands` at `0x145704`, which writes an eight-bit field at bits 12–19 in a BBP register in the `+0x48000` region. **CONFIRMED:** a real RX-side mask/configuration path exists. **UNKNOWN:** how its bit polarity, frequency ordering and receiver configuration map to usable over-the-air allocations or transmitted spectral notches.

Additional meaningful code is present: `ame_bbp_set_ofdma_en`, subband-type setters and `sched_ofdma_available` at `0x63f74`. The availability function checks enable state at `system_config+0x154` and resource/size conditions. `ame_check_hw_NoOFDMA` at `0x5708` reads a hardware-capability bit; it is consumed in capability-message construction. This is not evidence of a purely empty stub, but it is also not proof that every board/FPGA/peer combination supports 2/4/8-subband service.

The report's `ubntconf` address range around `0x42304..0x42390` includes literal data, not the asserted executable proof of every mode translation. Configuration strings exist; the full mode-to-scheduler/FPGA path remains incomplete. **UNKNOWN:** all supported `ofdma_mode` semantics, operational subcarrier allocation, uplink/downlink asymmetry, compatibility negotiation, allowed widths and net gain. Remove “already notches out interference” until spectrum and traffic measurements establish it.

### F13 — MEDIUM: higher-layer ideas are portable; the actuator is not automatic

**CONFIRMED:** LTU exposes a custom baseband/RF architecture distinct from the held QCA988x 802.11ac stack. Copying LTU setting names cannot add 4096-QAM, LTU framing or its subband scheduler to QCA988x. The broad “not a drop-in PHY upgrade” boundary is sound.

**UNKNOWN:** the report's absolute assertions about QCA shared-LO internals, precise retune timing and all possible nonstandard widths are not established by the LTU binaries. Separate TX/RX-frequency configuration paths support split-frequency operation as a design capability; they do not prove simultaneous full-duplex traffic or the claimed 100-MHz FPGA implementation. Keep those explanations conditional until their exact sources/hardware are verified.

Per-peer quality history, spectral scoring, pacing and desired-rate policies are higher-layer concepts that can inform a new QCA-side implementation. They require independently verified telemetry and control hooks. The report's “directly portable WMI rate ceiling” claim ignores the project's own documented rate-mask authority failure on the tested firmware: host API acceptance/reassociation did not establish enforced over-the-air masks. Preserve that limitation.

Two concrete CLI corrections from the held script:

- `mix_mcs` help gives **`<cpe_id> <q_id> <portion> <sub_mcs> <sub_mimo> [offset]`**, and writes `adj_mix_mcs`; it does not accept four queue percentages as the report suggests.
- `cpe_mcs` writes the **`cpe_mcs`** sysfs interface, not the stated `cpe_fixrate` path.

The presence of scheduler/debug pages and engineering interfaces is useful for offline understanding. It does not authorize enabling them on production or imply they are stable public APIs.

## Audit of Reddit, README and propagated public claims

### F12 — HIGH: the current public post is not ready to publish

| Location / claim | Audit result | Required wording or evidence |
| :--- | :--- | :--- |
| Reddit title and Win 5: “4096-QAM Unlock”, “only hid it”, “100% built” | UNKNOWN RF functionality; hardware guards exist | Say “static investigation found configuration and driver paths”; state no LTU RF qualification |
| Reddit Win 5: OFDMA already notches narrowband interference | UNKNOWN on-air result; input example is wrong | Describe unqualified hooks and RX mask, not a working interference-removal feature |
| Reddit Win 4: “fully mapped”, “proved two ways”, exact HSR GPIO/SPI sequences | REFUTED completeness and cited sequence | Retain confirmed prism selector; mark HSR protocol and OpenWrt port incomplete |
| Reddit Win 4 spoiler: `ath_dev` prism hook, “44-entry” table, 3-byte patch | REFUTED against held symbols/table/bytes | `umac`, six 44-byte entries, three instructions with six changed bytes; F01 still blocks patch approval |
| Reddit Win 1/2: any standard AP, transparent WDS, generic multi-vendor compatibility | UNKNOWN; demonstrated setup reportedly needs custom AP decapsulation | Name exact bench AP/build; publish frame-level matrix before expanding compatibility |
| Reddit Win 1: stock tools work “100% normally” | UNKNOWN full UISP/SNMP/WebUI/management acceptance | Scope to individually observed functions; retained packages are not end-to-end proof |
| Reddit Win 1: automatic three-minute safety net / zero truck roll | UNKNOWN; displayed loop is a one-minute mode toggle | Replace with “experimental recovery mechanism”; qualify fault cases before claiming safe migration |
| Reddit spoiler: applies/reloads in 3 seconds “without touching flash” | UNKNOWN timing; installation explicitly writes config flash | Distinguish temporary module alteration from persistent config installation |
| README line 137: 147 Mbps attributed to WA 8.7.25 | REFUTED by Stage 10's own version attribution | 147 belongs to reported WA 8.5.12; WA 8.7.25 reports 134 plain / 120 CCMP Mbps UL |
| README/ledger: full HSR architecture, radio counts, 4096-only-UI, notch mask | Same underlying defects as F04/F06/F09/F11 | Propagate corrections; a corrected Stage 11 alone leaves contradictory project truth |
| README: no production subscriber traffic is ever touched | Conflicts with Stage 10's live CPE configuration pre-staging/flash record | State exact historical activity; do not erase it or imply this audit performed it |

Stage 10 records four live CPEs receiving persisted cron configuration and a brief stock-mode health observation. That is different from a measured stock -> hybrid -> stock transition, recovery from failure, long soak, or a completed production AP migration. DECISIONS records later restoration, but this offline audit does not establish current live state. No network check was made.

Bench numbers must retain their source and limits. Stage 10 reports WA 8.5.12 at 147 Mbps UL, WA 8.7.25 plain at 134 Mbps UL / 78.8 Mbps receiver DL, and WA 8.7.25 CCMP at 120 Mbps UL / 79.5 Mbps receiver DL. CURRENT_STATE/ledger/Reddit additionally give 20-MHz values of 78.7/63.6 Mbps. **CONFIRMED:** those claims exist in the documents. **UNKNOWN in this audit:** independently reproducible raw logs/configurations/trial durations for those exact results; the inspected canary receipts concern backups/pre-staging rather than the complete traffic matrix. Attach the raw artifacts before treating the prose as independent measurement proof. This finding does not assert that the numbers were fabricated.

Calling a software `reboot` a **cold boot** conflates two different recovery tests. Preserve software-reboot evidence under that name; reserve cold/power-loss qualification for actual power removal and restoration. Ten pings or roughly one cron interval in stock mode cannot prove hours/days of hybrid stability.

Reddit's broader Stage 1–9 claims about continuous FFT, automatic channel changes, all-vendor support, performance and controller deployment were not fully re-audited here. They remain **UNKNOWN to this review**, not silently approved. Statements about product abandonment/vendor intent and “5+ years” also need independent sources or removal; none were fetched in this strictly offline task.

The linked Stage 10 page includes identifiable operational names, private addresses and subscriber-related metadata. Redact a public copy before publishing; this report intentionally does not repeat those identifiers. Repository MIT wording must be scoped to project-authored contributions: no evidence here establishes redistribution rights for vendor firmware, embedded key material or third-party components. Do not include the audit's raw extracted binaries in a public release merely because the analysis scripts are project-authored.

### F14 — LOW: reproducibility and documentation hygiene

Replace machine-specific `file:///G:/...` links with valid repository-relative links for public documentation. Correct the nonexistent `part02_Device_tree.bin` / `part03_Linux_Kernel.bin` pointers to actual held `part02_dtb.bin` / `part03_kernel.bin` names. Label file offset, ELF section offset and virtual address separately. Correct XC module sizes: held `ubnthal.ko` is **465360 bytes** and `umac.ko` **2358768 bytes**, not the sizes used in parts of the report. Generate hardware/rate/partition tables from a hashed source rather than editing inconsistent copies.

## Concrete corrections and bench verification checklist

These are acceptance criteria for the coordinator's existing work, **not actions performed or newly authorized by this audit**. No requested live work is necessary to complete the offline review.

### Immediate documentary/source corrections

- [ ] Mark the current patch and operational recipes **NOT ACCEPTED** pending F01; keep failed/unsafe evidence visible.
- [ ] Correct the relocation-aware patch design and have a separate reviewer verify instruction, delay-slot, relocation and epilogue semantics against each exact module hash.
- [ ] Replace size-only firmware dispatch with exact preimage identities and a fail-closed unknown-build path; prove corrupted/truncated artifacts cannot advance state.
- [ ] Correct LTU primary/HPS maps, container metadata, XC board decoder, prism edge algorithm, rate table and OFDMA numeric parser examples.
- [ ] Replace the invented HSR pin/protocol sequence with a traced call-chain finding or explicit UNKNOWN.
- [ ] Archive the exact original/patched AP module or source diff and raw packet evidence; distinguish 14-byte encapsulation handling from 802.11 Address4/VLAN headers.
- [ ] Propagate statuses to README, CURRENT_STATE, RESEARCH_LEDGER, DECISIONS and Reddit; preserve historical measurements with proper versions and limitations.
- [ ] Redact operational identities and exclude vendor/private-key material from public artifacts; repair source links.

### Stage 10 isolated bench acceptance, after separate authorization

- [ ] Exact board/revision, firmware/module hashes, preimage bytes and relocation table; verified recovery method and known-good configuration backup.
- [ ] Read back the **loaded** patched instructions and relocated targets, then deliberately exercise beacon miss/re-association with bounded recovery. A file MD5 alone cannot close F01.
- [ ] Full frame matrix: both directions, multiple bridged MACs, ARP, DHCP/renewal, IPv6 ND/RA, multicast, VLAN/QinQ, MTU boundaries, A-MSDU and ordinary clients. Preserve packet captures and build-specific patch evidence.
- [ ] Failure injection: missing/corrupt/truncated patch, unknown firmware, failed mount/load, AP absent/slow boot/CAC, authentication failure, associated-but-broken datapath, overlapping timer execution and stale mode marker.
- [ ] Mode transitions stock -> hybrid -> stock with exact configuration/module/service restoration; software restart and physical power loss as separate cases.
- [ ] Legal DFS/CSA/channel-width changes, WPA2 rekey, repeated reconnect, config regeneration and bounded multi-hour/day soak with loss, latency, resets and service identities. Never disable regulatory controls to make these pass.
- [ ] Publish per-trial offered load, topology, endpoint location, channel/width, duration, repeats, latency percentiles, loss and receiver goodput. Endpoint CPU limits and short samples must remain visible.

### XC AirPrism acceptance, after separate authorization

- [ ] Board/BOM identity from the corrected table plus physical evidence; no LAP image assumptions for Rocket hardware.
- [ ] Trace each real HSR parameter consumer to its programming path and verify the actual pins/bus; resolve any GPIO sharing before writes.
- [ ] Verify prism selection at band edges and across widths using full occupied interval, including fallback entries and channel-switch sequencing.
- [ ] Compare vendor baseline and candidate filter states for insertion loss, wanted-signal EVM, adjacent-channel rejection, blockers, throughput, latency and recovery.
- [ ] Capture spectral-filter GPIO/IRQ/FFT timing and scanner identity on the exact board.
- [ ] Qualify XC AP and STA modes independently; patch-site similarity cannot substitute for either.

### LTU acceptance, only if separately approved as a lab experiment

- [ ] Trace board capability bits, peer negotiation, active rate table, training policy, bandwidth and FPGA version before claiming a reachable 4096 path.
- [ ] Distinguish configuration ceiling/readback, selected internal rate and **actual transmitted/received constellation**; neither a UI label nor a register write is RF proof.
- [ ] Compare 1024/4096 with fixed power or documented backoff, measured EVM/BLER/PER, both directions, applicable widths, multiple peers, goodput and latency; keep negative results.
- [ ] Validate OFDMA numeric parsing/polarity and band ordering offline first; then measure actual spectral occupancy and per-peer allocations if authorized. RX mask readback is insufficient.
- [ ] Keep FPGA, calibration, regulatory, signature and protected-partition boundaries intact. The corrected maps are evidence, not permission to flash.

## Final disposition

**KEEP** the confirmed static observations and reproducible evidence. **REJECT** the current universal/safe patch claim, incorrect flash/board/rate tables, asserted HSR pin map and publication wording. **INCONCLUSIVE / UNKNOWN** for full transparent bridging, long-term recovery, XC native/hybrid operational acceptance and LTU 4096/OFDMA RF behavior.

The requested offline review is complete. All input reports remain unchanged for the coordinator to remediate with reviewable diffs. The next decisive work is to resolve F01 and the documentary errors, recover the missing AP implementation/raw bench evidence, and trace the real HSR/LTU capability boundaries. No physical operator action is required merely to accept this audit report; live qualification is a separate gated task.
