<!-- doc-head: Stage 920A audit of all docs/*.md for the <=180-line budget and a single opening doc-head; reports violations, fixes nothing -->
# Stage 920A — docs/*.md Line-Budget & doc-head Audit

- **Claim Status**: `CONFIRMED` (offline doc audit)
- **Attribution**: `external controller (offline doc audit)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage920a_docs_line_and_dochead_audit.json`
- **Tool**: `tools/verify/build_stage920a_docs_line_and_dochead_audit.py`
- **Evidence class**: `DOC_COMPLIANCE_AUDIT`

## 1. Contract audited
Every `docs/*.md` must satisfy:
- **≤ 180 lines**, and
- a single `<!-- doc-head: ... -->` as the **opening line**.

## 2. Result
- **Docs scanned**: 1134
- **Compliant**: 1134
- **Violations**: 0

The repository's doc corpus is fully within the 180-line budget with exactly one
opening doc-head each.

## 3. Note on a self-induced near-miss (fixed)
`docs/CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md` was pushed to 183 lines by
the Stage 890A classification append; it was compacted back to 174 lines (table
collapsed to prose) before this audit, keeping the "Post-Audit Evidence
Classification" marker the 890A gate checks. No other doc exceeded budget.

## 4. Reproduce & limits
```sh
python tools/verify/build_stage920a_docs_line_and_dochead_audit.py
python -m pytest tests/test_stage917a_to_922a_suite.py -q
```
Read-only audit: it reports violations for the owning author to resolve and does
not rewrite any doc. The count is a point-in-time snapshot; adding or editing docs
afterward requires re-running the audit.
