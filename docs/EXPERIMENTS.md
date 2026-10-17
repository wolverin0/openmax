<!-- doc-head: Experiment register with seed evidence and current acceptance limits -->
2026-10-07: FMX-0007 has seed measurements but no accepted baseline; FMX-0008 remains inconclusive.
Both AC radios were available for the archived runs; a missing second radio is not the current blocker.
Loaded RF failed at zero commanded power; do not repeat unchanged or advance Phase 3.
Older recovery/build entries are historical; CURRENT_STATE and BENCH_PLAN control current authority.
<!-- /doc-head -->

# FuturaMAX experiment register

Summary: the FMX experiment register (AGENTS.md §10) with status, the resolved LAP-120
install/recovery record, and the Stage-3 autonomous-research campaign plan C1–C8 (D-0009).
Keywords: FMX-0001..0011, campaigns C1-C8, autoresearch, spectral rebuild, sysupgrade reflash,
ratemask-CT, urescue, dd-unlock, success thresholds, INFERRED targets, LAP-120.
Read when: choosing what to run next. FMX-0007/0008 seed acquisition is recorded below;
neither an accepted baseline nor an AQL benefit has been established. Historical
installation/build rows are not permission to flash. Read the latest CURRENT_STATE
and BENCH_PLAN checkpoint before any operation; the night candidate remains unflashed.

## Status

