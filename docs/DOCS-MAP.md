# FuturaMAX documentation map

Summary: entry point for any agent joining FuturaMAX — classifies every document (CURRENT /
SUPERSEDED / ABANDONED / GENERATED) and gives the reading order. Keywords: docs map, navigation,
AGENTS.md constitution, decisions, experiments, control boundary, real-hardware literature,
recovery runbook, research prompt, evidence pipeline.
Read when: you are starting work on FuturaMAX. Read this, then AGENTS.md, then DECISIONS.md.
Current verdict: OpenWrt 24.10.4 runs on the lab LAP-120 with proven recovery; Stage 3 is an
autonomous research loop (D-0009); custom-MAC go/no-go is UNKNOWN by design (NO-GO retracted, D-0003). Status: CURRENT (2026-09-26).

## Read in this order

1. `docs/DOCS-MAP.md` — you are here.
2. `AGENTS.md` — **the constitution.** Goal, non-goals, safety boundaries, stages, methodology.
   A previous session lost the project's goal by skipping this; do not.
3. `docs/DECISIONS.md` — D-0001…D-0009, newest first. Retractions are listed by name so a wrong
   conclusion cannot be re-cited from a confident-sounding older file.
4. `docs/CURRENT_STATE.md` — chronological; **read the last addendum first.**
5. `docs/EXPERIMENTS.md` — FMX register, the resolved install/recovery record, campaign plan C1–C8.
6. `docs/QCA988X_CONTROL_BOUNDARY.md` — what the host can actually control on QCA988x (source-verified; §4 is the CT debugfs truth table).
7. `knowledge/REAL_HARDWARE_LITERATURE.md` — every paper we lean on, tiered, with what transfers.
8. `docs/HARDWARE_MATRIX.md` — Grade-A identity of all six live units (LAP-GPS included).
9. `safety/recovery/FMX-0002_recovery_runbook.md` — before touching the lab unit.
10. `prompt.md` — the standing research prompt; update BASELINE before each wave.

Background only after the above: `knowledge/AIRMAX_ARCHITECTURE.md`, `RADIO_FIRMWARE_ANALYSIS.md`,
`AIROS_CONTROL_SURFACE.md` (airOS is out of scope as a deliverable, D-0004), and
`research/audits/CONTRADICTION_AUDIT.md` before trusting any wave-1 claim.

Do not read the raw reports under `research/raw/` unless you are verifying a specific claim.
They total ~355k characters and six of them answer the same eleven questions.

## Document register

### `docs/` — navigation and state

| File | Class | Notes |
|---|---|---|
| `DOCS-MAP.md` | CURRENT | This file. |
| `DECISIONS.md` | **CURRENT** | Architectural decisions D-0001…D-0013 incl. D-0009 (autoresearch), D-0010 (testbed RF), D-0011 (multi-LLM debate consensus: split-plane shaping, CPU boundaries, uplink gate), D-0012 (CoTSQ 6ms, target SRAM rate-cache lock, Bianchi PtMP hidden-node proof), D-0013 (Complete P0/P1 production engines). |
| `CURRENT_STATE.md` | CURRENT | Chronological log; last addendum is the truth, older verdicts may be retracted. |
| `EXPERIMENTS.md` | **CURRENT** | FMX-0001..0016 status (incl. FMX-0012 multi-LLM debate, FMX-0013..0016 analytical queue recipes), install/recovery record, Stage-3 campaigns C1–C8, INFERRED success thresholds. |
| `QCA988X_CONTROL_BOUNDARY.md` | **CURRENT** | Source-verified host control surface on QCA988x under ath10k-CT; §4 = spectral/set_rates/set_rate_override/ratemask-CT truths. |
| `HARDWARE_MATRIX.md` | **CURRENT** | Grade A, all six models read live 2026-08-08 (LAP-GPS `0xe7fd`, LAP-120 `0xe8e5`, Prism `0xe7e9`). |
| `TESTBED_ENVIRONMENT_GUIDE.md` | **CURRENT** | 2 AP + 20 CPE physical testbed specs, RF attenuation calculations, Fraunhofer distance, unattended urescue recovery. |
| `COMMUNITY_CALL_FOR_COLLABORATION.md` | **CURRENT** | Community manifesto, call for WISP/kernel hacker participation, methodology disclosure. |

### `debates/` — Multi-LLM Cross-Model Architecture Reviews

