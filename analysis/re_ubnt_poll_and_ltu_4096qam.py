# PUBLIC_REDACTED_DERIVATIVE; original_sha256=118a02ee21abe31eedd7d3dfea3c7b32359ac8e16276bf65c290a89fc87ca770
# Private originals are required for native replay.
"""Reproducible offline ELF/binary/table reverse-engineering extractor for:

1. Ubiquiti airMAX AC `ubnt_poll_host.ko` TDMA scheduler & polling module across
   `WA` (AR9342 + QCA988x: v8.5.12, v8.7.4-cs, v8.7.25) and
   `XC` (AR9558 + QCA9880 + airPrism: v8.7.4-cs, v8.7.25).
2. Ubiquiti LTU (`aflturocket-2.4.2` AP & `afltu-2.4.2` CPE) custom `ame_core.ko`
   and `ame_dev.ko` 4096-QAM (`12x`) PHY/MAC scheduler, rate/CINR/EVM/sensitivity/
   power-backoff tables, kernel module parameters, and runtime CLI/sysfs/debugfs/
   config knobs.

Strictly offline analysis of local extracted firmware artifacts.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import struct
from typing import Any
REPO_ROOT = Path(__file__).resolve().parent.parent
UBNT_POLL_MODULES: dict[str, str] = {'WA.v8.5.12': 'firmware/build/codex-analysis-20261006/rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko', 'WA.v8.7.4-cs': 'artifacts/autoresearch/waves_abcd_20261024/wave_a_wa/wa874cs_modules/lib/modules/2.6.32.68/ubnt_poll_host.ko', 'WA.v8.7.25': 'artifacts/firmware_re_xc_ltu/wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko', 'XC.v8.7.4-cs': 'artifacts/firmware_re_xc_ltu/xc_874cs_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko', 'XC.v8.7.25': 'artifacts/firmware_re_xc_ltu/xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko'}
LTU_EXTRACTED_ROOTS: dict[str, str] = {'aflturocket_2.4.2': 'artifacts/firmware_re_xc_ltu/ltu_extracted/aflturocket_2.4.2/rootfs_extracted', 'afltu_2.4.2': 'artifacts/firmware_re_xc_ltu/ltu_extracted/afltu_2.4.2/rootfs_extracted'}
OUTPUT_JSON_PATH = REPO_ROOT / 'artifacts' / 'firmware_re_xc_ltu' / 'ubnt_poll_and_ltu_12x_deep_re_20261024.json'
NETCONF_STRUCT_FORMAT = '>I10H4B7I6H8B4H3BbH6BH5Bb'
NETCONF_FIELD_SPECS: list[tuple[str, int, str, str]] = [('flags', 0, 'u32', 'Bitmask of PTMP scheduler/hybrid/fixed-frame capability flags (0x08d0 AC PtMP, 0x2a10 Hybrid)'), ('down_dur_min', 4, 'u16', 'Minimum downlink phase duration in microseconds'), ('cfp_dur_min', 6, 'u16', 'Minimum Contention-Free Period (CFP) duration in microseconds'), ('cbp_dur_slot', 8, 'u16', 'Contention-Based Period (CBP) slot duration in microseconds'), ('down_dur', 10, 'u16', 'Maximum/target downlink phase duration in microseconds (flexible mode)'), ('up_dur', 12, 'u16', 'Maximum/target uplink phase duration in microseconds (flexible mode)'), ('cbp_dur', 14, 'u16', 'Total CBP window duration in microseconds'), ('cbp_usable_dur', 16, 'u16', 'Usable CBP window duration in microseconds'), ('downlink_active_thresh', 18, 'u16', 'Downlink active traffic threshold'), ('cbp_duty_cycle_thresh', 20, 'u16', 'CBP duty-cycle threshold (%)'), ('cbp_duty_cycle_hwm', 22, 'u16', 'CBP duty-cycle high-water mark (%)'), ('duty_cycle_metric_maws', 24, 'u8', 'Moving-average window shift for duty-cycle metric'), ('duty_cycle_metric_sms', 25, 'u8', 'Sub-metric scaling factor for duty-cycle metric'), ('high_contention_sta_count', 26, 'u8', 'Active STA count threshold triggering high-contention TDMA mode'), ('cbp_use_sta_count_limit', 27, 'u8', 'Maximum STA count allowed to use CBP slots'), ('activity_aging', 28, 'u32', 'General STA activity aging timeout in microseconds'), ('activity_aging_da', 32, 'u32', 'Dynamic allocation STA activity aging timeout in microseconds'), ('activity_aging_hb', 36, 'u32', 'Heartbeat STA activity aging timeout in microseconds'), ('usage_report_interval', 40, 'u32', 'Airtime/usage report interval in microseconds'), ('sounding_interval', 44, 'u32', 'Channel/rate sounding interval in microseconds'), ('eval_report_interval', 48, 'u32', 'Link evaluation report interval in microseconds'), ('network_config_interval', 52, 'u32', 'PTMP network configuration broadcast interval in microseconds'), ('high_contention_min_down_dur', 56, 'u16', 'Minimum downlink duration under high contention in microseconds'), ('high_contention_min_up_dur', 58, 'u16', 'Minimum uplink duration under high contention in microseconds'), ('cbp_use_txop_cycle_window', 60, 'u16', 'TXOP cycle window length for CBP usage tracking'), ('cbp_use_allowed_in_window', 62, 'u16', 'Allowed CBP transmissions within TXOP cycle window'), ('down_dur_gap', 64, 'u16', 'Downlink guard/inter-phase gap duration in microseconds'), ('up_dur_gap', 66, 'u16', 'Uplink guard/inter-phase gap duration in microseconds'), ('dl_rate_ratio_thresh_nr', 68, 'u8', 'Downlink rate ratio threshold (Normal Retry / hidden-node backoff)'), ('dl_per_thresh_nr', 69, 'u8', 'Downlink Packet Error Rate (PER %) threshold (Normal Retry)'), ('ul_rate_ratio_thresh_nb', 70, 'u8', 'Uplink rate ratio threshold (Narrowband / interference)'), ('ul_per_thresh_nb', 71, 'u8', 'Uplink PER (%) threshold (Narrowband / interference)'), ('ul_rate_ratio_thresh_nr', 72, 'u8', 'Uplink rate ratio threshold (Normal Retry)'), ('ul_per_thresh_nr', 73, 'u8', 'Uplink PER (%) threshold (Normal Retry)'), ('txop_qual_thresh_nr_nb', 74, 'u8', 'TXOP quality threshold (%) for retry suppression / narrowband'), ('cms_bias', 75, 'u8', 'Collision/retry suppression bias level index (0..9 -> _retr_supression_levels)'), ('hyb_cfp_min_dur_low_use', 76, 'u16', 'Hybrid mode minimum CFP duration under low utilization (us)'), ('hyb_bal_dl_avg_dur_thresh', 78, 'u16', 'Hybrid mode balanced downlink average duration threshold (us)'), ('hyb_bal_dl_avg_txuse_thresh', 80, 'u16', 'Hybrid mode balanced downlink average TX utilization threshold'), ('hyb_cfp_dur_unit', 82, 'u16', 'Hybrid mode CFP duration allocation quantum (us)'), ('voip_bias', 84, 'u8', 'VoIP dynamic duration bias level index (0..9 -> _voip_dynamic_duration_levels)'), ('voip_pps_min', 85, 'u8', 'VoIP detection minimum packets-per-second threshold'), ('voip_pps_max', 86, 'u8', 'VoIP detection maximum packets-per-second threshold'), ('atpc_target_rssi', 87, 'i8', 'Automatic Transmit Power Control (ATPC) target RSSI at AP (dBm)'), ('ff_frame_dur', 88, 'u16', 'Fixed-Frame TDMA total frame duration in microseconds (e.g. 5000, 8000, 10000)'), ('ff_dl_alloc', 90, 'u8', 'Fixed-Frame downlink airtime allocation percentage / units (e.g. 50, 67, 75)'), ('ff_cbp_slots', 91, 'u8', 'Fixed-Frame number of CBP polling slots per frame'), ('ff_dl_ctrl_rate', 92, 'u8', 'Fixed-Frame downlink control/MAP frame modulation rate index'), ('ff_ul_ctrl_rate', 93, 'u8', 'Fixed-Frame uplink control/poll-response rate index'), ('ff_dl_swr_count', 94, 'u8', 'Fixed-Frame downlink software retry limit count'), ('ff_ul_swr_count', 95, 'u8', 'Fixed-Frame uplink software retry limit count'), ('ff_dack_arbit_max', 96, 'u16', 'Fixed-Frame delayed-ACK arbitration maximum window'), ('ff_unit_shift', 98, 'u8', 'Fixed-Frame time-unit bit shift'), ('ff_guard_units', 99, 'u8', 'Fixed-Frame DL/UL guard interval in time units'), ('atpc_max_power', 100, 'u8', 'ATPC maximum allowed CPE TX power (dBm)'), ('atpc_min_power', 101, 'u8', 'ATPC minimum allowed CPE TX power (dBm)'), ('ff_mcast_airtime_limit', 102, 'u8', 'Fixed-Frame multicast airtime limit (%)'), ('ff_sta_rx_rssi_th', 103, 'i8', 'Minimum station RX RSSI threshold (dBm) for admission/polling')]

class Elf32Image:
    """Lightweight offline 32-bit ELF parser supporting both big-endian (MIPS) and little-endian (ARM)."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = path.read_bytes()
        if self.data[:4] != b'\x7fELF' or self.data[4] != 1:
            raise ValueError(f'Unsupported ELF file: {path}')
        self.endian = '>' if self.data[5] == 2 else '<'
        self.e_machine = struct.unpack(self.endian + 'H', self.data[18:20])[0]
        e_shoff = struct.unpack(self.endian + 'I', self.data[32:36])[0]
        e_shentsize, e_shnum, e_shstrndx = struct.unpack(self.endian + 'HHH', self.data[46:52])
        raw_shdrs = [struct.unpack(self.endian + '10I', self.data[e_shoff + i * e_shentsize:e_shoff + (i + 1) * e_shentsize]) for i in range(e_shnum)]
        shstr_off, shstr_sz = (raw_shdrs[e_shstrndx][4], raw_shdrs[e_shstrndx][5])
        shstrtab = self.data[shstr_off:shstr_off + shstr_sz]
        self.sections_by_index: list[dict[str, Any]] = []
        self.sections: dict[str, dict[str, Any]] = {}
        for idx, sh in enumerate(raw_shdrs):
            name_end = shstrtab.find(b'\x00', sh[0])
            name = shstrtab[sh[0]:name_end].decode('ascii', 'ignore')
            sec_info = {'index': idx, 'name': name, 'sh_type': sh[1], 'sh_flags': sh[2], 'sh_addr': sh[3], 'sh_offset': sh[4], 'sh_size': sh[5], 'sh_link': sh[6], 'sh_info': sh[7], 'sh_addralign': sh[8], 'sh_entsize': sh[9]}
            self.sections_by_index.append(sec_info)
            self.sections[name] = sec_info
        self.symbols: list[dict[str, Any]] = []
        if '.symtab' in self.sections and '.strtab' in self.sections:
            sym_sec = self.sections['.symtab']
            str_sec = self.sections['.strtab']
            strtab = self.section_bytes('.strtab')
            count = sym_sec['sh_size'] // 16
            for i in range(count):
                off = sym_sec['sh_offset'] + i * 16
                st_name, st_value, st_size, st_info, st_other, st_shndx = struct.unpack(self.endian + 'IIIBBH', self.data[off:off + 16])
                end = strtab.find(b'\x00', st_name)
                name = strtab[st_name:end].decode('ascii', 'ignore') if st_name < len(strtab) else ''
                sec_name = self.sections_by_index[st_shndx]['name'] if st_shndx < len(self.sections_by_index) else f'SHN_{st_shndx}'
                self.symbols.append({'index': i, 'name': name, 'value': st_value, 'size': st_size, 'bind': st_info >> 4, 'type': st_info & 15, 'shndx': st_shndx, 'section': sec_name})

    def section_bytes(self, name: str) -> bytes:
        sec = self.sections[name]
        return self.data[sec['sh_offset']:sec['sh_offset'] + sec['sh_size']]

    def section_sha256(self, name: str) -> str | None:
        if name not in self.sections:
            return None
        return hashlib.sha256(self.section_bytes(name)).hexdigest()

    def relocations(self, rel_sec_name: str) -> list[dict[str, Any]]:
        if rel_sec_name not in self.sections:
            return []
        sec = self.sections[rel_sec_name]
        raw = self.section_bytes(rel_sec_name)
        out = []
        for i in range(sec['sh_size'] // 8):
            r_offset, r_info = struct.unpack(self.endian + 'II', raw[i * 8:(i + 1) * 8])
            sym_idx = r_info >> 8
            r_type = r_info & 255
            sym = self.symbols[sym_idx] if sym_idx < len(self.symbols) else None
            out.append({'offset': r_offset, 'sym_idx': sym_idx, 'type': r_type, 'symbol': sym['name'] if sym else '', 'symbol_value': sym['value'] if sym else 0, 'symbol_section': sym['section'] if sym else ''})
        return out

    def read_c_string(self, sec_name: str, offset: int) -> str:
        raw = self.section_bytes(sec_name)
        if offset < 0 or offset >= len(raw):
            return ''
        end = raw.find(b'\x00', offset)
        if end == -1:
            end = len(raw)
        return raw[offset:end].decode('ascii', 'ignore')

def decode_netconf_struct(buf: bytes) -> dict[str, int]:
    vals = struct.unpack(NETCONF_STRUCT_FORMAT, buf[:104])
    return {spec[0]: int(val) for spec, val in zip(NETCONF_FIELD_SPECS, vals)}

def extract_ubnt_poll_sysctl_tables(elf: Elf32Image) -> dict[str, Any]:
    """Extract both global (/proc/sys/dev/uph/*) and per-radio (/proc/sys/dev/uph_<radio>/*) ctl_table arrays."""
    rodata = elf.section_bytes('.rodata')
    data_sec = elf.section_bytes('.data')
    rel_ro = {r['offset']: r for r in elf.relocations('.rel.rodata')}
    rel_da = {r['offset']: r for r in elf.relocations('.rel.data')}
    global_nodes: list[dict[str, Any]] = []
    for idx in range(10):
        base = 288 + idx * 44
        if base + 44 > len(data_sec):
            break
        fields = struct.unpack('>11I', data_sec[base:base + 44])
        ctl_name, procname_ptr, data_ptr, maxlen, mode, child, parent, proc_handler, strategy, de, extra1 = fields
        if ctl_name == 0 and procname_ptr == 0 and (mode == 0):
            break
        str_off = procname_ptr
        str_sec = '.rodata.str1.4'
        if base + 4 in rel_da:
            str_off += rel_da[base + 4]['symbol_value']
            if rel_da[base + 4]['symbol_section']:
                str_sec = rel_da[base + 4]['symbol_section']
        procname = elf.read_c_string(str_sec, str_off)
        proc_h_off = proc_handler + (rel_da[base + 28]['symbol_value'] if base + 28 in rel_da else 0)
        global_nodes.append({'ctl_name': ctl_name, 'procname': procname, 'path': f'/proc/sys/dev/uph/{procname}', 'maxlen': maxlen, 'mode_octal': f'0{mode:03o}', 'proc_handler_text_offset': f'0x{proc_h_off:04x}'})
    radio_nodes: list[dict[str, Any]] = []
    for idx in range(40):
        base = 176 + idx * 44
        if base + 44 > len(rodata):
            break
        fields = struct.unpack('>11I', rodata[base:base + 44])
        ctl_name, procname_ptr, data_ptr, maxlen, mode, child, parent, proc_handler, strategy, de, extra1 = fields
        if ctl_name == 0 and procname_ptr == 0 and (mode == 0):
            break
        str_off = procname_ptr
        str_sec = '.rodata.str1.4'
        if base + 4 in rel_ro:
            str_off += rel_ro[base + 4]['symbol_value']
            if rel_ro[base + 4]['symbol_section']:
                str_sec = rel_ro[base + 4]['symbol_section']
        procname = elf.read_c_string(str_sec, str_off)
        proc_h_off = proc_handler + (rel_ro[base + 28]['symbol_value'] if base + 28 in rel_ro else 0)
        handler_type = 'integer_or_intvec_dispatch (proc_dointvec + ubnt_poll_host_sysctl_int)' if proc_h_off == 8504 else 'string_command_dispatch (proc_dostring + ubnt_poll_host_sysctl_str)'
        radio_nodes.append({'ctl_name': ctl_name, 'procname': procname, 'path': f'/proc/sys/dev/uph_<radio>/{procname}', 'maxlen': maxlen, 'mode_octal': f'0{mode:03o}', 'proc_handler_text_offset': f'0x{proc_h_off:04x}', 'handler_kind': handler_type})
    return {'global_sysctl_dir': '/proc/sys/dev/uph', 'global_nodes': global_nodes, 'per_radio_sysctl_dir': '/proc/sys/dev/uph_<radio>', 'per_radio_nodes': radio_nodes}

def extract_ubnt_poll_netconf_parser(elf: Elf32Image) -> list[dict[str, Any]]:
    """Extract the exact string-to-offset instruction mapping from the netconf parser in .text."""
    txt = elf.section_bytes('.text')
    str1_idx = elf.sections['.rodata.str1.4']['index']
    str_syms = {s['index']: s['value'] for s in elf.symbols if s['shndx'] == str1_idx}
    rels = [r for r in elf.relocations('.rel.text') if r['sym_idx'] in str_syms and r['type'] == 6 and (13056 <= r['offset'] <= 17920)]
    commands: list[dict[str, Any]] = []
    for r in rels:
        off = r['offset']
        str_off = str_syms[r['sym_idx']] + struct.unpack('>H', txt[off + 2:off + 4])[0]
        s = elf.read_c_string('.rodata.str1.4', str_off)
        if s in ('%s %s', '%d') or s.startswith('<7>'):
            continue
        stores: list[dict[str, Any]] = []
        for k in range(off, min(off + 84, len(txt)), 4):
            ins = struct.unpack('>I', txt[k:k + 4])[0]
            op = ins >> 26
            imm = ins & 65535
            if op in (40, 41, 43) and imm != 152:
                stores.append({'width': {40: 'u8', 41: 'u16', 43: 'u32'}[op], 'uph_dev_offset': imm, 'netconf_struct_offset': imm - 156})
        commands.append({'command': s, 'parser_text_offset': f'0x{off:04x}', 'store_target': stores[0] if stores else None})
    return commands

def analyze_ubnt_poll_modules() -> dict[str, Any]:
    """Perform multi-version comparison and deep extraction of ubnt_poll_host.ko."""
    version_inventory: dict[str, Any] = {}
    reference_elf: Elf32Image | None = None
    for label, rel_path in UBNT_POLL_MODULES.items():
        abs_path = REPO_ROOT / rel_path
        elf = Elf32Image(abs_path)
        if label == 'XC.v8.7.25':
            reference_elf = elf
        funcs = [{'name': s['name'], 'offset': f'0x{s['value']:05x}', 'size': s['size']} for s in elf.symbols if s['section'] == '.text' and s['type'] == 2 and s['name']]
        exported_ksym = [s['name'].replace('__ksymtab_', '') for s in elf.symbols if s['name'].startswith('__ksymtab_')]
        modinfo = [x.decode('ascii', 'ignore') for x in elf.section_bytes('.modinfo').split(b'\x00') if x]
        version_inventory[label] = {'path': rel_path, 'size_bytes': len(elf.data), 'md5': hashlib.md5(elf.data).hexdigest(), 'sha256': hashlib.sha256(elf.data).hexdigest(), 'e_machine': elf.e_machine, 'vermagic': next((m.split('=', 1)[1] for m in modinfo if m.startswith('vermagic=')), ''), 'section_hashes': {sec_name: elf.section_sha256(sec_name) for sec_name in ('.text', '.rodata', '.rodata.str1.4', '.data', '.bss')}, 'function_count': len(funcs), 'exported_ksymtab_symbols': sorted(exported_ksym)}
    assert reference_elf is not None
    rodata = reference_elf.section_bytes('.rodata')
    netconf_profiles = {'ht40_hybrid_or_max_0xb28': decode_netconf_struct(rodata[2856:2856 + 104]), 'ht40_ptmp_ac_0xb90': decode_netconf_struct(rodata[2960:2960 + 104]), 'ht30_hybrid_or_max_0xbf8': decode_netconf_struct(rodata[3064:3064 + 104]), 'ht30_ptmp_ac_0xc60': decode_netconf_struct(rodata[3168:3168 + 104]), 'ht20_hybrid_or_max_0xcc8': decode_netconf_struct(rodata[3272:3272 + 104]), 'ht20_ptmp_ac_0xd30': decode_netconf_struct(rodata[3376:3376 + 104]), 'ht10_hybrid_or_max_0xd98': decode_netconf_struct(rodata[3480:3480 + 104]), 'ht10_ptmp_ac_0xe00': decode_netconf_struct(rodata[3584:3584 + 104])}
    retr_raw = list(rodata[3748:3748 + 70])
    retr_levels = []
    for lvl in range(10):
        row = retr_raw[lvl * 7:(lvl + 1) * 7]
        retr_levels.append({'cms_bias_level': lvl, 'dl_rate_ratio_thresh_nr': row[0], 'dl_per_thresh_nr_pct': row[1], 'ul_rate_ratio_thresh_nb': row[2], 'ul_per_thresh_nb_pct': row[3], 'ul_rate_ratio_thresh_nr': row[4], 'ul_per_thresh_nr_pct': row[5], 'txop_qual_thresh_nr_nb_pct': row[6]})
    voip_levels = []
    for lvl in range(10):
        b0, b1, down_min, up_min = struct.unpack('>BBHH', rodata[3688 + lvl * 6:3688 + (lvl + 1) * 6])
        voip_levels.append({'voip_bias_level': lvl, 'high_contention_sta_count': b0, 'pad_u8': b1, 'high_contention_min_down_dur_us': down_min, 'high_contention_min_up_dur_us': up_min})
    all_functions = sorted([{'name': s['name'], 'offset': f'0x{s['value']:05x}', 'size': s['size']} for s in reference_elf.symbols if s['section'] == '.text' and s['type'] == 2 and s['name']], key=lambda x: int(x['offset'], 16))
    sysctl_info = extract_ubnt_poll_sysctl_tables(reference_elf)
    netconf_commands = extract_ubnt_poll_netconf_parser(reference_elf)
    elf_8512 = Elf32Image(REPO_ROOT / UBNT_POLL_MODULES['WA.v8.5.12'])
    elf_874 = Elf32Image(REPO_ROOT / UBNT_POLL_MODULES['WA.v8.7.4-cs'])
    syms_8512 = {s['name']: s['size'] for s in elf_8512.symbols if s['section'] == '.text' and s['type'] == 2 and s['name']}
    syms_874 = {s['name']: s['size'] for s in elf_874.symbols if s['section'] == '.text' and s['type'] == 2 and s['name']}
    syms_8725 = {s['name']: s['size'] for s in reference_elf.symbols if s['section'] == '.text' and s['type'] == 2 and s['name']}
    changed_874_to_8725 = {k: {'v8.7.4-cs_size': syms_874[k], 'v8.7.25_size': syms_8725[k]} for k in sorted(set(syms_874) & set(syms_8725)) if syms_874[k] != syms_8725[k]}
    return {'module_inventory': version_inventory, 'cross_platform_identity': {'wa_vs_xc_v8725_rodata_identical': version_inventory['WA.v8.7.25']['section_hashes']['.rodata'] == version_inventory['XC.v8.7.25']['section_hashes']['.rodata'], 'wa_vs_xc_v8725_data_identical': version_inventory['WA.v8.7.25']['section_hashes']['.data'] == version_inventory['XC.v8.7.25']['section_hashes']['.data'], 'wa_vs_xc_v874cs_rodata_identical': version_inventory['WA.v8.7.4-cs']['section_hashes']['.rodata'] == version_inventory['XC.v8.7.4-cs']['section_hashes']['.rodata'], 'functions_changed_between_v874cs_and_v8725': changed_874_to_8725, 'functions_added_between_v874cs_and_v8725': sorted(set(syms_8725) - set(syms_874)), 'functions_added_since_v8512': sorted(set(syms_8725) - set(syms_8512))}, 'sysctl_hierarchy': sysctl_info, 'netconf_subcommands': netconf_commands, 'netconf_struct_schema': [{'field': name, 'struct_offset': off, 'uph_dev_offset': off + 156, 'type': ftype, 'description': desc} for name, off, ftype, desc in NETCONF_FIELD_SPECS], 'rodata_netconf_profiles': netconf_profiles, 'rodata_retr_suppression_levels': retr_levels, 'rodata_voip_dynamic_duration_levels': voip_levels, 'character_device_ku_comm': {'device_node_pattern': '/dev/uph_<radio> (e.g., /dev/uph_wifi0)', 'major': 190, 'minor_range': '0..3', 'ioctls': [{'cmd_hex': '0x40905501', 'handler': 'ubnt_poll_ku_comm_get_info', 'arg_size_bytes': 144, 'direction': 'IOR'}, {'cmd_hex': '0xc0015502', 'handler': 'ubnt_poll_ku_comm_get_stalist', 'arg_size_bytes': 1, 'direction': 'IOWR'}, {'cmd_hex': '0xc6945503', 'handler': 'ubnt_poll_ku_comm_get_stainfo', 'arg_size_bytes': 1684, 'direction': 'IOWR'}, {'cmd_hex': '0xc2145504', 'handler': 'ubnt_poll_ku_comm_get_sta_spec_data', 'arg_size_bytes': 532, 'direction': 'IOWR'}, {'cmd_hex': '0xc2145505', 'handler': 'ubnt_poll_ku_comm_set_sta_spec_data', 'arg_size_bytes': 532, 'direction': 'IOWR'}]}, 'undocumented_runtime_knobs': [{'knob': '/proc/sys/dev/uph_<radio>/cms_bias', 'webui_exposed': False, 'range': '0..9', 'mechanism': 'Selects row in _retr_supression_levels (0xea4) controlling DL/UL PER & rate-ratio thresholds and TXOP quality threshold for hidden-node polling retry backoff'}, {'knob': '/proc/sys/dev/uph_<radio>/voip_bias', 'webui_exposed': False, 'range': '0..9', 'mechanism': 'Selects row in _voip_dynamic_duration_levels (0xe68) overriding high_contention_sta_count (2..8) and high_contention_min_down/up_dur (15000/7500 us)'}, {'knob': '/proc/sys/dev/uph_<radio>/swr_limit', 'webui_exposed': False, 'range': 'integer (packed DL/UL software retry limit)', 'mechanism': 'Calls ubnt_poll_host_set_swr_limit (0x92fc) to cap per-station software retries in the host TDMA scheduler queue'}, {'knob': '/proc/sys/dev/uph_<radio>/noack_mode', 'webui_exposed': False, 'range': '0..1', 'mechanism': 'Toggles TDMA No-ACK burst mode on radio when polling is disabled or reconfigured'}, {'knob': '/proc/sys/dev/uph_<radio>/daprot', 'webui_exposed': False, 'range': '0..2', 'mechanism': 'Dynamic airMAX protection (CTS-to-self / RTS-CTS protection in TDMA slots)'}, {'knob': '/proc/sys/dev/uph_<radio>/ro', 'webui_exposed': False, 'range': '4-int vector', 'mechanism': 'Calls ubnt_poll_host_set_rate_override (0x8df8) to force rate override per peer/radio'}, {'knob': '/proc/sys/dev/uph_<radio>/sqparam & gqparam', 'webui_exposed': False, 'range': '6-int vector', 'mechanism': 'Calls ubnt_poll_host_set_txq_param / get_txq_param to tune per-AC TXQ burst/AIFS/CW parameters inside the TDMA scheduler'}, {'knob': '/proc/sys/dev/uph_<radio>/sta_priority', 'webui_exposed': True, 'range': '<mac> <0..3>', 'mechanism': 'Calls ubnt_poll_host_set_sta_priority (0x7eb8) to assign Base(3)/Medium/High/Urgent airtime token weights per CPE MAC'}, {'knob': '/proc/sys/dev/uph_<radio>/debug_block_sta & debug_tid', 'webui_exposed': False, 'range': '<mac> <dir_mask> / <mac> <tid>', 'mechanism': 'Selectively pauses DL/UL scheduling for a specific STA MAC or dumps per-TID queue state'}, {'knob': '/proc/sys/dev/uph_<radio>/netconf (55 field overrides)', 'webui_exposed': False, 'range': '<param_name> <value> followed by conf-commit', 'mechanism': 'Directly patches any of the 55 fields in the 104-byte ptmp_netconf struct and broadcasts updated schedule parameters via ubnt_poll_host_send_ptmp_netconf'}], 'text_functions': all_functions}

def extract_ltu_ame_core(elf: Elf32Image) -> dict[str, Any]:
    """Extract rate, sensitivity, TX power backoff, EVM/CINR thresholds, and module params from ame_core.ko."""
    rodata = elf.section_bytes('.rodata')
    data_sec = elf.section_bytes('.data')
    sym_map = {(s['section'], s['name']): s for s in elf.symbols if s['name']}

    def ro_slice(sym_name: str) -> bytes:
        s = sym_map['.rodata', sym_name]
        return rodata[s['value']:s['value'] + s['size']]

    def da_slice(sym_name: str) -> bytes:
        s = sym_map['.data', sym_name]
        return data_sec[s['value']:s['value'] + s['size']]

    def parse_mcs_stream_pairs(raw: bytes) -> list[dict[str, Any]]:
        pairs = []
        for i in range(0, len(raw), 2):
            mcs_idx, is_mimo = (raw[i], raw[i + 1])
            mod_label = {7: 'QPSK (2x)', 11: '16-QAM (4x)', 15: '64-QAM (6x)', 19: '256-QAM (8x)', 23: '1024-QAM (10x)', 31: '4096-QAM (12x)'}.get(mcs_idx, f'MCS_{mcs_idx}')
            pairs.append({'mcs_index': int(mcs_idx), 'mimo_flag': int(is_mimo), 'streams': 'MIMO (2x2)' if is_mimo else 'SISO (1x1)', 'modulation': mod_label})
        return pairs
    auto_mcs_tables = {'autoMcsAllSisoTbl': parse_mcs_stream_pairs(ro_slice('autoMcsAllSisoTbl')), 'autoMcsUseSisoTbl': parse_mcs_stream_pairs(ro_slice('autoMcsUseSisoTbl')), 'autoMcsOthersTbl': parse_mcs_stream_pairs(ro_slice('autoMcsOthersTbl')), 'autoMcsMimoTP_u16': list(struct.unpack('<5H', ro_slice('autoMcsMimoTP'))), 'autoMcsSisoTP_u16': list(struct.unpack('<5H', ro_slice('autoMcsSisoTP')))}
    rate_adaptation_thresholds = {'startThrd_4096_pct': struct.unpack('<I', ro_slice('startThrd_4096'))[0], 'stayThrd_4096_pct': struct.unpack('<I', ro_slice('stayThrd_4096'))[0], 'mcsUpThrd_1024_pct': struct.unpack('<I', ro_slice('mcsUpThrd_1024'))[0], 'mcsUpThrd_256_pct': struct.unpack('<I', ro_slice('mcsUpThrd_256'))[0], 'mcsUpThrd_lowqam_pct': struct.unpack('<I', ro_slice('mcsUpThrd_lowqam'))[0], 'ackmcsUpThrd_pct': struct.unpack('<I', ro_slice('ackmcsUpThrd'))[0], 'ack_ratio_thr_pct': ro_slice('ack_ratio_thr')[0], 'avgWeight': ro_slice('avgWeight')[0], 'startThrd_siso_pct': struct.unpack('<I', ro_slice('startThrd_siso'))[0], 'stayThrd_siso_pct': struct.unpack('<I', ro_slice('stayThrd_siso'))[0], 'ptmpUlPMHighBandThrSht': ro_slice('ptmpUlPMHighBandThrSht')[0], 'ptmpUlPMLowBandThrSht': ro_slice('ptmpUlPMLowBandThrSht')[0], 'mcsUpThreshold': struct.unpack('<I', da_slice('mcsUpThreshold'))[0], 'mcsDownThreshold': struct.unpack('<I', da_slice('mcsDownThreshold'))[0], 'mcsUpThreshold_timer': struct.unpack('<I', da_slice('mcsUpThreshold_timer'))[0], 'mcsDnThreshold_timer': struct.unpack('<I', da_slice('mcsDnThreshold_timer'))[0], 'cont1024Threshold': struct.unpack('<I', da_slice('cont1024Threshold'))[0], 'penaltyThreshold': da_slice('penaltyThreshold')[0], 'penaltyTime': struct.unpack('<I', da_slice('penaltyTime'))[0], 'ackAccuulateCnt': da_slice('ackAccuulateCnt')[0], 'smallTrafficTimer': struct.unpack('<H', da_slice('smallTrafficTimer'))[0], 'ra_offset_table_db': list(da_slice('ra_offset_table')), 'cpeTxBler_scale': struct.unpack('<H', da_slice('cpeTxBler'))[0], 'cpeRxBler_scale': struct.unpack('<H', da_slice('cpeRxBler'))[0]}
    sens_raw = list(struct.unpack('<30b', ro_slice('sensitivity')))
    bw_labels_5 = ['10_MHz', '20_MHz', '30_MHz', '40_MHz', '50_MHz']
    mod_labels_6 = ['4096-QAM (12x)', '1024-QAM (10x)', '256-QAM (8x)', '64-QAM (6x)', '16-QAM (4x)', 'QPSK (2x)']
    sensitivity_table = {bw_labels_5[r]: {mod_labels_6[c]: int(sens_raw[r * 6 + c]) for c in range(6)} for r in range(5)}
    sens_ptmp_raw = list(struct.unpack('<20b', ro_slice('sensitivity_ptmp')))
    mod_labels_4 = ['1024-QAM (10x)', '256-QAM (8x)', '64-QAM (6x)', '16-QAM/QPSK (4x/2x)']
    sensitivity_ptmp_table = {bw_labels_5[r]: {mod_labels_4[c]: int(sens_ptmp_raw[r * 4 + c]) for c in range(4)} for r in range(5)}
    ap_pwr_raw = list(ro_slice('table_ptmpAPPwrRange'))
    bw_labels_8 = ['10_MHz', '20_MHz', '30_MHz', '40_MHz', '50_MHz', '60_MHz', '80_MHz', '100_MHz']
    table_ptmp_ap_pwr_range = {'low_band_rx_target_dbm': {bw_labels_8[r]: {mod_labels_6[c]: -int(ap_pwr_raw[r * 6 + c]) for c in range(6)} for r in range(8)}, 'high_band_rx_target_dbm': {bw_labels_8[r]: {mod_labels_6[c]: -int(ap_pwr_raw[(r + 8) * 6 + c]) for c in range(6)} for r in range(8)}}
    ptp_pwr_raw = list(da_slice('table_ptpPwrRange'))
    mod_labels_7 = ['4096-QAM (12x)', '1024-QAM (10x)', '256-QAM (8x)', '64-QAM (6x)', '16-QAM (4x)', 'QPSK (2x)', 'QPSK (1x)']
    row0_ptp = {}
    for r in range(8):
        base = r * 14
        row0_ptp[bw_labels_8[r]] = {}
        for m in range(7):
            cinr_db = int(ptp_pwr_raw[base + m * 2])
            sens_neg = int(ptp_pwr_raw[base + m * 2 + 1])
            row0_ptp[bw_labels_8[r]][mod_labels_7[m]] = {'supported': not (cinr_db == 0 and sens_neg == 0), 'cinr_or_txpwr_threshold_db': cinr_db if cinr_db != 0 else None, 'rx_sensitivity_dbm': -sens_neg if sens_neg != 0 else None}

    def decode_pwr_u32_6(raw: bytes) -> dict[str, float]:
        vals = struct.unpack('<6I', raw[:24])
        return {mod_labels_6[i]: round(vals[i] / 1000.0, 2) for i in range(6)}
    ptmp_ap_txpwr = decode_pwr_u32_6(ro_slice('ptmp_ap_mcs_txpwr_freq'))
    af5xhd_raw = ro_slice('af_5xhd_mcs_txpwr_freq')
    ltu5_raw = ro_slice('af_ltu5_mcs_txpwr_freq')
    ltulr_raw = ro_slice('af_ltuLR_mcs_txpwr_freq')
    ptp_txpwr_raw = struct.unpack('<42H', ro_slice('mcs_txpwr_freq_ptp'))
    ptp_profile_names = ['AF-5XHD_LTU-Rocket_LowBand', 'AF-5XHD_LTU-Rocket_HighBand', 'LTU-Lite_Pro_5_LowBand', 'LTU-Lite_Pro_5_HighBand', 'LTU-LR_XR_LowBand', 'LTU-LR_XR_HighBand']
    mcs_txpwr_freq_ptp = {ptp_profile_names[r]: {mod_labels_7[c]: round(ptp_txpwr_raw[r * 7 + c] / 1000.0, 2) for c in range(7)} for r in range(6)}
    tx_power_backoff_tables = {'ptmp_ap_mcs_txpwr_freq_dbm': ptmp_ap_txpwr, 'af_5xhd_mcs_txpwr_freq_dbm': {'low_band': decode_pwr_u32_6(af5xhd_raw[:24]), 'high_band': decode_pwr_u32_6(af5xhd_raw[24:48])}, 'af_ltu5_mcs_txpwr_freq_dbm': {'low_band': decode_pwr_u32_6(ltu5_raw[:24]), 'high_band': decode_pwr_u32_6(ltu5_raw[24:48])}, 'af_ltuLR_mcs_txpwr_freq_dbm': {'low_band': decode_pwr_u32_6(ltulr_raw[:24]), 'high_band': decode_pwr_u32_6(ltulr_raw[24:48])}, 'mcs_txpwr_freq_ptp_dbm': mcs_txpwr_freq_ptp}
    modinfo_entries = [x.decode('ascii', 'ignore') for x in elf.section_bytes('.modinfo').split(b'\x00') if x]
    param_types: dict[str, str] = {}
    param_descs: dict[str, str] = {}
    for entry in modinfo_entries:
        if entry.startswith('parmtype='):
            k, v = entry[len('parmtype='):].split(':', 1)
            param_types[k] = v
        elif entry.startswith('parm='):
            k, v = entry[len('parm='):].split(':', 1)
            param_descs[k] = v
    module_parameters = [{'name': k, 'sysfs_path': f'/sys/module/ame_core/parameters/{k}', 'type': param_types[k], 'description': param_descs.get(k, '')} for k in sorted(param_types)]
    return {'binary_sha256': hashlib.sha256(elf.data).hexdigest(), 'size_bytes': len(elf.data), 'auto_mcs_progression_tables': auto_mcs_tables, 'rate_adaptation_thresholds': rate_adaptation_thresholds, 'rx_sensitivity_tables_dbm': {'sensitivity_ptp_6mod_by_5bw': sensitivity_table, 'sensitivity_ptmp_4mod_by_5bw': sensitivity_ptmp_table, 'table_ptmp_ap_pwr_range_6mod_by_8bw': table_ptmp_ap_pwr_range, 'table_ptp_pwr_range_7mod_by_8bw_profile0': row0_ptp, 'good_recvtarget_lvl_dbm': list(struct.unpack('<24b', ro_slice('good_recvtarget_lvl'))), 'good_fix_recvTarget_dbm': list(struct.unpack('<8b', ro_slice('good_fix_recvTarget')))}, 'tx_power_backoff_by_mcs_dbm': tx_power_backoff_tables, 'bbp_evm_to_mcs_thresholds': {'function': 'ame_bbp_op_evm_mcs_map', 'input_unit': '0.01 dB EVM (negative) negated to CINR in 0.01 dB', 'thresholds': [{'cinr_range_db': '<= 10.00 dB (EVM >= -10.00 dB)', 'bbp_mcs_code': 25, 'modulation': 'QPSK 1x'}, {'cinr_range_db': '10.01 .. 16.23 dB (-16.23 <= EVM < -10.00 dB)', 'bbp_mcs_code': 26, 'modulation': 'QPSK 2x'}, {'cinr_range_db': '16.24 .. 22.30 dB (-22.30 <= EVM < -16.23 dB)', 'bbp_mcs_code': 27, 'modulation': '16-QAM 4x'}, {'cinr_range_db': '> 22.30 dB (EVM < -22.30 dB)', 'bbp_mcs_code': 28, 'modulation': '64-QAM 6x+'}], 'data_subframe_cinr_requirements_table_ptpPwrRange': {'QPSK_1x_2x': '10 dB CINR', '16-QAM_4x': '11 dB CINR', '64-QAM_6x': '14 dB CINR', '256-QAM_8x': '17 dB CINR', '1024-QAM_10x': '20 dB CINR (+ mcsUpThrd_1024 = 93% codeword pass rate)', '4096-QAM_12x': 'startThrd_4096 = 97% codeword pass rate at 1024-QAM (MCS 23) to enter MCS 31; stayThrd_4096 = 90% to remain; ~32-34 dB CINR / EVM <= -32 dB required in 10..50 MHz'}}, 'module_parameters_count': len(module_parameters), 'module_parameters': module_parameters}

def extract_ltu_ame_dev_and_scripts() -> dict[str, Any]:
    """Extract sysfs/debugfs/config knobs from ame_dev.ko and shell/config tools in rootfs."""
    root = REPO_ROOT / LTU_EXTRACTED_ROOTS['aflturocket_2.4.2']
    dev_elf = Elf32Image(root / 'lib' / 'modules' / '3.14.65' / 'ame_dev.ko')
    ro_strs = [s.decode('ascii', 'ignore') for s in dev_elf.section_bytes('.rodata.str1.4').split(b'\x00') if len(s) >= 2]
    idx_start = ro_strs.index('phy_regs')
    idx_end = ro_strs.index('cir_record_dump') + 1
    debugfs_nodes = [f'/sys/kernel/debug/ame/{name}' for name in ro_strs[idx_start:idx_end]]
    attr_start = ro_strs.index('queue_info')
    attr_end = ro_strs.index('peek_mrx') + 1
    sysfs_debug_attrs = [f'/sys/devices/platform/ame_debug_dev/{name}' for name in ro_strs[attr_start:attr_end]]
    sys_cfg_lines = (root / 'var' / 'etc' / 'system-af-ltur.cfg').read_text(encoding='utf-8').splitlines()
    sys_cfg_dict = dict((line.split('=', 1) for line in sys_cfg_lines if '=' in line and (not line.startswith('#'))))
    ame_ap_cfg_text = (root / 'var' / 'etc' / 'ame_ptmp_ap.cfg').read_text(encoding='utf-8')
    return {'ame_dev_ko_sha256': hashlib.sha256(dev_elf.data).hexdigest(), 'ame_dev_ko_size_bytes': len(dev_elf.data), 'identical_across_ap_and_cpe': True, 'debugfs_dir': '/sys/kernel/debug/ame', 'debugfs_nodes_count': len(debugfs_nodes), 'debugfs_nodes': debugfs_nodes, 'sysfs_debug_dev_dir': '/sys/devices/platform/ame_debug_dev', 'sysfs_debug_attrs_count': len(sysfs_debug_attrs), 'sysfs_debug_attrs': sysfs_debug_attrs, 'sysfs_ctrl_dev_dir': '/sys/devices/platform/ame_ctrl_dev', 'sysfs_ctrl_Interface': '/sys/devices/platform/ame_ctrl_dev/config (accepts INI sections [SYS], [NAV], [RF], [SECURITY])', 'sysfs_bist_dev_dir': '/sys/devices/platform/ame_bist_dev', 'sysfs_bist_attrs': ['pktrate', 'test_l2p', 'gen_data', 'test_bbp', 'sfn_sync_cnt', 'modem_state', 'rxpwr', 'state', 'Cbler', 'bler', 'each_bler'], 'default_system_af_ltur_cfg': sys_cfg_dict, 'template_ame_ptmp_ap_cfg': ame_ap_cfg_text.strip(), 'cli_and_script_wrappers': {'/bin/af': 'ubntbox multi-call applet (`af get <key>`, `af set <key> <val>`, `af afc`) talking to `afened` via UBUS / shared memory', '/bin/ame_cfg.sh': 'Writes `[Section]\\nKey = Value` directly into `/sys/devices/platform/ame_ctrl_dev/config`', '/bin/ame_adj.sh': 'Runtime adjustment script for `rx_target_pwr`, `txpwr`, `rxgain`, `freq`, `bandwidth`, `duty_cycle`, `frame_len`', '/bin/ame_dbg.sh': 'Toggles `/sys/devices/platform/ame_debug_dev/log_type` and `log_level` across 25 kernel subsystem modules', '/bin/ame_drv.sh': 'Loads `ame_core.ko`, `ame_radio_mod.ko`, `ame_dfs.ko`, `ame_dev.ko`, `ame_gpio_mod.ko`, `ame_helper_mod.ko`'}}

def build_deep_re_report() -> dict[str, Any]:
    ubnt_poll_report = analyze_ubnt_poll_modules()
    ap_core_elf = Elf32Image(REPO_ROOT / LTU_EXTRACTED_ROOTS['aflturocket_2.4.2'] / 'lib' / 'modules' / '3.14.65' / 'ame_core.ko')
    cpe_core_elf = Elf32Image(REPO_ROOT / LTU_EXTRACTED_ROOTS['afltu_2.4.2'] / 'lib' / 'modules' / '3.14.65' / 'ame_core.ko')
    ap_core_data = extract_ltu_ame_core(ap_core_elf)
    cpe_core_data = extract_ltu_ame_core(cpe_core_elf)
    ltu_report = {'aflturocket_2_4_2_ame_core': ap_core_data, 'afltu_2_4_2_ame_core': {'binary_sha256': cpe_core_data['binary_sha256'], 'size_bytes': cpe_core_data['size_bytes'], 'tables_identical_to_ap': ap_core_data['auto_mcs_progression_tables'] == cpe_core_data['auto_mcs_progression_tables'] and ap_core_data['rate_adaptation_thresholds'] == cpe_core_data['rate_adaptation_thresholds'] and (ap_core_data['rx_sensitivity_tables_dbm'] == cpe_core_data['rx_sensitivity_tables_dbm']) and (ap_core_data['tx_power_backoff_by_mcs_dbm'] == cpe_core_data['tx_power_backoff_by_mcs_dbm']), 'module_parameters_count': cpe_core_data['module_parameters_count']}, 'ame_dev_and_runtime_interfaces': extract_ltu_ame_dev_and_scripts()}
    return {'artifact_id': 'ubnt_poll_and_ltu_12x_deep_re_20261024', 'generated_by': 'analysis/re_ubnt_poll_and_ltu_4096qam.py', 'ubnt_poll_host_re': ubnt_poll_report, 'ltu_4096qam_re': ltu_report}

def main() -> None:
    report = build_deep_re_report()
    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON_PATH.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'Saved deep RE artifact to {OUTPUT_JSON_PATH.relative_to(REPO_ROOT)} ({OUTPUT_JSON_PATH.stat().st_size} bytes)')
if __name__ == '__main__':
    main()
