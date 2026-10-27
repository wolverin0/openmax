<!-- doc-head: Stage356A offline tester bundle preflight and postflash evidence verifier -->
Local hashes and saved assertions never authorize a flash or prove physical acceptance.
WA watchdog embedding uses a pinned offline decoder; unsupported formats remain UNKNOWN.
<!-- /doc-head -->

# Stage356A

Parent: offline release safety and evidence boundaries, after Stage355.
This program only reads bounded local JSON/files and writes a JSON report.
It has no target/radio/SSH/WAN/flash/configuration executor. Its only native execution
is the pinned local sqfs2tar decoder, fixed argv, no shell,30s timeout,8MiB TAR cap.

Build inventory: `python tools/firmware/verify_openmax_tester_bundle.py inventory --build`.
Tests: `python -m pytest -q -o addopts= tests/test_stage356a.py`.
`--help`, `preflight --help` and `postflash --help` document the CLI.

## Independent trust and schema1

Both verification modes require --manifest, --trusted-manifest-sha256 and
--evidence. The trusted SHA256 MUST arrive through an independent caller channel;
a manifest cannot establish its own trusted hash. The tool validates the anchor
before opening evidence or referenced files. A hash is not a signature or proof
that the saved observations occurred on hardware. Outputs never contain backup bytes.

Manifest JSON has schema_version=1; target; image; protected_backups; watchdog;
rollback; saved_evidence_sha256. Unknown keys, duplicate keys, nonfinite values,
unsafe paths, oversized files and invalid field types reject with fixed error codes.
Target/image/rollback identity fields are family,model,sysid,profile,device_id_sha256.
Family is WA/XC/XW/LTU. WA additionally checks the known exact model/profile/sysid
matrix; other families are not silently promoted to supported firmware platforms.
An identity hash is a caller assertion, not a physical serial-number readback.

File references are {path,bytes,sha256}: canonical relative POSIX paths within the
manifest directory, never UNC/URI/device/ADS/traversal/symlink/reparse aliases.
Image and rollback each contain file,kind(factory|sysupgrade),identity,build_id.
Protected backups map EXACT mtd0,mtd1,mtd4,mtd5 to file,identity,boot_id records.
The four actual original files must match independently anchored expected sizes
and hashes, belong to the same identity/preboot, and not consist entirely of00/FF.
Matching erased bytes is rejected even when the expected hash was supplied.
Watchdog contains file and installed_path (/usr/sbin/safe-name); bundled file
matching does NOT mean embedded, installed, armed or safe to execute.

Evidence JSON has schema_version=1, source_kind(SAVED_RUNTIME_READBACK or
SYNTHETIC_FIXTURE), pre, optional post, and backups. The entire evidence file must
match saved_evidence_sha256 inside the independently anchored manifest.
Each backups entry contains identity,boot_id,bytes,sha256 and binds the actual file.
Snapshot fields: identity,boot_id,boot_started_s,timestamp_s,build_id,image_sha256,
protected_sha256,management_ok,rf_associated,counters,watchdog.
Counters: start_s,end_s,tx_before,tx_after,rx_before,rx_after; unsigned and separately
increasing within a fresh same-boot observation, never compared across boot resets.
Snapshot watchdog: installed,armed,boot_id,heartbeat_s,script_sha256,
rollback_image_sha256,installed_path. True booleans are required; missing/unknown/
false is never pass. Heartbeat must be within this boot, not future and <=150s old.
Snapshots allow at most5s clock skew and are <=150s old at --now-s (default local
wall clock). An explicit historical --now-s checks saved consistency only.

## Postflash comparison and image boundary

Postflash additionally requires changed boot IDs, post boot after the pre snapshot,
exact expected new build/image hash, unchanged four protected hashes, management,
RF, counter progress and installed/armed/current-boot/fresh-heartbeat watchdog.
Actual backup file bytes are hashed only; never printed, copied or executed.
Stage264 pure container CRC checks are reused. WA also checks the known official
kernel/DTB profile using Stage232's pure parser, without its UNSET v5 trust path.
CRC and metadata are not signature authentication. Unsupported container/board
joins remain UNKNOWN or mismatched, including unsupported XC/XW/LTU images.

After WA board/kernel/capacity validation, the exact rootfs bytes are passed to
pinned squashfs-tools-ng1.3.2. Only usr/sbin is streamed to bounded TAR bytes.
No files are restored. The declared watchdog must be a unique root-owned regular
executable with no group/world writes or set-ID bits, and match the trusted hash.
Unsafe TAR names, watchdog links, duplicates, oversize or decoder failure block.
Other stock links are ignored, never followed. Unsupported families keep embedding
UNKNOWN. Saved installed/armed assertions alone never prove image embedding.
data_contract_status/status may be SAVED_EVIDENCE_CONSISTENT_NOT_FLASH_APPROVAL
when every gate passes, including explicit synthetic fixtures; never flash approval.
Both image and rollback require exact board/kernel joins; WA payload<=0xf60000.
Current verifier modes exit1 when blocked; malformed/untrusted inputs exit2.
Exit0 means only complete consistent saved evidence, including verified image
embedding. It must never imply flash approval or independent hardware validation.

## Actual existing kits and reproducibility

The generated inventory hashes actual WA publicv4 files, Stage171 XC/XW/XM
diagnostic starter files and the LTU safe shell, comparing historical receipt
references where present. Drift is retained. No backups/runtime/postflash evidence
is invented. All three kit entries remain BLOCKED and target_access=false.
Historical inventory hashes are observations, not independent trust anchors.
Deterministic inventory/build output contains no current timestamps. Runtime
verification records the caller's as-of time and never claims fresh target access.
Outputs are finite atomic JSON; source/evidence/referenced-file collisions and
unowned existing output files are rejected. Public reports contain only hashes,
sizes, status/reason codes and check booleans, without raw configuration contents.
Decision: KEEP as an offline evidence checker; no deployment or zero-brick claim.
