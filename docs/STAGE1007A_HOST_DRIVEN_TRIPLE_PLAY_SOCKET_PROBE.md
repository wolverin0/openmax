<!-- doc-head: Stage 1007A - pure-Python host-driven Triple-Play (TCP bulk + UDP IPTV + UDP VoIP G.711) sink/probe tool for iperf3-less 8 MB radios; fail-closed, loopback self-test evidence only (LOOPBACK_SELFTEST_ONLY), no live devices touched. -->
<!-- /doc-head -->
# Stage 1007A - Host-driven Triple-Play socket probe

## Why

The 8 MB OpenWrt radios (Stages 929A/953A) have no `iperf3` and no `stat` in
BusyBox. Nothing can be generated or measured on the radio, so all traffic is
injected and measured from external hosts. This stage adds a stdlib-only tool
that does exactly that.

## Files

- `workloads/host_driven_triple_play_socket_probe.py` - sink + probe + receipt writer
- `workloads/test_host_driven_triple_play_socket_probe.py` - offline pytest suite
- `artifacts/autoresearch/stage1007a_host_driven_triple_play_socket_probe.json` - receipt
- `docs/STAGE1007A_HOST_DRIVEN_TRIPLE_PLAY_SOCKET_PROBE.md` - this file

`workloads/flent_orchestrator.py` is owned by another lane and is untouched.

## Roles

- `--role sink`: runs on the host behind the far radio. TCP sink acks the total
  byte count it received; UDP echo responder returns every datagram unchanged.
- `--role probe`: the measurer, runs behind the near side.
- `--role selftest` (default): sink and probe on `127.0.0.1`, then writes the receipt.

UDP loss and jitter cannot be observed without a reply path, hence the echo.

## Flows (run concurrently)

| Flow | Spec | Measured |
| --- | --- | --- |
| TCP bulk | 32 KiB chunks, real connect + stream | bytes sent, bytes acked by sink, goodput Mbps |
| UDP IPTV | 1316 B (7 x 188 TS), constant 2 Mbps | echoed count, loss %, RTT, RFC 3550 jitter |
| UDP VoIP G.711 | 172 B every 20 ms (50 pps) | loss %, RTT, jitter, send-interval median and stdev |

VoIP pacing uses an absolute schedule from `t0 + i * 20 ms`, so scheduler
overshoot does not accumulate.

## Fail-closed contract

- Every socket operation has a hard timeout (connect 2 s, IO 2 s, UDP recv 0.1 s,
  drain 0.4 s). Nothing can hang.
- No listener, no ack, or zero UDP echoes: `ProbeError`, CLI exit code 2.
- On failure no JSON is written (the `--out` file stays absent).
- No default values: a missing measurement is an error, never a zero.
- The receipt is written only after a successful self-test, then read back and
  checked (`raw.strip(b"\x00")` truthy, JSON parses, `stage == "Stage 1007A"`),
  retried up to 3 times, else it raises.

## Evidence class

`LOOPBACK_SELFTEST_ONLY`. The loopback numbers (multi-Gbps TCP, sub-ms RTT) say
nothing about a radio path; they only prove the tool measures real socket
round trips. This stage does not claim any `CONFIRMED_LIVE_*` result and touched
no device (`live_devices_touched=false`).

## Usage

```
python -m workloads.host_driven_triple_play_socket_probe --role selftest
python -m workloads.host_driven_triple_play_socket_probe --role sink --host 0.0.0.0 --tcp-port 5201 --udp-port 5201
python -m workloads.host_driven_triple_play_socket_probe --role probe --host SINK_IP --duration 10 --out result.json
```

Tests: `python -m pytest workloads/test_host_driven_triple_play_socket_probe.py -q`
(sink round trip with real counters, no-listener exits within 5 s with no file,
VoIP median interval within 20 ms +/- 8 ms, receipt integrity).

## Known limits

- Jitter is computed from echo arrival vs send time on one host clock (RTT-based),
  so it blends both directions; true one-way delay needs synchronized clocks.
- Single Python process: the TCP stream and two UDP flows share the GIL, so
  results above roughly 1 Gbps measure the host, not the link.
- Windows timer granularity makes exact 20 ms timing untestable; tests use a
  generous tolerance on the median.

## Next step

Live host-behind-radio runs need a separate, operator-gated stage with its own
receipt; this offline stage only qualifies the tool.
