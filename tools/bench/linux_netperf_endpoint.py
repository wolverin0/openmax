"""Pinned netserver supervisor for RRUL. Default plan has no endpoint I/O.

The private, hash-verified iperf supervisor supplies lifetime/stdin handling;
netserver process ownership, status namespace and fork validation are separate.
READY never qualifies source admission, routing, data-port use or RRUL results.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import signal
import subprocess
import sys
import threading
import time
import types

BASE_HASH = "55aeb6f845261752a1e938ecbc5f697cd57284ba5f03d5aea97dbc10112a8643"
BINARY = "/home/ggorbalan/.local/share/futuramax/e2-endpoint-20261015-QwnPFT/netperf-build-20261009-cSy3ed/runtime/bin/netserver"
BINARY_HASH = "ed5ea5a5367825bbbf5812ef4aa82d20304c1f14242e6d147b8cab7ca495d1fc"
ADDRESS = "192.168.1.170"
PORT = 5205
DATA_PORTS = {"TCP": tuple(range(5210, 5218)), "UDP": tuple(range(5218, 5221))}


def plan():
    return dict(Status="PLAN_ONLY_NO_IO", Port=PORT, DataPorts=DATA_PORTS,
                Executable=BINARY, SHA256=BINARY_HASH, Address=ADDRESS,
                MaxWorkers=11, TTLRange=[60, 900], E2="NOT_ACCEPTED",
                TrafficPathQualified=False)


def load_base():
    path = Path(__file__).with_name("linux_iperf_endpoint.py")
    source = path.read_bytes()
    if hashlib.sha256(source).hexdigest() != BASE_HASH:
        raise RuntimeError("private base source hash mismatch")
    module = types.ModuleType("_fmx_netperf_pinned_base")
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def translated(record):
    result = dict(record)
    result["Status"] = result["Status"].replace("LINUX_IPERF_", "LINUX_NETPERF_")
    result.update(Port=PORT, DataPorts=DATA_PORTS, TrafficPathQualified=False)
    result["Prerequisite"] = "Separate control/data source admission and bidirectional routing qualification required"
    return result


def make_host(base):
    # Clone only the trusted function's globals; never mutate the base module.
    inspect = types.FunctionType(base.inspect_identity.__code__,
                                 dict(base.inspect_identity.__globals__,
                                      BINARY=BINARY, BINARY_HASH=BINARY_HASH))
    control_listeners = types.FunctionType(base.LinuxHost.listeners.__code__,
                                           dict(base.LinuxHost.listeners.__globals__, PORT=PORT))

    class NetperfHost(base.LinuxHost):
        def __init__(self):
            self.parent = None
            self.wrapper = None
            self.seen = {}
            self.workers = []

        def inspect(self):
            return inspect()

        @staticmethod
        def stat(pid):
            fields = Path(f"/proc/{pid}/stat").read_text().rsplit(") ", 1)[1].split()
            return dict(Pid=pid, Parent=int(fields[1]), Group=int(fields[2]),
                        StartTicks=int(fields[19]))

        @classmethod
        def proc(cls, pid):
            return dict(cls.stat(pid), Executable=os.readlink(f"/proc/{pid}/exe"))

        @staticmethod
        def listeners():
            return control_listeners()

        def inventory(self, group):
            members = []
            for path in Path("/proc").iterdir():
                if not path.name.isdigit():
                    continue
                try:
                    item = self.stat(int(path.name))
                except (FileNotFoundError, ProcessLookupError):
                    continue
                if item["Group"] == group:
                    # Inaccessible executable of a member is a failure, not ignored.
                    try:
                        executable = os.readlink(str(path / "exe"))
                    except (FileNotFoundError, ProcessLookupError):
                        try:
                            self.stat(item["Pid"])
                        except (FileNotFoundError, ProcessLookupError):
                            continue  # Worker really exited between the two reads.
                        raise RuntimeError("live group member executable unavailable")
                    members.append(dict(item, Executable=executable))
            return members

        def bind(self, wrapper, parent, workers=()):
            self.wrapper, self.parent = dict(wrapper), dict(parent)
            self.seen = {x["Pid"]: dict(x) for x in workers}

        def validate_group(self, group, *, cleanup=False):
            members = self.inventory(group)
            if self.wrapper is None:
                raise RuntimeError("netserver group not bound")
            if self.parent is None:
                if cleanup and all(item == self.wrapper for item in members):
                    return members
                candidates = [item for item in members
                              if item["Parent"] == group and item["Executable"] == BINARY]
                if not cleanup or len(candidates) != 1:
                    raise RuntimeError("netserver parent not bound")
                self.parent = dict(candidates[0])
            workers = []
            parents = []
            for item in members:
                if item["Pid"] == self.wrapper["Pid"]:
                    if item != self.wrapper:
                        raise RuntimeError("timeout identity changed")
                elif item["Pid"] == self.parent["Pid"]:
                    if item != self.parent:
                        raise RuntimeError("netserver parent identity changed")
                    parents.append(item)
                else:
                    old = self.seen.get(item["Pid"])
                    if (item["Executable"] != BINARY or item["StartTicks"] < self.parent["StartTicks"]
                            or (old is not None and any(item[k] != old[k] for k in ("StartTicks", "Group", "Executable")))
                            or (item["Parent"] != self.parent["Pid"]
                                and not (cleanup and old is not None and item["Parent"] == 1))):
                        raise RuntimeError("foreign/reused netserver worker")
                    self.seen[item["Pid"]] = dict(item)
                    workers.append(item)
            if len(workers) > 11 or (not cleanup and len(parents) != 1):
                raise RuntimeError("netserver parent missing or worker limit exceeded")
            self.workers = workers
            return members

        def start(self, ttl):
            return subprocess.Popen([base.TIMEOUT, "--signal=TERM", "--kill-after=2s", str(ttl)+"s",
                                     BINARY, "-D", "-4", "-L", ADDRESS, "-p", str(PORT)],
                                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, start_new_session=True)

        def server(self, group):
            wrapper = self.proc(group)
            if wrapper["Group"] != group or wrapper["Executable"] != base.TIMEOUT:
                raise RuntimeError("wrong timeout wrapper")
            parents = [x for x in self.inventory(group)
                       if x["Parent"] == group and x["Executable"] == BINARY]
            if len(parents) != 1:
                raise RuntimeError("netserver parent not uniquely owned")
            self.bind(wrapper, parents[0])
            self.validate_group(group)
            return parents[0]

        def listening(self, parent):
            self.validate_group(parent["Group"])
            inodes = set()
            for fd in Path(f"/proc/{parent['Pid']}/fd").iterdir():
                try:
                    link = os.readlink(fd)
                    if link.startswith("socket:["):
                        inodes.add(link[8:-1])
                except FileNotFoundError:
                    continue
            expected = base.socket.inet_aton(ADDRESS)[::-1].hex().upper()
            listeners = self.listeners()
            return bool(listeners) and all(family == "tcp" and address == expected and inode in inodes
                                           for family, address, inode in listeners)

        def cleanup(self, process, wrapper, parent):
            if not self.inventory(process.pid):
                process.wait(timeout=1)
                return True
            if self.wrapper is None:
                if (wrapper is None or wrapper["Pid"] != process.pid
                        or wrapper["Group"] != process.pid or wrapper["Executable"] != base.TIMEOUT
                        or self.proc(process.pid) != wrapper):
                    raise RuntimeError("startup timeout ownership unverified")
                if parent is None:
                    try:
                        self.server(process.pid)
                    except RuntimeError:
                        self.wrapper = dict(wrapper)
                        self.validate_group(process.pid, cleanup=True)
                else:
                    self.bind(wrapper, parent)
            # A foreign group member prevents a broad signal. Preserve it and fail.
            for sig, seconds in ((signal.SIGTERM, 3), (signal.SIGKILL, 2)):
                members = self.validate_group(process.pid, cleanup=True)
                if not members:
                    process.wait(timeout=1)
                    return True
                os.killpg(process.pid, sig)
                deadline = time.monotonic()+seconds
                try:
                    # Reap our own timeout before inspecting /proc: an exited,
                    # unreaped wrapper can refuse /proc/PID/exe access.
                    process.wait(timeout=seconds)
                except subprocess.TimeoutExpired:
                    pass
                while self.inventory(process.pid) and time.monotonic() < deadline:
                    time.sleep(0.05)
            process.wait(timeout=1)
            return not self.inventory(process.pid)

    return NetperfHost()


def run_paths(base, directory, tag, *, create=False):
    directory, _, _, _ = base.run_paths(directory, tag, create=create)
    prefix = directory / ("linux-netperf-"+tag)
    return directory, Path(str(prefix)+".status.json"), Path(str(prefix)+".stop"), Path(str(prefix)+".lock")


def read_status(base, host, directory, tag, *, clock=time.monotonic):
    _, path, stop, _ = run_paths(base, directory, tag)
    info = path.lstat()
    if path.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077 or info.st_size > 65536:
        raise RuntimeError("invalid netperf status file")
    record = json.loads(path.read_text())
    if (record.get("Status") != "LINUX_NETPERF_READY" or record.get("Ready") is not True
            or record.get("Tag") != tag or record.get("Platform") != "linux"
            or record.get("Port") != PORT or record.get("DataPorts") != json.loads(json.dumps(DATA_PORTS))):
        raise RuntimeError("netperf status contract mismatch")
    if stop.exists() or stop.is_symlink():
        raise RuntimeError("netperf stop requested")
    def fresh():
        age = clock()-record["UpdatedMonotonic"]
        if not 0 <= age <= 2 or clock() >= record["ExpiresMonotonic"]:
            raise RuntimeError("stale netperf status")
        return age
    fresh()
    if host.inspect() != record["Identity"]:
        raise RuntimeError("netperf host identity changed")
    for key in ("Supervisor", "Wrapper", "Server"):
        if host.proc(record[key]["Pid"]) != record[key]:
            raise RuntimeError("netperf process identity changed")
    host.bind(record["Wrapper"], record["Server"], record.get("Workers", []))
    if not host.listening(record["Server"]):
        raise RuntimeError("netperf listener changed")
    return dict(record, Workers=host.workers, StatusAgeSeconds=fresh(), TrafficPathQualified=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=("plan", "inspect", "status", "serve"), default="plan")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--tag")
    parser.add_argument("--ttl", type=int)
    parser.add_argument("--run-dir")
    args = parser.parse_args(argv)
    if args.command == "plan":
        print(json.dumps(plan())); return 0
    if sys.platform != "linux":
        parser.error("Linux required")
    if args.command in ("serve", "status") and (not re.fullmatch(r"[a-f0-9]{32}", args.tag or "") or not args.run_dir):
        parser.error("tag32hex and private run-dir required")
    if args.command == "serve" and (not args.execute or type(args.ttl) is not int or not 60 <= args.ttl <= 900):
        parser.error("serve requires --execute and TTL60..900")
    base = load_base(); host = make_host(base)
    if args.command == "inspect":
        base.emit(dict(Status="LINUX_NETPERF_INSPECTED", Identity=host.inspect(), Ready=False, TrafficPathQualified=False)); return 0
    if args.command == "status":
        base.emit(read_status(base, host, args.run_dir, args.tag)); return 0
    _, path, stop, lock = run_paths(base, args.run_dir, args.tag, create=True)
    if any(x.exists() or x.is_symlink() for x in (path, stop, lock)):
        raise RuntimeError("fresh netperf tag required")
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600); os.close(descriptor)
    controls = queue.Queue()
    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, lambda *_: controls.put("STOP "+args.tag))
    threading.Thread(target=base.read_controls, args=(sys.stdin, controls), daemon=True).start()
    supervisor = host.proc(os.getpid())
    def publish(record):
        base.atomic_status(path, dict(translated(record), Supervisor=supervisor,
                                     Workers=host.workers, UpdatedMonotonic=time.monotonic()))
    try:
        return base.supervise(host, args.tag, args.ttl, controls,
                              output=lambda r: base.emit(translated(r)), heartbeat=publish,
                              stop_requested=lambda: stop.exists() or stop.is_symlink())
    finally:
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps(dict(Status="LINUX_NETPERF_FAILED", Ready=False, Reason=str(error))))
        raise SystemExit(1)
