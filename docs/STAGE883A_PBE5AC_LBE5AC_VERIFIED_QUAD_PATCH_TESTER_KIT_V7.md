<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage883A: tester kit BLOCKED

Question: can the verified native Quad-Patch be included in a compatible
PowerBeam5AC Gen2 and LiteBeam5AC Gen2 public tester release?
Answer UNKNOWN; Stage879 has not emitted the native Quad binary.
Attribution: external controller; future native behavior belongs to QCA firmware.

The verifier reuses Stage865's bounded checksum/path validation without invoking
its producer. The pinned public_release_v4/SHA256SUMS.txt is checked, then the
four selected factory/sysupgrade files are freshly SHA256-verified.
Their bytes, names and labels remain HELD_PUBLIC_V4_REFERENCE_ONLY. They are
not renamed v7, copied to a release directory, placed in an archive or flashed.
Hashes prove local held-byte integrity only, not image configuration or ABI.

PBE board0xe3d6 selects ubnt,powerbeam-5ac-gen2; LBE board0xe7f9 selects
ubnt,litebeam-ac-gen2. These are explicit selection metadata, not newly decoded
DTB identity or runtime acceptance of every board revision.

The source865 receipt's canonical manifest hash and selected baseline references
must agree with the fresh checksum audit. Source879 is parsed and pinned, and
its declared blockers are retained. Even quad_emitted=true or status=CONFIRMED
alone cannot approve a kit: emitted native bytes, independent review and actual
runtime/recovery on BOTH boards are required. Raw SGMT is not a flashable image
or a complete QCA-ATH10K container and cannot be relabeled firmware-5.bin.

Required missing evidence also includes45-second rollback, zero-rogue-DHCP
runtime plus cold-boot behavior, exact image matching and board-specific
rollback validation. No '100% compatible' claim follows from metadata/tests.

Public candidate material consists only of a canonical JSON manifest embedded
in the receipt: fixed board/profile fields, baseline filenames, sizes and hashes.
No configuration, credentials, internal addresses, native binary bytes, scripts
or private evidence payload are exported. No ZIP/bin or release is created.

Run `python tools/firmware/build_stage883a_pbe5ac_lbe5ac_verified_quad_patch_tester_kit_v7.py`.
Exit2 records BLOCKED; exit1 means invalid input and preserves the previous
receipt. Tests use disposable files and do not contact devices or producers.
Next: resolve879's native PB070/PB080 contracts, independently qualify the
Quad container, execute guarded RAM tests, then validate both-board recovery.
