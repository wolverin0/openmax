<!-- doc-head: Stage953A native tool qualification only; superseded before any multiflow campaign -->
<!-- /doc-head -->

# Stage953A — Multiflow admission checkpoint

Status: **RUNTIME_QUALIFIED_CAMPAIGN_NOT_EXECUTED_SUPERSEDED** by Stage995A..1000A.
Provenance: **CONFIRMED_LIVE_HARDWARE** for inventory and runtime version/dependency
readbacks only. No traffic, listeners, configuration setters or firmware changes.

Both PowerBeam units are OpenWrt24.10.4/ath79/generic, MIPS soft-float musl,
kernel6.6.110, VHT20 at5200MHz. Native iperf/netperf/UDP-capable nc were unavailable.
Both already read tcp_notsent_lowat131072; setting that value would not be a contrast.

Official OpenWrt24.10.4 mips_24kc iperf3.17.1-r4, libiperf3 and libatomic1 packages
were downloaded locally. Manifest size/SHA256, ELF32 big-endian MIPS, PT_MIPS_ABIFLAGS
soft-float and native musl interpreter/dependencies were checked. No detached usign
verification is claimed. ELF program headers were used because sections are stripped.

After coordinator approval, three exact files per host were copied only into private
RAM directories, verified by native SHA256, then executed only for --version and loader
--list. Both actual commands returned0 with all dependencies resolved.

| Host | Owned RAM directory |
| --- | --- |
| .241 | /tmp/fmx-s953-runtime-nlJGHG |
| .242 | /tmp/fmx-s953-runtime-bleMhe |

Those directories remain for the next authorized stage to reuse or explicitly clean.
No system package install or library replacement occurred.

AA, discovery and holdout have **0 pairs**, no normalized measurements, null gate
results and no replication receipt. A new AQL treatment still requires independent
native45s rollback proof; the earlier907 proof failed and does not qualify.

The generated harness is an **unreviewed, unexecuted draft**. Do not run it: its reset
placeholder, cleanup escalation, listener readiness and receiver JSON admission need
the fixes listed in the handoff. Bash syntax/py_compile passing is not runtime proof.

[Receipt](../artifacts/autoresearch/stage953a_live_powerbeam_multiflow_aa_discovery_holdout.json),
[handoff](../artifacts/verification/stage953a/handoff_checkpoint.json),
[native runtime proof](../artifacts/verification/stage953a/runtime_bootstrap.json).
