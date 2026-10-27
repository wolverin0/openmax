<!-- doc-head: Stage817A local PB040 PB050 PB060 composition; activation gated -->
<!-- /doc-head -->
# Stage 817A Universal PB060 triple-patch kit

`CONFIRMED` applies to offline byte composition only. Attribution: `QCA firmware` / `external controller`.
Built 7/7 target SGMT payloads: OpenWrt CT IE3 and airOS 8.7.25 WA/XC PtP/AP/STA.
PB040 is the exact unique CCA tuple; PB050 and PB060 use existing target-specific surgical specifications.
All sites must be disjoint, match original bytes and survive parse/repack with unchanged segment layout.
Hashes and individual patch receipts are in `artifacts/autoresearch/stage817a_universal_pb060_triple_patch_openwrt_airos_kit.json`.
Package: `artifacts/autoresearch/kits/stage817a`; `SHA256SUMS` covers its helper and payloads.
The shell loader defaults to inspection and supports checksum verification. Activation is refused.
These SGMT payloads are not complete flash images. airOS signature acceptance and OpenWrt container embedding are UNKNOWN.
No SSH, target writes, module reloads, flash or new performance measurements occurred.
Unsupported or missing target inputs stay UNKNOWN; no fallback binary is synthesized.
Online scholar grounding and durable MemoryMaster ingestion remain UNKNOWN.
