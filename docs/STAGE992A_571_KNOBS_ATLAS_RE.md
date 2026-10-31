<!-- doc-head: Stage 992A 571-knob catalog atlas with measured binary-reference provenance; 457 of 571 reference-provenanced (0.80035), 114 gaps enumerated by name; offline, no radio, coverage measured not guaranteed -->
# Stage 992A - 571-Knob Catalog Atlas & Binary-Reference Provenance

- **Claim status**: `CONFIRMED_STATIC_BINARY` for the measurement; `UNKNOWN` for
  anything a knob would do on a radio.
- **Attribution**: `static binary corpus (offline)`. No device, no controller,
  no firmware attribution is made by this stage.
- **Scope**: read-only. No SSH, no radio, no firmware read or write, no
  modification of `tools/qca988x/sgmt_container_inspector.py` or
  `firmware/xtensa_sgmt_surgical_patcher.py`.
- **Receipt**: `artifacts/autoresearch/stage992a_571_knobs_atlas_re.json`
- **Tool**: `tools/verify/verify_stage992a_571_knobs_atlas_re.py`

## 1. What this stage actually measured

The catalog `orchestration/autoresearch/firmware_knob_candidates.json`
(`schema_version` 1, `audit_id` `FMX-KNOB-AUDIT-20261024`) holds exactly 571
knobs, 42 sources and 6 firmware identities. For every knob the atlas records
the identifier, the family, the boundary, the addressing mode, whether the knob
names a module, whether it names a register, its declared binary anchor, and
whether any receipt in the corpus ties that anchor to a binary with
`CONFIRMED_STATIC_BINARY` provenance.

The provenance field used, in this receipt and in Stage 993A, is
`evidence_provenance_class`, accepted value `CONFIRMED_STATIC_BINARY`. No second
field is consulted, so the two stages are directly comparable.

**Link rule.** A knob counts as provenanced when at least one receipt whose
`evidence_provenance_class` equals `CONFIRMED_STATIC_BINARY` contains, anywhere
in its string pool, either the exact catalog source path or the exact catalog
sha256 of a module or firmware anchor declared by that knob's `source_refs`.
This is *reference* provenance. It proves a provenanced receipt names the binary
a knob is declared against; it does not prove the knob was located, decoded or
validated inside that binary.

## 2. Measured versus missing

| Quantity | Measured | Missing | Total | Fraction |
| :--- | ---: | ---: | ---: | ---: |
| Knobs with provenanced binary reference | 457 | 114 | 571 | 0.80035 |
| Knobs naming a module | 457 | 114 | 571 | 0.80035 |
| Knobs naming a register | 14 | 557 | 571 | 0.02452 |
| Knobs with a declared binary anchor | 457 | 114 | 571 | 0.80035 |

Arithmetic: `457 + 114 = 571`. Coverage is `457 / 571 = 0.80035`, printed to
five decimals, and `0.80035 * 100 = 80.03` percent. The partition is asserted
inside the verifier, so a future drift cannot silently unbalance the table.

This coverage figure is measured, and it is not a guarantee of correctness. It
falls materially short of 100 percent, and the 114 shortfall knobs are named
individually in section 5. Nothing in this document asserts that the 457 covered
knobs are safe, tested, or present on any particular deployed radio.

**Why 457 will not rise while this catalog stands.** All 457 knobs that declare
a binary anchor are already referenced by a provenanced receipt: the count of
anchored-but-unprovenanced knobs is 0, and the receipt records that as
`saturation.knobs_anchored_without_provenance`. Coverage is therefore capped by
the catalog rather than by the receipt corpus, and publishing further receipts
cannot move it. Only a catalog change that declares a binary anchor for a
currently anchorless knob can raise 457, and no such change is proposed here.
The corpus snapshot itself is volatile because sibling stages publish receipts
concurrently; the receipt records the exact file count, the provenanced-receipt
count and a `corpus_digest_sha256`, while the 457 and 114 figures above are
stable against that churn.

## 3. Where the 457 covered knobs sit

