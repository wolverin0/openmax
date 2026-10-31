<!-- doc-head: Stage1063A offline iw station bitrate, VHT-MCS/NSS, chain signal and retry-counter parsing -->
Saved native station text is replayed without collecting new hardware observations.
<!-- /doc-head -->

# Stage1063A: scoped PtP station parser

`tools/autoresearch/ptp_station_dump_mcs_retry_parser.py` parses one or multiple `iw dev INTERFACE station dump` blocks. Each block retains the peer MAC and its own interface, including `phy2-ap0.sta1` and `phy2-sta0`.

| Field | Representation |
|---|---|
| TX/RX bitrate | Separate direction dictionaries with Mbps, VHT-MCS, NSS, short-GI flag and raw line |
| Signal | Aggregate dBm and optional per-chain dBm list |
| Retry/failure/drop | `tx_retries`, `tx_failed`, `rx_drop_misc` uint64 counters |
| Optional byte counters | `tx_bytes`, `rx_bytes`, retained separately |

MBit/s and KBit/s are normalized to Mbps; nonfinite rates and malformed complete VHT tokens are rejected. A direction without VHT-MCS/NSS keeps those fields `None`; TX metadata is never copied to RX. MCS 0..9 and NSS 1..8 are VHT syntax bounds, not an assertion that this radio supports every combination.

Unreported fields remain `None`, not zero. Duplicate station identities and duplicate recognized fields are rejected. Other iw metadata is ignored; malformed known fields fail closed. An empty dump produces an empty list, not a fabricated peer.

```python
from tools.autoresearch.ptp_station_dump_mcs_retry_parser import parse_station_dump
rows = parse_station_dump(saved_text, interface='phy2-ap0.sta1')
```

`counter_delta(before, after, boot_id_before, boot_id_after)` requires an identical MAC/interface, identical nonempty string boot epoch, uint64 inputs and monotonic counters. Missing counters produce unknown deltas. This does not prove association continuity within an epoch; callers must establish a consistent acquisition window independently.

The receipt binds saved Stage995A native station text, source SHA256 and parsed results. Those records are historical observations, not newly collected measurements, new performance promotions, or proof that present radios still match them.

The parser does not infer packet-loss percentage from retry counters, convert MCS into measured application capacity, attribute drops to RF alone, or certify 0 false positives. Receipt: `artifacts/autoresearch/stage1063a_ptp_station_dump_mcs_retry_parser.json`.
