"""Generate a read-only ucode observer and validate its live JSONL stream.

No SSH, load, leases or execution-gate changes. Caller must bound transport,
stream lines promptly and supply a measured transport-age bound, not zero by
assumption. Ucode duration is cooperative; caller owns its outer deadline.
API references: https://ucode-lang.org/ucode/module-fs.html,
module-fs.proc.html, module-fs.file.html and module-core.html.
"""
import argparse
import hashlib
import json
import math
import re
import shlex

STATUS = "OBSERVATION_ONLY_NOT_LOAD_READY"
SCHEMA = "fmx.radio-survival.v1"
MAX_AGE_MS = 2000
MAX_DMESG_BYTES = 131072
OOM_MARKER = re.compile(r"invoked oom-killer:|\boom-kill:|Out of memory:|\boom_reaper:")
OOM_LINE = re.compile(r"^\[\s*([0-9]+\.[0-9]+)\]\s+(.+)$")


def options(role, tag, seconds):
    if role not in ("ap", "cpe") or not re.fullmatch(r"[a-f0-9]{32}", tag):
        raise ValueError("exact ap/cpe role and lowercase 32-hex tag required")
    if type(seconds) is not int or not 1 <= seconds <= 84:
        raise ValueError("duration must be an integer 1..84 seconds")


