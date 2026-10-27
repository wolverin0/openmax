<!-- doc-head: 987A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# Private Git status audit and reversible orphan quarantine

Git status, index, untracked and ignored inventories are retained in local Git metadata.
The public record contains aggregate counts and private inventory hashes only.
Default execution audits only; --quarantine authorizes reversible moves of proven ignored report temporaries.
Eligibility requires a generated stage JSON temporary name, age of at least24h, single-link regular file,
bounded size, exclusive reader, recognizable summary content and a complete negative reference scan.
A newer completed summary must already exist; orphan proof and references are rechecked before each move.
Raw captures, firmware, images, backups, tracked files and nonignored user work are never candidates.
Every move is revalidated, hash checked and journaled; a failed batch attempts reverse-order restoration.
There is no delete, reset, clean, stash, Git index mutation, network or device operation.
Proven orphans: 0; quarantined: 0; state: NO_PROVEN_ORPHANS.
Zero proven orphans is an explicit no-op, not a claim that unrelated work was removed.
Private inventory bindings cannot be replayed from the public checkout.
Physical acceptance: UNKNOWN.
