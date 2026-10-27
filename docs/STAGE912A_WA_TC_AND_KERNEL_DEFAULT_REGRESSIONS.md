<!-- doc-head: 912A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# WA tc and kernel-default regression contract

Regression sources exercise tc present, absent tc with fq_codel default, and absent/incorrect defaults.
Additional contracts cover dry-run, exact identity, per-profile native AQL labels, real verify readbacks,
backend persistence, readback drift, mutation failure rollback and failed restoration.
Tests replace every device getter/setter and restrict PATH for the tc-less path.
This receipt pins the test sources; it does not substitute declarations for executed pytest.
Fresh executed counts and exit codes are in Stage916A. Physical acceptance UNKNOWN.
