<!-- doc-head: STAGE421A_FMX_DISC_45_46_CURATION.md preserved document content -->
<!-- /doc-head -->



# Stage 421A — Formalization of `FMX-DISC-45` (`cbp_dur=180 us` $\rightarrow$ `20,000 ms` Deferred-STA Lockout) & `FMX-DISC-46` (`Panel3` `674.5M` `local_enqued` `MCS 2` Storm & `64`-Subcarrier EVM Radiography)

## 1. Executive Summary (`CONFIRMED`)
- **Claim**: `CONFIRMED` (`proprietary airMAX/LTU module` + `QCA firmware` + `hardware`, `0` writes performed).
- **Canonical Ledger Updated**: [`CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md) (`156` lines `< 220` line ceiling, `1` ``).

---

## 2. Formalized Discoveries (`FMX-DISC-45` & `FMX-DISC-46`)

| Discovery ID | Stage Provenance | Core Mechanism & Binary / Telemetry Proof | Attribution |
| :--- | :--- | :--- | :--- |
| **`FMX-DISC-45`** | `Stages 360A & 417A` | `ubnt_poll_host_on_probe_req_rx` (`0x00910c`) never populates `host_data->sta_hash_table` (`0x10f0($s1)`); only `ubnt_poll_host_on_assoc_req_rx` (`0x009594`) at `stage == 1` (`0x0095c0`) calls `ubnt_poll_host_sta_add` (`0x00ce9c` at `0x009c8c`). On `Panel2 (.82)` (`ff_frame_dur=10,000 us`), `cbp_dur` (`0x0208($s0)`) is compressed to **`180 us`** (`5.0x` narrower than `900 us` on `.83`), causing high-PER CPEs (`-69..-75 dBm`) to miss `0x009c8c` insertion and hit the `flags & 0x2000` (`0x0082b4`, live `flags=0x3a10`) deferral path into `deferred_list` (`0x10fc($s0)`) for `defer_timeout_ms = 20,000 ms` (`0x0220($s0)` at `0x015024`, default `0x4e20` at `0x006388`). | `proprietary airMAX/LTU module`, `QCA firmware` |
| **`FMX-DISC-46`** | `Stages 418A & 419A` | In `umac.ko:ol_get_radio_stats` (`0x000bcd40`) and `bin/athbox` (`0x00401930`), `ast_tx_mgmt` is copied 1:1 from `wal_dbg_stats.tx.local_enqued`. On `Panel3 (.83)` (`system.cfg polling=disabled` while `uph_wifi0/enable=1`, `flags=0x3a10`), the `QCA9882` target WAL generates **`674,501,176` `local_enqued` frames (`78.44%`)** and transmits **`669,086,302` frames at `MCS 2` (`99.20%`)**. Simultaneously, `3,072`-sample `64`-subcarrier EVM radiography exposed a **`6.66 dB` Chain 0 multipath notch** on `.60 <-> .61` (`subcarrier 51 = 24 dB` vs Chain 1 `38.39 dB`), a **`9.81 dB` notch** on `TABORDA_Ada` (`.83`), and a **`2.48 dB` spectral tilt** on `RODRIGUEZ_Marina` (`.82`). | `QCA firmware`, `proprietary airMAX/LTU module`, `hardware` |

---

## 3. Verification & Reproducibility
- **Script**: [`build_stage421a_fmx_disc_45_46_curation.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/verify/build_stage421a_fmx_disc_45_46_curation.py)
- **Artifact**: [`stage421a_fmx_disc_45_46_curation_receipt.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage421a_fmx_disc_45_46_curation_receipt.json)
- **Test Suite**: [`test_stage421a.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage421a.py)