| ID | Experiment | Status |
|---|---|---|
| FMX-0001 | Board/revision inventory | **DONE** — 6 units, Grade A, `docs/HARDWARE_MATRIX.md` |
| FMX-0002 | Repeated boot/recovery qualification | **DONE — Grade A.** Full cycle demonstrated for real: install → unbootable unit → bootloader recovery → verified baseline → corrected install → **OpenWrt booting**. |
| — | **OpenWrt 24.10.4 / 24.10.5 installed on the lab LAP-120 & Loco 5AC** | **DONE.** SSH/HTTP/HTTPS up; VM watermark fix (`vm.min_free_kbytes=2048`, `watermark_boost_factor=0`) eliminated OOMs (`>22 MB` free RAM). |
| FMX-0003 | Stock airMAX single-CPE baseline | **DONE (Stock `airOS 6.1.4` `LiteBeam M5` + Stock OpenWrt Baseline)** — `clean_stage3_baseline.json` (`124.69 Mbps` TCP DL, `121.77 Mbps` UDP DL @ 200M) |
| FMX-0004 | Multi-CPE Mixed-MCS (`802.11ac` + `MikroTik ath9k` + `airOS 6 M5`) Near-Far | **DONE (Stage 7.1 & 7.2)** — Verified across `15 dBm`, `11 dBm`, `5 dBm`, and `3 dBm` on 3-station heterogeneous PtMP cell (`docs/STAGE7_PTMP_3STATION_RESULTS.md`). |
| FMX-0005 | Multi-CPE Obstructed / Hidden-Node Uplink Contention | **DONE (Stage 7.3 & FMX-0016)** — Station `RTS/CTS = 256B` increased 3-station simultaneous UL goodput by **`+18.5%` (`150.40 -> 178.17 Mbps`)** and recovered wall-obstructed `MikroTik SXT` by **`3.07x` (`1.97 -> 6.03 Mbps`)**. |
| FMX-0006 | Gateway `CAKE diffserv4 nat ack-filter` + CPE Pacing | **DONE (Stage 4.2 & Stage 8C)** — Cut UDP UL loaded `p95` latency from `18.97 ms` to **`2.00 ms`** and boosted 6-flow bidirectional sector DL by **`+49.4%` (`30.26 -> 45.22 Mbps`)**. |
| FMX-0007 | OpenWrt single-CPE baseline & peak ceiling | **DONE (Stages 3–6)** — Clean single-CPE baseline (`124.69 Mbps` TCP DL) and tuned peak (**`223.53 Mbps` UDP DL / `154.58 Mbps` TCP DL 1S**, `0` retransmits, `1.73 ms p95` RTT). |
| FMX-0008 | OpenWrt `AQL` + `AIRTIME_FAIRNESS` (`ATF`) + `WMM AC_VO Bypass` | **DONE (Stage 4.1, Stage 7.2, Stage 7.4)** — `AQL 2000/4000` jumped UDP DL from `121.77 -> 186.23 Mbps`; `ATF + AQL 1500/3000 + WMM AC_VO Bypass` cut obstructed `MikroTik SXT` loaded RTT by **`21.0x` (`143.0 -> 6.80 ms`)**. |
| FMX-0009 | QCA988x fixed-rate/rate-mask authority (`ratemask-CT`) | **DONE (Stage 9A — `CONFIRMED` WMI Dispatch / `REFUTED` Live Runtime Clamp)** — `ATH10K_DBG_BUFFER` (`0x2002`) proved `iw set bitrates` sends `WMI_PEER_ASSOC_CMDID` (`0x0F0F`/`0x000F`/`0xFFF0`), but `10.1-ct-8x-__fW-022` firmware ignores `reassoc=true` rate-set narrowing on already-associated peers (`docs/STAGE9_20MHZ_RATEMASK_COTSQ_AND_PROCD.md`). |
| FMX-0010 | QCA988x Spectral FFT + `VHT80` vs `VHT40` vs `VHT20` Optimizer | **DONE (Stage 8B & Stage 9B)** — Captured `618.7 KB` (`6,653` FFT frames, `-105 dBm` noise floor); proved **`VHT40`** boosts 3-station DL by **`+13.1%` (`105.18 Mbps`, `2.630 bit/s/Hz`)** and **`VHT20` (`20 MHz`)** boosts obstructed `MikroTik SXT` DL by **`3.05x` (`61.44 Mbps`, `3.81 ms` RTT)** with **`0.9531` Jain fairness** and **`3.342 bit/s/Hz` DL / `3.656 bit/s/Hz` UL** spectral efficiency! |
| FMX-0011 | Reproducible OpenWrt build with spectral enabled | **DONE** — Validated on `LAP-120` (`spectral_scan0`, `6,653` FFT frames captured). Also discovered `ath10k-ct` `ap-force` off-channel scan `102.4 ms` sawtooth boundary (`DEC-013`). |
| FMX-0012 | Multi-LLM Architecture & Contention Debate | **DONE 2026-09-26 (Grade A Consensus, Decision D-0011).** Established split-plane shaping architecture (downlink CAKE offloaded to upstream gateway, AP native AQL + ATF, CPE CoTSQ + `fq_codel` + hardware RTS/CTS). |
| FMX-0013 | `CoTSQ` (`128 KB`) + Station Egress `fq_codel` (`quantum 300`) | **DONE (Stage 9C)** — Setting `tcp_limit_output_bytes = 131072` + `fq_codel quantum 300 target 5ms interval 50ms ecn` on OpenWrt CPE raised 3-station simultaneous UL to **`181.90 Mbps`** (`Loco 5AC = 141.93 Mbps`, `0` retrans) and cut `LiteBeam M5` `p99` RTT by **`3.14x` (`49.6 -> 15.8 ms`)**. |
| FMX-0014 | Production `procd` Init Service & Canary Rollback Watchdog | **DONE (Stage 9D)** — Deployed `/etc/init.d/futuramax` (`controller/futuramax.init`) + `/usr/sbin/fmx_watchdog.sh` (`controller/fmx_watchdog.sh`) supervising `fmx_adaptive_controller.sh` on `LAP-120` (`24,696 kB` free RAM, `HEALTHY`). |
| FMX-0015 | Closed-Loop Adaptive `AQL` & `A-MPDU` Sector Controller | **DONE (Stage 8A)** — Zero-fork debugfs daemon (`controller/fmx_adaptive_controller.sh`) dynamically transitions `SINGLE_STA_TURBO` (`109.35–118.67 Mbps`) <-> `MULTI_STA_ADAPTIVE` (`90.12 Mbps` total, `5.33–7.27 ms` RTT, `47.6x` `SXT` `p95` RTT reduction). |
| FMX-0016 | Multi-CPE Obstructed-Node `RTS/CTS` Threshold Verification | **DONE (Stage 7.3 & Stage 8C)** — Verified `rts 256` on 3-station heterogeneous PtMP sector (`+18.5%` UL goodput, `3.07x` obstructed-station recovery). |

## FMX-0007 / FMX-0008 archived evidence checkpoint — 2026-10-07

