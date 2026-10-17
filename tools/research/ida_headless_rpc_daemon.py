"""
Headless IDA Pro 9.3 JSON-RPC daemon on 127.0.0.1:13337 for ida-pro-mcp & REA.
Copies the target binary into an isolated scratch directory per session so stale
.id0/.id1 lockfiles never block idapro.open_database().
"""
import argparse
import importlib
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import idapro
import ida_auto
import ida_hexrays


DEFAULT_CANDIDATES = [
    Path(r"G:\_OneDrive\OneDrive\Desktop\Py Apps\_worktrees\futuramax-night-20261007\firmware\build\re1-latest-20261011T173813Z-3b5c139e44\WA\rootfs\lib\modules\2.6.32.68\umac.ko"),
    Path(r"G:\_OneDrive\OneDrive\Desktop\Py Apps\_worktrees\futuramax-night-20261007\firmware\build\re1-20261010\XC\rootfs\lib\modules\2.6.32.68\umac.ko"),
]


def stage_clean_binary(src: Path, port: int) -> Path:
    stage_dir = Path(rf"C:\_tmp\ida_rpc_daemon_{port}")
    if stage_dir.exists():
        shutil.rmtree(stage_dir, ignore_errors=True)
    stage_dir.mkdir(parents=True, exist_ok=True)
    dst = stage_dir / src.name
    shutil.copy2(src, dst)
    return dst


def main() -> None:
    parser = argparse.ArgumentParser(description="Headless IDA Pro 9.3 RPC Daemon on 127.0.0.1:13337")
    parser.add_argument("--binary", type=Path, default=None, help="Initial binary to open in headless idalib")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=13337)
    args = parser.parse_args()

    binary = args.binary
    if binary is None or not binary.exists():
        for cand in DEFAULT_CANDIDATES:
            if cand.exists():
                binary = cand
                break
    if binary is None or not binary.exists():
        raise FileNotFoundError("Could not find initial binary to open")

    staged = stage_clean_binary(binary, args.port)
    idapro.enable_console_messages(False)
    print(f"[IDA-RPC-DAEMON] Opening staged database: {staged} (from {binary})", flush=True)
    rc = idapro.open_database(str(staged), run_auto_analysis=True)
    if rc:
        raise RuntimeError(f"Failed to open database (rc={rc}): {staged}")

    ida_auto.auto_wait()
    if not ida_hexrays.init_hexrays_plugin():
        print("[IDA-RPC-DAEMON] WARNING: Hex-Rays decompiler did not initialize", flush=True)
    else:
        print("[IDA-RPC-DAEMON] Hex-Rays decompiler initialized OK", flush=True)

    plugin = importlib.import_module("ida_pro_mcp.mcp-plugin")

    httpd = plugin.MCPHTTPServer((args.host, args.port), plugin.JSONRPCRequestHandler)
    print(f"[IDA-RPC-DAEMON] Listening at http://{args.host}:{args.port}/mcp", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        idapro.close_database(save=False)


if __name__ == "__main__":
    main()