| Primary anchor module | Knobs |
| :--- | ---: |
| `umac.ko` | 369 |
| `ubnt_poll_host.ko` | 34 |
| `wa_8725_ubnt_poll_host.ko` | 34 |
| `ame_dev.ko` | 20 |
| `<no_binary_source>` | 114 |
| **Total** | **571** |

Every primary anchor that exists is a module; no knob resolves to a
firmware-kind primary anchor. The primary anchor is the lowest source id among
the knob's `source_refs` that resolve to kind `module` or `firmware`, which keeps
this table summing exactly to `knobs_total`; every declared binary source is
still kept per knob in `atlas[].binary_source_ids`.

| Family | Covered | Gap | Addressing mode |
| :--- | ---: | ---: | :--- |
| `airos_ioctl` | 339 | 0 | `ioctl_handler` |
| `airos_sysctl` | 68 | 0 | `sysctl_handler` |
| `airos_module` | 30 | 0 | `module_load` |
| `ltu_sysfs` | 20 | 0 | `sysfs_handler` |
| `wmi_vdev` | 0 | 45 | `firmware_message` |
| `wmi_pdev` | 0 | 42 | `firmware_message` |
| `ct_special` | 0 | 14 | `firmware_message` |
| `ath10k` | 0 | 5 | `firmware_message`, `host_ram` |
| `mac80211` | 0 | 3 | `firmware_message` |
| `policy_only` | 0 | 3 | `policy_metadata` |
| `htt` | 0 | 1 | `firmware_message` |
| `hardware` | 0 | 1 | `hardware_control` |
| **Total** | **457** | **114** | |

The pattern is unambiguous and is not a rendering artefact: the four airOS and
LTU families have a `.ko` or firmware path declared in the catalog and are
covered; the QCA firmware, ath10k, mac80211 and policy families cite driver
source text, local analysis and snapshots, never a binary. Their gap reason is
therefore `NO_BINARY_ANCHOR_DECLARED_IN_CATALOG`, not a missing search.

## 4. The catalog's own confidence field was not used as evidence

All 571 entries self-declare `confidence: CONFIRMED`. That is a catalog
assertion, not a measurement, and the atlas deliberately ignores it. The
measured figure is 457 of 571, which is the number an operator should read. A
self-declared 571 of 571 would have been a false 100 percent.

## 5. The 114 gaps, by name

Every knob below lacks a provenanced binary reference. None is omitted, none is
invented, and the verifier fails if any of these identifiers is absent from this
document.