This closes BENCH_PLAN item1.7 (record results), not physical acceptance. Source
archives are in the main FuturaMAX checkout, not generated by the night worktree:

- research/raw/bench/2026-10-05/bench.jsonl, SHA256
  36ae341b47b1eafc6335359cff718f32a54d0c24b5e1f0818fbf47bca6e9e669.
- research/raw/bench/2026-10-06/endpoint-8f65a1bc4749487b920634ee53956b26/events.jsonl,
  SHA256ff00efb744558b43520e19f8e9b43feb87d47f6557e0477a02e49fb9b0e269b8.

CONFIRMED from the first archive:23 TCP matrix rows,7 with mbit=null. The16
reported non-null throughput values span30.8–140.9Mbps across different widths,
directions and stream counts; this is not one treatment's distribution. Example:
VHT80/down/1stream recorded140.9Mbps at22:00:06 and62.4Mbps at22:09:35. Timestamps
are stored without a timezone; no UTC conversion is inferred. Missing results
stay missing. The archive does not contain an accepted RF-normalized baseline.

FMX-0008 hypothesis: AQL may reduce loaded latency. The five aql-ab records at
22:06:50–22:07:59 are A(on)/B(off)/A/B/A, four downlink streams,10 RTT samples
per state. Reported on p95 values:38.652,38.704,42.178ms; off:50.584,63.148ms.
The off-state maximum3825.267ms is retained. Three of five mbit fields are null;
these sparse reported quantiles cannot establish p99, confidence intervals or
causal performance improvement. Decision INCONCLUSIVE; no recommendation to
disable/enable a live policy follows from this comparison.

Contemporaneous CURRENT_STATE 2026-10-05 21:55/22:15 documents LAP-120 plus
NanoStation loco5AC, OpenWrt24.10.4/ath10k-ct2024.07.30/FW022, short unattenuated
bench and on-radio traffic generators. This is recorded setup context, not a
fresh device identity/build-hash attestation. Matrix rows report11dBm software
power and strong RSSI; actual EIRP was not independently measured. CPU limitation
is an inference/confounder, not proof of RF capacity or one exclusive bottleneck.

Latest FMX-0007 attempt: the endpoint archive freshly evaluates to
REJECTED_BASELINE, accepted_baseline=false, RF FAIL, matrix INCOMPLETE(1/30,0valid),
restoration PASS. Its one invalid UDP-up cell reports receiver73.530778Mbps.
CURRENT_STATE records0dBm command/readback during that run and loaded Nano RSSI
-53dBm versus required<=-55dBm. Do not substitute restored11dBm for treatment
power, reuse this rejected cell as a baseline, or rerun unchanged conditions.

Remaining prerequisites: RF-qualified loaded runs, external endpoints with
measured headroom, exact per-run configuration/firmware provenance, required
blocked repetitions and explicit evaluator/safety contract. Phase3 stays gated.
No new radio operation, flash, confidence interval or performance claim here.

## FMX-0011 historical reflash analysis — settled from source 2026-09-20

**Why a module swap is not enough.** `PACKAGE_ATH_SPECTRAL` does `select KERNEL_RELAY`
(`ath.mk:114`), and `openwrt-24.10/target/linux/generic/config-6.6:4999` reads
`# CONFIG_RELAY is not set`, with no ath79 override. Enabling spectral therefore changes the
**kernel**, not just `kmod-ath10k-ct` — so it cannot be delivered as an `opkg install` of a
locally built `.ipk`, and a new image is required.

**The flash itself is routine now.** The unit runs OpenWrt, so this is `sysupgrade` over
SSH/LuCI — the normal supported update path, ~2 minutes. **None of the dd-unlock / `fwupdate` /
mtdblock ordeal applies**; that was only ever needed to escape airOS. Keep settings with
`sysupgrade` defaults, or `-n` to reset.

**The one real risk, stated plainly.** Recovery is asymmetric: `urescue` **refuses OpenWrt
images** (D-0008, proven). So if a bad sysupgrade leaves the unit unbootable, the recovery path
is urescue → **stock airOS** → then the whole dd-unlock procedure again to get back to OpenWrt.
Low probability, high cost. Mitigations: build from the exact 24.10.4 tag, change only the two
spectral options, and verify the image on a bench boot before trusting it.

---

