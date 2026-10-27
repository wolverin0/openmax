<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage879A: binary generation BLOCKED

Parent: FMX-0011/RE1, authorized879..884 queue. Question: can exact native
Quad/Penta images be built without VA collisions? Attribution: external controller/QCA firmware.
The source audit found no executable PB070/PB080 specification. Output binaries:0.

The real baseline is a held OpenWrt CT `firmware-2` container SHA256
`398e4380e7e55105f3da0f78af29d1e437404ed3a82597aa4b6daaa7dce1a38e`.
It is not mislabeled as the current device image or as firmware-5.
The native parser enforces the12-byte QCA-ATH10K magic,4-byte aligned unique IEs,
exact lengths/padding, bounded input and unchanged metadata/order.
IE3 SGMT is fully decoded and its segment address ranges checked for overlap.
Reembedding the unchanged native IE3 reproduces the complete original byte-for-byte.
Zero base-segment collisions does not establish collisions for absent Quad/Penta sites.

The pure composition engine requires all4/5 patch labels, a matching source hash,
exact preimages, equal-size non-noop replacements, in-range sites and disjoint VAs.
It reparses the result and checks entry/layout preservation and every decoded diff.
Synthetic test recipes demonstrate this engine, not the semantics or safety of PB070/PB080.
There is no unchecked external recipe loader or production activation approval.

PB070 names two different things in existing documents: an experimental custom-PHY
eligibility gate and a proposed RC probe patch. Their locks are not interchangeable.
PB080 lacks a queue owner/unit/target and exact native site. Absence of ASCII
symbols does not prove that either change is impossible to reverse-engineer.
Existing PB050 probe instructions cannot be silently renamed PB070.

`python tools/firmware/build_stage879a_verified_pb070_and_pb080_native_sgmt_binaries.py`
returns2/BLOCKED. `--source` and `--sha256` inspect an explicitly hash-bound local
native source; changing the filename cannot qualify its driver API or patch semantics.
No binary is emitted. The first13-byte-header construction failure is retained in
`artifacts/verification/stage879a/first_builder_failure.json`; fixed header is12bytes.

Evidence: [receipt](../artifacts/autoresearch/stage879a_verified_pb070_and_pb080_native_sgmt_binaries.json),
[independent search](../artifacts/verification/stage879a/independent_patch_spec_review.json).
Next: define desired PB070 RC behavior and PB080 depth, map exact native sites,
review every changed instruction independently, then compose and qualify recovery.
