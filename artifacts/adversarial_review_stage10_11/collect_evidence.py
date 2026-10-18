"""Reproducible static audit evidence. Reads held firmware; writes only this directory."""
import hashlib
import json
import lzma
import re
import struct
from pathlib import Path
from elf_probe import Probe
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_BIG_ENDIAN

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'artifacts/firmware_re_xc_ltu'
OUT = Path(__file__).resolve().parent


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def digest(p):
    b=p.read_bytes()
    return dict(path=str(p.relative_to(ROOT)), size=len(b), sha256=hashlib.sha256(b).hexdigest(), md5=hashlib.md5(b).hexdigest())


def cstr(b, off=0):
    return b[off:b.find(b'\0',off)].decode('ascii',errors='replace')


def dtb_properties(b):
    h=struct.unpack('>10I',b[:40]); assert h[0]==0xd00dfeed
    strs=b[h[3]:h[3]+h[8]]; pos=h[2]; stack=[]; result={}
    while pos < len(b):
        t=struct.unpack_from('>I',b,pos)[0]; pos+=4
        if t==1:
            end=b.index(0,pos); stack.append(b[pos:end].decode()); pos=(end+4)&~3
        elif t==2: stack.pop()
        elif t==3:
            n,si=struct.unpack_from('>II',b,pos);pos+=8
            name=cstr(strs,si); val=b[pos:pos+n]; pos=(pos+n+3)&~3
            key='/'.join(stack)+'/'+name
            if name in ('compatible','model','device_type','reg','bootargs','lvds-type','spi-max-frequency','label'):
                result[key]=val.rstrip(b'\0').decode('ascii',errors='replace') if name in ('compatible','model','device_type','bootargs','label') else val.hex()
        elif t==9: break
        elif t!=4: raise ValueError(t)
    return result


manifest=[]; containers={}; dtbs={}
for p in sorted(BASE.glob('*.bin')):
    if '2.4.2' not in p.name and not p.name.startswith('XC-'): continue
    manifest.append(digest(p)); b=p.read_bytes()
    if b.startswith(b'AMEIMG'):
        count=struct.unpack_from('>I',b,0x54)[0]; pos=0x58; parts=[]
        for i in range(count):
            typ,size=struct.unpack_from('>II',b,pos); md5=b[pos+8:pos+24];name=cstr(b,pos+24)
            payload=b[pos+88:pos+24+size]
            parts.append(dict(index=i,name=name,offset=pos+88,size=len(payload),md5_matches=hashlib.md5(payload).digest()==md5,sha256=hashlib.sha256(payload).hexdigest()))
            if 'tree' in name or name=='dtb':dtbs[p.name+':'+name]=dtb_properties(payload)
            pos+=24+size
        containers[p.name]=dict(version=cstr(b,20),parts=parts,tail_bytes=len(b)-pos)
    else:
        positions=[m.start() for m in re.finditer(b'PART',b)];parts=[]
        for pos in positions:
            if b[pos+4:pos+10] not in (b'u-boot',b'kernel',b'rootfs'): continue
            size=struct.unpack_from('>I',b,pos+48)[0]
            parts.append(dict(offset=pos,name=cstr(b,pos+4),size=size))
        containers[p.name]=dict(version=cstr(b,4),parts=parts)
        if p.name.startswith('XC-8.7.25'):
            k=next(x for x in parts if x['name']=='kernel'); u=b[k['offset']+56:k['offset']+56+k['size']]
            assert u[:4]==bytes.fromhex('27051956')
            raw=lzma.decompress(u[64:64+struct.unpack_from('>I',u,12)[0]])
            (OUT/'xc_8725_kernel.raw').write_bytes(raw)
            containers[p.name]['kernel_raw_sha256']=hashlib.sha256(raw).hexdigest()

patches={}; disasm={}
for rev,sites in [('xc_8725_rootfs',[30784,31816,41976]),('xc_874cs_rootfs',[30072,31104,40916])]:
    p=BASE/rev/'lib/modules/2.6.32.68/ubnt_poll_host.ko'; manifest.append(digest(p));e=Probe(p)
    patched=bytearray(e.raw)
    for off,replacement in zip(sites,['00000000','10000006','24020001']):patched[off:off+4]=bytes.fromhex(replacement)
    patches[rev]=dict(metadata=e.metadata(),sites=[dict(file_offset=o,original=e.raw[o:o+4].hex(),assembly=e.dump('.text',o-64-16,56)) for o in sites],patched_md5=hashlib.md5(patched).hexdigest(),byte_changes=sum(a!=b for a,b in zip(e.raw,patched)))
    disasm[rev+':timer']=e.dump('.text',sites[1]-64-48,160)

hal=Probe(BASE/'xc_8725_rootfs/lib/modules/2.6.32.68/ubnthal.ko')
data=hal.elf.get_section_by_name('.data').data(); ro=hal.elf.get_section_by_name('.rodata').data();key=ro[0x3a8:0x3ac]
boards=[]
for i in range(34):
    b=bytearray(data[0x570+i*12000:0x570+(i+1)*12000])
    for st,n in [(0,32),(32,32),(64,16),(72,32)]:
        for j in range(n):
            if not b[st+j]:break
            b[st+j]^=key[j%4]
    radios=[]
    for r in range(b[0xcc]):
        q=r*3780
        radios.append(dict(radio_index=r,name=cstr(b,q+0xd0),subsys=hex(struct.unpack_from('>H',b,q+0x106)[0]),bus_id=struct.unpack_from('>I',b,q+0x110)[0],caps=hex(struct.unpack_from('>I',b,q+0xf6c)[0]),hsr_param=struct.unpack_from('>I',b,q+0xf8c)[0]))
    boards.append(dict(index=i,name=cstr(b),model=cstr(b,72),sysid=hex(struct.unpack_from('>H',b,0x2d1c)[0]),radio_count=b[0xcc],radios=radios))

