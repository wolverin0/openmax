<!-- doc-head: Stage1094A scoped offline line-budget, paired-header and local-link audit for Stage1001A..1078A docs -->
External URL availability is deliberately not checked in this offline wave.
<!-- /doc-head -->

# Stage1094A document audit

The script filename retains the requested1001A..1090A suffix, but the actual document scope is existing active Stage1001A..1078A Markdown files, including continuation pages. Archive trees are excluded. The receipt reports represented stages and gaps without inventing missing documents.

Every scoped document must have strictly fewer than220 lines and one paired doc-head at the beginning. Inline-code examples mentioning a doc-head are not additional header blocks. Link checks cover inline, image, reference and HTML links; fenced code, inline code and HTML comments are excluded.

Local destinations are resolved inside the repository, including angle-wrapped paths, percent-encoded spaces, parenthesized filenames, fragments and source line fragments. Heading anchors include duplicate-heading suffixes and explicit HTML ids. Missing files, missing anchors, unsupported local fragment types and parse failures fail the audit.

External schemes and network-path references remain `EXTERNAL_NOT_CHECKED_OFFLINE`. Zero broken local links is never presented as proof that external sites are reachable.

The receipt binds the exact document inventory and local target files with SHA256. It brackets the audit with both source and target hashes; the parent gate captures revision-bound test evidence separately. This is capture-time stability, not a promise that other lanes will never update a document. The audit does not rewrite documents or create missing evidence receipts.

Baseline findings are preserved in `artifacts/verification/wave12_stage1093_1094/baseline_doc_audit_corrected_parser.json`: fourteen missing paired-header closings and four links to unavailable Stage1044A..1047A receipts. Required corrections remain the coordinator's ownership; rerun the audit after those changes.

```powershell
python tools/verify/audit_stage1094a_docs_line_budget_and_links_1001a_1090a.py
```

Receipt: `artifacts/autoresearch/stage1094a_docs_line_budget_and_links_1001a_1078a.json`.

Exit0 requires a nonempty scope, no line/header/link violations and stable scoped input hashes. Exit1 preserves actual findings. This wave performs no SSH, network probe, kit execution or hardware operation.
