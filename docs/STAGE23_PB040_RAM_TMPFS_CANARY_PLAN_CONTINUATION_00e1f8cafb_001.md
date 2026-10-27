<!-- doc-head: STAGE23_PB040_RAM_TMPFS_CANARY_PLAN.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE23_PB040_RAM_TMPFS_CANARY_PLAN.md) | Part 1/2
<a id="research-decision-and-remaining-evidence"></a> [Research decision and remaining evidence](STAGE23_PB040_RAM_TMPFS_CANARY_PLAN_CONTINUATION_00e1f8cafb_002.md#research-decision-and-remaining-evidence) | <a id="revision-bound-independent-reviews"></a> [Revision-bound independent reviews](STAGE23_PB040_RAM_TMPFS_CANARY_PLAN_CONTINUATION_00e1f8cafb_002.md#revision-bound-independent-reviews)

<!-- stage822a-payload-begin -->

PB040 before/after hashes are freshly verified in memory using two decoders.
All three shell references exit 78 before mutation; no enabling flag exists.
API5 compatibility and operational rollback observers remain unqualified/unimplemented.
No radio, firmware export, surrogate observation or physical acceptance is added.


# Stage23: PB040 RAM tmpfs canary preparer

Task: `T-S23-CODEX-PB040-CANARY-LOADER-AND-SURROGATE-UPDATE`.
Decision: **KEEP offline preparer; BLOCK physical execution**.

## Prespecified question and boundary

Parent deliverable: original forward-plan control-authority and recovery tooling,
within BENCH_PLAN's offline analysis scope. E2 remains NOT_ACCEPTED. Question:
can the held canary hashes be independently reproduced in memory, and can a plan
constrain staging writes to tmpfs, preserve the stock file, specify watchdog and
rollback, and reject flash commands?

Before implementation, PB040 described a one-byte `.rodata` mutation in a vendor
SGMT inside `umac.ko`. Its AP container grows251681 to251839 bytes after patching,
although the decoded segment remains8500 bytes. This is not a qualified replacement
of a fixed-size ELF symbol. The helper does not rebuild a compatible UMAC module
preserving ELF layout/relocations. The ath10k loader requires another container/ABI.

Minimum acceptance was fixed before coding: authenticate the module, patcher,
spec and decoder; verify three originals/12 segments and exactly one changed
byte; export metadata without firmware payloads; generate copy/bind and inert
watchdog/rollback references; reject modified programs and false readiness claims;
run the single requested pytest file and obtain independent review. Stop there.
No radio access, mount, module operation, flash, reboot, WSL, RF/load experiment
or bench recipe is used. Runtime observers remain out of this offline scope.

Deliverables:

- [Preparer](../firmware/pb040_ram_tmpfs_canary_preparer.py)
- [JSON plan](../artifacts/physical_boundary/pb040_ram_tmpfs_canary_plan_20261025.json)
- This document
- [Tests](../tests/test_pb040_ram_tmpfs_canary_preparer.py)

The title mentions a surrogate update; the explicit task body requests these
canary outputs. No surrogate/training file is changed. JSON records zero new
physical observations, zero ready cells and no performance/training claim.

## Fresh offline evidence

Seven local sources are authenticated by SHA256 before helper import or parsing.
ELF parsing uses the authenticated UMAC byte snapshot, without another file read
or binary extraction. Existing PB040 helpers apply the patch in memory. The
independent `tools/research/sgmt.py` decoder checks originals and canary: ordered
payloads/destinations, flags, full consumption, entry and DONE. All12 original
segments undergo compression/decompression round trips; untargeted stored
segments remain identical. Explicit checks supplement historical helper asserts
and remain active under `python -O`.

| Object | Bytes | SHA256 |
| --- | ---: | --- |
| Held UMAC |2340372|`46525dc6f8b789bf820f0713841a2a9ecdcba833300ddb1ab1ef06fc4ab6a9c5`|
| AP SGMT before |251681|`55e9c94a2f0b466ff50ced26f589c755b955e751861b466bb71be9f87de261ee`|
| AP SGMT canary |251839|`e2402d644fc85e595d9efca09c65281076d05f839e3f47a94b7e9f8b2c82b415`|
| Segment1 before |8500|`4352471afde9d65477ebf3af97cdfffb48080895a43b3e71745c08389c589483`|
| Segment1 canary |8500|`5bae628f353f7e7960310a594ecba663555a7e7292e29a05c4f118d06b19bfdb`|

CONFIRMED offline: AP segment1 offset2387/address `0x0040b953` changes only
`0x65` to `0x45` (`ubnt_set_power_range` to `ubnt_set_power_rangE`). Entry stays
`0x00983c00`; DONE address stays0. This does not insert a literal
`PB040-CANARY-RODATA` log marker or establish harmlessness, ROM acceptance or RF behavior.

## Loader boundary

CONFIRMED source-format mismatch: held ath10k `hw.h:138-181` defines API5's
`QCA-ATH10K\0` magic/IE fields. `core.c:2381-2438` checks magic and aligned IEs;
`core.c:2484-2528` extracts firmware/WMI/HTT metadata. Raw `SGMT` renamed to
`firmware-5.bin` fails that magic check. A wrapper alone would not establish
vendor firmware/ath10k ABI compatibility. Source paths/pins are in JSON.

UNKNOWN: the exact qualified original/canary API5 pair, installed board/build,
driver ABI/module scope and semantic readback. API5 sizes/hashes remain `null`;
SGMT hashes are never substituted for them. No exact pair was found in the scoped
held firmware filenames. This is a negative result for this proposed route, not
a universal conclusion that the hardware cannot execute modified firmware.

## RAM policy and script references

Exact requested commands, generated only as data:

```sh
cp /lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin /tmp/fw_canary/firmware-5.bin
mount -o bind /tmp/fw_canary/firmware-5.bin /lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin
```

Main, watchdog and rollback are embedded in JSON with SHA256 hashes. Each starts
with a diagnostic and unconditional `exit 78` before mutation. No argument/env
flag enables execution. The unreachable references also have fail-closed
`observe()` stubs and `UNQUALIFIED` API5 placeholders. **Operational rollback and
observers are UNIMPLEMENTED.** These are inert transaction references, not an
operational loader or armed recovery system.

The reference copies stock to RAM and checks its qualified whole-API5 hash,
then stages a separately qualified API5 canary from RAM and checks hash/provenance.
That candidate does not exist here. SGMT before/after verification occurs offline;
it is not mislabeled as a whole-API5 runtime check. No SGMT/ELF/API5 binary is exported.

Writes are allowed only below `/tmp/fw_canary` and `/tmp/fw_canary_control`.
A future runtime must prove these roots and staging are tmpfs, swap is inactive,
parents are root-owned/nonsymlink, byte/memory budgets are sufficient, and roots
are fresh/exclusively owned. It must reject existing overlays/state and may not
run `swapoff`, adopt stale state or change persistent/global configuration.
`/tmp` alone proves nothing. The underlying stock file is never a data-write
destination. `filesystem_ram_only_policy_validated=True` describes static policy;
`runtime_ram_only_verified=False` records that it was not measured on hardware.

Before bind/module mutation, the reference requires a separate HUP-resistant
watchdog plus canonical rollback hash and PID-birth/argv/READY proof. Default
reference budgets:30s guard,5s external commands,10s rollback reserve. These are
not measured deadlines; a qualified observer must prove enough time remains for
complete restoration. The guard/control journal is outside the overlay being
removed. Main and watchdog coordinate cleanup; both exit codes are retained.

Ownership requires boot/mount-namespace identity, pending intent before bind,
exact top mount/source/inode identity, and PID birth/argv for guard signaling.
Path/PID alone is insufficient. A later implementation must handle the bind/
journal gap, concurrent cleanup and idempotence without adopting foreign mounts.
These observers and race/health handling are not implemented or accepted here.

Rollback reference order: owned bind unmount; verify visible stock file hash;
bounded `rmmod ath10k_pci`/`modprobe ath10k_pci` for a qualified initially loaded
single-device leaf module; exact stock runtime/health proof; then RESTORED/guard
disarm. Unmount alone does not replace firmware in SRAM. Ownership mismatch,
busy module, wrong hash or missing health means restoration incomplete. No
forced/global/lazy unmount or forced unload is allowed. Userspace cannot guarantee
recovery from kernel hang, power loss or memory collapse; proven physical recovery
remains a separate prerequisite under the existing operator gates.

Validation regenerates the whole plan from authenticated sources and compares
canonical JSON, including every nested evidence/readiness field. Scripts must
match exact canonical bytes, not just a mutable hash/blacklist. Freeform/encoded
`mtd`, `sysupgrade`, `dd`, arbitrary shell, persistent writes and modified gates
are rejected even after the inert exit or with a recomputed hash. A narrow command/
flash-device-path prohibition adds defense in depth.

## Validation and independent acceptance

Fresh generation wrote the metadata JSON with exit0. First pytest request did not
execute: resource guard timed out after10s with free RAM1.0GB below the2GB floor;
wrapper exit1 was retained. This is not a pytest failure/pass. A second request
keeps the same floor/guard. Final test and code-review receipts follow below.

Tests cover held-byte hashes/sole mutation, SGMT/API5 separation, requested
commands/order, three unconditional gates, canonical/rehash attacks, encoded flash
commands, typed watchdog bounds, nested false readiness, source drift, remote/
device/reparse paths, duplicate/nonfinite JSON, and no host actuation/binary export.
No generated script is executed; no radio/module/mount is touched. Unrelated
pytest files are outside this bounded task.
<!-- stage822a-payload-end -->
