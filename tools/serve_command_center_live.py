"""
FuturaMAX Live Command Center Server & Auto-Builder (`tools/serve_command_center_live.py`).

Provides:
1. Background file-system watcher that monitors:
   - `artifacts/autoresearch/*.json`
   - `artifacts/orchestration/*.json`
   - `artifacts/hyperresearch_vault/claims/*.json`
   - `docs/*.md`
   Whenever any artifact or Markdown report changes, it automatically invokes
   `build_html()` so `artifacts/dashboard/FUTURAMAX_COMMAND_CENTER.html` on disk is
   always synchronized (working seamlessly via `file:///...`).
2. Local HTTP server on `http://127.0.0.1:8765` with CORS (`Access-Control-Allow-Origin: *`)
   and `Cache-Control: no-store`:
   - `GET /` or `GET /FUTURAMAX_COMMAND_CENTER.html` -> serves the latest Command Center HTML
   - `GET /api/status` -> returns JSON with `html_mtime`, `latest_source_mtime`, `stage_rounds_count`, `profiles_count`
   - `GET /api/live_summary` -> returns JSON with the full Champion Ledger + recent Stage 14..25 autoresearch rows
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading
import time
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_command_center_html import (  # noqa: E402
    CHAMPION_LEDGER_JSON,
    HTML_OUT_DEFAULT,
    TASK_BOARD_JSON,
    build_html,
    build_live_observability_payload,
    collect_stage_autoresearch_receipts,
)
from tools.serve_openwisp_dual_nms_live import (  # noqa: E402
    PORTAL_HTML_OUT,
    build_iptv_and_capacity_ceiling_api_payload,
    build_openwisp_dual_nms_registry,
    build_openwisp_portal_html,
    build_stage47c_guards_and_24ghz_m18_api_payload,
    export_openwisp_bql_eth0_r5ac_txq256_champion_v15_netjson_template,
    export_openwisp_iptv_netjson_template,
    export_openwisp_sysfs_txq256_champion_v14_netjson_template,
    export_openwisp_tx_bias_2_dynamic_bql_champion_v16_netjson_template,
)


def compute_sources_signature() -> float:
    """Return the latest mtime across watched autoresearch, orchestration, and docs files."""
    latest = 0.0
    watch_globs = [
        (ROOT / "artifacts" / "autoresearch", "*.json"),
        (ROOT / "artifacts" / "orchestration", "*.json"),
        (ROOT / "artifacts" / "hyperresearch_vault" / "claims", "*.json"),
        (ROOT / "docs", "*.md"),
    ]
    for folder, pat in watch_globs:
        if not folder.exists():
            continue
        for p in folder.glob(pat):
            try:
                mt = p.stat().st_mtime
                if mt > latest:
                    latest = mt
            except OSError:
                continue
    return latest


class WatcherState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.last_source_mtime: float = 0.0
        self.last_build_utc: str = ""
        self.rebuilds_count: int = 0

    def ensure_fresh(self, force: bool = False) -> bool:
        with self.lock:
            src_mt = compute_sources_signature()
            html_exists = HTML_OUT_DEFAULT.exists()
            if force or not html_exists or src_mt > self.last_source_mtime:
                build_html()
                build_openwisp_portal_html()
                self.last_source_mtime = max(src_mt, time.time())
                self.last_build_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                self.rebuilds_count += 1
                return True
            return False


STATE = WatcherState()


def build_status_payload() -> Dict[str, Any]:
    STATE.ensure_fresh(force=False)
    html_mtime = HTML_OUT_DEFAULT.stat().st_mtime if HTML_OUT_DEFAULT.exists() else 0.0
    stage_rows = collect_stage_autoresearch_receipts()
    profiles_count = 0
    if CHAMPION_LEDGER_JSON.exists():
        try:
            profiles_count = len(json.loads(CHAMPION_LEDGER_JSON.read_text(encoding="utf-8")).get("profiles", {}))
        except Exception:
            pass
    return {
        "status": "ok",
        "server": "futuraMAX-command-center-live",
        "html_path": str(HTML_OUT_DEFAULT),
        "html_mtime": round(html_mtime, 3),
        "last_build_utc": STATE.last_build_utc,
        "rebuilds_count": STATE.rebuilds_count,
        "stage_rounds_count": len(stage_rows),
        "profiles_count": profiles_count,
    }


def build_live_summary_payload() -> Dict[str, Any]:
    status = build_status_payload()
    ledger = {}
    if CHAMPION_LEDGER_JSON.exists():
        try:
            ledger = json.loads(CHAMPION_LEDGER_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    board = {}
    if TASK_BOARD_JSON.exists():
        try:
            board = json.loads(TASK_BOARD_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        **status,
        "champion_ledger": ledger,
        "stage_autoresearch_receipts": collect_stage_autoresearch_receipts(),
        "task_board": board,
    }


class CommandCenterHandler(BaseHTTPRequestHandler):
    def _send_headers(self, code: int, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html", "/FUTURAMAX_COMMAND_CENTER.html"):
            STATE.ensure_fresh(force=False)
            body = HTML_OUT_DEFAULT.read_bytes()
            self._send_headers(200, "text/html; charset=utf-8")
            self.wfile.write(body)
        elif path == "/OPENWISP_DUAL_NMS_PORTAL.html":
            STATE.ensure_fresh(force=False)
            if not PORTAL_HTML_OUT.exists():
                build_openwisp_portal_html()
            body = PORTAL_HTML_OUT.read_bytes()
            self._send_headers(200, "text/html; charset=utf-8")
            self.wfile.write(body)
        elif path == "/api/v1/controller/device/":
            reg = build_openwisp_dual_nms_registry()
            payload = json.dumps(
                {
                    "count": reg["devices_count"],
                    "approved_profile_set_sha256": reg["approved_profile_set_sha256"],
                    "results": [
                        {
                            "id": d["id"],
                            "device_key": d["device_key"],
                            "name": d["name"],
                            "ip": d["ip"],
                            "mac": d["mac"],
                            "profile_id": d["profile_id"],
                            "champion_version": d["champion_version"],
                            **d["openwisp_controller"],
                        }
                        for d in reg["devices"]
                    ],
                },
                indent=2,
            ).encode("utf-8")
            self._send_headers(200, "application/json; charset=utf-8")
            self.wfile.write(payload)
        elif path == "/api/v1/monitoring/device/":
            reg = build_openwisp_dual_nms_registry()
            payload = json.dumps(
                {
                    "count": reg["devices_count"],
                    "results": [
                        {
                            "id": d["id"],
                            "device_key": d["device_key"],
                            "name": d["name"],
                            "ip": d["ip"],
                            **d["openwisp_monitoring"],
                        }
                        for d in reg["devices"]
                    ],
                },
                indent=2,
            ).encode("utf-8")
            self._send_headers(200, "application/json; charset=utf-8")
            self.wfile.write(payload)
        elif path == "/api/v1/uisp/envelopes/":
            reg = build_openwisp_dual_nms_registry()
            payload = json.dumps(
                {
                    "count": reg["devices_count"],
                    "results": [
                        {
                            "id": d["id"],
                            "device_key": d["device_key"],
                            "name": d["name"],
                            "ip": d["ip"],
                            **d["uisp_udapi_bridge"],
                        }
                        for d in reg["devices"]
                    ],
                },
                indent=2,
            ).encode("utf-8")
            self._send_headers(200, "application/json; charset=utf-8")
            self.wfile.write(payload)
        elif path == "/api/v1/iptv/capacity/":
            payload = json.dumps(build_iptv_and_capacity_ceiling_api_payload(), indent=2).encode("utf-8")
            self._send_headers(200, "application/json; charset=utf-8")
            self.wfile.write(payload)
        elif path == "/api/v1/controller/template/iptv/":
            payload = json.dumps(export_openwisp_iptv_netjson_template(), indent=2).encode("utf-8")
            self._send_headers(200, "application/json; charset=utf-8")
            self.wfile.write(payload)
        elif path == "/api/v1/controller/template/stage47c-guards/":
            payload = json.dumps(build_stage47c_guards_and_24ghz_m18_api_payload(), indent=2).encode("utf-8")
            self._send_headers(200, "application/json; charset=utf-8")
            self.wfile.write(payload)
        elif path in ("/api/v1/controller/template/champion-v14-aqm/", "/api/v1/controller/template/champion-v14/"):
            payload = json.dumps(export_openwisp_sysfs_txq256_champion_v14_netjson_template(), indent=2).encode("utf-8")
            self._send_headers(200, "application/json; charset=utf-8")
            self.wfile.write(payload)
        elif path in ("/api/v1/controller/template/champion-v15-aqm/", "/api/v1/controller/template/champion-v15/"):
            payload = json.dumps(export_openwisp_bql_eth0_r5ac_txq256_champion_v15_netjson_template(), indent=2).encode("utf-8")
            self._send_headers(200, "application/json; charset=utf-8")
            self.wfile.write(payload)
        elif path in ("/api/v1/controller/template/champion-v16-aqm/", "/api/v1/controller/template/champion-v16/"):
            payload = json.dumps(export_openwisp_tx_bias_2_dynamic_bql_champion_v16_netjson_template(), indent=2).encode("utf-8")
            self._send_headers(200, "application/json; charset=utf-8")
            self.wfile.write(payload)
        elif path == "/api/status":
            payload = json.dumps(build_status_payload(), indent=2).encode("utf-8")
            self._send_headers(200, "application/json; charset=utf-8")
            self.wfile.write(payload)
        elif path == "/api/live_summary":
            payload = json.dumps(build_live_summary_payload(), indent=2).encode("utf-8")
            self._send_headers(200, "application/json; charset=utf-8")
            self.wfile.write(payload)
        elif path in ("/api/v1/observability/live", "/api/v1/observability/live/"):
            import importlib
            import tools.build_command_center_html as _bch
            importlib.reload(_bch)
            obs_payload = _bch.build_live_observability_payload()
            obs_json_path = ROOT / "artifacts" / "dashboard" / "live_observability_hub.json"
            obs_json_path.parent.mkdir(parents=True, exist_ok=True)
            obs_json_path.write_text(json.dumps(obs_payload, indent=2, ensure_ascii=False), encoding="utf-8")
            payload = json.dumps(obs_payload, indent=2).encode("utf-8")
            self._send_headers(200, "application/json; charset=utf-8")
            self.wfile.write(payload)
        else:
            self._send_headers(404, "application/json; charset=utf-8")
            self.wfile.write(b'{"error": "not_found"}')

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return


def background_watcher(interval_s: float = 5.0) -> None:
    while True:
        try:
            STATE.ensure_fresh(force=False)
        except Exception:
            pass
        time.sleep(interval_s)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--once", action="store_true", help="Build once and print status JSON without serving.")
    args = parser.parse_args()

    STATE.ensure_fresh(force=True)
    if args.once:
        print(json.dumps(build_status_payload(), indent=2))
        return

    watcher = threading.Thread(target=background_watcher, args=(5.0,), daemon=True)
    watcher.start()

    candidate_ports = [args.port, 8787, 8899, 18765, 28765]
    server = None
    bound_port = None
    for pt in candidate_ports:
        try:
            server = ThreadingHTTPServer((args.host, pt), CommandCenterHandler)
            bound_port = pt
            break
        except OSError:
            continue

    if server is not None and bound_port is not None:
        live_js_path = HTML_OUT_DEFAULT.parent / "live_status.js"
        payload = build_status_payload()
        payload["http_url"] = f"http://{args.host}:{bound_port}/FUTURAMAX_COMMAND_CENTER.html"
        live_js_path.write_text(f"window.FMX_LIVE_STATUS = {json.dumps(payload)};\n", encoding="utf-8")
        print(f"SERVING_COMMAND_CENTER_LIVE: http://{args.host}:{bound_port}/FUTURAMAX_COMMAND_CENTER.html", flush=True)
        server.serve_forever()
    else:
        print("WATCHER_ONLY_MODE_ACTIVE", flush=True)
        while True:
            time.sleep(5.0)


if __name__ == "__main__":
    main()
