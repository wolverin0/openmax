# Codex Task — openMAX Physical-Boundary Phase 0

You are the lead implementation and experimental-methodology engineer for **openMAX**.

Repository: `wolverin0/openmax`

The immediate objective is **not** another broad literature review and **not** a risky radio-firmware experiment. Convert the new physical-boundary research into a source-audited, machine-executable experimental ladder, repair the experiment-selection infrastructure, and prepare the first bounded QCA988x bench gates.

## Mandatory reading order

Read the current repository before changing anything:

1. `AGENTS.md`
2. `README.md`
3. `docs/CURRENT_STATE.md` — newest entries first
4. `docs/DECISIONS.md`
5. `docs/EXPERIMENTS.md`
6. `docs/RESEARCH_LEDGER.md`
7. `docs/QCA988X_CONTROL_BOUNDARY.md`
8. `docs/UMAC_DATAPATH.md`
9. `knowledge/RADIO_FIRMWARE_ANALYSIS.md`
10. `knowledge/ATH10K_CT_FIRMWARE_DEEP_DIVE.md`
11. `knowledge/AUTONOMOUS_WIRELESS_RESEARCH_ENGINE.md`
12. `knowledge/SPECTRAL_AND_CSI_ANALYSIS.md`
13. `tools/research/intake.py`
14. `analysis/metrics/schema.py`
15. `analysis/regression_gate/gatekeeper.py`
16. `docs/TESTBED_ENVIRONMENT_GUIDE.md`
17. all relevant recovery/protected-partition rules under `safety/`

Also ingest and read the supplied report, preserving its bytes exactly:

`openMAX_QCA988x_physical_boundary_research_2026-10-24.md`

If the report is in the repository drop zone, use the existing intake/provenance workflow. If it is attached elsewhere, first copy it into the appropriate operator drop zone without editing it, extend the intake configuration minimally if needed, run the intake tool, and record SHA-256, size, model/provider, timestamp and raw immutable path. Do not hand-edit generated manifests.

## Scientific orientation

The program now distinguishes four boundaries:

1. Ubiquiti software/scheduler limits;
2. Qualcomm production-firmware limits;
3. standard 802.11ac implementation limits;
4. hard QCA988x RF/baseband/silicon limits.

The new report identifies two direction-changing exact-family leads:

- exact AR9888/Peregrine descriptors expose `bb_capture_channel`, `bb_captured_channel`, `bb_length`, `txbf_h_info`, EVM and timing metadata;
- a public Qualcomm-derived tree has an explicit `TARGET=AR9888` UTF/factory-test build path and broad TCMD/ART facilities.

It does **not** establish raw ADC capture, arbitrary IQ transmission, writable constellation/FEC/pilot tables or a reproducible production-target build. Keep those `UNKNOWN` until exact evidence or hardware measurement resolves them.

## This session's hard safety boundary

This first phase is **offline/read-only with respect to radios** unless every existing repository precondition for a sacrificial bench unit is already independently satisfied and the only physical action is explicitly classified below as read-only.

Do not:

- contact or change production devices;
- flash any radio;
- write OTP/eFuse, calibration, ART, board-data, factory or MAC-address storage;
- modify regulatory/DFS behavior;
- transmit outside a shielded/cabled legal bench;
- execute BMI memory/register writes;
- run unknown UTF commands on hardware;
- claim a QCA988x capability merely because a shared Qualcomm header contains it;
- vendor proprietary Ubiquiti code into the repository;
- copy third-party source without recording license and provenance.

Any future device-facing action must have an allowlist, exact target identity, immutable before-state, timeout, health gate, rollback and recovery path.

## Workstream A — register and distill the research

1. Register the report using the existing provenance/intake system.
2. Keep the byte-exact original under the raw research tree.
3. Create a concise authoritative synthesis, without replacing the raw report:
   - `knowledge/QCA988X_PHYSICAL_BOUNDARY_2026.md`
4. Create an evidence-delta document:
   - `research/physical_boundary/evidence_delta_2026-10-24.md`
5. The delta must separate:
   - already proven in openMAX;
   - genuinely new exact-family evidence;
   - cross-chip inference;
   - unsupported/unknown claims;
   - claims that correct an older repository statement.
6. Every material claim must include a pinned source URL or exact repository evidence path and the labels `CONFIRMED`, `INFERRED`, `UNKNOWN` or `REFUTED`.
7. Update `docs/DOCS-MAP.md`, `docs/RESEARCH_LEDGER.md` and any superseded control-boundary text without erasing historical evidence.

## Workstream B — audit the top exact-family claims

Audit the report's P0/P1 source chain directly. Do not trust the prose report by itself.

