<!-- doc-head: Stage958A native-evidence replay; real multiflow, blocked WA transactions and passive production limits stay distinct -->
<!-- /doc-head -->

# Stage958A — Live multiflow and Guarida gate

This is a **local verification gate**, not a new hardware acquisition or deployment.
It never opens SSH, creates traffic, writes radio settings or contacts device nodes.
The JSON result distinguishes local integrity from physical acceptance.

## Required evidence

| Stage | Gate checks |
| --- | --- |
| 953A | Actual native TCP receiver and two paced UDP flows, timing/RTT/loss, frozen gate objective, negative control, independent discovery/holdout |
| 954A | Exact RAM kit hashes; eight actual mode invocations; native pre/post AQL/AQM/sysctl identity; literal exit codes |
| 955A | Manifest-bound AP/CPE MACs and addresses; native association admission; preserved transport failures and fresh CPE reads |
| 956A | LTU-Lite native board/CPU/IRQ/network telemetry; no proprietary device-node access |
| 957A | Actual passive-input replay through Flent missing-workload guards; separate local numeric fixtures |

Native SHA/size bindings, target/user/command identities and parser recomputation are
checked independently of receipt success booleans. Missing source-binding coverage
fails closed. Local pytest validation must bind the exact suite/gate sources, command,
JUnit XML and log; a bare `passed` counter is insufficient.

## Physical boundaries

The objective is `LATENCY_WITH_CAPACITY_NONINFERIORITY`; a passing Python test cannot
substitute for real receiver evidence. HTTP is not a UDP instrument. Sender totals
are not application receiver service. AQL limits are per access category, not per TID.
An already-native tcp_notsent_lowat value is not a treatment contrast.

AA, discovery and holdout require their own actual acquisitions, source/plan hashes,
disjoint identities/times and an independent replication receipt where required.
Rejected or inconclusive gate results remain unchanged. Missing samples are not zero
latency, and a paired-block counter does not prove permutation inference was reached.
The prior239/240 control and failed45s autonomous restoration remain failed evidence.

The WA v14/v15 native commands currently reject before profile setters because `stat`
is absent. The gate verifies that rejection and unchanged readbacks; it does not call
it successful apply/verify/rollback. mac80211 iTXQ AQM is not an active root-qdisc dump.

Guarida and LTU reads are passive. Their counter deltas cannot establish application
goodput, controlled AA calibration, zero false positives or a physical Flent workload.
Flent must reject those incomplete workload schemas. Its local fixtures are not live
RF measurements. Official HTTPS package hashes are not a signature-verification claim.

## Reproduction

```text
python -m pytest -q tests/test_stage953a_to_958a_suite.py
python tools/verify/verify_stage958a_live_multiflow_and_guarida_gate.py --validation artifacts/verification/stage958a/validation.json
```

The gate writes the consolidated receipt `artifacts/autoresearch/stage958a_live_multiflow_and_guarida_gate.json`.
Exit2 / `INCOMPLETE` is expected whenever mandatory physical evidence is missing;
all local checks can pass while physical acceptance remains `NOT_ACCEPTED`.
No result authorizes firmware publication, radio deployment or a universal capacity claim.
