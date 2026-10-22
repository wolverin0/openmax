"""FMX-0017: AP-local daemon and controlled-load four-device, RAM-only open/WPA2/open bench acquisition."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shlex
import time

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
end=$(($(cut -d. -f1 /proc/uptime)+240))
printf '%s\n' "$end" > "$D/deadline"
: > "$D/ready"
sleep 2
''' + apply + '''
: > "$D/applied"
while test "$(cut -d. -f1 /proc/uptime)" -lt "$end"; do sleep 1; done
'''


def main(label):
    out = HERE / ('fmx0017_' + label)
    out.mkdir(mode=0o700, exist_ok=False)
    intake = json.loads(INTAKE.read_text(encoding='utf-8'))
    require(intake['status']=='PASS_OPEN_RF_LEGACY_IDENTITY_CONFIG_INTAKE', 'INTAKE_NOT_ACCEPTED')
    rec = dict(experiment='FMX-0017', status='INCOMPLETE_FOUR_CPE', started_utc=utc(),
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
    armed = False; rocket_stream = None; rocket_id = None
    legacy_clients = {}; old = access.load('root_multi_cpe_trial_20261022.py')
    streams = []; listener = None; event_buffer = ''; transcript = bytearray()
    interface = 'phy0-ap0'; obj = shlex.quote('hostapd.'+interface)
    whole_end = time.monotonic()+430; legacy_end = None
    rocket_before = None
    daemon_dir = None; daemon_id = None
    setup_stream = None; setup_id = None; setup_dir = None; setup_token = None
    setup_safe_for_restore = True
    daemon_source = (HERE.parent.parent / 'tools/bench/fmx_admitter.sh').read_bytes()
    require(b'\r' not in daemon_source and daemon_source.startswith(b'#!/bin/sh\n'), 'DAEMON_SOURCE_REQUIRES_LF')
    rec['daemon_source_sha256'] = sha(daemon_source)
    rec['load_recipe'] = dict(count=6001, interval_seconds=.01, payload_bytes=1200, request_payload_target_mbps=3.84, combined_echo_payload_target_mbps=7.68, saturation_claim=False)
    rec['autonomy_scope'] = 'AP-local IE decisions; one native timed XC scan/enable setup; Python observes only'
    rec['load_stream_starts'] = {}

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
        rec['legacy_guards'][name]={'directory':directory,'source_sha256':sha(script.encode()),'ttl_seconds':240,'intent_recorded':True}
        save();remote(c,cmd,timeout=8)
        end=time.monotonic()+1.5
        while True:
            x=remote(c,'test -f '+directory+'/ready && cat '+directory+'/guard.id '+directory+'/deadline',check=False,timeout=2)
            if x['exit_code']==0: break
            require(time.monotonic()<end,'LEGACY_GUARD_READY_TIMEOUT');time.sleep(.1)
        values=x['stdout'].split();require(len(values)==3 and all(v.isdigit() for v in values),'LEGACY_GUARD_ID_PROTOCOL')
        rec['legacy_guards'][name].update(pid=int(values[0]),ticks=int(values[1]),deadline_uptime=int(values[2]),host_armed=time.monotonic())
        if legacy_end is None: legacy_end=time.monotonic()+215
        save()
    def capture_start(mac,count):
        counts,_=station_snapshot();require(mac in counts,'TRAFFIC_STATION_MISSING')
        device=counts[mac]['interface']
        if mac in [WA,XC]:
            require(device.startswith(interface+'.sta'),'AC_WDS_CHILD_MISSING')
            address=old.LL[mac];command='ping -6 -c '+str(count)+' -s 1200 -i 0.01 -W 2 -I br-lan '+address
            filt='icmp6 and host '+address+' and (ip6[40] == 128 or ip6[40] == 129)';proto='ICMP6'
        else:
            address=access.DEVICES[LABELS[mac]][0];command='ping -c '+str(count)+' -s 1200 -i 0.01 -W 2 -I br-lan '+address
            filt='icmp and host '+address+' and (icmp[0] == 8 or icmp[0] == 0)';proto='ICMP'
        cap=ap.exec_command('exec tcpdump -p -n -l -tt -s 128 -c '+str(128)+' -i '+device+' '+shlex.quote(filt),timeout=90)
        cap[0].close();streams.append(cap);time.sleep(.15)
        require(not cap[1].channel.exit_status_ready(),'TRAFFIC_CAPTURE_START_FAILED')
        return dict(mac=mac,interface=device,address=address,command=command,count=count,proto=proto,cap=cap)
    def ping_start(item):
        wrapper="printf '__FMX_START__%s\n' \"$(cut -d' ' -f1 /proc/uptime)\"\n"+item['command']+"\nrc=$?\nprintf '__FMX_END__%s\n' \"$(cut -d' ' -f1 /proc/uptime)\"\nexit \"$rc\""
        p=ap.exec_command('exec /bin/sh -c '+shlex.quote(wrapper),timeout=85);p[0].close();streams.append(p);item['ping']=p;item['start_mono']=time.monotonic();rec['load_stream_starts'][LABELS[item['mac']]]=item['start_mono']
    def ping_finish(item):
        p=item['ping'];text=p[1].read(1048577).decode();err=p[2].read(8193).decode();rc=p[1].channel.recv_exit_status()
        channel=item['cap'][1].channel;data=bytearray();errors=bytearray();end=time.monotonic()+3
        while time.monotonic()<end:
            while channel.recv_ready():data.extend(channel.recv(4096))
            while channel.recv_stderr_ready():errors.extend(channel.recv_stderr(4096))
            require(len(data)<=65536 and len(errors)<=8192,'CAPTURE_BOUND')
            if channel.exit_status_ready() and not channel.recv_ready(): break
            time.sleep(.05)
        capture_rc=channel.recv_exit_status() if channel.exit_status_ready() else None
        captext=data.decode(errors='replace');pattern=item['proto']+r',? echo (request|reply), id (\d+), seq (\d+)'
        messages=re.findall(pattern,captext);req={(i,s) for kind,i,s in messages if kind=='request'};replies={(i,s) for kind,i,s in messages if kind=='reply'}
        stats=re.search(r'(\d+) packets transmitted, (\d+) (?:packets )?received',text)
        result=dict(mac=item['mac'],interface=item['interface'],stdout=text,stderr=err,exit_code=rc,capture_exit_code=capture_rc,
                    transmitted=int(stats[1]) if stats else None,received=int(stats[2]) if stats else None,
                    captured_requests=len(req),captured_replies=len(replies),paired=len(req&replies),
                    capture=private(LABELS[item['mac']]+'-capture.json',dict(stdout=captext,stderr=errors.decode(errors='replace'))))
        import math
        rtts=sorted(float(x) for x in re.findall(r'time[=<]([0-9.]+) ms',text))
        bounds=[re.search(r'__FMX_'+key+r'__([0-9.]+)',text) for key in ['START','END']]
        result['ap_start_uptime'],result['ap_end_uptime']=[float(v[1]) if v else None for v in bounds]
        result['ap_elapsed_seconds']=(result['ap_end_uptime']-result['ap_start_uptime']) if all(bounds) else 0
        result['achieved_receive_payload_mbps']=result['received']*1200*8/1e6/result['ap_elapsed_seconds'] if result['ap_elapsed_seconds']>0 and stats else 0
        result['rtt_samples']=len(rtts)
        result['rtt_ms']={str(q):rtts[max(0,math.ceil(q*len(rtts))-1)] if rtts else None for q in [.5,.95,.99]}
        result['request_payload_mbits_delivered']=result['received']*1200*8/1e6 if stats else None
        finite=all(math.isfinite(x) and x>=0 for x in rtts) and math.isfinite(result['ap_elapsed_seconds'])
        result['pass']=bool(finite and rc==0 and stats and int(stats[1])==item['count'] and 0<=int(stats[2])<=int(stats[1]) and int(stats[2])/int(stats[1])>=.99 and len(rtts)>=int(stats[2]) and result['ap_elapsed_seconds']>=60 and capture_rc==0 and len(req&replies)>=32)

        return result

    try:
        save();ap=access.load('root_goal_direct_link_connection_20261022.py').ap_client()
        rocket=access.load('root_step1c_rocket_observer_20261021.py').connect()
        rocket_before={k:remote(rocket,cmd)['stdout'] for k,cmd in {
            'hashes':'md5sum '+old.HASH_FILES,'bridge':'brctl show; ifconfig br0 | head -n 4',
            'addresses':'ip -4 addr show dev br0; route -n','rules':'ebtables -L FORWARD'}.items()}
        require([row.split()[0] for row in rocket_before['hashes'].splitlines()[:3]]==[old.CFG,old.CFG,old.AUTO],'ROCKET_BASELINE_CHANGED')
        require(not re.search(r'-i (?:ath0 -o eth0|eth0 -o ath0) -j DROP',rocket_before['rules']),'ROCKET_MATCHING_RULE_EXISTS')
        rec['rocket_baseline']=rocket_before
        rocket_stream=rocket.exec_command('exec /bin/sh -c '+shlex.quote(old.rocket_guard()),timeout=8);rocket_stream[0].close();streams.append(rocket_stream)
        first=rocket_stream[1].readline().strip();require(re.fullmatch(r'READY \d+ \d+',first),'ROCKET_GUARD_NOT_READY')
        rocket_id=first.split()[1:]
        for key,value in [('ssid','"FuturaMAX-LAB"'),('psk','"FuturaMAX2026"'),('key_mgmt','WPA-PSK'),('proto','RSN'),('pairwise','CCMP'),('group','CCMP'),('scan_freq','5180')]:
            require(remote(rocket,'wpa_cli -i ath0 set_network 0 '+key+' '+shlex.quote(value))['stdout'].strip()=='OK','ROCKET_WPA_SET_'+key)
        helper=access.ap_helper();rec['AP_initial']=helper.arm(ap);armed=True
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
        # One staged native XC setup: no external decision loop controls admission.
        require(remote(rocket,'wpa_cli -i ath0 disable_network 0')['stdout'].strip()=='OK','XC_DISABLE_FAILED')
        daemon_dir='/tmp/fmx-admitter-'+secrets.token_hex(12)
        cmd='set -eu\numask 077\ntest ! -e '+daemon_dir+'\nmkdir '+daemon_dir+'\nprintf %s '+shlex.quote(daemon_source.decode())+' > '+daemon_dir+'/admitter.sh\n'
        cmd+='test "$(sha256sum '+daemon_dir+'/admitter.sh | awk \'{print $1}\')" = '+sha(daemon_source)+'\n'
        cmd+='/bin/sh '+daemon_dir+'/admitter.sh '+daemon_dir+' </dev/null >'+daemon_dir+'/stdout 2>'+daemon_dir+'/stderr &\necho DISPATCHED\n'
        rec['daemon_directory']=daemon_dir;save();remote(ap,cmd)
        require(remote(ap,'sleep 1; test -f '+daemon_dir+'/ready; cat '+daemon_dir+'/daemon.id')['exit_code']==0,'DAEMON_NOT_READY')
        daemon_id=remote(ap,'cat '+daemon_dir+'/daemon.id')['stdout'].split()
        rec['daemon_id']=daemon_id;save()
        setup_token=secrets.token_hex(12);setup_dir='/tmp/fmx0017-xc-'+setup_token
        remote(rocket,'set -eu\numask 077\ntest ! -e '+setup_dir+'\nmkdir '+setup_dir+'\nprintf %s '+setup_token+' > '+setup_dir+'/owner\n: > '+setup_dir+'/allow')
        rec['XC_native_setup_directory']=setup_dir;setup_safe_for_restore=False;save()
        xc_script='D='+shlex.quote(setup_dir)+'\n'+"""set -eu
