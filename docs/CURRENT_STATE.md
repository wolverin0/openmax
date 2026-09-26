# FuturaMAX current state

Summary: chronological state log for FuturaMAX — READ THE LAST ADDENDUM FIRST; earlier sections
are history and some of their verdicts were later retracted (see DECISIONS.md D-0003..D-0009).
Keywords: OpenWrt 24.10.4 on LAP-120, FMX-0002 done, spectral rebuild FMX-0011, research wave 2,
IteRate, WiFiSpectralJam, D-0009 autoresearch, second radio, urescue.
Read when: resuming FuturaMAX work or handing it to another pane. Current verdict: **OpenWrt runs
on the lab unit; Stage 3 is defined as an autonomous research loop (D-0009); next actions are the
spectral rebuild (FMX-0011) and campaign C1; the second radio is the binding constraint.** Status: CURRENT, 2026-09-26 (FMX-0011 image built, not flashed; see last addendum).

## Pipeline position

| Stage | Status | Evidence |
|---|---|---|
| R0 intake & provenance | **COMPLETE** | 6 runs registered, hashed, raw-preserved; `research/intake/manifest.yaml` |
| R1 independent web discovery | **CLOSED for wave 1** | 6 independent runs ingested, well above the 2-run gate |
| R2 mechanical normalization | **PARTIAL** | sources done (535 deduped); claims/measurements/candidates **not** done |
| R3 source verification | **PARTIAL** | all 535 URLs reachability-checked; 1 device page read in full; content verification not done |
| R4 targeted gap research | NOT STARTED | gap ledger written, agents not dispatched |
| R5 workstream synthesis | NOT STARTED | needs C01–C03 settled first |
| R6 contradiction & portability | **MOSTLY RESOLVED** | 17 conflicts; 8 resolved incl. all 3 control-boundary questions |
| R7 canonical knowledge | **STARTED** | 5 of 19 written incl. `RADIO_FIRMWARE_ANALYSIS.md`, `CUSTOM_MAC_GO_NO_GO.md` |
| R8 experiment mapping | NOT STARTED | candidate experiments exist in raw reports, not specified |
| R9 research release gate | **BLOCKED** | see below |

## What was actually done this session

1. **Registered all six inputs** with SHA-256, byte-exact raw copies under
   `research/raw/<provider>/<run_id>/`. The 43 MB of browser asset bundles stay at their
   original path and are pinned by per-file hash indexes instead of being duplicated —
   provenance without the bloat. Originals in `futuramaxresearch/` were never modified.
2. **Extracted** all six to markdown plus per-run link ledgers (355k chars, 605 raw links).
3. **Deduped to 535 unique sources**, typed and cross-referenced by run.
4. **Reachability-checked all 535 URLs**: 424 reachable, 72 bot-blocked, 6 genuinely dead,
   9 damaged by our own extractor.
5. **Wrote the contradiction audit** — 17 conflicts across the six runs.
6. **Resolved 5 of them against primary sources**, including reading the NanoStation AC
   OpenWrt device page through a browser (plain HTTP gets a bot challenge).
7. **Wrote the first knowledge file** from Grade-A evidence.
8. **Recovered the exact wave-1 prompt** verbatim from the saved Grok page.

## The three findings that matter

### 1. Cross-model agreement is not evidence, and one run is actively unreliable

Only **51 of 535 sources** were cited by more than one run — six near-disjoint sweeps. Where
the runs do agree on conclusions, they mostly do not agree on evidence.

The `google` run produced the most quotable numbers from the fewest sources (20 URLs, versus
253 for mistral) and is the origin of every figure this audit rejected. Its IteRate citation
resolves to a **paper about active galactic nuclei**. Its target SoC (QCA9563 @ 750 MHz) is
wrong. Its OpenWrt-vs-airMAX regression figures are graded CONFIRMED against "Reddit
Reports" and are mutually inconsistent within one document.

### 2. All six runs described the wrong software stack

Every run framed the question as "airMAX firmware vs ath10k". The OEM boot log shows airOS
runs the **QCA vendor `ol_ath` offload driver (`ath_pci: 10.1.467`) plus proprietary
`ubnthal` and `ubnt_poll_host` kernel modules** — not ath10k. airMAX is a *host kernel
module*, and its printk parameters expose polling, fixed-frame mode, `noack_mode`, station
priority and ATPC by name.

This changes the framing of W02/W03 and means every airOS↔OpenWrt A/B test changes two
layers at once. It also gives W02 a real search handle (`ubnt_poll_host`) instead of a
marketing term.

### 3. First Grade-A evidence exists, and it is not for the AP

