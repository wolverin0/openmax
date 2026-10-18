"""Offline, read-only ELF evidence extraction; never executes target firmware."""
import argparse
import hashlib
import io
import json
import re
from pathlib import Path

from capstone import Cs, CS_ARCH_ARM, CS_ARCH_MIPS, CS_MODE_ARM, CS_MODE_MIPS32, CS_MODE_BIG_ENDIAN, CS_MODE_LITTLE_ENDIAN
from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection


class Probe:
    def __init__(self, path):
        self.path = Path(path)
        self.raw = self.path.read_bytes()
        self.elf = ELFFile(io.BytesIO(self.raw))
        self.syms = self.elf.get_section_by_name('.symtab')
        self.symbols = list(self.syms.iter_symbols()) if self.syms else []
        mode = CS_MODE_LITTLE_ENDIAN if self.elf.little_endian else CS_MODE_BIG_ENDIAN
        if self.elf['e_machine'] == 'EM_MIPS':
            self.cs = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | mode)
        else:
            self.cs = Cs(CS_ARCH_ARM, CS_MODE_ARM | mode)
        self.relocs = {}
        for sec in self.elf.iter_sections():
            if isinstance(sec, RelocationSection):
                st = self.elf.get_section(sec['sh_link'])
                for r in sec.iter_relocations():
                    sym = st.get_symbol(r['r_info_sym'])
                    sn = self.elf.get_section(sym['st_shndx']).name if isinstance(sym['st_shndx'], int) else sym['st_shndx']
                    self.relocs[(sec['sh_info'], r['r_offset'])] = f"{sym.name} {sn}+0x{sym['st_value']:x} type={r['r_info_type']}"

    def metadata(self):
        return dict(path=str(self.path), size=len(self.raw), sha256=hashlib.sha256(self.raw).hexdigest(), md5=hashlib.md5(self.raw).hexdigest(), machine=self.elf['e_machine'], endian='LE' if self.elf.little_endian else 'BE', sections=[dict(name=s.name, offset=s['sh_offset'], address=s['sh_addr'], size=s['sh_size']) for s in self.elf.iter_sections() if s.name in ('.text', '.data', '.rodata', '.rel.text')])

    def list_symbols(self, pattern):
        return [dict(name=s.name, value=hex(s['st_value']), size=s['st_size'], section=self.elf.get_section(s['st_shndx']).name if isinstance(s['st_shndx'], int) else s['st_shndx']) for s in self.symbols if re.search(pattern, s.name, re.I)]

    def dump(self, secname, start, size):
        if self.elf.get_section_by_name(secname) is None:
            seg=next(s for s in self.elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_vaddr']<=start<s['p_vaddr']+s['p_filesz'])
            off=seg['p_offset']+start-seg['p_vaddr']
            return [f"VA=0x{i.address:x} file=0x{off+i.address-start:x} {i.bytes.hex()} {i.mnemonic} {i.op_str}" for i in self.cs.disasm(self.raw[off:off+size],start)]
        idx = next(i for i,s in enumerate(self.elf.iter_sections()) if s.name == secname)
        sec = self.elf.get_section(idx)
        off = start - sec['sh_addr']
        lines=[]
        for ins in self.cs.disasm(sec.data()[off:off+size], start):
            reloc=self.relocs.get((idx, ins.address), '')
            lines.append(f"{secname}+0x{ins.address:x} file=0x{sec['sh_offset']+ins.address-sec['sh_addr']:x} {ins.bytes.hex()} {ins.mnemonic} {ins.op_str}" + (f" ; {reloc}" if reloc else ''))
        return lines

    def symbol(self, name):
        s = next(s for s in self.symbols if s.name == name)
        sec = self.elf.get_section(s['st_shndx'])
        return self.dump(sec.name, s['st_value'], s['st_size'])


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('file')
    p.add_argument('--symbols')
    p.add_argument('--symbol')
    p.add_argument('--section', default='.text')
    p.add_argument('--start', type=lambda x:int(x,0))
    p.add_argument('--size', type=lambda x:int(x,0), default=128)
    a=p.parse_args()
    e=Probe(a.file)
    if a.symbols:
        print(json.dumps(e.list_symbols(a.symbols),indent=2))
    elif a.symbol:
        print('\n'.join(e.symbol(a.symbol)))
    elif a.start is not None:
        print('\n'.join(e.dump(a.section,a.start,a.size)))
    else:
        print(json.dumps(e.metadata(),indent=2))
