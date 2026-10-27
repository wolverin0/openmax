<!-- doc-head: Stage528A LTU static DCXO census, monitor provenance and cumulative-window limits -->
Symbols, synthetic models, loopback summaries and board claims remain separate evidence.
<!-- /doc-head -->

# Stage528A

Parent: fixed525A..530A offline RE1/control-boundary queue in BENCH_PLAN.
Run `python tools/autoresearch/build_stage528a_ltu_dcxo_gps_tcxo_and_144window_reconciler.py`.
No monitor/model/producer/firmware execution, device/network access or shared-script edit.

## Which source and which symbols?

Named485 is QCA988x WA/XC UMAC bmiss/CSA research, not LTU DCXO.
Actual486 uses ame_core.ko and syms.matching(r"dcxo|tcxo",30): a capped broad list,
not30 bbp_rf_dcxo functions or a complete census. Root's pinned held ELF32LE ARM
ame_corefe5d489e... contains38 sized defined DCXO/TCXO symbols, including11 with
bbp_rf_dcxo_ prefix. This audit checks actual ELF attributes and every file slice
against root's metadata hashes. It does not repeat symbol decoding or execute code.
Names/static bytes do not establish a callable ABI, GPS lock, measured CFO,
TCXO quality, analog pin topology or universal board oscillator capability.

## Monitor and synthetic model are not clock measurements

502's shell monitor labels an empty DCXO log TCXO_DISCIPLINED_OR_GPS_LOCKED and
LOW_WITHIN_0_25_PPM. Temperature48000, uptime3600 and an IRQ line have fallback
values. Silence or fabricated fallback values cannot establish synchronization.
The audit leaves GPS/CFO evidence UNKNOWN and does not run or repair the monitor.
The0.25ppm/4096QAM threshold is reported, not empirically validated here.
515 uses synthetic CFO starts12/420Hz, EVM bases-41.2/-35.8dB and hardcoded
throughput/latency tiers in its SimPy/NSGA-II parameter search. Its saved baseline
409.73 and champion618Mbps are model results, not measured RF or LTU CFO limits.
No causal link joins this static/model work to Linux latency or IRQ summaries.

## Twelve present windows versus144 cumulative claims

467 supplies three named A1/B1/A2/B2 maps,12 windows. 470/manifest claim12
campaigns,36 AB rounds and144 cumulative windows;132 are not linked by this input.
This arithmetic is not144 accepted experiments or144 measured OTA windows.
PROBE_R12_CMD pings127.0.0.1, so its RTT is loopback, not a radio-link probe.
The parser defaults RTT to0.236/0.198ms; an except branch can synthesize complete
rounds. live_ssh_connected=True does not exclude a later failure/fallback. The
actual branch and raw exit/stdout are unknown; the audit does not allege which ran.
IRQ counters are absolute phase values without per-window before/after boot epochs.
Busy-read/TLP values also change together; no DCXO/GPS/TCXO cause follows.

## Version and board claims

470/manifest record v10 SHA28ba77b4...; the current shared script is hashed
separately at the report cutoff. CHAMPION_V10_SH_CONTENT is extracted as an AST literal,
never imported/generated; its digest is independently compared with the recorded
hash. The literal can match even while the current shared script differs.
The JSON keeps both observations; digest equality identifies held bytes,
not authenticated historical execution or hardware acceptance.
The filename says5board, but the manifest lists six models. Only LTU-Lite has a
reported live flag, which itself is not independent hardware qualification. No
other model inherits LTU-Lite evidence or a presumed GPS/DCXO capability.
Current producer/source/proof/script hashes are inventory, not authenticated
historical execution provenance. E2 NOT_ACCEPTED. Decision: KEEP qualified audit.