NanoStation AC is confirmed AR9342 rev 2 + QCA988X hw2.0, firmware `10.2.4-1.0-00037`,
`raw-mode` advertised, `max-sta 128`, with a complete flash map that pins the protected
partitions. **LAP-GPS — the AP the whole project depends on — remains unverified.**

## Critical path (four items)

| # | Question | Method | Owner |
|---|---|---|---|
| 1 | ~~airtime scheduler on ath10k~~ | **RESOLVED** — runs, but on estimated airtime with a 6 Mbps cliff | done |
| 2 | ~~rate control ownership~~ | **RESOLVED** — firmware, via `HAS_RATE_CONTROL` | done |
| 3 | ~~A-MPDU control~~ | **RESOLVED in code** — device-wide `htt_max_amsdu_ampdu`; firmware behaviour UNVERIFIED | E2 |
| 4 | ~~What silicon is in LAP-GPS?~~ | **RESOLVED** — 6 units read live; all QCA988x/AR934x (Prism QCA955x) | done |

**All four are settled.** The next constraint is the radio-firmware extraction (G08), not identity.

## Blocked on the operator

- **Physical hardware access** for item 4 and for every E-stage experiment. Nothing in the
  research pipeline can answer what silicon is in the AP.
- **Decision on wave 2 shape** — see below.

## Explicitly not done, and why

- **`claims.jsonl` / `measurements.jsonl` / `candidates.jsonl` were not generated.**
  Mechanically splitting six reports into thousands of atomic claim rows before C01–C03 are
  settled would produce a large, precise, and partly wrong dataset — and the precision would
  make it look verified. The contradiction audit is the honest intermediate artifact.
- **Eighteen of nineteen knowledge files were not written.** Same reason: they would restate
  model prose as canon.
- **W01–W14 workstream agents were not dispatched.** Awaiting the operator's decision on
  scale, and three of the four critical-path items are source-reading tasks that do not need
  a fan-out.
- **No engineering, flashing, or configuration change of any kind.** The handoff authorises
  research stages only.

## R9 verdict

**BLOCKED.** Named missing evidence: critical-path items 1–4. Named physical action
required: read PCI ID / sysid / firmware version off a real LAP-GPS, LiteBeam 5AC Gen2 and
Loco 5AC. A completed pipeline directory is not proof of readiness, and this one is
deliberately incomplete.

## Next actions

1. ~~Settle C01-C03 from source.~~ **DONE** - see `knowledge/QCA988X_CONTROL_BOUNDARY.md`.
2. Operator: run `tools/inventory/AIROS_INVENTORY.md` on one spare unit per model, LAP-GPS first.
2b. Then the peer-stats/airtime-estimate experiment (§2d of the control-boundary file) - highest decision value per unit of effort in the whole candidate list.
3. Characterise `ubnt_poll_host` / `ubnthal` from GPL releases and FCC filings (W02).
4. Only then: normalize claims, dispatch remaining workstreams, and write the knowledge files.

## Addendum 2026-08-08 (late): seventh run ingested

A `perplexity` run was supplied after the first six and is registered through the same
pipeline (`perplexity-5ed045f6`, 82 cited URLs, 65 of them new). Source universe is now
**600 unique sources across 7 runs**. Its claims have NOT yet been folded into the
contradiction audit - that is the next R6 increment.

## Addendum 2026-08-08 (later): live hardware sweep — G04 CLOSED

Operator authorised read-only access to six production radios. Collected via
`tools/inventory/collect.py`; raw output MAC-sanitised in `research/raw/hardware/`.

All six are QCA988x Wave 1 on AR934x @535 MHz (Rocket Prism 5AC on QCA955x @720 MHz).
LAP-GPS confirmed `sysid 0xe7fd`, GPS present. See `knowledge/HARDWARE_MATRIX.md`.

**The finding that changes the project:** airMAX loads *different QCA radio firmware per mode
and per role* — PTP ~214 KB, PTMP-AP ~250 KB, PTMP-STA ~233 KB, distinct binaries. The
airMAX/OpenWrt difference is therefore not only the host scheduler module; it includes the
radio firmware itself. This is the strongest evidence so far on custom-MAC feasibility and it
points to NO-GO on stock firmware while showing the silicon is capable. Full analysis in
`knowledge/AIRMAX_ARCHITECTURE.md`.

Also: `U-AME` appears on all six units including plain CPEs, so it is not a Prism-specific
accelerator — the "airMAX scheduler ASIC" claim (C15/G09) is now checked and unsupported.

R9 verdict moves BLOCKED -> **PARTIAL**. Remaining blockers are evidence tasks (G08 firmware
comparison, W02 module characterisation), not access.

## Addendum 2026-08-08 (final): G08 CLOSED — radio firmware extracted and compared

