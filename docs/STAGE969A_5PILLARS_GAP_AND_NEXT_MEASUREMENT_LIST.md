<!-- doc-head: Stage 969A gaps and suggested next hardware measurements for blueprint items lacking live-bench evidence; suggestions only -->
# Stage 969A — 5-pillar gaps & next-measurement list

Offline. 31 gaps (26 variable-level) for items not CONFIRMED_LIVE_BENCH.
Suggested measurements are keyword-derived SUGGESTIONS; none executed or approved.

| Scope | Item | Status | Gap | Suggested measurement |
| :-- | :-- | :-- | :-- | :-- |
| variable | Stage 347A | CONFIRMED_STATIC_BINARY | static binary proof only; runtime behaviour on hardware not measured | RAM-only patched firmware load on a bench QCA988x radio; verify WMI_READY boot and power-cycle restore |
| variable | Stage 353A | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | RAM-only patched firmware load on a bench QCA988x radio; verify WMI_READY boot and power-cycle restore |
| variable | PB-031 | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | RAM-only patched firmware load on a bench QCA988x radio; verify WMI_READY boot and power-cycle restore |
| variable | PB-030 | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | RAM-only patched firmware load on a bench QCA988x radio; verify WMI_READY boot and power-cycle restore |
| variable | Stage 348A | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | Capture rx_ppdu_end trailer on a bench radio and compare EVM/timestamp against a known distance |
| variable | Stage 317A | CONFIRMED_STATIC_BINARY | static binary proof only; runtime behaviour on hardware not measured | Counterbalanced A1-B1-A2-B2 live bench window on the relevant bench radio, 45s/120s watchdog |
| variable | Stage 318A | CONFIRMED_STATIC_BINARY | static binary proof only; runtime behaviour on hardware not measured | Counterbalanced A1-B1-A2-B2 live bench window on the relevant bench radio, 45s/120s watchdog |
| variable | Stage 319A | CONFIRMED_STATIC_BINARY | static binary proof only; runtime behaviour on hardware not measured | Counterbalanced A1-B1-A2-B2 live bench window on the relevant bench radio, 45s/120s watchdog |
| variable | Stage 320A | CONFIRMED_STATIC_BINARY | static binary proof only; runtime behaviour on hardware not measured | Counterbalanced A1-B1-A2-B2 live bench window on the relevant bench radio, 45s/120s watchdog |
| variable | Stage 321A | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | Counterbalanced A1-B1-A2-B2 live bench window on the relevant bench radio, 45s/120s watchdog |
| variable | Stage 322A | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | Counterbalanced A1-B1-A2-B2 live bench window on the relevant bench radio, 45s/120s watchdog |
| variable | Stage 354A | SIMULATED_MODEL_ONLY | model/simulation only; no physical measurement | Counterbalanced A1-B1-A2-B2 live bench window on the relevant bench radio, 45s/120s watchdog |
| variable | WMI 0x9064 | CONFIRMED_STATIC_BINARY | static binary proof only; runtime behaviour on hardware not measured | Counterbalanced A1-B1-A2-B2 bench of WMI command/retry-series on the PBE-5AC pair with 45s/120s watchdog |
| variable | WMI 0x9070 | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | Counterbalanced A1-B1-A2-B2 bench of WMI command/retry-series on the PBE-5AC pair with 45s/120s watchdog |
| variable | WMI 0x9065 | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | Counterbalanced A1-B1-A2-B2 bench of WMI command/retry-series on the PBE-5AC pair with 45s/120s watchdog |
| variable | WMI 0x9044 | SIMULATED_MODEL_ONLY | model/simulation only; no physical measurement | Counterbalanced A1-B1-A2-B2 bench of WMI command/retry-series on the PBE-5AC pair with 45s/120s watchdog |
| variable | Stage 342A | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | LTU-Lite bench windows (counterbalanced) for the SQ/AD9361/4096-QAM variable under test |
| variable | Stage 343A | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | LTU-Lite bench windows (counterbalanced) for the SQ/AD9361/4096-QAM variable under test |
| variable | Stage 344A | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | LTU-Lite bench windows (counterbalanced) for the SQ/AD9361/4096-QAM variable under test |
| variable | Stage 345A | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | LTU-Lite bench windows (counterbalanced) for the SQ/AD9361/4096-QAM variable under test |
| variable | Stage 346A | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | LTU-Lite bench windows (counterbalanced) for the SQ/AD9361/4096-QAM variable under test |
| variable | Stage 301A | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | Counterbalanced A1-B1-A2-B2 live bench window on the relevant bench radio, 45s/120s watchdog |
| variable | Stage 302A | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | Counterbalanced A1-B1-A2-B2 live bench window on the relevant bench radio, 45s/120s watchdog |
| variable | Stage 349A | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | LTU-Lite bench windows (counterbalanced) for the SQ/AD9361/4096-QAM variable under test |
| variable | Stage 350A | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | Counterbalanced A1-B1-A2-B2 live bench window on the relevant bench radio, 45s/120s watchdog |
| variable | Stage 59A | UNKNOWN | no matching classified receipt; provenance and bench evidence missing | Counterbalanced A1-B1-A2-B2 live bench window on the relevant bench radio, 45s/120s watchdog |
| pillar | A FullREA binary RE | PARTIAL | readiness 8.3% (1/12 live) | Close the variable-level gaps listed for this pillar |
| pillar | B HyperResearch/scholar | UNKNOWN | no blueprint variable maps to this pillar; readiness cannot be computed | Define a bench-linked scholar/literature receipt (offline) then pick one hardware hypothesis to measure |
| pillar | C Karpathy autoresearch | PARTIAL | readiness 8.3% (1/12 live) | Close the variable-level gaps listed for this pillar |
| pillar | D K-dense scientific | PARTIAL | readiness 0.0% (0/4 live) | Close the variable-level gaps listed for this pillar |
| pillar | E MemoryMaster | UNKNOWN | no blueprint variable maps to this pillar; readiness cannot be computed | Ingest bench-verified claims into MemoryMaster after a live measurement exists |
