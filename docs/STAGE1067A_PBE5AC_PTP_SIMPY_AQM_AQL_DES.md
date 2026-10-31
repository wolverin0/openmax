<!-- doc-head: 1067A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# PowerBeam PtP SimPy AQM and AQL discrete-event model

SIMULATED_MODEL_ONLY. No measured link, physical acceptance or firmware promotion.

Actual SimPy processes model3 TCP-like HTTP bulk sources,64B VoIP and1316B IPTV bursts.
Arms use the exact requested stock and v17 parameters; all capacities and mechanisms are assumptions.
Each width20/40/80MHz uses3 paired independent seeds,2seconds, empty initial queues.
Reported latency is modeled one-way delivery plus10ms propagation, never measured ping RTT.
Packet conservation includes unfinished/censored packets; application backpressure is separate.
See receipt model_assumptions for DRR/CoDel/AQL/TCP approximations and omitted radio mechanisms.
No claim that the v17 arm wins; no calibrated PHY, EDCA, aggregation or interference model.
Five pillars retain local references; scholar and durable-memory ingestion are deferred offline.

Software references: local `.agents/skills/simpy/SKILL.md` (SimPy4.1.2).
ScientificAgentSkills, Kassis etal.2026, arXiv2609.00065 is a skill-supplied bibliography reference, unverified offline.
