<!-- doc-head: Stage 75A Full-Stack /fullrea Binary Dissection of umac.ko and ath_dev.ko (WA AR9342 & XC QCA9558) — set_multiq, enable_tx_tcp_cksum, WMM Minfree/swretry, and UMAC-BUG-01..05 / ATHDEV-BUG-01..04 -->
All claims in this document carry explicit `CONFIRMED` | `INFERRED` | `UNKNOWN` | `REFUTED` labels and subsystem attribution (`proprietary airMAX/LTU module`, `Linux`, `QCA firmware`, or `hardware`).
<!-- /doc-head -->

# Stage 75A — `umac.ko` & `ath_dev.ko` `/fullrea` Binary Dissection (`WA.v8.7.25` & `XC.v8.7.25`)

## 1. Binary Identity & `WA` (`AR9342`) vs `XC` (`QCA9558`) Instruction Diffs (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` (`umac.ko` + `ath_dev.ko`) & `Linux` (`struct sk_buff` ABI).
- **Evidence**: [`dissect_stage75a_umac_and_ath_dev_ko.py`](../tools/re/dissect_stage75a_umac_and_ath_dev_ko.py) · [`stage75a_umac_and_ath_dev_fullrea_dissection_20261026.json`](../artifacts/autoresearch/stage75a_umac_and_ath_dev_fullrea_dissection_20261026.json).

| Module | Board | Size (B) | `.text` (B) | Symbols | SHA-256 | `.text` Word Diffs (`WA` vs `XC`) |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| `umac.ko` | `WA.v8.7.25` | `2,356,432` | `892,816` | `4,766` | `660435ed9c50f139...` | **`2,545` words** (`sk_buff` `+4 B` offset shifts `0xc4->0xc8`, `0x70->0x74`, `0x72->0x76` + `ol_ath_linux_attach` `+4 B` alignment shift) |
| `umac.ko` | `XC.v8.7.25` | `2,358,768` | `892,816` | `4,766` | `ec1df9e62f0e7664...` | Identical WMM/offload state machines & `.rodata`/`.data`/`.bss` knob tables |
| `ath_dev.ko` | `WA.v8.7.25` | `287,216` | `180,160` | `880` | `9328580821a806fe...` | **`162` words** (`sk_buff` `+4 B` shifts `0xc4->0xc8` `[124]`, `0xbc->0xc0` `[29]`, `0x72->0x76` `[6]` + GPIO/IRQ `0x21` vs `0x40`) |
| `ath_dev.ko` | `XC.v8.7.25` | `287,216` | `180,160` | `880` | `d1df65897c8ed1a0...` | Identical control flow, `.rodata`, `.data`, `.bss` |

---

## 2. `set_multiq` (`WEXT 0x019E` = `414`) & 5-Subqueue WMM Architecture (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` (`umac.ko` `osif_vap_init`, `osif_select_queue`, `ol_tx_ll`, `ieee80211_classify`) + `Linux` (`alloc_netdev_mq`).
- **VAP Creation (`osif_vap_init` at `.text+0x0a2838..0x0a2998`)**:
  - `0x0a2838: jal alloc_netdev_mq; addiu $a3, $zero, 5` (`0x24070005`) allocates **5 Linux TX subqueues** (`0..4`) per `athX` VAP and initializes `osifp->osif_is_multiq` (`dev+0x3dc` / `osifp+0x11c`) to `1` (`0x0a2878: sb $v0, 0x3dc($s1)` and `0x0a298c: sb $v0, 0x3dc($s1)`).
- **WEXT Handler (`.rodata+0x0b85c` -> `ieee80211_ioctl_setparam` at `.text+0x0976c8`)**:
  - `iwpriv ath0 set_multiq <val>` (`cmd=0x019e`, `set_args=0x4801`) executes `0x0976c8: sb $s2, 0x3dc($s3)` (`osifp->osif_is_multiq = val`); `get_multiq` (`.rodata+0x0b874`) reads `0x0932b4: lbu $v0, 0x3dc($s3)`.
