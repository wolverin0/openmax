<!-- doc-head: Guarida offline prestage and host recording watchdog -->
Production GO is HOLD; this package runs local recording fixtures only.
Canonical sources and the public kit run without private firmware or backups.
The ignored private prestage bundle contains sensitive held firmware/backups.
<!-- /doc-head -->

# Guarida preproduction package

From the repository root, run `python -B -m pytest tests/test_preprod_guarida.py -q` for the 21 synthetic local checks. The reviewed fresh-HEAD test verifies dependency closure. `python -B -m safety.preprod.guarida_watchdog` defaults to PLAN_ONLY.

The byte-exact distributable [public kit](public_kit_20261022/CHECKLIST.txt) contains the minimal host watchdog, rollback snapshot, power dependency and disposable tests. From `safety/preprod/public_kit_20261022`, run `python -B -m pytest test_watchdog.py -q` for its 15 standalone checks. This directory is the logical `host/` root mentioned in the captured checklist; no additional `host/` subdirectory is needed.

The watchdog process detects same-host health failure or timeout and records one simulated rollback with exclusive ownership and an immutable intent latch. Its only driver is `recording_stub`. AP execution, real transfer/PoE/TFTP/postboot health, failed-boot recovery and survival of host/AP power loss remain unqualified. No production installer is supplied.

The [readiness receipt](../../artifacts/canary_panel1_guarida/preprod_guarida_readiness_20261022.json) keeps GO=false and no deployment candidate selected. Historical rejected production v3 and the bench-only image remain separate. The ignored `artifacts/canary_panel1_guarida/preprod_guarida_20261022/` bundle holds 20 verified backup copies and firmware; local prepare/complete/repair commands require that private evidence and are not public-clone workflows. Never publish that parent bundle.
