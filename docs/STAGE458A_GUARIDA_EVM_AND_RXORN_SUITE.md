<!-- doc-head: STAGE458A_GUARIDA_EVM_AND_RXORN_SUITE.md preserved document content -->
<!-- /doc-head -->



# Stage 458A — Consolidated Verification Suite & `FMX-DISC-47/48` Curation (`Stages 453A..458A`)

- **Claim Classification**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module` (`umac.ko:process_rx_stats` `0x0b5044`, `ubnt_poll_host.ko` `0x00a3c4 -> 0x006b60`) + `QCA firmware` (`QCA9882` `wal_dbg_stats` & `tx_bd_ExchangeHandler` `0x0099b8d4`) + `hardware` (`Chain 0` two-ray Fresnel reflection null at `5705 MHz`)
- **Safety Gate**: `0` writes executed across all 6 stages (`453A..458A`) on `.60`, `.61`, `.82`, `.83`, `.84`.

---

## 1. Curated Discoveries Promoted (`FMX-DISC-47` & `FMX-DISC-48`)

1. **`FMX-DISC-47` (`Stages 453A & 455A` — `230.72M` `ast_rxorn` `htt_rx_desc->attention.flags & 0x0d` Struct-Offset Aliasing & `Panel2` `139.75M` `mpdus_requed` vs `Panel3` `9.52M` `excess_retries`)**:
   - In `umac.ko:process_rx_stats` (`0x0b5044..0x0b506c`), `(htt_rx_desc->attention.flags & 0x0d) != 0` (`first_mpdu | mcast_bcast | more_data`) increments `*(uint32_t *)(scn + 0x1e220)` (`scn->scn_stats + 0x00b0`), which `bin/athbox` (`0x00402174` at `user_buf + 0x02c0`) prints as `"ast_rxorn :\t%u\n"` (`0x00419960`). Across 5 live snapshots (`22.32 s`), `ast_rxorn` increments in **`94.30%..97.16%` lockstep** with normal received PPDUs (`CPU ERR = 0`, `phy_errs = 0`).
   - On `Panel2 (.82)` (`Fixed-Frame 10 ms`), `tx_bd_ExchangeHandler` (`0x0099b8d4`) preempts unacknowledged A-MPDU subframes at TDMA slot expiry into `mpdus_requed = 139,751,148` (`20.31%`, `excess_retries = 23 = 0.000005%`), whereas `Panel3 (.83)` (`polling=disabled` in `system.cfg` while `uph_wifi0/enable=1`) collides until exhausting `swr_limit` (`0x00b404`), driving `excess_retries = 9,522,084` (`24.84%`, `414,003x` higher than `.82`).
2. **`FMX-DISC-48` (`Stages 454A, 456A & 457A` — `ubnt_poll_host_on_rx_evm_meas` 64-Byte Circular Per-Chain EVM Buffers, `50.0%` Blind Chain RSSI False-Negative Rate, & `.60 <-> .61` Fresnel Notch Mitigation Pareto)**:
   - `ubnt_poll_host_on_rx_evm_meas` (`0x00a3c4 -> 0x006b60`) writes 64-byte circular EVM arrays at `sta + 0x0b7` (`Chain 0`) and `sta + 0x0f7` (`Chain 1`). Across 5 snapshots on `.60 <-> .61`, Chain 1 stays flat at `38.16 dB` / `40.48 dB` (`0/64` samples `< 27 dB`), while Chain 0 is locked at `29.95 dB` / `31.19 dB` (`7..9/64` samples `< 27 dB` down to `22..25 dB`), forcing **`32.27%` of `.60 -> .61` DL frames (`29.60M / 91.73M`)** down from `MCS 8` (`256-QAM`) to `MCS 7` (`64-QAM`).
   - Traditional `|Delta_RSSI| <= 2..3 dB` checks miss **`41.67%` (`5/12`) to `50.00%` (`6/12`)** of severe EVM pathologies across Guarida (`+6.55 dB` mean hidden EVM gap, `+15.13 dB` max on `SOSA_Joaquin`).
   - `SimPy` + `pymoo` `NSGA-II` (`Stage 457A`) proves a $\pm 10\text{ MHz}$ shift (`5695`/`5715 MHz`) + `WMI 0x9044` recovers Chain 0 EVM to `38.64 dB` (`+7.99 dB`), lifting `MCS 8` share to `98.80%` (`+17.17 Mbps`).

---

## 2. Stage-by-Stage Verification Matrix

| Stage | Artifact Receipt | Doc (`< 220` Lines) | `writes_performed` | 5-Pillar Gate |
| :---: | :--- | :--- | :---: | :---: |
| **`453A`** | [`stage453a_guarida_bh_230m_ast_rxorn_and_pcie_ce_ring_re.json`](../artifacts/autoresearch/stage453a_guarida_bh_230m_ast_rxorn_and_pcie_ce_ring_re.json) | [`STAGE453A_GUARIDA_BH_230M_AST_RXORN_AND_PCIE_CE_RING_RE.md`](STAGE453A_GUARIDA_BH_230M_AST_RXORN_AND_PCIE_CE_RING_RE.md) | `0` | `PASS` |
| **`454A`** | [`stage454a_guarida_60_61_subcarrier_notch_and_cinr_gap.json`](../artifacts/autoresearch/stage454a_guarida_60_61_subcarrier_notch_and_cinr_gap.json) | [`STAGE454A_GUARIDA_60_61_SUBCARRIER_NOTCH_AND_CINR_GAP.md`](STAGE454A_GUARIDA_60_61_SUBCARRIER_NOTCH_AND_CINR_GAP.md) | `0` | `PASS` |
| **`455A`** | [`stage455a_ubnt_poll_UL_slot_starvation_and_requeue_re.json`](../artifacts/autoresearch/stage455a_ubnt_poll_UL_slot_starvation_and_requeue_re.json) | [`STAGE455A_UBNT_POLL_UL_SLOT_STARVATION_AND_REQUEUE_RE.md`](STAGE455A_UBNT_POLL_UL_SLOT_STARVATION_AND_REQUEUE_RE.md) | `0` | `PASS` |
| **`456A`** | [`stage456a_blind_rssi_vs_64subcarrier_evm_false_negative_matrix.json`](../artifacts/autoresearch/stage456a_blind_rssi_vs_64subcarrier_evm_false_negative_matrix.json) | [`STAGE456A_BLIND_RSSI_VS_64SUBCARRIER_EVM_FALSE_NEGATIVE_MATRIX.md`](STAGE456A_BLIND_RSSI_VS_64SUBCARRIER_EVM_FALSE_NEGATIVE_MATRIX.md) | `0` | `PASS` |
| **`457A`** | [`stage457a_guarida_backbone_60_61_notch_mitigation_pareto.json`](../artifacts/autoresearch/stage457a_guarida_backbone_60_61_notch_mitigation_pareto.json) | [`STAGE457A_GUARIDA_BACKBONE_60_61_NOTCH_MITIGATION_PARETO.md`](STAGE457A_GUARIDA_BACKBONE_60_61_NOTCH_MITIGATION_PARETO.md) | `0` | `PASS` |
| **`458A`** | [`stage458a_guarida_evm_and_rxorn_suite_receipt.json`](../artifacts/autoresearch/stage458a_guarida_evm_and_rxorn_suite_receipt.json) | [`STAGE458A_GUARIDA_EVM_AND_RXORN_SUITE.md`](STAGE458A_GUARIDA_EVM_AND_RXORN_SUITE.md) | `0` | `PASS` |
