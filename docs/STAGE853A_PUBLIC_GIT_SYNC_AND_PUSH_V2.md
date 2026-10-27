<!-- doc-head: 853A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# Public Git sync and push v2

Prepared release; default execution audits the index and updates the two public reading routes.
Publication command: `python tools/verify/verify_stage853a_public_git_sync_and_push_v2.py --publish`.
Only the explicit849A..854A source/doc/test/receipt selection is staged.
Unrelated local edits are preserved; no broad git add is used.
The actual index is rescanned for restricted paths, binary dumps and sensitive content before commit.
Repository five-pillar gate and release854A receipt are mandatory.
Known baseline identifiers are redacted in public derivatives; private originals remain local.
Derivative source bindings require those originals and are not recertified as original evidence.
The push result and exact remote hash are stored in local Git metadata after publication.
This committed preparation record never certifies its own future push.
No history rewrite and no physical operation. Physical acceptance: UNKNOWN.