Pin and inspect at minimum:

- `SpaceExplorationTechnologies/starlink-wifi@1d585ee8909bf7bab4391c0c52d8a9d44137b3bb`
- `torvalds/linux@5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f`

Verify and record exact paths, symbols, field descriptions and source hashes for:

- AR9888 target build selection and UTF build graph;
- `bb_capture_channel`;
- `bb_captured_channel`;
- `bb_length`;
- `txbf_h_info`;
- compressed-V/SVD fields;
- EVM/timestamp fields;
- standard rate-series/MCS descriptor boundary;
- `ADCCAPTURE` shared ABI and whether an AR9888 handler/registration is actually present;
- `GENWAVEFORM` semantics and whether it accepts host IQ or only a waveform index;
- ath10k testmode/UTF load and segmented WMI transport;
- BMI and coredump read paths.

Create:

- `research/physical_boundary/source_manifest.json`
- `research/physical_boundary/source_audit.md`

Each source-manifest item must contain: repository, commit, path, file SHA-256, license/provenance note, relevant symbol/field, exact-family applicability and conclusion.

Do not vendor entire external trees into Git. A reproducible fetch/cache script with pinned commits is preferable.

## Workstream C — build the machine-readable experimental ladder

Create:

- `docs/PHYSICAL_BOUNDARY_EXPERIMENTAL_LADDER.md`
- `research/physical_boundary/ladder.yaml`
- JSON Schema or equivalent validation for the ladder
- unit tests for parsing and validation

Represent each gate as a node with at least:

- ID and title;
- hypothesis;
- current label/certainty;
- branch of the research tree it resolves;
- exact prerequisites;
- target hardware/firmware/driver;
- source evidence;
- reversible versus irreversible;
- brick/regulatory/RF risk;
- required equipment;
- allowed commands/actions;
- forbidden commands/actions;
- observables and artifact paths;
- success criterion;
- falsification criterion;
- stop condition;
- rollback/recovery procedure;
- whether it can be automated;
- dependencies/unlocks;
- operator action required.

Seed the ladder with the report's major gates, but re-order by real prerequisites rather than copying ranking blindly:

- `PB-000`: report intake and source audit;
- `PB-001`: metric/gatekeeper correctness;
- `PB-010`: descriptor/channel-capture static trace;
- `PB-011`: pre-stripped RX descriptor export design;
- `PB-020`: exact AR9888 UTF build-graph reconstruction;
- `PB-021`: known-good UTF binary provenance/build comparison;
- `PB-022`: read-only UTF transport qualification;
- `PB-023`: non-destructive UTF capability enumeration;
- `PB-024`: `ADCCAPTURE` implementation/handler decision;
- `PB-030`: channel-dump activation and memory-diff experiment;
- `PB-031`: channel-dump decoding/calibration;
- `PB-040`: one inert target-firmware modification and repeated recovery;
- `PB-050`: target timer/jitter measurement;
- `PB-051`: one-link target-resident scheduler prototype;
- `PB-060`: hidden mapper/pilot/FEC/arbitrary-IQ decision gate;
- `PB-070`: constrained autonomous MAC-policy search.

A node may not become `RUNNABLE` until all safety and evidence prerequisites are machine-verifiable.

## Workstream D — repair the autonomous experiment oracle before using it

The current infrastructure must not select winners until corrected.

### D1. Metric schema

`analysis/metrics/schema.py` currently auto-computes goodput/MHz using a fixed 40 MHz denominator when `goodput_per_mhz` is missing. Replace this with an explicit, validated channel-width source.

Requirements:

- no silent 40 MHz fallback;
- derive from experiment metadata or require width in every sample;
- support at least 5/10/20/40/80 MHz;
- reject inconsistent/missing widths;
- migrate existing records reproducibly or mark them legacy/unknown;
- add tests proving mixed-width rankings are correct.

### D2. Regression gatekeeper

`analysis/regression_gate/gatekeeper.py` claims a p99 → p95 → fairness → goodput hierarchy but currently does not fully implement it and treats A and B as independent groups.

Implement a scientifically defensible first version:

- preserve A/B temporal block identity and pairing;
- support randomized A/B/A/B and larger paired blocks;
- model or at least detect temporal drift using sentinel baseline blocks;
- enforce hard safety gates first;
- evaluate p99, p95, worst-peer service/fairness and goodput/MHz, not only goodput;
- avoid automatic `KEEP` from only two samples per arm;
- add paired permutation/bootstrap inference suitable for small RF experiments;
- record effect sizes and uncertainty, not only a p-value;
- implement an alpha budget or false-discovery control for repeated autonomous trials;
- distinguish `REJECT`, `INCONCLUSIVE`, `KEEP_FOR_REPLICATION`, and `PROMOTE`;
- require independent holdout replication before `PROMOTE`;
- add an A/A null-label simulation/replay test measuring false-positive rate;
- preserve backward compatibility through explicit schema/version handling, not silent reinterpretation.

