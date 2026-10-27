"""Retrospective descriptive/causal audit and prospective power sensitivity.

No observed-power calculation, causal promotion, hardware contact or bench import.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import math
from pathlib import Path

import numpy as np
from scipy import stats

from orchestration.autoresearch.fmx_offline_data import (
    ARTIFACTS, ROOT, descriptive_dataset, finite_number, load_measurements, software_versions, write_json,
)


def describe(values, confidence=0.95):
    values=np.array([finite_number(value,'sample') for value in values],dtype=float)
    if values.ndim!=1 or len(values)<2:
        raise ValueError('At least two finite scalar repetitions required')
    finite_number(confidence,'confidence',0.01,0.999)
    mean=float(values.mean())
    sd=float(values.std(ddof=1))
    margin=float(stats.t.ppf((1+confidence)/2,len(values)-1)*sd/np.sqrt(len(values)))
    return dict(n=len(values),mean=mean,sd=sd,median=float(np.median(values)),minimum=float(values.min()),maximum=float(values.max()),
                conditional_t_interval=[mean-margin,mean+margin],confidence=confidence,
                assumptions='Within-treatment receiver windows treated as iid normal for this descriptive interval; unverified with n2. No sector/population causal interval.')


def welch_contrast(candidate, control, alpha=0.05):
    finite_number(alpha,'alpha',0.000001,0.5)
    a,b=describe(candidate),describe(control)
    va,vb=a['sd']**2/a['n'],b['sd']**2/b['n']
    delta=a['mean']-b['mean']
    if va+vb==0:
        return dict(delta_mbps=delta,p_value=None,t_stat=None,df=None,conditional_interval=None,
                    reason='Both sample variances zero: sampling uncertainty not estimable; no automatic significance claim')
    se=math.sqrt(va+vb)
    df=(va+vb)**2/(va**2/(a['n']-1)+vb**2/(b['n']-1))
    t_stat=delta/se
    margin=float(stats.t.ppf(1-alpha/2,df)*se)
    return dict(delta_mbps=delta,t_stat=t_stat,df=df,p_value=float(2*stats.t.sf(abs(t_stat),df)),
                conditional_interval=[delta-margin,delta+margin],alpha=alpha,
                interpretation='Exploratory unpaired mean contrast; iid/normal windows assumed, sequential/adaptive treatment confounding unresolved')


def holm_adjust(p_values):
    """Preserve missing tests in the family size; never reinterpret missing as p0."""
    for p in p_values:
        if p is not None:finite_number(p,'p value',0,1)
    m=len(p_values)
    ordered=sorted((p,i) for i,p in enumerate(p_values) if p is not None)
    adjusted=[None]*m
    previous=0.0
    for rank,(p,index) in enumerate(ordered):
        previous=max(previous,min(1.0,(m-rank)*p))
        adjusted[index]=previous
    return adjusted


def tail_sample_requirement(quantile=0.99,coverage=0.95):
    finite_number(quantile,'quantile',0.001,0.999999)
    finite_number(coverage,'coverage',0.001,0.999999)
    return math.ceil(math.log1p(-coverage)/math.log(quantile))


def planning_power(n,effect_d,alpha=0.05,design='paired'):
    if type(n) is not int or not 2<=n<=100000:
        raise ValueError('2..100000 independent analysis units required')
    finite_number(effect_d,'prospective standardized effect',0.0001,10)
    finite_number(alpha,'alpha',0.000001,0.5)
    if design=='paired':
        df=n-1
        noncentral=effect_d*math.sqrt(n)
    elif design=='independent':
        df=2*n-2
        noncentral=effect_d*math.sqrt(n/2)
    else:
        raise ValueError('Unknown planned design')
    critical=stats.t.ppf(1-alpha/2,df)
    # Symmetry avoids SciPy1.17.1 negative-tail CDF NaNs at large df/ncp.
    # Reject other numerical failures rather than treating NaN as insufficient power.
    value=float(stats.nct.sf(critical,df,noncentral)+stats.nct.sf(critical,df,-noncentral))
    if not math.isfinite(value):
        raise ValueError('Noncentral-t solver produced non-finite planning power')
    return min(1.0,max(0.0,value))


def required_sample_size(effect_d,target_power=0.8,alpha=0.05,family_size=1,dropout=0.0,design='paired'):
    finite_number(alpha,'alpha',0.000001,0.5)
    finite_number(target_power,'target power',0.01,0.999)
    finite_number(dropout,'dropout',0,0.9)
    if type(family_size) is not int or not 1<=family_size<=1000:
        raise ValueError('Bounded positive multiplicity family required')
    corrected_alpha=alpha/family_size
    if planning_power(100000,effect_d,corrected_alpha,design)<target_power:
        raise ValueError('Power target not attained within sample-size cap')
    low,high=2,100000
    while low<high:
        mid=(low+high)//2
        if planning_power(mid,effect_d,corrected_alpha,design)>=target_power:high=mid
        else:low=mid+1
    return dict(design=design,standardized_effect=effect_d,target_power=target_power,alpha=alpha,
                family_size=family_size,bonferroni_alpha=corrected_alpha,analyzed_units=low,
                enrolled_units=math.ceil(low/(1-dropout)),dropout=dropout,
                achieved_planning_power=planning_power(low,effect_d,corrected_alpha,design),
                units='independent randomized AB pairs' if design=='paired' else 'independent windows PER arm',
                effect_definition='d_z: mean AB difference / SD of paired differences' if design=='paired' else 'd: mean arm difference / common within-arm SD',
                dropout_unit='whole AB pairs' if design=='paired' else 'windows within EACH arm',
                effect_basis='Illustrative standardized sensitivity assumption, not observed effect or an operator-approved SESOI')


def build_audit():
    records,provenance=load_measurements()
    descriptive=[]
    for row in records:
        descriptive.append(dict(round=row.round_id,iteration=row.iteration,receiver=describe(row.goodputs_mbps),
                                rtt_count=len(row.rtts_ms),recorded_p95_ms=row.p95_ms,recorded_p99_ms=row.p99_ms,
                                probability_max_exceeds_true_p99_under_iid=1-0.99**len(row.rtts_ms),flags=list(row.flags)))
    contrasts=[]
    for round_id in ('R1','R2'):
        group=[row for row in records if row.round_id==round_id]
        control=group[0]
        for candidate in group[1:]:
            contrasts.append(dict(round=round_id,control=control.iteration,candidate=candidate.iteration,
                                  **welch_contrast(candidate.goodputs_mbps,control.goodputs_mbps)))
    corrected=holm_adjust([row['p_value'] for row in contrasts])
    for row,p in zip(contrasts,corrected):
        row['holm_p_value']=p
        row['family_size']=len(contrasts)
        row['causal_conclusion']='NOT_IDENTIFIED'
    policy_changes=[]
    for key in sorted({row.policy_key for row in records}):
        a=[row for row in records if row.policy_key==key and row.round_id=='R1']
        b=[row for row in records if row.policy_key==key and row.round_id=='R2']
        if a and b:
            policy_changes.append(dict(knobs=list(key),R1=a[0].goodput_mbps,R2=b[0].goodput_mbps,
                                       difference_mbps=b[0].goodput_mbps-a[0].goodput_mbps,
                                       interpretation='Same reported policy, different round/context; uncontrolled drift or measurement context unresolved'))
    matrix=np.array([[1,*row.knobs,1 if row.round_id=='R2' else 0] for row in records],dtype=float)
    varying=np.ptp(matrix,axis=0)>0
    scaled=matrix.copy()
    scaled[:,varying]=(matrix[:,varying]-matrix[:,varying].mean(axis=0))/np.std(matrix[:,varying],axis=0)
    power=[required_sample_size(d,family_size=family,dropout=0.1,design=design)
           for design in ('paired','independent') for family in (1,3) for d in (0.2,0.5,0.8)]
    return dict(schema_version=1,status='RETROSPECTIVE_EXPLORATORY_AUDIT',sources=provenance,
                software_versions=software_versions(),
                automatic_execution_allowed=False,causal_effects_identified=False,independent_links=1,
                treatment_windows=len(records),descriptives=descriptive,contrasts=contrasts,
                same_policy_cross_round_changes=policy_changes,
                design_diagnostics=dict(columns=matrix.shape[1],rank=int(np.linalg.matrix_rank(scaled)),
                                        constant_columns=np.where(~varying)[0].tolist(),
                                        warning='Coupled AQL fields, unmeasured controls outside the matrix, adaptive chronology and changing context prevent isolated factor causal attribution'),
                tail_resolution=dict(iid_samples_for_p95_one_sided95=tail_sample_requirement(0.95,0.95),
                                     iid_samples_for_p99_one_sided95=tail_sample_requirement(0.99,0.95),
                                     warning='Order-statistic planning only, not independent randomized experimental units; serial correlation reduces information'),
                prospective_power_sensitivity=power,
                causal_rivals=['Time/round/environment drift','AQL low/high/threshold changed together','Adaptive selection and winner bias',
                               'TCP retransmission proxy is not MAC PER','CT setter errors/readback and restoration gaps',
                               'Sparse/correlated pings and absent block pairing IDs','Single-link-to-multivendor/PtMP transport untested'],
                index_discrepancies=['Frozen master says R1baseline102 Mbps/RC75; raw receipt75.5 Mbps/RC50',
                                     'Frozen master lists7 R2treatments; raw receipt5',
                                     'Frozen master R2baseline106 Mbps; raw receipt110.0 Mbps',
                                     'Former CT6 Dynamic BW RTS, CT5 GreenAP and CT3/4 coverage aliases contradicted by retained source; corrected in current index'],
                future_design='Prospective blocked randomized AB windows with concurrent control/reversal, true pairing IDs, full RTT traces, independently verified effective state/rollback and independent link/sector replication. No execution authorized.',
                observed_power_computed=False)


def render_report(audit):
    lines=['<!-- doc-head: Offline statistical and causal audit of frozen autoresearch receipts -->',
           'Thirteen sequential treatment windows on one link do not establish isolated causal effects.',
           'Receiver windows and ping subsamples stay separate; sparse tail quantiles remain uncertain.',
           'Prospective power is sensitivity planning, never observed power or permission for bench execution.',
           '<!-- /doc-head -->','', '# Stage12 — statistical and causal audit','',
           'The exact frozen R1/R2 receipts govern this retrospective analysis. R1 has8 windows and R2 has5; each has2 receiver repetitions and6 RTT samples. No source is re-acquired and no device is contacted. All contrasts are exploratory, after viewing the summaries; nothing here is preregistration or physical acceptance.','',
           '## Receiver summaries','', '| Round / window | n | Mean Mbps | SD | Conditional95% t interval | p95 / p99 ms (6 samples) |', '| --- | --- | --- | --- | --- | --- |']
    for row in audit['descriptives']:
        d=row['receiver'];lo,hi=d['conditional_t_interval']
        lines.append(f"|{row['round']} / `{row['iteration']}`|{d['n']}|{d['mean']:.3f}|{d['sd']:.3f}|[{lo:.3f}, {hi:.3f}]|{row['recorded_p95_ms']:.3f} / {row['recorded_p99_ms']:.3f}|")
    lines += ['', 'These intervals assume iid normal receiver windows; n2 cannot diagnose those assumptions. They are conditional descriptive uncertainty, not a sector/population or causal confidence interval. Zero SD is retained, never used to certify stability. Ping subsamples do not increase the number of randomized experimental units.','',
              '## Exploratory contrasts and multiplicity','',
              'Candidate minus within-round first control, unpaired Welch mean contrasts under the stated assumptions. Holm adjusts the complete11-contrast family, retaining missing tests in its size. Intervals below are marginal95%, not simultaneous family intervals; corrected p-values do not remove confounding or adaptive winner bias.','',
              '| Candidate | Delta Mbps | Conditional95% interval | Raw p | Holm p |','| --- | --- | --- | --- | --- |']
    for row in audit['contrasts']:
        interval=row['conditional_interval']
        ci='UNESTIMABLE' if interval is None else f'[{interval[0]:.3f}, {interval[1]:.3f}]'
        p='NA' if row['p_value'] is None else f"{row['p_value']:.6g}"
        adjusted='NA' if row['holm_p_value'] is None else f"{row['holm_p_value']:.6g}"
        lines.append(f"|`{row['candidate']}`|{row['delta_mbps']:.3f}|{ci}|{p}|{adjusted}|")
    diag=audit['design_diagnostics'];tail=audit['tail_resolution']
    lines += ['', '## Identification, tails and transfer','',
              f"The engineering design matrix has rank{diag['rank']} for{diag['columns']} columns. Its only constant column is the intercept; additional unmeasured controls lie outside this matrix. AQL low/high/threshold are coupled, RC/RIFS follow adaptive chronology, and randomization/block/pair identities are absent. No isolated AQL, RC, DynamicBW, TXOP or vendor causal effect is identified.", '',
              f"With6 iid RTTs, P(max exceeds the true p99)= {1-0.99**6:.4f}. At least{tail['iid_samples_for_p99_one_sided95']} iid samples are needed for the maximum to upper-bound p99 with95% one-sided coverage ({tail['iid_samples_for_p95_one_sided95']} for p95). Those are ping samples, not independent experimental runs; correlation makes the information gap larger.", '',
              'Same-policy cross-round goodput differences (uncontrolled context, not treatment effects):']
    for row in audit['same_policy_cross_round_changes']:
        lines.append(f"- `{row['knobs']}`: R1{row['R1']:.3f} vs R2{row['R2']:.3f} Mbps; delta{row['difference_mbps']:.3f}.")
    lines += ['', 'The helper uses TCP retransmits/500 as retry_rate and fixes Jain1.0 for a single link; neither is measured MAC PER or PtMP fairness. CT help/shadow getters and boolean restoration flags do not independently prove target effect or exact rollback. Simulated multivendor results are extrapolations with explicit assumptions; Monte Carlo intervals cannot validate transport.','',
              '## Prospective power sensitivity','',
              'Illustrative standardized effects0.2/0.5/0.8 are a sensitivity grid, not observed effects, expected gains or an operator-approved SESOI. Two-sided noncentral-t planning assumes normal independent differences (paired) or equal-variance independent arms. Three-endpoint planning uses Bonferroni alpha/3;10% unusable units are allowed. Paired n counts independent randomized AB pairs; independent n is PER ARM. Repeated pings or16 simulated CPEs are not these units. No observed/post-hoc power was computed.','',
              'Paired effect is d_z = mean AB difference / SD of paired differences; independent effect is d = mean arm difference / common within-arm SD. Equal numeric d values do not assert equal raw effects or variance models. Dropout applies to whole AB pairs or to windows within EACH independent arm, respectively.','',
              '| Design | Assumed effect | Family | Analyzed n | Enroll n | Planned power |','| --- | --- | --- | --- | --- | --- |']
    for row in audit['prospective_power_sensitivity']:
        lines.append(f"|{row['design']}|{row['standardized_effect']}|{row['family_size']}|{row['analyzed_units']}|{row['enrolled_units']}|{row['achieved_planning_power']:.4f}|")
    lines += ['', '## Source contradictions and next evidence','']
    lines.extend('- '+text for text in audit['index_discrepancies'])
    lines += ['',audit['future_design'],'', '## Reproduction and methods','',
              'Run `python -B -m analysis.statistics.fmx_autoresearch_statistical_audit` from the repository root. JSON output preserves descriptive contrasts, design diagnostics, power inputs, source SHA256 and limitations. Numerical tests compare known power results, rounding and monotonicity; this does not prove experimental assumptions. Dependencies use the installed local NumPy/SciPy versions; no package/network installation is performed.','',
              'Methods follow local experimental-design, hypothesis-generation, statistical-analysis, statistical-power, pymoo, SimPy and aeon skills. Aeon time-series fitting is deliberately not applied to six unordered/weakly timestamped pings: absent traces and group/time holdouts prevent defensible classification/forecasting. It was read and informs the non-leakage/data-boundary checks, without adding an unsupported classifier.','',
              'Reference declared by the local skills (bibliographic metadata not rechecked online in this offline task): Kassis T., Agarwal V., He Y., Patel D., Brueckner A.M. (2026), Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents, DOI10.48550/arXiv.2609.00065. Design/power methods are explicitly stated above; skill use is not scientific acceptance.']
    return '\n'.join(lines)+'\n'


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ARTIFACTS/'statistical_causal_audit_20261024.json')
    parser.add_argument('--write-report',action='store_true')
    args=parser.parse_args(argv)
    audit=build_audit()
    write_json(args.output,audit)
    records,refs=load_measurements()
    write_json(ARTIFACTS/'normalized_measurements_20261024.json',descriptive_dataset(records,refs))
    if args.write_report:
        (ROOT/'docs/STAGE12_AUTORESEARCH_STATISTICAL_AND_CAUSAL_AUDIT.md').write_text(render_report(audit),encoding='utf-8')
    print(f'OFFLINE_STATISTICAL_AUDIT: {args.output}')


if __name__=='__main__':
    main()
