<!-- doc-head: Stage818A static LTU 12X LDPC provenance and br1-only DHCP shield plan -->
<!-- /doc-head -->
# Stage 818A LTU 4096QAM 12X / LDPC / Super4096 safe kit

`CONFIRMED` applies to offline packaging only. Attribution: `Linux` / `proprietary airMAX/LTU module`.
Saved Stage651A and Stage546A receipts are hashed and copied into `artifacts/autoresearch/kits/stage818a`.
The RE module hashes are rechecked against actual local files; no producer or radio was executed.
4096QAM/12X tables, LDPC and Super4096 symbols are static evidence, not an unlock or radio acceptance.
The shell helper defaults to inspection, reports unavailable telemetry UNKNOWN and rejects modulation activation.
`--plan-zero-dhcp` prints a proposed br1-only filter; it executes no firewall command or daemon stop.
`--apply-zero-dhcp --confirm-br1-192.168.1.20` is packaged but was exercised only with local command stubs.
It requires uid0, exact br1 fallback address and a known ebtables backend; only its dedicated chain and
br1-only OUTPUT/FORWARD first-rule jumps change, preceding existing ACCEPT rules. Repeats require exact
rule and first-position readback; partial failures roll back.
Unrelated firewall chains, DHCP daemons and client requests remain untouched. No persistent service is installed.
The policy model blocks DHCPv4/v6 server offers on br1 in OUTPUT/FORWARD and preserves br0 DHCP.
The target fallback identity is `br1` / `192.168.1.20`. Actual service binding and firewall behavior remain UNKNOWN.
`zero_rogue_dhcp_verified=false`; no observed lease count is invented. A future authorized bench must test leases,
daemon respawn, restart persistence, unrelated LAN DHCP, IPv4/IPv6 and rollback before deployment.
No `/dev/ame*`, firmware, calibration, modem, LDPC, modulation or transmit-power writes are provided.
No SSH, live measurement, online scholar query or durable MemoryMaster ingestion occurred.
