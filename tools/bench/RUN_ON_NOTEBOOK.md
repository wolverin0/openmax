<!-- doc-head: One-copy offline notebook endpoint -->
Copy the generated FuturaMAX-Notebook folder by USB, then double-click START_FUTURAMAX.cmd.
Includes real x86 and x64 binaries; automatically selects the Windows OS architecture.
Approve the Windows administrator prompt; no commands, downloads or installations.
READY means the local server is listening, not yet a completed radio benchmark.
Q performs cleanup; an independent guardian handles accidental window closure.
<!-- /doc-head -->

# Notebook: one copy, one double-click

1. Copy the whole generated **FuturaMAX-Notebook** folder from this PC to the notebook using the USB drive. Keep its contents together. This replaces the old setup; do not run the old script.
2. Double-click **START_FUTURAMAX.cmd**, then approve Windows' administrator prompt.
3. Leave the window showing green **READY** open. No PowerShell commands or Internet connection are needed.

Press **Q** when finished. Automatic session expiry is two hours. Do not start another copy while the existing window is running.

## Automatic handling

- Automatically selects the **32-bit (x86)** or 64-bit runtime using Windows OS architecture. The operator's notebook is 32-bit; no architecture choice or command is required. Both the executable and DLL must match the selected architecture.
- Uses a hash-verified, pre-extracted iperf 3.22 runtime. Each architecture has its own verified backup ZIP, and an alternate built-in ZIP reader covers a failed archive helper.
- Waits for the known Ethernet adapter (MAC `88-AE-1D-73-E1-C3`) and discovers its current `192.168.1.x/24` address. It does not change DHCP, Wi-Fi, DNS, the default gateway or radio configuration.
- Verifies the binary runs, protects occupied ports and existing conflicting routes, and adds only the test return route plus narrow per-program firewall rules.
- Checks the actual listening socket before printing READY. Restarts a failed server at most twice and preserves every attempt's logs.
- Copies runtime and cleanup helpers to protected local storage, so runtime no longer depends on the USB staying connected.
- Starts a separate hidden cleanup guardian before changing networking. Normal exit, window closure and expiry remove only this run's resources. A later launch also recovers an interrupted prior session.
- Publishes read-only JSON status on TCP 5202 to the two authorized lab source addresses only. It cannot execute commands.

Diagnostics are retained at `C:\ProgramData\FuturaMAX-NotebookRuns\<run-id>` (or the system's ProgramData location). The window prints the exact path. A failure preserves its message, transcript and available server logs.

## Honest limits

Administrator approval is required; the launcher cannot approve UAC. Enforced organization policies, application-control rules or unsupported Windows builds are not bypassed. The supplied **local folder** is checked for Internet-zone markers during packaging and works with process-local RemoteSigned; use that USB folder, not a browser-downloaded copy that Windows might mark as untrusted. No machine-wide execution policy, certificate checks or firewall protections are disabled.

The corrected x86 executable/DLL architecture and package checks are verified,
including tests in 32-bit PowerShell. Actual x86 transfer testing was blocked
by this controller PC's Defender policy; it was not bypassed and no x86 runtime
success is claimed. The x86 Cygwin dependency is legacy. See
`RUNTIME_PROVENANCE.md` for exact sources, hashes and acceptance limits.

Power loss/logoff can also terminate the guardian: the volatile route disappears at reboot, but persistent firewall rules may remain until the next helper launch performs recovery. No scheduled task or service is installed. Notebook UAC, actual firewall behavior and physical throughput still require the notebook run; local controller tests do not prove them.

If the helper stops because the physical adapter/network is wrong or a foreign service occupies a test port, it leaves those resources alone. It will not guess another adapter, terminate somebody else's server, or keep retrying indefinitely.

## Reproducible local checks (maintainer only)

Run `test_notebook_runtime.ps1` for fixture/mocked lifecycle tests, `test_notebook_status.ps1` for loopback HTTP, and `test_notebook_loopback.ps1` for actual bundled iperf forward/reverse loopback. Python tests are `test_notebook_launcher.py` and `test_notebook_package.py`. The builder is `build_notebook_bundle.ps1`; it makes a fresh uniquely named folder, ZIP, manifest and checksum without modifying a previous build.
