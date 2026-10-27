"""Offline fixtures only; no ucode execution, SSH, radio or load commands."""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shlex
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location("survival",Path(__file__).with_name("radio_survival_observer.py"))
observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
TAG="a"*32
BOOT="11111111-2222-3333-4444-555555555555"


def sample(seq=0, role="cpe"):
    return dict(schema=observer.SCHEMA,status=observer.STATUS,kind="sample",role=role,tag=TAG,
        seq=seq,planned_seconds=2,boot_id=BOOT,uptime_start_s=700000+seq,sample_duration_ms=30,
        policy=dict(min_free_kbytes=8192,watermark_boost_factor=15000),
        memory=dict(MemTotal=56120,MemFree=10000,MemAvailable=5000,Slab=8000),
        normal=dict(free_pages=2500,min_pages=2048,boost_pages=0),
        services=dict(hostapd=[dict(pid=3427,start_ticks=661685),dict(pid=3428,start_ticks=661761)],
                      wpa_supplicant=[dict(pid=1409,start_ticks=3967)]),
        observer=dict(pid=9000,start_ticks=70000000,rss_kb=1800,utime_ticks=2,stime_ticks=3),
        oom=dict(records=[dict(timestamp="699148.126818",line="[699148.126818] Out of memory: Killed process 1434 (hostapd)")],
                 bytes=10000,first_line="[    0.000000] Linux version fixture"))


def feed(stream, value, now, age=20):
    return stream.feed(json.dumps(value)+"\n",transport_age_ms=age,received_monotonic=now)


