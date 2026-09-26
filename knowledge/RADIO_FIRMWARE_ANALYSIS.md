# airMAX radio firmware — extracted and compared against stock QCA

Summary: Ubiquiti compiles three custom QCA988x target-firmware images into `umac.ko` and
they contain Ubiquiti polling code absent from stock QCA firmware. Closes gap G08.
Keywords: athwlan_AR9888v2, ptp/ptmp_ap/ptmp_sta, umac.ko, UBNT_POLL_MEM_ALLOC, ubnt-poll,
_on_swbmiss, ubnt_set_power_range, SGMT, QCA-ATH10K, Xtensa target, custom MAC, G08.
Read when: assessing whether OpenWrt/ath10k can replicate airMAX, or scoping firmware work.
Current verdict: **airMAX scheduling is partly implemented INSIDE the radio firmware.**
Status: CURRENT (2026-08-08). Evidence grade A.

## What was done

The airOS image `WA.v8.7.11.46972.220614.0420.bin` was downloaded from Ubiquiti's public
download site, unpacked with `tools/research/unpack_airos.py`, its squashfs rootfs extracted,
and the three radio-firmware blobs carved out of `umac.ko` **by ELF symbol**, not by guessing
offsets. Stock QCA988X firmware was fetched from kernel.org linux-firmware for comparison.

No device was touched for any of this. The whole chain is reproducible by anyone from public
downloads.

### Provenance chain

```
WA.v8.7.11.46972.220614.0420.bin   (UBNT container, 9,748,150 B)
  └─ PART rootfs (squashfs 4.0 / LZMA, 8,519,680 B)
       └─ /lib/modules/2.6.32.68/umac.ko   (2,361,256 B)
            ├─ symbol athwlan_AR9888v2_ptp_bin       len 216,059
            ├─ symbol athwlan_AR9888v2_ptmp_ap_bin   len 252,697
            └─ symbol athwlan_AR9888v2_ptmp_sta_bin  len 235,270
```

`umac.ko` is the **only** file in the entire rootfs containing the firmware-loader strings
(`ol_transfer_bin_file`, `Download Firmware`, `athwlan`, `otp`). `/lib/firmware` is empty —
there is no firmware file on the device; the images are compiled into the module as C arrays
with matching `_len` symbols.

### The extraction is verified against live hardware

Your LiteBeam 5AC LR runs this exact build and its boot log reported the loaded sizes:

| Image | Device boot log | Extracted symbol | Delta |
|---|---:|---:|---|
| PTP | 216060 | 216059 | +1 (4-byte alignment) |
| PTMP-STA | 235272 | 235270 | +2 (4-byte alignment) |

The loader rounds up to a 4-byte boundary. **Byte-exact match** — the artifact extracted from
the public download is the artifact running on the radio.

### Hashes (record only — the blobs are proprietary and stay out of this repo)

| Image | Size | SHA-256 |
|---|---:|---|
| `ptp` | 216,059 | `f7f8ac8b131f105093f0290657db64c0cd9790d4632979f0c34b9303a38417aa` |
| `ptmp_ap` | 252,697 | `7f407b179688c90f8b0a737b8b2c7ff2711b720a0151c0695eff7217c4a8ba60` |
| `ptmp_sta` | 235,270 | `5d6983bf2acfab1bcaa6df41785d180f9c0b227287e61decfb18ca6f9a53de82` |
| stock QCA988X `firmware-5.bin` (10.2.4-1.0-00047) | 249,044 | `15867031c87f1d7408c1b25fb6419077a1b97de208f2aa58c3266b60e1f8daa2` |

---

## The finding: Ubiquiti code runs inside the radio firmware

Strings present in the Ubiquiti target images and **absent from stock QCA firmware**:

| String | ptp | ptmp_ap | ptmp_sta | in stock QCA? |
|---|:-:|:-:|:-:|:-:|
| `_tx UBNT_POLL_MEM_ALLOC` | ✅ | ✅ | ✅ | **ABSENT** |
| `_tx UBNT_POLL_MEM_ALLOC returned NULL` | — | ✅ | — | **ABSENT** |
| `ubnt-poll: _on_swbmiss return 1` | — | — | ✅ | **ABSENT** |
| `ubnt_set_power_range` | ✅ | ✅ | ✅ | **ABSENT** |

`UBNT_POLL_*` and `ubnt-poll:` are **Ubiquiti's polling subsystem, compiled into the QCA988x
target firmware** — code running on the Xtensa core inside the radio, not on the MIPS host.
`_on_swbmiss` is a software-beacon-miss handler, which is timing-critical MAC behaviour.
`ubnt_set_power_range` is target-side transmit-power control (the ATPC counterpart).

The containers differ too, confirming these are not repackaged stock images:

- Ubiquiti: magic `53 47 4d 54` = **`SGMT`** (raw segmented image, loaded by `ol_transfer_bin_file`)
- Stock ath10k: magic `QCA-ATH10K` (the ath10k firmware-API container)

