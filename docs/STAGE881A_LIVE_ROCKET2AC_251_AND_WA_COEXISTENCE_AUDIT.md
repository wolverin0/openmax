<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage881A: coexistence audit PARTIAL

Parent: authorized879..884 queue; question: what bands and identities are currently
observed on Rocket2AC .251 and WA .20/.250? Attribution: Linux/airMAX/controller.
Operator correction: MK1 is198.18.0.41, Rocket2AC Prism is198.18.0.48.

Fresh read-only .251 native board/status matches Rocket2AC, center2422MHz/20MHz.
The .20 OpenWrt AP readback has control/center5180MHz/20MHz. Their nominal band
envelopes do not overlap. This does not establish interference immunity or throughput.
Native identity/boot/status readbacks are pinned in the receipt.

The root/none-or-documented-password attempt to .250 failed authentication.
A separate attempt using the documented UBNT user also failed. Both failures are
preserved; no further credential guessing or alternate-address probing occurred.
.250's current channel, peer state and delivery remain UNKNOWN.
No success count for the pair is inferred from .20's reachability.

`python tools/autoresearch/run_stage881a_live_rocket2ac_251_and_wa_coexistence_audit.py --inspect`
performs bounded native reads; without `--inspect` it uses no network.
Exit2 records partial acceptance. No radio setting, route, scan, load or flash changed.
Host keys are observed fingerprints, not pre-pinned trusted deployment identities.

Evidence: [receipt](../artifacts/autoresearch/stage881a_live_rocket2ac_251_and_wa_coexistence_audit.json).
Next: obtain the correct documented credential pointer for .250, then collect its
native peer/channel evidence. A causal coexistence comparison still needs matched
receiver workload windows; this passive inventory is not such a benchmark.
