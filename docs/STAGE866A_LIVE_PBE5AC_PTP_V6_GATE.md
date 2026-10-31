<!-- doc-head: Stage866A incomplete live queue with separate local software validation -->
Passing pytest cannot approve absent firmware, unexecuted benchmarks or a v6 release.
<!-- /doc-head -->

# Stage866A: live acceptance INCOMPLETE

Parent: authorized861..866 bench queue; question: were861..865 physically
executed and independently accepted? Answer: no. Attribution: external controller.

| Stage | Verified scope | Remaining acceptance |
| --- | --- | --- |
|861|Native read-only bench identity; independent PB070 audit|PB070/native Quad-Patch absent|
|862|Three-round acquisition contract and refusal|Zero of12 live windows acquired|
|863|Read-only251 response identifies Rocket2AC|MK1 identity/path and v6 absent|
|864|Panel2/3 passive status, stations and L2 deltas|Delivered goodput and TDMA slots unknown|
|865|Four held v4 image hashes and candidate manifest|No v6 package; both-board runtime unknown|

`python tools/verify/verify_stage866a_live_pbe5ac_ptp_v6_gate.py` returns2.
It records separate receipt/capture integrity, documentation budget checks and
independent review links. Local integrity passing does not change INCOMPLETE.
The code is a fail-closed preparation/audit implementation; a real guarded loader,
native v6 benchmark and releasable v6 firmware are still unimplemented.

Run local disposable-fixture validation:
`python -m pytest -q tests/test_stage861a.py tests/test_stage862a.py tests/test_stage863a.py tests/test_stage864a.py tests/test_stage865a.py tests/test_stage866a.py tests/test_stage861a_to_866a_suite.py`
Exact results and retained first failures belong in
`artifacts/verification/stage861a_to866a_validation.json`.

PC-crash recovery preserves the four NUL-filled862..865 receipts under
`artifacts/verification/stage861a/crash_recovery_20261027/`.
Restored receipts reuse intact timestamped captures, not fresh hardware evidence.
New common JSON writes flush/fsync before atomic replacement.

No radio firmware/configuration/flash write, scan, load benchmark or publication
was executed. No durable background runner is active.
Next: independently implement/validate native PB070 and identify the actual MK1
route; then resume the authorized45-second RAM activation and matched measurements.