| File | Class | Notes |
|---|---|---|
| `debates/001-openmax-qca9880-ptmp-optimizat/synthesis.md` | **CURRENT** | Authoritative consensus synthesis (Claude Fable 5.1, OpenAI Codex GPT-6 Astra, Google Gemini 3.8 Flash): MIPS 74Kc CPU limits, external gateway CAKE offload, CPE TBF, and uplink go/no-go gate. |
| `debates/001-openmax-qca9880-ptmp-optimizat/transcript.md` | CURRENT | Full verbatim 3-round cross-examination transcript across all 3 models. |
| `debates/viewer.html` | CURRENT | Interactive multi-round debate viewer UI. |


### `knowledge/` — verified evidence, source-backed

| File | Class | Notes |
|---|---|---|
| `ANALYTICAL_QUEUE_MODEL_AND_HOOKS.md` | **CURRENT** | Canonical mathematical models ($\mathcal{H}_1 \dots \mathcal{H}_5$): CoTSQ 6ms A-MPDU efficiency $\eta(K)$, Bianchi Markov PtMP hidden-node collision derivations, and exact `ath10k-ct`/`mac80211` source hooks (`htt_max_amsdu_ampdu`, `num_rate_ctrl_objs_ct=24`, `num_msdu_desc_ct`). |
| `PRAISONAI_AQL_RESEARCH_REPORT.md` | **CURRENT** | Autonomous research report on AQL, CoTSQ, ath10k-ct internals, and PtMP queue optimization from PraisonAI multi-agent run. |
| `REAL_HARDWARE_LITERATURE.md` | **CURRENT** | Verified, tiered catalogue: IteRate, WiFiSpectralJam, ComMag 2024, ORCA, WiFi-CUTS, PNOFA, Quick & Plenty, Ending the Anomaly, hMAC, SmartLA, SRT-WiFi. Says what transfers (technique) vs what does not (numbers). |
| `ATH10K_CT_FIRMWARE_DEEP_DIVE.md` | **CURRENT** | Deep dive into QCA9880 / ath10k-ct internals: 30 vs 4 retries, HTT credit rings, bufferbloat, peer stats, and last_tx_bitrate airtime cliff. |
| `PACED_AGGREGATION_AND_COTSQ.md` | **CURRENT** | Mathematical and empirical analysis of A-MPDU aggregation in paced 802.11ac: why TSQ=1ms starves throughput and CoTSQ=6ms restores 10x goodput. |
| `PTMP_OUTDOOR_TDMA_VS_CSMA.md` | **CURRENT** | Physics of outdoor PtMP: hidden node collapse, airMAX AC proprietary Xtensa/ASIC architecture, and OpenWrt hybrid (AQL+RTS/CTS+DRR). |
| `AUTONOMOUS_WIRELESS_RESEARCH_ENGINE.md` | **CURRENT** | Specification of Karpathy/IteRate-style closed-loop AI optimization engine: parameter search space, multi-objective reward function, A/B/A/B gate. |
| `SPECTRAL_AND_CSI_ANALYSIS.md` | **CURRENT** | Baseband FFT scan architecture via RelayFS (PACKAGE_ATH_SPECTRAL) vs structural absence of CSI on QCA988x. |
| `AIRMAX_ARCHITECTURE.md` | CURRENT | Measured on 6 live radios. Per-mode/per-role radio firmware, `ubnt_poll_host` is control-plane only. |
| `RADIO_FIRMWARE_ANALYSIS.md` | CURRENT | Radio firmware carved from public images; Ubiquiti polling code inside it; frozen since ~2017. |
| `AIROS_CONTROL_SURFACE.md` | CURRENT, demoted (D-0004) | airOS config is reachable via `cfgmtd -w` + reboot incl. 62 hidden `radio.*` keys — real, but tuning airOS is **out of scope**. |
| `CUSTOM_MAC_GO_NO_GO.md` | CURRENT — verdict **UNKNOWN** | The earlier NO-GO was **RETRACTED (D-0003)**: it answered the wrong question, on the wrong stack. Stage-4 criteria must be *measured* on OpenWrt; radio-firmware work is deferred until a measured ceiling (D-0009). |

(`HARDWARE_MATRIX.md` and `QCA988X_CONTROL_BOUNDARY.md` live under `docs/` since the 2026-08-08
restructure; see the table above.)

