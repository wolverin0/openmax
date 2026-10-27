<!-- doc-head: STAGE581A_CROSS_FLEET_CHAMPION_V51_AND_TESTER_BUNDLE.md preserved document content -->
<!-- /doc-head -->



# Stage 581A — Cross-Fleet Champion `v51.0` & Tester Bundle (`588` Cross-Lane Windows)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-581A`
- **Champion Version**: **`v51.0`**
- **Cumulative Window Milestone (`588` Total Windows)**:
  - **`WA` Lane**: `228` counterbalanced `A1 -> B1 -> A2 -> B2` windows (`WA Champion v9`).
  - **Multi-Radio (`XC`/`2XC`/`XM`/`XW`) Lane**: **`180`** counterbalanced windows (`Stage 577A`, `R1..R116`).
  - **`AF-LTU` (`Beetle` + `ame_ASIC0`) Lane**: `180` counterbalanced windows.

## 2. Key Promotions in Cross-Fleet Champion `v51.0`
1. **WA v9 Kernel & Queue Promotions (`Stage 577A`)**: `net.ipv4.tcp_notsent_lowat=131072` (`128 KB`), `tx_queue_len=1000`, and `PB-050` Seg[2] `0x0040c140=4000ms` (`0xa00f0000`).
2. **QCA `PAPRD` + `CLPC` `1.5 dB` Backoff (`Stage 578A`)**: `paprd_enable=1` + `1.5 dB` `MCS 8/9` TX power backoff (`-34.9 dB` EVM, `93.4%` `256-QAM` residence, `0.0%` `1472B` loss).
3. **`AF-LTU` TDMA Frame & Split-Frequency Pareto (`Stage 579A`)**: `2.0 ms` (PtP) / `2.5 ms` (PtMP) frame duration, `40 MHz` TX/RX split-frequency isolation, and `ame_core_set_bc_dl_symbols=1`.
4. **Guarida Expansion Blueprint (`Stage 580A`)**: `Panel1-Guarida` (`.84`) `19.36h` zero-disconnect v9 soak validated as Wave 1 foundation for `Panel3` (`.83`, `6` CPEs) and `Panel2` (`.82`, `22` CPEs).

## 3. Artifacts
- **Script**: [`tools/autoresearch/build_stage581a_cross_fleet_champion_v51_and_tester_bundle.py`](../tools/autoresearch/build_stage581a_cross_fleet_champion_v51_and_tester_bundle.py)
- **Receipt**: [`artifacts/autoresearch/stage581a_cross_fleet_champion_v51_and_tester_bundle.json`](../artifacts/autoresearch/stage581a_cross_fleet_champion_v51_and_tester_bundle.json)
