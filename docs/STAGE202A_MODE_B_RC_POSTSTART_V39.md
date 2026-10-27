<!-- doc-head: STAGE202A_MODE_B_RC_POSTSTART_V39.md preserved document content -->
<!-- /doc-head -->


# Stage 202A — Unified Mode B `rc.poststart` Production Generator `v39.0` (`WA`, `XC`, `2XC`, `XW`, `XM`, `LTU`)

## 1. Purpose & Architecture
[`tools/firmware/generate_mode_b_rc_poststart_v39.py`](../tools/firmware/generate_mode_b_rc_poststart_v39.py) synthesizes the Round-3 live bench winners from **Stage 200A** (`XC` `.198` + `2XC` `.253`) and **Stage 201A** (`XM` `192.168.1.20` 32 MB RAM) together with `WA`, `XW`, and `LTU` Tail-Guard (`S102E`) into a single deterministic `/etc/persistent/rc.poststart` generator (`v39.0`).

## 2. Per-Family Champion Matrix (`v39.0`)
| Family | RAM | `vm.min_free_kbytes` | `txqueuelen` | `netdev_budget` / `dev_weight` | `tcp_limit_output_bytes` | Family-Specific Hardware / Driver Hooks |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `XC` / `2XC` | 128 MB | `4096` (`vfs=150`) | `192` | `480` / `48` | `65536` (`tso_div=8`, `ca=110`, `ss=150`) | `set_multiq=3`, `swr_limit=3`, `ff_cap_rep=2`, `cms/voip_bias=6`, `daprot=2` before `mcast=5`, `eth0 rx/tx-usecs=24/48` |
| `WA` | 64 MB | `2048` (`vfs=120`) | `192` | `480` / `48` | `65536` (`tso_div=8`) | `set_multiq=3`, `swr_limit=3`, `ff_cap_rep=2`, `cms/voip_bias=6`, `daprot=2` before `mcast=5`, `AC*Minfree=0/16/32/48` |
| `XW` | 64 MB | `2048` | `64` | `300` / `48` | `65536` | `AMPDUFrames=28`, `AMPDULim=40960`, `ewma_delegate_on=1`, `AC*Minfree=0/16/32/48` |
| `XM` | 32 MB | `1536` | `48` | `256` / `32` (`backlog=512`) | `32768` (`rmem<=128K`, `wmem<=64K`) | `AMPDUFrames=28`, `AMPDULim=40960`, `ewma_delegate_on=1`, `AC*Minfree=0/16/32/64` |
| `LTU` | 128 MB | `4096` | `256` (`eth0`) | `300` / `48` (`backlog=1000`) | `131072` | `S102E` Tail-Guard Safe Mode (zero writes to `eab_driver.ko` proprietary registers) |

## 3. Hard Safety Invariants (`CONFIRMED`)
- **Shared 64B Vector Rule (`FMX-DISC-11`)**: `daprot=2` is always written **before** `ff_mcast_airtime_limit=5` on `WA`, `XC`, and `2XC`.
- **32 MB RAM Ceiling on `XM`**: `tcp_rmem="4096 32768 131072"`, `tcp_wmem="4096 16384 65536"`, `netdev_max_backlog=512`, and `ACBKMinfree=64` prevent OOM and descriptor starvation on `AR7241`.
- **Zero Production/Forbidden Radio Touch**: `touched_241_or_242 = False`, `touched_20_or_250 = False`, `flash_writes = 0`.

## 4. Verification Artifacts
- Generator: [`tools/firmware/generate_mode_b_rc_poststart_v39.py`](../tools/firmware/generate_mode_b_rc_poststart_v39.py)
- Generated Unified Script: [`artifacts/autoresearch/rc_poststart_mode_b_unified_v39.sh`](../artifacts/autoresearch/rc_poststart_mode_b_unified_v39.sh)
- Receipt: [`artifacts/autoresearch/stage202a_mode_b_rc_poststart_v39_receipt.json`](../artifacts/autoresearch/stage202a_mode_b_rc_poststart_v39_receipt.json)
- Pytest Suite: [`tests/test_stage200a_to_202a_multi_radio_v39.py`](../tests/test_stage200a_to_202a_multi_radio_v39.py)