Not yet written (each needs R3 verification first, and several need C01–C03 settled):
`INDEX.md`, `PROJECT_CHARTER.md`, `OPENWRT_ATH10K.md`, `TDMA_AND_SCHEDULED_MAC.md`, `RATE_CONTROL.md`,
`AGGREGATION_AND_BLOCK_ACK.md`, `QUEUEING_AIRTIME_AND_QOE.md`,
`HIDDEN_NODES_AND_CONTENTION.md`, `SPECTRUM_AND_RF_OPTIMIZATION.md`,
`LONG_DISTANCE_AND_GPS_TIMING.md`, `TECHNIQUE_CATALOG.md`, `NEGATIVE_EVIDENCE.md`,
`SOURCE_LEDGER.md`, `EXPERIMENT_BACKLOG.md`, `OPEN_QUESTIONS.md`.

Writing these from wave-1 material alone would launder model prose into canon. That is the
failure this pipeline exists to prevent.

### `research/` — the evidence pipeline

| Path | Class | Notes |
|---|---|---|
| `intake/manifest.yaml` | GENERATED | Provenance for all six runs. Regenerate: `tools/research/intake.py`. |
| `intake/manifest.json` | GENERATED | Machine-readable twin of the above. |
| `raw/<provider>/<run_id>/` | CURRENT | Byte-exact primary documents + asset-bundle hash index. **Never edit.** |
| `raw/hardware/*.txt` | CURRENT | Live-unit inventory 2026-08-08. MAC-sanitised. Grade-A evidence. |
| `extracted/<provider>/<run_id>/report.md` | GENERATED | Readable text. Not evidence. |
| `extracted/<provider>/<run_id>/links.jsonl` | GENERATED | Per-run citation ledger. |
| `normalized/sources.jsonl` | GENERATED | 535 deduped sources, typed, with cross-run counts. |
| `normalized/link_check.jsonl` | GENERATED | Reachability per URL, timestamped. |
| `audits/CITATION_AUDIT.md` | GENERATED | Per-run citation quality. |
| `audits/CONTRADICTION_AUDIT.md` | **CURRENT** | Hand-written. 17 conflicts, 5 resolved. The most important file here. |
| `gaps/GAP_LEDGER.md` | CURRENT | Open questions with owners and methods. |

Not yet produced: `normalized/claims.jsonl`, `measurements.jsonl`, `candidates.jsonl`,
`conflicts.jsonl`, and the `workstreams/W01–W14` packets. See CURRENT_STATE for why.

### `inputs/`

| File | Class | Notes |
|---|---|---|
| `prompts/external-deep-research-prompt.md` | CURRENT | Wave-1 prompt, recovered verbatim from the saved Grok page. **Do not re-run it** — see the audit's closing note. |

### Root, `safety/`, `inventory/` — operational

| Path | Class | Notes |
|---|---|---|
| `AGENTS.md` | **CURRENT — constitution** | Byte-identical to `FUTURAMAX_PROJECT_GUIDE.md`. Read in full before anything else. |
| `prompt.md` | CURRENT | Standing deep-research prompt with guardrails; the BASELINE and "already in hand" list must be refreshed per wave. |
| `safety/recovery/FMX-0002_recovery_runbook.md` | **CURRENT (rev 2)** | Install + recovery on the LAP-120. Route A (dd-unlock) is the install; Route C (urescue install) is REFUTED; urescue is recovery-only and refuses OpenWrt images. |
| `safety/recovery/urescue_push.py` | CURRENT | TFTP push to a unit in urescue. Probe with a READ request only; a write-request probe consumes the single session. |
| `safety/recovery/install_openwrt_ddunlock.py` | CURRENT | Scripted dd-unlock: interrupt at the ROOTFS write, stage the image as a file, verify the whole image across the mtd2/mtd3 boundary before reboot. |
| `inventory/board_probe/preflash_probe.py` | CURRENT | Read-only pre-flash evidence collector with an enforced write-primitive guard and a 0-stations abort. |
| `firmware/openwrt/`, `firmware/WA.v8.5.12*.bin` | CURRENT | SHA-256-verified OpenWrt 24.10.4 images and the stock airOS rollback image. |
| `firmware/openwrt/futuramax-r28959-spectral/` | **CURRENT (2026-09-26, PROVISIONAL)** | FMX-0011 output: spectral-enabled 24.10.4 (r28959) images for LAP-120, LiteBeam AC Gen2, NanoStation 5AC, Loco 5AC + sha256sums, manifest, dot.config, build log. Not yet flashed. |
| `tools/openwrt-build/` | **CURRENT** | Reproducible build system: `MANIFEST.md` (what/how/hashes/caveats), seed config + diffconfig, `run-attached.sh`/`build.sh` (WSL runner with gcc-12 shim and retry), `exit-checks.sh`, `copy-artifacts.sh`, `diag-hang.sh`. |
| `research/raw/chatgpt/2026-09-20/` | CURRENT | Research waves 2 and 2b, verbatim, hashed, registered in the manifest with verification records. |

