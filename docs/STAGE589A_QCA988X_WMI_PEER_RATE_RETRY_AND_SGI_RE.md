<!-- doc-head: STAGE589A_QCA988X_WMI_PEER_RATE_RETRY_AND_SGI_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 589A — peer phymode, VHT rates, SGI masks and retry descriptors

- **Receipt**: [`artifacts/autoresearch/stage589a_qca988x_wmi_peer_rate_retry_and_sgi_re.json`](../artifacts/autoresearch/stage589a_qca988x_wmi_peer_rate_retry_and_sgi_re.json)
- **Tool**: [`tools/re/build_stage589a_qca988x_wmi_peer_rate_retry_and_sgi_re.py`](../tools/re/build_stage589a_qca988x_wmi_peer_rate_retry_and_sgi_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. The vocabulary is in exactly one module

The stage names three modules. Only one carries anything:

| Module | Total hits across the token set |
| :--- | :-: |
| `WA:umac.ko` | **95** |
| `XC:umac.ko` | **95** |
| `WA:ath_dev.ko` | **0** |
| `XC:ath_dev.ko` | **0** |
| `WA:ubnt_poll_host.ko` | **0** |
| `XC:ubnt_poll_host.ko` | **0** |

**`CONFIRMED`**: `vocab_is_umac_only = 1`. `ath_dev.ko` and `ubnt_poll_host.ko` are **completely
empty** of peer-rate vocabulary — not a sampling artefact, and identical on both AC images.

That is a structural result worth stating plainly: the per-peer rate descriptor is built **entirely
in the UMAC**. The device layer never sees a `phymode`, a VHT rate set or an SGI mask. Anyone
hunting for peer rate control in `ath_dev.ko` is looking in the wrong module.

## 1. phymode: a family of accessors, not a field

Ten distinct symbols:

```
wlan_get_current_phymode        wlan_set_desired_phymode
wlan_channel_phymode            wlan_get_bss_phymode
wlan_get_desired_phymode        wlan_scan_entry_phymode
ieee80211_scan_entry_phymode    ieee80211_update_ht_vht_phymode
ieee80211_phymode_name          ieee80211_phymode_to_name
```

**`CONFIRMED`**: `phymode_symbol_count = 10`. There is a **current** and a **desired** value, a
**BSS** value and a **scan-entry** value kept separately, plus a converter to and from a name.

**`UNKNOWN`**: the enumeration values behind `phymode`. The names are accessors; the numeric codes
are not in the strings.

## 2. VHT rates are set up per peer

```
ieee80211_setup_vht_rates       ieee80211_set_vht_rates
ol_ath_vht_rate_setup           rate_init_peer_ratectxt
```

**`CONFIRMED`**: `peer_ratectxt_present = 1` — there is a **per-peer rate context** initialised by
`rate_init_peer_ratectxt`. The VHT rate set is not global; it is built per association.

## 3. SGI is a per-rate mask with a default threshold

```
_RATE_SetSGIMasks               _RATE_GetSGIFlag
g_default_sgi_per_thresh
```

**`CONFIRMED`**: `sgi_is_per_rate_mask = 1`. There is a **setter of masks** (plural) and a
**default per threshold** (`g_default_sgi_per_thresh`). So SGI eligibility is a **bitmap over
rates**, seeded from a per-threshold default — not a single "enable short GI" bit.

**`UNKNOWN`**: the bitmap width and its bit order.

## 4. Two log lines make the descriptor observable

This is the most useful part of the stage, because it turns three static findings into something a
bench can read:

```
RATE: ChainMask %d, phymode %d, ni_flags 0x%08x, vht_mcs_set 0x%04x, ht_mcs_set 0x%04x
```

**`CONFIRMED`**: `rate_descriptor_line_present = 1`. One line carries **chainmask, phymode,
ni_flags, vht_mcs_set and ht_mcs_set**. That is the per-peer rate descriptor rendered as text — the
exact tuple the stage is trying to dissect, available at runtime without any patching.

```
SGI counts (0..9): …     NSS counts: 1x1 %u, 2x2 %u, 3x3 %u, 4x4 %u
```

**`CONFIRMED`**: `sgi_count_line_present = 1`. It prints **SGI counts per MCS index 0..9** plus an
NSS histogram. So the SGI mask's *effect* is countable per MCS on a live system.

Those two lines are the practical deliverable: an operator can read what the peer negotiated instead
of inferring it from throughput.

## 5. Both WMI command names are present

```
…WMI_PEER_ASSOC_CMDID…
…WMI_PEER_RATE_RETRY_SCHED_CMDID…
```

**`CONFIRMED`**: `wmi_command_count = 2`. Both names the stage asks about are real strings in the
UMAC name table.

**`REFUTED`**: the retry-schedule **descriptor** cannot be laid out. Stage 372A already showed that
`series_bw` — one of the five field names the descriptor needs — does **not** exist, and `retry_sched`
does not appear either. The command is named; its 4-series payload is not describable from strings.

`retry_descriptor_values_recovered = 0`.

## 6. What is established

| Claim | Status |
| :--- | :-: |
| the peer-rate vocabulary exists in `ath_dev.ko` | **REFUTED** (0 hits, both images) |
| it exists in `ubnt_poll_host.ko` | **REFUTED** (0 hits, both images) |
| it exists in `umac.ko` | **CONFIRMED** (95 hits each) |
| `phymode` has current / desired / BSS / scan values | **CONFIRMED** (10 symbols) |
| a per-peer rate context exists | **CONFIRMED** (`rate_init_peer_ratectxt`) |
| SGI is a per-rate mask with a default threshold | **CONFIRMED** (`_RATE_SetSGIMasks`) |
| the rate descriptor is printable at runtime | **CONFIRMED** (chainmask/phymode/mcs_set line) |
| per-MCS SGI counts are printable | **CONFIRMED** (`SGI counts (0..9)`) |
| `WMI_PEER_ASSOC_CMDID` and `PEER_RATE_RETRY_SCHED` are named | **CONFIRMED** |
| the retry-schedule 4-series layout | **UNKNOWN / not derivable** |
| the SGI bitmap layout | **UNKNOWN / runtime data** |
| the phymode enumeration values | **UNKNOWN / not recovered** |

## 7. The operational reading

Three things can be read off a live AC radio with no patching, because the UMAC prints them:

1. the **negotiated descriptor** — chainmask, phymode, `vht_mcs_set`, `ht_mcs_set`;
2. the **SGI distribution per MCS** — whether short GI is actually being used, and at which rates;
3. the **NSS histogram** — how many peers are 1x1, 2x2, 3x3, 4x4.

That answers the "is this station really at 2x2 VHT with SGI" question directly, which is exactly
the question Stage 437A's FMX-DISC-40 discussion needed and could not settle statically.

## 8. Gaps

- **`UNKNOWN`** — the SGI bitmap bit order and width.
- **`UNKNOWN`** — the phymode enumeration values.
- **`UNKNOWN`** — the VHT rate table contents per MCS/NSS.
- **`UNKNOWN`** — the retry-schedule descriptor layout; `series_bw` is absent (Stage 372A).
- **`UNKNOWN`** — what `ni_flags` bits mean.
- **Known limit** — a setter name proves a mask exists, not what it contains.
- **Not attempted** — dynamic validation, on-air capture of the log lines.
