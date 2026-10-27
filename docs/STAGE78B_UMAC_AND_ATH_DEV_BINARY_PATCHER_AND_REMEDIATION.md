<!-- doc-head: Stage 78B Deterministic ELF32 MIPS Binary Patcher & Runtime Remediation for umac.ko (UMAC-BUG-01..05) and ath_dev.ko (ATHDEV-BUG-01..04) across WA.v8.7.25 and XC.v8.7.25 -->
All claims in this document carry explicit `CONFIRMED` | `INFERRED` | `UNKNOWN` | `REFUTED` labels and subsystem attribution (`proprietary airMAX/LTU module`, `Linux`, `QCA firmware`, or `hardware`).
<!-- /doc-head -->

# Stage 78B — `umac.ko` & `ath_dev.ko` Binary Patcher & Runtime Remediation (`WA` & `XC` `v8.7.25`)

## 1. Curated Patched Binary Inventory & Relocation Audit (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` (`umac.ko` & `ath_dev.ko`).
- **Evidence**: [`patch_stage78b_umac_and_ath_dev_bugs.py`](../tools/re/patch_stage78b_umac_and_ath_dev_bugs.py) · [`stage78b_umac_and_ath_dev_binary_patch_20261026.json`](../artifacts/autoresearch/stage78b_umac_and_ath_dev_binary_patch_20261026.json) · [`fmx_stage78b_umac_athdev_runtime_remediation.sh`](../artifacts/curation/fmx_stage78b_umac_athdev_runtime_remediation.sh).

| Patched Artifact (`artifacts/curation/`) | Board | Size (B) | Patches | `.rel.*` Overlaps | Source SHA-256 | Patched SHA-256 |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| `wa_8725_umac_stage78b_patched.ko` | `WA` (`AR9342`) | `2,356,432` | `5` | **`0`** (`PASS`) | `660435ed9c50f139...` | `df325f4c36749225...` |
| `xc_8725_umac_stage78b_patched.ko` | `XC` (`QCA9558`) | `2,358,768` | `5` | **`0`** (`PASS`) | `ec1df9e62f0e7664...` | `e6347b4976fd6bd7...` |
| `wa_8725_ath_dev_stage78b_patched.ko` | `WA` (`AR9342`) | `287,216` | `11` | **`0`** (`PASS`) | `9328580821a806fe...` | `af5f4f12ea44fe5f...` |
| `xc_8725_ath_dev_stage78b_patched.ko` | `XC` (`QCA9558`) | `287,216` | `11` | **`0`** (`PASS`) | `d1df65897c8ed1a0...` | `f6af982623234196...` |

---

## 2. Exact ELF32 MIPS32 Instruction Patches (`0` Relocation Overlaps) (`CONFIRMED`)

### 2.1 `umac.ko` Surgical Patches (`WA` & `XC`)
1. **`UMAC-BUG-01` — `osif_vap_init` `osif_is_multiq` (`dev+0x3dc`) Default `1 -> 3` (`.text+0x0a2874` & `.text+0x0a2984`)**:
   - **Original**: `24 02 00 01` (`addiu $v0, $zero, 1`) followed by `sb $v0, 0x3dc($s1)`.
   - **Patched**: `24 02 00 03` (`addiu $v0, $zero, 3`).
   - **Effect (`CONFIRMED`)**: Enables both `bit 0` (`0x1`: 5-subqueue WMM mapping in `osif_select_queue` `0x09e9f0..0x09ea3c` + `ol_tx_ll` per-AC subqueue `__QUEUE_STATE_XOFF` backpressure at `0x0d0e08..0x0d0ed8`) and `bit 1` (`0x2`: deep `802.1Q` `0x8100` / `PPPoE` `0x8864` inner-DSCP classification at `0x09e9a4: andi $a2, $v0, 2; jal 0x09df98`).
2. **`UMAC-BUG-02` & `UMAC-BUG-03` — `ol_ath_linux_attach` Unconditional Hardware TX Checksum Offload (`.text+0x0bc1e8` `WA` / `.text+0x0bc1ec` `XC`)**:
   - **Original**: `10 40 00 04` (`beqz $v0, skip_netif_f_csum`).
   - **Patched**: `00 00 00 00` (`nop`).
   - **Effect (`CONFIRMED`)**: Unconditionally executes `lw $v0, 0x44($s0); ori $v0, $v0, 0x12; sw $v0, 0x44($s0)` (`NETIF_F_IP_CSUM | NETIF_F_IPV6_CSUM`) on `wifi0` at attach, which `osif_vap_init` (`0x0a2960`) copies into `ath0->features`, eliminating software TCP/UDP checksum calculation on `MIPS 74Kc` while driving QCA988x HTT TX descriptor bit 29 (`0x0d18bc` / `0x0d1afc`).
