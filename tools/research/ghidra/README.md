<!-- doc-head: Bounded offline Ghidra qualification and verified MCP integration -->
RE1 inspects five pinned ET_REL host functions and the AP SGMT map without target execution.
Private runtime/imports/logs stay under firmware/build; each rerun has a fresh evidence directory.
Generic Xtensa syntax and decompiler output do not establish exact QCA-core or runtime semantics.
RE1.5 adds verified upstream MCP, private persistent projects and bounded Codex annotation tools.
<!-- /doc-head -->

# RE1 headless pilot

Uses the existing Ghidra 12.1.4 loaders/decompiler, JDK21, pyelftools and Capstone.
No network server, MCP registration, firmware execution, emulator, radio access,
global installation, package upgrade or automatic download occurs in this runner.
The initial RE1 pilot did not start the separately built upstream bridge.
RE1.5 below now installs/registers/verifies actual MCP; it is distinct from
this unchanged headless validation runner and its no-server behavior.

Run from the owned checkout, pointing `SourceRoot` at the checkout that holds the
original WA8.5.12 modules, qualified SGMT decoder and prior decoder receipt:

```powershell
powershell -NoProfile -File tools/research/ghidra/run_re1.ps1 `
  -SourceRoot 'G:/_OneDrive/OneDrive/Desktop/Py Apps/futuraMAX' `
  -GhidraHome 'firmware/build/re1-20261010/ghidra/ghidra_12.1.4_PUBLIC' `
  -JavaExe 'C:/Program Files/Eclipse Adoptium/jdk-21.0.12.101-hotspot/bin/java.exe'
python -m unittest discover -s tools/research/ghidra -p 'test_re1_pilot.py' -v
```

The runner pins both input module hashes before and after inspection. It selects
Ghidra's native ELF loader for the host, preserving sections/relocations/symbols.
The existing SGMT decoder supplies ordered AP segments; the harness derives a
last-write-wins, non-gap-filling final map. Ghidra imports only those payloads.
Private database imports/disassembly are analysis, not target code execution.

`host-ghidra.json` contains bounded instruction windows and five decompilations;
`byte-qualification.json` compares original host bytes, declares changed ELF
relocation sites, and compares fresh AP instruction bytes/mnemonics/lengths
with explicitly reused hash-bound ESP32 objdump evidence. Changed declared
relocations are retained, **not independently qualified runtime addresses**.
`ap-ghidra.json` uses the common Xtensa profile/default context. LITBASE and
QCA-specific extensions remain unqualified. A listing gap after a return is
not automatically a decoder failure. Unmapped pointer slots stay unknown.
The preparation-only byte receipt is not final acceptance: the runner requires
a fresh AP file and successful final qualification with `xtensa_comparison`.

Results are decision evidence, not a new command generator or transplanted
proprietary implementation. No full proprietary payload/decompilation is
committed. Keep failures/logs; do not call test counts a wireless gain.
<!-- doc-head: Qualified offline Ghidra analysis and working upstream MCP -->
RE1.5 runs upstream MCP against private copied projects; actual stdio checks pass.
Client tool allowlist is distinct from backend authentication, file-root and script controls.
No radio/target execution; native session discovery and actual calls now verified.
<!-- /doc-head -->

# Ghidra MCP integration (RE1.5)

The latest operator instruction supersedes the earlier MCP parking decision.
`mcp_launcher.py` runs the existing upstream GhidraMCP7.0.0 headless backend
and Python stdio bridge. Codex starts/stops it on demand; no scheduled watcher,
global dependency installation or radio access is involved. Runtime lives in
ignored `firmware/build/re1-20261010`. The venv and Ghidra installation are
owned by the isolated `futuramax-night-20261007` worktree; both Codex registration
entries intentionally point there, rather than into the dirty main checkout.

- Private persistent copies of the qualified host/AP projects retain annotations.
- Backend binds authenticated loopback TCP; token stays in process environment.
- Settings/cache/temp are private. Scripts disabled; external debugger disabled.
- 45 Codex `enabled_tools` permit analysis/annotations, not execution, emulation,
  debugger, original-byte patching, imports/exports or destructive operations.
  This is a client allowlist, not a restricted-server claim about the HTTP catalog.
- Owned shutdown saves and exits. Windows kill-on-close job prevents orphaning.
- Backend opens the MIPS host first. `list_project_files`, `open_project` and
  `open_program` let the agent navigate the private AP copy without new imports.
- Native tools loaded after operator restart:45 exposed, actual connection,
  metadata and known command0x9064 decompilation PASS in the agent session.

Checks from the isolated worktree:

```powershell
firmware/build/re1-20261010/mcp-venv/Scripts/python.exe tools/research/ghidra/test_mcp_integration.py
firmware/build/re1-20261010/mcp-venv/Scripts/python.exe tools/research/ghidra/test_mcp_registration.py
```

These operate on private copied databases. The first saves/reloads/restores a
test comment and verifies unchanged original module hashes; the second verifies
both config entries, actual catalog names, execution exclusions and preservation
of every unrelated config value. Do not run while another client owns this MCP
project; an already-locked project must fail rather than run empty.
Private pseudocode/catalog/logs remain untracked. Tracked acceptance summary:
`research/raw/re1-mcp-integration-20261010.json`. Dated `config.toml.bak-ghidra-*`
files preserve original configurations; no global hook/rule was disabled.

## RE1.6 held control-boundary continuation

`control_boundary.py` reuses hash-pinned SGMT, overlay and ELF oracles from
`--source-root`; surveys the held AP/PTP/STA and bootstrap blobs in RAM only.
It never executes a binary, contacts a radio or reads physical OTP/calibration.
Slot absence is UNKNOWN runtime content, not zero. LITBASE is a register-value
hypothesis, not a memory slot. Exact aligned literals are search candidates.
`--native-evidence` optionally checks55 bounded native MIPS rows against original
bytes with declared relocation field masks. Private pseudocode/results stay
ignored; the tracked receipt is a curated summary with raw-result hashes.

```powershell
python tools/research/ghidra/control_boundary.py --source-root 'G:/_OneDrive/OneDrive/Desktop/Py Apps/futuraMAX'
python -m unittest discover -s tools/research/ghidra -p 'test_control_boundary.py' -v
```

`RE1BmiInspect.java` is a bounded offline Ghidra script for three selected
download functions in the pinned umac module, used in a separate private
project with the established headless launch recipe. Its pseudocode/type
warning is candidate evidence, not initialization or target-execution proof.
Receipt: `research/raw/re1-control-boundary-20261010.json`.
