<!-- doc-head: STAGE473A_OPENWRT_CT_VS_STOCK_XTENSA_RC_GLOBALS_MAP.md preserved document content -->
<!-- /doc-head -->


# Stage 473A — OpenWrt `10.1.467-ct` vs Stock `airOS 8` (`10.2.4`) `QCA988x` Xtensa Rate-Control Globals Map

- **Status**: `CONFIRMED` (`100%` Offline Binary Dissection across `10` `QCA988x` `SGMT` Firmware Images; `live_devices_touched = False`)
- **Attribution**: `QCA firmware` (`ath10k` `10.1.467-ct` `IE 3` vs Ubiquiti `10.2.4` `athwlan_AR9888v2_*_bin` in `WA.v8.7.25`, `XC.v8.7.25`, `WA.v8.7.11`)
- **Tool**: [`dissect_stage473a_openwrt_ct_vs_stock_xtensa_rc_globals_map.py`](../tools/re/dissect_stage473a_openwrt_ct_vs_stock_xtensa_rc_globals_map.py)
- **Artifact**: [`stage473a_openwrt_ct_vs_stock_xtensa_rc_globals_map.json`](../artifacts/autoresearch/stage473a_openwrt_ct_vs_stock_xtensa_rc_globals_map.json)

---

## 1. Executive Summary & Architectural Discoveries

1. **Two-Stage Initialization of `g_rc_probe_period_ms` and `g_rc_probe_pkt_threshold` (`CONFIRMED`, `QCA firmware`)**:
   - Across **both** OpenWrt `10.1.467-ct` (`IE 3`) and all 9 Ubiquiti `10.2.4` (`WA`/`XC`) target firmwares, the rate-control upward-MCS probing globals are initialized in **two distinct phases**:
     1. **Boot `.data` (`seg[2]`) Initialization**: The `SGMT` `.data` segment initializes `g_rc_probe_period_ms = 256` (`0x00000100` ms) and `g_rc_probe_pkt_threshold = 64` (`0x00000040` packets), with `g_rc_probe_enable = 1` in OpenWrt `10.1.467-ct` and `3` in Ubiquiti `10.2.4`.
     2. **First-Peer Association Override (`WMI_PEER_ASSOC_CMDID`)**: Inside `WMI_PEER_ASSOC_CMDID` (`0x0098a3db..0x0098a3ed` in OpenWrt `10.1.467-ct` `IE 3`; `0x0098a018..0x0098a02a` in `WA.v8.7.25` PtP), when the first peer associates (`b7_7` guard on `peer_count`), the firmware **overwrites** `*g_rc_probe_period_ms = 5000` (`0x00001388`, loaded via `l32r` from `seg[0]` `.lit4`) and `*g_rc_probe_pkt_threshold = 32` (`movi.n reg, 32` in `seg[3]` `.text`).
   - **Implication for `PB050-RC-PROBE-DAMPEN` (`Stage 474A`)**: A surgical `SGMT` patch must patch **both** the `seg[2]` `.data` initial words AND the `WMI_PEER_ASSOC_CMDID` override in `seg[0]`/ `seg[3]` (or suppress the `WMI_PEER_ASSOC_CMDID` overwrite) so that the first peer association does not clobber the dampened probe parameters back to `32` packets / `5000` ms.

2. **Mask ROM vs RAM Rate-Control Vtable Split (`OpenWrt 10.1.467-ct` vs Ubiquiti `10.2.4`) (`CONFIRMED`, `QCA firmware`)**:
   - In **Ubiquiti `10.2.4` (`WA.v8.7.25`, `XC.v8.7.25`, `WA.v8.7.11`)**, the target firmware replaces the Mask ROM rate-control module with a RAM-resident implementation (`0x0099d2f4..0x0099f56c` in `WA.v8.7.25` PtP) backed by a contiguous RAM `g_rc_ctx` block (`0x0040da10..0x0040da84` in `WA.v8.7.25` PtP):
     - `base + 0x04`: `g_default_no_ack_wifi_thr = 3` (read at `0x0099d689`)
     - `base + 0x10..0x5c`: `g_ratectrl_ops_vtable` (`20` function pointers)
     - `base + 0x64`: `g_rc_per_ceiling = 80` (`80%` PER ceiling clamp, read at `0x0099e565`, `0x0099e7d8`, `0x0099e95f`)
     - `base + 0x68`: `g_default_xretry_per_penalty = 30` (`+30%` instantaneous PER jump per `XRETRY` PPDU, read at `0x0099e95c`)
     - `base + 0x6c`: `g_rc_rate_max_per_thr = 65` (`65%` PER step-down threshold, read at `0x0099e673`)
   - In **OpenWrt `10.1.467-ct` (`IE 3`)**, boot initialization at `0x0098845f..0x00988468` invokes Mask ROM `0x00947a44(0x004003c0)` and `0x0094821c(0x004003cc)` referenced through `*0x0040940c` (with RAM hook table at `0x0040c698`), while keeping the probe control block in RAM `seg[2]` at `0x0040c240..0x0040c25c`.