Route: downloaded `WA.v8.7.11...bin` from Ubiquiti's public site, unpacked it
(`tools/research/unpack_airos.py`), extracted the squashfs rootfs, and carved three radio
firmware images out of `umac.ko` **by ELF symbol**. No device touched. Fully reproducible
from public downloads.

`athwlan_AR9888v2_ptp_bin` (216,059) / `_ptmp_ap_bin` (252,697) / `_ptmp_sta_bin` (235,270).
Verified byte-exact against the live LiteBeam 5AC LR running that same build (its boot log
reported 216060 / 235272 — the loader pads to a 4-byte boundary).

**Result:** the Ubiquiti images contain `UBNT_POLL_MEM_ALLOC`, `ubnt-poll: _on_swbmiss` and
`ubnt_set_power_range` — all **absent** from stock QCA988X firmware. airMAX's polling MAC
runs partly on the Xtensa core inside the radio. Different container magic too (`SGMT` vs
`QCA-ATH10K`).

Consequence: `knowledge/CUSTOM_MAC_GO_NO_GO.md` now reads **NO-GO for replicating airMAX on
stock firmware** (Grade A), which removes E5 from the roadmap and recommends not running the
E4 gate as a custom-MAC test. The airOS-first path (beating airMAX on latency/fairness/
spectrum rather than replacing its MAC) is untouched and is now the clear focus.

The blobs are proprietary and are **not** in this repo — only sizes, hashes and strings.

## Addendum 2026-08-08 (later still): G21 + G22 + G23 closed autonomously

**G21 — 14 airOS releases swept, 2016-09 to 2026-08-06.** Pulled every WA release build from
Ubiquiti's public firmware API, unpacked each, carved the radio firmware by symbol, and
captured changelogs. `tools/research/fw_version_sweep.py`;
matrix at `research/raw/hardware/fw_version_matrix.json`.

Headline: **the AP/STA firmware role-split landed in airOS v8.3.1 (2017-07-28)** — before it,
builds shipped one generic `athwlan_AR9888v2_bin`; from 8.3.1 that is replaced by
`ptmp_ap` + `ptmp_sta`. That release's changelog is almost entirely "airMAX-ac FF" (Fixed
Frame) work, and 8.3 is the release that brought GPS Sync to airMAX AC. Causally INFERRED,
temporally exact.

Also: `ubnt-poll` code is present in **every** build back to 2016 — there is no airMAX AC
whose radio firmware is stock QCA. And the radio firmware is effectively frozen: 8.7.13 =
8.7.17 and **8.7.22 = 8.7.25** byte-for-byte, so the upgrade released two days ago changes
nothing in the radio.

**G22 — the host/target split is settled and favours firmware.** `ubnt_poll_host.ko`'s 150
functions contain **zero** scheduling primitives (no slot/tdma/airtime/sched/tsf/framing).
It is a control plane: station table, management-frame hooks, IE negotiation, config push to
the target. This strengthens the custom-MAC NO-GO — the replaceable half is the half that
does not schedule.

**G23 — partially.** PtMP-only firmware strings (`POLL-ENABLE`, `LASTTXPEND`, `NO-TX-DETECT`,
`CONG-DROP`, `NONPAUSE_TID`, `TX ABORT`) read as a polling scheduler with per-station queue
accounting on the target. INFERRED; string archaeology is not disassembly.

**Fleet note for the operator:** the LiteBeam 5AC LR on 8.7.11 runs *different, larger* radio
firmware than the five units on 8.7.22. Any A/B measurement spanning those two is not
comparing like with like.

## Addendum 2026-08-08 (final): G10 closed, and the project's premise was backwards

Read-only `iwpriv` enumeration on the live LiteAP GPS (getters only; no `set` issued on
production) found **134 private ioctls on the radio and ~90 on the VAP**.

The vendor driver DECLARES a large ioctl surface (A-MPDU length/subframe count, rc_mode,
VHT MCS map, RTS/CTS, Dynamic ACK, distance, per-AC EDCA, LDPC, SW retry, PER telemetry,
setHALparam). **An earlier version of this addendum claimed that meant airOS gives more
control than ath10k. Lab testing disproved it the same day** — see the CORRECTION section of
`knowledge/AIROS_CONTROL_SURFACE.md`.

Four experiments on a clientless lab LiteAP AC (LAP-120, v8.5.12) changed **nothing**:
`iwpriv distance` and `iwpriv enablertscts` both returned rc=0 and left the value untouched;
editing `/tmp/system.cfg` and applying via `ubntconf -c` and then `rc.softrestart` changed the
config file but not the radio. **The setters accept writes and discard them.**

The reachable airOS surface is the `radio.*` keys in system.cfg: polling, ackless
(`pollingnoack`), airMAX priority (`pollingpri`), ACK distance/timeout, channel width, TX
power. **Aggregation and rate control are absent from it entirely**, so the PNOFA candidate is
blocked on BOTH stacks — a materially worse position than first reported.

