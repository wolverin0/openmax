<!-- doc-head: 961A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# PB controller unified physical runner migration 961A

The physical entrypoint delegates to the Stage959A unified acquisition/inference runner.
Its frozen controller role is `PB_032_033_RATEMASK_SGI`; cross-controller plans are rejected before acquisition.
Plan creation and execution are distinct. Inspection is the default and invokes no acquisition callback.
An executed campaign requires A/A, discovery and disjoint holdout with raw per-window SHA256 evidence.
Actual hardened Flent parsing and RegressionGatekeeper evaluate the supplied acquisition bytes.
Metric arrays, boolean holdout declarations and synthetic fixture verdicts cannot authorize physical promotion.
Legacy diagnostic mathematics and synthetic reports remain available, separately labeled and non-promotable.
The builder pins software only and never contacts a radio, runs a workload, or writes durable memory.
Offline fault-injection tests and their actual exit/count evidence are consolidated in Stage964A.
Source construction is CONFIRMED; actual physical acquisition and release acceptance remain UNKNOWN.
