<!-- doc-head: Stage525A saved PBE VHT40 and separate WA pktlog reconciliation -->
Saved arithmetic and producer semantics, never new radio acquisition or pooled gains.
<!-- /doc-head -->

# Stage525A

Parent: fixed525A..530A offline RE1/control-boundary queue in BENCH_PLAN.
Run `python tools/autoresearch/build_stage525a_pbe5ac_vht40_25mbps_and_pktlog_zero_reconciler.py`.
Input JSON, producer source and source docs are SHA256-bound and rechecked.
Producer scripts are read as text, never imported or executed.
Their current hashes do not establish the historically executed source revision.

## Separate result contracts

| Held source | Reproduced values | Qualification |
| --- | --- | --- |
|487 .241/.242 champion |16.74DL+8.09UL=24.83Mbps |Sequential interface rates, not concurrent TCP aggregate |
|487 different profile |10.81DL+9.96UL=20.77Mbps |PeakUL9.96 is not championUL8.09 |
|403 R45 .20/.250 |55.816 to71.252Mbps,+27.65515% |max(app sum,OTA), not one pure goodput layer |
|403 R45 p50 |17.633 to19.0515ms |Regression survives the goodput improvement |

487's nss=1 is the producer AP override index, intended2SS; STA command uses nss=0.
No native NSS readback is retained. PHY rates are reported values, not measured
per-frame MCS/NSS distributions. The VHT80 verification flag is an unconditional
True literal. VHT40_ASSOC comes from a ping marker, not an iw width getter or WPA
handshake transcript. The20MHz reference row is hardcoded historical input.
The source's22.80Mbps/3.60Mbps airOS comparison appears only in prose, without a
native matched baseline. No8.9% cross-width acceptance follows from these records.

Champion1472-byte ping reports8 replies and0.0% loss. This is not a persistent
zero-loss guarantee or path/OTA proof. Under the explicit additional assumption of
eight independent transmitted trials with zero failures, the one-sided95% loss
upper bound is about31.23%; the transmitted count and IID assumptions are unproven.
With8 samples the producer's p95 calculation selects the maximum. Raw replies,
management-vs-OTA routing, clock/byte counters and native command exits are absent.

R45 preserves orderedA1,B1,A2,B2 summary windows. Their metric is the maximum of
an application TCP+IPTV+VoIP sum and an OTA byte rate. Both component layers are
recomputed separately. Its generic knob_readback field serializes configured
values only; the actual AP/CPE extra getter strings are dropped by the helper.
A1=36.393 versusA2=75.239Mbps and opposite paired effect directions limit causal
confidence. Per-window RTT quantile means are not pooled quantiles; p95=p99 in all
four windows. Neither the claimed16-stream count nor a CE DMA relief mechanism
is independently established by these summaries. No gains are added/multiplied
onto24.83Mbps. R45 windows use tcp_streams4, but the promoted dictionary records2;
choosing a winner dict is not proof it was applied or persisted after the trial.
Decision: KEEP qualified saved reconciliation; E2 NOT_ACCEPTED.
No target, SSH, configuration, firmware/module execution, flash or load action.
