<!-- doc-head: STAGE100D_XC_BUG03_HS_UART_DISASM_AND_LTU_VERIFY.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 100D — Cross-Platform Disassembly of `XC-BUG-03` (`ath_hs_uart` at `0x80122d40..0x80123340`) & Live `AF-LTU` Read-Only SUID / `/dev/ame_*` Verification

- **Status**: `CONFIRMED` (`<memorymaster-id>`, `claim_id=152909`)
- **Attribution**: `Linux` (`QCA LSDK 2.6.32.68` `vmlinux` `drivers/serial/ath_hs_uart.c` on `QCA9558` `2XC.v8.7.11` & `XC.v8.7.25`) + `proprietary LTU module` (`afltu.v2.4.0` SUID binaries & `14` `/dev/ame_*` character devices)
- **Artifacts & Harness**:
  - Harness: [`tools/bench/run_stage100d_xc_bug03_hs_uart_and_ltu_suid_verify.py`](<repo>/tools/bench/run_stage100d_xc_bug03_hs_uart_and_ltu_suid_verify.py)
  - Receipt: [`artifacts/autoresearch/stage100d_xc_bug03_hs_uart_and_ltu_suid_verify.json`](<repo>/artifacts/autoresearch/stage100d_xc_bug03_hs_uart_and_ltu_suid_verify.json)
  - Verification Tests: [`tests/test_stage100d_xc_bug03_hs_uart.py`](<repo>/tests/test_stage100d_xc_bug03_hs_uart.py)

---

## 1. Cross-Platform Disassembly of `XC-BUG-03` (`ath_hs_uart_*`) Across `2XC.v8.7.11` (`.251`) and `5XC.v8.7.25` (`.198`) (`CONFIRMED`)

Read-only extraction of `1,536` bytes of live kernel `.text` at physical address `0x00122d40..0x00123340` (`KSEG0` `0x80122d40..0x80123340`) on both **`Rocket 2AC Prism` (`198.18.0.48`, `2XC.v8.7.11`)** and **`Rocket 5AC Prism Gen2` (`198.18.0.64`, `XC.v8.7.25`)** proved **100% byte-for-byte identity (`0` differing bytes)**:
- **`SHA256`**: `3e92126565d4b174a26ef1e138fd8abe5cd1f82091bc5b7df1f4fe74fd1867e6` (both `2XC.v8.7.11` and `XC.v8.7.25`)
- **`MD5`**: `586a2f646ee7992829072d97148f31f0` (both `2XC.v8.7.11` and `XC.v8.7.25`)

### 1.1 Exact Instruction-Level Proof of `ath_hs_uart_open` (`0x80122d40`) & `ath_hs_uart_close` (`0x80122d5c`) (`CONFIRMED`)

```text
=== ath_hs_uart_open (0x80122d40..0x80122d5c, 28 bytes) ===
0x80122d40: 8c830008  lw     $v1, 8($a0)          # $v1 = tty->driver
0x80122d44: 8c840010  lw     $a0, 0x10($a0)       # $a0 = tty->index
0x80122d48: 2402ffed  addiu  $v0, $zero, -0x13    # $v0 = -ENODEV (-19)
0x80122d4c: 8c630060  lw     $v1, 0x60($v1)       # $v1 = driver->num
0x80122d50: 0083182a  slt    $v1, $a0, $v1        # $v1 = (tty->index < driver->num)
0x80122d54: 03e00008  jr     $ra
0x80122d58: 0003100b  movn   $v0, $zero, $v1      # return (index < num) ? 0 : -ENODEV

=== ath_hs_uart_close (0x80122d5c..0x80122d64, 8 bytes) ===
0x80122d5c: 03e00008  jr     $ra                  # Empty stub! Never masks ATH_HS_UART_INT_EN (0xb8500010)
0x80122d60: 00000000  nop
```

### 1.2 Exact MMIO Register Dissection in `ath_hs_uart_init.part.1` (`0x80123064`) & `ath_hs_uart_isr` (`0x80123044` $\rightarrow$ `0x80122efc`) (`CONFIRMED`)

