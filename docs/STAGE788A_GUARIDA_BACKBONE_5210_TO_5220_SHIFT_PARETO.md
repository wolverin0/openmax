<!-- doc-head: Stage788A conditional5210-to5220MHz two-ray shift Pareto and missing counter provenance -->
The +10MHz decision is a scenario;209.5M subframes and zero-outage gains are not validated.
<!-- /doc-head -->

# Stage788A

Parent: fixed787A..792A offline RE1 support in BENCH_PLAN.
Run `python tools/sim/run_stage788a_guarida_backbone_5210_to_5220_shift_pareto.py`.
No channel command, SSH, RF acquisition, firmware or producer is executed.
SG-01 backbone and PoE switches remain untouched. This emits no operational commands.

## Evidence reconciliation

737 /backbone_telemetry and /expected_shift_outcome are saved synthesis fields.
Its producer constructs a literal dictionary and a preflight checklist marked PASS;
38.64dB,98.8% MCS8,+17.17Mbps and0s outage are expected/synthetic claims, not a
native before/after channel-shift measurement. The held457 simulation hardcodes
a50ns excess-delay premise and calls its baseline5705MHz. That cannot confirm
the requested physical baseline5210MHz, regulatory availability or actual center.
454 has saved EVM summaries; no calibrated transfer function or excess-delay fit.

The requested209,500,000 A-MPDU subframes has no native counter/source pointer
in these scoped inputs. It remains an UNLINKED_OPERATOR_PREMISE, not209.5M
independent trials, PPDU count, measured errors or post-shift evidence.737 instead
declares91,730,000 DL frames and3.92 MPDUs/A-MPDU PPDU without a common reset
epoch/cohort. Those quantities cannot be multiplied into the requested total.
Current absolute link frequency and authenticated acquisition chain remain UNKNOWN.

## Prespecified finite model

H(delta_f,x)=1+rho*exp(i*(phi+2*pi*(delta_f+x)*tau)). x spans[-10,+10]MHz.
For rho={0,.5,.9}, tau={0,25,50,100}ns, phi={0,pi/2,pi}, and SNR={10,20}dB,
compare center5210(stay) vs5220(+10) with assumed switch pauses{0,1,5}s.
There are216 cells, two choices per cell. No state is fitted to a desired winner.
Composite Simpson201 samples integrate log2(1+SNR_linear*abs(H)^2) per Hz.
This is an idealized frequency-selective AWGN capacity density with constant PSD,
not net WA throughput, EVM, MCS selection, latency or a calibrated RF forecast.
Effective density multiplies by(600-pause_s)/600 over an illustrative600s horizon.
Each cell's exact Pareto set maximizes effective density and minimizes pause.
Do not optimize across mutually incompatible unknown channel states.

The analytical mean power1+rho^2+2*rho*cos(phi+2*pi*delta_f*tau)*sinc(B*tau)
checks integration units. A physical spectral null stays at its absolute frequency;
shifting a20MHz window by10MHz retains50% passband overlap. It need not remove
the null, and the same shift can improve, worsen or leave modeled capacity equal.
Subcarrier51 is a saved array index; its vendor absolute-frequency map is unproven.
No assumption fixes multipath to be the actual notch cause or promises zero outage.
Channel legality/DFS/CAC/EIRP, real CSA support, remote coordination and recovery
remain unassessed. No regulatory constraints are waived by a Pareto label.
KEEP the bounded sensitivity; an actual shift remains NOT_APPROVED/UNKNOWN.
