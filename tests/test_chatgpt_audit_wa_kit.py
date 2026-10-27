"""WA actuator regressions; every device command is replaced by local stubs."""
from pathlib import Path
import os
import hashlib
import json
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh'
BASH = Path('C:/Program Files/Git/bin/bash.exe')


@pytest.mark.parametrize('mode',['','--dry-run','--inspect-only'])
def test_default_is_planned_without_device_commands(tmp_path,mode):
    bindir = tmp_path / 'bin'; bindir.mkdir()
    log = tmp_path / 'calls.txt'
    for tool in ('uci', 'tc', 'sysctl'):
        (bindir / tool).write_text('#!/bin/sh\nprintf "%s\\n" "$0 $*" >> "$WA_CALL_LOG"\nexit 17\n', encoding='utf-8', newline='\n')
    path = '/' + bindir.drive[0].lower() + bindir.as_posix()[2:]
    proc = subprocess.run([str(BASH), '-c', f'PATH="{path}:$PATH"; export PATH; exec sh "{HELPER.as_posix()}" {mode}'],
                          env=dict(os.environ, WA_CALL_LOG=log.as_posix()), capture_output=True, text=True)
    assert proc.returncode == 0 and 'PLANNED' in proc.stdout, (proc.returncode, proc.stdout, proc.stderr)
    assert not log.exists()


DRIVER = r'''
import json, os, pathlib, subprocess, sys
sys.stdout.reconfigure(newline='\n')  # Emulate device LF, not Windows CRLF.
tool,args=sys.argv[1],sys.argv[2:]
path=pathlib.Path(os.environ['WA_DEVICE_STATE'])
state=json.loads(path.read_text())
with pathlib.Path(os.environ['WA_CALL_LOG']).open('a') as stream:stream.write(json.dumps([tool,*args])+'\n')
def persist():path.write_text(json.dumps(state))
def convert(label):
    if len(label)>3 and label[0]=='/' and label[2]=='/':return label[1].upper()+':'+label[2:]
    return label
def mutation():
    state['mutations']+=1
    if state['mutations']==int(os.environ.get('WA_INTERRUPT_MUTATION','0')):
        # A Windows os.kill(SIGTERM) uses TerminateProcess and skips POSIX traps.
        # Signal the fixture's MSYS shell PID through its own shell runtime.
        persist();subprocess.run(['C:/Program Files/Git/bin/bash.exe','-c','kill -TERM "$WA_SHELL_PID"'],check=True)
    target=int(os.environ.get('WA_FAIL_MUTATION','0'))
    if state.get('failure_injected') and os.environ.get('WA_ROLLBACK_FAIL'):
        persist();sys.exit(17)
    if target and state['mutations']==target:
        state['failure_injected']=True;persist();sys.exit(17)
if tool=='id':print('0')
elif tool=='ubus':print(json.dumps({'board_name':'ubnt,lap-120','board_revision':os.environ.get('WA_REVISION','revA')}))
elif tool=='jsonfilter':print(json.loads(args[args.index('-s')+1]).get(args[args.index('-e')+1][2:],'') or '')
elif tool=='uname':print('6.6.110')
elif tool=='ethtool':print('driver: ath10k_pci\nfirmware-version: fixture-fw-v1')
elif tool=='readlink':
    print('/devices/ieee80211/phy1' if args[-1].endswith('/phy80211') else '/drivers/ath10k_pci')
elif tool=='stat':
    target=pathlib.Path(convert(args[-1]))
    metadata=target.stat()
    owner=os.environ.get('WA_STATE_OWNER','0')
    mode=os.environ.get('WA_STATE_MODE','700' if target.is_dir() else '600')
    print(f'{owner}:{mode}:{metadata.st_nlink}')
elif tool=='cat':
    label=args[-1]
    if label.startswith(('/sys/', '/proc/')):
        if label not in state['attrs']:sys.exit(1)
        print(state['attrs'][label])
    else:print(pathlib.Path(convert(label)).read_text().rstrip('\n'))
elif tool=='tee':
    label=args[-1];value=sys.stdin.read().strip()
    if label not in state['attrs']:sys.exit(1)
    mutation()
    if label.endswith('/aql_txq_limit'):
        ac,low,high=value.split()
        if low!='2000':state['restoring']=True
        native=state['attrs'][label].startswith('AC ')
        labels=['VO','VI','BE','BK']
        rows=[line.split() for line in state['attrs'][label].splitlines() if not line.startswith('AC ')]
        rows[int(ac)]=[labels[int(ac)] if native else ac,low,high]
        value=('AC low high\n' if native else '')+'\n'.join(' '.join(row) for row in rows)
    if not(os.environ.get('WA_FALSE_READBACK') and label.endswith('/limit_max') and value=='15140'):
        state['attrs'][label]=value
    persist()
elif tool=='sysctl':
    if args[0]=='-n':
        print(state['sysctl'][args[1]])
        if os.environ.get('WA_GETTER_ERROR') and state['mutations']>=10 and not state.get('restoring'):sys.exit(17)
    else:
        mutation();key,value=args[1].split('=');state['sysctl'][key]=value;persist()
elif tool=='tc':
    if 'show' in args:
        if os.environ.get('WA_SNAPSHOT_ERROR') and not state['mutations']:sys.exit(17)
        q=state['qdisc']
        print('qdisc fq_codel '+q['handle']+' root refcnt 2 limit '+q['limit']+'p flows '+q['flows']+' quantum '+q['quantum']+' target '+q['target']+' interval '+q['interval']+' memory_limit '+q['memory_limit']+'b drop_batch '+q['drop_batch']+' '+q['ecn']+os.environ.get('WA_UNKNOWN_QDISC',''))
    else:
        if 'fq_codel' not in args or 'initial_quantum' in args:sys.exit(18)
        mutation();tokens=args[args.index('fq_codel')+1:];q={'handle':args[args.index('handle')+1]}
        while tokens:
            key=tokens.pop(0)
            if key in ('ecn','noecn'):q['ecn']=key
            else:q[key]=tokens.pop(0)
        state['qdisc']=q;persist()
else:sys.exit(19)
'''