Do not overclaim formal statistical guarantees. Document assumptions and known limits.

## Workstream E — create offline reverse-engineering tools

Implement reusable, tested tools; do not manually grep and paste one-off findings.

Preferred initial tools:

1. `tools/qca988x/fetch_pinned_sources.py`
   - fetch/verify only required files at pinned commits;
   - record hashes and licenses;
   - support offline cache.

2. `tools/qca988x/extract_descriptor_map.py`
   - parse exact AR9888 descriptor headers;
   - emit JSON/Markdown field maps for channel capture, EVM, timing, TXBF and rate series;
   - retain bit offsets/masks and source locations.

3. `tools/qca988x/trace_utf_handlers.py`
   - map command dictionary → registration → handler → build condition;
   - classify each command `EXACT_AR9888`, `SHARED_ONLY`, `NOT_FOUND`, or `CROSS_CHIP`;
   - specifically cover `ADCCAPTURE`, `GENWAVEFORM`, `PHYDBGDUMP`, memory/register access and non-destructive status/version commands.

4. `tools/qca988x/utf_build_inventory.py`
   - reconstruct the AR9888 build graph, missing toolchain/includes/libraries/linker scripts;
   - output a blocker matrix rather than faking a build.

5. `tools/qca988x/memory_diff_analyzer.py`
   - offline utility for aligned target-memory snapshots;
   - detect packet-correlated regions, stable pointers/rings and changed blocks;
   - no device access in this phase.

Add unit tests and small committed fixtures derived from legally retainable snippets/metadata, not wholesale external source copies.

## Workstream F — prepare, but do not casually execute, the first physical campaign

Create a frozen plan for the first physical campaign:

`docs/bench/PB_FIRST_PHYSICAL_CAMPAIGN.md`

The campaign should have two tracks:

### Track 1 — exact UTF read-only qualification

1. sacrificial exact QCA988x unit identity and board-data hashes;
2. proven serial/TFTP/bootloader recovery;
3. normal-firmware baseline and post-UTF recovery baseline;
4. known-good or reproducibly built UTF provenance;
5. testmode start/stop only;
6. allowlisted version/status/capability commands only;
7. no register/memory/OTP/calibration writes;
8. bounded timeouts and power-cycle recovery;
9. complete command/event byte capture;
10. repeated normal-firmware restoration.

### Track 2 — channel-capture path qualification

Initially static/instrumentation only:

1. identify where `bb_capture_channel` can be set;
2. identify where `bb_captured_channel`, `bb_length`, EVM and H-info are consumed or stripped;
3. design a minimal copy/export path that preserves normal behavior;
4. define cabled/shielded known-channel stimuli;
5. define target-memory before/after snapshots and correlation tests;
6. do not perform unknown memory writes;
7. success requires a repeatable packet-correlated blob whose amplitude/phase behavior changes predictably under controlled channel changes.

Codex may execute a physical step only if the repository already proves every prerequisite, the target is explicitly sacrificial, the action is on the allowlist, production access is impossible, and the command is recoverable. Otherwise deliver a ready-to-run plan and stop before hardware mutation.

## Tests and acceptance

Run all relevant existing tests plus new tests.

Minimum Phase-0 acceptance:

- report registered with immutable provenance;
- all P0 exact-family claims independently audited;
- no cross-chip claim silently promoted;
- experimental ladder validates mechanically;
- width normalization bug removed;
- gatekeeper uses paired/block-aware logic and cannot `PROMOTE` from tiny/noisy A/B samples;
- A/A replay test reports an acceptable or explicitly unresolved false-positive rate;
- pinned-source tools are reproducible;
- first physical campaign is frozen with exact safety gates;
- no production device contacted;
- no irreversible radio action performed;
- repository documentation and ledgers updated.

## Required final response

Report:

1. current branch and starting commit;
2. files created/changed;
3. exact source claims confirmed, downgraded or refuted;
4. tests run and results;
5. whether any hardware was contacted and why;
6. blockers to exact UTF build/boot;
7. blockers to channel-dump activation/export;
8. the single next physical action, with its prerequisite checklist;
9. any operator-only action required;
10. final commit SHA, without pushing unless the existing repository workflow explicitly authorizes it.

Use the project labels `CONFIRMED`, `INFERRED`, `UNKNOWN`, `REFUTED`. Do not invent hardware results. One primary scientific change at a time.
