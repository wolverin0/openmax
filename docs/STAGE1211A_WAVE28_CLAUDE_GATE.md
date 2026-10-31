<!-- doc-head: Stage 1211A Wave 28 Claude gate offline: valida receipts 1206A..1210A, docs, enlaces rotos, aislamiento de corpus y humo del backbone SG-01 y del matcher sintoma/.ko. -->
# Stage 1211A - Wave 28 Claude gate

Compuerta 100% offline y fail-closed (`raise SystemExit(1)`), sin red ni dispositivos vivos.

## Entregables
- Gate: `tools/verify/verify_stage1211a_wave28_claude_gate.py`.
- Suite: `tests/test_stage1206a_to_1211a_suite.py`.
- Receipt: `artifacts/verification/stage1211a_wave28_claude_gate.json` (claim `FMX-STAGE1211A-WAVE28-CLAUDE-GATE`).

## Verificaciones
- Receipts 1206A..1210A en `artifacts/verification`: existen, no NUL, `status` CONFIRMED, `live_devices_touched` false, 5 pilares conformes.
- Docs: exactamente un `docs/STAGE{stage}_*.md` por etapa 1206A..1211A y ambos docs maestros, cada uno < 180 lineas con doc-head en la linea 1.
- Enlaces rotos: `tools/verify/build_stage1001a_broken_link_repair_and_reaudit.py` con `broken_links_after` == 0.
- Aislamiento de corpus sobre `artifacts/verification` y `artifacts/autoresearch` (sin fixtures sinteticos).
- Humo backbone: Almafuerte con 32 CPEs aguas abajo; `sg01_guard` veta `ether2-sw-poe200` power_cycle y permite channel_change en Guarida .61.
- Humo matcher: 9 clases de sintoma; cada una devuelve un `.ko` valido (ubnt_poll_host, ath10k_core, mac80211, eab_driver, ame_core) y una tarjeta PWO con `auto_approve` false.