def shell_path(path):
    path = Path(path)
    return '/' + path.drive[0].lower() + path.as_posix()[2:]


def identity(path, **changes):
    fields = dict(board='ubnt,lap-120', revision='revA', kernel='6.6.110', driver='ath10k_pci',
                  firmware='fixture-fw-v1', radio='wlan0', phy='phy1', egress='eth0', radio_ifindex='12', egress_ifindex='2')
    fields.update(changes)
    fields['fingerprint'] = hashlib.sha256(('\n'.join(fields.values())+'\n').encode()).hexdigest()
    path.write_text(''.join(f'{key}={value}\n' for key,value in fields.items()))


@pytest.fixture
def fixture(tmp_path):
    bindir=tmp_path/'bin';bindir.mkdir()
    driver=tmp_path/'driver.py';driver.write_text(DRIVER,encoding='utf-8')
    for tool in ('id','ubus','jsonfilter','uname','ethtool','readlink','cat','tee','tc','sysctl','stat'):
        (bindir/tool).write_text(f'#!/bin/sh\nexec "{Path(sys.executable).as_posix()}" "{driver.as_posix()}" {tool} "$@"\n',encoding='utf-8',newline='\n')
    attrs={'/sys/class/net/wlan0/ifindex':'12','/sys/class/net/eth0/ifindex':'2',
           '/proc/sys/net/core/default_qdisc':'fq_codel',
           '/sys/class/net/eth0/tx_queue_len':'1000',
           '/sys/kernel/debug/ieee80211/phy1/aql_txq_limit':'\n'.join(f'{i} {1000+i} {3000+i}' for i in range(4)),
           '/sys/kernel/debug/ieee80211/phy1/ath10k/pktlog_filter':'16',
           '/sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_max':'32768'}
    state=dict(attrs=attrs,sysctl={'net.core.netdev_tstamp_prequeue':'1','net.ipv4.tcp_autocorking':'1','net.ipv4.tcp_recovery':'0',
               'net.ipv4.tcp_notsent_lowat':'65536'},
               qdisc=dict(handle='8001:',limit='10240',flows='1024',quantum='1514',target='5000us',interval='100000us',memory_limit='33554432',drop_batch='64',ecn='ecn'),mutations=0)
    device=tmp_path/'device.json';device.write_text(json.dumps(state))
    contract=tmp_path/'identity';identity(contract)
    snapshot=tmp_path/'snapshot'
    def run(mode='--apply', qdisc_mode=None, tc_present=True, helper=HELPER, **settings):
        tc_stub=bindir/'tc'
        if not tc_present and tc_stub.exists():tc_stub.unlink()
        # A private PATH proves absence instead of accidentally finding a host's tc.
        for tool in ('sh','awk','sha256sum','mkdir','rmdir','mv'):
            (bindir/tool).write_text(f'#!/bin/sh\nexec /usr/bin/{tool} "$@"\n',encoding='utf-8',newline='\n')
        environment=dict(os.environ,WA_DEVICE_STATE=str(device),WA_CALL_LOG=str(tmp_path/'calls.jsonl'),MSYS2_ARG_CONV_EXCL='*')
        environment.update({f'WA_{key.upper()}':str(value) for key,value in settings.items()})
        option='' if qdisc_mode is None else ' --qdisc-mode '+qdisc_mode
        command=f'PATH="{shell_path(bindir)}"; export PATH; WA_SHELL_PID=$$; export WA_SHELL_PID; exec sh "{helper.as_posix()}" {mode} --identity "{shell_path(contract)}" --state-dir "{shell_path(snapshot)}"{option}'
        return subprocess.run([str(BASH),'-c',command],env=environment,capture_output=True,text=True)
    return dict(run=run,device=device,contract=contract,snapshot=snapshot,original=state,tmp=tmp_path)


