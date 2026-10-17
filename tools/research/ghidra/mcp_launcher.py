"""Run the upstream Ghidra MCP bridge and an owned, private headless backend.

This is process/configuration glue, not a replacement MCP implementation.
The Codex enabled_tools list restricts agent access; the upstream HTTP catalog
is broader. Authentication, file-root containment and disabled scripts are
separate backend controls. No firmware/device execution is performed here.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request


CHECKOUT = Path(__file__).resolve().parents[3]
RUNTIME = CHECKOUT / "firmware/build/re1-20261010"
STATE = RUNTIME / "mcp-runtime"
GHIDRA = RUNTIME / "ghidra/ghidra_12.1.4_PUBLIC"
JAR = RUNTIME / "ghidra-mcp/build/libs/GhidraMCP-7.0.0.jar"
JAVA = Path("C:/Program Files/Eclipse Adoptium/jdk-21.0.12.101-hotspot/bin/java.exe")
SOURCE_PROJECTS = RUNTIME / "run-20261010-161816-777-aa0f1fd1/projects"
HOST = "re1-host-20261010-161816-777-aa0f1fd1"
AP = "re1-ap-20261010-161816-777-aa0f1fd1"
PROGRAM = "ubnt_poll_host.ko"


def private_projects() -> Path:
    """Fork qualified databases once; never overwrite existing annotations."""
    projects = STATE / "projects"
    projects.mkdir(parents=True, exist_ok=True)
    for name in (HOST, AP):
        destination = projects / (name + ".rep")
        if not destination.exists():
            shutil.copytree(SOURCE_PROJECTS / (name + ".rep"), destination)
            shutil.copy2(SOURCE_PROJECTS / (name + ".gpr"), projects / (name + ".gpr"))
        if not (projects / (name + ".gpr")).is_file():
            raise RuntimeError("Incomplete private Ghidra project; refusing automatic overwrite")
    return projects


def request(url: str, token: str, path: str, *, method: str = "GET") -> dict:
    req = urllib.request.Request(url + path, headers={"Authorization": "Bearer " + token},
                                 method=method, data=b"" if method == "POST" else None)
    # Local backend traffic must not inherit a machine HTTP proxy.
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=3) as response:
        return json.load(response)


def main() -> int:
    for path in (JAVA, JAR, GHIDRA / "Ghidra/Framework/Utility/lib/Utility.jar"):
        if not path.is_file():
            raise RuntimeError("Required local component missing: " + str(path))
    projects = private_projects()
    stamp = time.strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(4)
    profile = STATE / "profiles" / stamp
    for folder in ("settings", "cache", "temp", "sockets"):
        (profile / folder).mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    token = secrets.token_urlsafe(32)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    env.update({
        "GHIDRA_MCP_AUTH_TOKEN": token,
        "GHIDRA_MCP_ALLOW_SCRIPTS": "0",
        "GHIDRA_MCP_FILE_ROOT": str(STATE),
        "GHIDRA_MCP_URL": url,
        "GHIDRA_DEBUGGER_TOOLS": "0",
        "XDG_RUNTIME_DIR": str(profile / "sockets"),
        "TEMP": str(profile / "temp"), "TMP": str(profile / "temp"),
    })
    env.pop("GHIDRA_DEBUGGER_URL", None)
    env.pop("GHIDRA_MCP_BIND_ADDRESS", None)
    jars = [JAR]
    for group in ("Framework", "Features", "Processors", "Debug"):
        jars.extend(sorted((GHIDRA / "Ghidra" / group).glob("*/lib/*.jar")))
    arguments = [
        "-Djava.system.class.loader=ghidra.GhidraClassLoader",
        "-Djava.awt.headless=true", "-Xshare:off", "-Xmx2G",
        "-Dghidra.home=" + str(GHIDRA),
        "-XX:ParallelGCThreads=2", "-XX:CICompilerCount=2",
        "-Dapplication.settingsdir=" + str(profile / "settings"),
        "-Dapplication.cachedir=" + str(profile / "cache"),
        "-Dapplication.tempdir=" + str(profile / "temp"),
        "-Djava.io.tmpdir=" + str(profile / "temp"),
        "-cp", os.pathsep.join(str(jar) for jar in jars),
        "com.xebyte.headless.GhidraMCPHeadlessServer",
        "--bind", "127.0.0.1", "--port", str(port),
        "--project", str(projects / (HOST + ".gpr")), "--program", PROGRAM,
    ]
    # Full upstream classpath can exceed Windows' command-line limit.
    argument_file = profile / "java.args"
    argument_file.write_text("\n".join('"' + arg.replace("\\", "/").replace('"', '\\"') + '"'
                                      for arg in arguments), encoding="utf-8")
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    backend = None
    owned_job = None
    if os.name == "nt":
        import win32job
        owned_job = win32job.CreateJobObject(None, "FuturaMAX-Ghidra-MCP-" + stamp)
        limits = win32job.QueryInformationJobObject(owned_job, win32job.JobObjectExtendedLimitInformation)
        limits["BasicLimitInformation"]["LimitFlags"] |= win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        win32job.SetInformationJobObject(owned_job, win32job.JobObjectExtendedLimitInformation, limits)
    with (profile / "backend.log").open("wb") as log:
        try:
            backend = subprocess.Popen([str(JAVA), "@" + str(argument_file)], env=env, cwd=CHECKOUT,
                                       stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                       creationflags=flags)
            if owned_job is not None:
                win32job.AssignProcessToJobObject(owned_job, backend._handle)
            deadline = time.monotonic() + 60
            while True:
                if backend.poll() is not None:
                    raise RuntimeError(f"Ghidra backend exited {backend.returncode}; see {profile / 'backend.log'}")
                try:
                    metadata = request(url, token, "/check_connection")
                    break
                except (OSError, urllib.error.URLError, ValueError):
                    if time.monotonic() >= deadline:
                        raise RuntimeError("Ghidra backend startup timeout; see " + str(profile / "backend.log"))
                    time.sleep(0.2)
            try:
                request(url, "", "/get_metadata")
            except urllib.error.HTTPError as error:
                if error.code not in (401, 403):
                    raise RuntimeError("Unexpected backend authentication response") from error
            else:
                raise RuntimeError("Backend unexpectedly allowed unauthenticated metadata access")
            # No tokens, input contents or pseudocode in the lifecycle record.
            lifecycle = {"backend_pid": backend.pid, "url": url, "profile": str(profile),
                         "project": str(projects / (HOST + ".gpr")), "metadata": metadata,
                         "scripts_enabled": False, "debugger_proxy_enabled": False,
                         "unauthenticated_metadata_denied": True}
            (profile / "lifecycle.json").write_text(json.dumps(lifecycle, indent=2), encoding="utf-8")
            if metadata.get("program") != PROGRAM and metadata.get("program_name") != PROGRAM:
                raise RuntimeError("Expected private program not loaded; refusing empty/wrong backend")
            os.environ.update(env)
            os.environ.pop("GHIDRA_DEBUGGER_URL", None)
            os.environ.pop("GHIDRA_MCP_BIND_ADDRESS", None)
            # Reuse upstream entry point directly: its stdio transport owns the
            # inherited MCP pipes, avoiding an extra Windows handle-inheritance hop.
            from bridge_mcp_ghidra.cli import main as upstream_main
            sys.argv = ["bridge-mcp-ghidra", "--transport", "stdio", "--no-lazy"]
            upstream_main()
            return 0
        finally:
            for process in (backend,):
                if process is not None and process.poll() is None:
                    try:
                        request(url, token, "/exit_ghidra", method="POST")
                        process.wait(timeout=8)
                    except (OSError, ValueError, subprocess.TimeoutExpired):
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait(timeout=5)
            if owned_job is not None:
                owned_job.Close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
