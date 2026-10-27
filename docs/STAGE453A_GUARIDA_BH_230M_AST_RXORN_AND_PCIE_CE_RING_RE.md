<!-- doc-head: STAGE453A_GUARIDA_BH_230M_AST_RXORN_AND_PCIE_CE_RING_RE.md preserved document content -->
<!-- /doc-head -->



# Stage 453A — Binary Dissection of `Guarida-BH (.61)` `230,722,380` `ast_rxorn` (`rx overrun`) & PCIe/CE/HTT Ring Telemetry in `umac.ko` & `bin/athbox`

## 1. Executive Summary (`CONFIRMED`)
- **Claim**: `CONFIRMED` (`proprietary airMAX/LTU module` + `ath10k` + `QCA firmware`, `0` writes performed).
- **Discovery (`FMX-DISC-47`)**:
  - The **`230,722,380`** (`231,839,941` in latest 5-snapshot capture) `ast_rxorn` counter reported by `athstats -ol` on `Guarida-BH (.61)` is **NOT** a hardware RX FIFO overrun or PCIe Copy Engine (`CE`) ring exhaustion (`CPU ERR = 0`, `wal_dbg_stats.rx.phy_errs = 0`).
  - In `umac.ko:process_rx_stats` (`.text + 0x0b4d64` at **`0x0b5044..0x0b506c`**), the `WDI` RX stats subscriber inspects `htt_rx_desc->attention.flags` (`0x0b5044: lw $a0, 4($s5); 0x0b5054: andi $a0, $a0, 0xd`) and whenever `(flags & 0x0d) != 0` (`BIT(0)=first_mpdu | BIT(2)=mcast_bcast | BIT(3)=more_data`), it increments `*(uint32_t *)(scn + 0x1e220)` (`0x0b5064..0x0b506c: lw/addiu/sw $v0, -0x1de0($fp)` where `$fp = scn + 0x20000`).
  - `scn + 0x1e220` sits at offset `+0x00b0` inside `scn->scn_stats` (`struct ol_ath_radiostats` at `scn + 0x1e170`, copied by `ol_get_radio_stats` at `0x0b5e20` into `user_buf + 0x0210..0x02ef`).
  - In `bin/athbox` (`-ol` handler at `0x00402170..0x00402180`), `0x00402174: lw $a2, 0x1510($sp)` loads `user_buf + 0x02c0` (`scn->scn_stats + 0x00b0`) and prints it with format string `"ast_rxorn :\t%u\n"` (`0x00419960`).

---

## 2. Exact Assembly Chain (`umac.ko` $\rightarrow$ `bin/athbox`)

| Component & Function | Offset / VA | Exact Instructions | Physical Meaning |
| :--- | :--- | :--- | :--- |
| `umac.ko:process_rx_stats` | `0x0b5044..0x0b506c` | `lw $a0, 4($s5); andi $a0, $a0, 0xd; beqz $a0, 0xb5070; lw $v0, -0x1de0($fp); addiu $v0, $v0, 1; sw $v0, -0x1de0($fp)` | Increments `scn + 0x1e220` on every received PPDU/MPDU with `rx_attention.flags & 0x0d != 0`. |
| `umac.ko:ol_get_radio_stats` | `0x0b5e20..0x0b5e68` | `lui $v1, 2; addiu $a1, $v1, -0x1e90; addu $a1, $s0, $a1; addiu $a2, $zero, 0xe0` | Copies `224` B from `scn + 0x1e170` into `user_buf + 0x0210`. |
| `bin/athbox` (`-ol` printer) | `0x00402170..0x00402180` | `lw $a2, 0x1510($sp); jal 0x430f30; addiu $a1, $a1, -0x66a0` | Reads `user_buf + 0x02c0` (`scn + 0x1e220`) and prints `"ast_rxorn :\t%u\n"`. |

---

## 3. Live 4-Radio & 5-Snapshot Differential Proof (`.60`, `.61`, `.82`, `.83`)

| Radio | `ast_rxorn` (`scn + 0x1e220`) | `sum(Rx MCS 0..9)` PPDUs | Cumulative Ratio | `22.3s` $\Delta\text{ast\_rxorn}$ | `22.3s` $\Delta\text{Rx PPDUs}$ | Differential Lockstep | PCIe `wifi0` `IRQ 64` | `TASKLET` SoftIRQ |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `Almafuerte (.60)` | `68,262,535` | `72,757,127` | **`93.82%`** | `+13,427` | `+13,820` | **`97.16%`** | `254,800,985` | `620,851,085` |
| **`Guarida-BH (.61)`** | **`231,831,523`** | **`248,253,379`** | **`93.38%`** | **`+8,418`** | **`+8,927`** | **`94.30%`** | **`688,732,728`** | **`1,780,322,625`** |
| `Panel2 (.82)` | `92,974,076` | `94,361,483` | **`98.53%`** | — | — | — | — | — |
| `Panel3 (.83)` | `60,729,340` | `363,292,519` | `16.72%` | — | — | — | — | — |

---

## 4. Verification & Reproducibility
- **Script**: [`dissect_stage453a_guarida_bh_230m_ast_rxorn_and_pcie_ce_ring_re.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/re/dissect_stage453a_guarida_bh_230m_ast_rxorn_and_pcie_ce_ring_re.py)
- **Artifact**: [`stage453a_guarida_bh_230m_ast_rxorn_and_pcie_ce_ring_re.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage453a_guarida_bh_230m_ast_rxorn_and_pcie_ce_ring_re.json)
- **Test Suite**: [`test_stage453a.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage453a.py)