class ObserverTests(unittest.TestCase):
    def test_explicit_duration_bound_accepts_45_and_84_but_rejects_85(self):
        for seconds in (30, 45, 84):
            with self.subTest(seconds=seconds):
                generated=observer.plan("ap",TAG,seconds)
                self.assertEqual(generated["seconds"],seconds)
                self.assertIn("SECONDS="+str(seconds)+";",observer.ucode_source("ap",TAG,seconds))
                self.assertEqual(observer.ObserverStream("ap",TAG,seconds).seconds,seconds)
        for seconds in (0, 85, True, 45.0):
            with self.subTest(seconds=seconds),self.assertRaises(ValueError):
                observer.plan("ap",TAG,seconds)

    def test_45_second_stream_requires_fresh_samples_and_full_terminal(self):
        def value(seq):
            record=sample(seq)
            record["planned_seconds"]=45
            return record
        complete=observer.ObserverStream("cpe",TAG,45)
        for seq in range(46):
            feed(complete,value(seq),10+seq)
        terminal=dict(schema=observer.SCHEMA,status=observer.STATUS,kind="end",role="cpe",tag=TAG,
                      seq=46,planned_seconds=45,elapsed_seconds=45.01)
        feed(complete,terminal,55.01)
        self.assertEqual(complete.finish(),dict(status=observer.STATUS,complete=True,samples=46,
                                               load_ready=False,execution_gate_cleared=False))
        for count in (20,46):
            with self.subTest(early_eof_samples=count):
                partial=observer.ObserverStream("cpe",TAG,45)
                for seq in range(count):feed(partial,value(seq),10+seq)
                with self.assertRaises(observer.ObservationError):partial.finish()
        early=observer.ObserverStream("cpe",TAG,45)
        for seq in range(20):feed(early,value(seq),10+seq)
        with self.assertRaisesRegex(observer.ObservationError,"incomplete/stale terminal"):
            feed(early,dict(terminal,seq=20,elapsed_seconds=20.01),29.01)
        stale=observer.ObserverStream("cpe",TAG,45)
        for seq in range(44):feed(stale,value(seq),10+seq)
        expired=value(44);expired["sample_duration_ms"]=1981
        with self.assertRaisesRegex(observer.ObservationError,"stale sample"):
            feed(stale,expired,54)
        with self.assertRaises(observer.ObservationError):stale.finish()

    def test_dmesg_errors_are_operation_scoped_and_current_read_close_errors_rejected(self):
        source=observer.ucode_source("ap",TAG,20)
        body=source.split("function oom() {\n",1)[1].split("    if (substr(text,-1)",1)[0]
        # A stale error may originate in an allowed vanished unrelated proc read.
        # Clear it only before the new operation, never after the current read.
        self.assertIn("fs.error();\n    let p=fs.popen('dmesg','r');",body)
        self.assertEqual(body.count("fs.error();"),2)  # before open and immediately after close
        ordered=["fs.error();", "fs.popen('dmesg','r')", "p.read(LIMIT+1)",
                 "error=p.error()", "rc=p.close()", "close_error=fs.error()"]
        indexes=[body.index(part) for part in ordered]
        self.assertEqual(indexes,sorted(indexes))
        self.assertIn("text==null || error!=null || rc!==0 || close_error!=null || !length(text) || length(text)>LIMIT",body)
        for field in ("text_null", "text_length", "read_error", "close_rc", "close_error", "limit"):
            self.assertIn(field+":",body)

    def test_structured_dmesg_abort_still_fails_closed_without_terminal(self):
        for details in (dict(text_null=True,text_length=None,read_error="I/O error",close_rc=0,close_error=None,limit=131072),
                        dict(text_null=False,text_length=11477,read_error=None,close_rc=1,close_error=None,limit=131072),
                        dict(text_null=False,text_length=11477,read_error=None,close_rc=None,close_error="No child processes",limit=131072)):
            stream=observer.ObserverStream("cpe",TAG,2)
            record=dict(schema=observer.SCHEMA,status=observer.STATUS,kind="abort",role="cpe",tag=TAG,
                        seq=0,planned_seconds=2,reason="dmesg error/empty/truncated "+json.dumps(details))
            with self.assertRaisesRegex(observer.ObservationError,"remote abort"):
                feed(stream,record,10)
            with self.assertRaises(observer.ObservationError):stream.finish()

    def test_regexes_are_hoisted_once_with_exact_prior_payload_semantics(self):
        mappings={
            "RX_UINT":r"/^[0-9]+$/", "RX_PROCESS":r"/^([0-9]+) \((.*)\) (.*)$/",
            "RX_SPACES":r"/ +/", "RX_MEMFIELD":r"/^([A-Za-z_]+): +([0-9]+) kB$/",
            "RX_MEMKEY":r"/^(MemTotal|MemFree|MemAvailable|Cached|Slab|SReclaimable|SUnreclaim|PageTables|KernelStack)$/",
            "RX_ZONEHEAD":r"/^Node +[0-9]+, +zone +([^ ]+) *$/", "RX_ZONEFREE":r"/^ *pages +free +([0-9]+) *$/",
            "RX_ZONEBOUNDS":r"/^ *(min|boost) +([0-9]+) *$/",
            "RX_OOMMARK":r"/invoked oom-killer:|oom-kill:|Out of memory:|oom_reaper:/",
            "RX_OOMSTAMP":r"/^\[ *([0-9]+\.[0-9]+)\] +(.+)$/", "RX_RSS":r"/VmRSS:[ \t]+([0-9]+) kB/",
        }
        source=observer.ucode_source("cpe",TAG,20)
        restored=source
        # Normalize only the separately tested operation-scoped error repair,
        # then retain the original exact-payload check for the regex hoisting.
        first=restored.index("function oom() {\n")
        last=restored.index("    if (substr(text,-1)",first)
        legacy=("function oom() {\n"
                "    let p=fs.popen('dmesg','r');\n"
                "    if (p==null) die('dmesg unavailable');\n"
                "    let text=p.read(LIMIT+1), error=p.error(), rc=p.close();\n"
                "    if (text==null || error!=null || rc!==0 || !length(text) || length(text)>LIMIT)\n"
                "        die('dmesg error/empty/truncated');\n")
        restored=restored[:first]+legacy+restored[last:]
        for name,literal in mappings.items():
            declaration="const "+name+"="+literal+";\n"
            self.assertEqual(source.count(declaration),1,name)
            self.assertLess(source.index(declaration),source.index("function now()"))
            self.assertNotIn("/g",literal)
            restored=restored.replace(declaration,"").replace(","+name+")",","+literal+")")
        self.assertEqual(hashlib.sha256(restored.encode()).hexdigest(),
                         "fe414ad679a7c6301600ae1fcce316216bfc70aa5ce6f206fbd4efcc9ec188c0")

    def test_send_calls_flush_without_trusting_installed_broken_return(self):
        source=observer.ucode_source("ap",TAG,20)
        body=source.split("function send(record) {",1)[1].split("\n}",1)[0]
        self.assertIn("out.write(line)!=length(line)",body)
        self.assertIn("out.flush();",body)
        self.assertEqual(body.count("out.flush()"),1)
        self.assertNotRegex(body,r"\bif\s*\([^;]*out\.flush")

    def test_first_sample_oom_during_collection_cannot_be_adopted_as_baseline(self):
        for timestamp in ("700000.010001", "700000.000000", "699999.990000"):
            stream=observer.ObserverStream("cpe",TAG,2)
            value=sample()
            value["oom"]["records"]=[dict(timestamp=timestamp,
                line="["+timestamp+"] Out of memory: Killed process 1434 (hostapd)")]
            with self.subTest(timestamp=timestamp),self.assertRaisesRegex(observer.ObservationError,"observation start"):
                feed(stream,value,10)
            self.assertEqual(stream.samples,[])
            with self.assertRaises(observer.ObservationError):stream.finish()
        historical=sample()
        historical["oom"]["records"]=[dict(timestamp="699999.989999",
            line="[699999.989999] Out of memory: Killed process 1434 (hostapd)")]
        stream=observer.ObserverStream("cpe",TAG,2)
        feed(stream,historical,10)
        self.assertEqual(len(stream.samples),1)

    def test_complete_bilateral_streams_never_become_load_ready_or_clear_gate(self):
        for role in ("ap","cpe"):
            stream=observer.ObserverStream(role,TAG,2)
            feed(stream,sample(0,role),10);feed(stream,sample(1,role),11)
            terminal=dict(schema=observer.SCHEMA,status=observer.STATUS,kind="end",role=role,tag=TAG,
                          seq=2,planned_seconds=2,elapsed_seconds=2.01)
            feed(stream,terminal,12)
            result=stream.finish()
            self.assertFalse(result["load_ready"])
            self.assertFalse(result["execution_gate_cleared"])
            self.assertEqual(result["status"],"OBSERVATION_ONLY_NOT_LOAD_READY")
            # Memory below the old AP lease threshold is observable, never permission for load.
            self.assertEqual(stream.samples[0]["normal"]["free_pages"],2500)

    def test_new_oom_reduction_or_timestamp_replacement_aborts(self):
        for change in ("new","reduced","timestamp","truncated","bytes"):
            stream=observer.ObserverStream("cpe",TAG,2);feed(stream,sample(),10)
            changed=sample(1)
            if change=="new": changed["oom"]["records"].append(dict(timestamp="700001.000001",line="[700001.000001] oom-kill: task=wpa_supplicant"))
            if change=="reduced": changed["oom"]["records"]=[]
            if change=="timestamp": changed["oom"]["records"][0]["timestamp"]="1.000000"
            if change=="truncated": changed["oom"]["first_line"]="[1.000000] ring advanced"
            if change=="bytes": changed["oom"]["bytes"]=9999
            with self.subTest(change=change),self.assertRaises(observer.ObservationError):feed(stream,changed,11)
            self.assertEqual(len(stream.samples),1)
            with self.assertRaises(observer.ObservationError):stream.finish()

    def test_wpa_respawn_hostapd_loss_and_boot_policy_changes_are_not_rebaselined(self):
        for field in ("wpa","hostapd","boot","factor","minfree","observer"):
            stream=observer.ObserverStream("cpe",TAG,2);feed(stream,sample(),10);changed=sample(1)
            if field=="wpa":changed["services"]["wpa_supplicant"]=[dict(pid=1435,start_ticks=699251)]
            if field=="hostapd":changed["services"]["hostapd"].pop()
            if field=="boot":changed["boot_id"]="22222222-2222-3333-4444-555555555555"
            if field=="factor":changed["policy"]["watermark_boost_factor"]=0
            if field=="minfree":changed["policy"]["min_free_kbytes"]=4096
            if field=="observer":changed["observer"]["start_ticks"]+=1
            with self.subTest(field=field),self.assertRaises(observer.ObservationError):feed(stream,changed,11)
            with self.assertRaises(observer.ObservationError):feed(stream,sample(1),11)

    def test_missing_stale_malformed_or_ambiguous_data_fails_closed(self):
        for change in ("missing","stale","roster","bool","oom","nan","negative","wrong_type"):
            stream=observer.ObserverStream("cpe",TAG,2);value=sample()
            if change=="missing":del value["normal"]["min_pages"]
            if change=="stale":value["sample_duration_ms"]=1981
            if change=="roster":value["services"]["wpa_supplicant"]=[]
            if change=="bool":value["memory"]["MemFree"]=True
            if change=="oom":value["oom"]["records"][0]["line"]="OOM without timestamp"
            if change=="nan":value["sample_duration_ms"]=float("nan")
            if change=="negative":value["normal"]["free_pages"]=-1
            if change=="wrong_type":value["memory"]="not a memory mapping"
            with self.subTest(change=change),self.assertRaises(observer.ObservationError):feed(stream,value,10)
            self.assertIsNotNone(stream.failed_line)
            with self.assertRaises(observer.ObservationError):feed(stream,sample(),10)
        for line in ('[]\n','{"seq":0,"seq":1}\n','{"schema":','{}'):
            with self.assertRaises(observer.ObservationError):observer.ObserverStream("ap",TAG,2).feed(line,transport_age_ms=0,received_monotonic=10)

    def test_partial_stream_missing_terminal_and_late_last_sample_are_not_complete(self):
        stream=observer.ObserverStream("cpe",TAG,2);feed(stream,sample(),10)
        with self.assertRaises(observer.ObservationError):stream.finish()
        with self.assertRaises(observer.ObservationError):stream.latest(12.1)
        terminal=dict(schema=observer.SCHEMA,status=observer.STATUS,kind="end",role="cpe",tag=TAG,
                      seq=1,planned_seconds=2,elapsed_seconds=2.1)
        with self.assertRaises(observer.ObservationError):feed(stream,terminal,12.1)

    def test_remote_abort_and_missing_middle_sample_invalidate_stream(self):
        stream=observer.ObserverStream("ap",TAG,2);feed(stream,sample(0,"ap"),10)
        missing=sample(2,"ap")
        with self.assertRaises(observer.ObservationError):feed(stream,missing,11)
        stream=observer.ObserverStream("cpe",TAG,2);feed(stream,sample(),10)
        aborted=dict(schema=observer.SCHEMA,status=observer.STATUS,kind="abort",role="cpe",tag=TAG,
                     seq=1,planned_seconds=2,reason="dmesg error/empty/truncated")
        with self.assertRaisesRegex(observer.ObservationError,"remote abort"):feed(stream,aborted,11)

    def test_command_is_one_ucode_process_readonly_and_shell_quoted(self):
        result=observer.plan("cpe",TAG,20)
        argv=shlex.split(result["command"])
        self.assertEqual(argv[:2],["/usr/bin/ucode","-e"])
        self.assertEqual(len(argv),3)
        source=argv[2]
        self.assertEqual(set(re.findall(r"fs\.([a-z]+)\(",source)),{"fdopen","readfile","glob","popen","error"})
        self.assertEqual(re.findall(r"fs\.popen\(([^\n]+)",source),["'dmesg','r');"])
        self.assertIn("out.flush()",source)
        for forbidden in ("writefile", "fs.open(","/dev/kmsg","system(","iperf","uci ","set txpower", "dmesg -c"):
            self.assertNotIn(forbidden,source)
        self.assertEqual(result["seconds"],20)
        for invalid in (0,85,True):
            with self.assertRaises(ValueError):observer.plan("ap",TAG,invalid)
        with self.assertRaises(ValueError):observer.plan("ap",TAG+";bad",20)

    def test_cli_generation_does_not_read_files_or_import_radio_runner(self):
        with patch.object(Path,"read_text",side_effect=AssertionError("file read")), \
             patch.object(Path,"read_bytes",side_effect=AssertionError("file read")), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(observer.main(["--role","ap","--tag",TAG]),0)
        self.assertEqual(json.loads(output.getvalue())["status"],observer.STATUS)
        self.assertEqual(json.loads(output.getvalue())["seconds"],20)


if __name__=="__main__":unittest.main()
