<!-- doc-head: Stage 479A Guarida Panel2 (.82) & Panel3 (.83) Coexistence Champion v3 Safe Kit -->
Packages the verified Guarida Coexistence v3 safe kit (`rc.poststart_panel2_panel3_coexistence_v3.sh`) unifying Stages 417A–420A (`cbp_dur=900 us` alignment, `flags=6672` `deferred_list` rescue, and `Panel3` `674.5M` `local_enqued` MCS 2 storm suppression).
<!-- /doc-head -->

# Stage 479A — Guarida `Panel2` (`.82`) & `Panel3` (`.83`) Coexistence Champion v3 Safe Kit

- **Epistemic Status**: `CONFIRMED` (`Stages 417A–420A` binary RE of `ubnt_poll_host.ko` & `umac.ko` + `SimPy`/`NSGA-II` joint Pareto validation)
- **Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`) · `QCA firmware` (`wal_dbg_stats.tx.local_enqued`)
- **Kit Script**: [`rc.poststart_panel2_panel3_coexistence_v3.sh`](../firmware/guarida_safe_kits/rc.poststart_panel2_panel3_coexistence_v3.sh) (`SHA-256: 8b5966ab4d10938e...`, strict `LF`)
- **JSON Receipt**: [`stage479a_guarida_panel2_panel3_coexistence_champion_kit.json`](../artifacts/autoresearch/stage479a_guarida_panel2_panel3_coexistence_champion_kit.json)

---

## 1. Three Root Causes Solved by Coexistence v3 (`Stages 417A–420A`)

1. **`Panel2` (`.82`, `22` CPEs) `180 µs` `cbp_dur` Contention Bottleneck (`Stage 417A`)**:
   - Disassembly of `ubnt_poll_host_on_probe_req_rx` (`0x00910c`) and `ubnt_poll_host_on_assoc_req_rx` (`0x009594`) proved that only `AssocReq` populates `host_data->sta_hash_table` (`0x10f0($s1)`).
   - Because `Panel2` ran with `cbp_dur = 180 µs` (`1.8%` of the `10 ms` frame) and `flags = 14864` (`0x3a10`, bit `0x2000` active), weak CPEs (`-69..-75 dBm`) collided on `AssocReq` inside the `180 µs` window and were exiled to `deferred_list` (`0x10fc($s0)`) for **`20,000 ms` (`0x4e20`)**.
2. **`Panel3` (`.83`, `6` CPEs) `674.5M` `local_enqued` MCS 2 Storm (`Stage 418A`)**:
   - Disassembly of `umac.ko:ol_get_radio_stats` (`0x000bcd40`) proved `ast_tx_mgmt === wal_dbg_stats.tx.local_enqued` (`674,501,176` frames = `78.44%` of all `msdus_enqued`), of which **`669,086,302` (`99.20%`)** transmitted at fixed **MCS 2** because `/proc/sys/dev/uph_wifi0/enable=1` ran unaligned (`30000/30000 µs`).
3. **Joint `Panel2` + `Panel3` TDMA Synchronization (`Stage 420A`)**:
   - Aligning both sectors to `down_dur=7500 µs`, `up_dur=2500 µs`, `cbp_dur=900 µs`, and `flags=6672` (`0x1a10`, bit `0x2000` cleared) eliminates `deferred_list` lockouts and cuts `Panel3` `local_enqued` waste from `78.44%` to `10.06%`.

---

## 2. Baseline vs Coexistence v3 Champion Metrics (`Stage 420A` Pareto Knee)

| Metric | Guarida Current Baseline | Coexistence v3 Champion | Verified Delta |
| :--- | :---: | :---: | :---: |
| **`Panel2` (`.82`) `cbp_dur` / `flags`** | `180 µs` / `14864` (`0x3a10`) | **`900 µs` / `6672` (`0x1a10`)** | `0.0` `deferred_list` lockouts (`-100%`) |
| **`Panel3` (`.83`) `local_enqued` Share** | `78.44%` (`674.5M` MCS 2 storm) | **`10.06%`** (aligned `7500/2500`) | **`-68.38 percentage points`** |
| **Joint Sector Goodput (`Panel2 + Panel3`)** | `109.16 Mbps` (`83.14 + 26.02`) | **`155.52 Mbps` (`93.11 + 62.41`)** | **`+46.36 Mbps` (`+42.47%`)** |
| **Joint Sector `p99` Tail Latency** | `89.58 ms` | **`19.44 ms`** | **`-70.14 ms` (`-78.30%`)** |
