# Custom PtMP MAC — go / no-go

Summary: RETRACTED AND REFRAMED 2026-08-08. An earlier version of this file declared NO-GO.
It answered the wrong question and pre-empted the Stage 4 gate that AGENTS.md defines.
Keywords: custom MAC, custom firmware, Stage 4 gate, OpenWrt, raw-mode, retraction, premise.
Read when: anyone cites a "NO-GO" for FuturaMAX. Current verdict: **UNKNOWN — as the
constitution requires, and as it must remain until the eight Stage 4 criteria are measured.**
Status: CURRENT (2026-08-08).

## Retraction

An earlier version of this file said:

> **NO-GO for replicating airMAX on stock firmware — high confidence, Grade A.**

That conclusion was defensible for the question it asked, and the question was wrong.

**The question it asked:** can we reproduce airMAX-class scheduling *while running Ubiquiti's
stock firmware*?

**The project's actual premise** (`AGENTS.md`): **build a custom firmware/software stack for
this hardware.**

Those are different questions with different answers. Discovering that Ubiquiti's scheduler
lives inside their proprietary radio firmware does **not** bound what a custom firmware can
do — it describes what *their* firmware does. Concluding "blocked" from it is like concluding
you cannot write an operating system because Windows is closed source.

Worse, it pre-empted the process. AGENTS.md §8 defines a **Stage 4 feasibility gate** with
eight specific criteria that must be *measured* before this call is made. None has been
measured. Declaring a verdict from firmware string analysis inverted the methodology the
project exists to follow.

## Cambium Elevate — CLOSED, and it was never the point

**Resolved by the operator 2026-08-08: Elevate covered M-series (802.11n) only, never AC.**
Dropped as a line of enquiry.

More importantly, the operator's follow-up dissolves the question entirely: *"if we have
openwrt to start with, why would we care about cambium"*. Correct. Elevate was only ever an
**existence-proof argument** — evidence that a third party *can* run a non-vendor stack on
Ubiquiti radios. That argument is redundant, because **OpenWrt already runs on our exact
hardware**, with official profiles for every target device. We do not need a precedent for
something we can boot today.

Recording this because it was my error twice over: I raised Elevate as "the highest-value
open research question" when the answer changes nothing. A competitor's proprietary firmware
tells us nothing actionable that the open platform we already have does not.

## What the firmware analysis actually established

The work in `knowledge/RADIO_FIRMWARE_ANALYSIS.md` remains valid. Restated against the real
goal, it says:

| Finding | What it means for a CUSTOM firmware |
|---|---|
| Ubiquiti ships custom QCA988x radio firmware with `ubnt-poll` code | Their scheduling is partly target-side. A custom host stack does **not** inherit it. |
| `ubnt_poll_host.ko` is control-plane only — no scheduling primitives | The host half of airMAX is small and replaceable. The hard part is target-side. |
| airOS runs `ol_ath`, not ath10k | OpenWrt+ath10k is a *different stack*, not a crippled airOS. Its limits are ath10k's, not the silicon's. |
| Radio firmware frozen since ~2017 | Confirms Ubiquiti abandoned optimisation — the project's motivating premise. |
| UBNT container format parsed; flash map and protected partitions known | **Direct groundwork for building and safely flashing our own image.** |

That last row is the point. Everything learned about their image format, partitioning and
recovery path is exactly what a custom-firmware effort needs.

## The real gate (AGENTS.md §8, Stage 4) — all UNMEASURED

Before writing a custom MAC, prove on the exact hardware:

1. precise TX completion visibility — **UNMEASURED**
2. bounded lower-layer queue ownership — **UNMEASURED**
3. bounded TX release timing — **UNMEASURED**
4. AP/CPE clock synchronization — **UNMEASURED**
5. controllable ACK/retry interaction — **UNMEASURED**
6. management/beacon survival — **UNMEASURED**
7. safe missed-slot recovery — **UNMEASURED**
8. usable GPS/timing access if required — **UNMEASURED**

Every one requires a lab unit running **OpenWrt** — not stock airOS. All of this session's
control-boundary probing was done on airOS, which is the wrong stack to evaluate for this
question. That is a scope error, not just an incomplete measurement.

**Verdict: UNKNOWN.** It stays UNKNOWN until Stage 2 (OpenWrt observability lab) is standing
and the eight criteria are measured. AGENTS.md is explicit that this file must not resolve
before then, and the earlier version violated that.

## What legitimately narrows the design space

These are real constraints on *how* a custom firmware would work — not arguments against one:

- `raw-mode` is advertised by stock ath10k firmware on this chip and is unexplored. It is the
  most direct lever toward host MAC authority and should be characterised early (G24).
- QCA988x cannot report actual TX airtime (10.4-only service), so a custom scheduler must
  work from estimates or derive timing another way.
- The 64 MB / AR9342 host is small; a heavy scheduler must be efficient or partly offloaded.
- Any custom MAC needs **both** ends — AP and CPE — which the project already assumes.

## Correct next steps

1. **Stand up Stage 2**: reproducible OpenWrt build for AR9342 + QCA988x, on a lab unit, with
   proven recovery. This is the vehicle for a custom firmware and the only stack on which the
   Stage 4 gate can be evaluated.
2. **Then** measure the eight criteria and resolve this file.

Do not cite this document as a reason not to attempt FuturaMAX.
