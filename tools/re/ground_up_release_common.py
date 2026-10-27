"""Local evidence utilities for353..358; no acquisition or device execution."""
from __future__ import annotations
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from controller.stage18_wmi_rate_schedule_and_sub20mhz_controller import local_path


def sha(data):return hashlib.sha256(data).hexdigest()


def read(path,expected=None,maximum=64*1024*1024):
    path=local_path(path)
    if path.stat().st_size>maximum:raise ValueError('input_size_limit')
    data=path.read_bytes()
    if expected is not None and sha(data)!=expected:raise ValueError('source_hash_mismatch:'+path.name)
    return data


def binding(path,root=ROOT,expected=None):
    path=local_path(path);data=read(path,expected)
    try:label=path.relative_to(local_path(root)).as_posix()
    except ValueError:label=path.as_posix()
    return {'path':label,'sha256':sha(data),'bytes':len(data)}


def pairs(items):
    obj={}
    for k,v in items:
        if k in obj:raise ValueError('duplicate_json_key:'+k)
        obj[k]=v
    return obj


def invalid_constant(value):raise ValueError('nonfinite_json:'+value)


def load(path):
    obj=json.loads(read(path),object_pairs_hook=pairs,parse_constant=invalid_constant)
    json.dumps(obj,allow_nan=False)
    return obj


def finite(value,label,low=0,high=1e12):
    try:ok=type(value) in (int,float) and math.isfinite(value) and low<=value<=high
    except OverflowError:ok=False
    if not ok:raise ValueError('invalid_'+label)
    return float(value)


def integer(value,label,low,high):
    if type(value) is not int or not low<=value<=high:raise ValueError('invalid_'+label)
    return value


def write_json(path,obj):
    path=local_path(path);path.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n'
    fd,name=tempfile.mkstemp(prefix=path.name+'.',suffix='.tmp',dir=path.parent)
    temp=Path(name)
    try:
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as stream:stream.write(text)
        temp.replace(path)
    finally:
        if temp.exists():temp.unlink()


def write_doc(path,text):
    lines=text.splitlines()
    if len(lines)>=220 or not re.fullmatch(r'<!-- doc-head: [^<>]+ -->',lines[0]):raise ValueError('doc_contract')
    if text.count('<!-- doc-head:')!=1 or text.count('<!-- /doc-head -->')!=1:raise ValueError('doc_head_pair')
    if '<!-- /doc-head -->' not in lines[1:8]:raise ValueError('doc_summary_budget')
    path=local_path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text.rstrip()+'\n',encoding='utf-8',newline='\n')


def anchors(path,needles,root=ROOT):
    data=read(path);lines=data.decode('utf-8').splitlines();rows=[]
    for needle in needles:
        hits=[i+1 for i,line in enumerate(lines) if needle in line]
        if not hits:raise ValueError('missing_source_anchor:'+needle)
        rows.append({'token':needle,'line_numbers':hits})
    return {**binding(path,root),'anchors':rows}


def elf_symbols(path,pattern,root=ROOT):
    from elftools.elf.elffile import ELFFile
    import capstone
    data=read(path);elf=ELFFile(io.BytesIO(data));table=elf.get_section_by_name('.symtab')
    if table is None:raise ValueError('ELF_symtab_missing')
    if elf.elfclass!=32 or elf.get_machine_arch()!='MIPS':raise ValueError('expected_ELF32_MIPS')
    mode=capstone.CS_MODE_MIPS32|(capstone.CS_MODE_LITTLE_ENDIAN if elf.little_endian else capstone.CS_MODE_BIG_ENDIAN)
    decoder=capstone.Cs(capstone.CS_ARCH_MIPS,mode);symbols=[]
    for sym in table.iter_symbols():
        if not re.search(pattern,sym.name) or not isinstance(sym['st_shndx'],int) or not sym['st_size']:continue
        section=elf.get_section(sym['st_shndx']);offset=sym['st_value']-section['sh_addr'];size=sym['st_size']
        if not 0<=offset<=section['sh_size']-size:raise ValueError('symbol_bounds')
        blob=section.data()[offset:offset+size]
        row={'name':sym.name,'type':sym['st_info']['type'],'section':section.name,
             'section_offset':offset,'file_offset':section['sh_offset']+offset,'bytes':size,'sha256':sha(blob),
             'first_32_bytes_hex':blob[:32].hex()}
        if sym['st_info']['type']=='STT_FUNC':
            row['first_instructions']=[{'address':ins.address,'mnemonic':ins.mnemonic,'operands':ins.op_str}
                                       for ins in decoder.disasm(blob[:64],sym['st_value'])]
        symbols.append(row)
    return {**binding(path,root),'endianness':'little' if elf.little_endian else 'big','symbols':symbols,
            'qualification':'STATIC_SYMBOL_BYTES_ONLY_NOT_PROVEN_RUNTIME_CALL_CHAIN'}
