<!-- doc-head: Stage 1160A - LTU ame_core.ko / ame_dev.ko passive sysfs/procfs/debugfs safe paths and /dev/ame char-dev paths, static binary RE, offline -->
# Stage 1160A - LTU `ame_core.ko` / `ame_dev.ko` Passive Safe Paths

**Provenance class:** `CONFIRMED_STATIC_BINARY`
**Radio safety:** static only. No SSH, no live IP, no firmware write, no target execution.
**Receipt:** `artifacts/verification/stage1160a_ltu_ame_passive_safe_paths_re.json`
**Tool:** `tools/re/ltu_eab_ame_passive_safe_paths_re_verifier.py`
**Reproduce:** `python tools/re/ltu_eab_ame_passive_safe_paths_re_verifier.py --verify-determinism`

## 1. Scope, and the two absences that define it

| Question | Measurement | Label |
| :--- | :--- | :--- |
| `eab_driver.ko` loose copies | 0 | REFUTED |
| `eab_driver.ko` tar members | 0 of 209121 members across 141 archives | REFUTED |
| LTU 2.3.1 filename hits | 0 | REFUTED |
| LTU 2.3.1 tar members | 0 | REFUTED |
| `ame_core.ko` present | 2 loose copies, 2 distinct hashes | CONFIRMED |
| `ame_dev.ko` present | 2 loose copies, 1 distinct hash | CONFIRMED |
| LTU 2.4.2 present | loose images plus two extracted trees | CONFIRMED |

`eab_driver.ko` is absent and is therefore not analysed. Its internals are not
described here, and nothing is claimed about it beyond absence. The earlier pass
that searched only loose files is not relied upon: the tar census enumerates
archive members, so a module living only inside an archive would have been found.
LTU 2.3.1 is absent by three independent searches, so the stage is scoped to 2.4.2.

Four loose `ame` files resolve to three distinct binaries. The `ame_dev.ko` in the
`afltu_2.4.2` and `aflturocket_2.4.2` trees is byte-identical (`912a7c1923aad381`),
so it is one binary, not two.

| Module | sha256 prefix | Size | Functions |
| :--- | :--- | ---: | ---: |
| `ame_core.ko` (afltu) | `fe5d489ea66bd2f3` | 3282052 | 2590 |
| `ame_core.ko` (rocket) | `a8d58e8d6a0c0665` | 3318764 | 2627 |
| `ame_dev.ko` (both) | `912a7c1923aad381` | 298760 | 783 |

All three are `EM_ARM`, ELF class 32.

## 2. The named mutex does not exist

Measured across all three binaries: symbol named `ame_ASIC0` is 0, string
`ame_ASIC0` is 0, and substring `asic0` in any case is 0. `ame_ASIC0` is REFUTED
as an identifier in these modules. Reporting a lock under that name would have
been fabrication, so the locks that do exist are reported instead.

| Module | Object | Offset | Size | Kind |
| :--- | :--- | ---: | ---: | :--- |
| `ame_core.ko` (afltu) | `add_cfgQ_lock` | `0x2ab828` | 24 | owned lock object |
| `ame_core.ko` (rocket) | `add_cfgQ_lock` | `0x2adfd4` | 24 | owned lock object |
| `ame_dev.ko` | none | - | - | no owned lock object |

`add_cfgQ_lock` is the only `STT_OBJECT` in either module whose name indicates a
synchronisation primitive. `ame_dev.ko` owns no lock at all: it is a thin front end
that dispatches into `ame_core.ko` through `g_core_hooks`.

Imported primitives, which are the lock operations actually reachable in code:

- `ame_core.ko`: `_mutex_lock`, `_mutex_unlock`, `rt_spin_lock`, `rt_spin_unlock`,
  `_raw_spin_lock_irq`, `_raw_spin_lock_irqsave`, `_raw_spin_unlock_irq`,
  `_raw_spin_unlock_irqrestore`, `wait_for_completion`, `complete`
- `ame_dev.ko`: `down`, `up`, `rt_spin_lock`, `rt_spin_unlock`,
  `__rcu_read_lock`, `__rcu_read_unlock`

Imports have no in-module offset, so their offset is null rather than a
misleading zero.

## 3. `/dev/ame` character-device paths

Ten node names, every one owned by `ame_dev.ko` and none present in `ame_core.ko`:
`ame_ctrl_dev`, `ame_p2s_bcon`, `ame_p2s_ctrl`, `ame_p2s_data`, `ame_p2s_mgmt`,
`ame_s2p_bcon`, `ame_s2p_ctrl`, `ame_s2p_data`, `ame_s2p_mgmt`, `ame_s2p_sys`.

Ownership is CONFIRMED by literal string presence in the module bytes.
`ame_dev.ko` imports `alloc_chrdev_region`, `cdev_init`, `cdev_add`,
`device_create`, `misc_register` and `debugfs_create_file`, which is the
registration machinery for those nodes.

Userspace openers found by static string scan: `/dev/ame_ctrl_dev` is referenced by
`bin/amespecd`, `bin/ame-debug-rxcap` and `bin/air_fpga`; the p2s and s2p family is
referenced by `bin/air_fpga`. The rootfs `/dev` contains only `console`, so nodes
are created at boot rather than shipped.

