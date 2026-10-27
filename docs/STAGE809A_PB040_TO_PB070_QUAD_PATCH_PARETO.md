<!-- doc-head: STAGE809A_PB040_TO_PB070_QUAD_PATCH_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 809A — PB-040 to PB-070 quad-patch Pareto

- **Receipt**: [`artifacts/autoresearch/stage809a_pb040_to_pb070_quad_patch_pareto.json`](../artifacts/autoresearch/stage809a_pb040_to_pb070_quad_patch_pareto.json)
- **Tool**: [`tools/sim/run_stage809a_pb040_to_pb070_quad_patch_pareto.py`](../tools/sim/run_stage809a_pb040_to_pb070_quad_patch_pareto.py)
- **Scope**: **offline static simulation.** Reads two JSON receipts only. No firmware, no flash, no radio.

## 0. This is a projection, not a measurement

The receipt carries the label explicitly:

```
measurement_or_projection = "projection"
```

Every number below comes from **fields already written** by the PB-040 dry run. Nothing was measured
in this stage, and no patch was executed.

That distinction is the entire value of the artefact: a Pareto front derived from a dry-run receipt is
a **planning object**, and calling it a measurement would be the kind of fabrication this series has
refused at every stage.

## 1. The input is smaller than the name implies

**`CONFIRMED`**: `roles_parsed = 3`, not four. The "quad patch" is the stage's label; the PB-040
receipt records **three** verified roles.

| Role | Cost (observed diff) | Offset in segment |
| :--- | :-: | :-: |
| `athwlan_AR9888v2_ptmp_ap_bin` | 4 | 5020 |
| `athwlan_AR9888v2_ptmp_sta_bin` | **4** | **4988** |
| third role | 4 | higher |

All three cost **4 bytes** — the same rename-style diff PB-040 documented
(`UBNT_POLL_MEM_ALLOC` → `OMAX_POLL_MEM_ALLOC`). Total cost across roles: **12 bytes**.

## 2. The Pareto front is a single point

Two objectives, both minimised and both taken from PB-040:

| Objective | Field | Meaning |
| :--- | :--- | :--- |
| **cost** | `observed_total_diff_bytes` | bytes actually changed |
| **offset** | `mutation_offset_in_segment` | how far into the segment the anchor sits |

**`CONFIRMED`**: `pareto_front_size = 1`, `dominated_count = 2`.

The single non-dominated role is **`athwlan_AR9888v2_ptmp_sta_bin`**, at **cost 4, offset 4988** —
the earliest anchor among the equal-cost roles.

`front_cost_bytes = 4` of `total_cost_bytes = 12` — `cost_fraction_on_front = 0.3333`.

**This is a degenerate front, and that is the honest result.** Because all three roles cost the same
4 bytes, the only discriminator is **offset**, so the front collapses to "the earliest one". A Pareto
analysis that needs all three roles is not what this data supports.

## 3. Every role is blocked, by two independent gates

| Gate | Value |
| :--- | :--- |
| `spi_flash_write_allowed` | **false** |
| `automatic_execution_allowed` | **false** |
| `operator_gate_required_for_bench` | **true** |
| PB-070 `ready_to_execute` | **false** |
| PB-070 `unmet_prerequisites` | listed |
| PB-070 `safety_level` | L3 |

**`CONFIRMED`**: `all_roles_blocked = 1`, `execution_authorised = 0`.

Two **independent** gates block: PB-040 forbids the write, and PB-070's prerequisites are unmet. So
even a perfect Pareto ordering would authorise nothing.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| the Pareto input is PB-040 receipt data | **CONFIRMED** (SHA-256 pinned) |
| the output is labelled a projection | **CONFIRMED** |
| there are four roles | **REFUTED** (3) |
| all roles cost the same 4 bytes | **CONFIRMED** |
| the front collapses to one point on offset | **CONFIRMED** |
| every role is blocked | **CONFIRMED** (two gates) |
| anything was executed | **REFUTED** (`execution_authorised = 0`) |
| a trade-off beyond what PB-040 recorded | **REFUTED** (both objectives come from the same receipt) |

## 5. The operational reading

A planner should take three things and nothing more:

1. **the three roles cost 4 bytes each** — a rename probe is cheap in bytes, which is why it was
   attempted first;
2. **offset is the only discriminator** — so ordering is by anchor position, not by merit;
3. **nothing is executable** — the gates are closed, and the Pareto front is an input to a gated
   bench decision, not a substitute for it.

What it must **not** be used for: justifying a write. `execution_authorised = 0` is in the receipt
precisely so that a later reader cannot mistake a ranking for permission.

## 6. Gaps

- **`UNKNOWN`** — whether the three roles' offsets are comparable; the segment base is ambiguous
  (Stage 806A), so the front is **ordinal only**.
- **`UNKNOWN`** — any objective PB-040 did not record, such as risk of corrupting adjacent code.
- **`UNKNOWN`** — how PB-070's unmet prerequisites would be satisfied.
- **Blocked** — `spi_flash_write_allowed: false`, `ready_to_execute: false`.
- **Known limit** — a degenerate front is a correct output for degenerate data.
- **Not attempted** — any execution, any write, any dynamic validation.
