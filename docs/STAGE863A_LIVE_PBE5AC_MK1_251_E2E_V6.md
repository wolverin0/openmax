<!-- doc-head: Stage863A corrected MK1 address1 and Rocket2AC address251; E2E withheld -->
The legacy filename retains251, but the operator corrected MK1 to198.18.0.41.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage863A: E2E BLOCKED

Parent: authorized861..866 physical bench queue; question: does the corrected MK1 .1-origin
Triple-Play workload traverse .241/.242 OTA under the native v6 treatment?
Attribution: external controller, Linux and QCA firmware. Answer UNKNOWN.

The saved2026-10-27 read-only SSH response from198.18.0.48 identified
Linux Rocket2AC Prism, `2XC.v8.7.11`, board0xe2f2. Reported local routes
include198.18.0.65 and198.18.0.148. An IP alias is not device identity.
The `hostname` utility was absent; stderr is retained rather than called success.
No RouterOS command, routing change, port toggle or endpoint substitution ran.
The operator subsequently confirmed .251=Rocket2AC and .1=MK1. The receipt now
stores that mapping; the old script filename is preserved for task compatibility.
MK1 .1 was not inspected or used as a benchmark origin while native v6 is absent.

`python tools/autoresearch/run_stage863a_live_pbe5ac_mk1_251_e2e_v6.py --inspect`
reads only the specified endpoint using the existing narrow credential pointer.
It returns2; `--execute` also refuses because native v6 and MK1 path are unverified.
No benchmark traffic was generated and all performance metrics are null.

Acceptance requires actual MK1 identity and authorized route, receiver identity,
bridge FDB/neighbor checks and radio counter deltas proving the RF path.
Ping reachability over a shared management switch does not establish OTA delivery.
PB070 activation must first pass861's independent native compatibility review.

Evidence: [receipt](../artifacts/autoresearch/stage863a_live_pbe5ac_mk1_251_e2e_v6.json).
Next: resolve endpoint identity/path and the missing native Quad-Patch.