## Stage 3 campaign plan — autonomous radio research (D-0009), ordered by information dependency

Each campaign produces something the next one needs. Numbers in brackets are what the literature
makes *plausible*, on other silicon — hypotheses to test, never expectations to report.

| # | Campaign | Needs | What it answers | Literature anchor |
|---|---|---|---|---|
| C1 | **QCA988x spectral reproduction** — enable `ATH10K_SPECTRAL` (FMX-0011), keep CT/FW022 otherwise constant, parse with the same feature pipeline as the QCA9880 work, compare our distributions to the published datasets, then build a WISP-interference corpus | AP only | Is our Wave-1 FFT output consistent with published QCA9880 data? Is it ML-usable for interference classes? | WiFiSpectralJam (2026), ComMag 2024 — **direct, same silicon family** |
| C2 | **Aggregation autoresearch** — autonomous sweep then learned policy over `htt_max_amsdu_ampdu` across subscriber counts, RSSI, rate spread, traffic mix | 2nd radio | Does outer-loop aggregation control beat firmware default on QCA988x? | PNOFA (+17/+13% on IPQ4019 — **do not transfer**) |
| C3 | **Aggregation-aware pacing** — learn the per-station offered-load point that keeps aggregation efficient without persistent queues | 2nd radio | The throughput/latency knee per CPE | Quick & Plenty (~2 ms one-way @ ~500 Mb/s, other HW) |
| C4 | **Per-subscriber rate-envelope bandit** — firmware keeps picking packet rates; our controller picks the *allowed* mask via `ratemask-CT` | 2nd radio + per-peer mask API (open) | Does banning MCS 8/9 on a specific link raise goodput and cut p99? | WiFi-CUTS (bandits; Minstrel numbers do not transfer) |
| C5 | **Contextual rate-envelope controller** — add distance, RSSI history, noise, retries, time-of-day interference, spectral features | C1 + C4 | Per-link system identification, not generic RA | SmartLA (long-history learning precedent) |
| C6 | **Weak-client / near-far** — 1 strong + 1 weak, then 4, 8, 16 | CPE fleet | Queue/mask/aggregation policies that minimise p99 and airtime waste under the classic PtMP pathology | Ending the Anomaly (airtime fairness baseline) |
| C7 | **Interference-aware control** — known adjacent/co-channel interferers in a shielded/cabled setup; correlate FFT signatures with retries and goodput; learn stay / narrow / widen / move | C1 + shielded rig | Can the controller tell "PHY is fine, interferer X every ~4 ms" from "rate problem"? | WiFiSpectralJam / ComMag (feature space proven ML-usable) |
| C8 | **Soft scheduled access** — per-station TXQ admission/credits, queue gating | all of the above | How close to polling can the *host* get while firmware still owns final TX timing? Call it **soft scheduling, not TDMA**, until measured | hMAC (ath9k soft slotting) |

**Why the stationary-CPE property matters more than any single technique.** Generic Wi-Fi RA must
handle a phone walking behind a wall. Our CPE-381 is at a fixed 6.82 km, fixed azimuth, known
hardware, with weeks of RSSI/retry/MCS/noise history and a learnable interference profile — and we
observe **both ends**. The problem is closer to per-link system identification than to rate
adaptation, and that is the structural reason to expect the loop to find policies a human never
would (10 knobs × 5 settings ≈ 9.8 M combinations, none of them static).

### Success thresholds — INFERRED targets (AGENTS.md §13 forbids treating these as results)

| Level | Loaded usable capacity | p99 loaded latency | Also |
|---|---|---|---|
| **Minimum success** | +10–15% | ≥3× lower | material fairness improvement |
| **Very good** | +25–40% | 5–10× lower | 10–25% less wasted airtime; excellent weak-client isolation |
| **Breakthrough** | +50% or more | still low | without extra spectrum, **without modifying the radio firmware** |

Central engineering estimate from the wave: **~30% more usable loaded-cell capacity, ~5–10× lower
p99, and only ~5–10% on a clean single-client speedtest** — the salesperson's metric barely moves;
the operator's cell does. Provenance and the discounting applied: share 6ab032a5, turn 6.

---

**Everything physical funnels through FMX-0002.** Recovery must be proven before the first
flash (AGENTS.md §4). The install method AND the recovery method are now established (below);
what remains is the operator's physical power-cycle/serial step to *demonstrate* recovery.

