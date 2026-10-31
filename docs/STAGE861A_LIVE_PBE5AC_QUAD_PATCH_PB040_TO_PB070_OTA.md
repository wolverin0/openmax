<!-- doc-head: Stage861A native bench observations and missing PB070 activation prerequisite -->
No Quad-Patch was loaded. Stage806A emitted a plan, not firmware.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage861A: activation BLOCKED

Parent: FMX-0011/RE1 native control boundary and the authorized861..866 bench queue.
Question: can the Stage806A Quad-Patch be safely activated on the two PowerBeams?
Answer: no deployable PB070 exists in the supplied source; activation is NOT_ACCEPTED.
Attribution: external controller, ath10k and QCA firmware.

Stage806A's source and receipt explicitly say `patch_emitted=0`. Its ASCII
anchor census is a research plan, not a patch specification. The held Stage817A
candidate contains three patches only; it cannot be relabeled Quad-Patch.
Some Stage806A prose contradicts its actual census/endian readings. Those prose
errors do not justify inventing an instruction offset or replacement byte.

The saved read-only capture on 2026-10-27 confirmed both exact boards as
`ubnt,powerbeam-5ac-gen2`: .241 AP and .242 STA, associated in VHT20 at
5200 MHz control/center. Both exposed pktlog `00000000`; neither had dnsmasq/
odhcpd PIDs or address198.18.0.50. This is an observation at that timestamp,
not a cold-boot persistence or application-path acceptance test.
Native debug paths were discovered dynamically. No firmware, module, register,
configuration, power or flash change was performed. No watchdog was armed.

`python tools/autoresearch/run_stage861a_live_pbe5ac_quad_patch_pb040_to_pb070_ota.py --inspect`
performs bounded reads and writes a local receipt. Exit2 means blocked.
`--execute` also returns blocked; there is no functioning activation loader yet.
The default command audits the missing prerequisite without contacting radios.

Before activation: require exact native firmware/API, all four patch preimages/
replacements and complete diff, independent loadability/safety review, verified
45-second local rollback, STA-first order, dynamic PHY discovery and exact
restoration. Never rename raw SGMT as a native firmware container.

Evidence: [receipt](../artifacts/autoresearch/stage861a_live_pbe5ac_quad_patch_pb040_to_pb070_ota.json),
[independent payload review](../artifacts/verification/stage861a/independent_payload_review.json).
The PC-crash recovery preserved four NUL-filled downstream receipts and rebuilt
them from intact captures. Recovery does not create new physical measurements.