def ucode_source(role, tag, seconds=20):
    options(role, tag, seconds)
    source = r'''import * as fs from 'fs';
const ROLE=__ROLE__, TAG=__TAG__, SECONDS=__SECONDS__;
const LIMIT=131072;
const RX_UINT=/^[0-9]+$/;
const RX_PROCESS=/^([0-9]+) \((.*)\) (.*)$/;
const RX_SPACES=/ +/;
const RX_MEMFIELD=/^([A-Za-z_]+): +([0-9]+) kB$/;
const RX_MEMKEY=/^(MemTotal|MemFree|MemAvailable|Cached|Slab|SReclaimable|SUnreclaim|PageTables|KernelStack)$/;
const RX_ZONEHEAD=/^Node +[0-9]+, +zone +([^ ]+) *$/;
const RX_ZONEFREE=/^ *pages +free +([0-9]+) *$/;
const RX_ZONEBOUNDS=/^ *(min|boost) +([0-9]+) *$/;
const RX_OOMMARK=/invoked oom-killer:|oom-kill:|Out of memory:|oom_reaper:/;
const RX_OOMSTAMP=/^\[ *([0-9]+\.[0-9]+)\] +(.+)$/;
const RX_RSS=/VmRSS:[ \t]+([0-9]+) kB/;
let out=fs.fdopen(1,'w');
if (out==null) die('stdout unavailable');
function now() {
    let c=clock(true);
    if (c==null) die('monotonic clock unavailable');
    return c[0]+c[1]/1000000000.0;
}
function read(path) {
    let value=fs.readfile(path,32769);
    if (value==null || length(value)>32768) die('missing/truncated proc '+path);
    return value;
}
function uint(value) {
    if (!match(value,RX_UINT)) die('malformed unsigned integer');
    return int(value);
}
function process(text) {
    let m=match(trim(text),RX_PROCESS);
    if (m==null) die('malformed proc stat');
    let f=split(m[3],RX_SPACES);
    if (length(f)<22) die('short proc stat');
    return {pid:uint(m[1]),name:m[2],start_ticks:uint(f[19]),
            utime_ticks:uint(f[11]),stime_ticks:uint(f[12])};
}
function rosters() {
    let result={hostapd:[],wpa_supplicant:[]};
    let paths=fs.glob('/proc/[0-9]*/stat');
    if (paths==null) die('proc glob failed');
    for (let path in paths) {
        let text=fs.readfile(path,4097);
        if (text==null) continue; // Unrelated processes may exit during the scan.
        if (length(text)>4096) die('truncated proc stat');
        let p=process(text);
        if (p.name=='hostapd' || p.name=='wpa_supplicant')
            push(result[p.name],{pid:p.pid,start_ticks:p.start_ticks});
    }
    for (let name in ['hostapd','wpa_supplicant']) {
        if (!length(result[name])) die('missing service '+name);
        sort(result[name],(a,b)=>a.pid-b.pid);
    }
    return result;
}
function memory(text) {
    let result={};
    for (let line in split(text,'\n')) {
        let m=match(line,RX_MEMFIELD);
        if (m!=null && match(m[1],RX_MEMKEY)) {
            if (exists(result,m[1])) die('duplicate meminfo field');
            result[m[1]]=uint(m[2]);
        }
    }
    for (let name in ['MemTotal','MemFree','MemAvailable'])
        if (!exists(result,name)) die('missing meminfo '+name);
    return result;
}
function zone(text) {
    let result={}, normal=false, zones=0;
    for (let line in split(text,'\n')) {
        let h=match(line,RX_ZONEHEAD);
        if (h!=null) { normal=(h[1]=='Normal'); if (normal) zones++; continue; }
        if (!normal) continue;
        let m=match(line,RX_ZONEFREE);
        let key='free_pages';
        if (m==null) { m=match(line,RX_ZONEBOUNDS); if (m!=null) {key=m[1]+'_pages';m=[m[0],m[2]];} }
        if (m!=null) {if (exists(result,key)) die('duplicate Normal field');result[key]=uint(m[1]);}
    }
    if (zones!=1 || !exists(result,'free_pages') || !exists(result,'min_pages') || !exists(result,'boost_pages'))
        die('missing/ambiguous Normal zone');
    return result;
}
function oom() {
    // fs.last_error is VM-global; exclude earlier unrelated proc/flush errors.
    fs.error();
    let p=fs.popen('dmesg','r');
    if (p==null) die('dmesg unavailable');
    let text=p.read(LIMIT+1), error=p.error(), rc=p.close(), close_error=fs.error();
    if (text==null || error!=null || rc!==0 || close_error!=null || !length(text) || length(text)>LIMIT)
        die('dmesg error/empty/truncated '+sprintf('%J',{
            text_null:text==null,text_length:text==null?null:length(text),
            read_error:error,close_rc:rc,close_error:close_error,limit:LIMIT}));
    if (substr(text,-1)!='\n') die('partial dmesg output');
    let events=[], lines=split(text,'\n');
    for (let line in lines) {
        if (!match(line,RX_OOMMARK)) continue;
        let m=match(line,RX_OOMSTAMP);
        if (m==null) die('OOM record lacks exact timestamp');
        push(events,{timestamp:m[1],line:line});
        if (length(events)>256) die('too many OOM records');
    }
    return {records:events,bytes:length(text),first_line:lines[0]};
}
function send(record) {
    let line=sprintf('%J\n',record);
    if (out.write(line)!=length(line)) die('stdout write failed');
    // Installed ucode 3f64c808 fs.c has an inverted fflush() return check.
    // Delivery is verified by the caller's fresh sequence, terminal and SSH rc.
    out.flush();
}
function snapshot(seq) {
    let start=now(), boot=trim(read('/proc/sys/kernel/random/boot_id'));
    let uptime=split(trim(read('/proc/uptime')),RX_SPACES)[0];
    let policy={min_free_kbytes:uint(trim(read('/proc/sys/vm/min_free_kbytes'))),
                watermark_boost_factor:uint(trim(read('/proc/sys/vm/watermark_boost_factor')))};
    let mem=memory(read('/proc/meminfo')), normal=zone(read('/proc/zoneinfo'));
    let services=rosters(), log=oom();
    for (let name in ['hostapd','wpa_supplicant'])
        for (let old in services[name]) {
            let current=process(read('/proc/'+old.pid+'/stat'));
            if (current.name!=name || current.start_ticks!=old.start_ticks) die('service changed during sample');
        }
    let self=process(read('/proc/self/stat'));
    let rss=match(read('/proc/self/status'),RX_RSS);
    let end=now();
    if (trim(read('/proc/sys/kernel/random/boot_id'))!=boot) die('boot changed during sample');
    return {schema:'fmx.radio-survival.v1',status:'OBSERVATION_ONLY_NOT_LOAD_READY',kind:'sample',
            role:ROLE,tag:TAG,seq:seq,planned_seconds:SECONDS,boot_id:boot,
            uptime_start_s:+uptime,sample_duration_ms:(end-start)*1000,
            policy:policy,memory:mem,normal:normal,services:services,oom:log,
            observer:{pid:self.pid,start_ticks:self.start_ticks,rss_kb:rss==null?null:uint(rss[1]),
                      utime_ticks:self.utime_ticks,stime_ticks:self.stime_ticks}};
}
let start=now(), deadline=start+SECONDS, seq=0, initial=null, previous=null;
try {
    while (true) {
        // Include a final observation at the requested duration boundary.
        let at_deadline=(now()>=deadline);
        let sample=snapshot(seq);
        if (sample.sample_duration_ms>2000) die('stale local sample');
        let first_uptime=initial==null?sample.uptime_start_s:initial.uptime_start_s;
        for (let event in sample.oom.records)
            if (+event.timestamp>=first_uptime-0.01) die('OOM record overlaps observation start');
        send(sample);
        if (initial!=null) {
            if (sample.boot_id!=initial.boot_id || sprintf('%J',sample.policy)!=sprintf('%J',initial.policy)) die('boot/policy changed');
            if (sprintf('%J',sample.services)!=sprintf('%J',initial.services)) die('service PID/start changed');
            if (sample.oom.bytes<previous.oom.bytes || sample.oom.first_line!=initial.oom.first_line) die('dmesg history reduced/truncated');
            if (sprintf('%J',sample.oom.records)!=sprintf('%J',initial.oom.records)) die('OOM records changed');
        }
        else initial=sample;
        previous=sample;
        seq++;
        if (at_deadline) break;
        let wait=min(start+seq,deadline)-now();
        if (wait>0) sleep(wait*1000);
    }
    send({schema:'fmx.radio-survival.v1',status:'OBSERVATION_ONLY_NOT_LOAD_READY',kind:'end',
          role:ROLE,tag:TAG,seq:seq,planned_seconds:SECONDS,elapsed_seconds:now()-start});
}
catch (e) {
    send({schema:'fmx.radio-survival.v1',status:'OBSERVATION_ONLY_NOT_LOAD_READY',kind:'abort',
          role:ROLE,tag:TAG,seq:seq,planned_seconds:SECONDS,reason:''+e});
    exit(2);
}
'''
    return source.replace("__ROLE__", json.dumps(role)).replace("__TAG__", json.dumps(tag)).replace("__SECONDS__", str(seconds))


