<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage880A: direct OTA treatment BLOCKED

Parent: authorized879..884 queue; question: does native Quad improve the verified
baseline directly between .241 AP and .242 STA? Attribution: ath10k/QCA firmware/controller.
The corrected topology has Rocket2AC at .251 and MK1 at .1; neither is a workload
origin for this direct comparison. No command was sent to MK1.

Fresh read-only observations2026-10-27: both PowerBeam5AC Gen2 units are associated
at control/center5200MHz, VHT20. Both expose pktlog0 and firmware-2 hash
`a49160ff008390a34e43145bc56f6b8d047f8e02433aff20f965b6f2874ef52f`.
This differs from the held stock CT reference inspected in879.
The earlier native driver evidence was API2; firmware-5 was not found in the current
directory listing. API5 compatibility cannot be inferred from a renamed SGMT.

Requested VHT40 target: center5190MHz, e.g. legal control5200MHz/HT40-minus.
5190 is not used as a20MHz control channel. Regulatory and power settings remain untouched.
Twelve A1,B1,A2,B2 windows across3 rounds are planned, all NOT_EXECUTED, metrics null.
No TCP/UDP load, firmware upload, SCP, bind mount, PHY reload, watchdog or flash ran.
There is no complete activation/benchmark runner while native Quad is absent.

`python tools/autoresearch/run_stage880a_live_pbe5ac_verified_quad_patch_ota_bench.py --inspect`
reads only the two PowerBeams; `--execute` records refusal and returns2.
Before activation require879's real reviewed Quad, exact native API/path, tested45s
local rollback, STA-first activation, dynamic PHY discovery and exact restoration.
Before benchmark require RF counters/FDB proving no management-switch bypass,
matched receivers and offered load. Ping reachability alone cannot prove OTA.

Evidence: [receipt](../artifacts/autoresearch/stage880a_live_pbe5ac_verified_quad_patch_ota_bench.json).
Next: resolve PB070 semantics and verified native payload before any link interruption.
