<!-- doc-head: STAGE40A_LTU_PERSISTENT_POSTSTART_AND_24GHZ_TRIPLE_PLAY_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 40A — LTU-Lite Persistent `/etc/persistent/rc.poststart` Master Unlock & 2.4 GHz + LTU Triple-Play Benchmark

- **Task ID**: `T-S40A-LTU-LITE-PERSISTENT-RC-POSTSTART-MASTER-UNLOCK-AND-R2AC-M18-IPTV-BENCH`
- **Date**: `2026-10-25`
- **Artifact**: [`artifacts/autoresearch/stage40a_ltu_persistent_poststart_and_24ghz_bench_20261025.json`](../artifacts/autoresearch/stage40a_ltu_persistent_poststart_and_24ghz_bench_20261025.json)
- **Deployment Tool**: [`tools/bench/deploy_stage40a_ltu_poststart.py`](../tools/bench/deploy_stage40a_ltu_poststart.py)
- **Benchmark Harness**: [`tools/bench/run_stage40a_ltu_poststart_and_24ghz_bench.py`](../tools/bench/run_stage40a_ltu_poststart_and_24ghz_bench.py)
- **Unit Tests**: [`tests/test_stage40a_ltu_and_24ghz_bench.py`](../tests/test_stage40a_ltu_and_24ghz_bench.py)

---

## 1. Executive Summary & Architectural Discoveries

### 1.1 Persistent `/etc/persistent/rc.poststart` Boot Mechanism on `LTU.afltu.v2.4.0` (CONFIRMED)
1. **Why `/etc/persistent/rc.poststart` Alone Does Not Run on Stock `LTU.afltu.v2.4.0`**:
   - In [`/usr/etc/rc.d/rc.funcs`](../tools/bench/deploy_stage40a_ltu_poststart.py), `rc_start()` checks:
     ```sh
     if [ -f /usr/lib/cs -a -f /etc/poststart ]; then
         . /etc/persistent/rc.poststart
     fi
     ```
   - Because standard `LTU.afltu.v2.4.0` SquashFS does not contain `/usr/lib/cs`, `rc_start()` skips `/etc/persistent/rc.poststart` unless triggered by `/etc/sysinit/iptables.conf` (`iptables.sys.masq.1.devname=br0 -j MASQUERADE; /etc/persistent/rc.poststart >/tmp/poststart.log 2>&1 & echo`) and `/etc/persistent/profile`.
2. **Cold-Boot Verification on `LTU-Lite #1` (`Boca 5`) & Flash Persistence on `LTU-Lite #2` (`Boca 7`)**:
   - Both `LTU-Lite #1` (`Boca 5`, `PUBLIC_DEVICE_0046%27`, `PUBLIC_DEVICE_0045`) and `LTU-Lite #2` (`Boca 7`, `PUBLIC_DEVICE_0076%27`, `PUBLIC_DEVICE_0043`) were provisioned with `/etc/persistent/rc.poststart` and persisted via `cfgmtd -w -p /etc/`.
   - Across a real cold reboot of `LTU-Lite #1` (`uptime = 115.02s`), `/etc/persistent/rc.poststart` executed automatically at boot:
     - Patched `/tmp/air_fpga` in RAM (`set_cfg_role` file offsets `1756200` -> `0x08` and `1756264` -> `0x01` `TYPE_AP`), bind-mounted over `/bin/air_fpga`, and brought up `ROLE=ap-ptmp` on `5500 MHz` (`20 MHz`, `SSID=FuturaMAX-LTU-Bench`).
     - Assigned `198.18.0.63/24` on `br1` (`eth0.1`) and `br0` (`198.18.0.84/24` + `198.18.0.63/24`), activated `fq_codel limit 1024 flows 1024 quantum 1514 target 2.5ms interval 50.0ms ecn` on `ath0`, and launched `iperf3 -s -p 5201/5202/5203 -D`.
   - On `LTU-Lite #2` (`Boca 7`), `/etc/persistent/rc.poststart` (`4249` bytes) was persisted via `cfgmtd -w -p /etc/` prior to moving `#2` to the standalone remote PoE injector, configuring `ROLE=cpe-ptmp` on `5500 MHz` (`FuturaMAX-LTU-Bench`), `198.18.0.118/24` on `br1` & `br0` (`198.18.0.140/24`), `ath0` `fq_codel quantum 1514 target 2.5ms`, and `iperf3 -s -p 5201/5202/5203 -D`.