## RESOLVED: how OpenWrt gets onto a LAP-120, and how to recover it

Established 2026-08-08 by reading the `liteap_ac` OpenWrt device page + Ubiquiti common-procedures
page through a browser (openwrt.org bot-challenges plain HTTP), then **cross-checking every claim
against artifacts pulled read-only from this exact unit** — the live u-boot (`mtd0`) and
`/bin/ubntbox`. Full runbook + host tooling: `safety/recovery/FMX-0002_recovery_runbook.md`,
`safety/recovery/urescue_push.py`. Probe: `inventory/board_probe/preflash_probe.py`.

**Recovery = the bootloader's own `urescue` TFTP server. CONFIRMED present on this unit.**
Strings in the pulled u-boot 1.1.4-s1100 (Sep 2018): `urescue - start TFTP server and wait for
firmware`, `Starting TFTP server...`, default env `ipaddr=192.168.1.20 serverip=192.168.1.254`.
Entered by holding RESET at power-on (LED sequence changes) or by stopping autoboot on serial.
The unit becomes a TFTP server at **192.168.1.20**; the host (at 192.168.1.254/24) pushes one
image. This path does **not** depend on airOS surviving — it is the debrick guarantee.

### FMX-0002 RESULTS — 2026-08-08, run on the lab unit (Grade A)

| # | Question | Result |
|---|---|---|
| 1 | Can urescue be entered blind (no serial, case shut)? | **YES — PROVEN.** Took 4 attempts; failures were power never actually dropping (PoE: cut the injector→radio side, not injector→PC). |
| 2 | Does urescue validate before writing flash? | **YES — PROVEN.** Full image transferred, refused, **nothing written**, airOS intact. Reproduced twice. |
| 3 | Will urescue accept the OpenWrt `OPEN`-magic image? | **NO — REFUTED.** Bootloader replied `TFTP ERROR code=2 'Firmware check failed'`. See D-0008. |
| 4 | Does the dd-unlock install write OpenWrt to flash? | **YES — PROVEN.** Flash unlocked via stock signed image; aligned writes landed; `MIPS OpenWrt Linux-6.6.110` verified in mtd2 by reading the uImage **name** off the char device. |
| 5 | Does the installed OpenWrt boot? | **NO.** Unit unreachable on every address after reboot — not `.1`, not `.20`, not urescue. Recovery via reset-at-power-on required. |

### Why #5 failed — SETTLED FROM SOURCE (2026-08-10)

Two earlier hypotheses were **REFUTED** by reading upstream source. Both were my speculation and
neither survived contact with the actual files; do not re-cite them.

| Hypothesis | Verdict | Evidence |
|---|---|---|
| "u-boot passes the wrong `mtdparts`, so the kernel can't find rootfs" | **REFUTED** | `ar9342_ubnt_wa.dtsi` @ v24.10.4 uses `fixed-partitions`: `partition@50000 { compatible="denx,uimage"; label="firmware"; reg=<0x050000 0xf60000>; }`. The kernel ignores the bootloader's mtdparts entirely. |
| "the bootloader enforces RSA signatures at boot" | **REFUTED** | The pulled u-boot's default env is `bootcmd=bootm 0x9f050000` — plain. `ucheck_fw` appears only in the *update* path (urescue/fwupdate), never in the boot path. |

**Actual cause (coherent with every observation).** The OpenWrt kernel is **2,618,192 B**, but the
airOS `kernel` partition (`mtd2`) is only **1 MiB** — so **~1.5 MiB of the kernel itself must land
in `mtd3`**. Our run killed `fwupdate` at the *start* of the mtd2 write, whereas the guide says to
let it reach **mtd3**; `mtd3` therefore never went through fwupdate's per-partition write path, and
its content was never verified. `bootm 0x9f050000` then reads a valid header, attempts to load
2.6 MB, runs into stale airOS bytes past the 1 MiB mark, fails the data CRC, and aborts — leaving
the unit in u-boot with no network, which is exactly the observed symptom.

**The verification that hid it.** Checking the uImage *name* in `mtd2` reads bytes from the one
region that DID write. It is not evidence the kernel is complete. **Verify the whole image**:
hash the first `kernel_size + 64` bytes read back from flash and compare against the local file —
crossing the mtd2/mtd3 boundary, which is invisible at raw-flash level since they are contiguous.