---

## 2. Cross-Firmware `QCA988x` Xtensa Rate-Control Globals Table (`10` Images)

| Firmware Image | `g_rc_probe_period_ms` (`seg[2]` / `seg[0]` `.lit4`) | `g_rc_probe_pkt_threshold` (`seg[2]` / `seg[3]` `movi.n`) | `g_rc_probe_enable` (`seg[2]` / Init) | `g_default_xretry_per_penalty` (`seg[2]` / Val) | `g_rc_rate_max_per_thr` (`seg[2]` / Val) | `g_default_no_ack_wifi_thr` (`seg[2]` / Val) | `g_dbg_max_sw_retry` (`seg[2]` / Val) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`OpenWrt 10.1.467-ct` (`IE 3`)** | `0x0040c24c` (`256` $\to$ `5000` @ `0x009805ec`) | `0x0040c250` (`64` $\to$ `32` @ `0x0098a3e7`) | `0x0040c254` (`1` $\to$ `1`) | `ROM+0x68` (`*0x0040940c`, `30`) | `ROM+0x6c` (`*0x0040940c`, `65`) | `ROM+0x04` (`*0x0040940c`, `3`) | `0x0040c140` (WAL TX struct) |
| **`WA.v8.7.25` `ptp`** | `0x0040d4e0` (`256` $\to$ `5000` @ `0x009805a0`) | `0x0040d4e4` (`64` $\to$ `32` @ `0x0098a024`) | `0x0040d4e8` (`3` $\to$ `1`) | `0x0040da78` (`30`) | `0x0040da7c` (`65`) | `0x0040da14` (`3`) | `0x0040d364` (`41`) |
| **`WA.v8.7.25` `ptmp_ap`** | `0x0040d9a0` (`256` $\to$ `5000` @ `0x00980598`) | `0x0040d9a4` (`64` $\to$ `32` @ `0x00989fc0`) | `0x0040d9a8` (`3` $\to$ `1`) | `0x0040df38` (`30`) | `0x0040df3c` (`65`) | `0x0040ded4` (`3`) | `0x0040d824` (`41`) |
| **`WA.v8.7.25` `ptmp_sta`** | `0x0040da50` (`256` $\to$ `5000` @ `0x00980598`) | `0x0040da54` (`64` $\to$ `32` @ `0x00989fc0`) | `0x0040da58` (`3` $\to$ `1`) | `0x0040dfe8` (`30`) | `0x0040dfec` (`65`) | `0x0040df84` (`3`) | `0x0040d8d4` (`41`) |
| **`XC.v8.7.25` `ptp`** | `0x0040d500` (`256` $\to$ `5000` @ `0x009805a0`) | `0x0040d504` (`64` $\to$ `32` @ `0x0098a024`) | `0x0040d508` (`3` $\to$ `1`) | `0x0040da98` (`30`) | `0x0040da9c` (`65`) | `0x0040da34` (`3`) | `0x0040d384` (`41`) |
| **`XC.v8.7.25` `ptmp_ap`** | `0x0040d9c0` (`256` $\to$ `5000` @ `0x00980598`) | `0x0040d9c4` (`64` $\to$ `32` @ `0x00989fc0`) | `0x0040d9c8` (`3` $\to$ `1`) | `0x0040df58` (`30`) | `0x0040df5c` (`65`) | `0x0040def4` (`3`) | `0x0040d844` (`41`) |
| **`XC.v8.7.25` `ptmp_sta`** | `0x0040da70` (`256` $\to$ `5000` @ `0x00980598`) | `0x0040da74` (`64` $\to$ `32` @ `0x00989fc0`) | `0x0040da78` (`3` $\to$ `1`) | `0x0040e008` (`30`) | `0x0040e00c` (`65`) | `0x0040dfa4` (`3`) | `0x0040d8f4` (`41`) |
| **`WA.v8.7.11` `ptp`** | `0x0040d3b0` (`256` $\to$ `5000` @ `0x00980598`) | `0x0040d3b4` (`64` $\to$ `32` @ `0x00989f9c`) | `0x0040d3b8` (`3` $\to$ `1`) | `0x0040d948` (`30`) | `0x0040d94c` (`65`) | `0x0040d8e4` (`3`) | `0x0040d234` (`41`) |
| **`WA.v8.7.11` `ptmp_ap`** | `0x0040d930` (`256` $\to$ `5000` @ `0x00980598`) | `0x0040d934` (`64` $\to$ `32` @ `0x00989f9c`) | `0x0040d938` (`3` $\to$ `1`) | `0x0040dec8` (`30`) | `0x0040decc` (`65`) | `0x0040de64` (`3`) | `0x0040d7b4` (`41`) |
| **`WA.v8.7.11` `ptmp_sta`** | `0x0040d920` (`256` $\to$ `5000` @ `0x00980598`) | `0x0040d924` (`64` $\to$ `32` @ `0x00989f9c`) | `0x0040d928` (`3` $\to$ `1`) | `0x0040deb8` (`30`) | `0x0040debc` (`65`) | `0x0040de54` (`3`) | `0x0040d7a4` (`41`) |

