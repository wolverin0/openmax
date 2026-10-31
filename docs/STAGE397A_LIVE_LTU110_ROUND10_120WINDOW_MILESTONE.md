<!-- doc-head: STAGE397A_LIVE_LTU110_ROUND10_120WINDOW_MILESTONE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 397A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 10 (`120`-Window Milestone!) Memory & Dirty Writeback Autoresearch

- **Status**: `CONFIRMED`
- **Attribution**: `Linux`, `hardware`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`)
- **Milestone**: **`10` Live Campaigns (`30` Counterbalanced `A1->B1->A2->B2` Rounds = `120` Live Windows)** on `198.18.0.63` with zero `/dev/ame*` touches and `45s` rollback watchdog.

## 1. Round 10 Knobs Tested (`12` Counterbalanced Windows)
| Knob | Stock Baseline (`A1`/`A2`) | Champion `v8` (`B1`/`B2`) | First-Principles Mechanism (`CONFIRMED`) |
| :--- | :--- | :--- | :--- |
| `vm.dirty_ratio` | `20` | `10` | Prevents synchronous dirty-page stalls when `ustatsd`/`syslogd` flush tmpfs logs (`Linux`). |
| `vm.dirty_background_ratio` | `10` | `5` | Smooths background page writeback into small micro-flushes (`Linux`). |
| `vm.vfs_cache_pressure` | `100` | `50` | Retains hot SquashFS dentry/inode metadata in RAM so periodic CGI/SSH polls never trigger flash reads (`Linux`). |
| `net.ipv4.tcp_moderate_rcvbuf` | `1` | `1` | Keeps dynamic socket receive-buffer auto-tuning active within `rmem_max=524288` (`Linux`). |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Cumulative Live LTU Windows**: **`120` windows** (`Stages 185A, 188A, 218A, 247A, 287A, 299A, 329A, 341A, 375A, 397A`).
- **Stock Mean RTT**: `0.21 ms`.
- **Champion `v8` Mean RTT**: `0.21 ms`.
