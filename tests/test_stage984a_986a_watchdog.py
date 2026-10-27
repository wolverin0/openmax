"""Watchdog deadlines and rollback faults use local command stubs only."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_rollback_watchdog.sh'
BASH = Path('C:/Program Files/Git/bin/bash.exe')


def shell_path(path):
    path = Path(path)
    return '/' + path.drive[0].lower() + path.as_posix()[2:]


DRIVER = r'''
import json,os,pathlib,sys,subprocess
sys.stdout.reconfigure(newline='\n')
tool,args=sys.argv[1],sys.argv[2:]
path=pathlib.Path(os.environ['WATCH_DEVICE'])
s=json.loads(path.read_text())
def persist():path.write_text(json.dumps(s))
def convert(label):
    if len(label)>3 and label[0]=='/' and label[2]=='/':return label[1].upper()+':'+label[2:]
    return label
s['calls'].append([tool,*args]);persist()
if tool=='id':print('0')
elif tool=='stat':
    p=pathlib.Path(convert(args[-1]));actual=p.stat()
    mode='700' if p.is_dir() else ('755' if p.name.endswith('.sh') else '600')
    owner='1001' if s.get('bad_owner') else '0'
    print(owner+':'+mode+(':'+str(actual.st_nlink) if args[1]=='%u:%a:%h' else ''))
elif tool=='cat':
    if args[-1]=='/proc/uptime':
        if s.get('clock_error') and s['now']>0:sys.exit(3)
        now=s['now']
        if s.get('clock_regression') and now>0:now=-1
        print(str(now)+'.00 0.00')
    else:print(pathlib.Path(convert(args[-1])).read_text().rstrip('\n'))
elif tool=='ping':
    s['probes'].append(s['now'])
    s['now']+=s.get('ping_duration',0);persist()
    if s.get('signal_on_ping'):
        subprocess.run(['C:/Program Files/Git/bin/bash.exe','-c','kill -TERM "$WATCH_SHELL_PID"'],check=True)
    if s.get('late_verify_duration'):s['after_ping']=True;persist()
    if s.get('ping_error'):sys.exit(2)
    sys.exit(0 if s['healthy_at'] is not None and s['now']>=s['healthy_at'] else 1)
elif tool=='sleep':
    if s.get('sleep_error'):sys.exit(3)
    if not s.get('clock_stalled'):s['now']+=int(args[0])
    persist()
elif tool in ('mkdir','mv'):
    target=pathlib.Path(convert(args[-1]))
    watch_action=tool=='mkdir' and target.name=='watch-state'
    if watch_action and s.get('arming_fail')=='mkdir':sys.exit(28)
    if tool=='mv' and s.get('arming_fail')=='phase_move':sys.exit(28)
    result=subprocess.run(['C:/Program Files/Git/bin/bash.exe','-c','exec /usr/bin/'+tool+' "$@"',tool,*args])
    if result.returncode:sys.exit(result.returncode)
    if watch_action:
        field=s.get('arming_fail')
        if field and field not in ('mkdir','phase_move'):(target/field).mkdir()
        if s.get('signal_on_watch_mkdir'):
            subprocess.run(['C:/Program Files/Git/bin/bash.exe','-c','kill -TERM "$WATCH_SHELL_PID"'],check=True)
    sys.exit(0)
elif tool=='transaction':
    if '--verify' in args:
        if s.get('signal_on_native_verify') and not s.get('verify_signal_sent'):
            s['verify_signal_sent']=True;persist()
            subprocess.run(['C:/Program Files/Git/bin/bash.exe','-c','kill -TERM "$WATCH_SHELL_PID"'],check=True)
        if s.get('after_ping'):s['now']+=s['late_verify_duration'];persist()
        if not s.get('identity_ok',True) or s.get('verify_error'):sys.exit(65)
        print('APPLIED_VERIFIED qdisc_backend=kernel_default_fq_codel hardware_acceptance=UNKNOWN')
    elif '--rollback' in args:
        s['rollback_calls']+=1;persist()
        if s.get('rollback_error'):sys.exit(70)
        if s.get('rollback_false_readback'):print('ROLLED_BACK unverified=true')
        else:print('FAILED_ROLLED_BACK readback=verified')
    else:sys.exit(64)
else:sys.exit(19)
'''


@pytest.fixture
def watchdog(tmp_path):
    bindir=tmp_path/'bin';bindir.mkdir()
    driver=tmp_path/'driver.py';driver.write_text(DRIVER,encoding='utf-8')
    target=tmp_path/'fmx_ptp_rollback_watchdog.sh';target.write_bytes(SOURCE.read_bytes())
    for tool in ('id','stat','cat','ping','sleep','mkdir','mv'):
        (bindir/tool).write_text(f'#!/bin/sh\nexec "{Path(sys.executable).as_posix()}" "{driver.as_posix()}" {tool} "$@"\n',encoding='utf-8',newline='\n')
    for tool in ('sh','awk','sha256sum','rmdir'):
        (bindir/tool).write_text(f'#!/bin/sh\nexec /usr/bin/{tool} "$@"\n',encoding='utf-8',newline='\n')
    transaction=tmp_path/'fmx_pbe_lbe_runtime_transaction.sh'
    transaction.write_text(f'#!/bin/sh\nexec "{Path(sys.executable).as_posix()}" "{driver.as_posix()}" transaction "$@"\n',encoding='utf-8',newline='\n')
    identity=tmp_path/'identity';identity.write_text('fixture exact identity delegated to reviewed transaction\n')
    native=tmp_path/'native-state';native.mkdir()
    watch=tmp_path/'watch-state'
    state={'now':0,'healthy_at':None,'identity_ok':True,'calls':[],'probes':[],'rollback_calls':0}
    device=tmp_path/'device.json';device.write_text(json.dumps(state))
    expected_hash=hashlib.sha256(transaction.read_bytes()).hexdigest()
    def run(mode='--apply',channel='non-dfs',include_args=True,**settings):
        current=json.loads(device.read_text());current.update(settings);device.write_text(json.dumps(current))
        args=([mode] if mode else [])
        if include_args:
            args += ['--identity',shell_path(identity),'--state-dir',shell_path(native),
                     '--watch-state-dir',shell_path(watch),'--peer','benchmark-peer',
                     '--channel-class',channel,'--transaction-sha256',expected_hash,'--qdisc-mode','auto']
        command='PATH="'+shell_path(bindir)+'"; export PATH; WATCH_SHELL_PID=$$; export WATCH_SHELL_PID; exec sh "'+shell_path(target)+'" '+ ' '.join('"'+x+'"' for x in args)
        return subprocess.run([str(BASH),'-c',command],env=dict(os.environ,WATCH_DEVICE=str(device),MSYS2_ARG_CONV_EXCL='*'),capture_output=True,text=True,timeout=45)
    return dict(run=run,device=device,watch=watch,transaction=transaction,identity=identity,tmp=tmp_path)


@pytest.mark.parametrize('mode',['','--dry-run','--inspect-only'])
def test_inspection_performs_no_getters(watchdog,mode):
    result=watchdog['run'](mode,include_args=False)
    assert result.returncode==0 and 'PLANNED' in result.stdout
    assert not json.loads(watchdog['device'].read_text())['calls']


@pytest.mark.parametrize('channel,budget',[('non-dfs',45),('dfs',120)])
def test_link_loss_reaches_exact_declared_deadline_then_verified_rollback(watchdog,channel,budget):
    result=watchdog['run'](channel=channel)
    assert result.returncode==2 and 'TIMEOUT_ROLLED_BACK' in result.stdout,(result.stdout,result.stderr)
    state=json.loads(watchdog['device'].read_text())
    assert state['now']==budget and state['rollback_calls']==1
    assert max(state['probes'])<budget
    assert (watchdog['watch']/'phase').read_text().strip()=='TIMEOUT_ROLLED_BACK'


def test_healthy_probe_verifies_native_state_without_rollback(watchdog):
    result=watchdog['run'](healthy_at=10)
    assert result.returncode==0 and 'WATCHDOG_HEALTHY_VERIFIED' in result.stdout,(result.stdout,result.stderr)
    state=json.loads(watchdog['device'].read_text())
    assert state['now']==10 and state['rollback_calls']==0
    checked=watchdog['run']('--verify')
    assert checked.returncode==0 and 'WATCHDOG_HEALTHY_VERIFIED' in checked.stdout


@pytest.mark.parametrize('fault',['clock_error','clock_regression','clock_stalled','sleep_error','ping_error'])
def test_armed_observation_failure_attempts_verified_restore(watchdog,fault):
    result=watchdog['run'](**{fault:True})
    assert result.returncode!=0 and 'FAILED_ROLLED_BACK' in result.stdout,(fault,result.stdout,result.stderr)
    assert json.loads(watchdog['device'].read_text())['rollback_calls']==1


@pytest.mark.parametrize('fault',['rollback_error','rollback_false_readback'])
def test_failed_or_unverified_restoration_is_not_safe(watchdog,fault):
    result=watchdog['run'](**{fault:True})
    assert result.returncode==70 and 'ROLLBACK_FAILED' in result.stderr
    assert 'TIMEOUT_ROLLED_BACK' not in result.stdout


def test_unknown_channel_class_and_invalid_identity_never_arm(watchdog):
    result=watchdog['run'](channel='unknown')
    assert result.returncode!=0
    assert not json.loads(watchdog['device'].read_text())['probes']
    result=watchdog['run'](identity_ok=False)
    assert result.returncode!=0
    assert json.loads(watchdog['device'].read_text())['rollback_calls']==0


def test_transaction_hash_change_is_rejected_before_arming(watchdog):
    watchdog['transaction'].write_bytes(watchdog['transaction'].read_bytes()+b'# changed\n')
    result=watchdog['run']()
    assert result.returncode!=0
    assert not json.loads(watchdog['device'].read_text())['probes']


def test_rolled_back_verify_does_not_mutate_again(watchdog):
    assert watchdog['run']().returncode==2
    before=json.loads(watchdog['device'].read_text())['rollback_calls']
    result=watchdog['run']('--verify')
    assert result.returncode!=0 and 'restored_state_requires_separate_baseline_audit' in result.stderr
    assert json.loads(watchdog['device'].read_text())['rollback_calls']==before


def test_probe_elapsed_time_is_included_in_deadline(watchdog):
    result=watchdog['run'](ping_duration=3)
    assert result.returncode==2 and 'TIMEOUT_ROLLED_BACK' in result.stdout,(result.stdout,result.stderr)
    assert json.loads(watchdog['device'].read_text())['now']==45


@pytest.mark.parametrize('settings', [dict(healthy_at=0,ping_duration=45),
                                     dict(healthy_at=0,late_verify_duration=45)])
def test_late_probe_or_native_verify_cannot_disarm_after_deadline(watchdog,settings):
    result=watchdog['run'](**settings)
    assert result.returncode==2 and 'TIMEOUT_ROLLED_BACK' in result.stdout,(result.stdout,result.stderr)
    assert json.loads(watchdog['device'].read_text())['rollback_calls']==1


def test_signal_after_arming_attempts_verified_restore(watchdog):
    result=watchdog['run'](signal_on_ping=True)
    assert result.returncode!=0 and 'FAILED_ROLLED_BACK' in result.stdout,(result.stdout,result.stderr)
    assert json.loads(watchdog['device'].read_text())['rollback_calls']==1


def test_watch_snapshot_hardlink_temporary_is_never_followed(watchdog):
    assert watchdog['run'](healthy_at=0).returncode==0
    victim=watchdog['tmp']/'victim.txt';victim.write_text('UNCHANGED\n')
    (watchdog['watch']/'phase.tmp').hardlink_to(victim)
    result=watchdog['run']('--verify')
    assert result.returncode!=0 and victim.read_text()=='UNCHANGED\n'


def test_deadline_cannot_be_rearmed_by_reusing_watch_state(watchdog):
    assert watchdog['run'](healthy_at=0).returncode==0
    before=json.loads(watchdog['device'].read_text())
    result=watchdog['run']()
    assert result.returncode!=0 and 'cannot restart its deadline' in result.stderr
    assert json.loads(watchdog['device'].read_text())['probes']==before['probes']


@pytest.mark.parametrize('fault',['mkdir','identity_sha','transaction_sha','native_state','peer',
                                  'channel','budget','qdisc_mode','uci_mode','phase.tmp',
                                  'phase_move','start_ms'])
def test_arming_io_failure_restores_already_verified_candidate(watchdog,fault):
    result=watchdog['run'](arming_fail=fault)
    state=json.loads(watchdog['device'].read_text())
    assert result.returncode!=0 and state['rollback_calls']==1,(fault,result.stdout,result.stderr,state)
    assert 'FAILED_ROLLED_BACK' in result.stdout
    assert not state['probes']
    if fault in ('mkdir','phase.tmp','phase_move'):
        assert 'WATCHDOG_STATE_RECORD_FAILED' in result.stderr
        assert 'ROLLBACK_FAILED reason=' not in result.stderr


def test_signal_before_first_state_write_restores_verified_candidate(watchdog):
    result=watchdog['run'](signal_on_watch_mkdir=True)
    state=json.loads(watchdog['device'].read_text())
    assert result.returncode!=0 and state['rollback_calls']==1,(result.stdout,result.stderr,state)
    assert not state['probes'] and 'FAILED_ROLLED_BACK' in result.stdout


@pytest.mark.parametrize('fault',['rollback_error','rollback_false_readback'])
def test_arming_io_failure_reports_unverified_restore_separately(watchdog,fault):
    result=watchdog['run'](arming_fail='mkdir',**{fault:True})
    state=json.loads(watchdog['device'].read_text())
    assert state['rollback_calls']==1 and result.returncode==70,(result.stdout,result.stderr,state)
    assert 'ROLLBACK_FAILED reason=' in result.stderr
    assert 'WATCHDOG_STATE_RECORD_FAILED' in result.stderr


@pytest.mark.parametrize('identity_ok',[True,False])
def test_signal_during_native_readback_defers_until_authority_is_known(watchdog,identity_ok):
    result=watchdog['run'](signal_on_native_verify=True,identity_ok=identity_ok)
    state=json.loads(watchdog['device'].read_text())
    assert result.returncode!=0 and not state['probes'],(result.stdout,result.stderr,state)
    assert state['rollback_calls']==int(identity_ok),(result.stdout,result.stderr,state)
    if identity_ok:assert 'FAILED_ROLLED_BACK' in result.stdout
