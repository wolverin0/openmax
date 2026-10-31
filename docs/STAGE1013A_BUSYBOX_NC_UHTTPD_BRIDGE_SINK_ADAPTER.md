<!-- doc-head: Stage 1013A - offline BusyBox nc/dd/awk/wget/uhttpd command-plan builder and output parser so Triple-Play can be measured on 8 MB MIPS radios with no iperf3/Python; capability-probe-first, UDP falls back to the Stage 1007A host-to-host bridge probe; COMMAND_PLAN_AND_PARSER_SELFTEST evidence only. -->
<!-- /doc-head -->
# Stage 1013A - BusyBox nc/uhttpd bridge-sink adapter

## What it is

`workloads/busybox_nc_uhttpd_bridge_sink_adapter.py` is a pure-stdlib module that
BUILDS argv command plans (it never executes them) and PARSES their text output.
The live lane runs the plans on the 8 MB MIPS radios (.241/.242), which have no
iperf3, no Python and no `stat`. Only binaries already on the radio are used:
`nc`, `dd`, `awk`, `wget`, `uhttpd` (plus the `sh` and `cat` applets).

Evidence class: `COMMAND_PLAN_AND_PARSER_SELFTEST`. No radio is touched, and
`--self-test` runs fixtures only (it never invokes nc/dd/wget on the host).

## Capability dependence (read this first)

BusyBox applets are build-dependent. No busybox `.config` is pinned under
`firmware/`, so `CONFIG_NC_SERVER` and `CONFIG_NC_EXTRA` are UNKNOWN. The adapter
therefore never assumes a flag:

1. The FIRST step of every plan is `capability_probe`:
   `sh -c "command -v nc dd awk wget uhttpd cat; /usr/bin/nc 2>&1 | head"`.
2. The live lane feeds its output to `parse_capability_probe(text)`, which returns
   binary presence plus `nc_flags`, `nc_listen` (-l and -p), `nc_udp` (-u),
   `nc_exec` (-e).
3. That map is passed back as `capabilities=` to `build_commands`. A mode whose
   required flag is not confirmed is emitted with `status` `UNAVAILABLE`, `argv`
   `None` and `fallback` `bridge_host_to_host`. With `capabilities=None` every
   radio mode is UNAVAILABLE (probe not yet observed).

## Public API

- `build_commands(role, host, tcp_port, udp_port, duration, capabilities=None,
  bins=None, target_mbps=50.0, bs=1024, out="probe_1007a.json") -> dict`
  returns named steps `{status, argv|None, note}`. Host and ports are validated
  (no shell metacharacters), unknown roles raise `ValueError`.
- `parse_capability_probe(text) -> dict`
- `parse_dd_transfer(stderr_text, bs=None) -> dict`
- `self_test(path)` and CLI `python -m workloads.busybox_nc_uhttpd_bridge_sink_adapter --self-test`
  (writes the receipt); `--plan ROLE` prints a plan with no capabilities.

Default binary paths (override with `bins=`): `/usr/bin/nc`, `/bin/dd`,
`/usr/bin/awk`, `/usr/bin/wget`, `uhttpd`.

## Role matrix

- `radio_tcp_sink`: `nc -l -p PORT >/dev/null`. CONDITIONAL on
  `CONFIG_NC_SERVER`; needs `nc_listen` confirmed. Else UNAVAILABLE.
- `radio_tcp_source`: `dd if=/dev/zero bs=B count=N 2>/tmp/fmx_dd.err | nc HOST PORT`
  then `cat` of the dd stderr. Client mode only; the host sink times the transfer.
- `radio_udp_reflector`: `nc -u -l -p PORT -e cat`. ONLY when `-u` AND `-e` (and
  `-l -p`) are confirmed. Many BusyBox nc builds lack `-u`; do not expect it.
- `radio_http_client`: `wget -q -O /dev/null http://HOST:PORT/zero.bin`. The radio
  is the CLIENT and the host serves the file. The sibling step
  `http_uhttpd_server` is always UNAVAILABLE: serving `/dev/zero` from `uhttpd`
  is not viable on 8 MB flash and is deliberately not invented.
- `bridge_host_to_host`: host-side only, references the existing Stage 1007A
  tool, does not reimplement it:
  `python -m workloads.host_driven_triple_play_socket_probe --role sink|probe
  --host H --tcp-port P --udp-port P --out F` (probe adds `--duration`).

## Fallback to the 1007A bridge

UDP IPTV and VoIP G.711 measurement needs an echo peer. When the radio cannot
reflect UDP (no `-u`/`-e` confirmed), run the sink on one L2 host and the probe
on another host across the bridge under test, using
`workloads/host_driven_triple_play_socket_probe.py`. The same fallback applies
to any TCP sink or source mode that the probe did not confirm. The radio's role
is then the bridge itself rather than an endpoint.

## dd parsing

`parse_dd_transfer` handles both BusyBox forms:

- Third status line present (`CONFIG_FEATURE_DD_THIRD_STATUS_LINE`):
  `1048576 bytes (1.0MB) copied, 0.25 seconds, 4.0MB/s` gives bytes, seconds,
  `rate_text` and `rate_bytes_per_s` (bytes/seconds, authoritative).
- Absent (only `N+0 records in/out`): bytes = full records out x `bs`, rate and
  seconds are `None`, so the host must time the transfer. `bs` is required.
- Neither parseable: `ValueError` (fail closed).

## Verification

- Tests: `workloads/test_busybox_nc_uhttpd_bridge_sink_adapter.py` (offline).
  They check argv basenames are only nc/dd/awk/wget/uhttpd/sh/cat (never
  iperf3/python/stat on radio roles), unconfirmed modes are UNAVAILABLE, the
  bridge role references 1007A, and the parsers on fixtures.
- Receipt: `artifacts/autoresearch/stage1013a_busybox_nc_uhttpd_bridge_sink_adapter.json`
  (status CONFIRMED, `live_devices_touched` false). The writer reads back and
  rejects all-NUL content, retrying up to 3 times then raising.

## Limits

- Fixtures are representative, not captured from the real radios. The live lane
  must confirm real probe output before trusting any mode.
- The probe adds `cat` to the requested binary list because the reflector and
  source plans use it.
- `nc -l` flag parsing is taken from the usage text; a usage text that omits a
  flag the binary actually accepts yields a false UNAVAILABLE (safe direction).
- The `/tmp/fmx_dd.err` path assumes a writable RAM `/tmp` on the radio.
