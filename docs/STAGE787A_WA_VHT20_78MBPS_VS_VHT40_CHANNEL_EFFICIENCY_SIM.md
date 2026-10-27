<!-- doc-head: Stage787A saved VHT20 anchor and conditional VHT40 edge-interference sensitivity -->
78.513Mbps is a selected saved window; bandwidth scaling and interference are assumptions.
<!-- /doc-head -->

# Stage787A

Parent: fixed787A..792A offline RE1 support in BENCH_PLAN, forward-plan reproducibility.
Run `python tools/sim/run_stage787a_wa_vht20_78mbps_vs_vht40_channel_efficiency_sim.py`.
Inputs are frozen on first run and reused byte-for-byte; producer files are text only.
No radio, network, target code, RF load, channel/configuration or firmware is executed.

## Saved anchor and units

676 /rounds[S676A-R77]/windows[B1] reports78.513Mbps over3.844s, with
41.041DL +33.918UL +3.430IPTV +0.124VoIP =78.513Mbps, OTA byte rate71.024.
The held measurement helper takes max(application sum, OTA byte rate); it does
not consistently define application-only goodput across all windows. Parse/default
and native acquisition provenance are not authenticated by current producer bytes.
R77 B2 reports74.578; the two-B arithmetic mean is76.5455Mbps. The selected B1
peak is neither a long-run average nor an independent replication distribution.
20MHz is a saved document/profile premise; per-window iw width readback is absent.

78.513Mbps /20MHz =3.92565 bit/s/Hz. Rounded to two decimals this is3.93,
not3.92; requested78.51 gives3.9255. Rates are aggregate bidirectional composite
service per nominal channel width, not PHY constellation or spatial-stream efficiency.

## Prespecified finite sensitivity

R=78.513 reference Mbps. For b20 in{0,.2,.5}, incremental edge busy fraction
e in{0,.1,.3,.5,.8}, and clean40/20 multiplier k in{1,1.5,2}:
G20=R*(1-b20); b40=min(1,b20+e); G40=R*k*(1-b40).
Efficiency is G/nominal_width_MHz. Forty-five assumption cells compare two widths.
Each cell gets an exact two-objective Pareto set (maximize G and G/width).
Do not pool different interference cells as if they were alternative controls.
G40>G20 iff b40<1-(1-b20)/k. Efficiency40>efficiency20 requires
k*(1-b40)>2*(1-b20). For k<=2 and b40>=b20,40MHz never has greater efficiency.

These busy fractions/multipliers are illustrative, not measured FFT occupancy,
PER, interference statistics, CPU headroom or equal-EIRP PHY scaling. No SimPy
queue or NSGA search is needed for this fully enumerated algebraic grid.
Noise-bandwidth/power-density, retries, hidden nodes, MAC scheduling and latency
are omitted. k=2 is a hypothetical scaling endpoint, not a guaranteed40MHz gain.
No confidence interval is invented from two B-windows or grid cells.
KEEP the sensitivity tool; physical width/interference superiority remains UNKNOWN.
The JSON includes exact pointers, arithmetic, assumptions and qualified boundaries.
