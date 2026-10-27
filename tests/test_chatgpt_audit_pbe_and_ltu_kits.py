"""Adversarial field-kit checks use disposable command stubs, never devices."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASH = Path('C:/Program Files/Git/bin/bash.exe')
LTU = ROOT / 'firmware/ltu_safe_kit/fmx_ltu_v20_264window_zero_dhcp_kit.sh'
DIRECTORIES = (ROOT / 'firmware/openwrt/pbe5ac_gen2_ptp_kit', ROOT / 'firmware/ltu_safe_kit')
ENGINES = (DIRECTORIES[0] / 'fmx_pbe_lbe_runtime_transaction.sh',
           DIRECTORIES[1] / 'fmx_ltu_runtime_transaction.sh')


def active_entrypoints():
    """Archived release snapshots remain immutable and are excluded from v23 packaging."""
    paths = []
    for directory in DIRECTORIES:
        candidates = list(directory.iterdir())
        if (directory / 'files').exists():
            candidates += list((directory / 'files').rglob('*'))
        for path in candidates:
            if not path.is_file():
                continue
            try:
                with path.open(encoding='utf-8') as stream:
                    first = stream.readline()
            except UnicodeError:
                continue
            if first.startswith('#!') and 'sh' in first:
                paths.append(path)
    return sorted(paths)


def shell_path(path):
    path = Path(path)
    return '/' + path.drive[0].lower() + path.as_posix()[2:]


DRIVER = r'''
import json, os, pathlib, sys
sys.stdout.reconfigure(newline='\n')
tool,args=sys.argv[1],sys.argv[2:]
path=pathlib.Path(os.environ['KIT_DEVICE'])
state=json.loads(path.read_text())
with pathlib.Path(os.environ['KIT_CALLS']).open('a') as stream:stream.write(json.dumps([tool,*args])+'\n')
def persist():path.write_text(json.dumps(state))
def convert(label):
    return label[1].upper()+':'+label[2:] if len(label)>3 and label[0]=='/' and label[2]=='/' else label
def mutate():
    state['mutations']+=1
    if state.get('failed') and os.environ.get('KIT_ROLLBACK_FAIL'):
        persist();sys.exit(17)
    if state['mutations']==int(os.environ.get('KIT_FAIL_WRITE','0')):
        state['failed']=True;persist();sys.exit(17)
def getter(kind):
    if os.environ.get('KIT_FAIL_GETTER')==kind and not state.get('getter_failed') and state['mutations']>=int(os.environ.get('KIT_GETTER_AFTER','0')):
        state['getter_failed']=True;persist();sys.exit(17)
if tool=='id':print('0')
elif tool=='ubus':
    getter('board')
    print(json.dumps({'board_name':state['board'],'board_revision':os.environ.get('KIT_REVISION','revA')}))
elif tool=='jsonfilter':print(json.loads(args[args.index('-s')+1]).get(args[args.index('-e')+1][2:],'') or '')
elif tool=='uname':print('6.6.110')
elif tool=='ethtool':
    getter('driver');print('driver: '+state['driver']+'\nfirmware-version: fixture-fw-v1')
elif tool=='readlink':print('/devices/ieee80211/phy1' if args[-1].endswith('/phy80211') else '/drivers/'+state['driver'])
elif tool=='stat':
    label=args[-1];obj=pathlib.Path(convert(label))
    if not obj.exists():sys.exit(1)
    fmt=args[args.index('-c')+1]
    owner='1000' if os.environ.get('KIT_BAD_OWNER') else '0'
    mode='700' if obj.is_dir() else '600'
    print(fmt.replace('%u',owner).replace('%a',mode).replace('%h',str(obj.stat().st_nlink)))
elif tool=='cat':
    label=args[-1]
    if label.startswith(('/sys/','/proc/')):
        getter('default' if '/proc/' in label else 'sysfs')
        if label not in state['attrs']:sys.exit(1)
        print(state['attrs'][label])
    else:print(pathlib.Path(convert(label)).read_text().rstrip('\n'))
elif tool=='tee':
    label=args[-1];value=sys.stdin.read().strip()
    if label not in state['attrs']:sys.exit(1)
    mutate()
    if not(os.environ.get('KIT_FALSE_SYSFS') and value=='1000'):
        state['attrs'][label]=value
    persist()
elif tool=='sysctl':
    if args[0]=='-n':getter('sysctl');print(state['sysctl'][args[1]])
    else:
        mutate();key,value=args[-1].split('=',1);state['sysctl'][key]=value;persist()
elif tool=='uci':
    verb=next((x for x in args if x in ('get','changes','set','revert','commit')),None)
    if verb in ('get','changes'):
        getter('uci')
        print(state['uci']['value'] if verb=='get' else state['uci']['changes'])
    elif verb=='set':
        mutate();value=args[-1].split('=',1)[1]
        if not os.environ.get('KIT_FALSE_UCI'):
            state['uci']['value']=value;state['uci']['changes']="network.lan.mtu='"+value+"'"
        persist()
    elif verb=='revert':
        mutate();state['uci']['value']=state['uci']['original'];state['uci']['changes']='';persist()
    else:sys.exit(19)
elif tool=='tc':
    if 'show' in args:
        getter('tc');q=state['qdisc']
        print('qdisc fq_codel '+q['handle']+' root refcnt 2 limit '+q['limit']+'p flows '+q['flows']+' quantum '+q['quantum']+' target '+q['target']+' interval '+q['interval']+' memory_limit '+q['memory_limit']+'b drop_batch '+q['drop_batch']+' '+q['ecn'])
    else:
        if 'fq_codel' not in args or 'initial_quantum' in args:sys.exit(18)
        mutate();tokens=args[args.index('fq_codel')+1:];q=dict(state['qdisc'])
        if 'handle' in args:q['handle']=args[args.index('handle')+1]
        while tokens:
            key=tokens.pop(0)
            if key in ('ecn','noecn'):q['ecn']=key
            else:q[key]=tokens.pop(0)
        state['qdisc']=q;persist()
else:sys.exit(19)
'''


def identity(path, family):
    ltu = family == 'LTU'
    fields = dict(board='ubnt,ltu-lite' if ltu else 'ubnt,powerbeam-5ac-gen2', revision='revA',
                  kernel='6.6.110', driver='eab_driver' if ltu else 'ath10k_pci',
                  firmware='fixture-fw-v1', radio='wlan0', phy='none' if ltu else 'phy1',
                  egress='eth0', radio_ifindex='12', egress_ifindex='2')
    fields['fingerprint'] = hashlib.sha256(('\n'.join(fields.values())+'\n').encode()).hexdigest()
    path.write_text(''.join(f'{k}={v}\n' for k,v in fields.items()), newline='\n')
    return fields


@pytest.fixture(params=ENGINES, ids=['PBE', 'LTU'])
def device(request, tmp_path):
    engine = request.param
    family = 'LTU' if 'ltu_safe_kit' in engine.parts else 'PBE'
    bindir = tmp_path / 'bin'; bindir.mkdir()
    driver = tmp_path / 'driver.py'; driver.write_text(DRIVER)
    for tool in ('id','ubus','jsonfilter','uname','ethtool','readlink','stat','cat','tee','tc','sysctl','uci'):
        (bindir/tool).write_text(f'#!/bin/sh\nexec "{Path(sys.executable).as_posix()}" "{driver.as_posix()}" {tool} "$@"\n',newline='\n')
    for tool in ('sh','awk','sha256sum','mkdir','rmdir','mv'):
        (bindir/tool).write_text(f'#!/bin/sh\nexec /usr/bin/{tool} "$@"\n',newline='\n')
    contract = tmp_path / 'identity'; fields=identity(contract,family)
    state = dict(board=fields['board'], driver=fields['driver'], mutations=0,
        attrs={'/sys/class/net/wlan0/ifindex':'12','/sys/class/net/eth0/ifindex':'2',
               '/sys/class/net/eth0/tx_queue_len':'42','/proc/sys/net/core/default_qdisc':'fq_codel'},
        sysctl={'net.core.netdev_max_backlog':'2000'},
        uci={'value':'1400','original':'1400','changes':''},
        qdisc=dict(handle='8001:',limit='4096',flows='512',quantum='1200',target='1000us',
                   interval='100000us',memory_limit='33554432',drop_batch='64',ecn='noecn'))
    statefile=tmp_path/'device.json';statefile.write_text(json.dumps(state))
    snapshot=tmp_path/'snapshot'
    def run(mode='--apply', *, tc_present=True, qdisc_mode=None, uci_mode=None, **settings):
        if not tc_present and (bindir/'tc').exists():(bindir/'tc').unlink()
        options=[]
        if qdisc_mode:options+=['--qdisc-mode',qdisc_mode]
        if uci_mode:options+=['--uci-mode',uci_mode]
        env=dict(os.environ,KIT_DEVICE=str(statefile),KIT_CALLS=str(tmp_path/'calls.jsonl'),MSYS2_ARG_CONV_EXCL='*')
        env.update({'KIT_'+k.upper():str(v) for k,v in settings.items()})
        command=f'PATH="{shell_path(bindir)}"; export PATH; exec sh "$1" "$2" --identity "$3" --state-dir "$4"'
        command+=''.join(' "${'+str(n)+'}"' for n in range(5,5+len(options)))
        return subprocess.run([str(BASH),'-c',command,'fixture',engine.as_posix(),mode,
                               shell_path(contract),shell_path(snapshot),*options],env=env,
                              capture_output=True,text=True,timeout=40)
    return dict(run=run,statefile=statefile,snapshot=snapshot,contract=contract,original=state,
                calls=tmp_path/'calls.jsonl',engine=engine,tmp=tmp_path)


def view(state):
    return {k:state[k] for k in ('attrs','sysctl','qdisc','uci')}


@pytest.mark.parametrize('tc_present', [True, False])
def test_both_families_apply_verify_and_restore(device, tc_present):
    result=device['run'](tc_present=tc_present)
    assert result.returncode==0,(result.stdout,result.stderr)
    assert 'APPLIED_VERIFIED' in result.stdout
    changed=json.loads(device['statefile'].read_text())
    assert changed['attrs']['/sys/class/net/eth0/tx_queue_len']=='1000'
    assert changed['sysctl']['net.core.netdev_max_backlog']=='1000'
    checked=device['run']('--verify',tc_present=tc_present)
    assert checked.returncode==0,(checked.stdout,checked.stderr)
    assert json.loads(device['statefile'].read_text())['mutations']==changed['mutations']
    restored=device['run']('--rollback',tc_present=tc_present)
    assert restored.returncode==0,(restored.stdout,restored.stderr)
    assert view(json.loads(device['statefile'].read_text()))==view(device['original'])
    if not tc_present:
        assert 'kernel_default_fq_codel' in result.stdout and 'active_qdisc=UNKNOWN' in result.stdout
        assert not any(json.loads(line)[0]=='tc' for line in device['calls'].read_text().splitlines())


@pytest.mark.parametrize('default', ['pfifo_fast',None])
def test_missing_tc_and_missing_or_wrong_kernel_default_rejected(device,default):
    state=json.loads(device['statefile'].read_text())
    label='/proc/sys/net/core/default_qdisc'
    if default is None:state['attrs'].pop(label)
    else:state['attrs'][label]=default
    device['statefile'].write_text(json.dumps(state))
    result=device['run'](tc_present=False)
    assert result.returncode!=0 and 'APPLIED_VERIFIED' not in result.stdout
    assert json.loads(device['statefile'].read_text())['mutations']==0


@pytest.mark.parametrize('ordinal',[1,2,3])
def test_every_tc_mutating_failure_rolls_back(device,ordinal):
    result=device['run'](fail_write=ordinal)
    assert result.returncode!=0 and 'FAILED_ROLLED_BACK' in result.stdout,(result.stdout,result.stderr)
    assert view(json.loads(device['statefile'].read_text()))==view(device['original'])


@pytest.mark.parametrize('ordinal',[1,2])
def test_every_tcless_mutating_failure_rolls_back(device,ordinal):
    result=device['run'](tc_present=False,fail_write=ordinal)
    assert result.returncode!=0 and 'FAILED_ROLLED_BACK' in result.stdout,(result.stdout,result.stderr)
    assert view(json.loads(device['statefile'].read_text()))==view(device['original'])


def test_failed_restoration_is_never_success(device):
    result=device['run'](fail_write=2,rollback_fail=1)
    assert result.returncode!=0 and 'ROLLBACK_FAILED' in result.stderr,(result.stdout,result.stderr)
    assert 'APPLIED_VERIFIED' not in result.stdout


@pytest.mark.parametrize('kind',['tc','sysfs','sysctl'])
def test_failed_snapshot_getters_never_mutate(device,kind):
    result=device['run'](fail_getter=kind)
    assert result.returncode!=0 and 'APPLIED_VERIFIED' not in result.stdout
    assert json.loads(device['statefile'].read_text())['mutations']==0


def test_false_sysfs_readback_cannot_be_accepted(device):
    result=device['run'](false_sysfs=1)
    assert result.returncode!=0 and 'FAILED_ROLLED_BACK' in result.stdout,(result.stdout,result.stderr)
    assert view(json.loads(device['statefile'].read_text()))==view(device['original'])


def test_real_verify_detects_sysfs_drift_without_writes(device):
    assert device['run']().returncode==0
    state=json.loads(device['statefile'].read_text());state['attrs']['/sys/class/net/eth0/tx_queue_len']='7'
    device['statefile'].write_text(json.dumps(state))
    result=device['run']('--verify')
    assert result.returncode!=0 and 'APPLIED_VERIFIED' not in result.stdout
    assert json.loads(device['statefile'].read_text())['mutations']==state['mutations']


def test_ram_uci_is_read_back_and_reverted_without_commit(device):
    result=device['run'](uci_mode='ram')
    assert result.returncode==0,(result.stdout,result.stderr)
    state=json.loads(device['statefile'].read_text())
    assert state['uci']['value']=='1500'
    assert device['run']('--verify',uci_mode='ram').returncode==0
    assert device['run']('--rollback',uci_mode='ram').returncode==0
    assert view(json.loads(device['statefile'].read_text()))==view(device['original'])
    assert not any(row[0]=='uci' and 'commit' in row for row in
                   map(json.loads,device['calls'].read_text().splitlines()))


def test_false_uci_readback_cannot_be_accepted(device):
    result=device['run'](uci_mode='ram',false_uci=1)
    assert result.returncode!=0 and 'FAILED_ROLLED_BACK' in result.stdout,(result.stdout,result.stderr)
    assert view(json.loads(device['statefile'].read_text()))==view(device['original'])


def test_uci_dirty_cache_is_not_overwritten(device):
    state=json.loads(device['statefile'].read_text())
    state['uci']['changes']="network.other.mtu='1400'"
    device['statefile'].write_text(json.dumps(state))
    result=device['run'](uci_mode='ram')
    assert result.returncode!=0
    assert json.loads(device['statefile'].read_text())['mutations']==0


@pytest.mark.parametrize('tc_present,ordinal', [(True,4),(False,3)])
def test_failed_uci_write_restores_earlier_knobs(device,tc_present,ordinal):
    result=device['run'](uci_mode='ram',tc_present=tc_present,fail_write=ordinal)
    assert result.returncode!=0 and 'FAILED_ROLLED_BACK' in result.stdout,(result.stdout,result.stderr)
    assert view(json.loads(device['statefile'].read_text()))==view(device['original'])


def test_failed_post_apply_tc_getter_is_not_masked(device):
    result=device['run'](fail_getter='tc',getter_after=3)
    assert result.returncode!=0 and 'FAILED_ROLLED_BACK' in result.stdout,(result.stdout,result.stderr)
    assert view(json.loads(device['statefile'].read_text()))==view(device['original'])


def test_explicit_tc_requires_binary_without_policy_fallback(device):
    result=device['run'](qdisc_mode='tc',tc_present=False)
    assert result.returncode!=0 and 'tc backend unavailable' in result.stderr
    assert json.loads(device['statefile'].read_text())['mutations']==0


def test_selected_backend_cannot_be_changed_by_verify(device):
    applied=device['run'](qdisc_mode='sysfs-default')
    assert applied.returncode==0,(applied.stdout,applied.stderr)
    before=json.loads(device['statefile'].read_text())
    failed=device['run']('--verify',qdisc_mode='tc')
    assert failed.returncode!=0 and 'backend mismatch' in failed.stderr
    assert json.loads(device['statefile'].read_text())['mutations']==before['mutations']


def test_ltu_default_does_not_claim_mutation_or_hardware_acceptance(tmp_path):
    result = subprocess.run([str(BASH), '-c', 'exec sh "$1"', 'fixture', str(LTU)],
                            env=dict(os.environ), capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, (result.stdout, result.stderr)
    assert 'PLANNED' in result.stdout
    assert 'br1_dhcp_disabled=1' not in result.stdout
    assert 'RTT' not in result.stdout


@pytest.mark.parametrize('entrypoint', active_entrypoints(), ids=lambda p:p.relative_to(ROOT).as_posix())
def test_every_active_entrypoint_defaults_to_no_device_commands(tmp_path, entrypoint):
    bindir=tmp_path/'bin';bindir.mkdir()
    log=tmp_path/'calls.txt'
    for tool in ('uci','tc','sysctl','ubus','cat','tee','ip','iw','iwpriv','iptables','ebtables',
                 'reboot','mtd','cfgmtd','sysupgrade','rmmod','insmod','devmem','ethtool'):
        (bindir/tool).write_text('#!/bin/sh\nprintf "%s\\n" "$0 $*" >> "$KIT_CALLS"\nexit 77\n',newline='\n')
    command=f'PATH="{shell_path(bindir)}:$PATH"; export PATH; exec sh "$1"'
    result=subprocess.run([str(BASH),'-c',command,'fixture',entrypoint.as_posix()],
        env=dict(os.environ,KIT_CALLS=log.as_posix()),capture_output=True,text=True,timeout=10)
    assert result.returncode==0 and 'PLANNED' in result.stdout,(entrypoint,result.stdout,result.stderr)
    assert 'APPLIED_VERIFIED' not in result.stdout
    assert not log.exists(), (entrypoint,log.read_text() if log.exists() else '')


@pytest.mark.parametrize('entrypoint',[p for p in active_entrypoints() if p not in ENGINES],
                         ids=lambda p:p.relative_to(ROOT).as_posix())
def test_retired_unsafe_actuators_cannot_be_enabled_by_apply(tmp_path, entrypoint):
    result=subprocess.run([str(BASH),'-c','exec sh "$1" --apply','fixture',entrypoint.as_posix()],
                           capture_output=True,text=True,timeout=10)
    assert result.returncode!=0 and 'APPLIED_VERIFIED' not in result.stdout,(entrypoint,result.stdout,result.stderr)


def test_identity_revision_is_mandatory_and_matches_native_readback(device):
    result=device['run'](revision='')
    assert result.returncode!=0 and 'APPLIED_VERIFIED' not in result.stdout
    assert json.loads(device['statefile'].read_text())['mutations']==0


def test_missing_identity_never_uses_profile_fallback(device):
    device['contract'].unlink()
    result=device['run']()
    assert result.returncode!=0
    assert json.loads(device['statefile'].read_text())['mutations']==0


def test_hardlinked_snapshot_file_is_rejected_before_rollback(device):
    result=device['run']()
    assert result.returncode==0,(result.stdout,result.stderr)
    existing=device['snapshot']/'tx_queue_len'
    backup=device['tmp']/'external-linked-value'
    backup.hardlink_to(existing)
    state=json.loads(device['statefile'].read_text())
    result=device['run']('--rollback')
    assert result.returncode!=0 and 'APPLIED_VERIFIED' not in result.stdout
    assert json.loads(device['statefile'].read_text())['mutations']==state['mutations']


def test_preexisting_phase_hardlink_cannot_overwrite_an_unrelated_file(device):
    result=device['run']()
    assert result.returncode==0,(result.stdout,result.stderr)
    victim=device['tmp']/'victim.txt';victim.write_text('UNCHANGED')
    (device['snapshot']/'phase.tmp').hardlink_to(victim)
    state=json.loads(device['statefile'].read_text())
    result=device['run']('--rollback')
    assert result.returncode!=0 and victim.read_text()=='UNCHANGED'
    assert json.loads(device['statefile'].read_text())['mutations']==state['mutations']


def test_wrong_snapshot_owner_is_rejected(device):
    assert device['run']().returncode==0
    state=json.loads(device['statefile'].read_text())
    result=device['run']('--verify',bad_owner=1)
    assert result.returncode!=0
    assert json.loads(device['statefile'].read_text())['mutations']==state['mutations']
