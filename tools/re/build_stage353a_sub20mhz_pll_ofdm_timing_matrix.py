#!/usr/bin/env python3
"""Stage353A source- and byte-bound sub20 timing matrix; no register writer."""
from __future__ import annotations
import argparse
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.re import ground_up_release_common as c

OUT='artifacts/autoresearch/stage353a_sub20mhz_pll_ofdm_timing_matrix.json'
DOC='docs/STAGE353A_SUB20MHZ_PLL_OFDM_TIMING_MATRIX.md'
MANIFEST='artifacts/verification/stage353a_sources/source_manifest.json'
SOURCE_ROOT='artifacts/verification/stage353a_sources/drivers/net/wireless/ath/'
SOURCE_TOKENS={
 'ath9k/hw.c':['ath9k_hw_set_clockrate','clockrate /= 2','clockrate /= 4','sifstime = 32','slottime = 13','sifstime = 64','slottime = 21'],
 'ath9k/ar9003_phy.c':['ar9003_hw_compute_pll_control_soc','AR_RTC_9300_SOC_PLL_CLKSEL','ar9003_hw_set_delta_slope','IS_CHAN_HALF_RATE','IS_CHAN_QUARTER_RATE'],
 'ath9k/hw.h':['CHANNEL_HALF','CHANNEL_QUARTER'],
 'ath10k/mac.c':['chan_to_phymode'],
 'ath10k/wmi.h':['REGDMN_MODE_11A_HALF_RATE','REGDMN_MODE_11A_QUARTER_RATE'],
 'ath10k/hw.c':['ath10k_hw_qca988x_set_coverage_class','ath10k_hw_qca6174_enable_pll_clock']}
MODULES={
 'WA_ath_hal':'artifacts/firmware_re_xc_ltu/wa_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko',
 'XC_ath_hal':'artifacts/firmware_re_xc_ltu/xc_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko',
 'WA_umac':'artifacts/firmware_re_xc_ltu/wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko',
 'XC_umac':'artifacts/firmware_re_xc_ltu/xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko'}
PATTERN=r'(?i)(init.?pll|chan.?2.?clock|set.?slot.?time|get_chan_width|pdev_set_channel|wlan_pll|halfrate|quarterrate)'


def timing(width):
    c.integer(width,'bandwidth_mhz',5,20)
    if width not in (5,10,20):raise ValueError('width_must_be_5_10_20')
    factor=20/width
    slot={20:9,10:13,5:21}[width];sifs=int(16*factor);ack_offset={20:0,10:16,5:32}[width]
    return {'bandwidth_mhz':width,'clock_divisor':int(factor),'legacy_ofdm_useful_symbol_us':3.2*factor,
            'legacy_ofdm_guard_us':.8*factor,'legacy_ofdm_symbol_us':4*factor,
            'subcarrier_spacing_khz':312.5/factor,'legacy_ofdm_preamble_us':20*factor,
            'ath9k_5ghz_sifs_us':sifs,'ath9k_slot_us':slot,
            'ath9k_precoverage_ack_setting_us':slot+sifs+ack_offset,
            'timing_assumptions':{'band':'5GHz','coverage_class':0,'dynack_enabled':False,
                                  'configured_20mhz_slottime_us':9},
            'fixed_nf_noise_bandwidth_delta_db':round(10*math.log10(width/20),8),
            'qualification':'LEGACY_OFDM_MODEL_AND_UPSTREAM_SETTINGS_NOT_VHT5_10_OR_MEASURED_PLL'}


