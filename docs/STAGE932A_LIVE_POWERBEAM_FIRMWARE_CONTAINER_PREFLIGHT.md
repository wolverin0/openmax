<!-- doc-head: Stage932A native PowerBeam firmware file hashes and structural API2 preflight; no firmware activation -->
<!-- /doc-head -->

# Stage932A — PowerBeam firmware container preflight

2026-10-27. Provenance **CONFIRMED_LIVE_HARDWARE** for native file/driver reads;
container grammar analysis is local static verification of those captured bytes.
Attribution: Linux/ath10k logs and filesystem; external controller binary analysis.

## Native result

| Check | .241 AP | .242 STA |
| --- | --- | --- |
| Native board | PowerBeam5ACGen2 OpenWrt | PowerBeam5ACGen2 OpenWrt |
| Last logged firmware API | 2 | 2 |
| Requested `firmware-5.bin` | ABSENT | ABSENT |
| Existing `firmware-2.bin` | 204796 bytes | 204796 bytes |
| SHA256 equals copied native bytes | YES | YES |
| Native IE grammar errors | 0 | 0 |
| Native container exact byte roundtrip | YES | YES |
| Operational SGMT | 4 segments, no VA overlap | 4 segments, no VA overlap |

Observed path: `/lib/firmware/ath10k/QCA988X/hw2.0/firmware-2.bin`.
Both files have SHA256:
`a49160ff008390a34e43145bc56f6b8d047f8e02433aff20f965b6f2874ef52f`.
The held CT reference used by the Stage879A codec has a different SHA256
(`398e4380e7e55105f3da0f78af29d1e437404ed3a82597aa4b6daaa7dce1a38e`).
This mismatch is retained; it does not mean the native file is corrupt or that a
candidate image matching that CT reference was loaded.

## Interpretation

The requested API5 filename cannot be qualified as present. It is not silently
renamed to API2. The API2 file is a valid native QCA-ATH10K container under the existing
bounded Stage879A parser, with an operational IE3 SGMT accepted by the held codec.
Byte/length/IE alignment and segment VA checks do not establish firmware patch
semantics, driver ABI acceptance, persistent compatibility or a performance gain.

The file's on-disk SHA and the last boot log are **CONFIRMED** observations.
The SHA of bytes currently executing inside QCA hardware remains **UNKNOWN**:
no runtime firmware memory dump or new firmware activation was performed.

## Acquisition and retained failures

The native OpenWrt builds lack `stat` and `base64`. Initial bounded reads depending
on those tools failed and remain in the capture ledger. The final method reads
binary stdout through bounded SSH `cat`, encodes it locally, and checks the exact
byte count and SHA against independently captured native `sha256sum` output.
No target package, temporary file or configuration was installed for extraction.

No firmware upload, bind mount, ath10k reload, reboot, flash, MTD/calibration access,
RF change or service mutation was performed. Captures include native board, boot,
IW, relevant driver logs, requested paths, hashes and mount-query exit codes.

[Script](../tools/autoresearch/run_stage932a_live_powerbeam_firmware_container_preflight.py),
[receipt](../artifacts/autoresearch/stage932a_live_powerbeam_firmware_container_preflight.json),
[native binaries and captures](../artifacts/verification/stage932a/).