def plan(role, tag, seconds=20):
    source = ucode_source(role, tag, seconds)
    return dict(status=STATUS, role=role, tag=tag, seconds=seconds, interval_seconds=1,
                command=shlex.join(["/usr/bin/ucode", "-e", source]),
                ucode_sha256=hashlib.sha256(source.encode()).hexdigest(),
                caller_timeout_seconds=seconds+3, requires_owned_transport_watchdog=True,
                E2="NOT_ACCEPTED", execution_gate_cleared=False,
                limits="Idle observer cost must be measured; dmesg polling can miss overwritten events. No load authority.")


class ObservationError(ValueError):
    pass


def _uint(value, name, positive=False):
    if type(value) is not int or value < (1 if positive else 0):
        raise ObservationError("invalid " + name)
    return value


def _number(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ObservationError("invalid " + name)
    return value


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result: raise ObservationError("duplicate JSON key")
        result[key] = value
    return result


class ObserverStream:
    """One radio stream; keeps raw samples on error. Never grants load readiness."""
    def __init__(self, role, tag, seconds=20):
        options(role, tag, seconds)
        self.role, self.tag, self.seconds = role, tag, seconds
        self.samples, self.complete, self.failed = [], False, None
        self.failed_line = None
        self.received_at = self.age_at_receipt_ms = None

    def feed(self, line, *, transport_age_ms, received_monotonic):
        try:
            return self._feed(line, transport_age_ms, received_monotonic)
        except (ValueError, KeyError, TypeError, AttributeError, IndexError, OverflowError) as error:
            self.failed = str(error)
            self.failed_line = line
            raise ObservationError(self.failed) from error

    def _feed(self, line, transport_age_ms, received_monotonic):
        if self.failed or self.complete: raise ObservationError("stream already failed/completed")
        _number(transport_age_ms, "transport age")
        _number(received_monotonic, "receipt time")
        if not isinstance(line, str) or len(line)>65536 or not line.endswith("\n"):
            raise ObservationError("partial/oversize JSONL line")
        record = json.loads(line, object_pairs_hook=_unique, parse_constant=lambda _: (_ for _ in ()).throw(ObservationError("nonfinite JSON")))
        if not isinstance(record,dict): raise ObservationError("JSON record must be an object")
        if (record.get("schema") != SCHEMA or record.get("status") != STATUS or record.get("role") != self.role
                or record.get("tag") != self.tag or record.get("planned_seconds") != self.seconds
                or type(record.get("planned_seconds")) is not int
                or type(record.get("seq")) is not int or record["seq"] != len(self.samples)):
            raise ObservationError("stream contract/sequence mismatch")
        if record.get("kind") == "abort": raise ObservationError("remote abort: " + str(record.get("reason")))
        if record.get("kind") == "end":
            elapsed = _number(record.get("elapsed_seconds"), "terminal duration")
            if not self.samples or not self.seconds <= elapsed <= self.seconds+2 or transport_age_ms>MAX_AGE_MS:
                raise ObservationError("incomplete/stale terminal")
            self.latest(received_monotonic)
            self.complete = True
            return record
        if record.get("kind") != "sample": raise ObservationError("unknown record kind")
        duration = _number(record["sample_duration_ms"], "sample duration")
        if duration+transport_age_ms>MAX_AGE_MS: raise ObservationError("stale sample including transport")
        _number(record["uptime_start_s"], "uptime")
        if not re.fullmatch(r"[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}", record["boot_id"]):
            raise ObservationError("invalid boot identity")
        if set(record["policy"]) != {"min_free_kbytes", "watermark_boost_factor"}:
            raise ObservationError("missing/unknown policy field")
        for k,v in record["policy"].items(): _uint(v,k)
        for key in ("MemTotal", "MemFree", "MemAvailable"): _uint(record["memory"][key],key)
        for k,v in record["memory"].items(): _uint(v,k)
        if set(record["normal"]) != {"free_pages", "min_pages", "boost_pages"}: raise ObservationError("invalid Normal fields")
        for k,v in record["normal"].items(): _uint(v,k)
        if set(record["services"]) != {"hostapd", "wpa_supplicant"}: raise ObservationError("missing service roster")
        for name, roster in record["services"].items():
            if not isinstance(roster,list) or not roster: raise ObservationError("missing "+name)
            pids = []
            for item in roster:
                if set(item) != {"pid", "start_ticks"}: raise ObservationError("invalid service identity")
                pids.append(_uint(item["pid"],"pid",True)); _uint(item["start_ticks"],"start ticks",True)
            if pids != sorted(set(pids)): raise ObservationError("duplicate/unsorted service PID")
        observer = record["observer"]
        for key in ("pid","start_ticks"): _uint(observer[key],key,True)
        for key in ("utime_ticks","stime_ticks"): _uint(observer[key],key)
        if observer["rss_kb"] is not None: _uint(observer["rss_kb"],"observer RSS")
        log = record["oom"]
        if set(log) != {"records","bytes","first_line"} or not 0<_uint(log["bytes"],"dmesg bytes")<=MAX_DMESG_BYTES:
            raise ObservationError("invalid dmesg extent")
        if not isinstance(log["first_line"],str) or not log["first_line"] or not isinstance(log["records"],list) or len(log["records"])>256:
            raise ObservationError("invalid dmesg history")
        previous_timestamp = -1
        first_uptime = self.samples[0]["uptime_start_s"] if self.samples else record["uptime_start_s"]
        for event in log["records"]:
            if set(event) != {"timestamp","line"}: raise ObservationError("malformed OOM event")
            match = OOM_LINE.fullmatch(event["line"])
            if not match or match[1] != event["timestamp"] or not OOM_MARKER.search(match[2]): raise ObservationError("malformed OOM timestamp/event")
            timestamp = float(event["timestamp"])
            if not math.isfinite(timestamp) or timestamp<previous_timestamp: raise ObservationError("unordered/invalid OOM history")
            if timestamp >= first_uptime-0.01:
                raise ObservationError("OOM record overlaps observation start")
            previous_timestamp = timestamp
        if self.samples:
            initial, previous = self.samples[0], self.samples[-1]
            for key in ("boot_id","policy","services"):
                if record[key] != initial[key]: raise ObservationError(key+" changed")
            if record["observer"]["pid"] != initial["observer"]["pid"] or record["observer"]["start_ticks"] != initial["observer"]["start_ticks"]:
                raise ObservationError("observer identity changed")
            if record["uptime_start_s"] <= previous["uptime_start_s"] or received_monotonic<self.received_at:
                raise ObservationError("clock/uptime did not advance")
            if record["uptime_start_s"]-previous["uptime_start_s"]>2 or received_monotonic-self.received_at>2:
                raise ObservationError("sample gap exceeds two seconds")
            if log["bytes"]<previous["oom"]["bytes"] or log["first_line"]!=initial["oom"]["first_line"]:
                raise ObservationError("dmesg history reduced/truncated")
            if log["records"] != initial["oom"]["records"]: raise ObservationError("OOM records changed")
        self.samples.append(record)
        self.received_at, self.age_at_receipt_ms = received_monotonic, duration+transport_age_ms
        return record

    def latest(self, now_monotonic):
        if self.failed or not self.samples: raise ObservationError("no healthy observation")
        age = self.age_at_receipt_ms+(_number(now_monotonic,"now")-self.received_at)*1000
        if not 0<=age<=MAX_AGE_MS: raise ObservationError("latest observation expired")
        return self.samples[-1]

    def finish(self):
        if self.failed or not self.complete: raise ObservationError("failed/partial stream: "+str(self.failed))
        return dict(status=STATUS, complete=True, samples=len(self.samples), load_ready=False,
                    execution_gate_cleared=False)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role",required=True,choices=("ap","cpe"))
    parser.add_argument("--tag",required=True)
    parser.add_argument("--seconds",type=int,default=20)
    parser.add_argument("--format",choices=("plan","command"),default="plan")
    args=parser.parse_args(argv)
    result=plan(args.role,args.tag,args.seconds)
    print(result["command"] if args.format=="command" else json.dumps(result))
    return 0


if __name__=="__main__": raise SystemExit(main())
