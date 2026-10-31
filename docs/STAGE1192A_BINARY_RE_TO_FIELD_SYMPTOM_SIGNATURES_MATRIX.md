<!-- doc-head: Stage 1192A binary RE to field symptom signature matrix over 1188A..1192A, confirmed inferred and refuted bands, label audit, coverage as a measurement -->

# Stage 1192A - Binary RE to Field Symptom Signature Matrix (1188A..1192A)

Static and offline. The matrix binds the binary evidence recovered by 1188A and 1189A and
the absences measured by 1191A to the field symptom vocabulary declared by 1190A. Nothing
was executed, loaded, flashed or contacted.

## Headline

| Measure | Value |
| :--- | ---: |
| Stages covered | 4 of 4 |
| Receipts found | 4 |
| Receipts missing | - |
| Signatures total | 2 |
| Confirmed | 0 |
| Inferred | 2 |
| Refuted | 0 |
| Binary to symptom rows | 2 |
| Symptoms mapped | 2 |
| Coverage measured | 0.0 |
| Gaps listed | 10 |

## The three bands

A row is never confirmed by declaration. It is confirmed only when the symptom's own
descriptor names an anchor and that anchor was physically located in a measured artifact:
a symbol string found in the module bytes, or an offset inside the module length. A row is
inferred when the binding is declared but the anchor is borrowed from elsewhere in the
wave or could not be probed. A row is refuted when a receipt says the binding does not
hold, or when the module it needs is declared and measured absent. A symptom the source
grades UNKNOWN carries no row at all, because a signature is a claim and the source makes
none.

| Module | Symptom | Band | Anchor | Reason |
| :--- | :--- | :--- | :--- | :--- |
| `ubnt_poll_host.ko` | mixed_m5_on_ac_tdma_slot_starvation | inferred | `-` | the binding is declared without an anchor specific to this sympt |
| `ubnt_poll_host.ko` | silent_sta_data_stall_while_associated | inferred | `ieee80211_free_node` | the receipt grades the binding inferred, so the band stays infer |

## Absent binaries and absent versions

| Binary | Declared | Measured tar members |
| :--- | :--- | ---: |
| `eab_driver.ko` | eab_loose=0, eab_present=0, eab_tar_members=0 | 0 |

Absent versions are kept apart from absent modules. `ltu_2_3_1_present = 0` says version
2.3.1 is absent while `ame_core.ko` is present, and reading that zero as a module absence
would refute every real `ame_core.ko` row. The absent version labels are:

`LTU 2.3.1`

## Label audit

| Label | Claim | Verified by a receipt | Image declares |
| :--- | :--- | ---: | :--- |
| OpenWrt 24.10.5 | UNVERIFIED | 0 | 24.10.4 |

The stock tar in `artifacts/verification/stage117a_build/stock.tar` declares its own
release in `/etc/openwrt_release`: 24.10.4 on ath79/generic. That is the only build identity in this
wave that carries a witness. `OpenWrt 24.10.5` carries none, so it stays UNVERIFIED.

## ath10k_core attestation

| Field | Value |
| :--- | :--- |
| Provenance | `tar_member:artifacts/verification/stage117a_build/stock.tar:./lib/modules/6.6.110/ath10k_core.ko` |
| Measured member | `tar_member:artifacts/verification/stage117a_build/stock.tar:./lib/modules/6.6.110/ath10k_core.ko` |
| Bytes | 600808 |
| sha256 prefix | `d7f2d1ac07a6c91f` |
| Copies in the declared archive | 1 |
| Copies in the archive census | 72 (re-measured here: False) |
| eab_driver.ko in the declared archive | 0 |

## Coverage

`coverage_measured = 0.0` over 3 declared symptoms.
Rule: Distinct symptoms with at least one confirmed row divided by the distinct symptoms the wave declares; a symptom that is only inferred or refuted lowers coverage rather than being counted as covered
The matrix does not assert 1.0. A symptom that is only inferred or refuted counts against
coverage instead of being counted as covered, and the gaps name every symptom left
without a confirmed row.

## Gaps

- symptom 'single_cpe_tx_rate_collapse_1x_lockup' names ubnt_poll_host.ko and is graded unclaimed (the receipt grades the symptom UNKNOWN, so no signature is claimed), so no signature is claimed for it
- symptom 'mixed_m5_on_ac_tdma_slot_starvation' names ubnt_poll_host.ko but the wave publishes no physically verifiable anchor for it
- 3 of 3 declared symptoms carry no confirmed binding, so coverage_measured is a measurement and not a target of 1.0
- declared symptom 'single_cpe_tx_rate_collapse_1x_lockup' carries no row at all
- LTU 2.3.1 is declared absent by ltu_2_3_1_present = 0; the matrix carries it as an absent version and not as a module absence, because ame_core.ko itself is present
- A confirmed row means the anchor it cites was found in the measured bytes. That is provenance, not semantics: the matrix does not prove that the instruction at the offset produces the field symptom.
- coverage_measured is a measurement over the symptom vocabulary the wave declares. A wave that declares fewer symptoms can raise coverage without adding evidence, and the gap list is the control for that rather than the number.
- signatures_confirmed, signatures_inferred and signatures_refuted are counted, not targeted. A zero in any of them is reported as measured.
- The label OpenWrt 24.10.5 is recorded as UNVERIFIED. The image in the stock tar declares 24.10.4 in /etc/openwrt_release, and no receipt in this wave witnesses 24.10.5.
- The archive-wide copy census is a labelled input, not a per-run measurement: this run re-measured the declared archive only. A census that opens 75 archives is a separate sweep and its number is carried, not re-derived.

## Reproduce

```
python tools/verify/verify_binary_re_to_field_symptom_signatures_1188a_1192a.py
python -m pytest tests/test_stage1188a_to_1193a_suite.py -q
```

