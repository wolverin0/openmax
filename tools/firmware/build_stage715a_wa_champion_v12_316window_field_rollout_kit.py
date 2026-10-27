#!/usr/bin/env python3
"""Retired historical WA v12 actuator: emit a refusal contract, never apply."""
from pathlib import Path
import hashlib
import sys

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from tools.verify import stage779_822_offline_common as c

HELPER_REL='firmware/openwrt/common/fmx_wa_v12_316window_field_kit.sh'
HELPER_PATH=ROOT/HELPER_REL
STEM='stage715a_wa_champion_v12_316window_field_rollout_kit'
RECEIPT_PATH=ROOT/f'artifacts/autoresearch/{STEM}.json'
DOC_PATH=ROOT/f'docs/{STEM.upper()}.md'
CANONICAL='firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh'


def build_helper_script() -> str:
    """Exact retirement contract; no historical executable body is retained."""
    return '#!/bin/sh\n# Historical WA v12 actuator is retired. No getters, mutation or delegation.\nset -eu\nMODE="${1:---inspect}"\ncase "$MODE" in\n  --inspect|--inspect-only|--dry-run)\n    [ "$#" -le 1 ] || { printf \'%s\\n\' \'RETIRED unsupported inspection arguments\' >&2; exit 64; }\n    printf \'%s\\n\' \'PLANNED_RETIRED wa_version=v12 runtime=UNKNOWN\'\n    printf \'%s\\n\' \'canonical=firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh explicit_identity_contract_required=true\'\n    ;;\n  *)\n    printf \'%s\\n\' \'RETIRED wa_version=v12 apply_refused=true canonical=firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh\' >&2\n    exit 64\n    ;;\nesac\n'


def build_htt_guard() -> str:
    """Historical guard generation is disabled; it is outside the v13 transaction."""
    raise RuntimeError('RETIRED: automatic HTT guard generation is disabled; review the canonical v13 contract')


def build(root: Path=ROOT) -> dict:
    root=Path(root)
    text=build_helper_script()
    c.atomic_write(c.local(root,HELPER_REL),text)
    data=c.receipt(715,'WA v12 historical actuator retirement',[c.snapshot(root,HELPER_REL)])
    data.update(status='RETIRED',execution_mode='OFFLINE_RETIREMENT',
                helper_script=HELPER_REL,helper_sha256=hashlib.sha256(text.encode()).hexdigest(),
                historical_reported_windows=316, historical_claim_scope='Imported historical summary only',
                runtime_acceptance='UNKNOWN',activation_allowed=False,automatic_execution_allowed=False,
                canonical_replacement=CANONICAL,automatic_alias=False,
                generation_contract='Emit identical refusal helper; do not recreate legacy queue/HTT mutators')
    return c.save(root,STEM,data,'Historical WA v12 actuator is RETIRED.\n'
        'Default/--inspect/--inspect-only/--dry-run returns PLANNED_RETIRED without getters or writes.\n'
        'Explicit apply and positional legacy arguments refuse with exit64.\n'
        'The canonical v13 path is a review pointer only, never an automatic alias or dispatch.\n'
        'Its own exact identity, snapshot/readback and rollback contract must be invoked explicitly.\n'
        'Historical 316 windows are imported claims, not fresh measurement or runtime acceptance.\n'
        'No queue, sysctl, DHCP, HTT guard, firmware or device action occurs during generation.\n')


def main() -> int:
    build()
    print('Stage715A RETIRED runtime=UNKNOWN')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