- **3-Bit Bitmask State Machine in `osif_select_queue` (`.text+0x09e8a8..0x09ea4c`)**:
  - `0x09e8bc: lbu $v0, 0x3dc($a0)` loads `multiq = osifp->osif_is_multiq`. If `multiq == 0` (`0x09e8d4`), it immediately returns subqueue `0` (`0x09e8dc..0x09e8e0`) without setting `skb` TID.
  - **`Bit 2 (`0x04`) — `hook_host_ops` Exclusive Classifier (`0x09e8e4..0x09e938`)**: When `(multiq & 4) != 0`, skips `umac.ko`'s L2/VLAN/PPPoE parser and calls `hook_host_ops->classify` (`+0x5c` at `0x09e910`, i.e., `ubnt_poll_host.ko`) to populate `tid` (`0x1c($sp)`).
  - **`Bit 1 (`0x02`) — Deep L2 / `802.1Q` (`0x8100`) / `PPPoE` (`0x8864`) Inner-DSCP Gate (`0x09e93c..0x09e9a8`)**: Unwraps `0x8100` (`0x09e940`) and `0x8864` (`0x09e960`) headers and passes `multiq & 2` (`0x09e9a4: andi $a2, $v0, 2`) to `0x09df98`, then calls `__adf_nbuf_set_tid(skb, tid)` (`0x09e9e4`).
  - **`Bit 0 (`0x01`) — TID-to-Linux-Subqueue Mapper (`0x09e9ec..0x09ea3c`) & `ol_tx_ll` Per-AC Backpressure (`0x0d0e08..0x0d0ed8`)**:
    - When `(multiq & 1) == 1`, `osif_select_queue` maps `tid` (`0..7`) + `is_high_prio` (`0x18($sp)`) to Linux TX subqueues:
      - `is_high_prio != 0` $\rightarrow$ **Subqueue `4`** (`0x09ea0c: addiu $v0, $zero, 4`)
      - `tid == 0 || tid == 3` (`AC_BE`) $\rightarrow$ **Subqueue `1`** (`0x09ea14..0x09ea1c`)
      - `tid == 1 || tid == 2` (`AC_BK`) $\rightarrow$ **Subqueue `0`** (`0x09ea24..0x09ea2c`)
      - `tid == 4 || tid == 5` (`AC_VI`) $\rightarrow$ **Subqueue `2`** (`0x09ea30..0x09ea38`)
      - `tid == 6 || tid == 7` (`AC_VO`) $\rightarrow$ **Subqueue `3`** (`0x09ea3c: movz $v0, $a0, $v1`)
    - Inside `ol_tx_ll` (`.text+0x0d0bd0`), `0x0d0e08: lbu $v0, 0x11c($s2); andi $v0, $v0, 1` checks `multiq & 1`. When enabled, `0x0d0e40..0x0d0ed4` loops across the 5 subqueues and executes `ll/ins/sc` (`0x0d0e90..0x0d0e98`) on `netdev->_tx[q].state` bit 0 (`__QUEUE_STATE_XOFF`) whenever a queue's pending descriptors exceed `75%` (`max - (max >> 2)` at `0x0d0e38..0x0d0e3c`), isolating bulk TCP (`AC_BE` subqueue `1`) from starving `AC_VO`/`AC_VI` (`subqueues 3/2`).

---

## 3. `/sys/module/umac/parameters/enable_tx_tcp_cksum=1` (`.bss+0x01bca0`) (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` (`umac.ko`) + `Linux` (`NETIF_F_IP_CSUM | NETIF_F_IPV6_CSUM`) + `QCA firmware` (`QCA988x` HTT TX descriptor).
- **Why Default is `0` & How Offload Works**:
  1. `enable_tx_tcp_cksum` is allocated in `.bss+0x01bca0` (`4` bytes, default `0`), registered in `__param` via `.rodata+0x0e3d0`.
  2. During `ol_ath_linux_attach` (`.text+0x0bc1b8..0x0bc1fc`), `umac.ko` loads `enable_tx_tcp_cksum` (`0x0bc1c4: lw $v0, ($v0)`).
  3. At `0x0bc1e8: beqz $v0, 0x0bc1fc`, if `enable_tx_tcp_cksum != 0`, it sets `wifi0` `net_device->features |= 0x12` (`NETIF_F_IP_CSUM (0x02) | NETIF_F_IPV6_CSUM (0x10)` at `0x0bc1f0: lw $v0, 0x44($s0); 0x0bc1f4: ori $v0, $v0, 0x12; 0x0bc1f8: sw $v0, 0x44($s0)`).
  4. When `ath0` is created in `osif_vap_init` (`0x0a2960..0x0a296c`), `umac.ko` copies `wifi0->features` (`lw $a0, 0x44($s3)`) to `ath0->features` (`sw $a0, 0x44($s1)`).
  5. On every TX packet, `ol_tx_desc_ll` (`.text+0x0d189c`) and `ol_tx_desc_hl` (`.text+0x0d1adc`) call `__adf_nbuf_get_tx_cksum(skb)` (`ip_summed == CHECKSUM_PARTIAL`), shift the result into **bit 29** (`0x0d18bc` / `0x0d1afc`: `sll $s6, $s6, 0x1d`), and write it to word `0` of the QCA988x HTT TX descriptor (`0x0d18d8: sw $s6, ($s2)`), instructing the QCA988x Peregrine MAC/CE engine to compute the TCP/UDP checksum in hardware DMA.

