<!-- doc-head: Stage865A blocked PBE5AC/LBE5AC v6 candidate manifest and verified held baseline hashes -->
Manifest version6 is not a new firmware image or runtime compatibility claim.
<!-- /doc-head -->

# Stage865A

This offline step prepares a deterministic public candidate manifest for
PowerBeam5AC Gen2 and LiteBeam5AC Gen2. It neither builds nor copies firmware.
Run `python tools/firmware/build_stage865a_pbe5ac_lbe5ac_tester_release_package_v6.py`.
Exit1 means the receipt was prepared but release gates remain BLOCKED; exit2
means invalid local evidence and leaves the prior receipt unchanged.

## Reused routes and selected baseline

The existing OpenWrt core builder and Stage170 WA public packager are inspected
and hashed as source references only, never imported or executed by this tool.
The four selected factory/sysupgrade images come from public_release_v4.
The complete SHA256SUMS.txt text is pinned; every line is parsed for safe names,
while only the four selected binary references are read and hash-checked.
Other manifest members are not claimed verified. Paths, duplicate/case aliases,
device names, symlinks, remote paths and oversized reads fail closed.

Each board retains its own profile and identity metadata: PBE0xe3d6 with
ubnt,powerbeam-5ac-gen2; LBE0xe7f9 with ubnt,litebeam-ac-gen2. These mappings
are declared selection metadata, not newly decoded image/DTB or device proof.
The v4 images remain BASELINE_REFERENCE_ONLY: they are never relabeled as v5/v6.
Local checksum agreement is held-byte integrity, not an authenticated release,
valid-container audit, embedded configuration audit or proof of safe flashing.

## Candidate public material

The receipt embeds a canonical JSON manifest and its SHA256. Public material is
constructed from fixed fields, board identities, selected filenames, sizes and
hashes only. No source configuration, credentials, shell script, proprietary
module, internal address or raw evidence payload is copied into the candidate.
The existing binary files are hashed but not included in a new package. No ZIP,
release directory, install/apply script or export of firmware bytes is created.
Native firmware export and publication remain prohibited in this step.

## Gates and evidence limits

The manifest is unconditionally BLOCKED pending independently validated native
quad support, a qualified v5 baseline and runtime/recovery evidence for BOTH
exact board revisions. Metadata, a PASS label or copied getters cannot unlock it.
The saved Stage806 PB-070 receipt is hashed and parsed if present; its patch
count is recorded as a reported field, not accepted native behavior. Missing
optional evidence stays MISSING. No target access, network, flash, deployment,
regulatory change, boot test or firmware producer invocation occurs here.

The result demonstrates bounded local manifest construction and checksum
validation only. It does not establish performance gains,100% compatibility,
watchdog installation, protected backup/restore or physical acceptance.
