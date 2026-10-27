<!-- doc-head: STAGE648A_LTU_AME_CORE_ARQ_RETRANS_AND_FEC_LDPC_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 648A — LTU ARQ / HARQ, LDPC / FEC and retry descriptors

- **Receipt**: [`artifacts/autoresearch/stage648a_ltu_ame_core_arq_retrans_and_fec_ldpc_re.json`](../artifacts/autoresearch/stage648a_ltu_ame_core_arq_retrans_and_fec_ldpc_re.json)
- **Tool**: [`tools/re/build_stage648a_ltu_ame_core_arq_retrans_and_fec_ldpc_re.py`](../tools/re/build_stage648a_ltu_ame_core_arq_retrans_and_fec_ldpc_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Two modules

`ame_core.ko` (3,282,052 bytes) and `ame_dev.ko` (298,760 bytes).

## 1. No ARQ and no HARQ by name — four zeros

| Token | Hits |
| :--- | :-: |
| `arq`, `ARQ` | **0** |
| `harq`, `HARQ` | **0** |
| `retrans`, `RETRANS` | **0** |
| `nack`, `NACK` | **0** |

**`REFUTED`**: `arq_harq_absent = 1`. Neither a retransmission state machine nor HARQ soft-combining
is a **named object** in these two modules.

That is a strong negative for a stage that asks for the state machine. It does **not** mean
retransmission does not happen — the next two sections show it is measured and controlled. It means
the mechanism is expressed as **error rate plus queue retry**, with no ARQ object to inspect.

`arq_state_machine_recovered = 0`, `harq_combining_recovered = 0`.

## 2. BLER is the retransmission telemetry, and it is per-CPE

**42 tokens, 20 distinct symbols.** The family:

```
ame_bbp_get_bler        ame_bbp_get_bler_cz      ame_bbp_set_bler_clear
bbp_show_bler           bbp_show_bler_cz
autoMCS_get_each_bler   autoMCS_reset_each_bler
check_cbler_decode      fty_bbp_log_bler         fty_bbp_log_bler_cz
cpeRxBler               cpeTxBler
```

Three properties make this genuinely useful:

**1. Uplink and downlink are separate.** `cpeRxBler` and `cpeTxBler` are distinct symbols
(`cpe_rx_tx_bler_pair = 1`). A PtMP AP can therefore tell whether a CPE's errors are on the way up or
on the way down — which is the difference between a CPE transmit problem and a sector receive
problem.

**2. There is a coded variant.** `check_cbler_decode` names **c-BLER** — coded block error rate,
measured after FEC decode — with its own `_cz` accessors. Pre-FEC and post-FEC error rates are
different quantities, and the module keeps both.

**3. There is a per-MCS variant.** `autoMCS_get_each_bler` / `autoMCS_reset_each_bler` — BLER **per
MCS index**, maintained by the auto-MCS controller. That is exactly the input a rate-selection
algorithm needs.

**`CONFIRMED`**: `cpe_rx_tx_bler_pair = 1`, `each_bler_present = 1`, `coded_bler_present = 1`.

## 3. LDPC iteration count is tunable

```
ame_bbp_op_get_rxTopB_ldpcIteration     ame_bbp_op_set_rxTopB_ldpcIteration
bbp_mrx_util_get_rxTopB_ldpcIteration   bbp_mrx_util_set_rxTopB_ldpcIteration
ame_check_hw_NoLDPC
```

**`CONFIRMED`**: `ldpc_iteration_controls = 4` and `ldpc_iteration_tunable = 1`. The iteration
count is **gettable and settable at two layers** (`ame_bbp_op_*` and `bbp_mrx_util_*`).

That is the lever a latency-versus-reliability trade-off needs: more iterations means more correction
and more decode time, and the module lets you move it.

**`CONFIRMED`**: there is a **hardware capability gate** — `ame_check_hw_NoLDPC` — plus the runtime
message `No ldpc supported`. So LDPC is conditional on the part, and the stack says so rather than
silently degrading.

`ldpc_token_hits = 22`, `ldpc_symbol_count = 7`.

## 4. The TX retry descriptor is a queue triple

The queue dump line:

```
Q[%d] tail=%d, reIdx=%d, retry=%d
```

**`CONFIRMED`**: `retry_descriptor_present = 1` (`retry_descriptor_lines = 2`).

Per transmit queue, the module reports:

| Field | Meaning |
| :--- | :--- |
| `tail` | queue tail index |
| **`reIdx`** | **retry index** — where the retry walk is |
| **`retry`** | **retry count** — how many attempts |

So retry state is **per queue**, not per packet. That is the correct design for a TDD scheduler that
retries within frame boundaries: the whole queue advances or retries together.

`fec_block_table_recovered = 0` — no per-block FEC table was found.

## 5. Four sysfs pairs make all of it reachable

| Pair | What it exposes |
| :--- | :--- |
| `bler_show/store` | the base BLER |
| `c_bler_show/store` | the **coded** BLER |
| `each_bler_show/store` | the **per-MCS** BLER array |
| `ldpc_iteration_show/store` | the iteration count |

**`CONFIRMED`**: `sysfs_pair_count = 4`. Every quantity in §2 and §3 is **readable and writable**
from userspace, including the per-MCS array.

That is unusual and worth stating: the observability here is better than the naming. There is no ARQ
object to read, but there are four knobs that describe exactly how well the link is decoding.

## 6. What is established

| Claim | Status |
| :--- | :-: |
| an ARQ state machine is named | **REFUTED** (0 hits) |
| HARQ / soft combining is named | **REFUTED** (0 hits) |
| `retrans` / `nack` appear at all | **REFUTED** (0 hits) |
| BLER is per-CPE with separate RX and TX counters | **CONFIRMED** |
| a coded (post-FEC) BLER exists | **CONFIRMED** (`check_cbler_decode`) |
| BLER is tracked per MCS by the auto-MCS controller | **CONFIRMED** |
| LDPC iteration count is settable at two layers | **CONFIRMED** (4 controls) |
| LDPC has a hardware capability gate | **CONFIRMED** (`ame_check_hw_NoLDPC`) |
| the TX retry descriptor is a queue triple | **CONFIRMED** (`tail`, `reIdx`, `retry`) |
| four sysfs pairs expose all of it | **CONFIRMED** |
| the retransmission state machine | **UNKNOWN / not named** |
| the FEC block table | **UNKNOWN / not found** |

## 7. The operational reading

A park debugging "packets are being retried" has four handles and no state machine:

1. **which direction** — `cpeRxBler` versus `cpeTxBler` localises the fault to uplink or downlink;
2. **how bad after FEC** — `c_bler` distinguishes a marginal link (high BLER, low c-BLER) from a
   failing one (both high);
3. **at which rate** — `each_bler` shows whether the errors cluster at high MCS;
4. **how hard the decoder works** — `ldpc_iteration` shows whether the receiver is already at its
   limit.

That is a complete diagnostic path without ever needing an ARQ object. The absence in §1 is a naming
result, and the four counters cover what the missing state machine would have told you.

## 8. Gaps

- **`UNKNOWN`** — the retransmission state machine itself; no ARQ/HARQ object exists by that name.
- **`UNKNOWN`** — the mapping from LDPC iterations to correction strength and decode latency.
- **`UNKNOWN`** — the BLER measurement window and how it is reset (`set_bler_clear` exists, the
  window does not).
- **`UNKNOWN`** — what `_cz` denotes beyond being a second variant.
- **`UNKNOWN`** — the per-block FEC table.
- **Known limit** — a counter proves errors are measured, not how retries are scheduled.
- **Not attempted** — dynamic validation, on-air retry measurement.
