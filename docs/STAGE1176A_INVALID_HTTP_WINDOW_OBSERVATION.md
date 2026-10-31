<!-- doc-head: Stage1176A preserves one invalid HTTP coverage observation without baseline certification -->
<!-- /doc-head -->

# Stage1176A: invalid HTTP coverage observation

Attempted physical windows: **1**. Valid windows: **0**. No measurement retry.

The first A/A-labelled Arm A window is **INVALID_HTTP_LOAD_COVERAGE**. Both HTTP loops exited zero and completed three/two 4 MiB requests. One DL0 coverage point observed its published HTTP child absent while its wrapper PID/startticks remained stable. A later sample observed a new live child and progress.

The source-bound raw ICMP counts are **10 transmitted / 10 received**, with **0% loss** and nearest-rank p95/p99 **50.874 ms**. These are facts from an invalid workload window, not a certified baseline or favorable comparison.

The receiver interface counter increased **16,262,206 bytes** over **5.48 s**. Interface bytes include protocol/background traffic and do not establish application goodput.

A real inter-request gap and a stale child-publication observer are both possible. Their exact timing and cause remain **UNKNOWN**; this observation does not establish an Arm A radio failure.

Exact per-probe timestamps are **UNKNOWN**: only sequence numbers, configured one-second spacing and the enclosing native uptime interval were captured.

Owned traffic quiescence, both emergency getter-verified restores, final entry-composite-B restoration and independent OTA health were captured. Both endpoint claims were released; no discovery or holdout ran.

Raw observation: [stage1176a-58f7e349439346e7adad7fe8fe526d87.json](../artifacts/verification/stage1176a/stage1175-59f9d3ae7b2544f186b8a39e39bdae43/raw/stage1176a-58f7e349439346e7adad7fe8fe526d87.json).

Bound summary: [invalid_http_window_observation.json](../artifacts/verification/stage1176a/stage1175-59f9d3ae7b2544f186b8a39e39bdae43/invalid_http_window_observation.json). The unchanged statistical and measurement gates remain blocking.
