#!/usr/bin/env python3
"""Held DHCP remediation evidence ledger; never certifies a live network."""
import ast
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.sim import stage787_792_common as h
c=h.c
SCRIPT='tools/observability/build_stage789a_bench_and_tower_rogue_dhcp_audit_ledger.py'
OUT='artifacts/autoresearch/stage789a_bench_and_tower_rogue_dhcp_audit_ledger.json'
DOC='docs/STAGE789A_BENCH_AND_TOWER_ROGUE_DHCP_AUDIT_LEDGER.md'
LTU='artifacts/autoresearch/stage774a_ltu_champion_v20_264window_zero_dhcp_kit.json'
OW='artifacts/autoresearch/stage763a_openwrt_lan_rogue_dhcp_and_ani_guard.json'
LIVE='artifacts/autoresearch/stage761a_live_ltu110_round22_264window_autoresearch.json'
LP='tools/firmware/build_stage774a_ltu_champion_v20_264window_zero_dhcp_kit.py'
OP='tools/firmware/build_stage763a_openwrt_lan_rogue_dhcp_and_ani_guard.py'
VP='tools/bench/run_stage761a_live_ltu110_round22_264window_autoresearch.py'
LS='firmware/ltu_safe_kit/fmx_ltu_v20_264window_zero_dhcp_kit.sh'
OS='firmware/openwrt/common/fmx_openwrt_lan_rogue_dhcp_and_ani_guard.sh'
SOURCES=(LTU,OW,LIVE,LP,OP,VP,LS,OS)
REQUIRED={'dhcp_lan_ignore':'1','dhcp_lan_dhcpv4':'disabled','dhcp_lan_dhcpv6':'disabled',
          'dhcp_lan_ra':'disabled','dnsmasq_service':'stopped_and_disabled','odhcpd_service':'stopped_and_disabled'}
DOC_TEXT='''<!-- doc-head: Stage789A bench and tower DHCP remediation evidence ledger with unknown runtime closure -->
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
'''


def literal(text,name,function=False):
    tree=ast.parse(text);bindings=[]
    for node in tree.body:
        names=set()
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):names.add(node.name)
        elif isinstance(node,(ast.Assign,ast.AnnAssign,ast.AugAssign)):
            targets=node.targets if isinstance(node,ast.Assign) else [node.target]
            names.update(n.id for target in targets for n in ast.walk(target) if isinstance(n,ast.Name))
        elif isinstance(node,(ast.Import,ast.ImportFrom)):
            names.update(a.asname or a.name.split('.')[0]for a in node.names)
        if name in names:bindings.append(node)
    if len(bindings)!=1:raise ValueError('unique_string_binding_required:'+name)
    node=bindings[0]
    if function:
        if not isinstance(node,ast.FunctionDef) or node.decorator_list:raise ValueError('plain_literal_function_required')
        body=node.body
        if body and isinstance(body[0],ast.Expr) and isinstance(body[0].value,ast.Constant) and isinstance(body[0].value.value,str):body=body[1:]
        if len(body)!=1 or not isinstance(body[0],ast.Return):raise ValueError('single_direct_literal_return_required')
        expression=body[0].value
    else:
        if not isinstance(node,ast.Assign) or len(node.targets)!=1 or not isinstance(node.targets[0],ast.Name):
            raise ValueError('plain_string_assignment_required')
        expression=node.value
    value=ast.literal_eval(expression)
    if not isinstance(value,str):raise ValueError('string_literal_required')
    return value


def declarations(profile):
    if not isinstance(profile,dict):raise ValueError('profile_object_required')
    return {key:dict(declared=profile.get(key),required=value,declared_match=profile.get(key)==value)
            for key,value in REQUIRED.items()}


