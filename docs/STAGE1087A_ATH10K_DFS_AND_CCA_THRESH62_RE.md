<!-- doc-head: STAGE1087A_ATH10K_DFS_AND_CCA_THRESH62_RE.md preserved document content -->
<!-- /doc-head -->

# Stage 1087A - ath10k DFS handlers and the CCA thresh62 surface

- **Receipt**: [`artifacts/autoresearch/stage1087a_ath10k_dfs_and_cca_thresh62_re.json`](../artifacts/autoresearch/stage1087a_ath10k_dfs_and_cca_thresh62_re.json)
- **Tool**: [`tools/re/dissect_stage1087a_ath10k_dfs_and_cca_thresh62_re.py`](../tools/re/dissect_stage1087a_ath10k_dfs_and_cca_thresh62_re.py)
- **Class**: `CONFIRMED_STATIC_BINARY`
- **Scope**: offline static ELF and archive analysis. No SSH, no live IP, no radio, no module load, no firmware write, no debugfs access on a target.
- **Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `cfg80211`, `proprietary airMAX/LTU module`.

## 0. Verdict: the premise is refuted, and the refutation is the finding

The brief carried a premise: `ath10k_core.ko` does not exist, so the five DFS handlers
cannot be read. The first clause was measured and holds for loose files. The second
clause does not follow, and is false.

| Membership test | Result |
| :--- | ---: |
| loose `.ko` files in the corpus | 1,169 |
| loose `ath10k_core.ko` files | 0 |
| tar archives holding an `ath10k_core.ko` member | 72 |
| distinct `ath10k_core.ko` hashes among those members | 1 |
| embedded member size / sha256 | 600,808 B / `d7f2d1ac07a6c91fe4284eac37bbe92e822b276a59928946ff86cb9da00ddf84` |

A file with a given sha256 must have that exact size, so the size-filtered hash search
used here is exhaustive for loose copies rather than heuristic. But a tar member is not a
loose file, and the nineteen prior confirmations only ever counted loose files. The
handlers were never measured against the archive member; the zero was inherited.

This receipt reports both numbers and refuses to overwrite the truth with the expectation.
`summary.spawner_expected_refuted` preserves the expected zeros beside the measured values
so the disagreement stays auditable rather than hidden.

## 1. The five handlers, as measured in the embedded module

All five resolve inside `.rodata.str1.4`. They are debugfs attribute names, not functions,
which is why a symbol-table probe returns zero for all five even where they are present.

| Requested name | Offset | Resolved string | Section | Symbol rows |
| :--- | ---: | :--- | :--- | ---: |
| `dfs_block_radar_events` | `0x64B1C` | `dfs_block_radar_events` | `.rodata.str1.4` | 0 |
| `dfs_simulate_radar` | `0x64B08` | `dfs_simulate_radar` | `.rodata.str1.4` | 0 |
| `dfs_stats` | `0x64B34` | `dfs_stats` | `.rodata.str1.4` | 0 |
| `quiet_period` | `0x64B50` | `quiet_period` | `.rodata.str1.4` | 0 |
| `thresh62` | `0x64B8C` | `thresh62_ext` | `.rodata.str1.4` | 0 |

They sit in one contiguous debugfs registration block, which is itself evidence that they
belong to a single table rather than to scattered code:

```
reg_value, mem_value, chip_id, restart_failed, htt_stats_mask, fw_dbglog, cal_data,
nf_cal_period, ani_enable, dfs_simulate_radar, dfs_block_radar_events, dfs_stats,
pktlog_filter, quiet_period, powerctl_table, tpc_stats, thresh62_ext, ct_special,
btcoex, peers, peer_stats, fw_checksums, tpc_stats_final, warm_hw_reset, ps_state
```

`offsets_from_ath10k = 5`, all from `.rodata.str1.4`. `offsets_from_ath10k_loose = 0`
because no loose `ath10k_core.ko` exists.

## 2. The CCA surface, which is what `thresh62` actually is

`thresh62_ext` is an eight-bit per-band CCA energy threshold, described by the driver's own
`T68` help text at `0x57A42`: `id: 3 THRESH62_EXT (both bands use same value currently)`
with `value = val & 0xFF`, and `id: 4 CCA-Values` with `band = val >> 24` and
`type = (val >> 16) & 0xFF`, where type `0` to `2` select `minCcaPwr[type]`, `3` selects
`noiseFloorThresh`, `4` selects `enable_minccapwr_thresh`.

Adjacent CCA strings, measured at file offsets: `adaptive-cca` at `0x674CD`,
`Setting disable-ibss-cca to %d` at `0x63E75`, `failed to enable adaptive cca: %d` at
`0x61D92`, `rx_drop_cac_running` at `0x58F48`, and
`failed to set quiet mode period %u duarion %u enabled %u ret %d` at `0x6CFB6`.
The `cac` count of 3 splits cleanly: two genuine DFS, one `kmalloc_caches`.

## 3. mac80211.ko, the DFS vocabulary that is genuinely present

`artifacts/canary_panel1_guarida/panel1_native_cutover_20261019/after/mac80211.ko`,
829,464 B, sha256 `19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416`,
ELF32 big-endian MIPS, 32 sections, 1,974 symtab rows, 1,621 defined. It is the only `.ko`
in that capture directory.

| DFS or radar symbol | Value | Size | Section | Exported |
| :--- | ---: | ---: | :--- | :--- |
| `ieee80211_dfs_cac_cancel` | `0x4FF60` | 332 | `.text` | no |
| `ieee80211_dfs_cac_timer_work` | `0x6253C` | 184 | `.text` | no |
| `ieee80211_dfs_radar_detected_work` | `0x500AC` | 208 | `.text` | no |
| `ieee80211_is_radar_required` | `0x5689C` | 108 | `.text` | no |
| `ieee80211_radar_detected` | `0x4A794` | 56 | `.text` | yes |