| MMIO Register (KSEG1 / Phys) | Instruction Address & Opcode | Exact Hardware Operation |
| :--- | :--- | :--- |
| **`0xb8500000` (`ATH_HS_UART_DATA`)** | `0x80122f18: 8c430000 lw $v1, ($v0)`<br>`0x80122f28: ae110000 sw $s1, ($s0)` | Reads RX byte + bit 8 (`0x100` `RX_VALID`); writes `0x100` back to pop RX FIFO and pushes byte to `tty_flip_buffer_push` (`0x80111378`). |
| **`0xb8500004` (`ATH_HS_UART_CS`)** | `0x801231b8: 24022188 addiu $v0, $zero, 0x2188`<br>`0x801231bc: ae020004 sw $v0, 4($s0)` | Initializes High-Speed UART control/status mode register to `0x2188`. |
| **`0xb8500008` (`ATH_HS_UART_CLK`)** | `0x801231b0: ae030008 sw $v1, 8($s0)` | Programs baud clock step/scale divider for `9600` baud GPS NMEA feed. |
| **`0xb850000c` (`ATH_HS_UART_INT_STATUS`)** | `0x80122fc8: 2402ffff addiu $v0, $zero, -1`<br>`0x80122fcc: ae02000c sw $v0, 0xc($s0)` | Writes `0xffffffff` (W1C) to clear pending UART interrupts inside ISR. |
| **`0xb8500010` (`ATH_HS_UART_INT_EN`)** | `0x80123108: ae030010 sw $v1, 0x10($s0)` (`0x101`)<br>`0x8012301c: ae020010 sw $v0, 0x10($s0)` (`0x101`) | Boot init sets `0x101` (`RX_VALID_INT \| TX_EMPTY_INT`) and the ISR unconditionally re-arms `0x101` on exit (`0x8012301c`). Because `ath_hs_uart_close` (`0x80122d5c`) is `jr $ra; nop`, `IRQ 22 hs-uart` fires at `~183.5 IRQs/sec` (`34.3M` interrupts) forever. |

---

## 2. Live Read-Only `AF-LTU` SUID Inode & `/dev/ame_*` Verification on `LTU-Lite #1` (`198.18.0.63`) (`CONFIRMED`)

Executed strictly read-only metadata checks (`ls -ln`, `md5sum`, `uname -a`) on live `LTU-Lite #1` (`198.18.0.63`, `afltu.v2.4.0`, `board.sysid=0xae08`, `Linux 3.14.65 #1 SMP PREEMPT RT Mon Aug 11 12:51:08 UTC 2025 armv7l GNU/Linux`):

### 2.1 SUID-Root (`-rwsr-xr-x 0:0`) Binaries (`CONFIRMED`)
| Binary Path | Permissions & Owner (`ls -ln`) | Size (Bytes) | MD5 Checksum |
| :--- | :--- | ---: | :--- |
| `/bin/cent-mgmt-cli` | `-rwsr-xr-x 1 0 0` | `14,796` | `1228031785acc442f8dc26dff81d1d25` |
| `/bin/ame-debug-rxcap` | `-rwsr-xr-x 1 0 0` | `53,990` | `694e8c20fc7a511dd4db196a3c26bde7` |
| `/bin/ame-debug-sched` | `-rwsr-xr-x 1 0 0` | `90,855` | `dc0e6e60f8cf97f67c55552cc66ef741` |
| `/bin/ame-debug-txcmd-dump` | `-rwsr-xr-x 1 0 0` | `4,846` | `5061fcc0040a34b5781853d9767d7ee9` |

### 2.2 Live `/dev/ame_*` Character Device Nodes (`14` Devices, `crw-rw---- 0:0`) (`CONFIRMED`)
- **Dedicated Major Numbers (`239..243`)**: `/dev/ame_dfs_dev` (`239, 0`), `/dev/ame_fty_dev` (`240, 0`), `/dev/ame_debug_dev` (`241, 0`), `/dev/ame_bist_dev` (`242, 0`), `/dev/ame_ctrl_dev` (`243, 0`).
- **Misc Character Devices (`Major 10, Minors 51..59`)**: `/dev/ame_s2p_sys` (`10, 51`), `/dev/ame_s2p_ctrl` (`10, 52`), `/dev/ame_p2s_ctrl` (`10, 53`), `/dev/ame_s2p_bcon` (`10, 54`), `/dev/ame_p2s_bcon` (`10, 55`), `/dev/ame_s2p_mgmt` (`10, 56`), `/dev/ame_p2s_mgmt` (`10, 57`), `/dev/ame_s2p_data` (`10, 58`), `/dev/ame_p2s_data` (`10, 59`).
