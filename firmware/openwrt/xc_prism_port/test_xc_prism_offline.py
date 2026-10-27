"""Disposable host fixtures only; never calls a radio/GPIO/network backend."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCRIPT = HERE / 'fmx-airprism-tuner.sh'
BASH = Path('C:/Program Files/Git/bin/bash.exe')
TABLE = ROOT / 'artifacts/adversarial_review_stage10_11/prism_table.json'
TABLE_SHA = '57a91beecd7329e1063dab757c35dc9173fdb9cde67fb1921d37d6c2dae99b6a'


def run(*args):
    return subprocess.run([str(BASH), str(SCRIPT), *map(str, args)],
                          text=True, capture_output=True, timeout=10)


class OfflinePrism(unittest.TestCase):
    def test_syntax_and_noop_default_live_refusal(self):
        result = subprocess.run([str(BASH), '-n', str(SCRIPT)],
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(run().returncode, 0)
        self.assertIn('PLAN_ONLY', run().stdout)
        self.assertNotEqual(run('--live', '5180', '20').returncode, 0)

    def test_exact_six_record_table_and_first_match_vectors(self):
        self.assertEqual(hashlib.sha256(TABLE.read_bytes()).hexdigest(), TABLE_SHA)
        table = json.loads(TABLE.read_text())
        embedded = SCRIPT.read_text().split("cat <<'TABLE'\n", 1)[1].split('\nTABLE', 1)[0]
        rows = [list(map(int, line.split())) for line in embedded.splitlines()]
        # Column nine in the original record is a reserved zero, not a pin.
        self.assertEqual([r[1:] for r in rows], [r[:9] + [r[10]] for r in table])
        vectors = [(5180, 20), (5230, 20), (5240, 80), (5500, 40),
                   (5775, 40), (5775, 80), (6000, 160), (5200, 100),
                   (5495, 50), (5495, 51), (5152, 5), (5250, 1),
                   (5260, 20), (5860, 20), (3080, 160), (6120, 160)]
        selected = set()
        for center, width in vectors:
            lo, hi = center - width // 2, center + width // 2
            expected = [next((i for i, row in enumerate(table)
                              if row[0] & stage and lo >= row[1] and
                              hi <= row[2] and width <= row[10]), None)
                        for stage in (1, 2)]
            result = run('--dry-run', center, width)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            m = re.search(r'stage1_entry=(\d+) stage2_entry=(\d+) bits_gpio16_to_13=(\d+)', result.stdout)
            self.assertIsNotNone(m, result.stdout)
            self.assertEqual(list(map(int, m.groups()[:2])), expected)
            selected.update(expected)
            a, b = table[expected[0]], table[expected[1]]
            bits = b[7] + 2 * b[8] + 4 * a[5] + 8 * a[6]
            self.assertEqual(int(m[3]), bits)
        self.assertEqual(selected, set(range(6)))

    def test_fixture_order_blanking_and_no_hardware(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'exclusive'
            result = run('--fixture', folder.as_posix(), 5240, 80)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            trace = (folder / 'trace.log').read_text()
            self.assertLess(trace.index('BLANK_CONFIRMED_MODEL'), trace.index('GPIO_MODEL'))
            self.assertLess(trace.index('VERIFY_MODEL'), trace.index('UNBLANK_MODEL_ONLY'))
            self.assertEqual(re.findall(r'GPIO_MODEL pin=(\d+) value=(\d)', trace),
                             [('15', '0'), ('16', '1'), ('13', '1'), ('14', '0')])
            self.assertIn('rf_enabled=0', (folder / 'state.txt').read_text())
            # Existing output/owner must never be adopted or overwritten.
            before = (folder / 'trace.log').read_bytes()
            self.assertNotEqual(run('--fixture', folder.as_posix(), 5180, 20).returncode, 0)
            self.assertEqual((folder / 'trace.log').read_bytes(), before)

    def test_every_failure_stays_blank_never_unblanks(self):
        for stage in ('blank', 'gpio15', 'gpio16', 'gpio13', 'gpio14', 'verify', 'unblank'):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp) / 'attempt'
                result = run('--fixture', folder.as_posix(), 5775, 80, stage)
                self.assertNotEqual(result.returncode, 0)
                trace = (folder / 'trace.log').read_text()
                self.assertNotIn('UNBLANK_MODEL_ONLY', trace)
                self.assertNotIn('PASS_OFFLINE_SEQUENCE', trace)
                state = (folder / 'state.txt').read_text()
                self.assertIn('model_blanked=' + ('unknown' if stage == 'blank' else '1'), state)
                self.assertIn('rf_enabled=0', state)
                if stage == 'blank':
                    self.assertNotIn('GPIO_MODEL', trace)

    def test_invalid_or_uncovered_input_cannot_switch(self):
        for center, width in [('05200', '20'), ('5180', '0'), ('5180', '161'),
                              ('3000', '160'), ('6200', '20'), ('5180', '2+2'),
                              ('999999999999999', '20'), ('-1', '20')]:
            result = run('--dry-run', center, width)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('GPIO_MODEL', result.stdout)
            self.assertNotIn('UNBLANK_MODEL_ONLY', result.stdout)

    def test_dts_has_no_adopted_flash_calibration_or_live_radios(self):
        common = (HERE / 'qca9558_ubnt_xc_prism_gen2.dtsi').read_text()
        self.assertIn('#include "qca955x.dtsi"', common)
        for node in ('pcie0', 'pcie1', 'wmac', 'spi', 'mdio0', 'mdio1', 'eth0', 'eth1'):
            self.assertIn('&' + node + ' { status = "disabled"; };', common)
        # Strip comments before checking live bindings, not prose disclaimers.
        code = re.sub(r'/\*.*?\*/', '', common, flags=re.S)
        for forbidden in ('reg =', 'gpios =', 'gpio-hog', 'nvmem-cells', 'partition@'):
            self.assertNotIn(forbidden, code)
        for name in ('rocket-prism-5ac-gen2', 'prismstation-5ac'):
            dts = (HERE / ('qca9558_ubnt_' + name + '.dts')).read_text()
            self.assertIn('#include "qca9558_ubnt_xc_prism_gen2.dtsi"', dts)
            self.assertIn('experimental offline draft', dts)


if __name__ == '__main__':
    unittest.main(verbosity=2)