`ieee80211_radar_detected` also appears in `__ksymtab_strings` at `0x9C2DC`, and the prel32
`__ksymtab` table (115 entries, 30 in the GPL table) resolves it by name. That is a static
fact with a useful consequence: this is the entry point an out-of-tree driver calls once
its own detector fires, and it is the seam between a vendor DFS detector and the kernel.
Imported DFS names are `__cfg80211_radar_event` and `cfg80211_chandef_dfs_required`, so
mac80211 both consumes and exports the radar path.

| Token | Raw bytes | Symbol rows | First offset | Note |
| :--- | ---: | ---: | ---: | :--- |
| `chan` | 157 | 77 | `0x8B87C` | channel context machinery, not DFS specific |
| `cac` | 12 | 12 | `0xA5AED` | three are allocator `cache` false positives |
| `dfs` | 6 | 4 | `0x93C0B` | two strings, four symbol names |
| `thresh` | 6 | 0 | `0x97EB8` | `aql_threshold`, `rssi_threshold`, four EHT PPE strings |
| `radar` | 5 | 4 | `0x9C2DC` | includes the `__ksymtab_strings` entry |
| `quiet` | 1 | 0 | `0x983C0` | only `HANDLES_QUIET_CSA`, a feature flag |
| `cca` | 0 | 0 | none | absent |
| `thresh62` | 0 | 0 | none | absent |

Two negative results carry weight. mac80211 has no `cca` token at all and no `thresh62`
token at all, so the CCA-extended energy threshold is not a mac80211 concept and cannot be
cross-checked there; the six `thresh` strings are AQL, RSSI and EHT PPE, none of which is a
CCA threshold. `quiet` occurs once, inside a capability name, not in a `quiet_period`
handler.

## 4. ath_spectral.ko, the proxy that does carry radar handling

`artifacts/firmware_re_xc_ltu/wa_8725_rootfs/lib/modules/2.6.32.68/ath_spectral.ko`,
37,656 B, sha256 `2b8526b0d008258c42bbf196ac1f5af9925f16a27827eaa3a74a179b4faf048a`.
Stage 857A is the originating receipt and is cited rather than re-derived; this stage
re-measured the same copy and agrees with it.

| Measure | Value |
| :--- | ---: |
| `radar`, case sensitive | 1 |
| `RADAR`, case sensitive | 3 |
| `radar`, case insensitive | 4 |
| `dfs`, `cac`, `cca`, `quiet`, `thresh62` | 0 each |
| first radar string | `SPECTRAL : radar threshold    : %d` at `0x4D17` |

The threshold accessors that really exist here are `spectral_set_thresholds` (`0x554`, 420 B)
and `spectral_get_thresholds` (`0x1018`, 128 B), reached through debugfs names at `0x4329`,
`0x7046` and `0x7141`. Stage 857A measured `radar = 1` in all four `ath_spectral.ko` copies
and `radar = 0` in both XW `ubnt_spectral.ko` copies; this stage confirms the count on the
37,656-byte WA copy and records `agreement = true`.

## 5. The runtime snapshot disagrees with the embedded copy

The capture directory also holds an `lsmod` text snapshot reading
`ath10k_core 548864 1 ath10k_pci, Live 0x82900000 (O)`. The panel reported a 548,864-byte
live module while the only copy in the corpus is 600,808 bytes, so the running module is
not in the corpus and its debugfs surface is inferred from a sibling build rather than
proven identical. The snapshot is a quoted document from an earlier capture, not a live
probe, and the receipt labels it that way.

## 6. What remains unknown

- No airOS or Ubiquiti `ath10k_core.ko` exists anywhere in the corpus. Only an OpenWrt
  6.6.110 `ath10k-ct` build was readable, so vendor DFS behaviour stays unmeasured.
- The five names are debugfs attribute strings. The functions behind them need call-site
  disassembly of `ath10k_debug_create`, which this stage did not do. A debugfs name is not
  evidence that its write handler does anything useful, and no such claim is made.
- Whether the 548,864-byte live module exposes the same five attributes cannot be answered
  offline with the artefacts present.

## 7. Claims

| Claim | Label | Basis |
| :--- | :--- | :--- |
| the five handler names exist in an `ath10k_core.ko` | CONFIRMED | `0x64B08` to `0x64B8C`, `.rodata.str1.4` |
| the five cannot be read from ath10k | REFUTED | readable from the embedded member |
| mac80211 exports the radar entry point | CONFIRMED | `__ksymtab_strings` `0x9C2DC` |
| ath_spectral carries radar handling | CONFIRMED | `radar = 1`, 857A agreement |
| mac80211 carries a CCA `thresh62` knob | REFUTED | `cca = 0`, `thresh62 = 0` |
| the live module equals the embedded module | REFUTED | 548,864 vs 600,808 B |
| the handler write paths do any particular thing | UNKNOWN | needs call-site disassembly |
| the vendor driver's DFS surface is known | UNKNOWN | no airOS `ath10k_core.ko` in corpus |

## 8. Reproduction

```
python tools/re/dissect_stage1087a_ath10k_dfs_and_cca_thresh62_re.py --check
```

`--check` builds the payload twice in one process and asserts the serialised bytes are
identical before writing. Two separate process runs were also compared by file hash and
matched. `generated_utc` is pinned to a constant so the receipt is reproducible.