ioctl entry points are `ame_ioctl` (`ame_dev.ko`, size 4084) and, in `ame_core.ko`,
`device_ioctl_uni` (size 9708) plus `ame_core_ioctls_callback`,
`ame_sched_ioctl_callback` and `ame_add_ioctl_callback`. Command-level semantics
were not reversed, so their behaviour is UNKNOWN.

## 4. Bounding method

`safe_paths_count` is only meaningful if the extent was actually bounded.

1. `.symtab` supplies `st_value` and `st_size`. The extent is rejected if it
   overlaps the next symbol start or runs past `.text`.
2. capstone A32 linear decode must consume the extent exactly,
   `sum(insn.size) == st_size`. Partial decode means UNBOUNDED.
3. Lock detection is relocation-based: `.rel.text` targets inside the extent are
   matched against acquisition and release primitive name sets. It is not
   string-based.
4. Local callees are followed breadth-first to depth 4, each bounded by the same
   test.
5. Any indirect branch or call through a register, or any callee that cannot be
   bounded, forces UNRESOLVED. It never degrades to SAFE.

`safe_paths_count` is therefore a proven-safe lower bound, not a census of passive
paths. Everything else is listed in `unresolved_handlers` with a reason.

## 5. Results

221 read-only handlers across the three binaries.

| Verdict | Count |
| :--- | ---: |
| `SAFE_NO_MUTEX` | 64 |
| `TOUCHES_MUTEX` | 1 |
| `UNRESOLVED` | 156 |

Of the 64 safe handlers, 56 have a proven registration, from a recovered
DEVICE_ATTR object or a proven fops pairing, and 8 are name-pattern matches only.
Of all 221 handlers, 205 have proven registration and 16 are name-inferred.

200 distinct sysfs attribute names were recovered from `.rel.data`
`device_attribute` objects. ARM is a REL architecture, so the string offset is read
from the addend stored in `.data`, not from the symbol value. Reading the symbol
value instead yields garbage, which is the trap this recovery avoids. Examples of
safe attributes with their handlers and offsets: `adj_txcmdagg`/`adj_txcmdagg_show`
at `0x1290c` (52 bytes), `autoMcsDbg`/`autoMcsDbg_show` at `0x076f0` (292 bytes),
`cir_record`/`cir_record_show` at `0x06904` (100 bytes).

Safe handlers in `ame_core.ko`, both builds: `_ame_file_read` (chrdev read,
`0x040594`, 32 bytes) and `_ame_sysfs_getattr` (sysfs getattr, `0x0404fc`, 120
bytes). `_ame_sysfs_getattr` was verified at instruction level: it calls
`filp_open`, `kernel_read` then `filp_close`, and contains no lock relocation. Its
safety is CONFIRMED for lock absence, not merely inferred.

**The single handler that touches a lock.** `rx_capture_bin_read` in `ame_dev.ko`,
offset `0x84bc`, size 152, acquires `down` and releases `up` around a `memcpy` of
the capture buffer into the caller buffer. This is a debug read, not a passive
telemetry read. Verified at instruction level, so CONFIRMED.

**Why 156 are unresolved.** All share one structural reason: the handler branches
or calls through a register, because `ame_dev.ko` reads core state through the
`g_core_hooks` function-pointer table. That target lives in `ame_core.ko` and
cannot be proven from `ame_dev.ko` alone without dataflow analysis of the hook
table. These paths are UNKNOWN with respect to locking, neither safe nor unsafe.

## 6. Bottom line

For read-only observation of LTU state: 64 handlers are proven lock-free with
bounded extents, 56 of them with proven registration. `rx_capture_bin_read` takes a
semaphore and should be treated as a non-trivial debug path. The remaining 156
passive paths are unproven; reading them is not known to be harmful, but this stage
does not certify them.

## 7. Gaps

1. `eab_driver.ko` is absent, so nothing about it is known or claimed here.
2. LTU 2.3.1 is absent, so cross-version behaviour of these handlers is UNKNOWN.
3. `ame_ASIC0` exists as neither symbol nor string. Prior text naming it refers to
   a different artifact or is wrong.
4. `ame_dev.ko` owns no lock and dispatches reads through `g_core_hooks`, so the
   locking of the 156 indirect paths is UNKNOWN.
5. `safe_paths_count` is a lower bound of proven-safe handlers.
6. ioctl command semantics were not reversed.
7. No live read of any sysfs, procfs, debugfs or `/dev/ame` node occurred, so
   runtime blocking behaviour is UNMEASURED.

## 8. Claim ledger

- CONFIRMED: absence of `eab_driver.ko` and LTU 2.3.1; presence and hashes of the
  three binaries; `add_cfgQ_lock` name, offset and size; the ten `/dev/ame` owners;
  200 recovered sysfs attribute names; 64 bounded lock-free handlers; the
  `down`/`up` pair in `rx_capture_bin_read`; the
  `filp_open`/`kernel_read`/`filp_close` body of `_ame_sysfs_getattr`.
- REFUTED: `eab_driver.ko` presence; LTU 2.3.1 presence; the existence of an
  `ame_ASIC0` identifier.
- INFERRED: registration of 16 name-pattern handlers, including 8 of the safe ones.
- UNKNOWN: locking of the 156 indirect paths; ioctl command semantics; all runtime
  behaviour.
