<!-- doc-head: 983A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# Local SquashFS factory fail-closed source contract

This is a local source contract; no native image was emitted or installed in this stage.
The requested generator path was absent; the older remote backend is not imported or executed.
Inspection is the default and never invokes an executable, resolves a radio or reads firmware.
Explicit build requires local POSIX root, a pinned SquashFS toolchain, base SHA256, declared board profile and private new output.
Four exact rootfs paths, single-link regular files,0755 modes and source hashes are mandatory.
Bootstrap must execute the runtime helper with --qdisc-mode auto; comments/string presence do not satisfy wiring.
Bootstrap and rc.local accept only complete straight-line launch templates; unreachable commands are rejected.
Watchdog and transaction bytes must equal the current reviewed canonical repository sources; caller hashes cannot approve alternatives.
rc.local must launch the guarded watchdog explicitly with --apply. Retired payloads are rejected.
Native unsquashfs extraction, repack and independent extraction readback are mandatory before candidate emission.
Unchanged filesystem entries retain hashes, types, modes, owners, symlinks, hardlinks and device metadata.
OPEN/kernel/rootfs CRCs, bounded SquashFSv4 structure and unsigned ENDS layout are checked.
Magic-only buffers and ZIP overlays cannot be accepted as SquashFS filesystems.
PowerBeam/LiteBeam profile names are declared input metadata, not hardware identity attestation.
Vendor RSA signature, native bootstrap interoperability, OTA rollback and physical compatibility are not accepted.
Current retired bootstrap and absent bound native toolchain keep actual emission BLOCKED.
No network/SSH, device operation, protected-partition write or memory ingestion occurs.

Current payload source snapshots (static hashes only; no rootfs or mode acceptance):
- 99-fmx-pbe5ac-ptp: edf58be7c1335da3d6e1daf3200ee63acf503e0c52dacf7ec7270480165aba4a.
- fmx_ptp_rollback_watchdog.sh: 68121a26071e66a0f4518a4ce4c06c3a957e22e2a19569ad4567f67ea75d72fd.
- fmx_pbe_lbe_runtime_transaction.sh: dce731cf8837884955be37efefb80b513addd79f9085af8f97a1b23b73fabf23.
