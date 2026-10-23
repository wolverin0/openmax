"""One 180s guarded open-RF management check of the interrupted bench M5."""
import importlib.util
import json
from pathlib import Path
import re
import shlex
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


def main():
    support = load('preprod1_r5aa_abort_restore_20261022.py')
    remote, require, sha = support.remote, support.require, support.sha
    out = HERE/'preprod1_r5aa_M5_recovery_window_20261022.json'
    require(not out.exists(), 'SINGLE_RESTORE_CHECK_ALREADY_USED')
    source = Path(__file__).read_bytes()
    record = dict(status='INCOMPLETE_M5_RECOVERY_CHECK', started_utc=support.utc(),
                  source_sha256=sha(source), parent='FMX0017/PREPROD1 AA exact restoration',
                  changed_evidence='Prior restore loop received ICMP then failed SSH near its deadline.',
                  radio_deadline_s=180, management_acquisition_s=90, production_access=False,
                  IE_or_daemon_or_CPE_treatment=False, observations=[], errors=[])
    rec = json.loads((support.RUN/'receipt.json').read_text(encoding='utf8'))
    g = rec['legacy_guards']['LBM5']
    intake = json.loads((HERE/'root_four_cpe_intake_20261022_run1/receipt.json').read_text(encoding='utf8'))
    access = load('root_four_cpe_access_20261022.py')
    access.remote = remote
    trial = load('preprod1_trial_20261022.py')
    helper = access.ap_helper()
    helper.TTL = 180
    helper.checked = lambda c, cmd, timeout=25: remote(c,cmd,timeout=timeout)['stdout'].encode()
    original_guard = helper.guard_body
    helper.guard_body = lambda: original_guard().replace('+480))','+180))')
    table = 'fmx_preprod_' + helper.TOKEN
    rules, cleanup = trial.bridge_isolation(table, helper.TOKEN)
    original_restore = helper.restore_body
    helper.restore_body = lambda: trial.restore_with_bridge_isolation(original_restore(),cleanup)
    record['guard_source_sha256'] = sha(helper.guard_body().encode())
    record['restore_source_sha256'] = sha(helper.restore_body().encode())
    ap = c = None
    armed = table_owned = False
    tables_before = None

    def save():
        temp=out.with_suffix('.pending')
        temp.write_text(json.dumps(record,indent=2),encoding='utf8')
        temp.replace(out)

    try:
        save()
        ap = access.load('root_goal_direct_link_connection_20261022.py').ap_client()
        record['AP_before'] = helper.off(ap)
        tables_before = remote(ap,'nft list tables')['stdout']
        require(('table bridge '+table) not in tables_before.splitlines(),'ISOLATION_EXISTS')
        # Install before RF. Every later removal requires verified radio-off.
        table_owned = True
        record['isolation_install'] = remote(ap,"set -eu\nnft -f - <<'FMX_RULES'\n"+rules+'FMX_RULES\n')
        record['isolation_table'] = table
        record['isolation_before'] = tables_before
        record['AP_initial'] = helper.arm(ap)
        armed = True
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
        cmd=('set -eu\nD='+d+'\ntest ! -L "$D"\ntest ! -L "$D/guard.sh"\n'
             'test "$(sha256sum "$D/guard.sh" | cut -d\' \' -f1)" = '+g['source_sha256']+'\n'
             'test ! -L "$D/guard.id"\ntest -f "$D/restored"\ntest "$(cat "$D/restore.rc")" = 0\ncat "$D/guard.id"\n')
        pid,ticks=guard_identity(remote(c,cmd)['stdout'])
        cmd=('set -eu\nD='+d+'\ntest ! -L "$D"\ntest ! -L "$D/guard.sh"\n'
             'test "$(sha256sum "$D/guard.sh" | cut -d\' \' -f1)" = '+g['source_sha256']+'\n'
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
                elif table_owned:
                    helper.off(ap)
                    # Exact owner test, copied from the guarded cleanup, after off.
                    remote(ap,'set -eu\n'+cleanup)
                record['nft_after']=remote(ap,'nft list tables')['stdout']
                require(record['nft_after']==tables_before,'ISOLATION_NOT_EXACTLY_RESTORED')
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
    raise SystemExit(main())
