<!-- doc-head: Stage 919A offline model attributing Stage 899A's 18.44% ICMP loss to congestion/bufferbloat (unpaced parallel downloads) vs LNA saturation; fq_codel/AQL mitigate, LNA ~0 at bench RSSI -->
# Stage 919A — PowerBeam Loss: LNA Saturation vs Congestion

- **Claim Status**: `CONFIRMED` (offline model)
- **Attribution**: `external controller (offline model)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage919a_powerbeam_lna_saturation_vs_congestion_loss_model.json`
- **Tool**: `tools/sim/run_stage919a_powerbeam_lna_saturation_vs_congestion_loss_model.py`
- **Evidence class**: `SIMULATED_MODEL_ONLY`

## 1. The observed anchor (real)
Stage 899A (A/A read-only control) recorded **18.44% aggregate ICMP loss**
(320 sent / 261 received over 16 windows) during concurrent 4 MiB HTTP downloads,
with **no `tc` installed** (`qdisc_readback=UNAVAILABLE_TC_NOT_INSTALLED`). So the
loss occurred under **unpaced** parallel load — the exact congestion scenario.

## 2. Two candidate mechanisms modelled
- **Congestion / bufferbloat**: ICMP probes queue behind unpaced bulk TCP and are
  tail-dropped. A SimPy queue sim compares FIFO (no pacing) vs fq_codel (ICMP flow
  isolation) vs AQL (bounded airtime backpressure).
- **LNA saturation**: near-field receiver compression above the ~−45 dBm P1dB knee;
  an analytic RSSI→loss curve. Loss here is ~independent of pacing.

## 3. Results
| ICMP-loss model | Loss |
| :--- | :--- |
| FIFO (no pacing) | 57.89% |
| fq_codel (flow isolation) | 0.0% |
| AQL (airtime backpressure) | 0.0% |
| LNA saturation @ bench −57 dBm | 0.0% |

- The observed **18.44%** is **bracketed** by the fully-paced (0%) and fully-unpaced
  (57.89%) predictions — it is *not* reverse-fitted to an exact value.
- At the bench RSSI (~−57 dBm, below the −45 dBm P1dB knee) modelled LNA loss is **0%**.

## 4. Attribution
**`CONGESTION_BUFFERBLOAT`** — the 899A loss is consistent with unpaced-download
congestion, which `fq_codel` flow isolation + `ath10k` AQL would mitigate (both drive
modelled ICMP loss toward 0). LNA saturation is not implicated at bench power.

## 5. Reproduce & limits
```sh
python tools/sim/run_stage919a_powerbeam_lna_saturation_vs_congestion_loss_model.py
python -m pytest tests/test_stage917a_to_922a_suite.py -q
```
A model, not a measurement. The bracketing supports congestion over LNA saturation
but does not prove it: per audit E5, a hardware PPS-vs-RF-ceiling test (external
generators, packet-size sweep at fixed PHY) is required to confirm the mechanism.
The AQL=0% result shows the mitigation direction, not a guaranteed field number.
