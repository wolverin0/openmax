<!-- doc-head: Stage263A complete Markdown inventory and active router budget audit -->
Local inventory preserves historical violations and enforces explicit active routers.
<!-- /doc-head -->

# Stage263A: documentation contract

Question: which active router documents violate the compact navigation contract?
Parent: reproducible research and continuity deliverables in BENCH_PLAN.
This is an external controller/local repository audit, with no device operations.

Run `python tools/verify/audit_all_docs_line_budget_and_dochead.py`.
The dedicated receipt is `artifacts/autoresearch/stage263a_docs_budget_audit_receipt.json`.
Every Markdown file recursively under `docs/` is inventoried with SHA256, line count,
opening and closing header positions, errors, and active-router classification.
Active means linked directly from AGENTS.md, plus CURRENT_STATE, the master index,
DECISIONS, RESEARCH_LEDGER and BENCH_PLAN. Missing active files fail the audit.

The budget is strictly fewer than 220 lines. A single opening header must be at
line 1, paired with one closing comment after no more than six summary lines.
Archived and other non-router documents retain visible inventory failures; they
are not silently counted as compliant. The scanner does not rewrite history.
UTF-8 BOM is accepted; malformed encodings and external symlinks fail inspection.

Exit 0 means active routers comply; exit 1 means recorded active violations.
A passing pytest validates detection, not that every historical document is short.
Acceptance stops at this reproducible inventory and qualified result. No RF claim,
live state, scientific five-pillar acceptance or publication follows from it.
