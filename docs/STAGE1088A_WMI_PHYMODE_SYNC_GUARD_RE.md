<!-- doc-head: STAGE1088A_WMI_PHYMODE_SYNC_GUARD_RE.md preserved document content -->
<!-- /doc-head -->

# Stage 1088A - audit of `fmx_wmi_peer_phymode_sync_guard.sh`

- **Receipt**: [`artifacts/autoresearch/stage1088a_wmi_phymode_sync_guard_re.json`](../artifacts/autoresearch/stage1088a_wmi_phymode_sync_guard_re.json)
- **Tool**: [`tools/re/audit_stage1088a_wmi_phymode_sync_guard_re.py`](../tools/re/audit_stage1088a_wmi_phymode_sync_guard_re.py)
- **Target**: `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_wmi_peer_phymode_sync_guard.sh`, 974 bytes
- **Class**: `CONFIRMED_STATIC_BINARY`
- **Scope**: offline static audit. No SSH, no live IP, no radio, no device access, audited script never executed.

## 0. Verdict

The file is a **deliberate retirement stub**, not a thin wrapper around WMI logic and not an
accident. It holds no WMI reference, no phymode reference, no debugfs access, no Mac80211 and
no ath10k string; its only provable behaviour is to print a retirement notice and, for any
mutating mode, exit 65.

`verdict = RETIRED_STUB_EFFECT_NONE`, `claims_total = 9`, `claims_provable = 5`. The WMI peer
phymode synchronisation the filename advertises cannot be established offline, because the
818-byte artefact Stage 586A recorded is absent. The wrapper is gone and only the refusal remains.

## 1. The file, in full

```sh
#!/bin/sh
# Legacy actuator retired: no direct firmware/configuration/device commands remain.
# Original source bytes are retained privately; this release does not activate them.
set -eu
set -f
MODE=--dry-run
QDISC_MODE=auto
SEEN_MODE=0
while [ "$#" -gt 0 ]; do
 case "$1" in
  --dry-run|--inspect-only|--apply|--verify|--rollback)
   [ "$SEEN_MODE" -eq 0 ] || exit 64; MODE=$1; SEEN_MODE=1; shift ;;
  --qdisc-mode) [ "$#" -ge 2 ] || exit 64; QDISC_MODE=$2; shift 2 ;;
  --identity|--state-dir|--uci-mode) [ "$#" -ge 2 ] || exit 64; shift 2 ;;
  *) printf 'FAILED_PRECONDITION retired legacy argument\n' >&2; exit 65 ;;
 esac
done
case "$QDISC_MODE" in auto|tc|sysfs-default) ;; *) exit 64 ;; esac
case "$MODE" in
 --dry-run|--inspect-only)
  printf 'PLANNED_RETIRED native_replacement=EXPLICIT_SEPARATE_TRANSACTION runtime=UNKNOWN\n'; exit 0 ;;
 *) printf 'FAILED_PRECONDITION legacy actuator retired; select reviewed native transaction explicitly\n' >&2; exit 65 ;;
esac
```

sha256 `edf58be7c1335da3d6e1daf3200ee63acf503e0c52dacf7ec7270480165aba4a`, 974 bytes, 23 lines.

## 2. Command census

Every non-comment fragment is classified, and the tool fails closed if one is unclassified.
Fragment totals: 19 commands, 7 keywords, 6 assignments, 3 case patterns, 8 separators, 0 unaccounted.

| Command | Count | Kind | Device mutating |
| :--- | ---: | :--- | :--- |
| `exit` | 7 | shell builtin | no |
| `[` | 4 | shell builtin | no |
| `printf` | 3 | shell builtin | no |
| `shift` | 3 | shell builtin | no |
| `set` | 2 | shell builtin | no |

`commands_total = 19`, all builtins, `external_commands = []`, `device_mutating_commands = []`.
Reachable exit codes are `0` at line 21, `64` at lines 12, 13, 14 and 18, and `65` at lines 15
and 22. That is the entire behavioural surface. Redirections are two `>&2` duplications and
zero writes to a file, so nothing here can mutate state even if run.

## 3. Reference census

| Token | Word-boundary hits | Reading |
| :--- | ---: | :--- |
| `wmi`, `phymode`, `phy_mode`, `debugfs` | 0 each | absent |
| `mac80211`, `ath10k`, `ath_spectral` | 0 each | absent |
| `iw`, `iwpriv`, `echo`, `radar`, `dfs`, `reg`, `nvram` | 0 each | absent |
| `uci` | 1 | only the literal option name `--uci-mode` |
| `sysfs` | 1 | only the literal case pattern `sysfs-default` |

So `wmi_refs = 0`, `phymode_refs = 0`, `debugfs_writes = 0`. The two nonzero tokens are argument
vocabulary, not commands, and are reported rather than suppressed.

## 4. The 974-byte class

Eighteen files in the kit are 974 bytes and all eighteen share one sha256, so this is a single
artefact distributed under eighteen names rather than eighteen thin wrappers.

| Group | Files |
| :--- | :--- |
| `99-fmx` hotplug hooks | `99-fmx-pbe5ac-ptp`, `-ptp-ap`, `-ptp-ap-241`, `-ptp-sta`, `-ptp-sta-242`, `99-fmx-wa-ptp-champion-v2`, `-v3`, `-v4`, `99-fmx-wa-universal-champion`, `-v4`, `99-fmx-wmm-dscp-qos` |
| rollback watchdogs | `fmx_ptp_rollback_watchdog_ap_241.sh`, `fmx_ptp_rollback_watchdog_sta_242.sh` |
| other | `enable_airos8_ap_hybrid_80211_for_openwrt_sta.sh`, `fmx_pbe5ac_admitter.sh`, `fmx_pbe5ac_dynamic_phy_and_sgmt_loader.sh`, `restore_stock_airos8_with_known_cfg.sh`, the audited guard |