**RESOLVED same day — airOS IS controllable.** `cfgmtd -w -p /etc/` + reboot changed
`radio.1.chanbw` 40→20 and the driver followed (`get_chanbw=20`), then reverted cleanly to 40.
The config path works; iwpriv is simply not it.

Consequences: every `radio.*` key is a testable lever, including the airMAX polling knobs
(`polling`, `pollingpri`, `pollingnoack`) and ACK timing — none of which have ever been tuned
on this network. But a change costs a **reboot**, so airOS supports **slow-loop optimisation
only** (minutes-to-hours), never reactive per-frame control. That matches the timescale the
research independently concluded was realistic. Aggregation and rate control remain absent
from the config surface, so PNOFA stays blocked on both stacks.

**G10 answered YES:** `/bin/ubntspecd` is already running on the production AP. Spectrum
telemetry does not require leaving airOS.

Live production config worth noting: **RTS/CTS is off** on a sector with known hidden nodes,
and **every rate-control knob is at default** — the supervisory rate-control idea has never
been tried here.

Consequence: `knowledge/QCA988X_CONTROL_BOUNDARY.md` has been scope-warned as **ath10k-only**.
The airOS-first architecture is no longer merely the safer choice; on current evidence it is
the technically better one. The main thing OpenWrt still offers that airOS does not is modern
queue management (CAKE/FQ-CoDel/AQL), which can be applied at the POP instead.

**The binding constraint is now a lab unit** (G25). Every remaining high-value experiment
needs one, and none of them should run on production.

## Addendum 2026-08-08 (final): the airMAX scheduler is reachable

Scanning the airOS binaries found **62 `radio.*` config keys that `ubntbox` reads but which
appear in neither the running config nor the web UI** — among them the fixed-frame scheduler's
parameters (`polling_ff_dur`, `polling_ff_dl_ratio`, `polling_ff_cbp_slots`, `polling_ff_timing`,
`polling_ff_sta_rx_rssi_th`, `polling_daprot`) plus aggregation (`ampdu.frames`, `ampdu.status`,
`amsdu`) and rate control (`rc_mode`, `rate.mcs`) — the very things earlier addenda declared
unreachable. `radio.1.web_exclude` is a real UI-hiding mechanism, consistent with these being
deliberately unexposed.

**PROVEN on the lab unit:** appending `polling_ff_flex=0`, `polling_ff_dur=8000`,
`polling_ff_dl_ratio=75`, persisting with `cfgmtd -w` and rebooting flipped the proprietary
module's own printk from `Fixed frame mode disabled` to `Fixed frame mode enabled`. Removing
them reverted it. **airMAX's fixed-frame scheduler parameters are settable.**

This is the capability the whole project was looking for, and it arrived from a question the
operator asked ("you're only modifying config?") rather than from any research report.

**Not established:** that any value improves performance. Enabling fixed-frame on a clientless
bench AP proves the control path, nothing more. Benefit measurement needs a second radio.

Lab unit verified restored to baseline: no `polling_ff` keys, chanbw 40, 802.11ac, 0 stations.

## Addendum 2026-08-08 (next session): FMX-0002 install/recovery METHOD established

Resolved blocker A (how OpenWrt gets onto the LAP-120 and how to recover it). Read the
`liteap_ac` OpenWrt device page + Ubiquiti common-procedures page through a browser, then
cross-checked every claim against artifacts pulled **read-only** from the live lab unit
(192.168.1.20) via `inventory/board_probe/preflash_probe.py` — the u-boot (`mtd0`) and
`/bin/ubntbox`. Nothing was written to the unit; it is still at airOS 8.5.12 baseline, 0 clients.

**Findings (see D-0006, `docs/EXPERIMENTS.md`, `safety/recovery/FMX-0002_recovery_runbook.md`):**
- **Recovery = bootloader `urescue` TFTP server — CONFIRMED present** in the pulled u-boot
  1.1.4-s1100 (device becomes TFTP server at 192.168.1.20; host pushes at 192.168.1.254). It is
  in the bootloader, so it survives a failed OS flash. Host push tool: `safety/recovery/urescue_push.py`.
- **Install = Route C, urescue-only** (corrected same day — see D-0007; the first version of this
  addendum said dd-unlock/Route A, which is **withdrawn** because it writes `u-boot` and this unit
  has no serial and no case access, i.e. no fallback). Push the OpenWrt **factory** image through
  the same urescue TFTP server used for recovery: never touches u-boot, and install/rollback
  become one operation with two different images.