### 1.2 Shared `sysctl_table->data` Buffer Ordering in `ubnt_poll_host.ko` (`Rocket 2AC Prism`) (CONFIRMED)
- On `Rocket 2AC Prism` (`2XC.v8.7.11`, Linux `2.6.32.68`), `/proc/sys/dev/uph_wifi0/{fixed_frame,cms_bias,voip_bias,ff_mcast_airtime_limit}` share a single 16-integer `sysctl_table->data` array (`64` bytes).
- Writing `echo 6 > /proc/sys/dev/uph_wifi0/cms_bias` or `echo 6 > /proc/sys/dev/uph_wifi0/voip_bias` AFTER `echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit` overwrites index 0 back to `6`.
- Writing `echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit` **LAST** preserves `FF_MCAST = 5 50 3 12 12 10 10 0 0 0 0 0 0 0 0 0` in `S40A-R1` phases `B1` and `B2`.

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Triple-Play Benchmark Results

### 2.1 `S40A-R1` — 2.4 GHz Lane (`Rocket 2AC Prism` `.253` + `NanoLoco M2` `.252` / `198.18.0.50`)

Keeping `tcp_wmem = '4096 16384 524288'` (`512 KB`) in both arms eliminated the `-14.79%` Bulk TCP starvation observed with `64 KB` `tcp_wmem` in `S38A-R1`:

