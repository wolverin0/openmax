<!-- doc-head: STAGE700A_LIVE_PBE5AC_PTP_V4_GATE.md preserved document content -->
<!-- /doc-head -->


# Stage 700A — Live `.241 <-> .242` PtP Champion v4 700-Stage Consolidated Gate

- **Claim Status**: `CONFIRMED`
- **Attribution**: `external controller`
- **Live devices touched**: `False` (reads existing receipts only; no radio write)
- **Milestone**: 700-Stage milestone for the live PowerBeam 5AC Gen2 PtP line.

## 1. Purpose
Stage 700A is the single consolidated gate that closes the live PtP Champion v4
arc (Stages 695A..699A). It re-verifies each upstream receipt's invariants,
re-runs their pytest suite, and re-runs the repo-wide 5-pillar research gate,
emitting one receipt the downstream stages (811A+) can depend on.

## 2. Verified Upstream Receipts
| Stage | Receipt | Key invariants asserted |
| :--- | :--- | :--- |
| 695A | `stage695a_live_pbe5ac_vht40_pb040_pb050_champion_v4.json` | `CONFIRMED`, `vht40_clean_associated`, `ap_241_pb040_pb050_active` |
| 696A | `stage696a_live_pbe5ac_mk1_251_e2e_vht40_pb050_triple_play.json` | `CONFIRMED`, `ap_wds_vlan_active`, `sta_4addr_wds_active` |
| 697A | `stage697a_pbe5ac_dynamic_phy_and_sgmt_loader_v4.json` | `CONFIRMED`, `deployed_on_241_and_242`, watchdog 45s/120s |
| 698A | `stage698a_pbe5ac_lbe5ac_tester_release_package_v4.json` | `CONFIRMED` |
| 699A | `stage699a_pbe5ac_ptp_complete_evolution_ledger_v4.json` | `CONFIRMED`, `total_ptp_stages_completed=25` |

## 3. Gate Composition
1. **Receipt audit** — each receipt above exists and matches every asserted invariant (`all_receipts_ok`).
2. **Pytest suite** — `tests/test_stage695a.py` .. `tests/test_stage699a.py` all pass.
3. **5-pillar gate** — `tools/verify/enforce_5pillar_research_gate.py --check-repo` returns 0.

All three must pass for `status = CONFIRMED` and `all_gates_passed = true`.

## 4. Live Bench Context (from upstream receipts)
- Topology: `Host PC -> .241 AP (OpenWrt 24.10.4) -> VHT40 PB-040/PB-050 OTA 4addr WDS -> .242 STA`.
- Silicon state on `.241` and `.242`: `athwlan=12b29d01`, `0x00029e00=0x13761320`, PB-050 SGMT in RAM (`/tmp/firmware-2-pb050.bin`), zero flash writes.
- Zero-Rogue-DHCP preserved: `dnsmasq` and `odhcpd` disabled, no `192.168.1.20` on `br-lan`.

## 5. Reproduce
```sh
python tools/verify/verify_stage700a_live_pbe5ac_ptp_v4_gate.py
python -m pytest tests/test_stage695a_to_700a_suite.py -q
```

## 6. Output
- Receipt: `artifacts/autoresearch/stage700a_live_pbe5ac_ptp_v4_gate_receipt.json`
- Exit code `1` with a printed `receipt_audit` block if any upstream invariant,
  pytest case, or 5-pillar check fails (fail-closed).
