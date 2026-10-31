<!-- doc-head: STAGE50B_LTU_HYBRID_SWQ_AND_MCS_CEILING_OTA_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 50B — LTU Hybrid SWQ/FPGA Register Suite, AP-Centralized `cpe_mcs` (`1024Ql`/`256Ql`/`64Ql`), `maxBD` High-Water Telemetry & 3-Tier HTB Over-The-Air Benchmark

**Date**: 2026-10-25  
**Task ID**: `T-S50B-LTU-HYBRID-S49B-R1-R2-ADAPTIVE-MCS-CEILING-AND-DUTY-CYCLE-OTA-BENCH`  
**Artifact**: [`artifacts/autoresearch/stage50b_ltu_hybrid_swq_and_mcs_ceiling_ota_bench_20261025.json`](../artifacts/autoresearch/stage50b_ltu_hybrid_swq_and_mcs_ceiling_ota_bench_20261025.json)

---

## 1. Executive Summary & Confirmed Kernel/Driver Discoveries (`CONFIRMED`)

On the live NLOS Over-The-Air link between **`LTU-Lite #1`** (`Boca 5`, `198.18.0.61`, `AP-PTMP(Run)`) and the remote standalone PoE **`LTU-Lite #2`** (`198.18.0.72`, `CPE-PTMP(Run)` at `-79/-78 dBm` UL, `-76/-70 dBm` DL), Stage 50B established two additional hardware/driver truths and executed a 9-trial counterbalanced Latin-square Triple-Play benchmark:

1. **Exact `ame_core_set_cpe_mcs` (`3329` / `3345`) AP-Centralized DL & UL Auto-MCS Ceiling Contract (`CONFIRMED`)**:
   - Inspecting kernel `dmesg` logs for `/sys/class/ame/ame_ctrl_dev/cpe_mcs` (`echo <cpe_id> <mcs_lvl> <opcode>`) proved that `ame_core_set_cpe_mcs` accepts the exact MIMO modulation ceiling index (`7, 11, 15, 19, 23, 31`) for both `opcode 0` (DL auto-MCS ceiling) and `opcode 2` (UL auto-MCS ceiling), whereas passing `32` (`0x20`) is out of range for `cpe_mcs` and falls back to `QPSKl`:
     - `echo 0 7 0 > cpe_mcs` $\rightarrow$ `Set CPE[0] DL automcs ceiling to QPSKl.`
     - `echo 0 11 0 > cpe_mcs` $\rightarrow$ `Set CPE[0] DL automcs ceiling to 16Ql.`
     - `echo 0 15 0 > cpe_mcs` $\rightarrow$ `Set CPE[0] DL automcs ceiling to 64Ql.`
     - `echo 0 19 0 > cpe_mcs` $\rightarrow$ `Set CPE[0] DL automcs ceiling to 256Ql.`
     - `echo 0 23 0 > cpe_mcs` $\rightarrow$ `Set CPE[0] DL automcs ceiling to 1024Ql.`
     - `echo 0 31 0 > cpe_mcs` $\rightarrow$ `Set CPE[0] DL automcs ceiling to 4096l.`
   - Because LTU's centralized TDMA MAP (`send_map_enable = 1`) grants both DL and UL modulation from the Master AP, setting `autoMcsCeiling` and `cpe_mcs` (`opcode 0` and `opcode 2`) on `LTU-Lite #1` controls both directions per CPE without requiring repeated SSH sessions to the remote CPE.
2. **`/sys/class/ame/ame_ctrl_dev/maxBD` (`adj_maxBD_show` / `adj_maxBD_store` in `ame_dev.ko`) is the In-Flight Hardware EAB High-Water-Mark Telemetry Counter (`CONFIRMED`)**:
   - Static ELF relocation analysis of `/lib/modules/3.14.65/ame_dev.ko` (`adj_maxBD_store` at `0x1281c`, `adj_maxBD_show` at `0x147c4` calling `g_core_hooks->set_maxBD` / `get_maxBD` in `ame_core.ko`) confirmed that `cat /sys/class/ame/ame_ctrl_dev/maxBD` reads the **peak in-flight Buffer Descriptor high-water mark** since the last write to `maxBD` (`echo 0 > maxBD` resets the peak counter to `0x0`).
   - Under unshaped stock `fq_codel` (Stage 48B `S48B-R0`), `maxBD` reached **`0x31` (`49` descriptors in flight = `74.34 ms` p95 RTT)**.
   - Under the Stage 50B 2-tier and 3-tier HTB profiles (`S50B-R0`, `S50B-R1`, `S50B-R2`), peak hardware EAB occupancy was capped at **`0x5`–`0xa` (`5`–`10` descriptors in flight)** across all 9 trials!
