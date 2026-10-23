"""Close only AA's known Rocket/AP/stagers after legacy restoration timed out."""
import ast
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'preprod1_r5aa_abort_restore_20261022.py'
spec = importlib.util.spec_from_file_location('_aa_known_close', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
prior = json.loads(SOURCE.with_suffix('.json').read_text(encoding='utf8'))
m.require(prior.get('ended_utc') and prior['status']=='INCOMPLETE_ABORT_RESTORATION', 'PRIOR_RESTORER_MUST_BE_ENDED')
m.require(set(prior.get('legacy_restoration', {}))=={'SXT'}, 'PARTIAL_STATE_CHANGED_REASSESS')
target = HERE / 'preprod1_r5aa_abort_final_closure_20261022.json'
m.require(not target.exists(), 'CLOSURE_ALREADY_EXISTS')
rec = json.loads((m.RUN/'receipt.json').read_text(encoding='utf8'))
record = dict(status='INCOMPLETE_KNOWN_DEVICE_CLOSURE', started_utc=m.utc(),
              source_sha256=m.sha(Path(__file__).read_bytes()),
              reused_cleanup_source_sha256=m.sha(SOURCE.read_bytes()),
              prior_restore_sha256=m.sha(SOURCE.with_suffix('.json').read_bytes()),
              M5_restoration='UNKNOWN_NO_RF_ACCESS_OPERATOR_ETHERNET_REQUIRED', events=[], errors=[])
access = m.load('root_four_cpe_access_20261022.py')
helper = access.ap_helper()
helper.TOKEN = rec['bridge_isolation']['owner']
helper.DIR = rec['AP_initial']['remote_ram']
helper.checked = lambda c, command, timeout=25: m.remote(c, command, timeout=timeout)['stdout'].encode()
guard = (m.RUN/'executed-source/AP_guard.sh').read_text(encoding='utf8').encode()
restore = (m.RUN/'executed-source/AP_restore.sh').read_text(encoding='utf8').encode()
helper.file_guards = lambda: ('test ! -L "$D/guard.sh"; test ! -L "$D/restore.sh"\n'
    'test "$(sha256sum "$D/guard.sh" | cut -d\' \' -f1)" = '+m.sha(guard)+'\n'
    'test "$(sha256sum "$D/restore.sh" | cut -d\' \' -f1)" = '+m.sha(restore)+'\n')
# Reuse the exact inspected cleanup statements. Freeze the selected executable
# source too: no legacy mutation, experiment or acceptance statements are reused.
tree = ast.parse(SOURCE.read_text(encoding='utf8'))
main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name=='main')
body = next(n for n in main.body if isinstance(n, ast.Try)).body
start = next(i for i,n in enumerate(body) if isinstance(n, ast.Assign)
             and ast.unparse(n.targets[0])=='rocket')
end = next(i for i,n in enumerate(body) if i>start and isinstance(n, ast.Assign)
           and ast.unparse(n.targets[0])=="record['status']")
selected = ast.Module(body=body[start:end], type_ignores=[])
frozen = HERE / 'preprod1_r5aa_abort_known_cleanup_source_20261022.py'
frozen.write_text(ast.unparse(selected)+'\n', encoding='utf8')
record['selected_source_sha256'] = m.sha(frozen.read_bytes())
ap = rocket = None
namespace = vars(m).copy()
try:
    ap = access.load('root_goal_direct_link_connection_20261022.py').ap_client()
    namespace.update(access=access, helper=helper, rec=rec, record=record, ap=ap,
                     rocket=None, rows=prior['unstarted_staged_trace_inventory'])
    exec(compile(selected, str(frozen), 'exec'), namespace)
    record['status']='PASS_ROCKET_STAGED_RAM_AP_OFF_CLOSED_M5_UNKNOWN'
except BaseException as error:
    record['errors'].append(dict(error_type=type(error).__name__, gate=str(error)[:160]))
finally:
    for client in [namespace.get('rocket'), ap]:
        if client:
            client.close()
    record['ended_utc']=m.utc()
    with target.open('x', encoding='utf8') as f:
        json.dump(record,f,indent=2)
print(json.dumps({k:record[k] for k in ['status','errors','M5_restoration']}))
raise SystemExit(0 if record['status'].startswith('PASS_') else 1)
