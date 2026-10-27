<!-- doc-head: Offline statistical and causal audit of frozen autoresearch receipts -->
Thirteen sequential treatment windows on one link do not establish isolated causal effects.
Receiver windows and ping subsamples stay separate; sparse tail quantiles remain uncertain.
Prospective power is sensitivity planning, never observed power or permission for bench execution.
<!-- /doc-head -->

# Stage12 — statistical and causal audit

The exact frozen R1/R2 receipts govern this retrospective analysis. R1 has8 windows and R2 has5; each has2 receiver repetitions and6 RTT samples. No source is re-acquired and no device is contacted. All contrasts are exploratory, after viewing the summaries; nothing here is preregistration or physical acceptance.

## Receiver summaries

| Round / window | n | Mean Mbps | SD | Conditional95% t interval | p95 / p99 ms (6 samples) |
| --- | --- | --- | --- | --- | --- |
|R1 / `iter0_baseline`|2|75.500|1.838|[58.982, 92.018]|39.449 / 41.482|
|R1 / `iter1_aql_2000_4000`|2|75.000|0.283|[72.459, 77.541]|17.198 / 17.675|
|R1 / `iter2_aql_1000_2000`|2|69.900|3.111|[41.946, 97.854]|12.072 / 12.265|
|R1 / `iter3_fq_quantum_1514`|2|70.200|1.273|[58.764, 81.636]|13.927 / 15.269|
|R1 / `iter4_htt_ampdu_3_32`|2|56.900|15.556|[-82.868, 196.668]|15.518 / 15.961|
|R1 / `iter5_htt_ampdu_2_48`|2|37.350|1.909|[20.197, 54.503]|18.383 / 19.397|
|R1 / `iter6_ct_rc_per_28`|2|66.150|11.384|[-36.135, 168.435]|9.588 / 9.727|
|R1 / `iter7_ct_rifs_1`|2|71.050|0.071|[70.415, 71.685]|11.277 / 11.411|
|R2 / `r2_iter0_stock`|2|110.000|0.000|[110.000, 110.000]|33.942 / 35.394|
|R2 / `r2_iter1_aql2000_rc28_rifs0`|2|110.000|1.414|[97.294, 122.706]|14.444 / 14.706|
|R2 / `r2_iter2_aql2000_rc28_rifs1`|2|110.000|0.000|[110.000, 110.000]|18.616 / 20.376|
|R2 / `r2_iter3_aql1500_rc28_rifs1`|2|106.500|0.707|[100.147, 112.853]|19.584 / 19.893|
|R2 / `r2_iter4_aql1500_rc35_rifs1`|2|106.500|0.707|[100.147, 112.853]|19.129 / 19.179|

These intervals assume iid normal receiver windows; n2 cannot diagnose those assumptions. They are conditional descriptive uncertainty, not a sector/population or causal confidence interval. Zero SD is retained, never used to certify stability. Ping subsamples do not increase the number of randomized experimental units.

## Exploratory contrasts and multiplicity

Candidate minus within-round first control, unpaired Welch mean contrasts under the stated assumptions. Holm adjusts the complete11-contrast family, retaining missing tests in its size. Intervals below are marginal95%, not simultaneous family intervals; corrected p-values do not remove confounding or adaptive winner bias.

| Candidate | Delta Mbps | Conditional95% interval | Raw p | Holm p |
| --- | --- | --- | --- | --- |
|`iter1_aql_2000_4000`|-0.500|[-15.530, 14.530]|0.766475|1|
|`iter2_aql_1000_2000`|-5.600|[-19.450, 8.250]|0.18858|1|
|`iter3_fq_quantum_1514`|-5.300|[-12.978, 2.378]|0.092073|0.903345|
|`iter4_htt_ampdu_3_32`|-18.600|[-150.619, 113.419]|0.336924|1|
|`iter5_htt_ampdu_2_48`|-38.150|[-46.225, -30.075]|0.0024209|0.0266299|
|`iter6_ct_rc_per_28`|-9.350|[-101.584, 82.884]|0.44917|1|
|`iter7_ct_rifs_1`|-4.450|[-20.865, 11.965]|0.180485|1|
|`r2_iter1_aql2000_rc28_rifs0`|0.000|[-12.706, 12.706]|1|1|
|`r2_iter2_aql2000_rc28_rifs1`|0.000|UNESTIMABLE|NA|NA|
|`r2_iter3_aql1500_rc28_rifs1`|-3.500|[-9.853, 2.853]|0.0903345|0.903345|
|`r2_iter4_aql1500_rc35_rifs1`|-3.500|[-9.853, 2.853]|0.0903345|0.903345|

