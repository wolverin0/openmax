"""Offline notebook bootstrap regressions; no radios or network requests."""
import hashlib
from pathlib import Path
import unittest
import zipfile


ROOT = Path(__file__).resolve().parent


class OfflineNotebookPackageTests(unittest.TestCase):
    def test_bootstrap_has_no_download_dependency(self):
        script = (ROOT / 'start_notebook_server.ps1').read_text(encoding='utf-8')
        script += (ROOT / 'notebook_core.ps1').read_text(encoding='utf-8')
        for token in ('Invoke-WebRequest', 'Invoke-RestMethod', 'https://', 'winget'):
            self.assertNotIn(token, script)
        self.assertIn("Join-Path $BundleRoot ('packages\\' + $spec.ArchiveName)", script)

    def test_archive_is_pinned_and_readable(self):
        for bits, expected in (
            ('64', 'c9feabb3d721039508ccb81f74c2ada3ae11b9e75d33d24510573c2aa21da420'),
            ('32', 'cedbca03a029ec35081b0466ab5d9aade099105bdabcf3c413204e9efa3b8a7c'),
        ):
            with self.subTest(architecture=bits):
                archive = ROOT / 'packages' / f'iperf-3.22-win{bits}.zip'
                self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), expected)
                with zipfile.ZipFile(archive) as package:
                    self.assertIsNone(package.testzip())
                    self.assertEqual(sum(name.endswith('/iperf3.exe') or name == 'iperf3.exe'
                                         for name in package.namelist()), 1)

    def test_validation_precedes_network_mutations(self):
        script = (ROOT / 'start_notebook_server.ps1').read_text(encoding='utf-8')
        for marker in ('if ($ValidatePackageOnly)', 'Copy-FmxRuntime $BundleRoot'):
            for mutation in ('New-NetRoute', 'New-NetFirewallRule'):
                self.assertLess(script.index(marker), script.index(mutation))
        self.assertLess(script.index('if ($ValidatePackageOnly)'), script.index('-Verb RunAs'))
        self.assertLess(script.index('if ($ValidatePackageOnly)'), script.index('Initialize-FmxRunRoot'))

    def test_runtime_validates_both_members_and_has_builtin_zip_fallback(self):
        core = (ROOT / 'notebook_core.ps1').read_text(encoding='utf-8')
        for name in ('iperf3.exe', 'cygwin1.dll'):
            self.assertIn(name, core)
        self.assertIn('bcafba4aff825fa94685b6b3d049f8b1338c69e6dc1d06e6a00ac046191e4999', core)
        self.assertIn('d66788fce4ef1ce787fc1a83f2dd1e063e58bbf0d48ad93164ee195a983c035e', core)
        self.assertIn('5ed5046041a53dad4e25945c0703739b95f68bf5477045c9beb5c7cd20288445', core)
        self.assertIn('f1f04586da69854a6e00f978dca5edb8318bd585f51aa88c5fd6ba9b0e3fbb65', core)
        self.assertIn('[IO.Compression.ZipFile]::OpenRead($zip)', core)
        self.assertIn('Runtime checksum failed', core)
        self.assertIn('Test-FmxPEMachine', core)

    def test_notebook_address_is_discovered_not_fixed(self):
        script = (ROOT / 'start_notebook_server.ps1').read_text(encoding='utf-8')
        core = (ROOT / 'notebook_core.ps1').read_text(encoding='utf-8')
        self.assertNotIn('192.168.1.170', script)
        self.assertIn('Select-FmxAdapter', script)
        self.assertIn('88ae1d73e1c3', core)
        self.assertIn('-LocalAddress $nic.IPv4', script)

    def test_launcher_and_uac_do_not_weaken_execution_policy(self):
        text = '\n'.join((ROOT / name).read_text(encoding='utf-8') for name in
                         ('START_FUTURAMAX.cmd', 'start_notebook_server.ps1', 'notebook_watchdog.ps1'))
        self.assertIn('-ExecutionPolicy RemoteSigned', text)
        for token in ('-ExecutionPolicy Bypass', '-ExecutionPolicy Unrestricted', 'Set-ExecutionPolicy'):
            self.assertNotIn(token, text)


if __name__ == '__main__':
    unittest.main()
