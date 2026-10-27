<!-- doc-head: Stage354A bounded synthetic four-series retry and finite Pareto study -->
Actual SimPy scheduling and pymoo ranking use uncalibrated synthetic inputs.
Native188-byte WMI ABI, packet fields, transport and physical acceptance stay blocked.
<!-- /doc-head -->

# Stage354A

Parent: offline RE1 retry/control-boundary analysis following Stage353.
Question: what tradeoffs does an explicit four-series model produce under the
same finite synthetic channel traces? No new device experiment is performed.

Run `python tools/sim/build_stage354a_wmi_4series_retry_fallback_pareto.py`, then
`python -m pytest -q -o addopts= tests/test_stage354a.py`.
The JSON binds the implementation, tests, helper, Stage18 codec and held header.
The exact header is frozen at artifacts/verification/stage354a/series_bw.h;
its pinned SHA256 is verified before simulation, without a temporary-directory dependency.

## Control boundary

The18 candidates use initial2SS SGI, retry2SS LGI, then1SS STBC across TWO TX
chains, followed by1SS LGI on chain0/chain1 or an explicit CDD hypothesis.
STBC is not one TX chain. CDD is not the STBC bit; enabling two chains with
STBC=0 does not establish a cyclic-delay configuration or target support.
Peer2SS/twoTX/LDPC/STBC/GI declarations are required by the candidate builder.
These declarations and the CDD assumption are model inputs, not runtime readbacks.
Every model series is VHT20/MCS0..8 with at most2SS/twoTX; proxy baselines require
2SS/mask3/LGI/LDPC and no STBC, CDD or beamforming. Other shared-codec modes reject.
The source-pinned16-byte descriptor template is not a complete PPDU or a native
188-byte WMI message. No transport endianness or retry-array binding is qualified.
No deploy payload is emitted; native_payload() always raises the ABI blocker.
Held WA8.7.25 umac wmi_send_node_rate_sched (.text+0xb0120,160B) has bounded
MIPS immediates0xbc and opcode0x9044. Its symbol/instruction hashes are retained.
This confirms a static sender length/opcode, not four-series payload semantics.

## Conceptual model and bounds

Twenty policies include two fixed/descending2SS PROXY baselines. Neither baseline
implements or measures Minstrel, ath10k, proprietary firmware rate control or airMAX.
Four scenarios are balanced control, mirrored asymmetric foliage, and correlated
multipath bursts. Each uses three fixed seeds and128 finite packet arrivals.
The240 replications start empty and drain every generated packet to a recorded
delivery, retry exhaustion or queue drop. This is a terminating transient study.
One SimPy FIFO resource serializes modeled transmissions; retries retain ownership.
SNR thresholds, diversity offsets, logistic PER, arrivals and timing overheads are
illustrative assumptions disclosed in JSON, not receiver calibration or RF evidence.
Independent RNG streams provide common random inputs across policies.
Packet/entity, attempt, event and simulated-horizon caps prevent open-ended runs.

Generated=delivered+retry_exhausted+queue_dropped, outstanding=0; payload bytes are
conserved. Goodput counts delivered bytes once over elapsed simulation time.
Busy time cannot exceed elapsed time. Every failed attempt consumes modeled service.
Queue drops have zero terminal delay; delivered-only delays and loss are separately
reported so a low delay from discarding packets cannot be read as healthy service.

## Finite Pareto interpretation

pymoo NSGA-II evaluates ALL20 finite policies as one complete initial generation.
Objectives minimize negative mean goodput, mean per-run terminal p99, and mean loss.
There is no continuous search, unseen-policy optimum or convergence claim.
Means give equal weight to the12 fixed scenario/seed combinations. A mean of p99s
is not a pooled p99. Per-scenario replication SD and ranges are descriptive, not
confidence intervals or statistical evidence of a causal radio improvement.
Results can expose tradeoffs in the chosen model, including negative outcomes.

Missing validation: measured per-chain quality/PER and burst statistics, actual
retry traces, CDD configuration, peer capabilities, aggregate/BA/TCP interactions,
packet-dependent duration/padding/symbol fields, vendor188-byte ABI and legal RF
characterization. No physical acceptance, measured gain or deployment follows.
Decision: KEEP as a reproducible offline hypothesis model; native execution BLOCKED.

Primary APIs: [SimPy Resource](https://simpy.readthedocs.io/en/stable/simpy_intro/shared_resources.html),
[pymoo NSGA-II](https://pymoo.org/algorithms/moo/nsga2.html).
