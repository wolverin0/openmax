"""PREPROD1: AP-only zero-touch admission and four-CPE recovery; bounded RAM-only bench."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shlex
import math
import threading
import time
import traceback

import root_four_cpe_access_20261022 as access

HERE = Path(__file__).resolve().parent
WA = 'fc:ec:da:c2:54:0a'
XC = 'b4:fb:e4:5c:d5:d2'
SXT = access.DEVICES['SXT'][1]
LBM = access.DEVICES['LBM5'][1]
MACS = [WA, XC, SXT, LBM]
LABELS = {WA:'WA', XC:'XC', SXT:'SXT', LBM:'LBM5'}
INTAKE = HERE / 'root_four_cpe_intake_20261022_run1/receipt.json'
sha = access.sha
require = access.require
remote = access.remote
utc = lambda: datetime.now(timezone.utc).isoformat()


def legacy_program(name, directory, cfgsha):
    common = '''#!/bin/sh
trap '' HUP
set -eu
D=''' + shlex.quote(directory) + '''
test -d "$D"; test ! -L "$D"
wp=; ws=
'''
    if name == 'SXT':
        restore = '''
 test "$(sha256sum /etc/config/wireless | awk '{print $1}')" = ''' + cfgsha + ''' || rc=81
 changed=0
 if uci changes wireless | grep -q '^wireless.default_radio0.encryption='; then uci revert wireless.default_radio0.encryption || rc=82; changed=1; fi
 if uci changes wireless | grep -q '^wireless.default_radio0.key='; then uci revert wireless.default_radio0.key || rc=83; changed=1; fi
 if test "$changed" = 1; then wifi reload radio0 || rc=84; fi
 test -z "$(uci changes wireless)" || rc=85
 test "$(uci -q get wireless.default_radio0.encryption)" = none || rc=86
'''
        apply = '''
test -z "$(uci changes wireless)"
test "$(sha256sum /etc/config/wireless | awk '{print $1}')" = ''' + cfgsha + '''
test "$(uci -q get wireless.default_radio0.encryption)" = none
uci set wireless.default_radio0.encryption=psk2
uci set wireless.default_radio0.key=FuturaMAX2026
wifi reload radio0
'''
    else:
        restore = '''
 if test -n "$wp" && test -r /proc/$wp/stat && test "$(awk '{print $22}' /proc/$wp/stat)" = "$ws"; then
  kill -TERM "$wp" || rc=87
  for n in 1 2 3 4 5; do
   test ! -r /proc/$wp/stat && break
   test "$(awk '{print $3}' /proc/$wp/stat)" = Z && break
   sleep 1
  done
 fi
 iwconfig ath0 key off open || rc=88
 iwpriv ath0 authmode 1 || rc=89
 iwconfig ath0 essid FuturaMAX-LAB || rc=90
 iwconfig ath0 commit || rc=91
 test "$(md5sum /tmp/system.cfg | awk '{print $1}')" = ''' + cfgsha + ''' || rc=92
'''
        apply = '''
test "$(md5sum /tmp/system.cfg | awk '{print $1}')" = ''' + cfgsha + '''
test -z "$(pidof wpa_supplicant || true)"
/usr/bin/wpa_supplicant -D wext -i ath0 -b br0 -c "$D/client.conf" -f "$D/wpa.log" </dev/null >"$D/wpa.stdout" 2>"$D/wpa.stderr" &
wp=$!
ws=$(awk '{print $22}' /proc/$wp/stat)
printf '%s %s\n' "$wp" "$ws" > "$D/wpa.id"
'''
    return common + '''cleanup() {
 trap - EXIT USR1 TERM INT
 set +e
 rc=0
''' + restore + '''
 printf '%s\n' "$rc" > "$D/restore.rc"
 if test "$rc" = 0; then : > "$D/restored"; fi
 exit "$rc"
}
trap cleanup EXIT
trap 'exit 0' USR1 TERM INT
printf '%s %s\n' "$$" "$(awk '{print $22}' /proc/$$/stat)" > "$D/guard.id"
end=$(($(cut -d. -f1 /proc/uptime)+900))
printf '%s\n' "$end" > "$D/deadline"
: > "$D/ready"
sleep 2
''' + apply + '''
: > "$D/applied"
while test "$(cut -d. -f1 /proc/uptime)" -lt "$end"; do sleep 1; done
'''


def traffic_ready(flows, deadline):
    """Keep observing stations while finite pings and guarded captures finish."""
    require(time.monotonic()<deadline,'QUALIFY_CAPTURE_TIMEOUT')
    return all(flow[index][1].channel.exit_status_ready() for flow in flows for index in [2,3])


def failure_record(error):
    """Retain empty-timeout location without source lines, locals or full paths."""
    frames=traceback.extract_tb(error.__traceback__,limit=8)
    return dict(type=type(error).__name__,gate=str(error)[:180],
                frames=[dict(file=Path(frame.filename).name,line=frame.lineno,function=frame.name) for frame in frames])


def stream_quality(po, pe, pc, co, ce, cc, label):
    """Keep actual packet deficits; invalid acquisition still stops immediately."""
    require(len(po)<=16384 and len(pe)<=8192,'QUALIFY_PING_OUTPUT_BOUND')
    require(len(co)<=32768 and len(ce)<=8192,'QUALIFY_CAPTURE_OUTPUT_BOUND')
    require(pc==0 and not pe,'QUALIFY_PING_EXIT_FAILED_'+label)
    require(cc==0,'QUALIFY_CAPTURE_EXIT_FAILED_'+label)
    stat=re.search(rb'(\d+) packets transmitted, (\d+) packets received',po)
    require(stat is not None,'QUALIFY_PING_FORMAT_FAILED_'+label)
    transmitted,received=int(stat[1]),int(stat[2])
    times=[float(x) for x in re.findall(rb'time=([0-9.]+) ms',po)]
    finite=all(math.isfinite(v) and v>=0 for v in times)
    messages=re.findall(rb'ICMP6?,? echo (request|reply), id (\d+), seq (\d+)',co)
    rq={(i,q) for kind,i,q in messages if kind==b'request'};rp={(i,q) for kind,i,q in messages if kind==b'reply'}
    pairs=len(rq&rp);failures=[]
    if not (transmitted==32 and received==32 and len(times)==32 and finite):
        failures.append('QUALIFY_ECHO_FAILED_'+label)
    if pairs<32:failures.append('QUALIFY_RADIO_PAIRS_FAILED_'+label)
    return dict(transmitted=transmitted,received=received,paired=pairs,reply_timings=len(times),
                p95_ms=sorted(times)[math.ceil(.95*len(times))-1] if times and finite else None,
                qualifying=not failures,failures=failures)


def traffic_qualification_complete(epochs):
    """Every original stream must pass, even when recovery observations continue."""
    return set(epochs)=={str(n) for n in range(5)} and all(
        set(rows)==set(LABELS.values()) and all(
            row.get('qualifying') is True and not row.get('failures') and
            row.get('transmitted')==32 and row.get('received')==32 and
            row.get('reply_timings')==32 and row.get('paired',0)>=32
            for row in rows.values()) for rows in epochs.values())


def capture_listening(stream, device, header, deadline):
    """Nonblocking native startup barrier; retain every consumed stderr byte."""
    require(time.monotonic()<deadline,'CAPTURE_LISTENING_TIMEOUT')
    channel=stream[1].channel
    while channel.recv_stderr_ready():
        chunk=channel.recv_stderr(2048)
        require(bool(chunk),'CAPTURE_EXITED_BEFORE_QUALIFIED_TRAFFIC')
        header.extend(chunk)
        require(len(header)<=8192,'CAPTURE_START_STDERR_BOUND')
    require(not channel.exit_status_ready() and not channel.closed and not channel.eof_received,'CAPTURE_EXITED_BEFORE_QUALIFIED_TRAFFIC')
    return re.search(rb'(?m)^listening on '+re.escape(device.encode())+rb',',header) is not None


def capture_startup_worker(stream, device, header, state):
    """Observe startup during station RPCs; never extend the five-second limit."""
    try:
        while not capture_listening(stream,device,header,state['deadline']):
            time.sleep(.02)
        state['ready_mono']=time.monotonic()
    except Exception as error:
        state['error']=str(error)[:180]


def capture_startup_ready(state):
    if state['error'] is not None:raise RuntimeError(state['error'])
    if state['ready_mono'] is not None:
        require(state['ready_mono']<state['deadline'],'CAPTURE_LISTENING_TIMEOUT')
        return True
    require(time.monotonic()<state['deadline'],'CAPTURE_LISTENING_TIMEOUT')
    return False


def path_capture_command(address):
    """Observe existing XC echo paths only; never generate additional traffic."""
    require(re.fullmatch(r'[0-9a-f:]+',address) is not None,'PATH_CAPTURE_INVALID_ADDRESS')
    filt='icmp6 and host '+address+' and (ip6[40] == 128 or ip6[40] == 129)'
    return 'exec tcpdump -p -n -l -tt -e -s 128 -c 256 -i any '+shlex.quote(filt)


def path_capture_evidence(stream, header):
    """Bound diagnostic output and preserve failures before validating them."""
    ended=stream[1].channel.exit_status_ready()
    output=dict(ended=ended,startup_stderr=bytes(header).decode(errors='replace'))
    if ended:
        stdout=stream[1].read(65537);stderr=bytes(header)+stream[2].read(8193)
        output.update(stdout=stdout[:65536].decode(errors='replace'),stderr=stderr[:8192].decode(errors='replace'),
                      exit_code=stream[1].channel.recv_exit_status(),truncated=len(stdout)>65536 or len(stderr)>8192)
    return output


def validate_path_capture(output):
    require(output['ended'],'PATH_CAPTURE_NOT_ENDED')
    require(not output['truncated'],'PATH_CAPTURE_OUTPUT_BOUND')
    require(output['exit_code']==0,'PATH_CAPTURE_EXIT_FAILED')
    require(re.search(r'(?m)^listening on any,',output['startup_stderr']) is not None,'PATH_CAPTURE_NOT_LISTENING')


def bridge_isolation(table, owner):
    """Forwarding only: keep the wired controller and AP-local CPE traffic."""
    require(re.fullmatch(r'[0-9a-f]{32}',owner) is not None and table=='fmx_preprod_'+owner,'ISOLATION_OWNER_FORMAT')
    rules='table bridge '+table+' {\n comment "'+owner+'";\n chain forward {\n  type filter hook forward priority -300; policy accept;\n  iifname "eth0" oifname "phy0-ap0*" counter drop\n  iifname "phy0-ap0*" oifname "eth0" counter drop\n }\n}\n'
    cleanup='fmx_tables=$(nft list tables)\nif printf "%s\\n" "$fmx_tables" | grep -Fx "table bridge '+table+'" >/dev/null; then\n'
    cleanup+=' fmx_table=$(nft -j list table bridge '+table+')\n fmx_owner=$(jsonfilter -s "$fmx_table" -e \'@.nftables[*].table.comment\')\n test "$fmx_owner" = '+owner+'\n nft delete table bridge '+table+'\nfi\n'
    return rules,cleanup


def restore_with_bridge_isolation(original, cleanup):
    anchor='ubus call network reload >/dev/null\nwifi down radio0\n'
    require(original.count('wifi down radio0\n')==2 and original.count(anchor)==1,'AP_RESTORE_ISOLATION_ANCHOR_CHANGED')
    off='fmx_wireless=$(ubus -t 4 call network.wireless status)\ntest "$(jsonfilter -s "$fmx_wireless" -e \'@.radio0.up\')" = false\nfmx_devs=$(iw dev)\ntest -z "$(printf "%s\\n" "$fmx_devs" | awk \'$1=="Interface" {print $2}\')"\n'
    return original.replace(anchor,anchor+off+cleanup,1)


def daemon_upload_commands(directory, source):
    """Keep each Dropbear exec string small; verify exact bytes before dispatch."""
    require(re.fullmatch(r'/tmp/fmx-admitter-[0-9a-f]{24}',directory) is not None,'DAEMON_UPLOAD_PATH')
    require(0<len(source)<=16384 and source.startswith(b'#!/bin/sh\n') and b'\r' not in source,'DAEMON_UPLOAD_SOURCE_BOUND')
    path=shlex.quote(directory+'/admitter.sh');parent=shlex.quote(directory)
    commands=['set -eu\numask 077\ntest ! -e '+parent+'\ntest ! -L '+parent+'\nmkdir '+parent+'\nset -C\n: > '+path+'\n']
    text=source.decode('utf8');offset=0
    for position in range(0,len(text),512):
        chunk=text[position:position+512]
        command='set -eu\ntest -d '+parent+'\ntest ! -L '+parent+'\ntest -f '+path+'\ntest ! -L '+path+'\ntest "$(wc -c < '+path+')" = '+str(offset)+'\nprintf %s '+shlex.quote(chunk)+' >> '+path+'\n'
        commands.append(command);offset+=len(chunk.encode('utf8'))
    commands.append('set -eu\ntest ! -L '+path+'\ntest "$(sha256sum '+path+' | awk \'{print $1}\')" = '+sha(source)+'\n')
    require(offset==len(source) and all(len(c.encode('utf8'))<=4096 for c in commands),'DAEMON_UPLOAD_EXEC_STRING_BOUND')
    return commands


def main(label):
    require(re.fullmatch(r'[A-Za-z0-9_-]+',label) is not None,'INVALID_RUN_LABEL')
    planpath=HERE/('preprod1_plan_'+label+'.json')
    plan=json.loads(planpath.read_text(encoding='utf8'))
    require(plan['production_access_permitted'] is False and plan['frozen'] is True,'PLAN_SCOPE_NOT_FROZEN')
    for name,digest in plan['source_bindings'].items():
        require(sha((HERE.parent.parent/name).read_bytes())==digest,'FROZEN_SOURCE_CHANGED_'+name)
    review=json.loads((HERE/plan['review_file']).read_text(encoding='utf8'))
    require(review['status'].startswith('PASS') and review['plan_sha256']==sha(planpath.read_bytes()) and review['source_bindings']==plan['source_bindings'],'INDEPENDENT_REVIEW_NOT_BOUND')
    load_tools=access.load('fmx0017_trial_20261022.py')
    out = HERE / ('preprod1_' + label)
    out.mkdir(mode=0o700, exist_ok=False)
    intake = json.loads(INTAKE.read_text(encoding='utf-8'))
    require(intake['status']=='PASS_OPEN_RF_LEGACY_IDENTITY_CONFIG_INTAKE', 'INTAKE_NOT_ACCEPTED')
    rec = dict(experiment='PREPROD1_FMX0017_ZERO_TOUCH_RECOVERY', status='INCOMPLETE_FOUR_CPE', started_utc=utc(),
               source_sha256=sha(Path(__file__).read_bytes()), bindings={n:sha((HERE/n).read_bytes()) for n in ['root_four_cpe_access_20261022.py','root_four_cpe_ap_window_20261022.py','root_multi_cpe_trial_20261022.py']}, samples=[], events=[],
               failures=[], cleanup_errors=[], legacy_guards={}, legacy_baselines={},
               forbidden_actions_executed=False, persistent_config_writes=False)
    def save():
        pending = out / 'receipt.pending'
        pending.write_text(json.dumps(rec, indent=2), encoding='utf-8')
        os.replace(pending, out/'receipt.json')
    def private(name, value):
        raw = value if isinstance(value, bytes) else json.dumps(value, indent=2).encode()
        with (out/name).open('xb') as f: f.write(raw)
        return dict(file=name, bytes=len(raw), sha256=sha(raw))
    ap = rocket = helper = None
    ap_trace = None
    armed = False; rocket_stream = None; rocket_id = None
    legacy_clients = {}; old = access.load('root_multi_cpe_trial_20261022.py')
    streams = []; listener = None; event_buffer = ''; transcript = bytearray()
    interface = 'phy0-ap0'; obj = shlex.quote('hostapd.'+interface)
    whole_end = time.monotonic()+1100; legacy_end = None
    rocket_before = None
    daemon_dir = None; daemon_id = None;isolation_table=None;isolation_tables_before=None
    pending_epochs=[];epoch_setup={};setup_streams=[];setup_drained=set();capture_headers={}
    startup_threads=[];startup_states={}
    owned_captures=[]
    path_capture=None
    daemon_source = (HERE.parent.parent / 'tools/bench/preprod1_admitter.sh').read_bytes()
    require(b'\r' not in daemon_source and daemon_source.startswith(b'#!/bin/sh\n'), 'DAEMON_SOURCE_REQUIRES_LF')
    rec['daemon_source_sha256'] = sha(daemon_source)
    rec['frozen_plan_sha256']=sha(planpath.read_bytes())
    rec['review_sha256']=sha((HERE/plan['review_file']).read_bytes())
    rec['IE_variant']='run8_accepted_60_byte'
    frozen=out/'executed-source';frozen.mkdir()
    (frozen/'preprod1_trial_20261022.py').write_bytes(Path(__file__).read_bytes())
    (frozen/'test_preprod1_audit.py').write_bytes((HERE.parent.parent/'tests/test_preprod1_audit.py').read_bytes())
    (frozen/'fmx_admitter.sh').write_bytes(daemon_source)
    if plan.get('AP_debug'):
        for name in ['preprod1_AP_debug_20261022.py','root_goal_ap_assoc_debug_20261022.py','root_goal_hostapd_cli_20261022.bin']:
            (frozen/name).write_bytes((HERE/name).read_bytes())
    rec['autonomy_scope']='AP-only admission/recovery; no XC exec commands during admission window'
    rec['XC_command_audit']=[]
    control_window=False
    class AuditedXC:
        def __init__(self,client): self.client=client
        def __getattr__(self,key): return getattr(self.client,key)
        def exec_command(self,command,*args,**kwargs):
            rec['XC_command_audit'].append(dict(mono=time.monotonic(),window=control_window,command=command))
            require(not control_window,'FORBIDDEN_XC_EXEC_DURING_ZERO_TOUCH_WINDOW')
            return self.client.exec_command(command,*args,**kwargs)
    # Only the independent deadline differs from the inherited Rocket guard.
    original_rocket_guard=old.rocket_guard
    old.rocket_guard=lambda: original_rocket_guard().replace('+420))','+1140))')

    def clients():
        result = json.loads(remote(ap,'ubus call '+obj+' get_clients',timeout=8)['stdout'])
        return result.get('clients',{})
    def good(mac, row):
        return all(row.get(k) is True for k in ['auth','assoc','authorized']) and (mac not in [WA,XC] or row.get('wds') is True)
    def events():
        nonlocal event_buffer
        if listener is None: return []
        while listener.recv_ready():
            b=listener.recv(8192);transcript.extend(b);event_buffer+=b.decode()
            require(len(transcript)<=524288,'EVENT_OUTPUT_BOUND')
        require(not listener.recv_stderr_ready(),'EVENT_LISTENER_STDERR')
        result=[];decoder=json.JSONDecoder()
        while event_buffer.strip():
            event_buffer=event_buffer.lstrip()
            try: value, used=decoder.raw_decode(event_buffer)
            except json.JSONDecodeError: break
            event_buffer=event_buffer[used:];result.append(value)
            rec['events'].append(dict(mono=time.monotonic(),utc=utc(),value=value))
        return result
    def station_snapshot():
        devs=remote(ap,'iw dev')['stdout']
        names=[interface]+re.findall(r'(?m)^\s*Interface ('+re.escape(interface)+r'\.sta[1-9]\d*)$',devs)
        result={};raw={}
        for name in names:
            text=remote(ap,'iw dev '+name+' station dump')['stdout'];raw[name]=text
            for block in re.split(r'(?m)^Station ',text)[1:]:
                mac=block.split()[0].lower()
                if mac not in MACS: continue
                row={'interface':name}
                for key,pattern in [('connected_seconds',r'connected time:\s*(\d+) seconds'),
                                    ('rx_bytes',r'(?m)^\s*rx bytes:\s*(\d+)\s*$'),
                                    ('tx_bytes',r'(?m)^\s*tx bytes:\s*(\d+)\s*$')]:
                    m=re.search(pattern,block);require(m is not None,'STATION_COUNTER_MISSING');row[key]=int(m[1])
                sig=re.search(r'(?m)^\s*signal:\s*(-?\d+)',block)
                row['signal_dbm']=int(sig[1]) if sig else None
                result[mac]=row
        return result,raw
    def wait_ap():
        end=time.monotonic()+20
        while time.monotonic()<end:
            helper.guard_identity(ap)
            state=json.loads(remote(ap,'ubus call network.wireless status')['stdout'])
            if state.get('radio0',{}).get('up'):
                return helper.readiness(remote(ap,'iw dev')['stdout'],remote(ap,'iw reg get')['stdout'],remote(ap,'iw phy phy0 info')['stdout'],state)
            time.sleep(.3)
        raise RuntimeError('AP_MODE_CHANGE_TIMEOUT')
    def mode(secure):
        # Only the owned encryption delta changes; key is held baseline.
        cmd='set -eu\nwifi down radio0\n'+('uci revert wireless.default_radio0.encryption\n' if secure else 'uci set wireless.default_radio0.encryption=none\n')+'wifi up radio0\n'
        remote(ap,cmd,timeout=20)
        ready=wait_ap();rec.setdefault('AP_mode_transitions',[]).append(dict(utc=utc(),secure=secure,ready=ready));save();return ready
    def legacy_connect(name):
        try:
            c,pin=access.connect_legacy(ap,name,intake['devices'][name]['pin'])
        except Exception:
            if name!='LBM5':raise
            c,pin=access.connect_legacy(ap,name,intake['devices'][name]['pin'],address_override='192.168.1.5')
            rec.setdefault('management_fallbacks',[]).append(dict(name=name,address='192.168.1.5',mono=time.monotonic(),RF_only_confirmed=True))
            rec.setdefault('management_neighbor_observations',[]).append(remote(c,"ip neigh show | grep -E '10.99.0.1|192.168.1.2'",check=False))
        require(pin==intake['devices'][name]['pin'],'LEGACY_PIN_CHANGED')
        return c
    def legacy_snapshot(name,c):
        if name=='SXT':
            cmd='cat /proc/sys/kernel/random/boot_id; sha256sum /etc/config/wireless; md5sum /dev/mtd0 /dev/mtd3 /dev/mtd4 /dev/mtd5 /dev/mtd6 /dev/mtd7 /dev/mtd8; ip -4 addr; ip route; uci changes wireless; iw dev phy0-sta0 link'
        else:
            cmd='cat /proc/sys/kernel/random/boot_id; md5sum /tmp/system.cfg /dev/mtd0 /dev/mtd1 /dev/mtd4 /dev/mtd5; ip -4 addr; ip route; brctl show; iwconfig ath0; iwpriv ath0 get_authmode; iwpriv ath0 get_wds'
        return remote(c,cmd,timeout=20)['stdout']
    def network_state(text):
        return dict(addresses=re.findall(r'(?m)^\s+inet ([^\n]+)',text),
                    routes=[line for line in text.splitlines() if re.match(r'^(default |[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(?:/[0-9]+)? (?:dev|via) )',line)])
    def cleanup_ram_guard(name,c,g):
        d=g['directory'];data=intake['devices'][name]
        cfg=data['wireless_config']['sha256'] if name=='SXT' else data['system_md5']
        md5=hashlib.md5(legacy_program(name,d,cfg).encode()).hexdigest()
        pid,ticks=g['pid'],g['ticks']
        cmd='set -eu\nD='+shlex.quote(d)+'\n'
        cmd+='if test ! -e "$D"; then echo ALREADY_ABSENT; exit 0; fi\n'
        cmd+='test -d "$D"; test ! -L "$D"; test ! -L "$D/guard.sh"\n'
        cmd+='test "$(md5sum "$D/guard.sh" | awk \'{print $1}\')" = '+md5+'\n'
        cmd+='test "$(cat "$D/guard.id")" = "'+str(pid)+' '+str(ticks)+'"\n'
        cmd+='if test -r /proc/'+str(pid)+'/stat && test "$(awk \'{print $22}\' /proc/'+str(pid)+'/stat)" = '+str(ticks)+' && test "$(awk \'{print $3}\' /proc/'+str(pid)+'/stat)" != Z; then exit 74; fi\n'
        cmd+='if test -d "$D/ctrl"; then test ! -L "$D/ctrl"; if test -S "$D/ctrl/ath0"; then rm -f "$D/ctrl/ath0"; fi; rmdir "$D/ctrl"; fi\n'
        for file in ['guard.sh','guard.id','deadline','ready','applied','restore.rc','restored','guard.log','client.conf','wpa.id','wpa.log','wpa.stdout','wpa.stderr']:
            cmd+='test ! -L "$D/'+file+'"; rm -f "$D/'+file+'"\n'
        cmd+='rmdir "$D"\ntest ! -e "$D"\necho OWNED_RAM_GUARD_REMOVED\n'
        return remote(c,cmd)
    def arm_legacy(name,c):
        nonlocal legacy_end
        data=intake['devices'][name]
        cfg=data['wireless_config']['sha256'] if name=='SXT' else data['system_md5']
        directory='/tmp/fmx-four-'+secrets.token_hex(12)
        script=legacy_program(name,directory,cfg)
        config='ctrl_interface='+directory+'/ctrl\nap_scan=1\nnetwork={\n ssid="FuturaMAX-LAB"\n psk="FuturaMAX2026"\n key_mgmt=WPA-PSK\n proto=RSN\n pairwise=CCMP\n group=CCMP\n}\n'
        check="test \"$(uci -q get wireless.default_radio0.encryption)\" = none\ntest -z \"$(uci changes wireless)\"\n" if name=='SXT' else "test -z \"$(pidof wpa_supplicant || true)\"\n"
        cmd='set -eu\n'+check+'test ! -e '+shlex.quote(directory)+'\numask 077\nmkdir '+shlex.quote(directory)+'\nset -C\nprintf %s '+shlex.quote(script)+' > '+directory+'/guard.sh\n'
        if name=='LBM5': cmd+='printf %s '+shlex.quote(config)+' > '+directory+'/client.conf\n'
        script_md5=hashlib.md5(script.encode()).hexdigest()
        cmd+='test "$(md5sum '+directory+'/guard.sh | awk \'{print $1}\')" = '+script_md5+'\n'
        cmd+='/bin/sh '+directory+'/guard.sh </dev/null >'+directory+'/guard.log 2>&1 &\necho DISPATCHED\n'
        rec['legacy_guards'][name]={'directory':directory,'source_sha256':sha(script.encode()),'ttl_seconds':900,'intent_recorded':True}
        save();remote(c,cmd,timeout=8)
        end=time.monotonic()+1.5
        while True:
            x=remote(c,'test -f '+directory+'/ready && cat '+directory+'/guard.id '+directory+'/deadline',check=False,timeout=2)
            if x['exit_code']==0: break
            require(time.monotonic()<end,'LEGACY_GUARD_READY_TIMEOUT');time.sleep(.1)
        values=x['stdout'].split();require(len(values)==3 and all(v.isdigit() for v in values),'LEGACY_GUARD_ID_PROTOCOL')
        rec['legacy_guards'][name].update(pid=int(values[0]),ticks=int(values[1]),deadline_uptime=int(values[2]),host_armed=time.monotonic())
        if legacy_end is None: legacy_end=time.monotonic()+875
        save()
    try:
        save();ap=access.load('root_goal_direct_link_connection_20261022.py').ap_client()
        rec['native_wait_preflight']=remote(ap,"set -eu\ncommand -v ucode; command -v ping; command -v tcpdump\nread up rest < /proc/uptime\ntest -n \"$up\"\nucode -e 'sleep(500)'")
        rocket=AuditedXC(access.load('root_step1c_rocket_observer_20261021.py').connect())
        rocket_before={k:remote(rocket,cmd)['stdout'] for k,cmd in {
            'hashes':'md5sum '+old.HASH_FILES,'bridge':'brctl show; ifconfig br0 | head -n 4',
            'addresses':'ip -4 addr show dev br0; route -n','rules':'ebtables -L FORWARD'}.items()}
        require([row.split()[0] for row in rocket_before['hashes'].splitlines()[:3]]==[old.CFG,old.CFG,old.AUTO],'ROCKET_BASELINE_CHANGED')
        require(not re.search(r'-i (?:ath0 -o eth0|eth0 -o ath0) -j DROP',rocket_before['rules']),'ROCKET_MATCHING_RULE_EXISTS')
        rec['rocket_baseline']=rocket_before
        (frozen/'Rocket_guard.sh').write_text(old.rocket_guard(),encoding='utf8')
        rocket_stream=rocket.exec_command('exec /bin/sh -c '+shlex.quote(old.rocket_guard()),timeout=8);rocket_stream[0].close();streams.append(rocket_stream)
        first=rocket_stream[1].readline().strip();require(re.fullmatch(r'READY \d+ \d+',first),'ROCKET_GUARD_NOT_READY')
        rocket_id=first.split()[1:]
        helper=access.ap_helper();helper.TTL=1200
        if plan.get('AP_debug'):
            trace_module=access.load('preprod1_AP_debug_20261022.py')
            trace_out=HERE/'preprod_guarida_20261022'/'history'/('preprod1_'+label+'_AP_debug')
            ap_trace=trace_module.APTrace(helper,trace_out)
            ap_trace.stage(ap)
            rec['AP_debug_preflight']=dict(global_ping_verified_before_window=True,private_raw_logs=True)
        original_ap_guard=helper.guard_body
        helper.guard_body=lambda: original_ap_guard().replace('+480))','+1200))')
        isolation_table='fmx_preprod_'+helper.TOKEN
        isolation_rules,isolation_cleanup=bridge_isolation(isolation_table,helper.TOKEN)
        isolation_tables_before=remote(ap,'nft list tables')['stdout']
        require(('table bridge '+isolation_table) not in isolation_tables_before.splitlines(),'ISOLATION_TABLE_ALREADY_EXISTS')
        original_ap_restore=helper.restore_body
        helper.restore_body=lambda:restore_with_bridge_isolation(original_ap_restore(),isolation_cleanup)
        rec['guard_budgets']=dict(AP=1200,Rocket=1140,legacy=900,daemon=780)
        (frozen/'AP_guard.sh').write_text(helper.guard_body(),encoding='utf8')
        (frozen/'AP_restore.sh').write_text(helper.restore_body(),encoding='utf8')
        rec['AP_initial']=helper.arm(ap);armed=True
        rec['bridge_isolation']=dict(table=isolation_table,owner=helper.TOKEN,original_tables=isolation_tables_before,rules_sha256=sha(isolation_rules.encode()),scope='OnlybridgeFORWARDeth0<->phy0-ap0*, noINPUT/OUTPUT; existingAP1200sguard removesonlyafterreloadandverifiedradiooff/noVAP')
        save()
        rec['bridge_isolation']['install']=remote(ap,"set -eu\nnft -f - <<'FMX_ISOLATION'\n"+isolation_rules+'FMX_ISOLATION\n')
        rec['bridge_isolation']['installed_table']=remote(ap,'nft -j list table bridge '+isolation_table)
        save()
        wait_end=time.monotonic()+75;online=set()
        while time.monotonic()<wait_end and len(online)<2:
            for name,(address,mac) in access.DEVICES.items():
                if name in online:continue
                probe=remote(ap,'ping -c 1 -W 2 -I br-lan '+address,check=False,timeout=4)
                rec.setdefault('open_reacquisition_probes',[]).append(dict(name=name,mono=time.monotonic(),result=probe))
                save()
                if probe['exit_code']==0:online.add(name)
            time.sleep(.2)
        require(len(online)==2,'LEGACY_REACQUISITION_FAILED_'+'_'.join(sorted(set(access.DEVICES)-online)))
        for name in access.DEVICES:
            c=legacy_connect(name);legacy_clients[name]=c
            # Clean only the exact ended guards from the preserved first trial.
            prior_path=HERE/'root_four_cpe_20261022_run2/receipt.json'
            if prior_path.exists():
                prior=json.loads(prior_path.read_text(encoding='utf-8'))
                old_guard=prior.get('legacy_guards',{}).get(name)
                if old_guard is not None:
                    rec.setdefault('prior_guard_RAM_cleanup',{})[name]=cleanup_ram_guard(name,c,old_guard)
            baseline=legacy_snapshot(name,c);rec['legacy_baselines'][name]=baseline
            require(baseline.splitlines()[0]==intake['devices'][name]['boot_id'],'LEGACY_BOOT_CHANGED')
        save()
        # Both guards are dispatched while their open RF management is usable.
        for name in access.DEVICES:arm_legacy(name,legacy_clients[name])
        for c in legacy_clients.values():c.close()
        legacy_clients.clear()
        rec['AP_secure']=mode(True)
        # Seed the exact discovery IE before XC's initial scan can cache this BSS.
        seed=re.search(rb'(?m)^IE=([0-9a-f]+)$',daemon_source).group(1).decode()
        require(len(seed)==120,'PREPARATION_IE_NOT_EXACT_60_BYTES')
        rec['AP_discovery_seed_before_XC_preparation']=remote(ap,'set -eu\nubus -t 4 call '+obj+' set_vendor_elements '+shlex.quote(json.dumps(dict(vendor_elements=seed)))+'\nubus -t 4 call '+obj+' update_beacon')
        rec['XC_preparation_after_AP_secure']=dict(mono=time.monotonic(),utc=utc())
        for key,value in [('ssid','"FuturaMAX-LAB"'),('psk','"FuturaMAX2026"'),('key_mgmt','WPA-PSK'),('proto','RSN'),('pairwise','CCMP'),('group','CCMP'),('scan_freq','5180')]:
            require(remote(rocket,'wpa_cli -i ath0 set_network 0 '+key+' '+shlex.quote(value))['stdout'].strip()=='OK','ROCKET_WPA_SET_'+key)
        # Open RF legacy setup has ended; flush only now, before the zero-touch window.
        require(remote(rocket,'wpa_cli -i ath0 bss_flush 0')['stdout'].strip()=='OK','XC_POST_SECURE_CACHE_FLUSH_FAILED')
        require(remote(rocket,'wpa_cli -i ath0 scan')['stdout'].strip()=='OK','XC_PRE_WINDOW_SCAN_FAILED')
        scan_end=time.monotonic()+35;fresh_bss=None
        while time.monotonic()<scan_end:
            result=remote(rocket,'wpa_cli -i ath0 scan_results',timeout=min(4,max(.1,scan_end-time.monotonic())))
            require(time.monotonic()<=scan_end,'XC_PRE_WINDOW_SCAN_DEADLINE_EXCEEDED')
            fresh_bss=next((line for line in result['stdout'].splitlines() if re.match(r'^18:e8:29:74:55:a2\s+5180\s+',line) and '[WPA2-PSK-CCMP]' in line and 'FuturaMAX-LAB' in line),None)
            if fresh_bss:break
            time.sleep(1)
        require(fresh_bss is not None,'XC_PRE_WINDOW_FRESH_SECURE_BSS_NOT_OBSERVED')
        rec['XC_fresh_secure_BSS_pre_window']=dict(mono=time.monotonic(),utc=utc(),row=fresh_bss)
        # Announce for discovery, then withdraw before XC's initial association.
        rec['AP_discovery_clear_before_XC_enable']=remote(ap,'set -eu\nubus -t 4 call '+obj+' set_vendor_elements '+shlex.quote(json.dumps(dict(vendor_elements="")))+'\nubus -t 4 call '+obj+' update_beacon')
        time.sleep(2)
        require(remote(rocket,'wpa_cli -i ath0 enable_network 0')['stdout'].strip()=='OK','XC_NORMAL_ENABLE_FAILED')
        require(remote(rocket,'wpa_cli -i ath0 reassociate')['stdout'].strip()=='OK','XC_PRE_WINDOW_REASSOCIATE_FAILED')
        rec['XC_pre_window_status']=remote(rocket,'wpa_cli -i ath0 status; wpa_cli -i ath0 list_networks')
        pre_window_states=re.findall(r'(?m)^wpa_state=([A-Z0-9_]+)\r?$',rec['XC_pre_window_status']['stdout'])
        require(len(pre_window_states)==1 and pre_window_states[0] in ['SCANNING','DISCONNECTED','INACTIVE','AUTHENTICATING','ASSOCIATING','ASSOCIATED','4WAY_HANDSHAKE','GROUP_HANDSHAKE'] and not re.search(r'(?m)^(?:FAIL|UNKNOWN COMMAND)',rec['XC_pre_window_status']['stdout']),'XC_PRE_WINDOW_STATUS_NOT_WAITING')
        rec['XC_pre_window_waiting_state']=pre_window_states[0]
        control_window=True;rec['control_window_start']=dict(mono=time.monotonic(),utc=utc());save()
        daemon_dir='/tmp/fmx-admitter-'+secrets.token_hex(12)
        upload_commands=daemon_upload_commands(daemon_dir,daemon_source)
        rec['daemon_directory']=daemon_dir;rec['daemon_upload']=dict(source_bytes=len(daemon_source),commands=len(upload_commands),max_command_bytes=max(len(c.encode('utf8')) for c in upload_commands),completed_commands=0,complete=False);save()
        for command in upload_commands:
            remote(ap,command);rec['daemon_upload']['completed_commands']+=1;save()
        rec['daemon_upload']['complete']=True;save()
        cmd='set -eu\ntest "$(sha256sum '+daemon_dir+'/admitter.sh | awk \'{print $1}\')" = '+sha(daemon_source)+'\n/bin/sh '+daemon_dir+'/admitter.sh '+daemon_dir+' </dev/null >'+daemon_dir+'/stdout 2>'+daemon_dir+'/stderr &\necho DISPATCHED\n'
        require(len(cmd.encode('utf8'))<=4096,'DAEMON_DISPATCH_EXEC_STRING_BOUND')
        remote(ap,cmd)
        require(remote(ap,'sleep 1; test -f '+daemon_dir+'/ready; cat '+daemon_dir+'/daemon.id')['exit_code']==0,'DAEMON_NOT_READY')
        daemon_id=remote(ap,'cat '+daemon_dir+'/daemon.id')['stdout'].split()
        rec['daemon_id']=daemon_id;save()
        # Observation only. The daemon owns every IE decision and exact-MAC drop.
        end=min(legacy_end-60,time.monotonic()+800)
        previous={};resets=set();qualified=set()
        while time.monotonic()<end:
            pid,ticks=daemon_id
            require(remote(ap,'test -r /proc/'+pid+'/stat && test "$(awk \'{print $22}\' /proc/'+pid+'/stat)" = '+ticks+' && test "$(awk \'{print $3}\' /proc/'+pid+'/stat)" != Z',check=False)['exit_code']==0,'DAEMON_ENDED_DURING_ACQUISITION')
            require(remote(ap,'test "$(nft -j list table bridge '+isolation_table+' | jsonfilter -e \'@.nftables[*].table.comment\')" = '+helper.TOKEN,check=False)['exit_code']==0,'ISOLATION_TABLE_OWNER_OR_PRESENCE_CHANGED')
            actions_before=remote(ap,'cat '+daemon_dir+'/actions.log')['stdout']
            rows=clients();counts,raw=station_snapshot()
            actions=remote(ap,'cat '+daemon_dir+'/actions.log')['stdout']
            requests=re.findall(r'DROP_REQUEST n=(\d+) target=([0-9a-f:]+)',actions)
            current_n,current_target=requests[-1] if requests else (None,None)
            recovered=current_n is not None and ('RECOVERED n='+current_n+' ') in actions_before
            if ap_trace is not None and current_n=='2':
                if not ap_trace.started:ap_trace.start(ap)
                ap_trace.sample(ap)
                if recovered:
                    rec['AP_debug']=ap_trace.finish(ap)
                    require(not rec['AP_debug']['errors'],'AP_DEBUG_TRACE_OR_RESTORATION_FAILED')
            expected=current_target if current_target is not None and not recovered else None
            if 'FOUR_ADMITTED' in actions_before:
                for mac in MACS:
                    require(mac==expected or good(mac,rows.get(mac,{})),'UNEXPECTED_CLIENT_LOSS_'+LABELS[mac])
                for mac,v in counts.items():
                    if mac not in previous:continue
                    decreased=any(v[k]<previous[mac][k] for k in ['connected_seconds','rx_bytes','tx_bytes'])
                    if decreased:
                        require(mac==current_target and current_n not in resets,'UNEXPECTED_SESSION_RESET_'+LABELS[mac])
                        resets.add(current_n)
                # Keep a removed target's last pre-drop counters until its new session is sampled.
                previous.update(counts)
                starts=re.findall(r'STABLE_START epoch=(\d+)',actions)
                epoch=int(starts[-1]) if starts else -1
                # Per-epoch packet qualification runs concurrently with native station monitoring.
                if epoch>=0 and epoch not in qualified and set(counts)==set(MACS) and all(good(m,rows.get(m,{})) for m in MACS):
                    rec.setdefault('epoch_preflight_context',{})[str(epoch)]={'before':remote(ap,'ip -6 neigh show dev br-lan; brctl showmacs br-lan',check=False)}
                    probes=[]
                    for mac in MACS:
                        address=old.LL[mac] if mac in [WA,XC] else access.DEVICES[LABELS[mac]][0]
                        command=('ping -6' if mac in [WA,XC] else 'ping')+' -c 3 -i 1 -W 1 -s 56 -I br-lan '+address
                        probe=ap.exec_command('exec '+command,timeout=8);probe[0].close();streams.append(probe)
                        key=str(epoch)+'-'+LABELS[mac];setup_streams.append((key+'-preflight',probe,bytearray()))
                        probes.append((mac,probe,counts[mac]['interface']))
                    epoch_setup[epoch]=dict(stage='preflight',probes=probes,deadline=time.monotonic()+8)
                    qualified.add(epoch)
            for epoch,setup in list(epoch_setup.items()):
                if setup['stage']=='preflight':
                    require(time.monotonic()<setup['deadline'],'PREFLIGHT_STREAM_TIMEOUT')
                    if not all(p[1].channel.exit_status_ready() for _,p,_ in setup['probes']):continue
                    for mac,probe,device in setup['probes']:
                        po=probe[1].read(16385);pe=probe[2].read(8193);pc=probe[1].channel.recv_exit_status()
                        key=str(epoch)+'-'+LABELS[mac]
                        rec.setdefault('epoch_preflight_probes',{})[key]=private('preflight-'+key+'.json',dict(stdout=po[:16384].decode(errors='replace'),stderr=pe[:8192].decode(errors='replace'),exit_code=pc,truncated=len(po)>16384 or len(pe)>8192,qualification_sample=False))
                        setup_drained.add(key+'-preflight');save()
                        require(len(po)<=16384 and len(pe)<=8192,'PREFLIGHT_OUTPUT_BOUND')
                    rec['epoch_preflight_context'][str(epoch)]['after']=remote(ap,'ip -6 neigh show dev br-lan; brctl showmacs br-lan',check=False)
                    setup.update(stage='capture',captures=[],capture_deadline=time.monotonic()+48,listening_deadline=time.monotonic()+5)
                    for mac in MACS:
                        device=next(device for m,_,device in setup['probes'] if m==mac);label_name=LABELS[mac]
                        address=old.LL[mac] if mac in [WA,XC] else access.DEVICES[label_name][0]
                        proto='icmp6' if mac in [WA,XC] else 'icmp'
                        command=('ping -6' if mac in [WA,XC] else 'ping')+' -c 32 -i 1 -W 1 -s 56 -I br-lan '+address
                        filt=(proto+' and host '+address+(' and (ip6[40] == 128 or ip6[40] == 129)' if mac in [WA,XC] else ' and (icmp[0] == 8 or icmp[0] == 0)'))
                        capcmd='exec tcpdump --immediate-mode -B 64 -p -n -l -tt -s 128 -c 64 -i '+device+' '+shlex.quote(filt)
                        capguard=load_tools.adaptive_ping_wrapper(capcmd).replace('now-start>=60','now-start>=45')
                        require(len(capguard.encode())<6000,'CAPTURE_COMMAND_BOUND')
                        cap=ap.exec_command('exec /bin/sh -c '+shlex.quote(capguard),timeout=48)
                        owned_captures.append(cap)
                        cap[0].close();streams.append(cap)
                        header=bytearray();capture_headers[id(cap)]=header;setup_streams.append((str(epoch)+'-'+label_name+'-capture',cap,header))
                        state=dict(deadline=setup['listening_deadline'],ready_mono=None,error=None);startup_states[id(cap)]=state
                        watcher=threading.Thread(target=capture_startup_worker,args=(cap,device,header,state),daemon=True)
                        startup_threads.append(watcher);watcher.start()
                        setup['captures'].append((mac,device,command,cap,header))
                    if epoch==0 and plan.get('AP_path_capture') is True:
                        capguard=load_tools.adaptive_ping_wrapper(path_capture_command(old.LL[XC])).replace('now-start>=60','now-start>=45')
                        require(len(capguard.encode())<6000,'PATH_CAPTURE_COMMAND_BOUND')
                        cap=ap.exec_command('exec /bin/sh -c '+shlex.quote(capguard),timeout=48)
                        owned_captures.append(cap);cap[0].close();streams.append(cap)
                        header=bytearray()
                        state=dict(deadline=setup['listening_deadline'],ready_mono=None,error=None);startup_states[id(cap)]=state
                        path_capture=(cap,header,state)
                        watcher=threading.Thread(target=capture_startup_worker,args=(cap,'any',header,state),daemon=True)
                        startup_threads.append(watcher);watcher.start()
                listening=[capture_startup_ready(startup_states[id(cap)]) for mac,device,command,cap,header in setup['captures']]
                if epoch==0 and path_capture is not None:
                    cap,header,state=path_capture
                    listening.append(capture_startup_ready(state))
                    rec['AP_path_capture_startup']=dict(header=header.decode(errors='replace'),timing=dict(state))
                rec.setdefault('capture_startup',{})[str(epoch)]={LABELS[mac]:header.decode(errors='replace') for mac,device,command,cap,header in setup['captures']}
                rec.setdefault('capture_startup_timing',{})[str(epoch)]={LABELS[mac]:dict(startup_states[id(cap)]) for mac,device,command,cap,header in setup['captures']}
                save()
                if not all(listening):continue
                paths=[]
                for mac,device,command,cap,header in setup['captures']:
                    ping=ap.exec_command('exec '+command,timeout=45);ping[0].close();streams.append(ping)
                    paths.append((mac,device,ping,cap))
                rec.setdefault('epoch_pending',{})[str(epoch)]=dict(started=time.monotonic(),capture_deadline=setup['capture_deadline'],native_listening_verified=True)
                pending_epochs.append((epoch,paths));del epoch_setup[epoch]
            for item in pending_epochs[:]:
                epoch,flows=item
                if not traffic_ready(flows,rec['epoch_pending'][str(epoch)]['capture_deadline']):continue
                results={}
                for mac,device,ping,cap in flows:
                    po=ping[1].read(16385);pe=ping[2].read(8193);pc=ping[1].channel.recv_exit_status()
                    co=cap[1].read(32769);ce=bytes(capture_headers[id(cap)])+cap[2].read(8193);cc=cap[1].channel.recv_exit_status()
                    artifact=private('epoch'+str(epoch)+'-'+LABELS[mac]+'.json',dict(ping=po[:16384].decode(errors='replace'),ping_stderr=pe[:8192].decode(errors='replace'),capture=co[:32768].decode(errors='replace'),capture_stderr=ce[:8192].decode(errors='replace'),ping_exit_code=pc,capture_exit_code=cc,truncated=len(po)>16384 or len(pe)>8192 or len(co)>32768 or len(ce)>8192))
                    rec.setdefault('epoch_stream_artifacts',{})[str(epoch)+'-'+LABELS[mac]]=artifact;save()
                    quality=stream_quality(po,pe,pc,co,ce,cc,LABELS[mac])
                    results[LABELS[mac]]=dict(interface=device,**quality,artifact=artifact)
                    rec['failures'].extend(dict(type='QualificationFailure',gate=gate,epoch=epoch,CPE=LABELS[mac]) for gate in quality['failures'])
                rec.setdefault('epoch_traffic',{})[str(epoch)]=results;pending_epochs.remove(item)
            rec['last_auth_flags']=rows
            rec['samples'].append(dict(mono=time.monotonic(),clients=rows,stations=counts,actions=actions))
            save()
            complete=remote(ap,'test -f '+daemon_dir+'/complete',check=False)['exit_code']==0
            if complete and not pending_epochs:break
            require(time.monotonic()<whole_end,'WHOLE_WINDOW_DEADLINE')
            time.sleep(.5)
        actions=remote(ap,'cat '+daemon_dir+'/actions.log')['stdout']
        require('COMPLETE' in actions and len(rec.get('epoch_traffic',{}))==5,'MULTICYCLE_RECOVERY_NOT_COMPLETE')
        require(resets=={'1','2','3','4'},'EXPECTED_STATION_SESSION_RESETS_NOT_VERIFIED')
        require(not any(x['window'] for x in rec['XC_command_audit']),'XC_COMMAND_DURING_WINDOW')
        if ap_trace is not None:
            require(ap_trace.started and ap_trace.finished and rec['AP_debug']['status']=='TRACE_COMPLETE','AP_DEBUG_NOT_COMPLETED')
        rec['recovery_matrix_complete']=True;rec['verified_session_resets']=sorted(resets)
        rec['traffic_qualification_complete']=traffic_qualification_complete(rec.get('epoch_traffic',{}))
        require(rec['traffic_qualification_complete'],'TRAFFIC_QUALIFICATION_FAILED')
        rec['multicycle_pass']=True;rec['verified_session_resets']=sorted(resets)
        rec['acquisition_complete']=True
    except BaseException as e:
        rec['failures'].append(failure_record(e))
        if ap is not None and armed:
            try:
                rec['failure_AP_clients']=clients();counts,raw=station_snapshot();rec['failure_station_snapshot']=private('failure-station-dumps.json',raw)
            except Exception:pass
    finally:
        control_window=False
        rec['control_window_end']=dict(mono=time.monotonic(),utc=utc())
        # No deferred CPE task was created; only independently bounded rollback guard exists.
        # End the AP-local daemon before reloading hostapd for restoration.
        if ap is not None and daemon_dir is not None:
            try:
                if daemon_id is None:
                    identity=remote(ap,'cat '+daemon_dir+'/daemon.id',check=False)['stdout'].split()
                    if len(identity)==2 and all(v.isdigit() for v in identity):daemon_id=identity
                if daemon_id is not None:
                    pid,ticks=daemon_id
                    cmd='set -eu\nif test -r /proc/'+pid+'/stat && test "$(awk \'{print $22}\' /proc/'+pid+'/stat)" = '+ticks+' && test "$(awk \'{print $3}\' /proc/'+pid+'/stat)" != Z; then kill -USR1 '+pid+'; fi\n'
                    cmd+='for n in 1 2 3 4 5 6 7 8 9 10 11 12; do if test -f '+daemon_dir+'/stop.reason && { test ! -r /proc/'+pid+'/stat || test "$(awk \'{print $22}\' /proc/'+pid+'/stat)" != '+ticks+' || test "$(awk \'{print $3}\' /proc/'+pid+'/stat)" = Z; }; then echo ENDED; exit 0; fi; sleep 1; done; exit 79'
                    rec['daemon_ended_verified']=remote(ap,cmd,timeout=18)
                data={name:remote(ap,'cat '+daemon_dir+'/'+name,check=False,limit=2097152)['stdout'] for name in ['actions.log','events.jsonl','state.log','stderr','listener.stderr','restore.rc','exit.rc','stop.reason']}
                rec['daemon_evidence']=private('daemon-evidence.json',data)
                rec['daemon_restore_rc']=data['restore.rc'].strip()
                require(rec.get('daemon_ended_verified'),'DAEMON_NOT_ENDED')
                if rec['daemon_restore_rc']!='0':
                    rec['cleanup_errors'].append('Daemon:DAEMON_CLEAR_FAILED_'+rec['daemon_restore_rc'])
                # Admission/error validation affects acceptance, not safe ended-file cleanup.
                rec['daemon_acceptance']=bool(rec['daemon_restore_rc']=='0' and data['exit.rc'].strip()=='0' and data['stop.reason'].strip()=='operator_signal' and 'COMPLETE' in data['actions.log'] and not data['stderr'] and not data['listener.stderr'])
                remote(ap,'set -eu\nD='+daemon_dir+'\ntest ! -L "$D"\ntest "$(sha256sum "$D/admitter.sh" | awk \'{print $1}\')" = '+sha(daemon_source)+'\nfor f in admitter.sh daemon.id listener.pid ready admitted complete actions.log state.log events.jsonl stdout stderr listener.stderr restore.rc exit.rc stop.reason drop1.ack drop2.ack drop3.ack drop4.ack drop1.observed drop2.observed drop3.observed drop4.observed; do test ! -L "$D/$f"; rm -f "$D/$f"; done\nrmdir "$D"')
                rec['daemon_RAM_files_removed']=True
            except BaseException as e:rec['cleanup_errors'].append('Daemon:'+str(e)[:160])
        if ap_trace is not None and ap is not None:
            try:
                rec['AP_debug']=ap_trace.finish(ap)
                rec['AP_debug_excerpt']=private('AP-debug-excerpt.json',rec['AP_debug'])
                rec['cleanup_errors'].extend('AP_debug:'+e for e in rec['AP_debug']['errors'])
            except BaseException as e:rec['cleanup_errors'].append('AP_debug:'+str(e)[:160])
        # Each capture uses the proven native PID/start-owned wrapper with a45s deadline.
        # Stop admission first, then prove those wrappers ended before CPE restoration.
        if startup_threads:
            try:
                for watcher in startup_threads:watcher.join(timeout=1)
                require(all(not watcher.is_alive() for watcher in startup_threads),'CAPTURE_STARTUP_WORKER_NOT_ENDED')
                rec['capture_startup_workers_ended']=len(startup_threads)
            except BaseException as e:rec['cleanup_errors'].append('capture_startup:'+str(e)[:120])
        if owned_captures:
            try:
                cap_end=time.monotonic()+48
                while any(not c[1].channel.exit_status_ready() for c in owned_captures) and time.monotonic()<cap_end:time.sleep(.2)
                require(all(c[1].channel.exit_status_ready() for c in owned_captures),'CAPTURE_NATIVE_GUARD_NOT_ENDED')
                rec['capture_native_guards_ended']=len(owned_captures)
            except BaseException as e:rec['cleanup_errors'].append('capture:'+str(e)[:120])
        if path_capture is not None:
            try:
                cap,header,state=path_capture
                output=path_capture_evidence(cap,header)
                rec['AP_path_capture']=private('epoch0-XC-any-path.json',output)
                validate_path_capture(output)
                require(capture_startup_ready(state),'PATH_CAPTURE_STARTUP_INCOMPLETE')
                rec['AP_path_capture_verified']=True
            except BaseException as e:rec['cleanup_errors'].append('AP_path_capture:'+str(e)[:160])
        for key,stream,header in setup_streams:
            if key in setup_drained:continue
            try:
                ready=stream[1].channel.exit_status_ready();output=dict(ended=ready,startup_stderr=header.decode(errors='replace'))
                if ready:
                    stdout=stream[1].read(32769);stderr=stream[2].read(8193)
                    output.update(stdout=stdout[:32768].decode(errors='replace'),stderr=stderr[:8192].decode(errors='replace'),exit_code=stream[1].channel.recv_exit_status(),truncated=len(stdout)>32768 or len(stderr)>8192)
                rec.setdefault('setup_stream_evidence',{})[key]=private('setup-'+key+'.json',output)
            except Exception as e:rec.setdefault('failure_evidence_errors',[]).append(str(e)[:120])
        for epoch,flows in pending_epochs:
            for mac,device,ping,cap in flows:
                try:
                    output={}
                    for kind,stream in [('ping',ping),('capture',cap)]:
                        ready=stream[1].channel.exit_status_ready()
                        output[kind]=dict(ended=ready)
                        if ready:
                            stdout=stream[1].read(32769);stderr=stream[2].read(8193)
                            output[kind].update(stdout=stdout[:32768].decode(errors='replace'),stderr=stderr[:8192].decode(errors='replace'),exit_code=stream[1].channel.recv_exit_status(),truncated=len(stdout)>32768 or len(stderr)>8192)
                    rec.setdefault('failed_epoch_streams',{})[str(epoch)+'-'+LABELS[mac]]=private('failed-epoch'+str(epoch)+'-'+LABELS[mac]+'.json',output)
                except Exception as e:rec.setdefault('failure_evidence_errors',[]).append(str(e)[:120])
        # Try explicit signal, otherwise leave each independent900s guard to
        # restore its original open profile, and verify over the open RF AP.
        for name,g in rec['legacy_guards'].items():
            c=legacy_clients.get(name)
            if c is None:
                try:c=legacy_connect(name);legacy_clients[name]=c
                except Exception:continue
            try:
                pid,ticks=g['pid'],g['ticks'];cmd='set -eu\ntest "$(awk \'{print $22}\' /proc/'+str(pid)+'/stat)" = '+str(ticks)+'\nkill -USR1 '+str(pid)
                remote(c,cmd,timeout=5);g['explicit_restore_signal_sent']=True
            except Exception:g['explicit_restore_signal_sent']=False
        for c in legacy_clients.values():c.close()
        legacy_clients.clear()
        if ap is not None and armed and rec['legacy_guards']:
            try:
                mode(False)
                restored=set();restore_end=min(whole_end,time.monotonic()+930)
                while time.monotonic()<restore_end and restored!=set(rec['legacy_guards']):
                    for name,g in rec['legacy_guards'].items():
                        if name in restored:continue
                        address=access.DEVICES[name][0]
                        if remote(ap,'ping -c 1 -W 1 -I br-lan '+address,check=False,timeout=3)['exit_code']!=0:continue
                        try:c=legacy_connect(name)
                        except Exception:continue
                        try:
                            d=g['directory'];check='set -eu\ntest -f '+d+'/restored\ntest "$(cat '+d+'/restore.rc)" = 0\ncat '+d+'/guard.id\n'
                            state=remote(c,check,check=False,timeout=5)
                            if state['exit_code']!=0:continue
                            snapshot=legacy_snapshot(name,c)
                            before=rec['legacy_baselines'][name]
                            # Boot, protected/config hashes and original open state.
                            require(snapshot.splitlines()[0]==before.splitlines()[0],'LEGACY_RESTORE_BOOT_CHANGED')
                            hashes=lambda text:re.findall(r'(?m)^([0-9a-f]{32,64})\s+(/\S+)$',text)
                            require(hashes(snapshot)==hashes(before),'LEGACY_RESTORE_HASH_CHANGED')
                            require(network_state(snapshot)==network_state(before),'LEGACY_RESTORE_ADDRESS_OR_ROUTE_CHANGED')
                            if name=='SXT':
                                require(remote(c,'uci changes wireless')['stdout'].strip()=='' and remote(c,'uci -q get wireless.default_radio0.encryption')['stdout'].strip()=='none','SXT_NOT_OPEN_RESTORED')
                            else:require('Encryption key:off' in snapshot and 'get_authmode:1' in snapshot and 'get_wds:0' in snapshot,'LBM5_NOT_OPEN_RESTORED')
                            pid,ticks=g['pid'],g['ticks']
                            ended=remote(c,'if test -r /proc/'+str(pid)+'/stat && test "$(awk \'{print $22}\' /proc/'+str(pid)+'/stat)" = '+str(ticks)+' && test "$(awk \'{print $3}\' /proc/'+str(pid)+'/stat)" != Z; then echo LIVE; else echo ENDED; fi')['stdout'].strip()
                            require(ended=='ENDED','LEGACY_GUARD_STILL_LIVE')
                            rec.setdefault('legacy_restoration',{})[name]=dict(status='PASS_OPEN_RF_CONFIG_PROTECTED_HASHES_GUARD_ENDED',snapshot=snapshot,ping=remote(ap,'ping -c 3 -W 2 -I br-lan '+address,check=False,timeout=8))
                            rec['legacy_restoration'][name]['guard_log']=private(name+'-guard-log.json',remote(c,'cat '+d+'/guard.log; test ! -f '+d+'/wpa.log || tail -n 25 '+d+'/wpa.log',check=False))
                            rec['legacy_restoration'][name]['RAM_guard_cleanup']=cleanup_ram_guard(name,c,g)
                            restored.add(name);save()
                        finally:c.close()
                    if restored!=set(rec['legacy_guards']):time.sleep(1)
                require(restored==set(rec['legacy_guards']),'LEGACY_OPEN_RF_RESTORATION_INCOMPLETE')
            except BaseException as e:rec['cleanup_errors'].append('legacy:'+str(e)[:180])
        if helper is not None and armed:
            if isolation_table is not None and 'bridge_isolation' in rec:
                try:rec['bridge_isolation']['final_counters']=remote(ap,'nft -j list table bridge '+isolation_table,check=False)
                except Exception as e:rec['bridge_isolation']['counter_snapshot_error']=str(e)[:120]
            try:
                rec['AP_restoration']=helper.restore(ap)
                if isolation_tables_before is not None:
                    after_tables=remote(ap,'nft list tables')['stdout']
                    require(after_tables==isolation_tables_before,'AP_BRIDGE_ISOLATION_NOT_EXACTLY_RESTORED')
                    rec['bridge_isolation']['restored_exact_tables']=True
                command='set -eu\n'+helper.header()+helper.file_guards()
                for file in ['owner','ready','guard.id','deadline','guard.sh','restore.sh','guard.log','restore.log','restored']:
                    command+='test ! -L "$D/'+file+'"; rm -f "$D/'+file+'"\n'
                command+='rmdir "$D"\ntest ! -e "$D"\necho AP_OWNED_RAM_GUARD_REMOVED\n'
                rec['AP_restoration']['RAM_guard_cleanup']=remote(ap,command)
            except BaseException as e:rec['cleanup_errors'].append('AP:'+str(e)[:160])
        if rocket is not None and rocket_id is not None:
            try:
                pid,ticks=rocket_id
                remote(rocket,'set -eu\nif test -r /proc/'+pid+'/stat && test "$(awk \'{print $22}\' /proc/'+pid+'/stat)" = '+ticks+' && test "$(awk \'{print $3}\' /proc/'+pid+'/stat)" != Z; then kill -USR1 '+pid+'; else echo OWN_GUARD_ALREADY_ENDED; fi',timeout=5)
                rocket_stream[1].channel.settimeout(12);text=rocket_stream[1].read(8193);error=rocket_stream[2].read(8193);rc=rocket_stream[1].channel.recv_exit_status()
                require(rc==0 and not error and b'ROCKET_RESTORE_RC=0' in text,'ROCKET_GUARD_RESTORE_FAILED')
                after={k:remote(rocket,cmd)['stdout'] for k,cmd in {'hashes':'md5sum '+old.HASH_FILES,'bridge':'brctl show; ifconfig br0 | head -n 4','addresses':'ip -4 addr show dev br0; route -n','rules':'ebtables -L FORWARD'}.items()}
                require(after==rocket_before,'ROCKET_EXACT_RESTORE_CHANGED')
                rec['rocket_restoration']=dict(status='PASS_EXACT_HASHES_RULES_BRIDGE_ORDERED_IPv4_ROUTES_GUARD_ENDED',evidence=after)
            except BaseException as e:rec['cleanup_errors'].append('Rocket:'+str(e)[:160])
        rec['events_artifact']=private('hostapd-events.jsonl',bytes(transcript))
        for stream in streams:
            for f in stream:
                try:f.close()
                except Exception:pass
        for c in [ap,rocket]:
            if c:c.close()
        passed=bool(rec.get('multicycle_pass') and len(rec.get('legacy_restoration',{}))==2 and rec.get('AP_restoration',{}).get('guard_ended_verified') and rec.get('rocket_restoration') and rec.get('daemon_restore_rc')=='0' and rec.get('daemon_RAM_files_removed') and rec.get('daemon_acceptance') and (plan.get('AP_path_capture') is not True or rec.get('AP_path_capture_verified')) and not rec['cleanup_errors'] and not rec['failures'])
        rec.update(status='PASS_PREPROD1_AP_ONLY_ZERO_TOUCH_FOUR_CPE_MULTICYCLE_RESTORED' if passed else 'INCOMPLETE_FOUR_CPE_PRESERVED',ended_utc=utc(),exit_code=0 if passed else 1)
        save()
        receipt=out/'receipt.json'
        final={k:v for k,v in rec.items() if k not in ['samples','events','legacy_baselines','legacy_secure_telemetry']}
        final.update(raw_receipt=str(receipt.relative_to(HERE)),raw_receipt_sha256=sha(receipt.read_bytes()),sample_count=len(rec['samples']))
        target=HERE/'preprod1_bench_result_20261022.json'
        if target.exists():
            prior=target.with_name(target.stem+'.before-'+label+'.json');require(not prior.exists(),'RESULT_HISTORY_COLLISION');os.replace(target,prior)
        target.write_text(json.dumps(final,indent=2),encoding='utf-8')
    print(json.dumps({k:rec.get(k) for k in ['status','failures','cleanup_errors','multicycle_pass','verified_session_resets','AP_restoration','rocket_restoration']},indent=2),flush=True)
    return rec['exit_code']


if __name__=='__main__':
    import sys
    if len(sys.argv)==3 and sys.argv[1]=='--execute':
        raise SystemExit(main(sys.argv[2]))
    print('PLAN_ONLY; --execute requires unique label')