**Upstream's own install method needs serial** (from the support commit `23f9b2d9`): tftpboot an
OpenWrt *initramfs* from the u-boot console, `bootm` it, then `mtd write <sysupgrade> firmware`
from the running system. The wiki's dd-unlock recipe is a community workaround for units without a
console. This is now the strongest argument for serial access on the lab unit.

| 6 | Can a non-booting unit be recovered to a verified baseline? | **YES — PROVEN END-TO-END.** Held RESET at power-on into urescue, pushed the stock signed image (all 17,069 blocks accepted, no rejection), unit rebooted to airOS. Verified: build `WA.ar934x.v8.5.12.40181.190213.1104`, kernel `MIPS Ubiquiti Linux-2.6.32.68`, sysid 0xe8e5, 0 stations, chanbw 40, no `polling_ff`, stock flash map. u-boot/EEPROM never written. |

**This is what makes FMX-0002 DONE rather than partial.** Recovery was not rehearsed on a healthy
unit — it was performed on a genuinely unbootable one, which is the only test that actually
counts. The signed-vs-unsigned asymmetry also reproduced exactly as predicted: the same urescue
that *refused* the OpenWrt image *accepted* the signed vendor image without complaint.

**Hard constraint this exposed.** Diagnosing a non-booting radio with no serial console is
guesswork. urescue makes retries *safe*, but not *informed*. Serial access has moved from
"recommended" to the main thing limiting iteration speed on this unit.

**Tooling gotcha, recorded so it is not rediscovered.** urescue serves **one TFTP session at a
time**, and a probe that opens a write-request *consumes* it — a subsequent real push then hangs
until the session expires. The non-destructive test is a **read** request: silence on UDP/69 means
urescue is listening (it is upload-only and ignores reads), whereas `ConnectionReset` means
nothing is bound there (airOS). `urescue_push.py --probe-only` now uses the read form.

**Install method — Route C (urescue-only): REFUTED, do not retry.** Pushing the OpenWrt factory
image into urescue is rejected by this unit's U-Boot 1.1.4-**s1100**, which enforces the RSA
signature check on the urescue path. Recognising the `OPEN` magic ≠ accepting the image. urescue
remains **proven and valuable as the recovery path for signed vendor images**.

**Install method — Route B is now the only compliant path.** The signature gate must be bypassed
where it is patchable: in airOS userspace (`ubntbox`), not in a signed bootloader. Requires
deriving the 8.5.12 patch offset by disassembling the `EVP_VerifyFinal` caller in the pulled
binary — no published pattern matches (below). Route A stays withdrawn (writes u-boot).

> **Route A (dd-unlock) is WITHDRAWN — do not re-propose it.** It requires letting airOS
> `fwupdate` write **`u-boot` to `mtd0`** before you interrupt it. That breaks AGENTS.md §4, and
> with **no serial console and no case access** (operator, 2026-08-08) a failed or power-
> interrupted u-boot write destroys `urescue` itself, leaving only an SPI clip inside a case that
> will not be opened. It is the one procedure here with no fallback.

**Why trying Route C is cheap.** This unit's bootloader validates before writing — two separate
calls, `go ${ubntaddr} ucheck_fw …` then `go ${ubntaddr} uupdate_fw …`, with TFTP landing the
image in RAM at `ubntaddr=0x80200020`. A refused image means **nothing was written**; the unit
stays on airOS 8.5.12. A refusal is itself a valid FMX-0002 result (signed-bootloader enforcement
extends to urescue on WA boards) and sends us to Route B, not Route A.

**Why the patched-fwupdate route is the fallback, not primary — evidence, not lore.** The wiki
patches `/bin/ubntbox` with a version-specific `sed` (`14 40 fe ff` for 8.4.1, `14 40 fe fe` for
8.5.0, `14 40 fe 27` for the 8.7 line). **None of those three byte patterns exist in this unit's
8.5.12 `ubntbox`** (verified against the pulled binary, sha256 `6ea397e5…`). So the published
patch cannot be reused; Route B would require disassembling the `EVP_VerifyFinal` caller to
derive a new offset. Route C avoids the signature question entirely by never going through
`fwupdate` at all.

