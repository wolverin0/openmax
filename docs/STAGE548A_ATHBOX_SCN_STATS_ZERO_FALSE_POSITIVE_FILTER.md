<!-- doc-head: Stage 548A athbox scn_stats Struct-Offset Aliasing Filter Eliminating False-Positive ast_rxorn Alerts (Stage 453A RE) -->
Integrates Stage 453A's binary RE proof (`umac.ko:process_rx_stats` at `0x0b5044` writing `scn->scn_stats + 0x00b0` on `attention.flags & 0x0d`) into the WISP observability classifier so false `ast_rxorn` alerts on `QCA988x` offload radios are permanently eliminated.
<!-- /doc-head -->

# Stage 548A — `athbox` `scn_stats` Struct-Offset Aliasing Filter (Zero False-Positive `ast_rxorn` Observability)

- **Epistemic Status**: `CONFIRMED` (`Stage 453A` MIPS32 disassembly of `umac.ko` & `bin/athbox` + 5-snapshot live lockstep proof)
- **Attribution**: `proprietary airMAX/LTU module` (`umac.ko:process_rx_stats` & `bin/athbox` `-ol` printer)
- **Filter Script**: [`build_stage548a_athbox_scn_stats_zero_false_positive_filter.py`](../tools/observability/build_stage548a_athbox_scn_stats_zero_false_positive_filter.py)
- **JSON Receipt**: [`stage548a_athbox_scn_stats_zero_false_positive_filter.json`](../artifacts/autoresearch/stage548a_athbox_scn_stats_zero_false_positive_filter.json)

---

## 1. Stage 453A Binary RE Proof: Why `ast_rxorn = 231.8M` on `.61` Is NOT an RX FIFO Overrun

Prior to Stage 453A, `athstats -ol` reporting `ast_rxorn = 230,722,380` on `Guarida-BH (.61)` appeared to indicate severe hardware RX FIFO overruns. Disassembling `WA.v8.7.25` `umac.ko` and `bin/athbox` **refuted** that interpretation:
1. **`umac.ko:process_rx_stats` (`0x0b4d64` at `0x0b5044..0x0b506c`)**:
   - Reads `htt_rx_desc->attention.flags` (`lw $a0, 4($s5)`) and checks `andi $a0, $a0, 0xd` (`BIT(0)=first_mpdu | BIT(2)=mcast_bcast | BIT(3)=more_data`).
   - Whenever any of those normal PPDU boundary bits is set, it increments `*(uint32_t *)(scn + 0x1e220)` (`scn->scn_stats + 0x00b0`).
2. **`umac.ko:ol_get_radio_stats` (`0x0b5e20`) & `bin/athbox` (`0x00402174`)**:
   - Copies `0xe0` (`224`) bytes from `scn + 0x1e170` to `user_buf + 0x0210..0x02ef`.
   - `bin/athbox` loads `user_buf + 0x02c0` (`scn->scn_stats + 0x00b0`) and prints it with the legacy Direct-Attach (`ath_dev.ko`) label `"ast_rxorn :\t%u\n"` (`0x00419960`)!

---

## 2. Live Lockstep Verification & Zero-False-Positive Filter Results

| Radio Endpoint | `ast_rxorn` Sample / $\Delta$ | `Rx MCS 0..9` PPDU Sum / $\Delta$ | Lockstep Ratio (`%`) | `CPU ERR` IRQ | Filter Verdict & Alert Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`Almafuerte (.60)` (`22.3 s` $\Delta$)** | `+13,427` (`68.26M` total) | `+13,820` (`72.76M` total) | **`97.16%`** | `0` | `NORMAL_HTT_RX_ATTENTION_0X0D` $\rightarrow$ **`Alert=False`** |
| **`Guarida-BH (.61)` (`22.3 s` $\Delta$)** | `+8,418` (`231.84M` total) | `+8,927` (`248.25M` total) | **`94.30%`** | `0` | `NORMAL_HTT_RX_ATTENTION_0X0D` $\rightarrow$ **`Alert=False`** |
| **`Panel2-Guarida (.82)` (Cumulative)** | `92,974,076` | `94,361,483` | **`98.53%`** | `0` | `NORMAL_HTT_RX_ATTENTION_0X0D` $\rightarrow$ **`Alert=False`** |
