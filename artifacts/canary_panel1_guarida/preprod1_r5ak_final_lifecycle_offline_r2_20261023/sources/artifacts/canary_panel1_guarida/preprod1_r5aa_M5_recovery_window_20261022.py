"""Guarded Ethernet-only closure of AA's own M5 guard; AP radio stays off."""
import importlib.util
import hashlib
import json
from pathlib import Path
import re
import shlex
import sys
import threading
import time
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location('_aa_m5_' + name[:-3], HERE/name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def connect_before_deadline(access, ap, pin, end, address=None):
    """Close only the new forwarding socket, including auth/identity waits."""
    expired=threading.Event()
    owned=[]
    def expire():
        expired.set()
        for channel in owned:
            channel.close()
    def open_owned(*args,**kwargs):
        remaining=end-time.monotonic()
        access.require(remaining>0 and not expired.is_set(),'M5_CONNECT_DEADLINE')
        kwargs['timeout']=min(kwargs.get('timeout',8),remaining)
        channel=ap.get_transport().open_channel(*args,**kwargs)
        owned.append(channel)
        if expired.is_set() or time.monotonic()>=end:
            channel.close()
            raise RuntimeError('M5_CONNECT_DEADLINE')
        return channel
    proxy=SimpleNamespace(get_transport=lambda:SimpleNamespace(open_channel=open_owned))
    remaining=end-time.monotonic()
    access.require(remaining>0,'M5_CONNECT_DEADLINE')
    timer=threading.Timer(remaining,expire)
    timer.daemon=True
    timer.start()
    client=None
    try:
        client,pin=access.connect_legacy(proxy,'LBM5',pin,address_override=address)
        access.require(not expired.is_set() and time.monotonic()<end,'M5_CONNECT_DEADLINE')
        return client,pin
    except BaseException:
        if client:
            try:client.close()
            except Exception:pass
        for channel in owned:
            channel.close()
        if expired.is_set() or time.monotonic()>=end:
            raise RuntimeError('M5_CONNECT_DEADLINE')
        raise
    finally:
        timer.cancel()


def guard_identity(raw):
    fields=raw.split()
    if len(fields)!=2 or any(not re.fullmatch(r'[1-9][0-9]*',x) for x in fields):
        raise RuntimeError('M5_GUARD_ID_PROTOCOL')
    return fields


def guard_native_md5(text, expected_sha):
    body=text.encode('ascii')
    if len(body)>8192 or hashlib.sha256(body).hexdigest()!=expected_sha:
        raise RuntimeError('M5_GUARD_LOCAL_SHA256_MISMATCH')
    return hashlib.md5(body).hexdigest()


def main():
    support = load('preprod1_r5aa_abort_restore_20261022.py')
    remote, require, sha = support.remote, support.require, support.sha
    out = HERE/'preprod1_r5aa_M5_ethernet_source_check_20261022.json'
    require(not out.exists(), 'SINGLE_RESTORE_CHECK_ALREADY_USED')
    source = Path(__file__).read_bytes()
    record = dict(status='INCOMPLETE_M5_RECOVERY_CHECK', started_utc=support.utc(),
                  mode='ETHERNET_ONLY_AP_RADIO_OFF',
                  source_sha256=sha(source), parent='FMX0017/PREPROD1 AA exact restoration',
                  changed_evidence='Operator connected M5 Ethernet; its held route to192.168.1.0/24 uses AP10.99.0.1. Restore only that guarded temporary alias, no RF.',
                  alias_guard_deadline_s=180, management_acquisition_s=90, production_access=False,
                  IE_or_daemon_or_CPE_treatment=False, observations=[], errors=[])
    rec = json.loads((support.RUN/'receipt.json').read_text(encoding='utf8'))
    g = rec['legacy_guards']['LBM5']
    intake = json.loads((HERE/'root_four_cpe_intake_20261022_run1/receipt.json').read_text(encoding='utf8'))
    access = load('root_four_cpe_access_20261022.py')
    access.remote = remote
    helper = access.ap_helper()
    helper.TTL = 180
    helper.checked = lambda c, cmd, timeout=25: remote(c,cmd,timeout=timeout)['stdout'].encode()
    original_guard = helper.guard_body
    helper.guard_body = lambda: original_guard().replace('+480))','+180))')
    record['guard_source_sha256'] = sha(helper.guard_body().encode())
    record['restore_source_sha256'] = sha(helper.restore_body().encode())
    ap = c = None
    armed = False
    tables_before = network_before = None

    def save():
        temp=out.with_suffix('.pending')
        temp.write_text(json.dumps(record,indent=2),encoding='utf8')
        temp.replace(out)

    try:
        save()
        ap = access.load('root_goal_direct_link_connection_20261022.py').ap_client()
        record['AP_before'] = helper.off(ap)
        tables_before = remote(ap,'nft list tables')['stdout']
        network_before = remote(ap,'ip -4 addr show dev br-lan; ip route')['stdout']
        record['AP_network_before'] = network_before
        # Install the proven rollback program without calling helper.arm():
        # only the management alias is added, with wireless UCI left untouched.
        armed = True
        remote(ap,helper.prepare())
        for _ in range(4):
            try:
                guard=helper.guard_identity(ap)
                break
            except RuntimeError:
                time.sleep(.5)
        else:
            raise RuntimeError('ALIAS_GUARD_NOT_READY_NO_ADDRESS_ADDED')
        record['AP_guard_identity']=dict(pid=guard[0],start_ticks=guard[1],deadline_uptime=guard[2])
        remote(ap,'set -eu\n'+helper.header()+helper.file_guards()+
               'test ! -f "$D/restored"\nip addr add 10.99.0.1/24 dev br-lan\n')
        record['AP_alias_ready_radio_off']=helper.off(ap)
        save()
        end=time.monotonic()+90
        while time.monotonic()<end:
            probe=remote(ap,'ping -c 1 -W 1 -I br-lan 10.99.0.4',timeout=3,check=False)
            record['observations'].append(dict(mono=time.monotonic(),ping_exit=probe['exit_code']))
            save()
            if probe['exit_code'] != 0:
                time.sleep(1)
                continue
            try:
                c,_ = connect_before_deadline(access,ap,intake['devices']['LBM5']['pin'],end)
                break
            except Exception as error:
                record['last_connect_error'] = dict(type=type(error).__name__,gate=str(error)[:100])
                if time.monotonic()<end:
                    try:
                        c,_ = connect_before_deadline(access,ap,intake['devices']['LBM5']['pin'],end,'192.168.1.5')
                        record['pinned_management_fallback']='192.168.1.5'
                        break
                    except Exception as fallback_error:
                        record['last_fallback_error']=dict(type=type(fallback_error).__name__,gate=str(fallback_error)[:100])
        require(c is not None, 'M5_PINNED_SSH_NOT_REACQUIRED')
        cmd='cat /proc/sys/kernel/random/boot_id; md5sum /tmp/system.cfg /dev/mtd0 /dev/mtd1 /dev/mtd4 /dev/mtd5; ip -4 addr; ip route; brctl show; iwconfig ath0; iwpriv ath0 get_authmode; iwpriv ath0 get_wds'
        snapshot=remote(c,cmd,timeout=20)['stdout']
        record['M5_snapshot']=snapshot
        before=rec['legacy_baselines']['LBM5']
        require(snapshot.splitlines()[0]==before.splitlines()[0],'M5_BOOT_CHANGED')
        hashes=lambda t:re.findall(r'(?m)^([0-9a-f]{32,64})\s+(/\S+)$',t)
        require(hashes(snapshot)==hashes(before),'M5_HASH_CHANGED')
        network=lambda t:dict(addresses=re.findall(r'(?m)^\s+inet ([^\n]+)',t),
            routes=[x for x in t.splitlines() if re.match(r'^(default |[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(?:/[0-9]+)? (?:dev|via) )',x)])
        require(network(snapshot)==network(before),'M5_NETWORK_CHANGED')
        require('Encryption key:off' in snapshot and 'get_authmode:1' in snapshot and 'get_wds:0' in snapshot,'M5_NOT_OPEN_RESTORED')
        d=shlex.quote(g['directory'])
        raw=remote(c,'set -eu\nD='+d+'\ntest ! -L "$D"\ntest ! -L "$D/guard.sh"\ncat "$D/guard.sh"\n',limit=8192)['stdout']
        native_md5=guard_native_md5(raw,g['source_sha256'])
        record['M5_guard_source_local_verification']=dict(bytes=len(raw.encode('ascii')),
            sha256=sha(raw.encode('ascii')),native_md5=native_md5,
            note='Exact own guard bytes verified locally because this airOS has md5sum but no sha256sum; source SHA criterion unchanged.')
        cmd=('set -eu\nD='+d+'\ntest ! -L "$D"\ntest ! -L "$D/guard.sh"\n'
             'test "$(md5sum "$D/guard.sh" | cut -d\' \' -f1)" = '+native_md5+'\n'
             'test ! -L "$D/guard.id"\ntest -f "$D/restored"\ntest "$(cat "$D/restore.rc")" = 0\ncat "$D/guard.id"\n')
        pid,ticks=guard_identity(remote(c,cmd)['stdout'])
        cmd=('set -eu\nD='+d+'\ntest ! -L "$D"\ntest ! -L "$D/guard.sh"\n'
             'test "$(md5sum "$D/guard.sh" | cut -d\' \' -f1)" = '+native_md5+'\n'
             'test ! -L "$D/guard.id"\ntest "$(cat "$D/guard.id")" = "'+pid+' '+ticks+'"\n'
             'test -f "$D/restored"\ntest "$(cat "$D/restore.rc")" = 0\n'
             'if test -r /proc/'+pid+'/stat && test "$(awk \'{print $22}\' /proc/'+pid+'/stat)" = '+ticks+' && test "$(awk \'{print $3}\' /proc/'+pid+'/stat)" != Z; then exit 79; fi\n'
             'echo M5_GUARD_ENDED\n')
        record['M5_guard_ended']=dict(pid=int(pid),start_ticks=int(ticks),evidence=remote(c,cmd))
        for file in ['guard.sh','guard.log','guard.id','deadline','ready','applied','restored','restore.rc','client.conf','wpa.id','wpa.log','wpa.stdout','wpa.stderr']:
            cmd+='test ! -L "$D/'+file+'"; rm -f "$D/'+file+'"\n'
        record['M5_RAM_cleanup']=remote(c,cmd+'rmdir "$D"\ntest ! -e "$D"\necho M5_OWNED_RAM_REMOVED\n')
        record['M5_restoration']='PASS_ORIGINAL_BOOT_CONFIG_PROTECTED_HASHES_NETWORK_OPEN_GUARD_ENDED_RAM_REMOVED'
    except BaseException as error:
        record['errors'].append(dict(type=type(error).__name__,gate=str(error)[:150]))
    finally:
        if c:
            try:c.close()
            except BaseException as error:
                record['errors'].append(dict(type=type(error).__name__,gate='M5_CLOSE:'+str(error)[:100]))
        if ap:
            try:
                if armed:
                    record['AP_restoration']=helper.restore(ap)
                    cmd='set -eu\n'+helper.header()+helper.file_guards()
                    for file in ['owner','ready','guard.id','deadline','guard.sh','restore.sh','guard.log','restore.log','restored']:
                        cmd+='test ! -L "$D/'+file+'"; rm -f "$D/'+file+'"\n'
                    record['AP_RAM_cleanup']=remote(ap,cmd+'rmdir "$D"\ntest ! -e "$D"\necho AP_OWNED_RAM_REMOVED\n')
                record['nft_after']=remote(ap,'nft list tables')['stdout']
                require(record['nft_after']==tables_before,'ISOLATION_NOT_EXACTLY_RESTORED')
                record['AP_network_after']=remote(ap,'ip -4 addr show dev br-lan; ip route')['stdout']
                require(record['AP_network_after']==network_before,'AP_NETWORK_NOT_EXACTLY_RESTORED')
            except BaseException as error:
                record['errors'].append(dict(type=type(error).__name__,gate='AP_CLOSURE:'+str(error)[:150]))
            try:ap.close()
            except BaseException as error:
                record['errors'].append(dict(type=type(error).__name__,gate='AP_CLOSE:'+str(error)[:100]))
        record['status']=('PASS_M5_ORIGINAL_RESTORED_RECOVERY_WINDOW_CLOSED' if record.get('M5_restoration') and record.get('AP_restoration',{}).get('guard_ended_verified') and not record['errors'] else 'INCOMPLETE_M5_RESTORE_PRESERVED_AP_CLOSURE_RECORDED')
        record['ended_utc']=support.utc()
        save()
    print(json.dumps({k:record[k] for k in ['status','errors','ended_utc']}))
    return 0 if record['status'].startswith('PASS_') else 1


if __name__=='__main__':
    if sys.argv[1:]==['--ethernet-source-check']:
        raise SystemExit(main())
    raise SystemExit('Use --ethernet-source-check')