- The three published `ubntbox` sed-patch patterns are **absent** from this unit's 8.5.12
  `ubntbox` (verified against the pulled binary), so the patched-fwupdate route (Route B) is a
  fallback needing fresh disassembly. Route C bypasses `fwupdate` entirely.
- **24.10.4 clears** the 24.10<.3 read-only-flash bug (Linux 6.6.110).
- Bootloader recognises `OPEN` magic (INFERRED-strong from its string table) → possible
  urescue-only install; to be confirmed on serial during the recovery dry-run.

## Addendum 2026-08-08 (later): FMX-0002 RUN — three Grade-A results, unit unharmed

Ran FMX-0002 on the lab LAP-120 with the operator power-cycling. **No flash occurred and the unit
is intact on airOS 8.5.12.** Full result table in `docs/EXPERIMENTS.md`; decision in **D-0008**.

1. **urescue entry is achievable blind** (no serial, case never opened) — **PROVEN**, on the 4th
   attempt. The three failures were *power never actually dropping*: on a PoE radio, pulling the
   injector→PC cable drops the link but leaves the radio energised (signature: a ~2 s outage
   instead of a 40–60 s reboot). Cut the injector→radio side or the injector's mains.
2. **urescue validates in RAM before touching flash** — **PROVEN**, reproduced twice. A refused
   image costs nothing.
3. **urescue REFUSES the OpenWrt factory image** — **REFUTED** the prior inference. The bootloader
   itself said so: `TFTP ERROR code=2 'Firmware check failed'` on the final block. This unit runs
   U-Boot 1.1.4-**s1100** (Sep 2018), which enforces RSA signature checking on the urescue path.
   Containing the `OPEN` magic string ≠ accepting an `OPEN` image. **Scope: the bootloader build,
   not the model, decides — do not generalise to other fleet units.**

**Consequence.** Route C dead; Route A withdrawn (writes u-boot). **Route B is the only compliant
path left**: derive the 8.5.12 `ubntbox` patch offset by disassembling the `EVP_VerifyFinal`
caller in the already-pulled binary, then install from inside airOS. urescue keeps its real job —
proven recovery for signed vendor images.

**Untested assumption to settle before committing to Route B:** it assumes this bootloader will
*boot* an unsigned kernel even though it will not *accept* one via urescue. If that is wrong, the
unit ends up non-booting and must be restored via urescue with stock airOS (recoverable, but a
wasted cycle). Worth checking against the OpenWrt device page's own boot logs first.

**Standing hardware request unchanged:** a second radio for FMX-0003 onward.

## Addendum 2026-08-09: FMX-0002 CLOSED — install attempted, failed to boot, unit recovered

Ran the documented dd-unlock install end to end, then recovered from its failure. **The lab unit
is back at its exact baseline** (`WA.ar934x.v8.5.12.40181.190213.1104`, airOS kernel, sysid
0xe8e5, 0 stations, chanbw 40, no `polling_ff`, stock flash map; u-boot and EEPROM never written).

- **The install mechanically worked.** Flash unlocked via the stock signed image, aligned writes
  landed, and `MIPS OpenWrt Linux-6.6.110` was verified in `mtd2` off the char device.
- **It did not boot.** Unit unreachable on every address. Leading hypothesis (UNTESTED): airOS's
  u-boot passes `1024k(kernel)+14720k(rootfs)` while OpenWrt expects one `15744k(firmware)`
  region, so the kernel cannot find its rootfs. Fixing that means writing `u-boot-env` — protected,
  and not to be done without an explicit operator decision.
- **Recovery proven on a genuinely dead unit**, which is the only version of that test worth
  anything. urescue accepted the signed vendor image (17,069/17,069 blocks) having refused the
  OpenWrt one — the predicted asymmetry, reproduced.

**Consequence for how we work:** flashing blind is now the bottleneck, not safety. Recovery is
cheap and proven; *diagnosis* is not, because there is no console. Two sane next moves — get
serial on the lab unit, or run the parallel track (FMX-0006, CAKE/FQ-CoDel at the POP) which needs
no flashing at all. Continuing to guess at boot failures without console output is the worst of
the three.

## Addendum 2026-08-10: OpenWrt 24.10.4 IS RUNNING ON THE LAB LAP-120 — Stage 2 unblocked

Retried the install after reading the primary sources properly (support commit, the v24.10.4
device tree, `common-ubnt.mk`, and the originating PR thread the wiki paraphrases). **It booted.**
LuCI is served on the OpenWrt default LAN address; SSH/HTTP/HTTPS all up; the radio's own MAC
answers there.

**What changed versus the failed attempt — two things, both from the guide rather than from me:**
1. **Let `fwupdate` reach the ROOTFS partition before interrupting**, as the guide says. Stopping
   at the kernel partition (what I did the first time) leaves the second partition outside the
   updater's write path. Since the OpenWrt kernel is 2.6 MB it *overruns* the 1 MiB kernel
   partition by ~1.5 MiB, so a kernel truncated at the boundary results — valid header, failed
   `bootm` CRC, silent device.
