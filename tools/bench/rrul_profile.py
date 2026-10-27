"""Canonical Flent 2.3.0 RRUL with fixed remote data ports; no acquisition.

The default CLI prints a pure plan. load_canonical() reads the held installed
profile explicitly, without host lookup. This module never starts runners,
loads BatchRunner, grants admission, or changes endpoint/network guards.
"""
import argparse
import copy
from dataclasses import asdict, dataclass
import hashlib
import ipaddress
import json
from pathlib import Path

VERSION = "2.3.0"
CONTROL_PORT = 5205
PROFILE_SHA256 = {
    "rrul.conf": "e9dd384e8ebc2ff0b4d46c7a429704ea4c1f8f418b2222d93c17606b71ae4ced",
    "netperf_definitions.inc": "d424a9c9f63f06dbecff7344bff8022ce92f319a352e91f623543e013fe0762e",
}


@dataclass(frozen=True)
class Flow:
    dataset: str
    protocol: str
    test: str
    remote_port: int | None


FLOWS = tuple(
    Flow("TCP " + direction + " " + marking, "TCP", test, 5210 + i * 4 + j)
    for i, (direction, test) in enumerate((("upload", "TCP_STREAM"),
                                          ("download", "TCP_MAERTS")))
    for j, marking in enumerate(("BE", "BK", "CS5", "EF"))
) + tuple(Flow("Ping (ms) UDP " + marking, "UDP", "UDP_RR", 5218 + i)
          for i, marking in enumerate(("EF", "BK", "BE"))) + (
    Flow("Ping (ms) ICMP", "ICMP", "ICMP", None),)


def plan(host="192.168.1.170"):
    """Pure JSON-compatible plan; no filesystem, Flent import, or network I/O."""
    host = str(ipaddress.IPv4Address(host))
    return dict(status="PLAN_ONLY_NOT_ADMITTED", flent_version=VERSION,
                host=host, control_port=CONTROL_PORT, length=60, delay=1,
                step_size=0.2, total_length=62,
                flows=[asdict(flow) for flow in FLOWS],
                execution=False, E2="NOT_ACCEPTED",
                prerequisites=["independent source review and full runtime admission",
                               "qualified netperf binary in controller PATH; irtt absent",
                               "bidirectional control/data routing and endpoint supervision",
                               "60s TCP plus62s latency monitoring and owned cleanup"])


def _stable(value):
    if isinstance(value, dict):
        return tuple((k, _stable(v)) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return tuple(_stable(v) for v in value)
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    # Canonical Flent Glob instances have stable repr but identity equality.
    return (type(value).__module__, type(value).__name__, repr(value))


def _canonical(settings, version):
    if version != VERSION:
        raise ValueError("Flent version must be exactly 2.3.0")
    for key, expected in dict(NAME="rrul", LENGTH=60, DELAY=1, STEP_SIZE=0.2,
                              TOTAL_LENGTH=62, NETPERF_CONTROL_PORT=5205,
                              IP_VERSION=4, SWAP_UPDOWN=False).items():
        if getattr(settings, key, None) != expected:
            raise ValueError("noncanonical setting: " + key)
    if settings.TEST_PARAMETERS or settings.REMOTE_HOSTS:
        raise ValueError("test parameter or remote runner override")
    data = settings.DATA_SETS
    if len(data) != 18:
        raise ValueError("canonical RRUL requires12 physical and6 derived datasets")
    physical = [n for n, d in data.items()
                if d.get("runner") in ("netperf_demo", "udp_rtt", "ping")]
    if physical != [flow.dataset for flow in FLOWS]:
        raise ValueError("missing/altered canonical physical datasets")
    ports = [flow.remote_port for flow in FLOWS if flow.remote_port is not None]
    if len(set(ports + [CONTROL_PORT])) != 12:
        raise ValueError("control/data port collision")
    host = str(ipaddress.IPv4Address(settings.HOST))
    if settings.HOSTS != [host]:
        raise ValueError("one numeric IPv4 host required")
    for flow in FLOWS:
        d = data[flow.dataset]
        if "extra_args" in d or "extra_test_args" in d:
            raise ValueError("dataset extra-argument override")
        if d.get("host") != host:
            raise ValueError("dataset host override")
        if flow.protocol == "TCP":
            expected = {"test": flow.test, "runner": "netperf_demo",
                        "length": 60, "delay": 1,
                        "marking": {"BE": "CS0,CS0", "BK": "CS1,CS1",
                                    "CS5": "CS5,CS5", "EF": "EF,EF"}[flow.dataset.split()[-1]]}
        elif flow.protocol == "UDP":
            expected = {"runner": "udp_rtt", "length": 62}
            marking = {"EF": "EF,EF", "BK": "CS1,CS1", "BE": None}[flow.dataset.split()[-1]]
            if d.get("marking") != marking:
                raise ValueError("UDP DSCP changed")
        else:
            expected = {"runner": "ping", "length": 62, "interval": 0.2,
                        "ip_version": 4}
        if any(d.get(k) != v for k, v in expected.items()):
            raise ValueError("canonical runner/direction/marking/timing changed")


def validate_profile(canonical, adapted, *, version):
    """Reject any change beyond the eleven per-dataset test arguments."""
    _canonical(canonical, version)
    restored = copy.deepcopy(adapted)
    for flow in FLOWS:
        if flow.remote_port is not None:
            d = restored.DATA_SETS[flow.dataset]
            if d.pop("extra_test_args", None) != "-P 0," + str(flow.remote_port):
                raise ValueError("fixed remote data-port mapping changed")
    if _stable(vars(restored)) != _stable(vars(canonical)):
        raise ValueError("profile metadata or canonical dataset changed")
    return plan(canonical.HOST)


def build_profile(canonical, *, version):
    """Copy an already loaded canonical settings object, adding only data ports."""
    _canonical(canonical, version)
    adapted = copy.deepcopy(canonical)
    for flow in FLOWS:
        if flow.remote_port is not None:
            adapted.DATA_SETS[flow.dataset]["extra_test_args"] = "-P 0," + str(flow.remote_port)
    validate_profile(canonical, adapted, version=version)
    return adapted


def load_canonical(host="192.168.1.170"):
    """Explicit local profile read, no DNS lookup or runner checks/execution."""
    import importlib.metadata
    import flent
    from flent import settings
    if importlib.metadata.version("flent") != VERSION:
        raise ValueError("wrong installed Flent version")
    for name, pin in PROFILE_SHA256.items():
        path = Path(flent.__file__).parent / "tests" / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != pin:
            raise ValueError("held canonical profile hash mismatch: " + name)
    s = settings.new()
    s.HOST = str(ipaddress.IPv4Address(host))
    s.HOSTS = [s.HOST]
    s.LENGTH, s.DELAY, s.STEP_SIZE = 60, 1, 0.2
    s.NETPERF_CONTROL_PORT, s.IP_VERSION = CONTROL_PORT, 4
    s.load_test("rrul", informational=True)
    _canonical(s, VERSION)
    return s


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.1.170")
    args = parser.parse_args()
    print(json.dumps(plan(args.host), indent=2))
