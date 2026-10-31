<!-- doc-head: STAGE242A_GUARIDA_STAGE0_MODE_B_KITS.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 242A — Pre-Staged `Mode B` `rc.poststart` & `system.cfg` Patch Bundles (`tools/guarida_stage0_kits/`)

## 1. Checksum-Verified Stage 0 Kit Inventory (`Operator-Gated`, `0` Live Writes)

| Node | IP | `board.sysid` | Script Path | SHA-256 Prefix |
| :--- | :--- | :--- | :--- | :--- |
| `almafuerte_60` | `198.18.0.3` | `0xe3d6` | `tools/guarida_stage0_kits/almafuerte_60_mode_b.sh` | `dd98228caab54b0a...` |
| `guarida_61` | `198.18.0.4` | `0xe3d6` | `tools/guarida_stage0_kits/guarida_61_mode_b.sh` | `c4c76e9a7f23f20a...` |
| `panel2_82` | `198.18.0.5` | `0xe8e5` | `tools/guarida_stage0_kits/panel2_82_mode_b.sh` | `6281429c1824f6d5...` |
| `panel3_83` | `198.18.0.6` | `0xe8e5` | `tools/guarida_stage0_kits/panel3_83_mode_b.sh` | `dc6aa206832d0faa...` |

## 2. Exact Knobs Staged Per Node (`CONFIRMED`)

1. **Immediate Zero-Drop Runtime Tuning (`/etc/persistent/rc.poststart`)**:
   - `vm.min_free_kbytes = 4096` (up from `1019`, preventing atomic skb allocation failures during `ath0` DMA refills)
   - `net.core.netdev_max_backlog = 2048` (up from `1000`)
   - `net.core.rmem_max = 4194304` & `wmem_max = 4194304`
   - `ath0` & `eth0` `tx_queue_len = 500` (down from `1000` to cap `pfifo_fast`/`mq` standing queue latency)
2. **Staged Maintenance-Window `/tmp/system.cfg` Fixes**:
   - **`.60` & `.61` (`0xe3d6` Backhaul)**: `ackdistance=4050`, `acktimeout=54`, `polling_11ac_11n_compat=0`, `.61` `freq=5355`, `txpower=20`, `airview.status=disabled`.
   - **`.82` (`0xe8e5` `Panel2`)**: `ackdistance=3150`, `acktimeout=45`, `atpc.status=enabled`, `txpower=20`, `freq=5825`, `airview.status=disabled`.
   - **`.83` (`0xe8e5` `Panel3`)**: `polling=enabled`, `polling_ff_flex=1`, `ackdistance=3150`, `acktimeout=45`, `txpower=20`, `freq=5745`, `airview.status=disabled`.
