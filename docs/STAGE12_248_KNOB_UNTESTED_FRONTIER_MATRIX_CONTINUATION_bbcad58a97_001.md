<!-- doc-head: STAGE12_248_KNOB_UNTESTED_FRONTIER_MATRIX.md continuation 1 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE12_248_KNOB_UNTESTED_FRONTIER_MATRIX.md) | Part 1/3
<a id="reproduction-and-validation"></a> [Reproduction and validation](STAGE12_248_KNOB_UNTESTED_FRONTIER_MATRIX_CONTINUATION_bbcad58a97_003.md#reproduction-and-validation)

<!-- stage822a-payload-begin -->

Pinned original248/33-source catalog recovered; no arbitrary first248subset.
Current571 catalog keeps213same rows,34revisions and one superseded UNKNOWN ID.
Eight controls vary inside saved packages; one is recorded without within-round variation.
No isolated effect, exact runtime-build authority or safe range is qualified.
Closed-build, excluded, untested and missing110-113 evidence remain explicit.
Pure offline implementation/test evidence; independent and full-task gates remain separate.


# Original248-control untested frontier against saved R1-R134 evidence

Status: **IMPLEMENTED / pending independent acceptance**. This is a catalog identity and evidence-classification audit, not an experimental win or permission to apply a knob. The current task remains subject to its separate law, independent-review and full-suite requirements. No result for those gates is inferred from this report.

## Exact historical identity

The authoritative original is the retained [248-entry catalog](../artifacts/autoresearch/waves_abcd_20261024/inputs/firmware_knob_candidates.json),760365bytes, SHA256 `b2810269d0a7afb8715ebbeb901e169a2fd0b5cf61c3d667f91d7aae15585c07`. Its248unique IDs/33sources agree with the [original validation](../artifacts/autoresearch/firmware_knob_audit_20261024/validation.json) and [independent closed-firmware integration review](../artifacts/autoresearch/firmware_knob_audit_20261024/review_closed_catalog.md). The historical section4of the master index cites this version; its live catalog link now resolves to the expanded571-entry catalog, so taking the first248current rows would be wrong.

The [current catalog](../orchestration/autoresearch/firmware_knob_candidates.json) has571rows/42sources. Of the original248identities,213rows remain identical,34WA-UPH rows have revised provenance, and one historical ID is absent from the current version. That absent ID is `wa_8_7_25_sys_module_umac_parameters`, the original unresolved WA module-parameter inventory. Its original UNKNOWN entry is retained here; it is not silently replaced by one of the later15concrete WA parameter rows. Current and original row hashes are separate.

All original source references, build scopes, interface selectors and exclusions remain literal. Those historical static provenance references are not claims that the old live pathname still has those bytes. In particular source s015 retains its historical hash in the original catalog; the current catalog resolves that same hash to the protected PB01before-snapshot. This audit does not modify either catalog or any PB01artifact and does not repeat proprietary-module analysis.

## Evidence and classification contract

The [machine matrix](../artifacts/autoresearch/knob_248_untested_matrix_20261024.json) has exactly one row per original ID. Each row retains original interface/build scope and static source/hash locators, its relation to the current catalog, classification, and exact saved round/arm/endpoint/key/value/JSON-pointer/source-SHA evidence where present. Evidence uses130authenticated frozen receipt copies behind the accepted360-record R1-R134 corpus:358primary windows and2auxiliary summaries excluded from control-treatment evidence. R110-R113 have recipes but no measurement JSON/TSV; all four remain UNKNOWN, with no fabricated result.

An explicit mapping table permits only original interface/selector matches. It bridges exact recorded flat, endpoint-prefixed or endpoint-state schema keys and verifies each against the corresponding normalized coordinate. Missing/None fields, including RTS null, are unknown, never invented zero/default writes. Explicit RTS `off` is retained separately as the defined off value. AP/CPE asymmetry is preserved. All3075package-coordinate evidence observations point to saved source bytes and raw keys. Every normalized_coordinates entry is an existing JSON pointer: the HTT pair uses separate htt_max_amsdu and htt_max_ampdu coordinates with an explicit ordered-pair transform. The replay verifies7535raw and3102normalized pointers, including all27HTT pairs; no recipe is imported or executed.

TESTED_AS_DECLARED_PACKAGE means that at least two saved values for that exact control vary within a round and endpoint while measurements of the full package exist. It does **not** prove the running firmware consumed the setting, independently verify a device readback, isolate a control effect, establish safety or transfer one build to another. The constant-value category is weaker still: a coordinate was recorded but not varied within a round. All248rows have zero qualified isolated effects, no treatment authority and no approved safe range.

| Primary category | Controls | Meaning |
| --- | ---: | --- |
| `PROTECTED_OR_EXCLUDED_NO_TREATMENT_AUTHORITY` | 62 | Original safety/unsupported/read-only exclusion remains; absence is not a recommendation to try it. |
| `UNTESTED_EXACT_INTERFACE_IN_SAVED_CORPUS` | 81 | No exact supported-interface match in the authenticated saved measurements. |
| `TESTED_AS_DECLARED_PACKAGE` | 8 | Recorded full-package coordinate varies within a saved round; effect is not isolated. |
| `PACKAGE_VALUE_RECORDED_NO_VARIED_TREATMENT` | 1 | Recorded declaration only; no within-round varied treatment for this coordinate. |
| `INAPPLICABLE_CLOSED_FIRMWARE_BUILD_TO_OPENWRT_CORPUS` | 96 | airOS WA/XC or LTU build scope is not this OpenWrt/CT measurement context. |

Knowledge and authority are separate axes:247original static interfaces are identified but runtime application remains unknown; one original interface is explicitly unresolved. That UNKNOWN inventory also remains excluded, so it is not double-counted as a249thcontrol.

## Controls with exact package-coordinate evidence

| Stable ID | Saved evidence observations | Saved rounds | Within-round variations | Interpretation |
| --- | ---: | ---: | ---: | --- |
| `ct_special_7` | 689 | 130 | 237 | `TESTED_AS_DECLARED_PACKAGE` |
| `ct_special_10` | 20 | 3 | 2 | `TESTED_AS_DECLARED_PACKAGE` |
| `ct_special_12` | 7 | 1 | 1 | `TESTED_AS_DECLARED_PACKAGE` |
| `aql_txq_limit` | 689 | 130 | 256 | `TESTED_AS_DECLARED_PACKAGE` |
| `aql_threshold` | 689 | 130 | 256 | `TESTED_AS_DECLARED_PACKAGE` |
| `fq_quantum` | 689 | 130 | 133 | `TESTED_AS_DECLARED_PACKAGE` |
| `htt_aggr_size` | 27 | 4 | 1 | `TESTED_AS_DECLARED_PACKAGE` |
| `rts_threshold` | 97 | 17 | 14 | `TESTED_AS_DECLARED_PACKAGE` |
| `coverage_class` | 168 | 81 | 0 | `PACKAGE_VALUE_RECORDED_NO_VARIED_TREATMENT` |

The eight varied controls are CT-special7/10/12, AQL per-AC limits, AQL threshold, fq_quantum, the HTT AMSDU/AMPDU pair and supported iw RTS. Coverage class is recorded across declared contexts but does not vary between arms within a round in these retained sources. It is therefore classified as a recorded package coordinate, not as an isolated distance/coverage experiment. Declared coverage/timing is not verified physical separation or a silicon maximum.

## Non-aliases and qualified negatives

- WMI parameter descriptors and airOS WEXT/UPH nodes are not tested merely because a saved policy has a similar retry, aggregation, rate or fairness name. A WMI retry selector is not automatically the short/long retry interface.
- Original `codel_target`/`codel_interval` are Linux-qdisc policy-metadata interfaces. Later `fq_target_us`/`fq_interval_us` mac80211 package fields are not automatically the same controls. These original IDs remain untested by exact-interface evidence; no conversion by label is made.
- XC/WAairOS8.7.25 and LTU2.4.2 static build tables do not become OpenWrt-tested controls because a radio shares a hardware family. LTU2.4.0historical results do not qualify2.4.2.
- R116-R121UL2 treatments cochange full AQL/CoDel/TSQ/rate packages. R122-R134UL8hammer treatments include RTS/ACK-clocking/VO and other package differences. Their recorded coordinates are not isolated logarithmic laws, RTS effects, pureVO causal improvements or universally qualified distance curves.
- The current advice policy class31 is not a proven hardware ceiling. All physical range, exact applied firmware state, causal/noninferiority and sector acceptance remain outside this saved-source frontier.

## Complete248-row matrix

P=protected/excluded; U=untested exact interface; X=closed-build inapplicable; T=declared package varied; C=recorded constant coordinate. JSON contains full interface/selector, build, original/current hashes, source locators and all evidence values.

<!-- stage822a-payload-end -->
