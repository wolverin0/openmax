"""Close only the ended V-owned daemon RAM after exact AP-off restoration."""
from pathlib import Path
from datetime import datetime,timezone
import json,re,hashlib
import root_four_cpe_access_20261022 as access
B=Path(__file__).resolve().parent
p=B/'preprod1_20261022_run5v/receipt.json';raw=p.read_bytes();j=json.loads(raw)
d=j['daemon_directory'];pid,ticks=j['daemon_id']
assert re.fullmatch(r'/tmp/fmx-admitter-[0-9a-f]{24}',d) and pid.isdigit() and ticks.isdigit()
assert j['ended_utc'] and j['daemon_ended_verified']['stdout'].strip()=='ENDED'
assert j['AP_restoration']['status']=='PASS_RAM_WINDOW_RESTORED_RADIO_OFF'
assert j['bridge_isolation']['restored_exact_tables'] is True
assert j['daemon_restore_rc']=='249'
rec=dict(utc=datetime.now(timezone.utc).isoformat(),status='INCOMPLETE_POSTRESTORE_CLEANUP',original_receipt_sha256=hashlib.sha256(raw).hexdigest(),original_failure_preserved=True,radio_changes=False,CPE_contact=False)
ap=access.load('root_goal_direct_link_connection_20261022.py').ap_client()
try:
 access.ap_helper().identity(ap)
 state=access.remote(ap,'ubus -t 4 call network.wireless status')
 assert json.loads(state['stdout'])['radio0']['up'] is False
 assert access.remote(ap,'iw dev')['stdout'].strip()==''
 rec['AP_radio_off_verified']=True
 command='set -eu\nD='+d+'\ntest ! -L "$D"\ntest -d "$D"\ntest "$(cat "$D/daemon.id")" = "'+pid+' '+ticks+'"\n'
 command+='if test -r /proc/'+pid+'/stat && test "$(awk \'{print $22}\' /proc/'+pid+'/stat)" = '+ticks+' && test "$(awk \'{print $3}\' /proc/'+pid+'/stat)" != Z; then exit 71; fi\n'
 command+='test "$(sha256sum "$D/admitter.sh" | awk \'{print $1}\')" = '+j['daemon_source_sha256']+'\n'
 command+='for f in admitter.sh daemon.id listener.pid ready admitted complete actions.log state.log events.jsonl stdout stderr listener.stderr restore.rc exit.rc stop.reason drop1.ack drop2.ack drop3.ack drop4.ack drop1.observed drop2.observed drop3.observed drop4.observed; do test ! -L "$D/$f"; rm -f "$D/$f"; done\nrmdir "$D"\ntest ! -e "$D"\necho V_OWNED_DAEMON_RAM_REMOVED\n'
 rec['cleanup']=access.remote(ap,command,timeout=15)
 rec['tcpdump_help']=access.remote(ap,'tcpdump --help',check=False,limit=16384)
 rec['memory']=access.remote(ap,'head -n 8 /proc/meminfo')
 rec['status']='PASS_POSTRESTORE_ENDED_OWN_DAEMON_RAM_REMOVED_AP_OFF'
finally:
 ap.close()
 (B/'preprod1_r5v_postrestore_cleanup_20261022.json').write_text(json.dumps(rec,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in rec.items() if k not in ['tcpdump_help','memory']},indent=2))