---

## 4. `aggr_swretry` / `nonaggr_swretry`, `CABlevel` (`ath_cabq_update`), & `Minfree` Buffers (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` (`ath_dev.ko` + `umac.ko`) + `QCA firmware` (`WMI_PDEV_PARAM_AGGR_SW_RETRY_TH`).
- **`ath_dev.ko` Default WMM `Minfree` Reservations (`.data+0x03c8..0x03d4` & `.bss+0x00c8..0x00cc`)**:
  - `CABMinfree` (`.data+0x03c8`) = `48`; `ACVIMinfree` (`.data+0x03cc`) = `16`; `ACBEMinfree` (`.data+0x03d0`) = `32`; `ACBKMinfree` (`.data+0x03d4`) = `48`; `UAPSDMinfree` (`.bss+0x00c8`) = `0`; `ACVOMinfree` (`.bss+0x00cc`) = `0`.
  - Copied by `umac.ko` `__ath_attach` (`.text+0x09116c..0x0911ec`) into `ath_dev_param+0xac..0xc0` and enforced in `ath_tx_send_normal` (`ath_dev.ko` `.text+0x01b148..0x01b154`: `lw $a1, 0x3aa8($s7) [sc_txbuf_free]; lw $a0, 0x20($a2) [txq->axq_minfree]; sltu $a0, $a1, $a0`). When `sc_txbuf_free < axq_minfree`, the frame is dropped (`ast_tx_nobuf++` at `0x01b164..0x01b170`), reserving the final `32` `ath_buf`s for `AC_VI` (`>= 16`) and `AC_VO` (`>= 0`).
- **Software Retry & CABQ Handlers**:
  - **Offload (`umac.ko` `ol_ath_set_config_param` `.text+0x0b36c8..0x0b3710`)**: `aggr_swretry` (`0x1075`, `.rodata+0x0e698`) and `nonaggr_swretry` (`0x1074`, `.rodata+0x0e680`) call `wmi_unified_pdev_set_param(wmi, 0x29, val)` (`0x0b36cc..0x0b36d0`).
  - **Direct-Attach (`ath_dev.ko` `ath_set_config` `.text+0x0236ac..0x023730`)**: Clamps retry counts `< 64` (`0x0236b0: slti $a0, $v1, 0x40`) into `sc+0x4ba..0x4c3` and dispatches `CABlevel` (`0x1012`, `.rodata+0x02218`) to `ath_cabq_update` (`.text+0x0168d4`).

---

## 5. Catalog of 9 Newly Discovered Binary Bugs (`UMAC-BUG-01..05` & `ATHDEV-BUG-01..04`) (`CONFIRMED`)