2. **Verify the WHOLE image read back from flash across the partition boundary**, not a header
   field. This caught a genuinely incomplete write (the trailing erase block had not committed)
   and correctly refused to reboot. A `sync` plus re-write fixed it and it then verified clean —
   note an immediate char-device readback can race the mtdblock cache, so re-check before
   concluding a write failed.

**Sources that settled it** (all read *before* acting, which was the operator's core correction):
upstream `Build/mkubntimage-split` confirms the 1024k split is exactly right; the DTS uses
`fixed-partitions` so the kernel ignores the bootloader's mtdparts; `bootcmd` is a plain `bootm`
with no signature gate; and the method's originator used the **same** airOS version already
installed, not "the latest" as the wiki paraphrase suggests.

**Now unblocked:** FMX-0007…0010. FMX-0010 (spectral FFT) and part of FMX-0009 (does the driver
accept/report rate masks?) are measurable on the AP alone — **no second radio required**. FMX-0007
and FMX-0008 still need a link partner, so the second-radio request stands and is now the single
binding constraint on the highest-value experiment in the project (AQL/TXQ on vs off).

**Note for future flashes:** once the updater reaches rootfs the vendor OS is unbootable, so the
procedure is committed from that point; bootloader recovery is the only way back — and it is
proven.

## Addendum 2026-09-20: research wave 2 (+2b) — the project's method is reshaped, inside the constitution

Two ChatGPT deep-research passes were run under `prompt.md` and both registered in
`research/intake/manifest.yaml` (`chatgpt-d3f52524`, and the operator's follow-up share
`6ab032a5`). **Unlike August, the citations resolve AND match on independent spot-check.**

**Wave 2 (source-level):** spectral is a build option we never enabled (`CONFIG_RELAY` is off in
stock 24.10 → reflash via routine `sysupgrade`, FMX-0011); `set_rates` is bcast/mcast only;
`set_rate_override` is Wave-2-only; `ratemask-CT` is the real supervisory hook. Details:
`QCA988X_CONTROL_BOUNDARY.md` §4.

**Wave 2b (literature + method), operator-driven:** a targeted real-hardware search found what the
general pass missed. Catalogued with tiers and verification status in
`knowledge/REAL_HARDWARE_LITERATURE.md`. Three corrections to our own record:
1. **IteRate is real** (arXiv:2605.02542, MIT, May 2026). The August citation audit rejected a
   *broken link* in the google run, not the paper. Its autonomous loop on 58 real radios is the
   closest published system to AGENTS.md §9's "automated experiment loop".
2. **"No strong QCA988x spectral literature" is REFUTED** — ComMag 2024 (peer-reviewed) and a
   522-million-observation 2026 dataset, both QCA9880 + ath10k. FMX-0010 gets an external
   validation target.
3. **Closed firmware is not a wall** — PNOFA beat Qualcomm's own aggregation on a closed Wave-2 part
   with an outer-loop controller (abstract verified in-browser 2026-09-20: user-space process on
   IPQ4019, +17% UDP / +13% TCP, Computer Communications 180).

**Decision D-0009:** Stage 3 runs as an autonomous research loop — immutable bench, mutable policy,
A/B/A/B blocking, hard validity gates, lexicographic objective — with a deliberately narrow first
knob set and radio-firmware work **deferred until a measured firmware-owned ceiling** is hit.
Campaign order C1–C8 and the INFERRED success thresholds are in `EXPERIMENTS.md`.

**What is unchanged:** the binding hardware constraint is still the **second radio** — C2 onward
need a link. C1 (spectral reproduction) needs only the AP plus the FMX-0011 rebuild.

## Addendum 2026-09-26: Testbed scaling (2 APs + 20 CPEs), unattended recovery, and research tooling

1. **Testbed RF Architecture Defined (Decision D-0010)**:
   - Evaluated warehouse vs cabled matrix vs multi-room setup.
   - Refuted the warehouse proposal: metal reflection multipath (Rayleigh fading) distorts outdoor LOS channels and prevents genuine hidden-node isolation.
   - Adopted a two-tier strategy: Tier 1 benchtop cabled RF attenuation matrix (SMA cables + 30-40 dB attenuators + Wilkinson power dividers) for deterministic algorithm/aggregation sweeps; Tier 2 multi-room distributed layout (feedhorns only, no metal dishes, minimum TX power -4 dBm to 0 dBm) for spatial and hidden-node evaluations.
   - Complete technical specification written in `docs/TESTBED_ENVIRONMENT_GUIDE.md`.

2. **Unattended Bootloader Recovery (`urescue`) Solved**:
   - Analyzed extracted U-Boot 1.1.4-s1100 binary (`lab-lap120-mtd0-u-boot-*.bin`).
   - Hardware path: Ubiquiti remote reset uses DC voltage (~15–24V) injected on Ethernet data transformer center taps. Inside the radio, a Zener + transistor circuit shorts the SoC reset GPIO low. Automated by wiring a relay across the tactile switch of a PoE injector to hold reset for 17s during power-up.
   - Software path: For responsive units, `fw_setenv bootcmd "urescue"` triggers direct boot into the TFTP recovery server without hardware button interaction.

3. **Research Tooling Synchronized**:
   - `ScholarEngine` located in `wezbridge/scholar`, verified operational via CLI and MCP for automated arXiv search and Jev semantic gating.
   - `nlm` CLI authenticated with profile `default: ggorbalan@gmail.com` via local Chrome DevTools Protocol; queried project notebook `ebf66972-afc2-4173-95cf-bc5ff07ceb03` ("futuraMAX").
   - Science skills `http_client.py` patched for Windows cross-platform compatibility.

## Addendum 2026-09-26 (continued): Deep Research Synthesis, Knowledge Hub, and Technical Breakthroughs

1. **Literature Base Expanded in NotebookLM**:
   - Ingested three landmark academic preprints into project notebook `ebf66972-afc2-4173-95cf-bc5ff07ceb03`:
     - `[1703.00064]` *Ending the Anomaly: Achieving Low Latency and Airtime Fairness in WiFi* (Høiland-Jørgensen, Kazior, Täht, Brunstrom).
     - `[2101.07562]` *Modelling Downlink Packet Aggregation in Paced 802.11ac WLANs* (Gringoli, Leith).
     - `[1803.10170]` *A New Aggregation based Scheduling method for rapidly changing IEEE 802.11ac Wireless channels*.

2. **Candela Technologies (`ath10k-ct`) Internals Verified**:
   - **The 30-Retry Save**: Upstream Qualcomm firmware enforces 30 retries (`0x1e`) per frame, which devastates outdoor PtMP sectors during CPE signal fades. Candela Technologies dropped this to 4 retries (0 non-agg, 4 agg), preventing sector stall.
   - **Initial Rate Fix**: CT lowered initial association rate from MCS5 down to MCS0/MCS3, preventing DHCP timeout drops on distant CPEs.
   - **Memory Stability**: Confirmed `kmod-ath10k-ct-smallbuffers` is mandatory on 64 MB / 128 MB MIPS 74Kc boards to prevent kernel OOM panics under multi-client traffic.

3. **The `last_tx_bitrate` Airtime Cliff Identified**:
   - Because QCA9880 (Wave 1) lacks `WMI_SERVICE_REPORT_AIRTIME` (Wave 2 only), Linux mac80211 calculates airtime using host estimation.
   - `last_tx_bitrate` is populated only via `HTT_T2H_MSG_TYPE_PEER_STATS`. If peer stats drop, mac80211 assumes 6 Mbps across all stations, converting airtime fairness into degraded packet fairness.

4. **CoTSQ & Paced Aggregation Settled**:
   - Proved that standard Linux TSQ (1 ms / 2 packets) starves 802.11ac aggregation engines.
   - Sizing socket queues to 6 ms of airtime (Controlled TSQ) enables full 32–64 frame A-MPDUs, unlocking up to an order-of-magnitude goodput improvement on clean channels while keeping loaded latency under 40 ms.

5. **Knowledge Hub Established**:
   - Created comprehensive public knowledge documents:
     - `docs/COMMUNITY_CALL_FOR_COLLABORATION.md`
     - `knowledge/ATH10K_CT_FIRMWARE_DEEP_DIVE.md`
     - `knowledge/PACED_AGGREGATION_AND_COTSQ.md`
     - `knowledge/PTMP_OUTDOOR_TDMA_VS_CSMA.md`
     - `knowledge/AUTONOMOUS_WIRELESS_RESEARCH_ENGINE.md`
     - `knowledge/SPECTRAL_AND_CSI_ANALYSIS.md`
   - Synchronized `docs/DOCS-MAP.md` and `README.md`.


## Addendum 2026-09-26 (Claude pane): FMX-0011 built, exit checks PASS, image not yet flashed

1. **FMX-0011 delivered as an artifact, not yet on the radio.** OpenWrt `v24.10.4` (r28959, same
   revision as the stock image on the LiteAP) rebuilt in WSL with `PACKAGE_ATH_DEBUG`,
   `PACKAGE_ATH_SPECTRAL` (→ kernel `CONFIG_RELAY=y`), `MAC80211_DEBUGFS`, `ATH_DFS`, plus bench
   tools (iperf3, tcpdump-mini, iw-full, ethtool). Four profiles in one multi-profile build:
   `ubnt_lap-120`, `ubnt_litebeam-ac-gen2`, `ubnt_nanostation-ac`, `ubnt_nanostation-ac-loco`.
   Exit checks (`tools/openwrt-build/exit-checks.sh`) all PASS: `ath10k_core.ko` defines
   `ath10k_spectral_process_fft` and imports `relay_open`; CT firmware stays FW022; Linux 6.6.110.
   Artifacts + sha256sums + dot.config + build log: `firmware/openwrt/futuramax-r28959-spectral/`.
2. **Build host caveat (D-0011 candidate).** This PC's WSL (2.7.14, kernel 6.18.33.2,
   `autoMemoryReclaim=gradual`) produced one kernel mmap deadlock and three unrelated, non-reproducible
   compiler crashes during the build. The final image came from a clean single pass, but treat it as
   **PROVISIONAL**: validate on the lab LiteAP (boot, radio up, `spectral_scan_ctl` present) or rebuild
   on a healthy Linux host before it becomes the research baseline. Details in `tools/openwrt-build/MANIFEST.md`.