3. **`UMAC-BUG-04` — `ol_ath_set_config_param` `scn->burst_dur` (`-0x1f76($s0)`) Clobber Fix (`.text+0x0b3704..0x0b3708`)**:
   - **Original**:
     - `0x0b3704`: `14 40 01 e6` (`bnez $v0, 0xb3ea0`)
     - `0x0b3708`: `8f bf 00 24` (`lw $ra, 0x24($sp)`) — redundant because `0x0b370c` jumps to `0x0b3e9c: 8fbf0024 lw $ra, 0x24($sp)`!
     - `0x0b3710`: `a6 11 e0 8a` (`sh $s1, -0x1f76($s0)`) — clobbered `-0x1f76($s0)` with 1-bit `$s1` instead of `0x1fe0` (`8160` us).
   - **Patched**:
     - `0x0b3704`: `14 40 01 e5` (`bnez $v0, 0xb3e9c`)
     - `0x0b3708`: `24 11 1f e0` (`addiu $s1, $zero, 0x1fe0`)
   - **Effect (`CONFIRMED`)**: Loads `0x1fe0` (`8160` us) into `$s1` before `0x0b3710: sh $s1, -0x1f76($s0)` while preserving `$ra` restoration at `0x0b3e9c` on both success and error paths.

### 2.2 `ath_dev.ko` Surgical Patches (`WA` & `XC`)
1. **`ATHDEV-BUG-01` — `ath_tx_init` Zero-`Minfree` Unsigned Underflow Fix (`.text+0x016728..0x016774`, 8 words)**:
   - **Original**: `24 65 ff ff` (`addiu $a1, $v1, -1`) + `2c a5 01 c0` (`sltiu $a1, $a1, 0x1c0`) across `ACBK` (`0x016728`), `ACBE` (`0x016740`), `ACVI` (`0x016758`), and `ACVO` (`0x016770`).
   - **Patched**: `24 65 00 00` (`addiu $a1, $v1, 0`) + `2c a5 01 c1` (`sltiu $a1, $a1, 0x1c1`).
   - **Effect (`CONFIRMED`)**: Accepts `0 <= Minfree <= 448` (matching `ath_txq_set_minfree` at `0x019a10`) without underflowing `0 - 1 = 0xFFFFFFFF` into the hardcoded `48 / 32 / 16` fallback.
2. **`ATHDEV-BUG-02` — `ath_cabq_update` `CABlevel` Minimum Clamp `15% -> 2%` (`.text+0x016908` & `.text+0x016914`, 2 words)**:
   - **Original**: `0x016908: 2c 43 00 0f` (`sltiu $v1, $v0, 0x0f`) and `0x016914: 24 02 00 0f` (`addiu $v0, $zero, 0x0f`).
   - **Patched**: `0x016908: 2c 43 00 02` (`sltiu $v1, $v0, 0x02`) and `0x016914: 24 02 00 02` (`addiu $v0, $zero, 0x02`).
   - **Effect (`CONFIRMED`)**: Allows `iwpriv wifi0 CABlevel 2..14` to cap multicast CABQ burst airtime down to `2%` of the beacon interval.
3. **`ATHDEV-BUG-03` — `ath_tx_start_dma` Global A-MPDU TX Buffer Cliff `48 -> 16` (`.text+0x01ba00`, 1 word)**:
   - **Original**: `2c 42 00 30` (`sltiu $v0, $v0, 0x30` — aborts **all** A-MPDU queues when `sc_txbuf_free < 48`).
   - **Patched**: `2c 42 00 10` (`sltiu $v0, $v0, 0x10` — lowers cliff to `16`).
   - **Effect (`CONFIRMED`)**: Preserves `AC_VO` (`Minfree=0`) and `AC_VI` (`Minfree=16`) A-MPDU transmission after `AC_BK` (`Minfree=48`) and `AC_BE` (`Minfree=32`) have been throttled under bulk TCP saturation.

---

## 3. Stock-Firmware Runtime Remediation (`fmx_stage78b_umac_athdev_runtime_remediation.sh`) (`CONFIRMED`)
- For unmodified stock `WA`/`XC` `airOS 8` radios where kernel modules are loaded from read-only SquashFS, [`fmx_stage78b_umac_athdev_runtime_remediation.sh`](../artifacts/curation/fmx_stage78b_umac_athdev_runtime_remediation.sh) applies the safe runtime equivalent:
  - `iwpriv ath0 set_multiq 3` (activates both `bit 0` 5-subqueue XOFF backpressure and `bit 1` VLAN/PPPoE inner-DSCP classifier).
  - `echo 1 > /sys/module/umac/parameters/enable_tx_tcp_cksum` + `ethtool -K wifi0 tx on && ethtool -K ath0 tx on`.
  - `iwpriv wifi0 aggr_swretry 4 && iwpriv wifi0 nonaggr_swretry 4 && iwpriv wifi0 CABlevel 15`.
  - Enforces WMM `Minfree` hierarchy (`ACBKMinfree=48`, `ACBEMinfree=32`, `ACVIMinfree=16`, `ACVOMinfree=1`).
