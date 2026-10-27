<!-- doc-head: Stage264A complete held firmware inventory and independent container CRC audit -->
Container integrity is separate from signature authenticity, board approval and boot tests.
<!-- /doc-head -->

# Stage264A: held image verification

Run `python tools/firmware/verify_all_openmax_kit_checksums_and_headers.py`.
Receipt: `artifacts/autoresearch/stage264a_all_firmware_crc32_verification_receipt.json`.
Parent: reproducible firmware release deliverable; question: which held containers
pass their actual format checks without assuming that every .bin is flashable?

Every `.bin` under `firmware/openwrt/` is enumerated, including caches, working
outputs and unknown formats. SHA256 binds the complete bytes. No image is modified.
The independent parser verifies OPEN header and ordered PARTkernel/PARTrootfs CRC32,
length/capacity/padding, uImage header/data CRC32, and every trailing FWx0 CRC32.
Rootfs is located by the declared kernel-aligned boundary after reassembling PARTs,
never by accepting a stray `hsqs` string. SquashFS v4 superblock and bytes-used
bounds are checked; there is no whole-filesystem CRC32 field in this format.
Decompression and rootfs content trust are outside this stage.

[OpenWrt mkfwimage](https://github.com/openwrt/firmware-utils/blob/master/src/mkfwimage.c)
defines END. with a CRC, while ENDS is a zeroed RSA placeholder in this builder.
The scanner checks the applicable structure and never calls an ENDS placeholder
or a FWx0 fake-certificate wrapper an authenticated signature.

Kernel-only uImages are explicitly classified separately. Unsupported ELF, tar,
stock formats or malformed images remain FAILED_OR_UNSUPPORTED with a reason.
Exit 1 preserves such gaps; it does not imply those formats are corrupt.
This local software audit grants no board match, recovery, boot or RF acceptance.
