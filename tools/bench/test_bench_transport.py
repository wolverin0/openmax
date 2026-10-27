"""Offline transport and wireless-only recovery guards; never contacts radios."""
import os
import unittest
from unittest.mock import patch

from tools.bench import bench


class TransportTests(unittest.TestCase):
    def capture(self, host):
        with patch.object(bench.subprocess, 'run') as run:
            run.return_value.stdout = 'ok\n'
            run.return_value.stderr = ''
            run.return_value.returncode = 0
            self.assertEqual(bench.ssh(host, 'echo ok'), ('ok', '', 0))
            return run.call_args.args[0]

    @patch.dict(os.environ, {'FMX_CPE_VIA_AP': '1'})
    def test_wireless_cpe_uses_proxy_and_air_address(self):
        args = self.capture(bench.CPE)
        self.assertEqual(args[-2:], ['root@10.99.0.2', 'echo ok'])
        proxy = next(arg for arg in args if arg.startswith('ProxyCommand='))
        self.assertIn('root@192.168.1.2', proxy)
        self.assertIn('%h:%p', proxy)

    @patch.dict(os.environ, {'FMX_CPE_VIA_AP': '0'})
    def test_legacy_direct_route_preserved(self):
        self.assertEqual(self.capture(bench.CPE)[-2], 'root@192.168.1.3')

    @patch.dict(os.environ, {'FMX_CPE_VIA_AP': '1'})
    def test_ap_stays_direct(self):
        args = self.capture(bench.AP)
        self.assertEqual(args[-2], 'root@192.168.1.2')
        self.assertFalse(any(arg.startswith('ProxyCommand=') for arg in args))

    @patch.dict(os.environ, {'FMX_CPE_VIA_AP': '1'})
    def test_unsafe_legacy_operations_fail_before_any_ssh(self):
        for operation, argument in [(bench.set_txpower, 0),
                                    (bench.set_htmode, 'VHT20'),
                                    (bench.cmd_persist, None)]:
            with self.subTest(operation=operation.__name__):
                with patch.object(bench, 'ssh') as ssh, \
                     patch.object(bench.time, 'sleep'), \
                     patch.object(bench, 'wait_link', return_value=False):
                    with self.assertRaisesRegex(RuntimeError, 'wireless-only'):
                        operation(argument)
                    ssh.assert_not_called()


if __name__ == '__main__':
    unittest.main()
