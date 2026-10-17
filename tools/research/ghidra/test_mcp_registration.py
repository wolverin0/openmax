"""Check exact Codex registrations without printing unrelated credentials."""
import json
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[3]
PATHS = [Path("C:/Users/pauol/.codex/config.toml"),
         Path("C:/Users/pauol/AppData/Roaming/orca/codex-runtime-home/home/config.toml")]


def main():
    catalog = json.loads((ROOT / "firmware/build/re1-20261010/mcp-runtime/catalog.json").read_text())
    entries = []
    for path in PATHS:
        current = tomllib.loads(path.read_text(encoding="utf-8"))
        backup = sorted(path.parent.glob(path.name + ".bak-ghidra-*"))[-1]
        previous = tomllib.loads(backup.read_text(encoding="utf-8"))
        entry = current["mcp_servers"].pop("ghidra")
        assert current == previous, "An unrelated configuration value changed"
        entries.append(entry)
        assert Path(entry["command"]).is_file() and Path(entry["args"][0]).is_file()
        assert entry["enabled"] and entry["startup_timeout_sec"] >= 60
        allowed = set(entry["enabled_tools"])
        assert allowed <= catalog.keys(), "Unknown tool name would be silently unavailable"
        assert {"get_metadata", "find_functions", "get_functions", "set_comment", "save_program"} <= allowed
        assert not any("debugger" in name or "emulat" in name or name.startswith("delete_")
                       or name.startswith("server_") or name.startswith("run_script")
                       or name.startswith("run_ghidra_script") for name in allowed)
        assert not allowed & {"import_file", "export_program", "exit_ghidra", "set_memory_block", "create_memory_block"}
    assert entries[0] == entries[1]
    print(json.dumps({"state": "PASS_REGISTRATION", "registrations": len(entries),
                      "enabled_tools": len(entries[0]["enabled_tools"]), "unrelated_config_preserved": True,
                      "execution_and_destructive_tools_excluded": True}))


if __name__ == "__main__":
    main()