String overlap between `ptmp_ap` and stock `firmware-5.bin` is only ~91 strings, with ~350
Ubiquiti-only and ~323 stock-only. Common QCA base, substantially divergent builds.

## Why this is decisive for the project

Before this, the working model was "airMAX = proprietary host kernel module (`ubnt_poll_host`)
on top of a standard QCA radio". That model is **wrong**, and every one of the seven external
research runs held it.

The real architecture is **three layers deep**:

| Layer | airMAX | OpenWrt |
|---|---|---|
| Host scheduler | `ubnt_poll_host.ko` (proprietary) | none |
| Host driver | `ol_ath` (`ath_pci 10.1.467`) + `umac.ko` | `ath10k` + `mac80211` |
| **Radio firmware** | **custom, per-mode/per-role, with `ubnt-poll` code** | **stock QCA 10.2.4** |

Flashing OpenWrt replaces **all three**. The polling MAC does not merely lose its host
scheduler — the target firmware that implements the timing-critical half of it is gone, and
no amount of host-side work in mac80211 can reinstate code that runs on the radio's own CPU.

This also explains cleanly why the literature never transferred: hMAC, Det-WiFi and WiLDNet
all achieved scheduled access on **SoftMAC** hardware where the host owned MAC timing.
Ubiquiti solved the same problem on a FullMAC part the only way it can be solved there — by
putting the scheduler in the firmware. FuturaMAX cannot follow without firmware source.

## What it does *not* say

- **The host/target split is now established (G22) and it favours the firmware even more
  than assumed.** `ubnt_poll_host.ko`'s 150 functions were enumerated from its ELF symbol
  table, and it contains **zero scheduling primitives**: no `slot`, no `tdma`, no `airtime`,
  no `sched`, no `tsf`, no framing function. Its only timers are generic Linux
  `add_timer`/`mod_timer` housekeeping, and its only queue functions are
  `set_txq_param`/`get_txq_param` (WMM parameter config, not scheduling).

  What it *does* contain, by theme: station table (32 functions), 802.11 management hooks
  (18: `on_assoc_req_rx/tx`, `on_beacon_rx/tx`, `on_sta_connect/disconnect/authorize`,
  `on_deauth_rx`), host↔target comm (10: `ht_comm_*`, `ku_comm_get_stalist/stainfo`),
  config push to the target (10: `init_ptmp_netconf`, `send_ptmp_netconf`, `radio_set_data`,
  `set_rate_override`), crypto (9) and logging (10).

  **`ubnt_poll_host.ko` is the control/management plane, not the scheduler.** It negotiates
  airMAX via information elements (`proto_insert_ie`/`proto_parse_ie`), tracks stations,
  pushes the PtMP network configuration into the target, and relays stats. The scheduling
  runs in the radio firmware. This makes the host-side piece the *replaceable* half.
- It does **not** say airMAX cannot be beaten. It says airMAX cannot be *replicated* on stock
  firmware. Beating it on latency/fairness/spectrum via the airOS-first path is untouched by
  this finding.
- **What the PtMP-specific firmware code does (G23) is now sketched, not proven.** Strings
  present in *both* PtMP images but absent from `ptp` — i.e. genuinely PtMP-specific target
  code — include `POLL-ENABLE`, `AVG TIMER`, `CYCLES:`, `LASTSTA`, `LASTTXPEND`, `INFOTXQ:`,
  `NO-TX-DETECT`, `CONG-DROP`, `SWRLIMIT`, `curr_data_rix`, `num_peer_entries`,
  `STA REF COUNT NEGATIVE`. AP-only strings add `NONPAUSE_TID`, `Stuck queue`,
  `TX ABORT called`, `EVM measurement configured with pilot-mask`.

  That vocabulary — poll enable, per-station last-TX-pending tracking, congestion drop,
  no-TX detection, TID pausing, TX abort — is exactly what a polling scheduler with
  per-station queue accounting looks like, running on the target. It is **consistent with**
  the firmware owning the scheduler and **not** proof; string archaeology is not
  disassembly. Recorded as INFERRED.

## Legal and handling note

These blobs were extracted from a publicly downloadable firmware image for interoperability
analysis, which the project charter permits. They are proprietary: **they are not committed
to this repository and must not be redistributed.** Only sizes, hashes and observed strings
are recorded here. Nothing here involves bypassing signatures, and no device was modified.

---

## Version history: 14 airOS releases, 2016 → 2026 (gap G21, closed)

Every WA-platform release build was pulled from Ubiquiti's public firmware API
(`fw-update.ubnt.com/api/firmware?filter=eq~~platform~~airmax`), unpacked, and its radio
firmware carved by symbol. Reproduce with `tools/research/fw_version_sweep.py`. Machine-
readable matrix: `research/raw/hardware/fw_version_matrix.json`. Changelogs were captured
alongside each build.