trap '' HUP
trap 'exit 0' USR1 TERM INT
printf '%s %s\n' "$$" "$(awk '{print $22}' /proc/$$/stat)" > "$D/setup.id"
printf 'READY %s %s\n' "$$" "$(awk '{print $22}' /proc/$$/stat)"
test -f "$D/allow" || exit 0
wait_for() {
 end=$(($(cut -d. -f1 /proc/uptime)+$1))
 while test "$(cut -d. -f1 /proc/uptime)" -lt "$end"; do sleep 1; done
}
wait_for 5
test -f "$D/allow" || exit 0
wpa_cli -i ath0 bss_flush 0 | grep -q '^OK$'
wpa_cli -i ath0 scan | grep -q '^OK$'
wait_for 60
test -f "$D/allow" || exit 0
wpa_cli -i ath0 scan_results | grep -i '^18:e8:29:74:55:a2'
test -f "$D/allow" || exit 0
wpa_cli -i ath0 enable_network 0 | grep -q '^OK$'
test -f "$D/allow" || exit 0
wpa_cli -i ath0 reassociate | grep -q '^OK$'
echo XC_NATIVE_SETUP_DONE
"""
        setup_stream=rocket.exec_command('exec /bin/sh -c '+shlex.quote(xc_script),timeout=75)
        setup_stream[0].close();streams.append(setup_stream)
        ready=setup_stream[1].readline().strip();require(re.fullmatch(r'READY \d+ \d+',ready),'XC_SETUP_ID_MISSING')
        setup_id=ready.split()[1:];rec['XC_native_setup_id']=setup_id
        rec['XC_native_setup_sha256']=sha(xc_script.encode())
        # Observation only; the daemon owns vendor-IE decisions from here.
        all_end=min(legacy_end-88,time.monotonic()+100)
        while time.monotonic()<all_end:
            events();rows=clients();rec['last_auth_flags']=rows;save()
            if all(good(mac,rows.get(mac,{})) for mac in MACS):break
            time.sleep(.2)
        require(all(good(mac,clients().get(mac,{})) for mac in MACS),'FOUR_SIMULTANEOUS_AUTHORIZATION_NOT_REACHED')
        for n in range(30):
            if remote(ap,'test -f '+daemon_dir+'/admitted',check=False)['exit_code']==0:break
            time.sleep(.1)
        require(remote(ap,'test -f '+daemon_dir+'/admitted',check=False)['exit_code']==0,'DAEMON_NOT_ADMITTED')
        rec['XC_native_setup'] = dict(stdout=setup_stream[1].read(16385).decode(),stderr=setup_stream[2].read(8193).decode(),exit_code=setup_stream[1].channel.recv_exit_status())
        require(rec['XC_native_setup']['exit_code']==0,'XC_NATIVE_SETUP_FAILED')
        # Self-reported CPE telemetry supplements the AP's per-station view.
        for name in access.DEVICES:
            c=legacy_connect(name);legacy_clients[name]=c
            rec.setdefault('legacy_secure_telemetry',{})[name]=legacy_snapshot(name,c)
        require(legacy_end-time.monotonic()>80,'INSUFFICIENT_GUARDED_MEASUREMENT_BUDGET')
        for mac in MACS:
            target='ping -6 -c 3 -W 2 -I br-lan '+old.LL[mac] if mac in [WA,XC] else 'ping -c 3 -W 2 -I br-lan '+access.DEVICES[LABELS[mac]][0]
            rec.setdefault('pre_stream_probes',{})[LABELS[mac]]=remote(ap,target,check=False,timeout=8)
        items=[capture_start(mac,6001) for mac in MACS]
        for item in items:ping_start(item)
        begin=time.monotonic();first,raw=station_snapshot();previous=first
        rec['first_station_dumps']=private('first-station-dumps.json',raw)
        while True:
            require(time.monotonic()<legacy_end-15,'SECURE_WINDOW_DEADLINE')
            pid,ticks=daemon_id
            require(remote(ap,'test -r /proc/'+pid+'/stat && test \"$(awk \'{print $22}\' /proc/'+pid+'/stat)\" = '+ticks+' && test \"$(awk \'{print $3}\' /proc/'+pid+'/stat)\" != Z',check=False)['exit_code']==0,'DAEMON_ENDED_DURING_LOAD')
            events();rows=clients();counts,raw=station_snapshot();now=time.monotonic()
            require(all(good(mac,rows.get(mac,{})) for mac in MACS),'FOUR_WAY_ASSOCIATION_LOST')
            require(set(counts)==set(MACS),'FOUR_STATION_DUMP_MISSING')
            for mac in MACS:
                require(all(counts[mac][key]>=previous[mac][key] for key in ['connected_seconds','rx_bytes','tx_bytes']),'STATION_COUNTER_OR_SESSION_RESET')
            rec['samples'].append(dict(mono=now,utc=utc(),clients=rows,stations=counts,
                                       raw=private('station-dumps-'+str(len(rec['samples'])).zfill(3)+'.json',raw)))
            previous=counts;save()
            if now-begin>=60:break
            time.sleep(1)
        rec['four_way_stability_seconds']=now-begin;rec['four_authorized_60s']=True
        rec['pings']={LABELS[item['mac']]:ping_finish(item) for item in items}
        rec['load_stream_overlap_seconds']=min(p['ap_end_uptime'] for p in rec['pings'].values())-max(p['ap_start_uptime'] for p in rec['pings'].values())
        require(rec['load_stream_overlap_seconds']>=59,'INSUFFICIENT_LOAD_STREAM_OVERLAP')
        rec['radio_traffic_pass']=all(p['pass'] for p in rec['pings'].values())
        rec['all_radio_counters_advanced']=all(previous[mac]['rx_bytes']>first[mac]['rx_bytes'] and previous[mac]['tx_bytes']>first[mac]['tx_bytes'] for mac in MACS)
        rec['load_collection_finished_mono']=time.monotonic()
        rec['load_actual_host_elapsed_seconds']={name:rec['load_collection_finished_mono']-t for name,t in rec['load_stream_starts'].items()}
        rec['acquisition_complete']=True
    except BaseException as e:
        rec['failures'].append(dict(type=type(e).__name__,gate=str(e)[:180]))
        if ap is not None and armed:
            try:
                rec['failure_AP_clients']=clients();counts,raw=station_snapshot();rec['failure_station_snapshot']=private('failure-station-dumps.json',raw)
            except Exception:pass
    finally:
        # Cancel/verify the owned deferred XC task before any restoration.
        if rocket is not None and setup_dir is not None:
            try:
                fence='set -eu\nD='+shlex.quote(setup_dir)+'\ntest -d "$D"; test ! -L "$D"; test ! -L "$D/owner"; test "$(cat "$D/owner")" = '+setup_token+'\nrm -f "$D/allow"\nif test -f "$D/setup.id"; then cat "$D/setup.id"; else echo NEVER_PASSED_GATE; fi'
                state=remote(rocket,fence)['stdout'].split()
                if setup_id is None and len(state)==2 and all(v.isdigit() for v in state):setup_id=state
                if setup_id is None:
                    require(state==['NEVER_PASSED_GATE'],'XC_SETUP_UNCERTAIN_ID')
                    # ID is written before any allow check. No ID + fence removed
                    # proves a delayed process cannot reach a modifying command.
                    setup_safe_for_restore=True
                    rec['XC_native_setup_ended']={'status':'FENCED_BEFORE_FIRST_COMMAND'}
                else:
                    pid,ticks=setup_id
                    cmd='set -eu\nif test -r /proc/'+pid+'/stat && test "$(awk \'{print $22}\' /proc/'+pid+'/stat)" = '+ticks+' && test "$(awk \'{print $3}\' /proc/'+pid+'/stat)" != Z; then kill -USR1 '+pid+'; fi\n'
                    cmd+='for n in 1 2 3 4 5; do if test ! -r /proc/'+pid+'/stat || test "$(awk \'{print $22}\' /proc/'+pid+'/stat)" != '+ticks+' || test "$(awk \'{print $3}\' /proc/'+pid+'/stat)" = Z; then echo ENDED; exit 0; fi; sleep 1; done; exit 78'
                    rec['XC_native_setup_ended']=remote(rocket,cmd,timeout=8)
                    setup_safe_for_restore=True
                if setup_safe_for_restore:
                    remote(rocket,'set -eu\nD='+setup_dir+'\ntest ! -L "$D/setup.id"; rm -f "$D/setup.id" "$D/owner"; rmdir "$D"')
                    rec['XC_native_setup_RAM_removed']=True
            except BaseException as e:rec['cleanup_errors'].append('XC_SETUP:'+str(e)[:160])
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
                data={name:remote(ap,'cat '+daemon_dir+'/'+name,check=False)['stdout'] for name in ['actions.log','events.jsonl','stderr','listener.stderr','restore.rc','exit.rc','stop.reason']}
                rec['daemon_evidence']=private('daemon-evidence.json',data)
                rec['daemon_restore_rc']=data['restore.rc'].strip()
                require(rec['daemon_restore_rc']=='0' and rec.get('daemon_ended_verified'),'DAEMON_CLEAR_OR_END_FAILED')
                # Admission/error validation affects acceptance, not safe ended-file cleanup.
                rec['daemon_acceptance']=bool(data['exit.rc'].strip()=='0' and data['stop.reason'].strip()=='operator_signal' and 'FOUR_ADMITTED' in data['actions.log'] and 'ASSOCIATION_LOST' not in data['actions.log'] and not data['stderr'] and not data['listener.stderr'])
                remote(ap,'set -eu\nD='+daemon_dir+'\ntest ! -L "$D"\ntest "$(sha256sum "$D/admitter.sh" | awk \'{print $1}\')" = '+sha(daemon_source)+'\nfor f in admitter.sh daemon.id listener.pid ready admitted actions.log events.jsonl stdout stderr listener.stderr restore.rc exit.rc stop.reason; do test ! -L "$D/$f"; rm -f "$D/$f"; done\nrmdir "$D"')
                rec['daemon_RAM_files_removed']=True
            except BaseException as e:rec['cleanup_errors'].append('Daemon:'+str(e)[:160])
        # Try explicit signal, otherwise leave each independent240s guard to
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
                restored=set();restore_end=min(whole_end,time.monotonic()+260)
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
            try:
                rec['AP_restoration']=helper.restore(ap)
                command='set -eu\n'+helper.header()+helper.file_guards()
                for file in ['owner','ready','guard.id','deadline','guard.sh','restore.sh','guard.log','restore.log','restored']:
                    command+='test ! -L "$D/'+file+'"; rm -f "$D/'+file+'"\n'
                command+='rmdir "$D"\ntest ! -e "$D"\necho AP_OWNED_RAM_GUARD_REMOVED\n'
                rec['AP_restoration']['RAM_guard_cleanup']=remote(ap,command)
            except BaseException as e:rec['cleanup_errors'].append('AP:'+str(e)[:160])
        if rocket is not None and rocket_id is not None and setup_safe_for_restore:
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
        passed=bool(rec.get('four_authorized_60s') and rec.get('radio_traffic_pass') and rec.get('all_radio_counters_advanced')
                    and len(rec.get('legacy_restoration',{}))==2 and rec.get('AP_restoration',{}).get('guard_ended_verified')
                    and rec.get('rocket_restoration') and rec.get('daemon_restore_rc')=='0' and rec.get('daemon_RAM_files_removed') and rec.get('daemon_acceptance') and rec.get('XC_native_setup_ended') and rec.get('XC_native_setup_RAM_removed') and not rec['cleanup_errors'] and not rec['failures'])
        rec.update(status='PASS_AP_LOCAL_ADMISSION_FOUR_CPE_CONTROLLED_LOAD_RESTORED' if passed else 'INCOMPLETE_FOUR_CPE_PRESERVED',ended_utc=utc(),exit_code=0 if passed else 1)
        save()
        receipt=out/'receipt.json'
        final={k:v for k,v in rec.items() if k not in ['samples','events','legacy_baselines','legacy_secure_telemetry']}
        final.update(raw_receipt=str(receipt.relative_to(HERE)),raw_receipt_sha256=sha(receipt.read_bytes()),sample_count=len(rec['samples']))
        target=HERE/'fmx_0017_bench_result_20261022.json'
        if target.exists():
            prior=target.with_name(target.stem+'.before-'+label+'.json');require(not prior.exists(),'RESULT_HISTORY_COLLISION');os.replace(target,prior)
        target.write_text(json.dumps(final,indent=2),encoding='utf-8')
    print(json.dumps({k:rec.get(k) for k in ['status','failures','cleanup_errors','four_way_stability_seconds','radio_traffic_pass','AP_restoration','rocket_restoration']},indent=2),flush=True)
    return rec['exit_code']


if __name__=='__main__':
    import sys
    if len(sys.argv)==3 and sys.argv[1]=='--execute':raise SystemExit(main(sys.argv[2]))
    print('PLAN_ONLY; --execute requires unique run label')