for model in ('aflturocket','afltu'):
    folder=BASE/f'ltu_extracted/{model}_2.4.2/rootfs_extracted'
    for name in ('ame_core.ko','ame_dev.ko','ame_radio_mod.ko'):
        p=folder/'lib/modules/3.14.65'/name;manifest.append(digest(p))
    for rel in ['bin/ubntbox','bin/ame_adj.sh','usr/www/ameeng.cgi']:
        p=folder/rel
        if p.is_file():manifest.append(digest(p))

e=Probe(BASE/'ltu_extracted/aflturocket_2.4.2/rootfs_extracted/lib/modules/3.14.65/ame_core.ko')
names=['AME_Scheduler_AutoMCS_GetPtmpDLCeiling','autoMCS_get_rate_table','ame_check_hw_NoOFDMA','sched_ofdma_available','ame_bbp_set_ofdma_subbands','bbp_mrx_band_ofdma_subbands','ame_bbp_set_autoMcsCeiling','bbp_rf_set_super4096','ame_bbp_set_ofdma_en','bbp_base_set_ofdma_subband_type','mcs_ceiling_toggle_txpwr','ame_bbp_set_Param_mcs','ptmp_ap_rx_expected_10x_mcs']
for n in names:disasm[n]=e.symbol(n)

# Keep the decisive source-level observations together with their provenance.
halpath=BASE/'xc_8725_rootfs/lib/modules/2.6.32.68/ubnthal.ko'
umacpath=BASE/'xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko'
athpath=BASE/'xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko'
for p in (halpath,umacpath,athpath):manifest.append(digest(p))
umac=Probe(umacpath);ath=Probe(athpath)
for n in ('ubnthal_get_radios_count','ubnthal_get_radio_bus'):
    disasm['hal:'+n]=hal.symbol(n)
for n in ('ubnt_prism_hook','ath_spectral_filter_init'):
    target=umac if n=='ubnt_prism_hook' else ath
    disasm[n]=target.symbol(n)
disasm['prism_edge_selector']=umac.dump('.text',0xabeb0,0x1b0)
disasm['alleged_hsr_gpio_site']=umac.dump('.text',0x8cb20,0x90)
disasm['real_hsr_cap_query']=umac.dump('.text',0xbbf30,0x80)
prism=umac.elf.get_section_by_name('.data').data()[0x1510:0x1510+264]
save('prism_table.json',[list(struct.unpack_from('>11I',prism,i*44)) for i in range(6)])
dev=Probe(BASE/'ltu_extracted/aflturocket_2.4.2/rootfs_extracted/lib/modules/3.14.65/ame_dev.ko')
disasm['ofdma_subbands_store']=dev.symbol('ofdma_subbands_store')
box=Probe(BASE/'ltu_extracted/aflturocket_2.4.2/rootfs_extracted/bin/ubntbox')
disasm['ubntconf_mcs_validate']=box.dump('.text',0x40240,0xa0)
disasm['ubntconf_mcs_serialize']=box.dump('.text',0x41da0,0xc0)
raw=(OUT/'xc_8725_kernel.raw').read_bytes()
cs=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_BIG_ENDIAN)
disasm['xc_kernel_R_MIPS_26']=[f'VA=0x{i.address:x} file=0x{i.address-0x80002000:x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in cs.disasm(raw[0xa8ac:0xaa10],0x8000c8ac)]
wa=OUT/'wa_8725_ubnt_poll_host.ko'
if wa.exists():
    manifest.append(digest(wa));w=Probe(wa);x=Probe(BASE/'xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko')
    sites=[30784,31816,41976];patched=bytearray(w.raw)
    for o,h in zip(sites,['00000000','10000006','24020001']):patched[o:o+4]=bytes.fromhex(h)
    patches['wa_8725']=dict(metadata=w.metadata(),sites=[dict(file_offset=o,original=w.raw[o:o+4].hex(),assembly=w.dump('.text',o-64-16,56),xc_96_byte_context_identical=w.raw[o-48:o+48]==x.raw[o-48:o+48]) for o in sites],patched_md5=hashlib.md5(patched).hexdigest(),text_byte_differences=[i for i,(a,b) in enumerate(zip(w.elf.get_section_by_name('.text').data(),x.elf.get_section_by_name('.text').data())) if a!=b])
for name in ('autoMcsUseSisoTbl','autoMcsOthersTbl','startThrd_4096','stayThrd_4096'):
    s=next(s for s in e.symbols if s.name==name);sec=e.elf.get_section(s['st_shndx'])
    disasm['data:'+name]=dict(section=sec.name,offset=hex(s['st_value']),size=s['st_size'],bytes=sec.data()[s['st_value']:s['st_value']+s['st_size']].hex())
for doc in ['ADVERSARIAL_REVIEW_BRIEF.md','STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md','STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md','STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md','REDDIT_POST.md']:
    manifest.append(digest(ROOT/'docs'/doc))
save('manifest.json',manifest);save('containers.json',containers);save('dtb_properties.json',dtbs);save('patch_sites.json',patches);save('xc_boards.json',boards);save('selected_disassembly.json',disasm)
print('Wrote manifest, containers, DTB properties, patch sites, decoded boards and disassembly; target firmware was not executed.')