| Bug ID | Module & Offset | Severity | Exact Binary Mechanism & Remediation |
| :--- | :--- | :--- | :--- |
| **`UMAC-BUG-01`** | `umac.ko` `.text+0x0a2878`, `0x09e9a4`, `0x0d0e08` | `HIGH` | **`set_multiq=1` Default Disables Deep VLAN/PPPoE DSCP Parser (`Bit 1`)**: `osif_vap_init` sets `osif_is_multiq=1` (`bit 0` only). At `0x09e9a4` (`andi $a2, $v0, 2`), `bit 1` (`0x2`) is `0`, skipping inner VLAN/PPPoE DSCP parsing; setting `multiq=0` disables `ol_tx_ll` per-AC subqueue XOFF (`0x0d0e08`). **Fix**: `iwpriv ath0 set_multiq 3` (`0x1 \| 0x2`). |
| **`UMAC-BUG-02`** | `umac.ko` `.bss+0x01bca0`, `.text+0x0bc1e8`, `0x0d189c` | `HIGH` | **`enable_tx_tcp_cksum=0` Default Wastes MIPS 74Kc CPU While Still Running Descriptor Logic**: `.bss+0x01bca0` defaults to `0`, skipping `dev->features \|= 0x12` (`0x0bc1f4`), yet `ol_tx_desc_ll` (`0x0d189c`) and `ol_tx_desc_hl` (`0x0d1adc`) still call `__adf_nbuf_get_tx_cksum` on every frame. **Fix**: Enable `enable_tx_tcp_cksum=1`. |
| **`UMAC-BUG-03`** | `umac.ko` `.text+0x0bc1c4`, `0x0a2960` | `MEDIUM` | **Late `sysfs` Write to `enable_tx_tcp_cksum` Fails to Update `dev->features` (`+0x44`)**: `enable_tx_tcp_cksum` is read only once during `ol_ath_linux_attach` (`0x0bc1c4`). Post-boot `sysfs` writes do not update `wifi0->features` or `ath0->features`. **Fix**: Pass at `insmod` or run `ethtool -K ath0 tx on`. |
| **`UMAC-BUG-04`** | `umac.ko` `.text+0x0b36e8..0x0b3710` | `MEDIUM` | **`aggr_swretry` Handler Corrupts `scn->tx_sendq_maxsize` (`-0x1f76($s0)`)**: After sending WMI param `0x28` (`0x1fe0 = 8160` at `0x0b3700`), delay slot `0x0b3710` executes `sh $s1, -0x1f76($s0)`, storing the retry count `$s1` instead of `0x1fe0`. |
| **`UMAC-BUG-05`** | `umac.ko` `.text+0x0b37f4..0x0b3808`, `0x0914ec` | `MEDIUM` | **`AMPDUFrames` (`0x1008`) & `AMPDULim` (`0x1007`) Are Host-Only Stubs on `ol_ath` Offload**: Write `-0x1d3c($s0)` / `-0x1d40($s0)` without calling `wmi_unified_pdev_set_param`; `__ath_attach` (`0x0914ec`) has a `3x msleep(1000)` loop when `ubnthal_GetSystemId` fails. |
| **`ATHDEV-BUG-01`** | `ath_dev.ko` `.text+0x016724..0x01677c`, `0x0199c8` | `HIGH` | **Unsigned Underflow (`val - 1 < 0x1c0`) Rejects `Minfree=0` & `ath_txq_set_minfree` Ignores `CABQ`**: `addiu $a1, $v1, -1; sltiu $a1, $a1, 0x1c0; movz $v1, $v0, $a1` treats `0` as `0xFFFFFFFF >= 448` and forces `48/32/16`; `0x0199c8` (`addiu $v0, $a1, -2; sltiu $v0, $v0, 2`) returns early for `HAL_TX_QUEUE_CAB` (`2`). **Fix**: Use `Minfree=1` instead of `0`. |
| **`ATHDEV-BUG-02`** | `ath_dev.ko` `.text+0x016904..0x016928` | `MEDIUM` | **`ath_cabq_update` Hard-Clamps `CABlevel` (`sc_cabq_maxdur`) to `[15%, 96%]`**: `0x016908: sltiu $v1, $v0, 0x0f` overwrites any value `< 15%` with `15%` (`0x0f`), preventing reduction of multicast CABQ burst airtime below `15%` of beacon interval via `iwpriv`. |
| **`ATHDEV-BUG-03`** | `ath_dev.ko` `.text+0x01b9fc..0x01ba04` | `HIGH` | **Hardcoded `sc_txbuf_free < 48` (`0x30`) Cliff in `ath_tx_start_dma` Blocks All A-MPDU Queues**: `0x01ba00: sltiu $v0, $v0, 0x30` aborts A-MPDU transmission for **all** WMM ACs (including `AC_VI` with `Minfree=16` and `AC_VO` with `Minfree=0`) whenever `sc_txbuf_free < 48`, defeating WMM buffer reservations for aggregated traffic. |
| **`ATHDEV-BUG-04`** | `ath_dev.ko` `.text+0x027c00..0x027c78` | `LOW` | **Unconditional GPIO `1` + Threaded IRQ `0x21` Registration in `ath_spectral_filter_init`**: Requests GPIO `1` interrupt and threaded IRQ `33` (`0x21`) with `IRQF_ONESHOT` (`0x20`). |
