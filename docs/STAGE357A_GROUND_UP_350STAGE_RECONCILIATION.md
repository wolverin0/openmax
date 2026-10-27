<!-- doc-head: Stage357A qualified ground-up architecture and held350-stage ledger reconciliation -->
Counts describe held evidence, not completed experiments or hardware acceptance.
<!-- /doc-head -->

# Stage357A

Parent: original control-boundary/RE1 deliverable after353A..356A.
Run `python tools/verify/build_stage357a_ground_up_350stage_reconciliation.py`.
The scan reads only local regular JSON files under artifacts with stage1..350 names.
Symlinks/reparse paths are not followed. Size, count, JSON-depth and reference
budgets bound the scan; malformed/nonfinite/duplicate-key JSON stays invalid.
Missing numbers are retained, not filled with invented receipts.

## Frozen receipt snapshot

| Observation | Count |
| --- | ---: |
| Receipt files | 598 |
| Valid object receipts | 598 |
| Distinct content hashes | 573 |
| Numeric stage IDs present of350 | 320 |
| Filename/declared identity conflicts | 1 |
| Saved comparison fingerprints | 250 |
| Saved comparison locations | 265 |
| New physical results | 0 |

Each receipt retains its hash, location role and unresolved empirical acceptance.
Support snapshots/copies are distinguished by location, not treated as independent
measurements. Identical-content aliases remain visible. Parsed stage/meta IDs are
compared with filename IDs; unknown declaration formats are not guessed. A missing
letter suffix is compatible but underspecified, not a conflicting numeric stage.

The existing five-pillar function is invoked as a STRUCTURAL PRESENCE HEURISTIC.
Its acceptance of a summary/boundary/meta field does not prove binary provenance,
scholar verification, counterbalanced acquisition, inference or durable memory.
Its booleans are retained without promoting them to scientific acceptance.

Saved ABAB arrays reuse Stage266's finite metric/order/quantile normalization and
recompute arm means and changes. These are summary arithmetic, not authenticated
native measurements. Each source location preserves order provenance and exact
array pointers: reported array order, assumed named-phase order, or ABAB
reconstructed from separate A/B arm arrays. Reconstruction is not observed order.
Fingerprints group equal round/family-hint/metric summaries;
genuine equal observations and copied summaries cannot be distinguished here.
No count is called a unique physical experiment; gains are never added or pooled
across radios/topologies. Unresolved filename family hints remain unresolved.
Rejected arrays keep their locations and reasons. No raw device config is emitted.

Recognized repo-relative path/SHA256 references are checked within a256MiB read
budget and32MiB per file. Missing, drifted, unsafe and budget-skipped bindings stay
visible. Hash agreement authenticates current bytes only, not original acquisition.
Receipt hashes are rechecked after the scan to expose concurrent source drift.
This is a reproducible held-file snapshot, not an immutable historical archive.

## Architecture boundaries

| Owner | Established offline | Remaining gap |
| --- | --- | --- |
| Linux/ath9k | Conditional half/quarter timing and PLL source paths | Exact board/runtime support |
| ath10k/QCA firmware | No normal upstream5/10MHz phymode cases | Native capability/control |
| Proprietary WMI | Held0x9044 sender/188-byte copy; descriptor bits | Native ABI and peer acceptance |
| External simulator | Finite seeded retry/hopping fronts | Calibrated RF/vendor protocol |
| Linux/mac80211 | Exact WA kernel/DTB and watchdog byte checks | Installed/armed semantics |
| LTU/hardware | Local kit inventory | Image join, boot, restore, RF |

353A..356A receipts are separately pinned as current architecture context and are
outside the1..350 ledger cutoff. Simulation is not physical acceptance. Manifest
trust anchors are caller-selected, saved watchdog assertions are not fresh device
proof, and no verifier can guarantee zero bricks. Decision: KEEP qualified offline
reconciliation. E2 NOT_ACCEPTED. No live radio, SSH, flash or target execution.