The kit holds 9 `fmx_*` scripts and 5 of them are this stub. The four that are real are
`fmx_pbe5ac_v16_statless_tcless_busybox_kit.sh` (9,029 B),
`fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh` (12,029 B),
`fmx_pbe_lbe_runtime_transaction.sh` (13,033 B) and `fmx_ptp_rollback_watchdog.sh` (9,770 B).

Stated plainly: every PTP boot hook in this kit is inert, and both per-node rollback watchdogs
are inert while the base watchdog is real. Any operational assumption that a `99-fmx` hook fires
at boot, or that nodes 241 and 242 carry a working rollback watchdog, is unsupported by the
shipped bytes. All 22 `SHA256SUMS` entries verify, so the stub state is the intended published
state rather than corruption.

## 5. Stage 586A does not describe the file that ships

Stage 586A records `status: CONFIRMED`, `deployed_on_241_and_242: true`, and a `deploy_readback`
showing a 2,885-byte hotplug helper and an 818-byte guard on both nodes, with
`guard_sha256 = abecd564613b...` and `helper_sha256 = d69a809cee96...`.

The file at that exact path today is 974 bytes with sha256 `edf58be7c133...`. A size-filtered
hash search over the whole working tree found 21 candidates at the recorded sizes and zero
matches for either hash. Because a file with a given sha256 must have that exact size, the
filter is exhaustive rather than heuristic. The guard 586A certified has been replaced, and
what the 818-byte version did is unknown, not merely unproven.

## 6. Claims

| Id | Claim | Label | Basis |
| :--- | :--- | :--- | :--- |
| C1 | no direct firmware, configuration or device commands remain | CONFIRMED | 19 invocations, all builtins, zero external |
| C2 | original bytes are retained privately | UNKNOWN | retention is unobservable, no private copy in corpus |
| C3 | a dry run reports `PLANNED_RETIRED` and exits 0 | CONFIRMED | line 21 |
| C4 | a reviewed native replacement transaction exists | UNKNOWN | the string names a policy, not a path |
| C5 | runtime behaviour cannot be established from this file | CONFIRMED | no observation path exists |
| C6 | an unrecognised argument is refused with 65 | CONFIRMED | catch-all arm, line 15 |
| C7 | `--apply` is refused with 65 and no mutation | CONFIRMED | no `--apply` arm, falls to line 22 |
| C8 | the file synchronises the WMI peer phymode | REFUTED | `wmi = 0`, `phymode = 0`, `debugfs = 0` |
| C9 | 586A's CONFIRMED deployment describes today's guard | REFUTED | hash and size mismatch, zero corpus copies |

`claims_provable = 5` and `claims_unprovable = [C2, C4, C8, C9]`, where C8 and C9 are provably
false rather than merely unproven; `claim_counts` records that split.

## 7. The domain is real, which is why the stub matters

Absence in this file is not absence in the corpus, and that is what makes the stub a gap.

- Stage 589A measured `WMI_PEER_ASSOC_CMDID` and `WMI_PEER_RATE_RETRY_SCHED_CMDID` in `umac.ko`,
  with 10 phymode symbols including `wlan_get_current_phymode` and `wlan_get_desired_phymode`.
- Re-measured on `.../wa_8725_rootfs/.../umac.ko` (2,356,432 B): `WMI_PEER_ASSOC_CMDID` 1, `WMI_`
  188, `phymode` 15, `wlan_get_desired_phymode` 1. The exact token `peer_phymode` is 0, and
  `ath10k_peer_assoc_h_phymode` is 0 because that symbol lives in ath10k_core, not umac.
- Stage 947A's `mac80211.ko` sha256 matches the Stage 1087A capture, so that side is shared evidence.
- Stage 857A measured `radar = 1` in all four `ath_spectral.ko` copies and `radar = 0` in both XW
  `ubnt_spectral.ko` copies, so the radar half of the stack is evidenced on WA and XC.
- Real WMI-bearing actuators do exist here, at
  `firmware/openwrt/common/fmx_qca988x_wmi_peer_rate_sgi_guard.sh` (2,044 B, `wmi` 10, `phymode`
  2, `peer_assoc` 5, `--apply` 2) and `.../fmx_qca988x_peer_sgi_retry_helper.sh` (1,789 B). No
  file under that directory carries the WMI phymode guard name.

The capability the stub points at plausibly exists under a different name, but the stub names no
destination and no destination can be confirmed. Reading it as a working synchroniser would
upgrade an unprovable claim because the script looks plausible, which is the exact error this
stage exists to prevent.

## 8. What this stage does not establish, and the follow-up

- It does not establish that the 818-byte guard ever worked; that artefact is gone.
- It does not establish that nodes 241 and 242 are in a bad state, only that the shipped kit
  cannot put them into the state 586A described.
- It does not execute the script. Running it would show that a retirement notice prints, which
  the text already shows, and would add a live-provenance claim for no information.
- Stage 1086A did not exist at run time, so mac80211 symbols are cited from 947A and re-measured
  directly instead of cross-checked.

Follow-up: re-grade Stage 586A from `CONFIRMED` to `UNKNOWN` for the deployment claim, because
its recorded artefacts are absent. If the phymode synchronisation is still wanted, point the kit
at a named file and record the sha256 of whatever is actually deployed in the same receipt.

## 9. Reproduction

```
python tools/re/audit_stage1088a_wmi_phymode_sync_guard_re.py --check
```

`--check` builds the payload twice in one process and asserts identical bytes before writing.
Two separate process runs were also compared by file hash and matched. The total file count is
deliberately not emitted, because other agents write into this tree while the tool runs.