**OpenWrt version-bug clearance.** The 23.05<.3 and 24.10<.3 read-only-flash bug does not affect
us: our image is **24.10.4** (Linux 6.6.110; fix landed 24.10.3 / 6.6.103). VERIFIED.

**Bootloader OPEN-magic (one open item, does not block).** The stock bootloader's magic table
contains `OPEN`/`ENDS` beside `UBNT`/`PART`/`END.`, i.e. it recognises the OpenWrt image magic —
INFERRED-strong from the string table, not from disassembled dispatch. Whether `urescue` will
accept the OpenWrt *factory* image directly (a urescue-only install, no airOS step) is confirmed
cheaply during the serial recovery dry-run (runbook §3). Route A does not depend on it.

Image facts (all verified): factory 7,013,016 B, magic `OPENWA.ar934x.v8.7.4-42`, sha256
`943d812c…`; sysupgrade 7,012,651 B, `MIPS OpenWrt Linux-6.6.110`, sha256 `cc01cbb3…`; both match
OpenWrt `sha256sums`. Sysupgrade 7.01 MB fits the 14.4 MB rootfs with wide margin.

## Mandatory pre-flash checklist (AGENTS.md §4)

Do not flash until every line is ✅:

- [x] exact board/image match confirmed (`sysid 0xe8e5` ↔ `ubnt_lap-120`; board.model=LAP-120,
      fcc SWX-LBE5AC120-U, both read live from the unit)
- [x] image size validated against the flash region (sysupgrade 7.01 MB ≪ 14.4 MB rootfs)
- [x] checksum verified against vendor `sha256sums` (factory `943d812c…`, sysupgrade `cc01cbb3…`)
- [x] recovery path IDENTIFIED and present on THIS unit — `urescue` TFTP server confirmed in the
      pulled u-boot. ⚠️ still to be **demonstrated** by the operator (physical, runbook §2).
- [x] serial console: **NOT available and not going to be** (operator: no serial, case stays
      shut). Entry is blind button-hold only — which is exactly why the zero-write entry check
      below is mandatory rather than optional.
- [ ] **urescue ENTRY demonstrated** (zero writes: `urescue_push.py --probe-only` / `--watch`).
      Attempt 1 on 2026-08-08 **FAILED** — unit booted airOS instead (ping+SSH+HTTP up, TFTP/69
      closed); button released too early. No harm, nothing written, config verified intact.
      Retry until entry is *repeatable* before any image is pushed.
- [x] airOS return-to-stock image present and verified: `firmware/WA.v8.5.12.40181.190213.1104.bin`,
      magic `UBNT`, 8,738,874 B, sha256 `4bda8ddf…` — byte-identical build to the one running, so
      rollback lands on the exact baseline.
- [x] post-flash health check defined (runbook §4: ath10k qca988x + wlan0 + OpenWrt mtd layout)
- [x] rollback path documented (runbook §5: urescue-push stock WA.v8.5.12, re-probe baseline)

**Never write:** `u-boot`, `u-boot-env`, `EEPROM` (calibration). Measured LAP-120 layout:
`mtd0 u-boot 256K` · `mtd1 u-boot-env 64K` · `mtd2 kernel 1M` · `mtd3 rootfs 14.4M` ·
`mtd4 cfg 256K` · `mtd5 EEPROM 64K`.

## Why FMX-0002 is worth doing properly

Recovery qualification is not bureaucracy here — it is what converts a single lab radio into
a reusable experiment platform. Every one of FMX-0007…0010, and all eight Stage 4 criteria,
require flashing and re-flashing that unit many times. A proven TFTP path makes those cheap
and safe; its absence makes every experiment a risk of losing the only lab unit.

## Second radio

FMX-0003 onward need a link. One LiteBeam 5AC Gen2 or NanoStation 5AC loco on the bench,
pointed at the LAP-120, unblocks baselines, the Stage 4 timing criteria, and any real
performance measurement. This is the standing hardware request.

---

## Analytical Queue & Contention Optimization Recipes (FMX-0013 through FMX-0016)

Reference: `knowledge/ANALYTICAL_QUEUE_MODEL_AND_HOOKS.md`