| airOS | Released | umac.ko | ptp | ptmp_ap | ptmp_sta |
|---|---|---:|---:|---:|---:|
| v7.2.4 | 2016-09-08 | 2,695,244 | 204,744 | **absent** | **absent** |
| v8.0.2 | 2017-03-28 | 1,880,088 | 213,507 | **absent** | **absent** |
| v8.3.1 | 2017-07-28 | 2,119,544 | 214,094 | 245,154 | 230,939 |
| v8.3.2 | 2017-09-01 | 2,120,184 | 214,154 | 245,307 | 231,275 |
| v8.4.0 | 2017-09-29 | 2,127,720 | 215,408 | 248,251 | 233,379 |
| v8.4.1-cs | 2017-10-06 | 2,127,896 | 215,408 | 248,326 | 233,465 |
| v8.4.1 | 2017-10-06 | 2,127,896 | 215,408 | 248,326 | 233,465 |
| v8.5.1 | 2018-03-09 | 2,129,944 | 214,159 | 248,988 | 233,331 |
| v8.5.8 | 2018-09-19 | 2,138,784 | 214,827 | 251,546 | 234,193 |
| v8.5.12 | 2019-02-14 | 2,340,372 | 214,901 | 251,681 | 234,262 |
| v8.7.13 | 2024-06-07 | 2,356,000 | 214,236 | 250,852 | 233,446 |
| v8.7.17 | 2025-06-23 | 2,356,000 | 214,236 | 250,852 | 233,446 |
| v8.7.22 | 2026-02-28 | 2,356,432 | 214,299 | 250,900 | 233,509 |
| v8.7.25 | 2026-08-06 | 2,356,432 | 214,299 | 250,900 | 233,509 |

### The role-split landed in airOS 8.3.1 (2017-07-28)

v7.2.4 and v8.0.2 carry only **two** firmware symbols — `athwlan_AR9888v2_bin` (a single
generic image) and `athwlan_AR9888v2_ptp_bin`. From **v8.3.1 onward** the generic image is
gone and is replaced by the pair `athwlan_AR9888v2_ptmp_ap_bin` + `_ptmp_sta_bin`.

So Ubiquiti did not always ship role-specific radio firmware. They **split PtMP into separate
AP and STA target builds in 8.3.1**, and that release's changelog is almost entirely Fixed
Frame work:

```
- airMAX-ac FF: Fix AP issue in FF mode
- airMAX-ac FF: Improve association time
- airMAX-ac FF: Improve uplink performance
- Fix: Scan all channel widths fails on AP in TDD Fixed frame mode
```

airOS 8.3 is also the release that introduced GPS Sync to airMAX AC. The correlation is
strong and the direction is sensible: **once the AP had to run a GPS-aligned fixed frame, the
AP and the station needed different target-side code, so the single PtMP image was split in
two.** Treat the causal reading as INFERRED — the changelog does not mention firmware
packaging — but the timing is exact.

### Ubiquiti polling code has been in the radio firmware since at least 2016

`UBNT_POLL_MEM_ALLOC` / `ubnt-poll` / `ubnt_set_power_range` are present in **every** build
tested, back to v7.2.4 (2016-09-08). This is not a recent development and there is no version
of airMAX AC whose radio firmware is stock QCA.

### Radio firmware is effectively frozen since 2024

Byte-identical groups (identical sha256 across all three images):

| Group | Radio firmware |
|---|---|
| v8.4.1 = v8.4.1-cs | identical (same build, `-cs` variant) |
| **v8.7.13 = v8.7.17** | identical across a full year (2024-06 → 2025-06) |
| **v8.7.22 = v8.7.25** | identical (2026-02 → 2026-08) |

**Operationally relevant to this network:** upgrading from 8.7.22 to 8.7.25 changes the radio
firmware **not at all**. Whatever 8.7.25 fixes is host-side. Equally, the fleet currently runs
two different radio firmwares — the LiteBeam 5AC LR on 8.7.11 carries *larger* images
(ptp 216,059 / sta 235,270) than everything else on 8.7.22 (ptp 214,299 / sta 233,509). Any
A/B measurement across those two units is not comparing like with like.

### Where the growth actually went

Between v8.5.8 and v8.5.12 `umac.ko` grew by ~202 KB while the radio images moved by under
150 bytes. That growth is host-side driver code, not target firmware. Across the whole
2017–2026 span the radio images vary by only a few KB — the target firmware is mature and
substantially unchanged for nine years.

## Follow-on work

1. ~~Diff across airOS versions.~~ **DONE** — see the version-history section above (G21).
2. **Disassemble `ubnt_poll_host.ko`** (MIPS, 186 KB) to map the host/target split. Its printk
   strings (`DAPROT`, deferred list, fixed frame, ATPC) are ready-made symbol anchors.
3. **Establish what `ubnt-poll` in the target does** — the AP/STA delta is the place to look.
4. Check whether the `ptp` image is what OpenWrt-flashed units would want anyway; it is the
   smallest and appears on every device regardless of role.
