<!-- doc-head: STAGE727A_QCA988X_SPECTRAL_SCAN_FFT_AND_RADAR_PHYERR_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 727A — spectral-scan FFT PHY errors and DFS radar PHY errors

- **Receipt**: [`artifacts/autoresearch/stage727a_qca988x_spectral_scan_fft_and_radar_phyerr_re.json`](../artifacts/autoresearch/stage727a_qca988x_spectral_scan_fft_and_radar_phyerr_re.json)
- **Tool**: [`tools/re/dissect_stage727a_qca988x_spectral_scan_fft_and_radar_phyerr_re.py`](../tools/re/dissect_stage727a_qca988x_spectral_scan_fft_and_radar_phyerr_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. `ath10k_core.ko` absent — seventh confirmation

**0 files.** `ATH10K_PHYERR_SPECTRAL` and `ATH10K_PHYERR_RADAR` are ath10k enum constants; they
cannot be read here, and they would be macros anyway. The **vendor** PHYERR path spans **four
modules** and is fully named.

| Module | Bytes | PHYERR tokens | radar tokens |
| :--- | :-: | :-: | :-: |
| `WA:umac.ko` | 2,356,432 | **34** | 37 |
| `WA:ath_dev.ko` | 287,216 | 4 | 1 |
| `WA:ath_spectral.ko` | 37,656 | 6 | 1 |
| `WA:ath_dfs.ko` | 203,796 | **19** | **43** |

## 1. The PHYERR handler is an object with a lifecycle

```
ol_ath_phyerr_attach    ol_ath_phyerr_detach
ol_ath_phyerr_enable    ol_ath_phyerr_disable
```

**`CONFIRMED`**: `phyerr_handler_named = 1`, `phyerr_lifecycle_count = 4`.

Attach and enable are **separate**. That means the PHY-error path can be **disabled without being
torn down** — which is exactly what DFS regulatory changes require: turning radar detection off
while keeping the interface alive.

## 2. Spectral control is twelve symbols, with enabled separate from active

```
init_spectral_capability        ol_if_spectral_configure_params
ol_if_ic_start_spectral_scan    ol_if_ic_stop_spectral_scan
ol_if_is_spectral_active        ol_if_is_spectral_enabled
ol_if_spectral_enable           ol_if_spectral_detach
ol_if_spectral_get_capability   ol_if_spectral_get_current_channel
ol_if_spectral_get_chain_noise_floor   ol_if_spectral_get_ctl_noisefloor
```

**`CONFIRMED`**: `spectral_symbol_count = 12`.

**`is_spectral_active` beside `is_spectral_enabled`** is the detail worth keeping: *enabled* means
configured, *active* means actually sampling. A scan can be enabled and never start — which is a real
failure mode on a bench, and the two predicates separate it from a configuration problem.

`configure_params` and `get_capability` show the scan is **parameterised and capability-gated**, not a
toggle.

## 3. The decisive finding: five PHYERR processors, four named after silicon

In `ath_dfs.ko`:

```
dfs_process_phyerr              dfs_process_phyerr_bb_tlv
dfs_process_phyerr_merlin       dfs_process_phyerr_owl
dfs_process_phyerr_sowl
```

**`CONFIRMED`**: `phyerr_processor_count = 5`, `chip_generation_count = 4`
(`bb_tlv`, `merlin`, `owl`, `sowl`).

The PHY-error **payload format differs per Atheros generation**, so the radar detector is a **family
of parsers selected by chip**, not one parser. A radar finding on one generation does not transfer to
another — the same lesson as TxBF in Stage 615A and the bin detectors in Stage 499A.

The dispatcher is completed by:

```
dfs_init_radar_filters    dfs_process_radarevent
dfs_radar_enable          dfs_radar_disable        dfs_reset_radarq
```

`dfs_reset_radarq` is a **queue reset** for radar events, so radar findings are **queued**, not
handled inline.

## 4. Regulatory radar tables are per domain

```
etsi_radartool_alow       fcc_radartool_alow
```

**`CONFIRMED`**: `regulatory_tool_count = 2`.

ETSI and FCC have different pulse-width and PRI tolerances, so the radar tool's **acceptance table is
per regulatory domain**. A detector tuned for ETSI is not the FCC detector; the module keeps both.

## 5. Where the spectral predicate actually lives

`is_spectral_phyerr` is in **`ath_spectral.ko`** (4 hits) — **not** in `umac.ko`, where the first
probe returned 0.

**`CONFIRMED`**: `spectral_predicate_present = 1`, `spectral_predicate_modules = ['WA:ath_spectral.ko', ...]`.

That is a methodology note with teeth: a single-module sweep would have concluded the predicate does
not exist. The classification of "is this PHY error a spectral sample or a radar pulse" sits in the
spectral module, one layer away from the PHY-error handler.

## 6. The WMI commands are VDEV-scoped

```
WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID     WMI_VDEV_SPECTRAL_SCAN_ENABLE_CMDID
```

**`CONFIRMED`**: `wmi_command_count = 2`.

Stage 451A established these are **VDEV**, not PDEV — per virtual interface. So the scan is configured
per VAP, consistent with the per-VAP enable in §1.

`phyerr_code_table_recovered = 0`: the numeric PHY-error codes are an ath10k concept with no named
vendor equivalent, and no numeric table was located.

## 7. What is established

| Claim | Status |
| :--- | :-: |
| `ath10k_core.ko` exists | **REFUTED** (0 files) |
| `ATH10K_PHYERR_SPECTRAL` / `_RADAR` are readable | **REFUTED** |
| the PHYERR handler has attach/detach and enable/disable | **CONFIRMED** (4 calls) |
| spectral control is a 12-symbol parameterised surface | **CONFIRMED** |
| enabled and active are separate predicates | **CONFIRMED** |
| radar PHYERR has **five** processors, four per generation | **CONFIRMED** |
| radar events are queued (`dfs_reset_radarq`) | **CONFIRMED** |
| the radar tool table is per regulatory domain | **CONFIRMED** (ETSI + FCC) |
| `is_spectral_phyerr` is in `ath_spectral.ko`, not `umac.ko` | **CONFIRMED** |
| the spectral WMI commands are VDEV-scoped | **CONFIRMED** |
| the numeric PHY-error code table | **UNKNOWN / no vendor equivalent** |
| the FFT bin format | **UNKNOWN** (451A's limit stands) |

## 8. The operational reading

For a "spectral scan shows nothing" symptom, the two predicates give the first cut: if
`is_spectral_enabled` is 1 and `is_spectral_active` is 0, the scan was **configured but never
started** — a configuration or capability problem, not a signal problem.

For a radar false-positive, the **per-generation** processors and the **per-domain** tables both
matter: a detector behaving differently on two AP models is expected, because they run different
parsers; and the same pulse can be accepted by FCC and rejected by ETSI.

## 9. Gaps

- **`UNKNOWN`** — the numeric PHY-error codes and the dispatch table over them.
- **`UNKNOWN`** — the payload format of each of the four per-generation parsers.
- **`UNKNOWN`** — the ETSI-versus-FCC acceptance parameters.
- **`UNKNOWN`** — the FFT bin format (451A's limit).
- **`UNKNOWN`** — how `is_spectral_phyerr` decides, beyond its name.
- **Known limit** — five named processors prove per-generation dispatch, not the formats.
- **Not attempted** — dynamic validation, radar injection.
