<!-- doc-head: Stage171 offline public XC/XW/XM diagnostic starter and evidence limits -->
Packages read-only identity collection and disabled candidate templates.
Exact official profiles, historical source conflicts and source hashes remain explicit.
No firmware image, WA module, actuation, device contact or RF acceptance is supplied.
<!-- /doc-head -->

# Stage171A public XC / XW / XM tester release

Stage171 follows Stage170's completed local WA build. Its deliverable is a
diagnostic starter for testers with an already booted device. It is not an
XC/XW/XM firmware build, installer, deployment or proof of interoperability.

The builder is `tools/firmware/package_public_xc_xw_tester_release.py`.
Its output directory is `firmware/openwrt/public_xc_xw_tester_release/`.
The local receipt is
`artifacts/autoresearch/stage171a_public_xc_xw_tester_release_receipt.json`.
The second CLI run exported12 files with exit0 after preserving the initial
source-drift failure (exit2). Execution receipts live in the dedicated local
`firmware/openwrt/public_xc_xw_tester_release_work/` directory.
An independent fixture-root rebuild reproduced all12 exported files and the
complete receipt byte-for-byte (exit0). GitBash `-n` parsed the collector with
exit0; the collector was not executed. Runs3/4 preserve those receipts.

## Source authority

The packager pins the complete bytes of Stage158,159,165,166 JSON receipts,
the current champion scripts and their manifests. It never imports or runs
the old bakers, scripts, proprietary modules or configurations.

The first local build failed closed: current XC/XW scripts differ from the
hashes declared in165/166 and contain later tuning additions. The new receipt
preserves declared and observed hashes. XC candidate numbers come only from
the original2014ede2 script recovered as bytes from the pinned historical
overlay; XW/XM candidates come from the166 family JSON. The later scripts are
neither applied nor redistributed. The overlay's WA module is hashed and excluded.

It separately pins the held official OpenWrt24.10.4 `ath79/generic`
`profiles.json` and `sha256sums` under
`artifacts/verification/stage170_to_172_sources/`.
These were acquired by the coordinator over HTTPS. GPG verification is absent.
Presence in that inventory confirms a profile name, not a board revision,
calibration layout, driver ABI, flash/recovery path or physical performance.

## Matrix and unresolved identities

`PROFILE_MATRIX.json` preserves each reported record with a source and record
identifier. Sysid is a claimed attribute, never a globally unique key.
No record grants firmware-install approval.

| Target | Public qualification |
| :--- | :--- |
| Rocket Prism5AC Gen2 / PrismStation | Retain stock airOS; active GPIO/HSR filtering remains unqualified here. |
| PowerBeam5AC500 | Exact official profile exists; revision/DTS/calibration identity remains unqualified. |
| PowerBeam5AC620 | Exact official profile absent; the500 profile is not installation authority. |
| IsoStation5AC XC | Claimed exact profile absent from the held inventory. |
| NanoBeam5AC19 XC | Candidate XC profile exists; variant and revision remain unqualified. |
| XW ath9k | Preserve30 Stage158 records and separate Stage166 claims; check each exact profile. |
| XM32MiB | Stock-airOS-only in this kit; OpenWrt24.10.4 memory safety is unqualified. |
| XM with other/unknown RAM | Preserve source claims; no inference of installation safety. |

Stage165 sysid/model/profile mappings disagree with Stage159. Stage166 XW
mappings disagree with Stage158, including reported e845/e855/e866/e885 models.
Stage166 labels XM32MB profiles verified although Stage158 explicitly blocks
OpenWrt24.10.4 on32MB XM. Both source claims remain visible with qualifications.

The old Stage165 overlay declared a WA `mac80211` object. It is excluded.
No `.ko` or `.bin` is distributed by this packager. WA compatibility never
establishes XC QCA9558/QCA9880 or XW/XM ath9k module compatibility.

## Contents and use

The ZIP and TAR.gz contain the same eight regular files:

- `README.md`, `PROFILE_MATRIX.json`, `SOURCE_PROVENANCE.json`;
- `collect_capabilities.sh`, manually invoked only;
- `families/xc.candidate.json`, `families/xw.candidate.json`,
  `families/xm.candidate.json`;
- `PACKAGE_MANIFEST.json` with hashes/modes for the preceding payloads.

Standalone copies, both archives, `SHA256SUMS` and its byte-identical
`SHA256SUMS.txt` alias are written to the output directory.
The checksums cover standalone payloads and archives; they do not recursively
include themselves. The manifest does not hash itself.

Inspect the collector before optionally running it yourself on an already
booted tester-owned device. It reads selected board/kernel/RAM and driver-link
metadata, plus bounded interface names and presence of wireless metadata.
It does not read IP/MAC addresses, credentials, private configuration,
calibration data, debugfs hardware knobs or arbitrary device nodes.
It never connects to another device or changes configuration.
Missing identity remains `UNKNOWN`; missing RAM remains `null`.
Reported identity is not authenticated and never approves firmware installation.

Candidate JSON preserves historical configuration proposals with `enabled=false`
and `approved_for_live=false`. It contains no apply code. Memory thresholds,
queue values, AQL/ANI or airtime flags are not independently measured safe defaults.
The package supplies no RF gain, capacity, fairness, loaded-tail-latency or
stability acceptance. No test of the collector on hardware is claimed.

## Local reproduction and safety

Run from the repository with CPython:

```text
python tools/firmware/package_public_xc_xw_tester_release.py
```

`--root` supports disposable local fixture roots. Output must use a dedicated
`firmware/openwrt/public_xc_xw_tester_release...` directory. Receipt paths must
be Stage171 JSON under that root's `artifacts/autoresearch` directory.
UNC, URI, device, alternate-stream, traversal, symlink and reparse paths fail closed.
Source-byte drift, duplicate JSON keys and nonfinite JSON fail closed.

Existing output needs `--force` plus a matching managed manifest and exact
inventory. Unknown files/directories and unowned receipts are preserved.
Each file is atomically replaced; the directory is not a transactional deployment.
ZIP/TAR timestamps and ownership are fixed. Two serializations are compared and
both archives and saved outputs are read back. This establishes local byte
reproducibility, not cross-toolchain, hardware or deployment acceptance.

## Five pillars and remaining work

The receipt has five explicit qualified fields: saved-source audit; official
inventory provenance without a new scholar run; offline archive checks without
counterbalanced RF trials; no Pareto/performance acceptance; and no new MemoryMaster
claim. Older claim IDs are provenance only. Schema presence does not prove a pillar.

Stage172 owns independent tests and gate integration. Before any later physical
work, resolve exact identity and ABI, validate DTS/calibration and RAM constraints,
establish recovery, and obtain the applicable operational authorization.
Nothing in this package authorizes flashing, RF changes, protected-partition writes
or publication. No operator physical action is needed to produce this offline kit.
