"""Offline launcher/build contract checks; never starts the notebook helper."""
from pathlib import Path
import hashlib
import unittest
import zipfile

ROOT = Path(__file__).resolve().parent


class NotebookLauncherTests(unittest.TestCase):
    def test_launcher_uses_system_powershell_and_remote_signed(self):
        cmd = (ROOT / 'START_FUTURAMAX.cmd').read_text()
        self.assertIn('"%SystemRoot%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"', cmd)
        self.assertIn('-NoProfile -ExecutionPolicy RemoteSigned -File', cmd)
        for forbidden in ('Bypass', 'Unrestricted', 'Set-ExecutionPolicy', '-Command'):
            self.assertNotIn(forbidden.lower(), cmd.lower())

    def test_paths_quoted_without_trailing_backslash_or_delayed_expansion(self):
        cmd = (ROOT / 'START_FUTURAMAX.cmd').read_text()
        self.assertIn('setlocal DisableDelayedExpansion', cmd)
        self.assertIn('-File "%~dp0start_notebook_server.ps1" -BundleRoot "%~dp0."', cmd)
        # Exercise literal substitutions, including cmd metacharacters and spaces.
        line = next(line for line in cmd.splitlines() if line.startswith('"%SystemRoot%'))
        for parent in ('C:\\Notebook files\\', 'C:\\A&B (lab)!^%\\'):
            expanded = line.replace('%SystemRoot%', 'C:\\Windows').replace('%~dp0', parent)
            self.assertIn(f'-File "{parent}start_notebook_server.ps1"', expanded)
            self.assertIn(f'-BundleRoot "{parent}."', expanded)

    def test_success_does_not_pause_and_failure_preserves_exit(self):
        cmd = (ROOT / 'START_FUTURAMAX.cmd').read_text()
        before, after = cmd.split(':failed', 1)
        self.assertIn('if errorlevel 1 goto failed', before)
        self.assertIn('exit /b 0', before)
        self.assertNotIn('pause', before.lower())
        self.assertIn('pause', after)
        self.assertIn('set "FUTURAMAX_EXIT=%errorlevel%"', after)
        self.assertIn('exit /b %FUTURAMAX_EXIT%', after)

    def test_builder_is_offline_non_destructive_and_uniquely_named(self):
        script = (ROOT / 'build_notebook_bundle.ps1').read_text()
        for forbidden in ('Invoke-WebRequest', 'Invoke-RestMethod', 'https://', 'Remove-Item',
                          'New-NetRoute', 'New-NetFirewallRule', 'Start-Process', 'Expand-Archive'):
            self.assertNotIn(forbidden, script)
        self.assertIn("Join-Path $PSScriptRoot '..\\..'", script)
        self.assertIn("'notebook-bundle-'", script)
        self.assertIn('[guid]::NewGuid()', script)
        self.assertIn('refusing overwrite', script)
        self.assertIn('ExtractToFile', script)
        self.assertIn('manifest.json', script)
        self.assertIn('FuturaMAX-Notebook.zip.sha256', script)

    def test_builder_pins_exact_member_names_and_contents(self):
        script = (ROOT / 'build_notebook_bundle.ps1').read_text()
        core = (ROOT / 'notebook_core.ps1').read_text()
        specs = {
            '32': ('iperf3/', 'cedbca03a029ec35081b0466ab5d9aade099105bdabcf3c413204e9efa3b8a7c',
                   '5ed5046041a53dad4e25945c0703739b95f68bf5477045c9beb5c7cd20288445',
                   'f1f04586da69854a6e00f978dca5edb8318bd585f51aa88c5fd6ba9b0e3fbb65'),
            '64': ('', 'c9feabb3d721039508ccb81f74c2ada3ae11b9e75d33d24510573c2aa21da420',
                   'bcafba4aff825fa94685b6b3d049f8b1338c69e6dc1d06e6a00ac046191e4999',
                   'd66788fce4ef1ce787fc1a83f2dd1e063e58bbf0d48ad93164ee195a983c035e'),
        }
        self.assertIn('Get-FmxRuntimeSpec -Architecture $architecture', script)
        self.assertIn("@('x86', 'x64')", script)
        self.assertIn('$seen.ContainsKey($entry.FullName)', script)
        self.assertIn('$directoryCount -gt 1', script)
        self.assertIn('-ceq $entry.FullName', script)
        for bits, (prefix, archive_hash, exe_hash, dll_hash) in specs.items():
            with self.subTest(architecture=bits):
                archive = ROOT / 'packages' / f'iperf-3.22-win{bits}.zip'
                self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), archive_hash)
                with zipfile.ZipFile(archive) as package:
                    files = {name for name in package.namelist() if not name.endswith('/')}
                    self.assertEqual(files, {prefix + 'iperf3.exe', prefix + 'cygwin1.dll'})
                    for name, expected in (('iperf3.exe', exe_hash), ('cygwin1.dll', dll_hash)):
                        self.assertEqual(hashlib.sha256(package.read(prefix + name)).hexdigest(), expected)
                        self.assertIn(expected, core)
                self.assertIn(archive_hash, core)

    def test_bundle_contains_only_declared_helpers_and_offline_runtime(self):
        script = (ROOT / 'build_notebook_bundle.ps1').read_text()
        for filename in ('START_FUTURAMAX.cmd', 'start_notebook_server.ps1',
                         'notebook_watchdog.ps1', 'notebook_core.ps1', 'RUN_ON_NOTEBOOK.md', 'RUNTIME_PROVENANCE.md'):
            self.assertIn(filename, script)
        self.assertIn("'packages\\' + $spec.ArchiveName", script)
        self.assertIn("'runtime\\' + $spec.Architecture", script)
        self.assertIn('Test-FmxPEMachine -Path $destination -Machine $spec.Machine', script)


if __name__ == '__main__':
    unittest.main()
