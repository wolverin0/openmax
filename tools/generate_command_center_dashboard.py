#!/usr/bin/env python3
"""Generate the FuturaMAX Command Center HTML Dashboard and synchronize the Live Observability Hub."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_command_center_html import build_html
from tools.generate_observability_hub import generate_observability_hub


def generate_dashboard(md_out: Path | None = None) -> Path:
    """Refresh live_observability_hub.json and rebuild FUTURAMAX_COMMAND_CENTER.html."""
    generate_observability_hub()
    html_path = build_html(md_out_path=md_out)
    return html_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate FuturaMAX Command Center HTML and Live Observability Hub.")
    parser.add_argument("--md-out", type=Path, default=None, help="Optional Markdown spoiler digest output path.")
    args = parser.parse_args()
    out = generate_dashboard(md_out=args.md_out)
    print(f"GENERATED_COMMAND_CENTER_DASHBOARD: {out}")


if __name__ == "__main__":
    main()