def build(root=ROOT):
    root=Path(root);manifest=c.load(root/MANIFEST);sources=[]
    for row in manifest:
        c.read(root/row['path'],row['sha256'])
    for relative,tokens in SOURCE_TOKENS.items():
        sources.append(c.anchors(root/(SOURCE_ROOT+relative),tokens,root))
    mac=c.read(root/(SOURCE_ROOT+'ath10k/mac.c')).decode()
    start=mac.index('chan_to_phymode(')
    body=mac[start:mac.index('\n}',start)+2]
    if 'NL80211_CHAN_WIDTH_5:' in body or 'NL80211_CHAN_WIDTH_10:' in body:
        raise ValueError('source_control_boundary_changed_reassess_matrix')
    modules={name:c.elf_symbols(root/rel,PATTERN,root) for name,rel in MODULES.items()}
    # XW path is discovered from the held Stage259 provenance, never guessed by family name.
    xw_root=root/'artifacts/firmware_re_xw_m5'
    xw_candidates=sorted(xw_root.rglob('ath_hal.ko')) if xw_root.exists() else []
    for i,path in enumerate(xw_candidates[:8]):modules['XW_held_'+str(i)]=c.elf_symbols(path,PATTERN,root)
    matrix=[{'family':'WA','host':'AR934x-class','radio':'QCA988x ath10k/offloaded',
             'status':'UNKNOWN_INSTALLED_BUILD_SUB20','control':'upstream inspected chan_to_phymode has no5/10 cases; vendor chanbw/symbols do not prove actuation'},
            {'family':'XC','host':'QCA955x-class','radio':'PCIe QCA988x ath10k/offloaded',
             'status':'UNKNOWN_INSTALLED_BUILD_SUB20','control':'Do not apply integrated-ath9k PLL recipe to the QCA988x radio'},
            {'family':'XW','host':'exact board may be AR934x','radio':'exact ath9k-class device requires identity',
             'status':'CONFIRMED_UPSTREAM_PATH_ONLY','control':'ath9k half/quarter clock, delta-slope, PLL selector and timing paths exist; board runtime UNKNOWN'},
            {'family':'XM','host':'exact board/revision UNKNOWN','radio':'ath9k-class not universally AR934x/QCA955x',
             'status':'UNKNOWN_EXACT_BOARD','control':'Do not infer XM silicon or5/10 qualification from the marketing family'}]
    result={'stage':'353A','task_id':'T-S353A-SUB20-PLL-OFDM','static_sources':sources,
            'upstream_manifest':c.binding(root/MANIFEST,root),'source_version':'Linuxv6.6.110 plus separately qualified vendor ELF',
            'binary_dissection':modules,'matrix':matrix,'timing_matrix':[timing(w) for w in (20,10,5)],
            'source_findings':{'ath10k_upstream_5_10_phymode_cases':False,
                             'qca6174_pll_code_is_qca988x_proof':False,
                             'regdomain_half_quarter_bits_are_runtime_support_proof':False},
            'gaps':['Exact installed firmware accepts and applies sub20 command','Native PLL readback and lock, spectral mask/EVM and legal channel eligibility','Exact XW/XM board/radio identity and boot recovery','VHT5/10 and peer interoperability not established'],
            'summary':{'families':4,'bandwidth_rows':3,'hardware_results':0},
            'boundary':{'hardware_access':False,'register_write':False,'firmware_modified':False,'physical_acceptance':False},
            'attribution':['Linux ath9k source','ath10k host interface','proprietary vendor ELF static symbols','theoretical legacy OFDM']}
    text='''<!-- doc-head: Stage353A source and binary qualified sub20 PLL and OFDM timing -->
Offline dissection does not establish installed-board sub20 support or regulatory eligibility.
<!-- /doc-head -->

# Stage353A

Parent: reproducible firmware/control-boundary RE1. Question: where are actual
half/quarter clock and timing controls, and where are only ABI names or bits?
Run `python tools/re/build_stage353a_sub20mhz_pll_ofdm_timing_matrix.py`.
The dedicated JSON retains hashed Linuxv6.6.110 sources with line anchors and
held vendor ELF symbol offsets, bytes, hashes and first MIPS instructions.
No module is executed, loaded, patched, or used to write a register.

| Legacy OFDM width | Divisor | Useful+GI us | Symbol us | Spacing kHz | ath9k5GHz SIFS/slot us |
| :--- | ---: | :--- | ---: | ---: | :--- |
| 20MHz | 1 | 3.2+0.8 | 4 | 312.5 | 16/9 |
| 10MHz | 2 | 6.4+1.6 | 8 | 156.25 | 32/13 |
| 5MHz | 4 | 12.8+3.2 | 16 | 78.125 | 64/21 |

Slot time is NOT naively multiplied by2/4. The ACK values in JSON are upstream
pre-coverage settings, not universal over-air ACK durations or timeout getters.
The20MHz row assumes ah->slottime=9; every ACK/slot row excludes dynack and
uses coverage_class=0. Actual configured slot, coverage and dynack can change it.
Noise-bandwidth arithmetic assumes fixed NF and temperature; it is not measured gain.
These are legacy OFDM timing models, not proof of VHT operation at5/10MHz.

ath9k ar9003 has PLL CLKSEL half/quarter branches and delta-slope scaling.
AR934x/QCA955x host identification alone does not identify the actual RF path.
WA/XC QCA988x remains firmware-offloaded: inspected upstream chan_to_phymode
has no5/10 cases. Regulatory capability bits, fork flags, vendor named tables,
and chanbw ioctl metadata do not authenticate a working end-to-end control path.
The qca6174 PLL function is not a QCA988x PLL recipe. XM is not one silicon revision.

Primary anchors: [ath9k hw.c](https://github.com/gregkh/linux/blob/v6.6.110/drivers/net/wireless/ath/ath9k/hw.c),
[ar9003_phy.c](https://github.com/gregkh/linux/blob/v6.6.110/drivers/net/wireless/ath/ath9k/ar9003_phy.c),
[ath10k mac.c](https://github.com/gregkh/linux/blob/v6.6.110/drivers/net/wireless/ath/ath10k/mac.c).
The source cache and module pins are the reproducibility record; observed hardware
support, spectral compliance, PLL lock and peer interoperability remain UNKNOWN.
Decision: KEEP this offline matrix; no device configuration or sub20 enablement.
'''
    c.write_doc(root/DOC,text);result['outputs']={DOC:c.binding(root/DOC,root)};c.write_json(root/OUT,result)
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    args=p.parse_args(argv);print(build(args.root)['summary']);return 0


if __name__=='__main__':raise SystemExit(main())
