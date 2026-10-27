<!-- doc-head: Stage 885A post-audit hardening of WA v14/v15 + LTU v21 field kits to the A01/A02 remediation standard; set -eu, dry-run default, --apply gate, snapshot/verify/rollback, fixed fq_codel, no || true -->
# Stage 885A — Post-Audit Field-Kit Hardening (WA v14/v15 + LTU v21)

- **Claim Status**: `CONFIRMED` (offline static shell audit)
- **Attribution**: `external controller (offline static audit)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage885a_post_audit_field_kits_hardening.json`
- **Tool**: `tools/verify/build_stage885a_post_audit_field_kits_hardening.py`
- **Evidence class**: `CONFIRMED_STATIC_SHELL_AUDIT`

## 1. Context
The ChatGPT audit (`artifacts/chatgpt_audit_1afaeb7/AUDITORIA_2026-10-27.md`) found
`fmx_wa_v13_344window_field_kit.sh` fail-open (A01) and carrying an `initial_quantum`
fq_codel token rejected by iproute2 (A02). The v13 kit is owned by another lane and
was **not edited**. The v14/v15/v21 kits did **not exist** at the audited snapshot;
they were **created here** to the hardened v13 contract.

## 2. Kits created
| Kit | Path | Lines |
| :--- | :--- | :--- |
| WA v14 (356-window) | `firmware/openwrt/common/fmx_wa_v14_356window_field_kit.sh` | 130 |
| WA v15 (368-window) | `firmware/openwrt/common/fmx_wa_v15_368window_field_kit.sh` | 130 |
| LTU v21 (276-window) | `firmware/openwrt/common/fmx_ltu_v21_276window_field_kit.sh` | 111 |

## 3. Hardening contract (A01/A02 remediation)
Each kit statically satisfies:
- `set -eu` and `set -f`.
- **Default mode `--dry-run`** (inspect only); `--apply` is required to touch the system.
- **No `|| true`** anywhere — errors propagate.
- fq_codel contract **`quantum 1514 target 5ms interval 100ms flows 1024 ecn`**, no
  `initial_quantum`, and an explicit guard that rejects `initial_quantum` in readback
  (never silently substitutes `fq`).
- **Snapshot** to `/tmp/fmx_kit_snapshot/<profile>` before apply; `--verify` does a
  real readback; `--rollback` restores and re-verifies.
- Success marker `APPLIED_VERIFIED` is emitted **only after** a passing readback.
- WA kits: board allowlist via `ubus system board` (no blind phy0 fallback).
- LTU v21: **HARD guarantee of zero `/dev/ame*` touch**; tunes only Linux datapath
  (eth fq_codel, IRQ `smp_affinity`, `tx_queue_len`, 3 sysctls).

## 4. Verification
- `sh -n` syntax clean on all three.
- `--dry-run` (default, no args) prints the plan and exits 0 without touching anything.
- The 885A static auditor reports `all_kits_hardened=true` (every contract check passes).
- `target_patch_execution=UNKNOWN` is stated explicitly — these kits tune Linux queues,
  they do not prove any firmware/MAC change on the target.

## 5. Reproduce & limits
```sh
sh firmware/openwrt/common/fmx_wa_v14_356window_field_kit.sh        # dry-run plan
python tools/verify/build_stage885a_post_audit_field_kits_hardening.py
python -m pytest tests/test_stage885a_to_890a_suite.py -q
```
Static audit only: the hardening contract is verified by inspection; the kits were
**not executed against a live OpenWrt/LTU target** in this offline role. Live
`--apply`/`--verify`/`--rollback` behaviour must be confirmed on hardware before field use.
