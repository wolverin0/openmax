<!-- doc-head: 911A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# Native WA tc-optional field-kit source package

Source package only; no radio is contacted or mutated by this builder.
`--qdisc-mode auto|tc|sysfs-default` defaults to auto. Inspection/dry-run performs no getters.
Auto selects tc when installed; tc command/readback failure never silently selects another backend.
Without tc, the kernel default must read exactly fq_codel; otherwise fail before device writes.
Kernel-default mode tunes/readbacks AQL, pktlog, BQL, tx_queue_len1000 and profile sysctls.
It does not set or verify custom qdisc quantum, target or interval and does not prove an existing active root qdisc.
`qdisc_backend=kernel_default_fq_codel`, `qdisc_readback=default_policy_only`, `active_qdisc=UNKNOWN`.
`--verify --identity FILE --state-dir ABSOLUTE` requires a matching successful transaction and performs real reads.
Snapshot profile/backend are fixed across apply, verify, idempotence and rollback; no fallback after drift.
Existing state requires root-owned mode700 directories, mode600 single-link regular files and no phase temporary file.
BusyBox-compatible stat -c metadata support is required; missing tools fail before writes.
All three kits require exact board/revision/driver/firmware/interface identity; old positional v14/v15 calls fail closed.
Native AQL VO/VI/BE/BK and numeric AC rows are normalized; duplicate/incomplete rows are rejected.
Failure restores all changed knobs and verifies restoration; failed restoration is ROLLBACK_FAILED.
Missing board_revision and other historical897A blockers are not bypassed.
Attribution: Linux/mac80211/ath10k configuration; hardware and physical acceptance UNKNOWN.
