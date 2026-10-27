<!-- doc-head: Pinned offline Windows runtime provenance and architecture -->
Both x86 and x64 packages contain iperf 3.22; select by OS architecture.
Every archive/member hash and executable/DLL PE machine is checked.
The x86 Cygwin dependency is legacy; this is a restricted temporary lab endpoint.
Controller Defender blocked actual x86 execution; static checks are not runtime acceptance.
<!-- /doc-head -->

# Runtime provenance

The operator confirmed the notebook is **32-bit Windows** on 2026-10-06.
The prior x64-only bundle was an incorrect unverified assumption and is superseded.
Selection uses `Environment.Is64BitOperatingSystem`, not the shell's bitness.
The bundle includes both architectures, with no runtime Internet dependency.

## x86 / 32-bit

- Publisher asset: [lmq8267/iperf3 release 3.22, iperf3-x86-pc-windows.zip](https://github.com/lmq8267/iperf3/releases/download/3.22/iperf3-x86-pc-windows.zip).
- Release published 2026-09-29; local archive `packages/iperf-3.22-win32.zip`.
- Archive size 1,354,118 bytes; SHA256 `cedbca03a029ec35081b0466ab5d9aade099105bdabcf3c413204e9efa3b8a7c`, matching the GitHub release API asset digest.
- `iperf3/iperf3.exe`: 322,362 bytes; SHA256 `5ed5046041a53dad4e25945c0703739b95f68bf5477045c9beb5c7cd20288445`.
- `iperf3/cygwin1.dll`: 3,315,439 bytes; SHA256 `f1f04586da69854a6e00f978dca5edb8318bd585f51aa88c5fd6ba9b0e3fbb65`.
- BOTH files independently inspected: PE machine `0x014c` / PE32 magic `0x010b`, not merely an x86 filename.
- [Release-tag build workflow](https://github.com/lmq8267/iperf3/blob/3.22/.github/workflows/build-iperf3.yml) selects Cygwin `platform: x86`, checks out ESnet's release ref and builds the Windows target. No Windows application-source patching is shown. Mutable workflow actions and lack of verified attestations limit reproducibility/provenance claims.

[Cygwin ended x86 support at 3.3.6](https://cygwin.com/pipermail/cygwin/2022-November/252542.html).
A current iperf release does not make that dependency maintained. This package
is for the explicitly scoped, temporary notebook bench with exact-IP firewall
rules, not public exposure or production service installation.

Execution acceptance: the controller's Defender Exploit Guard blocked the new
x86 executable with event 1121, rule `C1DB55AB-C21A-4637-BB3F-A12568109D35`.
No security setting was changed or bypassed. PE/hash checks and 32-bit PowerShell
tests are separate from actual iperf execution, which remains **BLOCKED on this
controller / NOT_RUN on the notebook**. Previous x64 loopback results do not
validate the x86 binary. Original failed test evidence is retained at
`artifacts/notebook-loopback-3c2e837f60eb497e8760d84fc09f7dd7`.

## x64 / 64-bit

- Publisher asset: [ar51an/iperf3-win-builds release 3.22](https://github.com/ar51an/iperf3-win-builds/releases/download/3.22/iperf-3.22-win64.zip).
- Archive SHA256 `c9feabb3d721039508ccb81f74c2ada3ae11b9e75d33d24510573c2aa21da420`.
- `iperf3.exe`: SHA256 `bcafba4aff825fa94685b6b3d049f8b1338c69e6dc1d06e6a00ac046191e4999`.
- `cygwin1.dll`: SHA256 `d66788fce4ef1ce787fc1a83f2dd1e063e58bbf0d48ad93164ee195a983c035e`.
- Required PE machine `0x8664` / PE32+ magic `0x020b` for both files.

The builder validates both archives and exact members, normalizes the x86
archive's `iperf3/` prefix, and emits `runtime/x86` and `runtime/x64`.
Only the selected pair is copied into the active run's runtime directory.
