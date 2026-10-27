"""Local-only Stage45B saved Stage51A/Stage49B verifier; no device dispatch."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from controller.stage51a_v17_and_stage49b_ltu_verifier import (  # noqa: E402
    OUTPUT, REPORT_51A, REPORT_49B, SOURCE_51A, SOURCE_49B, audit_saved_sources, write_audit,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Local repository or saved-source fixture root")
    parser.add_argument("--output", type=Path, help="Local managed JSON destination")
    parser.add_argument("--strict", action="store_true", help="Export, then exit1 while evidence qualifications remain")
    args = parser.parse_args(argv)
    try:
        audit = audit_saved_sources(args.root)
        path = write_audit(audit, args.output or args.root / OUTPUT,
                           protected_paths=tuple(args.root / p for p in (SOURCE_51A, SOURCE_49B, REPORT_51A, REPORT_49B)))
    except (OSError, ValueError, UnicodeError) as error:
        print(json.dumps({"status": "ERROR", "error": str(error), "native_dispatch_allowed": False}))
        return 2
    print(json.dumps({"status": audit["audit_status"], "output": str(path), "rounds": 6, "windows": 24,
                      "ltu_trials": 9, "native_acceptance": False}))
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