```
ct_special_3, ct_special_4, ct_special_5, ct_special_6, ct_special_7, ct_special_8,
ct_special_9, ct_special_10, ct_special_11, ct_special_12, ct_special_13, ct_special_14,
ct_special_15, ct_special_16, aql_txq_limit, aql_threshold, fq_quantum, htt_aggr_size,
rts_threshold, coverage_class, vht_mcs_mask, set_rates, set_rate_override,
wmi10_1_pdev_tx_chain_mask, wmi10_1_pdev_rx_chain_mask, wmi10_1_pdev_txpower_limit2g,
wmi10_1_pdev_txpower_limit5g, wmi10_1_pdev_txpower_scale, wmi10_1_pdev_beacon_gen_mode,
wmi10_1_pdev_beacon_tx_mode, wmi10_1_pdev_resmgr_offchan_mode, wmi10_1_pdev_protection_mode,
wmi10_1_pdev_dynamic_bw, wmi10_1_pdev_non_agg_sw_retry_th, wmi10_1_pdev_agg_sw_retry_th,
wmi10_1_pdev_sta_kickout_th, wmi10_1_pdev_ac_aggrsize_scaling, wmi10_1_pdev_ltr_enable,
wmi10_1_pdev_ltr_ac_latency_be, wmi10_1_pdev_ltr_ac_latency_bk, wmi10_1_pdev_ltr_ac_latency_vi,
wmi10_1_pdev_ltr_ac_latency_vo, wmi10_1_pdev_ltr_ac_latency_timeout,
wmi10_1_pdev_ltr_sleep_override, wmi10_1_pdev_ltr_rx_override,
wmi10_1_pdev_ltr_tx_activity_timeout, wmi10_1_pdev_l1ss_enable, wmi10_1_pdev_dsleep_enable,
wmi10_1_pdev_pdev_stats_update_period, wmi10_1_pdev_vdev_stats_update_period,
wmi10_1_pdev_peer_stats_update_period, wmi10_1_pdev_bcnflt_stats_update_period,
wmi10_1_pdev_pmf_qos, wmi10_1_pdev_arp_ac_override, wmi10_1_pdev_dcs, wmi10_1_pdev_ani_enable,
wmi10_1_pdev_ani_poll_period, wmi10_1_pdev_ani_listen_period, wmi10_1_pdev_ani_ofdm_level,
wmi10_1_pdev_ani_cck_level, wmi10_1_pdev_dyntxchain, wmi10_1_pdev_fast_channel_reset,
wmi10_1_pdev_burst_dur, wmi10_1_pdev_burst_enable, wmi10_1_pdev_cal_period,
wmi10_1_vdev_rts_threshold, wmi10_1_vdev_fragmentation_threshold, wmi10_1_vdev_beacon_interval,
wmi10_1_vdev_listen_interval, wmi10_1_vdev_multicast_rate, wmi10_1_vdev_mgmt_tx_rate,
wmi10_1_vdev_slot_time, wmi10_1_vdev_preamble, wmi10_1_vdev_swba_time,
wmi10_1_vdev_wmi_vdev_stats_update_period, wmi10_1_vdev_wmi_vdev_pwrsave_ageout_time,
wmi10_1_vdev_wmi_vdev_host_swba_interval, wmi10_1_vdev_dtim_period,
wmi10_1_vdev_wmi_vdev_oc_scheduler_air_time_limit, wmi10_1_vdev_wds, wmi10_1_vdev_atim_window,
wmi10_1_vdev_bmiss_count_max, wmi10_1_vdev_feature_wmm, wmi10_1_vdev_chwidth,
wmi10_1_vdev_chextoffset, wmi10_1_vdev_disable_htprotection, wmi10_1_vdev_sta_quickkickout,
wmi10_1_vdev_mgmt_rate, wmi10_1_vdev_protection_mode, wmi10_1_vdev_fixed_rate, wmi10_1_vdev_sgi,
wmi10_1_vdev_ldpc, wmi10_1_vdev_tx_stbc, wmi10_1_vdev_rx_stbc, wmi10_1_vdev_intra_bss_fwd,
wmi10_1_vdev_def_keyid, wmi10_1_vdev_nss, wmi10_1_vdev_bcast_data_rate,
wmi10_1_vdev_mcast_data_rate, wmi10_1_vdev_mcast_indicate, wmi10_1_vdev_dhcp_indicate,
wmi10_1_vdev_unknown_dest_indicate, wmi10_1_vdev_ap_keepalive_min_idle_inactive_time_secs,
wmi10_1_vdev_ap_keepalive_max_idle_inactive_time_secs,
wmi10_1_vdev_ap_keepalive_max_unresponsive_time_secs, wmi10_1_vdev_ap_enable_nawds,
wmi10_1_vdev_mcast2ucast_set, wmi10_1_vdev_enable_rtscts,
wmi10_1_vdev_ap_detect_out_of_sync_sleeping_sta_time_secs, wmi10_1_vdev_rc_num_retries,
codel_target, codel_interval, cake_bandwidth, airprism_gpio_hsr
```

## 6. What closes this gap

A gap closes only when a `CONFIRMED_STATIC_BINARY` receipt names the catalog
source path or sha256 of a binary that carries the knob. For the 114 QCA
firmware and driver-source knobs that means extracting the WMI/CT message table
or the driver object itself and recording it with that provenance class. Adding
a narrative cross-reference, or relabelling an existing `SIMULATED_MODEL_ONLY`
receipt, does not close a gap and would be a provenance forgery.

## 7. Reproduction

```
python tools/verify/verify_stage992a_571_knobs_atlas_re.py
python tools/verify/verify_stage992a_571_knobs_atlas_re.py --check
```

The second command re-measures and compares byte-for-byte with the committed
receipt. The receipt carries no wall-clock field by design; its corpus digest
covers file names and hashes so any change in the receipt population is visible
rather than silent.
