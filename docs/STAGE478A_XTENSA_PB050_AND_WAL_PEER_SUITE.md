<!-- doc-head: STAGE478A_XTENSA_PB050_AND_WAL_PEER_SUITE.md preserved document content -->
<!-- /doc-head -->



# Stage 478A — Consolidated Verification Suite: `QCA988x` Xtensa RC Globals, `PB050` Patcher, `wal_peer` & `HT_COMM` (`Stages 473A..478A`)

- **Claim Status**: `CONFIRMED` (`100%` offline static binary verification + `SimPy`/`NSGA-II` Pareto audit; `live_devices_touched = False`).
- **Subsystem Attribution**: `QCA firmware` & `proprietary airMAX/LTU module` (`QCA988x` Xtensa target RAM `SGMT` firmware).
- **Generator & Suite Receipt**:
  - [`verify_stage478a_xtensa_pb050_and_wal_peer_suite.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/verify/verify_stage478a_xtensa_pb050_and_wal_peer_suite.py)
  - [`stage478a_xtensa_pb050_and_wal_peer_suite_receipt.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage478a_xtensa_pb050_and_wal_peer_suite_receipt.json)
  - [`test_stage473a_to_478a_suite.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage473a_to_478a_suite.py)

---

## 1. Consolidated Summary of `Stages 473A..478A`

| Stage | Deliverable & Scope | Key Technical Finding / Quantitative Result |
| :--- | :--- | :--- |
| **[Stage 473A](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/STAGE473A_OPENWRT_CT_VS_STOCK_XTENSA_RC_GLOBALS_MAP.md)** | `OpenWrt 10.1.467-ct` vs Stock `airOS 8` (`10.2.4`) RC Globals Map (10 `SGMT` images) | Mapped `g_rc_probe_period_ms` (`0x0040c24c`/`0x0040d4e0`), `g_rc_probe_pkt_threshold` (`0x0040c250`/`0x0040d4e4`), `g_default_xretry_per_penalty` (`0x0040da78=30`), `g_rc_rate_max_per_thr` (`0x0040da7c=65`), and the `WMI_PEER_ASSOC_CMDID` runtime overrides (`0x0098a3d8` / `0x0098a015`). |
| **[Stage 474A](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/STAGE474A_PB050_XTENSA_RC_PROBE_DAMPENER_SGMT_PATCH.md)** | `PB050-RC-PROBE-DAMPEN` Surgical `SGMT` Binary Patcher (7 images) | Built verified `.sgmt.bin` images (`0` signature bytes) patching both static `.data` and `WMI_PEER_ASSOC_CMDID` code overrides (`32 -> 512` pkts via literal pool hijack, `5000 -> 15000` ms, `XRETRY 30 -> 12`, `max PER 65 -> 72`). |
| **[Stage 475A](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/STAGE475A_XTENSA_WAL_PEER_32PARAMS_AND_RETRY_SCHED_RE.md)** | `wal_peer_set_param` (`0x0098c0c0`) & `wal_peer_get_param` (`0x0098c4c8`) 33-Slot Dissection | Reconstructed `wal_peer` struct (`0x00..0x48`) across all 33 slots (`0..32`; 22 active set, 21 active get), proving Slots `15..17` read/write per-peer rate-control context pointers at `peer+0x44`, `peer+0x48`, and `peer+0x40`. |
| **[Stage 476A](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/STAGE476A_XTENSA_HT_COMM_OPCODES_FULL_TABLE_RE.md)** | `HT_COMM` 51-Slot RX (`0x009b1024`), Unpack (`0x009b3c88`), Pack (`0x009b2f98`) & TX (`0x009b43a0`) | Mapped all 51 slots (`0..50`: 21 active RX opcodes, 24 active Unpack opcodes, 14 Pack opcodes), 9-byte `0xaa 0x05` big-endian wire header, WMI event `0x901f` (`literal @ 0x00980594`), and `+4` byte shift in `XC.v8.7.25`. |
| **[Stage 477A](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/STAGE477A_PB050_RC_PROBE_DAMPENER_VS_STOCK_PARETO.md)** | `SimPy` + `pymoo` (`NSGA-II`) Evaluation of `PB050-RC-PROBE-DAMPEN` vs Stock | Under near-field reflection (`MCS 7` sweet spot vs `MCS 8/9` ISI cliff), `PB050` yields **`+122.861 Mbps` (`+44.15%`) goodput**, **`-9.19%` `p99` latency reduction**, and **`-0.5193` `fmx_loss` improvement**. |
| **[Stage 478A](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/STAGE478A_XTENSA_PB050_AND_WAL_PEER_SUITE.md)** | End-to-End 5-Pillar & Offline Safety Gate Suite | Verifies all 6 stage receipts, markdown line budgets (`< 220` lines), and `live_devices_touched == False`. |