## Identification, tails and transfer

The engineering design matrix has rank9 for10 columns. Its only constant column is the intercept; additional unmeasured controls lie outside this matrix. AQL low/high/threshold are coupled, RC/RIFS follow adaptive chronology, and randomization/block/pair identities are absent. No isolated AQL, RC, DynamicBW, TXOP or vendor causal effect is identified.

With6 iid RTTs, P(max exceeds the true p99)= 0.0585. At least299 iid samples are needed for the maximum to upper-bound p99 with95% one-sided coverage (59 for p95). Those are ping samples, not independent experimental runs; correlation makes the information gap larger.

Same-policy cross-round goodput differences (uncontrolled context, not treatment effects):
- `[5000, 12000, 24000, 50, 0, 300, 3, 64]`: R175.500 vs R2110.000 Mbps; delta34.500.

The helper uses TCP retransmits/500 as retry_rate and fixes Jain1.0 for a single link; neither is measured MAC PER or PtMP fairness. CT help/shadow getters and boolean restoration flags do not independently prove target effect or exact rollback. Simulated multivendor results are extrapolations with explicit assumptions; Monte Carlo intervals cannot validate transport.

## Prospective power sensitivity

Illustrative standardized effects0.2/0.5/0.8 are a sensitivity grid, not observed effects, expected gains or an operator-approved SESOI. Two-sided noncentral-t planning assumes normal independent differences (paired) or equal-variance independent arms. Three-endpoint planning uses Bonferroni alpha/3;10% unusable units are allowed. Paired n counts independent randomized AB pairs; independent n is PER ARM. Repeated pings or16 simulated CPEs are not these units. No observed/post-hoc power was computed.

Paired effect is d_z = mean AB difference / SD of paired differences; independent effect is d = mean arm difference / common within-arm SD. Equal numeric d values do not assert equal raw effects or variance models. Dropout applies to whole AB pairs or to windows within EACH independent arm, respectively.

| Design | Assumed effect | Family | Analyzed n | Enroll n | Planned power |
| --- | --- | --- | --- | --- | --- |
|paired|0.2|1|199|222|0.8017|
|paired|0.5|1|34|38|0.8078|
|paired|0.8|1|15|17|0.8213|
|paired|0.2|3|265|295|0.8007|
|paired|0.5|3|45|50|0.8024|
|paired|0.8|3|20|23|0.8184|
|independent|0.2|1|394|438|0.8006|
|independent|0.5|1|64|72|0.8015|
|independent|0.8|1|26|29|0.8075|
|independent|0.2|3|525|584|0.8001|
|independent|0.5|3|86|96|0.8043|
|independent|0.8|3|35|39|0.8111|

## Source contradictions and next evidence

- Frozen master says R1baseline102 Mbps/RC75; raw receipt75.5 Mbps/RC50
- Frozen master lists7 R2treatments; raw receipt5
- Frozen master R2baseline106 Mbps; raw receipt110.0 Mbps
- Former CT6 Dynamic BW RTS, CT5 GreenAP and CT3/4 coverage aliases contradicted by retained source; corrected in current index

Prospective blocked randomized AB windows with concurrent control/reversal, true pairing IDs, full RTT traces, independently verified effective state/rollback and independent link/sector replication. No execution authorized.

## Reproduction and methods

Run `python -B -m analysis.statistics.fmx_autoresearch_statistical_audit` from the repository root. JSON output preserves descriptive contrasts, design diagnostics, power inputs, source SHA256 and limitations. Numerical tests compare known power results, rounding and monotonicity; this does not prove experimental assumptions. Dependencies use the installed local NumPy/SciPy versions; no package/network installation is performed.

Methods follow local experimental-design, hypothesis-generation, statistical-analysis, statistical-power, pymoo, SimPy and aeon skills. Aeon time-series fitting is deliberately not applied to six unordered/weakly timestamped pings: absent traces and group/time holdouts prevent defensible classification/forecasting. It was read and informs the non-leakage/data-boundary checks, without adding an unsupported classifier.

Reference declared by the local skills (bibliographic metadata not rechecked online in this offline task): Kassis T., Agarwal V., He Y., Patel D., Brueckner A.M. (2026), Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents, DOI10.48550/arXiv.2609.00065. Design/power methods are explicitly stated above; skill use is not scientific acceptance.