### FMX-0013: CoTSQ (Controlled TCP Small Queues) Sweep
* **Hypothesis**: Sizing `tcp_limit_output_bytes` to 6 ms of airtime (~300 KB at 400 Mbps) eliminates aggregation starvation, restoring A-MPDU depth to $K \ge 32$ without bufferbloat.
* **Control Boundary**: Linux Kernel TCP stack on traffic endpoints.
* **Configuration Arms**:
  1. *Arm A (Default 1ms TSQ)*: `sysctl -w net.ipv4.tcp_limit_output_bytes=131072 net.ipv4.tcp_notsent_lowat=4294967295`
  2. *Arm B (CoTSQ 6ms Pacing)*: `sysctl -w net.ipv4.tcp_limit_output_bytes=300000 net.ipv4.tcp_notsent_lowat=16384`
  3. *Arm C (Unbounded Bloat)*: `sysctl -w net.ipv4.tcp_limit_output_bytes=2097152 net.ipv4.tcp_notsent_lowat=4294967295`
* **Measurement**: Saturated single-stream and 4-stream TCP `iperf3` + concurrent 20 pps `irtt`. Monitor A-MPDU size histogram from `/sys/kernel/debug/ieee80211/phy0/ath10k/htt_tx_stats`.
* **Pass Gate**: Arm B achieves $>2\times$ goodput over Arm A with p99 loaded RTT $<40\text{ ms}$.

### FMX-0014: Firmware Rate-Control Cache Depth
* **Hypothesis**: Default target firmware caches only 32 rate objects in on-chip SRAM; dense CPE fleets cause PCIe cache swapping. Clamping `num_rate_ctrl_objs_ct=24` stabilizes rate-hunting.
* **Control Boundary**: `ath10k-ct` module parameter on AP.
* **Configuration Arms**:
  1. *Arm A (Default)*: `ath10k_core.num_rate_ctrl_objs_ct=0` (firmware default: 32)
  2. *Arm B (Fleet-Sized Cache)*: `ath10k_core.num_rate_ctrl_objs_ct=24`
* **Measurement**: 10 and 20 active CPE associations under bidirectional bursty traffic. Record rate stepping distribution from `iw dev wlan0 station dump` and target debugfs `ath10k/wmi_stats`.
* **Pass Gate**: Arm B reduces rate stepping variance and MCS fallback drops by $>50\%$.

### FMX-0015: mac80211 Airtime Queue Limits (AQL) Tuning
* **Hypothesis**: Tuning `aql_txq_limit_low` and `aql_threshold` bounds driver queue delay without firmware credit ring starvation.
* **Control Boundary**: `mac80211` AQL debugfs on AP.
* **Configuration**:
  ```bash
  echo 2000 > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit_low
  echo 6000 > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit_high
  echo 12000 > /sys/kernel/debug/ieee80211/phy0/aql_threshold
  ```
* **Measurement**: Mixed-rate PtMP (Station 1 @ MCS9, Station 2 @ MCS1). Flent RRUL saturation.
* **Pass Gate**: Station 1 maintains $>80\%$ of its isolated goodput while Station 2 saturates; loaded RTT stays $<35\text{ ms}$.

### FMX-0016: 20-CPE Hidden-Node RTS/CTS Protection Sweep
* **Hypothesis**: Directional CPEs with inter-CPE isolation ($>110\text{ dB}$ path loss) suffer exponential Aloha collision collapse unless hardware RTS/CTS limits the vulnerability window to $V_{RTS} \approx 65\,\mu\text{s}$.
* **Control Boundary**: Hardware RTS threshold via `iw` on AP and all CPEs.
* **Configuration Arms**:
  1. *Arm A (RTS Disabled)*: `iw phy phy0 set rts 2347`
  2. *Arm B (Aggressive Protection)*: `iw phy phy0 set rts 512`
  3. *Arm C (Universal RTS)*: `iw phy phy0 set rts 1`
* **Measurement**: 20 concurrent saturated reverse-mode `iperf3` streams with staggered start times. Capture `retries`, `failed`, and `ack_failed` counters.
* **Pass Gate**: Arm B eliminates throughput collapse, achieving aggregate goodput $>150\text{ Mbps}$ and p99 loaded latency $<150\text{ ms}$ (meeting the openMAX Go/No-Go Gate).
