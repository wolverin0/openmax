#!/usr/bin/env python3
"""Generate the Live Observability Hub JSON payload and HTML section for FuturaMAX Command Center.

Includes:
- 4 Live Lanes (5GHz Bench, OpenWISP/ImageBuilder, Multi-Radio LTU+2.4GHz, Codex Verifiers + Stage 54C Sim)
- Promoted Champions (v1 -> v18, including Stage 51A Champion v17, Stage 52A Champion v18, and Stage 53A/54A PBE5AC PtP OTA)
- Rejected / Refuted Experiments (including Stage 51A and Stage 52A with physical mechanism explanations)
- PowerBeam 5AC Gen2 vs LiteBeam 5AC Gen2 PtP Comparison (Stage 54C: FF 8ms, FF 5ms, Flexible, OpenWrt Champion v18)
- Forward Roadmap (Stage 51A, Stage 52A, Stage 53A/54A, Stage 54C, Stage 48B Far, Stage 55A)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_command_center_html import (
    build_live_observability_payload,
    render_live_observability_hub_html,
)

DEFAULT_JSON_OUT = ROOT / "artifacts" / "dashboard" / "live_observability_hub.json"


def generate_observability_hub(output_path: Path = DEFAULT_JSON_OUT) -> Dict[str, Any]:
    """Build and write the Live Observability Hub payload to disk."""
    payload = build_live_observability_payload()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def main() -> None:
    payload = generate_observability_hub()
    html_snippet = render_live_observability_hub_html(payload)
    print(
        f"GENERATED_OBSERVABILITY_HUB: {DEFAULT_JSON_OUT} "
        f"(champions={payload['counts']['champions_promoted']}, "
        f"rejected={payload['counts']['experiments_rejected']}, "
        f"ptp_rows={payload['counts'].get('ptp_comparison_rows', 0)}, "
        f"html_bytes={len(html_snippet)})"
    )


if __name__ == "__main__":
    main()