@pytest.mark.parametrize('backend,tc_present', [('tc', True), ('sysfs-default', False)])
def test_qdisc_modes_apply_verify_and_restore(fixture, backend, tc_present):
    first=fixture['run'](qdisc_mode=backend,tc_present=tc_present)
    assert first.returncode==0, (first.stdout,first.stderr)
    selected='tc' if tc_present else 'kernel_default_fq_codel'
    assert 'qdisc_backend='+selected in first.stdout
    before=json.loads(fixture['device'].read_text())['mutations']
    checked=fixture['run']('--verify',qdisc_mode=backend,tc_present=tc_present)
    assert checked.returncode==0 and 'APPLIED_VERIFIED' in checked.stdout,(checked.stdout,checked.stderr)
    assert json.loads(fixture['device'].read_text())['mutations']==before
    restored=fixture['run']('--rollback',qdisc_mode=backend,tc_present=tc_present)
    assert restored.returncode==0,(restored.stdout,restored.stderr)
    assert device_view(json.loads(fixture['device'].read_text()))==device_view(fixture['original'])


def test_auto_without_tc_uses_configured_kernel_default(fixture):
    result=fixture['run'](tc_present=False)
    assert result.returncode==0 and 'qdisc_backend=kernel_default_fq_codel' in result.stdout,(result.stdout,result.stderr)
    calls=[json.loads(line) for line in (fixture['tmp']/'calls.jsonl').read_text().splitlines()]
    assert not any(row[0]=='tc' for row in calls)
    assert 'active_qdisc=UNKNOWN' in result.stdout


@pytest.mark.parametrize('default', ['pfifo_fast', None])
def test_no_tc_and_no_fq_codel_default_fails_before_mutation(fixture,default):
    state=json.loads(fixture['device'].read_text())
    label='/proc/sys/net/core/default_qdisc'
    if default is None:state['attrs'].pop(label)
    else:state['attrs'][label]=default
    fixture['device'].write_text(json.dumps(state))
    result=fixture['run'](tc_present=False)
    assert result.returncode!=0 and 'FAILED_PRECONDITION' in result.stderr
    assert json.loads(fixture['device'].read_text())['mutations']==0


def device_view(state):
    return {key:state[key] for key in ('attrs','sysctl','qdisc')}


def test_validated_apply_and_idempotent_rollback(fixture):
    first=fixture['run']()
    assert first.returncode==0 and 'APPLIED_VERIFIED' in first.stdout,(first.stdout,first.stderr)
    changed=json.loads(fixture['device'].read_text())
    assert changed['qdisc']['quantum']=='3028' and changed['qdisc']['target']=='2500us'
    assert fixture['snapshot'].is_dir()
    repeat=fixture['run']()
    assert repeat.returncode==0 and 'idempotent=true' in repeat.stdout
    assert json.loads(fixture['device'].read_text())['mutations']==changed['mutations']
    for _ in range(2):
        rollback=fixture['run']('--rollback')
        assert rollback.returncode==0 and 'FAILED_ROLLED_BACK' in rollback.stdout,(rollback.stdout,rollback.stderr)
        assert device_view(json.loads(fixture['device'].read_text()))==device_view(fixture['original'])


@pytest.mark.parametrize('ordinal',range(1,12))
def test_every_mutating_command_failure_restores_snapshot(fixture,ordinal):
    failed=fixture['run'](fail_mutation=ordinal)
    assert failed.returncode!=0 and 'FAILED_ROLLED_BACK' in failed.stdout,(ordinal,failed.stdout,failed.stderr)
    assert 'APPLIED_VERIFIED' not in failed.stdout
    assert device_view(json.loads(fixture['device'].read_text()))==device_view(fixture['original'])