---

## 3. Instruction-Level Proofs

### 3.1 `WMI_PEER_ASSOC_CMDID` Probe Globals Override (`OpenWrt 10.1.467-ct` vs `WA.v8.7.25` PtP)
```text
# OpenWrt 10.1.467-ct (IE 3) @ 0x0098a3d8..0x0098a3ed:
0x0098a3d8: 977d13  b7_7   a13, a9, 0x0098a3ef         ; if (peer_count != 0) skip
0x0098a3db: b17a15  l32r   a11, 0x009805e8 [0x0040c24c]; &g_rc_probe_period_ms
0x0098a3de: a17b15  l32r   a10, 0x009805ec [0x00001388]; 5000 ms
0x0098a3e1: d17c15  l32r   a13, 0x009805f0 [0x0040c250]; &g_rc_probe_pkt_threshold
0x0098a3e4: e17d15  l32r   a14, 0x009805f4 [0x0040c254]; &g_rc_probe_enable
0x0098a3e7: 2c0c    movi.n a12, 32                     ; 32 packets
0x0098a3e9: 490e    s32i.n a4,  a14, 0                 ; g_rc_probe_enable = 1
0x0098a3eb: c90d    s32i.n a12, a13, 0                 ; g_rc_probe_pkt_threshold = 32
0x0098a3ed: a90b    s32i.n a10, a11, 0                 ; g_rc_probe_period_ms = 5000
```

### 3.2 `XRETRY` Additive PER Penalty (`+30%`) and Step-Down Threshold (`65%`) in `WA.v8.7.25` PtP
```text
# Step-down check @ 0x0099e66d..0x0099e676:
0x0099e66d: f21516  l16ui  a15, a5, 44                 ; a15 = peer_rc->per[rate_idx]
0x0099e670: 91ea16  l32r   a9,  0x00980ba8 [0x0040da10]; &g_rc_ctx
0x0099e673: 92291b  l32i   a9,  a9, 108 (0x6c)         ; a9  = g_rc_rate_max_per_thr (65)
0x0099e676: 973f4a  bltu   a15, a9, 0x0099e6c4         ; if (per < 65) keep rate; else step down!

# XRETRY additive penalty @ 0x0099e956..0x0099e96a:
0x0099e956: f1ea16  l32r   a15, 0x00980ba8 [0x0040da10]; &g_rc_ctx
0x0099e959: 821516  l16ui  a8,  a5, 44                 ; a8  = peer_rc->per[rate_idx]
0x0099e95c: 922f1a  l32i   a9,  a15, 104 (0x68)        ; a9  = g_default_xretry_per_penalty (30)
0x0099e95f: f22f19  l32i   a15, a15, 100 (0x64)        ; a15 = g_rc_per_ceiling (80)
0x0099e962: 9a88    add.n  a8,  a8, a9                 ; per += 30
0x0099e964: 8080f4  extui  a8,  a8, 0, 16
0x0099e967: 80ff63  minu   a15, a15, a8                ; per = min(80, per + 30)
0x0099e96a: f25516  s16i   a15, a5, 44                 ; peer_rc->per[rate_idx] = per
```