| Phase | Arm | `FF_MCAST` (Index 0) | Bulk TCP Goodput (Mbps) | TCP Retrans | IPTV Goodput (Mbps) | IPTV Jitter (ms) | IPTV Loss (%) | VoIP Goodput (Kbps) | VoIP Jitter (ms) | VoIP Loss (%) | Loaded Ping p95 (ms) | Composite p95 RTT (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | Baseline (`S34A-R1` `ff_mcast=10`) | `10` | `93.118` | `0` | `2.148` | `0.7272` | `0.0%` | `125.10` | `0.8786` | `0.0%` | `9.352` | `11.761` |
| **`B1`** | Candidate (`S40A-R1` `ff_mcast=5` Last + `CS4`/`EF`) | `5` | `86.315` | `0` | `2.148` | `0.3870` | `0.0%` | `125.11` | `0.5246` | `0.0%` | `7.234` | `8.601` |
| **`A2`** | Baseline (`S34A-R1` `ff_mcast=10`) | `10` | `97.050` | `0` | `2.148` | `0.2479` | `0.0%` | `125.11` | `0.3179` | `0.0%` | `10.473` | `11.322` |
| **`B2`** | Candidate (`S40A-R1` `ff_mcast=5` Last + `CS4`/`EF`) | `5` | `95.246` | `0` | `2.148` | `0.4386` | `0.0%` | `125.11` | `0.6930` | `0.0%` | `7.995` | `9.692` |
| **Mean A** | **Arm A Summary** | `10` | **`95.084`** | **`0.0`** | **`2.148`** | **`0.4875`** | **`0.0%`** | **`125.11`** | **`0.5983`** | **`0.0%`** | **`9.913`** | **`11.542`** |
| **Mean B** | **Arm B Summary** | `5` | **`90.781`** | **`0.0`** | **`2.148`** | **`0.4128`** | **`0.0%`** | **`125.11`** | **`0.6088`** | **`0.0%`** | **`7.615`** | **`9.147`** |
| **Delta** | **Arm B vs Arm A** | `5 vs 10` | **`-4.53%`** | **`0.0`** | **`0.00%`** | **`-15.32%` (`-0.075 ms`)** | **`0.0%`** | **`0.00%`** | **`+1.75%`** | **`0.0%`** | **`-23.18%` (`-2.298 ms`)** | **`-20.75%` (`-2.395 ms`)** |

- **Promoter Decision (`S40A-R1`)**: `RETAIN_CURRENT_CHAMPION` (`pareto_score_delta_pct = +3.00%`, `p95_delta_pct = -20.75%`, `gp_delta_pct = -4.27%`). Keeping `tcp_wmem = 512 KB` recovered `+10.26%` of the Bulk TCP throughput lost in `S38A-R1` (`90.78 Mbps` vs `78.57 Mbps`) while cutting loaded p95 RTT by **`-20.75%`** (`11.542 -> 9.147 ms`) and IPTV jitter by **`-15.32%`** (`0.4875 -> 0.4128 ms`) with **`0.0%`** IPTV/VoIP packet loss and **`0`** TCP retransmits.

---

### 2.2 `S40A-R2` — LTU Lane (`LTU-Lite #1` `.110` <-> `LTU-Lite #2` `.111` with `ap-ptmp` Active)

| Phase | Arm | `tcp_notsent_lowat` | `ath0` / `eth0.1` Qdisc | Bulk TCP Goodput (Mbps) | TCP Retrans | IPTV Goodput (Mbps) | IPTV Jitter (ms) | IPTV Loss (%) | VoIP Goodput (Kbps) | VoIP Jitter (ms) | VoIP Loss (%) | Loaded Ping p95 (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | Baseline (`S24F-R1`) | `-1` | `fq_codel quantum 300 target 5ms` | `32.625` | `0` | `2.150` | `0.3791` | `0.0%` | `125.09` | `0.5647` | `0.0%` | `9.017` |
| **`B1`** | Candidate (`S40A-R2`) | `-1` | `fq_codel limit 1024 quantum 1514 target 2.5ms` | `25.806` | `0` | `2.150` | `0.1523` | `0.0%` | `125.11` | `0.1769` | `0.0%` | `5.615` |
| **`A2`** | Baseline (`S24F-R1`) | `-1` | `fq_codel quantum 300 target 5ms` | `34.532` | `0` | `2.161` | `0.9034` | `0.0%` | `125.11` | `0.5384` | `0.0%` | `22.127` |
| **`B2`** | Candidate (`S40A-R2`) | `-1` | `fq_codel limit 1024 quantum 1514 target 2.5ms` | `30.509` | `0` | `2.153` | `0.5445` | `0.0%` | `125.07` | `0.2945` | `0.0%` | `9.833` |
| **Mean A** | **Arm A Summary** | `-1` | `quantum 300 target 5ms` | **`33.579`** | **`0.0`** | **`2.156`** | **`0.6412`** | **`0.0%`** | **`125.10`** | **`0.5515`** | **`0.0%`** | **`15.572`** |
| **Mean B** | **Arm B Summary** | `-1` | `quantum 1514 target 2.5ms` | **`28.158`** | **`0.0`** | **`2.152`** | **`0.3484`** | **`0.0%`** | **`125.09`** | **`0.2357`** | **`0.0%`** | **`7.724`** |
| **Delta** | **Arm B vs Arm A** | `-1` | `limit 1024` syntax fix | **`-16.14%`** | **`0.0`** | **`-0.19%`** | **`-45.66%` (`-0.293 ms`)** | **`0.0%`** | **`-0.01%`** | **`-57.26%` (`-0.316 ms`)** | **`0.0%`** | **`-50.40%` (`-7.848 ms`)** |

- **Key Findings (`S40A-R2`)**:
  - Activating `fq_codel limit 1024 flows 1024 quantum 1514 target 2500us interval 50000us ecn` + `DSCP CS4` (`0x80` -> `WMM AC_VI`) + `DSCP EF` (`0xb8` -> `WMM AC_VO`) cut IPTV jitter by **`-45.66%`** (`0.6412 -> 0.3484 ms`), cut VoIP jitter by **`-57.26%`** (`0.5515 -> 0.2357 ms`), and cut loaded ICMP p95 RTT by **`-50.40%`** (`15.572 -> 7.724 ms`) with **`0.0%`** IPTV/VoIP packet loss and **`0.0`** TCP retransmits.
  - Because `LTU-Lite #1` was simultaneously running `ap-ptmp` (`[ame.core.Hi]` `SCHED_FIFO 90` and `[ame.core.Frm]` `SCHED_FIFO 85` on `CPU0`) and software `fq_codel` on `eth0.1` adds per-packet CPU overhead on `CPU0`, `eth0.1` should remain `noqueue` (relying on `eth0` hardware `mq` + `ath0` `fq_codel limit 1024 quantum 1514 target 2500us`).
  - **Promoter Decision (`S40A-R2`)**: `RETAIN_CURRENT_CHAMPION` (`S24F-R1` retained in `champion_state_ledger.json`).
