<!-- doc-head: Stage 182A live counterbalanced A1->B1->A2->B2 Round 2 autoresearch on Rocket Prism 5AC Gen2 (.198 XC.v8.7.25) and Rocket 2AC Prism (.253 2XC.v8.7.11) -->
Carry authorized bench work through live execution, readback verification, and 5-pillar compliance without touching .241, .242, .20, or .250.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 182A — Live XC (`Rocket Prism 5AC Gen2` `.198`) & 2XC (`Rocket 2AC Prism` `.253`) Round 2 Counterbalanced Autoresearch

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-182A` (`T-S182A-LIVE-XC-2XC-ROUND2-AUTORESEARCH`)
- **Bench Targets**:
  - `198.18.0.64`: Ubiquiti `Rocket Prism 5AC Gen2` (`board.sysid=0xe7e9`, `QCA9558 720 MHz + QCA9880 + AirPrism`, `airOS 8 XC.v8.7.25`, Linux `2.6.32.68`)
  - `198.18.0.65`: Ubiquiti `Rocket 2AC Prism` (`board.sysid=0xe2f2`, `QCA9558 720 MHz + QCA988x 2.4 GHz + AirPrism`, `airOS 8 2XC.v8.7.11`, Linux `2.6.32.68`)
- **Hard Safety Boundaries (`CONFIRMED`)**:
  - `touched_241_or_242 = false`
  - `touched_20_or_250 = false`
  - `touched_production_guarida = false`
  - `flash_writes = 0` (100% volatile RAM-only `sysctl`/`iwpriv`/`/proc/sys/dev/uph_wifi0` actuation)
- **Attribution**: `Linux` + `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`, `ath_dev.ko`, `umac.ko`) + `QCA firmware` + `hardware`.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Round Design (`S182A-R4..R6`)
Building on `Stage 151A` (`S151A-R1..R3`) and adapting the `Stage 145A` + `Stage 161A..163A` principles (`vm.min_free_kbytes`, `ubnt_poll_host` 64-byte shared vector ordering, `txqueuelen`, and NAPI/softirq pacing) to 128 MB DDR2 `XC`/`2XC` platforms:

| Round | Hypothesis Tested | Arm A (Baseline) | Arm B (Candidate) | Key Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **`S182A-R4`** | Atomic `sk_buff` DMA reserve for `AirPrism` + `QCA9880` RX rings | `vm.min_free_kbytes=2048`, `vfs_cache_pressure=100` | `vm.min_free_kbytes=4096`, `vfs_cache_pressure=150` | Prevents `GFP_ATOMIC` page allocation stalls during high-PPS burst aggregation on 128 MB RAM (`XC`/`2XC`). |
| **`S182A-R5`** | `ubnt_poll_host.ko` (`uph_wifi0`) 64B vector & AirPrism/HSR filter hooks | `swr_limit=4`, `ff_cap_rep=1`, `cms_bias=0`, `voip_bias=0`, `daprot=2`, `mcast=5` | `swr_limit=3`, `ff_cap_rep=2`, `cms_bias=6`, `voip_bias=6`, `daprot=2`, `mcast=5` | Bounds software retry tail latency (`swr_limit=3`), doubles fast-frame capacity report (`ff_cap_rep=2`), and preserves `daprot=2` before `ff_mcast_airtime_limit=5` (`FMX-DISC-11`). |
| **`S182A-R6`** | Device queue depth (`txqueuelen`) + NAPI softirq budget + `eth0` IRQ coalescing | `txqueuelen=256`, `netdev_budget=600`, `dev_weight=64`, `eth0 coal=0/0` | `txqueuelen=192`, `netdev_budget=480`, `dev_weight=48`, `eth0 rx/tx-usecs=32/64` | Bounds `NET_RX_SOFTIRQ` time slice on single-core `MIPS 74Kc` so `uph_wifi0` timer callbacks never starve under line-rate TCP load. |

## 3. Winning `XC` / `2XC` Round 2 Champion Profile (`rc.poststart` RAM-Verified)
```sh
# Stage 182A XC (.198) & 2XC (.253) Round 2 Champion Profile
sysctl -w vm.min_free_kbytes=4096 vm.vfs_cache_pressure=150 \
  net.core.netdev_budget=480 net.core.dev_weight=48 \
  net.core.netdev_max_backlog=1024 net.ipv4.tcp_limit_output_bytes=65536 >/dev/null 2>&1 || true
iwpriv ath0 set_multiq 3 2>/dev/null || true
echo 0  > /sys/module/ath_dev/parameters/ACVOMinfree 2>/dev/null || true
echo 16 > /sys/module/ath_dev/parameters/ACVIMinfree 2>/dev/null || true
echo 32 > /sys/module/ath_dev/parameters/ACBEMinfree 2>/dev/null || true
echo 48 > /sys/module/ath_dev/parameters/ACBKMinfree 2>/dev/null || true
echo 3  > /proc/sys/dev/uph_wifi0/swr_limit 2>/dev/null || true
echo 2  > /proc/sys/dev/uph_wifi0/ff_cap_rep 2>/dev/null || true
echo 6  > /proc/sys/dev/uph_wifi0/cms_bias 2>/dev/null || true
echo 6  > /proc/sys/dev/uph_wifi0/voip_bias 2>/dev/null || true
echo 2  > /proc/sys/dev/uph_wifi0/daprot 2>/dev/null || true
echo 5  > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit 2>/dev/null || true
iwpriv wifi0 vow_extstats 0 2>/dev/null || true
echo 1  > /sys/module/umac/parameters/enable_tx_tcp_cksum 2>/dev/null || true
for dev in br0 ath0 eth0; do ifconfig "$dev" txqueuelen 192 2>/dev/null || true; done
ethtool -C eth0 rx-usecs 32 tx-usecs 64 2>/dev/null || true
```

## 4. Artifacts & Verification
- **Live Runner**: [`tools/benchmarks/run_stage182a_live_xc_2xc_round2_autoresearch.py`](../tools/benchmarks/run_stage182a_live_xc_2xc_round2_autoresearch.py)
- **Receipt JSON**: [`artifacts/autoresearch/stage182a_live_xc_2xc_round2_autoresearch.json`](../artifacts/autoresearch/stage182a_live_xc_2xc_round2_autoresearch.json)
- **Pytest Suite**: [`tests/test_stage182a_to_184a_xc_2xc_xm.py`](../tests/test_stage182a_to_184a_xc_2xc_xm.py)
