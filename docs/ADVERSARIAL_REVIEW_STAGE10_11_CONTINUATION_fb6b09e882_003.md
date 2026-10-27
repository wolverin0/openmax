<!-- doc-head: ADVERSARIAL_REVIEW_STAGE10_11.md continuation 3 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](ADVERSARIAL_REVIEW_STAGE10_11.md) | Part 3/3
<a id="adversarial-review--stage-10-stage-11a-stage-11b-and-public-claims"></a> [Adversarial review — Stage 10, Stage 11A, Stage 11B and public claims](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#adversarial-review--stage-10-stage-11a-stage-11b-and-public-claims) | <a id="executive-verdict-and-severity-table"></a> [Executive verdict and severity table](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#executive-verdict-and-severity-table) | <a id="evidence-method-and-reproducibility"></a> [Evidence, method and reproducibility](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#evidence-method-and-reproducibility) | <a id="detailed-findings--stage-10-wa-stock-airos-8-interoperability"></a> [Detailed findings — Stage 10: WA stock airOS 8 interoperability](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#detailed-findings--stage-10-wa-stock-airos-8-interoperability) | <a id="f01--critical-a-retained-elf-relocation-invalidates-the-nop-claim"></a> [F01 — CRITICAL: a retained ELF relocation invalidates the NOP claim](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#f01--critical-a-retained-elf-relocation-invalidates-the-nop-claim) | <a id="remaining-watchdog-reconnect-and-dfs-paths"></a> [Remaining watchdog, reconnect and DFS paths](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#remaining-watchdog-reconnect-and-dfs-paths) | <a id="f02--high-persistence-is-not-a-transactional-fail-safe"></a> [F02 — HIGH: persistence is not a transactional fail-safe](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#f02--high-persistence-is-not-a-transactional-fail-safe) | <a id="f03--high-the-bridging-claim-lacks-the-decisive-implementation-and-packets"></a> [F03 — HIGH: the bridging claim lacks the decisive implementation and packets](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#f03--high-the-bridging-claim-lacks-the-decisive-implementation-and-packets) | <a id="detailed-findings--stage-11a-xc-rocket-prism-and-airprism"></a> [Detailed findings — Stage 11A: XC Rocket Prism and AirPrism](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#detailed-findings--stage-11a-xc-rocket-prism-and-airprism) | <a id="f04--high-the-published-board-layout-and-hardware-matrix-are-not-faithful-to-the-elf"></a> [F04 — HIGH: the published board layout and hardware matrix are not faithful to the ELF](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#f04--high-the-published-board-layout-and-hardware-matrix-are-not-faithful-to-the-elf) | <a id="f05--high-the-prism-algorithm-tests-the-full-channel-interval"></a> [F05 — HIGH: the prism algorithm tests the full channel interval](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f05--high-the-prism-algorithm-tests-the-full-channel-interval) | <a id="f06--high-the-purported-hsr-spigpio-sequence-is-misattributed"></a> [F06 — HIGH: the purported HSR SPI/GPIO sequence is misattributed](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f06--high-the-purported-hsr-spigpio-sequence-is-misattributed) | <a id="f07--medium-spectral-filtering-and-hybrid-mode-need-narrower-claims"></a> [F07 — MEDIUM: spectral filtering and hybrid mode need narrower claims](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f07--medium-spectral-filtering-and-hybrid-mode-need-narrower-claims) | <a id="detailed-findings--stage-11b-ltu-4096-qam-ofdma-and-architecture"></a> [Detailed findings — Stage 11B: LTU 4096-QAM, OFDMA and architecture](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#detailed-findings--stage-11b-ltu-4096-qam-ofdma-and-architecture) | <a id="f08--critical-the-published-flash-map-contradicts-the-actual-dtb"></a> [F08 — CRITICAL: the published flash map contradicts the actual DTB](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f08--critical-the-published-flash-map-contradicts-the-actual-dtb) | <a id="f09--high-meaningful-4096-qam-software-exists-a-qualified-ptmp-unlock-is-unproven"></a> [F09 — HIGH: meaningful 4096-QAM software exists; a qualified PtMP unlock is unproven](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f09--high-meaningful-4096-qam-software-exists-a-qualified-ptmp-unlock-is-unproven) | <a id="f10--high-rate-mapping-is-wrong-and-ceiling-is-not-fixed-modulation"></a> [F10 — HIGH: rate mapping is wrong, and ceiling is not fixed modulation](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f10--high-rate-mapping-is-wrong-and-ceiling-is-not-fixed-modulation) | <a id="f11--high-ofdma-parsing-and-notch-interpretation-are-overstated"></a> [F11 — HIGH: OFDMA parsing and notch interpretation are overstated](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f11--high-ofdma-parsing-and-notch-interpretation-are-overstated) | <a id="f13--medium-higher-layer-ideas-are-portable-the-actuator-is-not-automatic"></a> [F13 — MEDIUM: higher-layer ideas are portable; the actuator is not automatic](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_002.md#f13--medium-higher-layer-ideas-are-portable-the-actuator-is-not-automatic)

<!-- stage822a-payload-begin -->
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
<!-- stage822a-payload-end -->
