<!-- doc-head: 1068A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# PowerBeam PtP NSGA-II channel-width sensitivity

SIMULATED_MODEL_ONLY. Actual pymoo NSGA-II evaluates the Stage1067A SimPy model at20/40/80MHz.

Five sensitivity variables: FQ packet limit, byte quantum, perAC AQL scale, airtime threshold and unsent TCP bytes.
Each width uses population12,4generations,2 common simulation seeds and0.6seconds per replication.
Objectives minimize negative modeled goodput, VoIP p95 one-way model delay and IPTV drop fraction.
Rounded candidates and returned objective vectors are revalidated. Full evaluated candidates are retained.
This is a bounded approximate front; no global optimum, calibrated capacity or physical champion is claimed.
Sensitivity tuning seeds are discovery only: no independent holdout or Gatekeeper acceptance.
Flat objectives and ties are reported explicitly and do not identify superior knob values.
Five-pillar metadata is structural; external scholarship and durable-memory ingestion are deferred offline.

Software references: local `.agents/skills/pymoo/SKILL.md` (pymoo0.6.2), `.agents/skills/simpy/SKILL.md` (SimPy4.1.2).
ScientificAgentSkills, Kassis etal.2026, arXiv2609.00065 is a skill-supplied bibliography reference, unverified offline.