3. **Simultaneous `<1.0%` IPTV Loss and `<11 ms` Loaded `p95` RTT Achieved (`CONFIRMED`)**:
   - **`S50B-R0-STAGE49B-BASELINE`** (`pb_boost=1`, `autoMcsCeiling=23` `1024Ql`, `cpe_mcs=23`, `ulautogain=1`, `ulpwrtune=-75`, `26mbit` 2-tier HTB) achieved **`23.371 Mbps` mean aggregate DL**, **`0.374%` mean IPTV loss** (`0.332%`, `0.319%`, `0.471%`), **`0.0%` VoIP loss** (`0.829 ms` jitter), and **`7.153 ms` mean (`7.210 ms` median) loaded ping `p50` / `10.437 ms` mean (`9.880 ms` median) loaded ping `p95` RTT**.
   - **`S50B-R1-HYBRID-AUTOMCS-19-256QAM-8X`** (`pb_boost=1`, `autoMcsCeiling=19` `256Ql`, `cpe_mcs=19`, `SWQ_INTERVAL_EXTEND=2`, `DGAIN_DL_ENABLE=1`, `ul_pm=0`, `21mbit` 3-tier HTB) achieved **`9.814 Mbps` mean IPTV throughput** (`0.920%` median IPTV loss, `0.770 ms` jitter), **`0.0%` VoIP loss**, and **`5.843 ms` mean (`5.734 ms` median) loaded ping `p50` / `7.663 ms` mean (`7.424 ms` median) loaded ping `p95` RTT** (**-26.6% lower mean `p95` RTT** than `S50B-R0`, with `maxBD = 0x5–0x6`).
   - **`S50B-R2-HYBRID-AUTOMCS-15-64QAM-6X-SWQ2`** (`pb_boost=1`, `autoMcsCeiling=15` `64Ql`, `cpe_mcs=15`, `SWQ_INTERVAL_EXTEND=2`, `DGAIN_DL_ENABLE=1`, `ul_pm=0`, `21mbit` 3-tier HTB) achieved the lowest loaded `p50` RTT of **`4.105 ms` mean (`4.119 ms` median, `-42.6%` vs `S50B-R0`)** and **`8.892 ms` mean (`9.359 ms` median) loaded ping `p95` RTT**, while cutting RF fragment BLER from `37%` (`1024Ql`) down to **`19%–21%`** (`64Ql`).
4. **Dual-Partition Flash Persistence (`Active[1]` & `Backup[2]`) on Both Units (`CONFIRMED`)**:
   - Persisted the winning hybrid Champion (`S50B-R1-HYBRID-AUTOMCS-19-256QAM-8X`) to `/etc/persistent/rc.poststart` (`cfgmtd -w -p /etc/ -> [%100]`) on both **`LTU-Lite #1` (`Boca 5`)** and the remote standalone PoE **`LTU-Lite #2` (`198.18.0.72` Over-The-Air)**.

---

## 2. Counterbalanced 9-Trial Over-The-Air Benchmark Summary (`198.18.0.61` $\rightarrow$ `198.18.0.72`)

| Profile | Trials | Mean Aggregate DL (`Mbps`) | Mean Bulk TCP (`Mbps`) | Mean IPTV UDP (`Mbps`) | Mean / Median IPTV Loss (`%`) | Mean VoIP Jitter (`ms`) | Mean VoIP Loss (`%`) | Mean / Median Ping p50 (`ms`) | Mean / Median Ping p95 (`ms`) | Peak `maxBD` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S50B-R0-STAGE49B-BASELINE`** (`1024Ql` `23`, `26mbit` 2-Tier HTB) | 3 | **`23.371`** | `14.545` | `8.826` | **`0.374%` / `0.332%`** | `0.829` | `0.0%` | `7.153` / `7.210` | `10.437` / `9.880` | `0x5–0xa` |
| **`S50B-R1-HYBRID-AUTOMCS-19-256QAM-8X`** (`256Ql` `19`, `SWQ=2`, `DGAIN_DL=1`, `21mbit` 3-Tier HTB) | 3 | `19.589` | `9.775` | **`9.814`** | `1.207%` / **`0.920%`** | `0.989` | `0.0%` | `5.843` / `5.734` | **`7.663` / `7.424`** | **`0x5–0x6`** |
| **`S50B-R2-HYBRID-AUTOMCS-15-64QAM-6X-SWQ2`** (`64Ql` `15`, `SWQ=2`, `DGAIN_DL=1`, `21mbit` 3-Tier HTB) | 3 | `19.620` | `10.028` | `9.592` | `1.334%` / `1.467%` | `0.896` | `0.0%` | **`4.105` / `4.119`** | `8.892` / `9.359` | `0x5–0x7` |
