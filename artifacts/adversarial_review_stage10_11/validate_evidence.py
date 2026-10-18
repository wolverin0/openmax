"""Validate report provenance and decisive evidence without target execution."""
import hashlib
import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
checks = []


def check(name, condition):
    checks.append({'name': name, 'passed': bool(condition)})
    if not condition:
        raise AssertionError(name)


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


for entry in read('manifest.json'):
    p = ROOT / entry['path']
    content = p.read_bytes()
    check('input unchanged: ' + entry['path'],
          len(content) == entry['size'] and hashlib.sha256(content).hexdigest() == entry['sha256'])

containers = read('containers.json')
for name, value in containers.items():
    if name.startswith('afltu'):
        check(name + ': all payload digests match', all(p['md5_matches'] for p in value['parts']))
        check(name + ': no unparsed trailer', value['tail_bytes'] == 0)

sites = read('patch_sites.json')
for name, value in sites.items():
    check(name + ': original patch instruction words',
          [s['original'] for s in value['sites']] == ['0c000000', '14400006', '0002102b'])
    check(name + ': first site retains R_MIPS_26',
          any('ubnt_poll_host_sta_bmiss_ind' in s and 'type=4' in s for s in value['sites'][0]['assembly']))
check('WA proposed patch MD5 reproduces reported value',
      sites['wa_8725']['patched_md5'] == '3f2e756225bf67947abcc5dd46bccd9d')
check('WA/XC local neighborhoods identical', all(s['xc_96_byte_context_identical'] for s in sites['wa_8725']['sites']))

boards = read('xc_boards.json')
check('34 XC records', len(boards) == 34)
check('old Rocket records retain actual sysid', all(boards[i]['sysid'] == '0xe3f5' for i in (11, 12, 13)))
check('ISO example has two radios', boards[4]['model'] == 'PBE-5AC-500-ISO' and boards[4]['radio_count'] == 2)

table = read('prism_table.json')
edge_match = next(i for i, row in enumerate(table) if row[0] == 1 and row[1] <= 5200 and row[2] >= 5280 and row[10] >= 80)
center_match = next(i for i, row in enumerate(table) if row[0] == 1 and row[1] <= 5240 <= row[2] and row[10] >= 80)
check('prism example differentiates edge/center algorithms', edge_match == 4 and center_match == 0)
check('OFDMA decimal example is 0xc7', int('11111111', 10) & 0xff == 0xc7)

dtbs = read('dtb_properties.json')
for name, properties in dtbs.items():
    if name.endswith(':dtb'):
        check(name + ': EEPROM location', properties['/soc/nand@F0900000/partition@nand-eeprom/reg'] == '00240000000c0000')
        check(name + ': cfg location', properties['/soc/nand@F0900000/partition@nand-config/reg'] == '00300000000c0000')

report_path = ROOT / 'docs/ADVERSARIAL_REVIEW_STAGE10_11.md'
report = report_path.read_text(encoding='utf-8')
check('report has no trailing whitespace', all(line == line.rstrip() for line in report.splitlines()))
check('report has no conflict markers', not any(line.startswith(('<<<<<<< ', '=======', '>>>>>>> ')) for line in report.splitlines()))
for link in re.findall(r'\]\((\.\./[^)]+)\)', report):
    check('report link exists: ' + link, (report_path.parent / link).exists())
check('report omits device addresses', not re.search(r'\b(?:10\.10\.|192\.168\.1\.)\d', report))
check('report includes all finding IDs', all(f'### F{i:02d}' in report for i in range(1, 15)))
result = {'status': 'PASS', 'check_count': len(checks), 'checks': checks,
          'report_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest(),
          'scope': 'Offline artifact consistency only; no firmware execution or hardware acceptance.'}
(OUT / 'validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(f"PASS: {len(checks)} offline provenance/consistency checks; report SHA256 {result['report_sha256']}")
