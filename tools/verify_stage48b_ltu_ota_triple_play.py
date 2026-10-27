"""Local-only CLI for Stage44B saved Stage48B evidence; never a radio runner."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from controller.stage48b_ltu_ota_triple_play_and_loop_flee_verifier import (  # noqa: E402
    OUTPUT, REPORT, SOURCE, audit_saved_sources, write_audit,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Local repository or saved-source fixture root")
    parser.add_argument("--output", type=Path, help="Local JSON destination; defaults to the requested audit artifact")
    parser.add_argument("--strict", action="store_true", help="Export, then exit1 while evidence qualifications remain")
    args = parser.parse_args(argv)
    try:
        audit = audit_saved_sources(args.root)
        path = write_audit(audit, args.output or args.root / OUTPUT,
                           protected_paths=(args.root / SOURCE, args.root / REPORT))
    except (OSError, ValueError, UnicodeError) as error:
        print(json.dumps({"status": "ERROR", "error": str(error), "native_dispatch_allowed": False}))
        return 2
    result = audit["stage48b"]
    print(json.dumps({"status": result["audit_status"], "output": str(path), "trials": len(result["trials"]),
                      "findings": len(result["findings"]), "native_acceptance": False}))
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