def test_rollback_failure_is_not_success(fixture):
    failed=fixture['run'](fail_mutation=7,rollback_fail=1)
    assert failed.returncode==70 and 'ROLLBACK_FAILED' in failed.stderr
    assert 'APPLIED_VERIFIED' not in failed.stdout


def test_termination_during_mutation_restores_snapshot(fixture):
    failed=fixture['run'](interrupt_mutation=7)
    assert failed.returncode!=0 and 'FAILED_ROLLED_BACK' in failed.stdout,(failed.stdout,failed.stderr)
    assert device_view(json.loads(fixture['device'].read_text()))==device_view(fixture['original'])


def test_missing_identity_cannot_select_a_fallback(fixture):
    fixture['contract'].unlink()
    failed=fixture['run']()
    assert failed.returncode!=0 and 'FAILED_PRECONDITION' in failed.stderr
    assert json.loads(fixture['device'].read_text())['mutations']==0


def test_pktlog_restore_preserves_the_original_numeric_representation(fixture):
    state=json.loads(fixture['device'].read_text())
    label='/sys/kernel/debug/ieee80211/phy1/ath10k/pktlog_filter'
    state['attrs'][label]='0x10';fixture['device'].write_text(json.dumps(state))
    applied=fixture['run']()
    assert applied.returncode==0,(applied.stdout,applied.stderr)
    restored=fixture['run']('--rollback')
    assert restored.returncode==0,(restored.stdout,restored.stderr)
    assert json.loads(fixture['device'].read_text())['attrs'][label]=='0x10'


def test_auto_allocated_qdisc_handle_is_not_claimed_restorable(fixture):
    state=json.loads(fixture['device'].read_text());state['qdisc']['handle']='0:'
    fixture['device'].write_text(json.dumps(state))
    result=fixture['run']()
    assert result.returncode!=0 and 'APPLIED_VERIFIED' not in result.stdout
    assert json.loads(fixture['device'].read_text())['mutations']==0


@pytest.mark.parametrize('setting',['false_readback','getter_error'])
def test_false_or_failed_readback_cannot_approve(fixture,setting):
    failed=fixture['run'](**{setting:1})
    assert failed.returncode!=0 and 'FAILED_ROLLED_BACK' in failed.stdout,(failed.stdout,failed.stderr)
    assert 'APPLIED_VERIFIED' not in failed.stdout
    assert device_view(json.loads(fixture['device'].read_text()))==device_view(fixture['original'])


@pytest.mark.parametrize('field,value',[('board','ubnt,other'),('revision','revB'),('kernel','other'),
    ('driver','ath9k'),('firmware','other'),('phy','phy9'),('radio_ifindex','99'),('egress_ifindex','99')])
def test_wrong_identity_never_mutates(fixture,field,value):
    identity(fixture['contract'],**{field:value})
    failed=fixture['run']()
    assert failed.returncode!=0 and 'APPLIED_VERIFIED' not in failed.stdout
    assert json.loads(fixture['device'].read_text())['mutations']==0


def test_missing_revision_and_unsupported_qdisc_fail_before_mutation(fixture):
    for settings in ({'revision':''},{'unknown_qdisc':' ce_threshold disabled'},{'snapshot_error':1}):
        failed=fixture['run'](**settings)
        assert failed.returncode!=0 and 'APPLIED_VERIFIED' not in failed.stdout
        assert json.loads(fixture['device'].read_text())['mutations']==0


def test_no_dhcp_global_service_or_fake_patch_claims():
    text=HELPER.read_text(encoding='utf-8')
    assert 'uci ' not in text and 'odhcpd' not in text and 'initial_quantum' not in text
    assert '|| true' not in text and 'KIT_OK' not in text
    assert 'target_patch_execution=UNKNOWN' in text


def test_generator_packages_canonical_helper_without_overwriting(tmp_path):
    from tools.firmware import build_stage773a_wa_champion_v13_344window_field_rollout_kit as builder
    dest=tmp_path/builder.HELPER_REL;dest.parent.mkdir(parents=True);dest.write_bytes(HELPER.read_bytes())
    before=dest.read_bytes();report=builder.build(tmp_path)
    assert dest.read_bytes()==before
    assert report['runtime_acceptance']=='UNKNOWN' and report['dhcp_services_changed'] is False
    assert 'verified_metrics' not in report
    assert report['historical_reported_windows']==344
