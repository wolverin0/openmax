<!-- doc-head: Stage789A bench and tower DHCP remediation evidence ledger with unknown runtime closure -->
Static helpers and saved declarations do not prove current or persistent rogue-DHCP eradication.
<!-- /doc-head -->

# Stage789A

Parent: fixed787A..792A offline RE1 support in BENCH_PLAN.
Run `python tools/observability/build_stage789a_bench_and_tower_rogue_dhcp_audit_ledger.py`.
Only frozen local files are read. No helper, producer, shell, service, network,
DHCP probe, SSH, radio configuration or remediation command is executed.

## Claim ledger

774 /rogue_dhcp_remediation declares LTU-Lite .110 br1, fallback192.168.1.20,
dnsmasq/udhcpd neutralized and zero leases. The held helper is compared to its
receipt SHA and the constant extracted with AST literal_eval from its producer.
The helper's process matching/killing is gated by literal argument apply.
Its unconditional success echo prints br1_dhcp_disabled=1 and RTT0.184 even
in default inspect-only mode. No boot-service disable, persistent restart block,
applied readback or DHCP packet transcript is established. Process suppression
at one instant cannot prove a service will not restart or bind via another form.
This ledger does not run, repair, recommend or certify the helper for deployment.

763 /lan_dhcp_and_ani_profile declares OpenWrt br-lan dhcp.lan.ignore=1,
DHCPv4/v6/RA disabled, dnsmasq/odhcpd stopped and disabled. Its --apply text
contains UCI commit/service operations; static intent is checked independently
from a runtime state. Status getters default to1/disabled on failure and operations
use || true. Healthy-looking output or exit0 is therefore insufficient evidence.
ANI inspection is a separate RF concern; it proves nothing about DHCP isolation.
No emitted image/rootfs, applied persistent config or reboot test is audited here.

761 /counterbalanced_rounds has12 saved daemon-count windows; the parser can
default count0, RTT0.184/0.231, and synthesize rounds on exception. Its RTT probe
is127.0.0.1. A live_ssh_connected flag does not exclude fallback after connection.
We do not infer which branch ran, nor turn missing probe data into a healthy count.
The process grep is not per-interface UDP67/547/RA attribution or an offer capture.

## Acceptance remains UNKNOWN

Bench and tower eradication require separate per-device/interface/VLAN evidence:
daemon argv and socket binding, actual UCI/service/startup state, boot identity,
native command exits/readbacks, DHCPv4 offers/acks plus IPv6 DHCP/RA capture with
duration and capture/interface filters, and a reboot/link-down/fallback recurrence
test tied to the same build. Include router identity/default route attribution;
a fallback management IP alone is not proof of a rogue DHCP server.
All those native runtime/persistence/packet-proof links are missing in scoped inputs.
The ledger's eradication_verdict is UNKNOWN_NOT_PROVEN, independently of saved
CONFIRMED labels, zero counts, matching hashes or passing tests. No all-tower
acceptance or present network health is asserted. SG-01 remains untouched.
KEEP the auditable gap ledger; physical remediation is not established offline.
