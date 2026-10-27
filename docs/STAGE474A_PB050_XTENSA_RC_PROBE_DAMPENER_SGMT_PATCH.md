<!-- doc-head: STAGE474A_PB050_XTENSA_RC_PROBE_DAMPENER_SGMT_PATCH.md preserved document content -->
<!-- /doc-head -->


# Stage 474A — `PB050-RC-PROBE-DAMPEN` Surgical `SGMT` Patch Profile (`QCA988x` Xtensa)

- **Status**: `CONFIRMED` (`7` `SGMT` Firmware Images Patched & Round-Trip Verified; `live_devices_touched = False`)
- **Attribution**: `QCA firmware` (`SgmtSurgicalPatcher` + `BMI_LZ` Lossless Re-Packer)
- **Tool**: [`build_stage474a_pb050_xtensa_rc_probe_dampener_sgmt_patch.py`](../tools/firmware/build_stage474a_pb050_xtensa_rc_probe_dampener_sgmt_patch.py)
- **Artifact**: [`stage474a_pb050_xtensa_rc_probe_dampener_sgmt_patch.json`](../artifacts/autoresearch/stage474a_pb050_xtensa_rc_probe_dampener_sgmt_patch.json)

---

## 1. Engineering Problem & Surgical Patch Architecture

From `Stage 473A`, stock `QCA988x` target firmware (`10.1.467-ct` in OpenWrt and `10.2.4` in `WA`/`XC` `airOS 8`) suffers from two coupled rate-control pathologies on outdoor reflective links:
1. **Suicidal Upward MCS Probing Every 32 Packets**:
   - In `WMI_PEER_ASSOC_CMDID`, the first peer association overwrites `g_rc_probe_pkt_threshold = 32` (`movi.n reg, 32`) and `g_rc_probe_period_ms = 5000` (`0x1388` from `seg[0]` `.lit4`).
   - On links with near-field multipath or selective fading where high-order VHT MCS (`MCS 8`/`9`) fails, probing upward every `32` packets wastes `>3%` of airtime and triggers BA window head-of-line blocking stalls.
2. **Instantaneous `XRETRY` "MCS Cliff" (`+30%` PER Jump per Failed PPDU)**:
   - In Ubiquiti `10.2.4` (`WA`/`XC`), `g_default_xretry_per_penalty = 30` (`0x0040da78` in `WA.v8.7.25` PtP) adds `+30%` directly to `peer_rc->per[rate_idx]` (`0x0099e956..0x0099e96a`) whenever a PPDU exhausts hardware retries, causing just `2` consecutive `XRETRY` PPDUs (`+60%`) to breach `g_rc_rate_max_per_thr = 65` (`0x0040da7c`) and collapse the link to lower MCS.

### Why `PB050-RC-PROBE-DAMPEN` Uses a 3-Part Surgical `seg[2]` + `seg[3]` Design
- **Why NOT mutate `0x00001388` in `seg[0]` (`.lit4`)?** Because `lit@0x009805ec` (OpenWrt) and `lit@0x009805a0` / `0x00980598` (`WA`/`XC`) are shared constant-pool entries referenced by multiple unrelated functions in `seg[3]`.
- **Why NOT replace `movi.n reg, 32` (`2` bytes) with `movi reg, 512` (`3` bytes)?** Because Xtensa `movi.n` only encodes a 7-bit immediate (`-32..95`), and expanding a 2-byte instruction to 3 bytes shifts every subsequent instruction in `seg[3]`, breaking all PC-relative `call8` and `l32r` offsets.
- **The Surgical Solution (`PB050-RC-PROBE-DAMPEN`)**:
  1. **Patch `seg[2]` (`.data`) 32-bit globals directly**:
     - `g_rc_probe_period_ms`: `256` $\to$ `15000` ms (`0x00003a98`)
     - `g_rc_probe_pkt_threshold`: `64` $\to$ `512` packets (`0x00000200`)
  2. **Neutralize the `WMI_PEER_ASSOC_CMDID` overwrite in `seg[3]` (`.text`)**:
     - Replace the two 2-byte narrow store instructions (`s32i.n a12, a13, 0; s32i.n a10, a11, 0` = `c9 0d a9 0b` in OpenWrt `@ 0x0098a3eb`; `f9 08 d9 0e` in `WA`/`XC` `@ 0x0098a028` / `0x00989fc4`) with two 2-byte narrow self-moves (`mov.n r, r` = `cd 0c ad 0a` / `fd 0f dd 0d`).
     - Preserves exact segment byte length (`len(patched_seg) == len(orig_seg)`), zero register clobber, and zero literal drift.
  3. **Patch `seg[2]` (`.data`) `XRETRY` Hysteresis Globals (`WA`/`XC` `10.2.4`)**:
     - `g_default_xretry_per_penalty`: `30` $\to$ `12` (`0x0000000c`)
     - `g_rc_rate_max_per_thr`: `65` $\to$ `72` (`0x00000048`)

---

## 2. Verified `PB050-RC-PROBE-DAMPEN` `SGMT` Images (`0` Signature Bytes)

| Target ID | Probe `.data` VA (`seg[2]`) | `WMI_PEER_ASSOC` Guard VA (`seg[3]`) | `XRETRY` / `MAX_PER` VA (`seg[2]`) | Repacked Size (B) | Repacked `SGMT` `SHA-256` (Prefix) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`OpenWrt_10.1.467-ct_IE3`** | `0x0040c24c` (`15000`, `512`) | `0x0098a3eb` (`c90da90b` $\to$ `cd0cad0a`) | Mask ROM (`*0x0040940c`) | `200,943` | `30acdd3a92d5783a` |
| **`WA.v8.7.25_ptp`** | `0x0040d4e0` (`15000`, `512`) | `0x0098a028` (`f908d90e` $\to$ `fd0fdd0d`) | `0x0040da78` (`12`, `72`) | `218,500` | `83ffcd3f9e63e6a5` |
| **`WA.v8.7.25_ptmp_ap`** | `0x0040d9a0` (`15000`, `512`) | `0x00989fc4` (`f908d90e` $\to$ `fd0fdd0d`) | `0x0040df38` (`12`, `72`) | `255,671` | `45de8697625d88c1` |
| **`WA.v8.7.25_ptmp_sta`** | `0x0040da50` (`15000`, `512`) | `0x00989fc4` (`f908d90e` $\to$ `fd0fdd0d`) | `0x0040dfe8` (`12`, `72`) | `237,995` | `12a95004388f8ea1` |
| **`XC.v8.7.25_ptp`** | `0x0040d500` (`15000`, `512`) | `0x0098a028` (`f908d90e` $\to$ `fd0fdd0d`) | `0x0040da98` (`12`, `72`) | `219,369` | `ef0bbb913a43e098` |
| **`XC.v8.7.25_ptmp_ap`** | `0x0040d9c0` (`15000`, `512`) | `0x00989fc4` (`f908d90e` $\to$ `fd0fdd0d`) | `0x0040df58` (`12`, `72`) | `256,561` | `42654ad9105e66d1` |
| **`XC.v8.7.25_ptmp_sta`** | `0x0040da70` (`15000`, `512`) | `0x00989fc4` (`f908d90e` $\to$ `fd0fdd0d`) | `0x0040e008` (`12`, `72`) | `238,874` | `c6f3429de3277544` |