### `tools/research/`

| File | Class | Purpose |
|---|---|---|
| `intake.py` | CURRENT | R0 registration + hashing. Idempotent. |
| `extract.py` | CURRENT | HTML/PDF/MD → markdown + link ledger. |
| `normalize_sources.py` | CURRENT | R2 cross-run source dedupe. |
| `check_links.py` | CURRENT | R3 reachability probe. Resumable; `--refresh` to redo. |
| `make_citation_audit.py` | CURRENT | Renders the citation audit. |
| `unpack_airos.py` | CURRENT | Unpacks a published airOS `.bin` into u-boot/kernel/rootfs parts. |
| `praison_researcher.py` | CURRENT | PraisonAI autonomous research loop driver for queue and ath10k deep-dives. |
| `praison_grounded_investigator.py` | CURRENT | Grounded multi-agent research team with C-source grep and silicon feasibility gatekeeper. |
| `srccache/` | GENERATED | Shallow ath10k-ct clone + fetched mainline sources. Reproducible; safe to delete. |

### `tools/sim/`

| File | Class | Purpose |
|---|---|---|
| `ptmp_contention_sim.py` | CURRENT | Discrete-event PtMP CSMA/CA simulator with hidden-node geometry, validating Bianchi models. |

### `telemetry/spectral_fft/`

| File | Class | Purpose |
|---|---|---|
| `parser.py` | CURRENT | High-performance binary RelayFS parser (`fft_sample_ath10k`) and sub-millisecond interference classifier (23.4 µs/sample). |
| `test_parser.py` | CURRENT | Unit test suite and CPU benchmark for the spectral parser. |

### `controller/optimizer/`

| File | Class | Purpose |
|---|---|---|
| `rate_bandit.py` | CURRENT | ADR-bandit (Adaptive Resetting Multi-Armed Bandit) rate-mask controller with Page-Hinkley drift detector. |
| `test_rate_bandit.py` | CURRENT | Dynamic fading benchmark verifying rapid convergence and rain fade adaptation. |

### `tools/observability/`

| File | Class | Purpose |
|---|---|---|
| `dashboard.py` | CURRENT | Real-time CLI/Markdown observability dashboard for multi-agent telemetry and experiment tracking. |
| `ledger.py` | CURRENT | SQLite ledger abstraction (`telemetry.db`) recording experiment metrics, queue states, and hypotheses. |

### `tools/inventory/`

| File | Class | Purpose |
|---|---|---|
| `AIROS_INVENTORY.md` | CURRENT | Read-only command sheet. G04 closed with it. |
| `collect.py` | CURRENT | Automated read-only SSH collector. `UBNT_PASS` from env, never on disk. |

### Pre-existing, operator-owned

| Path | Class | Notes |
|---|---|---|
| `obsidian-vault/log.md` | CURRENT | Operator's append-only log. **Inspected only; never edited.** |
| `futuramaxresearch/` | CURRENT | Operator drop zone. Read-only to this pipeline; originals untouched. |
| `researchplan.md` | CURRENT | The multi-agent research program spec (W01–W14). |
| `handoffs/handoff-2026-08-08T12-57-03-a63934.md` | CURRENT | The R0–R9 / E0–E5 contract this work follows. |

## Regenerating everything

```bash
python tools/research/intake.py            # idempotent, content-derived run_ids
python tools/research/extract.py
python tools/research/normalize_sources.py
python tools/research/check_links.py       # resumable; ~6 min for 535 URLs
python tools/research/make_citation_audit.py
```

## Rules that outlive this file

- Generated indexes never override current source evidence.
- Preserve `UNKNOWN`; do not omit uncertainty to make a document read cleanly.
- Time-sensitive statements carry an accessed/verified date.
- A completed JSON directory is not proof that research is ready.