3. **Two conflicts found in the 2026-09-26 Antigravity-pane docs, not yet resolved (operator call):**
   - `docs/TESTBED_ENVIRONMENT_GUIDE.md` §6.2 Option C and D-0010 item 3 prescribe
     `fw_setenv bootcmd "urescue"`, i.e. a write to mtd1 (u-boot-env). **AGENTS.md §4 forbids this**;
     README §8 written the same day forbids it too. The compliant unattended path is the PoE-injector
     remote-reset relay (§6.1).
   - The testbed names **LAP-GPS** as both APs. **OpenWrt 24.10.4 has no LAP-GPS profile** (only
     `ubnt_lap-120`, `ubnt_rocket-5ac-lite`, `ubnt_bullet-ac` among airMAX AC APs). Either the APs are
     LAP-120s or a LAP-GPS port (DTS + GPS UART) is a new task. Also README §6 (rooftop Tier 2) and
     the guide (multi-room Tier 2) disagree.
4. **Next actions:** (a) operator powers the LiteAP (192.168.1.1) → flash
   `openwrt-ath79-generic-ubnt_lap-120-squashfs-sysupgrade.bin` via `sysupgrade`, verify
   `/sys/kernel/debug/ieee80211/phy0/ath10k/spectral_*`, reboot-persistence → FMX-0010/C1 can start;
   (b) decide the build-host question (fix WSL config, or move builds to a Linux host);
   (c) resolve the two doc conflicts above.

