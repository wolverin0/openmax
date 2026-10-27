<!-- doc-head: STAGE532A_ATHBOX_VS_UMAC_SCN_STATS_ALIASING_MAP.md preserved document content -->
<!-- /doc-head -->



# Stage 532A — `umac.ko` & `bin/athbox` Complete `scn_stats` (`0x1e170..0x1e24f`) Struct-Offset Aliasing Map (`WA` & `XC`)

- **Claim Classification**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module` (`umac.ko:ol_get_radio_stats` `0x0b5e20`, `process_rx_stats` `0x0b4d64`, `bin/athbox` `0x00401930..0x004023f0`) + `QCA firmware` (`QCA988x` `wal_dbg_stats`)
- **Safety Gate**: `0` writes executed on `.60`, `.61`, `.82`, `.83`, `.84`.

---

## 1. `SIOCGATHSTATS` (`0x89f0`) `0x0310`-Byte `user_buf` Memory Layout (`$sp + 0x1250`)

When `athstats -ol` invokes `ioctl(fd, 0x89f0, &ifr)`, `umac.ko:ol_ath_ioctl` (`0x0bcc40`) populates a `0x0310`-byte (`784 B`) kernel buffer copied to userspace at `$sp + 0x1250`:
1. **`user_buf + 0x0000..0x020f` (`$sp + 0x1250..0x145f`, `528 B`)**: Target `struct wal_dbg_stats` copied by `ol_get_wal_dbg_stats` (`0x0bcd30`).
2. **`user_buf + 0x0210..0x02ef` (`$sp + 0x1460..0x153f`, `224 B`)**: Host `scn->scn_stats` (`scn + 0x1e170..0x1e24f`, accessed via `-0x1e90..-0x1db0($reg)` where `$reg = scn + 0x20000`) copied by `ol_get_radio_stats` (`0x0b5e20`).
3. **`user_buf + 0x02f0..0x030f` (`$sp + 0x1540..0x155f`, `32 B`)**: Host `aggr_stats` (`tx_packets`, `tx_errors`, `tx_long_retries`, `tx_short_retries`).

---

## 2. Complete 25-Field `athstats -ol` to `umac.ko` Writer & Aliasing Table

| `athstats -ol` Field | `athbox` VA | `$sp` Offset | `user_buf` | `scn_stats` (`scn` Offset) | `umac.ko` Writer Instruction | Classification & True Runtime Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ast_be_xmit` | `0x00401ea0` | `0x1460..64` | `0x0210` | `0x0000` (`0x1e170`) | `ol_get_radio_stats` (`0x0b5da0`) | **`GENUINE`**: 64-bit sum of VAP `tx_packets`. |
| `ast_be_nobuf` | `0x00401ec0` | `0x1468` | `0x0218` | `0x0008` (`0x1e178`) | `ath_attach+0xc0` (`0x01c3bc`) | **`UNPOPULATED`**: Always `0` on Offload (`wifi0`). |
| `ast_tx_buf_count` | `0x00401ed8` | `0x146c` | `0x021c` | `0x000c` (`0x1e17c`) | `ol_get_radio_stats+0x24` (`0x0b5e44`) | **`GENUINE`**: Host TX descriptor pool count. |
| `ast_tx_packets` | `0x00401eec` | `0x1478+147c`| `0x0228+22c`| `0x0018+001c` (`0x1e188`)| `process_tx_stats+0x7c` (`0x0b57cc`) | **`COMPOSITE`**: Adds WDI TX data (`0x147c`) + `ast_tx_mgmt` (`0x1478`). |
| `ast_rx_packets` | `0x00401f08` | `0x1474` | `0x0224` | `0x0014` (`0x1e184`) | `process_rx_stats+0x6b8` (`0x0b541c`) | **`GENUINE`**: Total WDI RX packets. |
| **`ast_tx_mgmt`** | `0x00401f1c` | `0x1478` | `0x0228` | `0x0018` (`0x1e188`) | `ol_get_radio_stats` (`0x0bcd68`) | **`STRUCT ALIAS (`FMX-DISC-46`)`**: Copies `wal_dbg_stats.tx.local_enqued` (target TDMA polls/BARs). |
| `ast_tx_nobuf` | `0x00401f30` | `0x13a0` | `0x0150` | `wal_dbg+0x0150` | `ol_get_wal_dbg_stats` (`0x0bcd30`) | **`GENUINE`**: Target WAL TX ring-full drops. |
| `ast_tx_xretries` | `0x00401f44` | `0x13c0` | `0x0170` | `wal_dbg+0x0170` | `ol_get_wal_dbg_stats` (`0x0bcd30`) | **`GENUINE`**: Target WAL `excess_retries` (`swr_limit` exhausted). |
| `ast_rx_num_data` | `0x00401f58` | `0x1480` | `0x0230` | `0x0020` (`0x1e190`) | `process_rx_stats+0x6c8` (`0x0b542c`) | **`GENUINE`**: WDI RX data MPDUs. |
| `ast_rx_num_mgmt` | `0x00401f6c` | `0x1488` | `0x0238` | `0x0028` (`0x1e198`) | `process_rx_stats+0x9ac` (`0x0b5710`) | **`GENUINE`**: WDI RX management frames. |
| `ast_rx_num_ctl` | `0x00401f80` | `0x148c` | `0x023c` | `0x002c` (`0x1e19c`) | `process_rx_stats+0x98c` (`0x0b56f0`) | **`GENUINE`**: WDI RX control frames. |
| `ast_tx_rssi` | `0x00401f94` | `0x1490` | `0x0240` | `0x0030` (`0x1e1a0`) | `ol_get_radio_stats` (`0x0b5df4`) | **`GENUINE`**: Last ACK RSSI from WMI stats. |
| `ast_rx_rssi_*` | `0x00401fa8` | `0x14e4..f7` | `0x0294..a7`| `0x0084..97` (`0x1e1f4`) | `process_rx_stats+0x78` (`0x0b4ddc`) | **`GENUINE`**: Per-chain `pri20/sec20/sec40` RX RSSI. |
| `ast_rx_bytes` | `0x004020d4` | `0x14f8` | `0x02a8` | `0x0098` (`0x1e208`) | `process_rx_stats+0x6cc` (`0x0b5430`) | **`GENUINE`**: 32-bit wrapping WDI RX bytes. |
| `ast_tx_bytes` | `0x004020e8` | `0x14fc` | `0x02ac` | `0x009c` (`0x1e20c`) | `process_tx_stats+0x80` (`0x0b57d0`) | **`GENUINE`**: 32-bit wrapping WDI TX bytes. |
| `tx_compaggr` | `0x004020fc` | `0x1500` | `0x02b0` | `0x00a0` (`0x1e210`) | `ol_get_radio_stats` (`0x0bcda0`) | **`GENUINE`**: Target WAL `comp_aggr`. |
| `rx_aggr` | `0x00402110` | `0x1504` | `0x02b4` | `0x00a4` (`0x1e214`) | `process_rx_stats+0x6f8` (`0x0b545c`) | **`GENUINE`**: WDI RX aggregated MPDUs. |
| `tx_bawadv` | `0x0040214c` | `0x1508` | `0x02b8` | `0x00a8` (`0x1e218`) | `NONE` | **`UNPOPULATED`**: Always `0` on Offload (`wifi0`). |
| `tx_compunaggr` | `0x00402160` | `0x150c` | `0x02bc` | `0x00ac` (`0x1e21c`) | `ol_get_radio_stats` (`0x0bcda8`) | **`GENUINE`**: Target WAL `comp_unaggr`. |
| **`ast_rxorn`** | `0x00402174` | `0x1510` | `0x02c0` | `0x00b0` (`0x1e220`) | `process_rx_stats+0x300` (`0x0b5064`) | **`CRITICAL STRUCT ALIAS (`FMX-DISC-47`)`**: Increments on `htt_rx_desc->attention.flags & 0x0d != 0` (`first_mpdu \| mcast_bcast \| more_data`), counting `94.3%..97.2%` of normal RX PPDUs! |
| `ast_txurn` | `0x00402188` | `0x13b4` | `0x0164` | `wal_dbg+0x0164` | `ol_get_wal_dbg_stats` (`0x0bcd30`) | **`GENUINE`**: Target WAL TX FIFO underrun. |
| `ast_txto` | `0x0040219c` | `0x13d8` | `0x0188` | `wal_dbg+0x0188` | `ol_get_wal_dbg_stats` (`0x0bcd30`) | **`GENUINE`**: Target WAL PDEV TX timeout. |
| `ast_mib` | `0x004021b0` | `0x1538` | `0x02e8` | `0x00d8` (`0x1e248`) | `NONE` | **`UNPOPULATED`**: Always `0` on Offload (`wifi0`). |
| `ast_rx_badcrypt` | `0x004021c4` | `0x1514` | `0x02c4` | `0x00b4` (`0x1e224`) | `process_rx_stats+0x8ec` (`0x0b5650`) | **`GENUINE`**: WDI RX decrypt errors. |
| `ast_rx_badmic` | `0x004021d8` | `0x1518` | `0x02c8` | `0x00b8` (`0x1e228`) | `process_rx_stats+0x7f4` (`0x0b5558`) | **`GENUINE`**: WDI RX MIC errors. |

---

## 3. Reproducible Verification
- Tool: [`dissect_stage532a_athbox_vs_umac_scn_stats_aliasing_map.py`](../tools/re/dissect_stage532a_athbox_vs_umac_scn_stats_aliasing_map.py)
- Artifact: [`stage532a_athbox_vs_umac_scn_stats_aliasing_map.json`](../artifacts/autoresearch/stage532a_athbox_vs_umac_scn_stats_aliasing_map.json)
- Test Suite: [`test_stage532a.py`](../tests/test_stage532a.py)
