"""Run with the held Flent2.3.0 private Python; all subprocesses forbidden."""
import copy
import importlib.util
import shlex
import unittest
from unittest.mock import PropertyMock, patch

import rrul_profile as profile


class PurePlanTests(unittest.TestCase):
    def test_plan_is_pure_and_mapping_immutable(self):
        with patch("builtins.open", side_effect=AssertionError("file I/O")), \
             patch("subprocess.Popen", side_effect=AssertionError("process")):
            result = profile.plan()
        self.assertEqual(result["status"], "PLAN_ONLY_NOT_ADMITTED")
        self.assertEqual([f["remote_port"] for f in result["flows"]],
                         list(range(5210, 5221)) + [None])
        result["flows"][0]["remote_port"] = 1
        self.assertEqual(profile.FLOWS[0].remote_port, 5210)
        with self.assertRaises(AttributeError):
            profile.FLOWS[0].remote_port = 1

    def test_plan_rejects_hostname(self):
        with self.assertRaises(ValueError):
            profile.plan("example.com")


@unittest.skipUnless(importlib.util.find_spec("flent"), "held Flent runtime required")
class ActualCanonicalTests(unittest.TestCase):
    def setUp(self):
        # Any implicit capability probe/connection, fork or process is forbidden.
        self.forbid = patch("subprocess.Popen", side_effect=AssertionError("no traffic/process"))
        self.forbid.start()
        self.addCleanup(self.forbid.stop)
        self.original = profile.load_canonical()
        self.adapted = profile.build_profile(self.original, version="2.3.0")

    def test_actual_canonical_unchanged_except_eleven_arguments(self):
        self.assertEqual(len(self.adapted.DATA_SETS), 18)
        self.assertNotIn("extra_test_args", self.original.DATA_SETS["TCP upload BE"])
        self.assertEqual(profile.validate_profile(self.original, self.adapted,
                                                 version="2.3.0")["total_length"], 62)
        for name, original in self.original.DATA_SETS.items():
            candidate = dict(self.adapted.DATA_SETS[name])
            candidate.pop("extra_test_args", None)
            self.assertEqual(profile._stable(candidate), profile._stable(original))
        self.assertEqual(profile._stable(self.original.PLOTS), profile._stable(self.adapted.PLOTS))

    def test_eleven_commands_from_actual_flent_runners_no_execution(self):
        from flent import runners
        cache = {"": {"executable": "/held/netperf", "-e": True, "buffer": ""}}
        commands = []
        with patch.object(runners.NetperfDemoRunner, "cache", new_callable=PropertyMock,
                          return_value=cache), \
             patch.object(runners.IrttRunner, "check", side_effect=runners.RunnerCheckError("no irtt")), \
             patch.object(runners.ProcessRunner, "run_simple", side_effect=AssertionError("capability probe")):
            for flow in profile.FLOWS:
                if flow.remote_port is None:
                    continue
                cfg = copy.deepcopy(self.adapted.DATA_SETS[flow.dataset])
                cls = runners.get(cfg.pop("runner"))
                runner = cls(name=flow.dataset, settings=self.adapted, **cfg)
                runner.check()
                if flow.protocol == "UDP":
                    self.assertEqual(len(runner._child_runners), 1)
                    runner = runner._child_runners[0]
                    self.assertIsInstance(runner, runners.NetperfDemoRunner)
                argv = shlex.split(runner.command)
                control, data = argv[:argv.index("--")], argv[argv.index("--")+1:]
                self.assertEqual(control[control.index("-p")+1], "5205")
                self.assertEqual(control[control.index("-t")+1], flow.test)
                self.assertEqual(control[control.index("-l")+1], "60" if flow.protocol == "TCP" else "62")
                self.assertEqual(data[data.index("-P")+1], "0,"+str(flow.remote_port))
                self.assertEqual(data.count("-P"), 1)
                commands.append(runner.command)
        self.assertEqual(len(commands), 11)

    def test_wrong_version_or_profile_refused(self):
        with self.assertRaises(ValueError):
            profile.build_profile(self.original, version="2.2.0")
        self.original.NAME = "rrul_be"
        with self.assertRaises(ValueError):
            profile.build_profile(self.original, version="2.3.0")

    def test_missing_dataset_and_overrides_refused(self):
        for change in (lambda s: s.DATA_SETS.pop("Ping (ms) ICMP"),
                       lambda s: s.DATA_SETS["TCP upload BE"].update(extra_test_args="-P 0,9999"),
                       lambda s: s.DATA_SETS["TCP upload BE"].update(marking="EF,EF"),
                       lambda s: s.TEST_PARAMETERS.update(tcp_cong_control="other")):
            with self.subTest(change=change):
                s = copy.deepcopy(self.original)
                change(s)
                with self.assertRaises(ValueError):
                    profile.build_profile(s, version="2.3.0")

    def test_collision_and_tampered_metadata_refused(self):
        with patch.object(profile, "FLOWS", profile.FLOWS[:1]+(
                profile.Flow("TCP upload BK", "TCP", "TCP_STREAM", 5210),)+profile.FLOWS[2:]):
            with self.assertRaises(ValueError):
                profile.build_profile(self.original, version="2.3.0")
        for change in (lambda s: s.DATA_SETS["TCP download EF"].update(extra_test_args="-P 0,5210"),
                       lambda s: s.DATA_SETS["TCP totals"].update(units="changed"),
                       lambda s: setattr(s, "DELAY", 0)):
            s = copy.deepcopy(self.adapted)
            change(s)
            with self.assertRaises(ValueError):
                profile.validate_profile(self.original, s, version="2.3.0")


if __name__ == "__main__":
    unittest.main()
