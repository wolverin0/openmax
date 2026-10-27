<!-- doc-head: STAGE300A_LTU_AES_CRYPTO_OFFLOAD_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 300A: Binary RE of LTU Encryption Engine (`ame_asic0` AES Hardware Offload)

## 1. Binary Provenance (`CONFIRMED` — Attribution: `proprietary airMAX/LTU module`)
- **`afltu_2.4.2/ame_core.ko`**: SHA-256 `fe5d489ea66bd2f32d6844d4ebefc4a12df367c2e5a1df3568973b28685059d2` (`231` security/AES/GEM symbols).
- **`aflturocket_2.4.2/ame_core.ko`**: SHA-256 `a8d58e8d6a0c0665da361b6c188f8d266856b703ec76961927e450acacb143af`.
- **Safety**: 100% static on-disk ELF32 dissection; zero touches on `/dev/ame*` or `.241`/`.242`/`.20`/`.250`.

## 2. Inline `ame_asic0` Hardware Cipher Pipeline (`CONFIRMED`)
- **Zero Host-CPU Data-Plane Penalty**: `cds_mac_mod.ko` (`skb_fpga_thread`) hands raw L2 frames over the DMA ring directly to the Beetle ASIC `GEM`/`L2P` hardware block, which performs inline AES encryption/decryption per CPE key index without consuming Cortex-A7 cycles.
- **Configuration Interface**: `[SECURITY]` section in `/sys/devices/platform/ame_ctrl_dev/config` (`aes_en`, `aes_key`).
