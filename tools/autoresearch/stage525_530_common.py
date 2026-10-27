"""Bounded local receipt utilities; never imports acquisition producers."""
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.re import ground_up_release_common as c


def snapshot(root,label,maximum=32*1024*1024):
    if not isinstance(label,str) or not label or '\\' in label or ':' in label or label.startswith('/') or '..' in Path(label).parts:
        raise ValueError('repo_relative_source_required')
    root=c.local_path(root).resolve();path=c.local_path(root/label);path.relative_to(root)
    data=c.read(path,maximum=maximum)
    return data,{'path':path.relative_to(root).as_posix(),'sha256':c.sha(data),'bytes':len(data)}


def json_source(root,label):
    data,pin=snapshot(root,label)
    obj=json.loads(data,object_pairs_hook=c.pairs,parse_constant=c.invalid_constant)
    json.dumps(obj,allow_nan=False)
    if not isinstance(obj,dict):raise ValueError('receipt_object_required')
    return obj,pin


def finish(root,stage,script,out,doc,text,result,sources):
    root=c.local_path(root)
    for source in sources:
        if snapshot(root,source['path'])[1]!=source:raise ValueError('input_drift:'+source['path'])
    c.write_doc(root/doc,text)
    result.update(stage=str(stage)+'A',task_id=f'T-S{stage}A-OFFLINE-RECONCILIATION',static_sources=sources,
        source_binding_meaning='Held current bytes, not authenticated historical executed-source or native acquisition provenance.',
        implementation=c.binding(root/script,root),
        analysis_dependencies=[c.binding(root/p,root) for p in ('tools/autoresearch/stage525_530_common.py',
            'tools/re/ground_up_release_common.py','controller/stage18_wmi_rate_schedule_and_sub20mhz_controller.py')],
        boundary={'target_access':False,'network_access':False,'target_commands_executed':False,
                  'physical_acceptance':False,'flash_approved':False},
        outputs={doc:c.binding(root/doc,root)})
    c.write_json(root/out,result);return result


def number(value,label,low=0,high=1e12):return c.finite(value,label,low,high)


def delta(a,b):return 100*(b/a-1) if a>0 else None