## Addendum 2026-09-26: Multi-LLM Frontier Debate Executed & Synthesized (Decision D-0011)

1. **3-Way Frontier AI Debate Completed**:
   - Orchestrated via `skills/debate/tools/runner.py` across 3 complete rounds plus authoritative synthesis.
   - Models utilized: **Claude Fable 5.1** (`claude-fable-5.1`), **OpenAI Codex GPT-6 Astra** (`gpt-6-astra`), and **Google Gemini 3.8 Flash** (`gemini-3.8-flash`).
   - Artifacts generated: `debates/001-openmax-qca9880-ptmp-optimizat/` (`transcript.md`, `synthesis.md`, `state.json`, and per-round markdown files).
2. **Key Architectural Breakthroughs & Consensus**:
   - **CPU Offload Bound**: Unanimous proof that the AR9342 MIPS 74Kc CPU cannot run CAKE shaping at line rate. Downlink CAKE is strictly offloaded to an upstream x86/ARM gateway. The AP runs native `ath10k` AQL and driver-level `fq_codel`.
   - **Lightweight CPE Pacing**: OpenWrt CPEs run lightweight `tc-tbf` egress rate-limiting paired with hardware-assisted RTS/CTS thresholds to protect against hidden-node collisions without CPU starvation.
   - **Soft-Poll Fallacy Discarded**: PS-Poll / U-APSD pseudo-TDMA schemes were tested and unanimously rejected due to station firmware latency variance and framing overhead.
   - **Decisive Stress Test**: Defined 20-CPE saturated reverse-mode (`iperf3` uplink + `irtt` 20 pps) under hidden nodes as the make-or-break go/no-go gate for openMAX CSMA. Threshold: p99 loaded RTT < 150 ms and aggregate goodput within 25% of airOS TDMA.
   - **RF Reality Check**: Coordinates indicate ~21 m between buildings, not 100 m; two APs at 21 m form a single RF domain. Orthogonal channels (UNII-1 and UNII-3) and manufactured hidden nodes (attenuators/shielding) are mandatory for valid experimentation.

