<!-- doc-head: CG-CJ saved PB probes and available hMAC package integration -->
Five available R135-R139 receipts are frozen; R140-R146 were absent at cutoff.
PB arithmetic is internally consistent under its reported clock, not hardware acceptance.
R135 ACK30 differs from PB class2 ACK36; source declarations remain unchanged.
hMAC/VoIP is a separate regime; five packages remain blocked with explicit gaps.
Historical R1-R134 interfaces and serialized records remain preserved.
Offline external-controller analysis only; E2 remains NOT_ACCEPTED.
<!-- /doc-head -->

# Stage12: saved PB021/031/050 and available R135-R139 hMAC evidence

Parent deliverable: control authority and experimental methodology in the original
[forward plan](../artifacts/2026-09-20-forward-plan.html) and the current BENCH_PLAN.
Question: what do these saved probes and complete packages establish without new acquisition?
The [contract](../artifacts/autoresearch/waves_cg_to_cj_20261024/prespecified_contract.json)
was written before outcome analysis. The original filename inventory incorrectly looked for dated
TSV names; it is preserved. The [corrected inventory](../artifacts/autoresearch/waves_cg_to_cj_20261024/inputs_manifest_v2.json)
adds the five existing undated TSV files without changing the round cutoff or acceptance.
Later receipts are reserved for the later queued task.

## Saved PB probe: reported observation versus qualification

CONFIRMED offline: the seven hex/cycle/microsecond rows agree arithmetically with the
receipt's reported 88 cycles/us, slot=9+3c and ACK/CTS=30+3c. The LDPC words, channel
bank coordinates, capture-bit decoding and three host HTT readback strings are retained.
This verifies the contents and arithmetic of the saved report. It does not independently
verify the installed clock, register semantics, physical acquisition or effective controls.

UNKNOWN: the exact firmware/driver/board hashes, command/output acquisition transcripts
and raw160 clock samples are absent. The seven TSF2 words are identical, so they do not
demonstrate TSF progression, precision or drift. Reported p99 two-register debugfs roundtrip
is2758.85us; reported host/target midpoint absolute jitter p99 is813.82us. These summaries
were not independently recomputed and do not qualify either sub50us TDMA or a reliable
>=1ms hMAC queue-gating cadence. The receipt explicitly reports no associated CPE.

The capture bit is0. Static nonzero channel banks do not establish packet-attributed CSI.
Readable LDPC words and a reported800-cycle value do not establish LDPC switch authority
or decoder latency. HTT strings3/16,3/32,3/64 are host readbacks, not measured aggregation
depth. TPC text does not establish per-peer power authority. Restoration fields report
states0 and3/64; an independent before/after baseline and health postcheck are missing.
Source verdict strings remain attributed claims; all physical/control-qualification flags
remain false. See the [independent source audit](../artifacts/autoresearch/waves_cg_to_cj_20261024/pb_source_audit.json)
and [source-bound machine qualification](../artifacts/autoresearch/waves_cg_to_cj_20261024/pb_receipt_qualification.json).

The historical advisory ACK formula18+6c is distinct from the PB report's30+3c; their equality
atc4 does not permit transfer. Historical metadata is not rewritten. New R135 declares30us
atc2 whereas the saved PB row reports36us; R136-R139 declarations match their reported PB rows.
Neither matching nor differing source values proves the effective timing used in a workload.

## Available hMAC/VoIP corpus and selector

The cumulative view contains370 records,3516 crossed windows (1670 matched pairs)
and16 retained sequential observations. The prior360 records/3356 crossed windows and
historical serializations are preserved. Five new two-arm comparisons contribute10 records,
160 crossed windows and80 matched pairs. R110-R113 remain historical missing measurements;
R140-R146 were absent at this task's fixed cutoff. Programmed distance labels are not physical RF range.

| Round | Declared meters / class | Declared ACK us | Saved PB ACK us | Offline promotion |
| :--- | :--- | ---: | ---: | :--- |
| R135 | 1000 / 2 | 30 | 36.0 | BLOCKED |
| R136 | 3000 / 6 | 48 | 48.0 | BLOCKED |
| R137 | 6000 / 13 | 69 | 69.0 | BLOCKED |
| R138 | 9000 / 20 | 90 | 90.0 | BLOCKED |
| R139 | 12000 / 26 | 108 | 108.0 | BLOCKED |

The new identity is `bidir_8flow_voip_hmac`, eight bidirectional flows with the recorded
0xb8 probe declaration. It is never aliased to ordinary bidirectional8 evidence. Source
packages retain `tx_aggr_factor`, requested`fq_flows`, TID0/TID6 counters and literal timing.
The five target packages request fq_flows1024 whereas their retained readback text reports4096;
these source conflicts remain explicit. The frozen recipes do not retain an explicit ping
`-Q0xb8` command; that absence does not establish effective end-to-end marking either way.
No effective hMAC mechanism is inferred from a label or counters.

All five recorded target means satisfy the descriptive literal<2% total-goodput-loss predicate.
This is neither statistical noninferiority nor experiment acceptance. Generic RTT samples
remain generic: separate voice latency, jitter, loss and MOS are unavailable, and effective
AC mapping/packet attribution is unqualified. An independently accepted statistical receipt
for this exact regime, effective queue-gating authority and the Stage4 boundaries are missing.
Therefore the new selector abstains and the structural gate blocks all five packages.
Existing strict goodput/QoE/source/health/statistics rules and legacy APIs remain unchanged;
no Holm family is reset, no earlier significance is borrowed and no synthetic p-values are supplied.
The control of R138 records159/160 received probes (0.625% loss), despite the zero-loss filename.
Across the ten new arms,1599/1600 attempted RTT probes were received. Those failed observations
remain in the source-bound corpus and are not replaced by a zero-loss label.

See the [diagnostic selector artifact](../artifacts/autoresearch/waves_cg_to_cj_20261024/hmac_package_selector_audit.json)
and [repaired dataset validation](../artifacts/autoresearch/waves_cg_to_cj_20261024/dataset_repair1_validation.json).
New APIs expose authenticated saved inputs and explicit refusals; they never actuate hardware.

The first source revision passed4627 tests. Independent review subsequently reproduced
a parser gap: a declared aggregation factor could contradict the recipe-authenticated
airtime_flags. The failing regression and previous source/test/output/verification bytes
are retained. The minimal guard requires the exact recipe relationship;46 affected tests
pass, and both normalized artifacts and this selector diagnostic remain byte-identical.
A fresh whole-suite receipt for the repaired revision is required for final acceptance;
the earlier green run is not substituted for it.

## Decision and remaining evidence

KEEP the offline ingestion and control-boundary diagnostic. REJECT promotion of saved report
titles/readbacks to silicon authority, CSI, TDMA feasibility, effective hMAC or voice-QoE certification.
The unqualified physical conclusions remain INCONCLUSIVE. The later queued task can process
newly completed R140-R146 receipts under its own freeze; missing measurements are not fabricated.
Physical/control qualification needs exact-build transcripts, raw synchronized samples,
loaded packet/queue/ACK/retry/beacon evidence and verified restoration. No device action is
part of this offline delivery, and E2 remains NOT_ACCEPTED.

Software acceptance is recorded separately in [final validation](../artifacts/autoresearch/waves_cg_to_cj_20261024/final_validation.json),
including fresh scoped pytest and independent reviews. A successful software suite does not
change any physical qualification above. No radios, recipe execution/import, GEM edits,
installation, global configuration, commits, deployment or publication were performed.
