<!-- doc-head: STAGE653A_PB040_PB050_PB060_TRIPLE_PATCH_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 653A — `SimPy` + `pymoo` (`NSGA-II`) Triple-Patch Pareto Validation (`PB-040 + PB-050 + PB-060`)

- **Status**: `CONFIRMED` (100% offline `SimPy` discrete-event + `pymoo` `NSGA-II` multi-objective Pareto optimization across 4 counterbalanced seeds `A1 -> B1 -> A2 -> B2`; `live_devices_touched = False`)
- **Attribution**: `QCA firmware` (`firmware-2.bin_10.1.467-ct-com-full-014-96d543` & `WA`/`XC` `v8.7.25` `vmlinux.bin`)
- **Tool**: [`run_stage653a_pb040_pb050_pb060_triple_patch_pareto.py`](../tools/sim/run_stage653a_pb040_pb050_pb060_triple_patch_pareto.py)
- **Artifact**: [`stage653a_pb040_pb050_pb060_triple_patch_pareto.json`](../artifacts/autoresearch/stage653a_pb040_pb050_pb060_triple_patch_pareto.json)

## 1. Four-Profile Counterbalanced Progression (`Stock` $\rightarrow$ `PB-040` $\rightarrow$ `PB-040 + PB-050` $\rightarrow$ `PB-040 + PB-050 + PB-060`)
Each profile models the disassembled `QCA988x` Xtensa firmware instructions across `4` counterbalanced seeds (`653..656`) under Triple-Play traffic (`Bulk TCP + IPTV + VoIP`) on a near-field reflection / multipath fading channel (`MCS 7` `64-QAM 5/6` sweet spot at `585 Mbps` PHY; `MCS 8/9` `256-QAM` cliff):

1. **`Stock 10.1.467-ct / v8.7.25`**:
   - Hardware retry ceiling `hw_retry_max = 4`; upward RC probe every `32` packets or `5000 ms` (`_rate_find_rc` at `0x0099d1c0`); `XRETRY` penalty `+30` (`0x0099e65c`); step-down threshold `65%` (`0x0099e956`); `wal_vdev_attach` (`0x00983d5b` / `0x00983c94`) A-MPDU subframes `26` (`5caa`) and per-AC/TID SW retry limit `31` (`3cfb`).
2. **`PB-040 Alone` (`PB040-RETRY-AGGR`)**:
   - Tightens hardware descriptor retry chain (`4 -> 2`) and global `g_dbg_max_sw_retry` (`41 -> 12`), reducing `XRETRY` airtime stalls while still exposed to `32`-packet upward RC probing and `wal_vdev_attach` `26`-subframe / `31`-retry defaults.
3. **`PB-040 + PB-050 Dual-Patch` (`PB040 + PB050-RC-PROBE-DAMPEN`)**:
   - Dampens upward RC probing (`g_rc_probe_pkt_threshold = 512`, `g_rc_probe_period_ms = 15000`, `g_default_xretry_per_penalty = 12`, `g_rc_rate_max_per_thr = 72`), locking `MCS 7` stability while VDEV attach still caps A-MPDUs at `26` subframes.
4. **`PB-040 + PB-050 + PB-060 Triple-Patch` (`PB040 + PB050 + PB060-TXOP-CABQ-SCHED`)**:
   - Adds `PB-060` (`wal_vdev_attach` `5caa -> 2c0a` = `32` A-MPDU subframes; `3cfb -> 0cab` = `10` per-AC/TID SW retries; `wal_vdev_set_param` `1cfc -> 0ccc` = `12` runtime SW retry clamp), amortizing PLCP + BlockAck overhead across `+23.1%` larger A-MPDUs while cutting per-AC/TID software retry head-of-line (`HoL`) blocking by `-67.7%` (`31 -> 10`).

## 2. Multi-Objective `NSGA-II` Pareto Frontier
- Decision vector $\mathbf{x} = [\text{hw\_retry}, \text{probe\_pkt\_thr}, \text{probe\_period\_ms}, \text{xretry\_pen}, \text{vdev\_subframes}, \text{vdev\_sw\_retry}]$.
- Objectives minimized simultaneously: $[-\text{Goodput}_{\text{Mbps}}, \text{Latency}_{p99\text{, ms}}, \text{VoIP Jitter}_{p95\text{, ms}}]$.
- Monotonic dominance verified in [`stage653a_pb040_pb050_pb060_triple_patch_pareto.json`](../artifacts/autoresearch/stage653a_pb040_pb050_pb060_triple_patch_pareto.json):
  - $\text{Goodput}_{\text{Triple}} > \text{Goodput}_{\text{Dual}} > \text{Goodput}_{\text{PB-040}} > \text{Goodput}_{\text{Stock}}$
  - $\text{p99}_{\text{Triple}} < \text{p99}_{\text{Dual}} < \text{p99}_{\text{Stock}}$
  - $\text{QoE}_{\text{Triple}} > \text{QoE}_{\text{Dual}} > \text{QoE}_{\text{Stock}}$