def window_counts(receipt):
    rounds=receipt['counterbalanced_rounds']
    if not isinstance(rounds,list) or not 1<=len(rounds)<=20:raise ValueError('bounded_rounds_required')
    rows=[];seen=set()
    for r in rounds:
        rid=c.integer(r['round'],'round',1,100)
        if rid in seen:raise ValueError('duplicate_round')
        seen.add(rid)
        windows=r['windows']
        if list(windows)!=['A1','B1','A2','B2']:raise ValueError('ABAB_required')
        for name,w in windows.items():
            count=w.get('rogue_dhcp_daemon_count')
            if count is not None:c.integer(count,'daemon_count',0,100000)
            rows.append(dict(round=rid,window=name,count=count,
                             status='SAVED_DECLARATION' if count is not None else 'UNKNOWN_MISSING'))
    return dict(windows=rows,count=len(rows),all_saved_counts_zero=all(w['count']==0 for w in rows),
                native_transcripts_available=False,eradication_proven=False)


def build(root=ROOT):
    payloads,sources=h.freeze(root,789,SOURCES)
    l=h.json_source(payloads[LTU]);o=h.json_source(payloads[OW]);v=h.json_source(payloads[LIVE])
    ls=payloads[LS].decode('utf-8');os=payloads[OS].decode('utf-8');vp=payloads[VP].decode('utf-8')
    generated_l=literal(payloads[LP].decode('utf-8'),'build_helper_script',function=True).encode()
    generated_o=literal(payloads[OP].decode('utf-8'),'HELPER_SH_CONTENT').replace('\r\n','\n').encode()
    rows=[dict(scope='LTU110_BR1',claim_pointer='/rogue_dhcp_remediation',saved_claim=l['rogue_dhcp_remediation'],
        helper_hash_matches_receipt=c.sha(payloads[LS])==l['helper_sha256'],helper_matches_held_producer=generated_l==payloads[LS],
        static_patterns=dict(apply_gate='if [ "$MODE" = "apply" ]' in ls,
            default_inspect='MODE="${1:---inspect-only}"' in ls,
            literal_healthy_echo='br1_dhcp_disabled=1' in ls and 'rtt_ms=0.184' in ls),
        runtime_applied='UNKNOWN',persistence='UNKNOWN',offer_capture='MISSING'),
        dict(scope='OPENWRT_BR_LAN',claim_pointer='/lan_dhcp_and_ani_profile',
        requirements=declarations(o['lan_dhcp_and_ani_profile']),
        helper_hash_matches_receipt=c.sha(payloads[OS])==o['helper_script']['sha256'],helper_matches_held_producer=generated_o==payloads[OS],
        static_patterns=dict(apply_gate='if [ "$MODE" = "--apply" ]' in os,
            status_healthy_fallback='|| echo "1"' in os and '|| echo "disabled"' in os,
            ignored_command_failures='|| true' in os,uci_commit_text='uci commit dhcp' in os),
        runtime_applied='UNKNOWN',persistence='UNKNOWN',offer_capture='MISSING')]
    risks=dict(loopback_probe='127.0.0.1' in vp,count_can_default_zero='else 0' in vp,
        broad_exception_path='except Exception:' in vp,rtT_literal_defaults='rtt_avg_ms = 0.184' in vp,
        actual_fallback_execution='UNKNOWN')
    return h.finish(root,789,SCRIPT,OUT,DOC,DOC_TEXT,dict(status='QUALIFIED_OFFLINE_DHCP_EVIDENCE_LEDGER',
        claim_classification='UNKNOWN_RUNTIME_ERADICATION',attribution='Linux / external offline auditor',
        eradication_verdict='UNKNOWN_NOT_PROVEN',scopes=rows,saved_windows=window_counts(v),producer_risks=risks,
        missing_evidence=['Interface/VLAN-bound native daemon/socket/config/boot readbacks.',
                         'DHCPv4/DHCPv6/RA packet capture with duration and source attribution.',
                         'Persistence and fallback recurrence after reboot/link-down.']),sources)


if __name__=='__main__':raise SystemExit(h.cli(build))
