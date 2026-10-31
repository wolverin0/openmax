<!-- doc-head: Stage1062A offline bounded uclient-fetch TCP load plans, ICMP size proxies and aggregate counter checks -->
No commands are executed; ICMP probes do not measure UDP VoIP or IPTV application QoE.
<!-- /doc-head -->

# Stage1062A: tiny-radio load adapter

`tools/autoresearch/uclient_fetch_dual_radio_load_adapter.py` produces a bounded BusyBox shell plan and parses saved or synthetic output. It never opens sockets, invokes SSH, starts load, or writes on a radio.

The peer must already serve the exact, separately qualified 4 MiB `/www/bench4m.bin` through HTTP. Its size and content SHA256 must be verified before a later acquisition. No HTTP server or file is silently installed or started by this adapter.

The generated plan concurrently runs two `ping -i 1` streams with 64-byte and 1316-byte **ICMP payloads**, alongside one `/bin/uclient-fetch` TCP download. These are packet-size latency proxies; they are not UDP pacing, VoIP/IPTV jitter, or an accepted Triple-Play workload.

Unlike a quiet download to `/dev/null`, the plan pipes fetched bytes to `wc -c` under `set -o pipefail`. It captures the actual receiver-stream byte count, fetch exit and uptime markers. Missing byte count, unsuccessful fetch, wrong file length, or invalid elapsed time leaves goodput unknown. A successful fetch exit by itself never supplies 4 MiB of measured data.

The fetch timeout and ping count are independently bounded, each from 1 to 120. The timeout is not a fixed throughput measurement window. Temporary probe logs use a private directory; cleanup signals only a child PID whose PPID and process start ticks still match.

| API | Contract |
|---|---|
| `build_plan(source, peer, interface, duration=20, ping_count=20)` | Literal IPv4 endpoints; explicit native interface, including `.sta1`; injection rejected |
| `parse_load_output(text, exit_code)` | TCP fetch result only; finite positive elapsed and native integer shell exit |
| `parse_ping(text, expected_payload_bytes=None)` | Complete ICMP summary and exact latency-array coverage |
| `crosscheck_counters(before, after, application_bytes=None)` | uint64 RX/TX deltas; decreasing counter rejected |

Counter snapshots are interface aggregate RX/TX bytes and include headers and unrelated traffic. `rx_covers_payload` is only a consistency check; it cannot establish exact application bytes, exclusive load, physical RF traversal, or absence of a reset that occurred between snapshots. Independently qualify the same interface and boot epoch.

The ICMP parser accepts the observed BusyBox `PING IP (IP): N data bytes` header and the no-colon variant. Every latency must be finite, even when an expected payload size was not supplied. The receipt replays one exact historical Stage1019A 56-byte-payload block; its 64/1316-byte size examples are explicitly synthetic parser fixtures, not new measurements.

Required applets, `uclient-fetch` location and pipefail support are explicit plan prerequisites. Saved radio discovery established other BusyBox tools, but does not automatically qualify `wc`, the HTTP file, or this complete plan. No fallback to iperf3, stat, tc, another host, or a synthetic receiver occurs.

There are no A/A, discovery, or holdout observations in this stage. The receipt uses clearly labeled synthetic parser fixtures and preserves physical acceptance as unknown. Receipt: `artifacts/autoresearch/stage1062a_uclient_fetch_dual_radio_load_adapter.json`.
