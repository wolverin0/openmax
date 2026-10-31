<!-- doc-head: Stage 1149A read-only git staging manifest for Stages 995A..1150A: classification by path, clutter and credential scan (path names only), manifest_status CLEAN/CLUTTER_PRESENT/CREDENTIAL_PRESENT -->
# Stage 1149A - Git staging manifest 995A..1150A

Tool: `tools/verify/verify_git_staging_manifest_995a_to_1150a.py`.
Receipt: `artifacts/verification/stage1149a_git_staging_manifest_995a_to_1150a.json`, claim `FMX-STAGE1149A-GIT-STAGING-MANIFEST`, evidence class `GIT_STAGING_MANIFEST`.

## Behaviour

- Read-only: only runs `git status --porcelain -uall`. Never runs `git add`, `commit` or `push`.
- Scope: changed paths whose name carries a stage number 995..1150. Clutter and credential scan covers ALL changed paths.
- Classes: `receipt`, `tool`, `doc`, `test`, `firmware_kit`, `other`.
- Reports `staged_count`, `by_class`, `manifest` (sorted, capped at 400), `clutter_findings`, `credential_findings`.

## Scan

- Credentials: `.env`, key/cert extensions, names like secret, token, password, private key. Path and classification only; no content is read or printed.
- Clutter: `*.log`, `*.bak`, `*.orig`, `*~`, `Thumbs.db`, `.DS_Store`, scratch dirs.

## Status

`manifest_status` is `CREDENTIAL_PRESENT`, `CLUTTER_PRESENT` or `CLEAN`. Receipt `status` is CONFIRMED iff `credential_findings == 0`; clutter is a reported warning.
