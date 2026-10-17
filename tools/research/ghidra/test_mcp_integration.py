"""Real stdio MCP acceptance on private copied projects, not radio hardware."""
import asyncio
from datetime import timedelta
import hashlib
import json
import os
from pathlib import Path
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import mcp_launcher

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODULES = Path("G:/_OneDrive/OneDrive/Desktop/Py Apps/futuraMAX/firmware/build/codex-analysis-20261006/rootfs/lib/modules/2.6.32.68")
MARKER = "RE1 MCP acceptance annotation; no firmware/device mutation"


def body(result):
    payload = json.loads("".join(item.text for item in result.content if hasattr(item, "text")))
    if isinstance(payload, dict):
        assert payload.get("success", True), payload
        assert not payload.get("error"), payload
        return payload.get("data", payload)
    return payload


async def call(session, name, args=None):
    result = await session.call_tool(name, args or {})
    assert not result.isError, (name, result)
    body(result)
    return result


async def main():
    initial_profiles = set((mcp_launcher.STATE / "profiles").glob("*/lifecycle.json"))
    before = {name: hashlib.sha256((MODULES / name).read_bytes()).hexdigest()
              for name in ("umac.ko", "ubnt_poll_host.ko")}
    server = StdioServerParameters(command=sys.executable, args=[str(HERE / "mcp_launcher.py")])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=90)) as session:
            await session.initialize()
            tools = await session.list_tools()
            catalog = {tool.name: tool.model_dump(mode="json") for tool in tools.tools}
            assert "get_metadata" in catalog and "get_functions" in catalog
            results = {}
            for name, args in (
                ("get_metadata", {}),
                ("find_functions", {"name_pattern": "ubnt_poll_host_ht_comm_tx", "limit": 5}),
                ("get_functions", {"function": "ubnt_poll_host_ht_comm_tx", "fields": "decompiled_code,signature,callers,callees"}),
            ):
                result = await call(session, name, args)
                results[name] = result.model_dump(mode="json")
            payload = json.dumps(results)
            assert "ubnt_poll_host_ht_comm_tx" in payload
            assert "decompiled" in payload.lower()
            decompiled = body(result)["decompiled_code"]
            assert isinstance(decompiled, str) and decompiled.strip(), "Empty decompiler output"
            assert "ubnt_poll_host_ht_comm_tx" in decompiled, "Wrong decompiled function"
            assert "0x9064" in decompiled or "36964" in decompiled, "Known command literal missing"
            metadata = body(await call(session, "get_metadata"))
            assert metadata["language"] == "MIPS:BE:32:default", metadata
            assert metadata["program_name"] == "ubnt_poll_host.ko", metadata
            previous = body(await call(session, "get_comment", {"address": "0x11020"}))
            # Preserve the existing plate comment rather than clearing unrelated annotations.
            assert "plate" in previous and (previous["plate"] is None or isinstance(previous["plate"], str)), previous
            prior_plate = previous["plate"] or ""
            await call(session, "set_comment", {"address": "0x11020", "comment": MARKER})
            assert MARKER in json.dumps(body(await call(session, "get_comment", {"address": "0x11020"})))
            await call(session, "save_program")
            await call(session, "open_project", {"path": str(mcp_launcher.STATE / "projects" / (mcp_launcher.AP + ".gpr"))})
            await call(session, "open_program", {"path": "ap-segment-00.bin"})
            ap_metadata = body(await call(session, "get_metadata"))
            assert ap_metadata["language"] == "Xtensa:LE:32:default", ap_metadata
            ap_bytes = await call(session, "read_memory", {"address": "0x9b7264", "length": 12})
            assert body(ap_bytes), "Actual AP mapped bytes missing"
            private = ROOT / "firmware/build/re1-20261010/mcp-runtime"
            (private / "catalog.json").write_text(json.dumps(catalog, indent=2), encoding="utf-8")
            (private / "acceptance-private.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    # Fresh backend/process proves annotations survived save and server teardown.
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=90)) as session:
            await session.initialize()
            saved = body(await call(session, "get_comment", {"address": "0x11020"}))
            assert MARKER in json.dumps(saved), "Annotation did not persist"
            await call(session, "set_comment", {"address": "0x11020", "comment": prior_plate})
            await call(session, "save_program")
            restored = body(await call(session, "get_comment", {"address": "0x11020"}))
            assert (restored["plate"] or "") == prior_plate, "Original private annotation not restored"
    after = {name: hashlib.sha256((MODULES / name).read_bytes()).hexdigest() for name in before}
    assert after == before, "Original module changed"
    profiles = set((mcp_launcher.STATE / "profiles").glob("*/lifecycle.json")) - initial_profiles
    owned_pids = [json.loads(path.read_text())["backend_pid"] for path in profiles]
    assert len(owned_pids) == 2, "Expected two fresh backend lifecycle records"
    if os.name == "nt":
        import pywintypes
        import win32api
        import win32process
        for pid in owned_pids:
            try:
                handle = win32api.OpenProcess(0x1000, False, pid)
            except pywintypes.error as error:
                assert error.winerror == 87, "Cannot verify backend cleanup"
            else:
                try:
                    assert win32process.GetExitCodeProcess(handle) != 259, "Owned backend still alive"
                finally:
                    handle.Close()
    else:
        raise RuntimeError("This cleanup acceptance is qualified only on Windows")
    (mcp_launcher.STATE / "cleanup-final.json").write_text(json.dumps({"owned_backend_pids": owned_pids,
        "all_exited": True, "annotation_restored_and_reread": True}, indent=2), encoding="utf-8")
    print(json.dumps({"state": "PASS_REAL_STDIO_MCP", "tool_count": len(catalog),
                      "calls": list(results), "mips_host": "PASS", "xtensa_ap": "PASS",
                      "annotation_save_reload_restore": "PASS", "owned_backend_cleanup": "PASS",
                      "owned_backend_pids": owned_pids, "original_hashes": after}))


if __name__ == "__main__":
    asyncio.run(main())
